# Block Operations Reference

## Detecting Block Boundaries

When data is organized into repeated blocks, use a distinct field value in a consistent column to identify where each block starts.

**Pattern:**
```python
blocks = []
current_block = []
for row in data:
    if row[0] == 'date':  # header row detected
        if current_block:
            blocks.append(current_block)
        current_block = [row]
    else:
        current_block.append(row)
if current_block:
    blocks.append(current_block)
```

## Control-Cell Branching

Read the control cell early and branch cleanly:

```python
control_value = sheet['I2'].value
if control_value is None:
    # Path A: delete all empty rows
    ...
else:
    # Path B: delete empty rows only from matching block
    ...
```

## Normalizing Inter-Block Spacing

After operations, ensure exactly one empty row between blocks and none at the end:

```python
output = []
for i, block in enumerate(blocks):
    output.extend(block)
    if i < len(blocks) - 1:
        output.append([])  # single separator row
# Write output to sheet
```

## Common Pitfalls

- **DO NOT** hardcode row ranges (e.g., `A1:A20`). Block sizes vary.
- **DO NOT** leave trailing empty rows after the last block.
- **DO NOT** entangle conditional logic for different modes; branch early.