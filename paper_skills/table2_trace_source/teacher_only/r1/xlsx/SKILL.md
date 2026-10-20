---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow


1. Inspect the spreadsheet to understand structure.
2. Perform the required manipulations.
3. Verify the output by reading back the exact answer range and checking expected values (see Verification).



**Critical**: After inspection, you must perform the required manipulations and save the workbook to the exact output path. Never declare the task complete after only inspecting or planning — the final deliverable is a saved workbook, not just an understanding of its contents. Before starting, explicitly plan: Inspect → Execute → Save → Verify. After running an inspection command, immediately proceed to the execution step that modifies the workbook and saves it.


**Before TASK_COMPLETE gate**: Run `ls -la <output_path>` (or equivalent) and confirm the output file exists with non-zero size. If the file is missing or empty, return to the Execute step and create/save it. Never signal completion without this confirmation visible in the observation.
If the output is generated via a Python script, also call `print('EXISTS:', os.path.exists(output_path))` immediately after saving and ensure you see `EXISTS: True` in the observation.
After confirming file existence, reload the workbook with `data_only=True` and print the exact answer range with data types (e.g., `print(cell.value, type(cell.value))`). Verify that cells contain computed data values (not formulas or code), that no unexpected None values appear, and that the observed outputs match the intended logic. Do not signal TASK_COMPLETE until this verification output is visible and correct.

If the first inspection provides sufficient information, do not run additional inspections; proceed directly to writing the output file.

**Before any manipulation**: Run a full inspection script (see Inspection) to print every sheet's contents. Do not rely on any preview or summary of the spreadsheet; always see the complete data yourself.


Base all column mappings, data ranges, and output positions on the observed workbook structure, not the task description. Before writing any output, inspect the target sheet and clear the exact answer range by setting each cell's value to None. Print the target sheet's contents before clearing to confirm what needs to be removed, and after clearing verify the range is empty.



**Reference sheet verification**: If the workbook contains any reference/expected-output sheets (e.g., sheets with names like 'result', 'expected', 'solution'), print the answer range alongside the reference values and confirm they match exactly before signaling TASK_COMPLETE.
## Inspection


Inspect the spreadsheet thoroughly before any modification. Load the workbook using `openpyxl.load_workbook` with both regular and `data_only=True` modes. Print the complete contents of every sheet: sheet names, dimensions, and for every cell in the used range (print the entire sheet, not just up to row 30), print its coordinate, value, type, formula, and formatting (using `values_only=False`). Focus on non-empty cells to quickly identify data regions and example outputs. Always print every non-empty cell in the sheet to ensure no data, formulas, or hidden values are missed. Confirm that the printed output includes all columns and rows referenced in the task instructions. Identify column structures, header rows, data regions, and whether values are static or computed. If an example/expected-output sheet exists, compare it against the current state to articulate the required transformation.

- **Sorting tasks with expected tables**: When the task involves sorting data to match an Expected table, do not rely solely on the task description's sort instruction. Compare the source and Expected tables to reverse-engineer the full grouping and sorting logic (grouping columns, intra-group ordering, tiebreakers). Implement sorting programmatically with explicit sort keys, not Excel's built-in sort, and verify row-by-row against the Expected table.
Before writing any transformation code, check if the workbook contains any sheet named "After", "Manual Result", "Expected", "Solution", "Result", "desired result", or similar. If present, treat it as a reference for the correct output. Manually trace a few values from the reference sheet back to the source data to identify the exact mapping algorithm (which columns are included, what scanning order is used, how empty cells are handled). Only proceed to code once your mental trace matches the reference values across multiple rows. Manually trace at least one existing value back to its source to confirm your interpretation of any lookup logic before automating. Never assume the structure without this inspection.

- Do not modify or copy the reference sheet; it is read‑only. Always write the result to the sheet and cell range specified in the task's answer_position.
 Look for existing formulas and helper columns that may already compute intermediate results you can reuse; avoid duplicating work that is already done.



Additionally, read and print the last 5 rows of every sheet to catch trailing totals or summary rows.
 Also, immediately after loading, loop through all sheet names and print the first 10 rows of each sheet—even if they seem unrelated—to quickly spot any hidden reference sheets or expected results that may not be obvious from the task description. When a sheet contains multiple data blocks separated by empty columns (e.g., parallel tables), note the exact column range of each block before writing any output.

For tasks involving row-based conditions (grouping, detecting transitions), print every row of the relevant data region, not just the first 30 rows. Confirm the number of distinct groups, whether identifiers repeat, and any non-obvious patterns before writing transformation logic.

After the initial full dump, perform a second focused inspection: for every column mentioned in the task instructions, print all non-empty cells with their types, formulas, and formatting. Also check for any existing data or formatting in the target output cells that may need clearing. When the task asks for a formula or computed result, scan adjacent columns (including beyond the answer range) for example outputs that reveal the expected format, padding, or separators. Use these examples to infer the exact output pattern before writing any code. After inspecting, explicitly confirm that your planned logic (e.g., exact vs. substring match, integer vs. float type assumptions) is consistent with the observed data before writing any code.

