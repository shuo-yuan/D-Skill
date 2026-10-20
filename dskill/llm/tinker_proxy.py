"""OpenAI-compatible shim in front of a Tinker sampling checkpoint.

Serves a fine-tuned (or base) model at the address dskill.llm.client uses
when no OPENAI_API_KEY is set, so the eval harnesses need no changes.
Listens on 127.0.0.1 only and answers 403 to browser requests (any Origin
header).

Usage:
    TINKER_MODEL_PATH=<ckpt> python -m dskill.llm.tinker_proxy --port 8088
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

_STATE: dict = {}


import re as _re

# HD_STRIP_THINK=1 moves <think> reasoning into reasoning_content and scrubs
# it from incoming history; off by default (raw passthrough).
_STRIP_THINK = os.environ.get("HD_STRIP_THINK", "0") == "1"


def _split_think(text: str) -> tuple[str, str]:
    """Return (content, reasoning): reasoning is everything before the first
    </think> (the prompt opens the block), content everything after it."""
    if "</think>" in text:
        reasoning, content = text.split("</think>", 1)
    else:                       # never closed: treat the whole reply as answer
        reasoning, content = "", text
    reasoning = reasoning.replace("<think>", "")
    content = content.replace("<think>", "").replace("</think>", "")
    return content.strip(), reasoning.strip()


def _scrub_history(content: str) -> str:
    if "</think>" in content:
        content = content.split("</think>", 1)[1]
    return content.replace("<think>", "").replace("</think>", "").lstrip()


def _render(messages: list[dict], tok) -> list[int]:
    """Chat messages -> flat token id list, clipping history to fit ctx."""
    msgs = [{"role": m.get("role", "user"), "content": m.get("content") or ""}
            for m in messages]
    if _STRIP_THINK:
        for m in msgs:
            if m["role"] == "assistant" and ("<think>" in m["content"]
                                             or "</think>" in m["content"]):
                m["content"] = _scrub_history(m["content"])
    def _tokens(ms):
        o = tok.apply_chat_template(ms, tokenize=True, add_generation_prompt=True)
        if hasattr(o, "input_ids"):           # BatchEncoding
            o = o.input_ids
        elif isinstance(o, dict):
            o = o["input_ids"]
        if o and isinstance(o[0], (list, tuple)):   # batched
            o = o[0]
        return list(o)
    out = _tokens(msgs)
    # tinker rejects prompts over ctx: clip the largest message to head + tail
    reserve = int(os.environ.get("HD_CTX_RESERVE", "4096"))
    limit = _STATE.get("ctx", 40960) - reserve
    clips = 0
    while len(out) > limit and clips < 20:
        cand = max((i for i, m in enumerate(msgs) if m["role"] != "system"),
                   key=lambda i: len(msgs[i]["content"]), default=None)
        if cand is None or len(msgs[cand]["content"]) < 4000:
            break
        c = msgs[cand]["content"]
        keep = max(1000, len(c) // 3)
        msgs[cand]["content"] = (c[:keep] + "\n...[clipped by proxy: "
                                 f"{len(c) - 2*keep} chars omitted]...\n" + c[-keep:])
        out = _tokens(msgs)
        clips += 1
    if clips:
        print(f"[proxy] ctx-guard clipped {clips} message(s) -> {len(out)} tokens",
              flush=True)
    return list(out)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _reject_browser(self) -> bool:
        """Answer 403 to a browser request (Origin header); True if rejected."""
        if self.headers.get("Origin") is None:
            return False
        n = int(self.headers.get("Content-Length", 0) or 0)
        if n > 0:
            self.rfile.read(n)
        self._json(403, {"error": {"message":
                                   "browser (Origin) requests are refused"}})
        return True

    def do_GET(self):                              # /v1/models probe
        if self._reject_browser():
            return
        self._json(200, {"object": "list", "data": [
            {"id": "tinker-sft", "object": "model"}]})

    def do_POST(self):
        if self._reject_browser():
            return
        if not self.path.rstrip("/").endswith("chat/completions"):
            return self._json(404, {"error": "not found"})
        n = int(self.headers.get("Content-Length", 0))
        req = json.loads(self.rfile.read(n) or b"{}")
        tok, sampler = _STATE["tok"], _STATE["sampler"]
        from tinker import types
        try:
            ids = _render(req.get("messages", []), tok)
            # shrink max_tokens to fit the context window (floor 256)
            mt = int(req.get("max_tokens") or _STATE["max_tokens"])
            mt = max(256, min(mt, _STATE["ctx"] - len(ids) - 16))
            # the sampler does not stop at <|im_end|> by itself; stop on EOS
            eos_ids = [i for i in {tok.eos_token_id,
                                   tok.convert_tokens_to_ids("<|im_end|>"),
                                   tok.convert_tokens_to_ids("<|endoftext|>")}
                       if isinstance(i, int) and i >= 0]
            caller_stop = req.get("stop") or []
            if isinstance(caller_stop, str):
                caller_stop = [caller_stop]
            params = types.SamplingParams(
                max_tokens=mt,
                temperature=float(req.get("temperature", 1.0)),
                top_p=float(req.get("top_p", _STATE["top_p"])),
                top_k=int(req.get("top_k", _STATE["top_k"])),
                stop=(eos_ids if not caller_stop else list(caller_stop)))
            out = sampler.sample(
                prompt=types.ModelInput.from_ints(ids),
                sampling_params=params, num_samples=1).result()
            toks = list(out.sequences[0].tokens)
            cut = next((k for k, t in enumerate(toks) if t in eos_ids),
                       len(toks))
            finish = "stop" if cut < len(toks) or len(toks) < mt else "length"
            toks = toks[:cut]
            text = tok.decode(toks, skip_special_tokens=True)
        except Exception as e:                     # noqa: BLE001
            return self._json(500, {"error": {"message": repr(e)}})
        reasoning = ""
        if _STRIP_THINK:
            text, reasoning = _split_think(text)
        msg = {"role": "assistant", "content": text}
        if reasoning:
            msg["reasoning_content"] = reasoning
        self._json(200, {
            "id": f"chatcmpl-tinker-{int(time.time()*1000)}",
            "object": "chat.completion",
            "model": req.get("model", "tinker-sft"),
            "choices": [{"index": 0, "finish_reason": finish,
                         "message": msg}],
            "usage": {"prompt_tokens": len(ids),
                      "completion_tokens": len(toks),
                      "total_tokens": len(ids) + len(toks)},
        })


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8088)
    ap.add_argument("--model-path", default=os.environ.get("TINKER_MODEL_PATH"))
    ap.add_argument("--base-model", default=os.environ.get("TINKER_BASE_MODEL"))
    # model-published defaults, used only when the caller omits the param
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--top-k", type=int, default=20)
    # <think> reasoning shares this budget
    ap.add_argument("--max-tokens", type=int, default=32768)
    # context budget (tokens) used by the overflow guard
    ap.add_argument("--ctx", type=int, default=40960)
    args = ap.parse_args()
    if not (args.model_path or args.base_model):
        sys.exit("need --model-path (tuned checkpoint) or --base-model "
                 "(untuned base, for floor measurements)")

    import tinker
    sc = tinker.ServiceClient()
    if args.model_path:
        _STATE["sampler"] = sc.create_sampling_client(
            model_path=args.model_path)
        served = args.model_path
    else:                                   # untuned base model floor
        _STATE["sampler"] = sc.create_sampling_client(
            base_model=args.base_model)
        served = f"{args.base_model} (UNTUNED base)"
    _STATE["tok"] = sc.create_lora_training_client(
        base_model=args.base_model, rank=1).get_tokenizer() \
        if args.base_model else _STATE["sampler"].get_tokenizer()
    _STATE["served"] = served
    _STATE["top_p"] = args.top_p
    _STATE["top_k"] = args.top_k
    _STATE["max_tokens"] = args.max_tokens
    _STATE["ctx"] = args.ctx

    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"[proxy] serving {_STATE['served']} on "
          f"http://127.0.0.1:{args.port}/v1", flush=True)
    print(f"[proxy] sampling defaults: top_p={args.top_p} top_k={args.top_k} "
          f"max_tokens={args.max_tokens} (caller values take precedence)",
          flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
