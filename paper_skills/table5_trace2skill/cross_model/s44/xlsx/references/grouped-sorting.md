# Grouped Sorting Pattern

## When to Use
When data must be reordered such that rows belonging to the same category stay together, and the categories themselves follow a specific order distinct from the within-group row order.

## Pattern

1. **Deduce the logic from a reference table** if one exists. Compare the reference ordering with the source data to identify:
   - Grouping key column (e.g., stock symbol)
   - Within-group row order (e.g., ascending date, with special rows pinned last)
   - Inter-group order (e.g., by a numeric field descending)

2. **Group first, then sort groups and rows separately:**
   - Collect rows into groups keyed by the grouping column.
   - Sort rows inside each group by the within-group rule.
   - Sort the groups themselves by the aggregated inter-group property (e.g., max of a column per group).

3. **Flatten the sorted groups** into the final row sequence and write back.

## Formatting Preservation
When moving rows, copy each cell's full formatting object (`font`, `fill`, `border`, `alignment`, `number_format`) along with its value, then reapply after placement.