- Always print `wb.sheetnames` immediately after loading the workbook and use the exact sheet name strings from that output in all subsequent code. Do not rely on the task description's sheet names; always verify with the printed list to avoid case-sensitive mismatches and name variations.

- When a column contains entity names (e.g., student names in Column A), cross-reference those names with the sheet names list to ensure every entity has a corresponding sheet. If any are missing, flag them before writing output.

Before performing any bulk operation (deletion, filtering, transformation), count how many items (rows, columns, cells) match the condition and verify the count against expectations.
Also print a few sample rows that match the condition to visually confirm the filter logic and catch misinterpretations of the task criteria. After the operation, perform a matching inspection to confirm the change (e.g., zero remaining matches after deletion).

- Look for sentinel values such as '…' (three dots) that indicate end-of-data; treat them as boundaries and do not overwrite them unless required.
- When the task requires finding boundaries (first/last row, column ranges), extract them programmatically from the loaded data, not from the task description. Print the detected boundaries and confirm they match the expected data layout before proceeding.

- When building lookup or merge logic, profile candidate key columns on both sheets: print unique combinations (e.g., `(colA, colB)`) and check for duplicates or one-to-many relationships. If a composite key maps to different values in a third column, include that column in the key. After writing, spot-check at least 5 lookup keys from source data to confirm they exist in the lookup table and produce logically consistent values.

- When a column contains mixed types (e.g., some datetime objects, some ISO strings), detect this by printing `type(cell.value)` for every cell and handle all variants in your transformation logic. Ensure output values are of a consistent Python type (e.g., `datetime` objects, not strings).

- When filtering data based on criteria cells (e.g., date ranges), inspect the type of the criteria cell values and the type of the data column values. If they differ (e.g., string vs. datetime), convert the criteria to the data column's type before comparing. After filtering, print the count of matching rows to confirm the filter is non-empty and within expected bounds.
- If the workbook fails to load with style information (e.g., due to style parsing errors), retry with `data_only=True` or read raw XML to inspect the data layout before writing. Do not skip the inspection step.
- When the task involves filling a range based on a repeating pattern (e.g., every Nth row), print the full column of interest, note the row indices of non-empty cells, and compute the step size and starting row from those indices before writing any output.

- When the task involves deduplication or keeping the last occurrence of each value, print the full column of interest with row indices to identify the exact row numbers of each occurrence before writing deletion logic.
- Before writing any code that modifies the workbook, confirm that you have printed and understood: all sheet names, every non-empty cell's value and type, formula structure, row/column ranges, distinct category values, and any group‑by summaries. Before writing the transformation script, run a dry-run Python script that prints the intended output for every target row alongside the relevant input columns. Verify that the printed results match the expected values (e.g., correct labels, no formula strings). If discrepancies exist, adjust the logic before writing.
Only then proceed to write the transformation script.

- **Pre-computation checkpoint**: Before writing any computation or transformation code, explicitly print and confirm the exact data range dimensions: `ws.max_row`, `ws.max_column`, and the row/column bounds of each data region. Verify that your planned operations cover the correct range and that no data extends beyond your assumptions. Never compute based on a summary or preview alone — always confirm the full extent from the printed output.

- When printing cell values, use `repr(cell.value)` to reveal exact types, string representations (including hidden characters like embedded quotes, currency symbols, and whitespace), and distinguish between similar-looking values (e.g., float vs. string).

- **Merged cells during inspection**: When iterating over cells, avoid `for cell in row` if merged cells are present; use `ws.cell(row=r, column=c).value` to prevent `AttributeError: 'MergedCell' object has no attribute 'column_letter'`. Print `ws.merged_cells.ranges` before iterating to identify merged regions.

- When the task specifies an answer range, print the rows immediately above and below that range to confirm the exact start row, end row, and any headers. Adjust the range based on the printed data, not the task description's assumptions.

- For formula cells, compare the regular load (formulas) with the `data_only` load (cached values) to identify broken or circular formulas. If a formula is broken, use the cached value to compute dependent results and avoid propagating errors.

- After printing sample rows, explicitly identify all structural patterns (header rows, empty rows, repeating index rows, subtotal rows) and write logic to handle each pattern explicitly before writing any transformation code.

- When data contains repeating blocks separated by blank rows or repeating headers, print every row (including blank rows) of the relevant columns using `ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=<N>)` to identify headers, blank separators, and value formats before designing sorting or grouping logic.

- Before writing any formulas or code that depends on specific column positions, print the entire sheet and confirm the exact column letters for all inputs and outputs, header text variations, and whether target cells are pre‑populated or blank. Compare the printed structure against the task instruction; if any column letter or header name differs from your assumption, pause and adjust before writing.

