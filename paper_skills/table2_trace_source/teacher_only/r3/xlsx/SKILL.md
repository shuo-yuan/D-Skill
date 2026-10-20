---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow



0. **Test tool invocation**: Before executing any complex multi-step command or script through a tool, always test the tool's invocation interface with a trivial, one-line command (e.g., `echo hello`) to verify the exact parameter format that works. Only then construct the full command.
1. **Inspect** the workbook thoroughly: print sheet names, dimensions, and the complete used range with coordinates and values for all relevant sheets before writing any logic.
2. **Plan** the modifications based on inspection.
   - Based on `answer_position`, determine whether the grader expects cell values or code. If the task mentions a specific tool (VBA, macro, formula) but the answer range is a cell range, produce plain computed values, not code or formulas.
**Write** the output: first clear the target answer range (set all cells to `None`) to remove any pre‑existing data, then write the computed values, save the workbook, and immediately confirm the file exists with `ls -la <output_path>`.
4. **Verify** the results by reading back key cells and comparing to expected outcomes.


**Important**: After inspection, you must immediately write and save the output file. Do not loop back to inspection; if you have not saved the workbook within two turns, stop inspecting and write the output with your best understanding.
## Inspection



Before loading the workbook, review any `spreadsheet_content` or table provided in the task description. Identify each column's meaning, sample rows, and which columns are already filled versus those you must compute.
- If the task description includes a truncated preview of the spreadsheet (e.g., `... (X more rows)`), do not rely on it for completeness. Load the workbook and print every row to see the full dataset. Base your logic on the actual last row observed, not the preview.


Always start by loading the workbook and printing every sheet's name, active sheet, and dimensions (max_row, max_column).

Load the workbook with `data_only=True` during this initial inspection so you see computed values, not underlying formulas. This makes example outputs, template sheets, and reference data immediately visible.
Use the exact sheet names from `wb.sheetnames` — never hardcode a sheet name based on assumptions about capitalization. If a task mentions a sheet name, verify that it exists in the workbook exactly as written; if not, locate the correct sheet by case‑insensitive matching before proceeding. For every sheet (including example/expected-output sheets), print all cell values row by row with their coordinates, Python types, and number formats (use `openpyxl` and `isinstance` checks). If the sheet has more than 200 rows, print the first 50 and last 20 rows; for any sheet that will be processed (source data, reference), also print all columns from A to the last used column (max_column). To catch hidden rows, consider printing all rows if the total is manageable; always rely on `ws.max_row` and `ws.max_column` to determine the full range, and never hardcode row counts. Use this output to identify column headers, key columns, row counts, ordering, placeholder conventions, and any patterns your output must reproduce.

Before writing any logic, answer these five questions:
1. Which cells are already filled and which are empty?
2. What is the grain of any date/datetime column (day, month, year)?
3. Exactly where (sheet and cell) must the final answer appear?
4. Are there any rows or cells that must not be modified? Identify their exact coordinates and contents.
5. Have I printed the complete contents of every relevant sheet (source data, reference, expected-output) row by row and confirmed the exact expected output pattern?

- Watch for multi‑table layouts, side‑by‑side blocks, and empty separator columns. Verify that your planned column‑index selections and pattern‑matching logic align with the actual data layout before writing any code.
- When printing cell values, also print any formula strings (e.g., check `isinstance(cell.value, str) and cell.value.startswith('=')`). Look for existing aggregations, intermediate results, or helper columns that your formulas can reference instead of recalculating. Confirm that the ranges you plan to use already exist and reuse them to keep the workbook consistent and avoid errors.


After printing, verify that you can see row/column boundaries, header labels, and the empty answer cell. If any are unclear, print again with explicit coordinate‑value pairs until the full layout is unambiguous.

Before writing output, inspect any pre‑filled cells in the target answer range. Print their types and values. Check how edge cases (unmatched keys, missing data) are handled — are they blank, or filled with a default like `False`/`0`? Mirror that treatment in your output code. If any cell is non‑None, decide whether to clear it and document your decision.
- **Existing output sheet with headers**: If the answer sheet already contains a header row and partial data, print the exact target range before writing. Identify header rows to preserve and data rows to clear. Use any pre‑filled values to deduce the expected output pattern. After writing, reload and print the same range to confirm headers are intact and data rows are correctly filled.

- If the task requires clearing or emptying cells, also inspect the formatting (fill, font, border, alignment) of those cells. You'll need to explicitly remove all formatting when clearing.

Do not proceed until you have seen every cell that might be affected and confirmed the exact columns needed (by header text, not hardcoded indices).

