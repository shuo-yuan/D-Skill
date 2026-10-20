# Ranking Patterns

## Tied Descending Rank Within Groups (Sequential)

Use when you need descending ranks (highest value = 1) within categories, with ties broken by row order.

### Pattern
```excel
=IF(OR(value_cell="", group_cell=""), "",
  COUNTIFS(group_range, group_cell, value_range, ">"&value_cell) +
  COUNTIFS(group_range, group_cell, value_range, value_cell, 
           INDEX(range,1,1):INDEX(range,ROW(),COLUMN()), value_cell)
)
```

### How It Works
1. **Blank guard**: `IF(OR(...))` leaves the cell empty when value or group is missing.
2. **Strictly greater count**: `COUNTIFS` for all rows in the same group with a higher value.
3. **Cumulative tie count**: Second `COUNTIFS` counts equal values up to the current row, breaking ties sequentially.
4. **Group constraint**: Both `COUNTIFS` include the group field so rankings stay within each category.

### Verification
- Recalculate after inserting the formula.
- Confirm the first row in each group starts at rank 1.
- Confirm blank rows show empty, not 0 or #VALUE!.
- Spot-check a few tied values to ensure sequential ranks (e.g., 2, 3, 4 not 2, 2, 3).