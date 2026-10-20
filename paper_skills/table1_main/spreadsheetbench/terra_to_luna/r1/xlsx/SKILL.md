---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow





**CRITICAL: NEVER write Excel formulas into any cell unless the task explicitly says 'write a formula'. Always compute values in Python and write literal results.**
## Mandatory Gates

**STOP — Do not write any transformation code until you have completed both gates.**

1. **Inspection Gate:** Run a read‑only inspection script that prints the exact cells and ranges you plan to modify (headers, data rows, answer range). You must see this output before writing any code. Skipping this gate will cause failure.
2. **Verification Gate:** After saving, reload the workbook and print every cell in the answer range with its value and type. You must see this output and confirm it is correct before calling TASK_COMPLETE. Skipping this gate will cause failure.


**CRITICAL: Never skip inspection or verification.**

**CRITICAL: NEVER write Excel formulas into any cell unless the task explicitly says 'write a formula'. Always compute values in Python and write literal results.**
Use `openpyxl` for all workbook reading, writing, and manipulation; do not use other spreadsheet libraries.
This script‑based approach (openpyxl + saving to the exact output path) has been proven successful across many tasks; never deviate from it.
**Before writing any code, open the workbook twice: once with `data_only=False` to see formulas, and once with `data_only=True` to see cached values. For every cell in the used range, print its coordinate, value, type, and formula (if any) from the `data_only=False` load, and its cached value from the `data_only=True` load. This is the mandatory first step; do not proceed without it.**

**If after inspection you consider writing an Excel formula, STOP: compute the result in Python and write the literal value instead. Only write formulas if the task explicitly says 'write a formula'.**
After saving, reload the workbook with `data_only=True` and print the answer range cells (value, type) to confirm they are as expected. If any cell contains a formula string or is None (when a value is expected), raise an error and fix the output before calling TASK_COMPLETE. These steps are mandatory for every task.


1. **Run a standalone read‑only inspection script** (see Inspection section). Do not combine this with the transformation script. Print sheet names, dimensions, and for every sheet print the coordinate, raw value, and Python type of every cell (if ≤500 rows) or the first 50 and last 50 rows (if larger). Include the destination sheet. **Never skip this step, even for simple‑looking tasks.**
**Do not write any transformation code until you have completed the inspection script and printed its output.** If you start writing the transformation script without having done this, you are making a mistake.
2. **Plan and execute** the required transformation.

- **Before writing, determine whether the task explicitly requires Excel formulas. If not, compute all output values in Python and write them as literal values. Never write formula strings (e.g., `=IF(...)`, `=VLOOKUP(...)`) into cells.**
- Only write Excel formulas if the task explicitly states that the output cells must contain formulas (e.g., 'write a formula in cell X'). If the task asks for a calculation result, compute it in Python and write the literal value, even if the task description mentions spreadsheet function names like SUMIF, COUNTIF, or VLOOKUP. Do not write those functions as formulas.
- - **Before writing any data, parse the `answer_position` to identify the target sheet and range. If the target sheet does not exist in the workbook, create it with `wb.create_sheet(title=sheet_name)`. If it exists, clear the entire answer range (set all cells to `None`) to remove stale data. Do not assume the output should go to the source sheet unless the sheet names match exactly.**
Use a single, self-contained Python script with **openpyxl** to implement the transformation. The script should read the input workbook, perform all required logic, and save the output at the prescribed path in one shot. This ensures reproducibility and avoids multi-step manual editing.
3. **Save** the output file.

**After saving, you MUST reload the workbook and verify the answer range. Do not skip this step; file size alone is not verification.**

4. **Re-open and verify** – reload the saved workbook, print every cell in the exact answer range with its value and type, and confirm they are correct literal values (not formula strings, not None). Only after this verification passes, call TASK_COMPLETE. Do not skip this step; it is the final gate before completion.


- If the task is phrased as "How can I create a macro/formula that does X?", treat it as a request to apply X to the workbook and save the result, not to provide code. Deliver the transformed workbook, not the macro/formula text.


- **Multi‑sheet processing:** If the task specifies a range of sheets (e.g., "beginning with sheet 'BR1' onwards"), implement a loop over all sheets from that starting point, even if the current workbook has only one sheet. Use `wb.sheetnames` to locate the starting sheet index and iterate over `wb.worksheets[ start_index : ]`. After writing, verify the sheet‑selection logic would work for any number of sheets.

**Critical: The verification step must be integrated into the transformation script. After saving, the script must reload the workbook and run the checks described in the Verification section (print answer‑range cells, confirm no formula strings, sanity‑check ordering/groups). If any check fails, raise an error. Do not call TASK_COMPLETE until this automated verification passes. Never treat verification as a separate optional step.**

When you need to find rows that contain a specific marker, use the displayed (cached) value from the `data_only=True` load, normalized with `.strip().upper()` (or `.casefold()`) to avoid missing markers due to formulas, spaces, or case differences.
## Inspection


Before any manipulation, perform a full inspection of every sheet. Print sheet names, dimensions, and a representative sample of non-empty cells (first few rows and last few rows; for sheets with ≤500 rows, print all rows) with their coordinates, data types, number formats, and formula strings (if the cell contains a formula).

- When inspecting a data range, always print the last 5 rows (or the last row if fewer) to confirm the exact row boundaries and data types, even if you plan to process only a subset. For larger sheets (>500 rows), print the first 50 and last 50 rows and programmatically scan the rest for headers, totals, and special rows. Do not truncate the preview to a small number of rows (e.g., `max_row=min(ws.max_row, 8)`); confirm that the number of rows printed equals `sheet.max_row`.
If the answer sheet already contains data, print every row (no truncation) to see the expected ordering and structure. This is critical even if the sheet has >500 rows; print all rows or at least the full range that will be used. This reveals layout, headers, date formats, and prevents off-by-one errors and hard-coded range assumptions. Do this as the first step for every task.

