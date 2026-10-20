---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow

1. **Inspect the spreadsheet exhaustively before any manipulation.** Load the workbook with `openpyxl.load_workbook()`, list exact sheet names via `wb.sheetnames`, and print non-empty cells with coordinates, Python types, and number formats. Confirm headers, row/column ranges, data types, blank cells (`None`), merged cells, and any pre-filled example cells. Use `ws.max_row` to dynamically determine the last data row—avoid hardcoded ranges. When `answer_position` metadata is provided (e.g., sheet name and cell range), use it to identify the exact cells to modify, and always treat the first row as a header—start modifications from row 2 to protect it.
2. **Load the workbook twice for complex scenarios.** Use `openpyxl.load_workbook(path, data_only=True)` to read cached computed values (especially array formulas), and a separate instance without `data_only=True` for writing to preserve formulas. When formula chains are complex, fragile, or broken, read the ultimate source data directly, compute the result in Python, and write the literal value to the target cell.
3. **Plan transformations.** Identify grouping, sorting, mapping, filtering, and value replacement logic based on the inspection. For merges, build a lookup dictionary keyed by the unique identifier from the source data, then iterate over the master list sequentially: write the full source row when the ID exists, otherwise write an empty row containing only the ID. For per-category operations, group by category first. Use composite-key dictionaries (e.g., `{(city, date): value}`) for cross-table matching, normalizing string keys by stripping whitespace and converting to consistent case.
4. **Apply changes programmatically.** Use openpyxl to manipulate rows and cells, preserving formatting and using explicit column mapping and value transformations as needed. For extraction/filtering, work in this order: inspect raw data, apply filtering logic, clear the destination range, then write results. For row deletions, collect all target row indices first, then delete from the highest index downward to prevent index shifts.
5. **Verify output.** Reload the file and confirm changes match expectations. Save the modified workbook to the exact output path and verify the file exists before ending the turn.

- When filling missing values that extend an existing sequence, account for already-present intermediate values to maintain correct ordering. Check whether intermediate values are already present and need to be factored into the counter state.
- When checking for co-occurrence of multiple attributes within a group, aggregate per group first, then join back to rows. Use a composite key (e.g., employee + week) to identify groups meeting all criteria efficiently.
- To detect transitions (e.g., "only when preceded by a different value"), compare each row's value to the previous row while iterating. Track the prior value in a variable; flag rows where the value changes.
- For sparse column-based data with variable rows, iterate down each column and collect only non-None values: `if val is not None: values.append(val)`. This yields a clean list for expansion or cross-tabulation.
- Extract tagged values from unstructured text using a regular expression that captures the value between a known prefix and a delimiter (e.g., `r'Prefix-([^,]+)'`). Strip whitespace from the captured group.
- When distributing a quantity across bounded columns, use ordered greedy distribution: process columns left-to-right for positive residuals, right-to-left for negative. At each column, compute available capacity (max − current for addition, current − min for subtraction), set capacity to 0 if the current cell is 0, then apply min(remaining, capacity).
- Restrict all modifications to exactly the cells specified in the task's answer position or target range. Do not alter cells outside the target range.

## Inspection

