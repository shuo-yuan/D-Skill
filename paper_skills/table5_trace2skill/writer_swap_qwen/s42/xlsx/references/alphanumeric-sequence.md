# Alphanumeric Sequence Generation (Base-26 Pattern)

Standard modulus arithmetic fails when sequences must go beyond 'z' (e.g., 'a' through 'aa', 'ab', …). The pattern below treats the counter as a base-26 number, producing robust strings of any length.

```python
def index_to_label(index: int) -> str:
    # Convert a 1-based index to an Excel-style label (a, b, …, z, aa, ab, …).
    result = ''
    n = index
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(ord('a') + remainder) + result
    return result
```

**Usage example** – filling a column with suffixes that reset per group:

```python
last_valid = None
counter = 0

for row in rows:
    cell_value = row[col_index]
    if cell_value:  # non-blank → new group
        last_valid = cell_value
        counter = 1   # reset for a new group
        suffix = index_to_label(counter)
        fill_value = f'{last_valid}{suffix}'
        counter += 1
    else:  # blank → derive from current group
        suffix = index_to_label(counter)
        fill_value = f'{last_valid}{suffix}'
        counter += 1
    row[fill_col_index] = fill_value
```
