---
name: xlsx
description: "Spreadsheet manipulation skills distilled from execution experience."
---

## Core Workflow

1. Inspect the actual workbook before editing: sheet names and positions, dimensions, headers, formulas, merged cells, populated bounds, blank separators, structural rows, lookup sheets, representative values, and the exact requested output path.
2. Map the explicitly requested source, destination, marker, lookup, criteria, and output ranges. Resolve numbered-sheet instructions by worksheet position, and use authoritative IDs or observed headers rather than assumed names, offsets, or relative positions.
3. Build stable in-memory mappings or source snapshots before transforming rows. Use composite keys for all identifying fields, preserve complete row records so associated columns remain aligned, and apply every inclusion, exclusion, ordering, and group criterion explicitly.
4. Make the smallest targeted change: preserve headers, separators, formulas, styles, dimensions, unrelated sheets, and existing correct destination values. Clear or rebuild only confirmed dynamic output regions, and never overwrite populated destinations with blank sources.
5. Process multiple deletions or insertions from the bottom upward and do not reprocess newly written rows. Save to the exact requested path, recalculate when formulas are written, then reopen and verify the completed workbook.

## Inspection

- Identify the header and first and last data rows explicitly. Detect populated blocks, repeated headers, marker intervals, blank separators, summary or `TOTAL` rows, and actual output bounds dynamically; keep structural rows outside data criteria unless requested.
- Restrict edits to the named worksheet, rows, columns, and cells. Record source indices before inserted columns or rows shift them, and inspect merged ranges overlapping target cells before writing.
- Normalize native datetimes, recognized date strings, numeric text, and whitespace consistently. Use inclusive date bounds when requested, derive relative-date cutoffs from the specified source column's maximum valid date, and treat `None` and whitespace-only strings as blank.
- For text, distinguish exact, substring, suffix, delimiter, and prefix requirements. Use `casefold()` for case-insensitive matching, type-check strings before prefix tests, and extract variable-position tags through the next delimiter or end of cell.
- For duplicate, grouped, or relationship-based tasks, inspect every identity field, category, eligibility condition, and protection constraint. Preserve first-seen group order, retain the first duplicate occurrence when duplicates qualify, and map existing synchronized rows by authoritative unique ID.
- Before formulas or lookups, identify all row and column criteria, complete source ranges, selectors, summary labels, upstream inputs, dependent cells, and required fallbacks. Confirm whether approximate date matching requires sorted data and whether a target formula would otherwise reference itself.

## Writing Output

- Write only within verified ranges and use direct value transformations or explicit mapping dictionaries with unchanged fallbacks when formulas are unnecessary. For trailing text, use the required suffix test or slicing; for literal quote cleanup, use literal replacement rather than broad patterns.
- Build composite-key aggregates and lookup maps once. Preserve every duplicate match in source order, flatten multi-column results in column order, retain identifying fields in wide-to-long output, and keep paired or associated columns together during sorting or movement.
- Use anchored copyable formulas: absolute lookup tables and selectors, relative intended row or header references, `SUMIF`/`SUMIFS` for stated criteria, exclusive next-month bounds with `EDATE`, wildcard criteria for embedded terms, and membership tests for multi-value criteria. Guard missing or optional inputs with `IFERROR`, `IFNA`, or explicit nonblank tests, and use upstream cells rather than formula targets as inputs.
- For cumulative formulas, anchor the starting row and vary only the ending row. Preserve condition priority and fallbacks; write zero for empty marker intervals. For group rankings, scope comparisons to the group and allocate ties according to the specified rule.
- For filtering and compact output, copy headers and all required populated columns, write qualifying rows contiguously, preserve source order or the requested frequency/tie ordering, and clear stale values and formatting only inside the destination range. For row expansion or transposition, snapshot original records and emit copies in source order without processing generated rows.
- For authoritative synchronization, follow the ID list's membership and order, reuse matching rows, create placeholders for missing IDs, and preserve reference formatting. For row moves or structural edits, copy values, formulas, styles, number formats, alignment, fonts, fills, borders, protection, widths, row heights, and hidden state as required.
- Apply requested number formats and other formatting explicitly to every modified target cell without replacing unrelated font or style attributes. Delete multiple rows bottom-to-top, preserve headers and structural totals, handle overlapping merges, and save directly to the exact requested filename and directory.

## Verification

- Confirm the exact output path, file existence, worksheet names and order, active sheet when relevant, dimensions, headers, merged ranges, and that no cells outside the requested scope changed. Reopen the saved workbook rather than relying on a successful save.
- Validate the complete requested range, including expected blanks, separators, formulas, evaluated values, styles, dimensions, and stale-output cleanup. Check beginning, middle, ending, boundary-date, marker-transition, nonmatch, duplicate, missing-key, numeric-text, and case/type variants.
- Verify source and destination row counts, contiguous output, original order or specified sorting, complete duplicate coverage, composite-key grouping, authoritative-ID membership and order, placeholder rows, aligned associated columns, and preserved structural rows.
- Inspect formulas with both formula text and cached or recalculated values. Confirm anchored ranges and selectors, intended relative references, complete lookup extents, fallback behavior, exclusive monthly boundaries, absence of circular references or `#REF!`, correct precedence, and usable calculated results.
- Confirm deletions and insertions handled each recorded original target exactly once, remained within bounds, preserved later rows and required groups, and respected marker-plus-related-cell protections. Verify styles, number formats, widths, heights, hidden states, formulas, and formatting scope.
- Compare totals, balances, scores, and aggregates with independently calculated values using appropriate numeric conversion and business tolerances rather than exact floating-point equality. Confirm required signs, tie ordering, endpoint placement, and that the source workbook remains unchanged when a separate output was requested.

## Common Pitfalls

- Do not assume sheet names, worksheet positions, fixed ranges, column letters, row bounds, marker spacing, unique keys, or block layouts; do not edit whole columns, headers, structural totals, unrelated sheets, or cells outside the requested scope.
- Do not treat headers, separators, formulas, similar text, non-string values, whitespace-only cells, or formatted blanks as ordinary qualifying data. Do not use broad substring matching for suffix or literal requirements, unsafe prefix checks, or case-sensitive logic when case-insensitive matching is required.
- Do not use partial keys, a single repeated label, or a non-unique grouping key when row and column criteria or composite identity are required. Do not stop at the first duplicate, overwrite complete destinations with blank sources, or discard authoritative IDs and placeholders.
- Do not create reversed marker ranges, hard-code monthly day counts, truncate source ranges, reference a formula's target as its input, leave selectors or lookup ranges unanchored, treat formula text as an evaluated result, or rely on a library to recalculate formulas.
- Do not process row changes top-down, reuse live worksheet cells as snapshots, reprocess generated rows, sort related columns independently, delete from a marker without required protections, or infer deletion bounds from worksheet maximum rows.
- Do not leave stale values or formatting, lose headers, populated columns, separators, styles, dimensions, signs, padding, delimiters, or explicit blank handling. Do not rebuild a worksheet when a value-only edit suffices, and do not save under an approximate path or skip post-save read-back.
