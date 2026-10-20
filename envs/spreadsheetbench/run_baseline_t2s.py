#!/usr/bin/env python
"""SpreadsheetBench-Verified runner on the Trace2Skill scaffold.

One CLIOnlyAgent (or, with --skills-dir, CLISkillPreloadedAgent) per task, scored
with the official comparison into runs/<run>/results.jsonl. Resumable.
Without --ids it runs a task set of assets/split_shuffled42.json: --split eval
(default, the paper's 200 eval tasks) or --split distill (the 99 distillation tasks).

    python -m envs.spreadsheetbench.run_baseline_t2s --model <student> [--split distill]
        [--skills-dir <dir with xlsx/SKILL.md>] [--run-tag <tag>] [--concurrency 6]
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parents[1]
sys.path.insert(0, str(REPO))
import dskill  # noqa: E402,F401  (puts third_party/trace2skill on sys.path)

from envs.spreadsheetbench.spreadsheet_agent.agents.cli_only_agent import CLIOnlyAgent  # noqa: E402
from envs.spreadsheetbench.spreadsheet_agent.agents.cli_skill_preloaded_agent import (  # noqa: E402
    CLISkillPreloadedAgent)
from envs.spreadsheetbench.spreadsheet_agent.runner import SpreadsheetBenchRunner       # noqa: E402

from envs.spreadsheetbench.dataset import VERIFIED, load_verified  # noqa: E402
from dskill.llm.client import make_client  # noqa: E402

_CLIENTS: list = []


def _mk_tracked(model, effort):
    c = make_client(model, effort)
    _CLIENTS.append(c)
    return c

# string-aware action parsing + missing-brace repair (HD_ROBUST_PARSE=0 disables)
from dskill.llm import robust_parse as _robust_parse  # noqa: E402
from envs.spreadsheetbench.native_tools import install as _native_tools_install  # noqa: E402
_native_tools_install()          # no-op unless HD_NATIVE_TOOLS=1
_robust_parse.maybe_install()
from envs.spreadsheetbench.scoring import score_instance                         # noqa: E402


def run_one(tid: str, by_id: dict, base: Path, model: str,
            max_turns: int, skills_dir: str | None = None,
            effort: str | None = None) -> dict:
    t0 = time.time()
    rec = by_id[tid]
    data_file = VERIFIED / f"_hd_bl_{model.replace('/', '_')}_{tid}.json"
    data_file.write_text(json.dumps([rec]))
    status = "ok"
    try:
        if skills_dir:
            agent = CLISkillPreloadedAgent(
                _mk_tracked(model, effort), skills_dir=skills_dir,
                max_turns=max_turns, verbose=False,
                log_dir=str(base / "logs"))
        else:
            agent = CLIOnlyAgent(_mk_tracked(model, effort),
                                 max_turns=max_turns,
                                 verbose=False,
                                 log_dir=str(base / "logs"))
        runner = SpreadsheetBenchRunner(
            agent, data_path=str(data_file),
            output_dir=str(base / "outputs"),
            working_dir=str(base / "work"))
        runner.run()
    except Exception as e:                    # noqa: BLE001
        status = f"error:{type(e).__name__}"
    finally:
        try:
            data_file.unlink()
        except OSError:
            pass
    soft, hard = score_instance(tid, base / "outputs",
                                rec["spreadsheet_path"])
    return {"task": tid, "soft": soft, "hard": hard, "status": status,
            "wall_s": round(time.time() - t0, 1)}


def main():
    from dskill.llm.pin_provider import install as _pin_install
    _pin_install()
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--concurrency", type=int, default=6)
    ap.add_argument("--max-turns", type=int, default=100)
    ap.add_argument("--run-tag", default="",
                    help="suffix for the results dir (repeat passes)")
    ap.add_argument("--effort", default=None,
                    help="reasoning_effort for the model (e.g. high)")
    ap.add_argument("--skills-dir", default=None,
                    help="frozen skills root (skills_vK) -> eval with "
                         "CLISkillPreloadedAgent; results dir gets a tag")
    ap.add_argument("--split", choices=("eval", "distill"), default="eval",
                    help="task set of assets/split_shuffled42.json: eval (the "
                         "200 eval tasks) or distill (the 99 distillation tasks)")
    ap.add_argument("--ids", default=None,
                    help="comma-separated task ids to run (overrides "
                         "--split/--n; for batch-iterated campaigns)")
    args = ap.parse_args()

    _, by_id = load_verified()
    split_ids = json.loads((_HERE / "assets/split_shuffled42.json").read_text())[args.split]
    if args.ids:
        todo = [t for t in args.ids.split(",") if t.strip()]
    else:
        todo = split_ids[:args.n] if args.n else split_ids

    tag = f"_effort-{args.effort}" if args.effort else ""
    if args.skills_dir:
        tag = "_" + Path(args.skills_dir).parent.name + "_" + \
            Path(args.skills_dir).name
    rt = f"_{args.run_tag}" if args.run_tag else ""
    base = REPO / "runs" / (f"baseline_t2s_{args.model.replace('/', '_')}"
                            f"{tag}{rt}")
    base.mkdir(parents=True, exist_ok=True)
    results = base / "results.jsonl"
    done = set()
    if results.exists():
        done = {json.loads(l)["task"] for l in
                results.read_text().splitlines() if l.strip()}
    todo = [t for t in todo if t not in done]
    total = len(todo) + len(done)
    print(f"{args.model} @ T2S scaffold: {len(done)} done, {len(todo)} to "
          f"run, conc={args.concurrency}", flush=True)

    lock = threading.Lock()
    stats = {"n": len(done), "hard": 0, "t0": time.time()}

    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = [ex.submit(run_one, t, by_id, base, args.model,
                          args.max_turns, args.skills_dir, args.effort)
                for t in todo]
        for f in as_completed(futs):
            r = f.result()
            with lock:
                with results.open("a") as fh:
                    fh.write(json.dumps(r) + "\n")
                stats["n"] += 1
                stats["hard"] += r["hard"]
                k = stats["n"] - len(done)
                rate = (time.time() - stats["t0"]) / max(1, k)
                eta = rate * (total - stats["n"]) / 60
                print(f"[{stats['n']}/{total}] hard(new)={stats['hard']}/{k} "
                      f"avg={rate:.0f}s eta={eta:.0f}min "
                      f"({r['task']}: {r['hard']} {r['wall_s']}s "
                      f"{r['status']})", flush=True)

    lines = [json.loads(l) for l in results.read_text().splitlines()]
    n = len(lines)
    try:
        ut = {"prompt_tokens": 0, "completion_tokens": 0,
              "cached_tokens": 0, "calls": 0}
        for c in _CLIENTS:
            for k in ut:
                ut[k] += getattr(c, "usage_totals", {}).get(k, 0)
        if ut["calls"]:
            (base / "usage.json").write_text(json.dumps(
                {**ut, "n_tasks": n}, indent=1))
            print(f"USAGE {ut}")
    except (OSError, TypeError, AttributeError) as e:
        print(f"warning: usage.json not written ({type(e).__name__}: {e})",
              file=sys.stderr)
    print(f"FINAL {args.model}: n={n} "
          f"hard={sum(r['hard'] for r in lines)/n:.4f} "
          f"soft={sum(r['soft'] for r in lines)/n:.4f}", flush=True)


if __name__ == "__main__":
    main()
