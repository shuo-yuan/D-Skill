# Formula Troubleshooting Patterns

## Table of Contents
- [Custom Number Formats Masking Values](#custom-number-formats-masking-values)
- [Resolving Circular References](#resolving-circular-references)
- [Reading Cached Values with data_only=True](#reading-cached-values-with-data_onlytrue)

## Custom Number Formats Masking Values

A cell displaying `000` or another unexpected string may have a custom number format (e.g., `000`) that hides the actual value. Always check `cell.number_format` alongside `cell.value` or `cell.data_type`.

**Example:**
```python
# openpyxl
fmt = cell.number_format  # e.g., '000'
val = cell.value          # may be an error or zero
```

## Resolving Circular References

When a formula's range includes its own cell, it creates a circular reference. Do not attempt to fix the formula; instead:

1. Load the workbook with `data_only=True` if you need cached values.
2. Identify the correct data range (excluding the target cell).
3. Compute the result externally (e.g., `max()`, `sum()`).
4. Write the literal result to the cell, preserving the original `number_format`.

**Example:**
```python
wb = openpyxl.load_workbook(path, data_only=True)
ws = wb['Sheet1']
vals = [ws.cell(row=r, column=c).value for r in range(1, 323)]
result = max(vals)
target = ws['B323']
target.value = result
# number_format is preserved automatically
wb.save(path)
```

## Reading Cached Values with data_only=True

When openpyxl cannot evaluate a formula, use `data_only=True` to read the last saved computed value. This is essential for inspecting conditional logic or computing aggregates.

```python
wb = openpyxl.load_workbook(path, data_only=True)
ws = wb.active
cached = ws['A323'].value  # returns the cached result, not the formula text
```
