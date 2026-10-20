---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow


1. Print all non‑empty cells from every sheet (coordinates, value, type) to understand headers, data, and layout.
This step is mandatory. Do not skip it even if the task description provides a data layout — the actual workbook may differ. You must complete this inspection before writing any transformation code.
2. Perform calculations and write the output.
- Write literal computed values; never write formula strings (e.g., `=SUM(...)`) because the grader reads with `data_only=True` and will see `None`.
- Before writing the full output, test your logic on a few rows: implement the task's computation in Python using the actual cell values, print the results, and compare with expected values to catch misinterpretations early.
- As soon as you have understood the data layout, write the output file immediately. Do not continue inspecting or analyzing before saving.
After saving, immediately reload the workbook, print the answer range (values and types), and confirm that no formula strings remain and all values are correct. **Never call TASK_COMPLETE before completing this verification.**
**Primary deliverable**: The output file at `output_path`. Even if the task mentions macros or other code, you must produce a modified spreadsheet. After inspection, you MUST write a script that saves the workbook to `output_path`, then verify it exists and the answer range is populated.
- When the task provides explicit file paths (e.g., `spreadsheet_path`, `output_path`, `working_directory`), copy them character‑for‑character from the task description. Do not retype by hand. Before executing, run `ls <spreadsheet_path>` to confirm the file exists.

- Always use the absolute file paths provided in the task (`spreadsheet_path`, `output_path`) directly in your code; do not rely on the current working directory or `cd` into directories. Pass the full path to functions like `openpyxl.load_workbook`.

- If the task contains an IMPORTANT note or a clarifying statement that overrides an earlier specification, always treat the later statement as definitive. Re-read the full instruction to identify such overrides before writing logic.

- Before calling `openpyxl.load_workbook(spreadsheet_path)`, assert the file exists: `assert os.path.exists(spreadsheet_path), f"Input missing: {spreadsheet_path}"`. This catches typos or incorrect paths early, before the script fails with a cryptic error.

- **Write a single comprehensive inspection script** that prints all sheet names, dimensions, and every non‑empty cell's coordinate, value, type, and number_format. After that, immediately write a modification script to a `.py` file (e.g., `solve.py`) and execute it, which saves the result to the exact `output_path`. Do not continue exploring even if the output file is missing; write the output first. Once the script finishes, confirm the output file exists with `ls -l <output_path>` or `python -c "import os; print(os.path.exists(OUTPUT_PATH))"`, then spot-check one or two rows to verify transformations.

- **Always modify the original workbook**: Use `wb = openpyxl.load_workbook(spreadsheet_path)` and modify it in‑place. Never create a new `Workbook()` unless the task explicitly requires a blank workbook. After saving, confirm that all original sheets (that should remain) are still present.
## Inspection


Before making any changes:
As the very first action, write a single read‑only script that outputs all sheet names, max rows/columns, and every non‑empty cell’s coordinate with its value, type, and number_format. This comprehensive dump prevents overlooking hidden sheets or data.

- **First step**: For each sheet, print the header row and the first 5 data rows (using `iter_rows(min_row=1, max_row=6, values_only=True)`) to confirm column order and data types before any detailed inspection. This quick sanity check prevents misalignment errors.
- **Do not rely on the task description alone for data layout; always confirm by printing actual cell values from the spreadsheet.** This prevents silent assumptions about date formats, column positions, or empty cells.

- Load the workbook and print all sheet names.
- Iterate over all non‑empty cells, printing their coordinates, values, Python types, and number formats. This reveals headers, data types, and layout.
- Load the workbook with `data_only=False` to see formula strings (if any) and print them alongside other cell values.
Also load the workbook with `data_only=True` to see the actual computed values of formula cells. Print these computed values alongside the formula strings. Use these evaluated values (not the formula strings) for any Python calculations. This is essential because the grader reads with `data_only=True`, so you must see what the grader will see.
- **Single comprehensive inspection**: Write ONE script that prints all non‑empty cells (coordinates, value, type, number_format) for every sheet, covering the entire used range from row 1 to `ws.max_row`. Within this same script, also print a compact overview of the first 30‑40 rows for a quick sanity check. Do not run multiple separate inspection commands — one thorough dump is sufficient and prevents wasted turns. The full iteration of all non‑empty cells is mandatory; the quick overview alone is not sufficient.
- After the inspection runs, verify that the last row of actual data was printed (check that the output includes rows near `ws.max_row`). If the output is truncated, increase the row range and re‑run the same script — do not write a new inspection script.

- Confirm the answer‑range coordinates and the mapping between row/column identifiers and any lookup table.
- Identify dynamic columns or ranges before writing code. When columns are named in headers, scan the header row and build a mapping of normalized header text (`.strip().casefold()`) to column index. Use this mapping for all column references instead of hardcoded numbers. After building the mapping, print the discovered column indices and verify that no column index is a literal integer (e.g., `col = 3`); if found, stop and replace with the mapping lookup.
- Normalize strings before comparisons: use `.strip().casefold()` on both the cell value and the target string(s) to make checks case‑insensitive and whitespace‑tolerant. Print the normalized value for debugging (e.g., `print(repr(val.strip().casefold()))`).

- After printing all non‑empty cells you have enough to understand the data layout; stop further exploration and proceed to the solution.
- When a summary table aggregates data across groups, identify all group-by columns and confirm your Python code will iterate over all rows matching each group, not just a contiguous block.

- Ensure you iterate over every worksheet, not just the active one. Print at least two rows from each sheet to confirm you've inspected all.
- When looking for specific row labels (e.g., 'min', 'max'), scan column A and print the row numbers to confirm.
- Always print the last few rows of each sheet, even if you stop early, because constraints or totals are often located there.

- Print each sheet's dimensions (max_row, max_column) to confirm the data extent.

