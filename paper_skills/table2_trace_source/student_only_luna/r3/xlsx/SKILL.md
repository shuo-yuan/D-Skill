---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow



0. As the first action, print all sheet names, row counts, and first-row headers to map the workbook structure. Then inspect the sheet area you will modify: print the header rows and the target rows/columns (or the entire sheet if small) to establish a baseline before any manipulation.
  When printing the initial sample, include enough columns to capture both source and destination regions, even if they are non-adjacent (e.g., columns A–E and I–M). This reveals column mappings, criteria cells, and pre-existing formulas in one scan.
If the task mentions "all columns" or "entire worksheet", inspect every occupied column and row to confirm the full data extent before writing any transformation logic.
When multiple sheets are present, also print the first 100 rows of each sheet to compare structure and content across sheets before any modification. If the sheet is small (e.g., fewer than 50 rows), print all rows to see the complete layout and any pre-existing data.


**CRITICAL**: Never rely on any preview, summary, or truncated view of the spreadsheet provided by the environment. These previews may show only the first few rows and can be misleading. Always run your own `openpyxl` inspection code as the very first action to confirm the full workbook structure, sheet names, row counts, and column contents.


**DATA BOUNDARIES**: After the initial inspection, always determine the data extent programmatically: use `ws.max_row` and `ws.max_column`, and print the last 3–5 rows to confirm where data ends. Never hardcode row ranges (e.g., `range(2, 6)`) based on a preview or sample — always derive loop bounds from the actual sheet dimensions. If the preview shows only 6 rows, do not assume there are only 6 rows; inspect `ws.max_row` and print the tail of the sheet to confirm.


**Identify the deliverable type**: Re-read the instruction to determine whether the expected output is data in cells, formulas, VBA code, or a macro. If the instruction mentions VBA, macros, or automation, the deliverable is executable code embedded in the workbook, not static values. Embed VBA using xlwings.

1. Perform the required spreadsheet operations (insert, copy, formula, etc.).

When performing multiple operations, combine them into a single Python script that loads the workbook once, applies all modifications, and saves it in one turn. This avoids inter-turn state errors and keeps the logic self-contained and reviewable.
2. **MANDATORY VERIFICATION**: After saving, immediately run a separate script (see Verification Script Template) to re‑open the workbook with `data_only=True` and print the exact answer range. Confirm every cell's value matches expectations. If formulas were written, this step is non‑negotiable — you must see computed values, not `None` or formula text. Do not skip this step.


**Verification Script Template**: After any write, run this exact script (adapt the path and range) to confirm the saved output:
```python
import os
import openpyxl
output_path = 'output_path_here'
print('Output path:', output_path)
print('File size:', os.path.getsize(output_path))
wb = openpyxl.load_workbook(output_path, data_only=True)
ws = wb['SheetName']
for row in ws['A1:C10']:
    print([cell.value for cell in row])
```
Only proceed to TASK_COMPLETE after inspecting the printed values and confirming they are correct, non-empty, and match expectations.
**CRITICAL**: If your observation after the write script contains only a file path or a success message (no printed cell values), you have NOT verified. Stop immediately, run a separate script that re‑opens the workbook with `data_only=True`, prints the answer range, and confirm the values before TASK_COMPLETE.
3. Only declare completion after verification passes.



**CRITICAL**: Before declaring completion, you MUST re-open the saved workbook and print the exact answer range. If any cell is None, empty, or contains an error, stop and fix the issue. Do not assume the write succeeded.

Do not rely on the in-memory cell value after assignment; it may show formula text, not the computed result. Always re-open the saved file with `data_only=True` and print the answer range to confirm the actual values.


- If a sheet is referenced by position (e.g., 'sheet 2'), list all sheet names first and map the index to the exact sheet name. Use that name in all subsequent operations.
- Before any manipulation, read the `answer_range` specification from the task. The output must be placed in that exact cell range as data (values or formulas), not as code, commentary, or VBA text, **unless the instruction explicitly requires VBA or macro code.** If VBA is required, embed the macro in the workbook (using xlwings) and ensure any answer_range contains the expected results of running that macro, not the code itself.

**REMINDER**: The most common failure is calling TASK_COMPLETE without first re-opening the workbook and printing the answer range. Always confirm the saved file contains computed values, not None or formula text, before declaring completion.


**CRITICAL**: If formulas were written, the verification step above is mandatory. Skipping it is the most common cause of task failure — the answer range will contain None values, not computed results. Always re‑open with `data_only=True` and print the answer range before declaring completion.
- To minimize turns, include the verification step (re-open the saved workbook with `data_only=True` and print the answer range) at the end of the same Python script that performs the modifications, rather than running a separate verification script. This keeps the entire operation in one action.
When you combine verification into the same script, the observation must show the printed cell values from the answer range, not just the output file path.


**OBSERVATION CHECK**: After running any script that saves the workbook, your observation MUST show the printed answer range values (e.g., a list of lists of cell values). If the observation only shows a message like 'Script executed successfully' or a file path, you have not verified the output. Re‑open the workbook separately with `data_only=True`, print the answer range, and confirm the values before TASK_COMPLETE.

- When the task involves fixing, modifying, or auditing existing formulas, print all row values (not just headers) in every column that the formula references or writes to. This ensures complete visibility into data types, empty cells, and formula structure before any change.

After printing the initial sample, explicitly note the column indices of any columns referenced in the task (e.g., 'COUNT' column) and the presence of empty rows that require special handling.


- If a script fails with an error, read the full traceback, diagnose the cause (e.g., missing import, typo, logic error), fix the code, and re-run until the script completes without errors. After any fix, always perform the mandatory verification step (re-open with `data_only=True` and print the answer range) to confirm the output is correct, as the fix may have introduced new issues.
- If the workbook contains a sheet that appears to be an expected output (e.g., named 'Expected', 'Result', 'Manual Result'), print its first 25 rows as part of the initial inspection to understand the target layout and any structural differences from the source data.

Always load the provided input workbook (do not create a new blank workbook), modify only the required sheets and cells, and save the result to the exact output_path without changing the file extension. This preserves existing sheets and structure that the grader expects.
Always include any reference, example, or expected output sheets in this initial scan; print at least the first 10-20 rows of those sheets to understand the target layout.

- When the task specifies an `answer_range`, print the current values and `number_format` of every cell in that range before any modification. This establishes the baseline for later verification and reveals any pre-existing data or formatting that must be preserved or overwritten.

