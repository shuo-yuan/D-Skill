---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow


**Deliverable Type Check**: Before any manipulation, re-read the task to identify the deliverable type. If the task asks for a macro, VBA, or formula, the deliverable is the code itself, not the resulting data. Insert the macro/formula into the workbook and verify its presence (e.g., check VBA project for macros). Do not replace with precomputed data unless the instruction explicitly asks for output values.


**Mandatory Verification**: After any write operation (including deletions, formulas, formatting), you MUST re-open the saved workbook with `data_only=True` and read the entire answer range to confirm correctness before calling TASK_COMPLETE. Never skip this step.


- When the manipulation is straightforward and you have already inspected the workbook and printed the relevant data ranges, combine inspection and targeted write operations into a single action to reduce turn count.

- For deletion or filtering tasks, after inspecting the structure, implement the operation in a single self-contained script that opens the workbook, performs the modification, and saves. Then verify the output with a read-back of the target range. This brackets the action with inspection and verification while minimizing tool calls. Always include a read-back of the entire target range (not just a few cells) in the same or immediately following step, and confirm the content type (values, formula strings, or None) before declaring completion.

- - When combining, first print sheet names, dimensions, and the exact data ranges you plan to read and write before any write operations.

When combining inspection and write into a single action, include a read-back within that script (e.g., read the target cell and print its value) to confirm the write succeeded before saving, but this in-script check is not a substitute for the mandatory post-save verification. After saving, you must re-open the workbook with `data_only=True` and read the answer range before calling TASK_COMPLETE. This two‑stage verification prevents silent failures where formulas are written but not evaluated.

- This includes applying a formula to a range: write the formula to all cells in one script, then recalc and verify the computed values within that same action.


**Mandatory Inspection**: Before any write operation, you MUST open the workbook and inspect every sheet: list sheet names, print dimensions, and display data. Confirm the target sheet and range exist and match the task's `answer_position`. Never skip this step.

- Before deploying formulas to a range, test the formula on a single cell with actual data: write it, run `recalc.py`, and read back the computed value with `data_only=True`. Verify the result matches expectations before scaling to the full range.
## Inspection


Before any manipulation, open the workbook and inspect every sheet: list all sheet names, print the dimensions (rows × columns), and display up to 25 rows of data for each sheet.

- When the task describes a conditional trigger based on a specific cell (e.g., 'if cell I2 is empty...'), inspect that cell's value before designing any logic. Print the cell's value and branch your implementation accordingly.

- Compare the listed sheet names against every sheet name mentioned in the task instruction. If a named sheet (e.g., 'BR1') is absent, explicitly report the mismatch and decide how to proceed — do not silently fall back to the only available sheet when the task demands a multi‑sheet scope.
- If the task instruction mentions specific cell references (e.g., 'cell I2', 'the value in A1'), after inspecting sheets, explicitly read and print the value(s) of those cells to confirm their current state before proceeding.
- When constructing cross‑sheet references (e.g., INDIRECT, VLOOKUP across sheets) that derive sheet names from cell values, print `wb.sheetnames` and compare against the derived names. If any expected sheet is missing, decide on a fallback (e.g., skip, error) before writing formulas. This reveals naming nuances (e.g., trailing spaces), missing‑data patterns, and expected structures. Print all column headers and confirm the header row. Never assume the prompt's snippet is complete.

```python
for row in ws.iter_rows(min_row=1, values_only=True):
    print(row)
```

- Build a header dictionary from the identified header row (not necessarily row 1): `headers = {str(cell.value).strip().lower(): col for col, cell in enumerate(ws[header_row], 1) if cell.value is not None}`. Use `headers.get('column_name')` to retrieve column indices, and raise a clear error if a required header is missing. Print the dictionary to verify before using it. This avoids fragile hard-coded column numbers and is resilient to reordering.

For each data region, explicitly extract header rows, row keys, and column keys from the actual sheet data. Print these mappings (e.g., `source1_names`, `source1_dates`) to visually confirm alignment between sources. Use these mappings to drive comparisons.

- Before writing any mapping logic that joins tables on a subset of columns, examine the full schema of both source and target sheets

- Before implementing any iterative or stateful algorithm (e.g., restarting counting, cumulative conditions), print the full input data and manually trace the logic on a small subset to confirm the algorithm matches the instruction. Cross-check with a manual example before writing any code. (headers, sample rows, unique key combinations) to determine whether the natural join key requires additional columns beyond the obvious ones. Print unique key counts and sample duplicates to confirm that the chosen key yields the correct granularity.

- **Pre-action type check**: Before applying any transformation to cell values, inspect the actual Python type of a sample cell (e.g., `type(ws.cell(2,1).value)`) and its `repr()` to confirm whether cells contain strings, datetime objects, or other types. Do not rely on printed summaries that may show formatted representations.
- **Regex/data cleaning pre‑check**: Before applying a regex or string‑based cleaning to cell values, inspect the raw `repr()` of a sample of cells to understand the exact content. Test the cleaning logic on a few representative cells, printing the original and cleaned values side‑by‑side to confirm the intended numeric payload is preserved and decimal points are not merged from unrelated fragments. After writing, re‑read the answer cells and verify the cleaned values match expectations.
Before writing to any output range, read and print the current values, formulas, and styles of the entire target range (all rows and columns) to identify structural features such as headers, constraints, empty cells, and data boundaries. Decide whether to overwrite, preserve, or merge only after inspecting.
If the answer range already contains some values, compare them to your computed results. If they match, the task may be to complete a pattern rather than replace all; preserve or extend as appropriate.

- For multi-table sheets, print the exact cell coordinates and values of every header row you intend to use as a key. Verify that each expected label appears exactly once at the position your code will target before using it.
- After reading headers, sample and print at least three raw data rows per source sheet to confirm which column holds the values to aggregate. Validate extracted numeric fields with `isinstance(amount, (int, float))` and log the first few extracted pairs to catch mis-mapped or empty values early.
- After inspecting structure, verify the target output range is empty (or contains expected placeholder values) before writing any formulas or values.


