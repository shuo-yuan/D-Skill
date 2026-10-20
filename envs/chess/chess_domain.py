"""Retarget the Trace2Skill consolidation prompts from spreadsheets to chess.

install() applies REPL to every str constant of the four evolving-agent
modules and wraps load_prompt_template, which loads some intros at call
time. Install it before dskill.consolidate.install_freq_dose so the dose
wrapper composes on top.
"""
from __future__ import annotations

REPL = [
    ("refine a spreadsheet\nskill folder so that agents using it make "
     "fewer errors in the future",
     "refine a chess move-selection\nskill document so that agents using "
     "it choose better moves more often"),
    ("iteratively refine a spreadsheet skill folder so that agents avoid "
     "recurring mistakes while preserving workflows that repeatedly "
     "succeed.",
     "iteratively refine a chess move-selection skill document so that "
     "agents avoid recurring move-selection mistakes while preserving "
     "decision habits that repeatedly succeed."),
    ("iteratively refine a spreadsheet skill folder so that agents using "
     "it can repeat robust, verified workflows more reliably in the "
     "future.",
     "iteratively refine a chess move-selection skill document so that "
     "agents using it can repeat robust, verified decision habits more "
     "reliably in the future."),
    ("- **recalc.py** — helper script (protected, never modify)\n", ""),
    ("- **LICENSE.txt** — license file (protected, never modify)\n", ""),
    ('"Be careful with formulas" is useless.',
     '"Verify before committing" is useless.'),
    ('"Use ArrayFormula(ref=..., text=...) for array formulas in '
     'openpyxl" is useful.',
     '"Before committing, run <safety> on the move and simulate the '
     'strongest forcing reply it lists" is useful.'),
    ("Agents keep forgetting recalculation -> mandatory checklist with "
     "exact command",
     "Agents keep skipping the forcing-reply audit -> mandatory audit "
     "step with the exact query to run"),
    ('"Handle formulas carefully" is weak.',
     '"Choose moves carefully" is weak.'),
    ('"Insert the formula, recalculate, then read back the result before '
     'saving" is useful.',
     '"Before committing, run <safety> on the move and simulate the '
     'strongest forcing reply it lists" is useful.'),
    ("references/formula-validation-patterns.md, not references/ref1.md",
     "references/forcing-line-audit-patterns.md, not references/ref1.md"),
    ("references/formula-patterns.md, not references/ref1.md",
     "references/forcing-line-audit-patterns.md, not references/ref1.md"),
    ('"references/formula-patterns.md")',
     '"references/motif-patterns.md")'),
    ('"Validate Data Structure Before Formulas"',
     '"Audit Checks And Captures Before Quiet Moves"'),
    ('"Incorrect Formula Logic"', '"Committing Unaudited Moves"'),
]


def _apply(s: str) -> str:
    for old, new in REPL:
        s = s.replace(old, new)
    return s


_installed = False


def install() -> None:
    """Patch all four agent modules + the template loader."""
    global _installed
    if _installed:
        return
    import skill_evolver.skill_evolving_agent as sea
    import skill_evolver.parallel_evolving_agent as pea
    import skill_evolver.success_evolving_agent as sue
    import skill_evolver.parallel_success_evolving_agent as psa
    mods = (sea, pea, sue, psa)
    n = 0
    for mod in mods:
        for name in dir(mod):
            v = getattr(mod, name, None)
            if isinstance(v, str):
                w = _apply(v)
                if w != v:
                    setattr(mod, name, w)
                    n += 1
    # call-time template loads (combined/success intros, size warnings)
    from skill_evolver import prompt_loader as pl
    orig = pl.load_prompt_template

    def patched(key):
        t = orig(key)
        return _apply(t) if isinstance(t, str) else t

    patched.__wrapped__ = orig
    if hasattr(orig, "cache_clear"):
        orig.cache_clear()
    pl.load_prompt_template = patched
    # modules that imported the loader by name need their ref swapped too
    for mod in mods:
        if getattr(mod, "load_prompt_template", None) is orig:
            mod.load_prompt_template = patched
    _installed = True
    print(f"[chess-domain] retargeted {n} module constant(s) + template "
          "loader wrapped", flush=True)
