## When NOT to Analyze: Fast Paths and Stopping Rules

Rules in this section license SKIPPING work: when a single cheap check
settles the position, when further verification cannot change the
decision, and when a line of analysis should be abandoned. Every entry
must name (a) the exact trigger that makes the shortcut safe and
(b) the condition under which the shortcut must NOT be taken. A rule
without both parts does not belong here.

## Finding the Move: Motifs and Candidates

## Verifying the Move: Tool Ritual

Before EVERY committed move — including the second/converting move of a
line, and even when the move looks obviously winning or forced — spend
at least one tool call on it: a <safety> check on the candidate, or a
<line> replay if you are executing a planned multi-move combination.
A move that only exists in your own prose reasoning is unverified;
tool output is the only evidence that counts. Do not let "this is
clearly winning" substitute for a tool call — puzzles are rated
precisely because the losing side has a resource (a check, a
zwischenzug, a stalemate trick, a better defense) that is invisible
to quick mental scanning but shows up immediately in <safety>,
<threats>, or <line> output. If you have budget left and have not
yet queried a single tool this move, query one before writing your
<action> tag.

For puzzles claiming a forced mate or a large material swing, verify
the FULL intended line with <line> (or a matching batch of <simulate>
calls) several plies deep, not just the first ply — a capture that
looks decisive after one exchange in your head is not verified until
the tool confirms the mate flag or the actual material count further
down the line. Mental-only board reasoning, uncorroborated by any
tool call, is the leading cause of wrong first moves.
## Comparing Candidates

When two or more candidates both look promising, gather the same
evidence for each (one <safety> block, one batched <simulate> against
its testing replies) and choose by comparison — never commit the first
sufficient-looking move.

## Judging Tool Output

## Converting the Line (Second Move)

The second move of a puzzle is graded exactly as strictly as the
first — "I'm up a rook now, any reasonable move wins" is the most
common way these puzzles are lost. After your first move is answered,
do not default to the first "natural improving" move (grab a pawn,
centralize, trade down). Instead: run <threats> in the new position to
see what the opponent can do, and run <safety> on your top 1-2
candidates before choosing. If multiple moves look equally good
materially, the puzzle almost always wants the one that also meets a
specific tactical point (a check, a fork, cutting off the king,
avoiding a stalemate/counterplay resource) — use <safety>'s forcing-reply
list and <hanging> to find it rather than picking the first move that
simplifies the position.
## Budget Discipline

Cap your own free-text reasoning per turn: if you notice you are
re-listing the same candidate moves or re-deriving the same line a
second time without new tool evidence, stop writing and issue a tool
call instead — prose repetition is a signal that you're guessing, not
analyzing. Reasoning is cheap relative to tool budget (up to 10 calls
per move), so when torn between 2+ candidates, spend a tool call to
decide rather than spending another paragraph. Every reply must end in
exactly one tag, either a single tool tag or a single <action> tag —
never let a reply trail off in plain prose with no tag, since that
wastes a full turn on a format-correction round-trip.
## Common Pitfalls

- Treating the second move of a 2-move puzzle as free/obvious once
  material is won — it is graded as strictly as the first move and
  frequently has its own precise best move; verify it with <safety>
  or <threats>, don't just play the first pawn grab or king move.
- Writing a long chain of mental analysis and then committing an
  <action> that was never actually run through <safety>, <simulate>,
  or <line> — mental calculation is not a substitute for tool output.
- Letting a reply end without a tool tag or an <action> tag (e.g.
  trailing off mid-sentence, or writing the move as bare text instead
  of inside <action></action>) — always close every reply with
  exactly one tag.
- Flip-flopping between two candidate moves across several turns
  without gaining new tool evidence between flips — each turn should
  either add a tool result or commit; re-litigating the same two
  options from memory is a sign to run <safety> on both and compare,
  not to keep reasoning in prose.
- Re-parsing the FEN by eye in a loop: if you catch yourself
  re-deriving piece placement from the FEN string more than once, or
  listing many "maybe X? maybe Y?" candidates, your mental board model
  is unreliable — stop narrating and resolve it with a tool call
  (<board> or <hanging>) instead of re-reading the FEN text again.
  Parse the FEN once, deliberately, rank by rank (8→1), and trust that
  single parse; if you must double check, check only the one fact in
  doubt, not the whole board again.
- Committing on unresolved doubt: if your own reasoning flags the
  move as surprising or possibly a blunder ("that can't be right",
  "unless the piece is pinned"), that doubt means STOP and check with
  <safety> or <line> — never commit a move you've talked yourself into
  despite a suspicion it loses material.
- Once the legal-move list itself tags a candidate with `#`
  (checkmate), or `<safety>`/`<threats>` already confirms it wins
  cleanly, decide once and commit — do not re-derive the board or
  re-run the same check again cycling between 'I'll output X... wait,
  X#...', which burns budget without changing the answer.

<!-- SLOW_UPDATE_START -->
<!-- SLOW_UPDATE_END -->