- Before writing, print the exact answer_range boundaries and confirm your write operations will populate EVERY cell in that range. Do not write only to the rows or columns that appear broken — the grader checks the entire range. After writing, re-read the full answer range and confirm zero None values across all cells.


**FAILURE GATE**: If you call TASK_COMPLETE without printing the answer range values from the saved file (using `data_only=True`), the task will fail because the grader will see `None` values. Your observation MUST contain the printed cell values before you can complete. If you have not printed them yet, re‑open the workbook and print the exact answer range now.
## Inspection


- Before any lookup or match formula, inspect the actual values in the lookup cell and the lookup range. Confirm compatibility (same data type, same year if dates, no hidden time components). Also inspect the source sheet's full contents (row count, header row, duplicates, empty rows) and the entire sheet layout (header and table regions) to choose the appropriate lookup strategy (e.g., two-dimensional lookup) rather than defaulting to VLOOKUP/INDEX/MATCH.
- Before writing any code, first perform a minimal initial read: print the row count, column count, and the first 10-15 rows of the relevant columns to quickly confirm column order, data types, and layout. This economical scan is often sufficient to confirm layout assumptions. - For tasks involving lookups, duplicates, empty rows, data integrity checks, or sparse/irregular data, expand to a full scan of all values from row 1 to the maximum row to understand the distribution and locate all data positions.
Before clearing or writing to any target range, inspect the sheet's full properties: existing values, number formatting, merged cells, data validations, conditional formats, and protected ranges. Use `.value` and `.number_format` checks on the exact target range. If the range already contains formulas or values, compare them to what you intend to write. After writing, re-read the range to confirm that the new values replaced the old ones, that the written cells contain data values (not formula text or error codes), and that the dimensions match expectations. This prevents overwriting important data or missing hidden structure.
- Before any deletion or filtering operation, print all values in the target column(s) for the entire data region (all rows, not a sample) to confirm which rows match the condition and whether any rows need removal at all. Also print the full sheet (all rows and columns) to see the complete layout and avoid missing hidden data.
- When deleting rows, first identify any rows with special roles (totals, subtotals, blank structure rows) and note their indices and key cell values. Exclude these rows from the deletion range or add an explicit guard condition. After deletion, verify that all special rows remain present and unchanged.

- Before writing any data extraction or aggregation logic, print a sample of rows from each source sheet (e.g., first 5 rows) to understand column contents and decide which columns hold the relevant data. After extraction, verify by printing 2–3 mapped rows from each output bucket and confirm they match the source values. When multiple numeric columns exist (e.g., DEBIT/CREDIT), explicitly decide which to use based on data inspection, not header names alone.

- Before writing formulas into a target range, print the full row of headers and the first data row for the exact columns of the answer range. Verify that the column you intend to write into matches the position expected by the grader. Confirm the range boundaries by reading the current values of the first and last cell of the target answer range before writing.

- When performing exact string comparisons or filter/replacement logic based on specific text patterns, scan the FULL relevant column(s) for the exact text patterns you plan to match. Print unique values and their counts for each condition column. Copy-paste the exact strings from the printed output into your code to avoid invisible character mismatches. If the strings are absent, explicitly decide whether that is expected or a problem.

- Before writing to a data range that spans multiple rows, programmatically detect the header row (e.g., find row containing a known header label) and the last data row (last non-empty row) to avoid hardcoding indices. Confirm that metadata rows (like min/max labels) are excluded from the write range.

- When filtering rows based on a condition, inspect the header row and first few data rows to confirm the condition correctly distinguishes header from data. After writing the filtered output, read back the entire target sheet (all rows, all columns) and verify that the header is present only if intended, and that no extra rows or columns exist.

- When column order may vary, build a header map: read the first row, normalize header names to lowercase, and map each to its column index. Before using any column, confirm the required name exists in the map (not None). This avoids hard-coded positions and adapts to layout changes.

- When inspecting a sheet, also note any existing formulas, named ranges, data validation rules, or conditional formatting that could affect calculations or data integrity, even if they are not in the immediate target range.

- When the task involves programmatic manipulation (copying, shifting, inserting rows, etc.), read and display the entire data region (all rows and columns up to the maximum row) before designing any logic. This reveals blank rows, metadata, and exact layout that affect offsets and conditions.

- When writing to cells based on a condition that involves other columns (e.g., only fill rows where a customer name matches), read and print the full column(s) of those condition values for the entire range you plan to modify. Confirm that every row qualifies; if any row does not, adjust the write range or logic. This prevents filling rows that should remain unchanged.

- When source data is organized in repeated sections (e.g., invoice groups with header lines and total rows), parse it row by row, identifying section start markers and terminators, to extract values precisely before writing. This prevents ad-hoc value selection and ensures the extracted data matches the source structure.

- When the task involves any non-trivial layout, perform a full dump of all non-empty cells with their coordinates (row, column, value) for each sheet. This reveals hidden structures and ensures accurate column mapping.

- When deleting rows based on a condition, first determine the data boundaries by scanning for the first and last non-blank rows in the relevant column. Iterate in reverse only within that range to preserve header rows and trailing empty rows that should remain.


- Before building a lookup map between two sheets, print and compare the actual key-value pairs from both sides for at least 10 rows — including header rows — and verify that the join key uniquely identifies the intended records. After populating the target range, inspect a sample of rows that should differ (e.g., rows with different IDs or ranks) to confirm they do not all contain identical copy-pasted values. If the output is expected to be dense values, verify the header row is not treated as data and remains untouched or intentionally set.
- When an instruction describes deriving values from multiple source columns, always inspect the target range's existing layout or any provided sample before choosing the output format. If the format is ambiguous, test the first few output cells by writing only one candidate value (e.g., the leftmost non-missing column) and verify visually that the shape matches the rest of the sheet. Never concatenate values unless the instruction explicitly requires a delimited list inside a single cell.
- When the task mentions modifying an existing macro or VBA code, locate and read that macro before writing any processing code. Use `openpyxl` to inspect the actual cell types (e.g., `type(cell.value)`) for the target column to confirm whether values are strings, datetime objects, etc., and design logic accordingly.
- Before applying formatting or cosmetic changes, read the current values in the target range. If the range is empty or contains errors, first compute and write the required data. Formatting alone does not satisfy a task that expects computed outputs.


