# Consolidation Patterns

## Dictionary-Based Grouping for Row Consolidation
When merging rows by a key column (e.g., column H), collect rows into a dictionary keyed by that column. For each group, iterate over all collected rows and sum numeric columns, treating non-standard blanks (`\xa0`, empty strings) as zero. This pattern reliably consolidates data without missing rows.

Example (openpyxl):
```python
groups = {}
for row in ws.iter_rows(min_row=2, values_only=False):
    key = row[7].value  # column H
    groups.setdefault(key, []).append(row)

for key, rows in groups.items():
    total = [0.0] * num_cols
    for row in rows:
        for i in range(num_cols):
            val = row[i].value
            if val is None or val == '\xa0' or val == '':
                val = 0
            total[i] += float(val)
```

## Preserve Source Cell Formatting with `copy()`
When copying cells between sheets, replicate all style attributes using `copy()` to maintain the original appearance. This prevents loss of visual consistency.

Example (openpyxl):
```python
from copy import copy

for src_cell, dst_cell in zip(src_row, dst_row):
    dst_cell.font = copy(src_cell.font)
    dst_cell.border = copy(src_cell.border)
    dst_cell.fill = copy(src_cell.fill)
    dst_cell.alignment = copy(src_cell.alignment)
    dst_cell.number_format = src_cell.number_format
```

## Zero-as-Blank Display with Decimal Formatting
To meet a requirement that zeros display as blanks while still showing decimals, set the cell value to `None` when the computed sum is zero, and apply a fixed number format like `'0.00'` to all aggregated cells. This cleanly satisfies both conditions without interference.

Example (openpyxl):
```python
for i, total in enumerate(totals):
    cell = ws_out.cell(row=out_row, column=start_col + i)
    cell.value = None if total == 0.0 else total
    cell.number_format = '0.00'
```
