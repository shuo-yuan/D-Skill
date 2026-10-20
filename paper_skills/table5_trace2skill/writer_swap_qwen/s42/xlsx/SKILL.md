---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow

Follow an inspect→plan→write→verify loop for every spreadsheet task.

1. **Inspect first.** Verify the file path exists, then load with `openpyxl.load_workbook()`. Print sheet names, dimensions, and sample rows. Use the task's `answer_position` when provided; otherwise detect boundaries dynamically.
2. **Determine output type.** Examine the task and any reference/desired output. Write computed values unless live Excel formulas are explicitly expected. Formula strings can appear empty when read with `data_only=True`.
3. **Prepare the destination.** Clear the target sheet or explicit range before writing; create a new workbook when the answer position refers to a sheet not present in the input. Remove extraneous sheets before saving.
4. **Transform data safely.**
   - Verify dependencies before writing formulas; confirm the exact cells that contain source/intermediate values.
   - Precompute filtering boundaries and extract criteria into variables before loops.
   - Use dictionary lookups keyed by stable identifiers; strip keys and values. Avoid positional row alignment.
   - Normalize search strings case-insensitively (`.lower()` or `re.IGNORECASE`).
   - Cast cell values to `str` before methods like `startswith`, `replace`, or `split`; handle mixed types with `isinstance`.
   - Delete or insert rows bottom-to-top; use batch calls such as `delete_rows(start, count)`.
   - Use openpyxl range objects (`ws['A1:A10']`) instead of manual index arithmetic.
   - Split delimiter text with `[p.strip() for p in str(v).split(';') if p.strip()]`.
   - Filter out `None`/empty values before processing.
   - For frequency counts, use `collections.Counter`; sort by counts.
   - For multi-level sorting, use tuple keys; see [references/sorting-patterns.md](references/sorting-patterns.md).
   - For pattern extraction, use bounded regex like `re.search(r'Tag-([^,]*)', text)`.
   - For aggregations between markers, locate marker positions first, then iterate consecutive marker pairs.
   - For context-dependent cells, use a two-pass approach: first compute group aggregates, then assign values row-by-row.
   - Date parsing and style copying: normalize dates before sorting and copy styles safely; see [references/openpyxl-patterns.md](references/openpyxl-patterns.md).
   - For multi-step transformations, write a complete openpyxl script and execute it; prefer scripted, formula-light computation unless formulas are required.
5. **Write output.** Assign values or formula strings directly (e.g., `ws['D2'] = '=SUMIF(A:A,"111111",B:B)'`), save with `wb.save(path)`, and recalculate formulas if present.
6. **Verify.** Reload from disk and inspect the header plus a sample of data rows before marking complete.

## Inspection

Before writing any manipulation code, load the workbook and inspect the actual structure.

- Print `wb.sheetnames`, dimensions (`max_row`, `max_column`), and sample rows. If an `answer_position` range is provided, use that exact range; otherwise detect boundaries dynamically.
- **Dynamic header discovery**: scan the first row, normalize with `lower().strip()`, and map header names to column indices. Never hardcode indices. Example:
  ```python
  header = [str(c).lower().strip() for c in next(ws.iter_rows(min_row=1, max_row=1, values_only=True))]
  target_col = header.index('target name')
  ```
- **Dynamic range detection**: when a worksheet contains multiple independent blocks separated by blank rows, scan key identifier columns for empty cells to determine start/end boundaries.
- **Dependency tracing**: before writing formula or logic, read the actual cells that hold source and intermediate values; do not assume positions.
- Map column letters to 0-based list indices explicitly; column indices can be robust, but print headers to confirm.
- Check cell values robustly with `cell.value is None or str(cell.value).strip() == ''`.
- When searching for substrings, iterate rows and use `if substring in str(cell_value)`. For text filters, use case-insensitive matching (`substring.lower() in str(cell_value).lower()`).
- For mixed-type columns, branch with `isinstance(value, str)` and parse each type appropriately.
- For delimiter-separated values, strip whitespace and filter empty strings.
- **Repeating section headers**: track a `prev_was_header` boolean and collect the next row's value instead of assuming a flat layout.
- **Block-based mapping**: when assigning sequential values to blocks filtered by a condition, advance the source index only for matching blocks to preserve alignment.
- If a Desired Results or reference table exists, inspect it before writing to confirm target structure, sort order, separators, and edge cases.
- Inspect any provided 'after' sheet to infer implicit selection/highlighting criteria.
- Identify stable identifier columns (e.g., numeric IDs) rather than relying on fragile full-text columns.
- For numeric or mixed ID ordering, sort numerically: `sorted(ids, key=lambda x: int(x) if str(x).isdigit() else x)`.
- Validate file paths before loading; on FileNotFound, list parent directories to resolve the correct path.

