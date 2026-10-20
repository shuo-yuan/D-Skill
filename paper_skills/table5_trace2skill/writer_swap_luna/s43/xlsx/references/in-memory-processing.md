# In-Memory Processing for Spreadsheets

## When to Use This Pattern
Use for deduplication, aggregation, or lookups over large datasets where cell-by-cell API calls would be slow. Load all data into memory, process, then write results in a single output pass.

## Composite Key Deduplication
When uniqueness depends on multiple columns (e.g., A, B, C), combine their values into a tuple key.
```python
key = (row[0], row[1], row[2])
```
Use this key in a dictionary to merge or sum rows that match across all identifying columns.

## One-Pass Aggregation
1. Initialize an empty dictionary.
2. Read each row once:
   - Build the composite key.
   - If key is new, store the initial record.
   - If key exists, aggregate values (e.g., add to running totals).
3. Do not iterate over the sheet repeatedly for duplicate checks.

## Single Output Pass
1. Clear the target output range.
2. Write headers once.
3. Write all consolidated rows from the dictionary.
4. Save the workbook only after all values are written.

This minimizes spreadsheet operations and keeps output explicit.