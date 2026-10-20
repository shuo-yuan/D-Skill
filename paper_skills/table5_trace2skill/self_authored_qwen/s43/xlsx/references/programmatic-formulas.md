# Programmatic Formula Generation

## Table of Contents
- [Loop-Based Generation](#loop-based-generation)
- [Dynamic References](#dynamic-references)
- [Best Practices](#best-practices)

## Loop-Based Generation
When filling a range of cells with similar formulas that vary by row/column position, generate them programmatically using nested loops.

**Workflow:**
1. Determine the start and end cells for the output range.
2. Iterate through rows and columns.
3. Construct each formula string by concatenating cell references.
4. Assign the formula string to the target cell.

## Dynamic References
- **Lookup Tables**: Use absolute references (e.g., `$A$1:$D$10`) so they don't shift when copied.
- **Query Values**: Use relative references (e.g., `A1`) or construct them dynamically based on loop indices.
- **Range Construction**: Build ranges like `Cells(i, 1).Address(1, 1)` to avoid hardcoding.

## Best Practices
- Validate formula syntax before assignment.
- Test on a small subset before applying to the full range.
- Ensure loop bounds match the actual data dimensions to prevent out-of-bounds errors.
- Use explicit cell mapping (see Core Workflow) to anchor references correctly.