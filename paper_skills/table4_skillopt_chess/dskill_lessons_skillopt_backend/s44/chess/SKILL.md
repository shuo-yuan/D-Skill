## When NOT to Analyze: Fast Paths and Stopping Rules

Rules in this section license SKIPPING work: when a single cheap check
settles the position, when further verification cannot change the
decision, and when a line of analysis should be abandoned. Every entry
must name (a) the exact trigger that makes the shortcut safe and
(b) the condition under which the shortcut must NOT be taken. A rule
without both parts does not belong here.

**Spiral breaker.** Trigger: you re-derive the same fact (FEN layout, who defends a square) a 2nd time, write 'I'm not sure' / 'let me trust memory', contradict yourself, or several turns pass with no new tool call. Action: stop prose analysis, emit one tool call for the next unresolved candidate (<safety>/<simulate>/<board>), or commit the best tool-supported move. Must NOT be used to skip verification of the move you are about to play: the commit gate (a tool result covering that exact move in the current position) still applies. Unused tool calls are wasted, so use them instead of long hand calculation.

## Finding the Move: Motifs and Candidates

**Parse once, then scan forcing moves first (work from the printed legal-move list, not a mental board).**
- Read the printed board and Material line once and treat them as ground truth. Do NOT re-derive piece placement from the FEN by hand. If you give two different contents for one square, or list the same pieces a second time, stop and generate candidates. If a square is genuinely in doubt, confirm it with a tool (<threats>, <hanging>, <board>).
- State the key features once: passed pawns, king exposure, loose pieces, forcing moves available. Classify the position (tactical melee vs quiet vs endgame) from king safety and piece activity. If a check or capture plausibly rips open the enemy king, make it the primary candidate, including as a sacrifice.
- Scan order: (1) list every move in the legal-move list ending in "+" or "#" (checks), (2) every move containing "x" (captures), (3) threats/forks, (4) only then quiet moves. A move suffixed `#` is the top-priority candidate: verify it first, and dismiss other checks/captures by name in a short phrase (e.g. "Qxh2+ is not mate"). At least one member of a non-empty check or capture list must be checked with <simulate> or <safety> before you commit to a non-forcing move.
- Runtime check: count your candidates as checks/captures vs quiet moves. If quiet moves dominate in a position described as a tactical puzzle, re-scan the legal-move list for checks/captures you skipped.
- A candidate that is not in the legal-move list is discarded immediately (you mislocated a piece; re-read the FEN piece by piece).
- Trace EVERY check at least two plies deep (forced king reply, then the next check or capture) looking for mate or a larger gain. Do not stop at the first check that fails, and do not settle for a 'safe material win' until no check leads to mate or a bigger gain. Runtime check before committing: "did I trace every check two plies?"
- Do not choose a move from recollection of a 'similar puzzle' or because it 'feels forcing'; every candidate must be priced by a tool.
- Runtime check: if you have considered more than 2-3 candidates in prose before the first tool call, stop and batch them into one tool call now.

## Verifying the Move: Tool Ritual

**Tool-first rule.** Your first reply in a position should be a tool call on your top 1-3 candidates (e.g. `<safety>Rf7+, Ra8+</safety>`, batching all checks/captures together), not an essay.
- **Format:** when you intend a tool call, emit ONE bare tag from the allowed set (<hanging>/<threats>/<safety>/<simulate>/<board>/<line>) with valid arguments, with no reasoning block before it and no note after it. Never write 'I will run safety…' or 'let's check…' without emitting the tag in that same reply.
- Tool names never go inside <action>. <action> is reserved for a legal move. If the harness answers 'no tool tag and no move', your next reply must be nothing but one correctly named tag or an <action>.
- **Never hand-compute** check status, square colour, diagonals, attacker/defender counts, or 'is X defended' from the FEN. <safety>, <threats> and <hanging> report these. If you have written more than 2-3 sentences of geometry for a candidate, call the tool.
- **Multi-ply:** never assert more than one ply ahead from memory. Use <simulate>, <line> or <board> to get the actual resulting position. After each opponent reply, re-derive the next move fresh from the new FEN and legal-move list rather than following a precomputed plan.
- **Commit gate:** before writing <action>, confirm the most recent tool result in the CURRENT position covers that exact move. If not, call a tool first. For mate-in-2 follow-ups, read the resulting legal-move list for the mating move and check the king's escape squares from it.