- Before modifying any workbook, thoroughly inspect the spreadsheet layout: print sheet names, dimensions (`max_row`, `max_column`), data types, number formats (e.g., `dd/mm/yyyy`), and all non-empty cell coordinates and values. Identify header rows, data columns, and exact locations of headers, data, criteria, and output cells. Do not re-inspect the same data with different formatting; if uncertain, implement a best-guess solution and verify instead of re-inspecting.
- Verify sheet names with `wb.sheetnames` before accessing sheets to avoid `KeyError`.
- Look for embedded reference tables, "Expected Results" sheets, or notes that define desired output; deduce sorting/grouping rules by comparing reference data to source data. If the task description is ambiguous, the example sheet is the source of truth.
- Use `ws.max_row` (or equivalent) to dynamically determine the last data row; avoid hardcoded ranges and adapt to variable spreadsheet sizes.
- For keyword-based cell checks, normalize both text and keywords to lowercase for case‑insensitive substring matching (e.g., `any(kw in text.lower() for kw in keywords_lower)`).
- Reconcile headers by substring containment when keys are embedded in longer strings: use `if key in long_string` instead of exact equality when the key is guaranteed unique in the larger text.
- To find duplicate rows, collect column values and use `collections.Counter`; values appearing more than once are keys to extract duplicate rows.
- Check for extraneous columns that must be removed; note their numeric index (column Z → index 26).
- Always respect exact output ranges specified in the task (e.g., `F2:F71`); iterate only over those rows and columns.
- Load a second workbook instance with `data_only=True` to get computed numeric results when reading cells that may contain formulas. This is critical for diagnosis and verification.
- Check for merged cell ranges that overlap target write areas before writing.
- When searching for marker text or repeating labels, normalize with `.strip().lower()`, then read the adjacent cell to collect ordered values.
- For delimited/multi-value cells, split and trim each value before membership tests; use exact match instead of substring containment.
- When a cell displays an unexpected value, inspect its `number_format`. Custom formats (e.g., `000`) can mask the true content, such as showing `000` for a formula error or zero. Always check the format alongside the cell's `value` or `data_type`.
- When inspecting cell fill colours with `openpyxl`, always cast `fgColor.rgb` to `str()` before measuring length, slicing, or comparing — it may return an `RGB` object instead of a plain string.
- When reading reference tables for lookups, load the data into an in-memory dictionary keyed by the lookup column for fast, error-free access.
- Stop reading source data at the first empty row after the header to exclude unrelated content below (e.g., a second example table). Detect data boundaries dynamically: scan for actual first/last non-blank cells before range deletion or copying; do not hardcode start/end rows.
- Treat `None` cells as 0 in any arithmetic. Normalize with `value or 0` before calculations.
- To select whole numbers from mixed numeric data, treat whole-number floats as integers: `isinstance(val, float) and val == int(val)`.
- Before changing formulas, inspect both the existing formula and the referenced source data format. For structured text, map components to exact character positions; e.g., `dd.mm.yy HH:MM` has the two-digit year at characters 7–8 (1-indexed).
- When partial outputs are already present in target cells, use them to reverse-engineer the underlying pattern (e.g., locate matching values in the source data to compute step size and starting position).
- Check key uniqueness before mapping: confirm the intended source key is unique across rows. If a simple pair repeats, add distinguishing fields (e.g., date).

## Writing Output

### Deleting Rows
- Collect indices of rows to delete. Treat a row as blank only when every cell value is `None` or an empty string (`cell.value is None or cell.value == ''`).
- Delete rows from the highest index downward using `sorted(rows_to_delete, reverse=True)` or `reversed()` to prevent index shifts, then re-read the sheet.
- Determine deletion ranges dynamically by scanning the column for the first and last non-blank cells rather than hardcoding row numbers.
- For group-dependent deletions, group the data and evaluate the condition per group before deleting or modifying rows.

### Extraction and Filtering
- Prefer built-in string methods (`startswith`, `in`) for simple prefix and substring checks; avoid regex unless needed.
- Clear the destination range before writing new results (set target cells to `None`) to prevent leftover values from previous runs, especially when new output may be shorter.
- Date-threshold filtering: collect all valid `datetime` values from the target column, compute `max(dates)`, subtract a `timedelta` (e.g., 30 days), then filter rows with `date_val < cutoff`. Avoid string comparisons.
- When a column contains heterogeneous data types, use `isinstance()` checks to branch logic. Handle datetime objects and strings separately to apply appropriate conversion.
- To select integers from a column containing mixed numeric types, check `isinstance(val, float) and val == int(val)` to include whole-number floats while excluding true decimals.

### Grouped Aggregations
- For grouped aggregations that Excel formulas cannot express (e.g., case-sensitive multi-row sums), load data rows into Python and compare strings exactly with `==`.
- Define a `to_float` helper that returns `0.0` for `None` or empty strings. After arithmetic, write results with `int(round(total))` and set `cell.number_format = '0'` so displayed values are integers and blanks are treated as zero.
- Prefer programmatic calculation for complex conditional aggregations (e.g., SUMIFS with date ranges plus a list). Compute values directly in code and write static values, avoiding formula debugging. When a criteria list resides in a range, load it into a set for direct membership tests (e.g., `if category in criteria_set`).
- When merging rows based on one or more columns, use a dictionary keyed by the grouping column(s) (a tuple for multiple columns) and aggregate numeric columns by summing; treat non-breaking spaces and empty strings as blanks.
- For unique-value counts in a column range, collect non-null cell values into a Python set and use `len(set)` as the distinct count.

