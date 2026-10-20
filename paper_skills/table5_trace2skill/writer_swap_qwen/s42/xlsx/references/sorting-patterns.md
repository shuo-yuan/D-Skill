# Multi-Level Sorting Patterns

## Tuple-Based Sort Keys

Use Python's `sort()` or `sorted()` with a tuple key for multi-level sorting. Each tuple element corresponds to a sort level in priority order. Convert all key values to strings to handle mixed data types consistently.

### Example

```python
# Sort by column A ascending, then column B descending as tiebreaker
rows.sort(key=lambda row: (str(row[col_a]), str(row[col_b])), reverse=(False, True))
```

For mixed ascending/descending, sort in multiple passes from lowest priority to highest, or negate numeric values for descending levels.

### Why This Works

Tuple comparison compares element-by-element, naturally implementing multi-level sort without destroying prior ordering (unlike sequential single-column sorts).
