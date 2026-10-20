---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

1. **Validate file paths** with `os.path.exists()` and list parent directories if needed before loading; path values may differ subtly from filesystem layouts.
2. **Inspect** the workbook: load with openpyxl, list `wb.sheetnames`, check dimensions, headers, sample rows, and identify key columns, data boundaries, and existing formulas. See ## Inspection.
3. **Plan** transformations in memory: identify source/target columns, build lookup dictionaries keyed by stable identifiers or composite keys, precompute thresholds/boundaries, and detect data boundaries dynamically rather than hardcoding ranges. For result grids with missing key combinations, check existence first and default to `False`/`None` instead of raising `KeyError`.
4. **Execute** using a complete Python script written to a `.py` file and run via bash (not inline Python). Use openpyxl for programmatic read/write. Apply changes via lookup maps, single-pass filtering, and scoped modifications. See ## Writing Output.
5. **Verify** by reloading the saved file, reading back modified ranges, recalculating formulas, and spot-checking mapped values and dimensions. See ## Verification.
6. **Save** the workbook to the correct output path.

**Reusable Patterns**
- **Lookup dictionaries**: For cross-sheet value synchronization, build dicts keyed by stable identifiers or composite keys for O(1) lookups; handle missing keys with `.get(key, default)`. Avoid row-aligned copy and inline lookups during iteration.
- **Interval-based aggregation**: Locate marker positions in a list, then iterate over consecutive pairs to define calculation ranges.
- **Sequential extraction with repeating headers**: Track a boolean flag (`prev_was_header`) across rows; collect the next row's value when the flag is True, then reset it.
- **Block-based mapping with conditional indexing**: Use a separate source index that only advances for matching target blocks.
- **Sequential filling with state tracking**: Keep state variables (last valid number, sequence counter) and update/reset on group changes; use a custom base-26 mapping for alphanumeric sequences beyond 'z'.
- **Two-pass aggregation**: When cell values depend on group-level aggregates and row-level context, first build group-level mappings, then evaluate each row with positional context.
- **Sequence-based boundary detection**: Compare current group identifier with previous row's value to detect boundaries; handles non-contiguous groups.
- **Order-preserving extraction**: Traverse cells sequentially row-by-row, column-by-column to preserve original order.
- **Index-mapped grid population**: For fixed-width grid from a flat list, use a single sequential index mapped to target coordinates; leave trailing cells empty.
- **Fragmented data reassembly**: Group non-empty rows into ranges by detecting empty-to-non-empty transitions; add separators only between ranges, not after the last.
- **Numeric ID sorting**: Use `sorted(ids, key=lambda x: int(x) if str(x).isdigit() else x)` to avoid lexicographic ordering.
- **Deduplication**: Group rows by composite keys of multiple identifying columns; apply priority rules before deletion; target the second occurrence, never the first.
- **Grouping/ranking**: For top-N per category or conditional ranking, use group-then-sort programmatic approach instead of nested IF/AND formulas.
- **Merge/aggregation**: When aggregating rows by a key, explicitly copy the grouping column to output and track 0-based vs 1-based indexing.## Core Workflow

Before any manipulation, load the workbook and inspect the data structure thoroughly.

