"""Convert Claude Code episode transcripts into the staged trace format
the analyst reads (the `## [k] ROLE` layout of run_puzzles' episode logs).

Each session jsonl is matched to its puzzle by the post-setup FEN. Chess
MCP calls become tool tags with their results; other tool calls are dropped.

Usage:
  python -m envs.chess.cc_trace_convert \
      --project-dir ~/.claude/projects/<munged-run-dir> \
      --puzzles envs/chess/data/lichess_puzzles/puzzles_train_cc100.json \
      --out runs/staged_cc100_student [--budget 10]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import chess                                                 # noqa: E402

TAGMAP = {"hanging": lambda a: "",
          "threats": lambda a: "",
          "safety": lambda a: a.get("moves", ""),
          "simulate": lambda a: ", ".join(
              x for x in (a.get("candidate", ""),
                          a.get("replies", "")) if x),
          "board": lambda a: a.get("move", ""),
          "line": lambda a: a.get("moves", "")}


def fen_index(puzzles):
    idx = {}
    for p in puzzles:
        b = chess.Board(p["FEN"])
        b.push(chess.Move.from_uci(p["Moves"].split()[0]))
        idx[b.fen()] = p
    return idx


def convert_session(path, fenidx, budget):
    lines = [json.loads(l) for l in open(path) if l.strip()]
    # streaming repeats a message id with growing content: keep the longest
    best = {}
    order = []
    for j in lines:
        msg = j.get("message") or {}
        if msg.get("role") != "assistant":
            continue
        mid = msg.get("id") or f"anon{len(order)}"
        c = msg.get("content") or []
        if mid not in best:
            order.append(mid)
            best[mid] = c
        elif len(c) >= len(best[mid]):
            best[mid] = c
    blocks = []
    emitted_asst = set()
    seen_results = set()
    for j in lines:
        msg = j.get("message") or {}
        role = msg.get("role")
        if role == "assistant":
            mid = msg.get("id") or ""
            if mid in emitted_asst or mid not in best:
                continue
            emitted_asst.add(mid)
            blocks.append(("asst", best[mid]))
        elif role == "user":
            c = msg.get("content")
            if isinstance(c, str):
                blocks.append(("user_text", c))
            else:
                fresh = []
                for blk in (c or []):
                    if (isinstance(blk, dict)
                            and blk.get("type") == "tool_result"):
                        tid = blk.get("tool_use_id")
                        if tid in seen_results:
                            continue
                        seen_results.add(tid)
                    fresh.append(blk)
                if fresh:
                    blocks.append(("user_blocks", fresh))
    pz = None
    for kind, c in blocks:
        if kind == "user_text" and "Position (FEN):" in c:
            fen = c.split("Position (FEN):")[1].split("\n")[0].strip()
            pz = fenidx.get(fen)
            break
    if pz is None:
        return None, None
    # id -> tag call rendering, for matching tool_results
    calls = {}
    out = [f"# Puzzle {pz['PuzzleId']} ({pz['Rating']})\n"]
    k = 0
    qn = 0

    def emit(role, text):
        nonlocal k
        k += 1
        out.append(f"## [{k}] {role}\n\n{text}\n")

    for kind, c in blocks:
        if kind == "user_text":
            emit("USER", c.strip())
            continue
        if kind == "asst":
            parts = []
            for blk in c:
                if not isinstance(blk, dict):
                    continue
                t = blk.get("type")
                if t == "text" and blk.get("text", "").strip():
                    parts.append(blk["text"].strip())
                elif t == "tool_use":
                    name = blk.get("name", "")
                    if not name.startswith("mcp__chess__"):
                        calls[blk.get("id")] = None      # ToolSearch etc.
                        continue
                    short = name.replace("mcp__chess__", "")
                    a = blk.get("input") or {}
                    if short not in TAGMAP and short != "play":
                        calls[blk.get("id")] = None
                        continue
                    if short == "play":
                        tag = f"<action>{a.get('move', '')}</action>"
                        calls[blk.get("id")] = ("play", tag)
                    else:
                        tag = (f"<{short}>{TAGMAP[short](a)}</{short}>"
                               if TAGMAP[short](a)
                               else f"<{short}>")
                        calls[blk.get("id")] = (short, tag)
                    why = (a.get("why") or "").strip()
                    if why:
                        parts.append(f"WHY: {why}")
                    parts.append(("PLAY: " if short == "play"
                                  else "CALL: ") + tag)
            if parts:
                emit("ASSISTANT", "\n".join(parts))
            continue
        # user_blocks: tool_results (and possibly text)
        for blk in c:
            if not isinstance(blk, dict):
                continue
            if blk.get("type") == "text" and blk.get("text", "").strip():
                emit("USER", blk["text"].strip())
                continue
            if blk.get("type") != "tool_result":
                continue
            ref = calls.get(blk.get("tool_use_id"))
            if ref is None:
                continue                       # ToolSearch result
            body = blk.get("content")
            if isinstance(body, list):
                body = "\n".join(x.get("text", "") for x in body
                                 if isinstance(x, dict))
            body = (body or "").strip()
            short, tag = ref
            if short == "play":
                qn = 0
                emit("USER", body)
            else:
                qn += 1
                emit("USER",
                     f"Query result ({qn}/{budget}) for {tag}:\n{body}")
    return pz["PuzzleId"], "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-dir", required=True)
    ap.add_argument("--puzzles", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--budget", type=int, default=10)
    args = ap.parse_args()
    fenidx = fen_index(json.load(open(args.puzzles)))
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    n = 0
    degenerate = []
    bymd = {}
    pdir = Path(args.project_dir).expanduser()
    for f in sorted(pdir.glob("*.jsonl")):
        pid, md = convert_session(f, fenidx, args.budget)
        if pid is None:
            continue
        # several sessions per puzzle (rate-limit reruns): keep the longest
        if pid in bymd and len(bymd[pid]) >= len(md):
            continue
        bymd[pid] = md
    for pid, md in bymd.items():
        (outdir / f"puzzle_{pid}.md").write_text(md)
        n += 1
        if "ASSISTANT" not in md or "<action>" not in md:
            degenerate.append(pid)
    print(f"converted {n} episodes -> {outdir}")
    print(f"degenerate (no assistant turn or no action): "
          f"{len(degenerate)} {degenerate[:8]}")


if __name__ == "__main__":
    main()