## Writing Output

- **Values vs formulas.** Write computed values unless live formulas are explicitly required or ground truth contains formulas. If using openpyxl, assign formula strings to `.value`, then recalculate and read back.
- **Clear destination.** Clear target cells and fills before writing; set `cell.value = None` and reset `cell.fill`. Create a new workbook when the answer sheet does not exist in the input; remove extraneous sheets.
- **Placement.** Use exact task/`answer_position` cells; do not infer output locations from data bounds. Use `startcol=6` in `to_excel()` for column-offset output.
- **Structural changes.** Use native APIs (`delete_cols()`, `append()`, `delete_rows()`). Delete rows bottom-to-top and check only columns specified by the task.
- **String and type safety.** Cast cell values to `str` before replacing/stripping. Convert regex-cleaned numeric strings to `float`/`int`. Preserve `number_format` based on Python type; copy font, border, fill, alignment, and number format from source cells. Create new `Font` or `Alignment` objects instead of assigning proxies; see [references/openpyxl-patterns.md](references/openpyxl-patterns.md).
- **Bulk updates.** Use a replacement dictionary instead of long `if-elif` chains. For deduplication, collect unique values in a set and sort before joining.
- **Mapping and synchronization.**
  - Build identifier-keyed lookup maps for cross-sheet sync.
  - Preserve original column indices alongside values (e.g., `(value, column_number)`) when grouping and mapping.
  - For sequential block mapping, advance the source index only for matching blocks.
  - For grouped output, copy the grouping key into each output row.
- **Formula writing.** Construct formulas programmatically for repetitive patterns; each cell must get its own formula string because relative references do not auto-adjust on assignment.
  - `=SUMIF(criteria_range, criteria, sum_range)` for label-based summation.
  - Expanding cumulative range: anchor start absolute and leave end relative (`=SUM($A$2:A2)`).
  - Priority decisions: nest IF statements in priority order.
  - Multi-condition existence: `=IF(COUNTIFS(...)>0,"Yes","No")`.
  - Label lookup: `=INDEX(return_range, MATCH(lookup_value, label_range, 0))`.
  - Two-way lookup: `=INDEX(return_column, MATCH(1, (row_header_col=row_cond)*(col_header_col=col_cond), 0))`.
  - Multi-criteria concatenation: `MATCH(lookup1&lookup2, array1&array2, 0)`.
  - Suffix check: `=RIGHT(cell, LEN(check_cell))=check_cell`.
  - Guard blank inputs with `=IF(cell="","",...)`.
- **Restructuring and grouping.**
  - Group fragmented data by detecting empty-to-non-empty transitions; when reassembling, add separators only between blocks.
  - Wide-to-long unpivoting: extract constant fields once, then loop over variable columns.
  - Header handling: after filtering, if the first result row should become the header, set the `header` argument in `to_excel` accordingly.
  - For chunked row mapping, compute source indices with `(target_row - offset) * chunk_size + base_row`.
- **Filling sequences.** Track `last_valid` and reset counters when group keys change; for base-26 alphanumeric continuation, see [references/alphanumeric-sequence.md](references/alphanumeric-sequence.md).
- **Formula references.** For gap-aware counting and zero-padded strings, see [references/formula-patterns.md](references/formula-patterns.md).
- **Read back after writing.** Reopen the saved file and print or check target cells before declaring success.

## Verification

After every write operation, reload the output file with `openpyxl` (or `data_only=True` for calculated values) and verify:

- Print or assert modified cells; inspect the header row and representative sample rows.
- Sample the first 15–20 rows plus boundary rows (first, last, and around markers).
- Compare against any reference table or Desired Results before and after writing.
- Check blank cells with `cell.value is None or str(cell.value).strip() == ''`.
- After row insertions, verify newly inserted rows are empty and original rows shifted correctly.
- After deletions, verify group sizes and final row counts.
- Verify formatting matches the source (`number_format`, alignment, fill).
- Check formula results for `000`, `#REF!`, or calculation errors; ensure no target cell is inside its own formula range.
- Confirm final dimensions match the expected `answer_position` (row and column counts).
- Validate sheet names against `set(wb.sheetnames)` instead of hardcoding.
- Confirm all expected IDs/rows are present and ordered; spot-check tie-breaking and whole-number values (`float(value) == int(float(value))`).
- Use floating-point thresholds (`abs(value) < 0.011`) rather than exact equality for zero checks.
- If available, run `evaluate_output` for a definitive cell-level comparison.
- After writing formulas, recalculate before reading back; check adjacent cells were not unintentionally overwritten.

## Formula Patterns

When building formulas:

