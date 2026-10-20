"""TRANSLATE guard: stop invented `old_text` anchors from deleting the skill.

1. Lint: `replace_in_section` without `old_text` becomes `append_to_section`
   (TRANSLATE would otherwise invent the span), and `delete_section` is dropped.
2. Dry run: an edit deleting more than MIN_LINES lines and more than RATIO x
   the lines it adds is re-translated with those numbers, then falls back to
   `append_to_section`. `content` is never changed.

Installed by python -m dskill.consolidate --safe-translate.
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

MIN_LINES = 20      # absolute floor: below this, deletion is never flagged
RATIO = 3.0         # flag when deleted lines > RATIO x added lines
MAX_RETRIES = 2

_STATS = {"linted_replace": 0, "dropped_delete_section": 0,
          "retried": 0, "fallback_append": 0, "clean": 0}


def _nlines(s: str) -> int:
    return len((s or "").split("\n"))


def lint_patch(patch):
    """Layer 1 — remove ops that force TRANSLATE to invent a deletion."""
    kept = []
    for e in patch.edits:
        if e.op == "delete_section":
            _STATS["dropped_delete_section"] += 1
            log.warning("[safe-translate] dropping delete_section %r "
                        "(never legitimate in an accumulating skill)",
                        e.target_section)
            continue
        if e.op == "replace_in_section" and not (e.old_text or "").strip():
            e.op = "append_to_section"
            _STATS["linted_replace"] += 1
        kept.append(e)
    patch.edits = kept
    return patch


def delta(before: str, edit, apply_fn) -> tuple[int, int]:
    """Lines removed / added if this edit were applied (dry run).

    An edit that raises is treated as a no-op so the dry run cannot abort the
    step; the apply phase has its own guard.
    """
    try:
        after = apply_fn(before, edit)
    except Exception as exc:                      # noqa: BLE001
        log.warning("[safe-translate] dry run failed for op=%r (%s: %s) — "
                    "treating as no-op", getattr(edit, "op", "?"),
                    type(exc).__name__, exc)
        return 0, 0
    if after == before:
        return 0, 0
    bset: dict[str, int] = {}
    aset: dict[str, int] = {}
    for l in before.split("\n"):
        bset[l] = bset.get(l, 0) + 1
    for l in after.split("\n"):
        aset[l] = aset.get(l, 0) + 1
    removed = sum(max(0, c - aset.get(l, 0)) for l, c in bset.items())
    added = sum(max(0, c - bset.get(l, 0)) for l, c in aset.items())
    return removed, added


def too_destructive(removed: int, added: int) -> bool:
    """Flag only large, lopsided deletions."""
    return removed > MIN_LINES and removed > RATIO * max(1, added)


def install(evolver_cls, apply_fn):
    """Wrap run_translation_phase with the lint + dry-run retry guard."""
    orig_translate = evolver_cls.run_translation_phase
    orig_translate_one_marker = "[safe-translate]"

    def _delta(before, edit):
        return delta(before, edit, apply_fn)

    _too_destructive = too_destructive

    def safe_translation_phase(self, skill_state, final_patch):
        final_patch = lint_patch(final_patch)
        if _STATS["linted_replace"] or _STATS["dropped_delete_section"]:
            log.info("%s lint: %d replace_in_section -> append_to_section, "
                     "%d delete_section dropped", orig_translate_one_marker,
                     _STATS["linted_replace"], _STATS["dropped_delete_section"])

        translated = orig_translate(self, skill_state, final_patch)

        checked = []
        for edit in translated.edits:
            before = skill_state.get(edit.file, "")
            if edit.op in ("create", "delete_file") or not before:
                checked.append(edit)
                continue
            removed, added = _delta(before, edit)
            if not _too_destructive(removed, added):
                _STATS["clean"] += 1
                checked.append(edit)
                continue

            log.warning("%s edit on %s would delete %d lines and add %d "
                        "(%.1fx) — retrying translation",
                        orig_translate_one_marker, edit.file, removed, added,
                        removed / max(1, added))
            fixed = None
            for attempt in range(1, MAX_RETRIES + 1):
                _STATS["retried"] += 1
                msg = self._build_translation_user_message(
                    edit.file, before, [edit]) + (
                    f"\n\n!! YOUR PREVIOUS ATTEMPT CAUSED SEVERE INFORMATION "
                    f"LOSS: the old_text you produced spans {removed} lines "
                    f"while the replacement content is only {added} lines, so "
                    f"applying it would DELETE {removed - added} lines of "
                    f"accumulated knowledge. That is never correct. old_text "
                    f"must identify ONLY the specific passage the content "
                    f"replaces — normally a single bullet or sentence, at most "
                    f"a few lines. If the content is NEW material rather than "
                    f"a rewrite of an existing passage, return the edit with "
                    f"op \"append_to_section\" and an empty old_text. Keep "
                    f"content unchanged.")
                try:
                    resp, trace = self._call_llm(
                        self._translation_system_prompt, msg, tag="patch")
                    cand = self._coalesce_patches(self._parse_patches(
                        resp, tag="patch", phase="translation",
                        label="safe_retry", conversation_trace=trace))
                except Exception as exc:                      # noqa: BLE001
                    log.warning("%s retry %d failed: %r",
                                orig_translate_one_marker, attempt, exc)
                    cand = None
                if cand and cand.edits:
                    c = cand.edits[0]
                    r2, a2 = _delta(before, c)
                    if not _too_destructive(r2, a2):
                        log.info("%s retry %d ok: -%d/+%d lines",
                                 orig_translate_one_marker, attempt, r2, a2)
                        fixed = c
                        break
                    removed, added = r2, a2

            if fixed is None:
                # keep the CONTENT, make deletion structurally impossible
                edit.op = "append_to_section"
                edit.old_text = ""
                _STATS["fallback_append"] += 1
                log.warning("%s retries exhausted — converting to "
                            "append_to_section (content preserved)",
                            orig_translate_one_marker)
                fixed = edit
            checked.append(fixed)

        translated.edits = checked
        log.info("%s summary: %s", orig_translate_one_marker, dict(_STATS))
        return translated

    evolver_cls.run_translation_phase = safe_translation_phase
    print("[safe-translate] installed: lint (no-old_text replace -> append, "
          f"delete_section dropped) + dry-run guard (>{MIN_LINES} lines and "
          f">{RATIO}x added -> retry x{MAX_RETRIES} -> append fallback)",
          flush=True)
