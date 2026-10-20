# Dynamic Range Detection

## Overview
Scan rows sequentially to identify independent data blocks separated by blank rows or recognized header rows. This avoids brittle fixed-range assumptions.

## Algorithm
1. Initialize an empty list of ranges and a `current_start` variable set to `None`.
2. Iterate through rows from top to bottom.
3. For each row:
   - If the row is blank or matches a header pattern (bold text, merged cells, known label strings):
     - If `current_start` is not `None`, finalize the range from `current_start` to the previous row, append it to the list, and reset `current_start` to `None`.
   - If the row contains data (non-empty cells):
     - If `current_start` is `None`, set `current_start` to this row number.
4. After the loop, if `current_start` is not `None`, finalize the last range through the final data row.
5. Return the list of (start_row, end_row) tuples.

## Header Recognition
A row is a header if it contains cells with:
- Bold formatting
- Merged cells spanning multiple columns
- Text matching known labels (e.g., "Name", "Value", "ID", "Date")

## Usage
Call this detection before any sort, filter, or transformation that must operate on independent data blocks within a sheet.