---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow

Use Python with `openpyxl` for all spreadsheet operations; avoid VBA unless explicitly required. Follow this workflow:

1. **Inspect the workbook thoroughly**:
   - Load with `openpyxl.load_workbook(path, data_only=True)` when you need computed values; also load without `data_only` to preserve formatting for later writes.
   - Print sheet names (`wb.sheetnames`), dimensions, and dump all non-empty cells (coordinate, value, type, number_format) to understand layout.
   - Identify the exact output range (`answer_position`), input sheets, reference sheets, pre-filled target cells, headers, data rows, and any special rows (totals, subtotals).
   - Check for blank rows, hidden columns, merged cells, and mixed data types.

2. **Plan the transformation**:
   - Derive output structures from the actual data, not from instruction examples. Use `set()` or `Counter` to extract unique values.
   - Build efficient in-memory lookup structures: dictionaries keyed by single or composite keys (tuples), sets for membership tests.
   - For grouping/aggregation, use composite-key dicts; for ranking, group-then-rank; for latest-date-per-group, use two-pass grouping.
   - Reverse-engineer logic from any provided reference sheets or pre-filled target cells before scaling.
   - Prefer Python logic over Excel formulas for complex, conditional, or cumulative operations.

3. **Compute results in Python**:
   - Perform calculations, filtering, sorting, and aggregation in Python using standard libraries (`collections.Counter`, `datetime`, `re`, etc.).
   - For frequency-based sorting, use `Counter` and sort by `(-count, value)`; for regex extraction, use precise patterns with whitespace stripping.
   - Handle floating-point comparisons with tolerance; treat `None` as zero in arithmetic.

4. **Write output safely**:
   - Clear the target range (set cells to `None`) before writing new values to remove stale data.
   - Write only within the specified `answer_position`; do not modify input sheets or cells outside the range.
   - Preserve existing formatting: when copying cells, use a dual-workbook approach (one `data_only` for values, one without for formatting attributes).
   - Delete rows/columns in reverse order to avoid index shifting; for insertion, process from bottom to top.
   - For formula modification, replace only the specific sub-expression; keep the cell as a formula.
   - Save to a temporary path first, then atomically rename to the exact required output path; verify file existence with `os.path.exists` and `os.path.getsize`.

5. **Verify the output**:
   - Reload the saved file and read back key cells to confirm values, types, and formatting.
   - Compare against reference sheets, pre-filled targets, and task requirements.
   - Check row counts, header integrity, and that no data outside the output range was altered.
   - Spot-check edge cases, boundary conditions, and both positive and negative cases.## Core Workflow

## Inspection

Before any transformation, inspect the workbook thoroughly:

- Load the workbook with `openpyxl.load_workbook()`; if formulas are involved, also load with `data_only=True` to see cached values.
- Print sheet names, dimensions (`max_row`, `max_column`), and dump all non-empty cells with their coordinates, values, types, and `number_format`. This reveals headers, data ranges, blank rows, merged cells, and mixed types.
- Identify the exact output range, input sheets, reference sheets, and any pre-filled target cells. Treat input sheets as read-only.
- Detect dynamic boundaries: use `ws.max_row` instead of hardcoded ranges; scan for sentinel values to find block boundaries.
- When searching for text, normalize with `.strip().lower()` for robustness. For multi-value cells, split by comma and use exact match after stripping.
- Use `collections.Counter` to detect duplicate keys or values.
- For floating-point data, treat values within a small tolerance as effectively zero.
- To diagnose formula errors, compare the stored formulas (load without `data_only`) with cached computed values (load with `data_only`).
- Verify sheet names with `wb.sheetnames` before accessing to avoid `KeyError`.
- Inspect number formats alongside values to catch masked errors (e.g., `000` display).

## Writing Output

