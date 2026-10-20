"""Evolver entry point: upstream Trace2Skill plus the D-Skill options.

Drop-in replacement for upstream
    python -m skill_evolver.run_parallel_combined_skill_evolution <args>
The D-Skill flags below are stripped from argv, the vendored skill_evolver
modules are patched for them, and upstream main() runs with the rest.

    python -m dskill.consolidate --no-refs --max-skill-lines 400 \
        --error-json ... --success-json ... --skill-dir ... [upstream args]

    --no-refs          single-file skill: compress SKILL.md in place, never
                       create references/*.md, drop edits to other files
    --safe-translate   TRANSLATE guard (dskill/consolidator/safe_translate.py)
    --safe-apply       APPLY guard (dskill/consolidator/safe_apply.py)
    --freq-dose        dose-preservation rule on the merge prompts
    --domain-alf | --domain-chess   retarget the spreadsheet prompt text

Always installed: dskill.llm.pin_provider and a None-guard on
ParallelSkillEvolver._extract_reference_paths_from_text.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


# --no-refs: single-file skill mode. The student sees only SKILL.md, so the
# upstream prompts are rewritten to compress SKILL.md in place instead of
# moving content into references/*.md, and an apply-phase lint drops every
# edit that does not target SKILL.md.

_COMPRESS_WARNING = """**WARNING**: SKILL.md is at or near its line limit. You MUST now COMPRESS IT IN PLACE.

KEEP THE DOCUMENT SKELETON INTACT — compress WITHIN it, never around it:
- Keep the YAML frontmatter exactly as-is (`name`, `description`). Never alter or duplicate it.
- Keep every existing section header VERBATIM — same wording, same level, same order.
  Do NOT rename, merge, split, or reorder sections. Later edits target these headers by
  exact text; renaming one silently breaks every future edit aimed at it.
- Compress the CONTENT inside each section. Remove a section only if compression leaves
  it genuinely empty.
- Never introduce placeholder sections (e.g. "## New Section") or duplicate an existing header.

How to compress:
- Merge duplicate or overlapping rules into ONE authoritative statement.
- Shorten verbose prose: keep the actionable instruction and any concrete runtime check, drop the commentary.
- Delete the least valuable material (restated warnings, redundant examples, near-duplicate snippets).
- PRESERVE every distinct actionable rule, including narrow ones (unusual value types,
  edge-case APIs, format traps) — those are the highest-value content. Compress the
  repeated general advice instead. A one-line version of a specific rule is fine; deleting
  it is not.

Do NOT create reference files and do NOT link to them. SKILL.md is the ONLY file the
agent will ever read; anything moved out of SKILL.md is lost. Prefer `replace_in_section`
edits that shorten a section in place."""

# (old, new) substitutions, applied to every prompt string
_SUBS: list[tuple[str, str]] = [
    # file-level ops: also blocked by the apply lint; removing them from the
    # prompts keeps the model from spending edits on them
    ("""- "create": create a new file (file + content)
- "delete_file": delete a file""",
     """(the skill is a single file; there are no file-level ops)"""),

    ("Supported operations: insert_after, insert_before, append_to_section, "
     "replace_in_section, add_section, delete_section, create, delete_file",
     "Supported operations: insert_after, insert_before, append_to_section, "
     "replace_in_section, add_section, delete_section"),

    ("- Use only supported ops: insert_after, insert_before, "
     "append_to_section, replace_in_section, add_section, delete_section, "
     "create, delete_file",
     "- Use only supported ops: insert_after, insert_before, "
     "append_to_section, replace_in_section, add_section, delete_section"),

    ("create, delete_file.", "and nothing else."),

    ("For new files, use `create`, never `create_file`.",
     "There are no new files: every edit targets SKILL.md."),

    ("6. If a new references/*.md file is proposed, keep the create and its SKILL.md",
     "6. Reference files are not used; drop any patch that proposes one, and keep its SKILL.md"),

    ("**WARNING**: SKILL.md is approaching the line limit. Consider "
     "extracting detailed content into references/ files.",
     _COMPRESS_WARNING),

    ("""- SKILL.md must remain under 500 lines
