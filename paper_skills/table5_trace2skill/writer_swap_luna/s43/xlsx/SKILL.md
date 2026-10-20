---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow

1. **Inspect**: Load the workbook, enumerate sheet names (use exact names as reported by the workbook), and examine the first ~20 rows to identify headers, data boundaries, blank separator rows, merged cells, and target ranges. Check for an existing "Expected" or "Output" sheet that defines the target schema or summary layout.
2. **Plan**: Determine the operation and identify source worksheets. When a summary sheet marks a boundary, process only sheets appearing before it. For multi-sheet updates from a reference sheet, use aligned row-wise mapping (e.g., copy `Reference!B[row]` to column B of each target sheet for every populated row). Identify target columns, used row bounds, and the exact populated range to operate on.
3. **Execute**:
   - Scan the full data range; do not stop at the first blank row or header. Collect all valid records from every data block.
   - When filtering by relative dates, compute the cutoff from the maximum valid date in the relevant column (e.g., `MAX(column) - 30 days`). Use inclusive comparisons (`start <= value <= end`).
   - When filtering or relocating rows: read criteria from designated cells, clear the entire destination range before writing, and copy both values and source cell styles.
   - For row deletions, iterate bottom-to-top to avoid index shifting. Start below the header row. For prefix-based filtering, confirm the cell contains a string, then use `startswith` with the exact prefix.
   - Sort rows as tuples by the explicit sort key; never sort columns independently. Regenerate derived indices (e.g., sequence numbers) in final order.
   - When transferring data, only overwrite destination cells if the source contains a value (not `None`/empty). Preserve existing values when the source is blank.
   - Resolve formulas in Python and write materialized values when the grading environment reads stored cell values. Use spreadsheet formulas (e.g., `=SUM(...)`) for combined totals so they update automatically.
   - For detailed patterns on rebuilding summary tables, see [references/summary-rebuild-patterns.md](references/summary-rebuild-patterns.md).
4. **Save & Verify**: Save to the exact output path specified. Reopen the workbook and verify the written cells, confirming file existence, correct values, and intact formatting.

### Selecting Cells by Formatting
When filtering cells by fill color or other formatting, always require BOTH the target formatting condition AND a nonblank value. Exclude formatted-but-empty cells to avoid propagating blank placeholders.

### Transposing Data
When transposing a vertical range to a horizontal range (or vice versa), collect retained values into a list first, then write them sequentially from the first destination cell without gaps. Do not preserve original spacing.

### Writing to Destination Ranges
Before writing output, clear the entire target range. After writing, apply the requested formatting (fill, borders, etc.) to every populated cell individually. This prevents leftover values or formatting from previous runs from corrupting the result.

### Modifying Rows
When removing multiple rows based on cell criteria, always iterate from the bottom row upward to prevent shifting indices of rows still to be evaluated. Start from `ws.max_row` down to the first data row (usually row 2) to preserve headers.

### Filtering Data
When applying range-based filters (e.g., numeric thresholds), test both actual numbers and strings that can be converted to numbers via `float()`. Apply all filters together in memory before writing, rather than incrementally, to prevent unwanted rows from passing through.

### Text Processing
For text cleanup, use literal string replacement (`str.replace()`) instead of regex to avoid unintended side effects. Convert cell values to strings with `str()` before slicing or calling string methods.

### Grouping Tasks
Use the requested reference column as the grouping key, preserve first-seen group order, and consolidate each group into one output row. Retain the first row's identifying fields and aggregate the remaining value columns in a single pass through the data.

### Formula Generation
Plan logic systematically, handle edge cases (ties, empty cells, boundary conditions), and generate formulas mapping source to target cells precisely. Lock lookup ranges with absolute references (e.g., `$B$2:$B$8`) and wrap in `IFERROR` to return `""` for missing keys.

### Dynamic Intervals from Boundary Markers
When a column contains repeated markers that define intervals: track the previous marker row and compute the current interval as `previous + 1` through `current - 1`. If a marker immediately follows the previous marker, return `0` (or the defined empty-interval result). Do not hardcode fixed ranges.

### Sheet Synchronization
To align sheets to an authoritative ID list: map existing rows by unique ID into a dictionary, iterate through the authoritative list in order, reuse existing rows or insert placeholder rows (ID plus blanks), then copy formatting from a reference layout sheet. See [Sheet Synchronization Pattern](references/sync-pattern.md).

### Subset-Sum and Combination Tasks
Enumerate all candidate cells, compute sums of all subsets programmatically, and select a combination within the required tolerance. Convert zero-based array indexes to worksheet row numbers (index + 1), apply all modifications in one batch, and save to the requested output path.

### Row Deletion
When deleting rows above a target row, scan top-to-bottom and stop at the first matching row. If its index is greater than 1, delete only rows 1 through the row immediately above it; never delete the matching row itself.

### Moving Columns
When moving a column whose position may vary between runs:
1. Scan the header row for the exact label to locate the source column index.
2. Insert the destination column first, then adjust the source index to account for the shift (e.g., `source_index + 1` if the destination was inserted to the left).
3. Copy values, cell styles, and column width from the source before deleting the original column.
4. Verify the moved header and data appear in the correct destination and that totals remain intact.

