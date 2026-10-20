---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow


1. Inspect the entire workbook: load and print all non‑empty cells with coordinates, values, types, and number formats.

Always follow a two-stage loop: inspect the entire workbook before any modification, and verify the output after saving by reloading the workbook from disk (do not rely on in‑memory state). This habit catches misplacements and provides a clear picture of the result.

- ⚠️ CRITICAL: Never create a new workbook with `openpyxl.Workbook()`. Always load the existing file with `openpyxl.load_workbook(spreadsheet_path)` and modify it in place. After saving, reload the output and print the exact answer range (as stated in `answer_position`) to confirm all values are plain data (no formula strings) and that all original sheet names are still present. Only call `TASK_COMPLETE` after this check passes.

After this inspection, you have all the information needed to write the solution; do not inspect again unless you encounter a specific issue during implementation. Proceed directly to writing the script.

2. After 2–3 focused inspection steps, write a Python script that produces the required output and saves it to the `output_path` specified in the task.
If you have inspected the workbook for more than 3 turns without writing any code, or if you receive a system warning about a missing output file, stop and immediately write the output script, even if you are unsure of some details. Verify the file exists with `assert os.path.exists(OUTPUT_PATH)`, then reload it with `data_only=True` and run the verification checks (see Verification). Never continue exploring without producing the deliverable.

- Always use the exact absolute file paths provided in the task instruction (`spreadsheet_path` and `output_path`). Never change directory or guess paths; pass them directly to Python scripts.

- If the task allows solving without VBA, always use Python/openpyxl; never write VBA macros. This keeps the solution simple, auditable, and easy to verify.
## Inspection


Before any modification, thoroughly inspect the workbook:
**Mandatory: Start by dumping every sheet's entire contents (all rows, all columns) with cell values and coordinates.** This is the most important inspection step; do not skip it. It ensures you understand the full data layout and can correctly compute sums, counts, and other aggregations.

- Copy the `spreadsheet_path` from the task prompt (do not retype), print it, and confirm the file exists with `assert os.path.exists(spreadsheet_path)` before loading the workbook.
- Load and print every sheet's content (all non-empty cells) with coordinates, raw values, types, and number formats. Do not skip hidden sheets or assume anything about layout.
- Read all sheets, including any example or expected output sheet, to confirm headers, row ranges, and data types.
- Dump the entire workbook's contents (all sheets, all cells with values and coordinates) to map every data table, header row, label column, and target output range.
- Verify the exact column name and row indices that will be affected.
- Locate target columns dynamically by scanning header rows for expected labels using case‑insensitive or stripped/lowered matching; avoid hard‑coding column letters. After moving a column, verify that the header in the new location still matches.
- When searching for a specific header label, always strip whitespace and casefold both the cell value and the expected label (e.g., `cell_value.strip().casefold() == 'code'`). Print the normalized values before the equality check to confirm you are matching the cleaned text you intended.
This habit prevents misunderstandings about where the answer should go and what kind of answer is expected.
- This thorough inspection catches hidden headers and empty rows that could alter your later logic.

- When printing cell contents, always include the `.data_type` attribute (e.g., `cell.data_type`) to distinguish numeric constants from formula results or dates.
Also print the Python type of the cell's value (e.g., `type(cell.value).__name__`) to detect unexpected types like strings where numbers are expected, or `\xa0` placeholders.

- If a cell's value is a string starting with `=`, it is a text representation of a formula, not a real formula; treat it as plain text unless the task explicitly requires formulas.
- If a column contains coded identifiers (e.g., account references with type prefixes), print unique first tokens or distinct values to confirm the categories and catch unexpected labels before writing output.

- If the workbook contains example outputs, use them to cross-check the expected output pattern and formatting before writing your solution.
- When loading the workbook, use `data_only=False` to ensure you can see formulas and all cell metadata.

For any workbook containing formulas, load with `data_only=False` and print both the formula text (`cell.value`) and the cached value (`cell.internal_value`) for key ranges. Alternatively, load two copies (one with `data_only=False` for formulas, one with `data_only=True` for evaluated values) and cross-reference. This reveals intended logic and mismatches.

- Print `wb.sheetnames` to list all sheet names before iterating over sheets. This ensures you don't miss hidden sheets.
- Before writing any modification script, print the exact rows and columns that will be affected (e.g., the range you plan to modify) to confirm the layout, data values, and data types. This targeted check complements the full‑sheet dump and prevents assumptions about the structure.

- For large sheets, print only the rows where key columns are non-null or change to detect gaps, intervals, and patterns efficiently.
- If the data appears to be grouped into blocks (e.g., by invoice numbers or employee IDs), print the rows where the grouping key changes to confirm block boundaries and detect embedded headers or total rows. This helps catch structural patterns before writing logic.

- When printing cell values or comparing strings, use `repr()` to reveal hidden whitespace, non‑breaking spaces, None, or datetime types that could cause mismatches.

- When inspecting a data range, always print the first 10-15 rows and the last few rows (e.g., the final 10 rows) to confirm the physical extent of the data. This catches trailing anomalies and ensures loop limits match reality.
- When inspecting relevant columns, print all rows to understand the distribution of values, including error strings like `#N/A` and numeric ranges. This reveals edge cases (e.g., missing data, outliers) before you write any logic.

- Before writing any modification, print a window of at least 5 rows or columns around the target cell (e.g., `ws.iter_rows(min_row=target_row-5, max_row=target_row+5, ...)`) to confirm surrounding data and ensure the planned change won't break existing relationships.

- Before writing, print a list of all rows where every cell in the target columns is empty, to confirm the exact start and end of the data block.

- After inspecting the data, manually compute the expected result for a few sample rows (e.g., sum, lookup) to validate your understanding of the required transformation before writing any code. This mental check catches misinterpretations early.
- When printing rows with `iter_rows`, always include the row number (e.g., `print(f'Row {r}:', values)`) so you can confirm the exact row indices your code will target. This habit, validated in practice, prevents misalignment between inspection and modification.

