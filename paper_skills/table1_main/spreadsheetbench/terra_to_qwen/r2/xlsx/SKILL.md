---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow


Inspect the full spreadsheet (all sheets in the workbook) before any manipulation.
Perform a thorough inspection: print all non‑empty cells up to row 50 (or all rows if fewer) across all relevant sheets to capture layout, headers, data types, example output, and constant cells. After the initial inspection (at most 3 turns), the very next action must be to write a self-contained Python script that loads the workbook, performs all required transformations, and saves to the exact `output_path`. Do not insert any additional inspections, debugging prints, or exploratory steps between the initial inspection and file creation. Finally, reload the workbook and verify the answer range.


- Write the script to a dedicated `.py` file (e.g., using `cat <<'EOF' > solve.py`) and execute it with `python solve.py`. This keeps the manipulation reproducible and easy to adjust. Before execution, confirm the script writes to the exact `output_path` from the task.
## Inspection


- Print `wb.sheetnames` to confirm available sheets. Then iterate over every sheet, printing its name, dimensions, and the first few rows (e.g., `for name in wb.sheetnames: ws = wb[name]; print(name, ws.dimensions); [print(row) for row in ws.iter_rows(min_row=1, max_row=min(5, ws.max_row), values_only=True)]`). This catches reference or expected-outcome sheets. Select the target sheet by exact name: `ws = wb['SheetName']`. Never use `wb.active`.

- Note where rows are entirely empty and where data ranges start and end; this helps identify separate blocks and structure.
- Print a comprehensive dump of all non-empty cells (coordinates, values, data types, number formats, and fill properties: `print(cell.fill.fill_type, cell.fill.fgColor.type, cell.fill.fgColor.rgb)`) across all relevant sheets. If a sheet has many rows, print at least the first 50 rows, the last few rows, and the sheet dimensions. This reveals layout, headers, edge cases, constant cells (like `$B$2`), and formatting anomalies (e.g., sheets to delete). Record those constant cells for reuse.
- Locate target columns dynamically by scanning the header row for the required label. Pair with dynamic header-row detection (e.g., find the row containing `'Row Labels'`) to adapt to table movement. Never hard-code a column letter or index.



- Build a dictionary mapping normalized header text to column index: `col_map = {str(c.value).strip().lower(): c.column for c in ws[1]}`. Use it for all column access. Print the mapping to confirm it matches expectations.
- When the task references special rows (e.g., min/max, totals), scan the label column (usually A) for those strings and capture the row numbers. Print the discovered row numbers before using them.

- Always copy the file path verbatim from the task's `spreadsheet_path` field. Before loading, verify the file exists using `os.path.isfile(path)`. If it does not exist, print the path and re-check the task description for typos before retrying.
Before any file operation, print the path and visually confirm it matches the task's `spreadsheet_path` character‑by‑character; correct any discrepancy before proceeding.

- If the workbook fails to load with a file‑not‑found error, inspect the path for duplication or typos (e.g., repeated directory fragments) and retry with the corrected path.

- For sheets with fewer than ~100 rows, print every row to catch subtle patterns like invoice-number prefixes, total row placements, and data-type surprises (e.g., boolean `True` vs. the string `'none'`).

- Identify sentinel rows (e.g., rows containing `'\u2026'`) that mark table boundaries; treat them as separators, not as data to process.
- Check for merged cells (`ws.merged_cells.ranges`) and multi‑block regions (blank rows, repeated headers). Print any merged ranges and note block boundaries before manipulation. Merged cells can affect read/write behavior; treat each block separately.
When merged cells overlap with data you need to process, unmerge them first using `ws.unmerge_cells(str(range))` to avoid missing values; after unmerging, re-inspect the affected area.

- When printing cell details, always include the `number_format`, `data_type`, and `alignment` attributes: `print(c.coordinate, repr(c.value), type(c.value).__name__, 'fmt=', repr(c.number_format), 'dt=', c.data_type, 'align=', c.alignment.horizontal, c.alignment.vertical)`. This is critical for date/time/numeric columns and for distinguishing numeric zeros from empty strings when designing blank-check logic, and for preserving formatting rules.

- When the task specifies a range of columns (e.g., "columns A to F"), iterate over all columns in that range inclusive. Do not skip columns based on a quick visual inspection. Print the list of column indices being processed and confirm they match exactly the columns named in the instruction.
- When the task involves correcting a formula or computing a value that depends on other cells, print the full content of all referenced ranges (including any lookup tables) to ensure you have the correct source data and to detect any nested formulas that might affect the result.
- If the task involves modifying existing formulas, print the current formula strings of the target cells (e.g., `for r in range(min_row, max_row+1): print(ws.cell(r, col).value)`) to understand their logic and dependencies before writing new ones.
- Ensure the dump covers all rows that contain actual data, not just a fixed cutoff. Print enough rows to see the full extent of data and any repeating patterns (e.g., fixed-interval blocks). If `ws.max_row` is beyond the initial print range, extend the dump to include the last populated rows as well.
- When the task mentions specific cells (e.g., criteria cells like I2, J2), print those cells explicitly with their values and types before writing any logic. This confirms the criteria values and prevents misinterpretation.
- Always perform this thorough inspection before any manipulation; it is the foundation of correct output.
- After inspection and before writing any formulas or transformation code, pause to verify that the discovered data types and layout support the planned approach. If a column contains unexpected types (e.g., booleans where strings were assumed), adjust the logic before writing output.

