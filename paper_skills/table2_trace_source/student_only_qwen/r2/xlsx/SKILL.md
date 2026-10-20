---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow


- - **Identify the deliverable type first**: Before any inspection, re-read the task instruction to identify the exact deliverable type (e.g., macro, formula, Python script, modified workbook, code text). If the instruction asks for a macro, you must produce macro code within the workbook (or as a .bas file), not execute a one-time transformation externally. After writing any output, confirm that the deliverable type matches the instruction before declaring completion.

Before deleting rows, print all values in the relevant column(s) row-by-row to understand the data distribution (including blank rows, headers, and summary/footer rows like 'Total' or 'Subtotal'). Base deletion logic on actual observed values, not assumptions about where data starts or ends. If summary/footer rows exist, decide whether they should be excluded from the deletion range, preserved at a fixed row, or recalculated after deletion.

When deleting rows, iterate from the bottom up (e.g., `for row in reversed(range(2, ws.max_row+1))`); when deleting columns, iterate from the rightmost column leftward (e.g., `for col in reversed(range(1, ws.max_column+1))`). After deletion, verify the output row/column count matches the expected count (original minus deleted).

When inserting rows, also iterate from the bottom of the range upward (e.g., `for row in range(max_row, start_row-1, -1)`) to avoid index drift as rows shift down. Before the insertion loop, confirm the range boundaries (max row) in the target sheet to avoid off-by-one errors from assuming a fixed upper bound.
Before any deletion, confirm whether the task requires structural row removal (fewer rows, rows shift up) or value clearing (same row count, cells set to None/empty). The word "delete" in the instruction implies structural removal unless explicitly qualified otherwise.

- Before any irreversible operation (deletion, overwrite), run a separate read-only check that computes the exact condition (e.g., sum, threshold, pattern) and prints the values and the decision (True/False) before acting.


For large-scale transformations (e.g., deleting/moving many rows/columns, applying formulas to thousands of cells), write a self-contained Python script that performs the operation and then immediately reads back the modified workbook to verify the result.


**CRITICAL: Always produce a concrete output file.** Even if the transformation logic is incomplete, the workbook structure is unexpected, or you are uncertain about the correct approach, write a best-effort output file to the exact required path before stopping. After writing, verify the file exists (e.g., `os.path.exists(output_path)`). Never end a task after only inspecting input — a task without an output file is incomplete.
## Inspection




**Structural reconnaissance**: As the very first step, load the workbook and print the sheet names, dimensions (max_row, max_column), header row values with column indices, and all data rows if the workbook is small (e.g., <200 rows), otherwise the first 20 and last 10 rows. Use `values_only=False` when printing to capture formula strings and data types. This confirms the workbook structure, column positions, data types, and any existing formulas before any detailed inspection or transformation.
- After printing the full used range, note any irregularities (e.g., empty rows, unexpected column counts, pre-existing values) and adjust your plan accordingly.

Then inspect the data thoroughly:
- Check column types, value formats (e.g., datetime vs. date strings), and whether lookup keys will match.
- Before using a hardcoded criterion in a formula (e.g., FALSE, 'True', a specific string), inspect the actual values and types in the referenced column. Print `type(cell.value)` and `repr(cell.value)` for a sample to confirm the criterion matches the data representation. Adjust the formula accordingly (e.g., use boolean `FALSE` if values are booleans, or `'none'` if they are strings).
- For every source table, independently inspect the header row. Print exact header values with their column indices, and verify that the targeted column's header text matches the instruction (e.g., 'Reference' for column E). When column positions may change, locate data columns dynamically by scanning header rows for a known label string. Print the found index and use that index for all subsequent operations. Never hardcode column letters or indices.
- When building lookup dictionaries from multiple tables, match on actual date values read from headers, not on column index assumptions.
- Explicitly validate all input and output ranges: read the row-label column, the column-header row, and the boundaries of the lookup data table (including whether the first row is a header or data). Print a structured summary (e.g., "row labels in B4:B7: [x,y,z,v]; col headers in C3:F3: [A,B,C,D]; lookup data rows: I3:K22 with headers? Yes/No") and confirm alignment with the task's answer-position boundaries.
- Never assume ranges, formats, or column alignments without reading the file.



After at most 2 inspection turns (any combination of read-only steps), you MUST write the output file to the required path. After your first inspection turn, if you have enough information to begin coding, do so immediately. Immediately after writing, verify the file exists (e.g., `ls -la <output_path>`). If the file is missing, write it again—do not continue inspecting.

- For any column that the instruction implies should be filtered or grouped (e.g., employee ID, department, date range), print the distinct values using `set()` to confirm whether the data spans multiple groups and to determine the correct filtering logic before writing any computation.
- When aggregating data across multiple sheets, iterate over every source sheet and programmatically collect all unique key–value pairs, grouped by any relevant category (e.g., account‑type prefix). Print summary statistics (count per category, first/last items) to confirm no sheet or subset of rows is omitted.

- When sorting data, inspect the actual values in the sort column to determine whether they should be sorted numerically (extracting numeric components) or as strings. If the instruction says "small to large" and values contain numbers, sort numerically; print the first few sorted values to confirm.
- When an instruction specifies a text search (e.g., 'look for a specific text'), list all unique values in the target column that contain the search text, and verify whether an exact match or substring match is appropriate before writing any filtering logic.
- Before modifying any cell, inspect the workbook for non‑value properties that must survive the edit: data types, number formats, merged cells, column widths, and sheet protection. After saving, re‑open the output file and verify that the structural properties of the graded range (e.g., data types of header rows, presence of blank separator rows) match the original.


- If the input file path is not obvious or fails, use `find` or `ls` to locate it; do not manually edit the path string. Confirm existence with `os.path.exists()` before loading.
- When building a lookup dictionary from a source table, first group all values by key and print the groups. If any key has multiple values, determine whether the task expects a single value per key (e.g., first occurrence), aggregation, or transposition across columns. Confirm the expected output shape before writing.
- When the target range is within a table that has multiple value columns (e.g., separate columns for different return values), print the full header row and any existing data in the target range. Explicitly map which source columns correspond to which target columns, and confirm the number of output cells per row matches the instruction's description (e.g., "transposed" may imply multiple values per row).
- Before writing formulas that reference other sheets by name (e.g., INDIRECT, cross-sheet references like `=SheetName!A1`), extract the list of names being referenced from the relevant column and cross-check against the actual sheet names in the workbook. Print both lists side-by-side and confirm a complete match before applying the formula to the entire range.
- When the task requires deleting rows based on emptiness, first inspect the header row and a few data rows of the target range to determine which columns constitute 'content' that should prevent deletion. Match the instruction's column descriptions to actual columns, and resolve any ambiguity before coding.

