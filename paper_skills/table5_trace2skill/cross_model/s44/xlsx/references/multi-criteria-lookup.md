# Multi-Criteria Lookup Examples

## MATCH with Array Multiplication

To find a row where two or more columns must match:

```excel
=MATCH(1, (Sheet2!$A$3:$A$20=INPUTS!$A$14)*(Sheet2!$B$3:$B$20=INPUTS!$A16), 0)
```

This returns the row index where both conditions are true. Use it inside INDEX to retrieve a value from that row.

## Diagnosing Partial Formula Success

If a formula produces correct results for some rows but not others:

1. Identify a working row and a failing row.
2. Check whether the working row's result is correct by coincidence (e.g., it happens to be the first match).
3. Add criteria until the formula uniquely identifies each row.

## Column References When Copying Formulas

When a formula will be copied across columns, use relative column references so the column index auto-adjusts. If populating cells individually in a script, set the correct column letter explicitly for each cell.