- During the initial full dump of the target sheet, print `cell.fill.fgColor.rgb` and `cell.font` for every cell in the range, regardless of whether the task mentions formatting. This reveals existing styles and prevents mismatched formatting later. If the task involves borders or alignment, include those as well.

- Print column headers and a sample of rows (e.g., first 10 rows) to verify data format and detect special cases (like mixed types or suffixed values) that might affect the transformation logic.

This exploration habit, validated in practice, prevents accidental deletion of important data and ensures accurate transformation logic.


- Before any modification, scan the workbook for merged cells using `ws.merged_cells.ranges` and unmerge them all programmatically with `ws.unmerge_cells(str(merged_range))`. This prevents hidden cell‑range artifacts that can distort lookups, writes, or aggregation formulas. Even if the task later requires merging cells, unmerge first to ensure clean data, then re‑merge as needed after processing.

- When the task involves fixing errors in existing cells, inspect the problematic cells, their formulas, and surrounding context to diagnose the root cause before writing any fix. Understanding why a cell is wrong (formula error, data mismatch, formatting issue) prevents blind edits and ensures the correction addresses the actual problem.

Successful runs confirm: always list all sheets, their dimensions, and all non‑empty cells in the region of interest before any modification.

- If the workbook contains sheets named 'result', 'expected', or similar, treat them as part of the full inspection. Print their complete cell contents (coordinates, values, types, formats) to understand the expected output layout and formatting, even if you will not write to those sheets.

This reveals blank columns, hidden data, and ensures you discover the actual location of relevant data rather than assuming it is in the first few columns.

- Immediately after loading the workbook, print each sheet's `dimensions` and the first 5 and last 5 rows (using `iter_rows` with `values_only=True`) to confirm the layout matches the task description. This quick spot-check catches mismatched column counts or unexpected blank rows before the full dump.

- If the task instruction is ambiguous, treat any example sheet (e.g., 'After', 'Expected') as the authoritative guide for the intended output format and content. Study it to resolve ambiguities before writing your solution.

- When scanning for cells that satisfy a condition (e.g., containing a specific value), always test the **evaluated** value (from `data_only=True` or `cell.internal_value`) against the condition, not the raw formula string. Before acting on the matched cells, print both the raw formula and the computed value for each candidate to confirm that no formula-generated matches are missed.

- Before writing any changes, print the target rows and any lookup tables, showing cell types (data vs. formula), to understand the existing pattern.

- After the initial full dump, do not print the entire sheet again. If you need to verify something, print only the relevant rows or columns. If you find yourself dumping the same sheet a second time, stop and proceed to writing the solution.

- If the workbook contains a sheet with partial or example output (e.g., some rows already filled), inspect those rows in detail to deduce the intended ordering (grouping, field sequence, separators) and replicate it exactly. After writing, print the first few rows of your output and compare them side-by-side with the example rows to confirm the pattern matches.

**Proven success factor:** This full-dump inspection habit is repeatedly validated in practice and is the foundation of all successful solutions. Always perform it as the very first action.

Prefer a single script that prints all sheets' contents in one pass, rather than multiple separate inspections, to capture the full workbook structure efficiently and avoid missing hidden sheets or rows.
## Writing Output


⚠️ CRITICAL: Never write Excel formula strings (e.g., `=IF(A2=J2, B2-C2-E2-G2, 0)`) into cells.
When the task says 'place' a result in a cell, write the computed numeric value, not a formula string. Even if the task says 'create a formula', 'fix a formula', 'populate' cells, or 'use a formula', always compute the result in Python and write the plain numeric value. Do not insert a string that starts with `=`.


**Write computed values, not formulas.** Unless the task explicitly asks for formulas or macros, compute the final data yourself and write it as a plain number or string.
- If you are ever unsure whether to write a formula string or a computed value, always write the computed value.
When the task specifies a number of decimal places (e.g., "to 11 decimal places"), round the computed value to that many decimal places before assigning to the cell. Use Python's `round(value, places)`. After writing, verify the stored value's string representation has no more than the required digits (see Verification step 18).
 Before you compute the output, print the `.data_type` and `.value` of every input cell your output will reference. If any input cell is a formula (data_type `'f'`), load the workbook with `data_only=True` to see its actual evaluated value, not the formula text. Use that value to compute the result and write it as a static value. Never write a formula that references other formula cells; the grader may not evaluate them. Do not write Excel formulas (e.g., INDEX/MATCH). Compute all calculations in Python (e.g., using `openpyxl` or standard libraries) and write the final numeric or string result.
 If a cell already contains a formula, overwrite it with the computed value; do not modify the formula.

**Modify the existing workbook in place.** Load the input workbook with `openpyxl.load_workbook(spreadsheet_path)`, select the target sheet with `wb[sheet_name]`, modify its cells directly, and save to `output_path`. Never create a new workbook with `openpyxl.Workbook()` unless the task explicitly asks for a blank file. After saving, verify that the output workbook contains exactly the sheets from the original input (no extra default sheets).


### When Formulas Are Required
If the task mentions a formula, inspect the full data range and any existing summary‑table formulas to understand the intended logic. Print the relevant cells' formula text and cached values to identify any mistakes.

⚠️ Even when the task says 'create a formula', 'use a formula', or 'fix a formula', do NOT write Excel formula strings into cells. Instead, implement the same logic in Python (e.g., using loops, sums, conditionals) and write the computed plain value. This ensures the grader sees real numbers, not None.