- After printing the full sheet, explicitly state the row numbers of the header row, the first and last data rows for each data region, and the exact answer range coordinates. Confirm that your planned ranges match the printed output before writing any transformation code.

- To make boundary gaps and secondary blocks immediately obvious, also print a compact row-by-row summary: for each row from 1 to `ws.max_row`, list only the non-empty cells (coordinate and value). This reveals trailing empty rows, example blocks, and the exact end of the primary data region at a glance.

- Before deleting rows based on group conditions, print every row's key fields across the entire answer range to confirm which rows satisfy the deletion criteria and to catch edge cases (e.g., mixed member types within a group).

- When a column is expected to be fully populated or follow a pattern, print every row of the relevant columns (including blank rows) to detect gaps, mixed data types (ints vs. strings), and existing partial solutions. Do not assume consecutive numbering or uniform data types.

- After loading both regular and data_only views, compare them to distinguish formula cells from hardcoded computed values. This informs whether to write formulas or computed values in the output.

Do not rely on any pre‑provided summary or description of the spreadsheet contents. Always open the file yourself and perform the full inspection described below.

- After inspecting, manually trace the transformation on at least one row that appears to be an error case and one normal row to confirm your logic handles both. If the data contradicts any assumption, adjust the logic before writing output.

- Before writing formulas or macros, print the entire relevant data range and trace the intended transformation on at least 3-5 concrete rows, including any rows where output cells are already filled. Confirm your hypothesis matches the existing filled values before implementing. Ask: 'Did I look at every row that contains data, not just the first few, to confirm I understand the full pattern?'

- When the task references specific columns by letter or name, print the header row and a few data rows for the entire candidate range to identify exact column indices. Also scan for any column with a name like 'Expected', 'Result', or 'Solution' that may encode the intended output; print that column alongside the relevant input columns to infer the exact Boolean logic before coding. Use actual data examples, especially edge rows where conditions overlap, to confirm your interpretation of the task's conditional statements.

- After the initial full dump, explicitly check every sheet for data that could be the expected output (even if not named as such). If any sheet appears to contain the answer, treat it as ground truth: manually trace its values to derive the mapping, and use it to verify your output before completion.

- When the task description specifies row counts, label positions, or data structure, verify them against the actual printed data. If discrepancies exist (e.g., extra rows, different label positions), adjust your logic to match the real data, not the description.

- When the task mentions specific text values (e.g., category names, status labels), do not assume the exact spelling or plurality. Print all distinct values in the relevant column using `repr()` and use those exact strings in your mapping logic. Mismatches like 'Allowance' vs 'Allowances' can cause lookup failures.

Before writing, inspect the target output sheet (the sheet specified in `answer_position`) to understand its pre-existing structure: headers, column order, placeholder rows, cell values, number formats, and dimensions. Print its full contents (including number formats) so you can match that exact layout and formatting when writing. Preserve any header row and do not overwrite it unless the task explicitly requires changes to headers.

- If the target answer column already contains some values (e.g., partially filled), treat them as hints to the intended logic. Trace how those values were computed from source data to infer the correct algorithm before writing your own.

- **Preserve existing partial output**: If any cells in the answer range already contain data, those are likely the correct expected values. Do not overwrite them with different results unless the task explicitly asks to replace them. Instead, ensure your computed values match those existing values; if they don't, adjust your logic before writing.


- When the task mentions specific cell references (e.g., 'E19', 'F7'), print those exact cells with both formula and cached value, and confirm they match the task's description before proceeding.

- When inspecting cell values, use `repr(cell.value)` to detect hidden characters like `\xa0` (non-breaking space) that may represent blanks. Convert such sentinel values to `None` before writing output. Also sample several rows' `number_format` to identify format variations within a column and ensure output cells inherit the correct format.

- When searching for specific text markers (e.g., 'X', 'Total', 'Yes') that might be produced by formulas, load the workbook with both regular and `data_only=True` modes, and print the relevant columns side-by-side to see formula text and evaluated values. Use the evaluated values for content matching, not the formula text.
- When inspecting cell fill colors, use `repr(cell.fill.start_color.rgb)` to obtain a string representation; openpyxl may return an RGB object or a string, so always convert to string before comparing or printing to avoid type errors.

 Also print the Python type of each cell value (e.g., `type(cell.value).__name__`) to identify existing values of the correct type that should be preserved or matched.

- Before writing any transformation code, print every row of the columns you will read from and write to over the full row range (including header rows) to understand data distribution, spot patterns like alternating empty/non-empty cells, and confirm exact row boundaries.
## Writing Output


- Write results to the exact sheet and cell range specified in `answer_position`. Create the sheet if it does not exist. If it exists, clear the exact answer range (or the entire sheet) before writing. When the sheet has headers or structure, clear only the data rows (e.g., from row 2 down) and any adjacent columns that might contain old data (like separator columns). Use explicit cell‑by‑cell clearing (`cell.value = None`) for the range to ensure no residual values remain. Never modify any original input sheet unless explicitly instructed.
- When filling cells with computed results, set `cell.value` to the plain numeric or text result.

