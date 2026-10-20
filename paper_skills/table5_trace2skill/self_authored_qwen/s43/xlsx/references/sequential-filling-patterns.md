# Sequential Filling & Grouping Patterns

## Table of Contents
- [Stateful Iteration for Sequential Filling](#stateful-iteration-for-sequential-filling)
- [Custom Sequence Generation for Alphanumerics](#custom-sequence-generation-for-alphanumerics)
- [Resetting Counters on New Groups](#resetting-counters-on-new-groups)

## Stateful Iteration for Sequential Filling
When filling missing data points in a sequence, use a variable outside the loop to store the last valid value encountered. This allows the current cell to be derived from it.

```python
last_valid_number = None
for row in sheet.iter_rows(min_row=2, values_only=False):
    cell = row[0] # target column
    if cell.value is not None:
        last_valid_number = cell.value
    else:
        cell.value = last_valid_number # or derive from last_valid_number
```

## Custom Sequence Generation for Alphanumerics
Standard Excel features or simple modulo arithmetic fail when sequences extend past 'z' (into 'aa', 'ab'). Implement a dedicated helper function that treats the sequence counter as a base-26 system.

```python
def to_alphanumeric(n):
    result = ""
    while n > 0:
        n, rem = divmod(n - 1, 26)
        result = chr(ord('a') + rem) + result
    return result

# Usage:
counter = 1
for row in sheet.iter_rows(...):
    if cell.value is None:
        cell.value = to_alphanumeric(counter)
        counter += 1
```

## Resetting Counters on New Groups
When processing a stream of data containing distinct groups (e.g., '5a'...'5t', '6a'...'6c'), explicitly reset the sequence counter whenever a new base value is detected.

```python
last_base = None
counter = 1
for row in sheet.iter_rows(...):
    base_val = row[1].value # assume base is in adjacent column
    if base_val != last_base:
        last_base = base_val
        counter = 1
    else:
        counter += 1
    # assign counter to target cell
```