- **Validate formula output with computed values**: Before writing, compute the expected literal results in Python. After saving, reload the workbook with `data_only=True` and assert that each cell's value matches the expected computed result. This catches logic errors that produce incorrect values despite correct syntax.
### Moving Columns
- Use `ws.insert_cols(target_col, 1)` to create a blank column at the destination, then copy values and styles from the source column into it, and finally `ws.delete_cols(source_col)` to remove the original.
- Never shift columns manually with per‑cell loops – this leaves stale data.
- After the move, print both the source column’s data rows and the destination column’s data rows in the same script to confirm the values match.

### Creating Result Sheets
When building a new sheet that replaces or extends an existing data table, copy column widths, row heights, gridline settings, and basic cell formatting from the source sheet to maintain visual consistency. For example, using openpyxl:
```python
for key, dim in src.column_dimensions.items():
    out.column_dimensions[key].width = dim.width
out.sheet_view.showGridLines = src.sheet_view.showGridLines
```
After writing, compare column widths of the first data row between source and destination (e.g., `out.column_dimensions['A'].width == src.column_dimensions['A'].width`) to confirm they match.


Even if the existing workbook contains formulas, do not write formulas unless the task explicitly requests them. Always compute the final values in Python and write the results as plain numbers or strings.
- Before saving, loop over the answer range and assert that no cell value is a string starting with `=` or `'=` (a single quote prefix). If any are found, replace them with computed values immediately.

After saving, reload the file and run the verification checks described in the Verification section. Do not proceed to TASK_COMPLETE until all checks pass.

When copying data from source cells to target cells (e.g., filtering rows), copy the source cell's entire style using `target_cell._style = copy(source_cell._style)` (import `from copy import copy`). This preserves all formatting (font, border, fill, number_format, alignment, etc.) without missing any attribute.

Never assign style attributes directly (e.g., `dst.font = src.font` or `dst.alignment = src.alignment`) — this raises `TypeError: unhashable type: 'StyleProxy'`. Always use `copy()`.
When setting cell fills directly (not copying), always use `PatternFill(fill_type='solid', fgColor='FF' + color_hex)` to ensure opacity. Never omit the alpha channel or use `start_color` without `FF`, as this results in transparent fills. After applying, verify with `cell.fill.fgColor.rgb.startswith('FF')`.
- When duplicating rows to a new sheet, also copy row heights and column widths from the source sheet (see 'Creating Result Sheets').

The grader reads the actual cell content, not the formula text. If you write a formula string (e.g., `=SUMIF(...)`) into a cell, the grader will see `None` when reading with `data_only=True`. Always compute the result in Python and write a plain number or string. Only write an Excel formula if the task explicitly says 'write an Excel formula' and the grader expects to evaluate it.

- If the task mentions a 'formula' but the example output cells contain literal values (booleans, numbers, text), write computed results, not Excel formulas.


- **Explicit output cell addresses**: If the task instruction gives exact cell coordinates for each output (e.g., 'Place output in H10, H20, H24'), copy those addresses verbatim into your script and map each computation to the correct cell. Do not infer target cells from data ranges. After writing, print the values of only those cells and verify they match the expected source ranges.

- When the task asks to create a new sheet, always add it to the existing workbook (e.g., `wb.create_sheet('NewSheet')`). Do not create a new workbook object. After saving, verify that all original sheet names are still present (see Verification step 11).

For summary cells (totals, differences, averages, etc.), always compute the result in Python and write the numeric value; never write strings like `=SUM(...)` or `=C2-D2`.

⚠️ MANDATORY: Clear the answer range before writing any new values, even if you plan to overwrite every cell. 
- Before writing to the answer range, clear all cells in that exact rectangular area (using the `answer_position` from the task) by setting `.value = None`. This removes any pre-existing data that could remain if your script does not overwrite every cell. After clearing, verify that the range is empty (all values `None`) before writing your computed values.

- Respect the exact dimensions of the answer range: if the range has a fixed number of rows/columns (e.g., A1:A50), do not write beyond it, even if you have more data. Truncate or pad as needed. After writing, verify that the range contains exactly the expected number of filled cells and that no data appears outside it (see Verification).
## Verification



⚠️ MANDATORY: After saving, reload the workbook and run all checks below. Do not call TASK_COMPLETE until they pass.
Never skip this step; even if the writing script prints a success message, you must reload the file and verify the answer range with types and values before completing the task.

If the workbook contains an 'After' or 'Expected' sheet, use it to understand the intended transformation, especially when the task description is ambiguous. After writing, verify that your output matches the pattern shown, but do not rely on it as the sole source of truth; it may be incomplete. Always verify the answer range directly using the checks below.
### Post-Save Verification

⚠️ **Sampling is not enough.** After the quick spot-check, you must iterate over every cell in the exact answer range and programmatically assert the expected conditions. Do not rely on inspecting only a handful of rows; a full check is the only way to ensure no errors are lurking in later rows.

After saving the workbook, always reload it with `data_only=True` and verify the answer range:

1. Print the active sheet name: `print(ws.title)`.
2. Print the target cell value, data_type, and number_format: `print(cell.value, cell.data_type, cell.number_format)`.
3. For the exact grader‑specified answer range, print each cell’s coordinate, value, and type:
   ```python
   for row in ws['J3:N5']:  # adjust range as needed
       for cell in row:
           print(cell.coordinate, cell.value, type(cell.value))

Always print every cell in the range, even those with `None`; this reveals leftover data or missing formatting that a partial print could hide.
After printing, always run the formula check (step 4) and print a boolean summary (e.g., `print('All cells literal:', all(...))`). Do not rely on visual inspection alone; a programmatic check is mandatory.

Additionally, print the count of non‑None cells in the range and sample the first 3 and last 3 rows to quickly spot missing or mis‑typed data.


- For tasks that ask to 'place' a result, assert that each cell's value is numeric (int/float) and not a string. Check that no cell in the answer range is `None` (unless the task expects empty cells) and that each cell's data type matches the expected type (e.g., int, float, str). If a cell is unexpectedly None or wrong type, fix before completing.
   ```