- When the task identifies a specific target cell or range, print the surrounding rows and columns (e.g., a few rows above and below) to see the immediate data context, including neighboring values, formulas, or formatting that may affect the solution.
- Before writing any manipulation code, for each column that will be read or written, print every cell's coordinate, `repr(value)`, and `type(value).__name__` within the data rows. This focused inspection reveals exact data types and missing-value patterns, so logic can be built on actual cell content rather than assumptions.

Even for seemingly straightforward tasks, this inspection step is essential to avoid costly mis‑steps.


- When the task specifies an answer range (e.g., B2:B5), print every cell in that range during the initial inspection, including its value, type, and formula string (if any). This reveals existing formulas that must be replaced with computed literal values, and confirms the range is clear of hidden values, formatting, or extra rows.

- Also print font properties for each cell: `print(cell.font.name, cell.font.size, cell.font.bold, cell.font.italic, cell.font.color.rgb if cell.font.color else None)`. This captures styling that must be preserved or replicated.

- When the task involves splitting, mapping, or lookup, print the raw values of the input range and any auxiliary lookup tables before writing any transformation code. Use a simple read‑back script to confirm delimiters, missing values, and exact string formats. This concrete view guides how to split, map, and write output correctly.
- When the task mentions specific column names (e.g., 'AY', 'BG'), print those columns' headers and a few sample rows to confirm the mapping before proceeding.

- When inspecting, load the workbook with `data_only=True` to see cached computed values. For any cell containing a formula, print both the formula string (using `data_only=False`) and the cached value to understand the actual data.

- During initial inspection, also print the content of any hidden columns (check `ws.column_dimensions[col_letter].hidden`). Include any result or reference sheets (e.g., "Expected", "Manual Result") to understand the target output and the gap between current and desired state.

- After printing all rows, explicitly note any extra rows beyond the main data block (e.g., rows 6–17 with reference data) that may serve as lookup tables or reference information. Print their coordinates and values to ensure they are not overlooked.

- Before building a column map from row 1, print the first few rows and confirm that row 1 contains header-like text (e.g., strings), not data values. If the first row contains data (numbers, dates, etc.), treat it as data and do not use it as a header; instead, work with column indices or a manual mapping.

- When printing cell values, use `repr()` to reveal non‑printable characters such as NBSP (`\xa0`) that can cause matching failures.


This initial inspection is the single most important step; never skip it, even for seemingly straightforward tasks. It grounds all later decisions in the actual content of the workbook.

- Always inspect every sheet in the workbook, not just the one you think is relevant. Print all rows and columns up to `max_row`/`max_column` for each sheet, unless the sheet is extremely large (>200 rows), in which case print the first 50 rows, the last few rows, and the sheet dimensions.


When the task involves filtering, matching, or copying data based on criteria, print all source rows that will be affected (or a representative sample if too many) along with their Python types (`type(cell.value).__name__`). Also print the current content of the destination range (target sheet/columns) to determine if clearing is needed. This ensures you understand the exact data patterns and any pre-existing values that must be handled.
## Writing Output


**CRITICAL: The grader cannot evaluate formulas. Write literal values only.**
The grader loads the output file with `data_only=True`, which returns `None` for any cell containing a formula. Therefore, never write Excel functions (IF, VLOOKUP, INDEX, MATCH, SUMIF, etc.) as strings; compute the result in Python and write the literal value.

- Always compute results and write literal values (numbers, strings, booleans) into answer cells. Do not write formula strings (e.g., `=VLOOKUP(...)`, `INDEX/MATCH`) unless the task explicitly requires formulas.
- Even if a task mentions a formula name (e.g., SUMPRODUCT, VLOOKUP), compute the result using Python and write the literal value. Only write an actual formula string if the instruction explicitly says to place the formula itself in the cell (e.g., 'put the formula text in the cell' or 'the cell must contain the formula').
- If the task instruction provides a specific number‑format string (e.g., `m/dd/yyyy`, `yyyy-mm-dd`, `#,##0.00`), use that exact string for the `number_format` property. After writing, verify that all cells in the answer range have that exact format string.
- Otherwise, when writing a date value into an existing sheet, copy the number format from a representative date cell: `target_cell.number_format = source_date_cell.number_format`.

- When copying data from source cells to output cells, always write the raw Python value (e.g., datetime object, int, float) rather than converting it to a string. Apply the source cell's number_format if it exists. After writing, reload and verify that data types in the answer range match the source column (e.g., print `type(cell.value).__name__`).
- Before checking a cell value for a prefix pattern, verify it is a string with `isinstance(value, str)`. Then normalize with `.strip().upper()` (or `.lower()`) and use `startswith(('PREFIX1', 'PREFIX2'))` to avoid misclassifying numbers or whitespace.
- When moving a column, use native methods: `ws.insert_cols(target_index, 1)` then `ws.delete_cols(shifted_source_index, 1)`. Never manually iterate and copy cells; that causes off-by-one errors and loses formatting.

- When a task asks whether a condition holds for a group (e.g., “for a week number” or “per employee and week”), treat each **contiguous block of rows sharing the same identifier and week** as an independent instance. Do **not** pre‑compute sheet‑wide summaries that can leak information from earlier blocks into later ones.
- **If the task explicitly requires formulas** (e.g., SUMPRODUCT, SUMIFS):
  - Use ranges that span the entire data section (all rows with values), not a fixed small block. After writing, read back the range argument and verify it matches `max_row` from inspection.
  - Inspect adjacent formulas in the same answer row to discover how they partition data by a key column (e.g., fiscal year). Mirror that partitioning in your formula to produce per‑group results.
  - After writing, check that formula strings in cells for different groups are not all identical; identical formulas indicate a single global aggregate instead of per‑group results.
