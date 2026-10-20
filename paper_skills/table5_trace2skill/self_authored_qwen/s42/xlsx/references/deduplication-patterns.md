# Deduplication Patterns

## Composite Key Grouping
When detecting duplicates, do not rely on single-column matches. Group data rows by a composite key of identifying columns (e.g., Last Name, First Name, DOB) to reliably identify true duplicates. This prevents false positives where individuals share a name but differ in other identifiers.

## Priority-Based Preservation
When groups contain mixed relationship types, apply a "preserve if any entry is primary type" rule.
- Check if any entry in the group has a priority relationship type (e.g., 'Employee').
- If yes, retain all entries in the group.
- Only apply reduction rules (keep first, drop rest) when all entries lack the priority classification.

## Safe Row Deletion
When deleting duplicate rows from row-based spreadsheet data:
1. Verify group size > 1 before attempting deletion.
2. Target the second occurrence (index 1 in zero-based arrays) for removal.
3. Preserve the first occurrence (index 0) as the authoritative entry.