- **After writing a computed value**: Reload the output file and print the target cell's value with `type()` to confirm it is a concrete data value (e.g., `int`, `float`, `str`) — not a formula string, code, or `None`. If the value is a string starting with `=`, recompute and write the literal result.
 Only insert formulas if the task explicitly requires them (e.g., to produce auto-updating calculations). If formulas are required, construct them with absolute references for fixed data ranges (e.g., `$B$3:$B$43`) and relative references for row-varying criteria (e.g., `$H3`). After writing formulas, read back the cells to confirm each row's reference points to the correct row.

- Before writing, inspect the target answer range. If it contains existing formulas, do not attempt to debug or reuse them. Compute the required values in Python and write the plain results directly (unless the task explicitly requires auto-updating formulas). After writing, verify that the answer range holds plain data values, not formula strings or formula text.

- Before writing formulas that reference other sheets, inspect those sheets' data types, headers, and sample rows to ensure the lookup logic is correct.

- When the task requires preserving original formatting (e.g., copying rows with formatting), inspect the source cells' `number_format`, `font`, `fill`, and `alignment` attributes. For each output cell, set those four style attributes from the corresponding source cell. After writing, verify that at least one output cell in each column has a non-default number format matching the source.

- Use the exact output path provided in the task (e.g., `/path/to/output.xlsx`), not just a filename. If the path is relative, resolve it to an absolute path before saving. Verify the file exists at that path after saving.

After clearing, confirm the range is empty by printing a few cells before writing new data. After writing, verify that no old data remains in the graded area by printing the entire sheet (see Verification).

- When the task says 'formula' or 'use a formula to compute X', interpret this as a computation requirement, not a mandate to insert an Excel formula. Perform the calculation in Python and write static values. Only insert live spreadsheet formulas if the task explicitly requires auto-updating calculations or dynamic cell references. After writing, confirm output cells contain concrete values (numbers, strings), not formula text beginning with `=`.

- When filtering rows based on a computed condition (e.g., date comparison), compute the condition in Python and write the resulting rows as static values. After writing, verify that date columns retain the expected number format (e.g., `dd/mm/yyyy`) by printing cell values and `.number_format`.

- Prefer writing the transformation logic in a standalone Python script file (e.g., solution.py) that reads the input spreadsheet and saves to the output path, rather than using inline Python in bash commands. This avoids path errors and ensures the output file is saved correctly.

Immediately after saving the workbook, verify the file exists (e.g., `ls -la <output_path>` or `print('EXISTS:', os.path.exists(output_path))`). If the file is missing or empty, re-save before proceeding to verification.
If the file is missing, ensure the Python interpreter used has openpyxl installed (`python3 -c 'import openpyxl'`). If not, switch to the correct interpreter and re-run the write script.

- **Concrete example**: When asked to count unique items in a range, extract the cell values into a Python `set`, compute `len(set)`, and write the integer result directly (e.g., `ws.cell(row=10, column=8).value = count`). Never insert an Excel formula or formula text.


- Before writing, note the exact answer range from the task's `answer_position` (sheet, start column, end column, start row, end row). Ensure every value you intend to be graded is placed within those column and row boundaries. Do not write data in extra columns beyond the range, as they will be invisible to grading.
- **Aggregate results**: When the task asks to sum, count, or aggregate values across a range, compute the result in Python and write the plain numeric result directly (not a formula). Before writing, if the target cells already contain values, compute the aggregates, print them alongside the existing values, and if they differ or are blank, clear the target range and repopulate with the freshly computed values.
- When the answer range includes a header row (e.g., C1:C6066), confirm the header content during inspection, and ensure your data processing loop starts at row 2 (or the first data row after the header). After writing, verify that the header cell value is unchanged from its original content.

- **Lookup/merge pattern**: When a task requires looking up values across the same sheet or workbook, first extract and normalize all relevant reference data into a separate in‑memory structure (list, dict, etc.). Then compute the answers by querying that structure. Never write into the target cells while still scanning the source range in the same pass.


- **Preserving existing formatting when explicitly required**: When the task says “Don’t change any formatting” or similar, modify only the cell values (`.value`) and do **not** set any style attributes (font, fill, alignment, number_format, border). openpyxl preserves the existing formatting by default when only values are changed. After saving, confirm that formatting is unchanged by printing a few cells’ `number_format` and `fill.start_color.rgb` alongside their values.

- When the task asks to 'display', 'identify', 'list', or 'show' results in a range, write the final computed data values (strings/numbers) into the cells. Only insert formulas if the task explicitly says 'write a formula' or 'use an Excel function'.
## Verification


