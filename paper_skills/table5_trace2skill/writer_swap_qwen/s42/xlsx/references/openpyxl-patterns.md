# openpyxl Safe Patterns

## Table of Contents
- [Safe Style Assignment](#safe-style-assignment)
- [Robust Date Parsing for Sorting](#robust-date-parsing-for-sorting)
- [Tuple-Based Multi-Criteria Sorting](#tuple-based-multi-criteria-sorting)

## Safe Style Assignment

Direct assignment of `cell.font` or `cell.alignment` from another cell's style can raise `TypeError: unhashable type: 'StyleProxy'`. Instead, copy properties explicitly:

```python
from openpyxl.styles import Font, Alignment

source_font = source_cell.font
target_cell.font = Font(
    name=source_font.name,
    size=source_font.size,
    bold=source_font.bold,
    italic=source_font.italic,
    color=source_font.color
)

source_align = source_cell.alignment
target_cell.alignment = Alignment(
    horizontal=source_align.horizontal,
    vertical=source_align.vertical,
    wrap_text=source_align.wrap_text
)
```

## Robust Date Parsing for Sorting

Spreadsheet date columns may contain `datetime` objects, strings in various formats, and `None`. Sort safely by normalizing all values:

```python
from datetime import datetime

def parse_date(value):
    if value is None:
        return datetime.min
    if isinstance(value, datetime):
        return value
    for fmt in ('%d/%m/%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(value, fmt)
        except (ValueError, TypeError):
            continue
    return datetime.min

sorted_rows = sorted(rows, key=lambda r: parse_date(r[date_col_idx]))
```

## Tuple-Based Multi-Criteria Sorting

For stable multi-level sorting, return a tuple from the key function:

```python
def sort_key(row):
    balance = row[balance_col]
    date = parse_date(row[date_col])
    return (balance, date)

sorted_rows = sorted(rows, key=sort_key)
```

Python compares tuples element by element, applying secondary criteria only when primary values are equal.