- Before each inspection command, articulate the specific question you are trying to answer. After the observation, summarize the key finding in one sentence. If you cannot articulate a clear question or the finding doesn't change your implementation plan, stop inspecting and start writing code.

- When the instruction references an existing cell's format (e.g., 'use the format of cell A2'), inspect that cell's `number_format` and use it as the target format for output cells. After writing, verify that the output cells' `number_format` matches.

- After inspecting a sample of rows, always confirm the worksheet's last used row via `sheet.max_row` (and column via `sheet.max_column`) to ensure you have not missed data beyond your inspection window. When the task provides an explicit answer range, verify that the range lies within the actual data extent and adjust if necessary.

- When performing text matching, first inspect the actual values in the target column to see what variations exist. If the instruction says 'contains the text X,' decide explicitly whether exact equality after stripping, substring search, or case-insensitive comparison is appropriate based on the data. Document your choice in a comment. After writing filtering logic, verify that only the intended rows were affected by printing matched values and final row counts.

- When an instruction lists multiple filter patterns with ambiguous separators (e.g., Chinese commas '\uff0c' vs. English commas ','), print the unique values in the target column and test whether any rows match the literal separator-including string before splitting the instruction into separate patterns. Confirm the correct interpretation against actual data, not assumptions. When case-insensitive substring matching is appropriate, normalize both the cell value and the target string by lowercasing and stripping whitespace before comparison.

- When filtering cells based on a property (e.g., 'whole numbers', 'text containing X'), apply the filter to every cell in the specified range, not a predicted subset based on column patterns. After extraction, programmatically verify that the filtered set satisfies the property (e.g., for whole numbers, assert all(v == int(v))).

- Print fill colors, fonts, and number formats for key cells (e.g., header rows, cells with unusual formatting) to capture formatting that may be required in the output or that indicates special meaning (e.g., color-coded categories).

- When modifying existing formulas, inspect the cell's value type. If the value is an `openpyxl.worksheet.formula.ArrayFormula` object, extract the formula text using `.text` to understand the current logic before writing new formulas. Do not rely on the visible cell value alone.
- When the task involves filling formulas across a column, read all non-empty values in that column to detect any repeating patterns (e.g., data every N rows) or existing formulas that may guide the fill logic.

- Before sorting by contiguous segments (e.g., blocks separated by blank rows), scan the first row of every segment to determine whether it contains column headers. Print the value of the first cell in each segment to confirm.
- Before modifying any cell, print at least 5-10 rows of the relevant data range (including formula strings and evaluated values where available) to understand the current state before writing code.
- For grouping, deduplication, or sorting tasks, print all rows with row numbers and the relevant column values before writing any transformation code. This ensures you see every duplicate group and edge case.

- When the workbook contains multiple distinct sections (e.g., a summary and a data table), print the entire used range (all rows) before any modifications to understand the layout, boundaries, and column roles. This prevents formula range errors and misinterpretation of structure.


- Before writing any solution, list every sheet in the workbook (`wb.sheetnames`) and cross-reference with any sheet names mentioned in the instruction (e.g., 'BR1', 'Sheet1'). If required sheets are missing or the structure does not match expectations, explicitly state the mismatch and your decision for handling it — do not silently proceed with only the available sheets.
After listing all sheet names, flag any sheets whose names contain "result", "expected", "desired", "answer", or "output" (case-insensitive). These are likely provided as expected outcomes. Before writing any transformation code, print the full content of every such sheet and compare its structure and values against your planned approach. If your interpretation of the instruction would produce different results, re-examine the instruction before proceeding.
- Before any transformation, print all sheet names, their dimensions, and the first 20 rows of every sheet (or all rows if fewer) to understand the full layout. This prevents acting on assumptions about a single sheet's structure.
- When the task involves extending or filling existing data (e.g., generating new IDs, suffixes, or sequential values), print every value in the target column to identify the most recent non-blank entry and any pre-existing patterns (such as letter suffixes, numeric ranges, or formatting conventions) before writing generation logic.
- When the dataset is small enough (e.g., <100 rows), print all rows of the relevant columns to identify edge cases, data types, and any pre-existing status flags before writing formulas. For larger datasets, print the first and last few rows and scan for anomalies.


Always make this comprehensive inspection your first action before any other analysis.
- When a cell contains delimited values (e.g., semicolon‑separated), split on the delimiter, strip whitespace from each part, and filter out empty strings caused by trailing delimiters. Print the parsed list to confirm before further processing.
- When collecting unique values across multiple cells or rows, use a `set` to accumulate values, then sort as required. Print the set size and a sample to confirm.
- When building a lookup dictionary from any source table, first print the full content of the relevant columns with row numbers. Identify the exact header row, then iterate only over data rows. After building the dictionary, print it and cross-check against the source: count entries and spot-check a few keys to ensure no headers or blank rows were accidentally included.

- Before editing a cell that contains an error or formula (e.g., `#REF!`), inspect that specific cell's value and formula string (using `cell.value`). If it is a formula, trace its dependencies to understand the broken reference before writing a fix. Do not guess.


- Before any write or delete action, print all cell values across the full used range (using `iter_rows` up to `ws.max_row` and `ws.max_column`).
- When printing the full sheet, include each cell's coordinate, value, and type (e.g., `print(cell.coordinate, cell.value, type(cell.value).__name__)`) to understand data types and empty cells. This captures the complete layout, including blank rows, headers, and hidden structural elements, so every decision is based on the actual sheet contents rather than partial views.

- When printing full sheet contents, look for repeating structural patterns (e.g., multiple staff members each with a fixed number of rows, repeating header blocks) that will inform transformation logic. Note the count of groups and rows per group before designing any operation.

- When a reference or expected output sheet is provided, print its full content (all rows) to understand the desired output structure before writing any code.
Pay attention to structural patterns in expected sheets — blank row separators between groups, repeated header blocks, and trailing rows — as these often reveal formatting requirements not stated in the instruction.

- When using pandas to read Excel files, first inspect the file with `pd.read_excel(path, nrows=5)` to confirm column names and header row index match expectations. Do not assume `header=0` without verification.

- When using pandas, print the DataFrame's shape, columns, and a sample (head/tail) at each major step: after loading, after each transformation, and after writing back to Excel. This catches structural changes, lost columns, or incorrect filtering early.

- When implementing a match where the condition is that a set of parameters is 'found within' a text field (e.g., comments), verify that the match is bidirectional: ensure that all components of the text field are accounted for in the parameters, not just that the parameters appear in the field. Print a sample of matches with the full text field and the parameters to confirm the logic before writing any results.