### Lookups and Cross-Sheet Mapping
- Prefer computing and writing literal values over formulas when the goal is populated output cells. For cross-sheet mappings, loop over the key column, resolve the matching sheet or record per key, and write the resolved value directly instead of hardcoding a single source.
- Use `MATCH(1, (range1=criteria1)*(range2=criteria2), 0)` inside INDEX to match on multiple columns simultaneously when a single column is insufficient.
- When a formula will be copied across columns, use relative column references so the column index auto-adjusts. If populating cells individually in a script, explicitly set the correct column letter for each cell.
- For small fixed lookup tables, consider nested IF statements with absolute anchors for the lookup key and relative references for the return column, instead of VLOOKUP. Use programmatic formula assignment to avoid unintended reference shifts.
- For enrichment lookups during row generation, use `dict.get()` to safely handle missing keys.

### Sorting and Reordering
- **Group-then-sort**: For grouped reordering, collect rows by key, sort within each group, then sort groups by an aggregate property. See [references/sorting-patterns.md](references/sorting-patterns.md) for a full example. Avoid flat global sorts when groups must stay together.
- Frequency-based sorting: count occurrences (e.g., `collections.Counter`), sort items by descending count (tie-break by value), then repeat each item its count times to produce a column ordered by prevalence.

### Formatting and Cell Operations
- **Preserve formatting**: When moving or copying cells, transfer `font`, `fill`, `border`, `alignment`, and `number_format` from source to target using `copy()`. Do not copy only values.
- When copying cells that require formatting (e.g., dates, alignments), load the workbook without `data_only=True` to read attributes like `number_format` and `alignment`, then apply them to destination cells.
- **Bulk text replacement**: For simple find‑and‑replace across all cells, iterate with `ws.iter_rows()` and use `cell.value.replace(old, new)` on string cells. Avoid modifying cells unnecessarily.
- **Blank cells**: To leave a cell truly blank, assign `None` to `cell.value`. Do not use empty strings or spaces.
- To display zeros as blanks while keeping decimal formatting, set `cell.value = None` when the value is zero and apply a fixed number format like `'0.00'`.
- For tasks requiring alphabetic suffixes (e.g., generating unique identifiers), use a reusable letter-sequence generator. See [references/letter-sequence-generator.md](references/letter-sequence-generator.md) for a divmod-based implementation that handles sequences beyond 26 items.

### Column Operations
- **Column deletion**: after identifying the column index, call `worksheet.delete_cols(col_idx)`. Verify the removal by checking that `max_column` decreased.
- **Column rearrangement**: locate the source column by scanning the header row for an exact match (do not hard-code column letters). Insert a blank column at the destination position first, copy all cell data including formatting, then delete the original source column only after confirming the copy is complete. See [references/column-operations.md](references/column-operations.md) for detailed examples.
- **Explicit column mapping**: Identify source columns by header name or fixed index, then map them to target columns. Account for any extra columns in the source.
- **Value transformation**: When replacing values (e.g., country codes), define a lookup dictionary and apply the substitution during row‑by‑row copying to avoid intermediate columns.

### Formula Handling
- When a task says "modify the formula," keep the cells as formulas. Inspect the existing formula, identify only the sub-expression that must change, and apply a surgical replacement. Do not replace formulas with pre-computed static values.
- Preserve the original formula output type. If formulas return string values such as `dd/mm/yy HH:MM`, keep string results. Do not write datetime/number objects where the original formula produced strings.
- If a formula causes a circular reference (e.g., `SUM(A1:A10)` in A10), do not attempt to fix the formula. Identify the correct range excluding the target cell, compute the result externally using Python, and write the literal value into the cell. Preserve the existing `number_format`.
- When fixing a broken lookup formula such as `VLOOKUP` `#REF!`, inspect the data table structure to infer the intended result; replace the broken formula with either a corrected formula covering the full range or a literal resolved value. See [references/formula-troubleshooting.md](references/formula-troubleshooting.md) for detailed examples.
- To update values while preserving existing formulas (especially array formulas in header/aggregate rows), load the workbook twice: first with `data_only=True` to read resolved values for inspection, then without `data_only=True` to perform writes. Rows where the resolved value is a string (not blank) indicate detail rows; rows with blank resolved values are typically header/aggregate rows whose formulas must remain untouched.