### Deduplication and Aggregation
- When uniqueness depends on multiple columns, combine them into a composite key (e.g., a tuple of values) and use an in‑memory dictionary keyed by that composite.
- Process rows in a single pass: read each row, build the composite key, and aggregate values directly in the dictionary.
- Populate target ranges programmatically: when a task requires formulas across a contiguous range, generate the formula for each row in a loop (e.g., using openpyxl) and save the workbook. This ensures every required cell is populated and avoids manual copy-paste errors.

### Lookup with Duplicate Keys
- Iterate through all source rows and collect every matching record; do not stop at the first match.
- For multi-column returns, flatten each matching record's value columns into one ordered sequence before writing across consecutive output columns.

### Filtering and Contiguous Output
- Apply all filters (inclusion, exclusion, keyword) before writing any output.
- Write qualifying rows contiguously to the destination, preserving only requested columns.
- Save the workbook to the exact output path specified, then report the path and row count.

### Frequency-Based Organization
For frequency-based organization, compute a frequency map and preserve deterministic tie ordering (sort by negative frequency, then first appearance).

### Save
Always save the workbook to the exact output path specified by the task.

## Inspection

- Before editing, load the workbook and verify sheet names (use exact names as reported by the workbook, not the task description). Read the first ~20 rows to identify headers, data boundaries, blank separator rows, and formatting patterns. Do not assume fixed blank-row ranges.
- Identify the full data range including all relevant rows and columns; do not infer it from a partial preview. Include all rows/columns needed for lookup and return ranges.
- Identify all output blocks explicitly: for each block, note the column layout (item column, account-reference column, amount column, header row, total row). Do not rely on relative column offsets, as blocks may have different widths and layouts.
- When filtering rows by numeric criteria, account for both actual numbers and strings convertible to numbers; test numeric values directly and attempt `float()` conversion for strings before applying range checks.
- Before writing a derived cell, identify the source or intermediate cell that holds the needed value; do not reference the target cell itself.
- Call `openpyxl.load_workbook` and check `wb.sheetnames` for exact (case-sensitive) sheet names.
- Use `sheet.max_row` and `sheet.max_column` to determine populated ranges.
- Read a sample of rows to confirm column layout, headers, value formats, and existing formulas.
- To locate a column whose position may change, scan the header row for its label instead of hardcoding a column letter.
- Determine the full data extent (last row/column with values) before constructing any ranges.
- Check existing formulas for the range patterns they use; align new formulas with those patterns unless instructed otherwise.
- Identify the complete graded/answer range—include dependent cells that rely on formulas, not only cells you will directly edit.
- Enumerate workbook sheets and sample rows before editing to identify sheet names, dimensions, headers, and target ranges.
- Read source data values exactly as they appear, preserving plural forms, capitalization, and whitespace. Use these exact strings for headers and data mapping unless explicitly instructed otherwise.
- Identify the first and last nonblank cells in the target column before modifying rows.
- When selecting cells based on formatting (e.g., fill color), also require a nonblank value to avoid including empty placeholders.
- Inspect and handle mixed data types (e.g., datetime objects and strings) within the same column.
- Check for merged cells using `worksheet.merged_cells.ranges`; unmerge any overlapping target areas before writing.
- Look for an existing "Expected" or "Output" sheet that defines the target schema or summary layout.
- Use blank rows and header rows to detect independent data blocks dynamically, instead of assuming fixed ranges.
- For case-insensitive partial-match requirements, normalize cell values to strings via `str(v).casefold()` before testing keyword membership.
- When searching for text, normalize both cell values and target to lowercase (or casefold) for case-insensitive matching. Restrict inspection to the specified column(s) and row range.
- Distinguish between literal values (e.g., `"X"`) and formula results; match only the intended type.
- Before writing to any cell, inspect the worksheet's merged-cell collection. Unmerge any ranges that overlap the target cells to avoid blocked edits.
- When filtering by relative dates, scan the target column and compute the threshold from the actual maximum date found — do not assume a fixed reference date.
- When an instruction references a sheet by number, identify the worksheet by its position in the workbook (1-based index).
- Before editing formulas, read the worksheet's populated cells and dimensions to understand the actual data layout, headers, and criteria-list locations. This ensures formulas reference correct ranges and use appropriate absolute/relative references.
- For row operations, locate the target row by scanning the relevant column from row 1 downward and stop at the first cell that contains the target substring (case-insensitive).
- Before implementing a transformation, inspect the actual row-level data patterns: verify whether the task requires cumulative history, row-level values, or preservation of existing values.
- When searching a column for a target substring, scan top-down and stop at the **first** match. Normalize search strings and cell values using `casefold()` (or equivalent) for case-insensitive matching unless exact case is specified.
- Read numeric columns starting below header rows and validate each cell; skip non-numeric cells safely instead of aborting.
- **Distinguish literal text from Excel error values.** A cell displaying `#N/A` is not the string `"error"`; use `ISERROR`, `ISERR`, or `IFERROR`.
- When extracting text, use delimiter-based splitting (e.g., split on `Collection-` and take until the next field delimiter) rather than fixed character positions.
- Infer repeated layouts from examples: inspect completed cells to determine positional correspondence before filling remaining ranges.
- Before transforming grouped data, identify section boundaries. Repeated header rows (e.g., `date/id/batch`) mark separate data blocks; distinguish intentional separator blanks from redundant empty rows.
- When a target sum may be formed by multiple cells, exhaustively enumerate candidate subsets and retain combinations within the required tolerance. Map zero-based data indexes to corresponding worksheet row numbers before applying formatting.


