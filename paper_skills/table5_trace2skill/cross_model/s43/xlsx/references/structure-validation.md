# Structure Validation Patterns

## Cross-Checking Range Dimensions

When `answer_position` specifies explicit output ranges, compare expected row counts against your data:

```python
expected_rows = end_row - start_row + 1
actual_items = len(data_for_this_range)
if actual_items < expected_rows:
    # Missing structural rows — likely a TOTAL, subtotal, or header
    missing = expected_rows - actual_items
    # Investigate original template for what belongs in those rows
```

## Detecting Summary Rows from Original Layout

Before clearing a sheet, scan for aggregate patterns:
- Cells containing 'TOTAL', 'SUM', 'SUBTOTAL', 'GRAND TOTAL'
- Rows with SUM/SUBTOTAL formulas
- Rows that are visually distinct (bold, borders, merged cells)

Record their positions and content so they can be regenerated after repopulation.

## Regenerating TOTAL Rows

After writing all data items for a category:
1. Compute the sum of the amount column for that category
2. Write 'TOTAL' in the label column at the next available row
3. Write the computed sum in the amount column
4. Verify the TOTAL row falls at the expected position matching `answer_position` dimensions
