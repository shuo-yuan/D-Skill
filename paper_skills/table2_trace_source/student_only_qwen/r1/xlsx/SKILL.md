---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow


0. **Prepare Output File**

0.5 **Limit Inspection and Write Early**: Perform only enough inspection to understand the data layout and required transformations. After the first inspection that reveals the structure, immediately write a Python script that implements all required changes, saves the workbook to the exact output path, and prints a summary of changes. Do not perform more than two inspection-only commands without executing a write attempt. After each write attempt, confirm the output file exists using `ls -la` or `os.path.exists()` before continuing. A partial solution that can be refined is always better than no output file.
If you have not yet saved an output file, you must attempt to write one immediately after the next inspection. Never end the task without an output file.

If you are unsure how to proceed after inspection, still attempt to write a script that makes progress; never stop without producing an output file.
: Determine whether the task requires creating a new workbook or modifying an existing one. If the task describes modifying an existing file (e.g., sorting data in a worksheet, adding columns), load the original workbook using `openpyxl.load_workbook()`. If the task requires a new workbook, create it and save it at the required path. In both cases, verify the file exists on disk using `os.path.exists()` or `ls -la` before any deep exploration. This ensures a deliverable exists early and preserves existing structure when required.

1. **Inspect**: Read all sheet dimensions and data content thoroughly before any manipulation. Trace example logic manually. Inspect source data and target range (including headers and boundaries).
2. **Write**: Write formulas or computed values. Locate columns dynamically by scanning header rows for label matches; never hardcode column indices.
3. **Verify**: After saving, re-open the workbook and verify the answer range matches expectations (see Verification section). Do not call TASK_COMPLETE until this check passes.

- **VBA/Macro check**: If the task mentions “VBA”, “macro”, “debug my code”, or asks for code, produce the corrected VBA/macro code text as the answer and save the workbook as `.xlsm`. Do not perform the operation imperatively via Python; the deliverable is the code itself, not the result of running it. Before writing, inspect the workbook for existing macros (e.g., `wb.vba_archive` or `.xlsm` format) to understand the current VBA project and any code that needs debugging. If the task describes a broken macro but does not explicitly ask for the corrected macro code, still inspect the macro to understand the intended logic (grouping, thresholds, data handling) before implementing any fix in Python; the macro may encode critical constraints that a naive implementation would miss. Also inspect any referenced cells (e.g., I2) to understand conditional logic and encode it in the macro. After saving, verify the macro is present in the workbook before completing.

- **Verify**: After saving, re-open the workbook with `data_only=True` and read back the answer range. If any cell contains None or a formula string (starting with '='), the output is invalid. Recompute values in Python and rewrite before TASK_COMPLETE.
## Inspection


Start by printing all sheet names and a full dump of all non-empty cells with coordinates, values, and types for every sheet. This comprehensive initial scan, proven successful in practice, provides a complete map of data, headers, and example outputs, reducing the chance of premature assumptions before any manipulation.
Always access sheets by name (e.g., `wb['master']`) after confirming the sheet exists in `wb.sheetnames`. Do not rely on `wb.active` unless the task explicitly states to use the active sheet. Then,
Before any modifications, load all sheets and perform a full cell-by-cell read of the input workbook. Print every cell's coordinate and value (or at least all non-empty cells with coordinates) to understand layout, headers, empty cells, and boundary rows/columns.
Include the Python type of each cell's value (e.g., `type(cell.value)`) to catch type mismatches (int vs str, None vs empty string) before they cause downstream errors.
If tool output is truncated before reaching the last row, explicitly re-query the missing rows rather than proceeding with incomplete information. Never assume the unseen rows are empty or follow the same pattern as visible rows. Print source range dimensions and first/last rows. Confirm that lookup keys exist in the data, that date/number formats are compatible, and that the target range aligns with the intended mapping. Note which cells already contain data, which are empty, and whether the grader expects formulas or computed values. Do not assume boundaries from a single glance at labels. Manually trace one or two representative examples through the instruction's steps to catch edge cases or ambiguities before coding.


- If the answer range already contains some values (e.g., from a reference implementation or partial solution), verify that your computed results match those values before applying the approach to the full range.
When pre-existing values exist in the answer range, compute your values independently first, then compare them cell-by-cell with the pre-existing values. If any differ, pause and diagnose the discrepancy before overwriting — the pre-existing values may encode the correct interpretation or expected output format. Only overwrite after confirming your computed results are consistent with the existing data.
- If the answer range already contains values, examine the cell content type (formula string, number, text) and consider the task's phrasing. Phrases like 'How can I look up...' typically ask for a formula, not a computed value. Only overwrite with a different content type after confirming that your approach matches the expected output type.
When modifying existing formulas, diagnose the core problem from first principles: understand what the formula attempts, identify why it fails (e.g., function limitation, incorrect range), and explain the limitation before writing a replacement. Carry this analysis into verification to confirm the new logic handles the identified edge case.


Print the formula text, cell types, and any conditional logic across a sample of rows to understand the full structure before writing a replacement.

