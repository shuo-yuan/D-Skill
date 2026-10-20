---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow

1. Inspect: Load workbook, verify sheet names/headers, check structure, and identify dynamic boundaries using `answer_position` or header scanning.
2. Process: Map data using Python dictionaries for O(1) lookups. Handle duplicates with composite keys. Sort explicitly (e.g., tuple keys for multi-criteria) to prevent lexicographical errors.
3. Transform: Implement all logic in a single Python script using `openpyxl`. Precompute thresholds, filter boundaries, and calculate values in memory. Write numeric literals directly unless formulas are explicitly requested.
4. Modify: Delete rows bottom-to-top or collect indices first. Clear target ranges explicitly before writing to prevent stale data contamination.
5. Verify: Reload the saved file, read back a representative sample, and cross-check computed results against expectations before marking complete.

## Inspection

- Enumerate sheets, headers, and dimensions. Discover column indices dynamically (case-insensitive, strip whitespace); map 1-based letters to 0-based indices carefully.
- Scan identifier columns for empty cells to dynamically detect data boundaries; restrict blank-row detection to relevant ranges.
- Handle mixed types safely: convert values to strings (`str(cell.value)`) before pattern checks, explicitly handle `None`, and use `.lower()` for keyword matching.
- Validate data types (`isinstance`) and wrap numeric conversions in `try/except`.
- Check if target cells fall within their own formula's range to detect circular references early.
- Use `INDEX(range, MATCH(identifier, label_range, 0))` for label-based lookups instead of hardcoding row positions.
- See [references/openpyxl-patterns.md](references/openpyxl-patterns.md) for robust date parsing and multi-criteria sorting code patterns.
- See [references/regex-patterns.md](references/regex-patterns.md) for reliable delimited tag extraction.

## Writing Output

- Clear destination ranges by setting cells to `None` AND removing background fills (`cell.fill = PatternFill(...)`) to prevent stale data/color contamination.
- Use dictionary mappings for bulk insertions; handle missing keys gracefully.
- Apply safe styling: instantiate new style objects instead of direct assignment (`cell.font = ...`) to avoid `StyleProxy` errors.
- Write formulas as plain strings. Use absolute references (`$`) for constants and relative ranges for row-specific logic. Guard against self-referencing ranges.
- For multi-level sorting, use Python's `sorted()` with tuple keys.
- Apply type-aware formatting: explicitly set `number_format`, use `TEXT()` for zero-padding, and convert zero sums to blanks if required.
- See [references/formula-patterns.md](references/formula-patterns.md) for advanced conditional, cumulative, and string-matching logic.
- See [references/mapping-patterns.md](references/mapping-patterns.md) for detailed row/column mapping logic.
- See [references/sequence-generation.md](references/sequence-generation.md) for stateful filling and base-26 patterns.

## Verification

- Mandatory reload: Immediately reload the saved file and inspect dimensions, row/column counts, and sample content.
- Cross-check extracted data against source samples to ensure `None` values were filtered and output structure matches expectations.
- Validate formulas: check for `#REF!`/`#VALUE!` errors, confirm absolute/relative references produce consistent results, and verify no formulas were overwritten.
- Use tolerance for floating-point comparisons (e.g., `abs(total) < 0.01`) and `float_val == int(float_val)` for whole-number checks.
- Trust the evaluation tool's computed-value comparison over superficial cell-type differences.
- See [references/formatting-and-formulas.md](references/formatting-and-formulas.md) for detailed number formatting rules and validation steps.

## Common Pitfalls

- **Index Shifting & Forward Deletion**: Deleting rows in forward order shifts indices. Always iterate bottom-to-top or collect targets first.
- **Naive Empty-Cell Checks**: `cell.value == ''` misses `None` and whitespace. Use `cell.value is None or str(cell.value).strip() == ''`.
- **Incremental Modifications**: Avoid modifying cells one by one in an agent loop. Use a single script execution for the entire transformation.
- **Hardcoded References**: Never hardcode sheet names, row indices, or column positions. Use dynamic discovery or `INDEX/MATCH`.
- **StyleProxy & Type Mismatches**: Directly assigning `cell.font` raises errors. Instantiate new style objects. `openpyxl` stores fills as RGB objects; convert to string before checking.
- **Fragile Text Matching**: Never rely on exact string equality or row position. Map by stable keys, strip whitespace, and use case-insensitive matching.
- **Sorting Defaults**: Default alphabetical sorting breaks numeric IDs. Use explicit tuple keys for multi-level sorting.
- **Shell Escaping**: Inline Python in bash fails on special characters. Use file-based execution for complex scripts.
- **Verification Gaps**: Skipping post-save re-reading masks incomplete edits or formula errors. Always reload and cross-check.
- **Trailing Empty Rows**: Occur when flattening data. Verify if separators are needed after the final block.
- **Circular References & Merged Cells**: Target cells must not fall within their own formula's range. Unmerge or handle merged cells carefully.


## References

- [references/deduplication-patterns.md](references/deduplication-patterns.md) — Composite key grouping, priority preservation, and safe row deletion rules.
- [references/scripting-patterns.md](references/scripting-patterns.md) — Detailed regex patterns, `openpyxl` templates, and best practices for cell-level transformations.