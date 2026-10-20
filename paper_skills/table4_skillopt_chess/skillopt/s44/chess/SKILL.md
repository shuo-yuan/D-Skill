## When NOT to Analyze: Fast Paths and Stopping Rules

Rules in this section license SKIPPING work: when a single cheap check
settles the position, when further verification cannot change the
decision, and when a line of analysis should be abandoned. Every entry
must name (a) the exact trigger that makes the shortcut safe and
(b) the condition under which the shortcut must NOT be taken. A rule
without both parts does not belong here.

- **Listed mate.** Trigger: the current Legal moves list contains a move marked `#`. Play it. At most, spend one `<safety>` call on it, which reports CHECKMATE. Do not search for anything better. Do NOT take this shortcut if the `#` move is not in the current list, or if you only derived the mate yourself and it is not marked. In that case confirm it with `<safety>` first.

## Finding the Move: Motifs and Candidates

Read the puzzle `themes:` in the task header first. Then read the position from the printed Board diagram (rank 8 at top), one rank at a time, never by decoding the FEN in your head. Do not invent pieces. Before naming any move, check that it appears in the Legal moves list. If a move is missing (for example a rook capture blocked by another piece), your board picture is wrong, so re-read it.

If the themes say mate, mateInN, sacrifice, pin, skewer or crushing, the answer is a FORCING first move: a check, a sacrifice, or a quiet move that leaves the enemy king or queen 1-3 replies. A free-looking pawn or piece grab (Rxc2, Qxa5, Qxd5) or a queen chase is almost never the answer, even when you are down material. Build candidates in this order: (1) moves marked `#`, (2) EVERY check (`+`), including sacrifices, (3) captures of the defender of the king or of a key square, and among captures prefer the highest-value piece that has no defender, (4) quiet threats only if 1-3 fail. Take the top 3-5 forcing candidates to the tools rather than the first move that 'looks good'.

Use `<hanging>` to find loose enemy pieces. A capture that wins a whole piece beats a pawn grab or a check that only wins a pawn later. Typical mate geometry to look for: a queen or bishop covering the king's flight square along a long diagonal; a knight guarding the checking square; the defender's rook blocked by its own king, so it cannot recapture.

## Verifying the Move: Tool Ritual

Never commit after 0 tool calls unless there is only one legal move or the move is a listed `#` move. Minimum ritual: one `<safety>` call batching your 3-5 best candidates (checks first). Read its output for: `gives check` / CHECKMATE, `opponent legal replies` (a small number means a mating net, so test that move first), the `forcing replies` list, and `destination: attackers vs defenders`. Take defender counts from the tool, never from your own eyes. Then run `<simulate>` or `<line>` on the best 1-2 survivors against EVERY forcing reply, and confirm a mate or a clear gain against each. A candidate whose audit shows a piece en prise, or a reply that wins material without compensation, is refuted. Do not play it. Go back to other candidates and choose by comparing audit results, not by intuition about 'king safety' or 'material'. If `<threats>` says your queen or rook is capturable, your move must answer that or be a bigger forcing move. When you are in check, `<threats>` is unavailable: run `<safety>` on ALL your legal moves at once, then `<simulate>` the best against its listed forcing replies.

## Comparing Candidates

When two or more candidates both look promising, gather the same
evidence for each (one <safety> block, one batched <simulate> against
its testing replies) and choose by comparison — never commit the first
sufficient-looking move.

## Judging Tool Output

## Converting the Line (Second Move)

## Budget Discipline

- Every reply must END with exactly one tag: `<safety>Qxf7+, Rd1+</safety>`, `<threats></threats>`, `<hanging></hanging>`, `<simulate>m, r1, r2</simulate>`, `<line>m1, r1, m2</line>`, or `<action>SAN</action>`. `<tool_code>`, `<toolcall>`, `print(...)`, bare words, a tag that appears only inside your reasoning, and a reply ending in plain text or '(final)' all count as malformed. Each one wastes a turn and can end the episode. Always finish with an `<action>`.
- Keep reasoning to a few lines. If you catch yourself restating the piece list, re-parsing the FEN a second time, or repeating an analysis, stop and emit `<safety>` on your top checks and captures immediately.
- Spend the first 2-4 calls on breadth (different candidate first moves) and the rest on depth.

## Common Pitfalls

<!-- SLOW_UPDATE_START -->
<!-- SLOW_UPDATE_END -->