## New Section

## Data Preparation

Normalize mixed data types before processing. For date cells that may contain strings or datetime objects, inspect the value type, strip recognized time suffixes from strings, and convert date-only strings or datetime values to date values. This ensures consistent underlying values for formatting.
## Writing Output

### Deletion and Structural Edits
- When an instruction refers to a numbered sheet (e.g., "the second worksheet"), apply structural edits to the worksheet at that workbook position, not by name.
- **Marker-based row trimming**: When output must start at a boundary marker (e.g., a cell containing "Code" in column A), locate that marker row first, then delete ALL rows above it—regardless of whether they are blank or contain data. Do NOT filter by blankness unless the task explicitly requests blank-row removal only.
- **Post-deletion validation**: After deleting rows, verify the marker is now in row 1 (or the intended position), data below remains intact, and no trailing rows were removed unintentionally.
- Delete rows from the bottom up and require compound deletion conditions (e.g., target marker in Column A AND the immediately following cell is empty) to avoid accidentally deleting data rows.

### Writing Values vs Formulas
- Prefer writing computed values directly instead of formulas when using libraries that do not recalculate formulas (e.g., openpyxl). Resolve references like INDIRECT/IFERROR in Python and write the resulting value.
- For combined totals, use spreadsheet formulas (e.g., `=SUM(...)`) referencing detail rows so totals update automatically.
- When a formula must be stored, ensure the cell also has a cached result; if the library cannot set cached results, avoid storing the formula.

### Formula Patterns
- **Lock lookup ranges with absolute references** (`$B$2:$B$8`) while keeping input references relative (`$B12`) so formulas can be copied across rows and columns.
- **Prefer INDEX/MATCH** over nested IF chains: `=INDEX(return_col, MATCH(lookup_value, lookup_col, 0))`.
- **Wrap lookups in IFERROR**: `=IFERROR(..., "")` to handle missing keys gracefully.
- **Multi-criteria lookups**: Use `(category_range=cat)*(expense_range=exp)` inside `MATCH(1,...,0)` to avoid always returning the first occurrence.
- **Two-dimensional lookups**: Use separate row and column MATCH calls; wrap in `IFNA(...,0)` where missing values should become 0.
- **OR-list matching**: Use `SUMPRODUCT(ISNUMBER(MATCH(data_range, criteria_list, 0)))` instead of passing a range as a single SUMIFS criterion.
- **Monthly date ranges**: Use inclusive lower bound and exclusive upper bound (`>= month_header` AND `< EDATE(month_header, 1)`). Avoid hard-coding day-31.
- **Summary totals**: Use `SUMIF(criteria_range, summary_label, sum_range)`, not COUNTIFS. Lock source ranges as absolute, keep summary-label references relative.
- For conditional totals across multiple dimensions, use `SUMIFS`. See [references/sumif-patterns.md](references/sumif-patterns.md) for working examples.
- For date-based lookups, determine whether the task needs exact or approximate match. Use approximate lookup (VLOOKUP with TRUE, or INDEX/MATCH with match_type 1) for "latest date at or before" logic.

