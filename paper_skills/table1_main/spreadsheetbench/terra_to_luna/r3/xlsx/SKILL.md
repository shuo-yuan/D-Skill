---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow


Load the input workbook with `openpyxl`, modify only the required cells, and save the result to the exact output path specified in the task.

🚫 **CRITICAL: You must first inspect the workbook by printing sheet names, dimensions, and at least 15 rows of data. Do not write any transformation code until you have seen this output.**
 Do not alter formatting of cells that are not part of the answer unless the task explicitly requires it.

If the task asks for VBA code, use Python and openpyxl to directly manipulate the workbook and write the resulting computed value (e.g., an integer count) into the answer cell, not the VBA code; the deliverable is the modified spreadsheet file with a plain data value in the answer position. When a task mentions VBA or a macro but describes a data modification (e.g., 'insert … into column Q'), the grader expects the modified spreadsheet, not the code.


🚫 **CRITICAL: Never write Excel formulas (e.g., =SUM, =COUNTA, =UNIQUE, =FILTER, =IF, =VLOOKUP, =COUNTIF) into cells. Always compute results in Python and write literal values (int, float, str, bool). Only insert Excel formulas if the task explicitly asks to grade the formula text itself.**


This applies even when the task says "fix the formula" or "correct the formula" — compute the corrected result in Python and write the literal value. The grader expects the computed value, not a formula string.



Before writing any code, complete the Inspection steps below. CRITICAL: After saving, you must complete the Verification steps before declaring TASK_COMPLETE. Skipping verification will cause task failure.



- First, run a read‑only inspection script (e.g., `python3 -c '...'`) to print sheet names, dimensions, and at least 15 rows of data. Do not write any transformation code until you have seen this output. Then, in a second command, perform the manipulation, save, and verification: reload the output workbook, print the exact answer range with values and types, and assert that no cell is `None` or a formula string. Do not split the workflow across more than these two commands. This ensures inspection and verification are not skipped.

CRITICAL: Skipping either the Inspection or Verification steps will almost certainly cause task failure. Always inspect actual cell values and always verify the output after saving.

🚫 **After every save: reload the output file, print the answer range, and confirm no cell is None or a formula string. Do not call TASK_COMPLETE until this check passes.**


🚫 **MANDATORY: After every save, run the verification script from the 'Before TASK_COMPLETE' section. If any cell is None or a formula string, recompute the literal value and re‑save. Do not call TASK_COMPLETE until all assertions pass.**

Always use programmatic manipulation with openpyxl for all modifications; manual cell‑by‑cell editing is unreliable and not repeatable.
## Inspection


Before writing any code, read the entire input workbook: list all sheet names, print the dimensions, and print at least the first 15 rows and the last 5 rows (including column headers) along with cell coordinates, values, types (using `type(cell.value).__name__`), and number formats.

Always use `repr(cell.value)` when printing values — this reveals whether a cell contains a string that looks like a number, hidden whitespace, or unexpected decimal separators that a plain `print()` would mask.

Even if the prompt includes a summary of the spreadsheet content, always inspect the actual file; the summary may be outdated or incomplete.

- **Critical**: Full inspection of the data — printing every row or a comprehensive sample — is the single most effective step to prevent deletion, transformation, and lookup errors. Do not skip this even for simple tasks. Whenever feasible, print the entire workbook (all rows, all sheets) before writing any code.

- For larger datasets, also print a sample of rows from the middle of the data (e.g., around the midpoint) to detect hidden structure changes or data gaps. For lookup or merge tasks, also check for duplicate keys in the key column(s) and report them. This reveals mixed types, hidden sheets, and edge cases. For small workbooks, printing all non-empty cells is acceptable; for larger ones, a representative sample is sufficient.


- When a task requires acting on a specific column (e.g., deleting rows based on its values), print the full content of that column (or at least the first and last 20 entries) to locate the exact target cells and surface hidden headers or gaps that a limited row sample might miss.

### Dynamic Column Detection
When you need to find a column by its header label, scan the header row cells and match the label text. Never assume a fixed column letter or index, as column positions may change. After locating the header row, print the column index and label for each cell to verify the target label is correctly identified before proceeding.
Normalize header text by stripping whitespace and converting to lowercase (or casefold) before matching to avoid case or whitespace mismatches.

- Do not rely solely on the task description; always inspect the actual file for formatting clues. Before writing any manipulation code, print all non‑empty cell coordinates and values (or at least a representative sample of every column) and compare them with the task description; flag any discrepancies or extra details that you must replicate.
- After inspecting the full sheet, use the observed row contents to drive row‑selection logic. For example, iterate only over rows where a key column contains a numeric value (e.g., `isinstance(cell.value, (int, float))`) or matches a condition, rather than hardcoding a static row range. This avoids accidentally processing header, summary, or constraint rows.

- When inspecting cells, differentiate between `None` (empty cell) and empty strings (`''`), and note any cells containing formulas that evaluate to an empty string; this distinction is critical for conditions like 'if cell is empty' that may be used for deletion or filtering.
- Whenever practical, print every non-empty row (up to `ws.max_row`) of every sheet before writing any manipulation code. This avoids missing sentinel values, hidden rows, or layout quirks that a limited sample might overlook.