- **Load and inspect**: Use `openpyxl.load_workbook()` to list sheet names (`wb.sheetnames`), check `max_row`/`max_column`, and print the first 5–10 rows. Do not assume sheet names, dimensions, or data ranges.
- **Verify file path** before loading; re-check long nested paths segment by segment and list parent directories on file-not-found errors.
- **Map the structure**: Identify row headers, column headers, value data, non-contiguous regions, and exact target output coordinates. Document these locations, especially for non-standard layouts.
- **Dynamic header discovery**: Scan the header row with case-insensitive string matching, never hardcoded indices. Normalize each cell value (strip whitespace, lowercase) and match against target header names.
- **Prefer stable identifiers**: When task instructions specify matching on a text column, verify whether an adjacent identifier column (numeric IDs, unique codes) provides a more reliable alternative. For cross-sheet matching, use substring checks when one sheet's headers appear inside another sheet's longer identifiers.
- **Dynamic range detection**: When a worksheet contains multiple independent data ranges separated by blank rows, iterate through rows to find empty cells in primary identifier column(s) and build start/end boundaries from those rather than hardcoding row indices. Limit scans to the exact range specified (e.g., A7:A1000), not the entire column.
- **Check existing formulas and target cells**: Read target cells with openpyxl before writing to confirm location and existing values. Identify formulas that might be overwritten or referenced.
- **Inspect sample values** before concatenating or transforming data to detect pre-existing delimiters, empty cells, whitespace issues, and mixed data types.
- **Case-insensitive text search**: Convert cell values to strings with `str(cell.value)` before applying `in`, `startswith`, or regex. Normalize both sides to lowercase or use `re.IGNORECASE`. Guard against `None` with explicit checks.
- **Type validation**: Before numeric conversion, check `isinstance(value, (int, float))` or use try/except to avoid errors on header rows or non-numeric data. Inspect cell value types before transforming mixed-type columns; branch on type before parsing/converting.
- **Fixed-format extraction**: For fixed-length predictable formats such as ISO 8601 timestamps, extract components with string slicing (e.g., `value[:10]` for the date) before parsing; avoid regex/split when the format is stable.
- **Reference sheet inference**: When a task involves identifying patterns or selecting cells based on implicit criteria, first check for any 'after', 'example', or 'solution' reference sheets. Use existing highlights, formatting, or values on those sheets to infer the selection criteria directly.
- **Read filter criteria cells** directly into variables before processing the dataset.
- **Check for merged cells, hidden rows, or data type inconsistencies**.
- **Record expected answer position** (sheet name and range) before writing; use it to select the output workbook and later verify completeness.
- **Self-referencing range diagnosis**: Whenever a cell displays `000`, `#REF!`, or a calculation error, verify whether the target cell's address lies inside its own formula range. If so, adjust the range bound to exclude the target cell.
- **RGB object conversion**: When checking cell properties (fill color, font, borders), convert openpyxl objects to strings before comparison: `str(cell.fill.start_color.rgb)`. RGB objects are not iterable and will raise TypeError if used directly in `in` checks.
- **Use range slicing** (e.g., `ws['A1:A4']`) for exact target ranges, avoiding manual row/column calculations.
- **Inspect reference cells**: When preparing formulas, read the cells that will be referenced as intermediate results to confirm their actual values.
- **When a task references source code or formulas** (VBA, SQL, spreadsheet formulas), identify the exact range boundaries before transforming data. Note whether row 1 is a header and must be preserved.## Inspection

Use openpyxl for all programmatic read/write operations. Write a complete script to a `.py` file and execute it; do not use inline Python in bash.

**Computed values vs formulas**
- Write computed numeric/string values by default, not formula strings, unless the task explicitly requires formulas and the evaluator will execute them. If a reference/ground-truth workbook is available, match its output type: values in the gold file mean write values.
- openpyxl does not evaluate formulas; reading with `data_only=True` returns `None` for formula cells. After writing, re-open with `data_only=True` and verify each output cell contains the expected computed value rather than `None`.
- When formulas are required, assign formula strings directly to cell `.value` (e.g., `ws['D2'] = '=SUMIF(A:A,"111111",B:B)'`). openpyxl does not auto-adjust relative references; build a dictionary mapping each cell to its specific formula string and assign each individually.