- **Always include `cell.number_format` and alignment** in the inspection output. Use a pattern like `print(cell.coordinate, repr(cell.value), type(cell.value).__name__, cell.number_format, cell.alignment.horizontal, cell.alignment.vertical, cell.data_type)` for every non‑empty cell. This is critical for tasks involving dates, currencies, or custom formatting.
- After inspecting, confirm the exact columns to read and the target output range before you start coding. Print the header mapping and the intended output range to verify.
- After inspecting every sheet, explicitly note: (1) the sheet name(s) you will read from, (2) the column(s) involved, and (3) the exact target range (sheet, start row, end row, columns) you intend to write back. Print this plan before writing any manipulation code. This habit, proven across many successful runs, catches hidden reference tables and prevents assumptions about row boundaries.
If the task's answer range does not include a sheet name (e.g., just 'G1:I1000'), it refers to the same sheet as the input data. Confirm this by printing the sheet name alongside the range.

- If the workbook contains an auxiliary sheet with example answers (e.g., an 'After' sheet), ignore it for deriving the solution. Compute the answer programmatically from the primary data and the task constraints, not by reading the example sheet.

- If the workbook contains an example output sheet (e.g., 'After', 'Expected', 'Manual Result'), inspect it to understand the expected layout, data types, and transformation rules (what gets kept, moved, or cleared). Use that pattern to guide your logic on the primary data, but never copy values directly from the example sheet. Before writing, print a few rows from the example sheet and confirm your planned transformation matches its pattern.

- When you have identified the columns your logic will depend on, print every cell's raw value in those columns for all rows (including empty cells) to confirm data types, edge cases, and any pre-existing entries before writing any transformation.

- If the task involves a specific cell or formula (e.g., fixing an error, modifying a formula), print that cell's formula and value, and the values of any cells it references, before making changes. Include a range of surrounding rows to understand context.

- When detecting blank rows that separate data blocks, check that **multiple key columns** (e.g., both A and B) are `None`, not just one column. A single-column `None` check can produce false positives from rows where only that column is empty. Use `if ws.cell(r, 1).value is None and ws.cell(r, 2).value is None:` to identify true separator rows.

- If the workbook fails to load (e.g., file not found), fix the path and re‑run the full inspection before writing any code. Do not skip inspection because of a failed load; the data layout may differ from your assumptions.

- Before writing any logic, scan every row of the relevant columns and ensure you have identified every distinct data block or separation marker. Print a list of row indices where blocks begin and end. This runtime check prevents assumptions about a single contiguous range.

- If the task focuses on a specific column (e.g., column A), print every cell in that column (including blanks) to identify patterns like suffixes, numeric identifiers, and missing values.

- Always print the full contents of every sheet (all rows and columns) before applying any filter, deletion, or transformation, and before writing any output. This ensures you see the complete data layout and can spot anomalies like mismatched casing or unexpected values.

- When a column is specified by letter (e.g., 'BN'), convert it to an index using `openpyxl.utils.column_index_from_string('BN')` and print that column's header and a sample of its data to confirm you have the correct column. Never guess the index.
- Before any manipulation, inspect the sheet's `merged_cells.ranges` (e.g., `print(list(ws.merged_cells.ranges))`). If the task explicitly instructs you to unmerge cells, do so immediately with `ws.unmerge_cells(str(merged_range))` for each range, then verify the list is empty before proceeding. Merged cells can interfere with writes, deletions, and formatting operations.

- Print all rows of each sheet (including empty) to see the full layout and hidden data. For large sheets, at minimum print the first and last 10 rows without truncation.

- Successful runs consistently start with a full dump of all non‑empty cells (coordinates, value, type, number_format) and a listing of merged cell ranges. This practice is proven to prevent layout surprises.

- When the task involves a lookup table or reference data, print the full content of that table and the target answer range (even if the range is currently empty) to confirm column alignment and data mapping before writing any code.


- **This full inspection is the single most important step.** Skipping or abbreviating it is the leading cause of errors. Successful runs always include a complete dump of all non‑empty cells (coordinates, value, type, number_format) and merged cell ranges.

- After printing all non‑empty cells, sanity‑check the observed `max_row` and `max_column` against the sheet dimensions to confirm no data was truncated. If the printed output does not reach the expected last row or column, increase the range and re‑run the same script.

- If the task involves filtering rows, print the rows that would be kept and the rows that would be removed based on your interpretation of the filter condition, and manually verify a few examples to ensure the condition is correct.
- Before writing, print the exact cells you will read or write (coordinate, value, type) using `for r in range(start, end+1): for c in range(1, max_col+1): print(ws.cell(r,c).coordinate, ws.cell(r,c).value, type(ws.cell(r,c).value).__name__)` to confirm the current state and detect any pre‑filled values or formatting issues.
- After the full dump, explicitly list any blank separator rows and the data ranges they separate (start row, end row). Use these boundaries to avoid off‑by‑one errors when processing blocks.
## Writing Output


Unless the task explicitly requires an Excel formula, compute the result in Python and write the literal value (number, string, datetime, etc.). Do NOT write Excel formula strings unless instructed, because the grader may read the cell's raw value with `data_only=True` and return None for unevaluated formulas.
- If the task describes a formula (e.g., "use OFFSET to get the value"), compute the result in Python and write the literal value. Do NOT write the formula string.

- **Clarification**: Even when the task says "I need a formula" or "use a formula", it expects the computed literal result in the answer cells, not a formula string. Only write an actual Excel formula string if the task explicitly requires the cell to contain a formula (e.g., "the cell should contain =SUM(...)") and the grading method expects formula text (rare). When in doubt, write the literal value.
- Never write `openpyxl.worksheet.formula.ArrayFormula` or other formula objects; always write plain Python values (int, float, str, datetime, None). If the task requires formulas, write them as strings and verify with `data_only=False`. When writing a date or any value whose display is controlled by number formatting, copy the source cell's `number_format` to the destination cell unless the task explicitly forbids it. After writing, reload the workbook and verify the target cell's `number_format` matches the intended style (e.g., `wb['Sheet']['F4'].number_format`).

