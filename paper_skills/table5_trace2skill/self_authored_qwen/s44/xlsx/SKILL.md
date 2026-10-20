---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow

- Use `openpyxl` (or `pandas`) for programmatic manipulation; load workbook, inspect structure, and save once at the end.
- Pre-analyze: enumerate sheets, map headers/ranges, and define explicit input/output bounds. Use reference/"After" sheets to infer patterns.
- Plan transformations: parse lookup tables into dictionaries early. Use stateful iteration for grouped/fragmented data (two-pass or transition detection). For sequential extraction, use a single running index counter.
- Safe modifications: collect indices first and delete/insert in reverse order to prevent index shifting. Validate types before conversion.
- Formula vs. Values: Prefer pre-computed numeric literals unless formulas are explicitly requested. If formulas are needed, construct them programmatically with explicit absolute/relative references and self-reference checks.
- Workflow sequence: 1. Inspect & validate. 2. Map & prepare. 3. Transform & write. 4. Verify output.

## Inspection

- Programmatically enumerate sheets, headers, and data ranges. Never assume hardcoded indices; map structure dynamically.
- Restrict checks to exact column ranges specified. Scan for first/last non-blank values to define dynamic boundaries.
- Handle mixed types safely: convert to `str()` before pattern matching, explicitly check for `None` or empty strings.
- Parse two-column lookup tables into dictionaries early. Strip whitespace on keys/values.
- Track state across rows for grouped/repeating headers or fragmented data (e.g., `EMPTY -> NON_EMPTY` transitions).
- Cross-reference provided examples/"After" sheets to infer implicit patterns and validation targets.

## Writing Output

- **Clear & Prepare**: Explicitly clear target ranges before writing. Reset both `cell.value` and `cell.fill` to prevent stale content/background colors.
- **Data Handling & Formatting**: Store native Python types (e.g., `datetime`, `float`) and apply `cell.number_format` for display. Never convert datetimes to formatted strings.
- **Bulk Writes & Lookups**: Map data to dictionaries for O(1) lookups and bulk value replacements. Preserve grouping keys during aggregation.
- **Fragmented Data & Delimiters**: Detect block transitions. Insert separator rows only between blocks. Strip whitespace and filter empty strings from delimiter-separated values. See [Data Processing Patterns](references/data-processing-patterns.md) for parsing helpers.
- **Formulas & Ranges**: Assign formulas as exact strings. Ensure ranges explicitly exclude the target cell. Anchor lookups with `$` and adjust query references relatively.
- **Structural Changes**: Use native APIs (`delete_cols()`, `append()`, `insert_rows()`). Sort indices in descending order for batch insertions/deletions to prevent index shifting.
- **Deterministic Output**: Use `sorted()` or `collections.Counter` for frequency sorting to ensure reproducible results.

## Verification

- **Read-Back Confirmation**: Reload the saved workbook (`data_only=True` if needed) and immediately read back target ranges to confirm values/formulas persisted correctly.
- **Dimension & Structure Check**: Validate final row counts, column alignment, and fixed-width constraints against expected bounds. Confirm sequential IDs are contiguous and state variables were reset.
- **Data & Type Validation**: Cross-check aggregated results against raw data. Verify transformed cells retain correct Python types and that `number_format` matches requested styles.
- **Error & Boundary Checks**: Inspect samples for `#REF!`, `#N/A`, or `#VALUE!` errors. Use absolute thresholds (`abs(val) < 0.01`) for floating-point sums. Check for trailing delimiters or unstripped whitespace.
- **Final Sign-Off**: Do not mark complete until all transformations, formatting, and data integrity checks pass.

## Common Pitfalls

- **Index Shifting**: Deleting or inserting rows sequentially shifts indices. Always collect indices and process in reverse (bottom-to-top) order.
- **Type & Value Handling**: Never call string methods directly on `cell.value` without wrapping in `str()`. Validate types before numeric conversion. Avoid exact equality on floats; use absolute thresholds.
- **Stale Data & Formatting**: Clearing content does not remove background colors. Always reset `cell.fill` when clearing. Store native types and use `cell.number_format` for display.
- **Formula & Range Errors**: Self-referencing formulas cause fatal errors. Ensure ranges explicitly exclude the target cell. Anchor lookups with `$` and adjust relatively.
- **Header & Label Normalization**: Modifying source labels (case, stripping) breaks exact matches. Copy source strings verbatim.
- **Over-Scanning & Hardcoded Bounds**: Checking full rows or assuming fixed ranges causes incorrect results. Restrict checks to exact specified ranges. Verify actual used ranges programmatically.
- **Non-Deterministic Output**: Unsorted collections lead to flaky results. Always `sorted()` before joining or writing. Use `collections.Counter` for frequency sorting.
- **StyleProxy Errors**: Avoid direct assignment of `cell.font` or `cell.alignment`. Instantiate new `Font()`/`Alignment()` objects by copying properties. See [Sorting & Formatting](references/sorting-and-formatting.md) for safe style assignment.


## New Section

## Formula Patterns

- **Expanding Ranges for Cumulative Logic**: Anchor the start of ranges with absolute references (`$A$2`) and leave the end relative (`A{row}`). When copying down, this automatically creates a cumulative range.
- **Suffix Checking**: To verify if a string ends with a specific substring, use `=RIGHT(cell, LEN(check_cell))=check_cell`. This reliably extracts the last N characters and compares them to the target.
- **Multi-Condition Existence Checks**: Use `COUNTIFS(range1, criteria1, ...)` or `=INDEX(return_col, MATCH(1, (cond1)*(cond2), 0))` to verify multiple criteria simultaneously.
- **Priority Decisions with Nested IFs**: Chain `IF` statements to evaluate conditions in strict order. The first `TRUE` short-circuits and returns its result.