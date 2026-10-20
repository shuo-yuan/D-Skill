# Ranked Allocation Formulas

## Tie-Aware Point Distribution

When points must go to the highest value(s) with equal sharing among ties, use:

```excel
=IF(value=MAX(range), total_points/COUNTIF(range,MAX(range)), 0)
```

### Why this works
- `MAX(range)` finds the top score.
- `value=MAX(range)` identifies all cells that tie for first.
- `COUNTIF(range,MAX(range))` counts how many are tied.
- `total_points/COUNTIF(...)` divides points equally among them.
- Non-winners get zero.

### Edge cases handled
- Sole winner → full points.
- Two-way tie → half points each.
- Three-way tie → one-third points each.
- No special-case logic required.

## Systematic Block Generation

When filling a rectangular target range with formulas:

1. Identify the source rows and columns.
2. Iterate target rows and columns explicitly.
3. For each target cell, construct the formula using the mapped source row and column letter.
4. Verify relative and absolute references are correct before writing.

Example: Target B5:E7 maps to source rows 1–3, preserving column letters B–E.
