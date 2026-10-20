"""SkillOpt adapter for SpreadsheetBench whose rollouts run D-Skill's harness.

Each rollout writes the skill as skills/xlsx/SKILL.md, runs
envs.spreadsheetbench.run_baseline_t2s on the batch, scores it with the official
checker and saves the chat logs as predictions/<id>/conversation.json for SkillOpt's
reflect(). The harness settings defined here are also imported by the chess adapters.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from skillopt.datasets.base import BatchSpec
from skillopt.envs.base import EnvAdapter
from skillopt.envs.spreadsheetbench.dataloader import SpreadsheetBenchDataLoader

TASK_TYPES = ["cell_level", "sheet_level"]

# D-Skill checkout (DSKILL_ROOT) and the Python that runs its harnesses (DSKILL_PYTHON).
HARNESS_REPO = os.path.abspath(os.path.expanduser(os.environ.get("DSKILL_ROOT", "")))
if not os.environ.get("DSKILL_ROOT"):
    print("[skillopt-hd] DSKILL_ROOT is not set; set it to your D-Skill checkout", file=sys.stderr)
HARNESS_PY = os.environ.get("DSKILL_PYTHON", sys.executable)
OPENAI_ENV = os.environ.get("DSKILL_ENV_FILE", os.path.join(HARNESS_REPO, "openai.env"))
_KEY_RE = re.compile(r"^\s*export\s+OPENROUTER_API_KEY=(\S+)", re.M)


def _current_openrouter_key() -> str:
    """Re-read OPENROUTER_API_KEY from openai.env ($DSKILL_ENV_FILE) at each harness launch."""
    try:
        m = _KEY_RE.search(open(OPENAI_ENV).read())
    except OSError:
        return ""
    return m.group(1).strip("\"'") if m else ""
# relative to HARNESS_REPO, the evaluator's working directory
OFFICIAL_DATA = "envs/spreadsheetbench/data/spreadsheetbench_verified/spreadsheetbench_verified_400"
DATASET_JSON = (f"{HARNESS_REPO}/envs/spreadsheetbench/data/spreadsheetbench_verified/"
                "spreadsheetbench_verified_400/dataset.json")
SKILL_FRONT_MATTER = ('---\nname: xlsx\ndescription: "Spreadsheet manipulation '
                      'skills distilled from execution experience."\n---\n\n')
_BLOCK_RE = re.compile(r"^## \[\d+\] (SYSTEM|USER|ASSISTANT)\s*$", re.M)
_PROVIDER_ERR = re.compile(r"\b429\b|\b402\b|rate limit|queue_timeout|"
                           r"Error code: 5\d\d|provider returned no choices", re.I)
_MSG_CAP = 4000


def _parse_chat_log(path: str) -> tuple[str, str, list[dict]]:
    """Return (system_prompt, first_user_prompt, messages after the system)."""
    text = Path(path).read_text(errors="replace")
    parts = _BLOCK_RE.split(text)
    system, first_user, msgs = "", "", []
    # re.split with one capturing group -> [preamble, role, body, role, body, ...]
    for i in range(1, len(parts) - 1, 2):
        role, body = parts[i], parts[i + 1].strip()
        if role == "SYSTEM":
            system = body
            continue
        if role == "USER" and not first_user:
            first_user = body
        if len(body) > _MSG_CAP:
            body = body[:_MSG_CAP] + f"\n...[truncated {len(body) - _MSG_CAP} chars]"
        msgs.append({"role": role.lower(), "content": body})
    return system, first_user, msgs


class HDSpreadsheetBenchAdapter(EnvAdapter):
    """SkillOpt adapter whose rollouts run the D-Skill harness."""

    def __init__(
        self,
        split_dir: str = "",
        data_path: str = "",
        split_mode: str = "split_dir",
        split_ratio: str = "2:1:7",
        split_seed: int = 42,
        split_output_dir: str = "",
        data_root: str = "",
        workers: int = 12,
        max_turns: int = 100,
        analyst_workers: int = 16,
        failure_only: bool = False,
        minibatch_size: int = 8,
        edit_budget: int = 4,
        seed: int = 42,
        target_model: str = "qwen3.6-35b-a3b",
        harness_env: str = ("HD_PROVIDER=openrouter HD_OPENROUTER_PREFIX=qwen/ "
                            "HD_OR_PROVIDER=AkashML"),
        harness_timeout: int = 10800,
        harness_attempts: int = 3,
    ) -> None:
        self.workers = int(workers)
        self.max_turns = int(max_turns)
        self.analyst_workers = analyst_workers
        self.failure_only = failure_only
        self.minibatch_size = minibatch_size
        self.edit_budget = edit_budget
        self.target_model = target_model
        self.harness_env = dict(kv.split("=", 1) for kv in harness_env.split() if "=" in kv)
        self.harness_timeout = int(harness_timeout)
        self.harness_attempts = int(harness_attempts)
        self.dataloader = SpreadsheetBenchDataLoader(
            split_dir=split_dir, data_path=data_path, split_mode=split_mode,
            split_ratio=split_ratio, split_seed=split_seed,
            split_output_dir=split_output_dir, data_root=data_root, seed=seed)
        recs = json.load(open(DATASET_JSON))
        self._by_id = {str(r["id"]): r for r in recs}

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
        return list(TASK_TYPES)

    def _run_dir(self, skills_dir: Path, tag: str) -> Path:
        # mirrors envs.spreadsheetbench.run_baseline_t2s: runs/baseline_t2s_{model}_{parent}_{name}_{tag}
        return Path(HARNESS_REPO) / "runs" / (
            f"baseline_t2s_{self.target_model.replace('/', '_')}"
            f"_{skills_dir.parent.name}_{skills_dir.name}_{tag}")

    def _harness(self, ids: list[str], skills_dir: Path, tag: str, log: Path) -> None:
        env = dict(os.environ, **self.harness_env)
        key = _current_openrouter_key()
        if key:
            env["OPENROUTER_API_KEY"] = key
        cmd = [HARNESS_PY, "-m", "envs.spreadsheetbench.run_baseline_t2s", "--model", self.target_model,
               "--max-turns", str(self.max_turns), "--skills-dir", str(skills_dir),
               "--ids", ",".join(ids), "--run-tag", tag, "--concurrency", str(self.workers)]
        with open(log, "a") as fh:
            fh.write(f"\n$ {' '.join(cmd)}\n")
            fh.flush()
            try:
                subprocess.run(cmd, cwd=HARNESS_REPO, env=env, stdout=fh, stderr=subprocess.STDOUT,
                               timeout=self.harness_timeout, check=False)
            except subprocess.TimeoutExpired:
                fh.write(f"\n[hd-adapter] harness timed out after {self.harness_timeout}s\n")

    @staticmethod
    def _done_rows(run_dir: Path) -> dict[str, dict]:
        rows: dict[str, dict] = {}
        p = run_dir / "results.jsonl"
        if p.exists():
            for line in p.read_text().splitlines():
                if line.strip():
                    r = json.loads(line)
                    rows[str(r["task"])] = r
        return rows

    def _scrub(self, run_dir: Path, ids: list[str]) -> list[str]:
        """Drop episodes that died on provider errors so the resume re-runs them."""
        rows = self._done_rows(run_dir)
        bad = []
        for tid in ids:
            r = rows.get(tid)
            if r is None:
                continue
            logp = run_dir / "logs" / f"cli_skill_preloaded_agent_{tid}.md"
            txt = logp.read_text(errors="replace") if logp.exists() else ""
            if r.get("status") != "ok" or (not r.get("hard") and _PROVIDER_ERR.search(txt)):
                bad.append(tid)
        if bad:
            keep = [json.dumps(r) for t, r in rows.items() if t not in bad]
            (run_dir / "results.jsonl").write_text("".join(k + "\n" for k in keep))
            for tid in bad:
                for p in (run_dir / "logs" / f"cli_skill_preloaded_agent_{tid}.md",):
                    if p.exists():
                        p.unlink()
        return bad

    def _official(self, run_dir: Path, ids: list[str], log: Path) -> dict[str, dict]:
        cmd = [HARNESS_PY, "envs/spreadsheetbench/evaluate_with_official.py", "--data_path", OFFICIAL_DATA,
               "--output_dir", str(run_dir / "outputs"), "--start_idx", "0", "--end_idx", "400"]
        with open(log, "a") as fh:
            fh.write(f"\n$ {' '.join(cmd)}\n")
            fh.flush()
            subprocess.run(cmd, cwd=HARNESS_REPO, stdout=fh, stderr=subprocess.STDOUT,
                           timeout=3600, check=False)
        p = run_dir / "outputs" / "eval_official_results.json"
        d = json.load(open(p))
        rs = d["results"] if isinstance(d, dict) else d
        want = set(ids)
        out = {}
        for r in rs:
            rid = str(r.get("id", r.get("instance_id", r.get("task", ""))))
            if rid in want:
                out[rid] = r
        return out

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

        skills_dir = out / "skills"
        (skills_dir / "xlsx").mkdir(parents=True, exist_ok=True)
        (skills_dir / "xlsx" / "SKILL.md").write_text(SKILL_FRONT_MATTER + skill_content.strip() + "\n")
        # keyed on out_dir AND skill text: resumable, but a different skill never reuses old results
        tag = "so_" + hashlib.sha1((str(out.resolve()) + "\n" + skill_content.strip()).encode()).hexdigest()[:10]
        run_dir = self._run_dir(skills_dir, tag)
        log = out / "harness.log"
        t0 = time.time()

        for attempt in range(1, self.harness_attempts + 1):
            missing = [t for t in ids if t not in self._done_rows(run_dir)]
            if not missing:
                break
            self._harness(missing, skills_dir, tag, log)
            scrubbed = self._scrub(run_dir, ids)
            with open(log, "a") as fh:
                fh.write(f"[hd-adapter] attempt {attempt}: scrubbed {len(scrubbed)} provider-error episodes\n")
        rows = self._done_rows(run_dir)
        official = self._official(run_dir, ids, log)

        # token accounting for the target side (SkillOpt only sees optimizer calls)
        try:
            u = json.load(open(run_dir / "usage.json"))
            from skillopt.model.openai_compatible_backend import tracker
            tracker.record("rollout", int(u.get("prompt_tokens", 0)), int(u.get("completion_tokens", 0)))
        except Exception:  # noqa: BLE001
            pass

        results = []
        for it in items:
            tid = str(it["id"])
            rec = self._by_id.get(tid, {})
            itype = rec.get("instruction_type", it.get("instruction_type", ""))
            ttype = ("cell_level" if "cell" in itype.lower()
                     else "sheet_level" if "sheet" in itype.lower() else "other")
            off = official.get(tid)
            hard = 1 if (off and (off.get("success") or off.get("correct"))) else 0
            soft = float(off.get("soft_score", hard)) if off else 0.0
            row = rows.get(tid)
            logp = run_dir / "logs" / f"cli_skill_preloaded_agent_{tid}.md"
            system, user, msgs = _parse_chat_log(str(logp)) if logp.exists() else ("", "", [])
            n_turns = sum(1 for m in msgs if m["role"] == "assistant")
            if row is None:
                fail = "harness-missing"
            elif row.get("status") != "ok":
                fail = f"harness-error: {row.get('status')}"
            elif not hard:
                fail = ("eval-mismatch: " + "; ".join(
                    (c.get("message") or "output differs from the reference")[:160]
                    for c in (off or {}).get("test_cases", []) if not c.get("passed"))
                    if off else "output-not-found")
            else:
                fail = ""
            pdir = out / "predictions" / tid
            pdir.mkdir(parents=True, exist_ok=True)
            verdict = ("[POST-EXECUTION VERIFICATION]\n\nOfficial SpreadsheetBench scorer: "
                       + ("PASS" if hard else "FAIL")
                       + (f"\nFailure reason: {fail}" if fail else "")
                       + f"\nTest cases passed: {(off or {}).get('passed_count', 0)}/{(off or {}).get('total_count', 0)}")
            (pdir / "conversation.json").write_text(
                json.dumps(msgs + [{"role": "system", "content": verdict}], ensure_ascii=False))
            (pdir / "target_system_prompt.txt").write_text(system)
            (pdir / "target_user_prompt.txt").write_text(user)
            results.append({
                "id": tid, "ok": bool(hard), "hard": hard, "soft": soft,
                "instruction_type": itype, "task_type": ttype,
                "task_description": rec.get("instruction", ""),
                "n_turns": n_turns, "fail_reason": fail,
                "harness_status": (row or {}).get("status", "missing"),
                "harness_hard": (row or {}).get("hard"), "harness_wall_s": (row or {}).get("wall_s"),
                "harness_run_dir": str(run_dir),
                "target_system_prompt": system, "target_user_prompt": user,
            })
        with open(results_path, "w") as f:
            for r in results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        with open(log, "a") as fh:
            fh.write(f"[hd-adapter] {len(results)} items, official hard "
                     f"{sum(r['hard'] for r in results)}/{len(results)}, {time.time() - t0:.0f}s\n")
        return results
