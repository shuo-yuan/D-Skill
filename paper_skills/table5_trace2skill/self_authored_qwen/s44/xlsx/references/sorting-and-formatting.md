# Sorting and Formatting Patterns

## Safe Style Assignment
Avoid direct assignment of `cell.font` or `cell.alignment` objects to prevent `StyleProxy` errors.
Instead, explicitly create new objects:

```python
from openpyxl.styles import Font, Alignment
# ...
new_font = Font(name=source_cell.font.name, size=source_cell.font.size, bold=source_cell.font.bold)
target_cell.font = new_font
```

## Robust Date Parsing
Create a dedicated date parsing helper function to handle mixed date formats and null values when sorting.

```python
from datetime import datetime
def parse_date(val):
    if not val: return datetime.min
    for fmt in ('%d/%m/%Y', '%Y-%m-%d'):
        try: return datetime.strptime(val, fmt)
        except: pass
    return val
```

## Tuple-Based Multi-Criteria Sorting
Use a sorting key function that returns a tuple for stable multi-level sorting.

```python
def sort_key(row):
    return (parse_date(row.date_col), row.balance_col)
rows.sort(key=sort_key)
```