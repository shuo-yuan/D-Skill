# Data Processing Patterns

## Lookup Dictionary Construction
Convert two-column tables into dictionaries before processing.
```python
lookup = {}
for row in sheet.iter_rows(min_row=2, values_only=True):
    key, val = row[0], row[1]
    lookup[str(key).strip()] = str(val).strip()
```
Always strip whitespace during construction to prevent key mismatches.

## Delimiter-Separated Values
Parse cells containing semicolons, commas, or other delimiters carefully.
```python
def parse_delimited(value, delimiter=';'):
    parts = str(value).split(delimiter)
    return [p.strip() for p in parts if p.strip()]
```
This prevents empty strings from trailing/leading delimiters (e.g., `"PRD1;"` -> `['PRD1']`).

## Deduplication and Sorting
Use sets for automatic deduplication, then sort for deterministic output.
```python
unique_sorted = sorted(set(results))
output = ', '.join(unique_sorted)
```
Ensures consistent ordering regardless of input sequence, critical for reproducible spreadsheet outputs.