---
name: scripting-patterns
description: "Detailed regex patterns and openpyxl scripting templates for spreadsheet transformations."
---

# Scripting Patterns for Spreadsheet Transformations

## Regex for Delimited Tag Extraction
When parsing structured text fields where a known prefix tag (e.g., `Collection-`) appears at arbitrary positions, use `re.search` to capture values up to the first delimiter.

```python
import re

def extract_tag_value(text, prefix):
    if not isinstance(text, str):
        return ""
    pattern = rf"{re.escape(prefix)}\s*([^,\n]*)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""

# Usage:
# value = extract_tag_value(cell.value, "Tag-")
```

## Explicit Row-Range Mapping
Always calculate the exact iteration range to skip headers and avoid trailing blanks.

```python
from openpyxl import load_workbook

wb = load_workbook("input.xlsx")
ws = wb.active

# Define explicit ranges
start_row = 2  # Skip header
end_row = ws.max_row  # Or calculate dynamically to exclude trailing blanks

for row in range(start_row, end_row + 1):
    cell_a = ws.cell(row=row, column=1).value
    # Process cell_a...
    ws.cell(row=row, column=2).value = result
```

## Best Practices
- Use `isinstance(text, str)` checks before regex operations to handle numeric or None values safely.
- Print intermediate results to console for debugging before saving.
- Keep scripts focused on single transformations to reduce complexity.