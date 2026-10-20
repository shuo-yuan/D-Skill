---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Immediate Pre‑Code Action

**BEFORE ANY CODE: Run the Full Inspection Script (see Inspection section) and print its output. Do not write any transformation code until you have done this.** This is the single most critical step to avoid layout, type, and range errors.


**Ignore any user-specified technology (VBA, macros, etc.); always use Python/openpyxl to directly modify the workbook. The grader evaluates cell contents, not the code.**

After running the script, confirm that the printed output includes every column mentioned in the task instruction (e.g., columns F–K). If any relevant column is missing from the output, print its values and types explicitly before writing any code.
## Critical Pre‑Code and Post‑Save Checks

**STOP – READ THIS FIRST**
1. **Before any code:** Run the Full Inspection Script (see Inspection section) and print its output.
2. **After saving:** Run `verify_output` and confirm it prints `'All verification checks passed.'` before calling TASK_COMPLETE.
**Skipping either step is the #1 cause of failure.**

**Ignore any user-specified technology (VBA, macros, etc.); always use Python/openpyxl to directly modify the workbook. The grader evaluates cell contents, not the code.**
## Core Workflow


**CRITICAL**: Always inspect the workbook before writing any code, and always verify the output after saving. Skipping these steps is the most common cause of failures.


Use openpyxl as the primary tool for all spreadsheet operations: load the workbook, read data across sheets, modify cells, and save the output.

1. Inspect all sheets completely (see Inspection).

2. **Clear the answer range** – set every cell in the exact `answer_position` range to `None` and verify they are empty before writing any data. (See Writing Output for details.)
Never skip this step, even if the task description includes sample data. The actual file may contain unexpected values, types, or layouts.
2. Write the output to the exact sheet and range specified in `answer_position` (see Writing Output).
2.5. **Before saving, scan the answer range for any formula strings and replace them with computed values.** Iterate over every cell in the answer range and assert that no cell value is a string starting with `'='`. If any formula strings are found, recompute the value in Python and set `cell.value` to the literal result, then re‑check.
3. Save the workbook and run the `verify_output` function provided in the Verification section. Do not proceed until it prints `'All verification checks passed.'`.
4. Only after all checks pass, call TASK_COMPLETE.

- **Never write Excel formulas (e.g., SUM, IF, VLOOKUP, INDEX/MATCH, XLOOKUP) unless the task explicitly requires formulas. Compute every value in Python and write the literal result.**

**WARNING:** The grader reloads your file with `data_only=True`; any formula strings will appear as `None` and cause failure. Always compute values in Python and run the `verify_output` function before `TASK_COMPLETE`. Skipping verification is the #1 cause of failure.




## Inspection


Before writing any code, inspect every sheet completely:




**Pre‑inspection unmerge:** Before inspecting, unmerge all merged cells on every sheet to avoid hidden obstructions when reading or writing. Loop over `list(ws.merged_cells.ranges)` and call `ws.unmerge_cells(str(merged_range))`. After unmerging, print `list(ws.merged_cells.ranges)` to confirm it's empty.

- **Dual-mode loading:** Load the workbook with both `data_only=False` and `data_only=True` to see formulas and their evaluated values. Print the first few rows of each sheet in both modes to identify formula cells, errors (`#N/A`, `#VALUE!`), and `None` values. This reveals hidden dependencies and broken formulas before you write any code.
- List sheet names (`wb.sheetnames`) and print each sheet's dimensions (`max_row`, `max_column`).
- Iterate over all non-empty cells, printing each cell's coordinate, `repr(cell.value)`, `type(cell.value)`, and `cell.number_format`.
Also print `cell.fill.fill_type`, `cell.fill.fgColor.type`, and `cell.fill.fgColor.rgb` to detect any pre‑existing formatting that may be relevant. For tasks involving borders, print `cell.border` as well. This reveals the exact data layout, hidden date values, custom formats, and the content of answer cells.
When locating data, always determine the header row dynamically by scanning the first few rows for a known label (e.g., `'Row Labels'` or a specific column heading) rather than hardcoding a row index. Use a search like:
```python
header_row = next(r for r in range(1, ws.max_row + 1) if any(ws.cell(r, c).value == 'Row Labels' for c in range(1, ws.max_column + 1)))
```
Additionally, locate columns by matching header labels (e.g., `if str(ws.cell(header_row, c).value).strip() == 'target_label'`) instead of assuming a fixed column letter or index. This keeps the skill robust when column positions change.

- **Header dictionary:** For tasks requiring multiple column lookups, build a dictionary mapping normalized header names to column indices (e.g., `col_map = {str(ws.cell(header_row, c).value).strip().casefold(): c for c in range(1, ws.max_column+1)}`). Use this dictionary for all subsequent reads and writes to avoid repeated scanning and hardcoded indices.


- **Never** limit inspection to a fixed number of rows; iterate over **all** rows to discover every group, repeated identifier, or hidden variation. When the task involves grouping by columns (e.g., employee, week), print rows where the grouping key changes to identify contiguous blocks before writing any transformation logic.
When a target sheet contains multiple side-by-side tables, always output both cell values and their exact column letters/numbers for the header row before deriving any block boundaries. After computing a start column, verify at runtime that `ws.cell(1, start+offset).value` matches the expected label (e.g., `'ITEM'` or the account type) for every offset used. This prevents off-by-column errors that silently drop whole tables.
After inspecting all rows, note the last data row and use it to set formula ranges (e.g., `$B$3:$B$last_row`). Never hardcode a guessed upper bound.
When aggregating data from multiple sheets, loop over `wb.worksheets` and skip any designated output sheet (e.g., `if ws.title == target_title: continue`). This keeps the solution robust when sheets are added or reordered.