- When a reference or example output sheet is provided (e.g., 'Manual Result'), inspect its entire structure before implementing any logic. Note row lengths, repetition patterns, grouping, column counts, and any properties that differ from a naive interpretation. After writing, compare your output's structure (not exact values) against the reference to confirm agreement.


- When applying regex or string transformations to a range, first print the raw cell values across the entire target range to identify all distinct formats present (e.g., currency symbols, thousands separators, trailing zeros). After transformation, verify that no two originally distinct cells now have identical transformed values unless that normalization is intended.

- When writing a formula that tests a cell's value (e.g., IF(S2="error", ...)), first inspect the actual values in that column for several rows using openpyxl. Print the values to confirm the exact string, number, or error type. Do not rely on a textual preview or description, which may show a representation that does not match the cell's actual value.


- Before writing any manipulation code, print the full target range (all rows and columns that will be read or written). If the task mentions a specific data range, inspect that exact range, even if a sample is provided. Print at least the first 100 rows if large, and compare the printed values against every condition described in the task (e.g., 'yellow cells', 'identical index rows'). Do not write logic based solely on the task description; ground it in the actual data you see. After reading the target range, verbally confirm its contents in your trace before computing.
- When the task mentions a special condition on data (e.g., 'identical index rows'), locate and print at least one example of that condition in the source data before coding. Verify that your detection logic correctly identifies only those rows and does not accidentally skip or overwrite normal data.
- When data is organized in multiple separate blocks (e.g., separated by blank rows), inspect the entire data range to map each block's boundaries, header presence, and row count before writing any transformation logic. Do not assume all blocks share the same structure.


- When copying data from a source range, inspect the data types (`type(cell.value)`) of source cells and ensure the output matches the required format (e.g., string vs integer, date vs datetime).
- When you need to locate a specific value (e.g., 'domestic') to determine which rows to keep or delete, print the entire column of that potential marker to confirm its exact row position and ensure no other occurrences exist. This prevents deleting the wrong rows due to a misplaced assumption about the marker's location.


**CRITICAL**: Before writing any formulas, always inspect the target sheet’s headers and first data rows to confirm column positions and sheet identity. Do not assume column letters or starting rows from previews — this is a common failure point that leads to misaligned formulas and empty answer ranges.
- After identifying rows to delete based on grouping or conditions, print the exact row numbers and the full row data (or at least the key columns used for grouping) to confirm they are the intended rows before executing the deletion. This prevents accidental removal of wrong rows due to logic errors.


- Before building any normalization or mapping dictionary (e.g., mapping plural to singular names), print all unique values of the source column and ensure your mapping covers every observed value. Unmapped values must be handled explicitly (e.g., raised as an error or passed through unchanged), not silently dropped.

- Before computing sums or averages over entire columns, print at least the first 3–5 data rows and the last data row of the target columns to confirm they contain numeric values and no unexpected empty cells. After computing, cross-check one sheet's sum with a manual addition of the printed values to catch range errors.
- Before writing any formula, print the current values of the target cell and all cells that the formula will reference (precedent cells). This confirms that the dependencies exist and contain the expected data types, and prevents overwriting existing formulas or data without understanding the current state.

- When fixing existing formulas, print the surrounding rows (e.g., the row above and below the target) to compare working formulas with broken ones and understand the intended pattern before making changes.

- After any batch deletion of rows (or columns), before saving, re-read the worksheet dimensions (`ws.max_row`, `ws.max_column`) and count the non‑empty rows in the affected data region. Confirm the count matches the expected number and that no unexpected blank rows or residual data remain.

- If the sheet contains a column of expected results (e.g., 'Expected', 'Result', 'Manual Result'), print that column side‑by‑side with the answer range before any modification. This reveals the target values and helps verify alignment with the actual data.

- Before grouping or merging data across sheets, confirm that the reference column (e.g., 'Column H') exists and contains the expected data type by printing its header and a sample of values. This prevents mismatched joins and silent data loss.

- When filtering or selecting cells based on fill color or other cell formatting (e.g., yellow cells), before writing any logic, inspect the actual fill properties of at least one cell that visually appears to match the condition. Print the cell's `.fill.fgColor.rgb`, `.fill.fgColor.index`, `.fill.fgColor.theme`, `.fill.fgColor.type`, `.fill.bgColor.rgb`, and `.fill.patternType` to determine the exact encoding. Do not assume a specific RGB string or index without confirmation. After filtering, print the count of matched cells and compare to a manual spot-check of visible matches to ensure the predicate is correct. When the task involves color-based conditions, print the fill properties alongside the cell values to reveal exact formatting before any logic is written.
- When searching for a specific marker value (e.g., 'X') that could be generated by a formula, inspect the range with `data_only=True` to see evaluated results. Use that view to identify which cells actually contain the marker, not just `.value` which may be a formula string. Confirm whether the task intends to operate on displayed values or literal stored content before building logic.

- When writing lookup formulas (VLOOKUP, INDEX/MATCH, etc.), print the entire lookup table — headers and all data rows — and confirm: (a) the lookup column values are unique and in the expected order, (b) the return column indices correspond to the correct headers (print the header at each index), and (c) there are no gaps or extra rows that could misalign the INDEX range or VLOOKUP column index. This prevents silent mismatches that produce empty results.
- Before sorting or any operation that depends on data types (e.g., date parsing, numeric comparisons), print the distinct types in the relevant columns (e.g., `set(type(cell.value) for cell in column)`). If mixed types exist, normalize them to a consistent type before proceeding. After writing, verify that the output cells have the expected types.

- **PROVEN HABIT**: Before designing any transformation logic, perform a comprehensive dump of all rows and columns in the source sheet(s) AND the target range in a single observation. Print every occupied cell with its coordinates to confirm the full data extent, column relationships, and destination layout. This one-step scan prevents hidden-column and row-boundary errors that partial samples miss.

- When performing bulk matching between columns or sheets (e.g., mapping headers to entries), print a sample of the match‑candidate pairs — at least the first three matched pairs and any header that matched zero entries — to confirm the mapping is plausible. Prefer explicit delimiter‑based extraction (e.g., split on a known separator) over a generic `in` substring test, unless the task explicitly guarantees substring matching is sufficient.

- When performing case-insensitive substring matching (e.g., checking if any keyword appears within a cell), normalize both the target cell values and the keywords to the same case (using `.casefold()`) and use substring containment (`any(k in text for k in keys)`). This prevents false negatives from case or partial matches. After writing, verify that the iteration bounds match the exact answer range.
## Writing Output