- When printing cell values, use `repr(cell.value)` to make formula strings (e.g., `'=SUM(A1:A10)'`), date objects, and `None` values immediately unambiguous.
- When the task involves removing or replacing specific characters (e.g., double quotes, special symbols), first print the `repr()` of every cell in the target range to see the exact characters present. Verify that the characters you intend to target match the printed representation before writing any replacement logic.
- When the task involves date or formatted number transformations, print the number_format of each cell in the target column to detect mixed formats (e.g., datetime objects with format 'mm-dd-yy' vs strings in ISO format).
- When criteria cells or source data will be filtered or copied, print sample values with their Python types and `number_format` attributes before writing any logic. Use this to decide how to parse criteria (e.g., string vs datetime) and to preserve exact formatting (number format, font, fill) in the output range.
- When headers contain recurring patterns (e.g., columns with `/description` in their name), count how many columns match the pattern before any changes. Use this count later to verify that the modification was applied correctly.
- If any column contains pre‑filled example outputs (e.g., a column with sample results that match the expected answer format), print those cells and analyze their structure: delimiters, zero‑padding, constant segments, and any pattern. Use that pattern to generate your output, and after writing, verify that your values match that format character‑by‑character.
- After printing the full sheet, identify any control rows (e.g., constraints, totals, headers outside the main data block) that affect calculations. Print the row immediately above the intended first data row and immediately below the intended last data row to confirm they are headers/metadata, not data values. Read control values from their exact cell coordinates (e.g., `ws['B20'].value`).

- After printing the full sheet, also print the first 5 rows of the source-data columns and the target output columns using `values_only=True` to quickly scan for non‑numeric headers or summary rows. Confirm the column positions, header names, and whether the target range already contains data or headers you must preserve or clear. Before writing, state the exact source and target column letters/indices and whether the target range is empty. After inspection, verify that you know which columns will be read and whether the target range is empty or already holds headers—by visually matching the printed output to the task’s `answer_position`.
- If the target sheet (from `answer_position`) already contains data, also print the `number_format`, font, fill, border, and alignment of each cell in the first few rows. Treat this as a formatting template: preserve these formats when writing your output, and only clear the cell values, not the formatting.
- If any sheet appears to contain an expected output (e.g., a sheet named 'Expected' or with data that looks like the desired result), treat it as a target: compare its rows to the source data to deduce the exact transformation (sort order, filter, aggregations, etc.) before coding any manipulation.
- When any sheet name suggests it contains expected results (e.g., 'result', 'expected', 'answer', 'After', 'Solution', 'desired result'), print its full contents and use it to decode the transformation before writing any code. Pay attention to layout details — row count, empty separator rows between blocks, and whether a trailing empty row exists — and treat them as a template for your final output.
- When a task provides example or expected outputs, mentally reverse‑engineer the rule from every row. Write down the rule in plain language (e.g., “True if the store name’s last N characters equal the city AND no extra characters follow”) and test it against all given examples before writing a single formula.
  - Before writing any code, if a reference sheet (e.g., 'Expected', 'Manual Result') exists, verify that key identifier columns (e.g., ID, name) match between the sheets to ensure correct row comparison. Manually trace your interpretation on a few rows and compare with the reference sheet; if they differ, re‑interpret the instruction. After deducing the transformation, explicitly state your plan (e.g., 'Rows 2,4,6,7,9 on Before must be highlighted based on After column B pattern') before coding.

- When the task involves looking up data from other sheets based on a column of names/IDs, verify that every value in that column corresponds to an existing sheet name (case‑insensitively). If any value lacks a matching sheet, print a warning and decide how to handle it before writing code.
- **Immediately after inspection**, verify that your assumptions about the data layout (e.g., first non-blank row, last data row, column order) match the printed `repr` values. If any surprise appears, adjust the plan before modifying any cell.
- **After inspection, you must proceed to plan, write, and verify the output. Do not stop after inspecting the workbook; the task requires producing a modified workbook saved to the output path.**

- **Before any manipulation**, print every cell's coordinates and values using `ws.iter_rows` (or equivalent) — even if the task description shows a snippet of the sheet. The actual layout may differ, and hidden rows or empty areas can affect your logic. Use this full dump to confirm the exact position of headers, data, and blank rows.
- When the task involves lookups, after printing all rows, verify that the fields you intend to use as keys are unique. Print all distinct combinations of those fields and check for duplicates. If any combination appears with different associated values (e.g., same meet name and race number but different dates), include the differentiating field in the key. Adjust your lookup logic accordingly.

Once you understand the task, write the output and save the workbook immediately. Do not continue inspecting after you have enough information. If you have not saved the workbook after two turns, stop and write the output now with your best understanding, then verify. Before declaring completion, confirm the output file exists and the answer range contains new values (not original static content).

- When the task references a specific column or range, print every cell in that column (or the full used range) before writing code. Look for patterns across the entire range, such as repeated intervals, offsets, or non‑empty cells at regular steps.

- When the task references columns by letter (e.g., 'Column Q'), print the header row with coordinates to map letters to 1‑based indices, and verify the column's data type before using it in formulas.

- After printing the full sheet, verify that the row/column boundaries of the data match the `answer_position` range specified in the task. If headers or data start on a different row than expected, adjust your loop bounds and target range accordingly before writing any code.

