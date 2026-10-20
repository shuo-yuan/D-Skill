"""Chess analysis tools: hanging, threats, safety, simulate, board, line.

Each tool runs in-process on the live board and returns text; nothing is
searched or evaluated. run_puzzles calls them through tool tags
(find_queries, execute_tag; documented to the model by TOOL_DOC) and
chess_mcp through MCP.
"""
from __future__ import annotations

import re

import chess

_VAL = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
        chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}

QUERY_RE = re.compile(
    r"<(hanging|safety|simulate|threats|board|line)>(.*?)</\1>", re.S)

# Bare "<hanging>" / "<threats>" also count: these tools take no argument.
BARE_RE = re.compile(r"<(hanging|threats)>")


def find_queries(text: str) -> list:
    """All tool invocations in order, as (name, args) tuples. Bare open
    tags inside a closed pair's span are ignored."""
    closed = list(QUERY_RE.finditer(text))
    spans = [(m.start(), m.end()) for m in closed]
    hits = [(m.start(), m.group(1), m.group(2)) for m in closed]
    for m in BARE_RE.finditer(text):
        if any(a <= m.start() < b for a, b in spans):
            continue
        hits.append((m.start(), m.group(1), ""))
    return [(n, a) for _, n, a in sorted(hits)]

MAX_SAFETY_MOVES = 5

TOOL_DOC = """\
## Analysis tools

You SHOULD verify before committing to a move (up to {K} tool calls \
per move). Strong players check before they move: do not commit a move \
you have not audited unless it is forced.

To use a tool, reply with ONLY one tool tag and nothing else. The \
result comes back as the next message; then use another tool or commit \
your move. Write moves in SAN (Nf3, exd5, O-O) or UCI (g1f3); separate \
multiple moves with commas. These six tools are the ONLY analysis \
available. Every call, including malformed or illegal ones, spends one \
unit of the budget — EXCEPT exact repeats: re-running a query you \
already ran this move returns the cached result free of charge. If a \
reply contains several tool tags, only the LAST one is executed. The \
material count (pawn units: Q=9, R=5, B=3, N=3, P=1) is printed in \
every observation for free — there is no material tool.

### <hanging></hanging>
Lists every piece that is attacked and has NO defender, for both \
sides, in the current position. Takes no input. Pieces are shown as \
piece@square with uppercase = White. Output looks like:
    your side en prise: none
    opponent en prise:  ['N@e5']

### <safety>move</safety>   or   <safety>m1, m2, m3</safety>   (max 5)
Audits candidate move(s) YOU could play now. For each move it plays \
the move on a copy of the board and reports: whether it gives check \
(CHECKMATE or STALEMATE called out explicitly), how many legal replies \
the opponent has, every forcing reply (checks and captures, naming the \
piece captured), attackers vs defenders of the destination square, and \
which of your pieces are left undefended afterwards. Output is one \
block per move, like:
    safety(Qg5):
      gives check: no; opponent legal replies: 40
      forcing replies: Nxf7 (captures pawn), Bxf7+ (captures pawn, check)
      destination g5: attackers 0 vs defenders 0
      your pieces en prise after the move: none

### <threats></threats>
Answers "what is the danger right now?": pretends you passed and lists \
every forcing move the opponent would then have (checks and captures, \
naming the piece captured), plus any that would be immediate \
checkmate. Takes no input. Not available while you are in check. \
Output looks like:
    if you passed, opponent's forcing moves: Qxf7+ (captures pawn, check), Rxd8 (captures rook)
    mate threats: Qh4# (CHECKMATE)

### <board>your_move</board>
Shows the position after YOUR move only — no opponent reply. Input is \
exactly one move. Use it when you need to SEE the board one step \
ahead instead of imagining it: checking what a capture or a mate \
attempt really looks like, or re-verifying a planned second move. \
Output is the board after your move, the material count, your \
undefended pieces, and whether the move gives check (CHECKMATE \
flagged):
    after Qxf7:
    r . b . k . n r
    ... (8x8 board) ...
    material: White 39 - Black 36  (you are up 3)
    your side en prise: ['Q@f7']
    gives check: yes

### <simulate>your_move, reply1, reply2, ...</simulate>
Plays your move, then shows the resulting position for EACH opponent \
reply you list — up to 5 replies, ONE budget charge for the whole \
call. Every reply is simulated independently from the position after \
your move (they are separate what-if lines, not a sequence). Input is \
your move followed by 1-5 comma-separated opponent replies. Only ONE \
candidate move per call — to compare two of your own candidates, make \
two calls. With one reply the output is the board after both moves \
(uppercase = White, rank 8 at top), your undefended pieces, and \
whether you are then in check; with several replies you get one \
labeled block per reply:
    === simulate 1/2: Qg5, reply Nxf7 ===
    after Qg5 Nxf7:
    r . b . k . n r
    ... (8x8 board) ...
    material: White 38 - Black 38  (material level)
    your side en prise: ['r@h8', 'q@g5']
    you are in check: False

    === simulate 2/2: Qg5, reply d5 ===
    after Qg5 d5:
    ... (8x8 board) ...
    your side en prise: ['q@g5']
    you are in check: False
Use one batched call to audit your candidate against ALL the testing \
replies the <safety> block listed (its forcing replies), instead of \
one call per reply.

### <line>your_move, reply, your_move2, ...</line>
Replays a COMPLETE line you have calculated — your moves AND the \
opponent's replies, alternating, 2-6 plies — and shows where it \
really lands: final board, material, your undefended pieces, and \
check/mate status. Every move is supplied by YOU; the tool searches \
nothing — it verifies your plan instead of your imagination. Use it \
before committing the first move of a combination:
    line Qg5 Nxf7 Qxd8:
    ... (8x8 board) ...
    material: White 42 - Black 34  (you are up 8)
    your side en prise: none
    status: no check
If any move in the line is illegal, the error names the failing ply \
and lists the legal moves at that point (budget still spent).

Illegal or malformed calls return an error instead of a result — an \
ambiguous move like Nb3 suggests the exact spellings (Nab3, Ncb3), and \
an illegal opponent reply in <simulate> lists the opponent's actual \
legal replies (in a multi-reply call only that reply's block shows the \
error; the other replies still simulate). Errors still spend budget, \
so copy your own candidate moves exactly from the legal-move list."""


