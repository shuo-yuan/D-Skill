# Python Aggregation Patterns

Use when Excel formulas cannot express the required logic (e.g., case-sensitive matching, multi-row grouped aggregations).

## Pattern: Case-Sensitive Grouped Sum

```python
from openpyxl import load_workbook

def to_float(val):
    """Treat None and empty strings as 0.0."""
    if val is None or val == '':
        return 0.0
    return float(val)

wb = load_workbook('file.xlsx')
ws = wb.active

# 1. Inspect structure: print all cells to find column positions
for row in ws.iter_rows():
    for cell in row:
        print(f"{cell.coordinate}: {cell.value}")

# 2. Build aggregation (example: sum profit - expenses grouped by type)
agg = {}
for row in range(2, ws.max_row + 1):  # skip header
    key = ws.cell(row=row, column=type_col).value
    profit = to_float(ws.cell(row=row, column=profit_col).value)
    expenses = sum(to_float(ws.cell(row=row, column=c).value) for c in expense_cols)
    agg[key] = agg.get(key, 0) + profit - expenses

# 3. Write results as integers
for i, (key, total) in enumerate(agg.items(), start=2):
    cell = ws.cell(row=i, column=result_col)
    cell.value = int(round(total))
    cell.number_format = '0'

wb.save('file.xlsx')
```

## Key Rules
- Use `==` for case-sensitive string comparison (default Python behavior).
- Always inspect cell values with a print loop before writing code.
- Apply `int(round(...))` and `number_format = '0'` for integer output.