- When printing non‑empty cells, also note any existing formulas or repeated patterns (e.g., every Nth row) that may indicate the intended output structure.
- For any workbook with fewer than 100 rows, print every row and column (including empty cells) to capture the full layout, hidden blank rows, and trailing entries.

- If the task specifies an answer range (e.g., `'Students'!E2:E7`), also print every cell in that range with its value, type, and number_format before writing any code. Confirm that the observed types and formats align with the task requirements; adjust your approach if they don't.

For any cells that you plan to modify or use in computations, also print their formula text (load the workbook with `data_only=False` and check `cell.data_type == 'f'`; if true, print `cell.value` to see the formula) and the values and formulas of the immediate surrounding cells (e.g., the row above, below, and adjacent columns) to understand the intended logic and avoid introducing circular references or misaligned calculations. This reveals dependencies and prevents overwriting formulas with static values when they should be preserved.
- **Dual‑view inspection for formula‑dependent tasks**: When your computation depends on a value from another cell that might contain a formula, load the workbook twice during inspection: once with `data_only=False` (to see formulas) and once with `data_only=True` (to see the cached evaluated values). Use the evaluated values from the `data_only=True` load as inputs for your Python computation, then write the literal result. Never write a formula that references another cell hoping openpyxl will evaluate it; always read the source cell's evaluated value and compute in Python.


**Scanning for target strings**: When the task requires finding rows that contain a specific value (e.g., `"X"`), open the workbook with both `data_only=False` (to see formulas) and `data_only=True` (to see cached values). For each cell, test whether the raw formula text or the computed value matches the target. After building the candidate list, print each flagged row's raw value and computed value to confirm no formula‑evaluated match is missed.

- **Data validation / dropdowns**: If the workbook contains dropdown cells, inspect their data validation rules by printing `ws.data_validations.dataValidation` to see the allowed values and cell ranges. This reveals dependencies like market/category selectors that drive lookup logic.
- After your inspection, verify that you have printed at least one header row and at least one data row from every column referenced in the task; if not, inspect further.

- Do not stop at sheet names and dimensions; always print actual cell values and types. A printout of only sheet names and dimensions is insufficient to understand the data layout.

- If the answer range is known, print enough rows to cover the entire answer range plus a few rows above and below (at least the first 40 rows, or all rows if the workbook is small). This reveals hidden headers, repeated index rows, and data gaps.

- When a task involves writing to a destination sheet (e.g., a sheet named 'Items Older than 30 days'), always inspect that sheet's current content before writing any code. Print its used range, formulas, and any helper columns. This prevents overwriting unexpected data or missing deletions.
- After inspection, explicitly note any discrepancies from the task description in a comment before writing code (e.g., extra columns, formulas, unexpected data).

- Before writing any code, print the entire answer range (if known) with `data_only=False` to see current values, types, and any formulas. Note which cells are `None`, which contain numbers, and which contain formulas. This reconnaissance will guide your approach (e.g., whether to overwrite with computed values or preserve existing formulas).

- If the task mentions any formatting (fill, font, borders, alignment), print the fill, font, border, and alignment properties of the relevant cells before writing code. This ensures you can replicate or clear formatting accurately.

- Before writing any transformation script, print every row of every column you will read from or write to (up to `ws.max_row`) to confirm the data range and identify anomalies. Do not rely on a partial sample; print the full column(s) if feasible.
- As a final pre‑code check, verify that the printed output covers the exact answer range and any reference tables; flag mismatched columns or unexpected empty cells before writing any manipulation code.
- If the workbook contains a separate sheet that appears to be a reference or expected result (e.g., `'Desired Results'`, `'Expected'`, `'Manual Result'`), print its full content before writing any code. Use it to understand the expected output structure and to guide your transformation logic — the expected output is the best specification you have.
- Print any merged cell ranges (`ws.merged_cells.ranges`) and unmerge all of them before writing, unless the task explicitly requires keeping merges. This prevents write errors caused by merged cells.


- When planning to delete or filter rows based on a column condition, print the rows you intend to act on with the value in that column to verify your interpretation before writing any deletion code.

- **When source cells contain formulas**: If you need to use their values in computations, load the workbook with `data_only=True` to get the evaluated numeric results. Do not try to replicate the formula logic in Python unless the task requires it; the pre‑computed value is sufficient. After obtaining the values, compute your output in Python and write literal values, never formula strings.

- Inspect every sheet in the workbook, even those not directly mentioned in the task, to identify any pre‑existing data that may need to be cleared or preserved (e.g., a 'LIST' sheet that must be emptied).

- **Side-by-side formula/data comparison**: When inspecting formula cells, print both the formula text (from `data_only=False`) and the evaluated value (from `data_only=True`) side by side for the same cells. This reveals the intended computation and helps you replicate it correctly in Python.


- **Fill‑based selection**: When the task requires selecting cells by their fill colour, print the fill type and RGB value (e.g., `cell.fill.start_color.rgb`) for every row in the relevant column(s). After identifying the target cells, print the list of selected cell coordinates and values before writing any output. This end‑to‑end source inspection prevents missed or mis‑identified items.

