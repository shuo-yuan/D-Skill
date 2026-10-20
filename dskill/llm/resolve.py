"""Print provider-resolved LLM connection info for shell scripts.

Usage:
    python -m dskill.llm.resolve                 -> "<base_url> <api_key>"
    python -m dskill.llm.resolve <model>         -> "<base_url> <api_key> <slug>"

    read LLM_BASE LLM_KEY LLM_MODEL <<< "$($PY -m dskill.llm.resolve gpt-5-mini-2025-08-07)"
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dskill.llm.client import resolve_endpoint, resolve_model  # noqa: E402

base, key = resolve_endpoint()
if len(sys.argv) > 1:
    print(base, key, resolve_model(sys.argv[1]))
else:
    print(base, key)
