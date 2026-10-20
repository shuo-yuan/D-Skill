## Text Extraction Patterns

### Delimiter-Based Extraction

When extracting a value identified by a tag (e.g., "Collection-") from a text cell:

1. **Split on the marker, not a fixed position.**
   - The tag may appear at the beginning, middle, or anywhere in the cell.
   - Example: `parts = cell.split("Collection-", 1)` gets everything after the first occurrence.

2. **Stop at the next delimiter.**
   - After isolating the suffix, split on the next field separator (e.g., comma) to get only the value.
   - Example: `value = suffix.split(",", 1)[0].strip()`
   - If the value is the last field, the suffix itself is the value.

3. **Trim whitespace.**
   - Always strip leading/trailing whitespace from the extracted value before writing.

### Output Discipline

- Iterate only over the requested rows (e.g., rows 2–7 for range B2:B7).
- Write results to the exact destination column requested.
- Save as a new output file to preserve the source workbook.
- Verify the output file exists at the requested path after saving.