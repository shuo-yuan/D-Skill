"""Stage ALFWorld teacher traces for the difference analyst.

- USER turns: remove the '## Skill Knowledge' block, so the analyst does not see the teacher's skill.
- ASSISTANT turns: drop the (reasoning)/(final) wrappers and <think> blocks; keep only PLAN lines and action tags.

Usage: python -m envs.alfworld.strip_teacher_traces <src_logs> <dst>
"""
import re, sys
from pathlib import Path
TAG = re.compile(r"<(material|hanging|safety|simulate|threats)>.*?</\1>|<action>.*?</action>", re.S)
PLAN = re.compile(r"^PLAN:.*$", re.M)
def strip_assistant(text):
    m = re.match(r"\(reasoning\)\n.*?\n\(final\)\n(.*)", text, re.S)
    if m: text = m.group(1)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    keep = [p.group(0) for p in PLAN.finditer(text)] + [t.group(0) for t in TAG.finditer(text)]
    return "\n".join(keep) if keep else "(no action)"
def strip_user(text):
    i = text.find("## Skill Knowledge")
    if i < 0: return text
    j = text.find("You are an expert agent operating", i)
    if j < 0: return text
    return text[:i] + text[j:]
def main(src, dst):
    dst.mkdir(parents=True, exist_ok=True)
    n = skill_removed = 0
    for f in sorted(src.glob("*.md")):
        t = f.read_text(errors="replace")
        parts = re.split(r"(^## \[\d+\] (?:USER|ASSISTANT)\s*$)", t, flags=re.M)
        out = [parts[0]]; i = 1
        while i < len(parts):
            hdr, body = parts[i], parts[i+1] if i+1 < len(parts) else ""
            if "ASSISTANT" in hdr:
                body = "\n\n" + strip_assistant(body.strip()) + "\n\n"
            elif "USER" in hdr and "## Skill Knowledge" in body:
                body = "\n\n" + strip_user(body).strip() + "\n\n"; skill_removed += 1
            out.append(hdr); out.append(body)
            i += 2
        (dst / f.name).write_text("".join(out)); n += 1
    print(f"staged {n} logs, skill blocks removed from {skill_removed} turns")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
