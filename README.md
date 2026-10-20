# D-Skill

D-Skill distills a stronger teacher agent into a skill document for a cheaper student agent, with no weight
updates. A **difference analyst** compares teacher and student traces on the same tasks and writes lessons about
where their behavior diverges; a **consolidator** merges those lessons into a `SKILL.md` that the student reads in
context. Benchmarks: SpreadsheetBench-Verified, ALFWorld, and chess puzzles.

## Layout

| Path | Contents |
|---|---|
| `dskill/` | The method: `analyst`, `make_chunks`, `consolidate` (+ the `consolidator/` edit guards), LLM clients and proxies (`llm/`), SFT comparison (`sft/`) |
| `envs/{spreadsheetbench,alfworld,chess}/` | Benchmark harnesses and official scorers, starting and teacher skill documents (`assets/`), task sets (`data/`); `envs/alfworld/vendor/` is SkillOpt's ALFWorld runtime |
| `experiments/` | `PROVENANCE.md`: the code and settings behind each table and figure of the paper |
| `paper_skills/` | The skill documents behind every result in the paper, as evaluated, with a manifest |
| `third_party/trace2skill/` | Upstream [Trace2Skill](https://github.com/Qwen-Applications/Trace2Skill) code: the LLM client, the skill evolver the consolidator builds on, and the Trace2Skill baseline |
| `third_party/skillopt/` | Adapters for the SkillOpt baseline (Table 4) |

## Setup

```bash
python3.11 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp openai.env.example openai.env && chmod 600 openai.env    # API keys and provider settings (gitignored)
source openai.env                                           # after filling in your keys; in every new shell
export ALFWORLD_DATA=$PWD/envs/alfworld/data/alfworld_data  # ALFWorld only
alfworld-download --data-dir $ALFWORLD_DATA                 # ALFWorld only, once
```

Keep this environment active when evaluating: the SpreadsheetBench agent runs its scripts with the `python3` on your
PATH, and they import openpyxl and pandas.

Claude and Codex models run through their CLIs (`claude`, `codex`) behind an OpenAI-compatible proxy, for example
`python -m dskill.llm.claude_proxy --port 9990 --claude-model claude-sonnet-5 --effort medium` or
`python -m dskill.llm.codex_proxy --port 9993 --model gpt-5.6-terra --effort medium`. Point a run at a proxy with
`HD_PROVIDER=openai OPENAI_API_KEY=EMPTY OPENAI_BASE_URL=http://127.0.0.1:<port>/v1`.

GPT models use your OpenAI key (`HD_PROVIDER=openai`, the default). DeepSeek-V4-Pro and Qwen3.6-35B-A3B run through
OpenRouter: set `OPENROUTER_API_KEY` and prefix the command with `HD_PROVIDER=openrouter HD_OPENROUTER_PREFIX=deepseek/`
(or `qwen/`); model names stay bare, e.g. `--model deepseek-v4-pro` or `--model qwen3.6-35b-a3b`.

Good to know:
- OpenRouter requests from the analyst, the consolidator and the SpreadsheetBench runner carry a provider preference
  (`dskill.llm.pin_provider`): the model vendor's own host first, then hosts by declared precision, never fp4/int4.
  `HD_OR_PROVIDER=<host>` pins a single host.
- The Claude and Codex proxies listen on 127.0.0.1 without authentication, so any local process can use your
  subscription while one runs. `claude -p` runs under your Claude Code profile, with its settings and hooks
  (`HD_CC_CONFIG_DIR` selects another profile). The Codex proxy copies `~/.codex/auth.json` into a temporary
  `CODEX_HOME` that it deletes on exit.
- `dskill.sft.train` logs to W&B whenever `WANDB_API_KEY` or `WANDB_MODE` is set; `HD_WANDB=0` turns it off.

## Evaluate the paper's skills

`paper_skills/<table>/<cell>/<rN|sNN>/` holds each evaluated `SKILL.md`, and `paper_skills/manifest.tsv` gives its
table and cell. Reported values average a cell's documents and their evaluation passes;
`experiments/PROVENANCE.md` lists the code and settings behind each value. The paper's settings:

```bash
# SpreadsheetBench: the 200 eval tasks of split_shuffled42.json (the runner's default --split eval), 100 turns.
# GPT-5.6 students also set HD_NATIVE_TOOLS=1 (Luna: --effort medium).
EV=$(python -c "import json; print(','.join(json.load(open('envs/spreadsheetbench/assets/split_shuffled42.json'))['eval']))")
python -m envs.spreadsheetbench.run_baseline_t2s --model <student> --max-turns 100 --ids "$EV" \
  --skills-dir paper_skills/table1_main/spreadsheetbench/deepseek_to_qwen/r1 --run-tag <tag>
python envs/spreadsheetbench/evaluate_with_official.py \
  --data_path envs/spreadsheetbench/data/spreadsheetbench_verified/spreadsheetbench_verified_400 \
  --output_dir runs/<run>/outputs --ids "$EV"

# ALFWorld: the 134 test tasks, 50 steps
python -m envs.alfworld.run_alfworld --model <student> --items envs/alfworld/data/alfworld_test_items.json \
  --max-steps 50 --skill-file paper_skills/table1_main/alfworld/deepseek_to_qwen/r1/alf/SKILL.md --run-tag <tag>

# Chess, puzzle harness (Haiku -> Qwen; Tables 1b, 3, 4): 200 puzzles, 10 tool calls per move, tool-trust line
HD_TASK_EXTRA="$(cat envs/chess/assets/tool_trust.md)" python -m envs.chess.run_puzzles --model <student> \
  --tools 10 --puzzles envs/chess/data/lichess_puzzles/puzzles_eval_400_2000.json \
  --skill-file paper_skills/table1_main/chess/haiku_to_qwen/r1/chess/SKILL.md --run-tag <tag>

# Chess, Claude Code harness (Sonnet -> Haiku; Table 1b)
python -m envs.chess.run_agent_chess --harness cc --model claude-haiku-4-5 --effort medium --timeout 2400 \
  --puzzles envs/chess/data/lichess_puzzles/puzzles_eval_400_2000.json \
  --skill-file paper_skills/table1_main/chess/sonnet_to_haiku/r1/chess/SKILL.md --run-tag <tag>
```

The SpreadsheetBench runner repairs a common parse failure in the agent's JSON actions (a missing closing brace) by
default; `HD_ROBUST_PARSE=0` uses upstream's parser. The Claude Code harness runs `claude -p` under your Claude Code
profile and saves each episode's session in `~/.claude/projects`, which `envs/chess/cc_trace_convert.py` reads to build
traces; `HD_CC_CONFIG_DIR` selects another profile. Each run writes a folder under `runs/` (gitignored) with a
`results.jsonl`. All reported scores use each benchmark's
official scoring: the official SpreadsheetBench evaluation (saved cell values, no formula recalculation), the
ALFWorld environment's success signal, and the puzzle's solution line for chess.

## Distill a skill

The paper's traces and analyses are not released; distilling again regenerates them. First run the teacher and the
student with the runners above on the training tasks: SpreadsheetBench `split_shuffled42.json` `distill` ids
(`--split distill`; 99 of its 200 `train` ids), ALFWorld `envs/alfworld/data/alfworld_trainval_items.json`, chess
`envs/chess/data/lichess_puzzles/puzzles_train_cc100.json`.
Teachers carry a skill: `envs/spreadsheetbench/assets/skillopt_pkg` (DeepSeek) or `skillopt_pkg_proc` (Terra), and
`envs/alfworld/assets/skillopt_teacher/SKILL.md`; the chess teachers run without one. SpreadsheetBench students run
with the empty `envs/spreadsheetbench/assets/skeleton`. For ALFWorld, stage the teacher traces with
`python -m envs.alfworld.strip_teacher_traces <teacher_run>/logs <staged_dir>`, which removes the skill block and the
reasoning, and give the staged folder to the analyst as `--expert_logs`. For chess Sonnet -> Haiku, convert both Claude
Code runs with `envs.chess.cc_trace_convert`, then remove the play tool's final verdict from both trace folders with
`python -m envs.chess.redact_verdicts <staged_dir> <redacted_dir>` and give the redacted folders to the analyst.

`--prompt` selects the analyst prompt: `spreadsheet` for SpreadsheetBench (`spreadsheet_teacher_only` and
`spreadsheet_student_only` are the Table 2 variants), `alfworld` for ALFWorld, and `chess_fallible_verify`
(Sonnet -> Haiku) or `chess_commit_check` (Haiku -> Qwen) for chess. ALFWorld also passes
`--items_json envs/alfworld/data/alfworld_trainval_items.json`, and chess passes
`--items_json envs/chess/data/chess_cc100_items.json`.

```bash
# SpreadsheetBench training tasks: the 99 distill ids
IDS=$(python -c "import json; print(','.join(json.load(open('envs/spreadsheetbench/assets/split_shuffled42.json'))['distill']))")
# 1. analyst: one call per (teacher, student) trace pair
HD_PROVIDER=openrouter HD_OPENROUTER_PREFIX=deepseek/ python -m dskill.analyst --prompt spreadsheet \
  --expert_logs <teacher_run>/logs --student_logs <student_run>/logs \
  --output_dir $OUT/analysis --instance_ids "$IDS" --model deepseek-v4-pro \
  --parsed_errors $OUT/analysis/parsed_errors.json --parsed_success $OUT/analysis/parsed_success.json
# 2. split the lessons into chunks, then consolidate chunk by chunk into a copy of the starting document
python -m dskill.make_chunks --src $OUT/analysis --dst $CHUNKS --seed 0 --per-chunk 5
mkdir -p $RUN/skill && cp -r envs/spreadsheetbench/assets/skeleton_v2/xlsx $RUN/skill/
K=$(ls -d $CHUNKS/batch_* | wc -l)
for k in $(seq 1 $K); do
  B=$CHUNKS/batch_$(printf %03d $k)
  HD_PROVIDER=openrouter OPENAI_BASE_URL=https://openrouter.ai/api/v1 OPENAI_API_KEY=$OPENROUTER_API_KEY \
  python -m dskill.consolidate --no-refs --safe-translate --safe-apply --freq-dose \
    [--domain-alf | --domain-chess] --max-skill-lines 1200 \
    --error-json $B/parsed_errors.json --success-json $B/parsed_success.json \
    --skill-dir $RUN/skill/xlsx --model deepseek/deepseek-v4-pro --seed $((SEED + k))
done
```

`dskill.make_chunks` shuffles the task ids that have lessons with `--seed` and deals them round-robin into chunks of
about `--per-chunk` tasks: 5 for SpreadsheetBench (20 chunks over the 99 tasks), 10 for ALFWorld and chess. Use a
different seed for each replicate document. For the Haiku -> Qwen chess documents, the paper ran
`python -m dskill.repair_sections $RUN/skill/chess/SKILL.md` after any chunk that left two sections with the same
title.

Starting documents are in `envs/<benchmark>/assets/`: `skeleton_v2` for SpreadsheetBench (`skeleton_v3_critical` for
DeepSeek -> Luna), `skeleton_alfworld`, and `skeleton_chess_v5` (Haiku -> Qwen) or `skeleton_chess_v3`
(Sonnet -> Haiku). Use `--max-skill-lines 1200` for SpreadsheetBench (plus `--data-path` to the Verified-400 data)
and 900 for ALFWorld and chess.

## License

MIT License (see `LICENSE`). Bundled third-party code and data keep their own licenses, listed in `NOTICE`.
Built on [Trace2Skill](https://arxiv.org/abs/2603.25158) (Ni et al., 2026).
