---
name: formula-patterns
description: "Detailed patterns for dynamic counting, formatting, and references."
---

## Dynamic Counting with COUNTA
When source data has missing or skipped entries, a simple row-based index fails. Use `COUNTA` with a dynamic relative range to count only non-empty cells up to the current row.

**Pattern:**
```excel
=COUNTA($B$3:B[current_row])
```

## Zero-Padding with TEXT
Wrap numerical results in `TEXT(...,"000")` to enforce consistent fixed-width strings in concatenated output.

**Pattern:**
```excel
=TEXT(COUNTA($B$3:B3)+9,"000")
```

## Absolute vs Relative References
In multi-row formulas, distinguish between static context and dynamic calculations:
- **Absolute References (`$B$2`)**: Anchor constant values so they remain fixed across all rows.
- **Relative Ranges (`$B$3:B3`)**: Use for row-specific calculations so each row's formula adapts automatically.

**Example:**
```excel
=$B$2 & TEXT(COUNTA($B$3:B3)+9,"000")
```