---
name: chess
description: "Chess tactics skills distilled from expert-student contrast."
---

## When NOT to Analyze: Fast Paths and Stopping Rules

Rules in this section license SKIPPING work: when a single cheap check
settles the position, when further verification cannot change the
decision, and when a line of analysis should be abandoned. Every entry
must name (a) the exact trigger that makes the shortcut safe and
(b) the condition under which the shortcut must NOT be taken. A rule
without both parts does not belong here.


**Lone forcing winner.** Trigger: exactly one forcing candidate (check/capture/threat) delivers mate or wins decisive material and no other legal move is forcing. Commit to it without analyzing quiet alternatives. Do NOT take this shortcut when two or more forcing candidates look winning — follow the Comparing Candidates workflow instead.

**Trust a clean forcing-safety verdict.**
**Do not doubt a `#`/mate flag on surface geometry.** Trigger: the legal move list marks a candidate `#` (or `+`). Treat the flag as a fixed premise, not a hypothesis to test against your own visual read of the board. Use the flag to direct verification toward the supporting mechanism (open line, pin, overloaded defender, discovered check) rather than reasoning about why it looks illegal or wrong. Do NOT take this shortcut if `<safety>` itself later contradicts the flag — then treat the tool output, not your own geometry read, as the tiebreaker.

 Trigger: `<safety>` on a forcing candidate (check/capture/threat) reports zero capturing replies and lists only non-capturing responses (king retreats, passive blocks). Treat the move as verified and issue `<action>` next turn without further tools. Do NOT take this shortcut if `<safety>` lists any capturing reply, leaves any reply unevaluated, or the candidate itself was not forcing.

**Trust tool-reported reply counts and forcing labels.** Trigger: `<board>` or `<safety>` reports a specific restricted number of opponent legal replies (e.g., "legal replies: 1") or a "forcing replies: none/[move]" label for the candidate just played. Accept that count/label as verified fact — do not manually recount legal moves or debate whether an alternative reply is legal. Immediately calculate the forced follow-up or commit via `<action>`. Do NOT take this shortcut if you have reason to think the position given to the tool was wrong (e.g., wrong side to move, stale board state) — in that case re-issue the tool call once, not repeatedly.


**Stop scoring quiet moves once a forcing move is confirmed.** Trigger: a tool call has confirmed a forcing candidate is safe or winning. Immediately proceed to `<action>` on the next turn; do not continue evaluating or scoring quiet/positional alternatives in parallel. Do NOT take this shortcut if the confirming tool output was incomplete (see the rules above) — resolve that first.

## Finding the Move: Motifs and Candidates

Immediately scan the legal-move list for entries tagged `#` (mate), `+` (check), or `x` (capture) — these are your primary candidates for tool verification before anything else. A `#` annotation is a high-priority tactical signal: after a quick structural check (line of sight, king safety, capture path), commit to it rather than continuing to search for or doubt-check alternatives. Ground the position first: re-read the FEN/board grid from scratch rather than relying on memory (see Reading the Position below), then call `<hanging>` and `<threats>` before generating candidates to establish en prise pieces and opponent forcing moves — discard any candidate that ignores a direct opponent threat, and flag any free piece from `<hanging>` as an immediate candidate. Generate candidates strictly from the provided legal move list; never propose a move not present in it.

**Mandatory, non-skippable:** do not substitute manual FEN/board parsing or geometry-tracing (diagonals, pin lines) for the `<threats>` call — parsing geometry yourself does not surface opponent forcing replies and burns reasoning budget a single tool call would settle. If you find yourself debating square occupancy or diagonals in prose instead of having called `<threats>` first, stop and call it before picking a candidate. If your own manual reasoning flags a candidate as possibly losing material (e.g., to a same-file/diagonal recapture), never override that doubt by committing anyway — call `<simulate>` or `<board>` to resolve it before playing the move.


Scan the full legal move list first and build the candidate pool in priority order: checks, then captures, then threatening advances/forks; discard quiet moves and defer deep calculation to them only once every forcing candidate is exhausted or ruled out. This applies with extra force when the opponent's king is exposed (open lines, missing pawn cover, stuck in center) — enumerate ALL legal checks before considering anything positional, since forcing moves narrow the opponent's replies and are cheaper to verify.

Before committing to any capture or exchange, list every opponent piece that attacks the target square and confirm the resulting material balance is favorable or forced (e.g., "c6 is defended by the b5 bishop, so Qxc6 loses material"). Discard the capture as a candidate if this check fails.

Parse the board and FEN exactly once at the start — locate both kings, major attackers, and candidate target squares in a single pass and record it in your reasoning. Do not re-read or re-verify the board layout mid-calculation; treat your first parse as final and move directly to candidate generation and tool calls.