### Sequential Rank Assignment
When replacing ranking formulas with sequential, no-gap ranks:
- Group rows by the category column.
- Within each group, sort by the numeric value descending, then by original row index ascending to break ties in order of appearance.
- Assign ranks 1, 2, 3, ... to each row in the sorted order.
- Write the ranks back to the target column.

### Duplicate Lookup Keys → Horizontal Transposition
When a lookup returns multiple values for the same key and all must appear in one row:
1. Build a dict mapping each key to a **list** of retrieved tuples/values (preserve all duplicates).
2. Flatten the list into a single sequence before writing.
3. Write values sequentially across columns using an indexed loop with an offset:
   `for i, val in enumerate(flat_values): ws.cell(row=target_row, column=start_col + i).value = val`

### Other Patterns
- For row-duplication or count-expansion tasks, write output to a new sheet instead of inserting rows in place. Build the new sheet with a forward loop over source rows, writing each row the required number of times.
- For patterned row intervals (e.g., copying every Nth row), use an indexed loop over destination rows with an explicit `source_row = start_row + index * step` calculation. Prefer this programmatic approach over spreadsheet functions like OFFSET or INDIRECT.
- For column fills that change at section boundaries, iterate rows sequentially and advance the source pointer only when a delimiter row (e.g., `"TOTAL"`) is encountered.
- For cumulative, priority-based conditions over expanding ranges that are hard to express as a single Excel formula, compute values row-by-row in a Python loop and write the literal results.
- When multi-step conditional logic is described as a sequence ("first check A, then B, then C"), nest later conditions inside earlier ones. Treat earlier conditions as prerequisites unless the instruction explicitly states otherwise.
- When creating column headers from categorical values in a source column, extract the unique values directly from the data (e.g., using a set) rather than relying on instruction‑provided labels.
- Prefer negative character sets to keep allowed characters rather than listing characters to remove. Example: `re.sub(r'[^0-9.-]', '', str(cell.value))` keeps digits, dots, and minus signs.
- Guard numeric operations with `isinstance(cell.value, (int, float))`; compare floats with an absolute tolerance (`abs(value) < threshold`) instead of `== 0`.
- When iterating over a column that may have empty rows, conditionally act only on non-empty cells and leave empty cells unchanged.
- When a maximum destination range is specified (e.g., `'master'!A1:AH1`), enforce a hard limit on the output columns and truncate data that would write beyond it.
- For multi-step, conditional spreadsheet edits, externalise the logic in a standalone Python script file and execute it, rather than using `python3 -c` one-liners.
- For common operations like date‑threshold filtering or column deletion, see [references/common-operations.md](references/common-operations.md).
- For consolidation and formatting patterns, see [references/consolidation-patterns.md](references/consolidation-patterns.md).

### Saving Output
- Always call `wb.save(output_path)` after modifying the workbook. Do not consider the task complete until the output file is written to the exact required path.
- Restrict all writes to the exact `answer_position` sheet or range. Clear and populate only that target; never overwrite input or source sheets.
- Read `.xlsx` files with `openpyxl.load_workbook(path, data_only=True)` to access displayed (computed) cell values, not underlying formulas.
- When an example output sheet is provided, cross-reference it with the raw data to reverse-engineer the exact filtering, ordering, and formatting rules before writing any code.
- When overwriting an existing sheet, clear only the data area below the header (e.g., set values to `None` from row 2 onward) to remove old data while keeping the header row intact.

## Verification

