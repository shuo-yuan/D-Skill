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

- **Never bypass tools for non-trivial lines:** Do not rely on manual FEN parsing, heuristic guesses, or mental geometry. Every non-trivial candidate MUST be passed to `<safety>`, `<line>`, or `<simulate>` before commitment.
- **Never bypass tools for explicit mates:** Even if the legal-move list tags a candidate with `#`, you MUST run `<safety>` or `<line>` to get an objective confirmation (e.g., explicit "CHECKMATE" flag). Do not commit based on the `#` suffix alone; text annotations can be misleading or the position may contain hidden defenses.
- **Tool output is ground truth:** Treat the tool's explicit response as the final arbiter. Do not rely on internal mental calculation, FEN parsing, or suffixes to verify forcing outcomes.
- **Runtime check:** "Before committing, have I run this candidate through `<safety>` or `<line>` to get an objective result? If I am only thinking through variations or relying on formatting, I will call the tool immediately."

- **Never bypass tools for non-trivial lines or explicit mates (`#`):** Do not rely on mental calculation, FEN parsing, or suffixes. Every candidate MUST be passed to `<safety>`, `<line>`, or `<simulate>` for objective confirmation.
- **Tool output is ground truth:** Treat tool flags as final. Do not override with mental geometry or heuristic guesses.
- **Runtime check

- **Never bypass tools for non-trivial lines or explicit mates (`#`):** Do not rely on mental calculation, FEN parsing, or suffixes. Every candidate MUST be passed to `<safety>`, `<line>`, or `<simulate>` for objective confirmation.
- **Tool output is ground truth:** Treat tool flags as final. Do not override with mental geometry or heuristic guesses.
- **Runtime check:** "Before committing, have I run this candidate through `<safety>` or `<line>` to get an objective result? If I am only thinking through variations or relying on formatting, I will call the tool immediately."
## Finding the Move: Motifs and Candidates


- **Force-first ordering:** Immediately filter the legal-move list for moves tagged with `#` or `+`. Queue these flagged moves for tool verification before considering any other candidates. Do not manually scan or generate quiet moves first.
- **Threat-first filtering:** Call `<threats>` early. Narrow candidates to 2–4 moves that neutralize the opponent's strongest forcing reply or create a stronger counter-threat.
- **Check response:** When in check, filter the legal-move list to only block, capture the attacker, or move the king. Discard other candidates before deep calculation.
- **Threat neutralization:** Verify if a candidate directly addresses an opponent threat (vacating attacked squares or blocking lines). If a tool reports a threat, neutralization is instant; do not simulate opponent captures on squares your piece has already left.
- **Runtime check:** "When scanning the legal-move list, do I immediately filter for moves tagged with `#` or `+` and queue them for tool verification before considering other moves?"

- **Scan printed board, not FEN:** Immediately scan the printed board and legal-move list for tactical motifs. Do NOT manually parse, count, or list pieces from the FEN string.
- **Pre-move position reading:** Before generating candidates, explicitly note piece locations, material balance, and all immediate tactical targets (checks, captures, threats). Confirm at least three visible tactical targets on the board before narrowing to a candidate.
- **Baseline material check:** Call `<hanging>` immediately at the start of analysis to catalog all en-prise pieces for both sides. Use this output to supplement your candidate list, but treat it as one input among many rather than the sole driver of move selection.
- **Runtime check

- **Explicit Position Grounding:** At the very start of analysis, print the exact material count and state "Last move: [move]". Anchor all candidate generation in this concrete state before scanning for tactics.
- **Candidate-first tool usage:** Never call `<safety>` or `<threats>` on the raw position. Draft a concrete forcing line first ("Candidate: [Move]. Forcing nature: [Check/Capture/Threat]. If opponent replies [Reply], I will follow up with [Move].") before running any tools. Use `<hanging>` and `<safety>` to filter the legal-move list, discarding losing sacrifices and isolating 2–4 forcing candidates.
- **Force-first ordering:** Immediately filter the legal-move list for moves tagged with `#`, `+`, or `=`. Designate the annotated move as your primary candidate and skip deep analysis of other legal moves until this candidate is verified or refuted by a tool. Queue it for verification before considering any other candidates.
- **Threat-first filtering:** Call `<threats>` early. Narrow candidates to 2–4 moves that neutralize the opponent's strongest forcing reply or create a stronger counter-threat.
- **Check response:** When in check, filter the legal-move list to only block, capture the attacker, or move the king. Discard other candidates before deep calculation.
- **Threat neutralization:** Verify if a candidate directly addresses an opponent threat (vacating attacked squares or blocking lines). If a tool reports a threat, neutralization is instant; do not simulate opponent captures on squares your piece has already left.
- **Scan printed board, not FEN:** Immediately scan the printed board and legal-move list for tactical motifs. Do NOT manually parse, count, or list pieces from the FEN string.
- **Pre-move position reading:** Before generating candidates, explicitly note piece locations, material balance, and all immediate tactical targets (checks, captures, threats). Confirm at least three visible tactical targets on the board before narrowing to a candidate.
- **Mandatory Initialization:** Always call `<hanging>` before generating candidates. Use the output to establish the tactical baseline. Do not begin manual reasoning or coordinate scanning until `<hanging>` has run.
- **Forcing-only candidate pool:** Generate candidates exclusively from checks, captures, and direct threats. Discard quiet/retreating moves until all forcing lines are verified or exhausted.
- **Puzzle heuristic & dual-target prioritization:** When the prompt implies a "clearly best move" or tactical puzzle, treat forcing checks and captures as the primary solution path. Prioritize candidates that attack multiple pieces, combine a check with a secondary threat, or severely restrict the opponent's king.
- **Runtime check:** "Did I scan the legal move list for `+`, `#`, or `=` symbols before generating candidates? If found, treat it as the primary candidate and verify with a tool before analyzing quieter moves."

- **Mandatory Initialization:** Always call `<hanging>` and `<threats>` immediately. Map all `en prise` pieces and opponent threats before generating candidates.
- **Explicit Position Grounding:** At the start, print exact material count and "Last move: [move]". Anchor candidate generation in this concrete state.
- **Scan printed board, not FEN:** Read piece locations and tactical motifs from the printed board. Do NOT manually parse, count, or list pieces from the FEN string.
- **Force-first ordering:** Immediately filter the legal-move list for moves tagged with `#`, `+`, or `=`. Queue these flagged moves for tool verification before considering any other candidates.
- **Strict quiet-move ban:** DO NOT evaluate, calculate, or mention quiet/retreating moves until every forcing candidate has been explicitly verified or refuted by a tool.
- **Puzzle heuristic:** When the prompt implies a tactical puzzle, treat forcing checks and captures as the primary solution path. Prioritize candidates that attack multiple pieces or combine a check with a secondary threat.
- **Runtime check:** "Did I call `<hanging>` and `<threats>`, scan the printed board, split moves into forcing vs. quiet, and verify all forcing candidates before considering any quiet ones?"

- **Mandatory Initialization:** Always call `<hanging>` and `<threats>` immediately at the start. Map all `en prise` pieces and opponent threats before generating candidates.
- **Tool-first baseline:** Never fixate on a heuristic candidate or begin deep mental calculation without first calling `<hanging>` and `<threats>`. Use tool output to quantify en-prise status, attacker/defender ratios, and opponent threats before narrowing your candidate pool.
- **Explicit Position Grounding:** Print exact material count and "Last move: [move]". Anchor candidate generation in this concrete state.
- **Scan printed board, not FEN:** Read piece locations and tactical motifs from the printed board. Do NOT manually parse, count, or list pieces from the FEN string.
- **Force-first ordering:** Immediately filter the legal-move list for moves tagged with `#`, `+`, or `=`. Queue these flagged moves for tool verification before considering any other candidates.
- **Strict quiet-move ban:** DO NOT evaluate, calculate, or mention quiet/retreating moves until every forcing candidate has been explicitly verified or refuted by a tool.
- **Check response:** When in check, filter the legal-move list to only block, capture the attacker, or move the king. Discard other candidates before deep calculation.
- **Instant Capture Filter:** When evaluating a capture candidate, instantly check if it loses material or walks into a trap. Discard these blunders in under 5 seconds without calling a tool. Do not let this filter paralyze your search; immediately pivot to checks, sacrifices, or the next forcing candidate.
- **Puzzle heuristic:** When the prompt implies a tactical puzzle, treat forcing checks and captures as the primary solution path. Prioritize candidates that attack multiple pieces or combine a check with a secondary threat.
- **Runtime check:** "Did I call `<hanging>` and `<threats>`, scan the printed board, split moves into forcing vs. quiet, and verify all forcing candidates before considering any quiet ones?"

