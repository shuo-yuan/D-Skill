---
name: openpyxl-patterns
description: "Code patterns for safe styling, date parsing, and sorting."
---

## Safe Style Assignment
Avoid direct assignment of `cell.font` or `cell.alignment` objects to prevent `StyleProxy` errors when copying formatting.

```python
from openpyxl.styles import Font, Alignment

# Instead of: target_cell.font = source_cell.font
src_font = source_cell.font
new_font = Font(
    name=src_font.name,
    size=src_font.size,
    bold=src_font.bold,
    italic=src_font.italic,
    color=src_font.color
)
target_cell.font = new_font
```

## Robust Date Parsing
Create a dedicated parser to handle mixed date formats and `None` values before sorting.

```python
from datetime import datetime

def parse_date(val):
    if val is None:
        return datetime.max
    if isinstance(val, datetime):
        return val
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y'):
        try:
            return datetime.strptime(val, fmt)
        except (ValueError, TypeError):
            continue
    return datetime.max
```

## Tuple-Based Multi-Criteria Sorting
Use a sorting key function that returns a tuple to achieve stable multi-level sorting.

```python
# Example: Sort by Balance (asc), then Date (asc)
rows.sort(key=lambda r: (parse_date(r[1]), r[0]))
```
Python's default tuple comparison handles the hierarchy automatically. Ensure all elements in the tuple are comparable to avoid `TypeError`.