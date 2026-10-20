# Formula Patterns

Patterns that have repeatedly succeeded in practice.

## OR-List Matching with SUMPRODUCT

When a conditional sum must match any value from a list, do NOT pass the list range directly as a single `SUMIFS` criterion. Instead, use `ISNUMBER(MATCH(...))` inside `SUMPRODUCT`:

```
=SUMPRODUCT((ISNUMBER(MATCH(data_range, criteria_list, 0)))*1, sum_range)
```

This creates a Boolean mask for list membership and works reliably for multi-value criteria.

## Exclusive Next-Month Date Boundary

For monthly aggregation, use a lower bound at the current month and an exclusive upper bound at the first day of the next month:

```
=SUMIFS(sum_range, date_range, ">="&month_header, date_range, "<"&EDATE(month_header,1))
```

This avoids hard-coding day 31 and correctly handles months with fewer days and time components in date values.

## Non-Contiguous Data

When related event types are in different columns, use separate conditional counts (e.g., COUNTIFS) and combine them with an AND condition. Avoid assuming a single contiguous range.

## Group Gating

To return a result only once per consecutive group, compare the current group key with the previous row's key (e.g., `IF(A2<>A1, ...)`) so the output appears only on the first row of each group.

## Multi-Criteria Lookup with INDEX/MATCH

When a lookup table contains repeated labels, combine Boolean criteria (e.g., `(category_range=sel_cat)*(expense_range=sel_exp)`) and use `MATCH(1, ... , 0)` to identify the correct row. Use absolute anchoring for source ranges and selector cells (`$`). Wrap the result with `IFNA(...,0)` to return zero when the combination is missing.

For two-dimensional lookups, use one `MATCH` for the row (category/expense combination) and a second `MATCH` for the column header (e.g., `C$3`).

## Precise Suffix Verification

To verify that a cell ends exactly with another cell's value (and nothing after), use `=RIGHT(cell, LEN(reference))=reference`. This confirms the reference is the final portion, rejecting any extra trailing text that a substring check would miss.