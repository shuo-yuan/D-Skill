"""Chess adapter whose analyst reads pre-generated D-Skill lessons instead of trajectories.

The analyst keeps SkillOpt's prompt contract, edit budget and every later stage
(merge, rank, apply, val gate, slow update); only its input changes, to the D-Skill
contrast-analysis items (title / evidence / rule) of the minibatch's tasks. Train
rollouts are synthesised from the skill-free student run's labels; all other
rollouts are real. reflect() asserts that no val puzzle is requested.
"""
from __future__ import annotations

import json
import random
import re
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from skillopt.model import chat_optimizer
from skillopt.optimizer.meta_skill import format_meta_skill_context
from skillopt.optimizer.update_modes import truncate_payload
from skillopt.utils import extract_json

from skillopt.envs.spreadsheetbench_hd.adapter import HARNESS_REPO

from .adapter import ChessHDAdapter

_PROMPT_DIR = Path(__file__).parent / "prompts"
# Relative paths are resolved against the D-Skill checkout (DSKILL_ROOT).
LESSONS_DEFAULT = "runs/cqHQ3T/analysis"
STUDENT_RESULTS_DEFAULT = "runs/puzzles_qwen3.6-35b-a3b_qwtrT_tr100/results.jsonl"
_DECOR_RE = re.compile(r"^\((?:criticality:\s*[a-z]+|applies to [^)]*)\)\s*")


def _clean(content: str) -> str:
    return _DECOR_RE.sub("", (content or "").strip())


