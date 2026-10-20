# Trace2Skill (vendored)

Upstream code from [Trace2Skill](https://github.com/Qwen-Applications/Trace2Skill), commit
[`3d0b52a14`](https://github.com/Qwen-Applications/Trace2Skill/commit/3d0b52a140f002a512930252b613c49048f7d5ac).
D-Skill imports it at runtime: `import dskill` (or `import dskill.<module>`)
puts this directory and its `src/` on `sys.path`, so the modules import under their upstream names.

| Path | Used by |
|---|---|
| `src/react_agent/` | The LLM client (`OpenAIClient`, `Message`) behind the analyst, the consolidator and the SpreadsheetBench, ALFWorld and chess-puzzle harnesses, and the ReAct loop of the SpreadsheetBench harness (the Claude Code chess harness does not use it) |
| `skill_evolver/` | `dskill.consolidate`, which patches it at runtime (see `dskill/consolidator/`); run unpatched, it is the Trace2Skill baseline of Table 5 |
| `analysis/parse_{error,success}_analysis_outputs.py` | `dskill.analyst`, to turn the analyst's reports into `parsed_errors.json` / `parsed_success.json` |
| other `analysis/` scripts | The Trace2Skill baseline's own trace analysis (Table 5); `run_error_analysis_llm.py` is not used |
| `skills/skill-creator/scripts/quick_validate.py` | `skill_evolver`, which validates every `SKILL.md` with it and refuses to run without it |

## Local changes

Each modified upstream file starts with a one-line attribution header (after any shebang line). The other changes:

- `src/react_agent/models.py`, in `OpenAIClient`:
  - An HTTP-200 reply with no `choices` (how some gateways report a provider error) raises and is retried.
  - Every retried error is printed to stderr (its first 160 characters).
  - When a request fails with an error that names a parameter as unsupported, or that mentions `temperature`, `top_p`
    or `top_k`, the client drops that parameter for the rest of its life and retries at once. A dropped `stop` is
    emulated client-side: the reply is cut at the first line that starts with a stop sequence, and again after the
    first complete `Action:` JSON, so a reply carries at most one action.
  - `HD_LLM_TIMEOUT` (seconds) overrides the request timeout.
  - Token usage is kept per client (`usage_totals`) and per call (`last_usage`). With `HD_USAGE_LOG=<path>`, each
    response appends one JSON line to that file: token counts, the `HD_USAGE_TAG` label and, on OpenRouter, the
    billed cost. On an OpenRouter base URL it also asks for the cost by adding `usage: {include: true}` to the request
    body. The log holds no prompts or keys.
  - Reasoning text is also read from OpenRouter's `reasoning` field.
- `src/react_agent/models.py`, cache and logging: the disk reply cache of `OpenAIClient` and `ApiChatClient` is off by
  default. It is on only with `use_cache=True` or an explicit `cache_path` (the baseline runners' `--cache-path`).
  Upstream cached replies under `~/.cache` by default. `OpenAIClient` keys that cache on the model and messages only;
  `ApiChatClient`'s key also includes the request parameters. `ApiChatClient` logs its first
  request with `access_key`, `user_id` and `quota_id` replaced by `***`.
- `src/react_agent/agent.py`: with `HD_LOG_REASONING=1`, the ReAct loop also fetches the reasoning text and stores it
  on the step for the history logger. The reply the agent parses and acts on is unchanged.
- `skill_evolver/`: the SpreadsheetBench support import points at `envs.spreadsheetbench`, and `QUICK_VALIDATE_SCRIPT`
  is resolved from this directory instead of the working directory. `SkillEvolver.apply_edits`, which the sequential
  and the parallel evolver both use, skips any edit whose path is absolute, has a `..` component, or resolves
  (symlinks followed) outside the skill directory. It logs a warning and writes or deletes nothing for that edit.
- `analysis/`: imports point at `envs.spreadsheetbench`, and `run_error_analysis.py` adds the D-Skill repo root to
  `sys.path`. `evaluate_output.py` scores answer positions differently. A column-only range such as `A:G` is compared
  on rows 1-5 only. Sheet-qualified ranges (`Sheet1!A1:B2`) are found with a pattern instead of a comma split. If a
  position mixes qualified and unqualified ranges, only the qualified ones are kept. This affects only the baseline
  analyst's pass check, not the D-Skill evaluation.
- `skills/skill-creator/scripts/quick_validate.py` is not part of upstream Trace2Skill: it is the validator from
  Anthropic's skill-creator skill, which upstream expects to find at `skills/`.

Not kept here: `released_skills/` and `gen_config/` (unused) and upstream's `README.md` and `.gitignore`. Upstream's
SpreadsheetBench files (`evaluate_with_official.py`, `spreadsheetbench_support.py`, `spreadsheet_agent/` and
`data/`) live in `envs/spreadsheetbench/`. Upstream's `run_spreadsheetbench.py`, `analyze_results.py` and
`spreadsheet_agent/skills/` are not kept: no paper result uses them, and the `xlsx` skill there is Anthropic's
proprietary skill.

The upstream repository has no top-level license file at this commit. The license grant is in its `README.md`, lines
355-357 ("This project is released under the Apache License 2.0";
[README.md#L355-L357](https://github.com/Qwen-Applications/Trace2Skill/blob/3d0b52a140f002a512930252b613c49048f7d5ac/README.md#L355-L357)).
`LICENSE` here is the standard Apache-2.0 text, added for that grant.

## Running the Trace2Skill baseline directly

From the D-Skill repo root (from another directory, use
`PYTHONPATH=<repo>/third_party/trace2skill:<repo>`, since the evolver also imports `envs`):

```bash
PYTHONPATH=third_party/trace2skill python -m skill_evolver.run_parallel_combined_skill_evolution --help
python third_party/trace2skill/analysis/run_success_analysis_llm.py --help
python third_party/trace2skill/analysis/run_error_analysis.py --help
```

The evolution runners cache LLM replies only when given `--cache-path`. The analysis scripts do not cache.
