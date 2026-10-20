# Mapping Patterns for Spreadsheet Transposition

## Chunk-Based Row Mapping
When transposing vertical/wide data into condensed rows:
- Calculate chunk size: `chunk_size = total_source_rows / total_output_rows`
- Use formula: `source_index = (target_row - 1) * chunk_size + source_start_row`
- Adjust for 0-based vs 1-based indexing as required by your tool.

## Systematic Column Pair Mapping
Instead of manual assignments:
- Define column groups: `[(col_A, col_B), (col_C, col_D), ...]`
- Use a loop with offset logic: `target_col = base_col + (group_index * 2) + col_offset`
- This reduces code length, minimizes typos, and makes mapping transparent.

## Edge Case Handling
- For incomplete chunks at the end, use conditional logic: `if remaining_rows < chunk_size: handle_specially()`
- Always verify the last row of output against the last row of source data.