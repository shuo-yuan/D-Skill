# Text Matching and Row Deletion

## Case-Insensitive Text Matching

When searching for a phrase that may appear with different capitalization, normalize before comparing:

1. Convert non-empty cell values to strings.
2. Compare their lowercase form against the lowercase target phrase.
3. This handles variants like "INVOICE NO." vs "Invoice No." consistently.

## Preserve the First Matching Row

When deleting rows *preceding* a match, keep the matching row itself:

1. Scan top-to-bottom and stop at the first qualifying row.
2. If its row index is greater than 1, delete the range from row 1 through the row immediately above it.
3. Do NOT delete the matching row.

## Save to Exact Path

After completing transformations, write the modified workbook to the explicitly specified output path (e.g., `output.xlsx`). Do not change the filename or location.