- **When the task defines a specific input region** (e.g., a schedule template, a block of cells with existing formulas), print every cell in that region along with its coordinate, value, and `cell.data_type` (e.g., 'f' for formula, 'n' for number, 's' for string). This makes it easy to distinguish data from formulas and from empty cells before you write any code.

- **Blank‑row tasks**: When the task involves detecting or deleting blank rows (e.g., 'delete blank rows above a cell with text X'), print every row of the target sheet, including blank rows, using a loop from row 1 to `ws.max_row` and printing the row index and cell values. This reveals the exact positions of blanks and prevents misidentifying rows.

- **Existing output sheet pattern**: If the target sheet already contains data that serves as an example of the expected output (e.g., a partially filled list), print every row before writing to identify ordering patterns (grouping by a key, sort order, concatenation style) and adopt the same pattern in your new data.

When a reference sheet shows blank rows between groups, preserve exactly that number of blank rows in the output.

- **Output sheet full dump**: Before writing any code, print every cell (including empty ones) of the output sheet named in the task's `answer_position`, along with its value and type. This reveals existing placeholder values, formatting, and the exact layout you must work with.
## Writing Output


Always write a literal computed value into the answer cell unless the instructions explicitly require a formula. **Even if the task mentions 'formula' or 'method', write the computed literal values, not formula strings.** Only insert Excel formulas if the instructions explicitly say to grade the formula text itself. Do not insert unevaluated formulas that could return errors like #N/A.
Do not write any cell value that begins with '=', including simple formulas like `=RIGHT(A2,LEN(B2))=B2` or `=A1+B1`. Compute the result in Python and write the literal value (e.g., `True`/`False`, number).

**Clear the answer range before writing**: Before writing any computed results, set every cell in the answer range to `None`. This prevents stale data from remaining in cells your logic does not overwrite (e.g., when the new dataset is smaller than the old one). After clearing, write your new values — the grader will see only intended data, not leftover content from the original file.
If the answer range includes a header row, either exclude that row from clearing or explicitly re-write the header label after clearing.


- Always derive row and column boundaries from `ws.max_row` and `ws.max_column` instead of hardcoding numeric ranges. Loop over the full possible range and skip empty cells (e.g., `if cell.value is not None`).
- When building a list of values from a column, do not assume a fixed number of rows. Instead, scan backwards from `ws.max_row` to find the last cell with a non‑`None` value (e.g., `last_row = ws.max_row; while last_row > 1 and ws.cell(last_row, col).value is None: last_row -= 1`), then collect only rows 2 through `last_row`. After reading, print the count of retained items and confirm it matches the expected number of data rows — this guards against trailing empty rows that `ws.max_row` may include.
- When building a result grid that compares tables, define a sensible default value (e.g., `False` for a comparison) for cells where a lookup key is missing from one table; never leave cells as `None` or empty strings.

- **Conditional column writes**: Before writing values to a column based on a condition, first print the full column to see existing data. Then reset every cell in the target range to `None` (or the intended default) before writing only the matching rows. This guarantees non‑matching cells are left empty and no stale data remains. After saving, verify that all non‑matching cells are still `None`.
- Before saving, scan the answer range for any cell value that is a string starting with `'='`; if any are found, replace them with the computed literal value. The grader reads cell values as-is and will not evaluate formulas.
- When populating output tables with paired columns (e.g., 'ITEM' and a category label), locate the category column by scanning the entire header row and matching the exact label, not a fixed offset from the block start.
- Before writing final data, inspect the original output template for rows containing summary labels (like 'TOTAL') within the graded answer range. After populating detail data, rebuild those summary rows with appropriate aggregation functions computed in Python (e.g., using `sum()` or loops); do **not** write Excel formulas like `=SUM(...)`.
- When sorting data, define a clear sort key and apply it to the extracted records before writing.
- When a weighted average is required across groups, compute the numerator and denominator in Python using conditional sums (e.g., iterate over rows and sum values matching the condition) and write the resulting numeric value as a literal. Even if the task explicitly asks to use a formula like `SUMPRODUCT` or `SUMIFS`, compute the result in Python and write the literal numeric value. Openpyxl does not evaluate formulas; writing a formula string will leave the cell with a `None` value when read by the grader. Only insert Excel formulas if the instructions explicitly say to grade the formula text itself. Always reference the correct weight column for both parts.

- When clearing an output area, define the exact rectangular range that will be graded (e.g., from row X to Y, column A to B) and set every cell in that range to `None` before writing. Do not rely on the sheet's current `max_row` or `max_column`, as they may not cover the full grading area.

- Before writing any code, extract the exact answer range from the task description (e.g., `'Students'!E2:E7`). Write only to those cells; do not populate adjacent columns or rows unless explicitly instructed. After writing, verify that cells outside the answer range remain unchanged.

- For tasks requiring exact numeric sums (e.g., finding a subset that sums to a specific target), use Python's `decimal.Decimal` to avoid floating-point rounding errors.

When the task specifies a display format (e.g., 'no decimals', 'percentage', 'date'), set the cell's number_format attribute after writing the value. During verification, confirm that the number_format matches the required format.