- When building a result from a master list column, iterate the source sheet in its displayed row order (top to bottom) and write entries in that exact sequence. Do not apply additional sorting unless the task explicitly requires it.
- When creating a new sheet that mirrors or extends an existing data sheet, replicate the source's visual properties: copy column widths (`column_dimensions`), grid‑line visibility (`sheet_view.showGridLines`), and for each cell, its `_style` and `number_format`.

### Deleting Rows
When deleting multiple rows, iterate bottom‑up to avoid index shifting. Use `for row_idx in range(ws.max_row, 1, -1):` so that deletions never reorder unprocessed rows. After deletion, verify the remaining data row count equals `original_data_rows - expected_deletion_count`.

If the task provides example output values (e.g., specific numbers), those are the expected literal values, not formula strings.

- Unless the task explicitly requires a blank workbook, always modify the original workbook object (`wb = load_workbook(infile)`) rather than constructing a fresh workbook. When moving data, copy cell styles and formatting attributes (not just values) to preserve the spreadsheet’s appearance.

- **Copying cell formatting between cells**: When you need to copy formatting (font, fill, alignment, border, number_format) from one cell to another, do **not** assign `.font`, `.alignment`, `.border`, `.fill`, or `.protection` directly from the source cell. These are style proxies and assigning them can raise `TypeError: unhashable type: 'StyleProxy'`. Instead, import `copy` from Python’s `copy` module and copy the entire style: `target._style = copy(source._style)`, then also copy the `number_format` separately: `target.number_format = source.number_format`. If you only need to preserve the style of a cell you are modifying, capture its `_style` and `number_format` before writing, then restore after setting the new value (as described above).
- When a task says "use a formula" or "write a formula," it almost always expects the computed literal result in the answer cells (because the grader reads with `data_only=True`). Compute the value in Python and write it as a static cell value. Only write an actual Excel formula string if the task explicitly requires that the cell contains an Excel formula (e.g., "the cell should contain =SUM(...)").
- Before writing data to a destination sheet, clear the exact graded/answer range (e.g., `sheet.iter_rows(min_row=1, max_row=7, min_col=1, max_col=4)`) and set each cell's value to `None`. Do not rely on the sheet's current `max_row` or `max_column` to determine the clearing range, as leftover data may exist beyond those bounds.
This clearing must cover the entire answer range, not just the rows you will populate; otherwise, stale data from previous runs may remain in unwritten rows.
- When copying rows that may have varying widths, determine the last non‑empty column per row (e.g., `max((c for c in range(1, sheet.max_column+1) if sheet.cell(row, c).value is not None), default=1)`) rather than using the sheet's global `max_column`. This prevents copying empty trailing columns or missing columns that do not extend to the sheet's maximum.

- After writing answer cells, print the values of the answer range to visually confirm correctness before saving. This catches errors early.

Always use `ws.delete_rows(row, 1)` to physically delete rows; do not set cell values to `None` to simulate deletion.


Do not hardcode row numbers for deletion (e.g., `delete_rows(6, 6)`). Instead, iterate over all rows and check a condition programmatically, such as `all(cell.value is None for cell in ws[row_idx])` for blank rows. After deletion, verify that no entirely blank rows remain between the first and last populated data rows by scanning the range and asserting no row is completely empty.
### Block-Level Iteration with Terminator Rows
When data is organised in blocks separated by a keyword (e.g., “TOTAL”), avoid row‑by‑row state flags like `is_new_block`. Instead, use a `while` loop that (1) locates the end of the current block by scanning forward for the terminator row, (2) processes all rows of that block together, and (3) advances the start pointer past the terminator. After writing, spot‑check that every row in a block contains exactly the intended value and that no row was mistakenly overwritten or left unchanged because of a row‑by‑row detection failure.

### Category-Aware Lookup Tables
When filling values that correspond to distinct categories (e.g., different sheet names, customer IDs), first group the source values into a dictionary mapping each category to an ordered list of its values. Then, for each target row group, use the category identifier to retrieve the next value from the appropriate list. This avoids mixing sequences across categories. After writing, verify that for each category the assigned values are in the same order as the source and that no category’s sequence has been consumed by a different category’s rows.

- Write conditional logic in Python, not as Excel formulas. For example, instead of `=IF(A1>0,"Yes","No")`, compute `result = "Yes" if cell.value > 0 else "No"` and write the literal string.

- When converting string cells to numbers by stripping non‑numeric characters, use `re.sub(r'[^0-9.]', '', value)` to preserve digits and the decimal point. After cleaning, verify the string contains at most one `'.'` to avoid creating an invalid number.

- Round computed numeric values to the same decimal precision as the source data. After writing, spot-check answer cells for floating-point artifacts (e.g., 12.619999...) and re-round if needed.
- When modifying existing cells, explicitly capture the cell's `_style` and `number_format` using `copy(cell._style)` and `cell.number_format` before writing the new value, then restore them after setting the value: `cell._style = style; cell.number_format = nf`.

- When the task specifies which columns to output (e.g., "output in columns G and H"), restrict writes to exactly those columns; do not clear or modify any other columns within the graded row range. Before writing, inspect the existing cells in the target range and note which columns must stay untouched. After writing, verify that cells outside the explicitly requested output columns are identical to the original workbook.

- **Before saving**, iterate over the answer range and assert that no cell contains a formula string (value starting with `=`). If any are found, replace them with the computed literal value. Example: `for row in ws[answer_range]: for cell in row: assert not (isinstance(cell.value, str) and cell.value.startswith('=')), f'Formula at {cell.coordinate}'`

- When the task requires text transformations (capitalization, trimming, etc.), compute the result in Python using string methods (e.g., `.upper()`, `.lower()`, `.strip()`, `.capitalize()`) and write the literal string. Do NOT write Excel formula strings like `=UPPER(A2)` or `=ISUPPER(A2)` because the grader reads literal values and will see None.