### Data Transfer and Population
- **Avoid circular references**: For derived text, reference an upstream/intermediate cell, not the target cell.
- **Guard optional fields**: Use a nonblank check before transforming (e.g., `IF(F10<>"", LEFT(F10,1)&".", "")`) so blank sources produce blank output.
- **Preserve formatting**: When required, modify only cell values (`cell.value = new_value`); do not rebuild or copy worksheet structures unnecessarily.
- **Boundary-condition fills**: Require both current and preceding rows to meet continuation criteria to prevent fills from crossing blank-row boundaries. Skip cells that already contain values to preserve existing index or header rows.
- **Transposition**: Flatten source records in original order and pack into destination using a deterministic rule.
- **Match keys**: Use the specified key cell to identify the destination row, verify the match, then write the result.
- **Row compaction**: When removing interspersed blanks, filter rows where any cell in the relevant range is non-empty, copy each data row (values + styles) to the next available row in order, then clear trailing rows.
- When clearing and repopulating a block, preserve the total row: clear only data rows, write new data, and ensure the total row contains the correct label and formula. Use explicit column mappings per block, not relative offsets.
- When copying filtered data to a new sheet, preserve the table structure: include the header row, copy all populated columns, and transfer formatting and column widths where possible.
- Save the workbook to the exact output path and filename specified in the task.
- **String slicing**: When removing a fixed number of trailing characters, use direct string slicing (e.g., `str(cell_value)[:-3]`) rather than formula-based approaches.
- **Contiguous block writing**: Iterate over source rows; for each row that passes all filters, copy the specified source columns to the next available destination row, starting at the designated cell (e.g., A1). Do not leave gaps for filtered-out rows.
- **Conditional overwriting**: When transferring data, update destination cells only if the source cell contains a value (not `None` and not empty string). Explicitly clear non-matching rows in the target column.
- **Lookup-map enrichment**: Build a dictionary mapping keys to attributes from the lookup sheet, then apply it while generating output rows to avoid repeated searches.
- **Unpivot pattern**: To convert wide columns into long-format records, retain identifying columns and emit one row per variable column, copying the identifying values into each new row.
- **SUMIF totals**: For totals based on matching labels, use `SUMIF(criteria_range, summary_label, sum_range)`. Lock source data ranges as absolute references (e.g., `$B$12:$B$22`) and keep the summary-label reference relative (e.g., `A2`).
- **Distinct nonblank count**: Use `=COUNTA(UNIQUE(FILTER(range, range<>"")))` to count unique entries while excluding blanks.
- **Multi-cycle results**: When performing multiple cycles of analysis, write each cycle's summary formula to its designated endpoint cell rather than overwriting a single cell.
- **Paired-column sorting**: When sorting two-column records, collect each row as a (key, value) tuple, sort by the key column, and write both columns back to the same rows.
- **Style preservation**: Copy source row and cell styles, then apply required custom number formats only to aggregated numeric columns.
- **Formula best practices**: Prefer `INDEX`/`MATCH` for row-based lookups over long nested `IF` formulas. Lock lookup ranges with absolute references; keep input row references relative where needed. Wrap lookups in `IFERROR` to return `""` when keys are missing.
- **Conditional formulas**: Write formulas only on rows that satisfy the output condition; set all other target cells to `None` or the requested fallback value.
- For row deletion and filtering patterns, see [references/row-operations.md](references/row-operations.md).
- For tie-aware point distribution formulas, see [references/ranked-allocation-formulas.md](references/ranked-allocation-formulas.md).
- For large-scale deduplication and aggregation, see [references/in-memory-processing.md](references/in-memory-processing.md).
- Save the workbook to the exact file path specified in the task. Use `workbook.save(output_path)` without altering the filename or destination. Save only once after all output values have been written.
- Modify only the specified output cells; do not alter headers, formatting, or unrelated content. Save from the original input structure.
- Clear and repopulate only the specified output range; preserve existing headers and unrelated content.
- When copying or inserting rows, preserve formatting: copy cell styles, number formats, row heights, and hidden states from source rows. Apply number formats explicitly to every modified cell; do not rely on inherited formatting.
- For counting unique nonblank values in a range, use `=COUNTA(UNIQUE(FILTER(range, range<>"")))`.
- When performing multiple cycles of a task, place each cycle's summary or result in its own designated endpoint cell (e.g., the last row of that cycle's range) so that earlier results are not overwritten.
- For conditional sums matching any value from a list, use `SUMPRODUCT` with `ISNUMBER(MATCH(data_range, criteria_list, 0))` to create a Boolean mask. Avoid passing the list range directly as a single `SUMIFS` criterion.
- For monthly aggregation, use an inclusive lower bound and an exclusive upper bound: `date_range>=month_header` and `date_range<EDATE(month_header,1)`. This correctly handles months of all lengths and time components without hardcoding day numbers.
- Cumulative formulas: Use expanding mixed-reference ranges. Anchor the starting cell with `$` (e.g., `$A$2`) and let the ending cell be a relative reference that changes with the row (e.g., `A2`). This creates a range like `$A$2:A2` that grows when copied down.
- Priority-based outcomes: Nest conditional checks in the exact priority order specified by the task. Place the highest-priority condition first in `IF` or `IFS` functions, and use the fallback value only when all prior conditions fail.
- For repeated labels in lookup tables, match on all criteria instead of a single label: `(category_range=selected_category)*(expense_range=selected_expense)` with `MATCH(1,...,0)`.
- Anchor lookup ranges and selector cells with `$` when formulas will be copied: `Sheet2!$C$3:$G$20`, `$A$14`, `$A16`; only shift headers that must vary, such as `C$3`.
- For 2D lookups, use separate row and column `MATCH` inside `INDEX`, and wrap the result in `IFNA(...,0)` for missing combinations.
- **Row insertion order:** When inserting multiple rows based on original row numbers, process the targets in **descending** order (bottom to top) so that earlier insertions do not shift the positions of later targets.
- When using libraries that do not calculate formulas (e.g., openpyxl), write evaluated numeric or string values directly instead of formulas if the output will be inspected without recalculation. Use Python to compute the result and assign the value, not the formula.
- For lookups with duplicate keys: iterate all source rows, append values per match, and preserve source order. For multi-column returns: flatten each match's columns into a single row sequence.
- When extracting substrings from a cell, split on a known marker (e.g., "Collection-") rather than relying on fixed character positions. The marker may appear anywhere in the cell. After splitting on the marker, extract until the next field delimiter (e.g., comma) or end of cell. Trim whitespace from the result.
- For detailed extraction patterns, see [references/text-extraction-patterns.md](references/text-extraction-patterns.md).
- **Perform all edits (values, formatting, sheet deletions) in a single final update before saving.** This keeps the delivered workbook consistent.
- **Target only the specified result range** for formatting and value edits, excluding headers unless explicitly included.
- **Preserve source formatting through value-only edits**: load the existing workbook and assign values directly to target cells; do not rebuild or copy worksheet structures.
- **Encode multi-condition replacements** with direct boolean conditions and exact string matching. Include a fallback branch for rows meeting only some criteria. For categorical replacements, use `dict.get(value, value)` to leave unmapped values unchanged.
- **Threshold/excess logic**: use `if value > threshold: source = threshold; excess = value - threshold`. Leave values at/below threshold unchanged. Apply number formats only after value transformations; formatting must not replace or coerce cell values.
- **When relocating filtered rows**, copy both cell values and source cell styles (number formats, borders, fills, alignment). Clear the destination range before writing new results.
- **For sequential transposition**, flatten source records in original order and pack into the destination using a deterministic row-and-column rule.
- **Ranked allocation formula**: `=IF(cell=MAX(range), total_points/COUNTIF(range, MAX(range)), 0)` handles sole winners, ties, and non-winners.
- **For tied-rank-to-sequential-rank conversion**, combine `COUNTIFS` for strictly greater values with a cumulative `COUNTIFS` for equal values through the current row, constrained to the same grouping field. Add blank checks so incomplete source rows remain empty.
- **Single-criterion aggregation**: use `SUMIF(criteria_range, criterion, sum_range)` matching the target value exactly.
- **Formula handling with openpyxl**: it does not auto-calculate or populate cached values. For graded cells, either recalculate with a spreadsheet engine or write static computed results; do not leave formulas without cached values when values are required.
- **Save to the exact output path** provided; do not alter filename or directory. Preserve the original input workbook unchanged.
- **When copying cells to a new sheet**, preserve formatting: copy font, fill, border, alignment, number_format, and column widths.
- **When the task asks to delete rows**, use worksheet row deletion (bottom-up) rather than compacting non-empty values.
- **When generating formulas across a rectangular block**, iterate rows/columns and map each target cell to the correct source row/column.
- **Frequency-based sorting**: use the precomputed frequency map and first-appearance order, not alphabetical or numeric order.


