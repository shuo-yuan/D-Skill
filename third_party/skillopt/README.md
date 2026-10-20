# SkillOpt additions (Table 4 baseline)

Table 4 (SkillOpt on chess) runs a checkout of [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt) at commit
`0f76ab4` with the files here added:

| Path | Contents |
|---|---|
| `overlay/skillopt/envs/chess_hd/` | `adapter.py` runs SkillOpt's rollouts through D-Skill's chess puzzle harness (`envs.chess.run_puzzles`). `lesson_adapter.py` is the "D-Skill lessons with SkillOpt backend" row: its analyst reads D-Skill lessons instead of trajectories. Also the analyst prompts and the starting skill body (the body of `envs/chess/assets/skeleton_chess_v5`). |
| `overlay/skillopt/envs/spreadsheetbench_hd/adapter.py` | Harness settings and helpers that the chess adapter imports. Its SpreadsheetBench adapter class is not used in the paper. |
| `overlay/configs/chess_hd/` | `default.yaml` (plain SkillOpt), `lessons.yaml` and `lessons_A.yaml` (the lessons row). |
| `overlay/data/chess_split60/` | The 60/40 train/val split of the 100 distillation puzzles (stratified by rating band, seed 42) and the 200-puzzle test set. |
| `skillopt_local_changes.patch` | Registers the two environments (`chess_hd`, `chess_hd_lessons`) in `scripts/train.py`. |

Set up a checkout and train (seeds 42, 43, 44 in the paper):

```bash
git clone https://github.com/microsoft/SkillOpt.git && cd SkillOpt && git checkout 0f76ab4
git apply <D-Skill>/third_party/skillopt/skillopt_local_changes.patch
cp -r <D-Skill>/third_party/skillopt/overlay/. .
export DSKILL_ROOT=<D-Skill>    # DSKILL_PYTHON is optional (default: the current interpreter)
# also export the optimizer endpoint (see "Optimizer endpoint" below)
python scripts/train.py --config configs/chess_hd/default.yaml --out_root outputs/chess_s42 --seed 42
python scripts/train.py --config configs/chess_hd/lessons_A.yaml --out_root outputs/chessLA_s42 --seed 42
```

Notes:
- The adapters read API keys from `$DSKILL_ENV_FILE`, or `openai.env` in the D-Skill checkout.
- The lessons row reads two D-Skill run outputs, named in `lessons.yaml` relative to `DSKILL_ROOT`: the Haiku->Qwen
  chess analysis (`runs/cqHQ3T/analysis`) and the student's skill-free results on the distillation puzzles
  (`runs/puzzles_qwen3.6-35b-a3b_qwtrT_tr100/results.jsonl`). Both come from the Table 1b Haiku->Qwen pipeline; see
  `experiments/PROVENANCE.md`.
- The plain SkillOpt row evaluates each run's epoch-1 skill (`skills/skill_v0003.md`); the lessons runs train for one
  epoch. The evaluated documents are in `paper_skills/table4_skillopt_chess/`, scored with `envs.chess.run_puzzles`.

## Optimizer endpoint

All three configs set `optimizer_backend: openai_compatible`. SkillOpt then sends every optimizer call to an
OpenAI-compatible `/chat/completions` endpoint, set by these environment variables:

```bash
export OPTIMIZER_OPENAI_COMPATIBLE_BASE_URL=<base URL, ending in /v1>
export OPTIMIZER_OPENAI_COMPATIBLE_API_KEY=<key>          # a local proxy accepts any value
export OPTIMIZER_OPENAI_COMPATIBLE_MAX_TOKENS=64000       # SkillOpt's default (8000) caps every call
export OPTIMIZER_OPENAI_COMPATIBLE_TIMEOUT_SECONDS=1800   # SkillOpt's default is 300
```

The model name comes from `model.optimizer` in the YAML (`claude-sonnet-5`). It overrides
`OPTIMIZER_OPENAI_COMPATIBLE_MODEL`, so pick another model with `--cfg-options model.optimizer=<model>`. SkillOpt
also reads `OPTIMIZER_OPENAI_COMPATIBLE_TEMPERATURE`, and falls back to `OPENAI_COMPATIBLE_*` when a role-specific
variable is unset. This backend does not forward `reasoning_effort`.

The paper's optimizer was Claude Sonnet 5 at medium effort, served by D-Skill's `claude -p` proxy. The proxy needs a
logged-in `claude` CLI and must keep running during training:

```bash
# in a separate shell, in the D-Skill checkout
python -m dskill.llm.claude_proxy --port 9990 --claude-model claude-sonnet-5 --effort medium
# in the training shell
export OPTIMIZER_OPENAI_COMPATIBLE_BASE_URL=http://127.0.0.1:9990/v1
export OPTIMIZER_OPENAI_COMPATIBLE_API_KEY=EMPTY
export OPTIMIZER_OPENAI_COMPATIBLE_MODEL=claude-sonnet-5
export OPTIMIZER_OPENAI_COMPATIBLE_MAX_TOKENS=64000
export OPTIMIZER_OPENAI_COMPATIBLE_TIMEOUT_SECONDS=1800
```

The proxy answers every request with its `--claude-model`, whatever model the request names.

The student does not use SkillOpt's target backend. The adapters run it in D-Skill's chess harness: Qwen3.6-35B-A3B
on OpenRouter (provider AkashML), with `OPENROUTER_API_KEY` from `openai.env`. The paper still set
`TARGET_OPENAI_COMPATIBLE_BASE_URL=https://openrouter.ai/api/v1`, `TARGET_OPENAI_COMPATIBLE_API_KEY=$OPENROUTER_API_KEY`
and `TARGET_OPENAI_COMPATIBLE_MODEL=qwen/qwen3.6-35b-a3b`, but nothing calls them.
