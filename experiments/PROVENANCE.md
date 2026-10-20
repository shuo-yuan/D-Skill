# Paper provenance

The code and settings behind each result in the paper. The evaluated skill documents are in `paper_skills/`, and
`paper_skills/manifest.tsv` gives each one's table and cell. The teacher and student traces and the
analyses behind these documents are not released; running the pipeline again regenerates them (see the README).

Shared settings:

- **SpreadsheetBench**: the Verified-400 data in `envs/spreadsheetbench/data/`. Distillation uses the 99 `distill` ids (a
  fixed subset of the 200 `train` ids) and evaluation the 200 `eval` ids of
  `envs/spreadsheetbench/assets/split_shuffled42.json`, 100 turns per task. Scores use the official comparison in
  `envs/spreadsheetbench/evaluate_with_official.py` (saved cell values, no formula recalculation).
- **ALFWorld**: distillation on the 57 tasks of `envs/alfworld/data/alfworld_trainval_items.json`, evaluation on the 134
  tasks of `envs/alfworld/data/alfworld_test_items.json`, 50 steps per episode.
- **Chess**: distillation on the 100 puzzles of `envs/chess/data/lichess_puzzles/puzzles_train_cc100.json` (analyst items
  `envs/chess/data/chess_cc100_items.json`), evaluation on the 200 puzzles of `puzzles_eval_400_2000.json`.
- **Pipeline**: `dskill.analyst` (prompt selected by `--prompt`), lessons split round-robin into chunks (20 chunks of
  about 5 tasks for SpreadsheetBench, about 10 tasks per chunk for ALFWorld and chess), then
  `dskill.consolidate --no-refs --safe-translate --safe-apply --freq-dose` chunk by chunk.
- Reported values average a cell's documents (three unless noted) and their evaluation passes (usually two per document).