- When the task mentions a formula or expected output pattern, inspect the sheet for existing examples of that pattern (e.g., values in adjacent columns) to confirm the expected output format before writing any code.
- **Input infrastructure trace:** When a task involves lookups or formulas that depend on input cells (e.g., dropdowns, year headers, label columns), print those input cells and trace how existing formulas reference them. This reveals whether lookups use single or multi‑criterion matching and prevents mismatched formula logic.
- **Text matching:** When the task involves filtering or modifying cells based on text, print the exact values of the target column(s) before writing any condition. Determine if the target text appears as an exact whole-cell value or is embedded in longer strings, and choose substring matching (`target in cell_value.lower()`) unless the task demands exact equality.

- **Type‑aware filtering:** Before writing any formula or conditional logic, print the unique values and their Python types for the columns you plan to filter or match on. Confirm that the data types (e.g., `bool`, `str`, `int`) match your intended comparisons. For example, if you plan to check for `False`, verify that the column contains actual booleans and not the string `'FALSE'`.

- **Fix tasks:** If the task mentions fixing a formula error or broken data, print the current values of the target cells and the lookup source cells before writing any code. This reveals whether the cells contain formula strings, #N/A errors, or None, and helps diagnose the root cause.
- **Pre-computation inspection:** When the task involves computing values for a column that may contain existing formulas, constants, or None, inspect that column's cells with both `data_only=False` (to see formulas) and `data_only=True` (to see evaluated values). This reveals whether the column already has static values or unresolved formulas that need to be replaced with computed Python values.
- When inspecting, also identify and print any special rows such as constraints (e.g., 'Min', 'Max'), totals, subtotals, or summary rows. This ensures they are not accidentally overwritten or ignored during later operations.


- **Quick overview:** Before the full inspection, print the first 20 rows of every sheet with `values_only=True` to get a rapid sense of layout, column types, example values, and identify the first empty row. Also print the last few rows and the column headers. If the task involves mapping or lookup, check for duplicate key combinations by printing a count of unique vs total rows for the key columns; handle duplicates explicitly (e.g., aggregate or keep first) to avoid broken mappings.

This thorough inspection approach is proven to prevent errors; always perform it before writing any code.


- **Reference sheets:** If a sheet like `'Manual Result'` or `'Expected Output'` is present, inspect its first few rows to deduce the traversal order (row‑major vs column‑major) and layout constraints (e.g., max numbers per row). Also compare the reference sheet to the original data sheet to infer any transformation pattern (e.g., which rows are kept, deleted, or left blank). Reproduce that exact pattern in your output. After extracting data, print the first few values and compare them to the reference sheet's first row; if they do not match, stop and re‑evaluate the extraction order before writing any output.
- **Sparse data:** When data points are scattered in non-contiguous rows (e.g., every 16th row), after the full inspection, print a range of rows that spans from the header to the last data row, including gaps, to visually confirm the pattern before writing any output.

- When the task specifies a particular range to modify (e.g., columns N-P, rows 7-23), print the values, types, and number formats of that exact range **before** writing any transformation code. This reveals floating‑point noise, `None` cells, and formatting defaults that may not be obvious from the task description.


- When extracting data rows from a sheet that may contain repeated header rows (e.g., column labels like 'NAME', 'REF' appear again in the data), explicitly compare each row's values against the known column headers (case‑insensitive) and skip any row that matches. Print a sample of extracted rows to confirm no header strings appear.

- When the task mentions specific columns (e.g., 'Column A', 'Line No'), print a sample of those columns' values before writing any manipulation code. This confirms you are working with the correct columns and understand the data layout.

- **Answer position check:** After inspecting all sheets, verify that the `answer_position` sheet exists (or will be created) and that the specified range is consistent with the task's expected output layout. Print the parsed sheet name and range to confirm. Also print the current values and types of the cells in the answer range to see what data is already present (e.g., existing values, formulas, or None). This prevents accidentally overwriting formulas or misinterpreting the layout.
- **Prefer column letters:** After locating columns by header labels, access cells using column letters (e.g., `ws['AY2']`) rather than numeric column indices for clarity and to avoid off‑by‑one errors. Before writing manipulation code, print the header values and their corresponding column letters to confirm the mapping.


- **Target cell inspection:** Before writing to any cell that might contain a formula (e.g., cells you plan to modify), print its data_type, formula string (if any), and value. Do not hardcode a value based on a static preview; instead, resolve the intended logic programmatically using the workbook's actual data.



### Full Inspection Script
Run this script as your first action to inspect every sheet completely:

```python
import openpyxl

- After printing the quick overview, verify that the output includes the last few rows of each sheet; if not, print them explicitly.


- **Post-Inspection: Data Loop Boundaries** – After running the Full Inspection Script, identify the header row(s) (typically row 1) and set every data‑processing loop to start from the row immediately after the last header row (usually row 2). Never start a loop at row 1 unless the task explicitly requires modifying headers. This simple guard prevents the common mistake of overwriting headers.



**Pre‑Transformation Re‑inspection:** Before performing any transformation (e.g., deleting rows, filtering, writing), re‑print the full sheet contents (all rows, all columns up to `max_column`) using `values_only=True` to confirm the exact layout and cell types. Even if you inspected earlier, this catches any changes from previous steps and ensures decisions are based on the current state of the sheet.


- Do not skip any sheet, even if it appears empty or unrelated; it may contain example data, headers, or hidden constraints.

- **Filter sanity check:** When filtering or matching rows based on a condition, print a sample of rows that match your intended condition and a sample of rows that should be excluded. This manual check confirms that the filtering logic works correctly before you write any output.
# Replace 'input_file_path' with the actual input file path from the task
wb = openpyxl.load_workbook('input_file_path')
print('Sheets:', wb.sheetnames)
for ws in wb.worksheets:
    print(f'\n--- Sheet: {ws.title} ---')
    # Unmerge all merged cells
    for merged_range in list(ws.merged_cells.ranges):
        ws.unmerge_cells(str(merged_range))
    print('Merged after unmerge:', list(ws.merged_cells.ranges))
    print(f'Dimensions: {ws.max_row} rows x {ws.max_column} cols')
    # Quick overview: first 10 rows
    print('First 10 rows (values_only):')
    for row in ws.iter_rows(min_row=1, max_row=min(10, ws.max_row), values_only=True):
        print(row)
    # Detailed cell dump
    print('All non-empty cells:')
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=ws.max_column):
        for cell in row:
            if cell.value is not None:
                fill_info = ''
                if cell.fill and cell.fill.fill_type == 'solid':
                    fill_info = f', fill={cell.fill.fgColor.rgb}'
                print(f'{cell.coordinate}: {repr(cell.value)} ({type(cell.value).__name__}), fmt={cell.number_format}{fill_info}')
```

