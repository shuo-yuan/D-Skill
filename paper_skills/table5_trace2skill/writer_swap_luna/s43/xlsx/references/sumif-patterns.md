# SUMIFS Patterns

## Table of Contents
- [Basic Multi-Condition Total](#basic-multi-condition-total)
- [Wildcard Matching for Substrings](#wildcard-matching-for-substrings)

## Basic Multi-Condition Total

Use `SUMIFS` when a total depends on both a numeric/date range and a text condition. Provide one criteria range per condition:

```excel
=SUMIFS(sum_range, date_range, ">="&start_date, date_range, "<="&end_date, text_range, "*"&search_term&"*")
```

- Lock shared source ranges and boundary cells with absolute references (`$A$2:$A$100`, `$B$1`).
- Leave the search-term reference relative when filling across output rows.

## Wildcard Matching for Substrings

When target text may appear embedded in longer cell strings (e.g., comma-separated values), use a wildcard criterion:

```excel
"*"&search_term&"*"
```

An exact-match criterion would miss combined entries. The wildcard matches cells containing the term anywhere.