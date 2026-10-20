## When NOT to Analyze: Fast Paths and Stopping Rules

Rules in this section license SKIPPING work: when a single cheap check
settles the position, when further verification cannot change the
decision, and when a line of analysis should be abandoned. Every entry
must name (a) the exact trigger that makes the shortcut safe and
(b) the condition under which the shortcut must NOT be taken. A rule
without both parts does not belong here.

## Finding the Move: Motifs and Candidates

- The legal-move list is authoritative. Build candidates from it, not from memory. If it holds moves by many different pieces, you are NOT in check. If a listed move surprises you (a check or capture you did not see), your mental board is wrong, not the list.
- Order candidates: (0) '#' moves; (1) every check ('+'), counting the king's flight squares after each; (2) captures of undefended, pinned or high-value pieces; (3) sacrifices that open lines, deflect a defender or expose the enemy king (queen or rook sac next to the king, then a knight or bishop follow-up); (4) quiet moves last. A move like 'Qg8+' or 'Nf7+' next to a boxed-in enemy king is a prime suspect. Look for smothered and back-rank patterns. A check that drives the king off a line and exposes a loose piece is a common pattern (e.g. Rc8+ then Rxc1). Confirm a loose-piece capture with one `<safety>` call before committing.
- Use the metadata themes as hints. For `mateIn2`/`mate`/`crushing`, the first move is a check or a quiet move that leaves no defence, so a free capture or a solid move is usually a decoy, even when you are down material. For `fork`, `skewer` or `pin`, look for the move that hits two targets. For `sacrifice`, a material-saving move is probably wrong. For `defensiveMove`, expect a quiet or in-check reply that removes a threat. When you are down material in a puzzle, expect a forcing solution, not a quiet one.
- A check whose `opponent legal replies` count is 1-3 is a mating lead. Confirm that you have a mating or winning second move against EVERY reply.
- When two attractive moves win similar material (for example a check versus a direct capture), run `<safety>` on both and prefer the one that leaves the opponent fewer good replies. Do not default to the check.

## Verifying the Move: Tool Ritual

Your FIRST reply on every move must end in a tool tag, after at most ~10 lines of thought. Never commit a first move from mental analysis alone. The only exception is a '#' move already in the legal list. Do not re-parse the FEN by hand. Ground truth is the printed 8x8 board and the legal-move list.
1. If you are not in check, call `<threats></threats>`. If you are in check, `<threats>` is unavailable, so go straight to step 2.
2. Call one `<safety>` with up to 5 candidates: every '#' or '+' move, then the best captures and sacrifices. Read `opponent legal replies`, `forcing replies` and `your pieces en prise after the move`.
3. Verify the finalist with `<line>your_move, best_reply, your_move2</line>`, or a batched `<simulate>` against every forcing reply `<safety>` listed. The puzzle ends within 2 of your moves, so your second move must work against EVERY reply.
4. Only then commit with `<action>`. Never write a tool name inside `<action>`.

Reading `<safety>`: 'destination: attackers N vs defenders M' with N>=M means the moved piece can be captured. A queen or rook `en prise`, or `LOSING EXCHANGE RISK` on the destination, refutes the move unless a `<line>` or `<simulate>` shows the payoff. A forcing reply that captures your queen or rook (e.g. 'Rxb1 (captures rook)') means your 'win' is only a trade. A forcing reply marked '#' means the move loses to mate. Never call a move winning if the output shows a recapture or mate you have not answered.

Endgames and pawn endings are not exempt. `<simulate>` each king move and pawn move before committing, and prefer the move that keeps the opposition and tempo. Do not commit a pawn break just because it 'creates threats'.

## Comparing Candidates

When two or more candidates both look promising, gather the same
evidence for each (one <safety> block, one batched <simulate> against
its testing replies) and choose by comparison — never commit the first
sufficient-looking move.

## Judging Tool Output

## Converting the Line (Second Move)

On the second move the position has changed. Re-read the new FEN, board and legal list. Earlier tool output no longer applies. Do not follow the old plan blindly.
- If you are in check and can capture the checking piece, compare the captures by material result (e.g. Kxh6 winning a rook beats gxh6, which leaves you down).
- If an opponent piece is left undefended, take it after confirming with `<safety>` that the destination has no attackers.

## Budget Discipline

## Common Pitfalls

- **Hand-parsing the FEN / misreading the position.** Read squares from the printed 8x8 board once (rank 8 on top, uppercase = White, files a-h left to right). Check your piece list against the `material` line. If a legal move or tool output implies a piece you did not expect (e.g. 'Qxg7+', 'Rxb1'), your picture is wrong, so call `<board>` on a move to see the real position. Never claim 'I am in check' unless the legal list contains only king moves, blocks and captures of the checker.
- **Rationalising past a tool warning.** If `<safety>` shows the queen or a rook en prise or a losing exchange, do not commit that move on a hunch. Pick another candidate.
- **Taking free material in a mating or sacrifice puzzle.** A pawn grab, a rook capture or a queen-winning-looking fork must survive `<safety>` and `<simulate>` against every forcing reply. Compare it with the best check or sacrifice on the same evidence before committing.
- **Endless analysis or no tag.** If you have looped on the same lines twice, stop and emit a tool tag (`<safety>` on your top 3 candidates) or, after a tool result, an `<action>`. Long reasoning that ends without exactly one tool tag or one `<action>` tag costs a turn.
- **Lazy first move in quiet positions.** Do not commit the first sufficient-looking move. In this tactics task the intended move is usually a forcing check, capture or sacrifice, not a natural developing or evasive move.

<!-- SLOW_UPDATE_START -->
<!-- SLOW_UPDATE_END -->