## New Section

## Row Expansion

When expanding rows based on a count column:
1. Read the count value from the designated column for each source row.
2. Convert the count safely: use `max(1, int(count))` to handle missing or invalid values, defaulting to one copy.
3. Snapshot all source row locations before writing any duplicates to avoid reprocessing newly created rows.
4. Build the output sequentially by source row, emitting each row's copies one after another to preserve original order and keep duplicates adjacent.
## Verification

- After saving, verify the file exists at the specified path and can be opened.
- Reopen the workbook with `data_only=True` and confirm every cell in the exact answer range contains the expected value (not `None`/empty). Also inspect with `data_only=False` when formula strings matter, but do not assume a formula alone satisfies a graded cell-value check.
- After writing or reordering data, compare **every** cell in the requested range against the expected output, including helper/formula columns. Do not assume only visible table columns matter.
- Confirm the destination range contains only the newly written rows (no stale data from prior runs).
- Spot-check that formatting (dates, currencies, alignment) matches the source.
- After transformations, verify that existing data in target ranges was preserved where expected, especially index or header rows.
- Validate each output block: check that headers are correct, data rows are populated, total rows exist and contain correct totals, record counts match expectations, and no block is unexpectedly empty.
- Confirm the output is sorted by the column requested in the task, not by any other column. Verify that all data blocks in the source range were collected.
- Check that output sequence numbers restart from 1 and are sequential in final order.
- After writing formulas: recalculate, spot-check several cells including edge rows and columns, verify absolute references are intact, and confirm cells with missing keys return empty strings (not errors).
- After writing values:
- Read back the populated range and confirm each cell contains the expected value.
- For fills and propagations, spot-check boundary rows to confirm fills stopped where expected and pre-existing values were not overwritten.
- For lookup results, verify that every row matches the intended sequence.
- Ensure the output file exists at the specified path after saving.
- Reload or inspect the output workbook to verify the intended modifications (e.g., rows removed, formatting applied, surrounding data intact).
- When deleting rows based on blank cells, test every cell in the specified target range; delete a row only when all target cells are blank. Treat `None` and whitespace-only strings as blank.
- Spot-check formatted cells to ensure the displayed value matches the requested format string.
- After saving, reopen the workbook with `data_only=True` and read every cell in the graded range.
- Confirm that all cells—both directly edited and dependent formula cells—contain expected numeric results, not `None` or empty cached values.
- If any cached values are missing, recalculate and save again before final verification.
- Confirm that moved headers and data appear in the correct location and that totals remain accurate.
- After programmatic formula generation, confirm every requested cell in the target range is populated before saving.
- After writing replacement values, verify that the target cells are nonempty before applying dependent formatting (e.g., conditional fills).
- Verify that no blank cells appear between entries in a compacted output range, formatting is applied to all populated cells and absent from empty ones, and the destination range contains no leftover data from prior operations.
- Save the workbook only after all value and formatting changes are complete to preserve the final state.
- Confirm the output file was created at the exact requested path (e.g., by listing the directory).
- Reopen the workbook and read back the target range to verify correct values and formatting.
- Print or inspect at least the header row, the first data row, and the last data row of the edited column to confirm transformations applied correctly.
- Confirm output row count matches expectation (e.g., input rows × number of variables; rows remaining after filtering; authoritative ID count plus one header).
- Spot-check a few rows against source data to verify lookup mappings, column order, and formula results.
- For workbooks with formulas, run `recalc.py` to ensure formulas are computed, then spot-check key cells.
- Record computed values (e.g., sum of selected cells) in a designated cell to enable cross-checking.
- Confirm each generated formula uses valid, non-reversed row ranges and that non-qualifying target cells are explicitly cleared.
- After row deletions, confirm the remaining row count matches expectations before saving. After aggregation, verify output row count matches expected unique keys.
- For row-deletion workflows, ensure the first matching row remains intact.
- For lookups, confirm the matching key was found at the expected row before writing.
- Verify formula behavior: check a few cells to confirm that expanding ranges reference the correct rows and that priority logic returns the expected output for edge cases.
- Confirm no excluded rows appear in the destination and that output rows are contiguous (no gaps) and contain only the requested columns.
- After writing sequential labels, verify they follow the original numeric URNs (e.g., `6a`, `6b`, ..., `6z`, `6aa`) and that no generated label such as `6aa` or `9aaa` appears as a base for later labels.
- **Exact requested range** against the specification (values, datatypes, formatting). Ignore unrelated workbook differences.
- **Every requested cell was populated.** Validate at the cell level, including cells that appear blank; visually correct output can still have misplaced headers, missing records, or incorrect trailing rows.
- **Formulas are preserved** (not replaced by values) and placement matches the intended mapping.
- **Verify cached/formula values**: use `data_only=True` or read displayed values, not formula text. Check the first populated row for complete patterns (literals, separators, padding), rows after gaps for resume behaviour, and the final row for padding and prefix integrity.
- **Compare numeric totals** with a business-appropriate tolerance (`abs(total) <= tolerance`) rather than exact equality.
- **Suffix verification**: for "no text after" checks, use `=RIGHT(A2,LEN(B2))=B2` for precise suffix matching.
- Print the saved path, row count, and a sample of remaining rows; spot-check formatting and data integrity.


