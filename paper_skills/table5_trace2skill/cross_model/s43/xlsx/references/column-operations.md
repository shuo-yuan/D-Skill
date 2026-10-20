# Column Operations Reference

## Dynamic Column Location by Header Search

When a target column's position can vary, locate it by scanning the header row:

```python
def find_column_by_header(ws, header_row, target_name):
    for col in range(1, ws.max_column + 1):
        if ws.cell(row=header_row, column=col).value == target_name:
            return col
    raise ValueError(f"Column '{target_name}' not found in row {header_row}")
```

## Insert-Before-Delete Column Move

Safe sequence for moving a column without data loss:

```python
# 1. Find source and target positions
source_col = find_column_by_header(ws, header_row=5, target_name="0-15")
target_col = 2  # column B

# 2. Insert blank column at destination
ws.insert_cols(target_col)

# Adjust source_col index if insertion shifted it right
if source_col >= target_col:
    source_col += 1

# 3. Copy values and formatting
for row in range(1, ws.max_row + 1):
    src = ws.cell(row=row, column=source_col)
    dst = ws.cell(row=row, column=target_col)
    dst.value = src.value
    dst.number_format = src.number_format
    dst.font = src.font.copy()
    dst.fill = src.fill.copy()
    dst.border = src.border.copy()
    dst.alignment = src.alignment.copy()

# 4. Delete source column
ws.delete_cols(source_col)
```

## Formatting Properties to Preserve

When copying cells with openpyxl, always capture and reapply:
- `number_format`
- `font` (use `.copy()` for Font objects)
- `fill` (use `.copy()` for PatternFill objects)
- `border` (use `.copy()` for Border objects)
- `alignment` (use `.copy()` for Alignment objects)

Styles are not automatically transferred when setting `.value` alone.
