"""Opt-in native tool-calling bridge (HD_NATIVE_TOOLS=1).

Some models (e.g. gpt-5.6-luna) refuse the text-protocol scaffold because the
request attaches no `tools`. install() patches OpenAIClient to send the
text-protocol history as native tool calls and to render the model's tool calls
back as "Action:\\n{json}" text, so the rest of the harness is unchanged.
Without the flag install() is a no-op.
"""

from __future__ import annotations

import json
import os
import re

BASH_TOOL = {
    "type": "function",
    "function": {
        "name": "bash",
        "description": ("Run a shell command in the task working "
                        "environment and return its stdout/stderr. "
                        "Python is available as `python`/`python3`."),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string",
                            "description": "The shell command to run."}},
            "required": ["command"],
        },
    },
}

# HD_NATIVE_EXTRA_TOOLS: JSON list of extra function-tool specs attached alongside bash.
_EXTRA_TOOLS = json.loads(os.environ.get("HD_NATIVE_EXTRA_TOOLS", "[]") or "[]")

_ACTION_RE = re.compile(r"Action:\s*\n?\s*(\{.*\})\s*\Z", re.S)
_FMT_SECTION_RE = re.compile(
    r"## CRITICAL: Action Format Requirements.*?(?=## Completing the Task)",
    re.S)
_NATIVE_NOTE = (
    "## Tool Use\n\n"
    "A real `bash` tool is attached to this session via the native "
    "tool-calling API. Call it to run shell commands; its output is "
    "returned to you. Python is available inside it. Use one call per "
    "step and react to its output before the next call.\n\n")


def _swap_system(content: str) -> str:
    out, n = _FMT_SECTION_RE.subn(_NATIVE_NOTE, content)
    return out if n else content


def _to_native(openai_messages: list[dict]) -> list[dict]:
    out: list[dict] = []
    pending_id = None
    k = 0
    for m in openai_messages:
        role, content = m.get("role"), m.get("content") or ""
        if role == "system":
            out.append({"role": "system", "content": _swap_system(content)})
        elif role == "assistant":
            match = _ACTION_RE.search(content.strip())
            act = None
            if match:
                try:
                    act = json.loads(match.group(1))
                except Exception:                          # noqa: BLE001
                    act = None
            if act and isinstance(act, dict) and "name" in act:
                k += 1
                pending_id = f"call_hd{k:04d}"
                pre = content[:match.start()].strip()
                out.append({
                    "role": "assistant",
                    "content": pre or None,
                    "tool_calls": [{
                        "id": pending_id, "type": "function",
                        "function": {
                            "name": act["name"],
                            "arguments": json.dumps(
                                act.get("arguments", {}))}}]})
            else:
                out.append({"role": "assistant", "content": content})
                pending_id = None
        elif (role == "user" and pending_id
              and content.lstrip().startswith("Observation:")):
            obs = content.lstrip()[len("Observation:"):].strip()
            out.append({"role": "tool", "tool_call_id": pending_id,
                        "content": obs})
            pending_id = None
        else:
            out.append({"role": role, "content": content})
            pending_id = None
    return out


def install() -> None:
    if os.environ.get("HD_NATIVE_TOOLS") != "1":
        return
    from react_agent.models import OpenAIClient
    if getattr(OpenAIClient, "_hd_native_tools", False):
        return
    orig = OpenAIClient._send_request_with_retry

    def patched(self, messages, config):
        native = _to_native(messages)
        cfg = dict(config)
        cfg["tools"] = [BASH_TOOL] + _EXTRA_TOOLS
        # stop sequences belong to the text protocol and can truncate native replies
        cfg.pop("stop", None)
        # gpt-5.6 models reject function tools with any reasoning_effort but an explicit "none"
        cfg["reasoning_effort"] = "none"
        # the same key can arrive nested in extra_body (ModelSettings path)
        if isinstance(cfg.get("extra_body"), dict) and \
                cfg["extra_body"].get("reasoning_effort") not in (None, "none"):
            cfg["extra_body"] = dict(cfg["extra_body"], reasoning_effort="none")
        resp = orig(self, native, cfg)
        try:
            msg = resp.choices[0].message
            tcs = getattr(msg, "tool_calls", None)
            if tcs:
                tc = tcs[0]
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except Exception:                          # noqa: BLE001
                    args = {"command": tc.function.arguments or ""}
                act = {"name": tc.function.name, "arguments": args}
                pre = (msg.content or "").strip()
                msg.content = ((pre + "\n\n") if pre else "") + \
                    "Action:\n" + json.dumps(act, indent=4)
        except Exception:                                  # noqa: BLE001
            pass
        return resp

    OpenAIClient._send_request_with_retry = patched
    OpenAIClient._hd_native_tools = True
    print("[native-tools] HD_NATIVE_TOOLS=1: bash tool attached natively; "
          "text protocol translated at the client layer", flush=True)
