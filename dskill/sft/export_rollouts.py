"""Export the frozen expert rollout library as self-contained JSON.

Writes runs/rollouts/expert_rollouts.json (task metadata, full trace, outcome
and produced-workbook path per episode) for the 99 distill tasks of
split_shuffled42.json, the paper's SFT corpus and dskill.sft.build_data's
default --rollouts input. --teacher-run is the teacher's run on those tasks.

    python -m dskill.sft.export_rollouts --teacher-run runs/<teacher_run> \
        --out-dir runs/rollouts
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from envs.spreadsheetbench.dataset import load_verified   # noqa: E402

SPLIT = REPO / "envs/spreadsheetbench/assets/split_shuffled42.json"

_TURN = re.compile(r"^## \[(\d+)\] (SYSTEM|USER|ASSISTANT)$", re.MULTILINE)


def n_turns(trace: str) -> int:
    return sum(1 for m in _TURN.finditer(trace) if m.group(2) == "ASSISTANT")


def collect(run_dir: Path, by_id: dict, ids: list[str]) -> list[dict]:
    scores = {}
    rp = run_dir / "results.jsonl"
    if rp.exists():
        for line in rp.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                scores[r["task"]] = r
    out = []
    for tid in ids:
        lp = next(iter((run_dir / "logs").glob(f"*_{tid}.md")), None)
        if lp is None:
            continue
        trace = lp.read_text()
        rec = by_id[tid]
        od = run_dir / "outputs" / "spreadsheet" / tid
        xl = next(iter(od.glob("*_output.xlsx")), None) if od.exists() else None
        s = scores.get(tid, {})
        row = {
            "task_id": tid,
            "instruction": rec["instruction"],
            "instruction_type": rec.get("instruction_type"),
            "answer_sheet": rec.get("answer_sheet"),
            "answer_position": rec.get("answer_position"),
            "input_spreadsheet": rec.get("spreadsheet_path"),
            "trace": trace,
            "trace_chars": len(trace),
            "assistant_turns": n_turns(trace),
            "hard": s.get("hard"),
            "soft": s.get("soft"),
            "status": s.get("status"),
            "wall_s": s.get("wall_s"),
            "output_workbook": (str(xl.relative_to(REPO)) if xl.is_relative_to(REPO)
                                else str(xl)) if xl else None,
        }
        out.append(row)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--teacher-run", type=Path, required=True,
                    help="teacher run folder (logs/, outputs/, results.jsonl)")
    ap.add_argument("--out-dir", type=Path, default=REPO / "runs/rollouts")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    _, by_id = load_verified()
    train = json.loads(SPLIT.read_text())["distill"]

    exp = collect(args.teacher_run.resolve(), by_id, train)
    exp_doc = {
        "name": "expert_rollouts",
        "role": "expert / behavioural target",
        "agent_model": "deepseek-v4-pro",
        "skill": "SkillOpt-5.5 (envs/spreadsheetbench/assets/skillopt_pkg)",
        "max_turns": 100,
        "split": "split_shuffled42 distill (99 tasks)",
        "n_episodes": len(exp),
        "train_accuracy": round(
            sum(e["hard"] or 0 for e in exp) / max(1, len(exp)), 4),
        "source_run": str(args.teacher_run),
        "episodes": exp,
    }
    p = args.out_dir / "expert_rollouts.json"
    p.write_text(json.dumps(exp_doc, indent=1))
    print(f"[export] {p}: {len(exp)} episodes, "
          f"train acc {exp_doc['train_accuracy']:.3f}, "
          f"{p.stat().st_size/1e6:.1f} MB", flush=True)


if __name__ == "__main__":
    main()
