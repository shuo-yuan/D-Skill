# Summary Rebuild Patterns

## Table of Contents
- [Clear-before-write pattern](#clear-before-write-pattern)
- [Detail-values vs. formula-totals](#detail-values-vs-formula-totals)
- [Sheet-order boundary detection](#sheet-order-boundary-detection)

## Clear-before-write pattern
When rebuilding a summary table that aggregates data from multiple source sheets:
1. Identify the output region (e.g., columns B:E starting at row 2).
2. Clear that entire region before writing new data.
3. Write fresh headers, detail rows, and formula-based totals.

This prevents obsolete sheet names, stale aggregates, or orphaned rows from surviving when source sheets are added, removed, or renamed.

## Detail-values vs. formula-totals
- Compute per-sheet aggregates (sums, counts, balances) and write them as static values in detail rows.
- In the final total row, use spreadsheet formulas (`SUM`, `SUBTOTAL`) that reference the detail rows.
- This keeps the summary transparent and ensures totals automatically reflect changes if detail values are recalculated.

## Sheet-order boundary detection
When a designated summary sheet marks the end of source data:
1. Locate the summary sheet in the workbook's sheet order.
2. Iterate over all worksheets whose index precedes the summary sheet.
3. Skip the summary sheet itself and any sheets after it.

This approach naturally accommodates new source sheets inserted before the boundary without requiring code changes.