- When building formulas with expanding ranges (e.g., COUNTIFS with a dynamic upper row), lock both the column and row of the starting cell reference with absolute anchors (e.g., `$B$2`). After writing the formula, read back the cell value and confirm that every fixed reference is fully anchored with `$` for column and row.
- When writing formulas intended to be copied across rows or columns, identify which references must stay fixed (e.g., configuration/dropdown cells) and lock them with `$`. After writing, mentally simulate copying the formula one row down: fixed inputs should not shift, row-specific references should increment, and lookup ranges should stay anchored. If any reference would break, add the missing `$` before saving.

- Before writing to a specific graded answer range (e.g., A1:D7), clear every cell in that exact rectangular range, regardless of the sheet's current `max_row`/`max_column`. After clearing, verify all cells in that range are `None`, then populate the range. This prevents residual data from previous attempts contaminating the graded cells.

- When data is separated by delimiter rows (e.g., 'TOTAL'), pre‑scan the sheet to identify group boundaries (start/end rows). Process each group as a unit before writing any values, and print the discovered boundaries for sanity checking.

- Before any structural modification (deleting rows/columns, inserting, moving), print the full range of affected cells (e.g., all values in the column you plan to delete from) to confirm the exact extent of data. This prevents off‑by‑one errors and ensures you are modifying the correct rows.

- When saving the workbook, use the exact path from the task's `output_path` field. Do not retype or guess. Verify the directory exists or create it if needed.
Before executing the script, echo the `output_path` variable to the console and visually confirm it matches the task's exact output path.
- After saving the workbook, print a confirmation message: `print(f'Saved workbook to {output_path}')`. This confirms the save operation completed without error.

- Never write formula strings (e.g., `=IF(...)`, `=VLOOKUP(...)`, `=SUMPRODUCT(...)`) into answer cells.
For example, instead of writing `=SUMIF(A:A,"111111",B:B)`, compute the sum in Python and write the numeric result. The grader reads cell values, not formulas, and will see `None` for unevaluated formulas. Always compute the result with Python and write the literal value.
- When a task asks to "display" values from another location (e.g., every nth row, or a constant like `$A$25`), compute the values in Python and write them as literal numbers/strings; do **not** use OFFSET, INDIRECT, or INDEX/MATCH formulas.
- If the task asks to 'modify a formula' or 'fix a formula error', treat it as a request for correct values unless it explicitly requires preserving the formula text. Compute the result in Python and write the literal value.
- After saving, reload the workbook and verify the output. Do not declare task complete until verification passes. See Verification section for required checks.

- When computing derived values (e.g., differences, ratios), inspect the source data to determine the typical number of decimal places, and round results to that precision. Use Python's `round(value, ndigits)`. After writing, verify by printing a few cells to check for floating-point noise.


- **Pre‑save check**: Before saving, scan the answer range for any cell containing a formula string (i.e., a string starting with `'='`). If found, replace with the computed literal value. For tasks expecting numeric results, also verify that all cells in the answer range are instances of `int` or `float` (not strings or formulas); replace any non‑numeric values with the computed numeric result. This catches accidental formula writes early.

- For text manipulation tasks (e.g., correcting capitalization, extracting substrings), always use Python string methods (`.title()`, `.upper()`, `.lower()`, slicing, `re.sub()`, etc.) to compute the result and write the literal string. Do not write Excel formulas for text manipulation, as the grader may not evaluate them (e.g., a non-existent function like `ISUPPER` would leave cells empty).

- When the task specifies a column by its letter (e.g., "BN"), convert it to a numeric index using `openpyxl.utils.column_index_from_string('BN')` before writing. Never manually count columns. After writing, verify by printing the cells in that exact column range.
- When the task provides a finite set of allowed output strings (e.g., “the possible outcomes are A, B, or X”), produce only those exact literals in the final cells—never join them with commas or other delimiters.

- When computing values for multiple rows that depend on a cell in the same row (e.g., a lookup key in column H), always read the source value for the current row inside the loop (e.g., `key = ws.cell(r, 8).value`) and use it in the computation. Never hard-code a single row reference (e.g., H4) and reuse it for all output rows. After writing, verify that each output cell's value corresponds to the correct row's input.

Always do this, even if you plan to write to every cell. Conditional writes or off‑by‑one errors can leave stale values; clearing first guarantees a clean slate.


After saving the workbook, you must immediately run the verification checks described in the Verification section. Do not issue TASK_COMPLETE until all checks pass. Printing a confirmation message like 'Done' is not sufficient; you must reload the workbook and inspect the exact answer range cells (values, types) to confirm they contain literal data, not formulas or None. Only then may you complete the task.
## Verification


After writing all output cells, save the workbook to the output_path with `wb.save(output_path)`. Then confirm the file exists on disk by running `ls -l <output_path>` (or `os.path.exists`). If the file is missing or zero bytes, re-save before continuing.
- Also verify the file is not empty: `assert os.path.getsize(output_path) > 0, 'Output file is empty'`. If the file is zero bytes, re-save and re-check.

Immediately after saving, reload the workbook and print the sheet dimensions and the first few rows (or the full sheet if small) to visually confirm the expected transformation (e.g., headers changed, rows deleted).



