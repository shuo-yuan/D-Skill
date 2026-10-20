"""Evaluate a model on Lichess tactics puzzles with the chess_query tools.

One conversation per puzzle; after each correct non-final move the
scripted opponent reply is played. Prints strict (full-line) and
first-move accuracy per rating band and a 50%-solve rating estimate.
Default set: 200 puzzles, 4 rating bands x 50 (oneMove/short, RD<80,
NbPlays>200, Pop>70).

Usage:
  python -m envs.chess.run_puzzles --model qwen3.6-35b-a3b --run-tag qwpz \
      [--tools 10] [--skill-file F] [--slots 16]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import dskill  # noqa: E402,F401  (puts third_party/trace2skill on sys.path)

import chess                                                # noqa: E402

from react_agent.models import Message                      # noqa: E402
from dskill.llm.client import make_client                   # noqa: E402
TOOLS_SYSTEM = """\
You are a strong chess player. You will be shown a chess position and \
must choose one move.

{TOOL_DOC}
## Committing your move
1. Optionally start with one line: PLAN: <your plan in at most 25 \
words>. It will be shown back to you on your next move.
2. Output EXACTLY ONE move from the legal-move list, wrapped in action \
tags, in SAN (e.g. <action>Nf3</action>) or UCI (<action>g1f3</action>) \
notation. Output nothing after the action tag. Never mix a tool tag \
and an action tag in the same reply.
"""

def _board_obs(board: chess.Board, hist_n: int, plan_note: str) -> str:
    # reconstruct SAN history from the move stack
    stack = board.move_stack[:]
    replay = board.copy(stack=True)
    for _ in range(len(stack)):
        replay.pop()
    san_hist = []
    for mv in stack:
        san_hist.append(replay.san(mv))
        replay.push(mv)
    last = san_hist[-hist_n:] if hist_n else []
    # rendered on the agent's turn, so the last ply is the opponent's
    labeled = [f"{s} ({'opponent' if (len(last) - i) % 2 == 1 else 'you'})"
               for i, s in enumerate(last)]
    legal = sorted(board.san(m) for m in board.legal_moves)
    rep = board.is_repetition(2)
    parts = [
        f"Position (FEN): {board.fen()}",
        f"Board (uppercase = White, lowercase = Black, rank 8 at top):"
        f"\n{board}",
        f"You are playing: {'White' if board.turn else 'Black'}",
        chess_query.material_line(board, board.turn).capitalize(),
        f"Last moves (oldest first): "
        f"{', '.join(labeled) if labeled else '(game start)'}",
        f"Halfmove clock: {board.halfmove_clock}"
        + ("  [WARNING: position repeated before]" if rep else ""),
        f"Legal moves: {', '.join(legal)}",
    ]
    if plan_note:
        parts.append(f"Your note from last move: {plan_note}")
    parts.append("Choose your move now.")
    return "\n\n".join(parts)

def _parse_action(resp: str, board: chess.Board):
    m = re.findall(r"<action>\s*(.*?)\s*</action>", resp, re.S)
    if not m:
        return None
    raw = m[-1].strip().rstrip(".")
    try:
        return board.parse_san(raw)
    except ValueError:
        pass
    try:
        mv = chess.Move.from_uci(raw.lower())
        if mv in board.legal_moves:
            return mv
    except ValueError:
        pass
    return None
from envs.chess import chess_query                              # noqa: E402

PUZZLES = "envs/chess/data/lichess_puzzles/puzzles_eval_400_2000.json"
_RES_LOCK = threading.Lock()

PUZZLE_NOTE = ("\n\nThis is a tactics puzzle: there is a clearly best "
               "move in this position. Find it.")


def solve_puzzle(pz, model, effort, tools, skill):
    t0 = time.time()
    board = chess.Board(pz["FEN"])
    moves = pz["Moves"].split()
    board.push(chess.Move.from_uci(moves[0]))       # opponent setup move
    solver_line = moves[1:]
    base_sys = TOOLS_SYSTEM.format(
        TOOL_DOC=chess_query.TOOL_DOC.format(K=tools))
    system = base_sys + (f"\n## Skill\n{skill.strip()}\n" if skill.strip()
                         else "")
    # HD_TASK_EXTRA: optional extra system text (e.g. assets/tool_trust.md)
    _extra = os.environ.get("HD_TASK_EXTRA", "")
    if _extra.strip():
        system += "\n" + _extra.strip() + "\n"
    client = make_client(model, effort)
    usage = {"prompt_tokens": 0, "completion_tokens": 0,
             "reasoning_tokens": 0, "cached_tokens": 0, "calls": 0}
    first_ok, solved, ply_ok = None, True, 0
    turns = []
    # one conversation per puzzle; budget and query cache reset per move
    msgs = [Message(role="system", content=system)]
    for i in range(0, len(solver_line), 2):
        expected = solver_line[i]
        obs = _board_obs(board, 6, "") + PUZZLE_NOTE
        if i > 0:
            obs += ("\n(Note: tool results above refer to the previous "
                    "position — re-verify anything you rely on before "
                    "committing.)")
        turns.append(("USER", obs))
        msgs.append(Message(role="user", content=obs))
        resp, ntool, nudges = "", 0, 0
        qcache = {}          # (name, normalized args) -> result, per move
        while True:
            try:
                out = client.chat(msgs, return_reasoning=True)
                resp, rzn = out if isinstance(out, tuple) else (out or "", "")
                resp = (resp or "").strip()
                u = getattr(client, "last_usage", None)
                usage["calls"] += 1
                if u:
                    for k in ("prompt_tokens", "completion_tokens",
                              "reasoning_tokens", "cached_tokens"):
                        usage[k] += u.get(k, 0)
            except Exception as e:                          # noqa: BLE001
                resp = f"(error: {e})"
                turns.append(("ASSISTANT", resp))
                break
            turns.append(("ASSISTANT",
                          (f"(reasoning)\n{rzn}\n(final)\n{resp}"
                           if rzn.strip() else resp)))
            # neither a tag nor a move: nudge up to twice, free of budget
            if "<action>" not in resp and not chess_query.find_queries(resp):
                if nudges < 2:
                    nudges += 1
                    nmsg = ("Your reply contained no tool tag and no "
                            "move. Reply now with either ONE tool tag "
                            "(e.g. <safety>Nf3</safety>) or your final "
                            "move in <action></action> tags.")
                    turns.append(("USER", nmsg))
                    msgs.append(Message(role="assistant", content=resp))
                    msgs.append(Message(role="user", content=nmsg))
                    continue
            if "<action>" not in resp:
                # the last tag wins; prose may quote hypothetical tags
                tags = chess_query.find_queries(resp)
                mq = tags[-1] if tags else None
                qkey = (mq[0],
                        re.sub(r"\s+", "", mq[1])) if mq else None
                if mq and qkey in qcache:
                    # exact repeat: serve from cache, charge nothing
                    tmsg = (f"Query result (repeat — cached, not "
                            f"charged; {ntool}/{tools} used) for "
                            f"<{mq[0]}>{mq[1].strip()}"
                            f"</{mq[0]}>:\n{qcache[qkey]}")
                    turns.append(("USER", tmsg))
                    msgs.append(Message(role="assistant", content=resp))
                    msgs.append(Message(role="user", content=tmsg))
                    continue
                if mq and ntool < tools:
                    ntool += 1
                    try:
                        tout = chess_query.execute_tag(
                            board, mq[0], mq[1])
                    except chess_query.QueryError as qe:
                        tout = f"Query error: {qe}"
                    qcache[qkey] = tout
                    tmsg = (f"Query result ({ntool}/{tools}) for "
                            f"<{mq[0]}>{mq[1].strip()}"
                            f"</{mq[0]}>:\n{tout}")
                    if ntool >= tools:
                        tmsg += ("\n\nQuery budget exhausted. Reply with "
                                 "your move now.")
                    elif tools - ntool <= 5:
                        tmsg += (f"\n\n[{tools - ntool} tool calls left "
                                 "this move. Use them to COMPARE your "
                                 "audited candidates: pick the line with "
                                 "the largest verified gain, never a "
                                 "move whose audit showed danger (en "
                                 "prise, strong checks). Running out of "
                                 "budget is fine — committing an "
                                 "unaudited or refuted move is not.]")
                    turns.append(("USER", tmsg))
                    msgs.append(Message(role="assistant", content=resp))
                    msgs.append(Message(role="user", content=tmsg))
                    continue
            break
        msgs.append(Message(role="assistant", content=resp))
        mv = _parse_action(resp, board)
        exp_mv = chess.Move.from_uci(expected)
        # any alternate mate counts as correct (lichess rule)
        ok = (mv == exp_mv)
        if not ok and mv is not None:
            board.push(mv)
            ok = board.is_checkmate()
            board.pop()
        if first_ok is None:
            first_ok = bool(ok and i == 0)
        if not ok:
            solved = False
            break
        ply_ok += 1
        board.push(exp_mv)
        if i + 1 < len(solver_line):
            board.push(chess.Move.from_uci(solver_line[i + 1]))
    return {"puzzle": pz["PuzzleId"], "rating": int(pz["Rating"]),
            "band": pz["_band"], "themes": pz["Themes"],
            "solved": int(solved), "first_move_ok": int(bool(first_ok)),
            "solver_moves": (len(solver_line) + 1) // 2,
            "moves_correct": ply_ok, "usage": usage,
            "wall_s": round(time.time() - t0, 1)}, turns


def main():
    from dskill.llm.pin_provider import install as _pin
    _pin()
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--effort", default=None)
    ap.add_argument("--tools", type=int, nargs="?", const=10, default=10)
    ap.add_argument("--skill-file", default=None)
    ap.add_argument("--puzzles", default=PUZZLES)
    ap.add_argument("--run-tag", required=True)
    ap.add_argument("--slots", type=int, default=16)
    args = ap.parse_args()
    if args.tools < 1:
        ap.error("--tools must be >= 1 (the tool-free protocol was removed)")

    skill = ""
    if args.skill_file:
        skill = Path(args.skill_file).expanduser().read_text()
        if skill.startswith("---"):
            parts = skill.split("---", 2)
            if len(parts) == 3:
                skill = parts[2]
    puzzles = json.load(open(args.puzzles))
    base = Path("runs") / f"puzzles_{args.model}_{args.run_tag}"
    logdir = base / "logs"
    logdir.mkdir(parents=True, exist_ok=True)
    resfile = base / "results.jsonl"
    done = {json.loads(l)["puzzle"] for l in open(resfile)} \
        if resfile.exists() else set()
    jobs = [p for p in puzzles if p["PuzzleId"] not in done]
    print(f"puzzles {args.model} [{args.run_tag}]: {len(done)} done, "
          f"{len(jobs)} to run, tools={args.tools}", flush=True)

    def work(pz):
        rec, turns = solve_puzzle(pz, args.model, args.effort, args.tools,
                                  skill)
        md = [f"# Puzzle {pz['PuzzleId']} ({pz['Rating']})\n"]
        for k, (role, text) in enumerate(turns, 1):
            md.append(f"## [{k}] {role}\n\n{text}\n")
        (logdir / f"puzzle_{pz['PuzzleId']}.md").write_text("\n".join(md))
        return rec

    k = len(done)
    with ThreadPoolExecutor(max_workers=args.slots) as ex:
        futs = [ex.submit(work, p) for p in jobs]
        for f in as_completed(futs):
            try:
                rec = f.result()
            except Exception as e:                          # noqa: BLE001
                print(f"[puzzle crashed: {e!r}]", flush=True)
                continue
            with _RES_LOCK:
                with open(resfile, "a") as fh:
                    fh.write(json.dumps(rec) + "\n")
                k += 1
                if k % 20 == 0:
                    print(f"[{k}/{len(puzzles)}]", flush=True)

    rs = [json.loads(l) for l in open(resfile)]
    bands = sorted({r["band"] for r in rs})
    print(f"FINAL {args.model} [{args.run_tag}] n={len(rs)}")
    for b in bands:
        sub = [r for r in rs if r["band"] == b]
        print(f"  {b}: strict {sum(r['solved'] for r in sub)}/{len(sub)}  "
              f"first-move {sum(r['first_move_ok'] for r in sub)}/{len(sub)}")
    # logistic 50% crossing on strict solves
    try:
        import math
        xs = [r["rating"] for r in rs]; ys = [r["solved"] for r in rs]
        a, bcoef = 0.0, 0.0
        for _ in range(500):                      # simple gradient fit
            ga = gb = 0.0
            for x, y in zip(xs, ys):
                p = 1 / (1 + math.exp(-(a + bcoef * (x - 1200) / 400)))
                ga += (y - p); gb += (y - p) * (x - 1200) / 400
            a += 0.01 * ga / len(xs); bcoef += 0.01 * gb / len(xs)
        if bcoef < 0:
            est = 1200 + 400 * (-a / bcoef)
            print(f"  puzzle-rating estimate (50% strict): {est:.0f}")
    except Exception:                                       # noqa: BLE001
        pass


if __name__ == "__main__":
    main()