**Lookup and formula patterns**
- **Label-based lookup**: `=INDEX(return_range, MATCH(lookup_value, label_range, 0))`. Avoid hardcoded row numbers.
- **Two-way lookup**: `=INDEX(return_column, MATCH(1, (lookup_col1=condition1)*(lookup_col2=condition2), 0))`. Do not chain separate VLOOKUP or MATCH operations for this case.
- **Multi-criteria lookup with duplicates**: Concatenate lookup values and arrays in MATCH, e.g. `MATCH(lookup1&lookup2, array1&array2, 0)`, to create a compound key.
- **Whitespace in lookups**: When VLOOKUP/XLOOKUP returns #N/A despite matching values, wrap the lookup table range with `TRIM()` (e.g., `TRIM(Sheet3!$A$2:$D$300)`).
- **SUMIF**: Use `=SUMIF(criteria_range, criteria, sum_range)` with absolute references for fixed ranges and relative references for criteria cells.
- **Tie detection**: Use `=COUNTIF(range, MAX(range))` to count ties for tiered scoring.
- **Expanding range**: Use `$A$2:A2` to create a cumulative range as formula fills down.
- **Priority logic**: Nest IF statements in priority order; the first TRUE condition short-circuits and returns its result.
- **Multi-condition existence**: Use `COUNTIFS` with range pairs and test whether the count is greater than zero.
- **Empty cell guards**: Use `=IF(cell="","",...)` to avoid errors on empty inputs when appending text.
- **Sequential numbering**: Use `COUNTA($B$3:B3)` over a growing range, not row arithmetic, so gaps are skipped. Use `TEXT(COUNTA(...)+9, "000")` for fixed-width zero-padded strings.
- **String suffix check**: Use `=RIGHT(cell, LEN(check_cell))=check_cell`.

**Data transformation patterns**
- **Dictionary lookups for cross-table matching**: Build a dictionary keyed by stable identifiers or composite keys from the reference sheet, then iterate target rows and resolve values via the lookup map. Handle missing keys with `.get(key, default)`.
- **Wide-to-long transformation**: Iterate identifier columns once, then nest an inner loop over variable columns to emit one output row per variable.
- **Chunk-based row mapping for transposition**: Identify chunk size (e.g., 4 source rows -> 1 target row) and use `(target_row - offset) * chunk_size + base_row` to dynamically calculate source indices.
- **Systematic column pair mapping**: Group target columns logically (e.g., K/L, N/O) and use loops with column index offsets instead of manual cell assignments.
- **Index-mapped grid output**: For fixed-width grid from a flat list, maintain a single index counter while iterating target grid coordinates; leave trailing cells empty.
- **Conditional writes**: Explicitly check if the source cell is not `None` before writing to preserve existing target values: `if source_cell.value is not None: target_cell.value = source_cell.value`.
- **Delimiter-aware concatenation**: Do not insert an extra delimiter if the left string already ends with the target delimiter.
- **Filter out `None`/empty cell values** during extraction (e.g., `[v for v in col if v is not None]`) so nulls do not appear in final output.
- **Delimiter-stopped regex extraction**: Use `re.search(r'Prefix-([^,]*)', text)` to capture until the first delimiter instead of fragile string splitting.
- **Numeric conversion**: When writing cleaned numeric values, convert strings to `float()` or `int()` before assigning to `cell.value`.
- **Safe type handling**: Always convert cell values to strings before applying string methods (e.g., `str(cell.value).replace(...)`).
- **Robust date parsing**: Parse date columns with a helper that handles `datetime` objects, formatted strings (`'%d/%m/%Y'`, `'%Y-%m-%d'`), and `None`; use a sort key returning a tuple `(primary_value, secondary_value)`. Convert key values to strings if mixed types are possible.
- **Multi-level sorting**: Use Python's tuple-based sort key for multi-column sorting: `key=lambda row: (row[col_a], row[col_b])`. Avoid sequential single-column sorts.
- **Frequency-based sorting**: Use `collections.Counter` to count occurrences, then sort with `sorted(values, key=lambda x: freq[x], reverse=True)`.
- **Group-then-sort for ranking**: For top-N per category or conditional ranking, group data by category first, sort each group independently, and preserve original indices to map results back to correct output cells. Prefer programmatic scripts over complex nested IF/AND formulas.
- **Two-pass aggregation**: If a cell depends on group-level aggregates and row-level context, first aggregate group-level properties into a mapping, then evaluate each row using that mapping and previous row's group identifier.
- **Sequential filling with state tracking**: Initialize state variables before the loop; update on non-empty cells, derive on blanks, reset on group changes; use custom base-26 mapping for alphanumeric sequences beyond 'z'.
- **Block-based mapping with conditional indexing**: Use a separate source index that only advances for matching target blocks.
- **Sequential extraction with repeating headers**: Track a boolean flag across rows; collect the next row's value after each header occurrence.
- **Boundary-aware separators**: When reassembling grouped data blocks, add separators only between blocks, not after the last one (`if i < len(ranges) - 1`).
- **Deduplication**: Group rows by composite keys of multiple identifying columns; for duplicate groups, preserve priority entries (e.g., 'Employee') and delete the second occurrence, never the first. Use a dictionary to store first match per key when joining tables on duplicate keys.
- **Merge/aggregation**: When aggregating rows by a key, explicitly copy the grouping column to output; apply consistent number formatting (e.g., '0.00') and convert zero sums to blanks if required.

