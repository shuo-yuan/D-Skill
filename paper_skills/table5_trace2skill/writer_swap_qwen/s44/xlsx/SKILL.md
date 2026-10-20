---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow

1. **Resolve file paths**: Confirm or dynamically resolve input and output paths (e.g., using `os.listdir()`) before opening files. Do not assume the working directory matches the filesystem layout.
2. **Load the workbook**: Use `openpyxl.load_workbook()` to preserve formatting.
3. **Inspect the workbook**: Examine sheet names, dimensions, column headers, data types, dependencies, and boundaries. Map exact cell locations. See [Inspection](#inspection) for a detailed checklist.
4. **Plan the transformation**: Choose appropriate patterns. Pre-build lookup dictionaries for cross-sheet operations using stable identifiers (composite keys if needed). For formula-heavy tasks, use programmatic formula generation with absolute/relative references. For category-based ranking, use group-then-sort strategy. For complex multi-step transformations, write a standalone Python script (`.py` file) instead of inline `python -c` to avoid shell escaping issues.
5. **Execute changes programmatically**:
   - Iterate over defined ranges or use explicit row/column loops; prefer sequential traversal to preserve order.
   - Apply all filtering conditions in a single pass.
   - Clear target cells before writing new values.
   - Write values first, then copy formatting (font, border, fill, alignment, number_format) from source cells using new style objects.
   - For batch row deletions, use `delete_rows(start, count)` in a single call; for non-consecutive rows, process bottom-to-top.
   - Use `collections.Counter` for frequency tasks.
6. **Verify immediately**: After every write, recalculate if needed, save, reload, and read back the modified range. Use the `evaluate_output` tool when available. See [Verification](#verification) for a full checklist.

## Inspection

- **Always inspect first**: Load the workbook, print sheet names, dimensions, and sample the first few rows to confirm layout, data types, and boundaries.
- **Validate file paths**: Confirm or dynamically resolve input and output paths against the working directory before opening files.
- **Map structure**: Document exact cell locations of headers, data ranges, and output areas. Cross-check actual structure against the task description; trust the file, not the prompt. Identify source and target ranges before writing transformation code.
- **Programmatic boundary detection**: Always read cell values to detect table boundaries and column indices. Scan columns for first and last non-blank cells; handle multiple data blocks separated by blank rows. Use `answer_position` if provided to set exact bounds.
- **Dynamic column discovery**: Scan the header row with case-insensitive string matching to find column indices by name, normalizing for case and whitespace.
- **Check for mixed data types**: Before transforming a column, inspect for mixed types (e.g., datetime objects and strings) and branch by type.
- **Pre-build lookup dictionaries**: For cross-sheet joins, parse tables into dictionaries keyed by stable identifiers (strip whitespace, use composite keys if needed) for O(1) lookups.
- **Use case-insensitive matching**: Normalize spreadsheet text and search terms to lowercase (or use case-insensitive regex) before comparing; use `in` for substring checks.
- **Precompute thresholds**: When filtering based on dynamic conditions, compute the boundary value once before looping.
- **Trace data dependencies**: Confirm which cells hold intermediate results so conditional checks reference the correct data state.
- **Respect specified range boundaries**: Limit scanning and operations to the exact range given (e.g., A7:A1000); do not extend beyond unless explicitly required.
- **Empty-cell check**: Treat `None`, empty strings, and whitespace-only strings as empty: `cell.value is None or str(cell.value).strip() == ''`.
- **Circular reference detection**: If a cell shows errors like `000` or `#REF!`, check whether its own address appears in its formula range.
- **Delimiter parsing**: Strip whitespace from each part and filter out empty strings caused by trailing delimiters: `[p.strip() for p in str(value).split(';') if p.strip()]`.
- **Fixed-length formats**: For predictable formats (e.g., ISO 8601 timestamps), extract the needed part with string slicing (e.g., `value[:10]` for the date) before parsing.
- **Upward search**: When looking for the most recent match above a reference row, iterate from `reference_row - 1` down to 0.
- **Use workbook's own sheet names**: Use `set(wb.sheetnames)` as a dynamic reference set for validation instead of hardcoding.
- **Inspect reference/desired result sheets**: When a reference or example sheet is provided, read its structure to confirm expected output before writing code.
- **Regex extraction**: When parsing structured text with a known prefix, use `re.search(r'Tag-([^,]*)', text)` to capture up to the first delimiter.
- **Scope writes to target cells**: Before modifying, identify exact target cells; do not overwrite working formulas outside that scope.
- **Confirm target text**: Before transforming, iterate through relevant cells to confirm which rows contain target text and which columns hold conditional values.

## Writing Output

- **Clean destination before writing**: Clear existing content and formatting from the target range to prevent stale data. Set cells to `None` and reset fill with `PatternFill(start_color=None, end_color=None, fill_type=None)`.
- **Restore number formats on assignment**: When writing values programmatically, check the Python data type (e.g., `datetime`, `float`) and manually assign the appropriate `number_format` property.
- **Safe row deletion**: Collect target row indices first, then delete from bottom to top to avoid index shifting. For contiguous rows, use a single `delete_rows(start, count)` call. Before deleting duplicate rows, confirm group size > 1; delete only the second occurrence (index 1) to preserve the first entry. When a group contains mixed relationship types and at least one row is a priority type (e.g., 'Employee'), keep all rows in that group; remove duplicates only if no row qualifies as priority.
- **Type-safe conversion**: When converting cell values to numbers, check type first: use `isinstance(val, (int, float))` or wrap `float()` in try/except to skip header strings. Cast cleaned numeric strings to `int` or `float` before assigning to `cell.value`.
- **Conditional copy**: Explicitly check the source cell value before assignment (`if source.value is not None`) to preserve existing target values when the condition is not met.
- **Use answer_position bounds**: When a task provides an `answer_position` range, use it to set exact row bounds for loops or range operations.
- **Openpyxl formula assignment**: Assign formulas directly to cell `.value` (e.g., `ws['A1'].value = '=IF(F10="","",F10&".Jr")'`); each cell must receive its own formula string if relative references differ. Use absolute references for fixed ranges and relative references for row-varying parts.
- **Multi-level sorting**: Use Python's `sort` with a tuple key (e.g., `key=lambda row: (row[col_a], row[col_b])`). Convert all key values to strings to handle mixed data types. Sort numeric IDs numerically: `sorted(ids, key=lambda x: int(x) if str(x).isdigit() else x)`.
- **Dictionary mapping for bulk replacements**: Define a mapping dictionary first and iterate; avoid chained conditionals. For table comparisons, build dictionaries keyed by composite identifiers for O(1) lookups; handle duplicate keys by storing only the first encountered value.
- **Case-insensitive keyword matching**: Normalize cell text to lowercase once and store keywords in lowercase. Use `any(kw in text for kw in keywords)`.
- **Separate data and presentation**: Store date/datetime objects as cell values, then set `cell.number_format` to the desired display string (e.g., `m/dd/yyyy`). For fixed-length ISO 8601 timestamps, extract components with predictable slices.
- **INDEX/MATCH for two-way lookups**: Use `=INDEX(return_column, MATCH(1, (lookup_col1=condition1)*(lookup_col2=condition2), 0))` or concatenated MATCH for compound keys.
- **Programmatic formula generation**: For repetitive formulas across a range, generate them with nested loops, constructing each cell's formula string individually.
- **Single-pass filtering**: When extracting rows with multiple criteria, apply all conditions in a single loop over the data.
- **Formula scaling**: When building formulas that scale across rows, anchor fixed inputs with absolute references (`$B$2`) and use relative ranges (`$B$3:B3`) for dynamic calculations.
- **Grouping & Reassembly**: When data is scattered with irregular gaps, group non-empty rows into logical ranges first, then operate on those ranges. When reassembling grouped blocks, add separators only between blocks (not after the last one). Use a boundary check like `if i < len(blocks) - 1` to avoid trailing empty rows.
- **Pandas for aggregation**: For grouped aggregation (e.g., deduplication across multiple key columns with sum), prefer `df.groupby([col1, col2, ...])[value_col].sum().reset_index()`. When writing DataFrames to an existing sheet at a specific column offset, use `df.to_excel(writer, sheet_name, startcol=N)`.
- **Safe style assignment**: Never assign `cell.font` or `cell.alignment` directly from another cell. Create new `Font()` or `Alignment()` objects by copying properties explicitly.
- **Robust date parsing**: Date columns often mix `datetime` objects, strings, and `None`. Create a helper to parse multiple formats before sorting; return `datetime.min` as fallback.
- **Formula vs. computed values**: Prefer computing values in Python and writing numeric literals. Only write Excel formula strings if the task explicitly requires formulas. When formulas are used, assign each cell its own formula string.
- **Index mapping and placement**: To populate a fixed-width grid from a flat list, use a sequential index mapping each value to the next cell in row-major order. For transposition, calculate source indices with `(target_row - offset) * chunk_size + base_row`.
- **Row insertion**: Process bottom-to-top to avoid index shifting. After insertion, verify newly inserted rows are empty and original rows have shifted to expected positions.
- **Precompute thresholds**: Calculate boundary values once before iterating.
- **Transpose wide to long**: Use nested iteration: for each row, extract constant identifiers, then loop through variable columns to generate one output row per variable.
- **Substring deletion**: When removing a substring from a cell, write the complete remaining value back; do not clear the entire cell unless explicitly instructed.
- **Include grouping column**: When merging or aggregating rows by a grouping key, explicitly include that grouping column in the output.
- **Apply consistent number formatting**: After aggregation, apply formats like '0.00' and convert zero sums to blanks if required.
- **Preserve source labels exactly**: When creating headers or labels from source data, read the unique strings and write them directly without stripping or case changes unless the task requires it.
- **New sheet creation**: If the answer position specifies a sheet not present in the input, create a fresh workbook with that sheet name; do not modify the original.
- **Prefer column indices**: Use column indices (e.g., column 33 for "AG") over column names for stability.
- **Header handling with DataFrames**: When writing a filtered/transformed DataFrame, if the first result row should become the new header, extract it before writing: `header = df.iloc[0].tolist(); df.iloc[1:].to_excel(path, index=False, header=header)`.
- **Style copying**: Write values first, then copy formatting attributes (font, border, fill, alignment, number_format) from the corresponding source cells cell-by-cell using new style objects.
- **Frequency-based sorting**: Use `collections.Counter` to count occurrences, then sort by frequency.
- **Tie handling**: Use `=COUNTIF(score_range, MAX(score_range))` to count winners and conditionally assign points.
- **Save only after verification**: Save with `wb.save()` after all writes are complete and verified.

## Verification

- **Reload and read-back**: After saving, reload the output file and read back the exact range you wrote to. Compare values against expected results.
- **Recalculate before reading**: If formulas are involved, ensure the workbook is recalculated (or open in Excel) before verification.
- **Check dimensions**: Print or assert the final dimensions (max_row, max_column) to catch off-by-one errors.
- **Floating-point tolerance**: Use absolute tolerance (`abs(total) > 0.01`) instead of exact equality for floating-point comparisons.
- **Whole-number verification**: Use `float(value) == int(float(value))` to check for whole numbers, not string parsing.
- **Deduplication/deletion verification**: After deduplication, verify that groups containing a priority type remain intact and that first occurrences are preserved. Spot-check a few groups manually. Confirm only groups larger than one were reduced.
- **Sample input-output pairs**: Print a sample of input-output pairs covering exact matches, partial matches, and non-matches to confirm logic before saving.
- **Formula reference check**: Confirm that generated formulas reference the exact mapped cells and results appear in the intended output cells.
- **Do not mark complete until verification passes**.
- **Spot-check checklist**: Confirm (a) row counts match expected filtered set, (b) a sample of values is correct, (c) formatting matches the source, (d) written data falls within intended data blocks, (e) correct number of blocks and separators only between blocks, no trailing empty rows.
- **Sheet existence**: Ensure the target sheet exists and is named correctly.
- **Targeted change verification**: After writing, verify that only the targeted cells changed and that pre-existing formulas in other rows remain intact.
- **Use evaluate_output tool**: If an evaluation tool is provided, use it to verify correctness; do not mark complete until it reports PASS.
- **Header fidelity**: After writing output, read back the header cells and confirm they are byte-for-byte identical to the original source values.
- **Literal value assertion**: If the task expects pre-computed values, open the output file with `data_only=True` and assert that all calculated cells contain numbers, not `None`.
- **Numeric type verification**: Verify cleaned numeric cells are stored as numeric types (`float`/`int`), not strings.
- **Substring integrity**: After string operations, read back the affected cells and confirm the unaffected portion remains unchanged and only the specified substring was removed.
- **Suffix check**: Use `=RIGHT(cell, LEN(check_cell))=check_cell` to verify a string ends with a specific substring.
- **Index mapping verification**: After writing, verify that labels align with correct input columns by checking the index mapping used during computation.
- **Aggregation checks**: Confirm row count decreased correctly and sums match original totals.
- **Row insertion verification**: After row insertions, verify that (1) newly inserted rows are empty, and (2) original rows have shifted down by one position and still contain their original data.
- **Clear both content and formatting**: When clearing a column or range, ensure both `cell.value = None` and fill reset (`PatternFill(start_color=None, end_color=None, fill_type=None)`) are applied.
- **VBA macro audit**: When a macro loops over rows, check that it uses `Cells(row, col)` or `Range("A" & rowNumber)` — never `Columns(rowIdx, colIdx)`. See `references/vba-macro-patterns.md` for correct patterns.

## Common Pitfalls

- **Hardcoded indices / guessing positions**: Row/column numbers shift when sheets change. Always detect boundaries from cell content.
- **Index shifting on row deletion**: Deleting rows top-down shifts indices, causing skipped or wrong rows. Always delete bottom-up.
- **Header cells crashing numeric conversion**: String headers in numeric columns cause `float()` to raise ValueError. Validate types before conversion.
- **Floating-point exact equality**: Tiny precision artifacts make `sum() == 0` fail. Use `abs(sum()) < 0.01` for zero detection.
- **Single-column duplicate detection**: Detecting duplicates with only one column leads to mismatched groups. Always build a composite key from multiple identifying columns.
- **Duplicate lookup keys**: VLOOKUP or INDEX/MATCH on non-unique keys produce unpredictable results. Use a dictionary to store the first match per key.
- **Deleting rows without checking group size**: Can corrupt data. Ensure group size > 1 before removal.
- **Blind removal in mixed-role groups**: May delete important records. Apply priority-based preservation when roles differ.
- **Case-sensitive matching failures**: Always normalize to lowercase before string comparisons.
- **Off-by-one in index-based ops**: `delete_rows(idx)` uses 1-based indexing; verify target index against actual row position. Reload and check dimensions post-deletion.
- **Stale file handles / skipped verification**: Writing without reloading and reading back hides off-by-one errors, misaligned ranges, and incomplete deletions. Always verify before marking complete.
- **Gap-prone sequential numbering**: Avoid simple row-based counters when source data may contain blanks. Prefer `COUNTA($B$3:B[current_row])` to count only non-empty cells.
- **String concatenation with numbers**: Raw numbers lose leading zeros in concatenated strings. Wrap numeric results in `TEXT(value,"000")` (or appropriate digit count).
- **Mismatched dimension lookups**: When comparing sources with mismatched dimensions, always check for key existence before accessing dictionary values; return False for missing combinations.
- **Cell value type safety**: When checking cell values for prefixes or patterns, always convert to string first and handle `None` explicitly. Use `str(cell.value).startswith(...)` combined with a `None` check.
- **Structural changes via native APIs**: For adding/removing rows or columns, use the spreadsheet library's dedicated methods (e.g., `delete_cols()`, `insert_rows()`, `append()`) rather than manually nullifying cells.
- **VLOOKUP #N/A with visible matches**: Source data likely has leading/trailing whitespace. When you cannot modify the source data, wrap the lookup table range with `TRIM()` (e.g., `VLOOKUP(A1, TRIM(Sheet3!$A$2:$D$300), 2, FALSE)`).
- **Shell escaping in inline Python**: Dollar signs, quotes, and parentheses in formulas break inline bash Python. Always write the script to a file and execute it.
- **Empty-cell references in formulas**: Writing formulas that reference empty cells without guarding can produce unwanted results; always wrap in `IF(cell="","", ...)`.
- **Keystroke simulation**: Simulating keystrokes to enter formulas is error-prone; use openpyxl direct formula assignment instead.
- **Single-pass transformation of mixed-type columns**: Avoid applying one transformation to an entire column when values may have different types; inspect and branch by type first.
- **Repeated sheet lookups inside loops**: Pre-build dictionaries for joins to avoid O(n²) performance.
- **Failing to validate output dimensions**: Always check the output range and row count to catch truncation or duplication.
- **Hardcoding variable columns or indices**: Use programmatic boundary detection and iteration to handle dynamic column counts.
- **Circular references**: A cell showing `000`, `#REF!`, or calculation errors often means its own address is inside its formula range. Fix by adjusting the range bounds to exclude the target cell.
- **VBA column indexing misuse**: Use `Cells(row, col)` or `Range("A" & row)`. The `Columns(row, col)` syntax expects column indices, not row numbers. See `references/vba-macro-patterns.md`.
- **Forgetting to include the grouping column** in output after merge/aggregation.
- **Omitting consistent number formatting** (e.g., '0.00') and explicit zero-to-blank handling for aggregated numeric data.
- **Manual cell-by-cell clearing for structural changes**: Use native APIs like `delete_cols()`, `delete_rows()`, or `append()`.
- **None values in output**: Empty cells become `None` in openpyxl; always filter with `if value is not None` during extraction.
- **Duplicate delimiters**: If a string already ends with the delimiter (e.g., '+'), appending another produces '++'. Inspect first, then concatenate directly.
- **Exact-match assumptions**: Headers may be substrings within longer identifiers; use `in` checks rather than `==` for cross-sheet matching.
- **Assuming file structure matches task description** without inspection.
- **Skipping post-write verification**: Writes can silently land in wrong cells; always read back.
- **Reusing one openpyxl formula string** across multiple cells expecting relative-reference adjustment; each target cell must receive its own formula.
- **Missing combination handling**: When a result grid references combinations missing from one or both sources, check for existence in each source before comparing; return False instead of raising KeyError or NoneType errors.
- **Row deletion order**: Always delete rows in reverse order (bottom to top) to prevent index shifting.
- **String conversion before pattern matching**: Convert cell values to strings with `str()` before applying methods like `startswith()` to handle mixed data types.
- **StyleProxy error**: Assigning `cell.font` or `cell.alignment` directly from another cell. Always copy properties into new style objects.
- **Mixed date formats**: Sorting fails on heterogeneous date columns; always parse to `datetime` first.
- **Unstable sorts**: Single-key sorts on non-unique values are unpredictable. Use tuple keys for deterministic multi-level sorting.
- **Pattern matching on mixed types**: Convert cell values to strings before pattern matching.
- **Text matching must be case-insensitive and substring-aware**: Use `'target' in str(cell).lower()` for filtering, and `in` rather than exact equality when linking cross-sheet headers.
- **None vs. empty strings**: openpyxl may return `None` or empty strings for blank cells. Use `cell.value is None or cell.value == ''` and filter during extraction.
- **Case-sensitive sheet names**: Verify sheet names by printing `workbook.sheetnames` before referencing.
- **RGB color comparison**: openpyxl fill colors are RGB objects, not strings; always convert with `str()` before checking: `str(cell.fill.start_color.rgb)`.
- **Guard empty inputs in conditional formulas**: Use `IF(cell="","",...)` to avoid errors.
- **Complex IF/AND for category-based ranking**: Can fail when largest value overall belongs to a different category. Use group-then-sort strategy instead.
- **Duplicate delimiters when concatenating**: Inspect whether first string already ends with the delimiter.
- **Manual editing of expanding-range formulas row-by-row**: Use absolute-start/relative-end pattern (`$A$2:A{row}`).
- **Separate IF for priority conditions**: Use nested IF to ensure correct short-circuit evaluation from highest to lowest priority.
- **Avoid relying on exact header names**: Use numeric column indices when positions are consistent, or scan headers case-insensitively.
- **Skipping boundary checks**: Always verify first/last rows and incomplete chunks after transpositions.
- **Hardcoding per-cell assignments for scattered columns**: Use index/offset loops or `startcol`/`startrow` parameters.
- **Inline Python escaping**: Shell escaping breaks formulas containing `$`, quotes, or parentheses. Always write to a `.py` file and execute that file instead of using `python -c`.
- **Silent formatting failures**: Formulas may save correctly while number_format or alignment does not. Always verify both after writing.
- **openpyxl color checks**: Cell fill colors are RGB objects, not plain strings. Convert with `str()` before comparing.
- **Stale data**: Forgotten old values in cells that are skipped during a partial update. Always clear the full target range before writing.
- **Whitespace/delimiter mistakes**: Forgetting to strip whitespace when building lookup dictionaries, or not filtering empty strings when splitting delimiter-separated values.
- **Unsorted/non-deduplicated output**: Joining results without sorting or deduplication produces inconsistent output. Use a set to deduplicate and sort before joining.
- **Trailing empty rows**: Adding separators after the last data block when flattening multi-section data. Fix: conditional separator insertion (`if i < len(ranges) - 1`).
- **Overlooking reference sheets**: Failing to inspect a provided "Desired Results" or reference sheet. Always check for and read reference sheets first.
- **Header off-by-one**: After row filtering, keeping the original header and writing all filtered rows as data when the first result row should become the new header. Use the first filtered row as `header` and write only `iloc[1:]`.
- **VBA `Columns(row, col)` misuse**: The `Columns` property expects column indices, not row numbers. Always use `Cells` or constructed `Range` strings.
- **Hardcoding row indices**: Assuming fixed ranges when data ranges vary between worksheets. Use dynamic boundary detection.
- **Reading formulas before recalculation**: Reading formula results before recalculation returns cached/stale values. Always recalculate after writing formulas.
- **Assuming single contiguous block**: Assuming data is a single contiguous block without scanning for blank rows that separate sections.


## Common Pitfalls

### Suffix Verification
Use `=RIGHT(cell, LEN(suffix))=suffix` to check if a string ends with a specific substring.

### Two-Pass Aggregation for Context-Dependent Operations
When a cell value depends on both aggregated properties of a grouping (e.g., week, employee, category) and contextual positioning (e.g., row preceded by a different group), use a two-pass approach:
1. **First pass**: Scan all rows to build a mapping from group identifier to aggregated properties (e.g., a boolean dict indicating which weeks meet a condition).
2. **Second pass**: For each row, evaluate the condition using the aggregated mapping and the row's positional context (e.g., whether its group differs from the previous row).
This avoids fragile single-pass formulas and handles non-contiguous or re-occurring groups reliably.

### Sequence-Based Group Boundary Detection
To detect transitions between groups (e.g., the start of a new week block), compare each row's group identifier with the previous row's group identifier. When the values differ, a boundary is detected. This row-by-row comparison works correctly even when groups are non-contiguous or re-appear later in the sheet.

### Marker-Based Range Aggregation
For tasks requiring aggregation between repeating markers (e.g., section headers), first locate all marker positions and store their row indices. Then iterate over consecutive marker pairs to define calculation ranges. This avoids complex conditional logic inside data rows and reduces off-by-one errors.

### Lookup Dictionaries
When cross-referencing values from a two-column lookup table, parse the table into a dictionary first. Strip whitespace from keys and values during construction. This enables O(1) lookups and avoids repeated sheet reads.

### Delimiter-Separated Values
When parsing cells with delimiter-separated values (semicolons, commas, etc.), always strip whitespace and filter out empty strings from trailing/leading delimiters. Use: `[p.strip() for p in str(value).split(';') if p.strip()]`.

### Unique Collection and Sorting
Collect results in a set to automatically deduplicate, then convert to a sorted list before joining. This ensures deterministic, ordered output regardless of input order.

### Sequential Value Extraction Under Repeating Headers
When extracting values from rows grouped by repeating section headers, maintain a boolean flag to track when a header row has been seen and collect the value from the next row.

### Conditional Index Advancement in Block-Based Mapping
When mapping a sequential list of source values to target blocks filtered by a condition, increment the source index only for blocks that satisfy the condition. This preserves alignment between source values and matching targets regardless of non-matching blocks.

### Dynamic Reference Sets for Validation
Use the workbook's own structure (e.g., `wb.sheetnames`) as a reference set for validating column values instead of hardcoding values. This keeps the solution robust when sheet names or other structural elements change between file instances.

### Date-Range Filter Loop
For filtering rows by a date range, loop over rows, compare each date to start/end variables, and collect matching rows. This is simpler and more transparent than embedding complex date logic in spreadsheet formulas.

### Group-Then-Sort for Category-Based Ranking
When finding top N values per category, avoid complex IF/AND formulas. Instead:
1. Collect all values belonging to each category into separate lists, preserving original column indices.
2. Sort each list independently.
3. Select the desired rank from each sorted list.
4. Map the result back to the original column position using the preserved index.
This eliminates the need for conditional formulas and handles any number of categories or ranking positions.

### Sequential Filling Patterns
- **Stateful iteration**: Maintain a variable outside the loop to store the last valid value; update and use it to fill blanks.
- **Custom sequence generation**: For alphanumeric labels beyond 'z', implement a base-26 counter.
- **Resetting counters on new groups**: When a new base value is detected (e.g., new group number), reset the sequential suffix counter.

### Formula Patterns
- **Expanding cumulative ranges**: Anchor the starting cell with an absolute reference and leave the ending cell relative (e.g., `=SUM($B$2:B2)`). When copied down, the end reference increments while the start remains anchored.
- **Nested IF for priority logic**: Chain IF statements in priority order. The first TRUE condition returns its result; later conditions only evaluate if earlier conditions are FALSE.
- **COUNTIFS for multi-condition row evaluation**: Use COUNTIFS with paired criteria ranges, then test whether the count is greater than zero to detect existence.

### VBA Macro Patterns
For correct VBA cell referencing and bulk operations, see `references/vba-macro-patterns.md`.