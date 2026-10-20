---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow

- Validate file paths and resolve to absolute paths before loading.
- Inspect actual workbook structure (sheet names, headers, dimensions) rather than relying on documentation.
- Use `openpyxl` (or `pandas`) for modifications. Prefer direct Python scripting/file-based execution to bypass shell escaping.
- Precompute thresholds, boundaries, filters in memory; build lookup dictionaries for O(1) cross-referencing.
- Use `answer_position` to determine exact row ranges instead of guessing.
- For structural changes (deleting/inserting rows), always collect indices first and operate in reverse order (highest to lowest), or use batch deletion calls.
- Compute results programmatically in memory (write numeric values) rather than writing Excel formulas, unless explicitly requested.
- Use composite tuple keys for stable multi-level sorting.
- Save explicitly, then immediately reload the output file to verify dimensions, content, and formula evaluations.
- Clear target ranges before writing to prevent stale data contamination.
- See [Formula Patterns](references/formula-patterns.md) for lookup, ranking, and programmatic construction patterns.

## Inspection

- Load the workbook first and print full data/sheet names/dimensions to understand structure.
- Cross-reference task instructions with actual sheet names, headers, and dimensions; look for reference sheets.
- Dynamically discover target columns by scanning header row; strip whitespace, normalize to lowercase, locate indices by name or prefer 0-based indices.
- Validate cell types before numeric conversion (`isinstance()` or `try/except`); handle headers, `None`/null, mixed types.
- Detect dynamic boundaries by scanning for first/last non-blank cells or empty blocks.
- When searching for a value above a reference row, iterate backwards/upward to capture the closest match.
- Use robust blank checking (`cell.value is None or str(cell.value).strip() == ''`) and case-insensitive string matching.
- When inspecting cell properties (e.g., colors, formats), convert objects to strings first to avoid errors.
- Use dictionaries for O(1) lookups instead of iterating rows repeatedly.
- Carefully map between 1-based cell references and 0-based list indices.
- Strictly limit operations to specified ranges.

## Writing Output

- Parse explicit output cell addresses literally; avoid inferring from merged cells.
- Write computed numeric results as literal values (int/float), not Excel formulas, unless explicitly requested.
- Preserve grouping keys during aggregation/merging.
- Format consistently: apply required number formats (`cell.number_format`) to all numeric outputs. Handle zeros explicitly if blanks are required.
- When deleting/inserting rows iteratively, process bottom-to-top or collect indices first.
- For multi-criteria lookups, use programmatic dictionaries or `INDEX/MATCH`. For category-based ranking, use Group-Then-Sort (group, sort independently, map back using preserved indices).
- Generate formulas programmatically using loops if required. Anchor constants with absolute refs (`$A$1`) and use relative ranges for row-specific logic.
- For multi-column sorting, use a single `sort()` call with a tuple key.
- Use `TRIM()` on lookup ranges to handle invisible whitespace.
- Apply `cell.number_format` for display formats. To copy formatting, instantiate new `Font()`/`Alignment()` objects to avoid `StyleProxy` errors.
- For duplicate lookup keys, store only the first encountered value for deterministic results.
- Explicitly remove any sheets not required in the final output.
- Suffix Matching: Use `=RIGHT(cell, LEN(check_cell))=check_cell` to verify if a string ends with a specific substring.
- See [Lookup Patterns](references/lookup-patterns.md) for two-way INDEX/MATCH.
- See [Programmatic Formulas](references/programmatic-formulas.md) for loop generation strategies.
- See [Conditional Ranking & Index Tracking](references/conditional-ranking-patterns.md) for category-based sorting and top-N ranking.
- See [Indexing & Mapping Patterns](references/indexing-patterns.md) for dynamic row/column transposition and chunk handling.

## Verification

- Read back target cells immediately after writing and compare against expected results.
- Save, reload, and print row counts/content to verify post-manipulation state.
- Verify output dimensions (row/column counts) match expected `answer_position`.
- Cross-check every computed value against explicit placement instructions; validate output dimensions, data types, and sorting results.
- Use absolute value threshold comparisons (e.g., `abs(sum()) < 0.01`) instead of exact equality for floating-point checks.
- Inspect output rows for `None` strings, empty artifacts, `#REF!`, or calculation errors.
- Spot-check 3-5 cells across different groups, including exact, partial, and non-matches.
- Ensure data outside the target range remains intact.
- Never declare a task complete without confirming data integrity.

## Common Pitfalls

- **Index Shifting**: Deleting top-to-bottom shifts subsequent indices. Always delete backwards or collect indices first.
- **Type Errors & Mixed Data**: Headers often contain strings or `None`. Validate types before numeric operations.
- **Floating-Point Artifacts**: Tiny precision errors break exact zero checks. Use tolerance thresholds.
- **Hardcoded Ranges & Indices**: Break when workbooks change size or layout. Always scan headers dynamically.
- **Sequential Sorting**: Destroys previous sort levels. Use composite tuple keys for multi-level sorts.
- **StyleProxy Errors**: Directly assigning `cell.font` copies a proxy. Instantiate new `Font()`/`Alignment()` objects.
- **Formula & Reference Errors**: Mixing absolute/relative references incorrectly breaks dynamic ranges. Anchor constants properly. Never include the target cell in its own calculation range.
- **Inline Execution & Shell Escaping**: Avoid inline bash for script execution due to escaping conflicts. Use file-based Python execution.
- **Stale Data & Unconditional Overwrites**: Failing to clear target ranges leaves old values. Always clear first and conditionally copy.
- **Lexicographical Sorting of Numeric IDs**: Sort numerically to avoid lexicographical ordering.
- **Assuming `cell.value = None` removes background colors**: Explicitly reset fill properties.
- **Off-by-one errors**: Verify index conversions between list positions and cell coordinates.
- See [Sequential Filling & Grouping Patterns](references/sequential-filling-patterns.md) for detailed implementation logic.