class QueryError(Exception):
    pass


_SAN_RE = re.compile(r"^([KQRBN])?[a-h]?[1-8]?x?([a-h][1-8])")


def _disambig(board: chess.Board, raw: str) -> list[str]:
    m = _SAN_RE.match(raw.strip())
    if not m:
        return []
    piece = m.group(1) or "P"
    dest = chess.parse_square(m.group(2))
    out = []
    for mv in board.legal_moves:
        p = board.piece_at(mv.from_square)
        if mv.to_square == dest and p and p.symbol().upper() == piece:
            out.append(board.san(mv))
    return out


def _mv(board: chess.Board, raw: str) -> chess.Move:
    raw = raw.strip().strip("'\"")
    try:
        return board.parse_san(raw)
    except chess.AmbiguousMoveError:
        sug = _disambig(board, raw)
        raise QueryError(
            f"'{raw}' is ambiguous — did you mean: {', '.join(sug)}?")
    except ValueError:
        pass
    try:
        mv = chess.Move.from_uci(raw.lower())
        if mv in board.legal_moves:
            return mv
    except ValueError:
        pass
    raise QueryError(f"'{raw}' is not a legal move here")


def _enprise(b: chess.Board, color: bool) -> list[str]:
    out = []
    for sq, p in b.piece_map().items():
        if p.color != color or p.piece_type == chess.KING:
            continue
        if b.is_attacked_by(not color, sq) and not b.attackers(color, sq):
            out.append(f"{p.symbol()}@{chess.square_name(sq)}")
    return out


def material_line(board: chess.Board, us: bool) -> str:
    """Side-relative material summary for side `us`."""
    w = sum(_VAL[p.piece_type] for p in board.piece_map().values()
            if p.color)
    bl = sum(_VAL[p.piece_type] for p in board.piece_map().values()
             if not p.color)
    mine = (w - bl) if us else (bl - w)
    rel = ("material level" if mine == 0
           else f"you are up {mine}" if mine > 0
           else f"you are down {-mine}")
    return f"material: White {w} - Black {bl}  ({rel})"