- **Clear target range first**: Set all cells in the output area to `None` to remove stale data from previous runs. Preserve headers.
- **Write only to specified range**: Confine all modifications to the exact `answer_position`. Do not alter input sheets or cells outside the range.
- **Prefer Python computation over Excel formulas**: For complex, conditional, or cumulative logic, compute results in Python and write literal values. Use formulas only when explicitly required and for simple cases.
- **Preserve formatting**: When copying cells, use a dual-workbook pattern: load one instance with `data_only=True` for values, another without for formatting attributes (`font`, `fill`, `border`, `alignment`, `number_format`). Apply formatting to destination cells.
- **Formula modification**: If asked to modify a formula, keep the cell as a formula and replace only the specific sub-expression. Preserve the original output type.
- **Safe row deletion/insertion**: Delete rows in reverse order (`reversed(sorted(indices))`). For insertion, process from bottom to top to avoid index shifting.
- **Handle blanks correctly**: Use `None` for blank cells, not empty strings. Treat `None` as `0` in arithmetic using a `to_float` helper.
- **Whitespace stripping**: When splitting strings at character boundaries, strip artifacts using `.rstrip()` and `.lstrip()`.
- **Unmerge before writing**: If target cells are part of merged ranges, unmerge them first to avoid write errors.
- **Floating-point tolerance**: Use a small absolute tolerance for comparisons instead of exact equality.
- **Integer formatting**: After arithmetic, convert with `int(round(total))` and set `number_format = '0'` for integer display.
- **Gap-aware iteration**: When writing to sparse columns, iterate over the full range but only write to non-empty source cells, incrementing counters conditionally.
- **Duplicate aggregation**: Build a dict mapping key to list of values, then flatten and write across columns using an indexed loop with column offset.
- **Ordered merge**: When a master list dictates sequence, iterate it and write rows in order, including placeholder rows for missing IDs.
- **Two-key lookup**: Use composite keys (tuples) for multi-column lookups.
- **Bounded distribution**: Define processing order, compute available capacity per column, apply `min(remaining, capacity)`, and update.
- **Column rearrangement**: Locate columns by header value, insert a blank column at destination, copy data, then delete source column. Capture and reapply formatting.
- **Block compaction**: Insert exactly one empty row between consecutive blocks, omit after the last, and remove trailing empty rows.
- **Unpivoting**: For each data row, iterate variable columns, emitting one new row per variable while carrying forward fixed columns.
- **Enrich via lookup dict**: Load reference data into a dict keyed by join column; use `dict.get()` during row generation.
- **Clean numeric strings**: Use `re.sub(r'[^0-9.-]', '', text)` to preserve digits, decimal points, and minus signs.
- **Date-based filtering**: Use `datetime` and `timedelta` to compute cutoffs; avoid string comparisons.
- **Delete columns by numeric index**: Determine index and use `worksheet.delete_cols(index)`.
- **Delimiter pointer for grouped values**: Maintain a pointer into a value list; advance only when a delimiter row (e.g., 'TOTAL') is encountered.
- **Multi-criteria INDEX/MATCH**: Use `MATCH(1, (range1=criteria1)*(range2=criteria2)..., 0)` for multi-column lookups.
- **Batch string replacement**: Use a double loop over `iter_rows()` to replace substrings in all string cells.
- **Save and verify**: Save to a temp path, atomically rename, then check existence with `os.path.exists` and `os.path.getsize`.## Writing Output

## Verification

After saving, perform these checks:

- **File existence and size**: Confirm the output file exists at the exact required path and is non-empty (`os.path.getsize > 0`).
- **Reload and read back**: Reopen the file with `openpyxl` (and `data_only=True` if needed) and read key cells to verify values, types, and number formats.
- **Row count validation**: Compare written rows against expected counts from `answer_position` ranges; ensure structural rows (totals, subtotals) are present.
- **Reference sheet cross-check**: If a reference sheet exists, compare output cell-by-cell; verify formatting matches.
- **Annotation oracle**: Check pre-filled target cells or annotations as implicit expected outputs; confirm alignment.
- **Scope check**: Ensure only cells within the specified output range were modified; input sheets remain unchanged.
- **Header integrity**: Confirm headers are untouched and no stale data lingers below the output.
- **Edge cases**: Spot-check boundary rows, first and last data rows, and both positive and negative cases.
- **Sort order**: For sorted output, confirm the order matches requirements (e.g., lexicographic A-Z).
- **Formula verification**: If formulas were written, recalculate and read back results; ensure they produce correct values.
- **Structural changes**: After row/column deletions, verify `max_row`/`max_column` and that remaining data is correctly positioned.
- **Checklist**: Create a checklist from the task's explicit requirements and verify each one before finalizing.## Verification

