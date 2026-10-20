# Lookup Patterns

## Table of Contents
- [Two-Way INDEX/MATCH](#two-way-indexmatch)
- [When to Use](#when-to-use)

## Two-Way INDEX/MATCH
Use this pattern when looking up a value by matching both a row and column header in a cross-tabulated table.

**Formula Structure:**
```excel
=INDEX(return_column_range, MATCH(1, (lookup_col1_range=condition1)*(lookup_col2_range=condition2), 0))
```

**Steps:**
1. Identify the return column containing values.
2. Identify the column ranges for row and column headers.
3. Construct the `INDEX` function with the return range.
4. Use `MATCH` with an array formula combining conditions using `*` (AND logic).
5. Enter as an array formula (Ctrl+Shift+Enter in legacy Excel, or natively in modern Excel).

**Example:**
Looking up sales for "Product A" (column header) in "Q1" (row header):
`=INDEX(C2:E10, MATCH(1, (A2:A10="Q1")*(B1:D1="Product A"), 0))`

## When to Use
- Data is structured in a matrix/cross-tab format.
- Single-column VLOOKUP or HLOOKUP cannot handle both dimensions.
- Avoid chaining multiple lookups; this single formula finds the intersection directly.