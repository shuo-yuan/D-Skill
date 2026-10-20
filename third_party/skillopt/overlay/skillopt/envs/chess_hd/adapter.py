"""SkillOpt adapter for lichess tactics puzzles whose rollouts run D-Skill's harness.

Each rollout runs envs.chess.run_puzzles on the batch (the paper's qwen protocol:
10 engine queries per move, Tool-Trust line, skill under "## Skill"), scores
hard = solved and soft = correct moves / required, and saves the logs as
predictions/<id>/conversation.json for SkillOpt's reflect(). The analyst sees the
outcome, never the solution line.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from skillopt.datasets.base import BatchSpec, SplitDataLoader
from skillopt.envs.base import EnvAdapter
from skillopt.envs.spreadsheetbench_hd.adapter import (
    HARNESS_PY, HARNESS_REPO, _current_openrouter_key, _BLOCK_RE)

BANDS = ["400-800", "800-1200", "1200-1600", "1600-2000", "2000-2400"]

# verbatim from the paper's qwen chess protocol
TOOL_TRUST_EXTRA = (
    "## Tool Trust\n"
    "The tool outputs are computed by an exact chess engine and are 100% correct. "
    "Never question, re-derive, or override any tool result — including legal-move "
    "lists — with your own board reasoning. When your mental picture disagrees with "
    "a tool output, the tool is right and your picture is wrong; update your picture "
    "and move on.")


def _parse_puzzle_log(path: str, cap: int) -> list[dict]:
    """envs.chess.run_puzzles log -> chat messages (USER/ASSISTANT blocks)."""
    text = Path(path).read_text(errors="replace")
    parts = _BLOCK_RE.split(text)
    msgs = []
    for i in range(1, len(parts) - 1, 2):
        role, body = parts[i], parts[i + 1].strip()
        if role == "SYSTEM":
            continue
        if len(body) > cap:
            # keep head and tail: the tail carries the committed move after long reasoning
            head, tail = int(cap * 0.4), int(cap * 0.6)
            body = (body[:head] + f"\n...[truncated {len(body) - cap} chars of reasoning]...\n"
                    + body[-tail:])
        msgs.append({"role": role.lower(), "content": body})
    return msgs


def _system_prompt(tools: int, skill: str) -> str:
    """Reconstruct the harness system prompt (TOOLS_SYSTEM + ## Skill + Tool Trust)."""
    try:
        if HARNESS_REPO not in sys.path:
            sys.path.insert(0, HARNESS_REPO)
        from envs.chess import run_puzzles as rp, chess_query as cq  # type: ignore
        base = rp.TOOLS_SYSTEM.format(TOOL_DOC=cq.TOOL_DOC.format(K=tools))
    except Exception:  # noqa: BLE001
        base = ("You are a strong chess player. You will be shown a chess position and must "
                f"choose one move. Up to {tools} engine-query tool calls per move.")
    return base + (f"\n## Skill\n{skill.strip()}\n" if skill.strip() else "") + "\n" + TOOL_TRUST_EXTRA + "\n"


class ChessDataLoader(SplitDataLoader):
    """split_dir/{train,val,test}/items.json, one puzzle dict per item (id = PuzzleId)."""


class ChessHDAdapter(EnvAdapter):
    """SkillOpt adapter whose rollouts run D-Skill's qwen puzzle harness."""

    def __init__(
        self,
        split_dir: str = "",
        data_path: str = "",
        split_mode: str = "split_dir",
        split_ratio: str = "6:4:0",
        split_seed: int = 42,
        split_output_dir: str = "",
        workers: int = 12,
        tools: int = 10,
        analyst_workers: int = 4,
        failure_only: bool = False,
        minibatch_size: int = 8,
        edit_budget: int = 4,
        seed: int = 42,
        target_model: str = "qwen3.6-35b-a3b",
        harness_env: str = ("HD_PROVIDER=openrouter HD_OPENROUTER_PREFIX=qwen/ "
                            "HD_OR_PROVIDER=AkashML"),
        harness_timeout: int = 5400,
        harness_attempts: int = 3,
        msg_cap: int = 5000,
    ) -> None:
        self.workers = int(workers)
        self.tools = int(tools)
        self.analyst_workers = analyst_workers
        self.failure_only = failure_only
        self.minibatch_size = minibatch_size
        self.edit_budget = edit_budget
        self.target_model = target_model
        self.harness_env = dict(kv.split("=", 1) for kv in harness_env.split() if "=" in kv)
        self.harness_timeout = int(harness_timeout)
        self.harness_attempts = int(harness_attempts)
        self.msg_cap = int(msg_cap)
        self.dataloader = ChessDataLoader(
            split_dir=split_dir, data_path=data_path, split_mode=split_mode,
            split_ratio=split_ratio, split_seed=split_seed,
            split_output_dir=split_output_dir, seed=seed)

    def setup(self, cfg: dict) -> None:
        super().setup(cfg)
        self.dataloader.setup(cfg)

    def get_dataloader(self):
        return self.dataloader

    def build_env_from_batch(self, batch: BatchSpec, **kwargs):
        return list(batch.payload or [])

    def build_train_env(self, batch_size: int, seed: int, **kwargs):
        return self.build_env_from_batch(
            self.dataloader.build_train_batch(batch_size=batch_size, seed=seed, **kwargs), **kwargs)

    def build_eval_env(self, env_num: int, split: str, seed: int, **kwargs):
        return self.build_env_from_batch(
            self.dataloader.build_eval_batch(env_num=env_num, split=split, seed=seed, **kwargs), **kwargs)

    def get_task_types(self) -> list[str]:
        return list(BANDS)

    def _run_dir(self, tag: str) -> Path:
        return Path(HARNESS_REPO) / "runs" / f"puzzles_{self.target_model}_{tag}"

    def _harness(self, puzzles_file: Path, skill_file: Path, tag: str, log: Path) -> None:
        env = dict(os.environ, **self.harness_env)
        env["HD_TASK_EXTRA"] = TOOL_TRUST_EXTRA
        key = _current_openrouter_key()
        if key:
            env["OPENROUTER_API_KEY"] = key
        cmd = [HARNESS_PY, "-m", "envs.chess.run_puzzles", "--model", self.target_model,
               "--tools", str(self.tools), "--puzzles", str(puzzles_file),
               "--run-tag", tag, "--slots", str(self.workers), "--skill-file", str(skill_file)]
        with open(log, "a") as fh:
            fh.write(f"\n$ {' '.join(cmd)}\n")
            fh.flush()
            try:
                subprocess.run(cmd, cwd=HARNESS_REPO, env=env, stdout=fh, stderr=subprocess.STDOUT,
                               timeout=self.harness_timeout, check=False)
            except subprocess.TimeoutExpired:
                fh.write(f"\n[chess-adapter] harness timed out after {self.harness_timeout}s\n")

    @staticmethod
    def _done_rows(run_dir: Path) -> dict[str, dict]:
        rows: dict[str, dict] = {}
        p = run_dir / "results.jsonl"
        if p.exists():
            for line in p.read_text().splitlines():
                if line.strip():
                    r = json.loads(line)
                    rows[str(r["puzzle"])] = r
        return rows

    def _scrub(self, run_dir: Path, ids: list[str]) -> list[str]:
        """Drop episodes with a provider error (429/402) or no committed move, so they re-run."""
        rows = self._done_rows(run_dir)
        bad = []
        for pid in ids:
            if pid not in rows:
                continue
            logp = run_dir / "logs" / f"puzzle_{pid}.md"
            txt = logp.read_text(errors="replace") if logp.exists() else ""
            if "429" in txt or "402" in txt or "<action>" not in txt:
                bad.append(pid)
        if bad:
            keep = [json.dumps(r) for t, r in rows.items() if t not in bad]
            (run_dir / "results.jsonl").write_text("".join(k + "\n" for k in keep))
            for pid in bad:
                p = run_dir / "logs" / f"puzzle_{pid}.md"
                if p.exists():
                    p.unlink()
        return bad

    def rollout(self, env_manager, skill_content: str, out_dir: str, **kwargs) -> list[dict]:
        items = list(env_manager)
        ids = [str(it["id"]) for it in items]
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        results_path = out / "results.jsonl"
        if results_path.exists():
            existing = [json.loads(l) for l in results_path.read_text().splitlines() if l.strip()]
            if existing and {str(r["id"]) for r in existing} >= set(ids):
                return [r for r in existing if str(r["id"]) in set(ids)]

        skill_file = out / "skill.md"
        skill_file.write_text(skill_content.strip() + "\n")
        puzzles_file = out / "puzzles.json"
        puzzles_file.write_text(json.dumps(items, ensure_ascii=False))
        # keyed on out_dir AND skill text: resumable, but a different skill never reuses old results
        tag = "so_" + hashlib.sha1((str(out.resolve()) + "\n" + skill_content.strip()).encode()).hexdigest()[:10]
        run_dir = self._run_dir(tag)
        log = out / "harness.log"
        t0 = time.time()

        for attempt in range(1, self.harness_attempts + 1):
            missing = [t for t in ids if t not in self._done_rows(run_dir)]
            if not missing:
                break
            # run_puzzles skips puzzles already in results.jsonl, so pass the whole batch
            self._harness(puzzles_file, skill_file, tag, log)
            scrubbed = self._scrub(run_dir, ids)
            with open(log, "a") as fh:
                fh.write(f"[chess-adapter] attempt {attempt}: scrubbed {len(scrubbed)} bad episodes\n")
        rows = self._done_rows(run_dir)

        # target-side token accounting (the harness records usage per puzzle)
        try:
            from skillopt.model.openai_compatible_backend import tracker
            pt = sum(int((rows[t].get("usage") or {}).get("prompt_tokens", 0)) for t in ids if t in rows)
            ct = sum(int((rows[t].get("usage") or {}).get("completion_tokens", 0)) for t in ids if t in rows)
            tracker.record("rollout", pt, ct)
        except Exception:  # noqa: BLE001
            pass

        system = _system_prompt(self.tools, skill_content)
        results = []
        for it in items:
            pid = str(it["id"])
            row = rows.get(pid)
            band = str(it.get("_band") or it.get("task_type") or "")
            logp = run_dir / "logs" / f"puzzle_{pid}.md"
            msgs = _parse_puzzle_log(str(logp), self.msg_cap) if logp.exists() else []
            raw = logp.read_text(errors="replace") if logp.exists() else ""
            user = next((m["content"] for m in msgs if m["role"] == "user"), "")
            n_turns = sum(1 for m in msgs if m["role"] == "assistant")
            need = int((row or {}).get("solver_moves") or (len(str(it.get("Moves", "")).split()) // 2) or 1)
            got = int((row or {}).get("moves_correct") or 0)
            if row is None:
                hard, fail = 0, "harness-missing"
            elif row.get("solved"):
                hard, fail = 1, ""
            elif not row.get("first_move_ok"):
                hard, fail = 0, ("wrong first move: the committed move is not the puzzle solution"
                                 if "<action>" in raw else "no move committed (no <action> tag)")
            else:
                hard, fail = 0, f"first move correct, then wrong move {got + 1} of {need} (line not converted)"
            soft = float(got) / max(1, need) if row is not None else 0.0
            pdir = out / "predictions" / pid
            pdir.mkdir(parents=True, exist_ok=True)
            verdict = ("[POST-EXECUTION VERIFICATION]\n\nPuzzle outcome (env-side scoring): "
                       + ("SOLVED" if hard else "FAILED")
                       + (f"\nFailure reason: {fail}" if fail else "")
                       + f"\nSolver moves required: {need}; correct: {got}"
                       + f"\nPuzzle rating: {it.get('Rating', '?')} (band {band})")
            (pdir / "conversation.json").write_text(
                json.dumps(msgs + [{"role": "system", "content": verdict}], ensure_ascii=False))
            (pdir / "target_system_prompt.txt").write_text(system)
            (pdir / "target_user_prompt.txt").write_text(user)
            results.append({
                "id": pid, "ok": bool(hard), "hard": hard, "soft": soft,
                "task_type": band, "instruction_type": band,
                "task_description": (f"Chess tactics puzzle (lichess rating {it.get('Rating', '?')}, "
                                     f"themes: {it.get('Themes', '')}). Find the best move for the side "
                                     f"to move; the puzzle is decided within {need} solver move(s). "
                                     f"Up to {self.tools} engine-query tool calls per move."),
                "n_turns": n_turns, "fail_reason": fail,
                "harness_status": "ok" if row is not None else "missing",
                "harness_wall_s": (row or {}).get("wall_s"),
                "harness_run_dir": str(run_dir),
                "target_system_prompt": system, "target_user_prompt": user,
            })
        with open(results_path, "w") as f:
            for r in results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        with open(log, "a") as fh:
            fh.write(f"[chess-adapter] {len(results)} puzzles, solved "
                     f"{sum(r['hard'] for r in results)}/{len(results)}, {time.time() - t0:.0f}s\n")
        return results
