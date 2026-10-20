# Numeric Patterns

## Percentage Threshold Comparisons

Avoid floating-point multiplication for exact boundary checks. Floating-point representation can produce values like `110.00000000000001` for `100 * 1.10`, causing `110 >= 110.00000000000001` to evaluate to `False`.

**Pattern**: For a P% increase check, use scaled integer comparison:
```
value * 100 >= reference * (100 + P)
```

**Example (10% increase)**:
```python
# WRONG — floating-point error at exact boundaries
if values[i] >= ref_val * 1.10:

# CORRECT — integer arithmetic
if values[i] * 10 >= ref_val * 11:
```

**General form**:
```python
if values[i] * 100 >= ref_val * (100 + percentage):
```

## Restart/Reset Semantics

When instructions say "restart from the cell immediately right of X", the new reference is the adjacent cell, not X itself.

**Pattern**:
- New reference index = index_of_X + 1
- Skip the new reference during the next comparison (advance index by 2 total)

**Verification**: Check input data for pre-filled markers or annotations (e.g., row-2 labels like `1, 2, 3, 4`) that indicate expected output positions. Cross-check your restart logic against these markers before producing final output.