- When the task says 'calculate and display the result', it expects the final computed value, not a formula. Write the numeric result directly.
- **Unpivoting wide-format tables**: When transposing multiple variable columns into rows while keeping preceding columns constant and performing a lookup enrichment, use a double loop (data row × variable column) to build output rows as static values. Verify the approach by comparing a sample of output rows against the expected structure (e.g., an `Expected` sheet) before scaling to the full range.

- **Preserve source formatting when copying data**: When transferring cell values from a source sheet to a destination sheet, also copy the source cell's font, fill, border, alignment, and number_format using openpyxl's style copying (e.g., `copy(cell._style)` or individual attribute assignment). After writing, spot‑check a few output cells against the source to confirm visual appearance (bold, alignment, borders) is preserved.

- Always save the workbook using the exact `output_path` string provided in the task specification, without any path manipulation or renaming. Do not add directories, change the extension, or alter the filename in any way.

- When a calculation repeats across multiple columns with the same row pattern, use a loop over column indices and a mapping of source rows to target rows. This avoids copy‑paste errors and makes the intent clearer.

- When the `answer_position` specifies a range like `I4:I7`, write to rows 4 through 7 inclusive (e.g., `for r in range(4, 8)`). Do not enlarge or shift the range unless the task explicitly asks for it.

- Even for tasks that ask to “display” a result like a rank label (e.g., 'cat2'), compute the string in Python (e.g., using string concatenation or a lookup) and write it directly; never use an Excel formula like `=A1&COUNTIFS(...)` to produce the label.
## Verification


**Mandatory Verification Step**: Always re-open the output file after writing and print the exact grading range. Do not skip this step.


Do not rely on in‑memory record counts or lengths; only the reloaded file's printed cells provide definitive verification.

Print each cell's coordinate, value, data type, number_format, fill color, and border style. For example, if the answer range is A1:I2, you would print something like: A1: value=..., type=..., format=... . Do not rely on summary messages; verify every cell individually.

- After printing the grading range, count the number of non‑None rows in that range and ensure no unexpected empty rows remain.

Do not rely on the in‑memory workbook after saving; always inspect the reloaded file to confirm types and values.


After writing the final output file, load it back with `openpyxl.load_workbook(output_path, data_only=True)` to inspect computed values, and also with `data_only=False` to check for formulas. Print the exact cells the grader will read: coordinate, value, type, and whether it contains a formula. Confirm that no cell is None, an error string, an empty string, or a string starting with '=' (an unevaluated formula); if any are empty or contain a formula string, replace them with the appropriate default or computed value. Check that all answer cells contain the expected type (e.g., numeric). If a formula is required, test it against actual data to ensure it evaluates correctly.

- Imagine adding one more row of data and verify that your code would still capture it without manual adjustment.
- Do not declare TASK_COMPLETE until you have physically confirmed the output content.

- After writing, verify that every intended category block has a non‑zero number of data rows; if any block is empty, re‑examine the label extraction.
- Confirm that any expected summary row (e.g., 'TOTAL') within the graded answer range is not left empty.
- Do not rely on file size or metadata to confirm correctness; always read back the actual cell values in the answer range.
- For weighted average formulas, confirm that the numerator references the correct weight column and that the denominator sums that same weight column over the matching condition, not an unrelated column.

- For sorting tasks, after writing, verify that the key columns are monotonically non‑decreasing and that all original rows are present exactly once (compare the set of sorted-key tuples against the original set).
- If the task involves replacing specific strings, after reloading the output confirm that those strings have been replaced with the intended values in the answer range. Print each cell in the answer range and flag any that still contain the original text.
- Confirm that the output file was saved to the exact `output_path` string provided in the task specification, without any path manipulation or renaming.

- After saving, confirm that the file exists at the output_path (e.g., using `os.path.exists` or `ls -l`) before attempting to re-open it.
- Also check that the file size is non‑zero (e.g., `os.path.getsize(output_path) > 0`) to confirm the save was successful.
- Always determine the exact grading range from the task's `answer_position` (e.g., `A3:A24`). Print only that range, not a broader area, and verify each cell's value and type. This ensures you catch any formula strings or misaligned values within the graded cells.
- After printing the exact grading range, also print a sample of neighbouring cells (e.g., the row above, below, and columns left/right) to confirm no accidental overwrites occurred.

- For tasks that insert blank rows, after saving, print all non‑empty cells in the answer range (e.g., `[ (r, ws.cell(r,1).value) for r in range(1,71) if ws.cell(r,1).value is not None ]`) and confirm that the rows immediately before the marker rows are empty and the markers still contain the expected value.
- After loading the output, compare the answer range values to the original input to confirm that the intended transformation has been applied where expected, and that no cells remain unchanged when they should have been updated.
- If you performed row deletions, after saving, iterate over the remaining rows and confirm that no row still satisfies the deletion condition; if any do, your deletion is incomplete — fix and re-save.
For blank‑row deletion tasks, also confirm that no all‑`None` rows remain in the answer range; if any are found, use `delete_rows` to remove them and re‑save.

- Also print the number_format of each cell in the answer range. End with a summary assertion that all cells meet the required criteria (e.g., all values are date/datetime, not strings or formulas, and number_format matches the required format).