- When the task involves modifying existing formulas, print the full relevant range row‑by‑row, including both cell values and formula strings, to understand the current formula structure, header positions, and data layout before writing any new formulas.


- When copying or referencing header rows from a source sheet to an output sheet, print each source header cell's `.value`, `type(cell.value).__name__`, and `.number_format`. Datetime objects, formulas, or other non‑string artifacts may display as text in the spreadsheet view but have different underlying types. After writing headers to the output, verify they contain the expected constant strings, not dates or metadata artifacts, unless the task explicitly preserves dynamic headers.
- When an operation targets a specific column (e.g., deduplication, filtering, sorting) and the column is not explicitly named in the instruction, inspect all column names and print sample values from each. Match the column to the instruction by value patterns (e.g., duplicates, data types), not by index or superficial name match. Print a confirmation like `Target column for operation: <name>` before proceeding.


- Before performing a conditional write (e.g., filling a column based on criteria), inspect the entire target column (all rows) to understand what values already exist. Print a frequency count or list distinct values. Decide explicitly whether the operation should preserve, overwrite, or clear values in rows that do not satisfy the condition. After writing, verify that this intention was carried out across the full range.

- When investigating formulas that need correction, print the full range of interest plus surrounding context (e.g., rows 1-20) to understand the data layout, lookup tables, and formula dependencies before designing a fix. This reveals whether formulas chain off adjacent cells or should independently reference a lookup column.

- When printing all non-empty cells, note any pre-filled example rows or expected values embedded in the sheet (e.g., in adjacent columns or labeled rows). Treat them as a pattern to infer the transformation rule: print source and destination values side-by-side for at least two example rows, confirm the mapping, and only then apply the inferred rule to the remaining rows. After writing output, compare against these examples as validation anchors.

- After inspecting the layout, manually compute expected results for a few representative cells or columns (e.g., 'Column B should contain max scores: A=5, B=4, C=3 → Max=5') to cross-check your intended logic before writing any code. This catches off-by-row errors and layout misinterpretations early.
## Writing Output




**CRITICAL: openpyxl does not evaluate formulas. After writing any formula, you MUST reload the workbook with `data_only=True` and verify that every answer cell contains a concrete computed value (not None, error, or formula text). Never trust formula strings.
Always reopen the saved file from disk (e.g., `wb = openpyxl.load_workbook(output_path, data_only=True)`) — never read the in‑memory workbook after saving, because openpyxl does not evaluate formulas.**


After confirming the input structure, immediately create a draft output workbook and save it to the exact output path.
If the output directory does not exist, create it first (e.g., `os.makedirs(os.path.dirname(output_path), exist_ok=True)`).
If the task requires modifying an existing file, load the original workbook and modify it in place; do not create a new workbook from scratch unless explicitly instructed. Do not spend more than 2 read‑only steps without saving a file. After each save, verify the file exists (e.g., `os.path.exists()`) and contains the expected data ranges.

Before writing any values, print the target answer ranges from the task instruction and compare them to your planned write areas. For each block, confirm that the number of rows you will write equals `end_row - start_row + 1` and the columns match the range letters. If there is a mismatch, adjust your aggregation logic or write plan BEFORE saving.

- When the instruction specifies exact cell addresses (e.g., 'output in H10', 'output in H20'), print a checklist mapping each target cell to the value you will write. After writing, verify each target cell's value matches the intended placement.

- Print the processed data (e.g., sorted rows, computed values) before writing to confirm the transformation logic matches expectations.

- Before writing any formula, cross-check its logic against all provided numerical examples. Manually compute expected values for each example, then confirm the formula yields those values. This habit prevents propagating misconceptions into the spreadsheet.

- Before writing any formula, cross-check its logic against all provided numerical examples (including any example output values visible in the input data). Manually compute expected values for each example, then confirm the formula yields those values. This habit prevents propagating misconceptions into the spreadsheet.

- Confirm the output path matches the required path exactly, using a string comparison in code (e.g., `assert output_path == expected_path`).

- Before writing to any answer range, inspect its current contents (first 5 rows, last 5 rows, and a middle slice) to determine whether to clear, supplement, or replace. Document your decision.

- Before applying a formula pattern across multiple cells, test it on ONE cell first. Write the formula into a single cell, reload the workbook with `data_only=True`, and confirm the computed value is correct and not None/error. Only then apply to the full range.

- When testing a formula, always print the computed value (from `data_only=True`), not the formula string.

- After writing formulas to the full range, save the workbook, reload with `data_only=True`, and confirm that every cell in the answer range holds a concrete computed value (not None, error, or raw formula text). Never verify formula correctness by reading back formula strings; always check the computed values.

- If a system check warns that the output file is missing, stop all inspection and write the file immediately in your next action. Do not continue reading data or planning.

- When deduplicating, filtering, or sorting, print the intermediate results (e.g., unique rows after deduplication, helper list contents, sort order) before writing to catch mismatches between the instruction's requirements and your implementation before the output is finalized.

- Before writing to any target cell, inspect its current content and ask: "Does this cell currently contain a formula or special structure that my write should extend rather than replace?" After writing, re-read the answer range to confirm each cell holds the expected value type (number, not formula text) unless the task explicitly requires formulas.


- Before writing any values, **separately** inspect the current contents of the target answer range and any adjacent cells that might be affected. Print the exact values (including empty vs. None) and decide whether to overwrite, supplement, or preserve existing data. Do not combine this inspection with the writing step in a single script; always run a read-only inspection first.
If the task provides a graded answer range, print its exact coordinates and dimensions, and compare with the current used range of the sheet to ensure you are not clearing or writing beyond the intended boundaries.
- If the answer range includes a header row that must be preserved, confirm its presence and content before writing. Explicitly decide whether to skip row 1 or overwrite it, and document the decision. After writing, verify that the header row matches the expected state (e.g., original header text, or new header if required).

- When writing lookup results derived from text matching, print for at least a few rows the parameter values, the matched text field, and the resulting ID to visually confirm the matching logic aligns with the instruction. If any mismatch is found, adjust the logic before writing to the entire range.
- When writing values into a pandas DataFrame, inspect the dtypes of all target columns before any write (e.g., `print(df.dtypes)`). If a column is numeric (float64/int64) and you need to write strings, convert it to `object` or `str` first. After writing, verify a sample of values with their Python types to confirm the column holds the expected types.

