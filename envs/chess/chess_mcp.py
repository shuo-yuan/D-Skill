"""One chess puzzle episode as a dependency-free MCP stdio server.

Exposes the six chess_query analysis tools plus `play`. Moves are scored
here (the solver move, or any immediate checkmate) and the result row is
appended to HD_MCP_OUT.

Environment:
  HD_MCP_FEN     initial FEN (before the setup move)
  HD_MCP_MOVES   space-separated UCI: setup move + solver line
  HD_MCP_PID     puzzle id          HD_MCP_RATING  rating (optional)
  HD_MCP_OUT     results.jsonl path
  HD_MCP_BUDGET  analysis calls per move (default 10)
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import chess                                                 # noqa: E402
from envs.chess import chess_query                               # noqa: E402

T0 = time.time()
BOARD = chess.Board(os.environ["HD_MCP_FEN"])
MOVES = os.environ["HD_MCP_MOVES"].split()
BOARD.push(chess.Move.from_uci(MOVES[0]))       # opponent setup move
SOLVER = MOVES[1:]
BUDGET = int(os.environ.get("HD_MCP_BUDGET", "10"))
ST = {"i": 0, "q": 0, "nq": 0, "first_ok": None, "done": False,
      "solved": True, "ply_ok": 0}


def obs() -> str:
    b = BOARD
    legal = sorted(b.san(m) for m in b.legal_moves)
    stack = b.move_stack[:]
    replay = b.copy(stack=True)
    for _ in range(len(stack)):
        replay.pop()
    hist = []
    for mv in stack:
        hist.append(replay.san(mv))
        replay.push(mv)
    last = hist[-6:]
    lab = [f"{s} ({'opponent' if (len(last) - i) % 2 == 1 else 'you'})"
           for i, s in enumerate(last)]
    return (f"Position (FEN): {b.fen()}\n\n"
            f"Board (uppercase = White, lowercase = Black, rank 8 at "
            f"top):\n{b}\n\n"
            f"You are playing: {'White' if b.turn else 'Black'}\n\n"
            f"{chess_query.material_line(b, b.turn).capitalize()}\n\n"
            f"Last moves (oldest first): {', '.join(lab)}\n\n"
            f"Legal moves: {', '.join(legal)}")


def write_result(status: str) -> None:
    if ST["done"]:
        return
    ST["done"] = True
    row = {"puzzle": os.environ.get("HD_MCP_PID", "?"),
           "rating": int(os.environ.get("HD_MCP_RATING", "0")),
           "solved": int(ST["solved"] and status == "solved"),
           "first_move_ok": int(bool(ST["first_ok"])),
           "solver_moves": (len(SOLVER) + 1) // 2,
           "moves_correct": ST["ply_ok"], "n_queries": ST["nq"],
           "status": status, "wall_s": round(time.time() - T0, 1)}
    out = os.environ.get("HD_MCP_OUT")
    if out:
        with open(out, "a") as fh:
            fh.write(json.dumps(row) + "\n")


def _split(s: str) -> list:
    return [x for x in s.replace(",", " ").split() if x]


def q_guard(fn):
    if ST["done"]:
        return "The puzzle is over. No further analysis is possible."
    if ST["q"] >= BUDGET:
        return (f"Analysis budget for this move is exhausted "
                f"({BUDGET} calls). Commit your move with the "
                f"`play` tool.")
    ST["q"] += 1
    ST["nq"] += 1
    try:
        return fn()
    except Exception as e:                                   # noqa: BLE001
        return f"(query error: {e})"


def t_play(move: str) -> str:
    if ST["done"]:
        return "The puzzle is already over."
    exp = SOLVER[ST["i"]]
    try:
        mv = BOARD.parse_san(move.strip())
    except ValueError:
        try:
            mv = chess.Move.from_uci(move.strip().lower())
            if mv not in BOARD.legal_moves:
                raise ValueError
        except ValueError:
            return (f"'{move}' is not a legal move here. Pick a move "
                    f"from the legal-move list and call play again.")
    exp_mv = chess.Move.from_uci(exp)
    ok = (mv == exp_mv)
    if not ok:
        BOARD.push(mv)
        ok = BOARD.is_checkmate()
        BOARD.pop()
    if ST["first_ok"] is None:
        ST["first_ok"] = bool(ok and ST["i"] == 0)
    if not ok:
        ST["solved"] = False
        write_result("failed")
        return ("That move is not the puzzle solution. The puzzle is "
                "over (failed). Do not call any more tools; end your "
                "reply now.")
    ST["ply_ok"] += 1
    BOARD.push(exp_mv)
    ST["i"] += 1
    if ST["i"] < len(SOLVER):
        BOARD.push(chess.Move.from_uci(SOLVER[ST["i"]]))
        ST["i"] += 1
    if ST["i"] >= len(SOLVER):
        write_result("solved")
        return ("Correct! Puzzle solved. Do not call any more tools; "
                "end your reply now.")
    ST["q"] = 0
    return ("Correct. The opponent has replied — new position:\n\n"
            + obs())


TOOLS = [
    {"name": "hanging",
     "description": "List undefended / under-defended pieces for both "
                    "sides in the current position.",
     "inputSchema": {"type": "object", "properties": {"why": {"type": "string", "description": "one line, max 20 words: saw=<piece/square/threat/motif you are reacting to> | test=<what this call should confirm or rule out>"}}, "required": ["why"]}},
    {"name": "threats",
     "description": "What the opponent threatens if you pass: checks "
                    "and captures they could play next.",
     "inputSchema": {"type": "object", "properties": {"why": {"type": "string", "description": "one line, max 20 words: saw=<piece/square/threat/motif you are reacting to> | test=<what this call should confirm or rule out>"}}, "required": ["why"]}},
    {"name": "safety",
     "description": "Audit candidate moves: check status, opponent "
                    "reply count, forcing replies, destination "
                    "attackers vs defenders, your pieces en prise "
                    "after the move. Batch several moves in one call.",
     "inputSchema": {"type": "object", "properties": {
         "moves": {"type": "string",
                   "description": "comma-separated SAN moves"},
         "why": {"type": "string", "description": "one line, max 20 words: saw=<piece/square/threat/motif you are reacting to> | test=<what this call should confirm or rule out>"}},
         "required": ["moves", "why"]}},
    {"name": "simulate",
     "description": "Play one candidate against up to 5 opponent "
                    "replies (independent what-ifs); shows each "
                    "resulting position with material and en-prise "
                    "lists.",
     "inputSchema": {"type": "object", "properties": {
         "candidate": {"type": "string"},
         "replies": {"type": "string",
                     "description": "comma-separated SAN replies"},
         "why": {"type": "string", "description": "one line, max 20 words: saw=<piece/square/threat/motif you are reacting to> | test=<what this call should confirm or rule out>"}},
         "required": ["candidate", "replies", "why"]}},
    {"name": "board",
     "description": "Preview the position after ONE of your moves: "
                    "board, material, en prise, check status.",
     "inputSchema": {"type": "object", "properties": {
         "move": {"type": "string"}, "why": {"type": "string", "description": "one line, max 20 words: saw=<piece/square/threat/motif you are reacting to> | test=<what this call should confirm or rule out>"}},
         "required": ["move", "why"]}},
    {"name": "line",
     "description": "Replay a full calculated line (2-6 plies, your "
                    "moves and opponent replies alternating) and show "
                    "the final position, material, and "
                    "check/checkmate/stalemate status.",
     "inputSchema": {"type": "object", "properties": {
         "moves": {"type": "string",
                   "description": "comma-separated SAN, alternating "
                                  "sides, starting with your move"},
         "why": {"type": "string", "description": "one line, max 20 words: saw=<piece/square/threat/motif you are reacting to> | test=<what this call should confirm or rule out>"}},
         "required": ["moves", "why"]}},
    {"name": "play",
     "description": "Commit your move. This is final: a wrong move "
                    "ends the puzzle as failed. On a correct move the "
                    "opponent replies and you get the new position.",
     "inputSchema": {"type": "object", "properties": {
         "move": {"type": "string"}, "why": {"type": "string", "description": "one line, max 20 words: saw=<piece/square/threat/motif you are reacting to> | test=<what this call should confirm or rule out>"}},
         "required": ["move", "why"]}},
]


def dispatch(name: str, a: dict) -> str:
    if name == "play":
        return t_play(a.get("move", ""))
    if name == "hanging":
        return q_guard(lambda: chess_query.q_hanging(BOARD))
    if name == "threats":
        return q_guard(lambda: chess_query.q_threats(BOARD))
    if name == "safety":
        return q_guard(lambda: chess_query.q_safety(
            BOARD, *_split(a.get("moves", ""))))
    if name == "simulate":
        return q_guard(lambda: chess_query.q_simulate(
            BOARD, a.get("candidate", ""), *_split(a.get("replies", ""))))
    if name == "board":
        return q_guard(lambda: chess_query.q_board(BOARD, a.get("move", "")))
    if name == "line":
        return q_guard(lambda: chess_query.q_line(
            BOARD, *_split(a.get("moves", ""))))
    return f"unknown tool {name}"


def main() -> None:
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            req = json.loads(raw)
        except json.JSONDecodeError:
            continue
        rid = req.get("id")
        method = req.get("method", "")
        if method == "initialize":
            resp = {"protocolVersion":
                    req["params"].get("protocolVersion", "2025-06-18"),
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "chess", "version": "1.0"}}
        elif method == "tools/list":
            resp = {"tools": TOOLS}
        elif method == "tools/call":
            text = dispatch(req["params"]["name"],
                            req["params"].get("arguments", {}) or {})
            resp = {"content": [{"type": "text", "text": text}]}
        elif rid is None:                     # notification -> ignore
            continue
        elif method == "ping":
            resp = {}
        else:
            sys.stdout.write(json.dumps(
                {"jsonrpc": "2.0", "id": rid,
                 "error": {"code": -32601,
                           "message": f"unknown {method}"}}) + "\n")
            sys.stdout.flush()
            continue
        sys.stdout.write(json.dumps(
            {"jsonrpc": "2.0", "id": rid, "result": resp}) + "\n")
        sys.stdout.flush()
    write_result("abandoned")                 # stdin EOF, episode not done


if __name__ == "__main__":
    main()