After loading the output with `data_only=True`, iterate over every cell in the answer range. For cells that you wrote data into, assert that the value is not `None` and not a formula string. For any remaining cells in the answer range (beyond your written data), assert that they are `None` to confirm no stale leftovers. If any assertion fails, fix the cells and re‑save before declaring completion.
- After clearing the output area, verify that any header row within the answer range (e.g., the first row of the output block) still contains the correct labels and was not accidentally overwritten during the clear operation.
- If the task specifies formatting (fill, font, borders) on certain cells, after writing iterate over all cells in the sheet and confirm that only the intended cells have that formatting and that all other cells have the default (e.g., no fill). If the task requires deleting a sheet, print the list of sheet names to confirm the sheet is absent.
- If the workbook contains a sheet whose name suggests it is a reference result (e.g., `'Manual Result'`, `'Expected'`, `'Reference'`), load that sheet after saving and compare each cell in the answer range against the corresponding cell in the reference sheet. Print the coordinates and values of any mismatches. Do not declare TASK_COMPLETE until all cells match or you have understood and corrected the discrepancies.
- After performing string cleaning, compare the output cell types against the original input: any cell that was numeric before should remain numeric (unless the task explicitly requires conversion). Print the type of each answer cell and flag any unexpected stringification.

- Perform at least one targeted sanity check that verifies the transformation rules against the output (e.g., if the task says 'delete rows where column E is empty', confirm that no row with empty E remains).


- Before declaring TASK_COMPLETE, run this check on the reloaded workbook (adjust `answer_range` to the exact grading range, e.g., `'A1:A22'`):
  ```python
  for row in ws[answer_range]:
      for cell in row:
          assert cell.value is not None, f"Cell {cell.coordinate} is None"
          assert not (isinstance(cell.value, str) and cell.value.startswith('=')), f"Cell {cell.coordinate} contains formula string: {cell.value}"
  ```
  If the assertion fails, fix the cells and re‑save before proceeding.

- For incremental sequences (e.g., ascending letters, numbers, dates), print a few consecutive cells and confirm the pattern increments as expected (e.g., each value is exactly one more than the previous, no duplicates or skips).

- Even if you believe you wrote literal values, always run the assertion check for `None` and formula strings; a string like `=...` may have been set inadvertently. If any cell fails, recompute the literal value, write it, and re‑save before proceeding.

- If the task involves conditional formatting or conditional fill (e.g., applying a fill colour only when a certain condition is met), after saving reload the workbook and verify that the fill (or other formatting) is applied exactly where the condition holds, and not applied elsewhere. Print the rows that received the formatting and confirm the condition holds.

- For very large files, if reloading the entire workbook with `openpyxl` times out, use Python's `zipfile` to read the sheet XML directly and spot‑check a few cells from the answer range. This ensures you can verify the saved file without excessive memory or time.

- If the task specified a global scope (e.g., 'across all columns'), after writing, print a sample of cells from each originally populated column to confirm the transformation was applied everywhere, not just in the answer range.


- If you wrote values conditionally (only to some rows), scan the entire target range and confirm that cells not meeting the condition are empty (`None`) and not holding leftover data. Print any violations before declaring completion.

- **In‑memory prints are not verification**: Printing cell values from the in‑memory workbook (before saving) may show formula strings, but the saved file will contain unevaluated formulas that the grader reads as `None`. Always reload the saved file with `data_only=True` and check that the answer cells contain concrete values, not formula strings or `None`.


- **Self‑check by re‑computing expected values**: For tasks involving mapping or transformation rules, after reloading the output, re‑compute the expected answer values from the input data using the same rules you applied. Compare each expected value to the actual cell value in the answer range and print a summary of matches/mismatches, with at least three discrepancies if any. This catches off‑by‑one errors, logic mistakes, and incorrect handling of edge cases without requiring an answer key.
## Common Pitfalls


- **Never** write a cell value that starts with `'='` unless the task explicitly requests a formula. The grader reads cell values as-is and will not evaluate formulas, causing the answer range to appear empty. Instead, always write computed literal values.
- **Date formatting**: Whenever you write a date value to a cell, always set the cell's number_format to a date-appropriate format – ideally by copying the number_format from a source date cell in the same workbook. After saving, load the output and confirm the target cell’s data_type is 'd' and that number_format is not 'General' (e.g., contains 'd' or a date pattern), so the answer range presents a proper date, not a number, unless the task explicitly grades formulas.
- **Case-insensitive string matching and lookup keys**: Normalize string values to a consistent case (e.g., `.strip().casefold()` or `.lower()`) when the task explicitly requires case‑insensitive matching, when building lookup keys from data that may have inconsistent casing, or when performing flexible text search (e.g., keyword matching in comments).
- Hardcoding row/column ranges (e.g., `range(8,11)`) instead of using `ws.max_row`/`ws.max_column`; this breaks when data size changes.
- **Hardcoding column letters or indices**: Relying on fixed column positions (e.g., `ws['C']` or `col=3`) will fail when the spreadsheet layout changes. Always locate columns dynamically by scanning the header row for the desired label.
- **Dynamic header row location**: Never hardcode a row index when searching for column labels. Instead, first locate the header row by searching for a known anchor label (e.g., `'Row Labels'` or the first row with multiple string headers). Use that row to then find the target column. **Verification**: after loading the workbook, print the first 10 rows and visually confirm which row contains the anchor; only then proceed with column lookup.
- Leaving missing lookup matches as `None` instead of an explicit boolean or placeholder.
- **Deleting rows safely**: When removing rows in openpyxl, always iterate from bottom to top (`for r in range(ws.max_row, 1, -1)`) and use `ws.delete_rows(r, 1)`. This prevents index shift from causing rows to be skipped.

