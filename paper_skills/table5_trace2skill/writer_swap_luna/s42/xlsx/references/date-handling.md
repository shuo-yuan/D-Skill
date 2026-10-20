# Date Handling Patterns

## Normalizing Mixed Date Representations

When date cells may contain strings or datetime objects, normalize before formatting:

1. **Inspect the cell value type** — check whether it is a string, datetime, or other.
2. **Strip time suffixes from strings** — remove trailing time components (e.g., ` 00:00:00`) from string representations.
3. **Convert to date values** — transform date-only strings and datetime objects into date values for consistency.
4. **Apply formatting explicitly** — set the exact format string (e.g., `m/dd/yyyy`) on every modified cell.

## Example

```python
from datetime import datetime

for cell in target_range:
    val = cell.value
    if isinstance(val, str):
        # Strip time suffix if present
        val = val.split()[0]
        cell.value = datetime.strptime(val, "%Y-%m-%d").date()
    elif isinstance(val, datetime):
        cell.value = val.date()
    cell.number_format = 'm/dd/yyyy'
```

## Key Rules

- Never assume all date cells share the same type.
- Always set `number_format` explicitly on every modified cell.
- Verify by reading back a sample of formatted cells.