- Immediately after saving, reload the output file with `openpyxl.load_workbook()` and print all cell values to confirm changes match expectations. Verify that only the target output cells were modified and that existing formatting is intact.
- Re-read the sheet after any destructive operation (row deletion, column deletion) to confirm changes. After column deletion, confirm `max_column` dropped to the expected width.
- After writing formulas or lookups, test on at least two rows that should return different results; if both return the same value, suspect a missing MATCH criterion.
- After writing values, read back sample output cells and compare them with the expected source or lookup values for the same keys; verify values directly rather than relying on formula recalculation.
- If a reference sheet with expected output exists (e.g., "Desired Results"), read its values after writing and compare row-by-row; this catches ordering mistakes, off-by-one errors, or logic flaws.
- Verify the output retains the exact sequence of the master list and that all missing IDs are represented.
- For date filtering, spot-check that all remaining rows satisfy the threshold condition.
- Verify the output artifact exists at the required path with `os.path.exists(output_path)` and `os.path.getsize(output_path) > 0`; if a system warning says the output file was NOT created, immediately write and save the file instead of running more inspection.
- After saving a modified spreadsheet, reload the output file and inspect key cells again. Confirm that both values and number formats match the requirements. Print `value`, `type`, and `number_format` for each relevant cell. If discrepancies exist, fix and re-save.
- Spot-check both positive cases (rows that should have changed or been deleted) and negative cases (rows that should remain unchanged). Pick a few input rows, apply criteria by hand, and compare with the computed result.
- Confirm the destination sheet contains only the intended data, with no stale or leftover values from previous runs.
- Cross-check computed values (aggregates, rankings, counts) against original input or embedded reference/expected-result tables.
- If a formula or rule works for one row but fails for others, compare working and failing cases to identify implicit conditions such as first-match behavior.
- Before applying a full sort, test the sort key on a small manually checkable subset. For string sorts, use standard lexicographic order (e.g., "D 14" before "D 6"); do not extract numeric sub-parts unless explicitly requested.
- Verify that rows which should retain formulas (e.g., headers, aggregates) still contain the original formulas, not static values.
- If ranks were assigned, verify they are sequential within each category with no gaps or duplicates.
- Compare `answer_position` row counts against written data row counts for each target range. If a range has fewer rows than expected, inspect the original template for missing summary or header rows. See [references/structure-validation.md](references/structure-validation.md).
- Verify TOTAL rows contain the correct sums for their category data.
- After writing output, verify that the produced values match any provided sample outputs exactly. If the pattern was inferred from partial results, confirm that the computed step size and starting position reproduce the existing values before extending to the rest of the range.
- After editing formulas, verify the cells still contain formulas, recalculate, and read back the resulting values. Check that the value type matches the original output type, not just the displayed format.
- For conditional summation with complex criteria (e.g., date ranges + text matching), prefer computing results in Python and writing literal values rather than embedding fragile Excel formulas. See [references/complex-lookup-patterns.md](references/complex-lookup-patterns.md) for handling multi-value cells.
- After saving, verify the output file exists at the specified path. When feasible, reopen the workbook and read back a key value or sheet name to confirm the write succeeded.
- Before finalizing, review the task description line-by-line and confirm each explicit requirement has a corresponding implementation step. Pay special attention to formatting requirements (fill colors, fonts, borders) that are easily overlooked.

## Common Pitfalls

