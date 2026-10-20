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

## Finding the Move: Motifs and Candidates

## Verifying the Move: Tool Ritual

## Comparing Candidates

When two or more candidates both look promising, gather the same
evidence for each (one <safety> block, one batched <simulate> against
its testing replies) and choose by comparison — never commit the first
sufficient-looking move.

## Judging Tool Output

## Converting the Line (Second Move)

## Budget Discipline

## Common Pitfalls