- Always locate the header row dynamically. Search for a known label (e.g., 'Row Labels') across all rows and columns; never hardcode a row number. Then search for the target column header only within that row. After any layout changes, confirm the header row still contains the expected label.
- Before writing any lookup formula, compare the lookup value against the actual values in the lookup column. If there are systematic mismatches (e.g., year mismatch in dates), adjust the matching condition (e.g., month-only match).
- Perform a dry-run check: apply the formula logic to the reference value and one or two sample rows to confirm it returns a non-None, non-error value before embedding it in the workbook.

- When constructing formula ranges, always use `ws.max_row` (and `ws.max_column`) to determine the range bounds dynamically. After writing, print the formula string to confirm it uses the correct bounds (e.g., `$B$3:$B$<actual_max_row>`).

- When inspecting, note any existing formulas (cell values starting with '=') to understand dependencies and avoid overwriting them unintentionally.


- After inspection, explicitly confirm that the columns you plan to operate on exist in the inspected sheet and that you have correctly mapped their column indices before writing any manipulation code.
- When the task specifies a target range (e.g., `answer_position`), print the entire region (all rows and columns) before any modification, including headers and label rows. Verify that every expected label is present and note which cells are empty. This reference helps target modifications precisely and prevents accidental overwrites of structural cells.
 Also scan for blank-row-separated segments and repeated header rows that indicate grouped data; use this structure to design your transformation logic. After identifying repeated header rows, code explicit checks to skip or handle them (e.g., `if row_values == header_values: continue`).
- Before writing any column‑level business logic (e.g., filtering rows by cell content), print the unique or sample values of the target column. Verify whether the text to match appears as an exact match or as part of a longer string, and check for case variations. Use exact equality only if the cells match exactly; otherwise use substring containment (e.g., `'X'.casefold() in cell.value.casefold()`). Prefer `str.casefold()` over `.lower()` for robust case‑insensitive matching.. After implementing the logic, print the subset of rows that will be modified (indices and values) and manually confirm all intended rows are captured and no unwanted rows are affected, before saving.
- When a task involves matching or filtering against a list of criteria (e.g., a column of category names), inspect the full criteria range. Print every non‑empty cell's value and data type, confirm the exact start‑ and end‑row, and note any blanks. Never assume a fixed range like F10:F14.

- When the task describes a mapping that involves multiple columns and provides an explicit example (e.g., "if column J contains the number 1, then this result should reflect in cell I8"), manually trace the example using the actual data to confirm the logic before writing code. After writing, spot‑check that exact cell against the example.

- When inspecting the answer range, print the `.value`, `type(.value).__name__`, `.number_format`, and `.alignment` for every cell (or at least the first and last few rows) to understand the data types, formats, and alignment you must handle. Use this to adapt your transformation code.