- Before writing, check the exact sheet name from the `answer_position` or output requirements. Do not assume which sheet to use. After writing, read back the target sheet's name and contents to confirm the output landed in the correct sheet.


Before writing any formula to the answer range, print the current values of the target cells (including the exact row and any adjacent rows) to understand what is already there — example values, partial entries, or pre‑existing formulas. This prevents accidentally overwriting data that should be preserved or that reveals the intended output pattern.
- When the task explicitly requires formulas, inject them directly using openpyxl (e.g., `ws.cell(r, c).value = '=IF(...)'`). After writing, re-open the workbook with `data_only=True` and read back the computed values to confirm they are non-empty and correct.
- When the task requires a computed result (a number, sum, count, or derived value) without explicitly requiring formulas, compute the answer in Python from the source data and write it as a static value, **unless the source data contains formulas that should be preserved for dynamic updates (e.g., when copying a table that includes formula columns). In such cases, inspect the source cells for formulas and copy the formula strings, adjusting references as needed.** Never type results manually; always derive them programmatically from the workbook data.


- Save the workbook to the exact `output_path` provided in the task instructions. Before saving, verify the full path string to ensure the file is written to the location the grader expects.
- When the task specifies a display format (e.g., 'm/dd/yyyy', '0.00%'), explicitly set the `number_format` property of each written cell to match. After writing, read back a sample cell's `number_format` to confirm it was applied correctly, not just the cell value.

- When a transformation rule requires modifying a cell and also writing a derived value to an adjacent cell (e.g., capping a value and placing the overflow in the next column), compute and write both cells in a single loop. This keeps the logic coherent and makes it easy to verify by inspecting the output range afterward.
- When the task provides an explicit answer range (e.g., A3:F36), constrain all read and write operations to that exact range. Use the exact row and column boundaries from the task specification; do not expand or contract the range unless instructed.
 If the answer_range is larger than the cells you intend to write, ensure every cell in that range is populated appropriately. For cells that should be empty, write an empty string (`''`) or clear them explicitly; do not leave them as `None`, as the grader expects a value.


- When constructing formulas that need cumulative evaluation per row (e.g., cumulative COUNTIFS), use mixed references with an anchored start row and a relative end row (e.g., `$A$2:A2`) to expand the range as you fill down. Nest conditional checks in explicit priority order as specified.
After saving, print the full file path and size to confirm the file was written to the correct location and exactly matches the `output_path` from the task instructions.


- **After writing formulas, you must immediately re‑open the saved workbook with `data_only=True` and print the answer range values (see Verification Script Template). Only proceed to TASK_COMPLETE after confirming that every required cell contains a computed value, not `None` or formula text.**
If the observation after that script shows formula text (strings starting with `'='`) instead of computed values, you printed with `data_only=False`. Stop immediately, re‑open the workbook with `data_only=True`, and print the answer range again before proceeding.

- When filling formulas down a column, confirm the fill range row count exactly matches the source data row count (e.g., if source has 15 data rows, the formula should fill exactly 15 cells, not 14 or 16). After writing, verify the first and last cell of the answer range both contain computed values, not None or formula text.

- For extraction tasks (e.g., pulling a substring, splitting text, extracting a name from a cell), compute the result in Python using string methods or regex, and write it as a plain value. Do not write formula strings (e.g., `=MID(...)`) unless formulas are explicitly required. After writing, verify the answer range contains the computed values, not formula text.

- If the required sheet from `answer_position` does not exist in the output workbook, create or rename a sheet to match it, and copy the result data into that sheet. After saving, re-open and confirm the sheet name and range match the `answer_position` exactly.

- Before writing formulas, confirm the target sheet by printing `wb.sheetnames` and `ws.title`, and print the first row of that sheet to verify column headers. After writing, re-open the workbook and print the answer range to ensure formulas are present and produce values, not None.
- When writing a formula that will be filled down, test it on the first data cell: write it to that cell, save, re-open with `data_only=True`, and print the computed value. Confirm it matches the expected result before filling down to the remaining cells.
- If a required output value (e.g., a sum, count, or aggregated result) does not fit within the `answer_range` columns as initially planned, do not write it outside the graded region. Instead, place it inside the range (e.g., in an existing column) or re‑examine the instruction to determine the correct layout. All outputs the grader expects must be within the `answer_range`.
- When writing a formula to a range of cells, construct the formula string with relative references (e.g., `f'=IF(B{r}<37.5, D{r}*2, D{r}*1.5)'`) and apply it in a single loop over all target rows. This ensures each row's formula adapts correctly and avoids manual cell-by-cell entry.


This script-based injection is the recommended approach for regular patterns. After writing, always verify the computed values by re-opening the workbook with `data_only=True` and printing the answer range.

- If the range you are writing to includes a header row, always inspect the first row's value and treat it as a header: preserve it unchanged (skip transformations for row 1) and verify after writing that it remains intact.
- When the instruction says to "insert" a specific text into a column under certain conditions, first inspect the existing values in that column (print a sample or count non-empty cells). If the column already contains data, explicitly decide what to do with rows that do not meet the conditions and with any pre-existing data — do not assume an empty or clean slate. After writing, verify that only intended rows were modified and that pre-existing data is correctly handled.
- When the answer_range is provided, use its exact row and column boundaries to set loop bounds for reading and writing. This avoids unnecessary full-sheet scans and ensures you only touch the graded cells, reducing the risk of accidental modifications outside the target area.

- When the answer range already contains pre‑filled values (example rows, headers, etc.), print the full range before writing and note which cells are filled and which are empty. Preserve existing values unless the task explicitly asks to overwrite them, and fill only the empty cells following the same pattern. After writing, verify that the pattern is consistent and no example cells were accidentally changed.

- When scoring involves ties (e.g., points divided among top performers), use MAX and COUNTIF to dynamically allocate points, and test the formula on a sample row before filling down.

- When using a dictionary to populate cells from a lookup, always provide a default of empty string (`''`) for missing keys (e.g., `mapping.get(key, '')`). This prevents `None` from being written into cells that should be blank.

- For multi‑condition row filtering, implement the logic in Python using explicit condition checks (e.g., `str.startswith`, substring containment, equality) rather than relying on Excel formulas. Validate that all condition terms match the instruction’s exact phrasing before executing. After writing, read back the output range to confirm the filtering produced the expected row set and no excluded values slipped through.
## Verification