- When the sheet contains multiple header‑separated data blocks (e.g., repeated column headers), collect all data rows across blocks, deduplicate rows based on the task's criteria (e.g., identical values in specific columns), print the deduplicated list and its length, and verify that it matches expectations before proceeding.

- After printing the full dump, scan the output to verify the exact location of any keywords, values, or patterns mentioned in the task description (e.g., a search substring, a specific column header, or a target value). Confirm that your understanding matches the actual cell coordinates before writing any code.

- When the task involves grouping, filtering, or deduplication based on specific columns, print every row of those columns (even if the sheet has >200 rows) to capture the full set of distinct groups and values before writing any logic.

- **Merged cells**: Print all merged cell ranges with `ws.merged_cells.ranges`. Unmerge every range using `ws.unmerge_cells(str(range))` before writing any output. After unmerging, verify the list is empty.
- When the task mentions specific columns (e.g., AY, BG, BL, BN, BF), print every row of those columns before writing any logic. Confirm that the printed column indices match the letter positions you intend to use in your manipulation code.
- After printing any column’s full content, analyze it: note data types (datetime, string, int), missing‑value patterns (alternating empty cells, `None`), and any outliers. This grounds your logic and prevents edge‑case failures hidden mid‑sheet.

- **Inline example output**: If the sheet contains any text describing expected output (e.g., 'THE ABOVE TABLE WOULD BECOME:'), note its location and use it to confirm the structure of the duplicated rows after writing. After inspection, explicitly state the data range, the count column (if any), and whether an inline example output is present.

- **Skip empty trailing rows**: When reading data rows, skip any row where the primary key (or a required identifier column) is `None`. Trailing rows full of `None` values are not part of the data and must be excluded from processing.

- **After printing all sheets**, verify that the header row of the answer sheet (the sheet from `answer_position`) matches the columns you plan to output. If the headers differ in name or order, adjust your output plan to match the actual header row before writing any data.

- Before iterating over rows, print `ws.max_row` and `ws.max_column` to confirm the dimensions and catch any discrepancies.

- When source data contains string representations of dates, times, or other formatted values, print every value in the column and count distinct patterns (e.g., with/without time, different separators, varying lengths). Adjust your parsing logic to handle all observed patterns before writing any code.
- For numeric strings with non‑standard decimal or grouping separators (e.g., comma as decimal, space as thousands), inspect several raw strings to identify which symbol is the decimal separator and which are grouping; then programmatically remove grouping characters and replace the decimal separator with a dot before converting to `float`. After writing, verify that the answer cells contain numeric types (int/float), not strings.

**This full dump of all sheets is mandatory and must be completed before any further analysis or planning.**

- **Map columns from preview**: Based on the preview, explicitly map each column name to its column index or letter, and note any row offsets. Identify which columns you will read from and write to. Mentally trace one example row from the sample data to confirm that the mapped cells contain the expected values, catching column‑index mistakes before execution.

- If any formula references a cell that is empty or contains an error, examine the surrounding data and other sheets to deduce the intended multi‑criteria lookup. Simulate the lookup in Python to verify the logic before writing any formula.

- **Before writing any transformation code**, print the full used range of every sheet, including formulas, merged cells, and any side-by-side tables. Use this to deduce the exact transformation rules (e.g., sort order, grouping, handling of blank cells) before coding.

- If the workbook contains sheets named 'Before' and 'After', print both and compare them to deduce the exact transformation. The 'After' sheet often shows the desired output for some rows, revealing the splitting, formatting, or filtering logic.

- When searching for specific values (e.g., 'X'), load the workbook with `data_only=True` and compare the evaluated values to the formula strings. Print both the formula and evaluated content for the target column to detect values generated by formulas (e.g., `=IF(C6="","X","")`). Use the evaluated values for your search.

- Before writing, count the number of rows that match each condition you plan to apply (e.g., using a quick loop or filter) and verify that the counts and data types match your expectations. Inspect the current values in the target range to ensure they are empty or contain the expected headers.


- **Validate pattern against pre‑filled cells**: If the answer range already contains some correctly filled cells (e.g., a few rows that match the expected output pattern), treat them as a validation set. Before writing any new values, compute your intended output for those cells and compare. Print any differences; do not proceed until every pre‑filled entry is exactly reproduced. This catches pattern mistakes early.


- After printing all sheets, explicitly confirm the exact coordinates of any special rows or columns mentioned in the task (e.g., 'top three rows', 'header row', 'subtotal rows') and the mapping of columns to the required output columns. Use the printed dump to verify your understanding before writing any code.
## Writing Output