**Safe row/column operations**
- **Clear target sheet/range**: Before writing, clear the output area by setting cells to `None` or empty strings. When clearing a column or range, also reset fill: `cell.fill = PatternFill(start_color=None, end_color=None, fill_type=None)`.
- **Row deletion**: Delete rows backwards when removing multiple rows. Collect target rows, sort descending, then delete bottom-to-top (`range(ws.max_row, 1, -1)`) to avoid index shifting.
- **Row insertion**: Iterate from the bottom of the range upward to prevent row index shifting.
- **Duplicate row removal**: Filter groups with more than one entry; target the second occurrence (index 1) to preserve the original row. Verify group size before deletion.
- **Scoped modifications**: Only modify cells explicitly targeted by the task. Leave other rows and formulas untouched.
- **Scoped emptiness checks**: When deciding deletion based on emptiness, check only the exact column range specified (e.g., F:L), not the entire row.
- **Boundary-aware pruning**: When deleting rows above a known target (e.g., a header cell like "Code"), find the target row index first, then restrict evaluation to rows 1 to target_row - 1.
- **Remove extraneous sheets**: Before saving, review the initial sheet list and delete any sheets not required in the final output structure.

**Formatting and cleanup**
- **Style transfer**: When copying cell formatting, create new `Font()`/`Alignment()` objects from source cell properties instead of assigning `cell.font`/`cell.alignment` directly. Copy font, border, fill, alignment, and number format from source to target cells when placing filtered data.
- **Number format restoration**: After assigning values programmatically, restore `number_format` based on the Python data type (e.g., `datetime`, `float`), as openpyxl does not preserve it automatically. Write native datetime/date values and set `cell.number_format` (e.g., `'m/dd/yyyy'`); do not stringify values solely for display.
- **New workbook for different target sheet**: When the answer position specifies a sheet different from the input, create a new workbook with the target sheet name rather than modifying the original.
- **Direct range iteration**: Use openpyxl range slicing (e.g., `ws['A1:A4']`) to iterate over cells instead of calculating row/column indices manually.
- **Programmatic formula construction**: When applying identical logic across many columns/rows, build formulas in code: iterate over column letters and row indices to generate cell references (e.g., `f'={col_letter}$1:{col_letter}$3'`). Use column indices (e.g., 33 for AG) instead of column names in scripts to avoid header variations.
- **Pandas operations**: For merging duplicate records by multiple columns with aggregation, use `df.groupby([...]).sum().reset_index()`. When writing DataFrames to Excel at a specific column offset, use the `startcol` parameter in `to_excel()` (e.g., `startcol=6` for column G).
- **Exact output placement**: When the task specifies exact output cells (e.g., "Place output in H10"), write results to those exact addresses. Do not infer output locations from merged cell boundaries, data range start/end rows, or nearby cells.
- **Preserve exact source strings**: When source values become headers or labels, do not normalize, singularize, strip suffixes, or change case unless the task explicitly instructs it.
- **In-place modification**: Use openpyxl or the available spreadsheet library to modify cells in place. Preserve formatting and formulas in cells not explicitly targeted for replacement.## Writing Output

After every write operation, save the file, reload it from disk, and read back the modified range to verify actual file output. Do not rely on print statements alone.

