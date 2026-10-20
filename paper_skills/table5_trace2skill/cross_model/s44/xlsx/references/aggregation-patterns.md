# Aggregation Patterns

## Two-Pass "Last Date per Category" Aggregation

Use when the task requires: extracting the latest entry per group, then combining duplicates that share that latest date.

### Pattern

```python
from collections import defaultdict

# Pass 1: find max date per group
max_dates = {}
for row in data:
    group = row['brand']
    date = row['date']
    if group not in max_dates or date > max_dates[group]:
        max_dates[group] = date

# Pass 2: aggregate rows matching group + max_date
results = defaultdict(lambda: {'total': 0, 'first_row': None})
for row in data:
    group = row['brand']
    date = row['date']
    if date == max_dates[group]:
        entry = results[group]
        entry['total'] += row['value']
        if entry['first_row'] is None:
            entry['first_row'] = row  # preserve non-aggregated columns
```

### Why This Works
- Handles multiple records on the same latest date without data loss.
- Preserves non-aggregated columns (e.g., batch, origin) from the first matching row.
- Clean separation of "finding the target date" from "collecting matching rows" avoids nested loops and off-by-one errors.