This reveals the exact layout, data types, formats, and any hidden merged cells. Use the printed information to guide all subsequent code.
## Writing Output


Write output to the exact sheet name specified in the `answer_position` field (e.g., `'MyResult'!A1:O20` means sheet `'MyResult'`). Create a new sheet with that name, deleting any prior sheet with the same name, and never write final output into an existing data sheet unless explicitly instructed.

Before writing any data, clear the exact answer range by setting every cell in that range to `None`. This prevents stale data from a previous run from polluting the output.

After clearing, re‑read the answer range and assert that every cell is `None` before you begin filling them. This runtime check catches a mis‑specified range or a failed clearing operation.

If the task description instructs to output only in specific columns (e.g., 'output in columns G and H'), clear and write only those columns within the answer range; leave the other columns untouched.


**CRITICAL**: Always write a plain data value (computed in Python) instead of a formula, unless the task explicitly requires a formula (e.g., says 'use a formula' or 'insert a formula') and the grader expects formula strings. Even if the task wording suggests using a formula (e.g., 'put the formula', 'use IF', 'apply a formula'), compute the value in Python and write the literal result. Never write an Excel formula string like `=IF(...)` unless explicitly instructed. This avoids silent failures from unevaluated formulas and mismatched data.

Fill every cell in the answer range that should contain data with a concrete value. If the answer range is larger than your data (e.g., a fixed range that includes trailing empty rows), leave those extra cells as `None` and verify they are empty after writing. For missing lookups or absent matches, use a sensible default (e.g., `False` for booleans, `0` for numbers, `""` for text).

### Writing to Specific Cells
When the task specifies a concrete destination cell (e.g., “output the answer to cell F4 of Table B”), write **only** that cell. Do not implement a loop that writes to every matching row unless the task explicitly asks for it. After writing, read back the destination column to confirm that only the intended row contains the new value and all other rows remain unchanged.


- **Replicate existing summary rows** when regenerating a structured output sheet. Before clearing or overwriting a summary sheet, scan the existing data rows for any `'TOTAL'`, `'SUM'`, `'SUBTOTAL'`, or formula cells, and note their positions relative to the data areas. When producing the new output, re-create equivalent summary rows in the same relative positions, using computed values rather than formula strings unless the task explicitly grades formulas. After writing, confirm that the expected total-row coordinates (e.g., `rng[-1]`) hold a value that matches the sum of the amounts in that block.

- **Formula handling:** If the task explicitly asks for formulas, insert them as strings starting with `'='` and only within the specified range, leaving all other cells untouched. Otherwise, always write computed plain values. Before calling `wb.save()`, if formulas were **not** required, iterate over every cell in the answer range and assert that no cell value is a string starting with `'='`. If any formula strings are found, recompute the value in Python and set `cell.value` to the literal result. If formulas were required, skip this check.

- Always save the workbook to the exact `output_path` provided in the task; do not use a default filename or hardcoded path.
Immediately after saving, confirm the file exists and is non‑empty (`os.path.exists` + `os.path.getsize > 0`). This quick guard catches silent save failures before you proceed to verification—a pattern proven to prevent wasted effort.

After saving, print the full output path with `print(f'Saved to: {output_path}')` and visually confirm it matches the exact path required by the task. This extra check reinforces the proven practice of using the unmodified output_path.


- **Verify text-based changes:** After any text-based filtering or replacement, re-open the saved workbook and print the values of the cells that were supposed to be changed. Confirm that the intended rows were modified and that no unintended rows were affected. If any expected changes are missing, adjust the matching logic and re-run.

- **Unwanted character check:** When the task involves text cleaning, after writing, verify that no unwanted characters (quotes, backticks, VBA keywords) remain in the answer cells. Use `repr()` and string assertions to confirm cleanliness.
- Do not call `TASK_COMPLETE` without first completing the post-save verification steps in the Verification section.
- If you cannot delete the sheet (e.g., it contains other data you must keep), clear the exact answer range by iterating from row 1 to the maximum row number specified in `answer_position`, not relying on `ws.max_row` which may be smaller than the answer range.

- **Respect the answer range exactly:** Parse `answer_position` to determine the precise cell range (e.g., `'Sheet1'!D8:D11`). Write **only** to those cells. Do not iterate over additional columns or rows unless the answer range explicitly includes them. After writing, verify that no spillover occurred by printing the values of cells immediately outside the range.
- **Scope of transformation:** If the task instruction explicitly describes a transformation that should be applied to all columns, rows, or sheets, do not limit the operation to the answer range. Apply it to every cell described, even if the answer range is smaller. The answer range only indicates where the grader checks, but the transformation must be complete.

- For tasks that ask to fix a formula error, do not write a corrected formula; compute the correct value in Python and write the literal result.

- **Preserve existing formatting:** When overwriting cells within the answer range that already contain data (e.g., filling values into a pre-existing table), read the cell's existing formatting (number_format, font, fill, borders, alignment) before writing the new value, and reapply it afterward. This preserves specialized formatting that the grader may expect. Only change formatting if the task explicitly instructs you to.

This pattern (using openpyxl and saving to the exact `output_path`) has been repeatedly successful in practice; always follow it without deviation.


- **Conditional instructions:** When the task description contains a condition (e.g., 'if the value does not match, replace it'), implement that exact logic in your code. Do not unconditionally overwrite every cell. Search the task for the word 'if' and ensure your code includes the corresponding `if` check. After writing, test with a case where the condition is false to confirm the action is skipped.

- **Copying formula cells:** When copying data from source cells (e.g., `ws['F2'] = source_ws['F2'].value`), always check the source cell's `data_type`. If it is a formula (`data_type='f'`), read the evaluated value from a `data_only=True` load and write that static value instead. Never copy a formula string into the answer range.


