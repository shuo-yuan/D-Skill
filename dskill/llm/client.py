"""LLM endpoint and client helpers."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

if TYPE_CHECKING:
    from react_agent.models import OpenAIClient


def resolve_endpoint() -> tuple[str, str]:
    """(base_url, api_key). HD_PROVIDER=openrouter uses OpenRouter; otherwise
    OPENAI_BASE_URL, else api.openai.com when OPENAI_API_KEY is a real key
    (not empty or EMPTY), else the local tinker_proxy (:8088)."""
    if os.environ.get("HD_PROVIDER", "openai").lower() == "openrouter":
        return (os.environ.get("HD_OPENROUTER_BASE_URL",
                               "https://openrouter.ai/api/v1"),
                os.environ.get("OPENROUTER_API_KEY", "EMPTY"))
    api_key = os.environ.get("OPENAI_API_KEY", "EMPTY")
    default_base = ("https://api.openai.com/v1"
                    if api_key not in ("", "EMPTY")
                    else "http://127.0.0.1:8088/v1")
    return os.environ.get("OPENAI_BASE_URL", default_base), api_key


def resolve_model(model: str) -> str:
    """Provider-facing model id: on OpenRouter a bare name gets the
    HD_OPENROUTER_PREFIX (default 'openai/'); otherwise it is unchanged."""
    if os.environ.get("HD_PROVIDER", "openai").lower() == "openrouter" \
            and "/" not in model:
        return os.environ.get("HD_OPENROUTER_PREFIX", "openai/") + model
    return model


def make_client(model: str, effort: str | None = None) -> OpenAIClient:
    from react_agent.models import OpenAIClient
    base_url, api_key = resolve_endpoint()
    gen = {"reasoning_effort": effort} if effort else None
    return OpenAIClient(model=resolve_model(model), api_key=api_key,
                        base_url=base_url,
                        use_cache=False, timeout=600.0,
                        generation_config=gen)
