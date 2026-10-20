# Letter Sequence Helper

Reusable function to convert a 1‑based integer index to Excel‑style column letter(s).

```python
def col_letter(n):
    """Convert 1-based index to Excel-style column letter(s)."""
    result = ''
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(ord('a') + remainder) + result
    return result
```

Use this pattern whenever a task requires alphabetic suffixes beyond single letters (e.g., generating unique identifiers, column references).