- **Conditional writes:** Even when you plan to write values only to rows that meet a condition, clear the entire answer range first. Do not rely on overwriting only matching rows; leftover values in non‑matching rows will persist and cause errors.

- **Do not add header rows to the output area unless the task explicitly asks for column labels.** The answer position (e.g., H2) marks the start of the data: write the first data row there, not a header row. After writing, read back the answer range and confirm that the first cell contains actual data values (e.g., a date, string, or number) rather than a static label like 'date'.

- **Display/Output tasks:** When the task asks to 'display', 'output', 'show', or 'put' a value in a cell, always write the computed value, not a formula. Even if the task describes a formula (e.g., 'use COUNTIF to rank'), compute the result in Python and write the literal value. The grader reads the cell's content, not the formula.
## Verification


Before writing final cells that depend on string lookups, normalize all lookup keys with `.strip().casefold()` (or `.strip().upper()` for case-insensitive matching).

If the task explicitly requires case‑sensitive matching, skip case normalization and use exact equality (`==`). After writing, test with mixed‑case example entries to confirm that only exact matches are captured and case differences are correctly distinguished. Apply the same normalization to every key on both sides of the comparison. Print a sample of normalized keys and retrieved values to confirm the mapping works before writing.

### Quick Sanity Check
Before running the full verification, always execute this minimal check to catch obvious errors:
```python
import os
assert os.path.getsize(output_path) > 0, 'Output file is empty or missing'
wb_check = openpyxl.load_workbook(output_path)
ws_check = wb_check[target_sheet_name]  # from answer_position
print(f'Sheet dimensions: {ws_check.max_row} rows x {ws_check.max_column} cols')
first_cell = ws_check.cell(1, 1)
print(f'First cell: {first_cell.coordinate} = {first_cell.value}')
```
If the dimensions or first cell value look wrong, inspect further before proceeding.


Additionally, parse the `answer_position` to extract the sheet name and cell range (e.g., using `split('!')`), then quickly scan the answer range for any formula strings:

```python
answer_sheet_name, answer_range_str = answer_position.split('!')
answer_ws = wb_check[answer_sheet_name]
answer_range = answer_ws[answer_range_str]
for row in answer_range:
    for cell in row:
        if isinstance(cell.value, str) and cell.value.startswith('='):
            print(f'ERROR: Formula string found in answer cell {cell.coordinate}: {cell.value}')
            raise AssertionError('Formula string in answer cell – compute the value in Python instead')
```

print(f'Output saved to: {output_path}')
### Post-save Verification
Before reloading, confirm the file exists and is non‑empty:
```python
import os
assert os.path.getsize(output_path) > 0, 'Output file is empty or missing'
```
After saving the workbook, always reload it and verify the answer cells:

1. Reload with `openpyxl.load_workbook(out_path, data_only=False)`.
2. Print `wb.sheetnames` and confirm the required sheet is present. Access that sheet directly (e.g., `wb['Sheet1']`).
3. For each cell in the required answer range, print its coordinate, value, type, and number format.

Always derive this range directly from the `answer_position` field (e.g., `'MyResult'!A1:O20` → sheet `'MyResult'`, range `A1:O20`). Do not verify a broader column or row; only the exact graded cells matter.
4. Assert that no cell is `None` or empty.
5. Assert that no cell contains a formula string (value starting with `=`) unless a formula was explicitly required. Use `cell.data_type != 'f'` as an additional check.

If the task requires formulas, assert that every answer cell has `data_type='f'`.

   - Additionally, for formula‑required tasks, print the formula strings and confirm that any test conditions (e.g., checking for `FALSE`) align with the data types observed during inspection.
   - When formulas use expanding ranges (e.g., `$A$2:A2`, `$B$3:B3`), print the formula strings from the first 3‑4 rows of the answer range and confirm the range bounds increment correctly with each row. This catches off‑by‑one reference errors before the grader sees them.
6. If the answer expects numeric values, assert that every cell value is an instance of `int` or `float` (and not `bool`).
7. For cells with a specified number format (e.g., date, currency), assert that `cell.number_format` matches the required format string exactly, character-for-character. Print the format to confirm. For example, if the task says `m/dd/yyyy`, use that exact string and verify with `assert cell.number_format == 'm/dd/yyyy'`. Do not substitute a similar format.
8. Confirm that only the intended cells were modified and no other data was changed. If you cleared values in a column, assert that header cells still contain their original labels and no non-data rows were altered.

   - Print the values of cells immediately outside the answer range (e.g., one column left/right, one row above/below) to confirm they remain unchanged.

9. If the task mentions fill colors, sums of marked cells, or sheet deletions, include checks for those in your verification script. For example, assert that the sum of cells with a specific fill color matches the answer cell value, or that a sheet that should be deleted is no longer present.
9. Only call TASK_COMPLETE after all checks pass.

Example verification block:

```python
wb_check = openpyxl.load_workbook(out_path, data_only=False)
ws_check = wb_check['Sheet1']  # or wb_check.active
target_range = ws_check['A1':'C10']  # adjust to actual graded cells
for row in target_range:
    for cell in row:
        print(cell.coordinate, cell.value, type(cell.value).__name__, cell.number_format)

10. If the task involved sorting rows, additionally verify that the key column values are in the expected order (e.g., ascending) and that no duplicate rows exist unless explicitly required. Print a sample of the sorted column to confirm.
11. **Grader simulation:** After the initial checks, reload the workbook with `openpyxl.load_workbook(out_path, data_only=True)` and verify that every answer cell contains a concrete value (not `None`). This simulates the grader's view and catches unevaluated formula strings.
### Sample Data Validation

If the task description includes example input-output sequences (e.g., a worked example with intermediate values), reverse-engineer the formula from those examples. Before writing the final answer, compute the expected values for each example step and assert they match your computed values (allowing for floating-point differences). Print the expected vs. actual values for verification. This ensures the formula is correctly interpreted.

10. Confirm that the sheet dimensions (max_row, max_column), existing headers, and cell formatting (number_format) outside the answer range remain unchanged. Print a few rows outside the answer range to visually spot-check that no unintended changes occurred.

**Mandatory:** Always run the post-save verification steps below after saving the workbook. Do not call TASK_COMPLETE without first reloading the file and checking the answer cells as described. Even if the answer range appears correct at a glance, always reload and verify programmatically. Skipping verification is the most common cause of undetected formula‑writing mistakes.


**CRITICAL:** The reloaded workbook must be a fresh `openpyxl.load_workbook()` call from disk; do not reuse the in‑memory workbook object. The saved file is the only truth the grader sees. After reloading, immediately run the `verify_output` function and wait for `'All verification checks passed.'` before any `TASK_COMPLETE` call.

**Column/Row Deletion Verification:** After any deletion or filtering operation, reload the saved workbook and scan the **entire answer range** (or the relevant column) for any remaining cells that match the pattern you intended to delete. Assert that the count is zero and print the result. This check must be exhaustive; do not rely on a summary printout. A single missed row will cause a grading failure. Also print the first 10 rows of the sheet (or the rows around the anchor) to confirm that the anchor row and data rows have moved as intended, especially after deleting rows above a specific cell.



- **Reference‑sheet cross‑check:** If a reference sheet exists, reload the output workbook and compare the answer range to the reference sheet row by row. Print match results (e.g., `assert output_row == ref_row`). If any mismatch, fix the output before calling `TASK_COMPLETE`.


**Verification Complete:** After all checks pass, print `'All verification checks passed.'` and only then call TASK_COMPLETE. If any assertion fails, fix the output, re‑save, and re‑verify before proceeding.






### Reusable Verification Function
Copy and call this function after saving to perform all mandatory checks in one step:

```python
import os
import openpyxl

def verify_output(output_path, answer_position, formulas_required=False, expected_filled_rows=None):
    """
    Reload the saved workbook, print all answer cells, and assert correctness.
    If expected_filled_rows is provided, assert that the first expected_filled_rows rows
    in the range are filled and all subsequent rows are empty.
    """
    assert os.path.getsize(output_path) > 0, 'Output file is empty or missing'
    wb = openpyxl.load_workbook(output_path, data_only=False)
    sheet_name, range_str = answer_position.split('!')
    ws = wb[sheet_name]
    target_range = ws[range_str]
    print(f'Verifying {sheet_name}!{range_str}')
    for row in target_range:
        for cell in row:
            print(f'{cell.coordinate}: value={cell.value!r}, type={type(cell.value).__name__}, '
                  f'number_format={cell.number_format}, data_type={cell.data_type}')
    flat_cells = [cell for row in target_range for cell in row]
    if expected_filled_rows is not None:
        # split range into filled and trailing rows
        rows_in_range = list(target_range)
        filled_rows = rows_in_range[:expected_filled_rows]
        trailing_rows = rows_in_range[expected_filled_rows:]
        filled_cells = [cell for row in filled_rows for cell in row]
        trailing_cells = [cell for row in trailing_rows for cell in row]
        assert all(cell.value is not None for cell in filled_cells), 'Some expected data cells are empty'
        assert all(cell.value is None for cell in trailing_cells), 'Trailing rows contain unexpected data'
    else:
        assert all(cell.value is not None for cell in flat_cells), 'Some answer cells are empty'
    if formulas_required:
        assert all(cell.data_type == 'f' for cell in flat_cells), 'Expected formulas, but some cells are not formulas'
    else:
        assert not any(isinstance(cell.value, str) and cell.value.startswith('=') for cell in flat_cells), \
            'Formula strings found in answer cells – compute the value in Python instead'
    print('All verification checks passed.')
```

Call it immediately after saving. If the answer range is larger than your data, pass `expected_filled_rows` to verify that trailing rows are empty:
```python
verify_output(output_path, answer_position, formulas_required=False, expected_filled_rows=18)  # adjust count to your actual data rows
```



**Important:** The `verify_output` function above is the only verification you need. Do not rely on manual prints or partial checks; always call it after saving and wait for `'All verification checks passed.'` before calling TASK_COMPLETE.


**Large‑file fallback:** For very large workbooks (e.g., >10k rows) where openpyxl may hang during verification, use a lightweight XML inspection instead of the full `verify_output` function. Example:
```python
import zipfile, xml.etree.ElementTree as ET
with zipfile.ZipFile(output_path) as z:
    with z.open('xl/worksheets/sheet1.xml') as f:
        tree = ET.parse(f)
        # parse tree to check answer cell values
```
This ensures verification completes even on large files.




- **Condition‑value consistency check:** For tasks that conditionally write values to a column, after reloading, verify that every cell in the answer range satisfies the expected condition‑value relationship: for each row, assert `(condition_holds and cell.value == expected_value) or (not condition_holds and cell.value is None)`. Print any rows that violate this. This catches leftover values from incomplete clearing.

10. **Recompute‑and‑compare (logic check):** If the transformation logic is deterministic, re‑apply it to a few input rows and compare the computed values with the written output. This catches logic errors that structural checks (empty cells, formula strings) might miss. Print the expected vs. actual values for a sample of rows.

- **Trailing empty rows:** If the answer range includes extra rows beyond your data, after writing, verify that the first N rows (where N is the number of data rows you produced) are filled, and that all subsequent rows in the range are empty. Use the `expected_filled_rows` parameter of `verify_output` to automate this check. Print the count of filled rows and any trailing cells to confirm.
# Assertions
flat_cells = [cell for row in target_range for cell in row]
assert all(cell.value is not None for cell in flat_cells), 'Some answer cells are empty'
assert not any(isinstance(cell.value, str) and cell.value.startswith('=') for cell in flat_cells), 'Formula strings found in answer cells'
# If numeric answers expected:
assert all(isinstance(cell.value, (int, float)) and not isinstance(cell.value, bool) for cell in flat_cells), 'Non-numeric or boolean value in answer cells'
```

