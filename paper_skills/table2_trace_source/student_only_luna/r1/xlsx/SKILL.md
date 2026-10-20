---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow


Follow an inspect-then-act pattern: first, inspect the workbook structure and sample data using read-only operations; then, plan and execute write operations based on those observations.
After writing, before saving, read back the full answer range and verify the values match the expected output from the source data. After saving, recalculate formulas using recalc.py, then re-open the workbook and read back the answer cells. Verify they contain computed values (not None or formula text). Do not call TASK_COMPLETE until this final verification passes.


**CRITICAL:** Never call TASK_COMPLETE without first re-opening the saved workbook and printing the answer range to confirm computed values are present. This is the most common cause of task failure.

This applies to **all** tasks, including those with static values or row deletions; always verify the answer range contains the expected data.
Before writing any code, identify the exact deliverable type required (e.g., macro, chart, formula, data modification). If the deliverable cannot be directly produced with openpyxl (e.g., a VBA macro), inspect the workbook for existing macros or check whether the task context implies the macro was meant to be applied to the data. If you cannot produce the exact deliverable, state your interpretation and produce the closest feasible result, then verify that the saved output contains that result.


When the task explicitly permits a non-VBA solution (e.g., 'If you have to, you can solve it without VBA'), always choose a direct Python/openpyxl implementation over attempting to write macros.

Write a single, self-contained Python script that loads the workbook, inspects as needed, performs all transformations, saves to the exact output path specified in the instructions, and then verifies the result. Avoid multiple separate script executions or unnecessary file‑system explorations.

The single‑pass script‑then‑verify pattern has proven highly effective; always pair efficient computation with the full verification steps below.


- **Never hardcode row/column numbers or assume sheet structure from task descriptions or summaries. Always open the workbook and print its full contents (sheet names, dimensions, all rows or a representative sample) before writing any code.**
- Complete all data collection and in-memory computation before writing any changes to the workbook. This avoids leaving the output sheet in a partially modified state if an error occurs mid‑computation.
## Inspection


- **As the very first action**, print sheet names, dimensions, and all rows (or for large workbooks >500 rows, the header row and first 10–20 data rows plus unique values) using `iter_rows(values_only=True)`. Additionally, print `type()` and `repr()` for a sample of cells in each column to detect non‑numeric placeholders (e.g., `\xa0`), date headers, or other anomalies. After reviewing, map out key columns, the ordering of IDs across sheets, and any format templates. Verbally note the exact column letters and starting row numbers for every field you will reference, to lock in the mapping before coding.

- When printing the sheet, include all columns (not just the first few) to detect multiple independent data regions or pre‑existing content that may affect the task.
- For any target column or data range, print the full relevant range to avoid acting on truncated previews.
- Scan each sheet to discover actual data boundaries: find the first and last non-empty rows/columns. Stop at the first fully empty row. Use these dynamic bounds for all lookups and writes.
- **Do not assume the data column range from a preview snippet.** Always print `max_column` and inspect the actual data extent (headers and values at the rightmost columns) to confirm the full width. After writing, verify that the output's column count matches the intended range (e.g., check `target.max_column`).
- If an attached example file is referenced (e.g., Sample.xlsx), load and inspect it before coding. Compare its structure, labels, and computed results to the input workbook to confirm the expected mapping.
- When an answer range already contains values, inspect them first. Compare with the task description to decide whether to extend, complete, or replace. Print old vs. new values before overwriting.
- **Locating headers dynamically:** Before any column insert/delete/move operation, scan the header row (identify which row contains headers) to find the target column index dynamically. Never assume a fixed column letter. Print the located column index so it can be verified and reused.
Print the full header-to-column mapping (header text and index) to confirm it matches the expected column names before using it.

- **Before any cross-sheet lookup or matching logic**, print the header row with column indices for every source sheet involved.

- **When matching headers across sheets (e.g., to align columns), print the generated mapping of matched pairs and spot-check a few entries against the raw source data. Use exact or delimiter-bounded matching; avoid substring containment unless the task explicitly requires partial matching. Confirm no false positives before writing.**
When selecting a subset of sheets based on positional order (e.g., all sheets before a summary sheet), print the full list of sheet names and their headers. Confirm that each selected sheet contains the expected data columns and is not an auxiliary sheet (e.g., hidden, empty, or unrelated). Map the required fields from the task description to actual column positions by matching header strings (case-insensitive, stripped). Print a small sample (first 3–5 rows) of the mapped columns to confirm the extracted values match the intended data.

- Before aggregation or matching logic, inspect the first 5–10 data rows of every source sheet. Print the exact values you intend to match on (e.g., account references) and the values you intend to use as amounts. Confirm that your matching keys (substrings, patterns) actually appear in those rows. If any expected category has zero matches, stop and re-inspect the source data rather than proceeding silently.
- Before writing formulas that aggregate or match values, identify all grouping columns (e.g., OEM, category) that define distinct subsets. Print their unique values and ensure formulas include all necessary grouping dimensions to avoid mixing subsets.
- **Before writing any formula that uses a condition column (e.g., COUNTIF, SUMIF, IF based on a specific marker value), print the full column's values (all rows) and confirm the exact marker values, their data types, and their row positions.
- Before writing a scoring or normalization formula (mapping a range of values to a fixed scale), print the full column's values, compute the min and max, and test the formula on those anchor points to confirm the mapping. Verify the computed values after recalc. Do not rely on a preview of the first few rows; the marker may appear later or be absent.**
- **Never rely on `wb.active` without verification.** Always print `wb.sheetnames` first and explicitly select the target sheet by name (`wb['SheetName']`) or index. The active sheet may default to an unexpected sheet, causing output to land in the wrong place and grade as None.
- **When a sheet is referenced by ordinal (e.g., 'sheet 2'), print all sheet names with their indices** (`for i, name in enumerate(wb.sheetnames): print(i, name)`) and confirm the target sheet before any modification. After the operation, verify the affected sheet's structure changed as expected (e.g., column count decreased after deletion).
- When writing formulas, first inspect any existing formulas in nearby cells to understand the expected pattern and dependencies. This helps ensure new formulas reference the correct columns and ranges.