| Result | Value(s) | Code | Settings |
|---|---|---|---|
| T1a SpreadsheetBench, Qwen student / DeepSeek teacher | 28.0 / 79.3 | `envs.spreadsheetbench.run_baseline_t2s` | Student Qwen3.6-35B-A3B with the empty `assets/skeleton`; teacher DeepSeek-V4-Pro with `assets/skillopt_pkg` |
| T1a SpreadsheetBench, DeepSeek -> Qwen | 71.7 +/- 3.6 | `dskill.analyst --prompt spreadsheet`, `dskill.consolidate` | Starting document `assets/skeleton_v2`; teacher traces from DeepSeek-V4-Pro with `skillopt_pkg` |
| T1a SpreadsheetBench, Luna student / DeepSeek -> Luna | 25.3 / 73.3 | same, plus `envs.spreadsheetbench.native_tools` | GPT-5.6 Luna with `HD_NATIVE_TOOLS=1`; starting document `assets/skeleton_v3_critical` |
| T1a SpreadsheetBench, Terra teacher / Terra -> Qwen / Terra -> Luna | 78.5 / 73.1 / 69.7 | same, plus `dskill.llm.codex_proxy` | GPT-5.6 Terra with `assets/skillopt_pkg_proc` and `HD_NATIVE_TOOLS=1`; the analyst reads the teacher traces as logged; starting document `assets/skeleton_v2` |
| T1a ALFWorld, Qwen student / DeepSeek teacher | 59.0 / 88.4 | `envs.alfworld.run_alfworld` | Teacher skill `envs/alfworld/assets/skillopt_teacher/SKILL.md` |
| T1a ALFWorld, DeepSeek -> Qwen / DeepSeek -> Luna | 84.2 / 83.3 | `dskill.analyst --prompt alfworld`, `dskill.consolidate --domain-alf` | Starting document `assets/skeleton_alfworld`; teacher traces staged with the skill block and reasoning removed |
| T1a ALFWorld, Terra teacher / Terra -> Qwen / Terra -> Luna | 84.7 / 83.1 / 83.1 | same, plus `dskill.llm.codex_proxy`, `envs.alfworld.strip_teacher_traces` | Teacher traces staged with `strip_teacher_traces` |
| T1b chess, Haiku -> Qwen (student / D-Skill / teacher) | 24.8 / 39.0 +/- 3.5 / 41.0 | `envs.chess.run_puzzles`, `envs.chess.chess_query`, `dskill.analyst --prompt chess_commit_check`, `dskill.consolidate --domain-chess`, `dskill.repair_sections` | `--tools 10` with `HD_TASK_EXTRA` = `envs/chess/assets/tool_trust.md`; Claude Haiku 4.5 teacher; Claude Sonnet 5 analyst and consolidator through `dskill.llm.claude_proxy`; starting document `assets/skeleton_chess_v5`; `repair_sections` after any chunk that leaves duplicate section titles |
| T1b chess, Sonnet -> Haiku (D-Skill / teacher / student) | 52.5 +/- 1.1 / 56.2 / 41.2 | `envs.chess.run_agent_chess`, `envs.chess.chess_mcp`, `envs.chess.cc_trace_convert`, `envs.chess.redact_verdicts`, `dskill.analyst --prompt chess_fallible_verify`, `dskill.consolidate --domain-chess` | Claude Code harness; the analyst reads the staged traces with the play tool's final verdict removed (`redact_verdicts`); Claude Sonnet 5 analyst and consolidator through `dskill.llm.claude_proxy`; starting document `assets/skeleton_chess_v3`. One of the two teacher passes ran on `puzzles_eval_v1b5.json` and is scored on its puzzles rated below 2000, which are the 200 eval puzzles. The student value is Claude Haiku 4.5 on the same Claude Code harness |
| T1b estimated Elo | e.g. 1286 +/- 21 | `envs.chess.estimate_elo` | Per pass, a logistic fit of solve rate on puzzle rating, `p = sigmoid(a + b (r - 1200) / 400)`; the estimate is the 50% crossing `1200 - 400 a / b`, averaged over passes |
| T2 trace source (teacher only / student only) | 56.3 (Qwen) / 63.5 (Luna); 47.7 (Qwen) / 49.8 (Luna) | `dskill.analyst --prompt spreadsheet_teacher_only` / `spreadsheet_student_only`, `dskill.consolidate` | SpreadsheetBench |
| T3 chess analyst x consolidator | sq 34.3 / qs 31.1 / qq 32.6 (ss = the T1b 39.0) | as T1b Haiku -> Qwen | s = Claude Sonnet 5 through `dskill.llm.claude_proxy`, q = Qwen3.6-35B-A3B; `repair_sections` changed five chunks of the qs documents |
| T4 SkillOpt / D-Skill lessons with the SkillOpt backend | 29.6 +/- 1.4 / 36.9 +/- 5.7 | `third_party/skillopt` (SkillOpt 0f76ab4 plus the overlay) | `configs/chess_hd/default.yaml` / `lessons_A.yaml`, `data/chess_split60`, seeds 42-44; plain SkillOpt is evaluated at its epoch-1 skill (`skill_v0003`); see `third_party/skillopt/README.md` |
| T5 Trace2Skill baselines | self-authored 33.0 / 31.1; cross-model 34.2 / 37.0; writer swap 36.0 / 46.2 (Qwen / Luna) | `third_party/trace2skill` (`skill_evolver`, `analysis/run_success_analysis_llm.py`, `analysis/run_error_analysis.py`) | SpreadsheetBench; starting document `assets/skeleton_v2` |
| Fig 3, Tables 8-9 SFT vs D-Skill | see figure | `dskill.sft.{export_rollouts,build_data,train}`, `dskill.llm.tinker_proxy` | LoRA SFT of the student on the teacher's rollouts via Tinker; checkpoints evaluated with the same harnesses; D-Skill curves use the documents in `paper_skills/figure3_curves/` |
| Appendix A puzzle sets and tools | eval 200, distill 100, split 60/40 | `envs.chess.chess_query` | `envs/chess/data/lichess_puzzles/`; SkillOpt split `third_party/skillopt/overlay/data/chess_split60` |
| Appendix B prompts | `v2a`, `a0`, `c0p`, `c0ph` | `dskill.analyst` | Selected with `--prompt`. The paper's names map to `v2a` = `spreadsheet`, `a0` = `alfworld`, `c0ph` = `chess_commit_check`; `c0p` is `PROMPT_CHESS` in `dskill/analyst.py`, the base of both chess prompts (not selectable on its own). Table 2 also uses `v2t` = `spreadsheet_teacher_only` and `v2s` = `spreadsheet_student_only`. The Table 1b Sonnet -> Haiku documents use `chess_fallible_verify`: `c0p` plus a verification-before-commit dimension, with the expert framed as fallible |
