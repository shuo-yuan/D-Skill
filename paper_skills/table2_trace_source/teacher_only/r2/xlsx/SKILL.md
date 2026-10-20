---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow



1. **Inspect** – Dump every cell of every sheet to the observation log (see Inspection for details). This is the mandatory first step before any manipulation.
After the full dump, you may run a targeted scan of the output area and any columns referenced in the task to confirm emptiness, data types, and alignment. However, do not repeat the full dump or run multiple inspection scripts without progressing to writing.
2. **Write** – Produce the output, following the Writing Output rules.
  - Write computed values (not formula strings) unless the task explicitly asks for formulas.
3. **Execute** – Use the bash tool to run your solution script. Ensure it saves the output file at the exact path specified in the task. Confirm the file exists (e.g., `ls -la <output_path>`) before proceeding to verification.
4. **Verify** – Run verification checks as described in Verification.

- Before the full dump, note the `answer_position` and `instruction_type` from the task. If `answer_position` is a sheet range, your goal is to produce that exact sheet state, not code or formula text unless explicitly required. This prevents getting sidetracked by code‑fix requests in the problem description.
## Inspection


Before writing any transformation code, systematically inspect every sheet in the workbook.
 Always load the workbook with `openpyxl.load_workbook(filename, data_only=True)` to read computed values, not formula strings.

- Do not rely on any truncated `spreadsheet_content` snippet from the task prompt; always run the full dump script to see the actual data.

- **Before running the full-scan script, attempt to load the workbook with `openpyxl.load_workbook`. If loading fails (e.g., `TypeError` from broken fills), unzip the xlsx, inspect `xl/styles.xml` for malformed elements (like `<bgColor>`), patch them, re-zip, and retry loading. Only proceed with data inspection after the file loads successfully.**
- **Before any manipulation, list all merged cell ranges in each sheet you intend to modify (use `list(ws.merged_cells.ranges)`). Unmerge every range, then re-print the list to confirm it is empty. This prevents silent misplacement or errors when writing into merged areas.** Run a full-scan script that opens the workbook, lists all sheet names, prints each sheet's `max_row` and `max_column`, and then iterates over every row and column, printing `cell.coordinate=cell.value`, `type(cell.value).__name__`, and `cell.number_format` for every cell. This dump reveals headers, dimensions, data regions, and data types.

- **Immediately after loading the workbook successfully, print the sheet name, its dimensions (`max_row`, `max_column`), all merged cell ranges (using `ws.merged_cells.ranges`), and a preview of the first 30 rows (including the header) to confirm column positions and data structure before proceeding to the full dump.**
 When printing cell values, use `repr(cell.value)` to expose hidden characters or mixed types. Rely on this exhaustive dump, not on any snippet shown in the prompt. Before writing any cell, verify that you have read every existing value in every sheet. Additionally, inspect any sheet that shows the expected output (e.g., 'Result what i am expecting') to understand exact output format, including how missing IDs or empty values are represented.
- If a sheet appears to be a manual or expected result (e.g., named 'Manual Result', 'Expected', 'Result', 'Desired Result'), **you must print every cell in that sheet (all rows, all columns) before writing any code.** Treat it as the authoritative specification for the output pattern. Compare the task's verbal description with the sheet's layout; if there is any ambiguity (e.g., sorting order), the sheet's arrangement takes precedence.
 When the expected table is a transformed version of the source data (e.g., sorted, grouped, filtered), compare the source and expected rows to deduce the exact transformation logic: grouping columns, sort keys, ordering rules, handling of blanks, matching criteria (exact, substring, composite keys), and output formatting (delimiters, concatenation patterns). Use that inference to write your solution, and after writing verify that every cell in the output range matches the reference exactly. Summarize the layout clearly (e.g., 'Source 1 occupies rows 2–10, columns A–F; target range is J3:N5') and check whether existing cells in the target range contain values or formulas. For each cell whose value is a string starting with `=`, log it as a formula. If the task mentions formatting, inspect `number_format` and other style properties. Confirm that values, types, and ordering match the task description; build a mental model of the input structure and expected output. As a runtime check, ensure your preliminary script printed the header row and located the target column/row before attempting any move or deletion.

- When the answer cell is labeled (e.g., 'Answer:', 'Result:'), treat that as a directive to output a static value (number, text, date), not code, formula strings, or intermediate tools, unless the task explicitly requires code in that cell.

Before writing any logic that matches string values (e.g., filtering rows by a column value), print all unique values in that column and verify exact spelling and casing (e.g., 'Sick Day', not 'sick day').
After the dump, summarize the purpose of each column and confirm that you haven't missed any helper columns or formulas.
Identify any summary rows (e.g., TOTAL, subtotals) and formula cells that aggregate data; note their locations to plan clearing and avoid overwriting them incorrectly.

- If the data includes example output values (e.g., a column showing expected results), print those cells and cross-check your understanding against them before writing any code. After the dump, pause to verify that your planned output pattern matches any such examples exactly, including gaps, string formatting, and numbering conventions.

- When searching for a text value, check whether it appears as an exact match or as a substring (e.g., with suffixes) and plan your matching logic accordingly.