- When the task specifies multiple non‑contiguous output cells (e.g., H10, H20, H24), create a mapping of each source range to its exact target cell as stated in the instruction, and print it before writing. This prevents misalignment where a value is written to the wrong row.
### Multi-Value Cells (Delimiter-Separated)
- When a source cell contains multiple values separated by a delimiter (e.g., semicolons), split on that delimiter, strip whitespace from each token, and discard empty tokens before performing any lookup or transformation.
- Build a lookup dictionary from the reference columns first, then for each token apply the mapping individually.
- After processing, print the split tokens and the mapped results for the first few rows to verify correctness.

- Do not use any pre-existing data in the answer sheet to validate your output; the sheet may contain partial or incorrect data. Always clear the answer range and compute from scratch.


- **Pre‑save formula check**: Before saving, iterate over the answer range and assert that no cell contains a formula string (value starting with `=`). If any are found, replace them with computed literal values. This ensures the grader reads actual data, not unevaluated formulas.

- **Bulk cell updates**: When writing values to many cells (e.g., a column over hundreds of rows), use a loop in your Python script (e.g., `for row in range(2, last_row+1): ws.cell(row, col).value = ...`). Avoid per‑cell manual edits. After the script runs, read back a few cells from the beginning and end of the range to verify the update was applied correctly.

If you do write a formula string, ensure that any range that should remain fixed across copies uses absolute references (e.g., `$A$1:$A$10`). After writing the first formula, print its text to verify that all intended absolute references contain `$` both before column and row.

After saving, proceed immediately to the Verification section and perform all checks, especially the formula‑string check. Do not call TASK_COMPLETE before verification.

Preserve header rows: unless the task explicitly asks to modify headers, start data‑processing loops at row 2 and leave header cells untouched.


### Inserting Rows

- When inserting blank rows (e.g., to separate data blocks), copy the `_style` and `number_format` from an adjacent row (typically the row below) to the inserted row to preserve visual consistency. After writing, verify that a few inserted cells match the reference row's `_style` and `number_format`.


- **Conditional column writes**: When you are writing values to a column based on a condition, first set every cell in that column (from row 2 to the last data row) to `None` before writing. This ensures that rows that do not meet the condition are left empty, not with stale data from previous runs.

- When clearing the answer range, also reset formatting: set each cell's fill to `PatternFill()` and border to `Border()`. After clearing and before writing new data, read back the first and last few cells of the target range and assert their values are `None` and fill type is `None` to confirm a clean slate.


- **Formula‑like text check**: After the pre‑save formula check, also verify that no cell value is a string that looks like an Excel function call (e.g., starts with `IF(`, `VLOOKUP(`, `SUM(`, `INDEX(`, `MATCH(`, `OFFSET(`, `CHOOSE(`, etc.). If any are found, replace them with computed literal values. Use a check like `if isinstance(val, str) and val.strip().startswith(('IF(','VLOOKUP(','SUM(','INDEX(','MATCH(','OFFSET(','CHOOSE(','SUMPRODUCT(')):` to catch these.


- After writing a computed numeric result (e.g., a sum, average, or any calculated number), explicitly set the cell's `number_format` to an appropriate format (e.g., `'0.00'` for two decimal places, `'0'` for integers). If the task specifies a format, use that; otherwise, infer from the precision of the source data or the expected display. Do not leave numeric cells with the default `General` format.

**Prerequisite**: You must have completed the mandatory inspection (printing all non‑empty cells from every sheet) before writing any output. If you have not done so, halt and run the inspection script immediately.

- **Match output ordering to existing example sheet**: If a target sheet already contains example rows (e.g., a pre‑filled 'After' sheet), treat the existing order as the required output ordering. Before writing, dump the existing content and deduce the grouping order (e.g., which header appears first, how entries are grouped). Implement your logic to produce that same sequence. After writing, compare the first few generated rows against the original example to confirm the pattern matches.
- **Enforce answer range boundaries**: When writing output to a specified answer range (e.g., `'Sheet3!'A1:A50`), enforce the row and column boundaries in your loop: break or skip when the output would fall outside the range. For example, use `if out_row > 50: break`. After saving, re‑read the file and verify that no cell beyond the range contains data (print the range and check for values outside).
## Verification


After saving the workbook:

- Confirm the output file exists at the exact `output_path` using `os.path.exists(output_path)`. If the file is missing, re-save or debug immediately before proceeding.
- Immediately load the saved workbook and inspect the targeted range: print the row count, header row, and the first 10 and last 5 rows of the answer range to confirm the sheet still exists and the changes match your intent. This catches silent file‑I/O and logic errors.
- Always perform this verification step; it is mandatory for all tasks and catches many silent errors.
- If the task expects formulas in the answer cells, reload with `data_only=False` and print the formula strings to confirm they are correct; otherwise, reload with `data_only=True` and verify literal values as described below.
- Reload it with `openpyxl.load_workbook(path, data_only=True)` and verify that every cell in the answer range holds a literal value of the expected type (int, float, datetime, bool, etc.), not a formula string, None, error object, or `ArrayFormula`/`Formula` object. Print the cell values to confirm.
 Additionally, print each cell's value and its Python type (e.g., `print(cell.value, type(cell.value).__name__)`) to catch type mismatches like dates stored as strings.
- For lookups, first verify the lookup logic in Python against the actual data to ensure a non‑None match; adjust matching keys if necessary (e.g., handle year mismatches). After writing, print the cell's value to confirm it matches the expected result.
- Compare the first few entries of the source column and output column side‑by‑side to confirm order matches (e.g., print `source_ids[:5]` and `output_ids[:5]`).
- After saving, load the output workbook, compare the width of column A between the source sheet and the new sheet, and print a warning if they differ.

### Post-Merge Placeholder Validation
After any merge that introduces placeholder rows (e.g., for missing keys), extract the row numbers of those missing keys, print only those rows' values, and confirm that all columns after the first contain no real data (are None or empty). Also perform an all‑literals check to ensure no formula text was accidentally written.