- **Mandatory Initialization:** Always call `<hanging>` and `<threats>` immediately. Map all `en prise` pieces and opponent threats before generating candidates. Never begin manual reasoning until tools have run.
- **Explicit Position Grounding:** Print exact material count and "Last move: [move]". Anchor candidate generation in this concrete state.
- **Verify King Safety First:** Before generating candidates, explicitly locate the enemy King on the printed board and map its escape squares. Do not proceed until you have confirmed its exact coordinates.
- **Scan printed board, not FEN:** Read piece locations and tactical motifs from the printed board. Do NOT manually parse, count, or list pieces from the FEN string.
- **Force-first ordering & Suffix Prioritization:** Immediately filter the legal-move list for moves tagged with `#`, `+`, or `=`. Treat these symbols as direct candidate prioritization signals: sort all forcing moves to the front of your verification queue.
- **Strict quiet-move ban:** DO NOT evaluate, calculate, or mention quiet/retreating moves until every forcing candidate has been explicitly verified or refuted by a tool.
- **Forcing tempo overrides defense:** When a piece is under attack, DO NOT default to passive saving moves. Immediately scan for checks, captures, and direct threats. If a forcing move creates a decisive counter-threat, commit to it regardless of `[LOSING EXCHANGE RISK]` flags.
- **Avoid material-grabbing distractions:** When a checking candidate restricts the opponent's king or creates tactical complications, verify its forcing nature against all legal replies BEFORE considering quiet or purely material-gaining moves.
- **Ignore static material accounting:** When evaluating forcing candidates, focus on king restriction, piece coordination, and forcing sequences. Do NOT get bogged down in static material counts, exchange estimates, or endgame projections unless a line forces a decisive material win.
- **Check response:** When in check, filter to only block, capture the attacker, or move the king. Discard other candidates before deep calculation.
- **Puzzle heuristic:** When the prompt implies a tactical puzzle, treat forcing checks and captures as the primary solution path. Prioritize candidates that attack multiple pieces, combine a check with a secondary threat, or severely restrict the opponent's king.
- **Runtime check:** "Did I call `<hanging>` and `<threats>`, verify the enemy King's location, split moves into forcing vs. quiet, and verify all forcing candidates before considering any quiet ones?"

- **Mandatory Initialization:** Always call `<hanging>` and `<threats>` immediately. Map all `en prise` pieces and opponent threats before generating candidates. Never begin manual reasoning until tools have run.
- **Explicit Position Grounding & Parsing:** At the start, print exact material count and "Last move: [move]". Explicitly list 2-3 critical structural features and tactical motifs (e.g., overloaded defender, back rank) before generating candidates. Anchor your candidate list in this concrete state.
- **Scan printed board, not FEN:** Read piece locations and tactical motifs from the printed board. Do NOT manually parse, count, or list pieces from the FEN string.
- **Systematic Categorization & Force-first ordering:** Parse the legal move list into clear categories: checks, captures, threats, and quiet moves. Immediately filter for moves tagged with `#`, `+`, or `=`. Queue these flagged moves for tool verification before considering any other candidates.
- **Strict quiet-move ban:** DO NOT evaluate, calculate, or mention quiet/retreating moves until every forcing candidate has been explicitly verified or refuted by a tool.
- **Threat-first filtering & Neutralization:** Explicitly register opponent threats (`<threats>` output) before launching attacks. Ensure your candidate does not leave your king or major pieces unprotected. If a tool reports a threat, neutralization is instant; do not simulate opponent captures on squares your piece has already left.
- **Override material panic & deficit directive:** DO NOT manually calculate material trades to judge viability. Treat material deficits as secondary to king safety and forcing constraints. When starting with a noted material deficit or explicit "tactics" prompt, explicitly state that you must find a forcing line that changes the material balance or checkmates the opponent. Verify your first three candidates are all checks, captures, or direct threats.
- **Puzzle heuristic:** When the prompt implies a tactical puzzle, treat forcing checks and captures as the primary solution path. Prioritize candidates that attack multiple pieces, combine a check with a secondary threat, or severely restrict the opponent's king.
- **Runtime check:** "Did I call `<hanging>` and `<threats>`, ground my analysis in the literal board state, split moves into forcing vs. quiet, and verify all forcing candidates before considering any quiet ones?"

- **Mandatory Initialization:** Always call `<hanging>` and `<threats>` immediately. Map all `en prise` pieces and opponent threats before generating candidates. Never begin manual reasoning until tools have run.
- **Explicit Position Grounding:** Print exact material count and "Last move: [move]". Anchor candidate generation in this concrete state.
- **Scan printed board, not FEN:** Read piece locations and tactical motifs from the printed board. Do NOT manually parse, count, or list pieces from the FEN string.
- **Methodical Candidate Enumeration:** Systematically scan the full legal-move list. Explicitly call out every check, capture, and direct threat by name. Group candidates by tactical motif to ensure thorough coverage.
- **Force-first ordering & Strict quiet-move ban:** Immediately filter the legal-move list for moves tagged with `#`, `+`, or `=`. Queue these flagged moves for tool verification before considering any other candidates. DO NOT evaluate, calculate, or mention quiet/retreating moves until every forcing candidate has been explicitly verified or refuted by a tool.
- **Check Response Protocol:** When in check, filter to only block, capture the attacker, or move the king. Discard other candidates before deep calculation.
- **Puzzle Heuristic:** When the prompt implies a tactical puzzle, treat forcing checks and captures as the primary solution path. Prioritize candidates that restrict the king or combine checks with secondary threats.
- **Pre-commit legality check:** Before calling tools or committing, verify that your chosen move's piece type and destination are explicitly listed in the provided legal-move list. If it's not listed, discard it and re-evaluate.
- **Runtime check:** "Did I call `<hanging>` and `<threats>`, scan the printed board, enumerate all checks/captures/threats, split moves into forcing vs. quiet, and verify all forcing candidates before considering any quiet ones?"

- **Mandatory Initialization:** Always call `<hanging>` and `<threats>` immediately at the start. Map all `en prise` pieces and opponent threats before generating candidates. Never begin manual reasoning until tools have run.
- **Explicit Position Grounding:** Print exact material count and "Last move: [move]". Anchor candidate generation in this concrete state. Treat material counts as fixed; do not re-sum piece values.
- **Scan printed board, not FEN:** Read piece locations and tactical motifs from the printed board. Do NOT manually parse, count, or list pieces from the FEN string.
- **Force-first ordering & Strict quiet-move ban:** Immediately filter the legal-move list for moves tagged with `#`, `+`, or `=`. Queue these flagged moves for tool verification before considering any other candidates. DO NOT evaluate, calculate, or mention quiet/retreating moves until every forcing candidate has been explicitly verified or refuted.
- **Check response:** When in check, filter to only block, capture the attacker, or move the king. Discard other candidates before deep calculation.
- **Puzzle heuristic:** When the prompt implies a tactical puzzle, treat forcing checks and captures as the primary solution path. Prioritize candidates that attack multiple pieces, combine a check with a secondary threat, or severely restrict the opponent's king.
- **Forcing tempo overrides defense:** When a piece is under attack, DO NOT default to passive saving moves. Immediately scan for checks, captures, and direct threats.
- **Runtime check:** "Did I call `<hanging>` and `<threats>`, scan the printed board, split moves into forcing vs. quiet, and verify all forcing candidates before considering any quiet ones?"

- **Mandatory Initialization:** Always call `<hanging>` and `<threats>` immediately. Map all `en prise` pieces and opponent threats before generating candidates. Never begin manual reasoning until tools have run.
- **Rapid Position Categorization:** Before generating candidates, explicitly categorize the position as tactical, quiet, or endgame. For tactical positions, immediately filter the legal-move list into forcing moves (checks/captures) versus quiet moves. Never waste tool budget on quiet moves when a forcing sequence is required.
- **Explicit Position Grounding:** Print exact material count and "Last move: [move]". Anchor candidate generation in this concrete state.
- **Board-First Scanning:** Read piece locations and tactical motifs from the printed board. NEVER manually parse, count, or list pieces from the FEN string. Treat material counts as fixed; do not re-sum piece values.
- **Systematic Motif Scanning & Force-First Ordering:** Explicitly extract EVERY legal check, capture (`x`), and direct threat from the legal-move list. Queue these flagged moves (`#`, `+`, `x`, `=`) for tool verification before considering any other candidates.
- **Strict Quiet-Move Ban:** DO NOT evaluate, calculate, or mention quiet/retreating moves until every forcing candidate has been explicitly verified or refuted by a tool.
- **Check Response:** When in check, filter to only block, capture the attacker, or move the king. Discard other candidates before deep calculation.
- **Puzzle Heuristic:** When the prompt implies a tactical puzzle, treat forcing checks and captures as the primary solution path. Prioritize candidates that restrict the king, combine checks with secondary threats, or attack multiple pieces.
- **Runtime Check:** "Did I categorize the position, call `<hanging>`/`<threats>`, scan the printed board, extract every check/capture/threat, and queue all forcing candidates before considering quiet ones?"
## Verifying the Move: Tool Ritual


- **Mandatory Verification Sequence:** For any forcing candidate (check, capture, or mate threat), you MUST run `<board>` followed by `<safety>` or `<line>` before committing. Explicitly check tool output for `[LOSING EXCHANGE RISK]` or pieces left `en prise`. Do not commit until the tool confirms tactical soundness.
- **Escape/Capture/Block Triad:** For every forcing candidate (`#` or `+`), explicitly confirm: (1) **Escape**: systematically list every adjacent square to the opponent king and verify it is covered, blocked, or off-board; (2) **Capture**: the attacking piece cannot be captured (or is protected); (3) **Block**: no interposition is possible. Run this triad immediately after calling `<safety>` or `<simulate>`. Do not manually count escape squares or trace piece coverage.
- **Tool Validation:** Trust the tool's `"gives check"` flag and `"opponent legal replies"` count. Use these to gauge how forced the line is; if replies exist, verify the triad holds against each.
- **Pre-commitment Safety:** Before locking in, verify geometric legality, destination safety, and that opponent checks/captures cannot bypass your threat.
- **Runtime check:** "Does my candidate create a check, capture, or direct threat? If yes, run `<board>` then `<safety>` immediately to confirm forcing nature and opponent responses."