def q_hanging(board: chess.Board) -> str:
    return (f"your side en prise: {_enprise(board, board.turn) or 'none'}\n"
            f"opponent en prise:  "
            f"{_enprise(board, not board.turn) or 'none'}")


def _safety_one(board: chess.Board, raw: str) -> str:
    us = board.turn
    mv = _mv(board, raw)
    san = board.san(mv)
    dest = mv.to_square
    b = board.copy(stack=False)
    b.push(mv)
    gives_chk = b.is_check()
    nreplies = b.legal_moves.count()
    if nreplies == 0:
        status = ("CHECKMATE — opponent has no legal replies"
                  if gives_chk else
                  "STALEMATE — opponent has no legal replies (draw!)")
    else:
        status = (f"gives check: {'yes' if gives_chk else 'no'}; "
                  f"opponent legal replies: {nreplies}")
    forcing = []
    for r in b.legal_moves:
        is_cap, is_chk = b.is_capture(r), b.gives_check(r)
        if is_cap or is_chk:
            parts = []
            if is_cap:
                victim = ("pawn" if b.is_en_passant(r) else
                          chess.piece_name(b.piece_at(r.to_square).piece_type))
                parts.append(f"captures {victim}")
            if is_chk:
                parts.append("check")
            forcing.append(f"{b.san(r)} ({', '.join(parts)})")
    atk = len(b.attackers(not us, dest))
    dfn = len(b.attackers(us, dest))
    ep = _enprise(b, us)
    return (f"safety({san}):\n"
            f"  {status}\n"
            f"  forcing replies: {', '.join(forcing) or 'none'}\n"
            f"  destination {chess.square_name(dest)}: attackers {atk} "
            f"vs defenders {dfn}"
            + ("  [LOSING EXCHANGE RISK]" if atk > dfn else "") + "\n"
            f"  your pieces en prise after the move: {ep or 'none'}")


def q_safety(board: chess.Board, *moves: str) -> str:
    if not moves:
        raise QueryError("safety() needs at least one move")
    if len(moves) > MAX_SAFETY_MOVES:
        raise QueryError(f"safety() takes at most {MAX_SAFETY_MOVES} moves")
    return "\n".join(_safety_one(board, m) for m in moves)


MAX_SIM_REPLIES = 5


def q_simulate(board: chess.Board, move: str, *replies: str) -> str:
    """One candidate against 1..MAX_SIM_REPLIES independent opponent
    replies. With several replies, each gets a labeled block and its own
    error message instead of a QueryError."""
    if not replies:
        raise QueryError("simulate() needs your move and at least one "
                         "opponent reply")
    if len(replies) > MAX_SIM_REPLIES:
        raise QueryError(f"simulate() takes at most {MAX_SIM_REPLIES} "
                         "opponent replies (after your move)")
    us = board.turn
    base = board.copy(stack=False)
    m1 = _mv(base, move)
    s1 = base.san(m1)
    base.push(m1)

    def _legal_str() -> str:
        legal = [base.san(m) for m in base.legal_moves]
        return ", ".join(legal[:24]) + (", ..." if len(legal) > 24 else "")

    def _one(reply: str) -> str:
        b = base.copy(stack=False)
        m2 = _mv(b, reply)
        s2 = b.san(m2)
        b.push(m2)
        return (f"after {s1} {s2}:\n{b}\n"
                f"{material_line(b, us)}\n"
                f"your side en prise: {_enprise(b, us) or 'none'}\n"
                f"you are in check: {b.is_check()}")

    if len(replies) == 1:
        try:
            return _one(replies[0])
        except QueryError as e:
            raise QueryError(f"{e} (after {s1}; opponent's legal replies: "
                             f"{_legal_str() or 'none — game over'})")

    blocks = []
    for i, r in enumerate(replies, 1):
        hdr = f"=== simulate {i}/{len(replies)}: {s1}, reply {r} ==="
        try:
            blocks.append(f"{hdr}\n{_one(r)}")
        except QueryError as e:
            blocks.append(f"{hdr}\nerror: {e} (after {s1}; opponent's "
                          f"legal replies: "
                          f"{_legal_str() or 'none — game over'})")
    return "\n\n".join(blocks)


