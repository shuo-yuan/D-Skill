# Common Spreadsheet Operations

## Date‑threshold Filtering

When filtering rows by a date column (e.g., keep rows with dates within the last 30 days from the latest date):

1. Collect all valid `datetime` values from the target column.
2. Compute `cutoff = max(dates) - timedelta(days=30)`.
3. Filter rows with `date_val < cutoff` (or appropriate comparison).

This approach uses Python's `datetime` arithmetic, avoiding string comparisons and handling mixed data types.

Example:
```python
from datetime import datetime, timedelta

# Assume dates_list is a list of datetime objects extracted from column E
max_date = max(dates_list)
cutoff = max_date - timedelta(days=30)
filtered_rows = [row for row, date_val in zip(rows, dates_list) if date_val < cutoff]
```

## Column Deletion

To delete a column (e.g., column Z):

1. Determine its numeric index (A=1, B=2, ..., Z=26).
2. Call `worksheet.delete_cols(idx)`.
3. Verify that `worksheet.max_column` decreased accordingly.

Example:
```python
# Delete column Z (index 26)
ws.delete_cols(26)
assert ws.max_column == expected_new_max
```
