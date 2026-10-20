---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow

Follow this sequence for any spreadsheet task:

1. **Inspect exhaustively**: Load the workbook with openpyxl and print every cell's coordinate, value, type, and number_format on the active sheet. Identify exact header positions, data columns, target ranges, block boundaries, and any inconsistent key columns before writing transformation code. Confirm sheet names via `wb.sheetnames` — they are case-sensitive. If a required sheet name is missing, fall back to processing all available sheets. Perform this inspection exactly once; do not loop. (See [Inspection](#inspection) for details.)

2. **Interpret the task**: If given broken code or a description of an error, infer the intended business logic. Do not just fix syntax; understand the intended transformation. When an expected output sheet or manual result is provided, compare it with the raw data to reverse-engineer the exact filtering, ordering, and formatting rules before writing code. Use `answer_position` metadata (e.g., `'SheetName'!A1:B100`) to determine the exact output range. Treat the first row as a header unless specified otherwise. When a task has alternative behaviors based on a cell value (e.g., a control cell), read that cell early and branch the logic into clear, separate paths.

3. **Plan the transformation**: Identify the computation pattern. For interval-based tasks, segment data by marker columns and compute over the segments between consecutive markers. For "last date per category" aggregation, use a two-pass pattern. For complex cumulative or priority-based logic, prefer a Python script over nested Excel formulas. When source data rows are grouped by entity and sorted chronologically, iterate in natural row order to compute per-entity running balances.

4. **Choose the right tool**: Prefer Python with openpyxl for read/transform/write Excel tasks. Open the workbook twice when formulas are involved: once with `data_only=True` to read computed values, and once without to perform writes. Use programmatic formula assignment over manual copy/paste when populating ranges. When modifying formulas, edit the formula in-place; do not replace cells with static values unless the formula is broken beyond repair.

5. **Execute the transformation**: Modify only data rows; preserve header rows intact. When modifying a worksheet (e.g., deleting rows), always process deletions in reverse order to avoid index shifting. Before performing arithmetic on cell values, guard against non-numeric cells (e.g., headers) by checking `isinstance(cell.value, (int, float))`. Build lookup structures in memory (e.g., dictionaries keyed by tuples) to avoid nested scans, and normalize keys with `str(value).strip()`. For cross-table matching, normalize each source block into composite-key dictionaries by shared identifiers. When building dictionaries keyed by column index, ensure the keys match the exact indices used in cell read/write calls.