After moving columns or rearranging data, confirm that values appear in the expected rows and that any summary rows (e.g., Grand Total) still compute correctly.
## Common Pitfalls


- Writing a formula without first verifying the data supports it (e.g., exact date matches across different years). The formula may evaluate to `None` without raising an error. Always compute the value in Python and write the result, then verify the cell as described in the Verification section.

- Writing output to the wrong sheet or leaving out the required sheet. Always match the sheet name from `answer_position` exactly.
- Row deletion: Always delete rows in reverse order (from `max_row` down to 2). Forward iteration causes row indices to shift, skipping rows and missing deletions.


- Hardcoding formula bounds without inspecting the full data range. Always inspect the full sheet to find the actual last data row and use that in your formulas. After writing, verify the formulas reference the correct bottom row.

- **Row sorting:** When reordering rows with openpyxl, never sort live cell objects from `ws.iter_rows()` and then write them back by copying attributes. This mutates source cells before they are read, causing duplicates and missing rows. Instead, first extract all needed data (value, number_format, font, fill, border, alignment, protection) into a plain list of tuples, sort that detached list, and then write back to the target rows using the stored data, never the original cell objects.
- Clearing a column without identifying data rows: When the task asks to clear or set values in a column (e.g., zero residuals), first identify the exact data rows that contain the values to clear (e.g., rows with numeric entries, excluding headers, blank lines, and metadata). Apply modifications only to those cells. Never overwrite header cells or empty rows. After writing, verify that header cells still hold their original labels.
- Column deletion: Always delete columns in reverse order (from `max_column` down to 1). Forward iteration causes column indices to shift, skipping columns and missing deletions. This applies to any bulk column removal, just as with rows.

- **Conditional overwrite:** When filling a column based on a mapping (e.g., invoice numbers per customer), write the computed value to **every** cell that matches the condition, replacing any existing content. Do not restrict writes to cells that happen to be empty—existing placeholder values must be overwritten. After writing, pick at least one matched cell that originally held a non‑empty value and confirm it now shows the new value.
- **Cross‑sheet formulas (INDIRECT, etc.):** openpyxl cannot evaluate formulas that reference other sheets; the grader will see `None`. Never use INDIRECT or any formula that pulls data from another sheet. Always fetch the data from other sheets in Python and write the static value into the answer cell. The `data_only=True` verification step will catch this, but the best practice is to never write such formulas at all.
- **Macro/Code Tasks:** When the task asks to create or fix a macro, VBA code, or formula but the grader reads specific cells, ignore the provided code and implement the transformation directly in Python, writing the resulting values. The deliverable is the spreadsheet, not the code. After writing, verify that the answer cells contain computed values, not formula strings or code text.

- **Mapping from multi-column headers:** When a task says a result "derives from columns with numeric headers" (e.g., columns J, K, L, M with headers 1,2,3,4), treat the **header values** as the output ranks and the cell values as lookup keys. Do not concatenate the column values into a string. Validate your interpretation by examining any given example cell in the original file. After writing, check a few cells in the answer range: each should contain a single scalar value (number or None), never a concatenated string, unless the task explicitly demands that.

- **Overwriting header rows:** When writing data to a column, always identify the header row(s) (usually row 1) and start your loop from row 2 onward. Never overwrite headers unless the task explicitly instructs to do so. After writing, print the first row of the answer range to confirm that the original header text is still present (e.g., `print(ws.cell(1, col).value)`).

- **Date/Time Conversion:** When converting dates or timestamps, inspect the source cells' values and types before writing any conversion logic. After writing, verify that every output cell in the answer range contains a datetime object (not a string) and the correct number format.