- When the task involves fixing existing formula errors (e.g., #N/A, #VALUE!), inspect every sheet that supplies data to the failing formulas. Print sample values from lookup columns and compare them to the values used in the formulas. Identify mismatches (extra spaces, case differences, date mismatches) and correct them either by adjusting the formula or by writing computed values directly into the target cells. After fixing, verify that the answer range contains concrete data, not error values.


- When the workbook contains a reference or example sheet (e.g., 'Manual Result', 'Expected'), inspect it first to deduce the exact required output structure, ordering, and values. Use it as the ground truth for your transformation logic and verification, not as an afterthought.
- Before writing any formula or modifying cells that may be formula‑dependent, load the workbook with `data_only=False` and `data_only=True` to inspect the formula texts and their evaluated results for the target column and any referenced columns. Print both the formula and the computed value for each relevant cell. This reveals dependencies and helps avoid breaking existing calculations.
- When planning any data cleaning that involves string operations (regex, replace, strip), first identify which cells contain strings vs numbers. Print a summary of data types in the answer range. Only apply string transformations to cells where `isinstance(cell.value, str)` is True. Never convert numeric cells to strings by applying string methods indiscriminately.
- Before writing any transformation code, compare the observed sheet dimensions and data types against the task's described range and data format. If they mismatch, flag it and re-inspect before proceeding.
- When a task requires identifying a pattern (e.g., data rows occurring at a fixed interval), scan the relevant column(s) for non‑null cells and print their coordinates. Use these coordinates to determine the exact starting point and interval, rather than relying on visual inspection of only the first few rows.

- When collecting data rows, filter out any row whose values in key columns match typical header labels (e.g., `'item'`, `'name'`, `'ref'` case-insensitively). After building the data list, print a sample to confirm no header text appears as data.

- When extracting data from a sheet (e.g., building a lookup table or collecting unique pairs), scan all rows from the first data row to `ws.max_row`, not just a contiguous block. Use a seen‑set to deduplicate entries and preserve first‑appearance order unless otherwise specified.


- After printing, compare the observed types and values against the task description's preview to detect discrepancies (e.g., dates as strings vs datetime objects). If the actual data types differ, adjust your code accordingly.


- When a task describes a logical condition involving multiple columns and provides example rows, examine those rows carefully to deduce the precise predicate (e.g., suffix match, substring check) before writing any code. Test the deduced predicate against the given examples.

- When a sheet has a known header row (e.g., row 2), build a header mapping before any manipulation: `headers = {str(ws.cell(header_row, c).value).strip(): c for c in range(1, ws.max_column + 1)}`. Then verify that every required header name is present in the mapping (e.g., `assert 'Last Name' in headers`). Use header names (e.g., `headers['Last Name']`) to access columns, never hard‑coded column indices.


- **Proven practice:** After loading the workbook, output the values of every row and column that will be involved in the operation (not just a sample). This confirms the exact data range and has been shown to prevent off‑by‑one and column‑misalignment errors across tasks. Do this even when the range seems obvious from a quick glance.
- **Proven practice:** When printing sheet contents during inspection, use exact range strings (e.g., `ws['A1:G20']`) rather than row‑by‑row loops to avoid truncated output. Print the full header row(s) and column‑A labels of every sheet you will reference, and confirm the position of lookup values and data boundaries before writing any code.

- **Merged cells:** If the task mentions unmerging or you need to write to cells that could be merged, inspect every sheet for `ws.merged_cells.ranges`. Print all merged ranges, then unmerge them with `ws.unmerge_cells(str(rng))` before any other manipulation. This prevents write failures on merged cells.

- For small sheets (≤500 rows), print every cell's value and type; this comprehensive inspection has been proven to prevent misinterpretation and is a critical success factor.

Even if the task description includes a preview of the data, you must still load and inspect the workbook. The preview may be truncated or outdated.

- **Proven practice:** When inspecting cell values, explicitly check for non‑breaking space characters (`\\xa0`) and other invisible placeholder characters that may appear as blanks but are not `None`. Print `repr(cell.value)` for a sample of seemingly‑empty cells to reveal hidden characters. This prevents misinterpreting placeholder cells as truly empty.

- **Proven practice:** For the mandatory initial inspection, use `ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=ws.max_column, values_only=False)` to obtain Cell objects. Print each cell's coordinate, value, type, number_format, and formula (if any). This gives full visibility into the workbook. For subsequent quick scans where only values are needed, use `values_only=True` for efficiency.
- When the task involves filtering or conditional formatting based on cell formatting (e.g., fill colour, font weight, borders), print the relevant formatting attribute for every cell in the inspected range (e.g., `cell.fill.fgColor.rgb`, `cell.font.bold`). This ensures all qualifying cells are identified before writing.

- **Proven practice:** Begin every spreadsheet task by loading the workbook and printing all sheet names and the complete content of every sheet (or a representative sample for large sheets) before any manipulation. This full-state inspection has been proven to prevent misinterpretation and is a critical success factor.
## Writing Output


Always create or use the exact sheet name specified in `answer_position`. Do not substitute an existing sheet with a different name. After writing the workbook, print `wb.sheetnames` to confirm the required sheet exists.


Confine modifications to the required cells only; do not alter formatting, add extra sheets, or change the structure of the workbook unless explicitly required.

When writing result tables, ensure **every** cell in the target range receives an explicit computed value. Never leave a cell empty or set it to `None`. If a comparison or calculation cannot be performed, use a sensible default: `False` for booleans, `0` for numbers, empty string for text, depending on context.

### Row Deletion


When deleting rows based on blank conditions, iterate from the last data row down to the first non-header row (e.g., `for row in range(max_row, 1, -1)`). To check if a row is fully blank across a set of columns, use a condition that treats both `None` and empty strings as blank: `all(v is None or (isinstance(v, str) and v.strip() == '') for v in row_values)`. This prevents index shifts and correctly handles cells that appear empty but contain whitespace.

- Alternatively, collect row indices and delete them in reversed order (e.g., `for r in reversed(rows): ws.delete_rows(r, 1)`). Both approaches are proven safe.

- If the task specifies blank rows in relation to a particular column (e.g., "blank rows above 'Code' in column A"), define blankness as an empty cell in that column only, not an entirely empty row. Before executing deletion, print a sample of rows with a flag showing which would be deleted, and verify that the flagged rows match the intended rows (i.e., rows where the key column is genuinely blank).
- Before deleting, print the list of row indices you plan to delete (in descending order) to confirm no index shifting will occur.
### Column Deletion
When deleting columns in-place, iterate from the highest column index down to 1 (or use `reversed(columns_to_delete)`). This prevents index shifting of columns yet to be processed. Example: `for col_idx in range(ws.max_column, 0, -1): ws.delete_cols(col_idx)`.

When deleting rows, iterate from the last data row down to row 2 (preserve the header): `for row in range(max_row, 1, -1)`. Before any string operation, guard with `isinstance(value, str)` to avoid crashes on non‑string cells (e.g., numbers, None).

- Unless the task explicitly requires Excel formulas, write literal computed values (numbers, strings, booleans) into cells. Do not insert formula strings like COUNTIFS, IF, VLOOKUP, etc. This avoids unevaluated formulas that result in None when read back.
- **STOP CHECK — Before assigning any cell value:** If the string you are about to write starts with `=` (e.g., `'=SUMIF(...)'`, `'=VLOOKUP(...)'`, `'=COUNTIF(...)'`), you are making an error. Unless the task explicitly says "write a formula", compute the result in Python and write the literal value. Concrete example: instead of `ws['D2'] = '=SUMIF(A:A,111111,B:B)'` which produces `None` when read back, compute `total = sum(row[1] for row in data if row[0] == 111111)` and write `ws['D2'] = total`.
- **When constructing formulas that involve multi‑criteria MATCH with boolean multiplication, always wrap the product inside `INDEX(…,0)` to avoid requiring array entry.** Example: `=MATCH(1,INDEX((Sheet2!$A$3:$A$20=$A$14)*(Sheet2!$B$3:$B$20=$A16),0),0)`. This ensures the formula works without Ctrl‑Shift‑Enter.
  - This also applies to simple cell‑reference formulas like `=A25`. To copy a value from another cell, read the source cell's `.value` in Python and assign it directly. Never write a formula that references another cell.
- Before writing result data, clear the entire output range (set every cell to `None`) to remove any stale data.
  **Conditional writes:** When writing values only to rows that meet a condition, clear the entire column or answer range first, then write only to matching rows. This ensures non‑matching rows are blank (or contain the intended default) and no pre‑existing values remain. After clearing, verify at least one cell in the range is `None` before populating.

- As an alternative to clearing the range, delete the existing output sheet and create a fresh one with the same name using `create_sheet()`. Both approaches are proven to prevent stale-data contamination.

- When applying the same formula or logic to multiple rows, use a loop over the row indices (e.g., `for r in range(3, 7): ws[f'H{r}'] = ...`). Substitute row-dependent references (like `H{r}`) each iteration. This ensures uniform application and reduces manual errors.


- When clearing the output range, use the exact row and column boundaries from `answer_position` (e.g., A1:D7), not the sheet's current `max_row`/`max_column`. This guarantees all cells in the target rectangle are cleared, preventing stale data from remaining in rows beyond the current used area.
- Save the workbook to the exact `output_path` supplied in the task; do not derive a different path or filename.

- When filling values from a source lookup into a target column, always **overwrite every cell** in the target block, not only blanks, unless the task explicitly says to keep existing values. After writing, verify that rows satisfying the matching condition have new values (compare to original).

- When the task provides an `answer_position` range, modify **only** those exact cells. Do not extend writes to adjacent columns or rows. After saving, verify that no cell outside the answer range has been altered (print a few surrounding cells to confirm).

- If the `answer_position` range includes row 1, inspect that row for header labels. If headers exist, either exclude row 1 from the clearing and writing loop, or explicitly re‑write the header values after clearing. After writing, verify that row 1 still contains the expected headers.


- Immediately after saving, print the output path and file size (e.g., `print(f'Saved to {output_path}, size: {os.path.getsize(output_path)} bytes')`) to confirm the file was written and is non‑empty.


- When a task requires finding a combination of values that sums to a specific target or range, use exhaustive subset enumeration (e.g., `itertools.combinations` or bit‑mask iteration) to identify the exact subset. After identifying the subset, verify that the sum of the chosen cells exactly matches the target (and falls within any required range) before writing the answer.
- When copying data from a source range to a target range and the task requires maintaining original formatting, copy both the cell value and all formatting attributes (number_format, font, fill, alignment, border) using `copy.copy()`. For example: `new_cell.font = copy(src_cell.font)`, `new_cell.fill = copy(src_cell.fill)`, etc. Do not write formulas unless explicitly required.

- When performing arithmetic on floating‑point values (e.g., subtraction of a fixed threshold), round the result to the precision implied by the source data (e.g., `round(value - 40, 2)`). After writing, verify the answer range does not contain numbers with excessive decimal digits (e.g., `12.619999`). If found, re‑compute with rounding and re‑save.

- If the task specifies particular output columns within the answer range (e.g., 'output in columns G and H'), only write to those columns; do not clear or overwrite other columns. Before writing, print the current values of every column in the answer range to identify which columns to preserve.


- **Before saving**, scan every cell in the answer range(s) for strings that start with `=`. If any are found, replace them with the computed literal value and re‑check. Example:
  ```python
  for row in ws[answer_range]:
      for cell in row:
          if isinstance(cell.value, str) and cell.value.startswith('='):
              raise ValueError(f'Formula string found in {cell.coordinate}: {cell.value}')
  ```
  This guard ensures you never accidentally save formula text when the grader expects concrete values.

- **Template sheets:** When the answer sheet is a pre‑built template with existing headers and formatting, clear only the data rows of the answer range. Never overwrite or reformat the header row unless the task explicitly requires it. After writing, verify that the header row still contains the original values and formatting.


- **COUNTIF / SUMIF / VLOOKUP example:** If the task says "use COUNTIF to count the number of positive values", compute the count in Python (e.g., `count = sum(1 for v in values if v > 0)`) and write the integer. Do **not** write `'=COUNTIF(...)'`. The same principle applies to any spreadsheet function mentioned in the task description—always compute the literal result in Python.


- **Concrete example:** To derive a value from another cell (e.g., first letter of F10 plus "."), read the source cell's `.value` in Python, compute the result, and write the literal. Do NOT write a formula like `=IF(F10<>"",LEFT(F10,1)&".","")`. Correct:
  ```python
  src_val = ws['F10'].value
  result = src_val[0] + '.' if src_val else ''
  ws['F7'] = result
  ```
  This ensures the grader sees the computed string, not `None` from an unevaluated formula.
- **String concatenation (proven):** When the task requires joining field values (e.g., concatenating two columns), build the result string in Python (`f'{val1}{val2}'`) and write the literal. Never use `=A2&B2` or `=CONCATENATE(...)`. After writing, verify every cell in the answer range is a plain string, not a formula.

- **Proven practice:** When merging rows and summing a numeric column based on a composite key (e.g., columns A-C), use an ordered dictionary (`dict` in Python 3.7+) to group rows by the composite key while preserving first‑seen order. Accumulate the numeric total for each group and write the aggregated rows back. This avoids VBA and yields clean, repeatable results for range‑based answer cells.

- **Efficient data extraction:** When reading values from multiple sheets for aggregation, use `iter_rows` with `values_only=True` and filter with `isinstance(v, (int, float))`. This avoids formula strings and produces ready‑to‑write literal results.

Do not write VBA code, macro strings, or any formula-like text; assign the computed literal value directly.

### Row Insertion

- When inserting multiple rows, iterate from the largest row number down to the smallest to avoid index shifting.
- After each insertion, copy formatting attributes (`_style`, `number_format`, `alignment`, `protection`) from the original marker row (now one row below the new blank row) to the newly inserted blank row. Use `copy.copy()` for each attribute.
- After all insertions, reload the workbook and spot‑check a couple of inserted rows by printing their cell style and row height to confirm formatting transfer.

- **Pre-filled answer sheets:** If the answer sheet already contains pre-filled data, that data signals the expected output sequence. Your output rows must preserve that order. After writing, verify that the sequence matches the original pre-filled rows (excluding any rows you cleared).

- **Exception to the “fill every cell” rule:** When the task asks to show only the top‑N items per category across multiple columns, write labels only in the cells that correspond to those top items, leaving the other cells empty. After writing, verify that the number of filled cells equals the expected count (e.g., N items × number of categories).
## Verification


After saving, always reload the workbook and inspect every cell in the answer range(s) from `answer_position`. Do not skip this step, even if the output appears correct.

**GATE: Your transformation script must not end at `wb.save()`. After saving, the script must reload the workbook and print every cell in the answer range. A script that ends at `wb.save()` is incomplete — do not call TASK_COMPLETE until reload+print runs and passes.**
**If any printed cell value starts with `=` (a formula string), you have not completed the task. Fix the output (re-compute and write literals) and re-verify before calling TASK_COMPLETE.**

 Immediately after reloading, print every cell in the answer range with its value, type, and formula status. Do not rely on file size or path alone; you must see the actual cell contents.
**Before calling TASK_COMPLETE, you must print the answer range and run at least one automated correctness check (e.g., compute a list of rows that violate a known data-integrity rule and assert it is empty).**

- Always verify the exact cells specified in `answer_position`, not a generic range like 'column A rows 1..max_row'. Use the start and end rows/columns from `answer_position` to print and inspect the target cells.
- For each answer range, print the values using the exact boundaries, e.g., `for r in range(start_row, end_row+1): print(ws.cell(r, col).value)`. This ensures you are checking the grader's target cells.

- Before re‑opening, confirm the output file exists and has non‑zero size (e.g., `os.path.exists(path)` and `os.path.getsize(path) > 0`).


After every save, reload the workbook and print the sheet dimensions (`ws.max_row`, `ws.max_column`), the first few and last few rows, and the target answer range plus surrounding context. Confirm that the visible values match the expected effect and that the workbook was written to the exact required output_path.

After writing the final workbook, reopen it with `data_only=True` and read the answer range. Verify that every cell contains a non‑None, concrete data value (number, date, plain text), not a formula string (i.e., does not start with '='). Example: `wb = openpyxl.load_workbook(path, data_only=True); val = ws['E5'].value; assert val is not None and not (isinstance(val, str) and val.startswith('='))`.
If any answer‑range cell contains a formula string, immediately re‑write the output with literal values before declaring the task complete.

Print each cell's value and type. For numeric answer ranges, confirm all cells are numbers (not bool) with `all(isinstance(ws.cell(r,c).value, (int, float)) and not isinstance(ws.cell(r,c).value, bool) for r,c in answer_range)`.

If the task expects formulas, reload with `data_only=False` and verify that formulas appear in the output cells. If plain values are required, reload with `data_only=False` and check that cells have numeric type (`'n'`), not formula strings (`'s'`). Re‑examine the writing step if any cell contains a formula string when plain values were expected.

Only declare completion after confirming the answer range meets all requirements.

After writing, retrieve the exact cell ranges from `answer_position` and verify each one. For every range, print the number of non‑None cells and confirm it is greater than zero. If the task involves aggregation, scan for a row containing "TOTAL" (or equivalent label) with a numeric sum, not an empty row. Use `wb = openpyxl.load_workbook(out_path, data_only=False)` and inspect each range explicitly (e.g., `ws[rng]`).
For formula tasks, after saving, reload with `data_only=False` and verify that each target cell has `data_type == 'f'`. Print the formula text to confirm it matches the intended calculation structure.
- **After reloading, also verify that the formula strings contain the expected sheet names and absolute anchors (e.g., `$` signs).** Print the formula text and assert that expected substrings are present (e.g., `'Sheet2'`, `'$A$3'`). Do not assume the writing succeeded as intended; re‑reading the formula strings is mandatory.


After any destructive operation (column/row deletion, sheet deletion), reload the workbook and explicitly verify the operation's effect: scan the relevant area to confirm the removed items are absent and the remaining structure is intact.
- If you performed a column-wide modification, explicitly verify that the header row and any non-data rows (summary, labels) still contain their original contents and were not overwritten with the new constant.

- After a fill operation, reload the original workbook (or a copy saved before modification) and compare the target range in the output to the same range in the original. For rows that should have been updated, the values must differ. Print a sample of before/after pairs to confirm.

- For each answer range, print each cell's coordinate, value, type, and whether it is a formula (starts with '='). Confirm all are non‑None, non‑formula values. Example: `for row in ws[answer_range]: for cell in row: print(cell.coordinate, repr(cell.value), type(cell.value).__name__, 'formula' if isinstance(cell.value, str) and cell.value.startswith('=') else 'literal')`.

- When verifying, print the answer range alongside any relevant lookup or key column (e.g., the column used for matching) to visually confirm correct placement.

If the task specifies a required number format (e.g., `'m/d/yyyy'`, `'0'`), after writing, reload the workbook and print each cell's value, type, and number_format. Verify that the format matches the requirement and the value is the expected numeric result. Print a clear pass/fail summary for all answer range cells before calling TASK_COMPLETE.

- For tasks involving cell fills, verify that the fill colour matches the expected opaque ARGB value (e.g., `cell.fill.fgColor.rgb == 'FF00FF00'`). Print a pass/fail for each cell.


Only after all verification checks pass, call TASK_COMPLETE. If any check fails, fix the issue, re-save, and verify again.
- If a reference sheet exists, after saving, reload the output workbook and the original workbook, then compare the answer range cell-by-cell against the reference sheet. Print a pass/fail summary for each cell. Only declare completion when all values match exactly (same type, same formatted value).
- After writing, run a verification script that not only reads back values but also tests at least one logical invariant derived from the task (e.g., ranks are consecutive within groups, sums match expected totals, no duplicate keys). Print the results of these invariant checks before issuing TASK_COMPLETE.
  - **For conditional writes:** verify that every row that meets the condition has the correct value, and that every row that does **not** meet the condition is empty (or has the expected default). Print a summary of any mismatches.
- After data cleaning, reload the output workbook and verify the type integrity of the answer range. For each cell that was originally numeric (int/float), confirm it remains a numeric type, not a string. Print a before/after comparison of types for a sample of cells. If any numeric cell became a string, re‑run the cleaning logic with proper type guards.

- For tasks involving sorting or ordering, after reloading, iterate over every non‑blank segment in the answer range and programmatically verify the order. For ascending sorts, assert that consecutive values are strictly non‑decreasing (case‑insensitive for text). Print a pass/fail for each segment. If any segment is out of order, fix and re‑save before declaring completion.

- When the answer is a single computed value (count, sum, etc.), confirm the cell contains the actual result (e.g., a number or string), not a code snippet or formula. Print the cell’s type and value to verify it matches the expected output type.

- After writing, verify that any columns within the answer range that were not designated for output still contain their original values (compare to a before‑save snapshot).

- When copying cells, verify that the destination cell's `number_format` matches the source cell's for any formatted columns (especially dates). Print a comparison for a sample of cells before declaring completion.

Never rely on print statements from the transformation script as proof of correctness. Only the reloaded workbook's cell values and formatting count. After saving, you must reload and inspect the actual cells.


- After modifications, print **every cell** in the exact answer range with its coordinate, value, and a formula check. Example: `for r in range(start_row, end_row+1): for c in range(start_col, end_col+1): cell = ws.cell(r,c); print(f'{cell.coordinate}: {cell.value} ({"formula" if isinstance(cell.value, str) and cell.value.startswith("=") else "literal"})')`. This ensures you inspect all columns, not just the first, and catches any residual formula strings.


- After reloading, run this explicit check on the answer range to catch any lingering formula strings:
  ```python
  for row in ws[answer_range]:
      for cell in row:
          assert not (isinstance(cell.value, str) and cell.value.startswith('=')), \
              f'Formula string found in {cell.coordinate}: {cell.value}'
  ```
  If an assertion fails, re‑compute the value, write it as a literal, re‑save, and verify again.

- When verifying literal (non‑formula) results, reload with `data_only=False` and print each cell's `.value`, `.data_type`, and check that `.data_type` is not `'f'`. Example:
  ```python
  for row in ws[answer_range]:
      for cell in row:
          assert cell.data_type != 'f', f'Formula found in {cell.coordinate}'
  ```
  This catches residual formulas that string‑based checks might miss.


- After reloading, explicitly assert that no answer-range cell is `None`: `assert all(cell.value is not None for row in ws[answer_range] for cell in row), 'Found None in answer range'`. Print a pass/fail for this check alongside the formula-string check.

- After reloading, count the number of non‑empty data rows in the answer range and assert it matches the expected number of records you intended to write. Example:
  ```python
  non_empty = sum(1 for row in ws[answer_range] if any(cell.value is not None for cell in row))
  assert non_empty == expected_row_count, f'Expected {expected_row_count} rows, got {non_empty}'
  ```

- **Important:** After saving, always open the saved file with a new `openpyxl.load_workbook` call. Do not verify using the in‑memory workbook object; only the re‑opened file's cells are reliable. This guards against serialization bugs and file‑writing errors that would be invisible in the in‑memory state.

- If the task specifies any formatting (fill, border, number format), after reloading, print each answer cell's fill, border, and number_format and assert they meet the requirements. Do not rely on in‑memory state; only the reopened file's properties are reliable.


- **Per‑group output check:** If the task involves a per‑group condition, after writing, print the distinct groups present in the source data and verify that the answer range contains at least one row for each group. If any group is missing, the filtering logic is wrong.
- **Header‑label check:** After writing, read the entire answer range and verify that none of its cells contain text that matches a header label from the row immediately above the range (or from row 1 if the answer range starts at row 2). If a cell contains a header label where a data value should be, the row has been shifted; re‑write without the header row.


### Standard Verification Block

**Every transformation script must end with this block, adapted to the task's `answer_position`. Do not call TASK_COMPLETE until this block runs and passes.**

```python
import openpyxl
import os
assert os.path.exists(output_path), f"Output file not found: {output_path}"
assert os.path.getsize(output_path) > 0, f"Output file is empty: {output_path}"

# Reload the saved workbook
wb_verify = openpyxl.load_workbook(output_path, data_only=True)
ws_verify = wb_verify[answer_sheet]          # set from answer_position
print("Verification of answer range:")
for row in ws_verify[answer_range]:          # set from answer_position
    for cell in row:
        print(f"{cell.coordinate}: {repr(cell.value)} ({type(cell.value).__name__})")
        assert cell.value is not None, f"None value in {cell.coordinate}"
        assert not (isinstance(cell.value, str) and cell.value.startswith('=')), \
            f"Formula string in {cell.coordinate}"
print("All verification checks passed.")
```

Replace `answer_sheet` and `answer_range` with the exact sheet name and range string from the task’s `answer_position`. This block reloads the file, prints every answer‑range cell with its value and type, and asserts that no cell is `None` or contains a formula string (unless formulas were explicitly required). Only after this block succeeds may you call TASK_COMPLETE.
## Pre-Completion Checklist


4. You have printed the inspection output earlier in the conversation (if not, go back and run the inspection now).

Before calling TASK_COMPLETE, confirm:

1. The transformation script reloaded the workbook and printed every cell in the exact answer range.
2. All answer‑range cells contain literal values (not formula strings, not None).
3. The output file exists and has non‑zero size.
4. You have run the verification block (the script must include it after saving) and seen the printed output confirming all checks passed (e.g., "All verification checks passed."). If you have not seen this output, do not call TASK_COMPLETE.

If any check fails, fix the issue and re‑run the script. Do not call TASK_COMPLETE until all checks pass and you have seen the printed verification output.
## Pre-Completion Checklist

Before calling TASK_COMPLETE, confirm:

1. The transformation script reloaded the workbook and printed every cell in the exact answer range.
2. All answer‑range cells contain literal values (not formula strings, not None).
3. The output file exists and has non‑zero size.

If any check fails, fix the issue and re‑run the script. Do not call TASK_COMPLETE until all checks pass and you have seen the printed verification output.

## Common Pitfalls


- Leaving cells as `None` or empty when a default value is expected. Always provide explicit defaults and verify the written output.
- When building a dictionary from text-keyed lookup values (e.g., matching row labels against a data column), normalize both the stored key and the search key with `str(val).strip().casefold() if val is not None else None`. Apply the same normalization to the keys used in the target cells. This prevents silent lookup failures from whitespace or case differences.
- Skipping inspection leads to incorrect assumptions about data types, layout, or sheet names.
- Skipping verification after saving misses output errors that could have been caught by re-reading the file.
- For formula tasks, writing values instead of formulas (or vice versa) violates requirements.

- When an output sheet contains multiple side‑by‑side tables each identified by a category label in their header row, do not assume the category is always at a fixed column offset from the block’s start. Instead, scan the header row for the relevant label by its text (e.g., look for cells whose value equals one of the expected account‑type names). After extracting the category list, print it and confirm every expected category is present and none is a spurious label like "ITEM". For each source row, match the reference string against this verified list, not against a column‑offset derived from the output table’s layout.


- When sorting rows by column values, never read and write from live Cell objects simultaneously. Copy all needed cell attributes (value, style, number_format, etc.) into a list-of-dicts or list-of-tuples first, sort that list, then write back from the copy. After writing, verify the output range has the same number of data rows as the original and no duplicates (print the sorted key pairs and count unique rows).
- When applying a transformation to all values in a column (e.g., setting them to zero), do not loop over every row blindly. Use your inspection to identify which rows contain the data to modify (e.g., numeric entries) and skip headers, labels, and empty rows. Before saving, confirm the header and any summary rows remain intact.


- When writing date values, set the cell's `number_format` to the required format (e.g., `'m/dd/yyyy'`) to ensure proper display. Use `cell.number_format = '...'` after setting the value.


- When setting cell fill colours with `PatternFill`, always use an 8‑character ARGB hex string (e.g., `'FF00FF00'`), not a 6‑character hex. In openpyxl, a 6‑character string like `'00FF00'` is interpreted as ARGB with alpha=00 (fully transparent). After applying fills, reload the workbook and verify `cell.fill.fgColor.rgb` equals the intended opaque value.
- Applying string operations (e.g., `.replace()`, regex) to all cells without checking their type—this turns numeric values into strings. Always guard string operations with `if isinstance(cell.value, str):` and skip numeric cells.
- When a column may contain Excel error values (e.g., #N/A, #VALUE!), inspect the actual cell values to see how they are represented (as strings like `'#N/A'`, `None`, etc.). Never assume they appear as a specific string like `"error"`. Use Python logic to check for these representations and compute the result, then write the literal value. Do not write Excel formulas that attempt to test for error strings.

- When fixing a formula error, modify only the part that causes the error and preserve all other parts of the formula's logic, especially conditions like IF conditions. After writing, verify the output cell's value (not just the formula text) to confirm it returns the expected data.

- When a task says to "restart from the cell immediately right" (or any relative position) after a qualifying event, update your pointer to that exact relative location – not to the event cell itself. After writing the counting logic, perform a lightweight trace of the first few steps (print the current reference index/value and the index of each match) to confirm that the reset point matches the exact wording in the instruction.

- Combining inspection with the transformation script can lead to missing pre‑existing data or formulas in the destination sheet. Always run inspection as a separate, read‑only step before writing any manipulation code.

- Writing formula strings for any calculation (e.g., SUM, COUNTIF, VLOOKUP) instead of computing the result in Python. This produces blank cells when the grader reads the workbook with `data_only=True`. Always compute the value and write the literal result; openpyxl does not evaluate formulas, and the grader reads static values.


- When filling blanks in a column with incrementing suffixes that restart under each new base value, parse the numeric base from the last non-blank cell, maintain a separate counter for the suffix, reset it to 0 on each new base, and never use the previously-filled cell's full string as the next base. After writing, verify the suffix sequence is sequential (e.g., `a`, `b`, `c`...) and not accumulating (`aa`, `aaa`...).

- Hardcoding row counts or ranges (e.g., `for r in range(2, 86)`) when the number of data rows is variable. Always determine the data range dynamically by scanning for the last non‑empty row in the target column(s). Use `ws.max_row` as a starting point and loop downward to find the actual last populated row, or collect all non‑None values from the column into a list and use its length.

- When the task says a cell 'contains' a phrase, using exact equality (`==`) instead of substring containment (`in`). Always use a case‑insensitive substring check, normalizing both the search term and the target with `.casefold()` (e.g., `'to be processed'.casefold() in cell_value.casefold()`). After processing, scan the column with the same substring condition to confirm no matching rows remain.

- After row deletion, only printing the column or row count without verifying that rows matching the deletion condition are truly gone. Always iterate over the affected area post‑save, apply the same deletion condition, and print or assert that zero matching rows remain.

- When extracting a substring between a known marker and a delimiter, use string splitting (e.g., `s.split(marker)[1].split(delim)[0].strip()`) and write the extracted literal value into the answer cell. Verify the cell contains plain text, not a formula string.

- When deleting rows based on a blank condition, using a condition that checks all columns instead of only the column(s) relevant to the task. Always inspect the task description to identify the column(s) that define blankness, and print a sample of rows flagged for deletion before executing.
- When fixing a formula error (#REF!, #VALUE!, etc.), do **not** copy a value you observed in the inspection output. Instead, implement the intended computation in Python using the spreadsheet’s own data and write the literal result. Copying an eye‑matched value works only for the current data and fails when the data changes.

- When a task asks to "modify the formula" (or mentions a formula name) but the answer range is the cells' values, compute the result in Python and write the literal value. Do not write a formula string unless the task explicitly says 'write a formula'.

- When scaling numeric values to a signed target range (e.g., mapping negative inputs to a negative extreme), preserve the sign of the source value: compute `score = value * (target_extreme / source_extreme)`. Never apply an extra negative sign that would flip the sign. After writing the scaling code, sanity‑check by printing the computed score for the minimum (most negative) value; it must equal the target negative extreme (e.g., -5). Example debug print: `print('min test:', min_val, '->', score_for_min)`.

- When the task describes an operation on 'all columns' or a specific set of columns, do not limit the code to only columns that currently contain data. Use `ws.max_column` (or the exact column bounds from the task) to iterate over all required columns. After writing, print the range of columns processed to confirm it matches the task's scope.
- When reordering rows that contain helper columns with formulas, never write the raw formula string into the target sheet. Instead, parse the formula’s logic and compute the final static value from the rearranged data, then write that computed value. After writing, verify that the derived columns contain concrete values, not formula strings or None.
- When the task requires that zero values be displayed as blanks, write the numeric `0` into the cell and apply a custom number format that hides zero display (e.g., `'0.00;-0.00;;@'`). Never omit the value or write `None`. After writing, verify that all cells in numeric answer columns contain actual numbers (int/float), not `None`.
- When deduplicating rows based on a key column, failing to inspect the key column's data types and handle None/blank values can cause incorrect keep/delete decisions. Always print the key column's values with their types for the first ten rows. Normalise entries (strip + casefold for strings, convert numbers consistently) and skip None/blank cells so they are not treated as a distinct group. After loading, check for blank cells with `if any(cell.value is None for cell in key_column_cells): print('WARNING: blank cells detected')` and adjust logic accordingly.

- **Overwriting header rows:** Always identify header rows during inspection and start data loops from the row immediately below (typically row 2) unless the task explicitly requires modifying headers. After writing, verify that header cells still contain their original values.
- **Unintended string trimming:** Do not apply extra string cleaning (e.g., `.strip()`, `.rstrip()`, `.lstrip()`) beyond the exact substring extraction or manipulation described in the task. After processing, spot‑check a few cells with `repr()` to confirm no unintended whitespace changes were introduced.
- When searching for a specific marker value (e.g., 'X') that may be stored as a formula result or with varying case/whitespace, using exact equality without normalization. Always load with `data_only=True`, strip whitespace, and case‑fold (e.g., `str(val).strip().upper() == 'X'`) before comparing.
- Writing conditional values without first clearing the target range, leaving old values in non‑matching rows. Always clear the entire answer range before conditional writes.


- **Per‑group misinterpretation:** When a task says "per X" (e.g., per brand, per category), always group the data by X first, then compute the condition (last date, maximum, etc.) within each group. Never apply a single global aggregate to the whole dataset.
- **Header duplication in answer range:** Before writing data into the answer range, inspect the cells directly above that range. If they already contain header labels (e.g., "date", "brand"), do not write those labels again; start writing data values directly in the first cell of the answer range. Only add headers if the task explicitly asks for them.

- **Interpreting 'I need a formula' or spreadsheet function names as a request to write a formula string:** Even if the task description says 'I need a formula', 'use SUMIFS', or 'create a formula', always compute the result in Python and write the literal value, unless the task explicitly says 'write a formula in cell X' or 'the output must be a formula string'. The grader expects computed values, not formula strings. For example, if the task asks for a score based on rank, do not write `=IF(B1=MAX(...),6/COUNTIF(...),0)`. Instead, compute the scores in Python and write the numbers.

- When computing rank labels or concatenated strings (e.g., 'cat1', 'dog2'), compute the string in Python and write the literal value. Never use formulas like `=A1&COUNTIFS(...)+1` to build the label; the grader expects the final displayed text, not a formula string.