- **Prioritize `<line>` for forcing sequences:** Before evaluating non-forcing candidates with `<safety>` or `<hanging>`, always use `<line>` to verify checking, capturing, or sacrificing moves. This prevents missing forced solutions by avoiding distraction from material warnings on quiet moves.
- **Bundle forcing replies:** When verifying a check, capture, or major threat, list every plausible opponent reply in a single `<simulate>` call. Compare material outcomes across all branches in one read-through. Do not call tools separately for each branch or calculate variations mentally.
- **Pre-commit gate:** Before writing any `<action>` tag, verify that you have already executed at least one tool call (`<safety>`, `<simulate>`, or `<board>`) to audit the chosen move. If no tool has run, halt and call one immediately; never commit based on mental reconstruction or FEN parsing alone.

- **Mandatory Verification Sequence:** For any forcing candidate (check, capture, or mate threat), you MUST run `<board>` followed by `<safety>` or `<line>` before committing. **If the tool flags a forcing move with `[LOSING EXCHANGE RISK]` or an unfavorable attacker/defender ratio, DO NOT abandon it.** Immediately run `<line>` or `<simulate>` to trace the forced reply and verify if it leads to checkmate, decisive follow-up, or critical square clearance. Do not commit until the tool confirms tactical soundness.
- **Escape/Capture/Block Triad:** For every forcing candidate (`#` or `+`), explicitly confirm: (1) **Escape**: systematically list every adjacent square to the opponent king and verify it is covered, blocked, or off-board; (2) **Capture**: the attacking piece cannot be captured (or is protected); (3) **Block**: no interposition is possible. Run this triad immediately after calling `<safety>` or `<simulate>`. Do not manually count escape squares or trace piece coverage.
- **Tool Validation:** Trust the tool's `"gives check"` flag and `"opponent legal replies"` count. Use these to gauge how forced the line is; if replies exist, verify the triad holds against each.
- **Pre-commitment Safety:** Before locking in, verify geometric legality, destination safety, and that opponent checks/captures cannot bypass your threat.
- **Prioritize `<line>` for forcing sequences:** Before evaluating non-forcing candidates with `<safety>` or `<hanging>`, always use `<line>` to verify checking, capturing, or sacrificing moves. This prevents missing forced solutions by avoiding distraction from material warnings on quiet moves.
- **Bundle forcing replies:** When verifying a check, capture, or major threat, list every plausible opponent reply in a single `<simulate>` call. Compare material outcomes across all branches in one read-through. Do not call tools separately for each branch or calculate variations mentally.
- **Simulate all replies & plan follow-up:** When a candidate is a check or capture, run `<simulate>` against *all* listed legal replies. Do not assume the move is bad just because a piece appears to hang; verify the forced king movement or material win that follows. Explicitly state the concrete next step before committing.
- **Verify delayed payoffs & flight squares:** When a candidate appears to sacrifice material, explicitly trace the full forcing line to confirm the final outcome. For checking moves, verbally enumerate the king's flight squares and match each to a covering piece or obstruction. If you cannot justify one square's status, pause and call `<line>` or `<board>` to verify.
- **Mandatory Pre-commit Simulation:** Before outputting `<action>`, you MUST run `<simulate>` pairing your candidate move with the opponent's strongest reply. Never output `<action>` based on mental simulation, text-based calculation, or FEN parsing alone.

- **Mandatory Verification Sequence:** For any forcing candidate, run `<board>` followed by `<safety>` or `<line>` before committing. Explicitly check tool output for `[LOSING EXCHANGE RISK]` or pieces left `en prise`.
- **Handle flagged risks correctly:** If the tool flags `[LOSING EXCHANGE RISK]` or `en prise` on a check/capture, DO NOT abandon it immediately. Run `<simulate>` or `<line>` against the opponent's strongest forcing reply to calculate the exact tactical payoff. Only discard if the tool confirms a fatal refutation.
- **Bundle forcing replies:** List every plausible opponent reply in a single `<simulate>` call. Compare material outcomes across all branches in one read-through. Do not call tools separately for each branch.
- **Escape/Capture/Block Triad:** For every forcing candidate (`#` or `+`), explicitly confirm: (1) **Escape**: adjacent king squares are covered/blocked/off-board; (2) **Capture**: attacker is protected or cannot be captured; (3) **Block**: no interposition is possible. Run this immediately after tool output.
- **Pre-commit gate:** Before writing `<action>`, verify that you have already executed at least one tool call (`<safety>`, `<simulate>`, or `<board>`) to audit the chosen move. Never commit based on mental simulation or FEN parsing alone.
- **Runtime check:** "Does my candidate create a check, capture, or direct threat? If yes, have I run `<board>` then `<safety>` or `<line>` to confirm forcing nature and opponent responses before committing?"

- **Mandatory Verification Sequence:** For any forcing candidate (check, capture, or mate threat) that is NOT an unambiguous mate-in-1, run `<board>` followed by `<safety>` or `<line>` before committing.
- **Handle flagged risks correctly:** If the tool flags `[LOSING EXCHANGE RISK]` or `en prise` on a check/capture, DO NOT abandon it immediately. Run `<simulate>` or `<line>` against the opponent's strongest forcing reply to calculate the exact tactical payoff. Only discard if the tool confirms a fatal refutation.
- **Bundle forcing replies:** List every plausible opponent reply in a single `<simulate>` call. Compare material outcomes across all branches in one read-through. Do not call tools separately for each branch.
- **Escape/Capture/Block Triad:** For every forcing candidate (`#` or `+`), explicitly confirm: (1) **Escape**: adjacent king squares are covered/blocked/off-board; (2) **Capture**: attacker is protected or cannot be captured; (3) **Block**: no interposition is possible. Run this immediately after tool output.
- **Forced response material evaluation:** When forced to respond to a check or direct threat, immediately list all legal replies and compare their material outcomes. Prioritize captures that eliminate the attacking piece and recover lost value.
- **Objective filtering via tool output:** When evaluating multiple checks/captures, explicitly compare them using `<safety>`/`<line>` output fields. Discard candidates with `[LOSING EXCHANGE RISK]` or `opponent legal replies > 2`. Select the candidate that minimizes opponent options and shows zero `en prise` warnings.
- **Discard refuted candidates immediately:** When a candidate is identified as refuted or tactically unsound, immediately discard it. Do not attempt to rationalize the move; move directly to the next candidate in your prioritized list.
- **Pre-commit gate:** Before writing `<action>`, verify that you have already executed at least one tool call (`<safety>`, `<simulate>`, or `<board>`) to audit the chosen move. Never commit based on mental simulation or FEN parsing alone.

- **Mandatory Verification Sequence:** For any forcing candidate (check, capture, promotion, or mate threat) that is NOT an unambiguous mate-in-1, run `<board>` followed by `<safety>` or `<line>` before committing.
- **Candidate-specific verification:** `<threats>` only shows opponent responses if you pass. To verify a candidate, you MUST call `<safety>[move]` or `<simulate>[move]`. Before relying on any output, ask: "Does this show how the opponent responds to MY candidate, or only threats if I pass?" If it only shows passing threats, discard it for candidate evaluation and call `<safety>` on the move.
- **Bundle forcing replies:** List every plausible opponent reply in a single `<simulate>` call. Compare material outcomes across branches in one read-through. Do not call tools separately for each branch.
- **Handle flagged risks correctly:** If the tool flags `[LOSING EXCHANGE RISK]` or `en prise` on a forcing move, DO NOT abandon it immediately. Treat as forced-sequence indicator. Run `<simulate>` or `<line>` against the opponent's strongest reply to trace the exact tactical payoff. Only discard if the tool confirms a fatal refutation.
- **Escape/Capture/Block Triad:** For every forcing candidate (`#` or `+`), explicitly confirm: (1) **Escape**: adjacent king squares are covered/blocked/off-board; (2) **Capture**: attacker is protected or cannot be captured; (3) **Block**: no interposition is possible. Run this immediately after tool output.
- **Pre-commit gate:** Before writing `<action>`, verify that you have already executed at least one tool call (`<safety>`, `<simulate>`, or `<board>`) to audit the chosen move. Never commit based on mental simulation or FEN parsing alone.
- **Uninterrupted Verification Pass:** When verifying a forcing candidate, list all opponent responses (escape squares, captures, blocks) in a single, uninterrupted pass. Do not self-correct, backtrack, or re-scan mid-verification. If a discrepancy arises, halt and call `<board>` or `<safety>` to resolve it before continuing.
- **Discard refuted candidates immediately:** When a candidate is identified as refuted or tactically unsound, immediately discard it. Move directly to the next candidate in your prioritized list.
- **Runtime check:** "Does my candidate create a check, capture, or direct threat? If yes, have I run `<board>` then `<safety>` or `<line>` to confirm forcing nature and opponent responses before committing?"