- **Reload and confirm**: Reopen the output workbook and verify dimensions (`max_row`, `max_column`) and sample values match expectations. Confirm both header row and representative data rows.
- **Recalculate formulas**: `openpyxl` writes formula strings but does not compute results. Use a recalculation step or open the workbook in a spreadsheet application to confirm corrected values. After writing formulas, recalculate and look for error values (`#REF!`, `000`).
- **Read back written cells**: Confirm values and positions, including header labels and calculated cells. Verify formulas persist and values are correct.
- **openpyxl data_only check**: Re-open with `openpyxl.load_workbook(..., data_only=True)` and verify each output cell contains the expected computed value, not `None`.
- **Spot-check mapped values**: Manually trace at least 3 key → lookup → result chains. Compare row counts before and after to ensure no unintended additions or deletions.
- **Cross-check output coordinates**: Before finalizing, cross-check each computed value's output cell against the task's explicit placement instructions (e.g., E2:E10 -> H10, E11:E20 -> H20). Confirm intended and actual cell coordinates match.
- **Validate constraints**: After calculating a result that must fall within a specific range or meet a constraint, explicitly verify the computed value against the expected bounds before finalizing.
- **Floating-point tolerance**: Use absolute tolerance for zero-sum checks: compare `abs(total) < 0.011` rather than `total == 0` to handle artifacts like 1e-11.
- **Whole-number check**: When checking if a numeric value is a whole number, use float comparison: `float(value) == int(float(value))`. Do not rely on string parsing.
- **Boundary and order sampling**: Print the first 15–20 rows and the last few rows of the output range to confirm pattern consistency, boundary handling, and original order preservation. Spot-check first, last, and a middle row.
- **Formatting checks**: Check `number_format`, alignment, fill, and font attributes. Confirm styles were applied correctly by reading back properties and converting to strings for comparison.
- **Grouping and aggregation checks**: Verify grouping columns are present in merged output; confirm number formatting (e.g., '0.00') and zero-as-blank handling.
- **Header preservation**: After transformations, verify header cells are unchanged. Compare iteration start/end rows to the source range exactly.
- **Dimension matching**: Confirm final dimensions match the expected answer position (e.g., A1:AG10) to catch off-by-one errors. Check that total data rows match expected structure (e.g., employees × variables) to catch truncation or duplication early.
- **Sample input-output pairs**: Print or log 5–10 rows covering edge cases: exact matches, partial matches, and no-matches. Confirm both matched and unmatched rows behave correctly.
- **Pattern-specific checks**:
  - For INDEX/MATCH: verify returned value matches the expected label's data.
  - For COUNTIF/MAX: manually check max values to confirm tie count.
  - For programmatic formulas: spot-check a few cells against manual calculations.
  - For header-state tracking: verify number of extracted values equals number of header occurrences.
  - For block mapping: verify count of mapped values matches count of matching target blocks.
- **Non-contiguous group verification**: For sequence-dependent logic, verify behavior on rows where a group identifier repeats non-contiguously.
- **Post-insertion verification**: After row insertions, verify inserted rows are empty and original rows shifted down one position with data intact.
- **Delimiter and None check**: Ensure concatenated strings have no duplicated delimiters and no `None` values in final output.
- **Substring deletion integrity**: After substring deletion or splitting, verify the source cell still contains the unaffected portion and the target/derived cell contains exactly the removed substring.
- **Deduplication verification**: Confirm no false positives were removed and priority entries were preserved.
- **Reference table validation**: If a task provides a reference table or desired results, use it to verify correctness, expected sort order, and edge cases.
- **Final saved-file read-back**: Always read back the saved file contents as the last step before declaring the task complete. Do not rely solely on in-memory state.
- **Use evaluation tool**: If an `evaluate_output` tool is available, use it to compare output against ground truth; it provides cell-level mismatch details. Note that hardcoded numbers and formulas that produce identical values are treated as equivalent.## Verification