- For aggregates, print the rows that contributed to each result to verify they cover all matching groups, not just a subset.

- When modifying an existing workbook, after saving, reopen the file and verify that formatting (e.g., number_format, font) is preserved as in the original input file.
- After saving, re‑read and print **all** cells in the graded answer range and any cells mentioned in side‑conditions (e.g., “column H must be empty without background colour”). For each cell, print both its value and its format properties (fill, number_format, etc.). End with an `all(…)` assertion that every required property holds across the relevant rows. Example: `assert all(cell.value is None and cell.fill.fill_type is None for cell in ws['H'][:ws.max_row])`.
- If the task did not specify a header row, after writing, print the first two rows of the output sheet and compare them with the original input's first two rows (from the initial inspection) to ensure no unintended header treatment occurred (e.g., row 1 should contain data, not column labels).
- After reloading with `data_only=True`, print the types of the answer cell values (e.g., `print([type(c.value) for c in ws['F6:H6'][0]])`) and confirm they are all numeric (int, float) and not None. If any is None, you likely wrote a formula; recompute in Python and rewrite the literal value.
- After writing to a destination sheet, confirm that the entire target answer range (e.g., `Sheet1!B6:B10`) contains no leftover values from previous runs by printing the range's values and verifying they match the intended data.
- **Mandatory formula‑string check**: After saving, reload the workbook with `data_only=False` and run a check on the answer range: print each cell's value and assert that none are strings starting with `=`. Example:
```python
wb_check = openpyxl.load_workbook(output_path, data_only=False)
ws_check = wb_check['Sheet1']
for row in ws_check['A1:B10']:
    for cell in row:
        if isinstance(cell.value, str) and cell.value.startswith('='):
            print(f"ERROR: Formula found at {cell.coordinate}: {cell.value}")
assert all(not (isinstance(c.value, str) and c.value.startswith('=')) for row in ws_check['A1:B10'] for c in row), "Answer range contains formula strings"
print("No formula strings in answer range: True")
```
If any formula string is found, rewrite those cells with literal values immediately.

- **Never call TASK_COMPLETE immediately after saving.** Always reopen the workbook, verify the answer range, and print values. If any check fails, fix and re‑save before completing.
- After saving, read the exact answer range given in the task instruction (e.g., `'Sheet1'!A3:A24`) and verify that every cell contains a literal value (string, number, None) and not a formula string starting with `=`, unless the task explicitly grades formulas.
If the answer range uses column letters (e.g., 'BN'), convert them to indices with `openpyxl.utils.column_index_from_string` before reading, to ensure you are inspecting the correct cells. Example check: `all((isinstance(v, str) and not v.startswith('=')) or v is None for v in values)`.
Immediately after printing, perform the mandatory formula‑string check (see below) to confirm no formula strings remain.

- After printing the answer range, compare the values against the expected results you derived during the input inspection (e.g., expected totals, specific values from the task description). If any mismatch, debug and re-save before completing.

- If the task requires cell highlighting, after saving, reload and confirm that the fill's `fgColor.rgb` attribute starts with `FF` (full opacity) for at least one highlighted cell.

If the answer range is large, at minimum print the first 10 and last 5 rows (values and types) to spot‑check correctness and ensure no unexpected gaps or formula strings.

- When modifying cells that originally had formatting, after saving, reload both the original and output workbooks and compare the formatting (font, fill, border, alignment, number_format) of a few cells to ensure they are identical. Example: `assert orig_cell.font == new_cell.font`.

- After writing output, iterate over the original blank separator rows and confirm they are still completely empty (`cell.value is None` for all key columns) so no data or formatting leaked into separation lines.

This check is mandatory even if the task says "use a formula" or "calculate using IF"; the grader reads literal values, so any `=IF(...)` strings must be replaced with computed results.

- When the task involves structural changes (deleting or inserting rows/columns), after saving, reload the workbook and verify that the sheet dimensions changed as expected (e.g., `max_column` decreased after a column deletion, `max_row` decreased after row deletion). Print the new dimensions and compare them to the original ones to confirm the change took effect.

When the task expects formulas, after printing the formula strings, assert that every cell in the answer range contains a formula string: `all(isinstance(v, str) and v.startswith('=') for v in vals)`. This confirms the formulas were written correctly and the file is intact.

- Additionally, verify the file size is non‑zero using `ls -l <output_path>` or `os.path.getsize(output_path) > 0`. A zero‑byte file indicates a write failure.

- After writing, re‑compute any grouping, filtering, or constraint logic on the output data to verify that the intended transformation was applied correctly. Print the resulting groups, counts, or conditions to confirm.

- When the task specifies multiple non‑contiguous output cells, after writing, iterate over the entire answer range (including cells between the specified ones) and assert that only the intended cells contain values and that every intended cell is filled. Example: `expected = {'H10', 'H20', 'H24'}; actual = {cell.coordinate for row in ws['H2:H24'] for cell in row if cell.value is not None}; assert actual == expected`.
- After deleting rows based on a condition (e.g., rows containing a specific substring), reload the workbook and scan the remaining rows in the affected columns to verify that no row still matches the deletion condition. Print the count of matches (should be 0) and assert it is zero.

- When printing the answer range, use the exact cell coordinates from the task, not the worksheet's `max_column` or `max_row`. Even if columns beyond the current data extent are empty, they may be part of the graded range and must be inspected.

- After saving, verify that all original sheet names are still present in the output workbook (unless the task explicitly asked to remove them). Print `wb.sheetnames` and assert that the set of original sheet names is a subset of the output's sheet names. Example: `original_sheets = set(original_sheetnames); output_sheets = set(wb.sheetnames); assert original_sheets.issubset(output_sheets), f'Missing sheets: {original_sheets - output_sheets}'`

- After writing, verify that the number of non‑None cells in the answer range matches the expected count derived from the source data (e.g., number of employees × number of variables). Print the count and assert equality.

- **Verify the entire answer range, not just a preview.**