- Before performing any string-based filtering or replacement, print the relevant column's values using `repr()` to reveal exact content (e.g., trailing spaces, line breaks). This ensures matching logic accounts for actual cell content.
- When the task instruction provides text conditions (e.g., prefixes, delimiters), never trust the instruction's character encoding. Inspect the actual cell values with `repr()` to confirm the exact characters (full‑width vs ASCII commas, dashes, etc.) and build match logic using the observed characters.
- **Header row identification**: Never assume row 1 is the header row. Inspect the first few rows of each sheet to locate the actual header row by searching for known column labels. When copying headers to a destination sheet, inspect the destination to determine the correct placement (e.g., whether the sheet is empty or already has a header). After copying, verify the output header row contains the expected column labels (non‑empty strings, not numbers or blanks).
- When the task description contains conflicting or ambiguous range specifications (e.g., "F to M" vs "F - L"), inspect the actual data in the disputed columns for a sample of rows to determine the correct scope. Print the values to confirm whether including or excluding those columns would change the deletion outcome. Document the chosen condition in a comment before executing the delete loop.

- Before deleting columns or rows based on content matching (substring, regex, or case-folding), print a sample of matched and unmatched headers/keys from the actual data to confirm the filter logic targets the intended set. For example, print the first 5 headers to keep and the first 5 to delete.

- Before using extracted data from one sheet to populate another, print a few rows from the target sheet to see what's already there, and manually compare a sample of extracted keys/values against the target's existing rows to confirm the mapping logic (e.g., that the extracted invoice numbers correspond to the right rows). This catches mismatches early.

- After inspecting the sheets, explicitly state the data structure (which columns hold keys, which hold values, the row ranges for each table) before computing any outputs. This confirmation step catches misalignment early.

- When the task involves deleting rows based on a string match, before writing any deletion code, list all sheet names, print the entire column's values (or enough rows to locate the search phrase) on every sheet, and confirm the exact row index of the search phrase. This ensures you modify the correct sheet and delete the intended rows.
- When the task involves mapping data between sheets, always print the first few rows (headers and data) of both source and target sheets to confirm column positions, data types, and that the key column values align (if mapping by row order). If the key values differ, build a dictionary-based mapping using the identifier column instead of relying on row indices.

- When translating computed indices (e.g., from a list) into spreadsheet row numbers, print a complete mapping of (index, row_number, value) for the target sheet and visually confirm at least the first and last entries before writing.
- When the workbook contains reference or example sheets (e.g., 'Manual Result'), inspect them with `data_only=True` to see computed values and confirm the expected output structure, data types, and dimensions before writing any code.
- When the data layout may be sparse or non‑contiguous, scan the full column range (all rows) of the relevant key columns to identify where actual data values reside. Print the row indices and values to confirm the pattern before writing any formulas or lookups.


- When a task asks to fix an existing formula, first evaluate the original formula's result and inspect all referenced cells' values and formats to identify the exact source of the error (e.g., circular reference, wrong condition). Only then write a corrected version.
- For tasks that involve conditional copying or filling based on patterns (e.g., copying values downward while a condition holds in another column), print the full target range (all rows and columns involved) to understand the exact layout, including any index rows, header rows, and blank patterns. Confirm the pattern and the boundaries where copying should start and stop before writing any code.
- When the task involves a transformation that should apply to all data (e.g., sorting, filtering), inspect the full sheet's `max_row` and `max_column` to determine the complete data extent, not just the graded answer range. Confirm that your operation covers all populated rows, even if the answer range is a subset.
- When a task involves modifying or writing a formula in a specific cell, first print the surrounding rows and columns (at least 5 rows above and below, including the target cell) to understand the data layout and detect patterns that inform correct formula construction.

- When a task refers to a sheet by ordinal (e.g., "sheet 2"), first list all sheet names in workbook order and print the name and index of the sheet you intend to target. Confirm explicitly before performing any operation on it.

- When the task specifies output in certain columns but the answer range includes additional columns, inspect the current content of those columns (e.g., headers, existing data, blanks) to determine whether to leave them untouched, populate from source, or clear them. Print the inspection results to document the decision before writing.

- **Never rely on task preview alone**: Always open the workbook and inspect the actual sheet headers and data rows before writing formulas. The task's printed preview may not reflect the actual column layout or data content.
- **Inspect the full dataset before writing logic**: When the task provides a printed preview (e.g., `spreadsheet_content`), treat it as incomplete. Open the workbook and inspect the entire data range for columns that influence logic, not just the first few rows. Print at least the first, middle, and last rows, and confirm that patterns (e.g., delimiters, string formats) hold across the full dataset.
- If the preview is truncated (e.g., ending with '... (N more rows)'), treat it as incomplete; always open the workbook and inspect the full sheet to determine actual data extent before writing any logic.

- When the workbook contains a reference or example sheet (e.g., 'Desired Results'), treat it as the ground truth for output structure. Before writing, inspect its exact row order, row count per category, and any subtle structural details. Write the output to match that reference, not an independently computed version, unless the instruction explicitly asks to derive. After writing, verify that the output sheet matches the reference row-by-row on the key columns.

- When the task states that the number of data rows is variable, avoid hardcoding row ranges based on a single inspection. Determine the data range dynamically at runtime (e.g., iterate until an empty cell in a key column, or use `ws.max_row` but verify the last row contains data). After writing, confirm the output row count matches the input data count (excluding headers).

- Before executing any conditional fill (e.g., populating cells based on values in other columns), print all distinct values of the condition columns for the full target range. Confirm the logic covers only the intended rows and that no unexpected values accidentally trigger a write. After writing, spot‑check a few output rows to verify the condition held.

- Before any deletion or filtering operation, print the full content of the entire target range (all rows and columns) to identify structural patterns (header rows, totals, blank separators, non-data rows). This ensures that only intended data rows are removed and no structural rows are accidentally shifted into the answer range.

- Print merged cell ranges for each sheet (e.g., `ws.merged_cells.ranges`) to understand the layout and avoid writing into merged regions.

- When mapping source data to a fixed set of output categories, print unique values from the source column and compare against expected target categories. If mismatches exist (plural/singular, case, spacing), create a normalization dictionary to map variants before grouping or writing. This prevents silent data loss from near‑miss mismatches.


