---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow


After gathering enough information to understand the task (sheet structure, data patterns, target ranges), immediately transition to writing the output file. Do not continue exploration beyond what is needed to inform the write phase. Always produce a concrete output file at the required path.
## Inspection


- Print the **entire** dataset (all rows, all columns) at the start of every task before designing any logic. This reveals headers, data types, grouping dimensions, non-contiguous layouts, and edge cases that affect the solution. Print the name, dimensions, and ALL cell values for every sheet in the workbook before writing any code. Do not skip sheets even if they appear empty or irrelevant. If an output sheet already contains data or formatting, treat it as a template—decide explicitly what to preserve versus overwrite.

- Before any transformation, inspect ALL sheets in the workbook, especially sheets named "After," "Expected," or "Target." If such a sheet exists, treat it as a worked example defining the intended output. Load and print the contents of any example sheet. Reconcile your understanding of the task against what that sheet actually shows before writing code.
- Dump the **entire** target data range in one pass before deciding on a write strategy. Sampling only the first/last N rows hides repeating sub-headers, blank separators, and duplicate patterns that affect the transformation logic.
- Before modifying any cell, inspect its current state using `print()` or direct attribute access. Check value, fill, font, alignment, and number_format of at least one cell per target column. Example: `print(f'Cell {cell.coordinate}: value={cell.value!r}, fill.start_color={cell.fill.start_color.rgb!r}')`

- Before writing to a column identified by letter (e.g., BN), confirm its numeric index. Read the header row and search for the column letter, or use `openpyxl.utils.get_column_letter()` to map indices. Never assume a column letter maps to a small index — letters like BN correspond to high indices (e.g., 66). Print the mapping for all target columns before writing.
- When grouping or aggregating, inspect ALL columns that partition the data (e.g., employee numbers, regions, categories) not just the obvious one (e.g., week). Use a tuple of all partitioning columns as the grouping key. After building grouped structures, print the keys alongside their aggregated values to verify correct segmentation.
- After dumping the data, use the detected dimensions (`ws.max_row`, `ws.max_column`) or `ws.iter_rows()` with no arguments to define iteration ranges. Never hardcode cell ranges (e.g., `A1:A4`) based on assumptions or partial snippets — always derive ranges from actual workbook inspection.
- After loading the workbook, print the coordinate, `repr(value)`, type name, and `number_format` for every cell in the target range. Example: `for row in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=ws.max_column): for cell in row: print(f'{cell.coordinate}: {repr(cell.value)} ({type(cell.value).__name__}), format={cell.number_format}')` This reveals mixed data types (e.g., datetime objects vs. ISO strings) that would otherwise cause incorrect transformations.

- Read exact sheet names from `wb.sheetnames` before accessing any sheet. Never rely on sheet names from the task instruction — they may differ in capitalization, spacing, or spelling. Use the names exactly as returned by `wb.sheetnames`.
- Before modifying a target cell, inspect its full context: (a) the cell's current formula/value and `number_format`; (b) all cells referenced in its formula, including edge cases (e.g., the upper bound of a MAX range); (c) any cells affecting conditional logic (e.g., the IF condition). Use multiple exploration passes if needed. After changes, verify the number_format is preserved and surrounding cells are undisturbed.

- Print cell values, fonts, and fills together in one pass before any modifications. Example: `for row in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=ws.max_column): for cell in row: print(f'{cell.coordinate}: value={cell.value!r}, font={cell.font.name!r}, fill={cell.fill.start_color.rgb!r}')` This reveals header styling, existing formatting, and data layout in a single inspection step.
## Writing Output


- Before writing to any answer range, print all non-empty cells in that range with `repr(cell.value)`. If cells already contain data, verify them against the task logic. Preserve existing correct values and only fill in missing or incorrect cells. Do not blindly clear the answer range unless the task explicitly requires regenerating all values from scratch.

