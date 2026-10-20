# Formula Troubleshooting

## Circular References

When a formula creates a circular reference (its range includes its own cell):

1. Identify the correct range that excludes the target cell
2. Read the dependent data directly from the spreadsheet
3. Perform the computation externally (e.g., `max()`, `sum()`, conditional logic)
4. Write the literal result to the target cell
5. Preserve any existing `number_format` on the cell

This avoids reliance on formula recalculation and guarantees the correct value.

## Reading Cached Formula Values

Use `openpyxl.load_workbook(path, data_only=True)` to access the most recently saved computed values when:

- The environment cannot recalculate formulas
- You need to inspect a formula's actual result for conditional logic
- You need to compute aggregates over formula-driven ranges

This bypasses formula text and returns cached values, enabling correct downstream computation without manual formula evaluation.