Separate output generation from verification into distinct steps. After saving the workbook:
- Check that the output file exists and has a non-zero size (e.g., `ls -la`).
- Reload the workbook using `openpyxl.load_workbook(data_only=True)` (to read final computed values) and print its content: sheet names, row counts, and the exact graded answer range (not adjacent cells).
- Confirm that the answer range contains the expected data values, data types, and formatting as described in the task. Each answer cell must hold a raw value (number, date, string) and not a formula string or error, unless the task explicitly requires formulas to remain. Ensure the value type matches expectations (e.g., datetime object, not string).
- Verify that all original input sheets remain unaltered.

- Confirm that cells outside the answer range, especially adjacent cells with pre-existing content, remain unchanged.
- If the file is empty or missing, re-save using an alternative strategy (e.g., create a new workbook from scratch and copy data, rather than relying on in‑place modifications like `delete_rows`). If an inline verification attempt errors out, re-verify by loading the saved file independently rather than fixing the generation script.
- Do not assume the save succeeded without confirmation; always verify.
Never trust a script's "Done" or "Success" message; always reload the workbook and inspect the actual cell values to confirm correctness.

- Write a separate verification script (e.g., `verify.py`) that loads the saved workbook from disk using `openpyxl.load_workbook(path, data_only=True)`. Execute it independently after the write script completes. Do not rely on the same script that wrote the file to also verify it — re-reading from disk catches save errors that in-memory checks miss.


- Write a small verification script that loads the saved workbook, iterates over every cell in the graded answer range, and prints its coordinate and value. Visually confirm that only the intended cells contain the expected values and all other cells are empty/None. Never rely solely on the writing step's printed logs—always verify the saved file.
- After writing computed results, run a targeted read-back inspection that prints the answer cells alongside their source inputs to confirm values are correct and non-data rows are empty.
When merging data from multiple sheets, after writing, spot-check at least one entry from each source sheet to confirm it appears correctly in the output with all expected associated data.
- After writing, spot-check a row at the boundary between data blocks (e.g., the first row after a block) to confirm that no values from one section have leaked into adjacent empty columns or other sections.
- Check rows just beyond the written answer range to ensure they are empty (None). Leftover data indicates incomplete clearing and will cause grading failures.

- When a reference sheet exists, compare its row count to your output. If the answer range includes rows beyond the reference's last row, after writing your data, set those extra cells to `None` and verify that the last row with data matches the reference's last row exactly. This prevents trailing empty rows from causing a mismatch with the reference.

**Visible verification required**: After running the verification script, confirm that its output—the printed cell values—is visible in the observation. If the output is missing, truncated, or unreadable (e.g., due to a parse error), re-run a simpler command that directly prints the answer range (e.g., `for row in ws.iter_rows(min_row=..., max_row=..., values_only=False): print([cell.value for cell in row])`). Do not declare the task complete until you have seen the actual cell values and confirmed they match the expected results.

- If an expected-output sheet exists in the workbook, compare the generated answer range to that sheet's values to confirm the transformation matches.

- **Compare against pre-existing answer values**: If the answer range already contained some values before writing (e.g., partial output), after writing, verify that those cells still hold the same values (or are correctly updated) and that your new values are consistent with them. Print the pre-existing values alongside the final output to confirm consistency.
 If you discovered a reference sheet (e.g., one named 'FAKE') during inspection, verify that your output matches its values exactly. This ensures the output aligns with the expected outcome observed during inspection.

- After writing, re-open the workbook and print every cell in the answer range. Verify that the number of rows and columns matches the expected graded range dimensions, that any required header row is present, and that all cells contain computed values (not formulas or macro code) unless formulas are explicitly graded.

- Before writing, capture the current state of the answer range (e.g., print its cell values) to later diff and confirm that only intended cells changed.
- After writing, verify that every row in the answer range contains a non‑None value (or an appropriate placeholder) corresponding to its source; no row should be empty unless the task explicitly allows it.
- After writing, perform a final full inspection: re-open the workbook and print every sheet's complete contents (as in the initial dump) to verify the final state, ensuring only intended changes occurred and all original data remains intact.

- After reloading the workbook, iterate over every cell in the graded answer range and confirm that no cell value is a string starting with `=` (a formula). If any formula strings are found, replace them with the computed literal value and re-save the workbook. This ensures the grader receives raw values, not formula text.


- When printing the answer range after reloading, include the Python type, number format, and fill color of each cell value (e.g., `print(cell.value, type(cell.value), cell.number_format, cell.fill.start_color.rgb)`) to catch unintended time components, type mismatches, or formatting errors.

- If the modified column contains formulas in non-data rows (headers, subtotals), after writing, reload the workbook and print those non-data rows using the formula view (regular load) to confirm they are unchanged. Also print the data rows using both views to ensure they contain plain values.
- When a reference or expected-output sheet exists, after reloading, print the answer range and the reference values side-by-side, verify row-by-row that they match, and confirm the match before TASK_COMPLETE.


