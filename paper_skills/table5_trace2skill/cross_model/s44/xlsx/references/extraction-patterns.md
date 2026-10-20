## Regex Extraction for Tagged Values

When a cell contains multiple key‑value pairs separated by commas, use a regular expression that matches a fixed prefix and captures all characters until a delimiter. For example, `r'Prefix-([^,]+)'` will match the prefix and capture everything after it until the next comma. Strip whitespace from the captured value to handle optional spaces. This approach works regardless of the tag's position in the string.

Example:
```python
import re
value = re.search(r'Prefix-([^,]+)', cell_value)
if value:
    extracted = value.group(1).strip()
```