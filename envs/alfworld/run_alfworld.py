"""ALFWorld student runner (port of SkillOpt's vendored env).

--slots worker threads run the episodes in parallel, each with its own
single-env manager.
The episode protocol follows skillopt/envs/alfworld/rollout.py: the skill is
prepended to the env-templated observation, the action is read from
<action>...</action> ('look' if missing), and success is the env's 'won'.
Episodes are logged as '## [k] ROLE' markdown.

Usage:
  ALFWORLD_DATA=$PWD/envs/alfworld/data/alfworld_data \
  python -m envs.alfworld.run_alfworld --model deepseek-v4-flash-0731 \
      --items envs/alfworld/data/alfworld_test_items.json \
      --run-tag alftest --slots 16
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import dskill  # noqa: E402,F401  (puts third_party/trace2skill on sys.path)

from react_agent.models import Message                      # noqa: E402
from dskill.llm.client import make_client                   # noqa: E402

SYSTEM = "You are an expert agent operating in the ALFRED Embodied Environment."
_RES_LOCK = threading.Lock()


def _skill_prompt(skill: str) -> str:
    if not skill.strip():
        return ""
    return ("\n\n## Skill Knowledge\n"
            "Below is a skill document with learned strategies. "
            "Use these guidelines to inform your decisions:\n\n"
            f"{skill}\n")


def _extract_action(resp: str) -> str | None:
    m = re.search(r"<action>(.*?)</action>", resp, re.DOTALL)
    return m.group(1).strip() if m else None


def run_episode(item, skill, model, effort, max_steps, logdir):
    from envs.alfworld.vendor.builder import build_alfworld_env
    mgr = build_alfworld_env(env_num=1,
                             specific_gamefiles=[item["gamefile"]])
    t0 = time.time()
    won = False
    turns = [("SYSTEM", SYSTEM)]
    usage = {"prompt_tokens": 0, "completion_tokens": 0,
             "reasoning_tokens": 0, "cached_tokens": 0,
             "calls": 0, "uncounted_calls": 0}
    exhausted = True
    try:
        obs, infos = mgr.reset({})
        sp = _skill_prompt(skill)
        client = make_client(model, effort)
        for _ in range(max_steps):
            prompt = (sp + "\n" + obs["text"][0]) if sp else obs["text"][0]
            rzn = ""
            try:
                out = client.chat(
                    [Message(role="system", content=SYSTEM),
                     Message(role="user", content=prompt)],
                    return_reasoning=True)
                resp, rzn = out if isinstance(out, tuple) else (out or "", "")
                resp = (resp or "").strip()
                u = getattr(client, "last_usage", None)
                usage["calls"] += 1
                if u:
                    for k in ("prompt_tokens", "completion_tokens",
                              "reasoning_tokens", "cached_tokens"):
                        usage[k] += u.get(k, 0)
                else:
                    usage["uncounted_calls"] += 1
            except Exception as e:                          # noqa: BLE001
                resp, rzn = f"(error: {e})", ""
            if not resp or _extract_action(resp) is None:
                resp = resp + "\n<action>look</action>"
            turns.append(("USER", prompt))
            turns.append(("ASSISTANT",
                          (f"(reasoning)\n{rzn}\n(final)\n{resp}"
                           if rzn.strip() else resp)))
            obs, rewards, dones, infos = mgr.step([resp])
            if infos[0].get("won"):
                won = True
            if bool(dones[0]):
                exhausted = False
                break
    finally:
        try:
            mgr.envs.close()
        except Exception:                                   # noqa: BLE001
            pass
    if exhausted and not won:
        turns.append(("USER",
                      "You have used all the turns. The episode is over "
                      "and the task was not completed."))
    md = ["# Chat History: alfworld\n"]
    for k, (role, text) in enumerate(turns, 1):
        md.append(f"## [{k}] {role}\n\n{text}\n")
    iid = str(item["id"]).replace(":", "-")
    (logdir / f"alfworld_{iid}.md").write_text("\n".join(md))
    return {"task": iid, "hard": int(won), "soft": float(won),
            "task_type": item.get("task_type", ""),
            "n_turns": sum(1 for r, _ in turns if r == "ASSISTANT"),
            "usage": usage,
            "status": "ok", "wall_s": round(time.time() - t0, 1)}


def main():
    from dskill.llm.pin_provider import install as _pin
    _pin()
    assert os.environ.get("ALFWORLD_DATA"), "set ALFWORLD_DATA"
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--items", required=True)
    ap.add_argument("--ids", default=None)
    ap.add_argument("--skill-file", default=None)
    ap.add_argument("--run-tag", required=True)
    ap.add_argument("--max-steps", type=int, default=50)
    ap.add_argument("--slots", "--batch-size", type=int, default=16,
                    dest="slots")
    ap.add_argument("--effort", default=None)
    args = ap.parse_args()

    items = json.load(open(Path(args.items).expanduser()))
    if args.ids:
        keep = set(args.ids.split(","))
        items = [i for i in items
                 if str(i["id"]).replace(":", "-") in keep]
    skill = (Path(args.skill_file).expanduser().read_text()
             if args.skill_file else "")
    base = Path("runs") / f"alfworld_{args.model}_{args.run_tag}"
    logdir = base / "logs"
    logdir.mkdir(parents=True, exist_ok=True)
    resfile = base / "results.jsonl"
    done = {json.loads(l)["task"] for l in open(resfile)} \
        if resfile.exists() else set()
    todo = [i for i in items
            if str(i["id"]).replace(":", "-") not in done]
    print(f"alfworld {args.model} [{args.run_tag}]: {len(done)} done, "
          f"{len(todo)} to run, slots={args.slots}", flush=True)
    state = {"k": len(done), "won": 0, "new": 0}

    def worker(item):
        rec = run_episode(item, skill, args.model, args.effort,
                          args.max_steps, logdir)
        with _RES_LOCK:
            with open(resfile, "a") as fh:
                fh.write(json.dumps(rec) + "\n")
            state["k"] += 1
            state["new"] += 1
            state["won"] += rec["hard"]
            print(f"[{state['k']}/{len(items)}] "
                  f"hard(new)={state['won']}/{state['new']} "
                  f"({rec['task']}: {rec['hard']} {rec['n_turns']}t "
                  f"{rec['wall_s']}s)", flush=True)
        return rec

    with ThreadPoolExecutor(max_workers=args.slots) as ex:
        list(ex.map(worker, todo))
    allres = [json.loads(l) for l in open(resfile)]
    n = len(allres)
    hard = sum(r["hard"] for r in allres) / max(n, 1)
    print(f"FINAL {args.model}: n={n} hard={hard:.4f} soft={hard:.4f}")


if __name__ == "__main__":
    main()
