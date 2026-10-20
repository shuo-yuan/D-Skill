"""Constrain OpenRouter routing by weight precision, and log who served.

install() patches the openai SDK so each chat call carries a `provider` block:
the vendor's first-party host first, then hosts by declared precision and
throughput, never fp4/int4. HD_OR_PROVIDER=<slug> pins one host instead.
report() prints which providers served the calls.
"""

from __future__ import annotations

import json
import os
import urllib.request
from collections import Counter

_SEEN: Counter = Counter()
_INSTALLED = False

# roster snapshot, used when the /endpoints API is not queried or fails
_FALLBACK = {
    "deepseek/deepseek-v4-pro": {
        "unknown": ["deepseek", "together", "digitalocean", "cloudflare", "venice"],
        "fp8": ["streamlake", "gmicloud", "novita", "baidu", "alibaba",
                "siliconflow", "parasail", "coreweave"],
        "fp4": ["ionstream", "deepinfra", "atlas-cloud", "baseten"],
    },
    "qwen/qwen3.6-35b-a3b": {
        "unknown": ["phala"],
        "fp8": ["venice", "deepinfra", "akashml", "parasail", "atlas-cloud",
                "siliconflow", "coreweave", "io-net"],
        "fp4": [],
    },
}
_roster_cache: dict[str, dict] = {}


def _roster(model: str) -> dict:
    """{quantization: [slug,...]} for a model, live if possible."""
    if model in _roster_cache:
        return _roster_cache[model]
    out = None
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if key and os.environ.get("HD_PROVIDER", "openai").lower() == "openrouter":
        try:
            req = urllib.request.Request(
                f"https://openrouter.ai/api/v1/models/{model}/endpoints",
                headers={"Authorization": f"Bearer {key}"})
            with urllib.request.urlopen(req, timeout=15) as r:
                eps = json.load(r).get("data", {}).get("endpoints", [])
            g: dict = {}
            _tps: dict = {}
            for e in eps:
                slug = (e.get("tag", "") or "").split("/")[0]
                if slug:
                    g.setdefault(e.get("quantization") or "unknown", []).append(slug)
                    tp = (e.get("throughput_last_30m") or e.get("throughput")
                          or {})
                    try:
                        _tps[slug] = float(tp.get("p50") or 0)
                    except Exception:                          # noqa: BLE001
                        _tps[slug] = 0.0
            if g:
                g["__tps__"] = _tps
                out = g
        except Exception:                                      # noqa: BLE001
            out = None
    if out is None:
        out = _FALLBACK.get(model, {})
        if out:
            print(f"[pin-provider] endpoints API not queried or unavailable; using the "
                  f"2026-08-06 roster for {model}", flush=True)
    _roster_cache[model] = out
    return out


# precision rank, lower is better; ranks >= _NEVER_RANK are excluded
_RANK = {"fp32": 0, "bf16": 0, "fp16": 0,
         "unknown": 1,
         "fp8": 2, "int8": 2, "fp6": 3,
         "fp4": 9, "int4": 9}
_NEVER_RANK = 9


def _policy(model: str) -> dict | None:
    """Provider block: first-party host first, then by precision and
    throughput; fp4/int4 and slow hosts excluded. None if no host qualifies."""
    g = _roster(model)
    if not g:
        return None

    # hosts measured below HD_MIN_TPS tok/s are excluded; no data (0) is kept
    tps = g.get("__tps__", {}) if isinstance(g.get("__tps__"), dict) else {}
    min_tps = float(os.environ.get("HD_MIN_TPS", "15"))

    ranked, ignore = [], []
    for quant, slugs in g.items():
        if quant == "__tps__":
            continue
        r = _RANK.get(str(quant).lower(), 1)          # undeclared-ish default
        for slug in slugs:
            t = tps.get(slug, 0.0)
            if r >= _NEVER_RANK or (min_tps and 0 < t < min_tps):
                ignore.append((r, slug))
            else:
                ranked.append((r, -t, slug))

    ranked.sort(key=lambda t: (t[0], t[1]))           # precision, then -tps
    order = list(dict.fromkeys(s for _, _, s in ranked))

    # first-party always leads for its own vendor
    vendor = model.split("/", 1)[0].lower() if "/" in model else ""
    if vendor and vendor in order:
        order = [vendor] + [s for s in order if s != vendor]

    if not order:
        return None
    block = {"order": order, "allow_fallbacks": True}
    ig = list(dict.fromkeys(s for _, s in ignore))
    if ig:
        block["ignore"] = ig
    return block


def install() -> bool:
    """Patch the SDK call site. Returns True if applied."""
    global _INSTALLED
    if _INSTALLED:
        return True

    pin = os.environ.get("HD_OR_PROVIDER", "")

    try:
        from openai.resources.chat import completions as _c
    except Exception as e:                                     # noqa: BLE001
        print(f"[pin-provider] openai SDK not importable: {e}", flush=True)
        return False

    orig = _c.Completions.create

    def patched(self, *args, **kwargs):
        model = kwargs.get("model") or (args[0] if args else "")
        eb = dict(kwargs.get("extra_body") or {})
        if "provider" not in eb:
            if pin:
                eb["provider"] = {"order": [pin], "allow_fallbacks": False}
            else:
                blk = _policy(str(model))
                if blk:
                    eb["provider"] = blk
        if eb:
            kwargs["extra_body"] = eb
        resp = orig(self, *args, **kwargs)
        try:
            who = (getattr(resp, "provider", None)
                   or (getattr(resp, "model_extra", None) or {}).get("provider"))
            _SEEN[who or "unknown"] += 1
        except Exception:                                      # noqa: BLE001
            _SEEN["unknown"] += 1
        return resp

    _c.Completions.create = patched
    _INSTALLED = True
    if pin:
        print(f"[pin-provider] pinned to {pin!r} (no fallbacks)", flush=True)
    else:
        print("[pin-provider] precision policy ON: prefer undeclared, "
              "then fp8, never fp4", flush=True)
    return True


def served_by() -> dict:
    return dict(_SEEN)


def report(prefix: str = "[pin-provider]") -> None:
    if not _SEEN:
        print(f"{prefix} no calls recorded", flush=True)
        return
    tot = sum(_SEEN.values())
    parts = ", ".join(f"{k}={v} ({v/tot*100:.0f}%)" for k, v in _SEEN.most_common())
    print(f"{prefix} {tot} calls served by: {parts}", flush=True)