- After any write operation, explicitly read back the written range (especially the graded answer range) and confirm every cell's value matches expectations. Print the exact range using `ws.iter_rows(min_row=..., max_row=..., min_col=..., max_col=..., values_only=True)`. Confirm that cells contain computed data (numeric values, strings, etc.), not errors, `None`, or raw formula text, unless formulas are explicitly required. If any cell is None or empty when data should be present, investigate and correct before declaring completion.
- After writing any cell values, immediately read back the value(s) of those cells (e.g., `sheet['F4'].value`) and include the result in your observation before declaring the task complete. This catches write failures, empty cells, or unintended values.
- Cross-check at least one written cell's value against its corresponding source values to verify the computation logic executed correctly.

- When copying values from one sheet to another, after writing, read back the target range and compare the value in a row where the key order differs from the source to confirm the mapping is correct, not just positional.
- After constructing output, spot-check at least one row that should be blank and one that should contain data to verify merge logic.
- Only declare completion after confirming the output range holds the expected kind of result. Never rely on file size or dimensions alone; always open the saved workbook and read the cell values.

- **HARD GATE**: Do not emit `TASK_COMPLETE` until you have (a) re-opened the saved output workbook with `data_only=True`, (b) printed the exact answer range values, and (c) confirmed every required cell contains a clean, expected value (no `None` where data is expected, no floating-point noise, no formula text). Print the range explicitly in your observation before completing.


- Before declaring completion, read and print every cell range specified in the task's `answer_position` (or the graded region). Confirm that all ranges contain the expected data, including that empty ranges (zero-count buckets) are correct. If any range is empty or contains unexpected values, stop and diagnose the cause.

- When formulas have been written, always re-open the workbook with `data_only=True` before reading the answer range. Print at least 3 cell values from the answer range to confirm they are computed numbers or strings, not `None` or formula text.

- Before writing formulas, extract the expected output for at least one sample row from the task instructions and compute it manually. After writing, compare the formula's output to this expected value to verify the calculation logic matches the intended method.

- If you performed a sort, after writing, read back the full data range and confirm the ordering matches the expected precedence. Check a few rows at boundaries where the primary key changes to ensure the secondary sort is correct.

- After saving the workbook, re-open it with `openpyxl.load_workbook(filename, data_only=True)` and print the answer range to confirm the saved file contains the expected values, not just in‑memory changes. This catches cases where changes were only in memory or not persisted correctly.

- When reading back numeric answer ranges, scan for floating-point artifacts (e.g., `39.49999904632568` instead of `39.5`) and unexpected `None` values. If found, round or clean the values before saving, and confirm whether empty cells should remain blank or contain a default (e.g., `0`). Re-save and re-verify until the output is clean.


- When constraints (min/max values, bounds) are specified, verify that all output cells respect them. Also confirm that cells that should remain unchanged (e.g., originally zero or blank) are still unchanged after the operation. For tasks with ordering rules (e.g., add before subtract), spot-check a sample row's inputs and outputs to confirm the correct sequence was followed.

- After any structural modification (column/row insertion or deletion), read the header row(s) and column count to confirm the intended columns are present and unwanted columns are absent. For deletion operations, print a list of all column-header values and visually verify that no header matches the deletion criterion.

- When performing conditional writes (e.g., only filling blanks, only overwriting when a condition holds), save a copy of the target range's values before writing, then after writing, compare to confirm that only cells meeting the condition were changed and no pre‑existing data was lost.

- When the output involves transposition, reshaping, or multi-column writes, verify the output shape: confirm the number of rows and columns in the written range matches expectations, and spot-check that values intended to span multiple columns actually appear across columns, not stacked in a single column.

- After any operation that deletes, inserts, or reorders rows or columns, read back the exact answer range specified in the task (e.g., `'Sheet1'!A3:A24`) and verify that the number of cells matches the expected range size and that the content is consistent with the operation's intent. Print the full range to confirm no gaps or extra rows were introduced.
- After bulk deletion or filtering, print all remaining rows (or at least the first and last few rows) and confirm that the expected row types (headers, data rows, totals) are present and that no rows were erroneously kept or removed.

- After deleting rows or columns in a reverse loop, read back the remaining rows (or columns) and confirm that indices are contiguous, no gaps, and within the expected range before proceeding.


- When the task requires a specific data type or format (e.g., date without time, numeric, string), verify the type of output cells (e.g., `type(cell.value)`) and ensure it matches the requirement. For dates, confirm they are `datetime.date` objects, not `datetime.datetime`.
- After any formatting or style changes, re-read the answer range to confirm that the underlying data values are still present and correct. Formatting can sometimes overwrite cell values if applied incorrectly (e.g., setting value to text).
- After saving the workbook, verify the output file size is non-zero as a quick liveness check before re-opening.

- When you map indices from a list or array to spreadsheet rows (e.g., adding 1 to a 0-based index), after writing, read back the first and last cell of the mapped range and confirm each value matches the corresponding list element. Before mapping, inspect the first row to determine if it is a header (non-numeric/text) and adjust the row offset accordingly.

- When writing to a large answer range, always read back the first few rows and the last row explicitly to confirm that the last row contains data and not `None`. Do not assume the entire range is filled.

- After saving, print a confirmation message with the output path and key computed metrics (e.g., number of rows written, max date, sum) to catch gross errors early.
- After saving the workbook, print the answer-range values in the same script to provide a direct audit trail of what was written. This reduces turn count and confirms the saved state before declaring completion.

- After saving, print a few cells immediately outside the answer range (e.g., the row above and below) to confirm that no unintended modifications occurred. This ensures operations were constrained to the exact graded range.


- After any row/column deletion or insertion, always re-open the saved workbook (with `data_only=True` if formulas exist) and print the exact answer range. Do not rely on in-memory `ws.max_row` or cell values after structural mutations; they may be stale.
- Before TASK_COMPLETE, cross-check the printed answer range against any explicit constraints in the task instruction (e.g., specific rows that must remain, presence of certain headers). Confirm that all constraints are satisfied.
- When the task explicitly requires formulas, after writing, read back a sample cell with `data_only=False` (or print its `.value`) to confirm the cell contains a formula string (starting with '='), not a computed constant. This ensures the output is a formula, not a pre-calculated value.
- After grouping, filtering, or any transformation that modifies data layout, re-run the same inspection code used before the transformation to print the before-and-after state of the affected groups. Confirm that only intended changes were applied and no unexpected alterations occurred.

