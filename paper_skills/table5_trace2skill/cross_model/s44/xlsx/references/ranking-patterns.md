# Sequential Rank Assignment with Tie-Breaking

Use this pattern when built-in ranking formulas produce duplicate ranks and you need consecutive integers (1, 2, 3, …) per category.

## Algorithm
1. Group rows by the category column.
2. Within each group, sort rows by the numeric value descending, then by original row index ascending (ties broken in listing order).
3. Assign ranks 1, 2, 3, … sequentially to the sorted rows.
4. Write the rank integers back to the target cells.

## Python Pseudocode
```python
import openpyxl
from collections import defaultdict

# Load workbook for writing (no data_only)
wb = openpyxl.load_workbook('file.xlsx')
ws = wb.active

# Gather rows: (row_idx, category, value)
rows = []
for row in range(2, ws.max_row + 1):
    category = ws.cell(row, CAT_COL).value
    value = ws.cell(row, VALUE_COL).value
    if category is not None and value is not None:
        rows.append((row, str(category), float(value)))

# Group and sort
by_category = defaultdict(list)
for r in rows:
    by_category[r[1]].append(r)

for cat, group in by_category.items():
    # Sort by value descending, then by row index ascending
    group.sort(key=lambda x: (-x[2], x[0]))
    for rank, (row_idx, _, _) in enumerate(group, start=1):
        ws.cell(row_idx, RANK_COL).value = rank

wb.save('file.xlsx')
```

## Key Points
- Sort criteria: `(-value, row_index)` ensures highest value gets rank 1 and original order breaks ties.
- Only rows with non-None category and value are included; header/aggregate rows are skipped.
- The workbook is opened without `data_only` so writes don't corrupt formulas elsewhere.