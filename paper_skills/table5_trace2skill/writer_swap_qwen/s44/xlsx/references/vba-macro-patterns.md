# VBA Macro Patterns

## Row Iteration – Correct Cell Reference

**Problem:** `Columns(I, 1)` where `I` is a row number. `Columns()` expects column indices, so `Columns(I, 1)` actually references column I, row 1, not column 1 of row I.

**Correct approaches:**

### Using `Range` with a row number
```vba
For i = 1 To lastRow
    If Range("A" & i).Value = "" Then
        Range("A" & i).EntireRow.Delete
    End If
Next i
```

### Using `Cells(row, column)`
```vba
For i = 1 To lastRow
    If Cells(i, 1).Value = "" Then
        Rows(i).Delete
    End If
Next i
```

## Bulk Blank‑Row Deletion via `SpecialCells`

Instead of looping, use `SpecialCells` to operate on all blank cells in one call:
```vba
Columns(1).SpecialCells(xlCellTypeBlanks).EntireRow.Delete
```
This is simpler and faster when deleting all completely blank rows in a column.

## Deletion Order (Bottom‑to‑Top)

The same index‑shifting danger applies in VBA. When iterating with a counter, always go from `lastRow Down To 1`:
```vba
For i = lastRow To 1 Step -1
    If Cells(i, 1).Value = "" Then Rows(i).Delete
Next i
```