- While scanning, note any constraint-defining cells (e.g., rows with 'min'/'max' labels) outside the main data range; these may specify bounds for your output.


- Do not assume the sheet name mentioned in the task description matches any actual sheet name; always list all sheet names and use the exact names found.
- After printing sheet names, use those exact strings (including case) in all subsequent `wb[...]` calls; do not assume casing. Confirm that every sheet access in your script matches one of the printed names exactly.


- Look for helper rows or pre-sorted arrangements (e.g., a row with 'First Sort', 'Second Sort') that reveal the intended output structure or sort order.

- When the task involves finding columns or rows by a pattern (e.g., headers containing a keyword), programmatically count the matches and print the first 10 (column letters and header values) before acting. This confirms the pattern matches the expected count and avoids accidental deletions or moves.


- After dumping all sheets, examine every sheet for data that matches the expected output structure, even if the sheet is not labeled as 'expected'. Use any such reference sheet to validate your planned output pattern before writing.
When multiple sheets exist, print at least the first 10 rows of each sheet to detect any that might contain the expected output, even if not labeled as 'Expected'.
- Before writing any output, confirm that every sheet and cell you plan to reference exists and contains the expected data.
- After the full dump, for the target sheet, print all rows and explicitly note the indices of blank rows and whether they are fully empty or partially filled. Use this to plan deletions or data boundaries, and note any entirely blank rows or columns before the data region.

- When the task involves joining or looking up data across sheets, print distinct combinations of the columns you plan to use as keys (e.g., (date, meet)).
- When the task involves aggregating values by a key (e.g., summing preorders by item), scan the source data for duplicate keys. If duplicates exist, ensure your aggregation logic groups by the key and sums all values, not just the first occurrence. Group the lookup table by those key columns and print the count of rows for each combination. Verify that each combination uniquely identifies a target row. If any combination appears more than once, add more columns (e.g., date) to the key until each combination appears exactly once.
- When the task requires locating a specific text value (e.g., a header label like 'Invoice No.'), scan every row from 1 to `ws.max_row`, comparing cell values case‑insensitively (using `str(cell.value).strip().lower()`), and record the row number of the first occurrence. Do not rely on the sheet's apparent data start; always start from row 1.
- Before writing transformation logic on any column, print each cell’s value, `type(cell.value)`, and `cell.number_format` for that column to detect mixed data types (e.g., datetime vs string) and existing format codes that must be preserved or changed.

- When the workbook may contain formulas, load it twice: once with default settings (data_only=False) to see the underlying formulas, and once with data_only=True to see the computed values. Use the computed values to identify rows that need modification, but preserve formulas in non-target rows exactly as they were. After writing, verify that formulas outside the target range remain intact.

- **Before modifying a formula cell:**
- When writing or correcting formulas across a range, print all existing formulas in that range cell-by-cell and compare them to identify which references are locked (absolute) vs. relative. Confirm that the lookup column is the correct key column (e.g., a cycle-day identifier, not a date column). Print the cell's formula, its number_format, the values of all cells directly referenced in that formula (use `data_only=True` for evaluation), and at least 3–5 neighboring rows. If the formula uses a lookup function (e.g., MATCH, VLOOKUP), print the full lookup column(s) and verify that the lookup values are unique; if duplicates exist, a single-criterion lookup will return only the first match, so you may need to add additional criteria to uniquely identify rows. If the cell displays an error (e.g., `#REF!`, `#VALUE!`), also load the workbook with formulas and `data_only=True` and print every cell's formula and cached value for the entire sheet to understand the full context. Only proceed after you can explain what the formula currently does, why it fails, and what the corrected value or formula should produce. After writing the fix, reload the workbook and re-read the target cell to confirm it holds a non-error computed value (not a formula text or another error).

- When the data might have periodic spacing or skipped rows, after the full dump, explicitly check for repeating patterns in row indices (e.g., values every N rows) and note the step size before writing any logic.

- Before writing any transformation code, print the exact cell values, data types, and number formats for the entire target answer range and any source columns you'll be using (e.g., columns mentioned in the task). Use `repr(cell.value)` and `type(cell.value).__name__` to capture exact types. This reveals whether cells are already numbers, strings, None, or formulas, and prevents accidentally writing text where numbers are expected. Also print the first 5 rows of the target range to confirm emptiness or pre‑existing data, and the last 5 rows to confirm boundaries.
- Also print the last 5 rows of the target output range to confirm they are empty and that data boundaries are correct.
- **If the answer range already contains some pre‑filled values, treat them as a specification for edge‑case behavior.** Before writing any logic, manually run your intended rule on those pre‑filled cells and verify the result matches exactly. Pay special attention to blank cells at boundaries (e.g., first/last occurrence, interval start/end rows) — they reveal where the task‑giver expects no output. Only proceed after your mental model reproduces every pre‑existing value.


- After the dump, confirm that you have printed and reviewed every sheet in the workbook, and that you understand the data type (integer, float, string, None) of every cell in the source and reference ranges.


- Before constructing any formula, print the exact rows and columns referenced in the task (e.g., columns containing error status, difference values) to confirm actual cell contents, error values, and blanks. Adjust your approach if discrepancies exist.

