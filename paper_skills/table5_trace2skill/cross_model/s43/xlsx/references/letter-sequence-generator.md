# Letter Sequence Generator

A reusable helper to convert a 1-based integer index to Excel-style letter sequences (a, b, ..., z, aa, ab, ...).

```python
def col_letter(n):
    """Convert 1-based index to Excel-style column letters."""
    letters = ''
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters.lower()
```

Use this when generating alphabetic suffixes for unique identifiers or column references.