class ChessLessonAdapter(ChessHDAdapter):
    """ChessHDAdapter whose analyst reads D-Skill lessons instead of trajectories."""

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
        lesson_analysis: str = LESSONS_DEFAULT,
        student_results: str = STUDENT_RESULTS_DEFAULT,
        error_prompt: str = "analyst_error_lessons.md",
        success_prompt: str = "analyst_success_lessons.md",
        lesson_pool: str = "labels",
    ) -> None:
        super().__init__(
            split_dir=split_dir, data_path=data_path, split_mode=split_mode,
            split_ratio=split_ratio, split_seed=split_seed, split_output_dir=split_output_dir,
            workers=workers, tools=tools, analyst_workers=analyst_workers,
            failure_only=failure_only, minibatch_size=minibatch_size,
            edit_budget=edit_budget, seed=seed, target_model=target_model,
            harness_env=harness_env, harness_timeout=harness_timeout,
            harness_attempts=harness_attempts, msg_cap=msg_cap)
        if lesson_pool not in ("labels", "items"):
            raise ValueError("lesson_pool must be 'labels' (SkillOpt semantics: failed tasks -> gap "
                             "lessons, solved tasks -> keep lessons) or 'items' (any task with gap "
                             "items -> failure pool, any task with keep items -> success pool)")
        self.lesson_pool = lesson_pool
        lesson_analysis = str(Path(HARNESS_REPO) / lesson_analysis)    # no-op for absolute paths
        student_results = str(Path(HARNESS_REPO) / student_results)
        self.lessons = self._load_lessons(lesson_analysis)
        self.student = self._load_student_results(student_results)
        self.error_system = (_PROMPT_DIR / error_prompt).read_text()
        self.success_system = (_PROMPT_DIR / success_prompt).read_text()
        self._val_ids: set[str] = set()
        vp = Path(split_dir) / "val" / "items.json"
        if split_dir and vp.exists():
            self._val_ids = {str(x["id"]) for x in json.load(open(vp))}
        n_gap = sum(len(v["gap"]) for v in self.lessons.values())
        n_keep = sum(len(v["keep"]) for v in self.lessons.values())
        print(f"  [lesson-adapter] lessons from {lesson_analysis}: {len(self.lessons)} tasks, "
              f"{n_gap} gap items, {n_keep} keep items; student labels for {len(self.student)} "
              f"puzzles ({sum(1 for v in self.student.values() if v['solved'])} solved); "
              f"pool={lesson_pool}; val ids guarded: {len(self._val_ids)}", flush=True)

    @staticmethod
    def _load_lessons(analysis_dir: str) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for kind, fname in (("gap", "parsed_errors.json"), ("keep", "parsed_success.json")):
            p = Path(analysis_dir) / fname
            if not p.exists():
                raise FileNotFoundError(f"{p} not found (expected a D-Skill analysis dir)")
            for rec in json.load(open(p)):
                slot = out.setdefault(str(rec["instance_id"]), {"gap": [], "keep": []})
                for it in rec.get("items", []):
                    slot[kind].append({
                        "title": (it.get("title") or "").strip(),
                        "description": (it.get("description") or "").strip(),
                        "content": _clean(it.get("content") or ""),
                        "criticality": it.get("criticality"),
                    })
        return out

    @staticmethod
    def _load_student_results(path: str) -> dict[str, dict]:
        rows: dict[str, dict] = {}
        for line in open(path):
            if line.strip():
                r = json.loads(line)
                rows[str(r["puzzle"])] = r
        return rows

    def rollout(self, env_manager, skill_content: str, out_dir: str, **kwargs) -> list[dict]:
        """Train-batch rollouts come from the skill-free student run's labels; the val
        gate, baseline, slow-update and test rollouts are real (super().rollout)."""
        out = Path(out_dir)
        if out.name != "rollout":
            return super().rollout(env_manager, skill_content, out_dir, **kwargs)
        items = list(env_manager)
        out.mkdir(parents=True, exist_ok=True)
        results_path = out / "results.jsonl"
        if results_path.exists():
            existing = [json.loads(l) for l in results_path.read_text().splitlines() if l.strip()]
            ids = {str(it["id"]) for it in items}
            if existing and {str(r["id"]) for r in existing} >= ids:
                return [r for r in existing if str(r["id"]) in ids]
        rows = []
        for it in items:
            pid = str(it["id"])
            band = str(it.get("_band") or it.get("task_type") or "")
            srow = self.student.get(pid)
            need = int((srow or {}).get("solver_moves") or (len(str(it.get("Moves", "")).split()) // 2) or 1)
            got = int((srow or {}).get("moves_correct") or 0)
            d = self.lessons.get(pid, {"gap": [], "keep": []})
            if srow is None:                       # no label: fall back to the analysis
                hard = 0 if d["gap"] else 1
                fail = ("dskill_gap: " + d["gap"][0]["title"]) if d["gap"] else ""
            elif srow.get("solved"):
                hard, fail = 1, ""
            elif not srow.get("first_move_ok"):
                hard, fail = 0, "wrong first move or no move committed (skill-free student run)"
            else:
                hard, fail = 0, f"first move correct, then wrong move {got + 1} of {need} (line not converted)"
            rows.append({
                "id": pid, "ok": bool(hard), "hard": int(hard),
                "soft": (float(got) / max(1, need)) if srow is not None else float(hard),
                "task_type": band, "instruction_type": band,
                "task_description": (f"Chess tactics puzzle (lichess rating {it.get('Rating', '?')}, "
                                     f"themes: {it.get('Themes', '')}). Find the best move for the side "
                                     f"to move; the puzzle is decided within {need} solver move(s). "
                                     f"Up to {self.tools} engine-query tool calls per move."),
                "n_turns": 0, "fail_reason": fail,
                "harness_status": "synthetic_from_skill_free_student_run",
                "harness_wall_s": None, "harness_run_dir": "",
                "n_gap_items": len(d["gap"]), "n_keep_items": len(d["keep"]),
                "target_system_prompt": "", "target_user_prompt": "",
            })
        with open(results_path, "w") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        with open(out / "harness.log", "a") as fh:
            fh.write(f"[lesson-adapter] synthetic train rollout: {len(rows)} puzzles, student solved "
                     f"{sum(r['hard'] for r in rows)}/{len(rows)}, gap items "
                     f"{sum(r['n_gap_items'] for r in rows)}, keep items {sum(r['n_keep_items'] for r in rows)}\n")
        return rows

    # stands in for SkillOpt's fmt_minibatch_trajectories
    def _render_lessons(self, batch: list[dict], kind: str) -> tuple[str, int]:
        key = "gap" if kind == "failure" else "keep"
        parts, n = [], 0
        for r in batch:
            pid = str(r["id"])
            items = self.lessons.get(pid, {}).get(key, [])
            if not items:
                continue
            head = (f"### Task {pid} — {'FAILED' if kind == 'failure' else 'SOLVED'}\n"
                    f"Task: {r.get('task_description', '')}\n")
            if kind == "failure" and r.get("fail_reason"):
                head += f"Outcome: {r['fail_reason']}\n"
            body = []
            for k, it in enumerate(items, 1):
                n += 1
                body.append(f"Lesson {k}: {it['title']}\n"
                            + (f"Criticality: {it['criticality']}\n" if it.get("criticality") else "")
                            + f"Evidence: {it['description']}\n"
                            + f"Rule: {it['content']}")
            parts.append(head + "\n" + "\n\n".join(body))
        return "\n\n".join(parts), n

    def _analyze(self, kind: str, batch: list[dict], skill_content: str,
                 step_buffer_context: str, meta_skill_context: str) -> dict | None:
        text, n_lessons = self._render_lessons(batch, kind)
        if not text.strip():
            return None
        user = (f"## Current Skill\n{skill_content}\n\n"
                f"## Edit Budget\nProduce at most L={self.edit_budget} edits.\n\n")
        if step_buffer_context and step_buffer_context.strip():
            user += f"## Previous Steps in This Epoch\n{step_buffer_context}\n\n"
        ctx = format_meta_skill_context(meta_skill_context)
        if ctx:
            user += ctx + "\n\n"
        label = "FAILED" if kind == "failure" else "SOLVED"
        user += (f"## Distilled Lessons ({len(batch)} {label} tasks, {n_lessons} lessons)\n"
                 f"Each lesson was distilled by contrasting this student's trace with an expert's trace "
                 f"on the same task.\n\n{text}")
        system = self.error_system if kind == "failure" else self.success_system
        try:
            response, _ = chat_optimizer(system=system, user=user, max_completion_tokens=16384,
                                         retries=3, stage="analyst")
            result = extract_json(response)
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            return None
        if not result or "patch" not in result:
            return None
        result["source_type"] = kind
        result.setdefault("batch_size", len(batch))
        if kind == "failure":
            result.setdefault("failure_summary", [])
        else:
            result.setdefault("success_patterns", [])
        truncate_payload(result["patch"], self.edit_budget, "patch")
        result["_lesson_task_ids"] = [str(r["id"]) for r in batch]
        result["_n_lessons"] = n_lessons
        return result

    def reflect(self, results, skill_content: str, out_dir: str, **kwargs) -> list[dict]:
        """Same grouping as SkillOpt's run_minibatch_reflect (seeded failure/success
        minibatches, resumable patch files); only the analyst's input differs."""
        patches_dir = Path(kwargs.get("patches_dir") or (Path(out_dir) / "patches"))
        patches_dir.mkdir(parents=True, exist_ok=True)
        seed = kwargs.get("random_seed")
        M = max(1, int(self.minibatch_size))
        ids = [str(r["id"]) for r in results]
        leak = set(ids) & self._val_ids
        assert not leak, f"[lesson-adapter] val puzzles requested in reflect: {sorted(leak)[:5]}"

        if self.lesson_pool == "labels":
            failures = [r for r in results if not r.get("hard")]
            successes = [] if self.failure_only else [r for r in results if r.get("hard")]
        else:
            failures = [r for r in results if self.lessons.get(str(r["id"]), {}).get("gap")]
            successes = [] if self.failure_only else [r for r in results if self.lessons.get(str(r["id"]), {}).get("keep")]
        failures = [r for r in failures if self.lessons.get(str(r["id"]), {}).get("gap")]
        successes = [r for r in successes if self.lessons.get(str(r["id"]), {}).get("keep")]
        if seed is not None:
            random.Random(int(seed)).shuffle(failures)
            random.Random(int(seed) + 1).shuffle(successes)
        fail_batches = [failures[i: i + M] for i in range(0, len(failures), M)]
        succ_batches = [successes[i: i + M] for i in range(0, len(successes), M)]
        print(f"    [lesson-adapter] reflect: failure={len(failures)}->{len(fail_batches)} groups  "
              f"success={len(successes)}->{len(succ_batches)} groups  (M={M}, L={self.edit_budget}, "
              f"workers={self.analyst_workers}, pool={self.lesson_pool})", flush=True)

        raw: list[dict] = []
        pending: list[tuple[str, int, list[dict]]] = []
        for kind, batches in (("failure", fail_batches), ("success", succ_batches)):
            tag = "fail" if kind == "failure" else "succ"
            for idx, batch in enumerate(batches):
                p = patches_dir / f"minibatch_{tag}_{idx:03d}.json"
                if p.exists():
                    raw.append(json.load(open(p)))
                else:
                    pending.append((kind, idx, batch))
        sbc = kwargs.get("step_buffer_context", "") or ""
        msc = kwargs.get("meta_skill_context", "") or ""
        with ThreadPoolExecutor(max_workers=max(1, int(self.analyst_workers))) as ex:
            futs = {ex.submit(self._analyze, kind, batch, skill_content, sbc, msc): (kind, idx, len(batch))
                    for kind, idx, batch in pending}
            for f in as_completed(futs):
                kind, idx, n = futs[f]
                patch = f.result()
                tag = "fail" if kind == "failure" else "succ"
                if patch:
                    (patches_dir / f"minibatch_{tag}_{idx:03d}.json").write_text(
                        json.dumps(patch, ensure_ascii=False, indent=1))
                    raw.append(patch)
                    inner = patch.get("patch")
                    n_edits = len(inner.get("edits") or []) if isinstance(inner, dict) else 0
                    print(f"    [lesson-adapter] {tag} minibatch {idx}: {n} tasks, {patch.get('_n_lessons')} lessons -> "
                          f"{n_edits} edits, "
                          f"{len(patch.get('failure_summary', []))} failure types", flush=True)
                else:
                    print(f"    [lesson-adapter] {tag} minibatch {idx}: analyst returned nothing", flush=True)
        return raw