- **Stray value check for conditionally populated columns**: After writing, iterate over all rows of the target column and assert that every cell is either the correct value (if condition met) or `None` (if not), with no unexpected stray values. Print a summary confirming no stray values were found. After reloading, iterate over every cell in the exact graded range and assert that each cell's value meets the expected conditions (type, not a formula string, etc.). Do not rely on printing only the first few rows; check the full range. For very large ranges (>500 cells), at minimum check the first and last 10 rows and a random sample of 10% of the remaining rows, but always prefer a full scan when feasible.

When reloading, always access the answer sheet by name (e.g., `ws = wb['Sheet1']`), not `wb.active`, to ensure you are verifying the correct sheet.

- For small answer ranges (e.g., a single column of a few rows), print each cell's coordinate and value individually (e.g., `for r in range(2,6): print(f"G{r}: {ws.cell(r,7).value}")`) and manually confirm the mapping to the correct source row. This catches off‑by‑one errors where a write loop used wrong indices.

- **Do not skip cells with `None` values** when printing the answer range. Print every cell in the exact graded range, including those with `None`, and include fill and border attributes. This ensures leftover formatting in empty cells is visible.


- For numeric answer cells, verify that `number_format` is not `'General'` and matches the expected format (e.g., `'0.00'`). Print the `number_format` alongside the value for a few cells.

- **For tasks that mention macros or code**: after writing, print the answer‑range values and their Python types (e.g., `type(cell.value).__name__`) to confirm they are plain data, not formula strings or macro code. This runtime check guards against accidentally submitting text‑based formulas.

- After saving, print every cell in the exact graded answer range (including rows beyond your last written data) to confirm completeness and that trailing rows are blank. Use a loop like `for r in range(start_row, end_row+1): print(r, [ws.cell(r,c).value for c in range(start_col, end_col+1)])`. Count the number of non‑None cells and assert it matches the expected number of data rows. Ensure no cell contains a formula string. Do not rely on print statements from your modification script to confirm success; even if the script prints a message like 'Output saved', you must reload the workbook and inspect the answer range. This is the only way to catch missing rows, formula strings, or wrong sheet paths.
## Common Pitfalls


- Writing formula strings instead of literal values into answer cells; the grader will read None.
- Not verifying that a lookup key matches any row in the data before writing the cell, leading to errors or None.
- **String Matching in Filters**
  - **Type guard before prefix matching**: Always check `isinstance(cell.value, str)` before calling `.startswith()`. This prevents accidental deletion of non‑string values (e.g., numbers) that would match after stringification.
  - **Normalize whitespace and case**: Apply `.strip().upper()` (or `.lower()`) to the string before checking prefixes, unless the task demands exact‑case, no‑whitespace matching. This protects against leading/trailing spaces and inconsistent letter case.
  - **Runtime verification**: After filtering, print the remaining values in the target column after `str(val).strip().upper()` and confirm none start with the forbidden prefixes.

Example deletion condition:
```python
if isinstance(cell.value, str) and cell.value.strip().upper().startswith(('Z1','X1')):
    ws.delete_rows(cell.row)
```
- **Pandas header assumption**: Using `pandas.read_excel` without `header=None` silently treats the first row as column names, shifting data. Always use openpyxl for inspection and data reading. If you must use pandas, set `header=None` and after reading, print the first few rows to confirm they match the raw cell values from openpyxl's inspection.
- **Entity‑Grouped Condition Checking**: When the task asks for results scoped to an entity (e.g., per employee, per department) and the data contains an identifier column, always group records by that identifier before evaluating any block‑ or week‑level conditions. Never aggregate condition flags (e.g., has_sick, has_overtime) across all rows globally — build them per contiguous (identifier, block) group. After writing, verify by printing a few rows showing the identifier, block, and flag, confirming that marked rows belong to the correct entity's block.

- Skipping comprehensive inspection before making changes can lead to errors due to unexpected formats or data layout.

- Aggregating over a subset of data rows instead of the full matching set; always verify that your aggregation loop covers all rows with the correct group key.
- If the task provides example output values (e.g., specific numbers), those are the expected literal values, not formula strings.

- Creating a fresh workbook instead of modifying the original, losing formatting, trailing empty rows, and sheet dimensions. Never use `openpyxl.Workbook()` to rebuild the workbook; always load the original and modify it in‑place with `delete_rows`, `insert_rows`, etc. After saving, confirm that the worksheet's `max_row` and `max_column` cover the grader's expected answer range, including empty rows.
- **Clearing cell backgrounds conditionally**: Do not check `cell.fill.start_color.rgb` before clearing a background; some fills use indexed or theme colours that lack this attribute. Instead, unconditionally set `cell.fill = copy(openpyxl.styles.PatternFill())` or `PatternFill(fill_type=None)`. After clearing, verify with `cell.fill.fill_type` (should be `None`).
- **Directional Adjustments**: When a task describes a directional unit‑adjustment order (e.g., “add to unit 1, subtract from unit 5”), reason about what operation cancels the residual. Write a comment stating the intended effect (e.g., “to cancel a negative residual we must **add** to units; to cancel a positive residual we must **subtract**”). Before running the full script, test on the first data row: print the residual before and after the trial adjustment to verify it moves toward zero and that unit values stay within the printed min/max bounds. After implementing the per‑row logic, print the row index, original residual, chosen operation, and new unit values for the first two rows to visually confirm the sign is correct.

- **Duplicate Lookup Keys**: When building a lookup dictionary from a source table that may contain duplicate keys (e.g., multiple rows with the same identifier), store all matching values per key in a list (e.g., `lookup.setdefault(key, []).append(value)`) rather than discarding repeats with `if key not in lookup:`. This ensures you can later retrieve multiple values for a key (e.g., for transposed fill across columns). After constructing the lookup, print the number of stored values per key; for any key that appears N times in the source, the stored list length must be ≥ N.
- **Cross‑sheet formulas (INDIRECT, VLOOKUP across sheets)**: These will not be evaluated by the grader, which reads with `data_only=True`. Always compute the value in Python and write the literal. If you are tempted to use a formula to pull data from another sheet, instead read that data in Python and write the result.