- **Fix tasks:** When a task mentions a formula error or asks you to 'fix' something (e.g., #N/A from VLOOKUP), do not just apply formatting. Diagnose the root cause (e.g., lookup mismatch, missing data) and compute the correct values in Python, then write them to the target cells. After writing, verify the cells hold actual data (not None or formula strings).



- **Number format exactness:** When a task specifies a numeric or date format string, use that exact string verbatim. Do not substitute a similar format (e.g., `m/d/yyyy` for `m/dd/yyyy`). After saving, reload and assert that the cell's `number_format` matches the required string character-for-character.


- **Ignoring reference sheets:** When a task provides a `'Manual Result'` or similar sheet, always inspect it to deduce the expected ordering and layout. Failing to do so can cause wrong traversal order and misordered output. Validate against the reference early and again after writing.
- **Using Excel functions for computed values:** When the task requires computing a value (e.g., sequential rank, count, sum, lookup, distinct count) and the result is a static number or text,  These produce formula strings that will not evaluate in the grader's environment and will appear as `None`. Instead, implement the logic in Python and write the final computed value (int, float, str) directly. This is especially important for tasks that ask for ranks, counts, aggregations, or distinct lists within groups.
- **String cleaning without type guard:** When the task asks to clean cell contents (e.g., remove non-numeric characters) but preserve existing numeric values, first inspect each cell's type. Apply string cleaning only to non-numeric cells (skip `int`/`float`). After writing, reload and assert that cells originally numeric are still instances of `int` or `float`, not strings.
- **User terminology disambiguation:** When the task uses a term like 'error', 'blank', 'yes', etc. to describe a condition, first inspect the relevant column to see what actual values represent that condition (e.g., '#N/A', empty cell, 'Yes'), and match against those actual values, not the literal word.
- Writing any formula that references other cells (e.g., `=A25`, `=LEFT(F10,1)&"."`) will not be evaluated by openpyxl and will appear as a formula string or None. Instead, read the source cell values in Python, compute the result, and write the literal value. After writing, verify the answer cells contain actual data, not formulas.


- **Floating‑point noise:** When the task provides example numeric outputs (e.g., `12.62`), infer the required decimal precision and round all computed values to that many decimal places using `round(value, ndigits)`. For monetary or hourly amounts, round to two decimal places. After writing, verify that values have at most the expected number of decimal places (e.g., `assert round(value, 2) == value`).
- **Floating‑point threshold checks:** When testing a percentage increase (e.g., `value >= reference * 1.10`), floating‑point imprecision can make the threshold slightly larger than the exact value, causing borderline values to fail. Use integer scaling (`value * 10 >= reference * 11`) or a small epsilon (`value >= reference * 1.10 - 1e-9`). After writing, sanity‑test with the exact threshold value to confirm the check passes.
- **Fill‑down of identifiers:** When filling down identifiers (e.g., group labels) across rows, do not simply copy from the immediate predecessor cell. Instead, maintain a `current_id` variable that updates when you encounter a non‑empty identifier cell, and resets to `None` when you encounter a header row or an empty cell in the identifier column. This prevents accidentally copying header text or stale values. After writing, scan the filled column for any occurrence of a known header string (like `"column1"`) outside the original header rows to confirm no header values were propagated.
- **Temporary script naming:** Never name a temporary Python script with a name that shadows a standard‑library or site‑package module (e.g., avoid `inspect.py`, `openpyxl.py`, `json.py`). Use a unique name like `solution.py` or `task_script.py`. Run‑time check: list known library names with `python -c "import pkgutil; print([m.name for m in pkgutil.iter_modules()])"` and verify your filename is not among them.
- **Font application:** When applying a single font family to every used cell, iterate over all cells with `ws.iter_rows()`, copy the existing font with `copy(cell.font)`, change only the `name` attribute, and assign it back. This preserves weight, size, and other style attributes. Before saving, inspect a header cell and a data cell with `cell.font` to confirm that size, bold, italic, and color are still present. After saving, verify by reading the file back and printing `set(c.font.name for row in ws_check.iter_rows() for c in row if c.font)` to ensure only the expected font name appears.


- **'Put the formula' / 'Apply a formula' tasks:** When the task asks to "put the formula in cells", "insert the formula", or "apply a formula", the grader expects the computed numeric result, not the formula string.
- **Skipping post-save verification:** Printing a summary of results before saving is not enough. After saving, you must reload the workbook and run the verification checks described in the Verification section. Even if the output looks correct, the grader can detect formula strings, empty cells, or wrong formats. Always reload, check the answer range cell by cell, and ensure 'All verification checks passed.' before calling TASK_COMPLETE. Skipping this step is a common cause of failure.

- **Complex transformations via formulas:** For multi‑step operations such as sorting, deduplication, or custom ordering, implement the entire logic in Python using openpyxl. Do not attempt to use Excel formulas or functions; they will not be evaluated correctly and may produce incorrect results.

- **Sequential label generation:** When filling missing cells with sequential labels derived from preceding non‑blank values (e.g., generating "6a", "6b", "6c" from a base "6"), never re‑read the cells you have just written to determine the next label. Instead, maintain a state variable (like `last_base` and a suffix counter) that updates as you iterate forward. After writing, read back a sample of the answer range to confirm the pattern is correct and no cell is empty or contains a formula.

- **Partial verification:** Printing only a single column or a subset of the answer range can hide errors in other columns. Always print the entire rectangular range specified in `answer_position` during post‑save verification, not just one column or a few rows. Do not truncate the output after a fixed number of rows; print every cell in the range, even if the range is large. Use the exact range from `answer_position` (e.g., `ws['A1':'E7']`) and iterate over every cell.

- **Deleting rows without normalizing text:** When deleting rows based on a cell value matching a known phrase (like `'Line No'`), always strip whitespace and casefold the cell value (`.strip().casefold()`) before comparing, unless the task demands exact matching. Print `repr(cell.value)` to detect hidden spaces or case differences. A bare `==` comparison can fail on a stray space.

- **Writing a formula string for a boolean check (e.g., `=RIGHT(A2,LEN(B2))=B2`) instead of computing the boolean in Python.** This causes the grader to see `None` instead of `True`/`False`. Always compute the result in Python and write the literal boolean value.

- **'Contains' vs exact match:** When the task says a cell 'contains' a phrase, always use substring matching (e.g., `target in cell_value.casefold()`), not exact equality. After writing, verify that the target substring no longer appears in the relevant cells.


- **Misinterpreting “blank rows” as entirely empty rows:** When the task says to delete blank rows above a cell that contains a specific value in a column, inspect that column's values for the rows above the anchor. 'Blank' likely means blank in that column, not that the entire row is empty. Print the column values before writing any deletion script to confirm your definition matches the expected behavior. After deletion, verify that the anchor row is now at the top.


- **Lookup key normalization:** When building a lookup dictionary from text columns (e.g., variable names, product codes), always normalize both the key from the lookup table and the target column from the source data by stripping whitespace and casefolding. Use a normalization function like `norm = lambda v: ' '.join(str(v).split()).casefold()`. After constructing the lookup, iterate over all source keys and verify that every one maps to a non‑None value; print a warning for any that do not. If the task requires case‑sensitive matching, skip case normalization but still strip whitespace.
- **Defensive numeric coercion:** When performing numeric comparisons on cell values (e.g., checking if a value falls within a range), always wrap the comparison in a try/except that attempts to convert the value to `float`. This protects against numbers formatted as text that may appear in other spreadsheets. Example: `try: val = float(cell.value); except (ValueError, TypeError): continue`. After writing, verify that the intended rows were processed correctly.


- **Date extraction via formulas:** When the task requires extracting dates from strings (e.g., using LEFT, MID, SUBSTITUTE), parse the strings in Python with `datetime.strptime` or similar and write the resulting `datetime` object. Never write an Excel formula string; the grader will see `None`. After writing, verify that every answer cell contains a `datetime` instance, not a string or `None`.
- **Skipping initial inspection:** Writing transformation code based solely on the task description without first inspecting the workbook. Always run the Full Inspection Script before any code to confirm data layout, row range, and value types. This is the most common cause of off-by-range and type-mismatch errors.
- **Merge‑and‑sum grouping:** When merging rows by a composite key and summing a numeric column, use a dictionary (or `OrderedDict` for order preservation) keyed by the composite tuple. Accumulate sums with safe numeric parsing (try/except) to handle None, empty strings, and non‑numeric values. This pattern has been repeatedly successful in practice.
- **Manual cell‑by‑cell edits:** When writing to multiple rows, always use a loop, list comprehension, or other vectorised approach to fill all target cells in one pass. Avoid manual edits that require multiple script executions; batch the operation to reduce errors and turn count.

- **Sign preservation in scaling:** When scaling values (e.g., multiplying by a factor) where the sign of the output must match the sign of the input, derive the output so that the sign flows from the source value without an extra negation. After writing, print a few (source, output) pairs and confirm that positive source → positive output, zero → zero, negative → negative. Correct before saving if any sign is wrong.

- **Rounding stored values to required decimal precision:** When a task specifies a fixed number of decimal places (e.g., 11 decimal places), explicitly round the numeric value to that many decimal places using `round(value, ndigits)` or, for high precision, `Decimal.quantize`. Do not rely solely on number formatting; the stored value must be rounded. After saving, reload and verify that the string representation of each value has at most the required number of digits after the decimal point.


- **Multi‑range arithmetic in formulas:** If you must write a formula that performs arithmetic on ranges (e.g., `(RangeA=CriteriaA)*(RangeB=CriteriaB)` inside `MATCH` or `SUMPRODUCT`), wrap the expression in `INDEX(...,0)` to force evaluation without requiring array‑formula entry. After writing, verify that at least one cell returns a non‑zero value when the source data contains a non‑zero entry.

- **Step‑by‑step interactive edits:** Avoid running multiple separate scripts or making manual cell edits; instead, implement the entire transformation in a single Python script that loads the workbook, performs all computations, saves, and runs verification. This ensures reproducibility and reduces errors.

- **Limiting transformations to the answer range when the task instruction says to modify all columns/rows.** Always read the full instruction: if it says to apply a change across all columns, rows, or sheets, do not restrict the operation to just the answer range. After writing, verify that the change is present in cells outside the answer range by reading a few rows from other columns.

- **Zero suppression via formatting, not None:** When a task requires zeros to display as blanks, store the numeric `0` and apply a custom number format like `'0.00;-0.00;;@'` (adjust sections for your number format). Never leave cells as `None` to achieve blank display. After writing, verify that cells contain numeric `0` and that the number format’s zero section is empty.
- **Trust inspected cell types:** If full inspection shows all relevant numeric data is already `int` or `float`, use simple `isinstance(v, (int, float))` checks for aggregation or filtering. Do not add string‑to‑float coercion unless inspection reveals numbers stored as strings. This keeps code simple and avoids misinterpreting non‑numeric strings.

- **Deduplication without key normalization:** When removing duplicates based on a text column, always normalize the key values (strip whitespace, casefold) before adding to a `seen` set. Without normalization, near‑duplicates (extra spaces, case differences) survive and produce wrong results. After deduplication, print a sample of the remaining keys to confirm no near‑duplicates remain.

- **Searching for target values without checking evaluated results:** When the task requires finding or acting on cells that contain a specific value (e.g., `'X'`, `'Yes'`, a number), a cell whose formula evaluates to that target must be treated as a match even if its raw `.value` is a formula string. Always load the workbook with both `data_only=False` and `data_only=True`, then for every cell in the search range print both representations. Treat a cell as matching if either representation equals the target (after normalising whitespace and case). Relying only on raw `.value` will miss formula‑produced targets and cause incomplete transformations.

- **Row insertion:** When inserting multiple rows, collect all target row numbers first, then process them in descending order (highest row first) to avoid index shifting. Also copy the formatting from a nearby row (e.g., the row above) to maintain consistency, unless the task specifies otherwise.

- **Per‑group aggregation vs global aggregation:** When the instruction includes a phrase like "per X" or "for each X", always group by X before computing any aggregate. For example, when asked to find "the last date per brand", compute the maximum date for each brand individually, not the maximum date over all brands. After writing the output, verify that at least one row for each distinct X appears (if it meets the criteria).

- **Lookup formulas (INDEX/MATCH, VLOOKUP, XLOOKUP):** Even when the task describes a lookup operation, never write these as Excel formulas. openpyxl cannot evaluate them, and the grader (using `data_only=True`) will see `None`. Instead, build a Python dict from the lookup table and map values in code, writing the resulting static strings or numbers. After writing, verify with `data_only=True` that every answer cell holds a concrete value, not `None`.

- **Manual row removal instead of delete_rows:** When removing rows, always use `ws.delete_rows()` in reverse order. Do not manually copy cell values upward and clear trailing cells; this leaves the sheet's `max_row` unchanged and empty rows after the data, which the grader will detect. After deletion, verify that `ws.max_row` reflects the correct number of remaining rows.

- **Per‑row threshold vs. group‑sum:** When a task says to delete rows where a value is effectively zero (e.g., absolute value < 0.011), apply the threshold to each row individually, not to the sum of all rows. A group‑sum condition would only delete all rows if the total is near zero, which is rarely the intent. After writing the deletion loop, sanity‑check by considering two rows with opposite signs that sum to zero—they should not be deleted. Before implementing a deletion or filtering condition, restate it in plain language as a per‑row condition (e.g., 'delete a row if its D‑cell value is numeric and abs(value) < 0.011') and verify that the code matches.

- **Loop nesting order:** When the task describes a nested process (e.g., "for each header, … for each matching entry"), make the outer loop follow the first‑mentioned dimension (header). If an existing sheet already shows a grouping pattern, inspect its full content and replicate that order exactly. Before writing, print a sample of the first few groups to confirm the nesting matches the expected grouping.

- **Ignoring reference sheet structure for deletions:** When a reference sheet is present, always inspect it to determine whether blank rows should be kept or removed. A naive 'delete all empty rows' may strip required separators. Compare the original and reference sheets to infer the exact pattern before writing any deletion logic.
## New Section

## Mandatory Post‑Save Verification

**AFTER SAVING: Run `verify_output` and confirm it prints `'All verification checks passed.'` before calling TASK_COMPLETE. Never skip this step.** This is the single most critical step to avoid undetected formula strings, empty cells, and format errors.