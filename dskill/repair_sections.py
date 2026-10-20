"""Merge duplicate `## ` sections of a SKILL.md in place.

Same-title sections are merged in first-seen order and repeated paragraphs
(first 200 characters, whitespace-normalized) are dropped. Prints the number
of sections after the merge.

Usage: python -m dskill.repair_sections <path/to/SKILL.md>
"""
import re
import sys


def main(p):
    t=open(p).read()
    head, rest = t.split("\n## ", 1)
    secs=[]
    for chunk in rest.split("\n## "):
        title, _, body = chunk.partition("\n")
        secs.append((title.strip(), body))
    merged={}; order=[]
    for title, body in secs:
        if title not in merged: merged[title]=[]; order.append(title)
        merged[title].append(body.strip("\n"))
    out=[head.rstrip("\n")]
    for title in order:
        paras=[]; seen=set()
        for body in merged[title]:
            for para in body.split("\n\n"):
                key=re.sub(r"\s+"," ",para.strip())[:200]
                if key and key not in seen: seen.add(key); paras.append(para.rstrip())
        out.append("## "+title+"\n\n"+"\n\n".join(paras).strip("\n"))
    new="\n\n".join(out)+"\n"
    open(p,"w").write(new)
    print(len(re.findall(r"^## ", new, re.M)))


if __name__ == "__main__":
    main(sys.argv[1])
