"""String-aware action parsing + missing-brace repair for the ReAct harness.

Replaces ReActConverter.parse_response: braces inside JSON strings (such as
f-string placeholders in a bash command) are ignored, and an action object
left unclosed is closed and re-parsed. Well-formed actions parse as before.
run_baseline_t2s calls maybe_install() at import; HD_ROBUST_PARSE=0 disables it.
"""

from __future__ import annotations

import json
import os

_STATS = {"clean": 0, "repaired_braces": 0, "string_aware_save": 0,
          "still_failed": 0}


def scan_json(text: str) -> tuple[int | None, int | None, int]:
    """Find the outermost JSON object, ignoring braces inside strings.

    Returns (start, end, depth_at_eof). ``end`` is None when the object
    never closes; ``depth_at_eof`` is how many braces are missing.
    """
    depth = 0
    start = end = None
    in_str = False
    esc = False
    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                end = i + 1
                break
    return start, end, depth


def parse_action_text(action_text: str) -> dict | None:
    """action_text (everything after 'Action:') -> action dict, or None."""
    start, end, depth = scan_json(action_text)
    if start is None:
        return None

    if end is not None:
        candidates = [action_text[start:end]]
    elif depth > 0:
        # unclosed: also try cutting after the last } or ", as prose may follow
        tail = action_text[start:].rstrip()
        cuts = [len(tail)]
        last = tail.rfind("}")
        if last != -1 and last < len(tail) - 1:
            cuts.append(last + 1)
        last_q = tail.rfind('"')
        if last_q != -1 and last_q < len(tail) - 1:
            cuts.append(last_q + 1)
        candidates = []
        for cut in cuts:
            piece = tail[:cut]
            _, _, d = scan_json(piece)
            if d > 0:
                candidates.append(piece + ("}" * d))
    else:
        return None

    for cand in candidates:
        for attempt in (cand, cand.replace("'", '"')):
            try:
                data = json.loads(attempt)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict) and "name" in data:
                _STATS["clean" if end is not None else "repaired_braces"] += 1
                return data
    _STATS["still_failed"] += 1
    return None


def install() -> bool:
    """Monkeypatch ReActConverter.parse_response. Returns True if applied."""
    try:
        from react_agent import converter as C
    except Exception:                                     # noqa: BLE001
        return False

    Conv = getattr(C, "ReActConverter", None)
    if Conv is None:
        for name in dir(C):
            obj = getattr(C, name)
            if isinstance(obj, type) and hasattr(obj, "parse_response"):
                Conv = obj
                break
    if Conv is None:
        return False

    orig = Conv.parse_response

    def parse_response(self, response: str):
        if C.TASK_COMPLETE_SIGNAL in response:
            return orig(self, response)
        if self.ACTION_MARKER not in response:
            return orig(self, response)

        idx = response.find(self.ACTION_MARKER)
        action_text = response[idx + len(self.ACTION_MARKER):].strip()
        data = parse_action_text(action_text)
        if data is None:
            return orig(self, response)          # let upstream report the error
        return C.ParseResult(
            type=C.ParseResultType.ACTION,
            action=C.ParsedAction(name=data["name"],
                                  arguments=data.get("arguments", {})),
        )

    Conv.parse_response = parse_response
    print("[robust-parse] installed: string-aware brace scan + "
          "missing-brace repair", flush=True)
    return True


def maybe_install() -> None:
    """Install unless HD_ROBUST_PARSE=0."""
    if os.environ.get("HD_ROBUST_PARSE", "1") != "0":
        install()


def stats() -> dict:
    return dict(_STATS)
