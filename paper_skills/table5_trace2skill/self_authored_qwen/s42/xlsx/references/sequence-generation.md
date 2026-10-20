# Sequence Generation Patterns

## Stateful Iteration
When filling missing data points in a sequence, maintain state outside the loop.

```python
last_valid_base = None
current_suffix = 0
for row in data:
    if row['base'] is not None:
        last_valid_base = row['base']
        current_suffix = 0
    else:
        # Derive value from state
        row['value'] = f"{last_valid_base}{generate_suffix(current_suffix)}"
        current_suffix += 1
```

## Base-26 Alphanumeric Mapping
Standard Excel features fail for sequences > 'z'. Use this mapping logic:

```python
def generate_suffix(n):
    result = ""
    while n >= 0:
        result = chr(ord('a') + (n % 26)) + result
        n = n // 26 - 1
    return result
```