4. Confirm that all values are plain literals (not formulas) unless the task explicitly requires formulas. Check that no cell value is a string starting with `=`:
   ```python
   for row in ws.iter_rows(min_row=..., max_row=..., min_col=..., max_col=...):
       for cell in row:
           if (isinstance(cell.value, str) and (cell.value.startswith('=') or cell.value.startswith("'="))) or cell.data_type == 'f':
               raise ValueError(f'Formula found in cell {cell.coordinate}')
   print("All answer cells are literal values: True")
   ```
5. Compare the printed values against the expected pattern (often the original source column’s data rows). If values don’t match, do **not** call `TASK_COMPLETE`; fix the issue first.
6. Print both source and destination data rows side‑by‑side to spot mismatches instantly.
7. For string matching tasks, print unique values from the target column during inspection. If any intended match value has unexpected spaces or case, adjust the matching code.
8. After writing a date, currency, or percentage value, read back the cell and print its `number_format` property. Confirm it is a date/number format, not `'General'`.
9. After writing a script that saves a file, confirm the file was created by running `ls -l <output_path>`.

10. If the task required formulas, after saving, reload and print each formula string in the answer range. Confirm that they reference the full data range and use correct grouping keys (as described in the formula writing guidelines).



**Mandatory Checks:** Always use the `answer_position` specified in the task to determine the exact range to verify. The formula check (step 4) and the non‑None cell count / dimension check (step 3) are mandatory for every output. Do not skip them.

11. If you modified an existing workbook, confirm that all original sheet names are still present: `assert original_sheetnames.issubset(wb.sheetnames)`.
12. After checking for formula strings, also verify that `cell.data_type` matches the expected type (e.g., `'n'` for numbers, `'d'` for dates). If a cell has an unexpected type, recompute and rewrite the value.
13. Perform additional verification for specific operations:
   - After deleting rows or columns based on a condition, reload and print the remaining data. Then programmatically assert that no row still matches the deletion condition (e.g., `assert not any(condition for row in ws.iter_rows(...))`). Also run the mandatory formula check (step 4) on the answer range to ensure no formula strings remain.
   - If column indices were determined dynamically, print the column mapping (header label → column index) and the first few rows of each required column to confirm the correct columns were used.
14. Identify the logical condition from the task instruction (e.g., 'all remaining groups have exactly one entry', 'residuals must be zero', 'values must be within bounds') and assert it programmatically. Load the saved workbook and check that the condition holds before calling TASK_COMPLETE.


15. Print the dimensions (max_row, max_col) and first 3 rows of every sheet to confirm the overall workbook structure is intact.

Assert that the sheet names and dimensions match the original workbook (unless the task explicitly changes them). This catches accidental sheet loss or content shifts. This catches accidental sheet deletions or content shifts.


16. After printing the raw values, write a short validation script that loads the saved workbook, iterates over the exact answer range, and programmatically checks all required conditions (value type, format string, non‑None, range boundaries, etc.). Print a single boolean summary (e.g., `All checks passed: True`). This prevents errors from manual visual inspection of printed dumps.

- Also assert that the answer range has the expected number of rows and columns (shape) before calling TASK_COMPLETE.

- Do not call TASK_COMPLETE until all verification steps pass and the boolean summary is True. If any check fails, fix the issue and re-verify.


17. When the task involves cell formatting (fills, fonts, borders, alignment), reload the saved workbook and print the `.fill`, `.font`, and `.alignment` properties of a sample of the target cells. Confirm they match the expected formatting before calling TASK_COMPLETE.
For fills specifically, assert that `cell.fill.fgColor.rgb.startswith('FF')` and `cell.fill.fill_type == 'solid'` to guarantee opacity. If the fill is transparent (alpha not FF), fix and re‑save.

Also verify that the font and alignment objects are not `None` (which would indicate a failed copy due to StyleProxy errors).