- **Mandatory Verification Sequence:** For any forcing candidate (check, capture, promotion, or mate threat) that is NOT an unambiguous mate-in-1, run `<board>` followed by `<safety>` or `<line>` before committing.
- **Candidate-specific verification:** `<threats>` only shows opponent responses if you pass. To verify a candidate, you MUST call `<safety>[move]` or `<simulate>[move]`. Before relying on any output, ask: "Does this show how the opponent responds to MY candidate, or only threats if I pass?" If it only shows passing threats, discard it for candidate evaluation and call `<safety>` on the move.
- **Handle flagged risks correctly:** If the tool flags `[LOSING EXCHANGE RISK]` or `en prise` on a forcing move, DO NOT abandon it immediately. Treat it as a forced-sequence indicator. Run `<simulate>` or `<line>` against the opponent's strongest reply to trace the exact tactical payoff. Only discard if the tool confirms a fatal refutation.
- **Bundle forcing replies:** List every plausible opponent reply in a single `<simulate>` call. Compare material outcomes across all branches in one read-through. Do not call tools separately for each branch.
- **Pin & Legality Check on Defenders:** When a candidate involves a capture or check that could be met by a defender, explicitly verify if that defender is pinned, overloaded, or otherwise illegal to move. Do not assume a capture is legal based on visual inspection; run `<safety>` to confirm pin status and capture legality automatically.
- **Escape/Capture/Block Triad:** For every forcing candidate (`#` or `+`), explicitly confirm: (1) **Escape**: adjacent king squares are covered/blocked/off-board; (2) **Capture**: attacker is protected or cannot be captured; (3) **Block**: no interposition is possible. Run this immediately after tool output.
- **Pre-commit gate:** Before writing `<action>`, verify that you have already executed at least one tool call (`<safety>`, `<simulate>`, or `<board>`) to audit the chosen move. Never commit based on mental simulation or FEN parsing alone.

- **Mandatory Verification Sequence:** For any forcing candidate (check, capture, or mate threat) that is NOT an unambiguous mate-in-1, run `<board>` followed by `<safety>` or `<line>` before committing.
- **Handle Risk Flags Correctly:** If the tool flags `[LOSING EXCHANGE RISK]` or `en prise` on a forcing move, DO NOT abandon it immediately. Treat as a forced-sequence indicator. Run `<simulate>` or `<line>` against the opponent's strongest reply to trace the exact tactical payoff. Only discard if the tool confirms a fatal refutation.
- **Escape/Capture/Block Triad:** For every forcing candidate (`#` or `+`), explicitly confirm: (1) **Escape**: adjacent king squares are covered/blocked/off-board; (2) **Capture**: attacker is protected or cannot be captured; (3) **Block**: no interposition is possible. Run this immediately after tool output.
- **Bundle Forcing Replies:** List every plausible opponent reply in a single `<simulate>` call. Compare material outcomes across branches in one read-through. Do not call tools separately for each branch.
- **Pre-commit Gate:** Before writing `<action>`, verify that you have already executed at least one tool call (`<safety>`, `<simulate>`, or `<board>`) to audit the chosen move. Never commit based on mental simulation or FEN parsing alone.
- **Commit on forcing confirmation:** If `<safety>` reports `forcing replies: none` and zero defenders at the destination, commit immediately. Do not manually simulate opponent replies, switch candidates, or call additional tools on speculative traps.

- **Mandatory Verification Sequence:** For any forcing candidate (check, capture, promotion, or mate threat) that is NOT an unambiguous mate-in-1, run `<board>` followed by `<safety>` or `<line>` before committing.
- **Candidate-specific verification:** `<threats>` only shows opponent responses if you pass. To verify a candidate, you MUST call `<safety>[move]` or `<simulate>[move]`. If the output only shows passing threats, discard it for candidate evaluation and call `<safety>` on the move.
- **Handle flagged risks correctly:** If the tool flags `[LOSING EXCHANGE RISK]` or `en prise` on a forcing move, DO NOT abandon it immediately. Treat it as a forced-sequence indicator. Run `<simulate>` or `<line>` against the opponent's strongest reply to trace the exact tactical payoff. Only discard if the tool confirms a fatal refutation.
- **Bundle forcing replies:** List every plausible opponent reply in a single `<simulate>` call. Compare material outcomes across branches in one read-through. Do not call tools separately for each branch.
- **Escape/Capture/Block Triad:** For every forcing candidate (`#` or `+`), explicitly confirm: (1) **Escape**: adjacent king squares are covered/blocked/off-board; (2) **Capture**: attacker is protected or cannot be captured; (3) **Block**: no interposition is possible. Run this immediately after tool output.
- **Pin & Legality Check:** When a candidate involves a capture or check that could be met by a defender, explicitly verify if that defender is pinned, overloaded, or otherwise illegal to move. Do not assume a capture is legal based on visual inspection.
- **Pre-commit gate:** Before writing `<action>`, verify that you have already executed at least one tool call (`<safety>`, `<simulate>`, or `<board>`) to audit the chosen move. Never commit based on mental simulation or FEN parsing alone.

- **Mandatory Verification Sequence:** For any forcing candidate (check, capture, promotion, or mate threat) that is NOT an unambiguous mate-in-1, run `<board>` followed by `<safety>` or `<line>` before committing.
- **Handle Risk Flags Correctly:** If the tool flags `[LOSING EXCHANGE RISK]` or `en prise` on a forcing move, DO NOT abandon it immediately. Treat it as a forced-sequence indicator. Run `<simulate>` or `<line>` against the opponent's strongest reply to trace the exact tactical payoff. Only discard if the tool confirms a fatal refutation.
- **Bundle Forcing Replies:** List every plausible opponent reply in a single `<simulate>` call. Compare material outcomes across branches in one read-through. Do not call tools separately for each branch.
- **Escape/Capture/Block Triad:** For every forcing candidate (`#` or `+`), explicitly confirm: (1) **Escape**: adjacent king squares are covered/blocked/off-board; (2) **Capture**: attacker is protected or cannot be captured; (3) **Block**: no interposition is possible. Run this immediately after tool output.
- **Candidate-Specific Verification:** `<threats>` only shows opponent responses if you pass. To verify a candidate, you MUST call `<safety>[move]` or `<simulate>[move]`. If the output only shows passing threats, discard it for candidate evaluation and call `<safety>` on the move.
- **Pin & Legality Check:** When a candidate involves a capture or check that could be met by a defender, explicitly verify if that defender is pinned, overloaded, or otherwise illegal to move. Do not assume a capture is legal based on visual inspection.
- **Geometric Line-of-Sight & Pin Verification:** Before calculating a capture or pin, explicitly verify that the attacking piece's path is geometrically clear and that the piece is not pinned to a more valuable unit. Trace the exact line from attacker to target and confirm no intervening pieces block it.
- **Pre-Commit Gate:** Before writing `<action>`, verify that you have already executed at least one tool call (`<safety>`, `<simulate>`, or `<board>`) specifically for your chosen candidate. Never finalize a move based on mental verification or visual inspection alone.
- **Runtime Check:** "Does my candidate create a check, capture, or direct threat? If yes, have I run `<board>` then `<safety>`/`<line>` to confirm forcing nature and opponent responses before committing?"
## Comparing Candidates

- **Verify forcing first:** Before batching or evaluating quiet moves, run `<safety>` or `<simulate>` on the single most forcing candidate. If it succeeds, commit immediately. Do not linger on manual calculations of quiet moves or second-guess the forcing line.
- **Batch only if needed:** Only call `<safety>` on a batch of candidates if the primary forcing move fails verification or if multiple forcing moves exist. Rank them strictly by the tool's flags: prefer moves with `en prise: none`, `attackers ≤ defenders` at the destination, and `forcing replies: yes`.
- **Runtime Check:** After calling `<safety>`, explicitly match each candidate to its `en prise` status and attacker/defender ratio before choosing; only commit a move that has zero `enprise` warnings and favorable defender counts.

- **Batch only if needed:** Only call `<safety>` on a batch of candidates if the primary forcing move fails verification or if multiple forcing moves exist. Rank them strictly by forcing nature first, then tool flags. **If a candidate is abandoned after tool verification, immediately pivot to the next FORCING candidate. NEVER drift into quiet maneuvering when forcing options remain.**
- **Runtime Check:** After calling `<safety>`, explicitly match each candidate to its `en prise` status and attacker/defender ratio before choosing; only commit a move that has zero `enprise` warnings and favorable defender counts.

- **Verify forcing first:** Before batching or evaluating quiet moves, run `<safety>` or `<simulate>` on the single most forcing candidate. If it succeeds, commit immediately.
- **Batch only if needed:** Only call `<safety>` on a batch of candidates if the primary forcing move fails verification or if multiple forcing moves exist. Rank them strictly by forcing nature first, then tool flags.
- **Pivot on failure:** If a candidate is abandoned after tool verification, immediately pivot to the next FORCING candidate. NEVER drift into quiet maneuvering when forcing options remain.
- **Runtime Check:** After calling `<safety>`, explicitly match each candidate to its `en prise` status and attacker/defender ratio before choosing; only commit a move that has zero `enprise` warnings and favorable defender counts.

- **Verify forcing first:** Before batching or evaluating quiet moves, run `<safety>` or `<simulate>` on the single most forcing candidate. If it succeeds, commit immediately.
- **Batch only if needed:** Only call `<safety>` on a batch of candidates if the primary forcing move fails verification or if multiple forcing moves exist. Rank them strictly by forcing nature first, then tool flags.
- **Flag-driven comparison:** When multiple forcing candidates exist, compare them side-by-side using explicit tool flags (`attacker/defender` ratios, `en prise` status, `opponent legal replies`). Do not discard a candidate based on presumed material loss; run `<line>` or `<simulate>` to trace forcing follow-ups. Commit the candidate with the lowest verified risk and highest constraint.
- **Pivot on failure:** If a candidate is abandoned after tool verification, immediately pivot to the next FORCING candidate. NEVER drift into quiet maneuvering when forcing options remain.
- **Runtime Check:** After calling `<safety>`, explicitly match each candidate to its `en prise` status and attacker/defender ratio before choosing; only commit a move that has zero `enprise` warnings and favorable defender counts.