## Common Pitfalls

### Logic and Data Handling
- **Assuming key uniqueness**: Verify composite keys are deterministic; add fields if needed.
- **Hardcoding labels from instructions**: Always extract headers, categories, and keys from the actual data.
- **Sequential conditions**: Nest later conditions inside earlier ones when tasks specify a numbered sequence.
- **Incomplete deliverables**: Review the task description line-by-line to ensure all requirements are implemented.
- **Sorting**: "A to Z" means lexicographic string sort; do not parse embedded numbers unless specified.
- **Sort scope with grouping**: Apply grouping as a pre-processing step, then perform a global sort; preserve intra-group order unless instructed otherwise.
- **Floating-point thresholds**: Use scaled integer arithmetic (`value * 100 >= reference * (100 + percentage)`) to avoid representation errors.
- **Positional restart semantics**: When resetting from an adjacent cell, skip that cell in the next comparison (advance index by 2).

### Inspection and Assumptions
- **Skipping inspection**: Leads to wrong column assumptions and off-by-one errors. Always dump cell contents first.
- **Hardcoding row numbers**: Use dynamic detection (`max_row`, sentinel scanning) instead of fixed ranges.
- **Assuming uniform cell types**: Check `type` and `number_format`; handle mixed types explicitly.
- **Missing sheet names**: Always verify with `wb.sheetnames`; fall back to processing all sheets if target missing.
- **Regex overuse**: For simple prefix/substring checks, use `startswith` or `in` instead of regular expressions.

### Writing and Deletion
- **Overwriting input sheets**: Always double-check that writes target only the output range.
- **Stale output**: Clear the target range before writing to remove leftovers.
- **Top-down row deletion**: Causes index shifting; always delete in reverse order.
- **Formatting destruction**: Do not add headers, styles, or modify cells outside the output range.
- **Lost formatting on copy**: Use dual-workbook approach to preserve `number_format`, `font`, etc.
- **Using `data_only` workbook for writes**: Formulas and formatting may be lost; use a separate non-`data_only` instance.
- **Recreating workbooks**: Do not create a new workbook when the task requires preserving existing formatting.
- **Unmerge before write**: Writing to merged cells fails; unmerge first.
- **Formula replacement**: When asked to modify a formula, do not replace it with a static value; keep it as a formula.
- **Circular references**: Compute the intended value externally and write the literal result.

### Tool Usage and Process
- **Bash tool argument errors**: Adapt call format immediately if `unexpected keyword argument` occurs; use `"command"` directly.
- **Directional search misinterpretation**: "above" means search descending from reference row -1; "below" means ascending from +1; "left of" means right-to-left; "right of" means left-to-right.
- **Exploration-only loop**: Inspect once, then implement; do not loop between inspection and action.
- **Ignoring output-missing warnings**: If the system says the output file wasn't created, save it immediately.
- **Skipping verification**: Always reload and read back the output before declaring success.
- **Stdlib module filename conflicts**: Avoid naming scripts after standard-library modules (e.g., `inspect.py`, `csv.py`).

### Formula and Type Errors
- **Replacing formulas with hard-coded values** when asked to modify formulas.
- **Writing datetime objects with number formatting** when original formulas produced strings.
- **Using `TODAY()` or external functions** when the requirement is to extract data from a source cell.
- **Partial formula success**: A formula that works for the first row may fail for others; validate across multiple rows.
- **Multi-criteria MATCH**: Single-criterion MATCH returns the first match; use multi-criteria array multiplication for unique identification.

### Reference Sheet Misuse
- Treating non-formatting auxiliary data as ground truth.
- Preserving stale manual annotations in the output.
- Assuming the target is wrong when computed results don't match; re-validate cell selection logic.

### Scope and Format Rules
- **DO NOT** alter cells outside the explicit `answer_position` range.
- **DO NOT** copy source cell formatting when the task only requires transferring values; preserve the destination's format.
- **DO NOT** signal completion before confirming the output file exists on disk.## Common Pitfalls