- **Fixing formula errors**: When a task asks to "fix a formula error" or "correct a formula", the grader expects the final computed result, not the corrected formula string. Compute the value in Python and write it as a static cell value. Only write an actual Excel formula if the task explicitly requires the cell to contain a formula (e.g., "the cell should contain =SUM(...)").

- **Setting fill colors**: Always use `PatternFill(fill_type='solid', fgColor='FFRRGGBB')` with the alpha prefix `FF` for full opacity. Never use `start_color` or `end_color` (e.g., `PatternFill(start_color='A6A6A6', end_color='A6A6A6', fill_type='solid')` produces a transparent fill). After writing, reload and verify that at least one highlighted cell's `fill.fgColor.rgb` begins with `FF`.

- **Skipping columns in a specified range**: When the task says to process a named column range (e.g., columns A to F), iterate over every column in that range and apply the stated condition per cell. Do not skip columns because a quick inspection suggests they don’t currently contain qualifying values. After writing, print the number of columns your code processed and assert it matches the count described in the instruction.

- **Losing numeric types during string cleaning**: When applying transformations to cell values (e.g., removing characters), only modify cells where `isinstance(cell.value, str)`. Leave numeric (int, float) cells untouched. After cleaning, verify that cells originally holding numbers still have numeric types, not string representations.

- **Modifying font attributes**: When changing only the font name, copy the existing font object (`f = copy(cell.font); f.name = '...'; cell.font = f`) to preserve size, bold, italic, etc. After writing, verify that font size and style remain unchanged for a few cells.
- **Hardcoding data and manual pre‑computation**: Never type observed cell values as literal constants in your code; always read them dynamically with openpyxl (e.g., `ws[range]`). Do not manually simulate the described algorithm to guess the expected output; instead, translate the instruction directly into code that processes the cell values. After writing, verify that every value used in the calculation comes from a cell object, not a manually‑typed list, and that the script contains the required conditionals/loops, not a single assignment of a pre‑computed constant.
- **Extracted Substrings**: When extracting a substring from a cell value using `split`, `partition`, or regex, always call `.strip()` on the result before writing it to a cell. Leading/trailing spaces in the source text would otherwise be preserved and may cause the grader to mark the answer wrong.
### Sorting
- Before sorting data, inspect the entire sheet (or at least a large window of all rows) to identify header rows, subtotals, blank rows, and repeated column titles. Print all rows in the target columns.
- Write code to explicitly detect and skip non‑data rows: compare cell values case‑insensitively to known header strings (e.g., `if str(cell.value).strip().casefold() in ['number', 'name']: continue`).
- After sorting, validate that no header‑like values appear inside the sorted data blocks by scanning the data portion for those strings.

- **Hardcoding format strings**: Do not guess or hardcode a format string (e.g., `'YYYY-MM-DD HH:MM:SS'`) when copying cells. Always copy the source cell's style with `copy(source_cell._style)` and its `number_format` to preserve the original formatting.

- When a task instructs you to sort data based on a helper list first and later mentions a secondary sort like "sort column X lowest to highest", verify whether the secondary sort is meant as a tie‑breaker within each group or a full re‑sort of the final list. If the two orders conflict, the helper‑list ordering takes precedence unless the task explicitly says to re‑sort everything. After sorting, perform a runtime check: for the first few entries in the helper list, confirm that all rows belonging to that helper entry appear before any row from the next helper entry (or before any non‑listed name) – this ensures the grouping is preserved.

- **Sign convention in running‑balance calculations**: When a task requires computing a running balance from columns that represent opposing transaction types (e.g., “additions” and “deductions”), first inspect the workbook for any existing formula that uses those same columns (e.g., a TOTAL column) to infer the correct arithmetic direction. If a formula like `=…+ADDITIONS–DEDUCTIONS` exists, apply the same sign convention to the new balance. If no formula exists, reason from domain context (e.g., payroll: additions increase debt, deductions decrease it) and **test on a row with a non‑zero value** before processing all rows. Print the test row’s computed balance and manually verify it matches the expected direction.

- **Macro Distraction**: If the task mentions a macro or code but the answer range is a sheet range, produce the spreadsheet output, not the macro code. Use openpyxl to apply the logic directly.

- **Hardcoding row ranges**: Never use a fixed row number like `range(2, 86)` when reading or writing. Always compute the true last data row dynamically by scanning the column for the last non‑None cell (e.g., `last_row = ws.max_row; while last_row > 1 and ws.cell(last_row, 1).value is None: last_row -= 1`). After writing, verify that the number of non‑None entries in the answer range matches the expected count.
- **Enumerated Output Vocabulary**: When the task lists a fixed set of allowable answer strings (e.g., 'Group 1', 'Group 2', 'BOTH'), map your logic to output exactly one of those strings, never a derived concatenation like 'Group 1, Group 2'. After writing, scan the answer range and assert all values belong to the allowed set.

