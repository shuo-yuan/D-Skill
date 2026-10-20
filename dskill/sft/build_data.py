"""Convert the frozen teacher rollouts into SFT training data.

One example per episode: the student's own skill-free system prompt, then the
full ReAct exchange with loss on assistant turns only. Every episode is kept
(no correctness filter); assistant turns get deterministic protocol cleaning.

    python -m dskill.sft.build_data --student-run runs/<student_run> \
        --out runs/sft/teacher_sft.jsonl

--student-run is a skill-free student run; its first log holds the student's
system prompt.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

TURN = re.compile(r"^## \[(\d+)\] (SYSTEM|USER|ASSISTANT)\s*$", re.M)

_FABRICATED_OBS = re.compile(r"\n\s*Observation:", re.M)
_TRAILING_FENCE = re.compile(r"(</tool_call>|\})\s*\n\s*```\s*$")
_SECOND_ACTION = re.compile(r"(<tool_call>|^\s*Action:)", re.M)


def _repair_unclosed_json(text: str) -> tuple[str, bool]:
    """Close an action whose JSON object never closes; -> (text, repaired)."""
    if "Action:" not in text:
        return text, False
    head, body = text.split("Action:", 1)
    from dskill.llm.robust_parse import scan_json
    start, end, depth = scan_json(body)
    if start is None or end is not None or depth <= 0:
        return text, False
    tail = body[start:].rstrip()
    import json as _json
    for cut in (len(tail), (tail.rfind("}") + 1) or len(tail)):
        piece = tail[:cut]
        _, _, d = scan_json(piece)
        if d <= 0:
            continue
        cand = piece + ("}" * d)
        try:
            _json.loads(cand)
        except Exception:                                  # noqa: BLE001
            continue
        return head + "Action:" + body[:start] + cand, True
    return text, False


def clean_assistant(text: str) -> tuple[str, list[str]]:
    """Return (cleaned_turn, [pathologies_fixed]). Deterministic, no GT."""
    fixed = []
    text, did = _repair_unclosed_json(text)
    if did:
        fixed.append("unclosed_json")
    m = _FABRICATED_OBS.search(text)
    if m:                       # model narrated its own observation
        text = text[:m.start()].rstrip()
        fixed.append("fabricated_observation")
    starts = [mm.start() for mm in _SECOND_ACTION.finditer(text)]
    if len(starts) > 1:         # several actions crammed into one turn
        text = text[:starts[1]].rstrip()
        fixed.append("multi_action")
    new = _TRAILING_FENCE.sub(r"\1", text.rstrip()).rstrip()
    if new != text.rstrip():    # stray ``` the harness cannot parse
        fixed.append("stray_fence")
        text = new
    return text, fixed


def student_system_prompt(student_run: Path) -> str:
    """The skill-free system prompt the student actually sees at eval."""
    logs = sorted(glob.glob(f"{student_run}/logs/*.md"))
    if not logs:
        raise SystemExit(f"no episode logs in {student_run}/logs")
    f = logs[0]
    t = Path(f).read_text(errors="ignore")
    m = re.search(r"^## \[1\] SYSTEM\s*$", t, re.M)
    n = re.search(r"^## \[2\] USER\s*$", t, re.M)
    return t[m.end():n.start()].strip()


def split_turns(trace: str) -> list[tuple[str, str]]:
    """-> [(role, text), ...] for the episode body (system turn dropped)."""
    marks = [(m.start(), m.end(), m.group(2)) for m in TURN.finditer(trace)]
    out = []
    for i, (_s, e, role) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(trace)
        text = trace[e:end].strip()
        if role == "SYSTEM" or not text:
            continue
        out.append(("user" if role == "USER" else "assistant", text))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--student-run", type=Path, required=True,
                    help="skill-free student run whose logs hold the system prompt")
    ap.add_argument("--rollouts", type=Path,
                    default=REPO / "runs/rollouts/expert_rollouts.json")
    ap.add_argument("--out", type=Path, default=REPO / "runs/sft/teacher_sft.jsonl")
    ap.add_argument("--ids", type=str, default="",
                    help="comma-separated task_id allowlist (sample-"
                         "efficiency arms, e.g. the first 100 train ids)")
    args = ap.parse_args()

    doc = json.loads(args.rollouts.read_text())
    sysmsg = student_system_prompt(args.student_run)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    from collections import Counter
    kept, dropped, lens, trainable = [], 0, [], []
    fixes, eps_fixed = Counter(), 0
    allow = {t.strip() for t in args.ids.split(",") if t.strip()}
    for ep in doc["episodes"]:
        if allow and str(ep.get("task_id")) not in allow:
            continue
        turns = split_turns(ep["trace"])
        if not turns or turns[0][0] != "user":
            dropped += 1
            continue
        msgs = [{"role": "system", "content": sysmsg, "loss": False}]
        ep_fixed = False
        for role, text in turns:
            if role == "assistant":
                text, got = clean_assistant(text)
                for g in got:
                    fixes[g] += 1
                if got:
                    ep_fixed = True
                if not text.strip():          # nothing legitimate survived
                    continue
            msgs.append({"role": role, "content": text,
                         "loss": role == "assistant"})
        eps_fixed += int(ep_fixed)
        n_chars = sum(len(m["content"]) for m in msgs)
        lens.append(n_chars)
        trainable.append(sum(len(m["content"]) for m in msgs if m["loss"]))
        kept.append({"task_id": ep["task_id"], "messages": msgs,
                     "teacher_hard": ep.get("hard"),
                     "n_assistant_turns": sum(1 for m in msgs if m["loss"])})

    with args.out.open("w") as fh:
        for row in kept:
            fh.write(json.dumps(row) + "\n")

    import statistics as st
    s = sorted(lens)
    print(f"[sft] wrote {len(kept)} examples -> {args.out}"
          " (GT-free: all episodes)")
    if dropped:
        print(f"[sft] dropped {dropped} episodes")
    print(f"[sft] system prompt: {len(sysmsg):,} chars (skill-stripped)")
    print(f"[sft] example length: median {s[len(s)//2]:,}c "
          f"(~{s[len(s)//2]//4:,} tok) | p90 {s[int(.9*len(s))]:,} "
          f"| max {max(s):,} (~{max(s)//4:,} tok)")
    for ctx in (8192, 16384, 32768, 65536):
        pct = 100 * sum(1 for x in lens if x / 4 <= ctx) / len(lens)
        print(f"[sft]   fits {ctx//1024}k-token context: {pct:.0f}%")
    print(f"[sft] trainable (assistant) text: {sum(trainable)/1e6:.2f}M chars "
          f"(~{sum(trainable)/4e6:.2f}M tok), "
          f"mean {st.mean(trainable):,.0f}c/example")
    print(f"[sft] teacher accuracy in this set: "
          f"{100*sum(1 for r in kept if r['teacher_hard'])/len(kept):.1f}%")
    print(f"[sft] protocol cleaning: {eps_fixed} episodes touched "
          f"({100*eps_fixed/len(kept):.0f}%); turn-level fixes "
          f"{dict(fixes)}")


if __name__ == "__main__":
    main()
