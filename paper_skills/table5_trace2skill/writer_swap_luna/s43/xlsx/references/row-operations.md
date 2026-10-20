# Row Operations

## Deleting Multiple Rows Safely

When deleting rows that match a condition across the entire sheet:

1. **Start below headers.** Begin iteration from row 2 to preserve column headings.
2. **Iterate bottom-up.** Loop from `ws.max_row` down to row 2. This avoids shifting-row bugs where remaining rows change position after each deletion.
3. **Check cell type before string operations.** Confirm the cell value is a string before calling methods like `.startswith()` to avoid AttributeErrors on numeric or None cells.

### Example: Delete rows starting with "Z1" or "X1"

```python
for row_idx in range(ws.max_row, 1, -1):
    cell_value = ws.cell(row=row_idx, column=1).value
    if isinstance(cell_value, str) and (cell_value.startswith('Z1') or cell_value.startswith('X1')):
        ws.delete_rows(row_idx)
```

## Prefix and Pattern Matching

- Use Python string methods (`.startswith()`, `.endswith()`, `in`) directly instead of trying to replicate spreadsheet wildcard or filter syntax.
- Always guard with `isinstance(value, str)` before string operations.