**Verify the entire answer range, not just a sample.** After writing, reload the workbook and loop over every cell in the exact answer range (all rows and columns). For each cell, check that its value, type, and formatting meet the task's requirements. Print the coordinates of any failing cell; the output should be empty. If any failures appear, fix the logic and re-verify the full range before completing.

After saving, reload the workbook with `data_only=False` to see stored values (not cached results) and print the exact answer range cells' coordinates, values, data types, number formats, and relevant style attributes
 Always loop over the exact answer range cells, not just a full sheet dump, to ensure every graded cell is inspected. (e.g., font name, fill). Assert that no cell is `None` and that no value is a formula string (unless explicitly required). Compare each cell's value against expected outcomes. If the instructions mention any specific expected values, confirm no extra values appear in that range.
- Verify that all cells in the answer range contain literal data values, not formula strings (unless the task explicitly requires formulas). Use a check like:
  ```python
  all(not (isinstance(ws.cell(r,c).value, str) and ws.cell(r,c).value.startswith('=')) for r in range(...) for c in range(...))
  ```
  If formulas are found, re-save with pasted values only.
Also scan for strings that resemble Excel functions (e.g., start with `IF(`, `VLOOKUP(`, `SUM(`) without a leading `=`; if any are found, recompute the literal value and re-save.
- For date cells, verify `.data_type == 'd'` and `.number_format` is a date format (not `'General'`).
- If the task specified a number format string, after writing, confirm that all cells in the answer range have that exact `number_format` string.
- Before any write operation, print the sheet's first row to confirm expected headers are present.
- After deleting or filtering rows, print a sample of remaining values in the affected column to visually verify correctness.
- Confirm the expected number of rows or cell values.

- After reloading, check that all required answer ranges contain non‑blank values. If any cell in a graded range is `None`, fix the output logic and re‑save before signalling task completion.
- For results that depend on per‑block conditions, after writing, loop over every row you marked. For that row’s identifier and week, examine **only the set of consecutive rows that immediately follow it with the same identifier and week**; confirm that those rows genuinely contain all required attributes. If any marked row’s block does not contain them, remove the mark and reconsider your grouping logic.
- If the task requires formulas, also verify that cells in the answer range have `.data_type == 'f'` and that the formula string matches the expected structure (e.g., print the formula and confirm it starts with `'=VLOOKUP'`). Additionally, confirm that any range references that must remain fixed (e.g., the start of a criteria range) are fully anchored with `$` for both column and row.

After any structural change (deleting rows/columns, moving columns), reload the workbook and verify the result: print the first row headers to confirm removed columns are gone; for row deletion, print the coordinates and values of the answer range to confirm that rows are removed (not just cleared) and that surviving data has shifted upward. Check that the row count decreased appropriately.

- After locating a target column by header, print its index and the header text for visual confirmation against the printed sheet rows.

- After writing, verify **every** constraint the instructions mention—including formatting and non‑answer‑range cells—across the full set of affected rows/columns. Use a systematic check like `all(cell.value is None and cell.fill.fill_type is None for cell in ws['H2':'H17'])` to confirm the entire range meets requirements.

- If the task involves numeric constraints (bounds, sums, counts), after writing load the workbook and programmatically assert those constraints hold for every relevant cell. Print the result of each check. If any assertion fails, correct the logic and re‑save before completing.

- After writing, verify every cell in the exact answer range specified (e.g., D2:D20), including any trailing empty cells, by printing its value and type; this catches formula artifacts and missing values.

- For tasks that involve deleting rows, after reloading, print the full answer range and confirm that no rows that should have been deleted remain, and that all cells contain literal values (not formulas).

- After saving, run a validation script that loads the output, loops over all cells in the exact answer range, and asserts that each cell's value is of the expected Python type and its `number_format` matches the required pattern. Print a single Boolean result (e.g., `All cells OK: True/False`) so you can see at a glance whether the output is correct.

- After writing fills, reload the workbook and verify that all filled cells have `fill.fgColor.rgb` starting with `'FF'` (opaque). Print `cell.fill.fgColor.rgb` to confirm.
- For subset‑sum tasks, after computing, print the sum of the chosen values and assert it lies within the required range. If the instruction mentions a unique combination, verify that only one subset satisfies the constraint.
- If the task provides a reference sheet (e.g., "Manual Result"), after writing output, load both the output sheet and the reference sheet and compare every cell in the answer range. Assert that each cell's value matches the reference. Print mismatches and only declare completion if all cells match.
- **Reference sheets**: If the task explicitly provides a reference sheet (e.g., "Manual Result") with expected values, after writing output, compare every cell in the answer range against that reference and assert they match. However, if a sheet named "Expected" or similar is present but not explicitly designated as the reference, do not assume its values are correct; such sheets may be incomplete templates. Always compute values yourself and verify against the task's explicit requirements.

- After saving, reload the workbook with `data_only=True` and confirm that all answer cells contain literal values (not `None` or formula strings). This simulates the grader's view and catches formulas that would evaluate to `None`.
- After cleaning numeric strings with regex, verify that all cells in the answer range contain only digits and at most one decimal point (no letters, currency symbols, or punctuation). Use a pattern like `re.fullmatch(r'[0-9]+(\.[0-9]+)?', str(value))` to confirm.

- For tasks that involve sorting or reordering rows, after saving, reload the output and programmatically verify that each block's values are sorted correctly (e.g., `assert vals == sorted(vals, key=str.casefold)`) and that no cell contains a formula string (no `=` prefix). Only signal completion after this check passes.