- After the full dump, verify that you have read at least 20 rows beyond the apparent data region to confirm where data actually begins and ends. Print the raw cell values (using `repr`) to detect type mismatches (e.g., floats where integers are expected).

- After the full dump, scan the first 50 rows for repeated header rows (rows whose content mirrors the first header row) and for blank rows that separate data blocks. Identify the start and end rows of each block, note whether each block has its own header row, and log these patterns. Use this to design block-level operations (e.g., sorting each block independently) and ensure that your detection logic treats a row as a separator only when all relevant columns are empty.

- After the full dump, print a focused view of the columns directly relevant to the task (e.g., columns mentioned in the task description) to confirm the exact data blocks, header repeats, and empty rows you will need to handle. This focused view helps plan which rows to process and which to skip.

- If the task prompt includes a preview of the spreadsheet content (e.g., a table of rows), read it carefully before running the full‑scan script. Note the column headers, data types, patterns, and any partially filled answer columns. This pre‑inspection reveals the expected output format and helps you plan transformations.
- After the full dump, compare the number of data rows shown in the task's prompt preview against the actual rows found. If the actual data extends beyond the preview (e.g., the preview shows rows 1–5 but the sheet has data through row 7), adjust your processing range to include all rows. Verify that the row count you plan to process matches the graded answer range exactly, and note any initially blank cells you must fill.
- After the full dump, explicitly verify that your planned logic handles every observed cell state (e.g., None, integer, string with letters).
- Before writing any deletion or conditional logic, print the full answer range (including headers) and all key columns referenced in the task. Also print the full content of the columns and rows that will be affected by the deletion conditions. Verify that the data distribution (e.g., counts of 'Yes'/'No' in a Duplicate? column, distribution of Relationship values) matches the task's description and your mental model. Look for edge cases (e.g., non-blank cells where you expect blanks, data rows immediately below header-like rows) that contradict naive assumptions, and manually list the row indices you expect to delete and keep. Only proceed after this confirmation.
- Before writing any computed values to a column, print the target column and all input columns using both loads (normal and data_only=True) to distinguish between 0, None, and formula results. Use that to decide which rows need new values and whether existing formulas should be preserved or replaced.

- When comparing cell values to literal strings in your code (e.g., filtering, matching), always normalize by converting to a string with `str(cell.value).strip()` and treat `None` as an empty string `''`. This prevents false negatives from trailing spaces or empty cells.
- When the task includes a code snippet alongside a written goal, print the values in the condition column and verify that your filter matches the written description, not the code snippet. If they conflict, use the written description.
- After the full dump, for each sheet you intend to modify, explicitly note the row numbers of the header row, first data row, last data row, and any summary rows (e.g., 'Total'). Use these boundaries in your code; do not assume they match the task description.

- When inspecting, look for any second table or marker text (e.g., 'THE ABOVE TABLE WOULD BECOME:') that serves as an expected output example. Treat it as the authoritative specification for the output pattern, even if it resides on the same sheet as the raw data.


- After the full dump, explicitly note which columns are fixed identifiers (e.g., employee ID) vs. variable measures (e.g., metric names in a wide format), and confirm the shape (rows × columns) of each sheet. This ensures your transformation logic correctly handles unpivoting or reshaping.
- When an expected-result sheet contains trailing None rows (blank rows that are part of the output pattern), note their presence and ensure your output replicates them exactly.
- After the full dump, also print each row as a tuple (e.g., `for row in ws.iter_rows(min_row=1, max_row=ws.max_row, values_only=True): print(row)`) to clearly see empty rows and trailing None values. This view helps detect blank rows, incomplete data, and the exact boundaries of populated areas.

- When the task mentions comparing a specific cell (e.g., 'cell B2') between sheets, do not assume a row‑aligned comparison. Inspect all sheets, especially any that look like 'result' or 'expected', to discover a common identifier column (like an ID or serial number) that should govern the mapping. Build a lookup dictionary on that key, not on row position. This prevents row‑index misalignment errors.

- **If the target sheet already exists**, print the first row (header row) cell values and their Python types. If the task expects string headers (e.g., column labels), verify that every header cell is a `str`, not a `datetime` or other type. If mismatches exist, plan to overwrite those cells with the correct string values.

- After dumping all sheets, explicitly note any grouping keys, sentinel characters (e.g., `'\xa0'`), and formatting differences across sheets that could affect your transformation logic.
- After the full dump, explicitly list the columns involved, their data types, the exact number of rows, and whether a header row is present. Use this layout to anchor iteration logic (e.g., which column to process, direction of traversal).

- **When formulas are present, always use the evaluated values from the `data_only=True` load for any conditional logic (filtering, inserting, comparing). Do not rely on formula text to detect cell values.**

- **If a sheet access fails with a KeyError**, immediately print `wb.sheetnames` and use the correct name from that list. Do not guess; match by contextual clues (e.g., substrings, plural forms).

 Formulate a hypothesis about the pattern, test it against at least two example rows, and confirm it reproduces the given values exactly before writing any code.

- After inspection, confirm you can state the source data location and the target answer range before writing any formulas.

- After the full dump, explicitly identify: data ranges (start/end rows and columns), any parameter cells (e.g., date ranges, thresholds), header labels, and any cells that contain pre-existing example outputs. Use this list as a checklist before writing any transformation code.