- Before writing update logic that searches for specific text, inspect the target column's actual cell values. Print unique values and confirm whether the search text appears exactly as stated, as a substring, or in variant forms. Design matching logic accordingly (e.g., substring check vs. exact equality).


- For sheets that may contain summary or total rows (e.g., 'Total'), also print the last 5–10 rows to identify and preserve them during filtering or deletion operations.

- **Non-tabular layouts:** When source data is arranged in non-tabular layouts (e.g., invoice sections with header rows and total markers), identify semantic boundary markers (e.g., 'INVOICE NO', 'TOTAL') and parse sections systematically. Print and verify all extracted values before using them to populate another sheet.

- Before writing any transformation or cleaning code that depends on data types or string patterns, print the first 5–10 cell values of the target column using `repr()` and `type()` to see exact data types and formats (e.g., datetime vs. string, presence of time components). Design your branching logic around the observed types, not assumptions.

- If the task specifies case-insensitive matching, normalize both the search term and cell values to the same case (e.g., `.lower()`) before comparison.

- **When the task description mentions cell formatting (colors, fills, styles) as a condition**, inspect the relevant cells' fill, font, and style properties before writing any logic. Print a summary of cells with non-default formatting (e.g., fill color) and confirm they match the described condition. Use this inspected state as the basis for any computation, not assumptions.
- **When extraction logic depends on cell formatting (fill color, font, etc.), iterate over the entire relevant range** (e.g., all used rows in the target column) and print each cell's value alongside its formatting attributes (e.g., fill patternType and fgColor.rgb). Use the exact observed pattern criteria in your extraction code. Do not rely on a sample; formatting may be sparse or irregular.

- **If the workbook contains a sheet that appears to be a manual or expected output (e.g., 'Manual Result', 'Expected Output'), inspect it as a reference before writing any code:** print all rows of both the source data range and the reference range side-by-side (e.g., actual result columns alongside expected result columns). For the reference range, use `data_only=True` and also print cell properties (e.g., whether each cell contains a formula via `cell.data_type`) to understand the expected deliverable type. Confirm row counts, column structures, and value patterns match expectations before designing the transformation.

- Before writing formulas that use IF or other conditional logic referencing a column, print the first 5–10 values of that column to confirm the actual data values and types. Adjust the formula's comparison to match the observed values (e.g., check for '#N/A' instead of assuming the literal string 'error').

- When inspecting an answer range that already contains values, also print the data types (`type()`) of those cells to ensure correct comparisons (e.g., datetime vs string) and to decide whether to extend, complete, or replace.

- When data is sparse (e.g., rows with data separated by empty rows), scan the full column to find all non-empty cells and print their row indices. This reveals the exact data positions and prevents formulas from being written over empty gaps.


- When a cell displays an unexpected value or error, first load the workbook with `data_only=True` and print the computed value of that cell. Print the existing formula and evaluate its parts. Do not write a replacement until you understand why the current formula fails. After writing, verify the new formula's computed result with `data_only=True`.
- **Before writing to a specific answer range** (e.g., A3:F36), print the full range to verify its current content and structure. This reveals any existing headers, blank rows, or unexpected data inside the range and prevents assumptions based on truncated previews.
- Before sorting data that contains blank rows or header rows within the range, print all non-empty cells with their row indices and classify each row as data, header, or blank. Plan how to sort only the data blocks while preserving headers and blanks exactly as they appear. After writing, verify that the structure is preserved and the sort order is correct (see Verification).

- **When source data may contain repeated header rows or placeholder rows within the data region** (e.g., 'ITEM' appearing in column A in the middle of data), scan the full column for header-like strings matching the first row's headers and exclude them explicitly before further processing. Print a sample of the included rows and their original row numbers to verify that only genuine data rows remain.

- When computing date-based thresholds (e.g., max date, 30‑day cutoff), iterate through the column values, validate with `isinstance(v, (datetime, date))` and `try/except` for string parsing, collect only valid dates, and print a summary (count, max/min) before using the result.

- Before writing formulas that reference a previous row (e.g., running totals, carry-forward logic), print the relevant key columns (e.g., worker ID, date) for the entire range and confirm that the data is sorted appropriately and that each entity's records appear in consecutive rows. If the data is not sorted, sort it first or adjust the formula to use a lookup rather than a simple row offset.

- **Before any deletion or row/column modification, print the full data region (all columns) of the affected sheet, not just one column.** This reveals the complete layout and prevents missing data that may be affected.

- **Before any row deletion, print the full sheet content (all rows and columns) to confirm the exact data layout, including header rows, blank rows, and data rows. Verify the target answer range and the rows to be deleted.**
- **When deleting rows, inspecting only the target column (e.g., only column C) is insufficient.** Print all columns for the rows that would be deleted to confirm cross-column row integrity. After saving, re-open the workbook and print the full answer range (all columns and rows) to verify the correct rows were removed and remaining rows retain their correct data across all columns.

