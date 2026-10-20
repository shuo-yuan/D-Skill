"""Remove the play tool's final verdict from staged Claude Code chess traces.

The first USER turn that carries a final verdict ("Correct! Puzzle solved" or "That move is not the puzzle
solution") is replaced by a neutral "The puzzle is over" message, and every later turn is dropped, since the agent's
reaction would reveal the verdict. Intermediate "Correct. The opponent has replied" turns are kept.

Usage: python -m envs.chess.redact_verdicts <staged_traces> <dst>
"""
import re, sys
from pathlib import Path
NEUTRAL = "The puzzle is over. Do not call any more tools; end your reply now."
VERDICT = re.compile(r"Correct! Puzzle solved|That move is not the puzzle solution")
HEAD = re.compile(r"^## \[(\d+)\] (USER|ASSISTANT)\s*$", re.M)
def redact(t):
    heads = list(HEAD.finditer(t))
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(t)
        if h.group(2) == "USER" and VERDICT.search(t[h.end():end]):
            return t[:h.end()] + "\n\n" + NEUTRAL + "\n", "solved" if "Puzzle solved" in t[h.end():end] else "failed"
    return t, None
def main(src, dst):
    dst.mkdir(parents=True, exist_ok=True)
    n, verdicts = 0, {"solved": 0, "failed": 0}
    for f in sorted(src.glob("*.md")):
        out, v = redact(f.read_text())
        (dst / f.name).write_text(out)
        n += 1
        if v: verdicts[v] += 1
    print(f"{n} traces -> {dst}: redacted {verdicts['solved']} solved, {verdicts['failed']} failed")
if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