- Use `COUNTA` with a dynamic relative range (e.g., `COUNTA($B$3:B8)`) to create sequential numbers that skip gaps.
- Wrap numeric results with `TEXT(..., "000")` to enforce zero-padded fixed-width strings.
- Anchor shared context values with absolute references (`$B$2`) while keeping row-specific ranges relative (`$B$3:B3`).

## Common Pitfalls

- **Path and sheet assumptions.** Long paths cause `FileNotFoundError`; verify before opening. Print sheet names and confirm the active sheet. Do not assume sheet names or positions match the task description.
- **Hardcoded row/column indices.** Use dynamic header discovery, `answer_position`, or detected boundaries. Off-by-one conversions between column letters and array indices are common; print headers to confirm.
- **Row deletion order.** Always delete bottom-to-top; prefer batch calls such as `delete_rows(start, count)`. Forward or top-to-bottom deletion skips rows.
- **Over-checking row emptiness.** When evaluating rows for deletion, check only the columns specified in the task, not the entire row.
- **Target-aware pruning.** Locate boundary rows first and evaluate only the intended region above or below them.
- **Sequential restarts.** When an instruction says to restart from the cell immediately after a match, advance two positions: skip the matched cell, then set the next cell. A single-step advance inflates counts.
- **Formula vs value confusion.** Writing formula strings when an evaluator reads with `data_only=True` can produce empty cells. Write computed values unless formulas are required. If formulas are required, use openpyxl direct formula injection rather than simulating keystrokes.
- **Circular references.** A target cell inside its own formula range causes `000` or `#REF!`; adjust the range to exclude the target cell first.
- **Complex formulas.** Avoid deeply nested IF/AND formulas for ranking or top-N-per-group tasks; use programmatic grouping and sorting.
- **String and type safety.** Cast values to `str` before pattern methods. Do not apply one transformation to mixed-type columns. Regex cleaning returns strings—cast back to numeric types.
- **openpyxl fill/color.** Cell fill colors are RGB objects; always use `str(cell.fill.start_color.rgb)` before substring checks.
- **openpyxl styles.** Never assign `cell.font` or `cell.alignment` directly from another cell; copy properties into new `Font`/`Alignment` objects.
- **Changing strings vs clearing cells.** When deleting a substring from a cell, retain the rest of the cell's content; clear the entire cell only when instructed.
- **Delimiters.** Strip whitespace and filter empty strings when splitting; use boundary-aware separators to avoid trailing blank rows. Do not add an extra separator when the string already ends with one.
- **Case-sensitive matching.** Use lowercase comparisons for text filters; do not build multiple case variations.
- **Alignment assumptions.** Do not assume two sheets or tables are positionally aligned; use stable identifier-keyed dictionaries.
- **Duplicate keys and deduplication.** Use composite keys rather than single-column matches; see [references/data-cleaning-patterns.md](references/data-cleaning-patterns.md).
- **Missing keys and blanks.** Check for missing lookup keys and map them to a designated value instead of letting `KeyError` or `None` propagate; filter `None` to avoid literal `'None'` output.
- **Floating-point comparisons.** Use `abs(sum(...)) < tolerance` instead of `sum(...) == 0`.
- **Skipping verification.** Not reading the saved output is a leading cause of undetected off-by-one and wrong-range bugs.
- **Manual clearing instead of native APIs.** Use `delete_cols()`, `append()`, etc. for structural changes.
- **Overwriting existing work.** Modify only the specified cells; verify other rows and formulas remain intact.
- **Off-by-one interval aggregation.** Locate marker positions first and iterate consecutive marker pairs.
- **Header corruption.** Respect exact start and end rows; headers usually start at row 1 unless stated.
- **VLOOKUP whitespace.** If values look equal but return `#N/A`, wrap the lookup range with `TRIM()`.
- **Reverse search direction.** When searching upward for the nearest value, iterate `range(reference_row - 1, 0, -1)`; top-down scanning returns the wrong match.
- **Skipping file saves.** Forgetting `wb.save()` loses all modifications.
- For detailed multi-level sorting examples, see [references/sorting-patterns.md](references/sorting-patterns.md).

## Data Cleaning

For deduplication tasks, follow [references/data-cleaning-patterns.md](references/data-cleaning-patterns.md). The patterns cover composite-key grouping, conditional preservation when groups contain mixed priority types, and safe row deletion (check group size, preserve the first occurrence, and verify the final row count).

## Proven Patterns

- **Two-pass aggregation for context-dependent cells.** First scan to build group-to-aggregate maps, then iterate rows again using those aggregates and previous-row context.
- **Sequence-based boundary detection.** Compare each row's group identifier with the previous row's identifier in a linear scan; do not rely on formulas that assume contiguous grouping.
- **Reverse-iteration upward search.** Use `range(reference_row - 1, 0, -1)` to find the nearest match above a reference row.