- **Pre‑aggregation type check**: Before computing aggregates (SUM, AVERAGE, etc.) on a column, sample at least 5 rows of that column and print the type and value of each sampled cell to confirm they are numeric (int/float) and not text or empty. Use `isinstance(v, (int, float))` and handle conversion if needed. This prevents silent zeros from numbers stored as text.
- Before writing to a prescribed answer range, compare the source sheet's actual dimensions (max_row, last non‑empty row in key columns) against the answer range boundaries. If the source data extends beyond the answer range, confirm whether the transformation should apply to the full data or only the subset, and document the decision. Never assume the answer range covers all data without checking.
- After inspecting all sheets, review the printed data to identify any discrepancies between source and reference sheets (e.g., differing row counts, missing keys) and adjust your processing strategy accordingly. Do not ignore the inspection output when designing the manipulation logic.

- Before writing any transformation code, inspect the target sheet's full dimensions: print `ws.max_row` and `ws.max_column` to determine the actual data extent. Use these discovered dimensions to drive iteration ranges rather than hardcoding numbers from a preview snippet. If the task says 'across all columns' or similar, ensure your transformation covers all columns, not just the answer range, then verify the answer range specifically.

- When reordering one block of rows to match another by a multi-column key, before writing, verify that the key is unique in both the source and target blocks (e.g., assert `len(map) == len(source_rows)` and `set(target_keys) == set(source_keys)`), and log any mismatches. If keys are not unique, adjust the mapping strategy (e.g., use a composite key with additional columns) and re‑verify.