Identify the exact output cell ranges that will be graded (e.g., from the task's `answer_position` field). Print these ranges and confirm they exist as writable target areas.
Confirm the exact string values (e.g., 'Sick Day', 'Overtime') you will need for filtering or aggregation, and ensure they match the data exactly.

- Identify which rows are data rows (to be processed), which are blank/separator rows, and which are constraint/summary rows (to be left untouched). Confirm the exact range of rows that need processing and those that must remain unchanged.
When locating columns by header labels, use case-insensitive matching (e.g., `header.strip().lower()`) and print the found column indices before relying on them.

- When you need a list of columns to process (e.g., all variable columns after fixed key columns), programmatically extract the list from the header row rather than manually typing column names. Print the extracted list and confirm it matches the expected count before using it. This avoids misidentification due to case or whitespace differences.
- When the task references a column by letter (e.g., 'Column BN'), do not assume the column index from alphabetical ordering alone. Verify the mapping by either: (a) printing `openpyxl.utils.get_column_letter(index)` to confirm the index resolves to the expected letter, or (b) inspecting the header row at that column index to confirm it matches the task's column reference. Print the confirmed mapping before writing any values.
- Before writing any formula that uses a column's values (e.g., COUNTIFS, IF, SUMIF), print the unique values and their Python types (using `set()` and `type()`) for that column to confirm that your formula's constants and comparisons match the actual data types and values.
For tasks with a clear target range, print all non-empty cells in that range and adjacent columns/rows to ground the approach in actual spreadsheet state.
- Identify any pre-existing values in target cells that may interfere with the solution (e.g., need clearing before writing new data).

- When determining the exact range of data rows (e.g., for deletion, insertion, or formula application), scan the relevant column(s) from the first possible row to `ws.max_row` to find the first and last non-empty cells. Print these boundaries before acting to verify they match the task's expectations.
- When adjusting a formula's range boundary (e.g., to avoid self-reference), always inspect the full original range to confirm what data it covers. Print all non-empty values in that range (not just a sample) and verify the last non-empty row. Only then adjust the boundary, and document the evidence for that decision in the trace.
- If lookup data contains duplicate keys, print all duplicates and their associated values before choosing a merge strategy. State the chosen strategy (first-match, last-match, all-matches, etc.) and justify it against the instruction's language.
- When writing formulas that reference sheets by name (e.g., INDIRECT, `=SheetName!A1`), extract the full list of values from the source column and compare them side-by-side with `wb.sheetnames`. Confirm that every source value has a matching sheet and that no extra rows are processed. Print the comparison before writing any formulas.

- For the answer range, print all cell values and note which are empty, which contain formulas, and which contain static values. Determine which cells need to be populated and whether any existing data must be preserved.

- When you locate a header row that marks the start of data, always continue scanning to `ws.max_row` to confirm the full extent of data below it. Print the last row number that contains data, even if the sheet appears empty beyond the header. This prevents accidental truncation when rows are deleted later.

When a reference sheet (e.g., 'Manual Result') is present, inspect it thoroughly before writing any output. Print its full content and structure, and use it to infer the required extraction or transformation logic. Cross-check your planned approach against the reference to ensure alignment in count, order, and values.

If the task provides the exact answer range and the initial cell content (e.g., via `spreadsheet_content`), you may skip the full workbook inspection and proceed directly to writing the transformation. After saving, verify the output by reading back the saved file as described in the Verification section.

- When a formula depends on specific columns, print all values in those columns (including empty cells) to identify edge cases and data patterns before writing the formula.
- Always perform at least two inspection passes: first a broad overview of the first few rows of each sheet, then a deep scan of all relevant columns to their full extent (to `ws.max_row`) to confirm boundaries and data patterns before acting.

- Before writing any transformation logic, explicitly list the header row(s) and map all task column references (e.g., 'Column N') to the actual header names found in the data. Verify that the columns you plan to modify match the intended data semantically, not just by index.

- Perform a systematic reconnaissance pass: print sheet dimensions, list all non‑empty values in each relevant column separately, and confirm header names before writing any output code.

- Before writing, determine the deliverable type: is the task asking for code/macro text, computed data, formula strings, or a combination? Check the instruction wording and the answer_position range. If the answer_position is a cell range with data cells, the grader likely expects data values; if it's a single cell or a code module, they may expect code. Explicitly state your interpretation and reasoning before executing. After writing, confirm the answer range holds the artifact type the grader expects.

- When the task requires continuing a sequence or pattern (e.g., appending letters to numbers), inspect each cell in the target range to determine whether it already contains a valid instance of the pattern. Treat such cells as the current state to continue from, not as generic non-blank cells. Print the last valid pattern value and its row to anchor the continuation logic.
- When the task involves filling or modifying values across a dataset, dump the entire relevant column(s) — all rows — to confirm the complete pattern of blanks, existing values, mixed types, and any pre-existing partial solutions before designing the transformation logic.
- When the task involves formatting (fonts, fills, number formats), inspect the existing styles of relevant cells (font name, size, fill color, number format) and print them before writing any modification code. This ensures you can reproduce or modify styles as instructed.

- **Before writing a deletion or filtering script based on a column's values**, print the unique values and their types for that column across all relevant sheets (using `set()` and `type()`). Compare these to the filtering condition mentioned in the instructions and to any code snippets provided. State explicitly which condition you are implementing and why. This prevents acting on an ambiguous or contradictory specification.
- Map column indices to letters and print the full content of all relevant columns row-by-row (not just a sample) to understand data layout, value distributions, and edge cases before writing any logic.


- When building a mapping from categorical values to output columns (e.g., allowance types to columns), print all distinct values from the source column and confirm that your mapping covers every value. After writing, verify that each distinct value was mapped to a non-zero count or value, and that no input went to 0 unexpectedly.
- **Proven successful**: Always perform a full reconnaissance of every sheet (including any 'Expected', 'Template', or reference sheets) before writing transformation logic. This systematic inspection habit prevents downstream errors.

- **Failed inspection**: If any inspection command fails (e.g., file not found, path typo), fix the error and re-run the inspection before writing any processing code. Never proceed to write logic without a successful inspection of the actual file's structure and content.
- **Hidden sheets**: When loading a workbook, check for hidden sheets (e.g., using `wb.sheetnames` which includes hidden sheets) and inspect them as thoroughly as visible sheets. Hidden sheets often contain reference data or expected outputs that are critical for the solution.
- **When the task is to fix a formula in a specific cell (e.g., F7)**, inspect only the cells that directly affect that cell (precedents) and write the corrected formula immediately. Avoid scanning the entire workbook unnecessarily.
- Before applying any row-wise transformation to a column, scan the first few rows to distinguish headers from data rows. If a header exists, explicitly exclude it from the transformation range or conditionally skip rows whose values don't match the data pattern. After writing, verify that header cells in the output still contain their original descriptive values, not partially truncated or altered.
- When the task provides an explicit answer range (e.g., C1:C6066), verify that the range boundaries align with the actual data extent. Use `ws.max_row` and spot-check the last few rows in the column to confirm the range covers genuine data, not empty cells or an arbitrary cutoff. If a discrepancy exists, decide explicitly whether to follow the stated range or the data extent, and document that decision. Never assume the grader's stated row limits match the file's contents.
**Proven successful**: Before writing any formula or transformation, print the header row, a sample of source column values (including their types), and the existing values in the target range. This confirms data format, layout, and any pre‑existing content that may affect the solution.

**Proven successful**: Print the data shape, column names, and first/last rows of each relevant sheet to confirm structure before writing any transformation logic.


- **Header check in answer range**: When the answer range includes the first row, inspect its content to determine if it is a header (e.g., a column name like 'data'). If it is a header, skip transformation for that row unless the instruction explicitly demands processing headers. Print the first row values and explicitly decide whether they are headers before writing any transformation.


- **When fixing formulas, inspect the full region surrounding the answer area**: before modifying any formula, print the formula text and the values of all precedent cells (using `data_only=True` if needed) to understand dependency chains. Identify which cells reference which, and confirm that your planned replacement addresses the correct cells and follows the existing data patterns.
**Proven successful**: After inspecting all sheets, explicitly compute and print the intermediate logic (e.g., Counter of candidate values, list of matching rows) and validate that the intended operation matches the actual data before writing any output.

- **Inspect entire answer range for pre-existing patterns**: When the answer range already contains some values (even partial), inspect every cell in that range — not just the first few rows — to understand the pattern, gaps, and any partial examples. Do not assume the pattern from the first few rows applies to the entire range. Print the full answer range before deciding fill logic.

- When a threshold-based condition is given (e.g., 'if the sum of column D is less than 10'), compute the relevant metric from the actual loaded data and confirm the condition holds before proceeding. Print the computed metric and the condition check.

- **Dynamic range requirement**: If the task explicitly states that the process must handle all rows dynamically without a fixed range, always compute the last data row from the actual data (e.g., the last non-empty cell in the source column) and use that as the loop boundary. Do not rely on the `answer_position` metadata for the row count; it may be a hint, not a constraint. After processing, verify that the number of rows modified matches the number of rows with data in the source column, and confirm no data beyond the expected range was left unprocessed.

- **Inspect output sheet fully before writing**: Before writing to any output sheet, print its full contents (all non-empty cells) to understand existing data, headers, and row alignment. Explicitly decide whether to preserve, overwrite, or extend existing content, and ensure your write operation aligns with the existing structure. Do not assume the output sheet is empty or matches your planned write; verify its actual state.
## Writing Output


Determine whether the task expects formula strings or computed values. If the task asks to “write a formula to…”, “how can I look up…”, “provide the formula text”, or explicitly mentions spreadsheet functions (IF, VLOOKUP, etc.), write the formula as a string. Only if the task explicitly asks for computed values (e.g., “calculate the result”, “what is the value”) should you compute in Python and write the value. When uncertain, inspect the answer range for pre‑existing formulas or values to infer the expected type. Note: openpyxl does not evaluate formulas; if you write formula strings, the grader will read the formula text, not computed values. Ensure the grader expects formula text before writing formulas. 


Before writing any values, inspect the target range and its immediately adjacent cells (one row above, one column left/right, and a few rows beyond the expected end). Print their contents to confirm whether pre‑existing data, formulas, or formatting exist. If the range is not empty, decide whether to clear it first or adjust placement.
**Before writing to any cell, read its current value. If it is non‑empty, compare with your planned value; if they differ, diagnose the discrepancy before overwriting.**


When writing formulas:
- Determine whether the task requires formulas (to be preserved as formula strings) or computed values. If formulas are required, write them as formula strings and ensure the library does not evaluate them inadvertently. If computed values are required, ensure the library evaluates them; if it does not evaluate automatically, compute values in code and write them directly.


**openpyxl does not evaluate formulas.** If the task requires computed values (as most do), never write formulas expecting them to be calculated later. Always compute the values in Python and write them directly. Only write formulas when the task explicitly asks for formula strings.
- **Before writing a formula that references other cells (especially cells that themselves contain formulas), load the workbook with `data_only=True` and print the actual values of those precedent cells. Confirm they are not `None`, errors, or unexpectedly blank, and that they match expected data types. Only then write and verify the formula.**

If you accidentally write formula strings, you must replace them with computed values before the final save. Never leave formula strings in the answer range unless the task explicitly asks for formula text.
- After writing a formula, recalculate the workbook (e.g., open with `data_only=True` or save and reload with formulas calculated) and read back the cell's calculated value. Confirm it is a concrete number, string, or date, not `None` or an error.

- If the read-back value is `None` or a formula string, compute the value in Python and write it directly.
- Never hardcode data ranges without first inspecting them. Write only to cells that need values, preserving existing data and empty cells where appropriate.
- When inserting or deleting rows in a loop, iterate from the bottom upward (e.g., `for row_idx in range(max_row, min_row-1, -1):`) to prevent index shifting. Confirm the start point with `ws.max_row` and log each operation for traceability.

- Before writing formulas, inspect the data layout for natural groupings (repeated labels, blank separator rows, subtotal rows). If the task asks for a calculation per group, ensure formulas respect those groups rather than applying a uniform formula across all rows. When a formula repeats identically across rows, pause and verify that identical output across rows is intended—cross-check with existing per-row data or formulas elsewhere in the sheet.

- When writing formulas that will be applied to multiple cells (across columns or rows), first inspect any existing formulas in those cells to understand how references change (relative vs absolute). After writing, read back the formula strings (not just values) from each cell and verify that each cell's formula references the correct input cells for its position, not a single hard-coded reference for all.
- If the instruction is ambiguous about whether formulas or computed values are expected, default to writing computed values (evaluated in Python) rather than formula strings. openpyxl does not evaluate formulas, and the grader will see `None` for unevaluated formula cells. Only write formula strings when the task explicitly asks for them. After writing, verify that the cell contains a concrete value (not a formula string or `None`) unless formulas are explicitly required.

- **Before writing any values to the answer range**, read and store the current values of all cells in that range and any adjacent boundary rows (e.g., TOTAL rows, subtotal rows). After writing, compare the stored snapshot with the new values to confirm that only intended cells changed and that boundary rows retain their original values unless explicitly instructed otherwise.
- Before deleting rows based on a column's blankness (e.g., deleting rows where Column A is empty), inspect multiple columns — not just the trigger column — to confirm that the rows flagged for deletion are truly empty across all columns relevant to the task. Print row content for columns B through the last column for every flagged row to avoid accidental data loss.

- When constructing a formula that uses a function in a novel way (e.g., wrapping a range with a function that may not accept arrays), first write the formula to a single cell, recalculate, and verify the computed value is a concrete number/string/date. Only then apply the validated formula to the full range.

When writing a filtering or extraction rule, test it on a small subset of the source data first. Print the raw values and the rule's decision (keep/exclude) for each tested row, including edge cases such as zero, negative numbers, and boundary values. Confirm correct behavior before applying to the full dataset.

- Combine data loading, extraction, writing, and verification in a single script. Print the full answer range in a structured format immediately after saving to enable at-a-glance confirmation without requiring a separate read-back step.

- Before writing computed values to the answer range, perform a dry-run trace of the algorithm using actual workbook data. Print intermediate decisions and the final expected result, then compare against the values you plan to write. If they differ, pause and diagnose before saving.
- Build in-memory lookup structures (dictionaries, sets) from workbook data before processing rows, rather than performing repeated cell-by-cell lookups. Print the lookup dictionary contents and at least one processed row's intermediate steps (split parts, lookup results) to confirm the key structure matches expectations before writing output.

- When deleting rows based on grouping logic (e.g., duplicates), before deletion, verify each candidate row is truly part of a multi-row group: print all rows in the group and confirm group size > 1. If a group has only one entry, skip deletion for that group to avoid IndexError and accidental deletion. Print the full record for every deletion candidate and cross-check against raw data to ensure no unintended rows are flagged.
- Preserve original row positions when the answer range is a fixed address span (e.g., B2:O42). Do not compact the sheet by deleting rows and shifting data upward. Instead, clear the cells of deleted rows in-place (set values to None or empty string) to keep original row numbers. If you must delete rows, verify that remaining rows still occupy their original row numbers and that `ws.max_row` equals the expected upper bound of the answer range. After any deletion, explicitly check that the answer range's `max_row` matches the task's specification.
- If the task mentions 'formula' but the answer range already contains hard‑coded values (e.g., True/False as seen in the prompt's spreadsheet_content), compute the values in Python and write them directly, as the grader likely expects computed results, not formula strings.

- When the task specifies multiple output cells (e.g., 'Output in H10, H20, H24'), extract the exact cell addresses verbatim and write them down as a checklist. Map each computation result to its target cell before writing. After writing, read back the value at each specified address to confirm the mapping is correct.

- When the user provides a malformed formula (e.g., garbled syntax, missing operators, ambiguous structure), isolate the intended logical condition and arithmetic, and construct a syntactically correct formula before writing. Do not copy the garbled text verbatim; translate it into a valid expression that captures the intended meaning.

- **Before writing any formula that references another sheet**, inspect every sheet named in the task (headers, key rows, and exact cell values involved in lookups). Build formulas on confirmed structure, not assumptions about layout or column positions.


- **Process only data rows, preserve empty cells**: When processing a column that contains both data and empty cells, first enumerate which rows have non-None values. Only apply transformations to those rows. After writing, verify that empty cells remain None (not empty string) and that only data rows were modified.


- **VBA/Macro deliverable**: If the task asks for VBA/macro code, produce the code text and save as `.xlsm`; do not execute the operation via Python. Verify the macro is present in the workbook before completing.

- **Preserve existing formatting when required**: If the task instructs to preserve formatting (e.g., 'Don't change any formatting'), before writing, store the formatting properties of every cell in the target range (e.g., `cell.number_format`, `cell.font`, `cell.fill`, `cell.alignment`). After writing values, re-apply the stored formatting to the same cells, then verify by reading back a sample of cells' formatting properties.

- **After writing formulas via a loop**, print the formula text from the first, middle, and last cell of the range. Confirm that row-dependent references (those without `$` on the row) actually vary per row. If any are identical, fix the formula generation (e.g., use f-strings to embed the correct row number) before proceeding.


- **Keyword matching**: When classifying cells by keyword presence, convert both the cell text and keywords to lowercase (or a consistent case) and use substring containment (e.g., `any(kw.lower() in str(cell.value).lower() for kw in keywords)`) to ensure case‑insensitive partial matches. After writing, spot‑check a few rows to confirm expected matches and non‑matches behave correctly.


- **Confirm target sheet structure before writing**: Even when a target sheet appears empty or has minimal content (e.g., dimensions A1:A1), read and print the first several rows to determine whether a header row exists. Decide explicitly whether data should start at row 1 or row 2, and print that decision before writing. Never assume an empty-looking sheet has no headers.

- **Conditional transfer with None guard**: When transferring values from one column to another based on a condition (e.g., 'when present', 'if exists'), use an explicit `is not None` guard on the source cell to avoid overwriting the destination cell with `None`. After writing, spot-check rows where the source was empty to confirm the destination still holds its original value.
## Verification


**CRITICAL: After saving, verify the output file. If the task expects computed values (not formula strings), re‑open with `data_only=True` and confirm every graded cell contains a concrete value (not None or a formula string). If the task expects formula strings, re‑open without `data_only` and verify that the cells contain the correct formulas. Do not call TASK_COMPLETE until all graded cells meet the expected type.**


- **Never trust script print output alone.** Print statements reflect in-memory objects before they are serialized to the file. Values can change type during serialization (e.g., strings becoming tuples). After every save, open the output file and read back the actual cell values from disk. Only the file contents — not script logs — represent what the grader will see. Do not call TASK_COMPLETE until you have confirmed the saved file's answer range matches expectations.

- After every save, immediately reload the workbook and read back the cells you intended to write. Also print the full graded answer range to confirm writes took effect, that the range matches the specification boundaries exactly, and that no unintended empty cells exist. This catches save failures, path mistakes, or accidental overwrites.
- Open the output workbook with `data_only=True` and confirm that the graded cells contain non‑None, non‑formula values. If any cell contains a formula string or error, recompute the value and write it again.


- When using openpyxl, formulas will not be evaluated. If you wrote formulas and the computed values are `None`, you must compute the values in Python and write them directly—do not rely on the formula to produce a value after saving.
- Independently read back the exact graded cell(s) from the saved file, printing both the cell coordinate and its value. Compare this to the instruction's required output location (e.g., `'B'!F4`) to confirm correctness.
- Execute at least one explicit cross-check: pick a sample output cell, trace it back to the input data it depends on, and confirm the logic holds (e.g., verify that both source cells actually contain the same value if the output claims a match).
- **Spot-check arithmetic with manual calculation**: When performing arithmetic across multiple columns (e.g., summing per group), after writing, manually compute the expected value for one representative group using the source data and assert that the output cell matches. This catches off-by-one indexing errors early.
- If the task provides example cases with expected outcomes (e.g., in the prompt or spreadsheet_content), after writing, verify that your output matches those examples exactly. For formulas, compute the formula's result on the example cells and compare.
- Verify the answer range boundaries: print the row count and cell values in the exact `answer_position` range, and confirm that the last row number matches the expected end of the answer range (e.g., check `ws.max_row` equals the last row number of the answer range). Do not rely on printing the entire sheet; confirm the boundary explicitly.
- If a reference/expected sheet or column is provided (or if the task describes a relationship like 'column B should match column B in ITEMS'), perform a programmatic comparison: iterate through both ranges row-by-row, compare values, and report any differences. If no reference exists, at minimum verify that the output dimensions and key structural properties match the specification exactly.
- Reject any deliverable where a graded range contains `None` or an error value.

- After writing formulas, read back the **entire graded answer range** and surrounding cells using `data_only=True` to avoid reading formula strings.
 If formulas are required, also read back the formula strings (without `data_only`) and verify that each cell's formula uses the correct relative/absolute references for its position, not a single hard-coded reference for all cells in the range. Print every cell, confirm all cells contain values (not `None`), and verify that the cell content matches the requirement: if formulas are required, cells must contain formula text; if computed values are required, cells must contain concrete numbers/dates, not formula strings or errors. If any cell is unexpectedly empty, investigate and add missing formulas or values before completing.

- After writing, compare the answer range's pre‑execution snapshot to the post‑write state, printing all cells in the exact graded answer range to confirm only intended cells changed and the surrounding structure (headers, blank rows, subtotals) remains intact. Also verify that rows outside the processing range (e.g., constraint/summary rows) still contain their original values and no extra rows were skipped.
- When a task requires clearing or setting formatting (background colors, fonts, borders), after applying the change, read back the formatting properties (e.g., `cell.fill.start_color.rgb`, `cell.font.color.rgb`) for a sample of cells, including those that originally had formatting, and confirm they match the expected state.


- When a task specifies a column range to act on (e.g., 'columns F to M'), cross-check the phrase against the graded answer range. If ambiguous, inspect a few rows of the source data across the full graded range before writing the condition. After writing, sample edge rows (one that should be kept, one that should be deleted) and print their full graded-range values to confirm no column was mistakenly omitted.
- After any row/column deletion or filtering, reload the workbook and verify the graded range: print the values of the answer range (first 5 and last 5 rows) and confirm that only the intended rows were removed, the remaining rows satisfy the task's condition, and the row count matches expectations. Compare against a pre-deletion log of row classifications and deletion list. If any row violates the condition, fix the logic before completing.
 After any row insertion or shifting operation, reload the workbook, re‑run the detection logic on the modified sheet, and verify that the intended rows were affected and no unintended rows were altered. Print the exact answer range after the operation.
- After any deletion, insertion, or row-shifting operation that could alter the worksheet's row count, verify that the target answer range (explicitly given in the task's `answer_position` metadata) contains the expected number of rows after the operation (e.g., original count minus deleted rows for deletions, unchanged for in-place clearing). Read the answer range bounds from the task, iterate over that exact range in the output workbook, and print each cell's value — ensuring no truncation or unexpected emptiness beyond the operation's intended effect.
- After writing, print a row‑by‑row dump of the graded answer range plus one or two adjacent context columns (e.g., group delimiters, key columns) to visually confirm that fill‑in rules (stop conditions, skip logic) were applied correctly before calling the task complete.

- Before signaling task completion, verify the output file exists and print the entire answer range from the saved workbook. Only call TASK_COMPLETE after confirming the file is present and the answer range is fully populated with expected values.

- After writing date values, re-read every cell in the answer range and verify that stored Python types are `date` (not `datetime`) unless the task explicitly requires datetimes. Also confirm that any `datetime` objects have no non-zero time component if only dates are expected.

- After writing data to the answer range, explicitly read the last row of the expected range (e.g., `ws.cell(row=last_row, column=col).value`) and confirm it is not `None`. If the last row is empty, either truncate the range to the actual data boundary or note the gap before completing the task.

- After writing computed values, always read back the exact answer range boundaries specified in the task (e.g., `N7:O23`), not just the columns you modified. Print every cell in that range and confirm that original values were overwritten where intended, and that no cells outside the range were modified.

- When formatting (fonts, number formats) is required, after applying, read back the font name and number_format for a few cells, including cells outside the answer range, to confirm the formatting was applied globally. Print these properties alongside cell values.

- **After sorting or reordering data**, verify the output against the task's ordering/grouping clauses by inspecting rows one by one. For multi-step sorts, independently confirm that each sort criterion is satisfied in the final output; do not assume that chained sorts preserve prior groupings unless you have tested and re-inspected.

- When verifying the answer range, print every cell from the first row to the last row of the declared answer_position range, including empty cells. Do not stop at the last non-empty row; use the exact min_row and max_row from the answer_position to ensure no unexpected emptiness.

- After writing, load the saved file and compare the actual dimensions of the graded answer range (number of rows and columns) against the task's `answer_position` specification. If the row count or column count differs, investigate and fix before completing.

- If a reference output table (e.g., “Desired Results”, a highlighted range, or a separate sheet) is provided, after writing, programmatically compare your output range to that reference range row‑by‑row and cell‑by‑cell. Print any differences. Only claim success when they match exactly.

- After writing, iterate over **every cell** in the declared `answer_position` range, including cells you did not explicitly write to. Print each cell's value and confirm it matches the expected content—whether a computed value, an empty string, or a preserved original value. Do not assume that cells you didn't write are fine; explicitly check them and correct any unexpected `None` values.

- After reading back cells from the saved file, print `type(cell.value)` and `repr(cell.value)` for a sample of cells in the answer range. Confirm the types match expectations (e.g., `str`, `int`, `float`, `date`) and that no unexpected wrapping (tuples, lists) or artifacts are present. This catches silent type coercion before task completion.

- **After any deletion or insertion that could alter the worksheet's dimensions**, explicitly check `ws.max_row` and `ws.max_column` against the `answer_position` specification. If the dimensions differ, investigate and fix before completing. This ensures the grader reads the correct cells.
- After saving, print the full contents of all modified sheets (all cells with values) and also report the sheet's max_row and max_column to confirm the sheet dimensions match expectations and no unintended empty rows exist at the end.


- After any row deletion or filtering, reload the workbook and print the full answer_position range cell-by-cell to confirm that the number of rows matches the specification and that all cells contain expected values. Do not rely on a partial printout or assume the range is correct.
- When copying data from an existing sheet to a new location, verify that the copied cells retain the original data types, number formats, and formulas (if applicable) by comparing a sample of source and destination cells. Only strip formatting if the task explicitly permits it.


- After writing, verify that no pre-existing values remain in the answer range where blanks or recomputed values should appear. Scan the entire range and confirm each cell's value matches the intended computation or blank state.

- After every save, immediately reload the workbook and print the sheet name, max row, max column, and the first 5 rows of the answer range (or the first sheet if answer range unknown). This quick sanity check catches empty files, wrong output positions, and missing headers before deeper verification.

- **Proven successful**: After writing, reload the workbook and print the full contents of the output sheet or the entire answer range (all cells, not just a sample) to confirm values match expectations before calling TASK_COMPLETE.

- **After every write, reload the workbook and print the target range with both cell values and their `number_format`** (e.g., `cell.number_format`) to confirm correctness before concluding the task. This tight feedback loop catches formatting issues early.


- **Cell-by-cell before/after comparison**: After writing, compare the before and after states of the exact answer range cell-by-cell, ensuring that empty cells remained unchanged (None) and that only intended data rows were transformed. Print both states for the entire range to confirm no unintended side effects.


- **After conditional writes (e.g., filling values based on a condition), verify that all rows meeting the condition were modified and no unintended rows were affected. Scan all rows that should have been modified, count them, and confirm the count matches expectations. Then spot-check several rows that do NOT meet the condition to confirm their original values remain unchanged.**


- **Always inspect raw cell values and types, not formatted strings.** Converting values (e.g., `strftime`) for display can hide mixed types (datetime vs. string) or None values. Use `print(cell.row, cell.column, type(cell.value), repr(cell.value))` for every cell in the answer range to catch anomalies before completing the task.
- **Final pre-completion check**: Immediately before calling TASK_COMPLETE, reload the workbook and print the exact graded answer range's cell values. Confirm every cell matches the expected output. Only then call TASK_COMPLETE.

- **Header row integrity after row operations**: After any row deletion, insertion, or rearrangement, explicitly verify that the header row (or any fixed row identified during inspection) still contains its original values. This is especially important when the task mentions non-numeric header cells that could be accidentally modified or misaligned.

- **Verify pattern extension**: When you extend a pattern based on pre-existing data in the answer range, after writing, print the full answer range and manually compare at least two output rows beyond the initial examples to the source data to confirm the fill logic is correct.

- **If you wrote formulas**, after reloading with `data_only=True` and confirming concrete values, also print the formula text of each cell in the answer range. Verify that row-dependent references (without `$`) vary per row as expected. If any cell's formula is identical to another where it should differ, recompute and rewrite the formulas correctly before calling TASK_COMPLETE.

- **Full-range spot check**: When verifying a large output range, always check the first few, middle few, and last few rows of the written range, and print summary statistics (e.g., count of non-empty cells, count of specific values) to catch systematic errors. Do not rely on inspecting only the top of the range.

- **Cross-check with source data**: After writing, print the source data rows that were used to compute the answer range alongside the answer range itself. This enables manual verification that labels, rankings, or computed values align with the correct input data. This is especially useful for tasks involving sorting, ranking, or labeling.
## Common Pitfalls


- **Insufficient inspection**: Hardcoding data ranges or assuming formula structure without inspecting actual headers, data, and boundaries, leading to misaligned lookups or incorrect ranges.
- **Output-only verification**: Trusting output appearance without cross-checking any cell against its source data.
- **Unevaluated formulas**: Relying on formula strings that may not evaluate, leaving `None` or error values in output cells.
- **Ambiguous spatial instructions**: Interpreting terms like "above", "nearest", or "first" without listing all candidate cells and justifying the chosen interpretation.
- **Sheet name mismatches**: When a sheet name is read from tool output (especially with whitespace), capture the exact string using `repr(sheet_name)` before using it as a key in code. Never rely on visual inspection alone.
- **Column/Row Shifting and Overlapping Writes**:
  1. Read and store both source and shift-affected ranges into memory before modifying any cells.
  2. After the operation, compare stored original data against final data in both new and shifted ranges to confirm no values were lost, duplicated, or corrupted.
  3. Inspect cells that contain totals or formulas to distinguish formulas from static values; if formulas, verify that the shift preserved their references.
  4. After writing, confirm that the answer range holds the exact expected data patterns stated in the instruction.
- **Premature cosmetic work**: Prioritize core logic correctness over cosmetic enhancements (e.g., style copying). When errors occur, simplify the script and retry before adding formatting.

- **Unscoped aggregation**: When the instruction mentions per‑entity conditions (e.g., per employee, per product), partition data by that entity before computing aggregates or checking conditions. Never build a global lookup across all rows without filtering by the entity key. After writing, verify that each output value depends only on rows matching its own group key (e.g., iterate over unique employee numbers and confirm no cross‑employee contamination).

- **Creating a new workbook instead of modifying in-place**: When the task asks to modify an existing file (e.g., sort data, add a column), do not create a new workbook via `openpyxl.Workbook()`. Always load the original workbook, modify it directly, and save back. After saving, verify that the output workbook retains all sheets from the original by comparing `wb.sheetnames` before and after. If any sheet is missing, the modification was not in-place.
- **Sorting data as strings without considering natural sort order**: When sorting alphanumeric values (e.g., "CT1", "CT2", "DT1"), do not blindly convert to `str()` and use default string comparison. Inspect the actual values and decide on an appropriate sort key (e.g., extracting numeric parts, using `natsort` if needed). Before finalizing, test the sort on a sample and log a few sort-key values to confirm the order matches the intended "small to large" or "A to Z" semantics.
- **Verifying with raw values (not computed)**: After writing formulas, reloading the workbook with `data_only=False` or reading cells without `data_only=True` returns formula strings, not computed results. This leads to false confidence that formulas are present, while the actual computed values remain `None`. Always reload with `openpyxl.load_workbook(filename, data_only=True)` and inspect the cells that will be graded. If any cell is `None`, the formulas have not been evaluated; switch to writing computed values directly.
- **Partial verification**: Checking only a few changed cells after writing, ignoring the rest of the answer range. Always verify the entire graded range for unintended side effects.
- **Hard‑coded references across cells**: When duplicating a formula across multiple columns or rows, ensure that any relative references adjust appropriately. After writing, read back the formula strings and confirm that each cell's formula references the correct input cells for its column/row.
- **Macro requirement ignored**: If the instruction explicitly asks for a macro (e.g., a VBA subroutine), create the macro in an .xlsm file rather than performing the operation imperatively via a script. After insertion, verify the macro's presence by reading the VBA project or confirming the file format supports macros, and ensure the deliverable is a reusable macro, not static output.
- **Ambiguous keyword matching**: When a task says “contain the keyword X” or “cells with X”, inspect actual header values to determine if X appears as an exact match, substring, or prefix/suffix. Print distinct values and confirm the matching rule before writing deletion/filter logic.

- **Unverified lookup deduplication**: When building a lookup from a table with duplicate keys, do not default to first-match semantics without inspecting all duplicates and the task's stated challenge. Print duplicates, choose a strategy that aligns with the instruction (e.g., transposed all-matches), and verify the output pattern matches the intent.
- **Unverified sheet-name mapping**: Assuming that values in a column (e.g., names) exactly match existing sheet names without inspection. Before constructing formulas that reference sheets by name, always compare the unique values from the source column against `wb.sheetnames` and verify that every row's value corresponds to an existing sheet. Process only rows with valid matches.

- **Date cell type and format assumptions**: When writing date values, ensure the stored Python type is `date` (not `datetime`) if the task requires only dates. After writing, read back the cell value and assert it is a `date` instance, not `datetime`. Also, before overwriting a cell's number format, inspect the existing format and log it; only apply a new format if it differs from the target. This prevents hidden time components and format inconsistencies.

- **Unvalidated formula constructs**: When building formulas that use a function in a non‑standard way (e.g., applying a function to a range that typically expects a single cell), test the formula on a single representative cell first, recalculate, and verify the computed result before applying to the full range. After writing, always confirm the answer range contains computed values (not `None` or errors) by reloading with `data_only=True`, unless the task explicitly grades formula strings.

- **Copying answers from example sheets**: If the workbook contains a separate sheet that appears to show the expected result (e.g., highlighted cells, filled values), do not copy those values as the answer. The example may be incomplete, intentionally different, or not the correct answer. Always compute the solution independently, then verify against any provided reference or constraints.

- **ArrayFormula evaluation**: When using openpyxl's `ArrayFormula` objects, note that `.text` returns the formula string, not the computed value. After writing ArrayFormulas, always reload the workbook with `data_only=True` and verify that the graded cells contain evaluated numeric results, not `None` or formula strings.

- **Trusting script output over file inspection**: Print statements from your script are not a substitute for verifying the saved workbook. After saving, always re-open the file and read back the actual cell values (and types) in the graded range. Do not declare TASK_COMPLETE until you have confirmed the file content matches expectations.

- **Unvalidated pattern extension**: When you deduce a pattern from a few data points, always test it against all known reference values in the answer range (if any) before applying to the entire range. If reference rows are populated, confirm your computed approach reproduces them exactly before extending it.

- **Hardcoding data instead of reading from workbook**: After inspecting, do not retype data values as literal lists in your script. Always extract the data directly from the workbook using `iter_rows()` or `cell.value`. Before writing the output, confirm the read values match the expected dimensions and are not `None` for required cells. This prevents silent errors if the workbook data differs from what you manually transcribed.

- **Excessive Inspection Without Solution Synthesis**: Spending many turns inspecting data without writing any output. After the first inspection that reveals the data structure, immediately write the solution script. Never exceed two inspection-only commands. Always confirm the output file exists after each write attempt. If the initial inspection provides enough understanding to write transformation logic, write it immediately.

- **Unchecked header duplication after sorting blocks**: When sorting or restructuring data into multiple blocks, the header row may be inadvertently written into each block, producing duplicate headers. After sorting, scan the first column for the header literal and verify it appears exactly once (or as intended) across the graded answer range. If duplicate headers are found, correct the logic before completing.
- **Unverified blank-row partitioning**: When partitioning data by blank rows (e.g., for sorting blocks), do not assume blank rows are empty in all columns without inspection. Print the immediate neighborhood of each detected boundary (2 rows before and after each blank row) and visually confirm that the data blocks align as expected. This prevents accidental merging or splitting of contiguous data.

- **Indiscriminate clearing**: Clearing entire sheets or large ranges without inspecting existing content first. Always inspect the target region (values, formulas, formatting) before clearing, and clear only the cells that need to be overwritten. After clearing, verify that no data that should be preserved was lost.


- **Static formula strings in loops**: When writing formulas to multiple rows via a loop, do not assign the same static formula string (e.g., `'=IF(A2=J2, B2-C2-E2-G2, 0)'`) to every cell. openpyxl does not auto-adjust row references; every cell will contain the identical formula referencing the same row. Instead, generate row-specific formula strings using f-strings (e.g., `f'=IF(A{row}=J{row}, B{row}-C{row}-E{row}-G{row}, 0)'`). After writing, read back the formula text from the first, middle, and last row of the range and confirm each references its own row number before proceeding.

- **Unverified grouping logic and row compaction**: When deleting rows based on grouping (e.g., duplicates), always verify that each deletion candidate belongs to a multi-row group before deletion. Print all rows in each group and ensure group size > 1. If a group has only one entry, skip deletion to avoid IndexError or accidental deletion. When the task says "delete rows", determine whether the answer range is a fixed address span (e.g., B2:O42) or dynamic. For fixed spans, clear cells in-place to preserve row numbers. For dynamic ranges, actually delete the rows (shift up). After the operation, verify that the answer range's row count matches the expected outcome: unchanged for fixed spans, reduced by the number of deleted rows for dynamic ranges. Always re-read the task verb for the precise action requested ("delete" vs "clear").
- **Writing formulas to the answer range when the grader expects computed values**: Even if the task asks for a formula, the grader typically reads the cell values, not the formula text. Unless the task explicitly says to submit the formula text as the answer, always compute the values in Python and write them directly. After writing, verify that the answer cells contain concrete values, not formula strings.

- **Hardcoding row ranges for variable‑length data**: When the task states data is variable‑length, never hardcode row indices (e.g., `range(2, 86)`). Always compute the last row dynamically using `ws.max_row` or by scanning for the last non‑empty cell. After writing, verify that the processed row count matches the actual data extent.

- **Unverified column index-to-letter mapping**: Assuming column index N equals column letter N without verification. openpyxl uses 1‑based indices where A=1, B=2, …, Z=26, AA=27, etc. Column index 14 is 'N', not 'BN'. Always verify the mapping with `openpyxl.utils.get_column_letter(index)` or by inspecting the header row at that index before writing. After writing, read back the specific target column's cells to confirm they contain expected values, not `None`.

- **Misinterpreting formula requests**: When the task uses phrasing like 'How can I look up...', 'Write a formula to...', or 'Provide the formula text', it explicitly asks for formula strings. Do not overwrite with computed values unless the task explicitly asks for results. Inspect the answer range for pre-existing formulas to confirm the expected output type.


- **Unverified row deletion based on partial emptiness**: Deleting rows solely because one column is empty, without checking other columns for data. Always print the full row content for every candidate deletion row and confirm the row is truly empty across all columns (or that the deletion condition applies to all columns) before deleting.
- **Ignoring error cells**: If the task mentions an error like #REF!, #VALUE!, or #N/A in a specific cell, you must replace that cell's content with a corrected formula or value before saving. After writing, verify that the cell's value is not an error string and not None.
- **Stopping at the first empty row instead of scanning to ws.max_row**: When scanning for data boundaries, do not stop at the first row where all columns are None. Always scan the entire used range up to `ws.max_row` and identify the actual data region by inspecting headers, column values, and explicit markers (e.g., "THE ABOVE TABLE WOULD BECOME:"). Print the rows you intend to include and exclude before setting boundaries.


- **Assuming reference sheet sparsity is intentional incompleteness**: When comparing output to a reference sheet (e.g., 'Expected', 'Desired Results'), treat empty rows/columns as intentional layout constraints, not as incomplete data. Verify that your output matches the reference's exact row positions and dimensions, not just data values. Before completion, confirm that any gaps in the reference are preserved in your output unless the task explicitly states otherwise.
- **Hardcoding column names from visual inspection**: Never manually re‑type column names or lists that can be derived from the spreadsheet structure. Always extract column lists programmatically from the header row (e.g., by scanning for all columns after a known key column). Cross‑check that every entry in a lookup table or reference sheet has a corresponding column in the data. After writing, verify that the output's unique variable count matches the number of source columns processed.

- **Writing a new workbook when output position is specified within an existing file**: If the task says "output the answer from cell G2" or similar, this implies modifying the existing workbook. Always load the original file, write to the specified cells, and save, preserving all other content. Do not create a new workbook that contains only the computed result.
- **Unverified formula writes**: After writing formulas, trusting the script's success message without re-reading the saved file. Always reload and verify at least a sample of the answer range (first, middle, last rows) to confirm cells contain expected values, not `None` or formula strings. Do not declare success until you have inspected the file contents.
- **Blindly applying transformations to headers**: Applying a row-wise transformation (e.g., string truncation, substitution) to the entire answer range without first checking for a header row, causing the header text to be corrupted. Always inspect the first few rows to identify headers and exclude them from data-only transformations.


- **Unverified linear interpolation across zero**: When transforming values across a range that straddles zero, do not split into separate positive/negative formulas assuming zero is a boundary. Derive a single linear function mapping the full input range [min, max] to the output range [score_min, score_max] using the standard two-point formula. Before writing, test the formula on at least the min, max, and zero (if within range) to confirm anchor points are correct. After writing, verify a sample of computed values across the full range for consistency.
- **Fragile number-format logic based on floating-point heuristics**: When applying conditional number formats (e.g., whole numbers, 1 decimal place, 11 decimal places), do not rely on floating-point checks like `score == int(score)` or tolerance comparisons. After computing all output values, inspect the full list and classify each using robust methods (e.g., `Decimal(str(val)).as_tuple().exponent` or `val == round(val, d)` for each required precision). Print a summary of value-format assignments before writing to confirm the rule matches every cell.
- **Unverified substring matching**: When using string containment (e.g., `in`, `str.contains`) to filter or match data, always test for false positives by checking whether the search string appears as a substring of longer tokens. Print a sample of matches and non-matches and verify that the logic matches the task's intent (e.g., whole-word matching vs. substring).


- **Scope mismatch**: When the task describes a transformation that applies to a broader scope than the graded answer range (e.g., "across all columns", "entire sheet"), do not limit the operation to only the answer range. Inspect the full described scope and apply the transformation to all relevant cells. After writing, verify that the transformation was applied to the full described scope, not just the graded cells.

- **Unverified header and column completeness in table copy/reorder tasks**: When copying or reordering rows to match a reference table, do not assume the destination headers should match the reference headers; verify whether the task requires preserving original headers. After writing, inspect every column in the answer range — including formula columns — to confirm all cells contain concrete values, not formulas that evaluate to empty or `None`. If any column is empty, check whether a source column was omitted or formulas need to be replaced with computed values.

- **Header row value type corruption during copy**: When copying rows from a source sheet to a target sheet, openpyxl may auto-convert date-like strings into datetime objects, corrupting header labels. After copying, always inspect the header row of the output sheet and verify that every header cell contains the expected text string (not a datetime). If needed, explicitly read source cells with `data_only=True` and cast to string before writing.

- **Pandas write without verification**: Using `df.to_excel()` and assuming the output matches the expected layout without loading the workbook and verifying the answer range. Always load the written file with openpyxl and verify the answer range after any write operation, including pandas. Pandas may alter column order, data types, or sheet structure unexpectedly.


- **Clearing a fixed answer range and writing fewer values**: When transposing or writing a list of values to a fixed answer range that is wider than the list, do not clear the entire range and then write only the values, leaving trailing empty cells. Instead, either delete the surplus columns after the last written value or adjust the answer range to exactly match the number of values. After writing, verify that no trailing `None` cells exist in the answer range.
- **Substring matching on fill color strings**: When checking cell fill colors, avoid using substring containment (e.g., `'FFFF00' in str(fill_color)`) which can produce false positives. Extract the RGB value explicitly via `cell.fill.start_color.rgb`, strip any leading alpha prefix, and compare exactly against the target color. Print the extracted value to confirm before writing.

- **Unverified grouping keys**: Before finalizing any aggregation with `groupby`, print the columns used for grouping and compare them against the task's stated grouping criteria. Print the unique keys and the number of rows per group to confirm the aggregation collapses only across the intended dimensions. If extra columns are present, remove them and recheck.
- **Writing dates as strings**: When writing date values, never use `strftime` or manual formatting to produce string representations. Always write `datetime` or `date` objects directly. After writing, verify that `cell.data_type` is `'n'` (numeric) or `isinstance(cell.value, datetime)` is `True`, not a string, unless the task explicitly requires plain text.
- **Hardcoding blank-row deletion indices**: After inspecting data, never hardcode row indices for deletion based on visual inspection. Implement a dynamic detection loop that identifies rows where all cells in the used data columns are None/empty, and confirm the detection output by printing the indices before acting. This prevents fragility when the dataset changes.
- **Retrying without diagnosis**: When an operation fails, do not blindly retry by tweaking parameters. First, print the full exception traceback and inspect the objects involved (e.g., `print(type(cell.font), cell.font.__dict__)`). Only rewrite the code after understanding the failure cause. This prevents repeated identical failures and wasted turns.

- **Verifying formula text instead of computed values**: Even if the task asks for a formula, the grader typically reads cell values, not formula strings. After writing, always reload with `data_only=True` and verify that every cell in the answer range contains a concrete value (number, string, date), not `None` or a formula string. If any cell is `None`, compute the values in Python and write them directly, regardless of the task phrasing. Only when the task explicitly says 'submit the formula text' should you verify formula strings with `data_only=False`.

- **Unverified entry-to-header mapping**: When mapping entries to headers based on substring presence (e.g., matching product codes to column headers), do not use a greedy first-match that silently picks the first header containing the substring. Print all possible matches per entry, apply a disambiguation rule (longest match, exact token boundary, or explicit whitelist), and confirm that every source item resolves to exactly one match before writing output. After writing, trace a random sample of output rows back to source data to verify the mapping is correct.


- **Uninspected target sheet before overwriting**: Writing data to a target sheet without first reading its full content (headers, existing data, formatting). Even if the sheet appears empty (e.g., dimensions A1:A1), always read the first several rows to confirm whether a header exists and determine the correct starting row. Print the sheet's content and your starting-row decision before writing any data.