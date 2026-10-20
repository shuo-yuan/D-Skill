# Complex Lookup Patterns

## Parsing Comma-Separated Multi-Value Cells

When a cell contains multiple comma-separated values (e.g., `"fabric_crepe,fabric_velvet"`), do NOT use substring matching. Instead:

1. Split the cell value by comma
2. Strip whitespace from each part
3. Check for exact match among the resulting substrings

```python
cell_value = "fabric_crepe,fabric_velvet"
parts = [v.strip() for v in cell_value.split(",")]
if "fabric_crepe" in parts:
    # exact match found
```

This avoids false negatives from substring containment and handles whitespace variations.

## Programmatic Computation Over Excel Formulas

For tasks requiring conditional logic (date range filters, text membership checks, multi-criteria sums), compute results in Python rather than constructing complex Excel formulas like SUMIFS with wildcards. Write literal numeric results to output cells. This is more reliable and avoids formula fragility when the spreadsheet is modified or shared.

## Spot-Check Verification

After computing results, manually verify a sample of outputs:
- Pick 2–3 output cells
- Trace through the source data rows applying the same criteria
- Hand-calculate the expected value
- Compare to the computed output

This confirms algorithm correctness before running the full computation.