- After the full dump and before writing any code, run a dry-run of your intended logic on the data: iterate over the relevant rows, apply your planned conditions/transformations, and print the row index, the source values, the computed result, and any existing value in the target cell. Verify that the output matches expectations for edge cases (including near-miss strings, pre-existing values, empty cells) and that anomalies are handled exactly as the task's literal specification dictates, not based on assumptions about intent.

- Before writing any code, confirm you can answer: What are the exact columns? Where are the headers? How does any existing output look relative to the sources?

- When the task involves copying or moving values between columns (e.g., 'copy G to K'), print the full column values for both source and target columns row‑by‑row to detect patterns (e.g., alternating non‑empty cells, complementary data) before writing any logic. Use this to design the correct loop or vectorized operation.

Also print aggregate statistics (e.g., distinct prefixes, total match count) from the dry-run to confirm the scope of the transformation matches the task description before writing.
## Writing Output


- Write computed final values (numbers, dates, text) into answer cells, not Excel formula strings like `'=VLOOKUP(...)'`, unless the task explicitly asks you to insert a formula
- When the task mentions macros, VBA, or code but `answer_position` specifies a sheet and cell range, produce the resulting spreadsheet state (cell values after the operation), not the code text. Implement the transformation directly in your Python script and save the result as cell values. Check `answer_position` immediately after loading: if it is a sheet:range, never write code-strings into those cells unless the task explicitly asks for code output. (e.g., 'write the formula', 'insert an appropriate Excel formula', 'the cell should contain a formula'). If the task asks to 'write the correct formula' or 'apply the formula' and the answer cell is labeled with 'Answer:' or similar, compute the result and write the value. Otherwise, when the task explicitly requests a formula, store the formula string (starting with `=`).

- If the task mentions code (e.g., VBA, Python) but the answer cell is labeled with 'Answer:' or similar, compute the result and write the value directly, regardless of the code request.
- Write only the sheet specified in the task's answer_position (e.g., 'MyResult'!A1:O20). Do not modify any other sheet unless the task explicitly demands it. Always verify the target sheet name and position before writing.