## New Section

## Formula Patterns

### Separate criteria for non-contiguous data
When related event types are stored in different columns, use separate conditional counts (e.g., COUNTIFS per column) and combine them with an AND condition (e.g., multiply the counts).

### Gate results to the first row of each group
To output a result only once per consecutive group, compare the current group key (e.g., week number, employee ID) with the key of the preceding row. Display the result only when they differ.
## Common Pitfalls

### Row Reordering and Formulas
When reordering rows that contain formulas, do **not** copy the formula text verbatim. Row‑relative references (e.g., `A27`) will not adjust automatically. Instead, either replace the formula with its computed value before moving, use openpyxl's `Translator` to translate the formula to the new row coordinates, or explicitly rewrite the formula with the correct row numbers. After moving, recalculate and verify each formula cell returns the expected value.

### Deletion and Deduplication
- **Partial-key deduplication**: Grouping by a single field when the task specifies a multi-field identity key merges unrelated records. Always use the complete identity key.
- **Unconditional duplicate deletion**: Deleting all records marked as duplicates without checking additional constraints can remove records that must be preserved. Filter the duplicate subset against all task-specified criteria before deleting.
- **Top-down row deletion**: Deleting rows from top to bottom shifts positions of remaining rows, causing wrong rows to be deleted. Always delete in reverse order (bottom to top). See [Row Deletion Patterns](references/row-deletion-patterns.md) for details.
- **Incomplete blank-row detection**: Check every cell in the target range; treat `None` and whitespace-only as blank. Delete only if all cells are blank.

### Formula and Reference Pitfalls
- **Circular references**: A formula referencing its own target cell; use the upstream source cell instead.
- **Unwanted punctuation in blank fields**: Gate optional transformations with a nonblank check to avoid placeholder text (e.g., `IF(F10<>"", LEFT(F10,1)&".", "")`).
- Omitting the last row/column from lookup ranges.
- Using exact match for date lookups that require approximate matching.
- Assuming formulas will be recalculated automatically; openpyxl does not calculate formulas or populate cached results. Cells containing only formulas will read as empty with `data_only=True`. Resolve and materialize values instead.

