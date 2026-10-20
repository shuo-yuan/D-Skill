# Sheet Synchronization Pattern

Use when aligning one sheet's rows to an authoritative list of IDs while preserving existing data.

## Steps

### 1. Load the authoritative ID list
Read the ID column from the sheet that defines correct row order and membership (e.g., a manual-entry sheet or a source data sheet). These IDs determine the final row sequence.

### 2. Index existing target rows by ID
Read the target sheet. Build a dictionary mapping each row's unique ID to the full row data (list of cell values). Store the header row separately so it can be rewritten at the top.

### 3. Determine column count for placeholders
If the target sheet is empty or needs placeholder rows, derive the column count from the header. A placeholder row is `[ID] + [None] * (column_count - 1)`.

### 4. Build output rows in authoritative ID order
```python
output_rows = [header]
for id_val in authoritative_ids:
    if id_val in existing_rows:
        output_rows.append(existing_rows[id_val])
    else:
        output_rows.append([id_val] + [None] * (col_count - 1))
```

### 5. Write values and apply formatting
Write `output_rows` to the target sheet (starting at A1). If the workbook contains a reference layout sheet (often labeled "Expected" or "Template"), copy cell-by-cell formatting from it:
- Copy styles, number formats, alignments, and font properties.
- Copy row heights and column widths.
- Preserve cell protection settings.

Apply formatting after writing values to ensure visual consistency between populated and blank rows.