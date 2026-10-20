# Cumulative Logic Pattern

## When to Use
When requirements involve expanding windows, strict priority ordering, or mixed data types that make nested `COUNTIFS`/`SUMIFS` error-prone.

## Pattern
Use a nested Python loop that evaluates conditions row-by-row with full control over iteration order.

```python
import openpyxl

wb = openpyxl.load_workbook('input.xlsx')
ws = wb.active

# Assume: col A = State (bool), col B = some value, col C = output column
for i in range(2, ws.max_row + 1):
    # Evaluate an expanding window: rows 2 through current row i
    result = None
    for j in range(2, i + 1):
        state = ws.cell(row=j, column=1).value
        val = ws.cell(row=j, column=2).value
        # Priority-ordered conditions
        if state is False and val is None:
            result = 'none'
            break  # highest priority match
        elif state is True and val is not None:
            result = 'present'
            # continue checking — lower priority may override
    if result is None:
        result = 'other'
    ws.cell(row=i, column=3).value = result

wb.save('output.xlsx')
```

## Key Points
- Use `is False` / `is True` / `is None` for exact type matching when cells contain Python booleans or None.
- The outer loop defines the expanding window; the inner loop evaluates conditions within that window.
- `break` after a highest-priority match; let lower-priority conditions fall through.
- After saving, reload and print the output column to verify correctness.