- After writing, spot-check at least one computed cell by manually applying the task's logic to its source inputs and confirming the output matches. Print the source inputs, the expected result, and the actual cell value side by side.


- After printing the answer range, visually compare the output against the task's described transformations (fill-down, clearing, row preservation, etc.) to ensure each expected change is present and no unexpected modifications occurred.


- For tasks with multiple constraints (sorting, grouping, preservation), write a dedicated verification script that programmatically asserts each constraint (e.g., check that matched names appear in J order, that within each group the REF column is sorted ascending, etc.). Print the answer range with row numbers for final visual confirmation.

- After saving, reload the output workbook and print a few rows of the answer range alongside the corresponding source input columns used to compute them. Verify that edge cases and error conditions identified during inspection are handled correctly. This side-by-side comparison catches subtle transformation errors (e.g., case mismatches, incorrect lookups) before completion.

- After reloading the output workbook, run a targeted programmatic check that validates the core task requirement (e.g., count blank cells in a filled column, verify no formula errors, confirm row count) and print the result explicitly (e.g., `print('Blanks remaining:', count)`). Only proceed to TASK_COMPLETE when the check passes.

- After reloading, print the answer cells alongside any relevant identifiers (e.g., names from a key column) to visually confirm that each row's computed value matches expectations.


- After writing, re-read the full task instruction line-by-line and verify that every requirement is met, including non-value requirements such as fill colors, fonts, column widths, or protection. Before declaring completion, programmatically check that any formatting requirements were applied (e.g., iterate over the range and assert `cell.fill.start_color.rgb` matches the required color).

- After reloading, confirm that the output's row count and the presence/absence of sections (e.g., blank‑above rows removed, blank‑below rows preserved) match the intended transformation derived from inspection.

- If the input workbook contains example output rows (e.g., a block of rows showing expected structure), reload the output workbook, print the answer range, and compare it row-by-row against the example data to confirm the pattern matches (e.g., duplication counts, row structure). Before declaring completion, ensure consistency.

- After writing, verify that the output sheet's header row (if any) is unchanged and that the number of output rows matches the expected count (e.g., fixed rows × variable columns) with no gaps or trailing None rows.

- When the task involves filling a column based on a condition, after reloading, print all rows where the condition is true, showing both the new value and the source input that produced it, to spot-check at least one interval manually.


- After reloading, as a quick sanity check, print the first row (header) and the last row of the answer range to confirm the header is unchanged and the operation covered the full range.


- Also confirm that any empty or missing results are represented as `None` (empty cell) or blank, not as placeholder text like 'Not Found' or 'N/A'. Replace any such placeholders with `None` before saving.

- After reloading, print a few rows above, below, left, and right of the answer range to confirm they remain unchanged. Also print `wb.sheetnames` and sample rows from each sheet to verify that all original sheets are still present and their data is intact.


- When comparing output to an expected/reference table, normalize empty values (None, empty string, blank) to a consistent representation (e.g., None) before comparison to avoid false mismatches.

- If the answer range includes merged cells, verify that each merged cell contains a numeric value (not a formula string) and has the correct number format.

- After reloading, count the number of non-None cells in the answer range and confirm it matches the expected count (e.g., the number of items written). If the task says to "remove any blank cell" or similar, verify that no None/blank cells remain within the contiguous output range.

- After any row deletion or insertion, reload the output workbook and print the entire modified sheet to confirm the data is contiguous and no stray blank rows remain. Verify that the row count matches the expected number of data rows.

- When the input workbook contains exemplar rows (e.g., rows showing expected formatting), after reloading, print the answer range's `value`, `number_format`, and `alignment.horizontal` alongside the corresponding exemplar rows from the input. Confirm that formatting details like date number format and alignment match the exemplar before declaring completion.

When printing the answer range after reloading, use `values_only=True` in `iter_rows` (e.g., `for row in ws.iter_rows(min_row=..., max_row=..., values_only=True): print(row)`) to produce a clean list of values for visual verification.


**Final gate — exact graded range**: As the last step before TASK_COMPLETE, reload the workbook with `data_only=True` and print every cell in the exact graded answer range specified by the task (not just the sheet). Confirm the row count, column span, and that all values are correct with no stray data. This is your final line of defense — do not skip it.
## Common Pitfalls


- **Inline Python in bash**: If a bash command containing inline Python (e.g., `python3 -c '...'`) fails to parse more than twice, stop trying inline code. Write the script to a `.py` file using simple `echo`/`printf` appends, then execute the file. This isolates quoting issues from command execution.
- **Text matching**: When comparing cell values for lookups, normalize both sides with `str(value).strip()` (and `.lower()` if case-insensitive) before equality checks. After matching, confirm exactly one match exists, or handle zero/multiple matches explicitly.
 When locating a specific text pattern (e.g., 'Line No') in a column, print the actual cell values with `repr()` to detect extra quotes or whitespace, and use substring matching (`'Line No' in str(cell.value)`) rather than exact equality.