- **Range‑dependent formulas**: When writing formulas that reference a range of cells (e.g., `=SUM(B3:B40)`), first print all rows up to `ws.max_row` to determine the true last row of data. Hardcoding range bounds based on a partial inspection may exclude rows and produce incorrect results. After writing the output, reload and verify that the computed values cover all expected rows.
- **Interpreting 'formula/method' requests**: When a task asks for a ''formula/method to calculate X'', write the **computed numeric values** into the answer cells, not the formula strings. Only insert Excel formulas if the instructions explicitly say to grade the formula text itself. After writing, verify with `data_only=True` that no answer cell contains a string starting with `=`.

- **Sorting live cell references**: When reordering rows, never sort the tuples returned by `iter_rows` directly and then write them back. Writing to the sheet can mutate cell objects still being read, causing duplicated or missing rows. Instead, first extract all cell values and formatting into an independent list of tuples (e.g., `records.append((sort_key(r), cells))`), sort that list, and then write the stored data back row by row. After writing, verify that the number of data rows matches the original and that no row appears more than once.

- **Rearranging rows with derived columns**: When reordering rows, any column containing formula strings that reference the current row (e.g., `=IF(NOT(ISBLANK(E3)),A3,"")`) will break if copied unchanged — the references still point at the original cells, not the new row positions. Instead, after reordering, recompute the intended logic in Python for each new row and write static values. After saving, verify with `data_only=True` that no cell in the answer range contains a formula string.
- **String matching strategy**: Before writing any transformation logic that searches for a given text, always print the unique values (or a sample of rows) from the target column to see exactly how the text appears. Decide whether an exact match, a substring match, case‑insensitive match, or stripping of extra characters is needed, and implement that condition. After drafting the match, print the row numbers and values that your condition selects to confirm they are the rows you intend to change – if not, adjust the condition before applying any updates.
If the data contains error indicators like `#N/A` or `#VALUE!`, test for those strings explicitly; do not assume the word 'error'.
- **Overwriting non‑data rows during column‑wise operations**: When applying a uniform operation to a column (e.g., zeroing residuals), inspect the sheet first to distinguish header/label/constraint rows from data rows. Restrict the operation to rows where the target cell holds a numeric value using a type check (e.g., `if isinstance(cell.value, (int, float))`). After writing, verify that rows with non‑numeric labels in that column still contain their original text or empty value, not the overwritten constant.
- **Skipping inspection and verification**: Never skip the initial workbook inspection, even for simple tasks. Before writing any transformation code, print sheet names, dimensions, and a sample of the data that matches your criteria. After saving the output, re‑open it and verify that the answer range satisfies the requirements. Ask yourself: “Did I read the current state and confirm my change had the intended effect?”

- **The 'feels simple' trap**: The temptation to skip inspection is strongest when the task seems trivial — a simple column copy, a quick string replace, a small lookup. These are exactly the cases where hidden whitespace, unexpected data types, or pre‑existing values in the output range cause failures. Always print the raw `repr()` of every cell in the target and output columns before writing any code, regardless of how straightforward the task appears.

- **Imposing extra conditions**: Do not add conditions such as checking if a cell is blank before writing unless the task explicitly requires it. When a task describes a condition for writing (e.g., 'only when there is a matching sheet name'), implement exactly that condition; do not add extra checks like blank‑cell tests. After writing, verify that the answer range values have changed from the original for rows that satisfy the condition.
- **Cross‑sheet references**: Never use formulas like `INDIRECT` or `='SheetName'!A1` to pull values from other sheets. Always read the source sheets directly in Python and write the computed literal values. After saving, verify with `data_only=True` that the answer cells contain concrete numbers, not `None` or formula strings.
- **Deleting rows safely verification**: After deleting rows, reload the workbook and print the remaining rows to confirm no rows were accidentally skipped.

- **Misinterpreting multi-column source mappings**: When a task says to “derive” a result from adjacent columns, determine if the column headers encode keys (e.g., each header is a runner number) and the task provides an example mapping a row’s key to a specific column. This is a field‑by‑field lookup, not an aggregation. Before finalising, test a few rows with known expected values; after writing, verify no cell contains concatenated strings or repeated identical values across a group when single values are expected.
- **Duplicate lookup keys in sheet joins**: Before building a lookup dictionary from a source sheet, print the count of source rows vs. unique keys. If they differ, inspect duplicates and add distinguishing attributes (date, ID, etc.) to the key. After building the dict, assert `len(lookup) == source_row_count` or log duplicates; do not proceed until keys are unique.
- **'Fix the formula' tasks**: When a task says 'fix the formula' or mentions a formula error, never start with cosmetic formatting. First inspect every sheet the formula references — especially lookup tables — to detect mismatches like trailing whitespace or case differences. Compute the corrected values in Python and overwrite the broken cells with static results. Only apply formatting after the answer cells contain correct data. After writing, verify that every answer cell holds a concrete value (number or string), not `None` and not a formula string.
- **Exact number format strings**: When the task specifies a particular number format (e.g., `'m/dd/yyyy'`), use that exact string in the `number_format` assignment. Do not convert or simplify it, even if a similar format displays identically for some dates.