### Data Handling Pitfalls
- **Assuming fixed ranges**: Data blocks may shift; always detect boundaries from actual sheet content. Do not assume blank rows are at fixed positions.
- **Sorting columns independently**: This breaks row alignment. Always sort rows as tuples.
- **Sort-key substitution**: Replacing an explicit sort column with a grouping column from a helper or lookup column.
- **Partial range scans**: Stopping data collection at the first blank row or header, missing repeated data blocks.
- **Index copying**: Writing source row/item numbers into output position fields instead of generating sequential numbers from 1.
- **Assuming uniform column layouts**: Always map each block individually; do not rely on relative column offsets.
- Overwriting total rows when clearing data; treat total rows as structural.
- Skipping post-write validation; always inspect the saved file.
- Saving to a different path than the required output filename.
- **Skipping inspection**: Editing without first inspecting the workbook layout (sheet names, dimensions, data) leads to wrong ranges, overwritten data, or incorrect assumptions about sheet names/casing.
- **Unbounded fills**: Filling downward without boundary checks can propagate values across blank rows or into unrelated data.
- **Top-down row deletion**: Deleting rows in ascending order shifts remaining rows, causing subsequent targets to be missed or wrong rows deleted. Always delete from bottom to top.
- **Operating outside data bounds**: Inserting or deleting rows without first identifying the actual populated range can corrupt headers, footers, or adjacent data. Always find first/last nonblank cells. Do not delete blank rows outside the populated-cell bounds; preserve leading and trailing blanks that fall outside the intended range.
- **Filtering by substring alone**: Using `in` checks can match unintended substrings (e.g., `'**' in cell.value` matches `'*'`). Use `startswith` for prefix-anchored selection.
- **Copying only the identifying column**: Downstream consumers expect the full table structure; copy all populated columns.
- **Using a single-key lookup when the result depends on two criteria** (e.g., row and column). Always check if both a row label and a column header are needed.
- **Writing formulas without recalculating**: `openpyxl` does not evaluate formulas. Always recalculate with a spreadsheet engine after formula changes.
- **Verifying only edited cells**: Dependent formula cells may lose cached values on save. Check the entire graded range.
- **Truncated source ranges**: Hard-coded ranges like `B3:B40` may miss data. Inspect the actual data extent and match existing aggregation patterns.
- **Label normalization**: Do not alter singular/plural forms of source labels. Use the exact terminology from the task and data.
- **Formula-only cells**: Openpyxl does not auto-calculate; cells with only a formula string may appear blank in readers. Pre-compute results and write static numbers instead.
- **Copying blank cells** that match formatting but contain no data.
- **Leaving gaps in transposed output** or failing to clear/format the destination range before writing.
- **Assuming sheet names, column counts, or header positions** from a truncated preview. Do not assume column positions or row ranges without inspecting the actual worksheet.
- **Overwriting or stripping formatting** during value-only transformations. When moving or rewriting rows, always copy cell formatting (styles, number formats) along with values.
- **Assuming uniform data types**: Do not assume all cells in a column share the same data type; inspect and handle mixed types (e.g., datetime objects and strings).
- **Relying on existing cell formatting** to display values correctly after modifications; always set the number format explicitly on modified cells.
- **When a formula produces `#REF!`**, do not guess a replacement. Use the formula's intended lookup logic and nearby table values to determine a valid value that preserves the original intent.
- **Text matching**: Avoid splitting on delimiters when matching values within free-text comments. Use substring containment (`in`) against the full text instead. Normalize case before comparing strings—apply `.casefold()` or `.lower()` to both the search value and the source text.
- **Assuming exact matching** between compound identifiers and component headers; use containment instead. Do not overwrite output ranges outside the requested bounds.
- **Returning only the first match** for repeated lookup keys. Preserve all matching records and source column order to keep duplicate associations consistent.
- **Applying filters incrementally** instead of together, which can let unwanted rows through.
- **Writing non-contiguous output**, leaving gaps for filtered-out rows.
- **Saving to a default or incorrect path** instead of the specified output filename.
- **Deleting rows top-down**: Causes index shifts that skip rows or delete the wrong ones. Always delete bottom-up.
- **Assuming fixed ranges**: Hard-coded ranges break when data grows. Scan for blank rows, headers, and data boundaries dynamically.
- **Treating all values as one type**: Numeric filters fail when numbers are stored as strings. Always attempt `float()` conversion.
- **Transforming header rows as data**: Identify the first data row (usually row 2) and start iteration there unless the task explicitly includes headers.
- **Off-by-one boundary errors**: Verify the first and last rows of the requested range before saving.
- **Using regex for simple character removal**: Literal string replacement (`str.replace()`) is safer and avoids unintended side effects.
- **Processing the entire sheet instead of the specified range**: Target the exact worksheet and data-row range to avoid modifying unrelated cells.
- **Copy-reference errors when filling blocks**: Map target rows/columns to source rows/columns explicitly rather than dragging formulas blindly.
- **Using `COUNTIFS` for sum tasks**: It counts rows rather than totals. Use `SUMIF` for totals based on matching labels.
- **Exact-match vs substring search**: Use substring containment (`in`) unless the task explicitly requires full-cell equality.
- **Relying on visual inspection or fixed-size subsets** for combination sum tasks; always perform exhaustive enumeration.
- **Trusting write operations without reload**: Always reopen and read back to confirm the file was saved correctly.
- **Synchronizing sheets out of order**: Do not append unmatched records to the end; always rebuild in the authoritative ID order.
- **Skipping formatting copy** from a reference layout sheet; blank placeholder rows will look inconsistent without it.
- Merged cells can silently prevent cell‑level writes. Always check for and unmerge overlapping ranges before editing.
- DO NOT edit entire columns without row bounds — this overwrites headers.
- DO NOT confuse cell references with cell values when applying transformations.
- For suffix/prefix removal, prefer direct string slicing (e.g., `s[:-3]`) over formula-based approaches that may misinterpret references.
- Applying correct logic to incorrect ranges or sheets (fix: inspect first).
- Using a later match when the task requires the first match (fix: scan in specified order, stop at first qualifying result).
- Assuming a fixed row without verifying the matching key (fix: match keys before writing).
- Using `SUMIFS` with a range as a criteria argument does not evaluate as an OR condition; it may not work as expected. For matching any value from a list, use `SUMPRODUCT` with `ISNUMBER(MATCH(...))` instead.
- Avoid nested cell‑by‑cell searches for duplicates; always use an in‑memory dictionary for efficiency.
- Do not write partial results or save the workbook repeatedly during aggregation—collect and write everything at once.
- Using fixed ranges instead of mixed references for cumulative calculations, causing incorrect aggregation.
- Misordering nested conditions so that a lower-priority match overrides a higher-priority one.
- Populating only a subset of the target range when applying formulas manually.
- When deleting rows preceding a matched row, preserve the matched row. Scan top-to-bottom for the first qualifying row; if its index is `r > 1`, delete exactly rows `1` to `r-1`. Do not delete the matched row itself.
- Inserting rows in ascending (top-to-bottom) order causes subsequent target row numbers to become incorrect, leading to misplaced insertions. Always process insertions from the highest row number down.
- **Exact matching when data uses compound identifiers**: If one sheet has longer compound labels and another has component names, use containment matching (check if the shorter string is contained in the longer one) rather than requiring exact equality.
- **Skipping empty or unmatched entries**: Always skip blank source cells and unmatched lookup values so only valid associations are emitted.
- **Writing partial results before filtering is complete**: Apply all criteria first, then write.
- **Saving to a default or temp path**: Always save to the explicitly required output path.
- **Leaving gaps in destination rows**: Write qualifying rows consecutively without skipping rows.
- Relying on uncalculated formulas when cell values are graded.
- Assuming cumulative behavior without checking per-row data patterns.
- **In-place row reordering corrupts data**: When sorting or rearranging rows, `iter_rows()` returns live `Cell` objects that remain tied to their worksheet positions. Sorting these references and writing them back in-place causes data duplication and loss.
  - **DO**: Snapshot row values and styles into independent lists or tuples first. Sort the snapshots, then write the sorted data back to the worksheet in a separate pass.
  - **DO NOT**: Sort a list of row tuples obtained directly from `iter_rows()` and write them back to the same cells.