def q_board(board: chess.Board, move: str) -> str:
    """The position after YOUR move only (no opponent reply)."""
    us = board.turn
    b = board.copy(stack=False)
    m1 = _mv(b, move)
    s1 = b.san(m1)
    b.push(m1)
    chk = ("yes (CHECKMATE — opponent has no legal replies)"
           if b.is_checkmate() else ("yes" if b.is_check() else "no"))
    return (f"after {s1}:\n{b}\n"
            f"{material_line(b, us)}\n"
            f"your side en prise: {_enprise(b, us) or 'none'}\n"
            f"gives check: {chk}")


MAX_LINE_PLIES = 6


def q_line(board: chess.Board, *moves: str) -> str:
    """Replay a model-supplied line of 2..MAX_LINE_PLIES alternating plies
    and show where it lands."""
    if len(moves) < 2:
        raise QueryError("line() needs at least 2 moves: yours, then "
                         "the opponent's reply, alternating")
    if len(moves) > MAX_LINE_PLIES:
        raise QueryError(f"line() takes at most {MAX_LINE_PLIES} plies")
    us = board.turn
    b = board.copy(stack=False)
    sans = []
    for i, mv in enumerate(moves, 1):
        side = "you" if b.turn == us else "opponent"
        try:
            m = _mv(b, mv)
        except QueryError as e:
            legal = [b.san(x) for x in b.legal_moves]
            shown = ", ".join(legal[:24]) + (", ..." if len(legal) > 24 else "")
            played = " ".join(sans) or "(line start)"
            raise QueryError(
                f"ply {i} ({mv}, {side}): {e} (after {played}; "
                f"legal here: {shown or 'none — game over'})")
        sans.append(b.san(m))
        b.push(m)
    status = ("CHECKMATE — the line ends in mate" if b.is_checkmate()
              else "STALEMATE — the line ends in stalemate"
              if b.is_stalemate()
              else ("you are in check" if b.turn == us
                    else "opponent is in check") if b.is_check()
              else "no check")
    return (f"line {' '.join(sans)}:\n{b}\n"
            f"{material_line(b, us)}\n"
            f"your side en prise: {_enprise(b, us) or 'none'}\n"
            f"status: {status}")


def q_threats(board: chess.Board) -> str:
    if board.is_check():
        return ("you are IN CHECK right now — <threats> is not "
                "available while in check; resolve the check first")
    b = board.copy(stack=False)
    b.push(chess.Move.null())
    forcing, mates = [], []
    for r in b.legal_moves:
        is_cap, is_chk = b.is_capture(r), b.gives_check(r)
        if not (is_cap or is_chk):
            continue
        parts = []
        if is_cap:
            victim = ("pawn" if b.is_en_passant(r) else
                      chess.piece_name(b.piece_at(r.to_square).piece_type))
            parts.append(f"captures {victim}")
        if is_chk:
            parts.append("check")
            b2 = b.copy(stack=False)
            b2.push(r)
            if b2.is_checkmate():
                mates.append(b.san(r))
        forcing.append(f"{b.san(r)} ({', '.join(parts)})")
    return (f"if you passed, opponent's forcing moves: "
            f"{', '.join(forcing) or 'none'}\n"
            f"mate threats: "
            f"{', '.join(m + ' (CHECKMATE)' for m in mates) or 'none'}")


_DISPATCH = {"hanging": (q_hanging, 0, 0),
             "safety": (q_safety, 1, MAX_SAFETY_MOVES),
             "simulate": (q_simulate, 2, 1 + MAX_SIM_REPLIES),
             "threats": (q_threats, 0, 0),
             "board": (q_board, 1, 1),
             "line": (q_line, 2, MAX_LINE_PLIES)}


def execute_tag(board: chess.Board, name: str, inner: str) -> str:
    """Run one tool tag. Raises QueryError on any problem."""
    name = name.lower()
    if name not in _DISPATCH:
        raise QueryError(f"unknown tool '{name}'; available: "
                         f"{', '.join(_DISPATCH)}")
    fn, lo, hi = _DISPATCH[name]
    args = [a.strip().strip("'\"") for a in inner.split(",")] \
        if inner.strip() else []
    args = [a for a in args if a]
    if not (lo <= len(args) <= hi):
        raise QueryError(f"<{name}> takes {lo}"
                         + (f"-{hi}" if hi != lo else "")
                         + f" argument(s), got {len(args)}")
    return fn(board, *args)