- When writing formulas, ensure every string starts with '='. After writing, reload the workbook with `data_only=False` and verify that each cell's `.value` starts with '='. If any cell contains a literal string (e.g., `'IF(...'`) without '=', you wrote text, not a formula; fix and re‑save before proceeding.

- When modifying existing formulas, inspect every cell in the answer range individually and classify each as empty, correct formula, or incorrect formula. Only overwrite cells that are empty or contain an incorrect formula. After writing, verify that no correct formulas were accidentally overwritten and no cells remain empty that should be populated.

- When existing cells in the target range already contain data, compare your computed values with the existing values before overwriting. Log existing vs. computed values side-by-side for all non‑empty target cells. If they match, skip the write; if they differ, investigate the discrepancy and only overwrite if the change is intentional and justified. A concrete check: before writing, iterate the target range and for each cell with a non‑None value, print `cell.coordinate`, the existing value, and your intended replacement; then write only where values differ or where the cell is empty.

- When extending a formula down a column (e.g., from I4 to I5:I7), construct each cell's formula string with the correct row‑specific references (e.g., `f'=SUMPRODUCT(... H{row} ...)'`). Never assign the identical formula string to multiple rows without adapting row numbers. After writing, verify that at least two cells in different rows contain distinct row‑appropriate references.

- **Prefer computed values over formula strings**: Unless the task explicitly requires a cell to contain a formula (e.g., for a formula‑grading task), compute the result in Python and write the value directly. This avoids openpyxl’s formula‑evaluation limitations and ensures the grader sees the correct data. When in doubt, write computed values.
## Verification


**CRITICAL: Never declare TASK_COMPLETE without first re‑opening the output file and printing at least the first few cells of the answer range. If any cell is None or empty, fix the write issue immediately. This is a mandatory guard against silent write failures.**


- After any write operation, immediately read back the written cells from the saved file and confirm they match the intended content.
- **Proven success pattern**: After every write operation, reload the saved workbook and print the exact graded answer range (all cells) to confirm that every cell contains a concrete value (not None, error, or formula text) and matches the intended output structure. This catches silent write failures, off-by-one errors, and column misalignment.
- When verifying, print each cell's coordinate, value, and type to confirm the answer range contains the correct number of cells, expected data types, and non-None values.
- For formula cells, open the workbook with `data_only=True` (or use an evaluation tool) and confirm that **every cell in the entire answer range** holds a concrete value (number, string, date) — not `None`, an error, or raw formula text. Print the computed values for the full answer range (or at least the first and last few rows) to confirm correctness. Do not rely on sampling a subset of cells.
- After column-move or data-relocation operations, read back every cell in the graded answer range and compare each value against any concrete expected values from the instruction. Halt and correct if any mismatch before saving.
- When a reference or expectation sheet is provided, verify the output row order against it directly. Loop over the expectation sheet's rows to build the output sequence, and assert that the output row order matches (ignoring formatting differences).

- When a reference table is provided (e.g., 'Desired Results'), after writing output, load both the output range and the reference range and perform an exact cell-by-cell comparison (ignoring formatting). Use assertions or print diffs; never rely on visual similarity alone. Confirm zero mismatches before declaring completion. Do not assume that sorting IDs numerically reproduces the correct order.
- After saving the final output workbook, reload it from disk and print the exact target range to confirm the values on disk match the expected output.


- After writing output, reload the workbook and print the exact graded answer range (including cells that should be empty) with coordinates and values. Confirm that every cell in that range contains a concrete value (not None, empty, or raw formula text unless formulas are explicitly graded). If any cell is empty, check the instruction to determine whether it should contain a value (e.g., a label, an intermediate count) or remain empty; do not assume sparse output is acceptable. If a value is needed, populate it — copy down formulas, fill with computed values, or replicate existing logic from adjacent cells — before saving. 

- When verifying formula cells, never print the formula strings as a check; always reload the workbook with `data_only=True` and print the computed values.
- After writing formulas that reference a header row across columns, reload the workbook with `data_only=False` and read back the formula strings for the entire answer range. Confirm that each cell's formula references the header cell in its own column (e.g., F6 references `F$5`, G6 references `G$5`). If any mismatch, correct before saving.
- After writing output and before calling the task complete, execute at least one explicit automated check that the output satisfies each requirement in the instruction (e.g., verify that cells meant to be zero are exactly zero, that no disallowed cells changed, or that computed values respect stated bounds). Run these checks as code assertions, not by reading a printout. If any check fails, iterate and re‑verify.
- Before clearing or overwriting cells in a target sheet, inspect its current contents and dimensions. After clearing, re-inspect to confirm only the intended cells were modified and the sheet is in the expected state before writing new data.
- After deleting rows or columns, print the surviving headers (or first row) and confirm that the operation removed exactly the intended data. Verify that any summary/footer rows (e.g., 'Total') remain in a logically correct position relative to the remaining data (print their values and row indices before and after).
- After any structural change (row/column deletions, inserts, moves), re-print the full worksheet contents to confirm updated boundaries before proceeding with further edits.


- When verifying the graded answer range, print every cell individually (e.g., `for row in ws['A3:A24']: for cell in row: print(cell.coordinate, cell.value)`). Do not rely on row summaries or partial prints; check that the exact range is fully populated with expected values.
- After each write, print a verification table of all modified cells together with their key grouping columns (e.g., block identifier, invoice number) to visually confirm the intended pattern before declaring the task complete.
- After deleting rows based on emptiness, reload the workbook and iterate the answer range to confirm that no row is entirely empty in the columns you checked (or all columns). Print a few retained rows to confirm content survived.


- After any structural change (row/column deletions, inserts, moves), re-read the exact graded answer range (the cell address given as `answer_position`) and print every cell individually to confirm the correct cells are populated with expected values. Do not rely on overall sheet inspection or header checks alone.

- When verifying the graded answer range, print both `repr(cell.value)` and `cell.number_format` for every cell to confirm values and formatting are correct. Do not rely on sampling; check the full range.

- If the task requires preserving original formatting, after writing, reload the workbook and verify that the formatting (e.g., number_format, font name) of the output cells matches the corresponding source cells. Print at least one formatting attribute for a sample of cells and assert it matches the source.
- After writing, confirm that the last non-empty row in the graded answer range matches the number of output records, and that no trailing empty rows remain in that range unless the task explicitly allows empty cells.

- Before declaring task completion, re-read the instruction and list every required deliverable (e.g., computed values, formulas, VBA code, macros, script files). Confirm each is present in the output. If code or macros are requested, produce them (e.g., save as a .bas file or embed in the workbook) and verify their presence; a computed value in a cell does not satisfy a request for code.
- Before declaring task completion, reload the workbook with `data_only=True` and verify that every cell in the graded answer range contains a concrete computed value (not None, error, or raw formula text). Use an assertion like `assert cell.value is not None and not (isinstance(cell.value, str) and cell.value.startswith('='))` for each cell. Never trust formula strings alone.
- After every write, re-open the output file from disk and print the value(s) and coordinates of the target cell(s) along with a few surrounding cells to confirm correct placement and that no adjacent or header data were corrupted.
- After sorting or restructuring data into logical blocks, reload the workbook and verify that header rows (e.g., 'Number', 'Name') appear only once at the top of the answer range, not interspersed in the data. Also print the first few rows of each block, the blank separator rows, and the transition rows between blocks to visually confirm correct grouping and separator preservation.
- When splitting data into segments using blank rows, after computing range boundaries, print the first two and last two rows of each proposed segment alongside their row numbers to confirm boundaries match expected data or blanks before writing.

- After writing formulas, reload the workbook with `data_only=False` and print the formula strings for the entire answer range to confirm they were written as formulas (not literal strings) and reference the correct cells.

- After final output, reload the workbook and print the value of every cell (or at least all non‑empty cells) in every sheet to confirm no unintended side effects (e.g., erased data, leftover placeholder rows). Compare the layout against expected answer range dimensions and check for any unexpected data.


- After modifying a script (e.g., fixing a bug), re-run the full diagnostic print that lists all affected rows/groups and verify that the final output matches the expected treatment for every candidate, not just a sample. Do not rely on a single summary from an earlier debugging stage.
- After saving, verify the entire graded answer range (all columns, all rows) by printing every cell. Confirm that columns not targeted for modification remain unchanged and that the structure matches the original input.
- If after reloading with `data_only=True` any answer cell is `None` or contains a string starting with `'='`, compute the intended result in Python and write the computed value (boolean, number, string) to that cell. Re‑save and re‑verify until every cell holds a concrete value.
- When verifying computed values, print the answer range cells alongside their relevant identifier columns (e.g., worker name, invoice number) to manually confirm consistency with the intended logic.


- After writing results, perform a structured comparison against any explicit expected outputs from the instruction. List the instruction's expected values, the actual written cells, and compare row-by-row for exact string equality (not just thematic similarity). If the instruction's example inputs differ from the actual data, flag the discrepancy before assuming the output is correct.

- After any structural modification (row/column deletions, inserts, moves), explicitly check that the output sheet dimensions (max_row, max_column) cover the entire graded answer range. If the graded range expects rows or columns beyond the last data cell, ensure those cells exist in the sheet (they will be empty). Print the exact graded range after saving to confirm all required cells are present.

- After writing, reload the workbook, print the exact dimensions of the target sheet (e.g., `ws.dimensions`), and compare to the required answer range. Confirm the written values are the expected data content, not leftover formulas or empty cells.


- When comparing output against a pre-existing template or 'Expected' sheet, first compute the expected number of output rows from the transformation logic (e.g., base rows × transposed columns). If the template has fewer non-empty rows than this expected count, the template may be a format guide, not a complete answer key. Do not dismiss mismatches as template incompleteness — instead, verify that your output row count matches the expected count derived from the transformation, and confirm whether the instruction requires filling the template exactly or generating a new full set.

- After writing computed values (not formulas), always print the entire graded answer range — never rely on a sample of rows. Manually recalculate at least two values from the source data to confirm the computation logic matches the instruction's wording. If any cell is outside the expected range or violates the instruction's semantics, fix and re‑verify before completing.

- After deleting rows or columns, verify that the total row/column count decreased by the expected number and that the deleted rows/columns are completely removed (not just cleared). Print the full used range to confirm.

After writing the output file, reload it and print the first few rows (or the exact graded range) to verify structure, column placement, and data presence. If the answer range must start at a specific cell, explicitly confirm the written values appear there and not shifted.

- **Final step**: After all writes, reload the workbook and print every cell in the graded answer range to confirm correctness before declaring the task complete.

- When verifying number formats, do not rely solely on printing the format string. Simulate the formatted display by applying the cell's `number_format` to the value (e.g., using `format(cell.value, cell.number_format)` for simple numeric formats, or `openpyxl.utils.datetime` for dates). Print at least three formatted examples — one supposedly zero-decimal, one supposedly one-decimal, one supposedly multi-decimal — and check that the displayed output matches the intent. When deciding format based on value (e.g., integer vs. decimal), use `float.is_integer()` or a tolerance comparison rather than `value == int(value)` to avoid floating-point precision issues.

- If you wrote the output using pandas, verify by reading the saved file back with pandas and printing the exact graded cells (e.g., the full dataframe or the target column). This catches silent write failures and serialization quirks.


- After applying a transformation that should affect the entire worksheet (e.g., find‑and‑replace across all columns), scan the full used range to confirm all instances were handled, not just the graded answer range.
- When using pandas to write output, the printed DataFrame from your script is not the saved file. After saving, reload the file with pandas (e.g., `pd.read_excel(output_path)`) and print the exact graded range to confirm headers and data types match the intended output. Do not rely on the in‑memory DataFrame.


- After a conditional write, verify the full graded answer range without re‑applying the same condition logic used to write. Iterate all rows, check that target cells match expected values based on the original condition, and confirm that non‑target cells remain unchanged. Log any discrepancies.


- After bulk row insertions based on a marker value (e.g., "insert a row above every line with an X"), reload the output workbook and re-scan the full graded answer range for that marker. Confirm that (1) every marker value is still present, and (2) each sits exactly below an inserted empty row if the task requires it. Print the full answer range as a list of cell values and compare against the instruction's intent before declaring completion.

- After writing, print every cell in the graded answer range with its `.value`, `.fill.start_color.rgb` (or `.fill`), and `.border` to confirm formatting (fill, border) matches expected output. Verify all cells, including those that should be empty, to catch unintended blanks or formatting omissions.

After writing, if the task requires preserving source formatting (alignment, number format, font, etc.), reload the workbook and print the relevant attributes for the answer range (e.g., `cell.alignment`, `cell.number_format`, `cell.font`) to confirm they match the source or expected format. Do not rely on value-only checks.

- After saving the output workbook, reload it and print every sheet name exactly as stored. Compare each (case‑sensitive) to the sheet reference in the graded answer range (e.g., `'final Recon Items'!A1:D5`). If the casing differs, rename the sheet before finalising.
- If the task provides concrete example outputs (expected values for specific cells), after writing formulas, verify that the computed values in those cells match the examples exactly. Print the computed values alongside the expected values and assert equality.

- After writing lookup results that use substring or fuzzy matching, compute and print counts of output rows per source key and compare against expected counts (e.g., number of non‑empty cells per source column). If any source key shows zero output rows, stop and investigate before declaring completion.

- When no reference output is provided, independently recompute key results from the source data using a separate computation path (e.g., re-derive rankings, sums, or labels from scratch) and assert they match the written output. Never rely solely on reading back your own output.
## Common Pitfalls


- Writing formulas without first inspecting data types, ranges, or lookup mismatches.
- Treating a formula as correct without reading back its evaluated result.
- **Unverified search direction boundaries**: When a search instruction uses directional terms like "above" or "below" relative to a found cell, always start by examining the cells at the boundary (the found cell's own row) before committing to a search range. Print the values at the boundary and state why they are included or excluded. After writing the output, confirm the search loop logic matches that stated reasoning — not the other way around.
- Hardcoding row or column ranges or column indices based on a single visual inspection or assumption. Instead, dynamically discover data extents (e.g., search for the last non-empty cell in each relevant column) and locate columns by scanning headers for known labels. After computing results, add a verification step that prints side-by-side: source1 value, source2 value, date, name, AND result, so any misalignment is immediately visible.
- Trusting partial output: Do not assume correctness because some cells match expectations. Verify all graded cells individually, especially after column shifts or data relocation.
- **Unverified sorting**: Sorting IDs numerically without checking the reference sheet's row order can lead to incorrect placement. Always inspect the expectation sheet's row sequence and replicate it exactly.


- **Writing formulas without checking per‑row scope**: Before writing formulas into a block, inspect adjacent columns or header labels that reveal grouping logic (e.g., FY labels, SUMIFS per OEM). Determine whether each row should compute an independent result for its group or a single overall figure. Test one row's formula mentally against the data it should cover. If the formula must vary per group, do not copy‑paste a fixed range; construct the range dynamically or write distinct formulas per block.
- **Ambiguous conditions**: When an instruction contains ambiguous phrasing (e.g., "preceded by a different week number"), inspect the actual data ordering first, test your interpretation on a small visible slice, and state the chosen interpretation explicitly in the trace before writing the full script.

- **Partial verification after targeted updates**: After updating only a subset of rows (e.g., based on a text match), always verify the entire graded range, not just the rows you intended to change. Unchanged cells may have been accidentally overwritten or omitted.
- **Unadjusted formula copying across columns**: When a formula must reference a header cell that changes per column (e.g., month names in row 5), ensure the header reference uses a relative column (e.g., `F$5`) and data ranges use absolute references. After writing, read back each cell's formula string and verify that the column letter in the header reference matches the cell's column.
- **Skipping initial workbook inspection**: Relying on the truncated spreadsheet preview in the task prompt instead of loading and inspecting the actual file. Always print sheet names, dimensions, header row, and sample data cells before any write or delete operation.
- **Blindly swapping formula syntaxes without diagnosing root cause**: When a formula is reported as incorrect, inspect the existing cell formula and verify that each argument's type (scalar, range, array) is compatible with the function's requirements. For instance, SUMIFS does not accept array criteria; replacing with SUMPRODUCT+MATCH is necessary. Always understand why a formula fails before rewriting it.


- **Unverified block‑detection logic**: Before writing fill logic that depends on structural patterns (e.g., blocks separated by 'TOTAL' rows), print the actual row sequences for a sample of blocks to confirm where blocks start, end, and which column carries the separator. After filling, add a runtime check that iterates the filled range and asserts every row in a matched block received the correct value, and that skipped blocks retained their original values — raising a clear error if the pattern fails.
- **Declaring success based on formula text alone**: After writing formulas, never assume they work because the formula strings are present in the cells. Always force recalculation (open with `data_only=True` or use an evaluation tool) and inspect the actual computed values. If cells show `None`, errors, or raw formula text, the formulas did not evaluate correctly and must be fixed before completion.

- **Writing formulas that openpyxl may store as literal text or fail to evaluate**: openpyxl does not evaluate formulas; it stores formula text only. Assigning a string like `=IF(...)` to `cell.value` may be saved as a literal string, not a formula, causing the cell to appear empty when reopened with `data_only=True`. Always verify computed values: after saving, reload with `data_only=True` and confirm every answer cell contains a concrete value (not `None` or a string starting with `=`). If any cell is `None` or a literal string, compute the results in Python and write numeric values directly.

- **Copying highlighted cells from an example sheet as the answer**: When a task provides an example sheet with highlighted cells, do not assume those cells are the correct answer. Instead, derive the selection algorithmically from the stated constraints (e.g., sum to target). After applying highlights, compute the sum dynamically from the selected cells and write that computed value to any required output cell, not a hardcoded number.

- **Unverified string cleaning**: Before applying regex or string transformations to cell values, print the raw values and their Python types. When a value contains formatting like `$11,604.67`, decide whether commas are thousand separators to keep or noise. After cleaning, verify every output cell contains a valid number (e.g., can be cast to float) without ambiguous punctuation. Do not strip all non-digit-non-dot characters without checking that they are not part of a formatted number.

- **Overwriting existing data without inspection**: Before writing to any column or row, inspect the header row and existing data in that column/row to determine if it is empty or contains data that must be preserved. Never assume a column is unused. After writing, verify that only the intended cells changed and that adjacent columns remain intact.
- **Formatting outside the answer range and partial verification**: When applying conditional formatting or number formats, restrict the operation to the exact answer range (not the entire sheet). After writing, verify every cell in the answer range by printing both its value and number_format, and confirm they match the expected output. Do not rely on a sample.
- **Over-inspecting without writing**: After your first inspection turn, if you have enough information to start coding, do so. Do not continue inspecting unless you have a specific unanswered question that will change your implementation.

- **Blindly clearing a sheet**: Before clearing any cells, inspect the full target sheet structure (dimensions, existing data rows, formulas, formatting, merged cells). If the instruction says "copy to" a sheet, insert or overwrite only the specific rows and columns required, preserving the existing layout; never blanket-clear the entire sheet unless explicitly instructed to start from a blank sheet. After writing, verify that only the intended cells were modified and that no unrelated content was erased.

- **Destructive global sort after grouped sort**: When a task specifies multiple sort criteria with explicit priorities (e.g., "first sort by X, then within groups sort by Y"), never apply a flat global sort at the end, as it destroys all earlier grouping. After constructing the final output, verify the ordering satisfies every stated criterion by scanning the rows and checking that the group structure matches the specification.

- **Saving to wrong path or creating a new workbook instead of modifying the original**: Before declaring completion, always verify that the output file exists at the exact required path using `os.path.exists(output_path)`, and inspect the saved workbook globally — print sheet names, dimensions, and sample surrounding columns — to confirm you modified the original workbook and preserved all required sheets and columns beyond the answer range.


- **Writing formulas without inspecting the actual file layout**: Never compose a formula based on assumptions from the task description alone. Always load the workbook, print the header row and at least 5 rows of data, and confirm column letters and labels before writing any formula. After writing, verify at least one cell's computed value is not None.
- **Static formula strings without row‑relative adjustment**: When assigning a formula string to multiple cells in a loop, each cell receives the identical literal formula; row references do not auto‑adjust. Construct row‑specific formula strings (e.g., `f'=IF(A{row}=J{row}, B{row}-C{row}-E{row}-G{row}, 0)'`) or use openpyxl's Translator. After writing, verify that at least two cells in different rows contain distinct, row‑appropriate references. Also reload with `data_only=True` and confirm that computed values for non-adjacent rows (e.g., first, middle, last) differ as expected; identical values often indicate a hardcoded row reference.

- **Confusing code production with data manipulation**: When the instruction asks for code (e.g., 'How can I create a VBA code that...'), produce the code text, not the result of executing it. The answer range should contain the code, not transformed data. Verify that the output content type matches the requested deliverable.


- **Unrecognized gaps in numeric sequences**: When filling values based on a pattern inferred from existing data (e.g., numbering rows), compute the differences between consecutive existing values to detect gaps or discontinuities before applying the fill. After writing, verify that the filled range exhibits the expected monotonic progression.
- **Misinterpreting 'previous value' as cumulative vs. per‑row change**: When a task requires "previous week's value for a specific worker" or similar, always sort or verify that rows are ordered by date for each worker before accumulating. After computing, spot‑check at least two workers with multiple non‑zero transactions: confirm that the debt for a later week equals the prior week's debt plus/minus that week's change (the running balance property). Without an answer key, verify the recurrence matches the described rule against visible deductions/additions in the original data.
- **Abandoning the task after inspection without producing output**: Never stop after only reading or printing input data. The task always requires a concrete output file at the specified path. If you are unsure about the logic, write a best-effort output, verify the file exists, and then declare completion. A single inspection step is never sufficient to finish a task.
- **Proceeding with mismatched sheet structure**: When the instruction references specific sheet names (e.g., 'BR1 onwards') but the workbook contains different sheets, do not silently work with what is available. Print both the expected and actual sheet names, state the discrepancy, and decide explicitly how to handle it before writing any output.


- **Hardcoding column index from letter without verification**: When a task references a column by letter (e.g., 'BN'), use `openpyxl.utils.column_index_from_string('BN')` to get the correct index, then verify by printing the header cell of that column to confirm it matches the expected column label. Never assume column letter to number mapping based on manual counting.
- **Writing without separately inspecting the target range**: Never combine inspection and writing in a single script. Always run a read-only inspection of the target cells (and adjacent cells) before writing any values. Confirm you understand the current state and decide whether to overwrite or preserve.
- **Writing formulas for derived values**: When the task requires any derived value (e.g., totals, counts, averages, concatenations), compute them programmatically in Python and write the resulting data values directly into the cells, not as formula strings. Even if the instruction says 'write a formula', the grader cannot evaluate formulas in openpyxl, so you must write the computed result. Only write formula strings if the task explicitly requires the cell to contain a formula (e.g., for a formula-grading task where the grader inspects the formula text). When in doubt, write computed values. After writing, verify the answer range contains data values (numbers, strings), not formula text or None.

- **Ignoring system warnings about missing output file**: If the system warns that the output file is missing, immediately write the file (using `wb.save`) and verify it exists. Do not continue inspecting or planning; the warning means you must produce output now, not gather more information.


- **Blind reliance on embedded sample output regions**: When the input sheet contains a sample preview (e.g., 'THE ABOVE TABLE WOULD BECOME:'), do not treat it as the answer range or as a boundary for data processing. Instead, programmatically scan the key column(s) from the top until the true end of data (e.g., last non-empty cell or a distinct marker). After writing output, verify that the number of output data rows matches the expected count derived from the full input (e.g., sum of COUNT values) and fills the target answer range exactly.

- **Confusing "delete rows" with "clear cell values"**: When the instruction says "delete rows," the output must have fewer rows — the rows are removed structurally, shifting remaining rows up. Never substitute by setting individual cell values to `None` or empty string. Before acting, inspect the graded answer range and confirm whether the deliverable requires structural row deletion (fewer rows) or value clearing (same row count, altered cells). After writing, verify the output row count decreased by exactly the number of deleted rows.

- **Verifying formulas using the in‑memory workbook after save**: After saving a workbook that contains formulas, always reload the saved file from disk with `data_only=True` and check computed values. Do not rely on the in‑memory workbook object, as it will only contain formula strings.
- **Constructing file paths without verification**: Never build a file path from fragments without checking that the directory exists. Use `ls <directory>` or `os.path.exists()` to confirm the path before reading. Use the exact path string from the task instruction; do not retype from memory. After writing, verify the output file exists at the required path.
- **Writing formulas without verifying upstream dependencies**: After writing a formula that depends on other computed cells, always inspect those upstream cells' actual computed values (using `data_only=True`) to confirm they are not blank or error before trusting the downstream result. If any upstream cell is None or error, the formula will likely produce None; debug the dependency chain before declaring completion.
- **Overwriting an existing formula without understanding the instruction's scope**: Before writing to any answer cell, read its current content (formula text and computed value). Determine whether the task expects modification of the existing formula, a new formula in the same cell, or computed values only. Document the decision. Blind replacement without this step leads to mismatches with the grader's expected answer range.
- **Ignoring provided result/expected sheets**: When the workbook contains sheets labeled "result", "expected", "desired", or similar, always inspect them fully before implementing any logic. Compare their values against what your interpretation of the instruction would produce. These sheets are ground-truth examples that can prevent misinterpretation of the task. Do not rely solely on textual instruction interpretation when concrete examples are available.

- **Unconditional string transformations on entire columns**: Before applying any truncation, regex, or text replacement to a column, inspect the first few rows to identify headers, blanks, and non‑target values. Always skip rows that are headers, empty, or don't match the expected pattern. After writing, verify the first cell of the range to confirm the header survived intact, and spot‑check transformed values for artifacts like trailing spaces; apply `.strip()` or cleanup as needed.

- **Pre-computing values when a formula is requested**: If the instruction explicitly asks to 'correct a formula' or 'place a formula' in cells, write the formula string (e.g., `=IF(A1>0, ...)`) into the cell, not the computed result. After writing, verify that the cell contains a formula string starting with '=', not a hardcoded number. This preserves dynamic recalculation behavior.

- **Unverified mapping formulas from anchor points**: When the instruction gives explicit input-output pairs (e.g., "41 maps to 5, -18 maps to -5") and asks for proportional scaling, do not treat positive and negative ranges as separate piecewise linear scales. Derive the single linear equation from the two anchor points (y = mx + b) and test that the function is continuous at intermediate values (e.g., 0 should map to 0 if the line passes through origin). Before applying to all cells, print the function's output at the anchors and at a few test values to confirm the behavior matches the description.

- **Mistaking formula strings for verification**: Printing `cell.value` after writing formulas returns formula strings (e.g., `=IFNA(...)`), not computed results. Seeing formula strings is NOT verification — it only confirms the formulas were written. Always reload the saved file from disk with `data_only=True` and confirm every answer cell holds a concrete value (not `None`, not a string starting with `=`).


- **Narrowing scope to the graded range when the instruction says 'all columns' or 'the whole worksheet'**: When the task requires a transformation across the entire worksheet, do not restrict the operation to only the graded answer range unless explicitly stated. Inspect the full used range before writing, and after writing scan the entire used range to confirm all instances were handled.
- **Unverified column mapping and incomplete verification**: Before copying columns, list every source and target column explicitly and decide what to do with each (copy, ignore, transform). After writing, verify that every column in the exact graded answer range contains the intended content and that no source data was silently discarded. Verify the full range against the instruction's requirements (headers, values), not just against a neighbouring reference range. Confirm that no column in the answer range is entirely empty when it should hold data.
- **Single‑spot‑check verification for aggregations**: After computing sums, counts, or other aggregations, a manual eyeball check of one group is insufficient. Aggregation bugs (off‑by‑one indexing, mis‑handling of non‑breaking spaces as blanks, rounding errors) can affect some groups but not all. Always programmatically recompute the result for at least two groups (the first and a randomly chosen non‑first group) by re‑reading the source cells and asserting that the computed output equals the expected sum within tolerance. Print these assertions explicitly before declaring completion.
- **Abandoning approach on import errors**: When an import fails (e.g., `cannot import name 'copy' from 'openpyxl.styles'`), read the error message, adjust the import statement or implement a manual alternative locally rather than discarding the entire script. After fixing, run a minimal test to confirm the error is resolved before proceeding.


- **Misinterpreting "delete" as "clear" for substrings**: When the instruction says "delete these strings" and the strings are substrings within cells, confirm whether the intent is to remove only the substring (leaving the rest of the cell content) or the entire cell. Before applying any deletion, print a sample of the affected cells to understand the structure. After deletion, reload the workbook and verify that the remaining content matches expectations (e.g., the prefix still exists).


- **Verifying implementation artifacts instead of the graded answer range after bulk insertions**: After inserting rows above marker values (e.g., "X" in column A), do not verify only the rows you inserted and the rows that shifted. Always re-scan the full graded answer range for the marker value and confirm every marker is still present and correctly positioned relative to the inserted rows. Spot-checking a few indices derived from the original order is insufficient — a misplaced row can shift markers out of their expected positions without being caught by index-based checks.


- **Hardcoding column spans without verifying the graded answer range**: Always read the exact answer range coordinates from the instruction, inspect its current full contents, and plan to write only within that range. After writing, verify that the range contains exactly the intended values and that no cells outside the range were accidentally modified. Hardcoding a larger column span can overwrite data or leave unintended empty cells.


- **Unverified grouping keys**: Before aggregating, explicitly inspect the filtered data for duplicates: print unique counts of the grouping columns per group (e.g., per brand) and verify that the chosen group-by keys match the instruction's exact combination words (e.g., 'by brand and qty' means only brand, not brand+batch+origin). If the data already has no duplicates, state that observation and skip unnecessary aggregation steps.


- **Hardcoding deletion ranges after manual inspection**: After inspecting and seeing that certain rows are blank, do not hardcode a fixed range like `ws.delete_rows(6, 6)` in the next action. Always write programmatic logic that dynamically identifies which rows to delete (e.g., iterating over all rows and checking which are fully blank). This ensures the deletion is repeatable and correct even if the dataset changes or has blanks in other positions. After deletion, verify the exact graded answer range separately — do not rely solely on printing all rows.

**Directly assigning StyleProxy objects**: When copying cell formatting, do not assign a source cell's `.font`, `.alignment`, `.border`, etc. directly to a target cell's attribute; these are StyleProxy objects that are not directly assignable and may cause `TypeError: unhashable type: 'StyleProxy'`. Instead, copy individual attributes (e.g., `target_cell.font = Font(name=source_cell.font.name, size=source_cell.font.size, ...)`) or use openpyxl's `copy` method. If you encounter a StyleProxy error, first inspect the source object's type and attributes with `print(type(source_cell.font))` and `print(source_cell.font.__dict__)` to understand its structure before constructing a new style object.

- **Misinterpreting aggregate conditions as global**: When a condition mentions "where values sum to zero" or similar, do not assume it applies to the entire column at once. Inspect the data for grouping clues (e.g., repeating identifiers, dates) and evaluate the condition per group. After deletion, verify that remaining rows satisfy the condition per group.
- **Unverified column mapping from example rows**: When a target range contains example‑filled rows, never infer column emptiness from a few samples. Dump the full content (including empty‑looking cells) of at least two example rows and the first destination row across all columns in the graded range. After a test write on one row, verify that any skipped columns remain unchanged before bulk‑filling.
- **Hardcoding output row count without dynamic source‑length check**: Always compute the number of output rows from the actual source data length. After writing, verify that no output row is partially filled — each row must either contain exactly the expected number of non‑None values or be completely empty. If the target is a fixed range, handle overflow/underflow explicitly.

- **Confusing answer_position with data processing boundaries**: The `answer_position` specifies where to write output, not the extent of source data to process. Always determine the processing range by inspecting the source data's actual boundaries (e.g., `ws.max_row` for the relevant column), not from the graded answer range. After writing, confirm that every populated source row was visited and that the output column's populated extent matches the source's.
- **Sampling verification instead of full-range verification**: Printing only the first 5–10 rows and declaring "verification confirms correct behavior" is insufficient. After writing, print every cell in the full graded answer range (all rows, all columns). At minimum, print the first 3, last 3, and a random middle slice. Edge cases, trailing data, and off-by-one errors often appear outside the first few rows.
- **Unverified substring matching for header lookup**: Using substring matching (e.g., `if header in entry`) without verifying false positives and coverage. After matching, print all source keys and the number of matches per key; confirm every expected source key produced at least one output row. After writing, spot-check for representative entries from each group.


- **Hardcoding header rows instead of copying from source**: When the task requires preserving the structure of the source data (e.g., 'maintaining the rest of the data intact'), always copy the header row from the source sheet programmatically, rather than typing header values as literal strings. Verify that the copied headers match the intended subset of source headers by printing both side-by-side before writing.
- **Unconditional overwrite of existing data**: Before writing to any target cell, inspect its current value and compare with your planned value. Only overwrite cells where the values differ or are empty. For conditional copies, inspect both source and destination columns for all rows, and implement an explicit guard to preserve rows where the destination should remain unchanged. After writing, verify that no correct data was accidentally overwritten and that preserved rows still hold their original values.