- **Verify forcing first:** Before batching or evaluating quiet moves, run `<safety>` or `<simulate>` on the single most forcing candidate. If it succeeds, commit immediately.
- **Side-by-side tool comparison / Rank by forcing density:** When multiple candidates exist, bundle them in a single tool call. Strictly order analysis by the tool's `opponent legal replies` count: prioritize candidates with the lowest reply count and highest ratio of forcing replies. Compare candidates side-by-side using explicit tool flags (`attacker/defender` ratios, `en prise` status).
- **Prioritize forcing over static captures:** Rank candidates that demand an immediate opponent response (checks, direct threats) above static exchanges that allow recaptures. Do not discard a candidate simply because of a theoretical recapture; run `<simulate>` to verify if the recapture loses initiative or material.
- **Batch only if needed:** Only call `<safety>` on a batch of candidates if the primary forcing move fails verification or if multiple forcing moves exist. Rank them strictly by forcing nature first, then tool flags.
- **Pivot on failure:** If a candidate is abandoned after tool verification, immediately pivot to the next FORCING candidate. NEVER drift into quiet maneuvering when forcing options remain.
- **Flag-driven comparison:** Compare candidates using explicit tool flags. Discard candidates with `opponent legal replies > 2` or severe `en prise` warnings unless a forcing follow-up justifies it.
- **Runtime check

- **Verify forcing first:** Before batching or evaluating quiet moves, run `<safety>` or `<simulate>` on the single most forcing candidate. If it succeeds, commit immediately.
- **Batch only if needed:** Only call `<safety>` on a batch of candidates if the primary forcing move fails verification or if multiple forcing moves exist. Rank them strictly by forcing nature first, then tool flags (`en prise`, attacker/defender ratio, `opponent legal replies`).
- **Pivot on failure:** If a candidate is abandoned after tool verification, immediately pivot to the next FORCING candidate. NEVER drift into quiet maneuvering when forcing options remain.
- **Flag-driven comparison:** Compare candidates using explicit tool flags. Discard candidates with `opponent legal replies > 2` or severe `en prise` warnings unless a forcing follow-up justifies it.
- **Runtime Check:** After calling `<safety>`, explicitly match each candidate to its `en prise` status and attacker/defender ratio before choosing; only commit a move that has zero `enprise` warnings and favorable defender counts.

- **Verify forcing first:** Before batching or evaluating quiet moves, run `<safety>` or `<simulate>` on the single most forcing candidate. If it succeeds, commit immediately.
- **Batch only if needed:** Only call `<safety>` on a batch of candidates if the primary forcing move fails verification or if multiple forcing moves exist. Rank them strictly by forcing nature first, then tool flags (`en prise`, attacker/defender ratio, `opponent legal replies`).
- **Pivot on failure:** If a candidate is abandoned after tool verification, immediately pivot to the next FORCING candidate. NEVER drift into quiet maneuvering when forcing options remain.
- **Flag-driven comparison:** Compare candidates using explicit tool flags. Discard candidates with `opponent legal replies > 2` or severe `en prise` warnings unless a forcing follow-up justifies it.
- **Runtime Check:** After calling `<safety>`, explicitly match each candidate to its `en prise` status and attacker/defender ratio before choosing; only commit a move that has zero `enprise` warnings and favorable defender counts.

- **Verify forcing first:** Before batching or evaluating quiet moves, run `<safety>` or `<simulate>` on the single most forcing candidate. If it succeeds, commit immediately.
- **Batch only if needed:** Only call `<safety>` on a batch of candidates if the primary forcing move fails verification or if multiple forcing moves exist. Rank them strictly by forcing nature first, then tool flags (`en prise`, attacker/defender ratio, `opponent legal replies`).
- **Systematic comparison:** Do not stop checking once a move with `en prise: none` appears. Explicitly run `<safety>` or `<simulate>` on at least two different forcing candidates and compare them using tool flags. Commit only the candidate with the lowest verified risk and highest constraint.
- **Pivot on failure:** If a candidate is abandoned after tool verification, immediately pivot to the next FORCING candidate. NEVER drift into quiet maneuvering when forcing options remain.
- **Flag-driven comparison:** Compare candidates using explicit tool flags. Discard candidates with `opponent legal replies > 2` or severe `en prise` warnings unless a forcing follow-up justifies it.
- **Runtime Check:** After calling `<safety>`, explicitly match each candidate to its `en prise` status and attacker/defender ratio before choosing; only commit a move that has zero `enprise` warnings and favorable defender counts.

- **Verify Forcing First:** Before batching or evaluating quiet moves, run `<safety>` or `<simulate>` on the single most forcing candidate. If it succeeds, commit immediately.
- **Batch Only If Needed:** Only call `<safety>` on a batch of candidates if the primary forcing move fails verification or if multiple forcing moves exist. Rank them strictly by forcing nature first, then tool flags (`en prise`, attacker/defender ratio, `opponent legal replies`).
- **Pivot on Failure:** If a candidate is abandoned after tool verification, immediately pivot to the next FORCING candidate. NEVER drift into quiet maneuvering when forcing options remain.
- **Flag-Driven Comparison:** Compare candidates using explicit tool flags. Discard candidates with `opponent legal replies > 2` or severe `en prise` warnings unless a forcing follow-up justifies it.
- **Runtime Check:** After calling `<safety>`, explicitly match each candidate to its `en prise` status and attacker/defender ratio before choosing; only commit a move that has zero `enprise` warnings and favorable defender counts.
## New Section


## King Exposure & Mating Patterns
- **Identify tactical focal points:** When the opponent's king is exposed on the edge, lacks pawn cover, or sits in an open file/diagonal, immediately classify the position as a tactical melee rather than a positional game.
- **Prioritize flight-square reduction:** Prioritize moves that cut off king escape squares or deliver checks along converging lines. Continuously track how each candidate reduces the opponent's flight squares rather than focusing on piece trades or pawn captures.
- **Runtime check:** "After identifying the opponent's king position, have I marked its potential escape squares? Does my candidate reduce those squares or force a response that limits mobility?"
## Commitment Criteria
- **Anchor on forcing/structural impact:** Base final commitment on king restriction, piece coordination, or forced sequences—not surface material deficits or vague positional feelings.
- **Preserve forcing ideas:** If a forcing move creates an unbalanced tactical imbalance you cannot immediately refute, treat it as your primary candidate. Do not abandon it due to hesitation; verify with `<safety>` or `<simulate>` first.
- **Runtime Check:** "Does this move deliver a check, capture, or direct threat that logically forces a favorable continuation or restricts the opponent's king?" If yes, and a tool call confirms no immediate tactical refutation, commit.


- **Trust the tool's constraint metric:** When `<safety>` or `<line>` reports `opponent legal replies: 1` or `2`, treat the move as forcing and commit immediately. Do not second-guess or search for quieter alternatives once the tool confirms high constraint. **Runtime check:** Explicitly count the listed replies; if >2, discard the candidate and search for a more forcing alternative.
- **Ground commitment in explicit tool output:** Never commit a move in `<action>` solely based on an unverified mental picture. Always wait for the tool to confirm the outcome or verify the candidate against the position printer's explicitly listed legal moves before submitting `<action>`.

- **Anchor on forcing/structural impact:** Base final commitment on king restriction, piece coordination, or forced sequences—not surface material deficits or vague positional feelings.
- **Hard Tool Gate:** Do not output `<action>` until `<safety>` and `<simulate>` confirm the candidate's forcing nature and material outcome. If the tools were skipped or flagged a fatal flaw, abort the commit and search for an alternative.
- **Trust constraint metrics:** When `<safety>` or `<line>` reports `opponent legal replies: 1` or `2`, treat the move as forcing and commit immediately. If >2, discard and search for a more forcing alternative.
- **Ground commitment in explicit tool output:** Never commit a move in `<action>` solely based on an unverified mental picture. Always wait for the tool to confirm the outcome or verify the candidate against the position printer's explicitly listed legal moves before submitting `<action>`.

- **Anchor on forcing/structural impact:** Base final commitment on king restriction, piece coordination, or forced sequences—not surface material deficits or vague positional feelings.
- **Hard Tool Gate:** Do not output `<action>` until `<safety>` and `<simulate>` confirm the candidate's forcing nature and material outcome. If the tools were skipped or flagged a fatal flaw, abort the commit and search for an alternative.
- **Trust constraint metrics:** When `<safety>` or `<line>` reports `opponent legal replies: 1` or `2`, treat the move as forcing and commit immediately. If >2, discard and search for a more forcing alternative.
- **Ground commitment in explicit tool output:** Never commit a move in `<action>` solely based on an unverified mental picture. Always wait for the tool to confirm the outcome or verify the candidate against the position printer's explicitly listed legal moves before submitting `<action>`.
- **Runtime check

- **Anchor on forcing/structural impact:** Base final commitment on king restriction, piece coordination, or forced sequences—not surface material deficits or vague positional feelings.
- **Hard Tool Gate:** Do not output `<action>` until `<safety>` and `<simulate>` confirm the candidate's forcing nature and material outcome. If the tools were skipped or flagged a fatal flaw, abort the commit and search for an alternative.
- **Trust constraint metrics:** When `<safety>` or `<line>` reports `opponent legal replies: 1` or `2`, treat the move as forcing and commit immediately. If >2, discard and search for a more forcing alternative.
- **Ground commitment in explicit tool output:** Never commit a move in `<action>` solely based on an unverified mental picture. Always wait for the tool to confirm the outcome or verify the candidate against the position printer's explicitly listed legal moves before submitting `<action>`.
- **Calculate forced replies before material accounting:** When a candidate is a check, capture, or threat, calculate the opponent's forced replies first. Only evaluate static material outcomes after confirming the forcing sequence is sound.