- When the sheet contains multiple tables or expected output blocks, print the actual data and the expected data side-by-side (e.g., iterate rows and print both blocks' cell values) to visually confirm structural alignment before writing any manipulation code.

When the dataset is small (e.g., fewer than ~50 rows), print all rows to fully confirm structure and data types before writing any logic. This catches subtle patterns or anomalies that a 25‑row sample might miss.


- When the task involves selecting or filtering rows based on a column's value (e.g., rows with 'X'), print the entire column's values for the full data range to identify all occurrences and confirm the condition's exact form (literal vs. formula-derived). This prevents missing sparse values or misinterpreting formula results.

- **Style‑aware filtering**: When the task involves selecting or filtering cells based on formatting (e.g., background color, font color), inspect the relevant columns' fill, font, and pattern properties (e.g., `cell.fill.start_color.rgb`, `cell.font.color.rgb`) alongside values. Print a mapping of cell coordinates to style attributes for at least the first 25 rows and any rows that match the criteria. This ensures the filtering logic correctly identifies the intended cells.

- When the sheet may contain multiple data regions or hidden content, print the full data region (all rows and columns) using `iter_rows` with generous bounds to reveal the complete layout before writing. This prevents overwriting existing data blocks or misidentifying source ranges.
- When the task involves restructuring data (e.g., removing blank rows, compacting), print the full used range (all rows from min_row to max_row) to identify blank regions, data boundaries, and header positions before writing any logic.

- Before using an aggregate value (sum, count, etc.) to decide which rows to delete or filter, print all rows with their values and any grouping identifiers. Confirm whether rows belong to independent groups or a single entity. Never assume the entire sheet is one group unless the task explicitly states it. If grouping is ambiguous, treat each row independently or use explicit grouping columns.

- When the task says "complete the rest", "given some examples", or shows partial data in the answer range, treat the existing filled cells as immutable and only write to empty cells. After writing, verify that the original values remain unchanged.
## Writing Output


- Before writing final output, read the required sheet name and cell range from the task. If the sheet does not exist, create it explicitly. Then read back the sheet names to confirm the target sheet is present before writing any data.

### Safe Row Deletion
When deleting rows based on cell content with `openpyxl`, iterate from the bottom up (`for row in range(ws.max_row, 1, -1)`) to avoid index shift. Always guard string methods with `isinstance(cell_value, str)` before calling `.startswith()` or similar.

- Before writing formulas, inspect the header row and a few data rows of the target sheet to confirm column layout and reference logic. This ensures formulas align to the correct columns and reference values.
- Before writing formulas, also print the source data ranges (the cells that will be referenced) row-by-row using `data_only=True`, showing the first 5–10 rows and a tail sample to confirm they contain the expected data. If a source column is empty or sparse, adjust the formula logic accordingly. This prevents logic errors from unseen data anomalies.
- Before writing formulas to the full range, test the formula on a single cell: write it, run `recalc.py`, and read back the computed value with `data_only=True`. Confirm the value matches expectations (e.g., cross‑check with a known example) before scaling to the entire range. This catches formula errors early and prevents writing a full column of broken formulas.
- When formulas use row offsets (e.g., `r-4`) to reference source data, print the actual rows that the offsets will target for a few output rows, and confirm they contain the expected data before writing the full range.

- When modifying an entire column (e.g., setting all values to a constant), first inspect the column’s contents to distinguish header rows, summary/constraint rows, and data rows. Apply the change only to the intended rows, and verify after writing that non‑target rows (headers, labels, constraint values) retain their original content.



When deleting columns, iterate in reverse (`for c in range(ws.max_column, 0, -1)`) to avoid index shift. Before deleting any rows or columns, print the list of indices to be deleted and confirm they match the intended criteria.

- If using a conditional write strategy (e.g., fill only blanks, preserve existing values), first inspect the target cells to confirm whether the existing content matches the task's expected output. If it does not, overwrite the entire range instead of preserving.

- When the instruction describes a "system to automatically" perform a lookup or reference, prefer dynamic formulas (e.g., INDIRECT, INDEX/MATCH) over hard-coded values. Place the formulas in the exact graded range specified, not a precomputed static output, unless the task explicitly asks for values. However, when the lookup logic is complex (e.g., involving string parsing, multiple conditions, or variable delimiters that are difficult to express in a single formula), compute the values in Python and write them as static results, verifying correctness with a read-back. This avoids fragile formula construction and is often more reliable for complex matching tasks.

- When an instruction says results should derive from multiple source columns, inspect the target cells to determine the expected shape (single values, lists, separate columns). Never default to string concatenation unless the existing data or explicit instruction confirms that format. If ambiguous, test a small slice first. After writing, check that the data type and cardinality of values in the answer range match the apparent pattern of existing data in the target sheet.
- When the task asks to fix an existing formula error (e.g., #N/A, #REF!), inspect the formula and its dependencies, correct the logic (e.g., adjust ranges, apply TRIM), recalculate, and verify the computed values are correct before applying any formatting. After changes, confirm the answer range contains data (not None, empty, or error values).
- When the task provides an `answer_position` or `graded answer range` field, read it exactly and restrict all data writes to that range. Before writing, double‑check that your loop or vectorized operation covers the exact start and end coordinates (row and column indices) and does not extend beyond the graded cells, unless the task explicitly requires structural changes elsewhere.

- After inspecting, if the task requires overwriting the range with new data, clear all cells in the target range (set to None) before writing to eliminate leftover data from prior operations.
When compacting data (e.g., removing blank rows) and writing into a fixed answer range, after writing the compacted rows, explicitly clear any remaining cells in the range to ensure no residual None or blank values from the original data remain. Then verify the entire range.
- When saving, write directly to the exact output path provided by the task (e.g., `wb.save(output_path)`) without intermediate copies, temporary files, or renaming. This avoids path‑mismatch errors and ensures the grader finds the file in the expected location.
Prefer a single script that loads the workbook, performs all mutations, and saves directly to the output path in one atomic step. This minimizes turn count and eliminates path‑misalignment risks.
- Before writing the script, explicitly list the computational rules derived from the instruction (e.g., which columns to aggregate, conditions, formulas). This ensures correct translation of task requirements.
- When the task asks for a 'single formula' per cell (e.g., one formula per row in a column), translate multi-condition logic directly into a self-contained formula per cell and apply it across the answer range in one pass. Avoid creating intermediate helper columns or multi-step workflows unless the instruction explicitly requires them. Always verify computed results afterward.

- When the task asks to 'display' a specific numeric result or 'hardcode' a value, write the computed value directly into the cell, not a formula. The graded answer expects the final value, not a formula string. Verify by reading the cell value — it should be the number itself, not text starting with '='.
When the task asks 'how can I...?' or 'create a formula...', verify the answer cells contain formulas or instructional text, not static precomputed values, unless the graded answer range is explicitly for final outputs.

- When filtering rows based on date conditions, handle both `datetime` objects and string representations (e.g., using `dateutil.parser.parse` or `datetime.strptime` with an appropriate format). Compute cutoffs using `timedelta` (e.g., `max_date - timedelta(days=30)`). When copying matching rows to a new sheet, preserve the original cell's `number_format` and style by copying `cell._style` and `number_format` (e.g., `new_cell._style = src_cell._style; new_cell.number_format = src_cell.number_format`). Also ensure only the required columns (matching the graded range) are copied.

- When the task requires deduplication before sorting (e.g., removing duplicate (col B, col C) pairs), apply deduplication and blank-filtering as a preprocessing step before any sorting or ordering logic. Build a seen set of the dedup key (e.g., `(ws.cell(r,2).value, ws.cell(r,3).value)`) and skip rows where key columns are None or whitespace. Print the count of kept vs. discarded rows to confirm the filter.

- When deleting rows based on grouping criteria (e.g., duplicates, relationships), first group the rows and print a summary of each group with row numbers and relevant cell values. Confirm the groups match the intended deletion logic before executing the delete.
- When collecting rows into a list before deletion, sort them in reverse (`sorted(rows, reverse=True)`) before calling `ws.delete_rows(r, 1)` to preserve original indices of remaining rows.
- When deleting consecutive rows, combine them into a single `delete_rows(r, count)` call to reduce iterations and avoid index‑tracking errors.

- Before running a custom script that writes to the answer range, test it on a small, representative subset of data (e.g., 5–10 rows) and print the results to confirm correctness. This is critical when the script implements stateful logic (e.g., sequential labels, cumulative sums) to catch systematic errors early.

When testing a formula on a single cell, use actual data rows (e.g., first, middle, last) and manually compute the expected result from the raw cell values. Print both raw values and computed result side‑by‑side to verify logic before scaling to the full range.

After scaling the formula to the full range and saving, immediately re‑open the workbook with `data_only=True` and read the entire answer range to confirm computed values are present (not None). If any cell is empty, run `recalc.py` and re‑read. Do not proceed to any other step until this verification passes.

- When constructing cumulative formulas per group (e.g., running total by worker), use a technique that finds the last prior row for the same entity (e.g., `LOOKUP(2,1/($D$2:D{r-1}=D{r}),$J$2:J{r-1})` or `XLOOKUP` with reverse search). After writing the formulas, re‑open with `data_only=True` and verify that each cell contains a numeric value, not an error or None.

- At the start of the writing phase, extract the exact output file path and the answer range coordinates from the task's `answer_position` or `graded answer range` fields, and confirm you are working with those values before any save or write operations.

- When extracting substrings based on tags or delimiters, use string methods (split on the tag, then split on the delimiter, with a fallback to empty string) and verify the extraction on a sample of rows before applying to the full range.

- Before writing any loop or range-based operation, inspect the source data to determine the actual row and column boundaries (e.g., `max_row`, header row, last data row) and use those dynamic values rather than hardcoded numbers, unless the task explicitly specifies a fixed range.

When deleting rows relative to a marker cell (e.g., "delete all blank rows above the cell containing 'Code'"), first locate the marker by scanning the column for an exact match, then determine the rows to delete based on their position relative to the marker. Print the marker's row and the list of rows to delete before executing.

- When enriching rows with data from a lookup sheet, build an in‑memory dictionary from the lookup sheet in one pass (e.g., key → (category, subcategory)), then iterate the source rows and append matched values directly. This is more efficient than repeated cell‑by‑cell searches and reduces transcription errors.
- When the task asks for a calculation method (e.g., 'how can I calculate...', 'create a formula to...'), write formulas that compute the result dynamically rather than precomputed static values. This preserves the workbook's live calculation capability. Only hardcode values when the instruction explicitly asks for a static result or a specific numeric value.


- **Verify total‑row formulas**: When writing formulas into a total or summary row, after saving, re‑open the workbook with `data_only=True` and confirm that the total cells contain computed numeric values, not None or formula text. If any cell is None, run `recalc.py` and re‑read before calling TASK_COMPLETE. Do not assume the formulas evaluated correctly.
- When constructing formulas that reference columns by letter, first print the header row and map each required field to its column letter. Confirm the mapping in a comment before writing formulas. Never assume column positions from the task description alone.

- When writing a self-contained script, include the post-save verification within the same script: after saving, re-open the workbook with `data_only=True`, read the answer range, and print the values. If all values are correct, you may call TASK_COMPLETE immediately. This pattern is reliable and reduces turn count.

- If the target sheet already exists, inspect its contents (headers, data rows, and any pre-existing data) before writing. Decide whether to overwrite, append, or merge based on that inspection. Do not blindly overwrite headers or existing data that should be preserved.


### Row Insertion
When inserting rows (e.g., `ws.insert_rows(r, amount=1)`), first test the insertion on a small slice: print the values of the rows around the insertion point before and after the operation to confirm the shift direction and that the inserted rows are empty. After applying to the full range, re-open the workbook and read the answer range to verify that the inserted rows are blank and the original rows are in the correct positions.

- When transposing or collecting values from another sheet into a destination range, after clearing the target range, write the values and then verify that the output contains exactly the intended values — no extra blanks, no leftover original content, and no cells that were not explicitly written. Print the source list and the output row side‑by‑side to confirm.

- **Never hard-code row ranges** (e.g., `for r in range(2, 6)`) when writing to a target sheet. Always determine the target range dynamically from the sheet's actual dimensions: use `ws.max_row`, scan for the last data row in key columns, or compute the range from the source data count. Hard-coded ranges break when sheets have unexpected extra rows, headers, or different dimensions than assumed. Before writing, inspect the target sheet's current row count and content, then clear or adjust programmatically.
- **Answer range boundaries are not data extent**: When the task specifies an answer range like `F2:F71`, do not assume rows 2–71 are all populated. Always inspect the sheet to find the actual last data row (e.g., scan for the first empty cell in a key column). Process only populated rows, and after writing, clear any leftover cells in the answer range that should be empty.

- When conditionally copying values from one column to another (e.g., copy only if source is non‑empty), first inspect the current values of both the source and target columns for all rows. Identify which target cells should be updated and which must remain unchanged. After writing, verify that rows where the source was empty retain their original values.

- When replacing cell values using a lookup (e.g., old names to new codes), build a dictionary mapping old→new and apply it with `dict.get(key, key)` (or `mp.get(v, v)`) to safely preserve the original when no mapping exists. Print the full mapping dictionary and a sample of transformed values before saving to quickly verify correctness.
## Verification


**CRITICAL: After every save, re-open the workbook and read the answer range. Do not call TASK_COMPLETE without this verification.**
- **Before TASK_COMPLETE, confirm**: (1) I re-opened the workbook with `data_only=True` and read the answer range cell-by-cell; (2) all cells contain computed values (not None, not formula text); (3) I used dynamic row bounds, not a hard-coded range; (4) the output row count matches input data extent. If any check fails, do not complete.
- **Printed script output is not verification**: Even if your script prints the written values to stdout, you must re‑open the saved workbook and read the answer range directly. Printed output may be incomplete, from a different source, or not reflect what was actually written to the file. Always verify the file contents.

- After every write to the answer cell(s), read back the exact value(s) in that range.
- When writing transposed results (e.g., multiple matches spread across columns), after writing, read back the full target region (all columns that should contain transposed data) to confirm all expected values are present, not just the first column. If the answer range is a single column but the task implies horizontal expansion, re-read the instruction to confirm the expected output shape (concatenated vs. multi-column) before writing. Confirm the cells hold computed data values (not formula text, not None, not empty) and that the type matches expectations (e.g., a datetime, not a string). Check that the shape matches expected dimensions. Print the final computed value from the exact output cell to confirm it was written as expected.
- After saving, re-read the output file and print the target cell to double-check persistence.
- After any structural change (inserting columns/rows), re-scan the affected range to confirm exact positions of source data before copying. After copying, print a before/after comparison of the exact answer cells the grader will inspect to verify each value transferred correctly.
- When ordering output by an external key list, compare the sequence of identifiers in your output against the exemplar's identifier column row by row before writing. If they diverge, adjust ordering logic before writing to the graded range.
- For lookup‑and‑write operations, compare the set of requested lookups (key, column) against the available keys in the source data. If any combination is missing, confirm the desired output convention (e.g., leave blank, write #N/A, write a default) before writing.
- Before marking a task complete, re‑open the output workbook and read back the graded answer range using `iter_rows(values_only=True)`, printing each cell's value. Compare the row count and first‑column values against expectations from the source data. Verify that all expected properties (non‑empty, numeric, formatting) match and that the cells contain data values, not formula text or None.

- When writing formulas, run `recalc.py` on the workbook after saving to force calculation, then re-read the answer cells to confirm computed values (not formula text or None). openpyxl does not recalculate on save by default, so a read-back without recalculation will show None or stale values.
- When verifying cells that contain formulas, open the workbook with `data_only=True` (openpyxl) or equivalent evaluation mode. This ensures you read computed values (numbers, dates, strings) instead of formula text or None. Never rely on `ws.cell(r, c).value` without `data_only=True` to check formula results.
- If the task provides concrete example input‑output pairs, immediately compute and compare the resulting cell values against those examples after writing formulas. Hard‑code a minimal check (e.g., `assert ws['H2'].value == 1272`) to confirm formula correctness before scaling to the full range.
- After saving, print the header row and the first and last data rows of each output block to confirm data placement and range length. Verify that no block expected to contain data is entirely empty (unless the task explicitly allows emptiness); this catches off-by-one errors and missed mappings. Flag any empty block so you can revisit the logic.

- After inspection, record the expected row count and matching row indices (or the criteria that select them) for each output block. During final readback, compare the actual output dimensions and row identifiers against this record to catch missed rows or off-by-one errors.
- Before sorting or reordering data, inspect the pre-existing rows: print row count, first few rows, and check for duplicates. After sorting, verify: (a) row count unchanged, (b) sort key columns are in the expected order (ascending/descending), and (c) no unintended duplication. Print sample output rows to confirm before completing.
- After writing formulas, re‑open the workbook with `data_only=True` and print at least the first, middle, and last cells of the answer range. Verify that all printed values are non‑None and match the expected types. If any cell is None or empty, recalculate with `recalc.py` and re-read with `data_only=True`. **Do not call TASK_COMPLETE until you have confirmed the answer cells contain computed data values (not None, not formula text).**
- After clearing cells or resetting formatting (e.g., removing background color), re-read the affected cells' values and fill properties to confirm emptiness and absence of styling. Print a sample to verify.
- For any write operation that uses conditional logic (e.g., fill only blanks, string matching), after writing, re-read the answer range and confirm that the intended cells were actually modified. If no cells changed, re-examine the conditional logic against actual cell contents (use `repr()`).
- If the task involves constraints (min/max bounds, target totals, etc.) embedded in the sheet, after writing output re‑read those constraint cells and compare each computed cell against them. Print a comparison for a representative sample to confirm compliance before marking the task complete.
- After any transformation that modifies the answer range (deleting columns/rows, inserting, reordering), re-open the workbook and read at least the first and last rows of the graded region to confirm the expected columns/rows remain and the output shape matches expectations.
- After deleting rows based on emptiness conditions, re-open the workbook and print the entire graded answer range cell by cell to verify that rows intended for deletion are gone and rows with partial content are preserved. This catches over-deletion when the emptiness check uses a subset of columns that differs from the graded range.

- After populating the answer range via lookup or mapping, verify that rows which should be distinct (e.g., having different existing values in other columns) do not all share identical lookup results unless that is explicitly expected. Print a sample of rows with identical lookup results and cross-check with source data to ensure correctness.
- After any row deletion operation, re-open the workbook and read the entire answer range to confirm the correct rows were removed and the remaining rows are intact.
- After any row deletion or filtering that reduces the number of data rows, also verify that the output workbook's `max_row` matches the expected row count (based on the answer range or the number of remaining data rows). Print the full answer range cell by cell to confirm that cells beyond the last data row are empty (or contain expected placeholder values) as required by the task. This ensures the grader sees the correct structure and no stale data.
 When verifying after a deletion or structural change, print every cell across all columns of the answer range — not just the first column. A single‑column summary leaves multi‑column integrity completely unverified. For tasks that delete rows above a key row (e.g., "Invoice No."), verify that the key row is now the first row in the sheet and that all rows below it remain unchanged.
- Before marking complete, re-read the task instruction and compare each requested change against the current workbook state. Confirm that all required fixes, calculations, and formatting have been applied and that the answer range contains the expected data (not None, empty, or error values).
- After saving, confirm the output file exists at the expected path (e.g., `os.path.exists` or `ls`). Then re‑open and inspect the answer range to confirm persistence.
- After saving, print the full output path (e.g., `print(output_path)`) to confirm the file was written to the correct location before re‑opening.

- Before calling TASK_COMPLETE, re-open the workbook with `data_only=True` and read the entire answer range. Print the exact cell values, fill colors, and sheet names. Confirm all cells contain computed data values (not None, not formula text) and match the requirements. This confirms formatting, deletions, and persistence. After writing output, also read and print the last 5 rows of the answer range to confirm they contain data (not all None). If any trailing row is entirely empty, adjust the output range to exclude it unless the task explicitly expects empty rows. If a reference or example sheet is provided, compare the first row of your answer range against the corresponding row in the reference to confirm the fill order and values match. If the reference shows row‑major order and your output is column‑major, adjust before completing.
- **Save confirmation is not content verification**: The workbook save confirmation (e.g., `max_row`, `max_column`) only confirms the file was written, not that cells contain expected computed values. After any write, especially after formulas, always read back the answer range with `data_only=True` (and after `recalc.py` for formulas) to inspect actual cell contents before declaring completion.


- **After writing any formula and saving, never call TASK_COMPLETE before re‑opening the workbook with `data_only=True` and inspecting the evaluated value of every answer cell.** If any cell returns `None`, `#CIRCULAR REF!`, or another anomaly, diagnose and fix before completing. A successful write does not guarantee a correct result.
- After conditional copy or fill operations, print the modified range and compare key rows (boundaries around blank cells, index rows, and the start/stop points) against the pre‑modification state to confirm no unintended overwrites occurred. Ensure that header rows or index values were not overwritten by copied data.
When writing to a column that may contain pre-existing data, after writing, re-read the entire column (or at least the full range of rows that were originally populated) and confirm that only the intended cells were changed and that other rows retain their original values. This prevents silent corruption of unrelated data.

- After clearing a destination sheet (or any range) and writing new data, re‑open the workbook and read back the entire answer range (first and last rows at minimum) to confirm the clearing was successful and the new data is present with the expected row count and data types. Do not rely on the write confirmation alone.

- After writing to the answer range, re-open the saved workbook and print the exact range (e.g., F2:H10) cell by cell to confirm that every cell contains the intended data type (values, not headers or code) and no unintended rows (like duplicate headers) have leaked in. If any cell looks out of place, investigate before declaring completion.

**Final verification before TASK_COMPLETE**: Re‑open the workbook with `data_only=True`, read the entire answer range, and confirm every cell contains a computed value (not None, not formula text). If any cell is empty, recalc and re‑check; if still empty, debug the write operation. Only then call TASK_COMPLETE.

- After any custom script that generates patterned values (e.g., sequential labels, IDs), re‑open the workbook and print a sample of the output (first 20‑30 rows and rows near transitions) to verify the pattern matches the expected rules (e.g., resetting per group, correct progression). Do not assume the script is correct just because cells are non‑empty.
- **If any answer cell is None after recalc.py, do not call TASK_COMPLETE.** Diagnose the formulas: re-check references, test on a single cell, and if the formulas still fail to evaluate, fall back to computing the values in Python and writing them as static numbers. Do not leave None cells in the graded range.
- **File existence checks are not content verification**: Confirming that the file exists (e.g., `ls -l`, `os.path.exists`) does not guarantee that answer cells contain the expected computed values. Always re-open the workbook with `data_only=True` and read the answer range after any write, even if you already checked that the file was saved.

- After any deletion or row/column modification, re-open the workbook and read the exact answer range specified in the task's `answer_position`. Print its contents and compare the row count and dimensions against the pre-modification state. If the task specifies a target range, the output file must contain that exact range with the intended data. Flag any discrepancy before calling TASK_COMPLETE.

- After any write operation, re-open the workbook and read the exact `answer_position` range (including the sheet name) cell by cell to confirm data is present there. If the data was transposed or collected, also verify that the output contains no blank cells within the populated region (unless the task permits), and that the required fill and border styles are applied to every cell with a value. If the sheet does not exist, create it and re-write the data to that sheet before proceeding.
- When completing a partially filled range, after writing, re-open the workbook and print the answer range. Compare each cell against a pre-write snapshot to confirm that existing values were preserved and only empty cells were filled. Print both states to document the comparison.

- When deleting rows relative to a marker cell, after deletion confirm the marker cell is now at the expected row (e.g., row 1) and that all rows below it remain unchanged.

- If you performed the mandatory post‑save verification within the same script (re‑opening the workbook with `data_only=True` and reading the answer range) and the values are correct, you may call TASK_COMPLETE immediately. No additional separate verification step is required.


- After any bulk-clear or bulk-write operation that replaces existing data, read back the entire answer range and also inspect the rows immediately following the last written data to confirm no stale data remains from the original content. If the cleared range was larger than the written data, verify that the extra rows are empty and contain no unintended values.
- After writing, verify that all required outputs (e.g., aggregated totals, key computed values) are present within the graded answer range. If any expected value is missing or placed outside the range, adjust the layout before completing.
- After any copy or merge operation that relied on row order, re-open the workbook and print the first three rows of the key column and the written column from both source and target to confirm that each value was written to the correct row. If misalignment is found, redo using explicit key-based mapping.
- After any transformation that should produce varied output, count the unique values in the answer range. If every cell is identical and the original data likely wasn't, treat this as a red flag and re‑inspect the logic before completing.

- When the task requires a mathematical transformation (e.g., linear interpolation, scaling), after writing, verify the mapping by checking at least three points: the maximum, minimum, and zero (if applicable). Confirm the output values match the expected rule before completing.

- When the task specifies number formatting (e.g., decimal places, currency), after saving, re-open the workbook and print the `number_format` and raw value of representative cells. Verify that at least one example of each required format is applied correctly before calling TASK_COMPLETE.

- If your write script did not include a read-back of the saved file (re-opening with `data_only=True` and printing the answer range), you must run a separate command to do so before calling TASK_COMPLETE. Never call TASK_COMPLETE without having seen the actual cell values from the saved file.

- After rearranging rows by key, inspect columns that originally contained formulas to confirm whether the formulas or their computed values were written. If the instruction does not specify, sample a few cells post‑write to decide which is expected. If formulas are lost, re‑implement the rearrangement to preserve formula objects (e.g., copy cell objects instead of reading `.value`). Then verify the final answer range contains the intended content.

- After any row‑grouping or summarization operation, always re‑read the output workbook and inspect the resulting data rows. Specifically: (1) count the number of output data rows and verify it matches the number of distinct group keys from the source, (2) spot‑check at least one sum from the output against a manual per‑group calculation, and (3) confirm that no all‑None empty rows appear in the graded range unless explicitly intended.
- When a task mandates specific number formatting (decimals, comma removal, blank‑for‑zero), always take two steps after writing: (1) ensure cell values are rounded or coerced to the required precision (e.g., `round(total, 2)` before assignment), and (2) re‑open the saved workbook and verify by reading back a few formatted cells' `value` and `number_format` to confirm they meet the spec. Never rely solely on setting a format string without checking the actual stored value's precision.


- After any write operation, even if you only modified other cells, re-open the workbook and read the exact graded answer range (as specified in the task's `answer_position`). Verify that all cells in that range contain the expected values and that no cells were unintentionally cleared or overwritten. This is especially important when performing string manipulation or regex operations that might accidentally affect adjacent cells or the header row.


- **Plain‑value type check**: When the task expects plain values (not formulas or macros), spot‑check a few answer cells after writing to confirm they contain the expected data type (e.g., string, number, date) and not formula text or VBA code. This prevents silent mismatches where a formula string is written instead of a computed value.

- **Never rely on printing formula text as verification** — after writing formulas, always re‑open the workbook with `data_only=True` and print the evaluated values of every answer cell. If any cell shows `None` or a formula string, run `recalc.py` and re‑read before calling TASK_COMPLETE.
- Before saving, when using computed logic (e.g., duplicate detection, grouping), print the intermediate results (list of keys, counts) to verify the logic matches expectations before writing to the sheet.
- After copying rows or data between sheets, verify that each column in the output range has consistent data types across all rows (e.g., all date columns contain `datetime` objects, not a mix of strings and datetimes). Print `type()` and `repr()` for a sample of cells in each column to catch mixed formats that could cause downstream failures. Normalize types unless the task explicitly requires preserving source-level variants.
- When verifying, also print a few rows above and below the answer range to confirm that adjacent data remains untouched and no unintended shifts occurred.

- After any row deletion, if the answer range contains only headers and no data rows (and the task expects data), the deletion was too aggressive. Do not call TASK_COMPLETE; re-examine the deletion logic and restore the expected rows.
## Common Pitfalls


- **Unverified formula evaluation**: Writing formulas without recalculating and reading back with `data_only=True` (or equivalent). The output may be empty or incorrect. Always run `recalc.py` after saving, then re-read the answer range with `data_only=True` and compare against expected values when available. Never rely solely on file existence or the absence of Python errors; you must inspect cell values. If any cell remains None after recalc, do not call TASK_COMPLETE—fix the formulas or fall back to computing the values in Python and writing static numbers. Skipping verification after writing formulas is a common cause of empty graded ranges.

- **Brittle whole‑number checks via string patterns**: Checking for a decimal point or using string methods to determine if a value is a whole number is fragile and breaks on formatting differences. Instead, convert to `float` and use `.is_integer()`, wrapped in a `try`/`except` to safely fall back to a default (e.g., `whole=False`) for non‑numeric values. This correctly implements the semantic condition and avoids runtime crashes.

- **Inspecting formula results with `data_only=False`**: After writing formulas, never re‑open the workbook with `data_only=False` to verify results; the cells will show formula text, not computed values. Always re‑open with `data_only=True` after running `recalc.py` to confirm the computed values are present.

- **Bypassing provided artifacts**: When the task asks to diagnose and fix a provided macro, formula, or script, first read and analyze the artifact, identify at least one concrete error, and produce a corrected version. Do not replace it with a completely new solution unless the instruction explicitly asks for a different approach.

- **Applying formatting before fixing formula errors**: When the task requires fixing a formula error, do not apply formatting or other cosmetic changes until the formula logic is corrected and verified. Formatting empty or error cells hides the underlying problem and leads to empty graded ranges.

- **Assuming fill order without inspecting reference data**: When a reference or example sheet is provided, inspect it to determine whether data is filled row‑major or column‑major, and whether there is grouping or expansion. Do not assume a particular order; trace the mapping from source to reference before writing output. After writing, compare a sample row from your output against the reference to confirm the ordering matches.
- **Heuristic guessing for subset‑sum tasks**: When the task asks to find a subset of values that sum to a target, avoid manual guessing or heuristics. Instead, use exhaustive combinatorial search (e.g., `itertools.combinations` over all subset sizes) if the number of candidate values is manageable. Print the indices and values of the found combination for verification before writing to the spreadsheet.


- **Skipping pre‑action inspection and post‑action verification**: Before executing any transformation script, open the workbook and print the exact values, formats, and styles of the target range to confirm assumptions. After writing output, re‑read the answer range cell‑by‑cell and confirm values, formatting, and absence of errors. Do not rely on file size or save confirmation alone. If any warnings (e.g., deprecation) appear during execution, investigate and verify the intended operation succeeded before marking the task complete.
- **Hardcoding results when a formula or macro is expected**: When the task mentions creating a macro or formula that produces a result in a specific cell, do not precompute the value and write it as a static number. Instead, place the actual computation (formula or macro-triggered output) in the target cell. After writing, verify the cell contains a formula or computed value, not a hardcoded scalar, unless the task explicitly asks for a static snapshot.
- **Misinterpreting 'macro', 'VBA', or code‑debugging requests**: When a task asks to **create** a macro, VBA solution, or script, the deliverable is the code itself, not its computed output. Insert the macro code into the workbook (e.g., as a VBA module) and verify its presence after saving (e.g., check `wb.vba_archive` or that the file is saved as `.xlsm`). Do not replace the code with precomputed data values unless the instruction explicitly asks to run the macro and capture its output in a cell range. For debugging tasks where the answer range is a data block, produce the corrected final data values in that range, not the code. Always inspect any reference sheet to confirm the expected output type.
- **Script naming conflicts**: Naming a script after a standard library module (e.g., `inspect.py`, `csv.py`) can cause circular import or shadowing errors. If you encounter an import error, rename the script to a unique name (e.g., `xlread.py`) and verify it runs before proceeding.

- **Calling TASK_COMPLETE without verifying the output file**: Even if your script printed success messages, you must re-open the saved file with `data_only=True` (after running `recalc.py` if formulas were written) and read the answer range cell‑by‑cell to confirm the data is correct. If any cell shows `None`, an empty string, or raw formula text instead of a computed value, do not declare completion — investigate and fix first. Skipping this step leads to empty or incomplete answer ranges.

- **Hardcoding a special‑case value based on a summary term when explicit examples show a different format**: When the instruction contains ambiguous phrasing (e.g., a term like 'BOTH' vs. explicit example outputs like 'Group 1, Group 2'), inspect the spreadsheet's existing data and examples to resolve the ambiguity. If no resolution is found, default to the format shown in the explicit examples. Do not hardcode the summary term without checking.

- **Hardcoding a fix for a broken formula**: When a task asks to fix a formula error (e.g., #REF!, #N/A), do not replace the formula with a static value. Instead, inspect the formula's structure and correct the invalid argument (e.g., column index, range). After writing, verify the cell contains a corrected formula (use `data_only=False` to see formula text) and that it evaluates to the expected value. Only hardcode a value if the task explicitly asks for a static result.

- **Writing to the wrong sheet**: Ignoring the `answer_position` sheet specification and writing output to a different sheet (e.g., `Sheet1` when the answer range is `Sheet2!A1:AG10`). Always extract the sheet name from `answer_position`, create it if missing, and verify after writing that the data is on that sheet.

- **Using row counts or dimensions as sole verification**: Printing the number of rows written or the max_row value is not a substitute for reading and printing the actual cell values of the answer range. After any write, you must re-open the workbook and print the values (e.g., using iter_rows) of at least the header row and the first and last data rows to confirm content, not just shape. Never call TASK_COMPLETE based on row counts alone.

- **Assuming key uniqueness when reordering blocks**: When reordering rows to match a target order by a multi-column key, verify that the key is unique in both source and target and that all keys from one block appear in the other. Without this check, rows may be silently dropped or misaligned.

- **Overwriting pre-existing data without inspection**: Writing to a column that already contains data without first reading its current contents and verifying which cells should change. Always read and log the target range before writing, and after writing, re-read the entire column to confirm only the intended rows were modified and that other rows retain their original values.
- **Hardcoding row ranges from answer_position without verifying data extent**: Assuming the answer range covers exactly the data rows without checking `ws.max_row` or the actual last populated row. Always inspect the sheet's actual dimensions, compare them against the expected range, and handle any mismatch explicitly before looping.

- **Misinterpreting 'per X' as global aggregation**: When the instruction says 'per brand' or 'for each category', the aggregation must be done within each group, not across all data. Before coding, re‑read the grouping phrase and confirm the interpretation in comments. After computing, verify that the number of output rows equals the number of distinct groups in the source (unless filtering is intended). If they differ, the grouping logic is likely wrong.

- **Conditional copy without target inspection**: Writing a script that copies values from one column to another based on a condition (e.g., non‑empty source) without inspecting the target column's existing values beforehand can overwrite data that should have been preserved. Always inspect both source and target columns fully, and after writing verify that rows where the source was empty remain unchanged.