- Deleting rows in ascending index order shifts subsequent rows, leading to incorrect deletions; always delete in reverse index order.
- Cells that appear blank may contain formulas returning empty strings; rely on cell values, not visual appearance.
- Do not assume sheet or range layout before inspecting dependent sheets. Always inspect first.
- Do not embed formulas when literal output is sufficient or recalculation may not occur; do not hardcode a single source sheet when a key column determines the source per row.
- Single-criterion MATCH when multiple columns are needed: verify the match key uniquely identifies a row. If the first row tested happens to be the first match, the formula will appear correct but fail for other rows.
- Broken references after copying: check that column letters or relative references adjust as intended when formulas are replicated.
- Exploration-only loop: running repeated inspection scripts without implementing or saving.
- Missing output: declaring completion without calling save and verifying the file exists; ignoring system warnings about missing output and continuing to explore instead of writing the file.
- Overwriting a source sheet instead of the designated output range. Always resolve `answer_position` first and confine changes there.
- Overwriting valid data: modifying cells without first inspecting them can overwrite pre-existing correct values. Always inspect the range before writing.
- Assuming all cells in a column share the same data type. Always inspect first.
- Forgetting to strip unwanted time components from datetime objects when only dates are needed.
- Guessing sort order without consulting a reference table.
- Using a single‑column sort when groups must stay contiguous.
- Losing formatting by only copying cell values—always transfer style attributes.
- **Multi-step sorting scope**: When instructions combine a priority grouping/ordering step with a numeric sort, always apply the grouping as a pre-processing step first (preserve original intra-group order unless explicitly instructed to re-sort within groups), then perform the final sort **globally** over the entire collection. Do not apply the final sort within each group unless the task explicitly states "sort within each group."
- Avoid nested-loop row lookup when merging; use the ID-keyed dictionary for linear-time membership and row retrieval.
- **Skipping inspection / trusting task descriptions** causes wrong row/column bounds, off-by-one errors, and missed columns. Always inspect actual values, headers, sheet names, and layout first.
- **Hardcoding sheet names or layouts**; use `wb.sheetnames`, dynamic sheet detection, and key-column resolution instead.
- **1-based indexing**: openpyxl row and column indices start at 1, not 0; verify with printed output.
- **Blank cells are `None`, not empty strings.** Treat `None` as blank and set `cell.value = None` to clear cells.
- **Writing into merged cells without unmerging first** causes failures.
- **Forgetting to save** after modifications; prefer saving to a new filename to preserve the original.
- **Relying on complex Excel formulas** for dynamic assignments, multi-criteria logic, or per-category ranking; prefer Python scripts, sets, and grouped processing.
- **Floating-point equality** (`== 0`) misses tiny residuals like `1e-12`; use a tolerance.
- **Numeric operations on header strings** raise TypeError; guard with `isinstance(..., (int, float))`.
- **Substring matching on delimited values** produces false positives; split and use exact membership.
- **Complex deduplication logic** when a Python set suffices.
- **Stdlib-shadowing script names** (e.g., `inspect.py`, `copy.py`, `email.py`, `json.py`) shadow imports; use names like `check.py` or `util.py`.
- **String-vs-numeric sorting** confusion: default spreadsheet sort is lexicographic; do not extract numeric sub-parts unless explicitly requested.
- **Empty/trailing rows**: `max_row` may include empty rows from previous edits; filter all-`None` rows when needed.
- **Off-by-one in marker segmentation**: process rows strictly between consecutive markers unless the task explicitly includes the marker row.
- **Using `LARGE` with `IF/AND` for per-category ranking** fails because it returns the global k-th largest; group by category and rank separately.
- **Delete-before-insert**: Deleting the source column first risks data loss and overwrites. Insert the destination column first.
- **Hard-coded column letters**: Column positions shift between spreadsheets. Always locate by header name.
- **Debugging fragile embedded macros** is often slower and less reliable than a clean Python/openpyxl rewrite. Do not attempt to fix broken VBA macros; reimplement the intended logic in Python.
- **Calling `len()` or string methods directly on an openpyxl colour attribute** without first converting it to `str()` raises a `TypeError`.
- **Missing summary rows**: When clearing and repopulating a structured sheet, TOTAL/subtotal rows are often lost. Always check the original layout for aggregate rows and regenerate them.
- **Ignoring `answer_position` dimensions**: If the expected output range has more rows than your data, you are missing structural elements. Validate row counts per range before saving.
- **Brittle character stripping**: When cleaning strings, use negative regex character sets (e.g., `re.sub(r'[^0-9.-]', '', text)`) to keep only explicitly allowed characters. Avoid enumerating characters to remove, which risks accidentally deleting decimal points or minus signs.
- **Unconstrained loops/queries**: Always constrain loops and queries to the exact range specified in the task (e.g., `A7:A1000`). Avoid iterating over entire columns or rows to prevent accidental matches in headers or out-of-scope data.
- **Avoid manual copy/paste propagation** of formulas with mixed absolute/relative references; it can silently shift referenced columns or rows.
- **Overwriting array formulas**: Writing to cells that contain array formulas (e.g., SUMPRODUCT) can break them. Always identify which rows contain formulas vs. values before writing.
- **Duplicate ranks**: Formula-based rankings may assign the same rank to tied values. If the task requires unique consecutive ranks, replace them with programmatic assignment.
- **Using `data_only=True` for writing**: This mode discards formulas, so any save would lose them. Use it only for reading.
- **Assuming a displayed value reflects the true cell content** without checking `number_format`.
- **Trying to patch circular-reference formulas** instead of computing the value externally.
- **Relying on formula recalculation** in environments that may not support it.
- **Replacing formulas with static values** when the task asks to modify formulas.
- **Changing formula output from string to datetime/number**, which can break downstream formulas.
- **Assuming substring positions** without inspecting the actual source data format.
- **Guessing pattern parameters** (e.g., interval size) without examining source data and existing partial outputs. Always derive parameters from the actual data.
- **Iterative probing** of the dataset instead of a single comprehensive read.
- **Dimension mismatch**: accepting loaded data without cross-checking against task-description previews (row counts, '... (N more rows)' hints).
- **Deleting rows based on individual row checks without considering group context** can cause incorrect partial deletions when the rule is group-dependent.
- **Hardcoded ranges break on varying data sizes**; detect boundaries dynamically. See [references/block-operations.md](references/block-operations.md).
- **Floating-point in percentage thresholds**: use integer arithmetic: `value * 10 >= ref * 11` for a 10% increase, or generalize to `value * 100 >= ref * (100 + pct)` for pct%. Avoid `value >= ref * 1.10`.
- **Restart semantics**: when an algorithm says 'restart from the cell immediately right of X', set the new reference to the adjacent cell (index+1), not X. Validate restart logic against any pre-filled annotations in the sheet.
- **Spatial search direction**: when asked to find a value 'above' a reference row, search descending from `reference_row - 1` toward row 1 and stop at the first match (the closest occurrence).
- **Format preservation**: when writing a value into an existing column, inspect and replicate the target column's existing number format; do not apply an arbitrary new format.
- **Bash tool argument format**: when using the bash tool, pass the command directly using the `'command'` key, not nested inside `'arguments'`.
- **Missing expected sheet names**: if a specified sheet (e.g., `BR1`) is absent, fall back to processing all available sheets instead of failing.
- **Entangled conditionals obscure intent**: branch on control cells early and keep each path independent.
- **Dictionary key/index misalignment**: Align dictionary keys with actual worksheet column indices. When storing per-column data, ensure the keys match the 0-based or 1-based indices used in cell access code. Off-by-one mismatches cause KeyErrors.
- **Whitespace/case differences** in string identifiers causing silent lookup misses; always normalize keys with `str(value).strip()` and consistent types before mapping.
- **Non-unique composite keys** such as meet+race pairs repeating across dates; extend the key when necessary.
- **Changing zero cells** when a 'do not change zero cells' requirement exists.
- **Missing configuration rows** (min/max constraints) before building logic.
- **Forgetting to clear the target range** before writing transposed or variable-length data, leaving residual values from earlier usage.
- **Overwriting beyond the intended target range** when the data source has more entries than the destination allows.
- **When splitting strings at character boundaries** (e.g., digit-to-letter transitions), clean up whitespace artifacts by applying `.rstrip()` to the left portion and `.lstrip()` to the right portion, unless whitespace is semantically meaningful.
- **VLOOKUP/HLOOKUP `#REF!` errors**: Usually means the column/row index exceeds the lookup range. Fix by expanding the range or writing a corrected formula/resolved literal value.
- **Header loss**: Deleting or overwriting the header row when clearing a sheet for rewrite. Always preserve the header row.
- **Single-workbook corruption**: Using a single workbook object for both reading and writing can corrupt formulas. Use separate instances for reading (data_only=True) and writing.
- **None-value assumptions**: Not all numeric cells contain numbers; `None` is common. Always normalize to 0 before arithmetic.
- **Reference sheet formatting signals**: When a reference sheet exists alongside the target sheet, inspect cell formatting (fills, fonts, borders) as the primary indicator of the intended result. Do not rely on auxiliary column values that may be stale manual annotations.
- **Subset-sum mismatch**: If a claimed target sum range yields no valid subset from the data, re-examine how candidate values were identified rather than assuming the stated range is wrong.
- **Sheet name casing**: Assuming sheet name casing matches expectations. Always use `wb.sheetnames` to get exact names.


## Common Pitfalls

## Lookups and Mapping

When mapping rows between sheets, verify key uniqueness and normalize text. See [references/sheet-mapping-patterns.md](references/sheet-mapping-patterns.md) for the full pattern.