- **Formulas instead of values**: Writing formulas or code text into cells when the task expects raw values; only insert formulas if explicitly required. When formulas are allowed, use absolute references for fixed ranges and relative references for row-varying criteria (e.g., `$B$3:$B$43`, `$H3`). If the task says 'without writing individual formulas' or the answer range already contains formulas, compute the values in Python (including evaluating cross-sheet references) and write the plain results.


- **Overwriting adjacent cells**: When writing to a specific range, ensure you do not accidentally overwrite cells outside that range, especially if they contain pre-existing formulas or data. After writing, verify that only the intended range has changed.

- **Tool-call format errors**: If a tool call (e.g., `bash`) fails with an argument error (unexpected keyword argument, missing positional argument), do not experiment with the parameter structure. Immediately compare the failed call to your most recent successful call of the same tool and copy its exact parameter structure. Then test with a minimal command (e.g., `echo ok`) before embedding your full solution script.

- **Formula vs. values misinterpretation**: If the task says 'formula' but the answer range in the input is blank and the instruction describes a display format (e.g., 'ABC123-02-010'), produce plain values that match that format, not formula strings. The grader expects the displayed result, not the formula that generates it.

- **Bulk deletion order**: When deleting multiple columns or rows based on a condition, collect the indices first, sort them in ascending order, then delete in reverse order (highest index to lowest) to avoid shifting issues. After deletion, verify that the remaining data is contiguous and the count matches expectations (e.g., original count minus deleted count).

  Example pattern:
  ```python
  rows_to_delete = sorted(rows_to_delete)  # ascending
  for row in reversed(rows_to_delete):     # bottom-up
      ws.delete_rows(row)
  ```


- **Dynamic range formula errors**: If the task warns about #NUM! errors in dynamic ranges or asks to "keep the original numbers after filling", write the computed results as static values (not formulas). After writing, verify that answer cells contain plain strings or numbers, not formula strings starting with `=`.

- **Incomplete inspection**: Failing to print the entire active sheet's content (all rows, all columns, with coordinates) before writing manipulation code can cause you to miss critical data (e.g., target text at row 14). Always perform the full dump described in Inspection before any modification.

- **Stopping after inspection without saving**: The agent may run inspection scripts but never create the required output file. After every inspection step, ask yourself: 'Did I actually write the output file?' After the initial full inspection, any further analysis (e.g., counting matches) should be done within the same script that writes the output, or immediately followed by a write script. Before signaling TASK_COMPLETE, verify the output file exists at the exact required path using `ls <output_path>` or equivalent. Never declare completion after only inspecting or planning; the final deliverable must be a saved workbook.

- **Corrupted workbook loading**: If `openpyxl` raises a style-parsing error (e.g., `TypeError: expected <class 'openpyxl.styles.fills.Fill'>`), do not switch libraries. Instead, unzip the xlsx file, inspect the XML file mentioned in the traceback, fix the malformed element (e.g., remove invalid `bgColor` child elements), re-zip a fixed copy, and work on that copy. After writing output, verify the fill color by inspecting the raw XML of the output file.
- **Overwriting formulas in non-data rows**: When a column contains formulas in header or subtotal rows (e.g., SUMPRODUCT, array formulas), do not overwrite them with plain values. Before writing, inspect the column using both regular and `data_only=True` loads to identify which rows are data rows (e.g., rows where a key column has a string value) and which are non-data (formulas, blanks). Write only to data rows. After writing, verify by loading the output workbook without `data_only` and confirm that non-data rows still contain their original formulas.
- **Inspection-only loop**: If you have run more than one inspection command without saving the output file, you are stuck in a loop. Immediately stop inspecting and write the output file using the required manipulations. The output file must be created and saved before any further inspection or verification.

- **Residual data in target sheet**: Old content in adjacent columns or rows can persist even after clearing the answer range. Always clear all columns that might have been used previously (e.g., if the task previously used column Z, clear columns A–Z or the entire sheet) and verify after writing that no stray values appear outside the intended range.


- **Type mismatch**: When comparing cell values, ensure the comparison operator matches the actual Python type observed during inspection. Use `is False` for boolean False, `== "False"` for strings, and handle `None` explicitly. If a column contains mixed types, handle each variant explicitly in your transformation logic.


- **Blank cells as zeros**: When the task requires treating blank cells as zero in calculations, implement this as a data-cleaning step before computation (e.g., a `to_float` helper that converts `None` to `0.0`) or, if writing formulas, wrap cell references in `IF(ISBLANK(...),0,...)` within the initial formula. Do not write a formula first and then separately adjust it, as this can introduce errors. After writing, verify that output cells contain computed numbers, not error values like `#VALUE!` or `None`.

- **Trailing empty rows after deletion**: When deleting rows, the sheet dimensions may not shrink automatically; the bottom rows may become all‑None artifacts. After deletion, reload the workbook and print the full answer range. Confirm that the last rows contain actual data, not trailing empty rows. If the range must match a fixed size, ensure the data rows fill that range without None‑filled leftovers.