## Comparing Candidates

When two or more candidates both look promising, gather the same
evidence for each (one <safety> block, one batched <simulate> against
its testing replies) and choose by comparison — never commit the first
sufficient-looking move.

- Narrow to 2-3 finalists, then compare using tool output, not free-text walks through every legal move.
- Query all checks/captures together in ONE <safety> call and compare the returned fields (opponent legal-reply count, attackers vs defenders, own pieces en prise). Fewer opponent replies means more forcing. Runtime check: if you only tested one candidate, go back and query the others.
- Before the final <action>, name at least one alternative candidate (e.g. a different capture or check) and state in one sentence why it is inferior, using tool-reported material/safety data where available (e.g. "Nxe5 only wins a pawn and allows a recapture; Qxb5 wins an undefended piece").
- Price each candidate against the single most testing reply (material, king safety, forced sequence) before ranking. Never prefer a quiet material grab to a check or major-piece sacrifice without having simulated the check two plies deep. If you did not, say you have no tool evidence for it.
- A warning such as 'LOSING EXCHANGE RISK' or 'own piece en prise' on a check is a prompt to simulate the forced recapture line, not an automatic rejection. If the line shows a real loss, drop the move and test the next most forcing candidate.

## Judging Tool Output

- Trust the tool's attacker/defender/reply counts over your own re-scan of the board.
- Once a tool result settles a fact ('this loses the rook', 'opponent has exactly 1 reply'), treat it as settled and move to the next unresolved candidate.
- A `<safety>` flag of `[LOSING EXCHANGE RISK]` is information, not a veto. Do NOT discard or commit on the flag alone. Read the listed forcing replies and write at least one reply-and-follow-up pair for each (recapture, promotion, bigger threat, or a winning counter-capture), or run a `<simulate>` covering those replies, then decide. Take the flag as decisive only if some forcing reply has no adequate follow-up.
- If your own analysis or a tool finds a refutation of your candidate, do NOT play it unless a further tool call shows the refutation does not occur. Never resolve confusion with 'I'll trust the most forcing move'; resolve it with a tool call.
- Before rejecting a candidate ('this loses material / is bad'), you must hold tool output naming the opponent's actual replies to that exact move.

## Converting the Line (Second Move)

- Mate verification: before committing a move you believe is checkmate (flagged `#`, or a check you expect to be mate), explicitly check all three defenses in turn: (1) can the king move to any adjacent square (including capturing an adjacent piece)? (2) can any enemy piece capture the checking piece? (3) can any enemy piece block the check (not applicable to knight or adjacent checks)? Only after all three fail, commit.

## Budget Discipline

**Turn-ending protocol (mandatory).** Every turn must end with exactly one of: (a) one well-formed tool tag with valid arguments, or (b) one <action>MOVE</action> where MOVE is an exact string from the Legal moves list, including +, #, x and promotion suffixes. Reasoning-only turns and bare words like <action>safety</action> waste budget and fail to commit.
- Once you write "the best move is X", your very next output must be <action>X</action>. Never follow a stated conclusion with another tool call.
- Track remaining calls. When one or two remain, or reasoning is looping over the same lines, stop and commit the best-supported candidate (prefer a forcing move that survived verification).

## Common Pitfalls

- Playing a move with no tool observation for it (ending a long monologue with <action> after 'I'll go with the forcing one'), or playing a move your own analysis labelled 'bad'.
- Narrating a tool call instead of emitting it, wrapping the tag in reasoning, or putting a tool name inside <action>.
- Pure mental simulation loops: repeating the same material count without a tool result.
- Fixating on the one or two visually obvious moves (an eye-catching capture or pawn push) while a quiet-looking check in the legal-move list goes unexamined. Dismissing a check after one shallow mental ply is the same mistake.
- Equating 'wins material safely' with 'best' in puzzles: puzzle solutions are usually the most forcing line (mate or larger gain).
- Abandoning a line half-finished (identifying a reply like fxg3 and then dropping the analysis).
- Hand-parsing the FEN repeatedly, inventing pieces, or proposing illegal moves; re-verifying known facts instead of advancing to candidate comparison.
- Testing only one candidate when several checks/captures were available.