- **Not resetting existing formatting before applying new formatting**: When the task requires that only certain cells have a specific format (e.g., green fill), first inspect the current formatting of all cells in the target range. Then explicitly clear that formatting on all cells that should **not** carry it (e.g., set `fill = PatternFill()` for fill) before applying the new formatting to the intended cells. After writing, verify that only the intended cells have the formatting and no leftover formatting remains.
- **Preserving numeric cell values during string operations**: When applying string‑based transformations (e.g., `re.sub`, `str.replace`) to a range of cells, first check each cell's type. If the value is already a number (`int` or `float`), skip it; only convert string cells. After writing, reload the file and verify that cells that were originally numeric still have numeric types, not `str`.
- **Copying values from other cells**: When you need to place a value from another cell into an answer cell, assign the source cell's value directly (e.g., `ws['C2'].value = ws['A25'].value`). Do not use a formula string like `'=A25'`; the grader reads the cell as a string, not the value.

- **Formula string verification**: If you accidentally write a formula string (which you should never do), you must reload the output file and confirm that the cell's computed value is a concrete number or string, not None. A formula string alone is not sufficient; replace it with the literal computed value before declaring completion.

- **Restart logic in scanning/counting tasks**: When a task describes restarting a scanning or counting process from a specific new start after an event, move the reference to the exact new position (the cell after the event) rather than updating it to the event cell itself. After writing the logic, test it on a small known sequence by hand‑simulating a few steps to confirm the count matches the intended behaviour.

- **Writing VBA code into answer cells**: Never place VBA code, macro strings, or any non‑evaluated code into a cell. The grader reads the cell value directly and cannot execute code. Always compute the required result in Python and write the literal value (number, string, etc.) into the answer cell. This Python‑first approach has been proven successful: when a task references a VBA macro, ignore the macro entirely and replicate its logic in Python with openpyxl — iterate over the target rows, apply the transformation, and save.

- **Overwriting columns not explicitly requested**: When the task specifies that the output should occupy only certain columns (e.g., "columns G and H"), restrict write operations to exactly those columns. Do not clear or modify adjacent columns in the answer range. After writing, reload the workbook and confirm that the unmentioned columns still contain their original values (compare against a backup or print and inspect).
- **Failing to skip repeated header rows in data extraction**: Before extracting records from a sheet, scan all rows and remove any that contain the header labels (case‑insensitively) in the same positions as the original header. Implement a check that normalises each cell and skips the entire row if it matches header keywords. After building the record list, print the first and last records to verify that no header text appears among the data items.

- **Using any Excel formula (e.g., =SUM, =AVERAGE, =IF, =VLOOKUP, =SUMPRODUCT, =UNIQUE, =FILTER, =SUMIF, =COUNTIF, =COUNTIFS, =INDEX, =MATCH, =XLOOKUP, etc.)** – these will not be evaluated by the grader. Compute the result in Python (e.g., with a loop, set, or dictionary) and write the literal number. If you are tempted to write a formula, stop and compute it in Python instead.

- **Date‑based filtering with header inclusion**: When the task asks to filter rows based on a date threshold relative to the maximum date in a column (e.g., “items older than 30 days”), extract all date values from that column, find the maximum, subtract the required interval using `datetime.timedelta`, and compare each cell’s date value (not its string representation) to the cutoff. Always include the header row in the output and restrict columns to exactly those requested. After writing, verify the answer range contains plain values, no formula strings.
- **Defining duplicates by a composite key**: When the task defines duplicates based on multiple columns (e.g., identical entries in column B and C), build a composite key as a tuple of the relevant column values (e.g., `(str(b), str(c))`). Use a `seen` set to track keys and skip rows whose key is already present. After writing, verify uniqueness by printing the deduplicated list and checking for any duplicate keys.

- **Writing formulas for string transformations**: When a task requires correcting strings (e.g., adjusting case based on another column), compute the corrected strings in Python and write them as literal values. Do **not** write Excel formula strings like `=IF(...)`; they will not be evaluated and the grader will see empty cells or formula text. After writing, verify that all answer cells contain actual strings, not formula strings.

- **Skipping post-save verification**: After saving, always reload the workbook and print the exact answer range (e.g., B2:B7). If you skip this, you may miss formula strings or empty cells that cause the task to fail. Always print the coordinates, values, and types before declaring completion.


- **Interpreting 'blank row' conditions relative to a specific column**: When a task says 'delete blank rows above a cell with text X in column Y', a row is considered blank if the cell in column Y is empty (None or empty string), regardless of content in other columns. Do not require all columns to be empty. Before deleting, print the rows you plan to delete together with the value in the target column to confirm your interpretation.
- **Writing output to the wrong sheet**: Always read the `answer_position` field in the task specification; it specifies both the sheet name and cell range. Write your output to that exact sheet, not the input sheet. If the sheet does not exist, create it. After saving, reload the workbook and assert that the sheet exists and the answer range cells are populated.

