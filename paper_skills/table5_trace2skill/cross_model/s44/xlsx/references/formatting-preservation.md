# Formatting Preservation with openpyxl

When moving or copying cells, capture and reapply these properties to maintain visual consistency.

## Properties to Copy

```python
props = {
    'number_format': cell.number_format,
    'font': cell.font,
    'fill': cell.fill,
    'border': cell.border,
    'alignment': cell.alignment,
}
```

## Application

Assign each property to the destination cell after setting its value:

```python
target_cell.number_format = props['number_format']
target_cell.font = props['font']
target_cell.fill = props['fill']
target_cell.border = props['border']
target_cell.alignment = props['alignment']
```

## Order of Operations

1. Capture formatting from the source cell before any insertions or deletions.
2. Set the destination cell value.
3. Apply captured formatting to the destination cell.
4. Delete the source column only after confirming the destination is correct.