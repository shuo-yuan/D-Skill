# Sorting Patterns

## Group-Then-Sort Workflow

When rows must be reordered such that related rows stay together and groups follow a specific order:

1. **Collect rows into groups** based on a key column (e.g., stock symbol in column A).
2. **Sort rows within each group** by the within-group rule (e.g., date ascending).
   - Pin special rows (e.g., those with a non-null value in a specific column) to the end of their group.
3. **Sort the groups** by an aggregated property (e.g., `max(R_DAYS)`) descending.
4. **Flatten the groups** back into a single row sequence.
5. **Write rows back** preserving all cell formatting.

## Formatting Preservation

When moving cells with openpyxl:

```python
# Read formatting from source cell
src_cell = ws.cell(row=src_row, column=col)
fmt = {
    'font': src_cell.font,
    'fill': src_cell.fill,
    'border': src_cell.border,
    'alignment': src_cell.alignment,
    'number_format': src_cell.number_format,
}
val = src_cell.value

# Apply to target cell
tgt_cell = ws.cell(row=tgt_row, column=col)
tgt_cell.value = val
for attr, val_ in fmt.items():
    setattr(tgt_cell, attr, val_)
```

## Reference-Table Inspection

Before coding, look for sheets or ranges labeled "Expected Results" or similar. Diff the reference data against source data to infer:
- Grouping column(s)
- Within-group sort keys and direction
- Which rows are pinned to start or end of groups
- Inter-group sort key and aggregation method