- **Sign errors in proportional mapping**: When mapping numeric values to a proportional scale (e.g., score = value * factor), ensure that negative values retain their sign. Test with extreme negative and positive inputs before writing the full column: assert that the minimum negative input yields a negative output, zero yields zero, and the maximum positive input yields a positive output. This catches sign-flipping errors early.
- **Round stored values to match requested decimal display**: When a task specifies a number format with a fixed number of decimal places (e.g., 0, 1, or 11 decimals), round the underlying cell value to that many decimal places before saving, using `round(value, ndigits)` or `Decimal.quantize()`. After saving, read back the cell's value (with `data_only=True`) and confirm it matches the intended rounded number, not a high‑precision float that may cause display artifacts.
- **Scaling to symmetric ranges**: When mapping values to a target range symmetric around zero (e.g., -5 to 5) and zero must map to exactly zero, compute separate scaling factors for positive and negative input values. Use a conditional branch: if x >= 0, score = target_max * x / max_pos; else score = -target_max * x / max_neg (where max_neg is the absolute value of the smallest negative). This prevents a single linear mapping from shifting zero away from a score of zero.

- **Ignoring explicit scope keywords**: When the task says 'across all columns' or 'entire sheet', iterate over all occupied cells without column restrictions (e.g., `ws.iter_rows()` without `min_col`/`max_col`). After execution, print the values of all originally populated cells to confirm every column was covered.

- **Displaying zeros as blanks**: When a task says "0s should display as blanks" or "zeros should appear blank", store the numeric zero in the cell and set a custom number format that hides zero values (e.g., `'0.00;-0.00;;@'` where the third section is empty). Do **not** set the cell value to `None`; the grader expects a numeric zero. After writing, verify that such cells contain `0` (not `None`) and the number_format suppresses zero display.


- **Overwriting the header row**: When processing column data, always start from row 2 (after the header) unless the task explicitly asks to modify the header. Before writing, confirm the header row exists and is not part of the data range. After writing, verify that the header cell(s) still contain their original values.
- **Unnecessary string transformations**: Do not apply `strip()`, `rstrip()`, `lower()`, etc. unless the task explicitly requires them. Extra cleaning can alter the intended output. After writing, spot‑check a modified cell to confirm that any trimmed characters should indeed be removed.
- **Inserting rows safely with formatting preservation**: When inserting multiple rows, collect all insertion positions, sort them, and iterate in reverse (bottom‑up) to avoid index shifts. Copy the style, number_format, and row height of the row that was originally at the insertion position (which shifts down) to the newly inserted blank row. After insertion, verify that the row height of the inserted row matches the height of the row that was shifted down, and that a cell in the inserted row has a style (e.g., `ws.cell(inserted_row, 2).has_style` is True).

- **Misinterpreting 'per X' as a global aggregate**: When the instruction says “per X” (e.g., per brand, per category), always group the data by X *before* computing any aggregate or filter. Never apply a single global calculation to the whole dataset. Before writing code, explicitly list the grouping column and the required per‑group metric. After writing, verify the grouping was applied: count the distinct values of the grouping column in the input; the output should have that many result rows unless some groups are legitimately excluded. Print the number of unique values of the grouping column from the input and confirm the output contains at least that many rows of data.
- **Writing unnecessary header rows into the answer range**: When the task says “from cell X2 onwards”, treat X1 as the existing header and X2 as the first data row. Do **not** write column headers into the data area unless the task explicitly asks for them. Before writing, examine the target start cell and its surroundings for existing headers or content. After writing, verify that the top‑left cell of the answer range holds a data value (date, number, string) rather than a header label already present elsewhere. If you see a header there, remove it and shift your data up one row.
- **Never use manual value‑shifting to delete rows**: when the task says “delete blank rows” or “delete rows where …”, use `ws.delete_rows(row, 1)` to physically remove them. Do not copy non‑blank cells upward and then clear trailing rows; that leaves all‑`None` rows that still count as rows. After deletion, verify that no all‑`None` rows remain in the answer range.

- **Per‑row threshold misinterpreted as aggregate sum**: When a task says to delete rows where a value is less than a threshold (e.g., 'delete rows with absolute value < 0.011'), apply the condition to each row individually. Do not sum all values and compare the sum to the threshold. After writing the deletion logic, verify that each remaining row's value meets the condition (e.g., absolute value >= 0.011).

Even if you are confident the output is correct, always reload and print the answer range; missing blank rows or other layout issues are only visible in the saved file.
## Before TASK_COMPLETE

0.5. Confirm the output file exists and has non‑zero size (e.g., `ls -l <output_path>`). If the file is missing or empty, re‑save before proceeding.
0. Confirm that the sheet named in `answer_position` exists in the output workbook (e.g., `assert answer_sheet_name in wb.sheetnames`). If it does not, fix and re‑save.
1. Reload the output workbook with `data_only=True`.
2. Print the exact answer range with cell coordinates, values, types, and number_format.
3. For cells you populated, assert that the value is not `None` and not a formula string. For any cells in the answer range beyond your written data, assert that they are `None` (to confirm no stale leftovers).
4. If any assertion fails, fix the cells and re‑save.
5. Only after all assertions pass, call TASK_COMPLETE.