- Before applying logic to a range, print the first 3–5 rows of that range to confirm where actual data begins. Check for empty rows, sub-headers, or merged cells that could shift row offsets. Print the column values for the first and last data rows to ensure range bounds are correct.
- When constructing a lookup table from a reference range (e.g., columns G-H), print the full range (all rows) of the lookup table and verify the mapping for any codes that appear in the data. Do not rely on a partial preview; unexpected values beyond the initial rows can silently corrupt the lookup.


- **Before writing any code, after inspecting the workbook, systematically check:** (a) what the task expects as the final deliverable (e.g., a live formula, a static value, a chart), and (b) what currently occupies the target cell(s) — inspect the cell's value, formula text, and any error tokens (e.g., #N/A, #VALUE!) using both `data_only=True` and `data_only=False` as needed. This prevents overwriting a formula with a static value when a formula is required, or misinterpreting an error token as a blank cell.
- After diagnosing, correct the formula (adjust ranges, column indices, or references) rather than replacing the cell with a static value. Only replace with a static value if the task explicitly requires that.
- When printing column indices during header mapping, use 1‑based enumeration (`enumerate(row, 1)`) to match openpyxl’s column numbering and avoid off‑by‑one errors when referencing columns later.


- When selecting a sheet by name, use case-insensitive matching (e.g., `for s in wb.sheetnames: if s.lower() == 'target name'.lower(): ws = wb[s]; break`). If not found, fall back to the first sheet and print a warning. This guards against capitalization mismatches.
- **When a sheet contains transposed data (rows as columns) or Excel table objects**, print the table metadata (e.g., `ws.tables`) and scan both dimensions fully. Wide, transposed layouts often need normalization before joining with lookup tables. Confirm the row/column orientation matches the intended transformation logic before writing any code.
- Before writing any hardcoded normalization mapping (e.g., a dictionary mapping plural to singular forms), print all unique values in the source column (e.g., `set(ws[col][1:])`) and ensure the mapping covers every observed value. If any value is missing, adjust the mapping or use a more robust approach.

- **Before writing formulas that parse strings with fixed character positions (e.g., MID, LEFT, RIGHT based on hardcoded offsets), print the full column's values (all rows) to confirm that every value has the same length and structure. If any variation exists, use delimiter-based parsing (e.g., split on space or slash) instead of fixed offsets. After writing, test the formula on at least one row by evaluating it or checking the result cell is not None.**
- **Before writing any formula that references other cells, print the values of every referenced cell (e.g., `print(ws['F10'].value)`) to confirm they exist and contain the expected data or formulas. Do not rely on the task description's mention of helper cells; always verify against the actual workbook.**
- **Before writing values across sheets based on row position**, inspect the key column(s) (e.g., ID, S.N) in both source and target sheets. Print the first few rows of the key column to confirm whether the rows are aligned by index or need a lookup. If the task provides reference result sheets, compare a few rows of your output against them after writing to verify alignment.
- **Before writing transformation logic that modifies cell values** (e.g., string slicing, regex replacements, case changes), print the full answer range (first 5 rows, last 5 rows) and a summary of distinct values and blank cells. This reveals whether all values share the same pattern or if edge cases exist. Never assume uniformity from a small preview.
- For tasks with a clearly defined scope (e.g., a single known column and a simple transformation like string manipulation or arithmetic), you may skip full inspection of all sheets and instead inspect only the target range. However, always verify the output thoroughly after writing.

- Before summing, averaging, or other numeric aggregation on a column, print the first few rows' data types (`type()`) to confirm the values are numeric (int, float) and not datetime or text. Ensure the header row is excluded from the aggregation range.

- **If the workbook contains a sheet that appears to be a manual or expected output (e.g., 'Manual Result', 'Expected Output', 'Before and After'), inspect it as a reference before writing any code:** print all rows of both the source data range and the reference range side-by-side (e.g., actual result columns alongside expected result columns). For the reference range, use `data_only=True` and also print cell properties (e.g., whether each cell contains a formula via `cell.data_type`) to understand the expected deliverable type. Confirm row counts, column structures, and value patterns match expectations before designing the transformation. This is especially critical when the task mentions VBA or macros.

- **When writing conditional updates (only some rows get new values), first inspect the full column's existing values and decide what to do with non-matching rows (retain, clear, or set to a default). After writing, re-read the column and confirm that every cell in the answer range holds exactly the intended value, not leftover data from before.**


