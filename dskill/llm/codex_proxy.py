"""OpenAI-compatible chat proxy backed by `codex exec` (ChatGPT subscription).

Each /v1/chat/completions request becomes one `codex exec` call in a
read-only sandbox with web search off. CODEX_HOME (copied auth.json, model
catalog, codex session logs) is a temp dir deleted on exit. Listens on
127.0.0.1 only and answers 403 to browser requests (any Origin header).

Usage:
  python -m dskill.llm.codex_proxy --port 9992 --model gpt-5.4-nano --effort medium
Then point callers at OPENAI_BASE_URL=http://127.0.0.1:9992/v1.
"""
from __future__ import annotations

import argparse
import atexit
import json
import os
import shutil
import signal
import subprocess
import tempfile
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CFG = {"model": "gpt-5.4-nano", "effort": "medium", "timeout": 1800,
       "home": ""}

BASE_INSTRUCTIONS = ("You are a careful analyst. Reply directly with your "
                     "analysis in plain text. You have no tools; never try "
                     "to run commands or read files.")


def build_home(model: str, effort: str) -> str:
    """Temp CODEX_HOME: copied auth plus a model catalog, which non-default
    slugs such as gpt-5.4-nano need under a ChatGPT account."""
    home = tempfile.mkdtemp(prefix="codexproxy_")
    try:
        _fill_home(home, model, effort)
    except BaseException:
        shutil.rmtree(home, ignore_errors=True)
        raise
    return home


def _fill_home(home: str, model: str, effort: str) -> None:
    catalog = {"models": [{
        "slug": model, "display_name": model,
        "supported_reasoning_levels": [
            {"effort": "low", "description": "fast"},
            {"effort": "medium", "description": "balanced"},
            {"effort": "high", "description": "deep"}],
        "supports_search_tool": False, "shell_type": "default",
        "visibility": "list", "supported_in_api": True,
        "priority": 0, "support_verbosity": False,
        "truncation_policy": {"mode": "tokens", "limit": 250000},
        "experimental_supported_tools": [],
        "base_instructions": BASE_INSTRUCTIONS}]}
    with open(os.path.join(home, "catalog.json"), "w") as f:
        f.write(json.dumps(catalog))
    cfg = (f"model = {json.dumps(model)}\n"
           f"model_catalog_json = "
           f"{json.dumps(os.path.join(home, 'catalog.json'))}\n"
           f"model_reasoning_effort = {json.dumps(effort)}\n"
           'preferred_auth_method = "chatgpt"\n'
           f"base_instructions = {json.dumps(BASE_INSTRUCTIONS)}\n"
           'web_search = "disabled"\n'
           "[features]\nshell_tool = false\n")
    with open(os.path.join(home, "config.toml"), "w") as f:
        f.write(cfg)
    shutil.copy(os.path.expanduser("~/.codex/auth.json"),
                os.path.join(home, "auth.json"))


def cleanup_home() -> None:
    """Delete the temp CODEX_HOME (auth.json copy + codex session logs)."""
    home, CFG["home"] = CFG.get("home", ""), ""
    if home:
        shutil.rmtree(home, ignore_errors=True)


def _exit_on_signal(signum, _frame):
    cleanup_home()
    # re-deliver with the default action so the exit status shows the signal
    signal.signal(signum, signal.SIG_DFL)
    os.kill(os.getpid(), signum)


def render(messages):
    parts = []
    for m in messages:
        c = m.get("content", "")
        if isinstance(c, list):
            c = "\n".join(p.get("text", "") for p in c if isinstance(p, dict))
        role = m.get("role")
        if role == "system":
            parts.append(c)
        elif role == "user":
            parts.append(c)
        else:
            parts.append(f"(previous assistant reply)\n{c}")
    parts.append("Reply directly with your analysis. Do not run commands, "
                 "read files, or use any tools.")
    return "\n\n".join(parts)


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
        prompt = render(req.get("messages", []))
        out = tempfile.NamedTemporaryFile("r", suffix=".md", delete=False)
        out.close()                  # codex writes it by path; keep the name
        cmd = ["codex", "exec",
               "-s", "read-only",
               "--skip-git-repo-check",
               "--color", "never",
               "-o", out.name]
        env = {k: v for k, v in os.environ.items()
               if k != "OPENAI_API_KEY"}            # subscription only
        env["CODEX_HOME"] = CFG["home"]
        try:
            p = subprocess.run(cmd, input=prompt, capture_output=True,
                               text=True, timeout=CFG["timeout"], env=env,
                               cwd=tempfile.gettempdir())
            with open(out.name) as f:
                text = f.read()
            if p.returncode != 0 or not text.strip():
                raise RuntimeError(
                    f"codex rc={p.returncode}: "
                    f"{(p.stderr or p.stdout)[-300:]}")
        except Exception as e:                      # noqa: BLE001
            return self._json(500, {"error": {"message": repr(e)[:400]}})
        finally:
            try:
                os.unlink(out.name)
            except OSError:
                pass
        self._json(200, {
            "id": f"chatcmpl-codexp-{int(time.time()*1000)}",
            "object": "chat.completion", "model": CFG["model"],
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant",
                                     "content": text}}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0,
                      "total_tokens": 0}})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=9992)
    ap.add_argument("--model", default="gpt-5.4-nano")
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()
    CFG.update(model=args.model, effort=args.effort, timeout=args.timeout,
               home=build_home(args.model, args.effort))
    atexit.register(cleanup_home)
    for sig in (signal.SIGTERM, signal.SIGINT):
        if signal.getsignal(sig) is not signal.SIG_IGN:   # keep an inherited ignore
            signal.signal(sig, _exit_on_signal)
    print(f"[codex-proxy] :{args.port} -> codex exec -m {args.model} "
          f"(effort {args.effort}, subscription)", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), H).serve_forever()


if __name__ == "__main__":
    main()