**Runtime check before any tool call:** ask "Does my leading candidate give check, capture a piece, or create an immediate threat — and does any legal check restrict the opponent's king more than a capture would?" Re-filter the legal-move list checks-first, then captures, then threats, and test the most forcing one via `<safety>`/`<simulate>` before writing analysis on quiet alternatives. Do not open a manual scanning/doubt loop over quiet waiting moves, and do not fixate on a capture while an unverified check remains available. When a threats report shows an opponent piece attacking one of yours, do not switch into a defensive search before checking forcing options — list all legal checks against the enemy king first; a threat to your own piece never outranks an unrefuted forcing check.

Do not stop at the first plausible forcing move. Count the forcing candidates (checks/captures/threats) in the legal move list — if fewer than three exist, rescan to confirm none were missed; if three or more exist, call `<safety>` on each in rapid succession to compare verified risk levels before comparing and committing (see Comparing Candidates).

When multiple active pieces jointly threaten the enemy king (a mating net), identify which pieces are the coordinated attackers, check which can deliver check now or next move, and confirm each stays supported or unblocked through the forced sequence before committing — this is how short forced mates are built from several attackers rather than one.

When a candidate delivers check or creates a mating threat, explicitly list every escape square available to the opponent's king and confirm each is covered by your pieces, controlled by a threat, or already blocked/occupied — a hidden flight square is the most common reason a "winning" check fails.

Do not stop at the first plausible forcing move. Count the forcing candidates (checks/captures/threats) in the legal move list — if fewer than three exist, rescan to confirm none were missed; if three or more exist, call `<safety>` on each in rapid succession to compare verified risk levels before comparing and committing (see Comparing Candidates). When multiple checks are available, mentally compare the opponent's forced reply to at least two of them before picking one to verify — do not generate only your first-impression check and send it straight to a tool.


Work one forcing candidate to a definitive conclusion (tool-verified safe, refuted, or converted) before starting analysis on the next candidate — do not partially calculate several forcing moves in parallel and then abandon them from surface-level mental errors.

Before requesting tool output, explicitly list your 2-4 candidate moves and state the specific tactical motif or goal each pursues (e.g., "Bxh7+: sacrifice to open the king; Qh5: follow-up mating threat"). This keeps analysis focused and tool calls efficient — do this even when only one forcing candidate exists, so the motif is on record before `<safety>`/`<simulate>` is called.
## Reading the Position: FEN and Material Check

Before generating candidates, resolve the FEN string square by square and explicitly write out the piece count (major and minor pieces) for both sides; verify this tally against any printed material line. Quote the relevant FEN segment or board row when checking a candidate's start/destination squares. This prevents illegal move generation and misreads that derail later calculation, even when the eventual move choice is wrong.

## Verifying the Move: Tool Ritual

Call a tool on your top candidates BEFORE doing lengthy manual calculation — treat the tool's geometry, piece-interaction, and material reports as ground truth to confirm or correct your mental picture, not something to hand-verify first. Runtime check: "Am I about to manually count material or trace diagonals before letting a tool verify the core claim?" If yes, call the tool now.


Before verifying any forcing move, do a single read of the FEN/board and record a one-line positional anchor (attacker square, defender king square, key defending/interposing pieces) — treat this as fixed for the rest of the turn; do not re-parse piece locations mid-calculation.

If the legal move list flags a candidate with `#` (mate) or `+` (check), call `<safety>` on it FIRST rather than hand-verifying in text — a `CHECKMATE` or clean verdict is definitive: commit the move immediately via `<action>` without further tools, doubt, or alternative-candidate search. Only fall back to manual checklist verification (cross off each king escape square individually, list every piece that could capture or block the checking piece) when the tool cannot evaluate the position.

When falling back to manual verification of a mate/decisive candidate, use a full checklist, not a partial mental scan: list EVERY square adjacent to the opponent king, and for each mark it occupied-by-own-piece / attacked-by-you / blocked. Only trust doubt about a remaining square if it survives this full listed pass — a partial visualization that "misses" one square is usually incomplete coverage-checking, not a real refutation. If the full checklist confirms coverage, commit; do not keep re-scanning the same squares from memory.

For any other capturing or checking candidate not already flagged `#`/`+`, run `<safety>` before calculating it by hand. If it flags a quiet (non-forcing) capture as en prise or `[LOSING EXCHANGE RISK]`, discard the candidate immediately — do not continue mental calculation to rescue it. But do NOT discard a *forcing* candidate (a check, or a capture that removes a key defender) on that raw exchange arithmetic alone: first call `<simulate>` on the forced replies and judge the resulting position; only discard if the simulated line is actually bad. Never commit any capture/check whose safety you have not confirmed via `<safety>` or an explicit defender scan.

Do NOT abandon a forcing candidate (check or capture) based solely on a mentally-calculated immediate recapture (e.g., "Nf2+ Rxf2 loses material"). Before pricing or discarding any forcing move, call `<safety>` or `<simulate>` on it to see the tool-verified replies — mental one-ply lookahead frequently misses that the recapture itself is unsafe or that a follow-up wins back material. Runtime check: "Have I used a tool to verify the exact legal replies to this forcing move?" If not, call it before deciding the move loses.