- **When the task uses the word 'per' (e.g., 'last date per brand', 'sum per department'), print the unique values of the grouping column and for each group the relevant data (e.g., all dates, max date) to confirm the intended per-group operation before writing any aggregation or filtering code.**
- **When the task explicitly asks to debug or correct a macro**, first extract and print the existing VBA macro code (via openpyxl's VBA support) to understand its intended behavior. Then implement that behavior in Python. Do not attempt to edit the VBA unless you have a reliable tool (openpyxl cannot edit VBA).
- **If the sheet is small (fewer than 200 rows), print all rows to build a complete picture of the data layout, including blank rows and gaps.**

- **Before writing formulas that reference specific rows described in the task (e.g., 'top three rows', 'last 5 rows'), print the data region and confirm the exact row numbers where those rows reside.** Map the task's description to actual cell coordinates before writing any formula. After writing, verify the computed values (using `data_only=True`) and ensure they are not None — if any are None, the row references are likely wrong.
- When the task involves packing data from multiple rows into a single row (or transposing rows to columns), print the full source range (all rows and columns) and the intended destination range to understand the layout and mapping before writing any code. Confirm the orientation matches the task requirements.

- If the task description mentions 'all rows' or 'dynamic', do not assume a fixed row count. Always scan the relevant column to find the true last populated row, and use that as the loop bound. After writing, verify that the output range covers all populated rows.

- **When the output sheet already exists (e.g., a template with partial data), print the entire answer range before writing.** Confirm that the existing layout (headers, columns) matches the required range exactly. If the sheet is partially empty or contains placeholder values, explicitly decide which cells to overwrite and which to preserve, rather than using a blanket loop.

- **Before performing any conditional copy or transfer between columns (e.g., copy value from one column to another only when a condition is met), print the target column's existing values for all rows in the affected range. After writing, re-read the target column and verify that rows where the source was empty retain their original pre-write values (not None unless they were originally None).**

- **When the task specifies filtering by a list of prefixes or keywords (e.g., 'start with "A, B, C"'), do not assume the list is exhaustive or that the values match exactly as described.** Print all unique values in the filter column and design matching logic that handles variations (e.g., case, extra spaces). After writing, print the distinct values in the extracted output and compare against the source to confirm completeness.
## Writing Output


- Identify the exact output sheet name from the task instructions. Create the sheet if it does not exist; do not reuse a pre-existing sheet unless explicitly instructed.
- If the task specifies an answer range with a sheet name (e.g., `'Sheet2'!A1:AG10`), create that sheet if it does not exist before writing. After writing, print `ws.title` to confirm the output is on the correct sheet.
- Before clearing any cells in the output range, copy the current values to a backup (e.g., a list of tuples) so you can restore them if the write fails.
After writing, compare the post-write values to the backup. If no cells changed, the write did not take effect; inspect why the conditions were not triggered and adjust before proceeding.
- For tasks involving lookup, match, or returning values from a column, default to writing **formulas** (INDEX/MATCH, XLOOKUP, etc.) unless the instruction explicitly says to copy values. After writing, verify that answer cells contain formulas (`cell.data_type == 'f'`), not static numbers.
- After each write operation, read back the modified cells and print their values. After all writes, read back every cell in the expected output range and verify that no required cell is None unless explicitly expected.

- After writing formulas, immediately read back those cells and verify they contain the intended formulas (`cell.data_type == 'f'`), not static values or None. If any are missing, investigate before saving.
For each formula cell, also print the formula text (e.g., `print(cell.value)`) to confirm syntactic correctness—proper quoting in INDIRECT, correct range references, and intended row-by-row structure—before relying on computed-value checks alone.
 For cumulative formulas using mixed references (e.g., `$A$2:A2`), verify that the range expands consistently across rows (e.g., from `$A$2:A2` to `$A$2:A3`).

**WARNING: Do not skip the recalc and verification step. If you call TASK_COMPLETE without re-opening and printing the answer range with `data_only=True`, the answer cells will be None and the task will fail.**
CRITICAL: After writing formulas, save the workbook, run `recalc.py`, then re‑open with `data_only=True` and read the answer cells. 

- When the same formula pattern must be placed across many rows, use a programmatic loop (e.g., `for row in range(...)`) to construct and write formulas consistently. This avoids manual transcription errors. After bulk writes, always verify the computed values via recalc and `data_only=True`.

- Save the workbook to the exact `output_path` specified in the task instructions. Do not infer or hardcode a different path.

- When iterating over cells for computation, guard against None or zero values (e.g., `if cell.value is None or cell.value == 0`) to avoid arithmetic errors.

- When performing cell-level transformations (e.g., regex replacements, string cleaning), compute the new values in-memory first. Print a sample (first 3–5 rows) of the transformed values before writing them to the workbook. Only write after confirming the preview matches expectations.
- When populating an answer range, apply the formula or value to all rows in a single loop; do not split the range into multiple separate write operations.

- When applying transformations to a specific subset of rows (e.g., a known range), iterate over that exact range (e.g., `for row in range(start_row, end_row+1)`) rather than scanning the entire sheet. This keeps operations targeted and reduces unintended side effects.

- When the task provides an explicit answer range (e.g., 'answer_position': 'Sheet1!A3:D36'), extract the sheet name and cell range. **If the task describes a sheet-wide transformation (e.g., "remove all double quotes from the entire worksheet"), apply the operation to all populated cells, not just the answer range.** Otherwise, confine write operations (formulas, values, deletions) strictly to that range. Before writing, print the range boundaries and confirm they match the task. After writing, re-read the range and verify that no cells outside it were modified (unless the transformation was global).

After writing formulas, proceed to the **Verification** section and complete all steps (recalc, re‑open, read computed values) before calling TASK_COMPLETE. Skipping verification will leave answer cells as None and cause task failure.

- For multi‑condition sorts that rely on an auxiliary ordering list (e.g., a helper list of names), structure the logic as: extract and clean source data, then branch. If the helper list is non‑empty, match rows in helper order while preserving source order; otherwise fall back to alphabetical/numeric sorting. Use a `seen` set on key columns to deduplicate and filter blanks before processing.

- When the task requires case-sensitive conditional aggregation (e.g., summing values where a column matches an exact case-sensitive string), use a SUMPRODUCT formula with EXACT and N() to handle blanks safely and avoid Python loops. Verify computed values after recalc (see Verification).


After writing any formula, immediately save, run `recalc.py`, and read back the computed values with `data_only=True`. Do not skip this step—it is the only way to confirm formulas evaluate correctly.
- When populating an answer range, compute the required number of output rows dynamically from the source data (e.g., number of input rows × number of transposed variables). Print the computed row count and verify against the target sheet's dimensions before writing. Never hard-code row limits based on a preview snippet.

- When the natural output has more columns than the graded answer range (e.g., the task asks to output from G2 but your result has 4 columns and the range only has 3), adjust the layout so all required data fits inside the graded range. For example, merge columns or place the most critical data (e.g., totals) inside the range rather than omitting them. Never place required output outside the graded range. Verify that the answer range contains computed values for all produced rows.
- When the task provides the output path as a variable (e.g., `output_path`), use that variable directly when calling `wb.save()`; do not hardcode a literal path string.

- Before clearing or overwriting cells in an answer range, inspect the full existing content across the entire intended output area. Compare with the task requirements. Only clear or modify cells that actually need to change; preserve any existing correct data. After writing, re-read the range to confirm no unrelated content was lost.


- This confirms formulas are present, but does not verify their computed results. Proceed to the **Verification** section to recalc and check computed values.

- When computing outputs for multiple search terms already listed in an adjacent column, write a single formula pattern that references those search-term cells as criteria (e.g., `SUMIFS` with `"*"&H{r}&"*"`). Use a loop to write the formula into each target row. This keeps the solution dynamic and avoids hardcoding results.


- **Before writing final output, compute the total number of result rows that would be generated. Compare this count to the answer range size (e.g., number of rows in the graded range). If the count exceeds the range, inspect what would be omitted and decide whether to extend the range, report the discrepancy, or truncate only if the instruction explicitly limits output. Always flag mismatches during verification; never silently drop rows.**

- After each write operation, print summary metrics (e.g., 'wrote N rows', 'filtered from M total source rows') and compare to the expected answer range size. This provides a quick sanity check before proceeding to full verification.

- For group‑wise ranking (e.g., largest per category), use COUNTIFS with category and magnitude conditions instead of nested IF+AND. After writing, verify by picking one category and manually checking the computed rank against sorted values.
## Verification


- Before saving, read back the target graded cells and print their values. Confirm the output matches the task requirements.
- After saving, recalculate formulas using `recalc.py`. Then re-open the workbook with `data_only=True` (and read-only mode if possible) and print the exact answer-range cells.
- Before reading the answer range, confirm that the sheet you are accessing matches the answer sheet name from the task (e.g., `print(ws.title)`). If the sheet is missing or wrong, fix and re-save.
- Printing only row/column counts is not sufficient; you must print the actual cell values of the entire answer range to detect missing sheets or empty cells. This shows the computed values, not formula text. Confirm:
  1. Values are computed data (not formula text or None).
  2. The shape matches expected dimensions.
  3. For lookup/match tasks, answer cells contain formulas (`cell.data_type == 'f'`) rather than hardcoded values.
- After any column insert/delete/move, re-read the full table including total columns. Verify moved values are in the intended cells, totals still reference the correct range, and the previously located column index still points to the intended data (re-scan header row if structure changed). Spot-check that no data appears offset from its header.
- After any row insertion or deletion, verify the full graded answer range end-to-end. Print the row count and the first and last few rows of that range. Confirm the range still contains the expected number of rows and that no required cells were shifted out or wiped. If the range is large, print the total row count and spot-check the first and last rows.
- After programmatic formatting (style copy), read back at least one formatting property (e.g., `number_format` or `font.bold`) from a target cell and print it to confirm the style applied. If copying from a source range, also print the formatting of a source cell for comparison.
- Do not declare completion until all checks pass.

- When performing multi-step aggregation, insert a verification step after data collection but before writing. Print the count and a few sample entries per bucket. If any target bucket has zero entries, stop and investigate the source data and matching logic rather than proceeding. After writing, verify that every target answer range (not just the first one) contains non-empty data where expected.
- Never rely on inspecting formula strings (e.g., `cell.value` without `data_only=True`) as the final check; always verify the computed values after recalc.

- After sorting, read back a sample of rows (e.g., first and last few rows) to verify the order is correct and no duplicate or missing rows were introduced. If the sort involves multiple keys, verify that all keys are ordered correctly and that mixed data types (e.g., string dates vs. datetime objects) are compared consistently.

- After recalculating and re-opening with `data_only=True`, print at least the first 3 and last 3 rows of the answer range. This ensures you are not relying on a spot check of only a few cells and that all computed values are present and correct.
- For scoring or normalization tasks, after recalc, confirm that the scores are within the expected range and that the min/max values map to the intended anchor points. Print a few sample values to verify the mapping.

- After any iterative adjustment or balancing logic (e.g., distributing residuals across units), read back and print the entire answer range before saving. Spot-check at least two rows (one positive residual, one negative) against constraint rows (min/max) to confirm bounds are respected, no zero cells were altered, and residuals are fully consumed. Assert that the remaining residual is zero (or < 1e-6) before saving.

- After any bulk write (e.g., copying multiple rows), read back the full output range and print the row count plus the content of the first and last data rows. Confirm the header, data rows, and total count match expectations before saving.

- After any row or column deletion, print the first row (headers) of the affected sheet to confirm which columns remain. If using substring matching, verify the exact set of removed and retained columns against the task specification.

- After any save operation (even if you wrote only static values), re-open the saved workbook and print the exact answer-range cells (or a representative sample). Compare the printed values and cell coordinates against what you intended to write; for example, if you intended to transpose values across multiple columns, print the full span (e.g., D8:G11) and verify each column contains the expected data. This catches errors in row/column deletions, data modifications, boundary misalignment, or transposition that dimension checks alone miss.
- If any computed value is None or an error, debug the formulas. If the task does not require live formulas, you may write the computed values directly after verifying their correctness.

Confirm the file exists at the exact output path and has non-zero size (e.g., `os.path.exists(output_path)` and `os.path.getsize(output_path) > 0`). 
MANDATORY: Before calling TASK_COMPLETE, re-open the saved workbook with `data_only=True` and print the exact answer range cells.  If you have not done this, stop and do it now. Do not call TASK_COMPLETE until this passes.
If the entire answer range is None after recalc, the formulas were likely never written or the condition never matched. Re-inspect the source data and the written formulas before retrying.

- After saving, verify the file exists at the exact output path (e.g., `os.path.exists(output_path)`). 
After saving, print the file size (e.g., `os.path.getsize(output_path)`) to confirm the save succeeded. Then proceed with recalc and read-back of answer cells. When verifying output, print not only cell values but also their data types and number formats (e.g., `cell.number_format`). Confirm they match the required format (e.g., `m/dd/yyyy`) and that no unwanted time components remain. Never consider a non‑zero file size alone as success; always read back the answer range.

- After writing a filtered or truncated result, inspect the last row of the expected answer range. If trailing rows are entirely blank but the task implies a contiguous data block, compact the range (delete or shift cells) so the answer range ends exactly at the last row with actual content. Confirm no empty rows remain within the range.

- If a reference output sheet exists (e.g., 'Desired Results', 'Expected Output'), after writing read back the answer range and the reference range. Print them side-by-side for at least the first and last few rows, comparing both column organization and actual cell values. If any mismatch is detected, investigate and correct before completing.


- After writing any computed value (e.g., a count, sum, or lookup result), read the cell back from the saved file and print it explicitly.

- When the output includes algorithmically generated sequences (e.g., alphabetic suffixes, incrementing IDs, or pattern-based labels), print the first 5–10 values and verify the sequence follows the expected progression (e.g., a-z, aa-az, ba-bz, ...) and does not contain runaway repetitions or gaps. Do not rely on in‑memory values alone. Confirm the value is present and correct before declaring completion.
- After re‑opening the workbook, confirm that the answer range contains only the expected data rows and no stray header rows or unintended blank groups, unless the task explicitly allows them. If any stray headers or blank rows are present, correct them before completing.
- After sorting, read back the entire answer range and check: (1) every row is either data, preserved blank, or preserved header, with no gaps or merged blocks; (2) the sort order within each data block is sensible given the column's data type (e.g., numeric-aware sort for mixed strings like 'D 14'); (3) the row count and column span match the expected answer range exactly. If the sort order is ambiguous, ask for clarification or note the assumption.

- When printing the answer range, include every cell (even empty ones) so you can visually confirm there are no unexpected gaps or blank rows. Do not print only a summary of non‑empty cells or row counts.

- After deletion based on a condition, also print key columns (e.g., grouping keys and the condition column) and verify that the intended groups were modified correctly (e.g., one fewer row per duplicate group) and that no groups that should have been untouched were altered.

After any row deletion, re-open the saved workbook and print the full answer range (all cells, not just a single column) to confirm the correct number of rows and that header/summary rows are intact. Do not rely on in-memory state or partial column printouts.

**Example readback script after saving and recalc:**
```python
import openpyxl
wb2 = openpyxl.load_workbook(output_path, data_only=True)
ws2 = wb2['SheetName']  # use the exact sheet name
for row in ws2['H2:H24']:
    for cell in row:
        print(cell.coordinate, cell.value)
```

- After any unmerge operation, re-read the entire answer range to confirm that formulas are written into the intended cells and no cells are unexpectedly empty.
- When conditional logic (e.g., IF, nested conditions) is used, after writing, spot-check at least 3–5 rows that exercise different branches (including rows that should remain unchanged, rows that get primary output, and rows that get fallback values). Compare actual cell values against expected outcomes for those specific rows.

- After saving, never rely on print statements from the write script as final verification. Always re-open the saved workbook and print the answer range again to confirm the actual saved state.

If after re‑opening the answer range contains None or empty cells, do not proceed to TASK_COMPLETE. Re‑inspect the workbook to determine if formulas were written correctly and if recalc.py executed successfully. Re‑write and re‑verify if necessary.

- For tasks involving removal of a specific character or substring, after re-opening the workbook, scan the answer range (and if the transformation was global, a sample of other columns) to confirm the character is absent. If found, re-apply the transformation and re-verify.

- When the answer range is a single row, print every cell from the first to the last column, and verify that no trailing None values exist beyond the expected data. If blanks are found, investigate whether the extraction missed cells (e.g., due to filtering out None values that should have been included based on formatting or other conditions).


- After any operation that compacts rows (e.g., removing blank rows and shifting data up), re‑open the saved workbook and print the entire answer range to confirm that all rows in the expected range are non‑empty and contiguous. No blank rows should remain within the data block.

- Compare the printed values against any existing expected output, reference sheet, or pattern described in the task. If the output does not match, debug and re-verify.

- For tasks involving conditional logic, keyword matching, or string transformations, also print the corresponding source cells for the first few rows and verify that the output is correct given the source data. This helps catch issues like leading/trailing spaces, case mismatches, or missing matches.

- After writing, before saving, print the answer range and compare the values against the intended transformation logic (e.g., expected values computed from source data) for at least the first and last few rows. Confirm the mapping is correct, not just that cells are non‑None.
## Completion Checklist

Before calling TASK_COMPLETE, confirm:
- [ ] Workbook saved at exact output path and file size > 0.
- [ ] recalc.py executed successfully.
- [ ] Workbook re-opened with data_only=True.
- [ ] Answer range printed (all cells, including empty) and contains computed values, not None or formula text.
- [ ] For formula tasks, answer cells contain formulas (`cell.data_type == 'f'`).
- [ ] If any check fails, debug and re-verify.
## Common Pitfalls


- Skipping formula recalculation and verification, leading to None values in answer cells.
- Hard-coding row/column boundaries instead of discovering them from the data.
- Overwriting pre-existing values in the answer range without inspection.
- Declaring completion without reading back the written output range.
- Skipping inspection of an attached example file that demonstrates the desired output pattern.
- Writing static values into answer cells when the task expects dynamic formulas (especially for lookups).
- Acting on truncated previews without inspecting the full data.
- **Assuming structural changes are correct:** Column insert/delete can break alignment or total formulas; always verify.
- **Silent style-copy failures:** `copy(style)` may not apply; always inspect a formatting property after writing.
- **Row deletion:** Always iterate in reverse (`for r in range(ws.max_row, 1, -1)`) to avoid index shifting. Validate cell types (e.g., `isinstance(cell.value, str)`) before string methods like `.startswith()`. After deletion, re-open the saved workbook and print the full sheet content using `iter_rows(values_only=True)`. Confirm that the data starts at the expected row (usually row 1) and that there are no gaps or shifted rows. Verify that `ws.max_row` equals the expected number of kept rows.

- Verifying only formula text without recalculating and checking computed values, leading to empty answer cells.
- Writing output to `wb.active` without first printing `wb.sheetnames` and confirming the target sheet, causing formulas or values to land on the wrong sheet and the graded range to appear empty (all None).

- Sorting with inappropriate comparison type or unstable multi-level sort. Before sorting, inspect a few cell values to decide whether numeric or string comparison is appropriate, and use type-aware keys. When sorting by multiple keys, apply sorts from least to most significant key to maintain stability.

- Writing update loops without reading back the modified range to confirm changes took effect, leading to silently wrong results.

- Saving the workbook without first reading back and printing the final answer range, leaving errors in iterative adjustments (e.g., unconsumed residuals) undetected.

- Saving the workbook and immediately declaring TASK_COMPLETE without re-opening and reading back the answer range, leading to undetected mismatches (e.g., values written to a single column instead of transposed across multiple columns).


- Attempting to edit or execute embedded VBA/macro code to fix a spreadsheet issue. When the task describes a macro's faulty effect, do **not** try to modify the VBA. Instead, inspect the current data, compute the intended outcome, and implement the correction directly in Python using openpyxl. Verify the output against the graded range before completion.

- Writing transformation logic based on assumed cell types (e.g., `isinstance(v, str)`) without first printing the actual `type()` of a sample of cells, leading to untested branches and silent failures.
- Declaring completion after seeing a non‑zero file size without re‑opening the workbook and printing the answer range's values, types, and number formats to verify they meet the task's format requirements.

- Focusing on secondary formatting (e.g., number format, alignment) before ensuring the answer cells contain the required data (e.g., fixing a broken formula). Always address the primary task objective first, then apply formatting. After any write, verify that answer cells hold actual values, not None/empty, unless the task explicitly expects empty outputs.

- Ignoring existing cell formatting (fills, colors) when the task description uses them as a condition, leading to computing a result based on raw values instead of the highlighted cells.

- Writing conditional formulas that compare against a literal string (e.g., 'error') without inspecting the column's actual values, leading to mismatches (e.g., '#N/A' vs. 'error').

- Writing formulas in a loop where each iteration inadvertently overwrites the previous cell's formula (e.g., due to incorrect indexing or logic), leaving only the last iteration's formula. After any loop that writes formulas, read back the entire target range and print the formula text for each cell (e.g., `for row in range(...): print(ws.cell(row=row, column=col).value)`) to confirm all cells contain the correct formulas before saving.

- Cryptic import or environment errors (e.g., circular imports, unexpected file paths in tracebacks). Before retrying, inspect the error for unexpected file paths (like `/tmp/inspect.py` interfering with standard library imports). Remove or move the offending file and execute from a clean working directory. Do not blindly retry without cleaning up the environment.


- Blindly rewriting a formula without first evaluating the existing formula's computed result (using `data_only=True`), leading to a replacement that also produces None or empty output. Always diagnose before fixing.
- When the task asks to 'create VBA code' or 'write a macro', do **not** attempt to write VBA. Instead, compute the required result directly in Python and place it in the target cell. The grader expects the computed value, not code or a comment.
- Writing sort logic without first mapping the exact positions of data rows, blank rows, and header rows, and without verifying the output structure after sorting.

- Printing a summary (e.g., 'found 19 remaining 4') instead of the full answer range (including empty cells), leading to undetected gaps or missing data.
- Writing formulas that produce empty results because source ranges are misaligned; after recalc, if any answer cell is None, print the formula text and verify the referenced ranges against the actual data layout (row offsets, column letters) before proceeding.

- Using boolean criteria (e.g., `COUNTIFS(..., FALSE)`) without checking whether the target column contains boolean values or string representations like `'False'`. Always inspect the actual data type and exact content before writing criteria.

- Writing deletion scripts without first inspecting the sheet to confirm the exact row range, column headers, and sample data values, leading to hardcoded assumptions and off‑by‑range errors.

- Writing row-relative formulas (e.g., referencing the cell above) without first inspecting the data order and grouping, leading to incorrect carry-forward when the data is not sorted by the expected key.

- Failing to add explicit guards for protected rows/columns specified in the instructions. When the task names specific rows or columns that must not be altered, add a skip condition in the loop (e.g., `if row in (2,9): continue`) and verify those rows after execution.

- Writing formulas that produce text and skipping recalc/verification because the formulas 'look correct' — always re-open and check computed values regardless of output type.

- When deleting rows in reverse, document the reverse iteration with a comment (e.g., `# iterate in reverse to avoid index shifting`). This makes the intent explicit and prevents accidental reordering.

- After deletion, printing only a single column and assuming the full answer range is correct. Always re-open and print the entire answer range (all columns and rows) to verify row count and content.

- When deleting rows based on a condition, inspect the full row (all columns) to determine blankness or match criteria, not just a single column. Always iterate in reverse order (e.g., `for r in sorted(rows_to_delete, reverse=True)`) to avoid index shifting.

- **Assuming all sheets before a certain index are data sheets to process without verifying their content.** Always inspect each sheet's headers and data to confirm they are the intended sources. Never rely solely on a positional slice like `wb.worksheets[:idx]` without checking each sheet's actual structure and relevance.
- Assuming the task description's cell references are accurate without inspecting the workbook; always verify the existence and content of referenced cells before writing dependent formulas.

- Declaring TASK_COMPLETE after writing formulas without re‑opening the saved workbook and printing the answer range to confirm formulas are present and evaluated. If the answer range is None or empty, the formulas were not saved or recalc was not performed; do not complete until this is fixed.

- Assuming the transformation is limited to the graded answer range when the task describes a sheet-wide operation (e.g., "across all columns", "in the entire worksheet"). Always read the task description carefully and apply the operation to all populated cells. Verify that no cells outside the graded range still contain the target pattern.
- **Copying rows without preserving formulas:** When reordering or copying cells that may contain formulas, inspect the source cells’ `.data_type` (or check if the value starts with `'='`). Copy the formula string (e.g., `cell.value`) rather than the computed result. After writing, verify that formula-bearing cells still contain formulas (`cell.data_type == 'f'`) and not `None`.
- **Lookup key collisions:** When building a mapping (e.g., a dictionary keyed by one or more columns), verify key uniqueness: print the number of unique keys vs. total rows. If duplicates exist, handle them explicitly (e.g., use a list for values) to avoid silent overwrites and data loss.

- **When the task asks to 'create VBA code' or 'write a macro', do **not** attempt to write VBA.** Instead, compute the required result directly in Python and place it in the target cell. The grader expects the computed value, not code or a comment. Similarly, when asked to debug or correct a macro, first inspect the existing macro code to understand the intended transformation, then implement it in Python; do not attempt to edit the VBA unless you have a reliable tool (openpyxl cannot edit VBA).

- **Applying a transformation to a range without first checking if the first row contains headers**, leading to header destruction. Always inspect the first row of the target range and skip it if it's a header (unless the task explicitly requires processing headers). After writing, verify that header cells remain unchanged.

- Inserting rows (or columns) without reading back the full answer range to confirm the correct number of empty rows were inserted and no data was shifted incorrectly. After any insertion, re‑open the saved workbook and print the entire answer range, including the newly inserted rows, to verify the operation's effect.

- **Writing conditional updates without inspecting the column's existing values, leading to unintended carry-over of prior data.** Always inspect first, and after writing verify every cell in the answer range.


- **Misinterpreting 'per X' instructions as a single global operation** (e.g., taking the overall max date instead of per-brand max). Always inspect per-group data before writing aggregation code.
- **Performing a multi-key sort without first printing the parsed sort keys alongside the original values to confirm that mixed data types (e.g., string dates vs. datetime objects) are handled consistently.** After sorting, always read back the first few rows to verify the order matches all sort criteria.
- **Clearing or overwriting a destination sheet that already contains example rows without inspecting the example's structure, data types, and formatting.** Before clearing, inspect every row of the example, compare to the task requirements, and after writing, verify that formatting is consistent across all rows in each column.

- **Write-then-overwrite verification:** After overwriting cells with formulas (especially if you previously wrote static values), do not rely on in-memory state or formula text checks alone. Always recalc and re-open with `data_only=True` to confirm the grader sees the correct evaluated values, not formula code or None.

- **Ignoring the core mechanism when a macro is requested.** If the instruction says 'create a macro that does X,' you cannot write VBA with openpyxl, but you must still implement the described conditional logic in Python. First, inspect all referenced inputs (e.g., cell I2, column B) to understand the conditions, then code the exact behavior (e.g., conditionally delete rows based on those inputs). Do not replace the macro with a generic operation that ignores the specified conditions.

- **Applying a blanket 'remove all blank rows' to structured data with intentional separators.** Before deleting blank rows, inspect the data layout to identify whether empty rows serve as section headers or separators. After deletion, re-open the workbook and verify that the structure (including any intentional gaps) matches expectations. Do not assume that compacting all data is the correct outcome.