6. **Write results** to the target sheet, always clearing the destination area first (see [Writing Output](#writing-output)). Identify structural rows before clearing, and either preserve or regenerate them. For row-duplication tasks, write output to a new sheet to avoid index-shifting complexity.

7. **Save and verify**: Save the workbook to the exact output path using `wb.save(output_path)`. Never end the task without producing the output artifact. After saving, re-open the file and confirm key cell values (see [Verification](#verification)).

**Master-list merge pattern**: When merging a source dataset into a reference sheet, drive the merge from the master list to preserve order. Read source rows into a dictionary keyed by the unique ID, then iterate the master list sequentially: write the full row when the ID exists in the dictionary, otherwise write an empty row containing only the ID.

**Cross-sheet mapping**: Use single-pass cross-sheet mapping: inspect source uniqueness first, normalize keys, then apply a dictionary lookup from source to target. Keep lookup dictionaries small by storing only the values required downstream.

For complex row reordering requiring grouping and multi-level sorting, see [Grouped Sorting](references/grouped-sorting.md).


## New Section

## Lookup Patterns

For multi-criteria row lookups, use `MATCH(1, (range1=criteria1)*(range2=criteria2)..., 0)` to require all conditions. A single-criterion MATCH returns the first match and is only safe when one column uniquely identifies every row.

When a formula works for one row but fails for others, compare the working case against the failing cases. Check whether the working case accidentally satisfies an implicit condition (e.g., being the first match) that the others do not.

For detailed examples, see [Multi-Criteria Lookup](references/multi-criteria-lookup.md).
## Inspection

Before any transformation, perform a thorough inspection of the target sheet:

- **Dump all cells**: Print every cell's coordinate, value, Python type, and number format. This reveals mixed data types (e.g., datetime objects vs. strings), booleans, None values, and inconsistent formatting. Use this to identify data ranges, header positions, constraint rows, blank rows, and exact column indices for each data field.
  ```python
  for row in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=ws.max_column):
      for cell in row:
          if cell.value is not None:
              print(f"{cell.coordinate}: value={cell.value}, type={type(cell.value).__name__}, format={cell.number_format}")
  ```

- **Use data_only for reading**: When reading .xlsx files with openpyxl, use `data_only=True` to obtain displayed values (formula results) rather than underlying formulas. This is essential for filtering rows based on resolved values, reading marker/indicator cells, and comparing cached values against formulas to identify error cells (`#REF!`, `#N/A`). When you need to write back to the workbook, load a separate instance without `data_only=True` to preserve existing formulas.

- **Check dimensions and structure**: Print sheet names (use exact casing from `wb.sheetnames`), dimensions (`max_row`, `max_column`), column headers, and sample rows. Compare dimensions against any numerical hints in the task description. If a mismatch is found, re-examine the file path, re-load, or alert before proceeding.

- **Detect data boundaries dynamically**: Define the data range by scanning the first column and stopping at the first empty row after the header; this excludes unrelated content below. Identify block boundaries by scanning for header rows (e.g., rows where a key column equals a distinct value like `'date'`). Use this to partition the sheet into logical groups without hardcoding row ranges.

- **Header matching**: When keys may be embedded inside longer strings, use substring containment (e.g., `if key in long_string`) instead of exact equality. Ensure the key is unique enough to avoid false matches. For case-insensitive matching, normalize both cell text and keywords to lowercase.

- **Header/value pair scanning**: When source data uses repeating labels (e.g., "INVOICE NO"), search for the header text and read the adjacent cell (often the cell below or to the right) to collect values. Avoid hard-coded ranges.

- **Multi-value cells**: For cells containing comma-separated multi-values, split the cell on commas, trim whitespace, and check whether the target term exactly equals any part. Avoid substring containment that could cause false matches.

- **Reference sheet analysis**: When a reference sheet (e.g., "After" or "Expected Results") is provided, inspect cell formatting (fills, fonts, borders) as the primary indicator of the intended result. Do not rely on values in adjacent helper columns — those may be stale manual annotations. Compare the reference ordering with the source data to identify grouping criteria, within-group order, special row positions, and inter-group ordering.

- **Example-driven inference**: If the sheet contains rows demonstrating desired output (e.g., a "Result" or "Example" sheet), analyze them to deduce the exact transformation logic, output format, counter start, and increment behavior before coding. Treat any existing in-sheet rows that demonstrate the desired output as authoritative.

- **Formatting capture**: To capture cell formatting (number format, alignment), load the workbook without `data_only=True`; use `data_only=True` only for reading values. When a cell displays an unexpected value, inspect its `number_format` alongside its `value` — custom formats like `000` can mask error states or zero values.

- **Float and whole-number detection**: When comparing numeric cell values for deletion or filtering, use a small absolute tolerance (e.g., `abs(value) < 0.011`) instead of exact equality. Use `isinstance(val, float) and val == int(val)` to treat whole-number floats as integers when filtering for integers.

- **Group-conditional evaluation**: For group-conditional operations, group data by the relevant identity columns first, then evaluate the condition per group before deciding what to delete or modify.

- **Key uniqueness verification**: Before mapping rows between sheets, verify that the intended key is unique across rows; inspect for duplicates and add distinguishing fields (e.g., date) when needed. Normalize text identifiers before comparison: strip whitespace and convert to a common case (e.g., `str.strip().upper()`).

- **Unique value extraction**: When a task describes categorical values (e.g., allowance types), extract the unique values from the corresponding source column. Use these as the authoritative list for output headers or groupings. Print or log extracted unique values and compare them against any task-provided lists to catch discrepancies (e.g., plural vs. singular) before writing output.

- **Search direction**: When asked to find a value "above" a reference row, search descending from `reference_row - 1` down to row 1 and stop at the first match.

- **Openpyxl colour handling**: When inspecting cell fill colours with `openpyxl`, convert `fgColor.rgb` to `str()` before `len()`, slicing, or comparisons; it may be an `RGB` object, not a plain string.

For detailed guidance on diagnosing and resolving formula issues, see [Formula Troubleshooting](references/formula-troubleshooting.md).

## Writing Output

- **Clear destination first**: Before writing new data to a sheet, explicitly clear the target range (e.g., delete all cells in the target column or used area, or assign `None` to destination cells). This prevents leftover data from previous runs or templates from corrupting the output. When instructed to empty a cell or column, remove both value and formatting: set `cell.value = None` and apply `PatternFill(fill_type=None)`.

- **Scope modifications precisely**: Write only to the target sheet and range named by the task (e.g., `'MyResult'!A1:O20`). Clear and populate only that range; leave input and reference sheets untouched. Iterate only over the exact range specified, inclusive. Do not loop over all rows or a fixed large range.

- **Preserve headers when overwriting**: Clear only the data area below the header (row 2 to max) by setting cells to `None` before writing new data. This prevents leftover data from contaminating the output while keeping the header row intact.

- **Unmerge before writing**: Before writing into cells that may be part of merged ranges, unmerge those ranges first to prevent write failures or unexpected behavior.

- **Row deletions**: Collect row numbers meeting the condition (using tolerance if needed), then iterate `reversed(sorted(rows_to_delete))` and call `delete_rows(r)` to avoid index shifting.

- **Row insertions**: When inserting multiple rows above different positions, process insertions in descending order (highest row number first) to preserve original row indices.

- **Column deletion**: To delete a column, determine its numeric index (e.g., column Z is index 26) and use `worksheet.delete_cols(index)`. After deletion, verify that `max_column` decreased accordingly.

- **Column rearrangement**: When moving or inserting columns, use insert-before-delete: insert the destination column first, copy data, verify, then delete the source. Preserve all cell formatting when relocating data (see [Formatting Preservation](references/formatting-preservation.md)).

- **Fix broken lookup formulas**: When `VLOOKUP` or similar functions error due to column index exceeding range width, analyze the data table structure (headers, row values) to infer the intended result. Replace the broken formula with the resolved literal value or a corrected formula. Always prefer a working literal value over leaving a broken formula in place.

- **Grouping/merging rows**: For grouping rows by multiple columns, aggregate with a dictionary keyed by a tuple of grouping columns and sum numeric values directly: `key = (col_a, col_b, col_c); groups[key] = groups.get(key, 0) + numeric_value`. Treat `\xa0` and empty strings as blank values. Prefer Python aggregation over complex Excel formulas.

- **Handle duplicate keys**: When a lookup key may appear multiple times and all matches must appear in one row, aggregate all matching records into a list first, flatten the list, then write across columns using `enumerate` and a column offset (e.g., `for i, val in enumerate(values): ws.cell(row=row, column=start_col + i).value = val`).

- **Post-save verification**: After saving, re-open the workbook and read back modified cells to confirm edits were applied correctly and no unintended changes occurred.

- **Unpivot wide tables**: For each data row, iterate over variable columns, producing one new row per variable with fixed columns copied and the variable's name and value added.

- **Enrich with lookup table**: Build a dictionary from the reference sheet (key → attributes). During transformation, retrieve attributes using `dict.get()` to avoid manual matching.

- **Style preservation**: When duplicating or moving cells, preserve appearance by copying each style attribute: `copy(cell.font)`, `copy(cell.border)`, `copy(cell.fill)`, `copy(cell.alignment)`, and `copy(cell.number_format)`. When copying only values between cells, preserve the destination cell's original formatting unless explicitly instructed otherwise.

- **Zero as blank**: For zero-as-blank decimal output, set the cell value to `None` when the computed sum is zero and apply a fixed format such as `number_format = '0.00'` to non-blank aggregated cells.

- **Python fallback for complex logic**: For complex cumulative, priority-based, or conditional aggregation logic that is hard to express as a single Excel formula, compute the results in a Python script and write the literal numeric values directly to the cells. Prefer this over fragile Excel formulas such as SUMIFS with wildcard matching. For multi-step, conditional edits, externalize the logic in a standalone Python script file (e.g., using a heredoc) and execute it. This avoids quoting and escaping pitfalls of `python3 -c` one-liners. See [Cumulative Logic Pattern](references/cumulative-logic-pattern.md) and [Python Aggregation Patterns](references/python-aggregation.md).

- **Programmatic formulas**: Apply formulas programmatically rather than by copy/paste. Loop over target cells and construct each formula with explicit absolute/relative references (e.g., `$B{row}` for fixed lookup column, `{col}{row}` for relative return column). For small, fixed lookup tables, use nested IF chains instead of VLOOKUP.

- **Leave blank cells as None**: Assign `cell.value = None` for blank cells, not an empty string or space.

- **Sequence continuation**: When filling in missing values that extend an existing sequence, parse existing values to determine the current counter/sequence state; continue from the last present value, not from the start. For alphabetic sequences beyond 26 items, use a reusable `col_letter(n)` helper (see [Letter Sequence Helper](references/letter-sequence-helper.md)).

- **Structural row preservation**: When clearing and repopulating a target sheet, identify all structural rows (headers, TOTAL, subtotals, SUM formulas) before clearing. Either preserve structural rows by clearing only data rows, or regenerate them after writing data.

- **Mixed data types**: When a column contains mixed data types (e.g., datetime objects and date strings), use `isinstance()` checks to branch logic per type.

- **Inter-block spacing**: When compacting multiple data blocks, keep exactly one empty row between blocks and remove any trailing empty rows.

- **Date threshold filtering**: When filtering by date threshold, use Python's `datetime` and `timedelta` to compute a cutoff from the maximum date in the column. Collect valid datetime values, compute `max(dates)`, subtract `timedelta`, then filter rows with `date < cutoff`. This avoids string comparison pitfalls and handles mixed data types.

- **Frequency-based sorting**: Count occurrences with `collections.Counter`, sort items by count descending with value as tie-breaker, then reconstruct the list by repeating each item that many times. Do not rely on standard sort-by-value functions for frequency grouping.

- **Per-category ranking**: For per-category ranking (e.g., top‑N per group across a flat row), group values by their category label first, then sort and rank within each group. This avoids cross‑category interference that breaks simple conditional formulas. For consecutive, no-gap ranks, use the sequential rank assignment pattern (see [Ranking Patterns](references/ranking-patterns.md)).

- **Keeping last occurrence per unique value**: To retain only the last row for each unique value in a column, scan bottom-up. Record each value the first time it is seen; that row is the last occurrence. Delete all other rows in reverse order.

- **Normalize inter-block spacing**: When compacting multiple data blocks, keep exactly one empty row between blocks and remove any trailing empty rows.

- **Text cleaning**: When cleaning or transforming cell text, prefer a negative character set that keeps only allowed characters (e.g., `re.sub(r'[^0-9.-]', '', text)`) over enumerating characters to remove. This avoids accidentally deleting structural symbols such as decimal points or minus signs.

- **Batch replacements**: Use a simple `iter_rows` loop for find-and-replace across all cells. For lookup-based replacements, build a key-value dictionary from a reference sheet and overwrite target columns.

- **Always save**: Save the workbook with `wb.save(output_path)`. Never end the task without producing the output artifact.


## New Section

## Data Extraction

For extracting tagged values from unstructured text in cells, see [Extraction Patterns](references/extraction-patterns.md).
## Verification

- **Read back output**: After writing, read back the output cells and compare against expected values to confirm correctness.

- **Cell sampling**: After any bulk edit, load the output workbook and print cell values for: the header row, first 2–3 data rows, the last data row, and any edge cases. Confirm headers are unchanged and transformations applied consistently across the full range. Do not rely on visual inspection alone — read values programmatically.

- **Post-deletion check**: After deleting rows, re-read the sheet to confirm the expected rows are removed. Check that the number of remaining rows matches the expected count.

- **Stale data check**: After writing aggregated results, verify no stale or garbage values remain beyond the last valid output row.

- **Spot-check computed outputs**: Compare computed outputs against hand-calculated expected values for a sample of source rows before finalizing.

- **Reload and verify**: After saving, reload the output file and inspect key cells' `value`, `type`, and `number_format` to confirm both values and formatting match requirements. Spot-check both positive cases (rows that should have been changed/deleted) and negative cases (rows that should have been preserved), plus edge cases such as first row, last row, and transition points.

- **Cross-check answer_position dimensions**: For each range (e.g., A2:C1529), compute `expected_rows = end_row - start_row + 1` and compare to `len(data_items)`. If `data_items < expected_rows`, investigate missing structural rows (TOTAL, subtotals, headers).

- **Whole-number testing**: To test whether a number is whole, use `abs(val) == abs(int(val))`. This works for both `int` and `float` values without explicit type checks.

- **File existence check**: After saving, immediately confirm the output file exists at the required path with `os.path.exists(output_path)` and `os.path.getsize(path) > 0`. For extra safety, save to a temporary file first, then atomically rename to the target path.

- **Column deletion verification**: After column deletion, check that the sheet's `max_column` has decreased by the expected number of columns.

- **Formula preservation check**: Verify that formulas in non-target rows remain unchanged. Check a few known formula cells to ensure they still contain the expected formula, not a static value.

- **Comparative formula diagnosis**: After writing formulas, verify at least two rows that should return different values. If both return the same result, suspect a missing criterion in your lookup. Compare the working case against failing cases to identify implicit conditions that the formula does not enforce.

- **Requirement checklist**: Before finalizing, review the task description line-by-line and confirm that every requirement (data logic, formatting, etc.) has been addressed. Create a checklist if needed.

- **Reference sheet comparison**: If a reference sheet with expected output is provided (e.g., 'Desired Results'), read its values after writing and compare row-by-row against your output. This catches ordering mistakes, off-by-one errors, and logic flaws before finalizing.

- **Master-list order verification**: After writing, verify that output rows follow the master list order exactly and that missing IDs are represented as empty rows containing only the ID.

- **Composite-key uniqueness check**: Confirm the chosen composite key yields exactly one match per target row; no ambiguous or duplicate lookups.

- **Delimiter-driven grouping check**: After writing grouped values, spot-check that values change at delimiter rows and remain consistent within each block.

- **Sparse area recheck**: Recheck sparse areas to ensure empty source rows remain empty in the output.

- **Formatting verification**: For cells with custom number formats, verify both the cell's `value` and `number_format` match expectations. Confirm that relocated columns retain their original formatting (font, fill, border, number format, alignment).

- **Header lookup uniqueness**: Verify that header-based column lookup returns exactly one match; fail loudly if zero or multiple matches are found.


## New Section

## Proven Patterns

### Two-Pass Grouping for "Last Date per Category"
When aggregating by the latest date per group (e.g., "latest entry per brand, combine duplicates on that date"):
1. **First pass**: Build a dict mapping each group key to its maximum date.
2. **Second pass**: Iterate rows again, aggregating where `key == group_key and date == max_date`.

This naturally handles multiple records on the same latest date and preserves non-aggregated columns from the first matching row.

See [Aggregation Patterns](references/aggregation-patterns.md) for detailed examples.

## New Section

## Column Operations

- **Locate columns by header search**: When a column's position may vary, scan the header row for an exact match instead of using a fixed column letter. Iterate through cells in the header row and compare values to the target string.
- **Preserve all formatting during moves**: When moving a column, capture `number_format`, `font`, `fill`, `border`, and `alignment` from each source cell before any insertion, then reapply them to the destination cells.
- **Insert before delete for safe rearrangement**: To move a column, insert a blank column at the destination first, copy data there, then delete the original column. This sequence avoids data loss and preserves surrounding column order.
## Common Pitfalls

- Forgetting to clear the destination area before writing, leaving residual data from prior states.
- Using exact string equality when headers are only a substring of a composite label.
- **Exact equality on floats**: Use tolerance (e.g., `abs(value) < threshold`) instead of `== 0`.
- **Index shifting during deletion**: Delete rows in reverse order.
- **Non-numeric cells in arithmetic**: Skip cells with `isinstance` check before `abs()` or other numeric ops.
- **Overwriting headers**: Always skip row 1 when `answer_position` includes a header.
- **Fixing broken code literally**: Buggy scripts often contain logical errors; infer the business intent, not the bug-for-bug behavior.
- **Skipping verification**: A transformation that looks correct may have off-by-one errors or miss the last row. Sample the output.
- **Overwriting existing valid data without inspection**: Always inspect first to identify which cells need modification.
- **Assumption without inspection**: Writing logic before seeing the full data leads to missed edge cases.
- **Restarting sequences**: Forgetting to continue from existing intermediate values (e.g., restarting at 'a' when 'f' is already present).
- **Hardcoding limits**: Using fixed arrays for alphabetic sequences that break beyond 26 items.
- **Partial group deletion**: When a condition applies to a group, evaluate the whole group first. Deleting individual rows without group context can break rules like "delete one row only if all members satisfy X."
- **Lost summary rows**: Clearing an entire sheet and rewriting data without regenerating TOTAL/SUBTOTAL rows. Always check the original sheet for aggregate rows before clearing, and either preserve or regenerate them.
- **Ignoring answer_position dimensions**: The row count in answer_position ranges signals expected output structure. A mismatch between range rows and data item count means structural rows are missing.
- **Assuming uniform data types**: Always check for mixed types before writing transformation scripts.
- **Unnormalized keys**: Whitespace or type mismatches between lookup keys and source keys cause silent failures. Always strip and convert to strings.
- **Repeated scans**: Scanning the source data repeatedly for each target cell is inefficient and error-prone. Build an in-memory dictionary once.
- **Assuming sheet names**: Always list sheet names first; names may have extra spaces or different casing.
- **Losing formatting**: When using `data_only=True`, formatting is not available; load a separate workbook without `data_only` to read formats.
- **DO NOT use Excel formulas (SUMIFS, COUNTIFS) for complex criteria** like date ranges combined with comma-separated text matching. These are fragile and error-prone.
- **DO NOT rely on substring containment (`in`) for comma-separated cell values**. Always split and check exact match on each part.
- **Avoid guessing interval/step values** when partial outputs are present; derive them from matching source values.
- **Avoid OFFSET/INDIRECT** for fixed-interval row transfers; use programmatic indexed copying.
- **Overcomplicating text filters**: For simple prefix, suffix, or substring checks, prefer built-in string methods (`startswith`, `endswith`, `in`) over regular expressions.
- **First-match-only lookups**: Avoid first-match-only behavior when duplicate keys are possible; aggregate all matching rows or data will be silently dropped.
- **Fixed column ranges**: Do not hard-code fixed column ranges when writing a variable number of retrieved values; use `enumerate` over the flattened list.
- **Assuming layout matches description**: Always verify column positions and names by inspecting the actual file; do not assume the sheet layout matches the task description.
- **Script naming conflicts**: Do not name temporary helper scripts after Python standard-library modules (e.g., `inspect`, `copy`, `json`); use non-conflicting names like `check.py`. If such a file already exists, delete or rename it before importing those libraries.
- **Circular references**: A formula whose range includes its own cell will not evaluate correctly. Do not attempt to patch the formula. Instead, read the dependent data, compute the result externally, and write the literal value while preserving the existing number format.
- **Do NOT use IF/AND with LARGE for per-category ranking**; LARGE always returns the global maximum regardless of category filters.
- **Do not use a single workbook instance loaded with `data_only=True` for both reading and writing**. Writing with that instance will strip all formulas, replacing them with their last computed values. Always use a separate workbook instance for writing.
- **Sheet name casing**: Use `wb.sheetnames` to get exact casing; do not assume it matches expectations.
- **Stale destination data**: Always clear target ranges before writing new values.
- **Formula cells**: When checking cell values that may be formulas, load the workbook with `data_only=True` to read evaluated results, not formula text.
- **Row insertions and deletions**: Process target rows in descending order (highest first) to prevent index drift.
- **Range constraints**: Always explicitly limit operations to the specified cell range (e.g., `A7:A1000`). Avoid iterating over header rows or beyond the data boundary.
- **Incorrect condition ordering**: Implementing conditions in a different order than specified, especially missing prerequisite checks.
- **Omitting formatting**: Focusing only on data values and neglecting cell styling requirements.
- **Formula-based solutions may fail with dynamic ranges or irregular data**. When encountering #NUM! or similar errors, switch to direct cell-writing scripts. See [Script Fallback](references/script-fallback.md).
- **Stopping after read-only inspection** without writing the required output file.
- **Exploration loop**: Repeating inspections without implementing the solution. Limit to one inspection round.
- **Ignoring system warnings**: If the system indicates the output file is missing, immediately create it instead of running more diagnostics.
- **Type errors on headers**: Applying numeric filters (e.g., `-1 <= x <= 1`) to string headers raises TypeError. Always type-check first.
- **Non-unique key assumptions**: Assuming a simple pair is unique when it is not; the same meet+race can occur on different dates. Extend the key with additional fields.
- **Group-sort misinterpretation**: When a task specifies a priority grouping followed by a column sort, apply the grouping first and preserve the original intra-group order, then perform a **global** sort on the entire collection. Do not sort within groups unless explicitly instructed.
- **Creating a new workbook or calling formatting methods** can strip existing cell styles. Always load and modify in place unless the task explicitly requires reformatting.
- **Writing into merged cells** without unmerging first can raise errors or unexpected results.
- **Assuming data is contiguous**: empty rows are valid and must remain unchanged.
- **DO NOT parse formula strings to extract values**; use `data_only=True` on a separate read-only workbook instance.
- **DO NOT assume all cells contain numbers**. Explicitly handle `None` by converting to `0` before arithmetic.
- **Hard-coded ranges for semi-structured data**: Sheets with repeating header/value layouts break when ranges are fixed. Scan for headers instead.
- **Avoid debugging broken embedded macros (VBA)**. Reimplement the logic in Python using openpyxl instead.
- **Do not write to source or reference sheets** while producing an output sheet. Always separate the read phase from the write phase and restrict writes to the exact answer range.
- **Hard-coding column letters** when the spreadsheet structure may change; always scan headers.
- **Deleting a source column before copying data** to its destination, causing irreversible data loss.
- **Accidental formula destruction**: Array formulas (e.g., SUMPRODUCT) in header or aggregate rows are overwritten if you iterate all cells. Always filter rows by a distinguishing column's `data_only` value before writing.
- **Duplicate ranks from ties**: Built-in rank formulas can assign the same rank to tied values. For consecutive, no-gap ranks, use the sequential rank assignment pattern (see [Ranking Patterns](references/ranking-patterns.md)).
- **When inspecting cell fill colours with `openpyxl`**, always convert `fgColor.rgb` to a string with `str()` before any string operations (length, slicing, comparison) to avoid `TypeError`.
- **If a specific target range is given** (e.g., `A1:AH1`), enforce a hard column limit to avoid overwriting beyond the intended area.
- **Unconstrained ranges**: Explicitly bound loops and queries to the target range (e.g., `range(1000, 6, -1)`) to avoid matching header rows or out-of-scope data.
- **Relying on formula recalculation** may result in unpopulated or stale output; use literal values when feasible.
- **Treating auxiliary column values on a reference sheet as ground truth** when cell formatting (fills, fonts) encodes the answer.
- **Failing to clean stale manual-annotation data** from the output sheet before saving.
- **Off-by-one KeyErrors**: Dictionary keys built from column positions must use the same indexing base as cell access code.
- **Missing constraint rows**: Always dump the full sheet to discover configuration rows (min/max, thresholds) before writing logic.
- **Zero-cell mutation**: If requirements say "do not change zero cells", explicitly guard with `if current == 0: capacity = 0` in distribution loops.
- **Header-as-data**: Iterating from row 1 when row 1 is a header row overwrites column labels. Always verify whether the first row is data or headers before looping.
- **Whitespace artifacts on split**: When splitting a string at a character-class boundary, trailing whitespace often remains on the left part and leading whitespace on the right. Apply `.rstrip()` to the left portion and `.lstrip()` to the right portion.
- **Overwriting entire sheets or ranges**, which can clear pre-filled data or styles.
- **Failing to inspect example rows**, leading to incorrect pattern deduction.
- **Overlooking case sensitivity in comparisons**; always check with `.isupper()`/`.islower()` if case matters.
- **Assuming blank cells are empty strings ("")** instead of `None` — always inspect first.
- **Hardcoding a sheet name that may not exist** — fall back to processing all available sheets if the expected sheet is missing.
- **Replacing formulas with pre-computed static values** when the task asks to modify formulas.
- **Changing the underlying data type of formula outputs** (e.g., writing datetime objects where strings are expected).
- **When extracting substrings from structured text**, verify character positions against the actual data format before constructing formulas.
- **Spreadsheet libraries can silently produce empty or truncated files**. Always verify output after save.
- **Modifying input sheets** instead of the output sheet.
- **Using nested loops instead of dictionary lookup**, leading to inefficiency.
- **Not preserving the order of a master list** when merging.
- **Hardcoding labels from instructions**: Task descriptions may use approximate or illustrative names. Always derive headers and categorical labels from the actual source data to avoid mismatches.
- **Key Mismatches from Formatting**: When extracting lookup keys from spreadsheet cells, normalize them by stripping whitespace (e.g., `str(value).strip()`) and converting to a consistent type.
- **Deleting rows iteratively from top to bottom** shifts indices and causes missed deletions. Always process deletions bottom-up.
- **Treat `None` cell values as 0** in arithmetic operations to safely handle sparsely populated numeric columns. Normalize `None` to 0 before performing calculations to avoid type errors.

### Numeric Comparisons
- **Percentage thresholds**: Use integer arithmetic to avoid floating-point errors. For a P% increase check, write `value * 100 >= reference * (100 + P)`. Never use `value >= reference * 1.P`.
- **Restart/reset semantics**: "Restart from the cell immediately right of X" means the new reference is the adjacent cell (index+1), not X itself. Verify restart logic against embedded markers or annotations in the input data.

See [Numeric Patterns](references/numeric-patterns.md) for detailed examples.


## Data Extraction

## Text Manipulation

- To align the case of the first character of one cell value with another, use Python string methods: check `cell[0].isupper()` or `.islower()`, then apply `.upper()` or `.lower()` to the target's first character.

## Lookup Patterns

## Data Analysis

- To find duplicate rows in a column, use `collections.Counter` on all values from that column. Values with count > 1 identify the duplicate keys for extracting rows.