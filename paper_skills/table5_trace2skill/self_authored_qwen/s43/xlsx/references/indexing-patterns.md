# Indexing & Mapping Patterns

## Row Transposition Mapping
When transposing vertical/wide source data into condensed target rows, calculate source indices dynamically:

```
source_row = (target_row - offset) * chunk_size + base_row
```

- `target_row`: current row in the destination sheet
- `offset`: row offset adjustment (usually 0 or 1 depending on headers)
- `chunk_size`: number of source rows that map to one target row
- `base_row`: first data row in the source sheet

## Column Pair Mapping
Group scattered target columns into logical blocks and apply iterative offsets:
```
col_offset = block_index * pair_spacing
source_col = base_col + col_offset
target_col = base_target_col + col_offset
```
This reduces code length, minimizes typos, and makes the mapping logic transparent.

## Handling Incomplete Chunks
At the end of large datasets, the final chunk may be smaller than `chunk_size`. Always validate:
```python
actual_chunk_size = min(chunk_size, remaining_rows)
if actual_chunk_size == 0: break
```
Print boundary rows explicitly to catch silent misalignments before finalizing.