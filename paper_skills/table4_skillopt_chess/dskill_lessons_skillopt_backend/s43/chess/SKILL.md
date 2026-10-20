## When NOT to Analyze: Fast Paths and Stopping Rules

**Fast path: flagged mate.**
- Trigger: the Legal-moves list contains a move ending in `#`. Make ONE verifying call (`<safety>` or `<line>` on that move) and read the result: the opponent should have 0 legal replies / the resulting position is checkmate. If confirmed, commit with a single `<action>` right away. Skip the full check/capture enumeration, the quiet-move analysis and the pre-commit alternative comparison; a verified mate beats everything.
- Do NOT take this path if no `#` flag appears in the list, or if the verification call shows the opponent still has a legal reply (then fall back to the opening protocol). A `+` flag alone is not a mate: it only makes the move a first candidate to trace two plies deep.
- If several moves are flagged `#`, verify one and play it; do not compare them.

Rules in this section license SKIPPING work: when a single cheap check
settles the position, when further verification cannot change the
decision, and when a line of analysis should be abandoned. Every entry
must name (a) the exact trigger that makes the shortcut safe and
(b) the condition under which the shortcut must NOT be taken. A rule
without both parts does not belong here.

- **Stop re-parsing the board.** Trigger: you have already read the board diagram once this turn. Use `<hanging>`/`<threats>` for any further doubt about what is attacked. Do NOT apply this if a legal-move entry contradicts your read; then run one tool call on that move.
- **Stop when a tool has spoken.** Trigger: a `<safety>`/`<simulate>` result on a candidate shows it wins material or mates with no en-prise pieces of yours. Play it after naming one alternative. Do NOT apply this if the result stops at a non-quiescent point (a recapture is still available) or if a check was not traced two plies deep.
- **Abandon a hand-calculated line.** Trigger: the same square or count has produced two different answers in your prose. Drop the prose and call a tool on that move. Do NOT keep computing by hand.

## Finding the Move: Motifs and Candidates

**Opening protocol (do this BEFORE any long prose analysis):**

0. **Read pieces from the printed ASCII board diagram (one line per rank), never by counting characters in the raw FEN.** If FEN and diagram disagree, trust the diagram. If a legal move looks impossible from your read (e.g. a capture on a square you think is empty), you have mislocated a piece: run `<hanging>` or `<safety>` on that move once instead of debating it in prose.
1. Treat the printed board, Material line and Legal-moves list as ground truth. Parse the position ONCE; never re-derive the FEN a second time. If you state two different contents for the same square, reread the printed board once and move on. If your manual analysis contradicts the legal-move list, resolve it with a tool (`<threats>`/`<hanging>`), not more re-reading.
2. Make your first call `<threats></threats>` or `<hanging></hanging>` to get the engine's verified read of what is attacked or hanging for both sides. Do not derive attacked squares by hand.
3. Own-piece scan: for each of your pieces, note whether an enemy piece attacks it and whether it is defended ("Ne8: attacked by Bb5, undefended"). A candidate that ignores an attacked undefended piece of yours must be justified by a bigger threat or a forcing line.
4. Enumerate from the printed legal-move list: write down EVERY check, EVERY capture, and every move flagged as mate (`#`). If a move is not in the legal list, it is not a candidate. Odd-looking legal moves (e.g. a Bxc3 that seems geometrically impossible) usually capture an enemy piece that just moved there. Spend 1-2 sentences on this, then call `<hanging>`/`<safety>` if still unsure.

**Write two explicit lists before any other analysis: (a) every move ending in `+` or `#`, (b) every move containing `x`.** Do this BEFORE thinking about quiet moves, retreats or piece safety. At least one member of list (a) must be tool-checked (a `<safety>` batch) before you commit to any non-forcing move or capture. Never fixate on the first capture or pawn push that catches your eye while a check sits unexamined.
5. Mate/check flags first: if the legal-move list marks a move with `#`, verify it FIRST and rule out other checks/captures by name in one sentence each (e.g. "Qxh2+ is only check, Qg7# is mate"). A `#` move beats any material-winning alternative; if several moves are `#`, any is fine. Do not take this shortcut if no `#` flag is present. Then enumerate checks, captures and threats (forks, hanging pieces) instead.