- **Anchor on forcing/structural impact:** Base final commitment on king restriction, piece coordination, or forced sequences—not surface material deficits or vague positional feelings.
- **Hard Tool Gate:** Do not output `<action>` until `<safety>` and `<simulate>` confirm the candidate's forcing nature and material outcome. If the tools were skipped or flagged a fatal flaw, abort the commit and search for an alternative.
- **Trust constraint metrics:** When `<safety>` or `<line>` reports `opponent legal replies: 1` or `2`, treat the move as forcing and commit immediately. If >2, discard and search for a more forcing alternative.
- **Ground commitment in explicit tool output:** Never commit a move in `<action>` solely based on an unverified mental picture. Always wait for the tool to confirm the outcome or verify the candidate against the position printer's explicitly listed legal moves before submitting `<action>`.
- **Calculate forced replies before material accounting:** When a candidate is a check, capture, or threat, calculate the opponent's forced replies first. Only evaluate static material outcomes after confirming the forcing sequence is sound.

- **Anchor on forcing/structural impact:** Base final commitment on king restriction, piece coordination, or forced sequences—not surface material deficits or vague positional feelings.
- **Hard Tool Gate & Candidate Lock:** Do not output `<action>` until `<safety>` or `<simulate>` confirms the candidate's forcing nature. **CRITICAL:** The move in `<action>` MUST be the exact move passed to the most recent verification tool. If you switch candidates after a tool call, you MUST run a new tool on the new candidate before committing.
- **Trust constraint metrics:** When `<safety>` or `<line>` reports `opponent legal replies: 1` or `2`, treat the move as forcing and commit immediately. If >2, discard and search for a more forcing alternative.
- **Ground commitment in explicit tool output:** Never commit a move in `<action>` solely based on an unverified mental picture. Always wait for the tool to confirm the outcome or verify the candidate against the position printer's explicitly listed legal moves before submitting `<action>`.
- **Legal move list cross-check:** Before issuing `<action>`, cross-reference your calculated plan with the printed legal move list. Explicitly verify that no opponent piece can capture or block the finishing square.
- **Runtime verification:** Immediately before `<action>`, read the legal move list and confirm your candidate appears in it and that all opponent replies are accounted for. If discrepancies exist, halt and call `<board>` or `<safety>` to resolve them.

- **Anchor on forcing/structural impact:** Base final commitment on king restriction, piece coordination, or forced sequences—not surface material deficits or vague positional feelings.
- **Hard Tool Gate & Candidate Lock:** Do not output `<action>` until `<safety>` or `<simulate>` confirms the candidate's forcing nature. **CRITICAL:** The move in `<action>` MUST be the exact move passed to the most recent verification tool. If you switch candidates after a tool call, you MUST run a new tool on the new candidate before committing.
- **Trust constraint metrics:** When `<safety>` or `<line>` reports `opponent legal replies: 1` or `2`, treat the move as forcing and commit immediately. If >2, discard and search for a more forcing alternative.
- **Ground commitment in explicit tool output:** Never commit a move in `<action>` solely based on an unverified mental picture. Always wait for the tool to confirm the outcome or verify against the printed legal-move list before submitting `<action>`.
- **Decisive Commitment Rhythm:** Once `<safety>` or `<line>` confirms a candidate's forcing nature and safety, commit immediately in `<action>`. Do not re-scan the board, doubt the initial read, or search for hidden positional traps. Multi-turn hesitation after tool confirmation is a failure mode.
- **Calculate forced replies before material accounting:** When a candidate is a check, capture, or threat, calculate the opponent's forced replies first. Only evaluate static material outcomes after confirming the forcing sequence is sound.

- **Anchor on Forcing/Structural Impact:** Base final commitment on king restriction, piece coordination, or forced sequences—not surface material deficits or vague positional feelings.
- **Hard Tool Gate & Candidate Lock:** Do not output `<action>` until `<safety>` or `<simulate>` confirms the candidate's forcing nature. **CRITICAL:** The move in `<action>` MUST be the exact move passed to the most recent verification tool. If you switch candidates after a tool call, you MUST run a new tool on the new candidate before committing.
- **Trust Constraint Metrics:** When `<safety>` or `<line>` reports `opponent legal replies: 1` or `2`, treat the move as forcing and commit immediately. If >2, discard and search for a more forcing alternative.
- **Ground Commitment in Explicit Tool Output:** Never commit a move in `<action>` solely based on an unverified mental picture. Always wait for the tool to confirm the outcome or verify against the printed legal-move list before submitting `<action>`.
- **Decisive Commitment Rhythm:** Once `<safety>` or `<line>` confirms a candidate's forcing nature and safety, commit immediately in `<action>`. Do not re-scan the board, doubt the initial read, or search for hidden positional traps. Multi-turn hesitation after tool confirmation is a failure mode.
- **Calculate Forced Replies Before Material Accounting:** When a candidate is a check, capture, or threat, calculate the opponent's forced replies first. Only evaluate static material outcomes after confirming the forcing sequence is sound.
## Judging Tool Output


- **Trust tool flags over manual tracing:** Treat `en prise`, attacker/defender counts, and forcing replies as ground truth. NEVER manually trace diagonals, square colors, or override tool flags with mental geometry.
- **Stop Rule:** If you catch yourself manually counting defenders or tracing coordinates for more than two steps, halt and call `<safety>` or `<board>` immediately. Manual parsing is highly prone to fatigue errors.
- **Decision rule:** Treat safety/exchange warnings as tactical data, not automatic dismissals. Before abandoning a flagged candidate, run `<simulate>` or `<line>` against the opponent's strongest forcing reply to test if the risk materializes. Only discard if the tool confirms a fatal refutation.
- **No mental overrides:** Once `<safety>` or `<simulate>` confirms a candidate is forcing or strong, do not discard it based on subsequent mental calculations. Trust the tool's board states and material counts as the final arbiter.
- **Restrict tools to forcing moves:** Call `<safety>`, `<simulate>`, or `<line>` ONLY to verify checks, captures, or threats. Never use tools to rank, verify, or generate quiet moves.
- **Prune on explicit flags:** When a tool flags a losing exchange, defended destination, or forcing reply, immediately remove that candidate and shift focus to the next strongest forcing move. Do not mentally override explicit tool warnings or assume surface-level safety.
- **Tools as pruning filters:** Use `<threats>`, `<safety>`, and `<simulate>` strictly to prune dangerous or incorrect candidates, not to discover new tactical ideas. If a tool result indicates a safety vulnerability, stronger opponent reply, or refutation, immediately abandon the current line.

- **Trust tool flags over manual tracing:** Treat `en prise`, attacker/defender counts, and forcing replies as ground truth. NEVER manually trace diagonals, square colors, or override tool flags with mental geometry.
- **Stop Rule:** If you catch yourself manually counting defenders or tracing coordinates for more than two steps, halt and call `<safety>` or `<board>` immediately. Manual parsing is highly prone to fatigue errors.
- **Decision rule:** Treat safety/exchange warnings as tactical data, not automatic dismissals. Before abandoning a flagged candidate, run `<simulate>` or `<line>` against the opponent's strongest forcing reply to test if the risk materializes. Only discard if the tool confirms a fatal refutation.
- **No mental overrides:** Once `<safety>` or `<simulate>` confirms a candidate is forcing or strong, do not discard it based on subsequent mental calculations. Trust the tool's board states and material counts as the final arbiter.
- **Restrict tools to forcing moves:** Call `<safety>`, `<simulate>`, or `<line>` ONLY to verify checks, captures, or threats. Never use tools to rank, verify, or generate quiet moves.
- **Suppress coordinate obsession:** When a move is flagged `#` or `+`, DO NOT manually verify diagonal slopes or clock positions. Trust the tool's flag and skip non-forcing positional audits.

- **Trust tool flags over manual tracing:** Treat `en prise`, attacker/defender counts, and forcing replies as ground truth. NEVER manually trace diagonals, square colors, or override tool flags with mental geometry.
- **Stop Rule:** If you catch yourself manually counting defenders or tracing coordinates for more than two steps, halt and call `<safety>` or `<board>` immediately. Manual parsing is highly prone to fatigue errors.
- **Decision rule:** Treat safety/exchange warnings as tactical data, not automatic dismissals. Before abandoning a flagged candidate, run `<simulate>` or `<line>` against the opponent's strongest forcing reply to test if the risk materializes. Only discard if the tool confirms a fatal refutation.
- **No mental overrides:** Once `<safety>` or `<simulate>` confirms a candidate is forcing or strong, do not discard it based on subsequent mental calculations. Trust the tool's board states and material counts as the final arbiter.
- **Restrict tools to forcing moves:** Call `<safety>`, `<simulate>`, or `<line>` ONLY to verify checks, captures, or threats. Never use tools to rank, verify, or generate quiet moves.
- **Suppress coordinate obsession & positional drift:** When a move is flagged `#` or `+`, DO NOT manually verify diagonal slopes, square colors, or clocks. Trust the tool's flag and skip non-forcing positional audits.
- **Never extrapolate tool flags:** If `<safety>` flags one candidate as unsafe, do not assume siblings share the same flaw. Run the tool independently on each candidate to verify its specific safety flags before discarding.
- **Ignore non-forcing warnings when forcing lines exist:** If a forcing line is present, verify it with `<line>` first. Do not let safety flags on quiet moves derail your search for the forced solution.
- **No simulated tool calls:** If you mention a tool in your reasoning, you MUST execute it in the next turn or explicitly discard it. Never simulate tool usage in text without following through.
- **Targeted sanity check:** For mates, verify only (1) if the king's escape squares are genuinely blocked/controlled, and (2) if defenders can't capture/interpose. Commit once visually confirmed.
- **Avoid unverified mental pruning:** Generating a long list of candidates and calculating variations mentally leads to false switches and budget waste. Trust the tool's reply count to filter candidates. If a candidate yields >2 legal replies to the opponent, discard it mentally only after the tool confirms it.
- **Mandatory tool verification for forcing moves:** When a candidate is marked `#` or `+` on the legal-move list, immediately call `<safety>` or `<line>` to verify it. Do NOT manually trace diagonals, count escape squares, or simulate opponent replies in text. Treat the tool's output as the sole arbiter of tactical validity.
- **Pre-commit tool-call count check:** Before outputting `<action>`, verify that you have executed at least one tool call (`<safety>`, `<simulate>`, or `<line>`) specifically for your chosen candidate. If the count is zero, halt and run the tool immediately. Never finalize a move based on mental verification or visual inspection alone.
- **No reactive tool rescue:** Never call `<board>`, `<safety>`, or `<simulate>` reactively after losing focus or second-guessing your position read. Calibrate tools proactively on your initial forcing candidates.
## Converting the Line (Second Move)