- Compute values in Python and write the final results directly to cells — never write formula strings (e.g., `=IF(...)`) unless the task explicitly requires storing formulas. Formulas stored as text are not evaluated and cells appear empty to graders.
- When replacing or regenerating content in a target sheet, clear existing data in the target ranges first before writing new values. Use the answer-range dimensions as guidance for how many rows to clear and fill. After writing, check cells immediately beyond each table's data rows for stray values that the clearing step should have removed.
- When clearing backgrounds or formatting, use UNCONDITIONAL reset: `cell.fill = PatternFill(fill_type=None)` for every cell in the range. Do NOT gate clearing on existing fill attributes (e.g., `if cell.fill.start_color.rgb`). Apply clearing inside the same loop that writes new values, not in a separate pass.

- When copying rows from a source sheet, preserve ALL style properties from the source cell: font, fill, border, alignment, number_format, and protection. Use `copy()` on the source cell's style objects rather than resetting to defaults. Only modify number_format for columns that explicitly need different display formatting. After writing, spot-check that unmodified columns match the source formatting exactly.
- Before writing computed results to any answer range, explicitly clear every cell in that range (set to None or empty string). This prevents stale values from prior edits or template defaults from contaminating the output. After writing, scan the entire answer range to confirm only intended rows contain non-None values.
- When implementing conditional logic with multiple rules, decompose each sub-condition into a well-named boolean variable, then apply rules in priority order using if-elif. This makes the logic directly traceable to task instructions and prevents tangled nested conditions.

- When a task asks why a formula does not return a value or describes a displayed-value discrepancy, compute the result in Python and write the literal value — do NOT write a formula string. Load with `data_only=True` to read cached values, compute the intended result, and write it. After writing, confirm `cell.value` is a number/string, not a formula, unless the task explicitly requires formula correction.
## Verification


- After every `wb.save(output_path)`, run `ls -la <output_path>` to confirm the file was written to the exact expected location. Verify the saved file differs from the input file (check modification time or file size) to ensure you are not submitting an unmodified copy.
- After writing, read back answer cells to confirm they contain actual computed data, not formula text or None. Inspect answer-range cells to ensure they contain data values matching the required dimensions.
- Iterate the modified range and confirm `cell.fill.patternType` is `None` (or the expected default) for cleared cells. Spot-check at least one cell's value and formatting match expectations.

- After the initial write, load the output workbook and print every cell in the answer range with `repr(cell.value)`, `type(cell.value).__name__`, and `number_format` for key columns. Compare each against the specification. If any value, type, or format deviates, correct the logic, rewrite, and re-inspect until all cells match exactly. Also confirm the answer range is populated and not None. If the range is empty, trace the column indexing immediately. Do not declare completion until this loop passes.

- After writing, verify the output range against the task's `answer_position` (e.g., `A1:D7`). Read back the full target range including rows expected to be empty, and print cell values with coordinates. Confirm the range extends to the specified dimensions — populated rows plus any required empty rows. If the range is shorter than expected, clear or initialize the full target range before writing.
- After writing, load the output file with `data_only=True` and print every cell in the answer range using a loop that covers all targeted rows and columns — never filter with `if cell.value` or conditional printing that skips None/empty cells. Empty cells are as important as populated ones for confirming the output matches expectations. Confirm answer cells contain computed values (numbers, strings, booleans), not formula strings or `None`. When output involves computed aggregations (counts, sums, groupings), print a summary of the computed values alongside the expected logic. Example: print rows grouped by a key column and verify counts or sums match the intended intervals or thresholds. This catches logic errors before finalizing.
## Common Pitfalls


- When filling letter suffixes for URNs (e.g., '5a', '5b', '5f'): parse existing lettered values to set the letter counter correctly. For a pure numeric URN like '5', reset the counter to 0 (next blank gets 'a'). For an already-lettered URN like '5f', extract the letter index (f=6) and set the counter to that index so the next blank continues with 'g'. Do NOT reset the counter to 0 when encountering a lettered URN. After writing, verify that within each numeric URN group, letter suffixes increase strictly (a,b,c,...) with no gaps or repeats.