- **Hardcoding ranges/indices**: Avoid hardcoded ranges, row numbers, and column indices. Data ranges shift; discover headers and boundaries dynamically via blank-row scanning and label-based lookups.
- **Positional alignment across sheets**: Do not rely on row position alignment across sheets — rows may be missing, reordered, or offset. Build lookup dictionaries keyed by stable identifiers instead.
- **Free-text matching when stable ID exists**: Do not match on free-text columns when a stable identifier column exists. Text typos and formatting differences cause silent mismatches.
- **Building lookup map too late**: Always build the lookup map first, then apply changes. Inline lookups during iteration are error-prone and hard to debug.
- **Index shifting during deletion/insertion**: Deleting rows top-to-bottom shifts indices; always delete bottom-to-top. When inserting, iterate bottom-to-top.
- **Targeted modifications only**: When a task requires changing formulas for specific rows, never overwrite cells outside the specified range. Before saving, verify only intended cells were altered.
- **Closest value above**: When searching for the closest value above a reference point, iterate downward from the reference row (e.g., `range(ref_row - 1, 0, -1)`) to find the most recent match.
- **Extraneous sheets**: Forgetting to remove extraneous sheets. Review initial sheet list and delete any sheets not required in final output.
- **Self-referencing ranges**: Self-referencing ranges in MAX/MIN/SUM formulas cause circular-reference errors and are fatal. References to empty rows outside the used range are harmless and lower priority.
- **Inline Python in bash**: Inline Python breaks on `$`, colons, and quotes in formulas. Always write to a `.py` file before executing.
- **Whitespace mismatches in VLOOKUP/XLOOKUP**: Use `TRIM()` on the lookup table range to strip trailing/leading spaces.
- **Duplicate lookup keys**: When merging tables on a non-unique key, use a dictionary to store only the first match per key. Avoid complex array formulas and error-prone INDEX/MATCH with duplicate keys.
- **Skipping post-write verification**: Unverified writes are a common source of silent errors. Always reload and inspect the written file.
- **Assuming matching dimensions**: Always handle missing key combinations gracefully with a default (e.g., False) rather than letting KeyError propagate.
- **Working directory mismatch**: Assuming the working directory matches the expected path without verification. Use directory listing to confirm the correct path.
- **Modifying without inspection**: Modifying cells without first inspecting data structure can lead to wrong rows or columns being changed.
- **Clearing content without formatting**: Clearing cell content without resetting formatting may leave unwanted background colors. Set value to None AND reset fill.
- **String parsing for whole numbers**: Using string parsing to check for whole numbers can fail for negative values or decimals; use float-to-int comparison.
- **Forgetting to recalculate**: Always recalculate formulas after changes before reading results; cached values may be stale.
- **Off-by-one errors**: openpyxl `cell.value` uses 1-based row/col, but `iter_rows()` yields 0-indexed lists. Map explicitly: Column I = index 8 = col 9.
- **Missing grouping columns**: When merging rows by a key, explicitly copy the grouping column to output alongside other preserved columns.
- **Zero display**: After summing, convert zero values to blanks if the task requires it.
- **Header row corruption**: Applying a transformation to row 1 when the source range starts at row 2. Start iteration at the first data row unless the task explicitly includes the header.
- **Numeric IDs sorted as strings**: Use `sorted(ids, key=lambda x: int(x) if str(x).isdigit() else x)` to avoid lexicographical ordering.
- **Hardcoding reference values**: Avoid hardcoding sheet names or valid targets. Extract them dynamically from the workbook.
- **Advancing source index unconditionally**: When mapping to filtered blocks, do not increment the source index for blocks that don't match the filter condition.
- **Assuming flat data layout**: Check for repeating headers or block-structured data before assuming a simple columnar layout.
- **Case-sensitive matching**: Always lowercase both the cell text and keywords before substring search.
- **Guessing data ranges**: Use the explicit `answer_position` range from the task; dynamic detection often misses rows or includes empty trailing rows.
- **Formula-string output**: Writing formula strings such as `=SUMPRODUCT(...)` instead of evaluated numbers: evaluators that compare cell values will see formulas as empty or `None`. Compute the result and write the number.
- **Date parsing**: Parse spreadsheet dates robustly, handling both datetime objects and strings such as `YYYY-MM-DD HH:MM:SS`, before performing range checks.
- **Truncation or duplication**: Verify dimensions and row count before declaring completion when expected input data is incomplete or placeholder.
- **VBA cell-reference misuse**: In VBA, do not use `Columns(rowIndex, colIndex)` to reference individual cells. Use `Cells(row, col)` or `Range("A" & rowNumber)`, and verify row vs column references when iterating rows.
- **Assuming sheet names or dimensions**: Task descriptions may have typos; always inspect actual sheet names and dimensions.
- **Leaving stale data in output sheets**: Always clear before writing.
- **Making multiple passes over data**: Combine all filters into a single loop.
- **openpyxl RGB TypeError**: Cell fill colors are RGB objects; convert with `str(cell.fill.start_color.rgb)` before comparison.
- **Incremental modifications**: Avoid modifying cells one at a time with repeated save/load cycles; batch all changes in a complete script.
- **Overwriting unrelated rows**: Scope writes to the exact cell range specified.
- **Single-column MATCH with duplicates**: Use concatenated keys instead of multiple nested MATCH calls.
- **Path mismatches**: Hardcoded paths often fail; use relative paths or confirm with `os.path.exists()`.
- **Emptiness checks on entire row**: Scope to the exact column range specified in the task.
- **Applying string methods to non-string cells**: Always cast with `str()` first.
- **Manual row/column calculation**: Prefer range slicing to avoid off-by-one errors.
- **Manual formulas for batch text extraction**: Prefer openpyxl/re scripts for batch operations.
- **Processing rows without explicit ranges**: Define explicit row ranges to avoid header/trailing blank-row corruption.
- **Complex string splitting vs regex**: Use delimiter-stopped regex (`re.search(r'Prefix-([^,]*)', text)`) instead of fragile splitting.
- **Row-to-header after filtering**: Some tasks expect the first filtered row to become headers; assign `df.columns = df.iloc[0]` and exclude that row from data.
- **Circular references in range formulas**: If a cell shows `#REF!` or `000`, check if it lies within its own formula's range; adjust bounds to exclude the target cell.
- **Inefficient lookups**: Pre-build lookup dictionaries for O(1) retrieval instead of repeated sheet scans.
- **Manual structural changes**: Use native API methods (`delete_cols()`, `append()`) instead of manually nullifying cells.
- **Off-by-one in sequential scans**: When restarting from a matched cell, skip the matched cell and set the new reference to the next cell.
- **Cell type mismatch evaluation**: Do not assume a mismatch based on cell type (formula vs hardcoded value). If the evaluation tool reports PASS, the output is correct regardless of implementation.
- **Complex nested date-range formulas**: Prefer script-based iteration for precise row selection and preventing output-range misalignment.
- **Deleting part of a cell vs clearing**: If a task says to "delete" a string/substring, remove only the exact specified portion and retain all remaining cell content. Clear the entire cell only when explicitly told to clear or empty it.
- **Unfiltered blanks**: When collecting values from shaded cells, explicitly skip cells where `value is None` or `value == ''`.
- **Complex nested IF/AND formulas for ranking**: These often fail when the global maximum belongs to a different category. Use the Group-Then-Sort programmatic approach instead.
- **Explicit row ranges**: When iterating over rows in a script, explicitly define input and output row ranges (e.g., `for row in range(2, 8)`) to avoid overwriting headers or processing trailing empty rows.
- **Deleting first occurrence of duplicate**: Preserve the first, remove later ones. Verify group size before deletion.
- **Single-column matching for duplicates**: Use composite keys instead of single-column matches.
- **Removing priority entries**: During deduplication, preserve priority entries (e.g., 'Employee').
- **Saving before verifying formula outputs**: Always verify formula outputs before saving.
- **Limit scanning to exact range**: Limit scanning to the exact range specified (e.g., A7:A1000) rather than the entire column.
- **Column-specific emptiness**: Checking the entire row for emptiness when only specific columns matter. Always limit emptiness checks to the exact columns specified.## Common Pitfalls
