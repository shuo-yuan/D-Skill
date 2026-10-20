# Regex Patterns for Text Extraction

## Delimited Tag Extraction

Use this pattern to extract values following a labeled tag up to the first delimiter.

### Pattern
```python
import re
text = "Collection-Value1,Other"
match = re.search(r'Tag-([^,]*)', text)
if match:
    value = match.group(1)
```

### Usage
- **Prefix Tag**: Replace `Tag-` with the specific prefix (e.g., `Collection-`).
- **Delimiter**: The pattern `([^,]*)` captures everything until the first comma.
- **Edge Cases**: Handles end-of-string values seamlessly without complex splitting.