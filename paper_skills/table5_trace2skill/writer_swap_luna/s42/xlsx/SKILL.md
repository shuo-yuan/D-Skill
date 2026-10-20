---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow

1. **Read and understand** the entire task before acting.
2. **Inspect the workbook** (see [Inspection](#inspection)): load the workbook, examine sheet names, dimensions, headers, data ranges, and sample values. Never assume structure. Detect data ranges dynamically (see [Dynamic Range Detection](references/dynamic-range-detection.md)).
3. **Plan the transformation**: identify source and target ranges, keys, sort orders, formula patterns, and the order of operations. For lookups, determine composite keys if needed. For deletions, decide whether to stop at first match or process all. For marker-based operations, plan interval boundaries.
4. **Pre-process data**: normalize dates (see [Date Handling](references/date-handling.md)), apply filters, build in-memory mappings.
5. **Execute changes** (see [Writing Output](#writing-output)):
   - Prefer writing materialized values over formulas when using openpyxl; if formulas are required, use proven patterns (see [Formula Patterns](references/formula-patterns.md) and [Ranking Patterns](references/ranking-patterns.md)).
   - For row deletions or insertions, process from bottom upward to avoid index shifts.
   - For text matching, use case-insensitive comparison and stop at first match if required (see [Text Matching and Row Deletion](references/text-matching-deletion.md)).
   - Preserve source formatting; apply number formats explicitly after value edits.
   - Batch all edits and save once.
6. **Verify** (see [Verification](#verification)): reload the workbook, check representative cells, confirm correct sheets modified, no unintended changes, and file exists at exact path.
7. **Save** to the exact requested output path.

For specialized tasks like rebuilding summary sheets, synchronizing sheets by ID, or marker-based trimming, refer to the patterns in [Writing Output](#writing-output) and the reference files.

## Inspection

- **General**: Load the workbook and verify sheet names, dimensions, headers, and sample values before any edit. Print dimensions and row values for the affected region. Identify blank rows, gaps, and populated ranges.
- **Data ranges**: Identify exact data ranges with explicit row and column bounds. Use `ws.dimensions`, `ws.iter_rows()`, or `ws.values`. Scan the entire used range of relevant columns; do not stop at the first contiguous block if repeated headers or separated data sections may exist. Detect data ranges dynamically (see [Dynamic Range Detection](references/dynamic-range-detection.md)).
- **Headers and structure**: Identify header rows and data start rows to avoid off-by-one errors. Locate target columns by scanning the header row for exact labels instead of hardcoding column letters. When a worksheet is identified by number, use its positional index (1-based or zero-based as appropriate). Check for merged cells and unmerge them if they overlap target cells.
- **Values and types**: Inspect cell values to confirm data types (strings, numbers, dates). Normalize mixed date representations before sorting or filtering (see [Date Handling](references/date-handling.md)). When processing numeric columns, start below the header and handle non-numeric cells gracefully. For substring or keyword matching, normalize case (e.g., `str(value).casefold()`).
- **Duplicates**: When identifying duplicates, use all identity fields specified by the task. Count occurrences of the key column and retain every row whose key count exceeds one (do not keep only first or last).
- **Searching**: Restrict searches to the exact column and row range specified. Match literal values exactly; distinguish literal text from formulas or cell contents that merely contain the text. For text search, scan top-to-bottom and stop at the first match when required. When extracting substrings, split on the marker string rather than relying on fixed character positions.
- **Filtering and conditions**: When selecting cells based on formatting, also require a nonblank value. For date filtering, use inclusive bounds and derive relative-date cutoffs from the maximum date present in the data, not from an assumed reference. Apply all inclusion and exclusion criteria together before writing results.
- **Pre-computation checks**: Before writing formulas, identify upstream/intermediate cells, verify that mapping keys are unique for each destination row, and confirm the data pattern (cumulative vs. per-row). Inspect source data row by row to understand the actual data pattern before deciding on a transformation strategy.
- **Multi-sheet**: When processing multiple sheets, use sheet order to identify boundaries (e.g., stop before a summary sheet). Identify input sheets, output sheets, and required matching direction before transforming data.

## Writing Output

### General Rules
- **Target only the specified output range**. Clear the destination range before writing to avoid stale data. Populate all output cells (headers + data rows) in one pass, then save once.
- **Prefer materialized values** over formulas when using openpyxl, because it does not evaluate formulas. If formulas are required, recalculate the workbook before final evaluation, or write calculated numeric values directly.
- **Preserve existing data**: Before overwriting, check if the requested result is already present; skip those cells. When transferring data, only overwrite destination cells if the source has a value (not `None` and not empty string). For non-matching rows, explicitly clear the target cell.
- **Save to the exact output path** provided. Do not rename or relocate the file. After saving, confirm the file exists.

### Data Transformation
- **In-memory mapping**: Convert lookup-table rows into a dictionary keyed by the match column(s) before processing main data.
- **Row-wise iteration**: For bulk updates, iterate over populated data rows rather than writing one-off formulas per cell. Use aligned row-wise mapping when target rows correspond to the same rows in a reference sheet.
- **Sorting**: When sorting paired columns, collect rows as tuples, sort by the key, and write back. For multi-key sorts, convert date strings to datetime keys and sort by numeric fields first, then date fields. For frequency-based sorting, compute a frequency map, sort by counts, and preserve first-appearance order for ties.
- **Transposition**: Flatten source records in original order and pack into destination cells using a deterministic rule. Write retained values sequentially without gaps.
- **Unpivoting**: Preserve identifying columns and emit one normalized row per variable value.
- **Row expansion from count column**: Read the count value, emit that many copies using `max(1, int(count))` as a safe fallback. Snapshot source row locations before writing duplicates to avoid reprocessing newly created rows.
- **Consolidation**: Group by the specified reference column, preserve first-seen group order, keep identifying fields from the first row, and aggregate numeric values. Copy source formatting and apply custom number formats only to aggregated columns.

### Formulas
- **Absolute vs. relative references**: Lock lookup table ranges with absolute references (`$A$1:$B$10`). Keep input references relative as needed. When filling formulas, make source data ranges absolute and summary label references relative.
- **Cumulative formulas**: Use expanding mixed-reference ranges (e.g., `$A$2:A{r}`). Anchor the starting cell and let the ending row change with the destination row.
- **Lookups**: Prefer `INDEX`/`MATCH` over nested `IF`s. For multi-criteria matching, combine Boolean arrays and use `MATCH(1, ... , 0)`. For two-dimensional tables, use separate row and column `MATCH` inside `INDEX`. Wrap lookups in `IFERROR` or `IFNA` to handle missing keys gracefully.
- **Conditional logic**: Nest conditions in the exact task-specified order. For mutually prioritized outcomes, return the fallback only after all preceding tests are zero. Use `IF` with a nonblank guard to apply transformations only when source data exists.
- **Aggregation**: Use `SUMIF`/`SUMIFS` for conditional sums. For wildcard matching of embedded text, use `"*"&search_term&"*"`. For unique counts, use `=COUNTA(UNIQUE(FILTER(range, range<>"")))`.
- **Ranking**: For tied descending ranks within groups, use a combination of `COUNTIFS` for strictly greater values and a cumulative `COUNTIFS` for equal values up to the current row, with group constraints (see [Ranking Patterns](references/ranking-patterns.md)).
- **Piecewise scaling**: For proportional scaling with negative values, use `5 * value / abs(min_negative)` (the sign comes from `value` itself). Verify with sample inputs.
- **Composite identifiers**: When constructing concatenated strings, explicitly verify every required literal, separator, and component before filling.
- **Formula application**: Generate formulas programmatically across the target range; do not hand-place isolated formulas. After writing formulas, recalculate and read back results to confirm correctness.

### Formatting
- **Apply formatting after value edits**. Formatting must not replace or coerce cell values.
- **Copy source formatting** when transferring rows: copy cell styles, number formats, alignment, fonts, fills, borders, protection, and column widths.
- **Explicit number formats**: Apply number formatting explicitly to the target range using the exact format string (e.g., `m/dd/yyyy`). Do not rely on inherited formatting.
- **Font changes**: Copy the existing font object first, modify only the target property, and reapply.
- **Conditional formatting**: Apply dependent formatting only after the corresponding value has been written and validated as nonempty.

### Row Deletion and Insertion
- **Bottom-up processing**: When deleting or inserting multiple rows, collect target row numbers first, then process from the bottom upward to prevent index shifts.
- **Header protection**: Treat header rows as protected; never delete or filter them out. Start deletion below the header row (e.g., row 2).
- **Insertion**: When inserting rows into a formatted worksheet, copy row height, hidden state, and cell styles from the nearest existing row.
- **Deletion conditions**: Before deleting rows, evaluate every cell in the specified columns. Treat both `None` and whitespace-only strings as blank, and delete a row only when all target cells are blank. For marker-based deletion, delete all rows above the marker but keep the marker row itself. For text-matching deletion, stop at the first match unless instructed otherwise (see [Text Matching and Row Deletion](references/text-matching-deletion.md)).
- **Compound conditions**: Use compound conditions to protect data rows (e.g., require a target marker and a blank following cell) before deleting.

### Lookups and Matching
- **Composite keys**: When a result depends on both a row label and a column header, use composite-key matching.
- **Duplicate keys**: When lookup keys can repeat, collect every matching record rather than stopping at the first match; preserve source order.
- **Approximate match for dates**: For sorted historical data, prefer approximate match (`VLOOKUP` with `TRUE` or `INDEX/MATCH` with `1`) over exact match unless an exact date is required.
- **Containment matching**: When matching compound labels against component names, check whether the shorter header appears inside the longer entry. Use substring containment, not exact equality, when the task says "look for" or "find".
- **Text matching**: Normalize case with `.casefold()` for case-insensitive comparisons. For prefix checks, use `startswith()` after confirming the cell contains a string.

### Output Management
- **Clear and repopulate**: Before writing filtered or relocated rows, clear the entire destination range. Write contiguously: copy only the requested source columns, place each qualifying row into the next available destination row starting at the specified cell.
- **Total rows**: Identify final total rows before clearing or rebuilding a block. Populate data rows only within the data range, then write the total label and formula in the designated total row.
- **Preserve structure**: Modify only the specified output cells; do not add/remove headers, change formatting, or alter unrelated content unless explicitly instructed.
- **Sheet references**: When an instruction refers to a sheet by number, use the worksheet at that positional index.
- **Batch edits**: Combine all requested edits (value writes, formatting, sheet operations) into one final workbook update before saving. Delete or rename sheets as the final step.
- **Recalculation**: After inserting formulas, recalculate the workbook before saving. Use a spreadsheet engine or a calculation-capable tool if openpyxl is used.

## Verification

- **Post-save checks**: Save the workbook to the exact output path, then confirm the file exists (check path and size). Reopen the saved workbook with `data_only=True` to read cached values.
- **Range validation**: Inspect the exact answer range: every required cell must contain a visible value (not empty, not a formula string). Validate the entire requested range, including blank cells, headers, first/last rows, and transitions between groups. Confirm the correct sheets were modified and no unintended changes occurred elsewhere.
- **Spot-checking**: Verify a few representative cells (header, first data row, last data row, rows after gaps) against expected values. For formulas, recalculate and read back results; spot-check at least one row manually against source data.
- **Formula verification**: After writing formulas, confirm that absolute references stay fixed and relative references shift correctly when copied. Check both matched and unmatched rows to verify `IFERROR`/`IFNA` behavior. For cumulative formulas, confirm empty intervals produce 0 and non-qualifying rows contain the expected placeholder.
- **Structural integrity**: After row deletions, verify the header row remains intact and the marker/target is at the intended position. After sorting, spot-check row alignment to ensure paired data stayed together. After column moves, verify the moved header and data are in the intended column and totals remain intact.
- **Formatting checks**: Confirm that number formats, styles, and alignments are preserved and applied only to the requested range. For date cells, verify the displayed format matches the requested format string.
- **Task-specific checks**:
  - For duplicates: confirm row count matches the expected number of keys with count >1.
  - For aggregations: spot-check composite keys to confirm totals match source rows.
  - For transpositions: confirm no blank cells between entries and destination formatting matches.
  - For row expansion: verify output row count equals the sum of safe counts.
  - For consolidation: confirm row count matches the number of unique groups.
  - For scaling: confirm max input maps to expected max output, min to min, zero to zero, and signs are preserved.
- **Dependent cells**: Verify all cells in the graded/answer range, including dependent cells that may rely on formulas you did not directly edit. If any cached values are missing or incorrect, recalculate and re-verify.
- **Final confirmation**: Before reporting success, read back the populated range and confirm each row contains the expected values. Ensure the output file exists at the exact requested path.

## Common Pitfalls

- **Skipping inspection**: Modifying sheets before confirming their structure leads to wrong-sheet and wrong-range errors. Always inspect first.
- **Assuming formulas will be evaluated**: openpyxl writes formulas but does not calculate them. Always verify with `data_only=True` and rewrite as values if needed.
- **Hardcoding positions**: Hardcoding column letters, row numbers, or fixed character positions without inspecting the actual layout causes errors. Use header-based lookups and dynamic range detection.
- **Wrong deletion order**: Inserting or deleting rows from top to bottom shifts subsequent targets. Always process from the bottom upward.
- **Overwriting existing data**: Always inspect target columns first and skip cells that already contain correct data. Clear destination ranges before writing to avoid stale data.
- **Formatting loss**: Writing values without copying source formatting loses number formats, alignment, and styles. Explicitly copy cell styles, number formats, and column widths when transferring data.
- **Shifting lookup ranges**: Copying a formula without absolute references on the lookup table causes the table range to shift. Always lock table ranges with `$`.
- **Unhandled missing keys**: `#N/A` or `#VALUE!` errors appear when a key is not found. Use `IFERROR` or `IFNA` to handle missing or invalid keys gracefully.
- **Single-key lookups for multi-criteria tasks**: When a result depends on two or more criteria, use composite-key matching instead of a single-field lookup.
- **Overly complex nested IFs**: Long IF chains are error-prone and hard to copy. Use `INDEX/MATCH` or `XLOOKUP` instead.
- **Circular references**: Referencing the target cell itself in a formula. Reference the upstream or intermediate cell instead.
- **Partial data collection**: Stopping at the first contiguous table when the worksheet contains repeated headers or multiple data blocks. Scan all rows in the target columns.
- **Sorting errors**: Sorting date strings without converting to datetime produces lexical order. Sorting by the wrong key or using a helper column when the task specifies a different sort column leads to incorrect results.
- **Sign errors in piecewise formulas**: Using an extra minus sign in the negative branch flips the sign. The negative branch should be `5 * value / abs(min)`.
- **String matching mistakes**: Using exact equality when the task requires substring containment. Not normalizing case before comparison. Using `ISNUMBER(SEARCH(...))` for "ends with" checks—use `=RIGHT(cell, LEN(reference))=reference` instead.
- **Ignoring blank cells**: Blank cells with formatting can be mistakenly selected when filtering by format alone. Always combine format checks with a nonblank condition.
- **Incorrect range sizing**: Using arbitrary large ranges or entire columns instead of bounded ranges based on the last populated row.
- **Forgetting to recalculate**: After writing formulas, recalculate the workbook before reading results. Otherwise, cached values may be empty.
- **Overwriting headers**: Applying row conditions to the entire sheet can delete or modify the header row. Always start data operations below the header.
- **In-place row rearrangement**: When sorting or reordering rows, snapshot row values and styles into independent lists first, sort the snapshots, then write back. Modifying live references corrupts data.
- **Unsafe count values**: When expanding rows based on a count column, use `max(1, int(value))` with a fallback of 1 for invalid or missing counts.
- **Stale data in output range**: Always clear the full destination range before writing; prior runs may have left longer results.
- **Applying formatting to wrong range**: Apply formatting only to the explicitly requested data range. Exclude headers and totals unless specified.
- **Wrong match mode for dates**: When the lookup date falls between historical dates, use approximate match, not exact match.
- **Omitted fixed identifier segments**: When constructing composite identifiers, verify every literal part before filling.
- **Testing only the first row**: Errors can appear in later rows or after gaps. Validate the first, a middle, and the last populated row.
- **Using COUNTIFS when a sum is needed**: If the output should be a total, use `SUMIF`; `COUNTIFS` only counts matching rows.
- **Confusing marker-based trimming with blank-row removal**: Locate the marker first, then remove the complete prefix before it; do not filter rows by content when the goal is to start at a specific marker.
- **Deleting the matching row itself**: When removing rows above a target, delete only rows 1 through (match_index - 1).
- **Skipping post-deletion validation**: After deleting rows, verify the marker/target is now the first row and data below it remains intact.
- **Writing nonmatching rows or leaving gaps**: Write only qualifying rows contiguously; clear non-matching cells.
- **Assuming input layout without inspection**: Never assume sheet names, column positions, or data ranges; always inspect the actual workbook.
- **Saving to wrong path**: Always save to the exact output filename and location specified in the task.
- **Not verifying output**: After saving, reload and verify the output matches expectations before reporting success.