- Before writing aggregated data to a sheet, clear the entire target range (from the first data row down to the sheet's maximum row) to remove any leftover data from previous runs. After writing, verify that rows immediately after the last data row are empty.
- Before writing output, explicitly state the condition that determines which rows receive values (e.g., 'only at transition rows where the key field changes from the previous row'). Test your logic on a small sample of the data to confirm the condition matches the expected output placement.

- If the target range contains cells with background fills or other formatting that should not persist, clear both values and formatting (e.g., set fill to PatternFill(fill_type=None)).
- When a target sheet already contains example rows (e.g., a partially filled table), inspect those rows to determine the expected `number_format` and `alignment` for each column. When writing new data rows, apply those same formatting properties to the corresponding cells. After writing, reload and verify that the formatting of the newly written cells matches the example rows.


- When copying rows based on a filter, if the task says to include the header row, copy the header row first (unconditionally) before applying the row‑selection condition. After writing, verify that the first row of the destination range matches the source header in column count and cell values.

- When the task specifies different traversal directions for different operations (e.g., addition left-to-right, subtraction right-to-left), implement this as a sign- or operation-dependent column iteration order, not as a single fixed pass for all rows.


- After writing all cells, save the workbook to the task's specified output path with `wb.save(output_path)`. Immediately verify the file exists (e.g., `import os; print(os.path.exists(output_path))`) before proceeding to verification. An inspection script alone will not produce the deliverable; the solution script must include both writing and saving.
- Use the exact absolute path provided in the task (e.g., `/home/user/output.xlsx`). Do not convert it to a relative path or rely on the current working directory. The output path is always absolute.

- When filling a range, do not overwrite cells that already contain data unless the task explicitly requires replacement. Check each target cell's current value; if it is not None and not empty, skip writing.

- Even if the task mentions a specific Excel function (e.g., OFFSET, VLOOKUP), compute the result and write the value unless the task explicitly says 'write a formula' or 'the formula should be visible'.

- When computing sequential ranks within categories with tie-breaking by row order: group rows by the category column, sort each group by the value descending then by row index ascending, and assign sequential integers starting from 1. Confirm output cells contain actual integer values, not formula strings. After writing, verify that within each group ranks are sequential with no duplicates, and tied rows get consecutive different ranks.

- When applying number formatting to a range, only set `number_format` on cells that contain data (i.e., `value is not None`). Empty cells should retain their default format. After writing, spot-check one empty cell and one populated cell to confirm their formats differ as intended.

- Before writing any new output to a sheet (e.g., extracted rows, computed values), clear the target area of all previous content by setting each cell's value to `None`. This prevents contamination from old data or formulas. After writing, reload and print the full sheet to confirm only the intended data remains.

- When the task requires output "without decimals" (or similar phrasing), write integer values by setting `cell.value = int(round(...))` and `cell.number_format = '0'`. After saving, reload and verify the answer cells hold `int` values and their `number_format` equals `'0'`.

- When building the final answer, explicitly skip all header rows and completely empty records.

- If the task asks 'which formula could I use' or similar phrasing, but the answer range header indicates a result (e.g., 'Updated Values', 'Corrected Text'), write the computed result, not the formula text.
- When the task requires a column that accumulates a value per entity over ordered rows (e.g., running balance, cumulative sum), compute the final values in a script and write them as literal numbers. Do not insert formulas that reference the same column. After writing, verify the cells contain numeric values, not formula strings.

- After `wb.save(output_path)`, immediately attempt to load the saved file with `openpyxl.load_workbook(output_path)`. If loading fails, the file is corrupt or missing; do not declare completion.

- For tasks phrased as 'How can I...?' or 'create a macro that...', produce the resulting spreadsheet state with computed values, not the code or formula text, unless the task explicitly requires code output (e.g., 'write the formula in cell X').

- Before writing any output, load the workbook and check whether the target sheet already exists. If it does, inspect its contents; if they are partial, stale, or mismatched with the required output, delete the sheet or clear all its data before populating it. After writing, confirm the answer range contains only the newly written data, with no leftover rows or columns from a previous attempt.
- When the task specifies exact column names for the output, do not assume they are identical to values in the source data. Inspect both the required names and the actual source values; if they differ, create an explicit mapping from source values to target headers. After writing, verify each output header matches the requirement character‑for‑character.

- When the task specifies an `answer_range` (e.g., `'Sheet'!G1:I1000`), write data only into the columns within that range (G, H, I). Do not write into adjacent columns (e.g., J) unless the range includes them. After writing, verify that the answer_range's columns contain the expected values and no essential data is in ungraded columns.

- When populating summary cells (e.g., totals, balances), compute the aggregates in Python and write the numeric results directly. Do not use Excel formulas like `=SUM(...)` unless the task explicitly requires them.

- When the task description includes buggy code (e.g., VBA, Python) and asks for an explanation or fix, do **not** explain or repair the code. Instead, extract the intended spreadsheet manipulation, perform it on the provided workbook, and write the resulting computed values to the answer range. Inspect the answer range first to identify header rows that must remain unchanged, and after saving verify the answer cells contain plain data values, not formulas or error codes.

- When the task asks for an answer in a specific cell (e.g., 'output the answer in D2'), compute the value and write it directly as a number, text, or date. Do not write a formula like `=SUMIF(...)` even if it would produce the same result.

- After saving and confirming the file loads, reload the workbook and print the values and types of every cell in the answer range. This confirms the save produced the correct data before you proceed to verification.

- When modifying an existing workbook, preserve all existing formatting by loading with openpyxl (default settings) and setting only the `.value` attribute of existing cells; avoid creating new cells, sheets, or style objects unless the task explicitly requires formatting changes.

- When the task specifies an exact answer range (e.g., `'Sheet'!A1:D22`), clear every cell in that range (all rows and columns) by setting each cell's value to `None` before writing any new data. Do not assume that only the rows you intend to fill need clearing; leftover data in other cells of the range can cause grading errors.
## Verification


After writing, perform these verification steps:
- Reload the workbook and verify the output file exists and has non-zero size. Do not rely solely on print statements from your script.
- Confirm the active sheet is correct (check `wb.active.title`).
- Print and inspect every sheet that existed in the input file. Confirm that only the intended sheet was created or altered and that all original sheets retain their exact content.
- Print the full answer range and read back the answer cells: confirm they contain plain data values (not formula strings starting with `=`, and not code text such as VBA or Python), unless the task explicitly requires formulas or code. Verify the expected value and data type, and ensure every cell in the answer range is non‑empty and of the correct type. Print the Python type of each answer cell's value (e.g., `type(cell.value).__name__`) to catch any unexpected strings or None values.
- **After reloading, print the first row of the answer range and verify that any header cells are plain strings (type `str`), not `datetime` objects or numbers, unless the task explicitly requires non‑string headers.**
- If the task requires formulas, after writing, print the formula strings of a few adjacent target cells and verify that relative references (e.g., column letters without `$`) adjust correctly for each cell position, and that absolute references (with `$`) remain fixed as intended. Also reload with `data_only=True` and print the computed values of the answer range to confirm they resolve to data, not error values (e.g., `#REF!`, `#VALUE!`).
- Check that date cells have appropriate number formatting.
- When the task requires date-only values (no time components), reload the workbook and verify that any datetime objects in the answer range have `hour==0`, `minute==0`, `second==0`, and `microsecond==0`. If time components remain, adjust the transformation to strip them (e.g., build new `datetime` objects with only year, month, day).
- If an expected‑result sheet (or any reference pattern sheet) was provided, print both the answer range and the reference range, then compare them cell‑by‑cell to verify that structure and values match.
- Spot-check at least one computed value by manually recalculating it from the original source data and verifying the result matches the output.

- Read back the answer range with context columns: print each cell's row, value, and the values of the key columns used in your logic (e.g., employee, week) to confirm output is on the correct rows and that no unintended values remain.
- If the task description includes example computed values, print the first few rows of your answer range and verify the numbers match those examples exactly.

- If the task specifies constraints (e.g., min/max values, sentinel values like 0 in certain columns), reload the workbook and programmatically verify every cell in the answer range satisfies these constraints. Print a success message only if all checks pass.


- If the task required copying a header row, reload the output workbook and confirm that the first row of the destination range contains exactly the same number of columns and the same cell values as the source sheet's header row.


- After writing, reload the workbook and print the exact answer range. Verify that the output pattern matches expectations: check for continuity, correct prefix/suffix construction, zero-padded numbering, and that empty cells remain where the input had gaps.


- Embed verification logic directly in your solution script: after saving the workbook, re-open it and print the final values and any formatting attributes (e.g., fill type, number format) of the answer range. Do not declare TASK_COMPLETE until you have confirmed the printed output matches expectations.

- After printing the answer range, compare the printed values cell-by-cell with the plan you derived from the task description. At minimum, verify the first data row and the total number of written rows match expectations.
- When your transformation depends on a condition (e.g., clearing cells where another column is empty, copying values only when a stop column is non‑empty), verify that the condition holds for every affected cell: target cells are None where the condition is false, and the operation stops at the correct boundary without spilling into header rows or beyond.


- When the task specifies a grading answer range (e.g., D8:D11), reload the workbook and print those exact cells as the final check before signaling completion. Confirm the cells contain real data values, not None or formula strings.

- After writing, reload both the original and modified workbooks and compare the cells you intended to change. Any cell that already had a value in the original must still hold the same value in the output, unless a deliberate replacement was required.
- After any row or column deletion, reload the workbook and print the entire sheet (or at least the full range from row 1 to the last data row) to confirm that the intended rows/columns remain and that the deleted ones are gone. Also verify that preserved rows still contain their original cell values (not formulas or shifted references).
- Also verify that the resulting data rows are contiguous (no blank rows remain within the data range).

- When verifying formatting (e.g., cell fill, font), after reloading, confirm the style attributes via the library's API; for a definitive check, inspect the raw XML using `zipfile` to verify style definitions (e.g., `xl/styles.xml` for `FF00FF00`).

- If you computed ranks, verify that within each group ranks are sequential and no duplicates, and that tied rows within the same group get consecutive different ranks.

- Before writing your transformation code, enumerate the expected final values for at least two representative cells, especially those containing edge cases (e.g., mixed text and digits, multiple decimal points). After execution, compare your actual output against these pre‑written expectations to quickly spot discrepancies.

- After printing the answer range values, also print each cell's number_format and font.name to quickly confirm formatting is applied as expected.


- When the output contains multiple blocks (e.g., sorted groups separated by blank rows, each with its own header), print enough rows to cover at least two full blocks and verify that sorting is correct within each block, blank separators are intact, and headers appear at the top of every block.

- After writing, reload and print the full target sheet (or at least a few rows above and below the answer range) to verify that no stray formulas, extra rows, or leftover values contaminate the output.

- When sorting rules appear to conflict (e.g., 'keep original order inside a group' vs. 'sort column H lowest to highest'), re‑read every sorting‑related phrase in the task. Look for additional clues such as a hidden sheet or a reference list. Ensure the most explicit numeric‑sort rule is satisfied. After writing, scan the first few output rows and verify that within each group the specified sort column is in ascending order.

- After writing, scan the output data rows (excluding the header row) for any text that matches known header labels; if any appear, your row selection logic has erroneously included a header row. Correct and re-run.

- The reload-and-print cycle is your primary defense against silent writing errors: cells that saved successfully but contain wrong values, empty cells, or formula strings instead of data. Always print the full answer range after reloading and visually confirm correctness before declaring completion.

- After reloading, spot-check at least one positive and one negative example: pick a cell/row that must satisfy the task rule and one that must not, and confirm both are correct. For deletion tasks, verify that a row that should be deleted is absent and a row that should be kept is present.
- After writing, reload the workbook and programmatically count the number of blank cells in the answer range. Print a summary (e.g., `Total blanks remaining: 0`) to confirm complete coverage before finishing.
- After printing the full answer range, manually inspect a few rows where the result should be non‑trivial (e.g., rows with non‑zero inputs, complex calculations) and confirm they follow your intended logic. Only declare completion after this spot‑check passes.

- If the input workbook contains a column with expected results (e.g., header 'Expected', 'Target', 'Result'), after writing, reload the output and print a row‑by‑row comparison between your answer column and that expected column. Mark mismatches and confirm all non‑header rows match before declaring completion.
- After saving, reload the workbook and print every cell in the exact answer range specified by the task (e.g., `'Sheet'!A1:F9`). Scan the printed output to ensure it contains the intended data values and no formula text or stale code artifacts.

- After reloading, print the output sheet's dimensions (`max_row`, `max_column`) and confirm they exactly match the answer_range specification. Print all non‑empty cells in that range and compare the data pattern with any example data or specification embedded in the source workbook.

- After any modification (deletions, insertions, writes), reload the workbook and print the full answer range (or the entire target sheet from row 1 to max_row). Confirm the row count, header integrity, and that all data rows contain correct values (not formulas or None unless expected), and no trailing empty rows remain. This is the final check before declaring completion.

- After reloading, print a focused excerpt of the answer range (e.g., rows where a key condition is true) and verify that the values are plain data (not formula text) and match your mental benchmarks.

- After reloading the workbook for verification, use `openpyxl.load_workbook(output_path, data_only=True)` to read computed values. Print the exact graded answer range (the columns specified in the task). Also print a few surrounding cells (above, below, left, right) of any modified cells to detect unintended changes. Spot‑check the header row, first data row, a middle row, and the last data row to confirm values are correct, no formula strings remain, and data boundaries are correct. For key‑based lookups, additionally spot‑check a row where the source and reference differed to confirm the replacement used the correct key.

- If the task requires cell formatting (fill, font, border), after reloading, loop over the answer range and print each cell's `value`, `number_format`, and the relevant style attributes (e.g., `cell.fill.start_color.rgb`, `cell.font.color.rgb`). Verify these match the specification before declaring completion.
- **Final file check before completion:** After all other verification steps, run `ls -l <output_path>` using the bash tool. Confirm the output shows the file exists with non‑zero size. Do not declare TASK_COMPLETE until you see this confirmation. This is a mandatory final step.

- After reloading, print the exact graded answer range as specified in the task (e.g., `'Before'!K2:K19`), not just a broader inspection of nearby columns or rows. Verify its dimensions match the `answer_range` and compare each cell's value against the intended operation. If the range is larger than the data you wrote, confirm that the remaining cells are genuinely empty (`None`) and not stale data.


- After reloading and printing the answer range, count the number of non‑empty cells (e.g., using `sum(1 for row in ws.iter_rows(min_row=..., max_row=..., min_col=..., max_col=..., values_only=True) for v in row if v is not None)`) and verify the count matches the expected number of output cells. If the count is off, inspect for missing or extra values before completing.

- **After clearing an output area and writing new data:** reload the workbook and print every cell in the output columns from row 1 to `ws.max_row` (or at least from the header row to the last possible row), showing `coordinate`, `value`, and `type`. Confirm that only the intended rows contain non‑`None` values; any leftover data indicates incomplete clearing.

- If the answer range contained pre‑filled example values before writing, after reloading verify that those cells still contain their original values (unchanged).


- **If the system rejects your completion with 'Output file was not created' despite `ls` showing the file:** do not just re‑run `ls`. Re‑read the file's content (e.g., load with openpyxl and print summary) to confirm it's valid. Compare the saved path with the exact `output_path` from the task; if they differ, re‑save at the correct path. Only signal completion after confirming the file is at the exact path and contains correct data.

- If the task specifies an answer_range (e.g., `'Sheet'!A1:E19`), after writing, print the values of cells immediately outside that range (e.g., the first cell to the right, first cell below) and compare them to the original workbook to confirm they are unchanged, unless the task explicitly required modifications outside the range.
## Common Pitfalls


- Setting the active sheet with `wb.active = wb.sheetnames.index('SheetName')` raises a TypeError. Assign the worksheet object directly: `wb.active = wb['SheetName']` or use a 0‑based index (e.g., `wb.active = 0`).
- **Heredoc parsing failures:** Avoid heredocs that contain unescaped curly braces `{` or `}` in bash actions; they can break the action parser. Instead build the script line‑by‑line with `echo` and verify the file with `cat` before execution.
- Declaring completion before verifying output files exist and are non-empty.
- **Moving columns without preserving formatting**: When moving a dynamically found column (e.g., by scanning row headers), capture every cell's `value`, `number_format`, `font` (use `copy(cell.font)`), `fill`, `border`, and `alignment` for all rows (1 to `ws.max_row`). After inserting the target column (e.g., `ws.insert_cols()`), write these exact attributes to the new column's cells. After saving, load the workbook and verify that the moved column's values and a representative formatting attribute (e.g., `.font.name` or `.font.color.rgb`) match the original.
- **Missing fallback paths**: When the task specifies alternative behaviors for missing data, explicitly implement every fallback path with None‑checks or empty‑checks before the main logic. After writing the solution, verify that every conditional branch described in the requirements is implemented and that fallback values are drawn from the correct location.

- **Sorting by text labels containing numbers:** When instructed to sort by a number that appears inside a text label, extract the numeric part (e.g., using regex) and sort by the integer value, not by raw string comparison. Verify that numbers like 9 and 10 appear in ascending order.
- **Writing computed values when formulas are required:** When the task says 'write formulas' or 'insert formulas', you must write formula strings (starting with `=`) into the cells, not the computed numeric results. Verify after saving that the target cells contain formulas (cell.value starts with `=`).

- **Bash tool call format**: When invoking the bash tool, pass the command as a plain string (e.g., `\"python script.py\"`), not wrapped in a dictionary. If you receive an interface error, stop and inspect the expected signature; try the simplest possible call. If the interface remains unclear, write the logic to a Python file and run it with a minimal bash call, verifying the command runs and produces the expected output file before proceeding.

- **Fixing broken formulas instead of computing values:** When the input spreadsheet contains formulas that produce errors or incorrect results, do not attempt to debug or fix them. Instead, load the raw data, compute the correct results programmatically, and write the computed values directly to the answer cells. This avoids cross‑application formula issues and saves time. Verify that the written cells contain data values (not formula strings) unless the task explicitly requires formulas.


- **Deleting multiple columns/rows:** When deleting more than one column or row using index lists, sort the indices in descending order and delete from rightmost/leftmost to leftmost/topmost to avoid shifting corruption. After deletion, verify that the new max column/row count equals the original minus the number of deleted items, and scan the first 20 headers for any remaining items that should have been deleted.


- **Transposing multiple associated values:** When the task asks to transpose values from a lookup (e.g., 'transposed manner, going across the row'), collect every relevant value column from every matching source row, not just the first match. Flatten all (val1, val2, ...) pairs into a single list and write them consecutively across the row. After writing, verify that for each lookup key the number of non‑empty cells in that row equals the total count of value entries across all matching source rows, and that the first output column holds the first value from the first matching source row.
- **Deleting blank rows within a dynamic range:** When the task says to delete blank rows in a column starting from the first value and stopping at the last, compute the boundaries from the data: scan the column to find the first and last non‑blank row. Build a list of rows where the target column is `None` between those boundaries, then delete from bottom to top. After saving, reload and verify that every cell between the computed first and last row is non‑blank. This prevents accidentally deleting header rows or data before/after the range.
- **Inspection without output**: Running an inspection script that reads the workbook but never calls `wb.save(output_path)` will leave the output file missing. Always include the save step in your solution script and confirm the file exists before declaring completion.

- **Skipping script execution**: Never declare TASK_COMPLETE without having used the bash tool to run a script that produced the output file. Always verify file existence with a bash command (e.g., `ls -la <output_path>`) before declaring completion.


- **Never ending after inspection only**: If you have only inspected the workbook and not saved any output file, the task is incomplete. After inspection, you must write the solution script, execute it, and save the workbook. If the system reminds you that the output file is missing, stop inspecting and immediately write and save the required output. Do not repeat inspection loops; move to writing and saving.

- **Circular references:** If a formula references a range that includes its own cell (e.g., `MAX(B$7:B377)` in row 323), adjust the range to exclude the formula cell (e.g., `B$7:B322`). If formulas are not required, compute the value instead. **When writing a new formula, first check that the target cell is not referenced by the formula itself (directly or indirectly). If it is, or if the cell is part of a chain that could create circularity, compute the literal value from source data and write that instead.** After writing, verify with `data_only=True` that the cell holds a number, not `#CIRCULAR!`.

- **Saving with a relative path:** Always pass the full absolute output path to `wb.save()`, as given in the task. After saving, verify the file exists at that exact path with `ls -la <absolute_path>`.

- **Position‑based splitting for tagged substrings:** When extracting a tagged substring that ends at a delimiter (e.g., `Collection‑Name, ...`), do not split on the delimiter and take a fixed index; the tag may appear anywhere in the cell. Instead use a regex with a negated‑character‑class capturing group (e.g., `r'Tag-([^,]+)'`) to extract the text after the tag up to the delimiter. Write the captured value as plain text, never as an Excel formula. After saving, reload and verify every output cell holds a non‑empty plain string (no `=` prefix) where the source contains the tag.


- **Applying numeric conditions to non-numeric cells:** When a task asks to filter or delete rows based on a numeric range (e.g., "values between 1 and -1 inclusive"), first inspect each target cell's data type. Only apply the condition to `int` or `float` values (e.g., `if isinstance(value, (int, float)) and abs(value) < THRESHOLD`); treat text headers and `None` (empty) cells as not matching the numeric range, unless the task explicitly instructs otherwise. After writing the filtering logic, reload and verify that any header row is preserved and that only the intended rows were deleted.

- **Tool-call signature errors:** If a bash tool call fails with an argument-related error (e.g., unexpected keyword, missing required argument), immediately test with a minimal command (e.g., `echo test`) to verify the calling convention. Once the trivial command works, reuse the successful pattern for the real script.
- **Writing formulas programmatically without adjusting relative references:** When the task requires formulas that behave like a filled range (e.g., dragging across columns), do not write a single template string to multiple cells. Build each cell's formula string individually with the appropriate column letter and row number for that cell. After writing, print the formula strings of adjacent target cells and verify that relative references (e.g., column letters without `$`) differ as intended — for example, `C$3` in column C and `D$3` in column D.

- **Distraction by tool chatter:** When the task description mentions broken macros, VBA, or code that doesn't work, but the answer is a spreadsheet (sheet:range), ignore the tool description. Do not generate or fix code; instead, open the input file, inspect its contents, and apply the required transformation directly to cell values using openpyxl. After saving, reload and verify that every cell in the graded answer range contains plain data values, never formula strings or code snippets.

- **Library‑specific types and built‑ins:** openpyxl attributes (e.g., `Color.rgb`) may return objects that do not support `len()`. Always convert to a standard type (e.g., `str(rgb)`) before applying built‑ins. After fixing, re‑run and confirm the line executes without error.

- **Missing openpyxl library**: Before running any script that imports `openpyxl`, verify the library is available by running `python3 -c 'import openpyxl'`. If it fails, locate the correct interpreter (e.g., `which python3` and `python3 -c "import sys; print(sys.executable)"`) or install the library.

- **System warning about missing output**: When a system check warns that the output file does not exist, do not re‑run any inspection or diagnostic command. Immediately execute the script that creates the output file and saves it. After execution, confirm the file exists with `ls`.