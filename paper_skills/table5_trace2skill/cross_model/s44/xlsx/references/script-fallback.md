# Script Fallback Patterns

When spreadsheet formulas fail (e.g., #NUM! errors from mismatched dynamic ranges or non-contiguous data), use a procedural script to write values directly.

## Core Pattern

```python
import openpyxl

wb = openpyxl.load_workbook('file.xlsx')
ws = wb.active

# Iterate rows and write static values only where needed
source_index = 0
source_values = [...]  # values collected via inspection

for row in range(2, ws.max_row + 1):
    cell_value = ws.cell(row=row, column=1).value
    if cell_value == 'TOTAL':  # delimiter row
        source_index += 1
    else:
        ws.cell(row=row, column=2).value = source_values[source_index]

wb.save('file.xlsx')
```

## When to Use

- Dynamic ranges produce formula errors
- Source data is non-contiguous or irregularly spaced
- Grouped values need assignment based on delimiter rows
- Direct cell-by-cell control is simpler than complex formula logic