- If the instruction required VBA or macros, after saving, use xlwings to open the workbook and print the VBA module's code to confirm it exists and contains the expected logic. Also verify that any answer_range contains the computed results of the macro, not static values.
- After writing any conditional logic (e.g., if-else chains, filtering based on string matches), read back at least the first 5 and last 5 rows of the answer range and any conditionally formatted cells. Confirm that the computed values match the intended logic and that no unexpected Nones, wrong strings, or missing formatting appear. Only then proceed to TASK_COMPLETE.
- If the task instruction includes a specific output string format or example (e.g., 'would return Group 1, Group 2'), after writing, read back the answer range and confirm that the written cells contain that exact format character-for-character, not a different keyword or representation.

- Before TASK_COMPLETE, print all sheet names of the saved workbook (e.g., `wb.sheetnames`) and confirm the required sheet from `answer_position` is present. If not, do not declare completion; create the sheet and re-verify.


- When printing verification output, always include structural metadata alongside data values: print `ws.title`, `ws.max_row`, and column count to confirm the correct sheet was modified and the expected number of rows remain. This catches wrong-sheet writes and unintended row loss in a single observation.
- When the target sheet already contains expected output values (e.g., a pre-filled 'Expected' sheet), save a copy of the original values before writing. After writing, re-read the answer range and compare row-by-row against the original to confirm no unintended deviation. Flag any discrepancies before TASK_COMPLETE.

- After aggregation, grouping, or deduplication operations, verify that the number of non‑empty rows in the answer range matches the expected count of unique groups or aggregated entries. Print the count of non‑None cells in the key column and compare to the expected number.

- After writing, also print `cell.number_format` for at least the first and last cell of the answer range to confirm formatting matches the task specification.
- For any transformation that maps input values to output values (e.g., scoring, scaling, normalization), verify boundary conditions: check that the minimum input maps to the expected minimum output, the maximum maps to the expected maximum, and at least one intermediate value maps correctly.

- After reordering, sorting, or copying rows between ranges, print the header row and column count of both the source and target. Confirm the target has the same number of columns as the source and that every expected column header is present. Spot-check at least one row's formula columns (e.g., columns with `=IF(...)` or other computed values) to ensure they were preserved and not replaced with None.

- After writing, verify that no row in the answer range is entirely blank (unless explicitly required) and that the number of populated rows matches the expected count (e.g., derived from source data). Print the row indices and values for any blank rows to catch missing data.

- When the task requires removing blank cells (e.g., "remove any cell that is blank"), after writing the output, read the entire answer range and confirm that no empty cells (`None` or `''`) appear after the last non-empty value. If trailing blanks exist, remove them and re-save before declaring completion.
- For conditional writes, after saving, print the head and tail of the target column and count how many rows received the intended value. Confirm this count matches expectations and that no rows were incorrectly modified or left unchanged.
- After insertions or deletions, if the answer range contains formula‑driven markers (e.g., `=IF(condition, "X", "")`), verify that those cells still produce the expected marker and are not `None`.

- Do not rely on printing intermediate variables or a single column to verify the output. Always re‑open the saved workbook and print the exact answer range cell‑by‑cell as specified in the Pre‑Completion Checklist. Confirming `len(dups)`, row counts, or printing only one column is insufficient; you must inspect the graded range directly.
- When printing the answer range for verification, output it as a single 2D list (list of lists) to make the shape and values immediately comparable to the expected output. This structured format makes any missing or extra cells obvious at a glance.

- **If your verification printout shows formula text (strings starting with '='), you have NOT verified correctly.** You printed cell values without `data_only=True`. Stop, re-open the workbook with `data_only=True`, and print the answer range again before declaring completion.

- After writing output that involves per‑header row insertion or matching, count the number of output rows per matched header and compare to the expected count (e.g., number of source rows for that header). Print the per‑header row counts and verify they satisfy the task's constraint (e.g., "same number of rows") before calling TASK_COMPLETE.

- After writing, cross-check the output row count and column count against the expected dimensions derived from the source data (e.g., number of data rows, unique groups, or categories). Print both counts in the verification output to catch off-by-one errors and silent data loss.

- When performing conditional copy or fill operations (e.g., copy from column G to K only when G is non-empty), before writing, save a snapshot of the target column's values. After writing, print both the original and new values side-by-side for a sample of rows where the condition was false, and confirm that those cells are unchanged. This prevents overwriting existing data that should be preserved.
## Common Pitfalls


- Assuming a lookup value exists in the lookup range without inspecting actual cell contents. Always verify compatibility before writing the formula.
- Declaring the task complete without re-reading the answer range after modification. Always re-read and print the output cells.
- Skipping pre-write inspection of the target range. Always read the target range before you write.
- Do not assume insertion shifts resolve column indexing correctly without re-verifying source and target offsets. Before copying cells in a shifting operation, inspect the contents of the computed source column and target column in a small range to confirm the offset logic is correct and data aligns with expectations.
- Writing to the wrong sheet (e.g., overwriting an input sheet instead of the required output sheet).
- Assuming source data is complete without inspecting for duplicates, missing IDs, or misalignment.


- Relying on `ws.active` without confirming the sheet name. Always enumerate all sheet names (e.g., `wb.sheetnames`) and confirm the target sheet matches the `answer_position` sheet reference. After writing, read back cells from the exact sheet and range the grader will inspect, not from `active`.
- Writing formulas when the deliverable is computed values (e.g., 'y' or empty string). Prefer computing the answer in Python and writing static values, unless the prompt explicitly requires formulas. **Exception**: When the task describes a dynamic output that should respond to input cells (e.g., 'Display the dates based on the start and end date criteria entered in cells I2 and J2'), prefer formula-based approaches (e.g., FILTER, array formulas) that automatically update when criteria change, unless the grading specification explicitly asks for computed output only. Before writing, inspect the target area for any existing formulas or dynamic references, and re-read the instruction for phrases like 'based on criteria' that imply continued responsiveness. If formulas are written, verify that the saved file contains evaluated results, not formula text, by reading back the cell values after saving.

- Using multiple stable sorts to achieve a multi-key sort; this can break the secondary order. Instead, use a single sort with a compound key (e.g., `sorted(rows, key=lambda r: (key1(r), key2(r)))`). After sorting, read back a few rows across group boundaries to verify ordering.

