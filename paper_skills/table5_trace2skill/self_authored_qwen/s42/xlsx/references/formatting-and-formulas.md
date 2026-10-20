---
name: formatting-and-formulas
---

# Formatting & Formula Patterns

## Hour Splitting Logic
When splitting hours into regular and overtime:
- Values ≤ 40 remain unchanged in the regular column.
- Values > 40 split into regular (40) and overtime (value - 40).
- Apply appropriate number formatting: `#,##0.##` for non-whole numbers, `General` for whole numbers.

## Number Formatting Rules
- Use `#,##0.##` for decimal values requiring up to two decimal places.
- Use `General` for whole numbers or when no specific format is required.
- Always verify formatting matches the ground truth exactly, as spreadsheet tools often default to text or standard number formats that may not align with requirements.

## Formula Validation
- Insert formulas, recalculate, then read back the result before saving.
- Check for absolute vs. relative references when copying formulas across ranges.
- Use the evaluation tool to confirm cell-level accuracy.