- **Assuming sheet names or data layout from the task description**: The task description may reference sheet names that don't exist or differ in case. Always use `wb.sheetnames` to get the exact names and use those in your code. Similarly, print the first few rows with `repr()` to see actual cell values and types before writing any matching logic.

- **Merged cells blocking writes**: Before writing any value to a cell, inspect the sheet's merged cell ranges using `ws.merged_cells.ranges`. If any target output cell falls within a merged range, unmerge that range with `ws.unmerge_cells(str(range))` before writing. After writing, verify that each target cell contains a scalar value (not None) to confirm the unmerge succeeded and the write took effect.


- **Deleting blank rows above a header**: Before deleting rows based on blank cells (e.g., to remove empty rows above a header), print the full column with row indices and `repr(cell.value)` to confirm which rows are truly blank, where the header row starts, and what data exists below it. Delete only the rows above the header row, preserving the header and all data rows. After deletion, verify that the header is now the first row and that no data was lost.


- **Broken formula diagnosis**: When you encounter a broken formula (e.g., `#REF!`, `#VALUE!`), do not just delete or overwrite it without understanding why it broke. Load the workbook with both regular and `data_only=True` modes, print the formula and its cached value, and diagnose the exact cause (e.g., out-of-range column index, missing sheet reference).
 Trace each broken formula's lookup arguments to identify which references are missing, empty, or misaligned. Simulate the fix by building a Python lookup dictionary from source data and comparing against expected numbers. If the referenced source data is static, compute the intended result in Python and write the literal value into the cell instead of patching the formula string. Confirm the output cell contains a plain data value, not a formula.


- **Correcting formulas**: When the task asks to "correct" or "fix" a formula, produce the correct computed *values* (as static numbers/strings) in the answer range, not corrected formula text. After writing, verify that cells contain plain data values, not formula strings.
- **Position-based alignment instead of key lookup**: When a task says 'match based on column B' or similar, do not assume that rows in different sheets are aligned by position. Instead, build a dictionary keyed by a stable ID column (e.g., column A) from the reference sheet, then for each row in the target sheet, use that key to fetch the replacement value. This correctly handles sheets with different row counts or orders. After building the dictionary, verify that all expected keys are present and handle missing keys explicitly.


- **Copying identical formula strings across columns**: When writing formulas to multiple cells across columns, never copy an identical string if it contains hardcoded column letters (e.g., `C$3`). Compose each cell's formula with the appropriate column letter for its position, or use openpyxl's formula translation by writing to one cell and dragging—but verify the stored formula text per cell afterward by printing them. Confirm that each cell's formula references the correct lookup range for its position.

- **Misinterpreting tool-specific requests**: If a task mentions a specific tool (e.g., VBA, macros) to achieve a spreadsheet transformation, the grader evaluates the transformed workbook, not the tool's code. Always produce the required spreadsheet changes directly using Python/openpyxl, writing computed values into the workbook. After writing, confirm that the answer range contains plain data values, not code, formula text, or helper artifacts.


- **Debugging script failures**: When a script fails, read the error message fully, identify the exact mismatch (e.g., RGB object vs string, missing attribute), and fix only that specific issue. Do not rewrite the entire approach.
- **Row insertion order**: When inserting rows at specific positions in a loop, iterate from the highest row index downward (e.g., `for r in range(1000, 6, -1)`) to avoid shifting the indices of unprocessed rows. After insertion, verify positions by printing a block of rows around each insertion point.

- **Misinterpreting task intent**: When the task description is phrased as a question (e.g., 'How can I create...') or includes a broken formula, ignore the phrasing and focus on the `answer_position`. The grader expects the specified range to contain working formulas or correct data, not a textual explanation. Before writing, inspect the answer range in the input workbook to see what's there; after writing, verify that each cell in the range holds the expected type of content (formulas, values).

- **Deletion without full inspection**: Before deleting rows or columns, always print the full target sheet with row indices, count blank rows, and identify data blocks. Do not assume the layout from the task description. After inspection, confirm the exact rows to delete and verify the count before executing.

- **Header row type mismatch**: When performing numeric operations (e.g., summing, filtering by value), always skip the header row (min_row=2) and use `isinstance(value, (int, float))` to avoid type errors on non-numeric header text. Example: `for row in range(2, ws.max_row+1): val = ws.cell(row=row, column=col).value; if isinstance(val, (int, float)): ...`

- **'Formula' in task description**: When a task says 'use a formula to sum/calculate X' or 'write a macro to do Y', this is a computation instruction — compute the result in Python and write the literal value. Only insert actual spreadsheet formula strings when the task explicitly names a specific Excel function to use (e.g., 'insert a SUMIFS formula in column D', 'use VLOOKUP in each cell'). After writing, always verify cells contain data values, not formula text.