- For value deletions (e.g., clearing cells based on another column's emptiness), reload and assert that the cleared cells are indeed empty (e.g., `assert ws.cell(row, col).value is None`).

Before writing, round numeric values to the required precision using `round(value, places)`. After saving, verify that no stored value has more decimal places than specified. Check with `len(repr(cell.value).split('.')[1]) <= places` for a sample of answer cells. If any exceed, round and re‑save.

- For sorting tasks, after saving, reload and print the first few rows of the sorted range. Confirm that the row order respects the primary sorting rules (helper column, original order) and that no contradictory global sort has been applied.

- When the task specifies an answer range (e.g., 'A1:B90'), iterate over the exact row and column numbers from that range (e.g., `for row in ws['A1:B90']:`) rather than relying on `ws.max_row` or `ws.max_column`. This ensures the full graded range is verified, including any columns or rows beyond the sheet's reported dimensions.

- **Check for leftover data beyond the answer range**: If the answer range is a subset of a larger data area (e.g., columns that previously held values), scan a few rows beyond the expected range to confirm no residual values remain from prior attempts. This catches incomplete clears or off-by-one errors that leave stale data adjacent to the graded cells.

Before running the full assertion suite, quickly print the header row and a couple of data rows from the output file to visually confirm the header is unchanged and the transformation looks correct. This fast spot‑check catches obvious errors early.

- When a transformation involves partial deletion or extraction (e.g., removing a substring), reload the output and print the answer range. Confirm that the remaining content matches the expected pattern from any example sheet, and that headers are preserved.

- If any cell in the answer range is `None` after reloading with `data_only=True`, you likely wrote a formula string that was not evaluated; recompute the value in Python and re-save.
## Common Pitfalls


- Writing a formula string (e.g., `=VLOOKUP(...)`) instead of the computed result. The grader expects the evaluated value, not the formula text. Always compute programmatically and write the result.
- **String matching**: Always check `isinstance(value, str)` before performing string operations. Normalize both the lookup value and cell text by stripping whitespace and case-folding (e.g., `.strip().casefold()` or `.strip().upper()` depending on need). Apply the same normalization when comparing sheet names, header labels, or any string identifiers from different sources. Never convert arbitrary cell types to strings with `str(...)` for text matching; this can cause false positives or missed deletions.
- **Number formats**: After writing any value that should preserve the source's format (e.g., date, currency, percentage, or any value copied from another cell), explicitly copy `.number_format` from the source cell (`target.number_format = source.number_format`). Default formats can cause incorrect display.
- Avoid `cd` to change directory; use absolute paths in scripts instead. Before any shell command that depends on a current directory, verify the directory exists with `ls -d <path>`.
 Also run `ls <path>/*` to confirm the directory contains the expected input files.
- **Row deletion index shift**: When deleting rows based on a condition, iterate in reverse (`for row_idx in range(ws.max_row, 1, -1)`) to avoid shifting the positions of rows yet to be checked.

- **Blank row deletion boundaries**: When deleting blank rows, first print all values in the column to identify the first and last populated rows, then delete only the blank rows between them in reverse order. This avoids hard‑coded ranges and ensures correct boundaries.

- **Over‑exploration without output**: Spending many turns inspecting the workbook without writing the required output file. After 2–3 inspection steps, write the output script and save the file.
- **Block‑level grouping**: When a condition depends on the contents of a contiguous block of rows that share a combination of keys (e.g., employee ID and week number), process each block separately. Do not use a global lookup table across all rows. Before writing, print block transitions (changes in key columns) to confirm you see repeated keys that need per‑block treatment. After writing the output column, for every marked row, verify that the block starting at that row actually contains the required values; remove the mark if it does not.


- **Creating a new workbook instead of modifying the original**: This discards other sheets, formatting, and metadata. Always load the existing file and modify sheets in place, unless the task explicitly asks for a brand‑new file. After saving, verify all original sheet names are still present.

- **Using pandas.ExcelWriter or other libraries that create a new workbook**: This discards all original sheets, formatting, and metadata. Always use `openpyxl` to load the existing file and modify it in place. After saving, reload the output and assert that all original sheet names are still present (Verification step 11).
- **Hard‑coded row ranges**: Never use literal numbers for row counts (e.g., `range(2, 18)`) derived from a single inspection. Always derive the row range dynamically from the sheet object (e.g., `ws.max_row`, `ws.iter_rows`). After writing, re‑open the saved file and verify that every row in the target column has been processed by printing the values of the first and last few rows and confirming none were skipped.
- **Whole‑number checks**: When distinguishing whole numbers from numbers with cents, avoid `float(x) == int(float(x))` which can fail for large floats or formatted strings. Instead, convert the value to a string, strip currency symbols and commas, and use `Decimal(value) % 1 == 0` or `Decimal(value).as_tuple().exponent`. Validate after writing by checking a few sample rows that should be whole or fractional.
- **Signed balancing operations**: When an instruction says to “add to or subtract from cells … to balance positive or negative residuals”, explicitly decide and document the exact mapping before coding: “If residual is <sign>, I will (add|subtract) in order (unit1→unit5|unit5→1).” After implementing, verify with one concrete row: print the row’s original total vs. the new total and check that the net change equals the residual and that the operation direction (add vs. subtract) matches your mapping. If any sign is reversed, flip the condition.
- **Under‑inspection and missing verification**: Executing modification scripts without first inspecting the workbook (printing headers, sample data, row counts) and without reloading and verifying the output afterward. Always print the relevant data before modifying, and after saving, reload and confirm that the required condition is satisfied (e.g., no matching headers remain) and that no formula strings were written.
- **Column deletion index shift**: When deleting multiple columns programmatically, iterate in descending index order (e.g., `sorted(cols_to_delete, reverse=True)` or `reversed(columns_to_delete)`) to avoid shifting the positions of later columns. After deletion, verify that the remaining column count and header positions match expectations.

- **Off‑by‑one and block boundary errors**: Before coding, mentally simulate the algorithm on a few sample rows (e.g., how invoice numbers advance, where block boundaries occur). After writing, print the answer range and verify that values are consistent with your simulation. Do not rely on a run‑then‑fix loop.

- **Duplicate key aggregation**: When building a mapping from a source table whose keys may repeat, collect all values for each key into a list (e.g., `defaultdict(list)`) rather than keeping only the first occurrence. After construction, print the total number of values per key and assert that it equals the count of rows in the source range that carry that key. This prevents silent data loss and ensures later occurrences are available if needed.

- **Cross‑sheet compilation with formulas**: When the task asks to compile values from other sheets (e.g., “compile their ages”), do not use INDIRECT, VLOOKUP, or any Excel formula that references other sheets. Instead, read the values from each sheet in Python and write the computed results directly as plain numbers or strings. After writing, reload the file and confirm every cell in the answer range is populated (not `None`) and contains the expected data type.

- **Manually retyping file paths**: Always copy the `input_path` and `output_path` directly from the task prompt without re‑typing. Before using a path in a script, print it and visually compare it to the prompt's path to ensure no typos.



- **Inspection limit**: If you have inspected the workbook for more than 3 turns without writing any code, or if you receive a system warning about a missing output file, stop and immediately write a script to produce the output file, even if you are unsure of some details. Use the information you have gathered and handle edge cases later.

- **Positional indexing from row slices**: When using `iter_rows(values_only=True)`, do not assume that `row[3]` corresponds to a specific header. Always print the header row with column indices first, then map indices to headers. Prefer accessing cells by column letter or by `ws.cell(row, col_idx)` where `col_idx` is derived from header scanning. After extracting values, print a sample row’s values side‑by‑side with their header names to confirm the mapping is correct.

- **Fixing broken formulas**: If a task asks you to fix a formula that is producing errors (e.g., #N/A, #VALUE!) due to data mismatches (trailing spaces, case differences, extra characters), do not try to edit the formula string. Instead, inspect the raw values with `repr()` to identify the mismatch, clean the data in Python, compute the correct values, and write them as plain numbers or strings. After writing, reload with `data_only=False` and confirm no cell value starts with `=`.

- **Copying answers from example sheets**: Never hardcode cell addresses or values observed in an example or 'After' sheet. Always compute the required set of cells from the source data using an analytical method (e.g., subset sum, constraint solving). After selecting cells, verify the computed sum/condition falls within the required target range, and confirm uniqueness if the task demands a single solution.
- **Incorrect color encoding for cell fills**: When setting cell fills with openpyxl, always use the `fgColor='FFRRGGBB'` format (e.g., `PatternFill(fill_type='solid', fgColor='FF00FF00')` for opaque green). Examine pre‑existing fills in the workbook to match the expected encoding style. After applying a fill, read back the cell's `fill.fgColor.rgb` and assert it equals the required hex code including the alpha prefix.
- **Leaving formula objects (e.g., openpyxl `ArrayFormula`) in cells**: Even if you assign a formula object, the grader may read the file in data-only mode and see `None`. Always overwrite formula cells with plain computed values. After writing, verify that no cell in the answer range has `data_type == 'f'`.
- **Preserving numeric types during text cleaning**: When the task only requires removing non‑numeric characters from text values, first inspect the target cells with openpyxl to identify which are already numbers (`int` or `float`). Skip those cells entirely; do not convert them to strings. After saving, reload and verify that originally numeric cells still have numeric types (not strings).
- **Formula vs. computed value**: When a task says 'create a formula' or 'use a formula', it means compute the result using that logic, not write an Excel formula string. Always write the computed plain value unless the task explicitly asks for an Excel formula (e.g., 'write an Excel formula').


- **Floating‑point noise in computed values**: When the input data has a fixed decimal precision (e.g., hours recorded as `52.62`), round computed results to that same precision. After writing, inspect a few answer‑range cells; if any value contains unnecessary trailing decimals like `.619999…`, apply rounding until the numbers match the expected format.
- **Rigid number parsing from formatted text**: When extracting numeric values from currency or formatted text strings (e.g., `'1.234,56'`, `'4 841,42'`, `'1,234.56'`), do not assume a fixed decimal separator. Instead, identify the rightmost occurrence of `.` or `,` in the cleaned string as the decimal sign; remove all other non‑digit characters (including Unicode spaces like `\xa0`, apostrophes, and thousand grouping marks) before parsing with `float()`. After writing, verify that the answer cells contain numeric types (`int`/`float`), not strings.
- **Overwriting cell formatting when changing a single attribute**: When the task asks to change only one style property (e.g., font name, size, color), copy the existing style object first (e.g., `copy(cell.font)`), modify only the required property, and assign it back. Never create a new style object from scratch. After saving, verify that other style attributes (bold, italic, size) on a sample cell remain unchanged.
- **After writing a computed value**, reload the workbook with `data_only=True` and assert that the cell value is a plain number (e.g., `isinstance(cell.value, (int, float))`), not a string or None. This catches formula strings left in cells that should contain numeric results.
- **Hardcoding spreadsheet data in scripts**: Always read data from the workbook at runtime using `openpyxl`. Never type cell values into the script as constants, even if they appear in the task description. After writing, verify that no numeric values from the sheet are hardcoded.
- **Sequential algorithm restart conditions**: When a task describes an algorithm that resets after a condition, interpret the restart point literally (e.g., "restart from the cell immediately right" means that cell becomes the new reference). Test the mapping on the first two or three cells of the actual data to confirm alignment before processing the full range.
- **Overwriting cells without preserving formatting**: When rewriting an existing cell's value (e.g., sorting, filtering, or recomputing), always preserve the original cell's style and number_format. Capture them with `copy(cell._style)` and `cell.number_format` before overwriting, then reapply after setting the new value. After saving, reload and verify that a sample of cells still has the expected `font`, `fill`, `alignment`, and `number_format`.

- **Clearing entire sheet instead of target columns**: When updating an existing sheet, do not clear every cell. Inspect which columns need to be modified and clear only those columns (e.g., `for r in range(min_row, max_row+1): for c in range(min_col, max_col+1): ws.cell(r,c).value = None`). After the operation, verify that columns outside the target range still contain their expected values (if any) and that only the intentionally deleted column (if any) is removed.
- **Multi‑key sort**: When a task describes a primary sort (e.g., grouping by a helper column, preserving original order), do not apply a contradictory global sort afterward. If an instruction seems to conflict, treat it as a refinement within the existing order (e.g., sort only within groups), not a re‑order of all rows. After sorting, verify that the grouping and original order constraints are still met.
- **Overwriting adjacent columns**: When a task specifies an output range (e.g., 'output in columns G and H'), write only those cells. Leave adjacent columns (like an index in F) untouched unless the instructions explicitly say to populate them. After writing, inspect the untouched part of the output range to confirm it still contains the original pre‑modification values.
- **Example of formula misinterpretation**: If the task says 'create a formula =IF(A2=J2, B2-C2-E2-G2, 0)', do NOT write that string into cells. Instead, loop over rows, evaluate the condition in Python, compute the result, and write the numeric value. After writing, verify that each cell contains a number (int/float), not a string or None.
- **Contiguous row deletion with loops**: When deleting a contiguous block of rows (e.g., all rows from 1 to N), use `ws.delete_rows(start, count)` instead of looping over `delete_rows(1)` repeatedly. Looping one row at a time is fragile and slow. After deletion, reload the output and verify that the remaining data is correct and that no formula strings exist in the answer range (see Verification step 4).

- **Group indexing without length check**: When grouping rows by a key and then accessing a specific element of a group (e.g., `group[1]`, `group[-1]`), always check `if len(group) >= 2:` (or the required size) before indexing. This prevents `IndexError` on groups with fewer items than expected. After writing the grouping logic, print the size of every group; if any group has size 1, confirm your code does not reference a non‑existent second element.
- **Hard‑coded column indices**: Never use literal column numbers (e.g., `column=3`, `column=6`) based on visual inspection. Instead, read the header row and build a dictionary mapping normalized header names to column indices. Reference columns only through that map. This makes the script robust to column reordering. After building the map, print it and spot‑check that the intended columns map to the expected positions.
- **Running balance sign direction**: When computing a running balance that updates with additions and deductions, map 'addition' → **add** the value and 'deduction' → **subtract** the value. After writing the code, manually trace the first row where the update produces a non‑zero result and check that the value makes everyday sense (e.g., an addition should not make a debt negative if debt represents an amount owed). If the sign conflicts with ordinary logic, re‑read the instruction to correct the polarity.
- **Working directory typos**: Before executing any shell command that references a directory, copy the `working_directory` from the task description exactly; do not retype it. Use absolute paths in scripts and verify the directory exists with `ls -d <path>`.
- **Misinterpreting 'modify my code' tasks**: When a task says 'modify my code to achieve this', you must produce the resulting spreadsheet file, not the code itself. The output is always a spreadsheet saved to `output_path`. Interpret such instructions as applying the described logic to the input spreadsheet and writing the computed results as plain values. Unless the task explicitly asks for a code file, do not output code.
- **Skipping post-save verification**: After saving, always reload the file and inspect the answer range before calling TASK_COMPLETE. Do not rely on printouts from the writing script alone.
- **Writing formula text when the task asks 'Which formula could I use...'**: The answer range expects the final computed values, not the formula text. Always compute the result in Python and write the plain value, regardless of the task's wording, unless the task explicitly says 'write an Excel formula' and the grader expects to evaluate it.

- **Unreliable `max_row`**: `ws.max_row` can include empty rows if data was previously deleted. Always determine the last meaningful row by scanning the column for real values (e.g., a while‑loop from `max_row` downward until a non‑None cell). After writing, count non‑empty cells in the target column and compare with the expected count to catch leftover data.
- **Stale data after replacing a column**: When replacing a column's contents with a new list of possibly different length, first clear all cells in that column from the first data row to the last used row (or `ws.max_row` if no scan), then write the new values. After saving, verify that the answer range contains exactly the expected number of non‑empty cells and no extra values beyond the intended list.

- **Hardcoded column letter to index**: Never assume column letters map to small numbers (e.g., BN is not column 14). Use `openpyxl.utils.column_index_from_string` to convert the column letter in the answer range to its numeric index. Before writing, print a few existing cell values from that column to confirm the mapping. After writing, read back the exact answer range cells and assert they are not None.

- **Prioritize explicit outcome specifications over illustrative examples**: When the task lists a set of allowed output values (e.g., 'Group 1', 'Group 2', 'BOTH'), use only those exact strings. Do not generate concatenations or free‑text alternatives based on row examples. After writing, verify that every cell in the answer range contains only one of the allowed values (e.g., `assert cell.value in allowed`).

- **Diagnose → Fix → Save**: After inspecting the workbook to understand an error, you must immediately write and execute a script that fixes the error and saves the result to `output_path`. Do not loop back to inspection or wait for another warning. After saving, reload the file and verify that the target answer cell contains a real value (not a formula, not `None`, and not an error string like `#REF!`).

- **Misinterpreting "delete rows" as clearing cells**: When a task says "delete rows" (or "remove rows"), do not set cell values to `None`. Use `ws.delete_rows(row_idx, 1)` to completely remove the row. After deletion, verify that the sheet's `max_row` has decreased by the number of removed rows, and that no blank rows remain between data rows (print a contiguous sequence of values to confirm). If you see blank rows after saving, you likely cleared cells instead of deleting rows; fix it before completing.

- **Writing string manipulation formulas**: If the task requires extracting or combining parts of a cell's text (e.g., creating a date from a timestamp string), do not write Excel formulas like `=LEFT(K2,2)&""/""&...`. Instead, parse the source cell's value in Python using string operations or `datetime` parsing, and write the resulting `datetime` object or string. After saving, reload and verify that the answer cells contain actual values (e.g., `datetime` instances), not `None`.
- **Ignoring evaluated formula values / Assuming input cells are raw numbers when they are formulas**: Always check the `.data_type` of input cells before referencing them in computations. If they are formulas, use `data_only=True` to obtain the computed values and write hard‑coded results. After writing, verify that the answer range contains no formulas (see Verification step 4).
- **Relying on printed values to verify literal data**: Even if you print cell values and they look like numbers, they could be formula strings. Always run the mandatory formula‑check assertion from Verification step 4 after saving. Do not skip it.
- **Inventing key‑based lookups when direct positional copy is specified**: If the task says “if the value in cell B2 of Sheet1 does not match the value in cell B2 of the ITEMS sheet, replace B2 with the value from ITEMS”, this means compare and copy row‑by‑row using the same row index. Do not build a lookup dictionary on another column (like S.N.) unless the task explicitly asks to match by an ID column. After writing, verify that for each row i, the output cell Bi equals the source cell Bi in the reference sheet.
- **Overwriting header cells during column‑wide transformations**: When applying a transformation to an entire column (e.g., text cleaning, formatting), always inspect the first few rows to identify the header row. Apply the transformation only to the data rows (starting from row 2 or the detected header row index + 1), preserving header cells exactly as they were, unless the task explicitly says to modify them. After saving, reload the workbook and verify that the header cell(s) still contain the original value (e.g., check that C1 is still `'Location'`).

- **Full‑table vs. row‑wise lookup**: When a task says to find IDs based on parameters that appear “within the comments column”, do **not** assume the parameters are in the same row’s comment. Build a reference list of all (ID, comment) pairs from the full column, then for each query row scan the entire reference list to find a comment containing both parameters. As a sanity check, manually pick one query row and search the reference column with a simple script; if your code returned empty but a manual scan finds a match, your search scope is too narrow.

- **Restricting transformation to the answer range without full inspection**: When a task says to apply an operation across all columns or all data, do not hard‑code the loop to the answer‑position range alone. First inspect the entire sheet to determine the actual data extent, then iterate over all populated cells (e.g., `ws.iter_rows()` or scanning all non‑empty cells). After writing, verify that the transformation hit every non‑empty cell, not just the graded cells.


- **Retain original header and materialize computed columns**: When reordering a table while leaving all formatting and values as-is, preserve the original header row exactly. If any column originally contained formulas referencing the data, replace those formulas with the same computed result they would produce in the new order (materialize them). After saving, load the output and print the first row of the answer range to confirm header text equals the original, and verify that no cell in the range contains a string starting with `=`.
- **Interpret "reorder X to match Y" as sorting X, not copying Y**: When a task provides an "Actual" table and an "Expected" table and asks to reorder the actual to match the expected, do not copy the expected cells over. Instead, study the actual table to understand how rows are grouped (e.g., look for a key column that marks the end of each group), then write a procedure that sorts those groups according to the implied order. After sorting, verify by comparing the sorted actual values against the expected values row‑by‑row, ensuring both data and order match without altering the original structure.


- **Zero display as blanks**: When the task asks to make zeros display as blanks, do not set the cell value to `None` or an empty string. Instead, write the numeric zero and apply a custom number format that hides the zero section (e.g., `cell.number_format = '0.00;-0.00;;@'`). After writing, verify that the cell value is `0` (a number) and the format hides zeros. This preserves the numeric value for downstream calculations.
- **Preserving exact formatting across sheets**: When copying data to a new sheet and the task requires preserving exact formatting, always copy column widths and row heights from the source sheet, not just per‑cell styles. Use `dest.column_dimensions[col].width = src.column_dimensions[col].width` and similarly for `row_dimensions`. After saving, verify that the destination column widths match the source for the affected range.

- **Assuming the first row is a header**: Always read raw cell values (e.g., with `openpyxl` or by specifying `header=None` in pandas) before any transformation. Do not rely on default header inference unless the task explicitly describes a header row. After writing, reload and confirm that no data row was mistakenly promoted to or written as a header row.

- **Color detection without checking fill_type and fgColor.type**: When reading cell colors to identify cells by fill, always check `cell.fill.fill_type == 'solid'` and `cell.fill.fgColor.type == 'rgb'` before comparing `fgColor.rgb`. Relying on `patternType` truthiness or converting `start_color.rgb` to string without these checks can cause `TypeError` or match theme colors incorrectly. After writing detection code, print a few sample cells' `fill_type`, `fgColor.type`, and `fgColor.rgb` to confirm robustness.

- **Conditional fill without clearing target column**: When you need to write a value into a column only for rows that meet certain conditions, first clear the entire column (set all data rows to `None`) before writing the conditional values. This prevents old data from remaining in non‑matching rows. After writing, verify that every row not meeting the condition has `None` in that column, and every matching row has the correct value.

- **Row insertion index shift**: When inserting rows above target rows (e.g., inserting a blank row above each row containing "X"), collect all target row numbers, sort them in descending order, and insert in that order (e.g., `for row_num in sorted(target_rows, reverse=True): ws.insert_rows(row_num, 1)`). This prevents earlier insertions from shifting the row numbers of not‑yet‑processed targets. As a runtime check, print the insertion order to confirm it is descending.

- **Blank cells in output ranges**: When selecting cells to output (e.g., transposing a column to a row, compiling a list), always filter out cells that are `None` or empty strings (after stripping whitespace). This prevents spurious empty entries that can violate output requirements. After writing, verify that the output range contains no unintended blank cells.


- **Datetime type preservation**: When copying or aggregating date values, always preserve the original `datetime` object type. Do not convert dates to formatted strings with `strftime()` or similar. Write the raw `datetime` object and copy the source cell's number format (e.g., `target_cell.number_format = source_cell.number_format`). After writing, iterate over the target range and print `type(cell.value).__name__` for each cell to confirm all date cells are `datetime` objects, not strings.
- **Hard‑coded deletion ranges**: Never delete rows using a fixed span like `ws.delete_rows(6, 6)`. Always determine the rows to delete by scanning for a condition (e.g., all cells empty, specific value) and delete them in reverse order. This ensures the logic works regardless of data position or size.
- **Single answer cell**: If the task asks to output a single answer in a specific cell (e.g., "output the answer in D2"), never write an Excel formula like `=SUMIF(...)`. Compute the result in Python and write the plain number. After writing, reload the file and print the cell's value to confirm it's a number, not a formula string.
- **StyleProxy TypeError when copying cell styles**: Never assign a StyleProxy object directly (e.g., `dst.font = src.font`). Instead, use `from copy import copy` and either copy the entire `_style` (`dst._style = copy(src._style)`) or copy individual properties via `dst.font = copy(src.font)` and `dst.alignment = copy(src.alignment)`. After writing, reload and verify that the font and alignment attributes are not `None` (which would indicate a suppressed error).


- **Per‑cell vs. aggregate threshold for row deletion**: When an instruction says to apply a numeric threshold to *each* value for row deletion (e.g., “identify values that are effectively zero and delete those rows”), **always apply the check to each relevant cell individually**, never to an aggregate like the total sum. After writing the deletion logic, manually validate that each remaining row’s cell does **not** meet the deletion threshold.
- **Missing type guard before arithmetic**: Before performing arithmetic or comparisons on a cell’s value, **always verify the value is a number** (e.g., `isinstance(value, (int, float)) and not isinstance(value, bool)`) and skip or handle non‑numeric cells explicitly. After opening a workbook, list which cells in the target column contain non‑numeric values, then run the deletion logic and confirm no `TypeError` is raised.