- After saving, reload the workbook and confirm that all non‑answer columns and sheets remain intact (print `wb.sheetnames` and a few cells from columns not in the answer range).

- **Sheet preservation check**: Load the original workbook and the output workbook, then assert `set(output_wb.sheetnames) == set(original_wb.sheetnames)` (allowing for any new sheets the task explicitly required). Print both lists side by side. If any original sheet is missing, you likely created a new workbook instead of modifying the existing one — redo the task with `load_workbook`.
- For tasks that expect numeric results, after reloading, assert that each answer cell's value is an instance of `(int, float)` and not `None` or a string. Print the type of each cell to confirm. Example: `assert isinstance(ws.cell(r, col).value, (int, float))`.

- After saving, reload the workbook and confirm that at least one stylistic feature from the original (e.g., header row is still bold, a cell retains its fill) is present. If the output looks plain or loses formatting, you likely created a new workbook instead of modifying the original; redo the task using `load_workbook` and direct modifications.
- **Final gate**: After all other checks, reload the output workbook and print every cell in the exact answer range (coordinates, values, types). Visually confirm that all cells contain literal values (no `None`, no formula strings) and that types match task expectations (e.g., `int`/`float` for numeric results, `str` for text). Only issue `TASK_COMPLETE` after this final gate passes.

**CRITICAL**: After saving, always reload the workbook from disk (`wb = openpyxl.load_workbook(output_path)`) and inspect the answer range. The grader reads the saved file, not the in‑memory workbook. Never rely on print statements from the writing script; they show the in‑memory state, which may differ from what is actually written to disk.
- For row-deletion tasks, after saving, reload the workbook and iterate over the exact answer range. Confirm that no cell matches the deletion criterion (e.g., `all(target_string not in str(ws.cell(r,c).value) for r,c in answer_range)`). Also run the literal-value check (see above) to ensure no formula strings remain. Print a summary like `Remaining matching rows: []` and `All cells literals: True`.
- If the task specified an enumerated set of allowed output values, verify that every cell in the answer range contains exactly one of those strings (no extra characters, no concatenation).

- After saving, reload the workbook and print every cell in the exact rectangular answer range (e.g., A1:D5), including any empty cells. Verify that the pattern of data and empty cells matches the expected output layout; the grader may check the entire range, not just non-empty cells.

- After confirming all cells are literals and non‑None, print a summary line: `nonformula literals: True, filled rows: N` to quickly confirm the answer range is fully populated with data values.

Also run `ls -l <output_path>` as a final shell check before declaring completion; this catches silent save failures and misnamed files.

- For conditional updates where you write a value only for rows that satisfy certain criteria, after writing, loop over every row in the data range and check: if the row meets the condition, the target cell must contain the expected value; otherwise, the target cell must be `None` or the neutral value. Print a count of mismatches (or a clean "all correct" message). This exhaustive check catches stray values that spot-checking misses.

- After reloading, also print each cell's fill color (e.g., `cell.fill.fgColor.rgb`) and border style (e.g., `cell.border.left.style`) for every cell in the answer range. This confirms that all required formatting has been applied and no residual formula text remains.

- When the task involves copying formatting from a source sheet, after reloading, print for each answer cell its value, number_format, and alignment.horizontal (and vertical if relevant) and assert they match the source sheet's corresponding cells. Example: `print(cell.coordinate, cell.value, cell.number_format, cell.alignment.horizontal)`.
- When the task provides an `answer_position` field (e.g., `B2:B5`), use that exact range for verification. Print every cell in that range and confirm all values are literals, non‑None, and match expectations. This is the range the grader will read.

**Automated verification is mandatory.** Do not rely on visual inspection of the first few rows; always run an automated script that checks every cell in the answer range programmatically. Print a summary of errors (or 'All checks passed').


**CRITICAL: Never skip verification.** After saving, always reload the workbook and run the verification checks described below before calling TASK_COMPLETE. Skipping verification leads to silent failures.


**Most critical check**: After saving, reload the output workbook and run this assertion for the exact answer range:
```python
assert all(
    cell.value is not None and not (isinstance(cell.value, str) and cell.value.startswith('='))
    for cell in ws[answer_range]
), 'Answer range contains None or formula strings'
```
This single check catches the majority of silent failures where the grader would see empty or unevaluated cells.
## Common Pitfalls


- Writing formulas into answer cells: the grader reads final cell values, not formula code. Always compute and write literal values directly.
- Writing formula-like strings without a leading `=`: Strings that look like Excel functions (e.g., `IF(...)`, `VLOOKUP(...)`, `SUM(...)`) are stored as text and will not be evaluated. Always compute the literal value in Python and write that instead.
- Case‑sensitive / whitespace‑sensitive text matching: Always normalize cell text before comparing. Use `cell_value.strip().casefold()` (or `.lower()`) and compare against a lowercased, trimmed set. Example: `if cell_value.strip().lower() in {'yes', 'na'}:`
- Row deletion index drift: When deleting multiple rows in openpyxl, iterate in reverse order (`for row_idx in range(ws.max_row, 1, -1)`). Print each deleted row index for auditability.
- Do not hard-code column positions. Always scan headers to find the correct column by label.

- Skipping inspection or verification: Always inspect the workbook structure before any modification, and always reload and verify the output after saving. A missing verification step can lead to silent failures.

- Column deletion index drift: When deleting multiple columns, collect the column indices, sort them in descending order, and delete from largest to smallest (`sorted(cols_to_delete, reverse=True)`).