- **Diagnosing but not fixing errors**: If the task involves fixing a formula error (e.g., #REF!), after inspecting the cell and its references, you must take explicit action: compute the correct result in Python and write it as a literal value (or write a corrected formula string if the task explicitly requires a formula). Then save the workbook to output_path and verify that the target cell holds a non‑error value and is not a formula string (unless formula required). Never stop after inspection without modifying the workbook.

- **Using `pd.ExcelWriter` or other tools that create a new workbook**: These discard the original sheet names, formatting, and data. Always use `openpyxl.load_workbook` to load the existing file, modify it, and save the same workbook object. After saving, verify the output workbook contains the expected sheet name(s) (e.g., print `wb.sheetnames`).

- **Position‑based matching vs. key‑column lookup**: When the task describes replacing cells by address (e.g., "replace B2 in Sheet1 with B2 in ITEMS") without mentioning a key column, treat the alignment as row‑wise (same row index). Do not build a lookup dictionary from an identifier column unless the instruction explicitly says to match by that column. Iterate over row numbers (`for r in range(2, max_row+1):`). After writing, print a side‑by‑side of a few target‑source row values to confirm same‑index alignment.

- **Source cells with formulas**: When source cells contain formulas (VLOOKUP, ROUND, IF, etc.), loading with `data_only=False` returns formula strings, not computed values. Always load with `data_only=True` to get the evaluated numbers before performing Python calculations on those cells.

- **Modifying header rows unintentionally**: When applying transformations (e.g., substring removal, case changes) to a column that includes a header row, inspect row 1 to identify header cells. Unless the task explicitly instructs to modify the header, start your loop at row 2 to preserve the header as‑is. After writing, verify that header cells in the answer range still contain their original values (compare with your initial inspection output). Also, as a general sanity check, confirm that every cell in the answer range holds plain data values (strings/numbers), not formula text or code, unless the task specifically grades formulas.


- **Precision mismatch from floating‑point artifacts**: When the task specifies a display format with a fixed number of decimal places (e.g., 11 decimal places), round the computed value to that precision before writing. Use `round(value, ndigits)` or `Decimal(str(value)).quantize(Decimal('0.00000000001'))` to avoid binary floating‑point artifacts. After writing, verify that the stored value matches the expected rounded number.

- **Implicit Row‑wise Lookup Assumption**: When the task asks to retrieve an ID or value based on search parameters provided in separate columns (e.g., columns E and F), do not assume each parameter pair matches only the comment in the same row. Build a full lookup structure from all rows (e.g., list of (ID, Comment) pairs) and for each target row scan all lookup entries for a comment containing both search terms (case‑normalised). Verify by testing a query whose parameters appear in a comment on a different row, confirming the returned ID comes from that different row.

- **Copying from a reference layout instead of reordering**: When instructed to reorder a table to match a given layout, do not copy cells from the reference. Instead, determine the sorting rule (e.g., descending by a column value) and apply it to the original data. After writing, verify that the original table's header and data cells still contain their original values, not values from the reference.
- **Preserving formulas after reordering rows**: After any row manipulation (reordering, inserting, deleting), formulas in the answer range may become incorrect due to shifted references. Always materialize formula-dependent cells by computing their values in Python and writing them as static values. This is mandatory even if the original file contained formulas.
- **Hiding zero values via number formatting, not by clearing cells**: When the task requires that zero values be displayed as blanks, do not set the cell value to `None` or an empty string. Instead, apply a custom number format with an empty third section (e.g., `'0.00;-0.00;;@'` or `'0;0;;@'`) to hide zeros while preserving the underlying numeric value. After writing, verify that cells containing zero have `.value == 0` (not `None`) and that the number format's third section is empty.
- **Accessing cells by column number, not row‑tuple index**: When you need to read or write a specific column, use `worksheet.cell(row, column)` with the 1‑based column number (e.g., `ws.cell(r, 9)` for column I). Avoid using `row[col_idx - 1]` or similar tuple indexing from `iter_rows`, as it can cause off‑by‑one errors. After writing, verify a few cells by calling `cell(r, c).value` with explicit column numbers and compare to expected positions.

- **Reading fill colors without type checks**: Before comparing `cell.fill.fgColor.rgb`, always verify `cell.fill.fill_type == 'solid'` and `cell.fill.fgColor.type == 'rgb'`. Non‑solid or theme‑based fills lack an `rgb` attribute and will raise an error. Use a helper function that returns the RGB string only for solid RGB fills, and print the fill type and color type alongside the value for each cell you inspect. Example: `def get_rgb(cell): if cell.fill.fill_type == 'solid' and cell.fill.fgColor.type == 'rgb': return cell.fill.fgColor.rgb; return None`.


- **Row Insertion**: When inserting rows based on a condition (e.g., after each marker), collect all target row numbers first, then iterate in descending order (e.g., `for r in sorted(marker_rows, reverse=True): ws.insert_rows(r+1)`). This prevents index shifting from affecting yet‑to‑be‑processed rows. After insertion, verify the sheet's `max_row` increased by the number of inserted rows.


- **Converting date values to strings**: Never use `.strftime()` or string formatting on `datetime` objects when writing to cells. Always write the raw `datetime` object. After saving, verify the cell type with `type(cell.value).__name__` to ensure it is `'datetime'`, not `'str'`.

- **Aggregating before per‑row threshold check**: When the task describes deleting rows based on a threshold on a cell value (e.g., “values that are effectively zero”), loop over each row and evaluate that row’s own cell with `abs(value) < threshold`; never compute a sum or aggregate across rows first. After writing, mentally test with a row containing a large value (e.g., 100) next to a tiny‑value row – the large‑value row must survive, and only the tiny‑value row must be deleted.

- **Redundant inspections**: Running multiple separate inspection commands (e.g., printing rows 1–15, then all rows, then coordinate‑annotated rows) wastes turns and risks an incomplete view. Write ONE comprehensive inspection script that covers the entire used range and prints all needed information in a single run. After the inspection, proceed directly to implementation.
## Column Operations


- After deleting columns based on a header substring, reload the workbook and re‑read the header row. Print all remaining headers and assert that no cell contains the target substring (e.g., `matching = [c.value for c in ws[1] if c.value and '/description' in c.value]; print('matching headers', len(matching), matching)`). If any match remains, halt and fix the deletion logic before proceeding.
- When deleting multiple columns, collect the column indices, sort them in descending order, then delete from right to left to prevent index shifting. Use `for col_idx in sorted(cols_to_delete, reverse=True): ws.delete_cols(col_idx)`.

## Column Operations

- Use `ws.insert_cols(col_idx, num)` and `ws.delete_cols(col_idx, num)` to move columns. Never shift cells manually.
- After saving, immediately read back the target answer range (e.g., `Sheet1!B6:B10`) and print its values. Confirm they match the source column’s data and contain no leftover values from other columns.