- Write-and-Walk: after writing formulas, do not declare completion without re-opening the workbook (`data_only=True`) and reading the answer range values. If all values are None, the formulas were not evaluated (openpyxl does not compute formulas); re-check formula syntax, sheet name, and range, and re-save after ensuring formulas are correct. Otherwise, spot-check at least 3 cells to confirm they contain computed data, not empty cells or formula text.

- Hardcoding row indices without scanning for headers and data boundaries. Always programmatically determine the data range before writing, and verify that metadata rows (like min/max labels) are not accidentally overwritten in answer columns.

- Copying source cell styles (font, fill, number_format, etc.) without checking if they are appropriate for the output. Unless the task explicitly requires preserving formatting, write plain values without copying styles. After writing, read back a few cells and print their number_format and data types to ensure clean, legible output.

- When deleting rows or columns in a loop, always iterate in reverse: for rows use `for r in range(ws.max_row, 0, -1)`, for columns use `for c in range(ws.max_column, 0, -1)`. This avoids index shifting that would skip rows/columns or cause misalignment.

- Writing transposed or reshaped output without verifying the row/column layout. After any operation that changes data orientation (transpose, pivot, unstack), read back the output range and confirm values are distributed across the expected number of columns per row, not collapsed into a single column.

- DO NOT verify formulas by reading cells with `data_only=False` (the default) and seeing formula text; this does not confirm that the formulas produce values. Always re-open the workbook with `data_only=True` and read the answer range to confirm every cell contains a computed value, not `None` or an error.

- Performing destructive operations (deletion, filtering) without first printing the full data region to confirm what will be removed, and without re-opening the file to verify the answer range after saving. Always inspect the entire sheet before deleting, and after saving, re-open with `data_only=True` and print the exact answer range to confirm the result.


- Trusting a truncated spreadsheet preview or summary instead of running your own full inspection with openpyxl. Always inspect the workbook yourself as the first action.
Checking only file existence (e.g., `ls -l`) or file size after saving and assuming the write succeeded. File existence or size alone tells you nothing about cell contents. Always re-open the workbook and read back the answer range values.
- Skipping required steps from the task description. Always enumerate all required actions (e.g., fix a formula, apply formatting) before writing any code. After completing all steps, verify that each required action was performed by re-reading the relevant cells.


- Skipping inspection of reference or example output sheets. Always examine the reference sheet's structure before implementing, and compare your output's structure after writing.

- After any failed script execution, before rewriting the logic, diagnose the environment: check the working directory for stale files (especially `openpyxl.py` or other conflicting module names), verify the Python path, and ensure no circular imports. Remove or rename any conflicting files and re-run in a clean directory.


- When the task asks for VBA code, a macro, or any automation that should respond to data changes, do not write a static computed value. Instead, embed the executable code (VBA module, formula, etc.) in the workbook. Use xlwings to add VBA if needed. After embedding, test by changing an input cell and verifying the output updates.
- After any sort operation, do not assume the output is correctly ordered because the file was saved. Always re-open the workbook and print the sorted range, checking at least the first and last few rows to confirm the order matches the expected precedence. Pay special attention to string vs. numeric sort behavior (e.g., '10' before '2') when values are stored as strings.
- Writing a formula that unintentionally includes its own cell in the reference range, creating a circular reference. Before writing any formula that references a range (e.g., MAX, SUM, AVERAGE), print the formula cell's address and the intended range to confirm the cell is excluded.


- Assuming a numeric sheet reference (e.g., 'sheet 2') without listing all sheet names and mapping the index to the correct name. Always resolve ambiguous references to explicit sheet names.
- Misinterpreting the instruction as a request for code when the answer_range is a cell range. Always inspect answer_range; if it is a worksheet range, produce data in those cells, not VBA code or explanation.


- Implementing a custom algorithm (e.g., letter sequencing, complex logic) without first testing it on a tiny isolated case. Before scaling to the full dataset, run the core logic on a small sample (e.g., 3 blanks) and print the output to confirm it matches expectations. This catches off-by-one or mis-implemented letter-sequencing without a ground-truth answer.
- Skipping verification of generated patterns: after writing, always print the first few rows of the answer range and manually confirm that the pattern (e.g., sequential letters, dates) is correct, not just that cells are non-empty.

- Writing formulas with openpyxl and expecting the saved file to contain computed values. openpyxl does not evaluate formulas; the saved file will contain formula text, not computed values, unless the file is opened in Excel and saved. Always re-open with `data_only=True` to verify computed values. If the task does not explicitly require formulas, compute values in Python and write them as static data.
- Ignoring the full answer_range specification: the instruction text may mention only a few cells, but the graded region (from the task metadata) is the authoritative target. Always inspect the answer_range and ensure every cell in that range is handled — either filled with the correct value or explicitly cleared — before declaring completion.
- Confusing printing the output file path with verifying cell contents. Printing the output path is not verification; you must re-open the workbook and print the answer range values. The observation must contain actual cell values, not just a path.
- Treating instruction examples as illustrative rather than normative. If the instruction says 'would return Group 1, Group 2', the output must be exactly that string, not a different representation like 'BOTH'. Always treat example output strings as a spec; verify character-for-character after writing.

- When the task explicitly asks to fix a broken formula (e.g., 'Edit cell B7 so that it is not #REF!'), always inspect the formula's structure, identify the specific error cause, and correct the formula rather than replacing it with a hardcoded value. After repairing, verify by computing the result; if the formula references a lookup table, confirm the lookup parameters (range dimensions, column index) are consistent with the actual data layout.

- Assuming the output sheet already exists or that the data sheet is the answer sheet. Always check `answer_position` and create the required sheet if missing.


- Assuming the graded answer range defines the full data boundary for operations (e.g., deletion, filtering). Always inspect the entire sheet's data extent (print `ws.max_row`, scan tail rows) before performing operations that may affect rows beyond the graded region. After deletions, verify by printing the entire affected column's remaining values, not just the graded range.
- Iterating over all columns when the instruction names a specific range (e.g., 'Comp1 to performance'). Before writing transformation logic, print the column headers that will be processed and confirm the start/end indices match the requested set, not the entire table.
- Hardcoding row iteration bounds directly from the answer_range specification (e.g., `range(2,67)` from `C2:C66`) without first inspecting the sheet to determine the actual data extent. The answer_range describes where to place output, not how many data rows exist. Always read `ws.max_row` and inspect the relevant columns before setting loop bounds.
- Writing a conditional formula (e.g., `IF(B2=1, ...)`) without first printing the unique values in the condition column across the full data range. If the expected marker value is absent or formatted differently, the formula silently produces an empty answer range. Always inspect the condition column's actual values before writing the formula, and verify the output after saving.