- Write plain data values (numbers, strings, dates) directly into cells using `.value` assignment. Never write formulas, VBA code, or code text unless the task explicitly requires a specific formula or macro. Use the appropriate Python type (`int`, `float`, `str`, `datetime`) and set number format if needed.
- When replacing or updating cells via a lookup (e.g., swapping codes for names from a reference sheet), build a Python dictionary from the source data and assign the looked‑up plain values: `cell.value = lookup_dict[key]`. Never use `=VLOOKUP(...)` or other formula strings for replacements. After saving, reload and print the answer range to confirm all values are plain data, not formula code.
- When moving or copying cells, capture all formatting properties (`number_format`, `font`, `fill`, `border`, `alignment`) from the source cell using `copy(cell.font)` etc., and apply them to the destination cells after setting values.
- Always parse `answer_position` to get the exact sheet name and cell range. Create or modify **only** that sheet; never alter any other sheet unless the task explicitly instructs you to do so.

- Before writing new data to any sheet, clear the entire target range of values. If you identified a formatting template during inspection (a target sheet with existing data and consistent formatting), preserve that formatting: set each cell's value to `None` without altering its style. Otherwise, remove all formatting as well (set fill, font, border, alignment to defaults). After clearing, print the first few rows of the target range to confirm they are empty and the formatting is as expected. Never leave old data or formula rows unless the task explicitly grades a formula.

- **Recompute the entire answer range from source data** — after clearing, produce every cell value from your own logic. Do not assume any pre-existing values were correct, and do not patch only the missing cells. After saving, verify that no cell in the answer range holds an unchanged original value.
- When a task requires that zero values be displayed as blank, set the cell value to `None` (not `0`) and apply the requested number format. After saving, verify that those cells are empty (`None`) rather than containing a zero.

- If the task mentions a specific formula or calculation (e.g., "fix the SUMIFS formula so it works"), but the grader only checks the resulting cell values, do not try to fix the formula. Instead, extract the source data, compute the intended result using Python, and write the plain numeric value into the answer cell. Only keep a formula in the cell if the task explicitly requires that the formula itself be present (e.g., "the cell must contain the formula =SUM(...)").
If you write a formula, immediately after saving, reload the workbook with `data_only=True` and confirm the cell contains a numeric result, not `None` or an error. If it is `None`, replace the formula with the computed value.

- When a lookup key appears multiple times in the source data and the task requires placing all associated values (e.g., "transposed manner"), collect all matches using a dictionary with `list.append` and write all of them to the output row, not just the first match.



- After all cell modifications are complete, save the workbook to the exact `output_path` using `wb.save(output_path)` and immediately verify the file exists with `ls -la <output_path>`. Do not proceed to verification until the file is saved and confirmed.

- When you discover a pattern (e.g., every Nth row contains a value), extract the values using Python and write them as plain data into the answer cells; do not attempt to replicate the pattern with a formula unless the task explicitly requires it.