## Budget Discipline


- **Break mental loops:** When mental calculation produces contradictory lines, repeated doubts, or circular reasoning, immediately halt internal analysis and call `<simulate>`, `<line>`, or `<threats>`. Use tools as a mandatory loop-breaker rather than continuing to re-read the position mentally.
- **Ground complexity:** If a line requires tracking multiple exchanges or defenses, switch to tool calls immediately instead of continuing mental loops.
- **Avoid manual arithmetic:** Never rely on mental arithmetic for exchanges or material counts. If mental counting exceeds two exchanges, pause and verify with `<board>` or `<line>` immediately.
- **Commit after confirmation:** When `<line>` confirms a forcing win or mate, commit the first move immediately. Do not re-scan the board, question the calculation, or re-verify material balance.

- **Break mental loops immediately:** When calculation produces contradictory lines, repeated doubts, or circular reasoning, halt internal analysis and call `<simulate>`, `<line>`, or `<threats>`.
- **Ground complexity in tools:** If a line requires tracking multiple exchanges or defenses, switch to tool calls immediately. Never rely on mental arithmetic for material counts beyond two exchanges.
- **Commit after confirmation:** When `<line>` confirms a forcing win or mate, commit immediately. Do not re-scan, question, or re-verify.

- **Break mental loops immediately:** When calculation produces contradictory lines, repeated doubts, or circular reasoning, halt internal analysis and call `<simulate>`, `<line>`, or `<threats>`.
- **Ground complexity in tools:** If a line requires tracking multiple exchanges or defenses, switch to tool calls immediately. Never rely on mental arithmetic for material counts beyond two exchanges.
- **Commit after confirmation:** When `<line>` confirms a forcing win or mate, commit immediately. Do not re-scan, question, or re-verify.
- **Ban manual FEN re-reading:** Never manually re-parse the FEN or simulate long opponent refutation sequences in text. Immediately call `<safety>` or `<line>` on your strongest candidate to verify safety and forcing nature.

- **Break mental loops immediately:** When calculation produces contradictory lines, repeated doubts, or circular reasoning, halt internal analysis and call `<simulate>`, `<line>`, or `<threats>`.
- **Ground complexity in tools:** If a line requires tracking multiple exchanges or defenses, switch to tool calls immediately. Never rely on mental arithmetic for material counts beyond two exchanges.
- **Commit after confirmation:** When `<line>` confirms a forcing win or mate, commit immediately. Do not re-scan, question, or re-verify.
- **Ban manual FEN re-reading:** Never manually re-parse the FEN or simulate long opponent refutation sequences in text. Immediately call `<safety>` or `<line>` on your strongest candidate to verify safety and forcing nature.

- **Break mental loops immediately:** When calculation produces contradictory lines, repeated doubts, or circular reasoning, halt internal analysis and call `<simulate>`, `<line>`, or `<threats>`.
- **Ground complexity in tools:** If a line requires tracking multiple exchanges or defenses, switch to tool calls immediately. Never rely on mental arithmetic for material counts beyond two exchanges.
- **Mental simulation limit:** "Am I mentally simulating beyond two forced ply without a tool result?" If yes, stop calculating, invoke `<safety>` or `<simulate>` on the current line, and let the tool's material/response data dictate whether to commit or switch candidates.
- **Commit after confirmation:** When `<line>` confirms a forcing win or mate, commit immediately. Do not re-scan, question, or re-verify.
- **Ban manual FEN re-reading:** Never manually re-parse the FEN or simulate long opponent refutation sequences in text. Immediately call `<safety>` or `<line>` on your strongest candidate.
- **Treat material counts as fixed:** Never re-sum piece values or hunt for discrepancies in the provided material count. If arithmetic distracts you, assume the given count is correct and immediately list all checks, captures, and threats.

- **Break mental loops immediately:** When calculation produces contradictory lines, repeated doubts, or circular reasoning, halt internal analysis and call `<simulate>`, `<line>`, or `<threats>`.
- **Ground complexity in tools:** If a line requires tracking multiple exchanges or defenses, switch to tool calls immediately. Never rely on mental arithmetic for material counts beyond two exchanges.
- **Mental simulation limit:** "Am I mentally simulating beyond two forced ply without a tool result?" If yes, stop calculating, invoke `<safety>` or `<simulate>` on the current line, and let the tool's material/response data dictate whether to commit or switch candidates.
- **Commit after confirmation:** When `<line>` confirms a forcing win or mate, commit immediately. Do not re-scan, question, or re-verify.
- **Ban manual FEN re-reading:** Never manually re-parse the FEN or simulate long opponent refutation sequences in text. Immediately call `<safety>` or `<line>` on your strongest candidate.
- **Treat material counts as fixed:** Never re-sum piece values or hunt for discrepancies in the provided material count. If arithmetic distracts you, assume the given count is correct and immediately list all checks, captures, and threats.

- **Break mental loops immediately:** When calculation produces contradictory lines, repeated doubts, or circular reasoning, halt internal analysis and call `<simulate>`, `<line>`, or `<threats>`.
- **Ground complexity in tools:** If a line requires tracking multiple exchanges or defenses, switch to tool calls immediately. Never rely on mental arithmetic for material counts beyond two exchanges.
- **Mental simulation limit

- **Break Mental Loops Immediately:** When calculation produces contradictory lines, repeated doubts, or circular reasoning, halt internal analysis and call `<simulate>`, `<line>`, or `<threats>`.
- **Ground Complexity in Tools:** If a line requires tracking multiple exchanges or defenses, switch to tool calls immediately. Never rely on mental arithmetic for material counts beyond two exchanges.
- **Ban Manual FEN Re-reading:** Never manually re-parse the FEN or simulate long opponent refutation sequences in text. Immediately call `<safety>` or `<line>` on your strongest candidate.
- **Mental Simulation Limit:** "Am I mentally simulating beyond two forced ply without a tool result?" If yes, stop calculating, invoke `<safety>` or `<simulate>` on the current line, and let the tool's material/response data dictate whether to commit or switch candidates.
- **Commit After Confirmation:** When `<line>` confirms a forcing win or mate, commit immediately. Do not re-scan, question, or re-verify.
- **Treat Material Counts as Fixed:** Never re-sum piece values or hunt for discrepancies in the provided material count. If arithmetic distracts you, assume the given count is correct and immediately list all checks, captures, and threats.
## Common Pitfalls


- **Stop manual FEN parsing:** When the legal-move list marks a candidate with `#` or `+`, treat its legality as given. Shift evaluation to tactical weaknesses. **Runtime check:** Scan for `+`/`#` suffixes; if present, select that move, verify only immediate defensive resources (captures/blocks/king escapes), and commit. Discard weaker alternatives.
- **Targeted sanity check:** Verify only (1) if the king's escape squares are genuinely blocked/controlled, and (2) if defenders can't capture/interpose due to geometry/pins. Commit once visually confirmed.
- **Runtime check:** "Am I verifying legality or verifying the win? If legality, trust the tool. If win, focus on tactical constraints."
- **Never skip tools:** Skipping verification for standout candidates leads to unverified drafts, false uncertainty, and budget waste. Always verify with `<safety>` or `<simulate>` before committing.

- **Suppress coordinate obsession & positional drift:** When a move is flagged `#` or `+`, DO NOT manually verify diagonal slopes, square colors, or clocks. Trust the tool's flag and skip non-forcing positional audits.
- **Never extrapolate tool flags:** If `<safety>` flags one candidate as unsafe, do not assume siblings share the same flaw. Run the tool independently on each candidate to verify its specific safety flags before discarding.
- **Ignore non-forcing warnings when forcing lines exist:** If a forcing line is present, verify it with `<line>` first. Do not let safety flags on quiet moves derail your search for the forced solution.