**Mate-dismissal rule:** never declare a `#`-flagged move "not mate" after finding one apparent defence. The `#` flag comes from the legal-move list and is ground truth. If you doubt it, run `<simulate>` on that move once. The usual reason a seemingly available recapture or block fails is that the defender is PINNED against its own king (e.g. a queen on the king's file or diagonal with an enemy queen, rook or bishop lined up behind it). Check pins, all blocks and all king flight squares before dismissing.
6. Checks next: trace each check at least TWO plies deep (forced king reply, then your next check or capture) with `<line>` or `<simulate>` to see if it leads to mate or wins more than a simple capture. Settle for "safe material gain" only after confirming no check gives mate or a strictly larger gain.

**Every check gets a `<simulate>`/`<safety>` call unless a tool result already rejects it.** A check that does not win material immediately may still drag the king or a defender so that a piece hangs or a second check follows. **Rank checks by king restriction before comparing material:** note how many legal replies the enemy has (from `<safety>`'s reply count) and whether its own pieces block the king's escape squares (edge/corner king). A check leaving 0-1 replies, or driving the king into a trap, must be explored one ply deeper with `<simulate>`/`<board>` BEFORE any material-grabbing capture or pawn push is chosen. In puzzles with a short forced win, the answer is very often the only check on the board or a check/capture sequence, and a check limiting the king to 1-2 replies is usually the key move. Do not settle for a quiet material trade until every check has been priced.
7. Collect 2-4 candidates (checks and captures first) and go straight to a batched tool call on them, before hand-calculating any quiet alternative.
8. When in check (forced reply): evaluate EVERY legal reply by material outcome, not just "escapes check". Check whether a king move leaves one of your own pieces en prise, versus capturing the checking piece (which usually keeps the material gain). Prefer capturing the checker unless it loses more.

## Verifying the Move: Tool Ritual

- **Emit, don't narrate (hard rule).** Phrases like "I will run safety", "let's check X with the tool" or "(final) safety(...)" are worthless unless the turn IS the tag. If your draft contains such a sentence, delete all the prose and send only the literal tag, e.g. `<safety>Qa8+, Qb8+</safety>`. If a reply came back "no tool tag and no move", your very next reply is ONE minimal tag with no prose before it. Never write fake tool output in prose ("the safety analysis shows..."); only a real tag produces real results.
- **Hard prose limit:** never write more than ~3 sentences of analysis before the next tool call. If you find yourself writing "if X then Y, then Z" beyond one ply, stop and issue `<simulate>`/`<line>`. Zero tool calls before an `<action>` is a failure, except for a `#`-flagged mate.
- **No-tool-output, no-`<action>` gate / last-move verification.** The move you finally play must have a `<safety>` or `<simulate>` result for that EXACT move in the CURRENT position in the transcript. If you said you would verify and no result exists, make the call now. Never play a move just because the other candidates were discarded ("least bad").
- **Verdict ledger:** keep a running list `move: verdict (source tool/reason)`. Once a candidate has a verdict, do not re-open it unless a new tool result contradicts it; only introduce untested candidates in later calls. Asking yourself about the same move more than twice is the signal to call one tool on it and commit to the result.
- **Never put a tool name inside `<action>`** (`<action>safety</action>` is invalid). The action tag holds only one move copied verbatim from the Legal-moves list.

- **Tool over prose.** Never hand-compute attacker/defender counts, whether a piece is defended, check status, square colour/diagonals, or material after an exchange. Use `<safety>` for a candidate (en-prise pieces, attackers vs defenders, forcing replies), `<simulate>` for a candidate vs the opponent's replies or a multi-move forced line, and `<hanging>`/`<threats>` for the current position. Tool output overrides your mental count.
- **Trigger to stop and call a tool:** you have recomputed the same square's defenders or the same material count twice, written more than 2-3 sentences of geometry/diagonal reasoning, produced two contradictory totals for the same line, or your own piece list differs from an earlier turn. Call `<safety>`/`<simulate>` on that exact move.
- **Batch candidates.** Put all top candidates into ONE `<safety>` call and compare the returned fields (opponent legal-reply count, en-prise, material) across all of them. Up to 10 calls are available, but a typical puzzle needs 1-3: one `<hanging>`/`<threats>` (or none), one batched `<safety>`, optionally one `<simulate>` on the finalist, then commit.
- **One ply in prose, the rest via tool.** Never assert more than one future ply from memory. Use `<line>` or `<board>` to get the actual resulting position, and after the opponent replies, re-derive from the new legal list rather than from a pre-computed plan.
- **Every serious candidate (check, forcing capture, sacrifice) gets at least one `<safety>` or `<simulate>` before commitment.** Read the material/en-prise line from the output.
- **Full-depth simulation.** A `<simulate>`/`<line>` that ends right after the opponent's single reply to a sacrifice or exchange is NOT quiescent. Before discarding a candidate on a material deficit, check whether any of your remaining pieces attacks the square the opponent piece just landed on. If so, re-run with that recapture added as an extra ply. Discard only when material after the full forcing sequence is unfavorable.
- **Confirming a mate:** use `<line>` with the full mating sequence, then check the king's escape squares against the actual new legal-move list.

For any pre-computed multi-move line (3+ plies), confirm at least the first forced reply and resulting position with `<simulate>`/`<line>`. After the opponent actually replies, check the new Legal-moves list. Your final justification should cite a tool observation for every move-reply pair it claims.
- **Post-forcing-move re-scan:** after any of your own checks or captures that forces the enemy king or a defender to move, run `<hanging>` (or `<simulate>` and read the en-prise field) in the resulting position and ask "did the forced reply abandon a piece?" A rook or queen defended only by the king often becomes free once the king is dragged away or cut off. This is a standing question after every check, not just at move 1.
- **Tool-call formatting:** a tool call must be the ENTIRE reply, with one correctly-named tag and its argument. Put no reasoning essay before it and no '(final)' note after it. Never embed a tool tag inside prose. If the environment says 'no tool tag and no move', your next reply must be only one minimal tag or an `<action>`.
- Before `<action>`, confirm that a tool result from the CURRENT position supports the move. Do not commit on 'it feels forcing'.

## Comparing Candidates

- **Do not reject a candidate from mental arithmetic.** Before writing "this loses material", "this is bad" or "the endgame is lost" about any check, forcing capture or sacrifice, you must have `<safety>`/`<simulate>` output for that move naming the opponent's actual replies. Your own exchange count is a hypothesis, not evidence.
- **A `<safety>` flag prices only the immediate exchange.** If a check shows "opponent legal replies: 1" (or 0-2) but flags "captures queen/rook" or "attackers N vs defenders N", do NOT discard it. Run `<simulate>`/`<line>` with the forced reply appended and evaluate the resulting position (open files, follow-up checks, mate threats, recapture of the capturer). Discard only after the tool shows the follow-up is weak. A single forced reply is a strong sign of the key move.
- **Never play a move your own analysis just refuted.** Before `<action>`, re-read the last line you calculated for that move. If it ends in lost material or a non-mate, or you wrote "not winning"/"doesn't work", pick another candidate. Emit exactly ONE `<action>` tag per turn.

- **Commitment consistency check (mandatory before the action tag):** search your own turn text for the move you are about to play. If it appears near words like "blunder", "loses", "hangs", "refuted", or you admitted it loses material or is unclear, do NOT play it. Run `<simulate>`/`<safety>` on it, or switch to the candidate your analysis actually supported. Do not commit "because it's the most straightforward option" when your own analysis says it loses material.
- If your own analysis or a tool result (e.g. 'LOSING EXCHANGE RISK', or a destination square attacked and undefended) shows a refutation of a candidate, that candidate is dead. Move to the next most forcing check/capture and verify it with a tool.
- Do not discard a forcing check/capture you have already priced as winning in favour of a quieter, hand-calculated 'improvement' unless a tool run on that alternative in the current position shows it is safe AND better. Likewise do not declare a candidate refuted ('hangs the piece') without tool confirmation.
- **Pre-commit alternative:** before the final `<action>`, name at least one alternative candidate (e.g. a pawn-grabbing capture vs. winning an undefended piece) and state in one sentence why it is inferior, using tool-reported material/safety data where available. A mate beats any material gain; a larger safe material gain beats a smaller one.

When two or more candidates both look promising, gather the same
evidence for each (one <safety> block, one batched <simulate> against
its testing replies) and choose by comparison — never commit the first
sufficient-looking move.

## Judging Tool Output

## Converting the Line (Second Move)

- On the second move, re-read the new Legal-moves list (a mate move is flagged there, e.g. `Nh3#`) and check that the opponent's actual reply matches your plan. Do not assume the prior board: if a check is blocked or the position differs, call `<safety>`/`<threats>` on the new position.
- Verify mating candidates with `<safety>` or `<simulate>` (opponent legal replies / escape squares) instead of abandoning them from unaided mental calculation. Prefer a verified mate or forcing move over a quiet safe move.

## Budget Discipline

- **Spend calls early, not last.** Plan roughly: call 1 `<threats>`/`<hanging>`; call 2 a batched `<safety>` on ALL checks and forcing captures (up to ~6 moves in one call); call 3 `<simulate>` on the top 1-2 finalists including the opponent's most testing reply; then commit. Do not reach `<simulate>` only on call 10, and do not spend prose recomputing material between calls.
- **Trust provided annotations.** The Legal-moves list already shows checks (`+`) and mates (`#`), and the Material line and en-prise data come with each observation. Do not re-derive piece placement, legality or check status when the list states it; if you doubt one item, verify it with one `<safety>` call rather than rebuilding the board.

**Turn-ending format (hard rule):** every turn must end with EXACTLY ONE well-formed tag and nothing after it. That tag is either one tool tag (`<hanging>`, `<threats>`, `<safety>`, `<simulate>`, `<board>`, `<line>`) or one `<action>LEGAL_MOVE</action>`.
- The move in `<action>` must exactly match an entry in the Legal-moves list. Never put a tool name (e.g. `<action>safety</action>`) inside an action tag.
- Never send reasoning-only turns (they are rejected and burn budget). Never append text such as "(final)" or "PLAN:" after the tag. Never emit `<action>` more than once.
- If you say 'the move is X', the next output is `<action>X</action>`, not another tool call.
- Pre-send check: the draft contains exactly one opening/closing tag pair, and it is last.
- Count tool calls per move. Past 3-4 calls without a commit, stop opening new lines and commit the best tool-supported candidate. With 1-2 calls left, do not spend them on a fresh candidate; commit.
- Do not flip-flop between candidates across turns, and do not reopen a stated decision with "wait, what about..." unless a tool result contradicts it. Once a candidate is tool-verified as safe and forcing/winning, play it.
- If reasoning becomes circular (same board or candidate list restated twice), pick the top 1-2 candidates, issue exactly one tool call, then commit based on its output.
- Keep reasoning short: state features, list candidates, call the tool, read the output, commit.

## Common Pitfalls

- Hand-counting defenders, colours and diagonals and then flip-flopping (the most common failure): replace it with a tool call.
- Re-parsing the FEN repeatedly: parse once, trust the printed board.
- Zero tool calls on a tactical puzzle: a short tool-verified answer beats a long hand derivation.
- Playing a capture whose recapture you already noticed (queen takes a defended bishop, queen-for-rook trade) without verifying with `<safety>`/`<simulate>`.
- Playing a move whose refutation you already found because it 'felt forcing'.
- Missing that your own piece is attacked and undefended, then chasing speculative attacking sacrifices; dismissing a simple check-and-capture for a deep speculative line that puts a piece on an attacked square.
- Preferring a safe material grab over a forced mating check sequence without tracing the checks.
- Ending a turn with no tag, a malformed tag, duplicate action tags, or a tool tag instead of a final legal-move `<action>`.

- Writing "I will call `<safety>`" (or listing it as a plan) and then ending the turn with an `<action>` or with nothing. The intention is not a call.
- Committing on a hand-simulated multi-ply line with zero tool output in the transcript (repeatedly the reason for a wrong first move).
- Dismissing a check because `<safety>` says it "captures queen" without looking at the position after the single forced reply.
- Contradicting yourself about which piece stands where across king-move branches. This is the signal to stop and call `<simulate>` on the most forcing branch.