- Assuming that simple aggregate formulas (SUM, AVERAGE) don't need verification — they can still produce empty cells if the range is wrong or the data is non-numeric. Always re-open with `data_only=True` and print the answer range after writing any formula, no matter how simple.
- Blind row-position-based copying without verifying key alignment. When transferring values between sheets, never assume rows are in the same order. Always inspect the key column in both sheets; if the order differs, use a lookup (VLOOKUP, INDEX/MATCH, or a Python dictionary). After writing, spot-check a row where the key order differs to confirm the correct value was mapped.
- Using the answer_range specification as the loop bound for data extent. The answer_range defines where to place output, not how many data rows exist. Always inspect the sheet to determine the actual last row of data (e.g., `ws.max_row`, last non-empty row in the relevant column) and use that for loop bounds. After writing, confirm the number of rows written matches the original data extent unless the task explicitly asks for a subset.
- Applying string transformations (slicing, regex) without first printing the full column's distinct values. Always print the entire column's values, note all formats, and verify the transformation is safe for every observed value. After writing, spot-check multiple positions (beginning, middle, end) to catch silent corruption.
- Creating a new blank workbook instead of loading the provided input file. Always start from the given workbook to preserve existing sheets, data, and structure; only modify the target cells/sheets.

- Writing only to the rows that appear broken while ignoring other rows in the answer range. The graded region often spans multiple rows; ALL cells in the answer_range must be populated, even if some already contain working formulas. Before writing, print the full range boundaries and verify your code touches every row and column in that range.

- Assuming the transformation scope (e.g., "all columns") without inspecting the workbook structure. Always list all sheet names, print first rows of every sheet, and note which columns contain data. Match your loop bounds to the actual data extent, not a partial preview.

- Reordering or copying rows while writing only a subset of columns, silently dropping formula columns or other data. When reordering rows from a source range, always determine the full column count of the source and write ALL columns to the target, not just the explicitly mentioned ones. After writing, print the header row and column count to confirm no columns were lost.

- Applying number formats to header rows that contain non‑numeric data (dates, text). Before formatting a column, inspect the first row's data type; if it is not numeric, apply the format only to data rows (row 2 onward) to avoid corrupting headers.

- When removing duplicates and keeping only the last occurrence of each value, scanning forward and deleting on the fly corrupts the loop. Instead, scan backward to build a set of rows to keep, then delete all other rows in a separate pass (reverse order). Verify after the operation that the preserved rows still appear in their original relative order.

- Assuming fill color encoding (RGB string, index) without inspecting actual cell fill properties. Always print the fill details of at least one target cell before writing a color-based filter.

- Computing a global aggregate (e.g., `max(all_rows)`) when the instruction requires a per-group aggregate (e.g., "last date per brand", "total per category"). Always parse phrases like "per X", "for each X", or "by X" as requiring a group-level operation: group rows by the category column, then compute the statistic independently for each group. Before writing results, print the per-group intermediate values alongside a sample of the original rows to confirm the grouping matches the instruction's phrasing and that every expected group appears in the output.
- After a write that shifts rows, deletes blanks, or rearranges data, the answer range may still contain residual `None` values or misaligned data. Always re‑open the workbook and print the exact answer range to confirm every cell in the graded region is populated as expected, with no trailing blanks or artifacts. Never rely on file size or a success message alone.
- Treating a “debug my code” or “correct my macro” task as a data transformation. When the instruction references an existing macro or code on a named sheet, first inspect that sheet and any embedded VBA (use xlwings or openpyxl to read the module). Fix the macro in place, embed the corrected code, and verify it runs correctly on the target sheet. Do not replace it with a one‑off Python script that produces static data.

- Overwriting pre‑filled example cells in the answer range without inspecting them first. Always read the answer range before writing to understand the existing pattern and preserve any example values unless explicitly told to replace them.

- Assuming all values in a column are numeric or of the same type without handling headers, blanks, or text strings. When performing type-dependent operations (e.g., Decimal conversion), wrap the conversion in a try/except and skip non-conforming rows. After processing, verify that non-conforming rows (headers) are preserved correctly.

- Copying source cells as static values without first inspecting whether they contain formulas that should be preserved. When transforming data from a source range, always check if the source cells are formulas (print cell.value and check if it starts with '='). If the task does not explicitly require computed values, prefer preserving the formula structure by copying the formula strings (adjusting references) to maintain dynamic updates. Only write static values if the task explicitly asks for computed output or the transformation cannot be expressed as a formula.

- Printing a row count or summary metric after writing and treating it as verification. A row count tells you how many rows were written, not whether every cell in the graded answer range is populated. The answer range may extend beyond the written rows (e.g., A1:D22 with only 18 rows of data leaves A19:D22 empty). Always re-open the workbook and print the exact answer range cell-by-cell to confirm every cell in the graded region is populated as expected.
## Pre-Completion Checklist

Before calling TASK_COMPLETE, perform these checks in order:

1. Re-open the saved workbook with `openpyxl.load_workbook(output_path, data_only=True)`.
2. Print the exact answer range (all rows and columns specified in `answer_range`) using `ws.iter_rows(min_row=..., max_row=..., min_col=..., max_col=..., values_only=True)`.
3. For each cell in the answer range, print its value, `type(cell.value)`, and `cell.number_format`. Confirm that every cell contains the expected data type (no `None` where data is expected, no raw formula text, no error values) and that the number format matches the task specification.
4. Explicitly compare each output cell against the task's deliverable expectations (e.g., numeric values vs formulas, decimal representation, string format). If the task provides an example output string or a reference sheet, confirm a character-for-character match.
If the task required a macro or VBA code, print the VBA module's code to confirm it exists and contains the expected logic. Also verify that the answer_range contains the computed results of the macro (not static values) by changing an input cell, re-running the macro, and re-checking the output.
4. If the range includes a header row, confirm it is preserved and unchanged.
5. Print the first and last few rows of the answer range in your observation.
6. Only after all checks pass, emit TASK_COMPLETE.


**CRITICAL**: Before proceeding to step 6, confirm that your current observation includes the printed answer range values from the saved file. If it does not, stop and re‑open the workbook with `data_only=True` to print the range. Do not emit TASK_COMPLETE until the observation contains these values.