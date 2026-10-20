"""OpenAI-compatible chat proxy backed by `claude -p` (Claude subscription).

Each /v1/chat/completions request becomes one `claude -p` call with no tools,
no MCP servers and no saved session. Listens on 127.0.0.1 only and answers
403 to browser requests (any Origin header).

Usage:
  python -m dskill.llm.claude_proxy --port 9990 \
      --claude-model claude-sonnet-5 --effort medium
Then point callers at OPENAI_BASE_URL=http://127.0.0.1:9990/v1.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CFG = {"model": "claude-sonnet-5", "effort": "medium", "timeout": 1800}


def render(messages):
    system, rest = [], []
    for m in messages:
        c = m.get("content", "")
        if isinstance(c, list):                    # content-part arrays
            c = "\n".join(p.get("text", "") for p in c
                          if isinstance(p, dict))
        if m.get("role") == "system":
            system.append(c)
        else:
            rest.append(c if m.get("role") == "user"
                        else f"(previous assistant reply)\n{c}")
    return "\n\n".join(system), "\n\n".join(rest)


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _reject_browser(self):
        """Answer 403 to a browser request (Origin header); True if rejected."""
        if self.headers.get("Origin") is None:
            return False
        n = int(self.headers.get("Content-Length", 0) or 0)
        if n > 0:
            self.rfile.read(n)
        self._json(403, {"error": {"message":
                                   "browser (Origin) requests are refused"}})
        return True

    def do_GET(self):
        if self._reject_browser():
            return
        self._json(200, {"object": "list", "data": [
            {"id": CFG["model"], "object": "model"}]})

    def do_POST(self):
        if self._reject_browser():
            return
        n = int(self.headers.get("Content-Length", 0))
        req = json.loads(self.rfile.read(n) or b"{}")
        system, prompt = render(req.get("messages", []))
        # prompt and system go via stdin and a tempfile; argv can hit ARG_MAX
        # `--tools ""` is an empty allowlist: the model gets no tools at all
        cmd = ["claude", "-p",
               "--model", CFG["model"],
               "--effort", CFG["effort"],
               "--tools", "",
               "--strict-mcp-config",
               "--no-session-persistence",
               "--output-format", "json"]
        sysfile = None
        if system.strip():
            sysfile = tempfile.NamedTemporaryFile(
                "w", suffix=".md", delete=False)
            sysfile.write(system)
            sysfile.close()
            cmd += ["--system-prompt-file", sysfile.name]
        env = {k: v for k, v in os.environ.items()
               if k != "ANTHROPIC_API_KEY"}         # subscription only
        if os.environ.get("HD_CC_CONFIG_DIR"):       # optional separate CLI profile
            env["CLAUDE_CONFIG_DIR"] = os.environ["HD_CC_CONFIG_DIR"]
        try:
            p = subprocess.run(cmd, input=prompt,
                               capture_output=True, text=True,
                               timeout=CFG["timeout"], env=env,
                               cwd=tempfile.gettempdir())
            j = json.loads(p.stdout)
            if p.returncode != 0 or j.get("is_error"):
                raise RuntimeError(
                    f"claude rc={p.returncode}: "
                    f"{str(j.get('result', p.stderr))[:300]}")
            text = j.get("result", "")
        except Exception as e:                     # noqa: BLE001
            return self._json(500, {"error": {"message": repr(e)[:400]}})
        finally:
            if sysfile is not None:
                try:
                    os.unlink(sysfile.name)
                except OSError:
                    pass
        self._json(200, {
            "id": f"chatcmpl-claudep-{int(time.time()*1000)}",
            "object": "chat.completion", "model": CFG["model"],
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant",
                                     "content": text}}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0,
                      "total_tokens": 0}})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=9990)
    ap.add_argument("--claude-model", default="claude-sonnet-5")
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()
    CFG.update(model=args.claude_model, effort=args.effort,
               timeout=args.timeout)
    print(f"[claude-proxy] :{args.port} -> claude -p {CFG['model']} "
          f"effort={CFG['effort']} (subscription, tools disabled)",
          flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), H).serve_forever()


if __name__ == "__main__":
    main()