- Each `references/*.md` file must remain under 300 lines
- If SKILL.md would exceed the line limit, extract self-contained subsections into separate `references/*.md` files and replace the moved content with a brief summary and a `references/filename.md` link""",
     """- SKILL.md must remain under {MAXLINES} lines
- The skill is a SINGLE FILE: never create `references/*.md` files
- If SKILL.md exceeds the line limit, COMPRESS IT IN PLACE: merge redundant or
  overlapping rules into one statement, shorten explanations, and drop the least
  valuable details until it fits. Preserve every distinct actionable rule.
  Never relocate content into another file -- only SKILL.md is ever read.
- When compressing, keep the skeleton intact: preserve the YAML frontmatter exactly
  and keep every section header verbatim (same wording, level and order). Compress the
  content inside sections; never rename, merge or reorder headers, and never add
  placeholder sections."""),

    ("""- **references/*.md** — optional reference files for detailed or specialized
  guidance, loaded on demand when the agent encounters a link in SKILL.md
""", ""),

    ("4. SKILL.md must remain under 500 lines",
     "4. SKILL.md must remain under {MAXLINES} lines"),
    ("5. Each reference file should be under 300 lines",
     "5. The skill is a SINGLE FILE. Never create reference files. When SKILL.md "
     "nears the limit, compress it in place (merge duplicate rules, shorten "
     "prose, drop the least valuable details)"),

    ("""### Strategy 3: Organize Around Reusable Patterns
Keep SKILL.md focused on the minimum workflow that both avoids common failures
and preserves proven wins. Move detailed variants into references when helpful:
- SKILL.md: critical workflow, warnings, validation checkpoints, links to references
- references/*.md: fuller examples, edge cases, operation-specific working patterns

Rules:
- Reference files must be linked from SKILL.md with a clear description of when to read them
- Keep references one level deep (no references from within references)
- Each reference file should have a table of contents if >100 lines
- Name files descriptively: references/formula-validation-patterns.md, not references/ref1.md""",
     """### Strategy 3: Organize Within a Single File
SKILL.md is the ONLY file the agent ever reads. Keep everything in it, and keep it
dense: critical workflow, warnings, validation checkpoints, and the concrete
patterns worth reusing.

Rules:
- NEVER create reference files and never link to them. Extracted content is lost.
- Group related guidance under clear section headings so it is easy to scan.
- When the file nears its line limit, compress in place: merge overlapping rules
  into one authoritative statement, shorten explanations to the actionable core,
  and drop restated warnings and near-duplicate examples.
- Prefer one precise general rule over three overlapping specific ones."""),

    ('IMPORTANT — file creation rule: if you propose a "create" op for a new '
     'references/*.md file, you MUST also include an edit to SKILL.md (or the '
     'relevant parent file) that adds a link and a brief description of when to '
     'read the new file. Likewise, a "delete_file" op MUST be paired with an '
     'edit that removes the corresponding link from SKILL.md.',
     'IMPORTANT — single-file rule: the skill is SKILL.md and nothing else. NEVER '
     'propose a "create" op for a references/*.md file and never add links to '
     'reference files; that content would be invisible to the agent. If SKILL.md '
     'is near its line limit, propose edits that COMPRESS it (merge overlapping '
     'rules, shorten prose, delete redundant material) rather than edits that grow it.'),

    ('- "file": relative path within the skill folder (e.g. "SKILL.md",\n'
     '  "references/formula-patterns.md")',
     '- "file": always "SKILL.md" (the skill is a single file)'),
]

# merge-prompt rule 7 is a long block; replace by marker slice
_MERGE_START = '7. **Atomic create/link pairs**'
_MERGE_END = 'Likewise, "delete_file" and the edit that removes its SKILL.md link are a pair.'
_MERGE_NEW = """7. **Single-file rule**: the skill is SKILL.md and nothing else. DROP any edit that
   creates a references/*.md file and any edit that adds a link to one -- that content
   would be invisible to the agent. If the incoming patches would grow SKILL.md beyond
   its limit, prefer merged edits that COMPRESS existing content (combine overlapping
   rules, shorten prose) over edits that append new sections."""

_applied: set[int] = set()


def rewrite(text: str, maxlines: int) -> str:
    """Apply every single-file substitution to one prompt string."""
    if not isinstance(text, str) or len(text) < 40:
        return text
    out = text
    for i, (old, new) in enumerate(_SUBS):
        if old in out:
            out = out.replace(old, new.replace("{MAXLINES}", str(maxlines)))
            _applied.add(i)
    a, b = out.find(_MERGE_START), out.find(_MERGE_END)
    if a > 0 and b > a:
        out = out[:a] + _MERGE_NEW + "\n\n" + out[b + len(_MERGE_END):]
        _applied.add(len(_SUBS))
    return out


def install_noref(max_skill_lines: int = 400, strict: bool = True) -> None:
    """Enable single-file mode: prompt rewrites + reference-edit lint."""
    import skill_evolver.prompt_loader as pl
    from functools import lru_cache

    _orig = pl.load_prompt_template.__wrapped__       # bypass lru_cache

    @lru_cache(maxsize=None)
    def patched(key: str) -> str:
        return rewrite(_orig(key), max_skill_lines)

    patched.__wrapped__ = _orig
    pl.load_prompt_template.cache_clear()
    pl.load_prompt_template = patched

    # skill_evolver/__init__.py eagerly imports agent modules, so several
    # templates are already baked into module constants. Retrofit them.
    import skill_evolver                                  # noqa: F401
    import skill_evolver.parallel_success_evolving_agent  # noqa: F401
    import skill_evolver.success_evolving_agent           # noqa: F401
    n_const = 0
    for name, mod in list(sys.modules.items()):
        if not name.startswith("skill_evolver"):
            continue
        for attr in list(vars(mod)):
            if attr.startswith("__"):
                continue
            val = vars(mod).get(attr)
            if isinstance(val, str) and len(val) >= 40:
                new = rewrite(val, max_skill_lines)
                if new != val:
                    setattr(mod, attr, new)
                    n_const += 1

    # load the lazy templates now so unmatched substitutions fail at startup
    for key in ("skill_evolving_agent/size_warning",
                "success_evolving_agent/size_warning",
                "parallel_evolving_agent/verification_system_prompt",
                "parallel_evolving_agent/map_output_format"):
        patched(key)

    missing = [i for i in range(len(_SUBS) + 1) if i not in _applied]
    msg = (f"[noref] single-file mode ON (max_skill_lines={max_skill_lines}); "
           f"retrofitted {n_const} module constant(s); "
           f"{len(_applied)}/{len(_SUBS)+1} substitutions matched")
    print(msg, flush=True)
    if missing and strict:
        raise RuntimeError(
            f"[noref] substitutions never matched: {missing} — upstream "
            "prompt text changed; update the --no-refs section of "
            "dskill/consolidate.py")

    import skill_evolver.parallel_evolving_agent as pea

    # PatchEdit.content can arrive from model JSON as None or a non-str type,
    # which crashes several upstream call sites; coerce it on the class.
    try:
        _PE = pea.PatchEdit
        if not getattr(_PE, "_hd_content_guarded", False):
            _slot = "_hd_content"

            def _get(self):
                return getattr(self, _slot, "") or ""

            def _hd_coerce_content(v):
                if v is None or isinstance(v, str):
                    return v or ""
                if isinstance(v, dict):
                    for k in ("content", "text", "value"):
                        if isinstance(v.get(k), str):
                            return v[k]
                    return ""
                if isinstance(v, (list, tuple)):
                    return "\n".join(x for x in v if isinstance(x, str))
                return ""

            def _set(self, v):
                object.__setattr__(self, _slot, _hd_coerce_content(v))

            _PE.content = property(_get, _set)
            _PE._hd_content_guarded = True
            print("[noref] PatchEdit.content None-guard installed", flush=True)
    except Exception as _e:                                   # noqa: BLE001
        print(f"[noref] WARNING: could not install content guard: {_e}",
              flush=True)

    # apply-phase lint: only SKILL.md edits reach disk
    from dskill.consolidator import unsafe_path_reason

    _orig_apply = pea.ParallelSkillEvolver.run_apply_phase_programmatic

    def linted(self, skill_state, final_patch):
        edits = list(getattr(final_patch, "edits", []) or [])
        kept, dropped, stripped, rewrites = [], 0, 0, 0
        empty_sec = dup_sec = 0
        off_target = 0
        skill_dir = getattr(self, "skill_dir", None)
        for e in edits:
            f = getattr(e, "file", "") or ""
            op = getattr(e, "op", "") or ""
            # containment first: upstream writes skill_dir / file unchecked
            why = unsafe_path_reason(f, skill_dir)
            if why:
                off_target += 1
                print(f"[noref] lint: DROPPED {op or '?'} on {f!r}: {why}",
                      flush=True)
                continue
            # create/delete_file could only rewrite or delete SKILL.md or add a
            # stray file, and they bypass TRANSLATE's anchor checks
            if op in ("create", "delete_file"):
                rewrites += 1
                continue
            # upstream would apply any other target to an empty document and
            # write it to skill_dir / file (references/* are dropped below)
            if f != "SKILL.md" and not f.startswith("references/"):
                off_target += 1
                print(f"[noref] lint: DROPPED {op or '?'} on {f!r}: "
                      f"single-file mode only edits SKILL.md", flush=True)
                continue
            # add_section: drop empty ones (nothing can anchor into them) and
            # turn a duplicate of an existing header into an append, since a
            # second header would shadow the first.
            if op == "add_section":
                body = (getattr(e, "content", "") or "").strip()
                if not body:
                    empty_sec += 1
                    continue
                want = (getattr(e, "target_section", "") or "").strip()
                doc = (skill_state or {}).get(f or "SKILL.md", "") or ""
                if want and any(l.strip() == want for l in doc.splitlines()):
                    try:
                        e.op = "append_to_section"
                        dup_sec += 1
                    except Exception:                          # noqa: BLE001
                        pass

            if f.startswith("references/"):
                # no reference file exists in single-file mode
                dropped += 1
                continue
            # upstream crashes on content=None
            if getattr(e, "content", "") is None:
                e.content = ""
            c = getattr(e, "content", "") or ""
            if "references/" in c:
                # keep the rule, remove only the link line(s)
                lines = [l for l in c.splitlines() if "references/" not in l]
                new_c = "\n".join(lines).strip()
                if not new_c:
                    dropped += 1
                    continue
                e.content = new_c
                stripped += 1
            kept.append(e)
        if empty_sec or dup_sec:
            print(f"[noref] add_section hygiene: dropped {empty_sec} empty, "
                  f"redirected {dup_sec} duplicate-of-existing", flush=True)
            final_patch.edits = kept
        if dropped or stripped or rewrites:
            if rewrites:
                print(f"[noref] lint: BLOCKED {rewrites} file-level op(s) "
                      f"(create/delete_file) — not legitimate in "
                      f"single-file mode; they bypass TRANSLATE and the "
                      f"destruction guard", flush=True)
            if dropped or stripped:
                print(f"[noref] lint: dropped {dropped} reference edit(s), "
                      f"stripped links from {stripped}", flush=True)
            final_patch.edits = kept
        if off_target:
            final_patch.edits = kept
        return _orig_apply(self, skill_state, final_patch)

    pea.ParallelSkillEvolver.run_apply_phase_programmatic = linted


# --freq-dose: a rule that recurs across chunks may keep several placements
# instead of being merged into one statement. Patches every
# *MERGE_SYSTEM_PROMPT* constant and both size_warning templates; the MAP
# system prompt is not patched.

_DOSE_MERGE = """
DOSE PRESERVATION: duplicates are allowed. A rule stated at several
positions in the document is deliberate, not redundancy to clean up.
When merging or deduplicating you may SHORTEN the restatements, but keep
at least two placements; never collapse a repeated rule to a single
occurrence.
CODE BLOCKS: fenced code blocks survive merges VERBATIM -- never convert
a code block to a prose summary, never introduce placeholders into one.
Keep one canonical block per behavior; replace a block only with a
strictly more universal version of the same procedure."""

_COMPRESS_OLD = "into one authoritative statement"
_COMPRESS_NEW = ("into one authoritative statement per placement -- a rule "
                 "deliberately stated at several positions keeps at least "
                 "two of them (shorten the restatements rather than "
                 "deleting them)")

_installed = False


def install_freq_dose(pea, psa=None) -> None:
    """Add the dose rule to every merge prompt and the size_warning templates.

    pea, psa: the skill_evolver.parallel_evolving_agent and
    parallel_success_evolving_agent modules. Installs once per process.
    """
    global _installed
    if _installed:
        return

    n = 0
    mods = [pea] + ([psa] if psa is not None else [])
    for mod in mods:
        for name in dir(mod):
            if "MERGE_SYSTEM_PROMPT" not in name:
                continue
            v = getattr(mod, name, None)
            if not isinstance(v, str) or "DOSE PRESERVATION" in v:
                continue
            v2 = v
            if _COMPRESS_NEW not in v:
                v2 = v.replace(_COMPRESS_OLD, _COMPRESS_NEW)
            setattr(mod, name, v2 + "\n" + _DOSE_MERGE)
            n += 1

    # size_warning templates: loaded at call time, shown to MAP near the cap
    try:
        from skill_evolver import prompt_loader as _pl
        _lorig = _pl.load_prompt_template

        def _lpatched(key):
            t = _lorig(key)
            if isinstance(t, str) and "size_warning" in str(key) \
                    and "DOSE PRESERVATION" not in t:
                t = t.replace(
                    "into ONE authoritative statement.",
                    "into ONE authoritative statement per placement -- a "
                    "rule deliberately stated at several positions keeps "
                    "at least two of them (shorten the restatements "
                    "rather than deleting them).")
                t = t + "\n" + _DOSE_MERGE
            return t

        _lpatched.__wrapped__ = _lorig
        if hasattr(_lorig, "cache_clear"):
            _lorig.cache_clear()
        _pl.load_prompt_template = _lpatched
    except Exception as _e:                                    # noqa: BLE001
        print(f"[freq-dose] WARNING: size_warning patch failed: {_e}",
              flush=True)

    _installed = True
    print(f"[freq-dose] installed: MAP OFF (merge-side dose only); "
          f"merge clause appended to {n} merge prompt(s)", flush=True)


# The install order in main() is observable; keep it.
def main() -> None:
    # provider routing and serving-host logging (dskill.llm.pin_provider)
    from dskill.llm.pin_provider import install as _pin_install
    _pin_install()

    argv = sys.argv[1:]
    no_refs = "--no-refs" in argv
    safe_translate = "--safe-translate" in argv
    safe_apply = "--safe-apply" in argv
    freq_dose = "--freq-dose" in argv
    domain_alf = "--domain-alf" in argv
    domain_chess = "--domain-chess" in argv
    argv = [a for a in argv
            if a not in ("--no-refs", "--safe-translate", "--safe-apply",
                         "--freq-dose", "--domain-alf", "--domain-chess")]

    if os.environ.get("HD_PRECEDENCE") == "1":
        raise SystemExit("HD_PRECEDENCE=1 is no longer supported")

    # needed by the prompt rewrites, before any skill_evolver import
    maxlines = 500
    for i, a in enumerate(argv):
        if a == "--max-skill-lines" and i + 1 < len(argv):
            maxlines = int(argv[i + 1])
        elif a.startswith("--max-skill-lines="):
            maxlines = int(a.split("=", 1)[1])

    if no_refs:
        install_noref(max_skill_lines=maxlines)

    if domain_chess:
        # see envs/chess/chess_domain.py for the full retarget
        from envs.chess.chess_domain import install as _install_chess
        _install_chess()
        import skill_evolver.success_evolving_agent as _sue
        _OLDX = ("refine a spreadsheet\nskill folder so that agents "
                 "using it make fewer errors in the future")
        _NEWX = ("refine a chess move-selection\nskill document so "
                 "that agents using it choose better moves more often")
        _orig_rep_ch = _sue._replace_core_prompt_text

        def _rep_chess(base, *a, **k):
            try:
                out = _orig_rep_ch(base, *a, **k)
            except ValueError:
                out = _orig_rep_ch(base.replace(_NEWX, _OLDX), *a, **k)
            return out.replace("spreadsheet", "chess move-selection")

        _sue._replace_core_prompt_text = _rep_chess

    if domain_alf:
        import skill_evolver.skill_evolving_agent as _sea
        import skill_evolver.parallel_evolving_agent as _pea
        for _mod in (_sea, _pea):
            for _name in dir(_mod):
                _v = getattr(_mod, _name, None)
                if isinstance(_v, str) and "refine a spreadsheet" in _v:
                    setattr(_mod, _name, _v.replace(
                        "refine a spreadsheet\nskill folder so that "
                        "agents using it make fewer errors in the future",
                        "refine an embodied household-task agent\n"
                        "skill document so that agents using it complete "
                        "tasks more often"))
        # combined-success path: its prompt builder find-replaces the
        # ORIGINAL spreadsheet intro; retarget leniently at call time.
        import skill_evolver.success_evolving_agent as _sue
        _OLDC = ("refine a spreadsheet\nskill folder so that agents "
                 "using it make fewer errors in the future")
        _NEWC = ("refine an embodied household-task agent\nskill "
                 "document so that agents using it complete tasks "
                 "more often")
        _orig_rep = _sue._replace_core_prompt_text

        def _rep_alf(base, *a, **k):
            try:
                out = _orig_rep(base, *a, **k)
            except ValueError:
                out = _orig_rep(base.replace(_NEWC, _OLDC), *a, **k)
            return out.replace("spreadsheet", "ALFWorld household-task")

        _sue._replace_core_prompt_text = _rep_alf

    # always on: upstream regexes over edit.content, which can be None
    import skill_evolver.parallel_evolving_agent as _pea
    _orig_extract = _pea.ParallelSkillEvolver._extract_reference_paths_from_text

    def _safe_extract(text):
        return _orig_extract("" if text is None else text)

    _pea.ParallelSkillEvolver._extract_reference_paths_from_text = staticmethod(
        _safe_extract)

    if safe_apply:
        from dskill.consolidator.safe_apply import install as _install_apply
        _install_apply(_pea)

    if safe_translate:
        from dskill.consolidator.safe_translate import install as _install_safe
        _install_safe(_pea.ParallelSkillEvolver,
                      _pea._apply_patch_edit_to_content)

    if freq_dose:
        import skill_evolver.parallel_success_evolving_agent as _psa
        install_freq_dose(_pea, _psa)

    # imported after patching
    import importlib
    mod = importlib.import_module(
        "skill_evolver.run_parallel_combined_skill_evolution")

    sys.argv = [sys.argv[0]] + argv
    mod.main()


if __name__ == "__main__":
    main()