- **Trust tool safety flags over visual inspection:** When tools flag `en prise` or unsafe pieces, accept the warning immediately. Do not manually re-trace piece coverage or square control. If visual inspection contradicts the tool, run `<board>` or `<safety>` to resolve the discrepancy; never override the tool with mental geometry.
- **Force tool validation for forcing moves:** Never calculate checks, captures, or mate threats entirely in text. Geometric hallucinations and repetitive doubt loops are common. Use `<line>` or `<safety>` to verify the forcing structure, then pivot immediately if the tool flags a refutation, `[LOSING EXCHANGE RISK]`, or your key pieces as `en prise`.
- **Suppress coordinate obsession & positional drift:** When a move is flagged `#` or `+`, DO NOT manually verify diagonal slopes, square colors, or clocks. Trust the tool's flag and skip non-forcing positional audits.
- **Never extrapolate tool flags:** If `<safety>` flags one candidate as unsafe, do not assume siblings share the same flaw. Run the tool independently on each candidate to verify its specific safety flags before discarding.
- **Ignore non-forcing warnings when forcing lines exist:** If a forcing line is present, verify it with `<line>` first. Do not let safety flags on quiet moves derail your search for the forced solution.

- **Suppress coordinate obsession & positional drift:** When a move is flagged `#` or `+`, DO NOT manually verify diagonal slopes, square colors, or clocks. Trust the tool's flag and skip non-forcing positional audits.
- **Never skip tools:** Skipping verification for standout candidates leads to unverified drafts and budget waste. Always verify with `<safety>` or `<simulate>` before committing.
- **Never extrapolate tool flags:** If `<safety>` flags one candidate as unsafe, do not assume siblings share the same flaw. Run the tool independently on each candidate to verify its specific safety flags before discarding.
- **Ignore non-forcing warnings when forcing lines exist:** If a forcing line is present, verify it with `<line>` first. Do not let safety flags on quiet moves derail your search for the forced solution.
- **Avoid mental tool scheduling:** Announcing a tool call without executing it creates cognitive friction. If the board state and legal-move list already confirm the forcing nature of a candidate, commit directly.

- **Suppress coordinate obsession & positional drift:** When a move is flagged `#` or `+`, DO NOT manually verify diagonal slopes, square colors, or clocks. Trust the tool's flag and skip non-forcing positional audits.
- **Never skip tools:** Skipping verification for standout candidates leads to unverified drafts and budget waste. Always verify with `<safety>` or `<simulate>` before committing.
- **Never extrapolate tool flags:** If `<safety>` flags one candidate as unsafe, do not assume siblings share the same flaw. Run the tool independently on each candidate to verify its specific safety flags before discarding.
- **Ignore non-forcing warnings when forcing lines exist:** If a forcing line is present, verify it with `<line>` first. Do not let safety flags on quiet moves derail your search for the forced solution.
- **Tool-driven risk calibration:** Always run `<safety>` or `<threats>` on advancing pawns or pieces approaching key zones. Treat tool warnings like `[LOSING EXCHANGE RISK]` or `en prise` as mandatory stop-signs requiring `<simulate>` verification. Never override a tool's explicit risk flag with a mental variant.
- **Trust tool flags over manual tracing:** Treat `en prise` and attacker/defender counts as ground truth. NEVER manually trace diagonals or override flags with mental geometry.
- **Break mental loops immediately:** When calculation produces contradictory lines or circular reasoning, halt internal analysis and call `<simulate>`, `<line>`, or `<threats>`.

- **Suppress coordinate obsession & positional drift:** When a move is flagged `#` or `+`, DO NOT manually verify diagonal slopes, square colors, or clocks. Trust the tool's flag and skip non-forcing positional audits.
- **Never skip tools:** Skipping verification for standout candidates leads to unverified drafts and budget waste. Always verify with `<safety>` or `<simulate>` before committing.
- **Never extrapolate tool flags:** If `<safety>` flags one candidate as unsafe, do not assume siblings share the same flaw. Run the tool independently on each candidate to verify its specific safety flags before discarding.
- **Ignore non-forcing warnings when forcing lines exist:** If a forcing line is present, verify it with `<line>` first. Do not let safety flags on quiet moves derail your search for the forced solution.
- **No simulated tool calls:** If you mention a tool in your reasoning, you MUST execute it in the next turn or explicitly discard it. Never simulate tool usage in text (e.g., "Let's run safety...") without following through.
- **Targeted sanity check:** For mates, verify only (1) if the king's escape squares are genuinely blocked/controlled, and (2) if defenders can't capture/interpose. Commit once visually confirmed.

- **Suppress coordinate obsession & positional drift:** When a move is flagged `#` or `+`, DO NOT manually verify diagonal slopes, square colors, or clocks. Trust the tool's flag and skip non-forcing positional audits.
- **Never skip tools:** Skipping verification for standout candidates leads to unverified drafts and budget waste. Always verify with `<safety>` or `<simulate>` before committing.
- **Never extrapolate tool flags:** If `<safety>` flags one candidate as unsafe, do not assume siblings share the same flaw. Run the tool independently on each candidate to verify its specific safety flags before discarding.
- **Ignore non-forcing warnings when forcing lines exist:** If a forcing line is present, verify it with `<line>` first. Do not let safety flags on quiet moves derail your search for the forced solution.
- **No simulated tool calls:** If you mention a tool in your reasoning, you MUST execute it in the next turn or explicitly discard it. Never simulate tool usage in text without following through.
- **Targeted sanity check:** For mates, verify only (1) if the king's escape squares are genuinely blocked/controlled, and (2) if defenders can't capture/interpose. Commit once visually confirmed.
- **Avoid unverified mental pruning:** Generating a long list of candidates and calculating variations mentally leads to false switches and budget waste. Trust the tool's reply count to filter candidates. If a candidate yields >2 legal replies to the opponent, discard it mentally only after the tool confirms it.

- **Suppress coordinate obsession & positional drift:** When a move is flagged `#` or `+`, DO NOT manually verify diagonal slopes, square colors, or clocks. Trust the tool's flag and skip non-forcing positional audits.
- **Never skip tools:** Skipping verification for standout candidates leads to unverified drafts and budget waste. Always verify with `<safety>` or `<simulate>` before committing.
- **Never extrapolate tool flags:** If `<safety>` flags one candidate as unsafe, do not assume siblings share the same flaw. Run the tool independently on each candidate to verify its specific safety flags before discarding.
- **Ignore non-forcing warnings when forcing lines exist:** If a forcing line is present, verify it with `<line>` first. Do not let safety flags on quiet moves derail your search for the forced solution.
- **No simulated tool calls:** If you mention a tool in your reasoning, you MUST execute it in the next turn or explicitly discard it. Never simulate tool usage in text without following through.
- **Targeted sanity check:** For mates, verify only (1) if the king's escape squares are genuinely blocked/controlled, and (2) if defenders can't capture/interpose. Commit once visually confirmed.
- **Avoid unverified mental pruning:** Generating a long list of candidates and calculating variations mentally leads to false switches and budget waste. Trust the tool's reply count to filter candidates. If a candidate yields >2 legal replies to the opponent, discard it mentally only after the tool confirms it.
- **Mandatory tool verification for forcing moves:** When a candidate is marked `#` or `+` on the legal-move list, immediately call `<safety>` or `<line>` to verify it. Do NOT manually trace diagonals, count escape squares, or simulate opponent replies in text. Treat the tool's output as the sole arbiter of tactical validity.
- **Pre-commit tool-call count check:** Before outputting `<action>`, verify that you have executed at least one tool call (`<safety>`, `<simulate>`, or `<line>`) specifically for your chosen candidate. If the count is zero, halt and run the tool immediately. Never finalize a move based on mental verification or visual inspection alone.
- **No reactive tool rescue:** Never call `<board>`, `<safety>`, or `<simulate>` reactively after losing focus or second-guessing your position read. Calibrate tools proactively on your initial forcing candidates.

- **Suppress coordinate obsession & positional drift:** When a move is flagged `#` or `+`, DO NOT manually verify diagonal slopes, square colors, or clocks. Trust the tool's flag and skip non-forcing positional audits.
- **Never skip tools:** Skipping verification for standout candidates leads to unverified drafts and budget waste. Always verify with `<safety>` or `<simulate>` before committing.
- **Never extrapolate tool flags:** If `<safety>` flags one candidate as unsafe, do not assume siblings share the same flaw. Run the tool independently on each candidate to verify its specific safety flags before discarding.
- **Ignore non-forcing warnings when forcing lines exist:** If a forcing line is present, verify it with `<line>` first. Do not let safety flags on quiet moves derail your search for the forced solution.
- **No simulated tool calls:** If you mention a tool in your reasoning, you MUST execute it in the next turn or explicitly discard it. Never simulate tool usage in text without following through.
- **Targeted sanity check:** For mates, verify only (1) if the king's escape squares are genuinely blocked/controlled, and (2) if defenders can't capture/interpose. Commit once visually confirmed.
- **Avoid unverified mental pruning:** Generating a long list of candidates and calculating variations mentally leads to false switches and budget waste. Trust the tool's reply count to filter candidates. If a candidate yields >2 legal replies to the opponent, discard it mentally only after the tool confirms it.
- **Mandatory tool verification for forcing moves:** When a candidate is marked `#` or `+` on the legal-move list, immediately call `<safety>` or `<line>` to verify it. Do NOT manually trace diagonals, count escape squares, or simulate opponent replies in text. Treat the tool's output as the sole arbiter of tactical validity.
- **Pre-commit tool-call count check:** Before outputting `<action>`, verify that you have executed at least one tool call (`<safety>`, `<simulate>`, or `<line>`) specifically for your chosen candidate. If the count is zero, halt and run the tool immediately. Never finalize a move based on mental verification or visual inspection alone.
- **No reactive tool rescue:** Never call `<board>`, `<safety>`, or `<simulate>` reactively after losing focus or second-guessing your position read. Calibrate tools proactively on your initial forcing candidates.