- **Verify row preservation after reorder**: After any sort or reorder, confirm that the multiset of row contents (e.g., a sorted tuple of row identifiers) matches between the source and result to detect accidental duplication or omission before saving.
- **Sequential label generation:** Do not read previously generated output cells as the base for later labels. Keep `last_numeric_base` from the original source values and a separate `blank_count` reset after each numeric URN. Generate suffixes with a dedicated 1-based base-26 encoder using `divmod(n-1, 26)`, not by concatenating letters onto prior output.
- **Do not apply dependent formatting before the corresponding value is written and validated as nonempty.**
- **Top-down deletion** shifts indices of rows below, causing wrong rows to be removed. Always delete rows from bottom to top.
- **Using later matches when the first is required**: always use the first occurrence from the top; verify the row number before acting.
- **Case-sensitive searches when case-insensitive is needed**: use casefolded comparisons unless exact case is specified.
- **Comparing a cell to `"error"`** instead of using `ISERROR` for actual Excel error values.
- **Writing formulas with openpyxl without calculating them**, leaving graded cells empty to the evaluator.
- **Assuming column positions or sheet names without inspection.**
- **Omitting fixed literal segments in concatenated strings** (e.g., include `"-02-"` as a literal in formulas).
- **Verifying only formula text** instead of reading back computed values from key cells.
- **Compacting non-empty values instead of deleting rows**, which removes intentional blank separators and shifts row positions.
- **Treating all non-empty rows uniformly** and ignoring repeated headers that define separate data blocks.
- **Validating only visually**; blank cells and header placement must be checked explicitly.
- **Hardcoding row counts**; always adapt to the discovered worksheet size.
- **Do not confuse frequency order** with ordinary alphabetical, numeric, or formatting-based sorting.
- **Copying values without transferring cell styles**, causing inconsistent output.
- **Replacing values with a dictionary without preserving unmapped values**, leading to data loss.


## New Section

## Synchronizing Sheets

When synchronizing two sheets based on a key ID, follow these patterns:

- **Use the authoritative ID list to define row order:** Treat the manual or source ID sheet as the authoritative ordering and membership list. Build output rows by iterating through the source IDs, rather than by appending only unmatched records. This ensures existing records remain aligned and missing IDs are inserted in the correct positions.
- **Preserve existing rows while creating blank placeholders:** Map existing target rows by their key ID so data can be retained while missing keys receive empty records. Store each existing row as a complete list keyed by its unique identifier, then use a default row such as `[ID] + [None] * remaining_columns` for IDs absent from the target. This cleanly separates preservation from insertion logic.
- **Use a reference sheet for formatting consistency:** When the workbook includes an illustrated expected-layout sheet, reuse its formatting to make the modified sheet visually consistent. Copy styles, row heights, number formats, alignments, protections, and column widths from the reference layout after writing values. This preserves the intended appearance of both populated and newly blank rows.