**Calibrate tool use to non-obvious resources only.** Reserve `<safety>`/`<simulate>`/`<threats>` for hidden tactical resources — intermediate replies, discovered checks, overloaded defenders — not for re-confirming geometry already settled by your anchor or an already-flagged forcing move.


**Pre-action gate: no tool, no action.** Before issuing `<action>`, explicitly confirm you called `<safety>`, `<simulate>`, `<board>`, or `<line>` on the chosen candidate this turn — a move that "feels standard," matches a recognized motif, or was checked only mentally (counting defenders, tracing flight squares by hand) is NOT sufficient. Runtime check before finalizing: "Has a tool confirmed this move's immediate outcome and the opponent's strongest reply THIS turn?" If no, call the tool before writing `<action>`.

**Always pass a valid move argument.** Never call `<safety>`, `<threats>`, or `<simulate>` with an empty or missing move argument — this wastes budget and can incur a penalty without producing evidence. Confirm the candidate move string is set before issuing the call.

**Price every check before committing, not just its check status.** A move being a check does not guarantee safety — even `+`-flagged moves can be met by a capture that loses material. Before committing to any check, mentally play the opponent's most dangerous reply (capture or block) and calculate net material change; if negative, abandon the candidate and search alternatives rather than committing on the strength of the check alone.
## Comparing Candidates

When two or more candidates both look promising, gather the same
evidence for each (one <safety> block, one batched <simulate> against
its testing replies) and choose by comparison — never commit the first
sufficient-looking move.


If a candidate remains on your shortlist after the opponent replies, do not reuse its prior evaluation — call `<simulate>` with the opponent's actual reply to confirm the material outcome before committing to or retrying that candidate.

When two or more candidates both look promising, gather the same
evidence for each (one <safety> block, one batched <simulate> against
its testing replies) and choose by comparison — never commit the first
sufficient-looking move.

Even when only one candidate feels clearly best, before locking it in run `<safety>` on at least one other forcing legal move (another check, capture, or threat) from the list. If that tool call flags a danger (en prise, losing exchange, strong reply) on your leading candidate's rival, or reveals the rival has a clearly superior verified outcome, pivot to it; otherwise confirm and commit your original choice. Do not skip this audit just because the first candidate looked obviously correct.

Once a candidate is verified as forcing a win or mate, do not cycle back to weaker/quiet candidates you already generated or half-analyzed — discard them and commit. Do not second-guess a tool-verified forcing solution based on annotations, hunches, or re-reading; only reopen the decision if simulation or board inspection surfaces a concrete defensive resource the tool missed.
## Judging Tool Output

Treat `<safety>` flags of `en prise` (your pieces) or `[LOSING EXCHANGE RISK]` as a hard gatekeeper, not a warning to weigh: discard the candidate immediately and move to the next legal move rather than manually calculating through or mentally overriding what the tool reported (exception: forcing candidates — see Verifying the Move, where a simulated forced line can override a raw exchange warning). Conversely, when a tool call reports a candidate is clean, commit or promote it to comparison — do not manually re-simulate pawn races, king walks, or material counts to double-check a verdict the tool already gave; that is redundant and wastes turns. Limit yourself to one tool call per candidate for the initial verdict; call it again only when comparing against another equally strong candidate (see Comparing Candidates).

Treat `<safety>` flags of `en prise` (your pieces) or `[LOSING EXCHANGE RISK]` as a hard gatekeeper for quiet (non-forcing) candidates: discard immediately rather than manually calculating through or overriding what the tool reported. For a *forcing* candidate (check, or a capture removing a key defender) that gets flagged, do not discard on the raw flag alone — explicitly weigh the flagged risk against the tactical objective (forced mate, king exposure, decisive material) using a `<simulate>` line, and state that weighing in your reasoning before committing or discarding. Runtime check: "Does my decision explicitly name the flag the tool returned and say why it does or doesn't matter here?"


**Own-piece en prise is also a hard stop.** If `<board>` or `<safety>` output flags any of your own pieces (including the piece you are about to move) as `en prise`, `under attack`, or `hanging`, treat it as mandatory: before committing that candidate, verify a defender, safe retreat, or forcing justification exists. Never claim a tool is "inaccessible" or unavailable to justify skipping this check — if a tool call already returned output, that output is available and must be used; re-issue the call if you are unsure, but do not proceed on unverified intuition when a safety flag is sitting in front of you.
## Converting the Line (Second Move)

For any candidate that starts a forcing sequence (capture chain, check chain, or suspected tactic), call `<line>` with the candidate move plus up to five anticipated opponent replies and verify the resulting material/status before committing. Do not judge a multi-move tactic using only single-move `<safety>` checks — isolated checks miss deeper refutations that only a full simulated line exposes.

## Budget Discipline



## Common Pitfalls


