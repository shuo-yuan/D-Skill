# Sheet Mapping Patterns

Proven patterns for mapping rows between sheets using lookups.

## 1. Verify Key Uniqueness Before Lookups

A simple pair (e.g., meet + race#) may not be unique across rows. Before performing lookups:
- Inspect the source data for duplicates with respect to the intended key.
- Add extra distinguishing fields (e.g., date) until the key yields unique matches.
- Use a multi-field composite key when necessary: `(meet, date, race#)` instead of `(meet, race#)`.

## 2. Normalize Text Fields Before Comparison

String identifiers often carry whitespace or case inconsistencies across sheets.
- Always apply `.str.strip().str.upper()` (or equivalent) to text key fields before building lookups or comparing.
- Normalize both the source key and the lookup key to the same form.

## 3. Build a Dictionary Lookup for Single-Pass Mapping

Avoid nested loops. Pre-compute a lookup dictionary from the source sheet:
- Key: the composite unique key (normalized).
- Value: the columns needed from the source row.
- Iterate over the target sheet once, applying the dictionary lookup per row.

Example pattern:
```python
# Build lookup from source
lookup = {}
for _, row in source_df.iterrows():
    key = (row['meet'].strip().upper(), row['date'], row['race#'])
    lookup[key] = (row['top'], row['tab_positions'])

# Apply to target
for _, row in target_df.iterrows():
    key = (row['meet'].strip().upper(), row['date'], row['race#'])
    if key in lookup:
        row['top'], row['tab_positions'] = lookup[key]
```
