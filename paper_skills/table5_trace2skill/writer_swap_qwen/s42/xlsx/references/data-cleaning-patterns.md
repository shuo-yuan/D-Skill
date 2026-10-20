# Data Cleaning Patterns

## Composite Key Grouping

Group rows by a composite key of multiple identifying columns (e.g., Last Name, First Name, DOB) to reliably identify true duplicates. Avoid relying on single-column matches, which can produce false positives.

## Conditional Preservation

When groups contain mixed relationship types, apply a priority rule: if any entry in a group has a priority type (e.g., 'Employee'), keep all entries in that group. Only deduplicate groups where all entries are non-priority types.

## Safe Row Deletion

- Before deleting, filter for groups with more than one entry (size > 1).
- Always delete the second occurrence (index 1 in zero-based arrays), preserving the first entry as the authoritative record.
- After deletion, verify the final row count against expected values.