- Hardcoded row ranges: Always determine data boundaries dynamically using `ws.max_row` and skip rows where the key column cell is `None` or a sentinel like `'\u2026'`. Never hardcode row numbers like `range(7,12)`.

- Writing INDIRECT or other cross-sheet formulas: these will not be recalculated by the grader (they show as `None` when read with `data_only=True`). Always compute the value in Python and write the literal result, even if a formula seems simpler.

- When deleting rows based on emptiness, iterate in reverse and test each cell with `cell.value is None or (isinstance(cell.value, str) and not cell.value.strip())` to treat whitespace-only cells as blank.

- Attempting to fix formula errors by editing formula strings: If a task asks to resolve a formula error (e.g., VLOOKUP #N/A due to whitespace mismatches), do not modify the formula string; instead, compute the result in Python and write the literal value, unless the task explicitly requires preserving the formula.

- Setting fill colors without an explicit alpha channel: When applying solid fills with openpyxl, always include the alpha channel set to `FF` (opaque). Use `PatternFill(fill_type='solid', fgColor='FF00FF00', bgColor='FF00FF00')` or `Color(rgb='FF00FF00')`. Omitting the alpha (e.g., `'00FF00'`) may produce a transparent fill (`'0000FF00'`).
- Copying answers from auxiliary sheets: If the task asks to identify a subset of values that meet a condition (e.g., sum to a target), compute the selection programmatically from the primary data sheet. Do not rely on pre‑marked cells in reference or answer sheets unless the instruction explicitly says to copy them.
- Applying string transformations to entire ranges without checking cell types: When cleaning data (e.g., stripping whitespace, replacing substrings, regex), always check `isinstance(cell.value, str)` first. Apply string methods only to string cells; leave numeric, date, and boolean cells untouched. After cleaning, verify that originally numeric cells are still `int` or `float` (not `str`).

- Overwriting cell formatting when changing a single attribute: When the task asks to change only one aspect of a cell's style (e.g., font name), always copy the existing style object, modify only the required property, and assign back (e.g., `f = copy(cell.font); f.name = '等线'; cell.font = f`). This preserves other attributes like size, bold, etc. After writing, spot-check a few cells to confirm other attributes remain.

- Using formulas to generate incremental sequences (e.g., `=MAX(B$7:B322)+1`): The grader reads cell values, not formulas, so the cell will be `None`. Always compute the maximum in Python and write the literal integer.

- Misinterpreting restart instructions: When the task says to restart a counting/comparison process from a specific cell (e.g., 'from the cell immediately right of the match'), treat that cell as the new reference, not the cell where the condition was met. After coding, print the new reference value after each match and confirm it equals the value of the cell specified by the restart instruction (not the matched cell).

- Losing cell formatting when reordering rows: When sorting, moving, or swapping rows, always copy the original cell's style and number format to the new position, not just the value. Use `copy(cell._style)` and `cell.number_format`. After reordering, reload the original and output workbooks and compare `.font`, `.fill`, `.border`, and `.number_format` for a sample cell to confirm formatting was preserved.


- Preserving formatting when copying data: When the task asks to maintain formatting (dates, numbers, fonts, etc.), copy the source cell's style using `from copy import copy; target_cell._style = copy(source_cell._style)`. Do not manually set `number_format` or other style attributes unless the task specifies a format. After writing, verify that a sample cell's `number_format` matches the source cell's `number_format` from the original workbook.
- Clearing entire sheet: When populating a sheet that already has auxiliary data (helper columns, reference cells), do not clear the entire sheet. Only clear the exact range of cells you intend to overwrite, typically the same dimensions as the source data. Before clearing, print non-empty cells outside that range to confirm they are not needed, then restrict clearing to that range.
- Destroying grouping order with a global sort: When a task specifies multiple sorting/grouping rules (e.g., "show X first in X order, then others in original order, and sort by column Y within groups"), build a composite sort key that encodes all levels at once, and sort only once. Never apply a separate global sort that destroys earlier grouping. After writing, spot‑check the output to ensure the dominant grouping order is still evident.
Creating a new workbook instead of modifying the existing one: Always load the original workbook with `openpyxl.load_workbook(input_path)`, modify the existing sheets, and save to the output path. Do not create a new `Workbook()` unless the task explicitly asks for a fresh file. Do not use `pandas.ExcelWriter` or any other library that produces a new workbook; always load and modify the original. After saving, reload and verify that non‑answer data (other columns, auxiliary sheets, formatting) is still present and unchanged. Print `wb.sheetnames` and assert they match the input workbook's sheet names (except any new sheets you were instructed to add). If they differ, redo the task using `load_workbook`.
- Deleting contiguous blocks of rows with manual loops: When you need to delete a contiguous block of rows (e.g., rows 1 to N), use the built-in batch deletion method `ws.delete_rows(start_row, count)` instead of iterating and deleting one by one. After deletion, reload the workbook and verify that the remaining data starts at row 1 with the expected values.

- **Sign convention for cumulative columns**: When computing a cumulative column from debit/credit or addition/deduction columns, explicitly decide which operation increases the target column before coding. After writing, inspect the full answer range for unexpected negatives or sign patterns that contradict your chosen convention; if any appear, re‑evaluate the direction of the operations.
- Stopping after inspection without writing output: Always follow the core workflow: inspect, write output, save, verify. If you inspect and then stop, the output file is not created and the task fails. Ensure you write the output script and save the workbook.
- Writing boolean formulas (e.g., `=RIGHT(A2,LEN(B2))=B2`) instead of computing the boolean in Python and writing `True`/`False`. The grader cannot evaluate formulas, so the cell will be `None`. Always compute the result in Python and write the literal value.

- **Finding the last data row**: Do not rely solely on `ws.max_row`; start from that row and scan upward until a non‑empty cell is found in the key column (e.g., `last = ws.max_row; while last > 0 and ws.cell(last, 1).value is None: last -= 1`). This handles trailing blanks and avoids hardcoding the row count.
- **Assuming target cell positions follow a pattern**: When the task maps source ranges to specific target cells (e.g., 'E2:E10 → H10'), create an explicit mapping dictionary before writing any values. Use that mapping to assign computed results to the correct cells. Do not assume a pattern like first block goes to the row where the block starts. After writing, iterate over every cell in the full answer range and confirm that only the specified target cells have values; all others must be empty. This catches misplaced values.
- **Manually counting column letters to indices**: Use `openpyxl.utils.column_index_from_string` to convert column letters (e.g., 'BN') to numeric indices. Manual counting often leads to off-by-one errors, especially for columns beyond Z.

- Repeating inspection without progressing to output: After the initial inspection (at most 3 turns), you must write the transformation script. Do not re‑run inspection commands unless the script fails and you need to debug. If you find yourself re‑running the same inspection command, stop and write the script.

- **Losing formatting when duplicating rows to a new sheet**: When moving or duplicating rows to a new sheet, always copy column widths (`src.column_dimensions[letter].width`), row heights, cell `_style` (via `copy`) and `number_format`. After writing, reload and verify that column A width and last column width match the original; print a warning if they differ.

- When deleting a pre‑computed list of row indices, sort the list in descending order (`sorted(rows_to_delete, reverse=True)`) before deleting one by one. This prevents index shift for all deletions.

- **Detecting formulas during verification but not fixing them**: If your post‑save verification prints formula strings (values starting with `=`), you must immediately recompute those values in Python, rewrite the affected cells, and re‑save. Printing the formulas and moving on is not sufficient—the grader will see `None` for those cells. This is a common failure even when the verification code correctly identifies the problem.
- Confusing row deletion with clearing cells: When the task says “delete rows”, always remove the entire row with `ws.delete_rows(row, 1)`, not just clear cell values. Clearing cells leaves empty rows that shift subsequent data incorrectly. After deletion, verify that the row count decreased and that surviving data moved up.
- **Hardcoding variable column lists for transpose/unpivot**: When transforming wide data to long format (or any operation processing a dynamic set of variable columns), never hardcode a fixed list of column names (e.g., `var_columns = ['Comp1', '2_comp', 'dept1']`). Instead, iterate from the first variable column index to `ws.max_column` and read each header dynamically: `for c in range(first_var_col, ws.max_column + 1): variable = ws.cell(header_row, c).value`. After writing, verify that the output row count equals `(number of data rows) × (number of detected variable columns)` and that every cell contains a literal value, not a formula.

- Using Excel functions (e.g., DATEVALUE, TEXT, VALUE, LEFT, RIGHT, MID, CONCATENATE, UPPER, LOWER) to compute values or manipulate strings: The grader cannot evaluate these formulas; cells will appear as None. Always compute the result in Python and write the literal value. This includes data type conversions, text extraction, and string transformations. Only use Excel functions if the task explicitly requires preserving the formula text.
- **Writing formulas that reference formula cells**: Even if the source cells contain formulas (e.g., VLOOKUP, ROUND), the grader cannot evaluate them. Always load the workbook with `data_only=True` to obtain the computed values (or error strings like `'#N/A'`) and use those in your Python calculations. Write literal results, not formulas.
- **Modifying header rows when applying per-cell transformations**: Always identify the header row (usually row 1) and start your processing loop from the first data row (e.g., row 2) to avoid altering the header text. After writing, print the header cell(s) and verify they match the original values.
- **Overcomplicating matching logic with key‑based lookups when row‑aligned comparison suffices**: When the task uses direct cell‑address examples (e.g., "compare B2 of Sheet1 with B2 of Sheet2" or "replace with the corresponding value from the ITEMS sheet"), assume same‑row correspondence. Do not build dictionary mappings or introduce key columns unless the task explicitly names them as lookup keys. After writing, double‑check that your matching logic is the simplest possible interpretation of the instruction — not a generic keyed search.


- **Writing unrounded float values when decimal places are specified**: If the instruction asks for a specific number of decimal places (e.g., '11 decimal places'), round the computed value to that many decimal places using `round(value, ndigits)` or `Decimal.quantize` before writing to the cell. The grader may compare the stored value, not the formatted display, so excess precision can cause mismatches. After writing, verify the decimal digits count (e.g., `len(str(cell.value).split('.')[1]) == expected_digits`).

- **Assuming row‑wise matching for cross‑table lookups**: When the task asks to retrieve a value (e.g., an ID) from a column based on search parameters that appear in a different set of rows, treat the entire column as the lookup space. Build a list of all candidate (key, value) pairs from the reference table and search across that full list, not just the row where the parameters happen to be. Before writing the matching code, print the list of candidate rows you will search to confirm you are covering the whole reference set. Only assume a same‑row correspondence if the instruction explicitly states a row‑wise pairing.

- **Restricting transformation scope to the answer range when the task says "all columns" or "all cells"**: Always inspect the full workbook to determine the extent of data. If the task asks for a transformation that applies to all columns or all cells (e.g., "find and replace across all columns"), write code that operates on every used cell in every sheet, not just the reported answer range. After writing, confirm that the output cells hold computed values, not formula strings.
- **Copying the reference table's header when reordering rows**: When the task instructs you to reorder a table to match a reference, keep the original table's header/labels intact; only rearrange the data rows underneath. Before saving, verify that the header cell(s) of the target table still contain the same text as in the original spreadsheet (load the input workbook and check).
- **Leaving formulas in reordered rows without recomputing**: After reordering rows that contain formulas referencing other cells, openpyxl does not recalculate them, so the output will show `None` or stale values. Compute the intended result from the newly arranged data and write it as a static literal value. After writing, reload with `data_only=True` and verify that all cells in the affected columns contain correct computed values, not `None` or formula strings.
- **Hiding zeros via cell value deletion**: When the task asks to display zeros as blanks, do not set the cell value to `None` or an empty string. Instead, keep the numeric zero value and apply a custom number format that hides zeros, e.g., `'0.00;-0.00;;@'`. After writing, verify that the cell value is 0 and the number_format's third section (the zero part) is empty.

- **Misinterpreting “delete these strings” as clearing the entire cell**: When the task asks to move a substring from one column to another and then “delete these strings” from the source column, only remove the substring that was moved, not the entire cell content. Inspect any ‘After’ or ‘Expected’ sheet to see the intended final state of the source column (e.g., a numeric prefix may remain). After writing, verify that the source column retains the expected non‑alphabetic prefix and that the header row is unchanged.

- **Ignoring formula-generated marker values when scanning for action triggers**: Always inspect both the raw cell values and their computed (data_only) values across the entire target range before deciding which rows to modify. When the instruction mentions a value like `"X"`, treat any cell whose *displayed* value is `"X"` as a candidate—whether it comes from a literal string or a formula. Confirm this by loading the workbook with `data_only=True` and checking the rendered content. After writing the output, verify that every relevant row has been handled by dumping the computed values of the affected range, not just a few spot checks.

- **Not preserving row formatting when inserting blank rows**: Whenever you insert separating rows via `insert_rows`, immediately copy the style, number‑format, and row‑height from the displaced row (or the row below) to the new blank row. Use `copy(ws.cell(r, c)._style)` for each cell in the new row, and set `ws.row_dimensions[row].height` to match. This keeps the spreadsheet readable and meets the usual expectation that modifications don’t break the visual layout. After insertion, verify that blank rows share the look of adjacent rows.

- **Fragile fill-color detection**: Do not use `in` or substring checks on fill color attributes (e.g., `'FFFF00' in fill_color`). This can cause TypeError if the attribute is an object, or false matches. Instead, first print the type and value: `print(type(cell.fill.fgColor), cell.fill.fgColor.rgb)`. Then use explicit equality: verify `cell.fill.fill_type == 'solid'` and `cell.fill.fgColor.type == 'rgb'` and `cell.fill.fgColor.rgb == 'FFFFFF00'`. Avoid substring containment.

- **Setting a column to a value only for matching rows without clearing the rest**: If the task asks to set a column to a specific value for rows that meet a condition (e.g., "set column Q to 'Yes' if conditions X, Y, Z are true"), first clear the entire target column (or the relevant data range) to a neutral value (e.g., `None` or `""`) for all rows. Then apply the conditional writes. This ensures that any pre-existing data in that column is removed and only the intended rows contain the value. After writing, verify that only matching rows have the target value and all other rows are empty/None.

- **Hardcoded row deletion for blank rows**: Never delete rows using fixed row numbers (e.g., `ws.delete_rows(6, 6)`) based on a one‑time printout; always programmatically determine which rows are empty by checking cell values. Use the reverse‑iteration emptiness check described above.
- **Insufficient verification**: Printing rows with `print(row)` does not reveal cell types or formula strings. Always reload the workbook and use the verification loop described in the Verification section to inspect each cell's coordinate, `repr(value)`, type, and `number_format`, and assert no formula strings. A simple row print will not catch cells that are formula strings instead of literal values.
- **Copying style proxies directly**: When copying cell formatting (alignment, font, fill, border), use `from copy import copy; target.alignment = copy(source.alignment)` — never assign a style proxy directly (e.g., `target.alignment = source.alignment`), which raises `TypeError: unhashable type: 'StyleProxy'`. Apply the same pattern for font, fill, and border.

- **Applying a threshold check to an aggregate sum instead of per‑cell**: When the task says to delete rows where a cell’s absolute value is below a threshold (e.g., “use an absolute value check with a threshold to identify values that are effectively zero”), always check each cell individually, not the sum of all values. After coding, print the first few rows with their absolute values and whether they would be deleted to confirm the per‑row logic.

- Writing empty strings (`""`) instead of `None` for blank cells: When the task says 'leave blank' or 'otherwise leave empty', set the cell value to `None`, not an empty string. After writing, verify that blank cells read back as `None` (not a zero-length string).

- **Ignoring example output ordering**: If the workbook already contains an example output sheet (e.g., "Expected", "Manual Result", or a sheet with the final answer), inspect it thoroughly and replicate its row structure and ordering exactly, unless the task explicitly requires a different layout. When the task describes an operation like "for each header, for each matching entry", construct your loops to process headers first, then matching entries, to follow the implied grouping. After writing, reload the output and compare the relevant range against the original example to confirm values and order match.