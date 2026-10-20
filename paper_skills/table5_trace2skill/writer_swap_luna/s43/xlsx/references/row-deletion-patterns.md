# Row Deletion Patterns

## Bottom-to-Top Deletion
When deleting rows based on cell content, iterate in reverse to avoid index corruption.

```python
# Example: delete rows where columns F-L are all blank
rows_to_delete = []
for row_idx in range(max_row, min_row - 1, -1):
    values = []
    for col in range(6, 13):  # columns F-L
        cell = ws.cell(row=row_idx, column=col).value
        values.append(cell)
    if all(v is None or str(v).strip() == '' for v in values):
        ws.delete_rows(row_idx)
```

Key points:
- Iterate from `max_row` down to `min_row`
- Check every target column before deciding
- Handle `None` and whitespace as blank
- Call `delete_rows` within the reverse loop (no deferred list needed if deleting immediately in reverse order)