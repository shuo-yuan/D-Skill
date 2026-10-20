# Conditional Ranking & Index Tracking Patterns

## When to Use
Apply when ranking, filtering, or labeling data based on categories or subsets. Avoids error-prone nested spreadsheet formulas.

## Group-Then-Sort Strategy
1. **Group**: Collect values belonging to each category into separate collections.
2. **Sort**: Sort each collection independently (e.g., descending for top-N).
3. **Map**: Assign ranks/labels directly to the grouped data.
4. **Place**: Write results back to the original spreadsheet positions using preserved indices.

## Index Tracking
- Store tuples of `(value, original_index)` during grouping.
- This eliminates the need for post-hoc lookups or searches.
- Ensures output labels align with the correct input columns.

## Programmatic Implementation
Use Python with `openpyxl` or `pandas` for complex conditional logic:
```python
# Pseudocode example
data = [(row['value'], row['category'], row['original_col_idx']) for row in sheet_rows]
groups = defaultdict(list)
for val, cat, idx in data:
    groups[cat].append((val, idx))

results = {}
for cat, items in groups.items():
    sorted_items = sorted(items, key=lambda x: x[0], reverse=True)
    for rank, (val, idx) in enumerate(sorted_items, 1):
        results[idx] = rank

# Write results back using preserved indices
for idx, rank in results.items():
    sheet.cell(row=idx, column=TARGET_COL).value = rank
```

## Validation Checklist
- [ ] Groups cover all categories without overlap.
- [ ] Sorting order matches task requirements.
- [ ] Original indices are correctly mapped to output cells.
- [ ] Output dimensions match expected layout.