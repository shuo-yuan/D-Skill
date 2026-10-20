# Formula Patterns

Proven patterns observed in successful spreadsheet tasks.

## Dynamic Counting with COUNTA for Gap Handling

When source data contains gaps (missing or skipped entries), use `COUNTA` with a dynamic relative range to count only non-empty cells up to the current row. This produces sequential numbering regardless of gaps.

**Pattern:** `COUNTA($B$3:B[current_row])`

**Example:** If column B has data in rows 3, 5, 7 (with gaps at 4, 6), the formula in row 7 becomes `COUNTA($B$3:B7)` and returns 3.

## Zero-Padding with TEXT for Fixed-Width Formatting

Wrap numerical results in `TEXT(...,"000")` to enforce consistent N-digit zero-padded strings. Essential when numbers must appear as fixed-width strings in concatenated output.

**Pattern:** `TEXT(value,"000")` for 3-digit; adjust format string for other widths.

**Example:** `TEXT(COUNTA(...)+9,"000")` turns 10 into "010", 11 into "011", etc.

## Absolute Reference for Shared Context, Relative for Dynamics

Anchor constant values with absolute references (`$B$2`) while using relative ranges for row-specific calculations. This lets one formula scale across hundreds of rows without manual adjustment.

**Pattern:** Fixed context cells use absolute references; dynamic operations (counting, indexing) use relative ranges like `$B$3:B3`.

**Example:** `=$B$2 & TEXT(COUNTA($B$3:B3)+9,"000")` — prefix in B2 stays constant, counter adapts per row.