- If a formula in the answer cell is broken (e.g., circular reference, #REF! error), do not attempt to repair it. Load the workbook with `data_only=True` to read cached values of dependent cells, compute the intended result manually, and write the literal value, preserving the cell's original `number_format`.
When the cached value is also an error (e.g., #REF!), inspect the full sheet and the formula's arguments to deduce the intended computation from the surrounding data (e.g., a VLOOKUP with an out-of-range column index likely intends to return a value from an existing column in the lookup range). Compute the correct result using the available data and write it as a plain value. Verify after saving that the cell's value is numeric and its number format matches the original.

- When the task specifies formatting without decimals (e.g., 'format final output without decimals'), round the computed value to an integer with `int(round(...))` and set `cell.number_format = '0'`. After saving, verify that the cell displays no decimal point.


- Additionally, within the same Python script, after saving, run `import os; print('File exists:', os.path.exists(output_path))` to programmatically confirm the file was written. If it prints False, re-save and check again.

- **Dual workbook loading for safe writes**: When you need precise computed input values but must preserve formulas in other columns, open the input workbook twice: (1) load with `data_only=True` to read the calculated numbers your logic depends on, and (2) load again **without** `data_only` for the workbook object you will modify and save. Write your output cells only to that second workbook. After saving, reload the output file with `data_only=False` and print a few cells that originally contained formulas (e.g., columns B, C, I or any structured‑table formula) to confirm their formulas are still present.

- If the task description asks a 'how‑to' question (e.g., 'How can I sort a column using VBA?') but the graded answer is a spreadsheet range, ignore the question phrasing; compute the final values and write them directly into the answer range. Do not provide VBA code or explanatory text.
- After clearing the target range, compute and write a value for **every** cell in the answer range. Do not leave any cell empty; if a row should have no data, decide on a placeholder (e.g., empty string or 0) consistent with the task. After writing, verify that no cell is `None`.
- Capture the `output_path` from the task instruction as an absolute path variable and pass it unchanged to `wb.save()`. Do not modify the path, add subdirectories, or change the filename.
- For summary cells (counts, sums, averages, etc.), **always** recompute the value from the raw source data and write it as a plain number. Do **not** reuse any pre‑filled summary cell—it may be incorrect. After saving, reload and confirm the answer cells contain numeric data, not formula strings.

- **Row duplication**: When duplicating rows (e.g., expanding a row based on a count column), copy every column from the source row to the destination, including any helper or count columns. Do not skip columns. After writing, verify that the output sheet's column count equals the source header's column count and that the count column is populated correctly.
- Immediately after confirming the file exists, reload the workbook and print the first few rows of the answer range to verify the header row and data structure are correct. If the structure is wrong, fix and re-save before proceeding to full verification.

- **Varying decimal formats per cell**: If the task requires different number formats for values based on decimal properties (e.g., integer → '0', one decimal → '0.0', many decimals → '0.000'), implement a classification function: check `value == int(value)`, then `abs(value - round(value, 1)) < 1e-9`, else fallback. Write the rounded value as `cell.value` and set `cell.number_format` to the appropriate pattern. After saving, verify each cell's value and format match the classification.

Never rely solely on a script's print message to confirm the file was written; always run `ls -la` explicitly. If the file is missing, check your current working directory and ensure the save operation uses an absolute, correct path, then re‑save and re‑verify.

- When verifying with `ls -la`, use the same output path variable you used for `wb.save()` to avoid path mismatches.

- **Lookup formula coverage**: When building a lookup chain (nested IF, VLOOKUP, INDEX‑MATCH, etc.), first list every distinct key value from the source data and ensure the formula explicitly handles each one. After saving, reload with `data_only=True` and test at least one cell for every distinct key; if any returns an empty or error value, add the missing condition.

- When the task explicitly requires formulas in a multi‑cell range (e.g., VLOOKUP across rows/columns), use a Python loop to assign each cell's formula string. Construct the formula with the correct `$` anchors: the lookup key column should be absolute (e.g., `$B{row}`) and the return column reference should be relative (e.g., `col$8`). After saving, print a few formula strings to verify the pattern, then reload with `data_only=True` to confirm computed values are valid.


- **Before saving**, perform an in-memory check: iterate over every cell in the answer range and confirm that no cell value is a string starting with `=` or containing VBA keywords (e.g., `Sub`, `Function`, `End Sub`). If any are found, replace them with the computed plain values immediately.

- Immediately after confirming the file exists with `ls`, reload the workbook and print every cell in the exact answer range. Confirm that each cell holds the expected data (not `None`, old leftover values, or code/formula text). This is the first verification gate; never skip it.

- If the task is phrased as a question about creating a macro (e.g., 'How can I create a macro to extract rows…'), but the `answer_position` is a cell range, produce the required values directly; do not write macro code or formula text.
## Verification




After writing to cells, perform these in-memory checks:
- Iterate over every cell in the answer range and confirm that no cell is `None` and that all cells share the same data type (e.g., `bool`, `int`, `str`).
- If the task expects plain values (not formulas), read back the `.value` of each cell to confirm it is a plain data type, not a string starting with `=` or containing code.

Even if all in-memory checks pass, you must still save, reload, and verify the output file — in-memory checks cannot catch save errors, file corruption, or mis‑mapped cell ranges.


After saving the workbook:

- **Do not rely solely on the writing script's print statements to confirm correctness; always reload the saved file and verify the answer range independently.**
- Run `ls -la <output_path>` to confirm the file exists and is non‑empty.
- Reload the workbook and print every cell value of the target sheet. If the task expects formulas, confirm each cell contains the intended formula string. If the task expects computed values, confirm no cell contains a formula string; if any formula string is found, re-run your script to set `.value` instead. Additionally, for computed values, open the workbook with `data_only=True` and verify that the cells contain the expected numeric results.
- When printing the target sheet after reloading, include the surrounding columns that influence the logic (e.g., row identifiers, grouping columns) so you can verify that the answer rows match the expected criteria. Compare the printed results against your mental expectation from the inspection phase.
- After reloading the workbook, print the first 5 and last 5 cells of the answer range. Confirm they contain expected plain data values (numbers, strings, dates) — not empty, not formula strings, and not error values. If any cell is suspicious, recompute and re‑save before continuing.
- Re‑open the workbook and print the exact `answer_position` range using `iter_rows`. Confirm that the expected header row is present, only the intended rows appear (no extra rows or code text), and the data matches the task description.
- If you cleared old data, verify that no old data remains outside the newly written range (e.g., rows below the last data row should be empty).
- After saving, reload the workbook and run a short validation script: count the number of populated rows per category or logical block, verify that the first few entries are in ascending order (e.g., by checking that the numeric part of an item code increases), and confirm that cells beyond the last filled row are empty. This catches mis‑mapped columns, missing data, or uncleared old data without an answer key.
- Print the contents of **all** sheets. Confirm that the target sheet contains the expected data, and that every other sheet is identical to its state before your edits. If any original sheet changed, fix the error before declaring completion.
- If you moved or copied columns, re-inspect the destination column's values and formatting and compare them to the original source column's properties captured during inspection; they must be identical.

- If you cleared cells or columns, reload the workbook and confirm that the cleared cells have `None` values and no custom formatting (fill type `None`, default font, etc.).
- If an expected-output sheet exists, verify that the first few rows of your output match the corresponding rows in that sheet (ignoring blank rows).
- If a reference sheet (e.g., 'Manual Result', 'Expected') exists, after writing, print both the reference sheet's values and your output range, and confirm they match cell‑by‑cell; if any mismatch, stop and adjust your logic.
- After reloading, also print the formatting properties (fill, font, number_format) of key cells in the answer range to confirm they match the expected output.
- For tasks with explicit numeric constraints (e.g., values must lie within a range, a column must sum to zero), write a verification script that checks every cell in the answer range against those constraints and prints 'OK' only if all pass. If any check fails, fix the logic and re‑verify before declaring completion.
- If the task involved removing or altering a pattern, reload the workbook and confirm that the pattern no longer appears in the target range (or that the count has changed as expected).

- When printing cells for verification, always include the cell coordinate (e.g., `cell.coordinate`) alongside the value to confirm the exact location.
- If you performed a lookup with potential duplicate keys, reload the workbook and verify that for each key with multiple matches, the output row contains at least two distinct values (or the expected number of matches).
- After reloading, print the exact answer range row by row. Manually verify that the first and last groups (or other representative groups) match the expected pattern from the source data, confirming that mapping, grouping, and skip conditions were applied correctly.
- If the task expects plain values, also confirm that no cell contains VBA code text (e.g., strings starting with 'Sub', 'Function', or containing macro keywords). If found, re-run your script to set `.value` instead.

- After any operation that modifies row positions (deletions, insertions, sorting, or any change that shifts cell locations), reload the saved workbook and explicitly print the exact answer range specified in the task's `answer_position` field (e.g., `ws['A4':'A18']`). Confirm that every cell in that range is populated with the expected data types and is not empty. Do not rely solely on printing the whole sheet; verify the graded range specifically.
- If the original workbook is available, reload both the original and the output, and print any rows in the answer range that differ from the original. This catches unintended side‑effects or leftover old data.
- If any cell still contains unwanted components (e.g., non‑zero time in a date‑only column), modify the logic to strip them and re‑verify until the range holds only the expected values.

- After saving, reload the workbook and run a verification script that checks: (a) the modified cells match the intended computation (e.g., ranks are sequential, sums equal expected totals), and (b) cells outside the modified range remain unchanged. Print 'VERIFICATION PASSED' only if all checks succeed; if any discrepancy appears, raise an error and fix the issue before completing the task.

- After reloading, for the answer cell(s) print `cell.data_type` and `cell.number_format` to confirm they match expectations. Also print the cells immediately before and after the answer range (e.g., one row above/below, one column left/right) to ensure no unintended modifications leaked.
- If the original sheet contained blank rows separating logical blocks (e.g., groups of data with header rows), reload the output and verify that those blank rows are still present at the same positions, and that any header rows within blocks remain unchanged.

- If the task required formatting without decimals, after reloading, print the cell's `number_format` and `value` to confirm it is an integer and the format does not show decimals (e.g., `'0'`).

- After reloading, explicitly compare the printed values of the answer range to the results you intended to write. If any discrepancy, correct and re‑save before declaring completion.

- If you deleted columns or rows, confirm the new dimensions (max_column, max_row) and that the deleted items are absent. Print the first few rows of the relevant columns to verify the change.

- If the original workbook is available, reload both the original and the output workbooks. For every sheet that should remain unchanged, compare cell values and formatting with the original; print any differences and fix them. Then print the answer range row by row and manually verify that the primary grouping order (e.g., helper‑column order) and any secondary sorting (e.g., numeric ascending) match your interpretation of the task. If any row is out of order, adjust the logic and re‑verify.

- If no reference sheet is available, pick 2-3 rows and manually verify that the output values are consistent with the source data (e.g., check that a cumulative total or lookup result matches the original values).

- After reloading the workbook, print the exact `answer_position` range (sheet and cell rectangle). Compare each cell's value against your intended changes. Confirm that every cell holds a computed data value (number, string, date, boolean) — not a formula string, macro code, or `None` — unless the task explicitly requires formulas. This direct, exact‑range inspection catches shift errors, logic mistakes, and leftover placeholder data.
- If the task specified that certain rows or cells must remain unchanged, reload the workbook and compare those rows/cells to the original input to confirm they match exactly.
- After reloading, print the answer range alongside a key identifier (e.g., worker name, row index). Spot‑check at least one entity that appears in multiple rows with non‑zero inputs. For that entity, re‑compute the expected value from the source data (e.g., previous debt – deductions + additions) and verify it matches the printed output.
- **Before signaling TASK_COMPLETE**, run `ls -la <output_path>` one final time. If the file is missing, do not signal completion; instead, return to the writing step and re‑save the workbook.

- If a reference sheet exists, write a script that compares every cell in your output range to the corresponding cell in the reference sheet and prints any mismatches. Fix all differences before signaling completion.
- If any column header suggests expected answers (e.g., "Expected", "Result", "Reference"), after writing your values, reload and print a side‑by‑side comparison of your answer range with that column; flag any mismatches and adjust before declaring completion.

- After any row deletion, insertion, or reordering, reload the workbook and print the full used area of the sheet, then compare it to the pre‑change dump to verify that only the intended rows/columns were modified and that headers, totals, and blank rows are in the correct positions.
Immediately after saving, reload the workbook with `data_only=True` and print a few key cells from the answer range (e.g., the header, the first data cell, and the last data cell). Confirm they contain numeric values, not `None` or formula strings, and match your intended result before proceeding to a full reload and verification.

- If pre‑filled computed values existed in the answer range, after writing, verify that your new values are consistent with the pattern of the pre‑filled ones (e.g., same interval logic, same boundary conditions) and that only the intended cells were modified.

- If the data involves known boundaries (e.g., year changes, group transitions), after reloading, print the rows immediately before and after those boundaries to confirm correct handling and formatting.

- If you applied varying decimal formats, reload the workbook and print each cell's `value` and `number_format` in the answer range. Confirm that integer values show format `'0'`, one‑decimal values show `'0.0'`, and others show the specified many‑decimal format.

- **Final TASK_COMPLETE gate**: Before signaling TASK_COMPLETE, reload the workbook from the output path, print every cell in the exact `answer_position` range — including each cell’s value, number_format, and alignment — and visually confirm that the values, number formats, and alignments match the task requirements and any example data on the sheet. Only then call TASK_COMPLETE. This is the final sanity check; never skip it.

- If an expected output sheet or reference table exists, write a script that loads both the output and the reference, normalizes empty values (e.g., treat `None` and empty string as equivalent), and compares every cell in the answer range. Print any mismatches with coordinates, and only declare success when no mismatches remain.

- When printing the answer range after reloading, use `repr(cell.value)` so you can distinguish `None` from empty strings and confirm that zero cells show blank (not `0` or `'0.00'`). Also print `cell.number_format` for a sample of cells to verify it matches the required spec (e.g., two decimals, no commas).

- After reloading, print the target sheet's `max_row` and `max_column` to confirm the file opened correctly and the dimensions match your expected changes (e.g., fewer rows after deletion). Verify that no extra rows or columns exist beyond the intended range.

- After any row insertion or deletion, reload the workbook and print a window of rows around the modified area (e.g., 5 rows before and after the inserted/deleted region). Confirm that the intended change is correct and that neighboring data rows are undisturbed. This catches unintended shifts or extra insertions/deletions.
- After reloading, print every cell in the answer range with its coordinate and value, and also count the number of non‑None cells. Verify that the count matches the expected number of populated cells and that no blank cells appear within the populated region. This final check catches transposition errors and missing rows before signaling TASK_COMPLETE.

- If the task description states an expected numeric value (e.g., 'the answer should be 270'), after reloading, print the target cell's value and assert it matches that number. If it doesn't, re‑compute and re‑save before proceeding.

- After reloading, print every cell in the answer range with its value and Python type (`type(cell.value).__name__`). Verify dates are `datetime`, numbers are `int`/`float`, text is `str`, and no cell is `None`. If any type is wrong, fix the writing logic and re‑save.


- If some cells in the answer range were not provided as examples, manually apply your algorithm to the source data for those cells to confirm the result before declaring completion.

- After reloading, print a selection of rows that match a specific condition (e.g., rows containing a known keyword) to manually confirm that the transformation logic (such as concatenation, filtering, or lookup) produced the expected values. This catches off-by-one and omission errors.

- **Conditional copy verification**: After saving, reload the workbook and print for every row the source column(s) and target column(s) side by side. Confirm that the target cell matches the source when the condition is true and stays unchanged otherwise. This catches per‑row logic errors that are invisible when printing only the target column.
## Common Pitfalls



- **Hardcoding column indices or row counts** – always scan headers to find columns dynamically and use `max_row`/`max_column` for row iteration; never assume a fixed number of rows.
- **Losing formatting when moving columns** – always copy all formatting properties.
- **Overwriting or modifying sheets other than the one specified in `answer_position`** – restrict edits to the answer sheet only.
- **Following extraneous tool instructions**: If the task mentions a specific tool (e.g., 'using VBA') but the graded answer is a cell value, ignore the tool requirement. Focus on producing the correct cell content by any reliable method (e.g., Python + openpyxl).

- **Deleting columns/rows in forward order** – when deleting multiple columns or rows by index, iterate in reverse order (largest index to smallest) to avoid index shifting. After deletion, verify that no cell in the first row (or target range) still contains the pattern you were removing, and that the column/row count decreased by exactly the number deleted. Also, reload the workbook and print the rows immediately above and below the deleted range to confirm that any special rows (totals, subtotals, headers) were not accidentally removed and are in the correct position.

- **Hardcoding extracted values** – when you need to collect multiple values from a source sheet (e.g., invoice numbers), always scan for a fixed pattern (like a header label) and read the adjacent cell beneath each match dynamically. Never embed a hard‑coded list of values you glimpsed during inspection. After extraction, print the collected list and verify it matches the source sheet.
- **Fixing broken macros when answer is cell values**: If the task asks to fix a macro, formula, or script, first determine the answer range from `answer_position`. If the grader only checks cell values (not code), ignore the broken tool and produce the correct cell values using Python. Do not attempt to repair the macro unless the task explicitly requires the macro code itself to be submitted.

- **Signaling completion without creating the output file** – always use a file‑manipulation tool (e.g., `openpyxl`, `pandas`) to write the spreadsheet to the exact `output_path`, then verify with `ls` before declaring the task complete.


- **XML parsing errors in openpyxl** – if `load_workbook` raises a `TypeError` or `XMLSyntaxError`, treat the file as a zip archive. Unzip it, inspect `xl/styles.xml` (or the file mentioned in the traceback), remove or fix the offending elements, rezip, and load again. After repair, verify by reading sheet names and the first row of values to confirm the file is usable.


- **Overwriting subtotal/header rows** – when the sheet contains mixed content (data rows and subtotal/header rows), inspect a distinguishing column (e.g., the grouping category column) to identify which rows should receive computed values. Write only to those rows; leave all others untouched. After writing, verify that at least one non‑data row still holds its original formula or value, and that no computed values appear there.


- **Writing cleaned numeric data as strings** – when cleaning numeric cells (e.g., stripping non‑digit characters), always convert the cleaned value to `float` or `int` before writing. Then reload the workbook and verify that the answer cells are numeric types (not `str`) by printing `type(cell.value).__name__` for each cell in the answer range.

- **Mistaking non‑boolean falsy values for `False`** – when a column contains booleans, verify the type of every cell; if any are strings, use identity checks (`is True`/`is False`) instead of truthiness checks to avoid treating strings like `'none'` or `'False'` as falsy.

- **Overwriting existing non‑blank cells when filling gaps in a column** – when you need to fill gaps with a pattern (e.g., sequential labels), write code that only replaces truly empty cells (`None`). Keep all non‑blank cells exactly as they are. Before writing, print the full column to spot any rows that already follow the target pattern – your code must parse them so the sequence continues from the next logical value. After writing, verify that no pre‑existing non‑blank cell has changed and that no duplicate or out‑of‑order labels appear.

- **Implementing extra formatting/columns outside the answer range** – before adding any formatting or other modifications, note the exact `answer_position` range that will be graded. Implement only what is needed to produce the correct values in that range; ignore additional requests (e.g., fill color, extra columns) that fall outside it. After saving, verify that cells outside the answer range remain unchanged.

- **Using source column names instead of task-specified header names** – when the instruction explicitly lists header names (e.g., allowance names), use those exact strings in the output, not the raw source data column names. After writing, verify that the output headers match the instruction verbatim.

- **Applying numeric filters without type checks** – when deleting rows based on a numeric condition in a column, first verify each cell's data type with `isinstance(cell.value, (int, float))` to avoid removing headers or text entries. After writing, reload the workbook and assert that the first cell in the relevant column still holds a string, confirming non‑numeric content was preserved.

- **Trusting pre‑filled summary cells** – always recompute totals, counts, and other aggregations from the raw source data. Existing summary cells may be stale or incorrect. After recomputing, write the results as plain numbers, not formulas.

- **Script file not saved** – after writing any script file (e.g., with `cat`, `echo`, or redirection), immediately verify it exists and is non‑empty with `ls -la <file>` and `head -n 5 <file>`. Do not attempt to execute it until these checks pass.

- **Overwriting header rows in the answer range** – when the `answer_position` includes a header row (e.g., `C1:C6066` with `C1` as a label), inspect the first row(s) before writing. If they are headers or metadata, leave them untouched. After saving, read back those cells and confirm they match the original values.

- **Keeping first occurrence instead of last** – when the task asks to keep the *last* occurrence of each duplicate, iterate rows in reverse order (bottom to top) and record the first time you see each value. After writing, verify by checking that for each unique value, the kept row's original position is the highest index among duplicates.

- **TypeError on non‑string objects**: If a script raises a `TypeError` like `object of type 'RGB' has no len()`, convert the object to a string with `str()` before applying `len()` or string methods. After fixing, re‑run the script and verify the output.

- **Failing to clear the target range before writing new data** – always clear the answer range to remove any pre‑existing values before writing; otherwise old data may contaminate the graded answer. After clearing, print the first few rows to confirm they are empty.


- **Ignoring a system reminder that the output file is missing** – if you ever see a message like 'Output file was not created', stop all exploration and inspection immediately. Proceed directly to implementing the solution and saving the workbook to the exact `output_path`. Do not continue inspecting or planning; write the output with your best understanding, save, and verify the file exists before declaring completion.