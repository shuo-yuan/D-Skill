"""APPLY guard: anchored edits cannot touch section headers, and an edit aimed
at a missing section creates that section instead of being dropped.

Also: fuzzy header matching, dropping edits whose `file` escapes the skill
dir, restoring the YAML frontmatter if an edit changes it, and re-translating
edits that still change nothing (up to MAX_RETRIES times).

Installed by python -m dskill.consolidate --safe-apply.
"""

from __future__ import annotations

import logging
import re

from . import unsafe_path_reason

log = logging.getLogger(__name__)

_STATS = {"header_protected": 0, "section_created": 0,
          "retry_seen": 0, "retry_calls": 0, "retry_recovered": 0,
          "retry_failed": 0,
          "fuzzy_matched": 0, "dropped": 0, "clean": 0}


def _norm(s: str) -> str:
    """Case/space-insensitive key for a header line."""
    s = re.sub(r"[^\w\s]", "", (s or "").strip().lower())
    return re.sub(r"\s+", " ", s)


def _leads_with_header(text: str, sec: str) -> bool:
    """True when `text` opens with this section's own header line."""
    first = (text or "").lstrip("\n").split("\n", 1)[0].strip()
    return bool(first) and first == (sec or "").strip()


def _drop_leading_header(text: str) -> str:
    t = (text or "").lstrip("\n")
    parts = t.split("\n", 1)
    return parts[1] if len(parts) > 1 else ""


def _strip_header(edit, sec: str) -> str:
    """edit.content with a leading duplicate of the section header removed."""
    c = getattr(edit, "content", "") or ""
    return _drop_leading_header(c) if _leads_with_header(c, sec) else c


def _frontmatter(text: str) -> str | None:
    """The leading '---' ... '---' block, or None if absent/not at the top."""
    lines = (text or "").split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, min(len(lines), 30)):
        if lines[i].strip() == "---":
            return "\n".join(lines[:i + 1])
    return None


def _protect_frontmatter(before: str, after: str):
    """Restore the YAML frontmatter if an edit changed or removed it.

    Returns (content, restored: bool).
    """
    fm = _frontmatter(before)
    if fm is None or _frontmatter(after) == fm:
        return after, False
    body = after
    stale = _frontmatter(body)
    if stale is not None:                       # a different block at the top
        body = body[len(stale):].lstrip("\n")
    else:                                       # none at the top
        body = body.lstrip("\n")
    return fm + "\n\n" + body, True


def install(pea):
    """Patch pea._apply_patch_edit_to_content. Returns True if applied."""
    orig = pea._apply_patch_edit_to_content
    find_bounds = pea._find_section_bounds

    def _resolve(lines, target):
        """Exact -> fuzzy section lookup. Returns bounds or None."""
        b = find_bounds(lines, target)
        if b is not None:
            return b
        want = _norm(target)
        if not want:
            return None
        for i, l in enumerate(lines):
            if l.lstrip().startswith("#") and _norm(l) == want:
                _STATS["fuzzy_matched"] += 1
                return find_bounds(lines, l.strip())
        return None

    # Anchor fields come from model JSON and may be non-strings (e.g.
    # "after_section": true), which crash upstream; None means "no anchor".
    _ANCHORS = ("target_section", "after_section", "old_text",
                "target_text", "content")

    def _sanitize(edit):
        for field in _ANCHORS:
            v = getattr(edit, field, None)
            if v is not None and not isinstance(v, str):
                _STATS["coerced_field"] = _STATS.get("coerced_field", 0) + 1
                log.warning("[safe-apply] %s.%s was %r (%s), not a string — "
                            "coercing to None", getattr(edit, "op", "?"),
                            field, v, type(v).__name__)
                try:
                    setattr(edit, field, None)
                except Exception:                 # noqa: BLE001, frozen attrs
                    pass
        return edit

    def patched(content: str, edit) -> str:
        # A file missing from the skill state arrives with content '' and
        # would get a new section below, so refuse escaping targets first.
        why = unsafe_path_reason(getattr(edit, "file", ""))
        if why:
            _STATS["unsafe_path"] = _STATS.get("unsafe_path", 0) + 1
            log.warning("[safe-apply] dropped %s on %r: %s",
                        getattr(edit, "op", "?"), getattr(edit, "file", ""),
                        why)
            return content
        edit = _sanitize(edit)
        op = getattr(edit, "op", "")
        sec = getattr(edit, "target_section", "") or ""

        if op not in ("replace_in_section", "insert_after", "insert_before",
                      "append_to_section") or not sec:
            out = orig(content, edit)
            _STATS["clean" if out != content else "dropped"] += 1
            return out

        lines = content.split("\n")
        bounds = _resolve(lines, sec)

        # missing section: create it rather than discard the edit
        if bounds is None:
            body = (getattr(edit, "content", "") or "").rstrip()
            if not body:
                _STATS["dropped"] += 1
                return content
            header = sec if sec.lstrip().startswith("#") else f"## {sec.strip()}"
            _STATS["section_created"] += 1
            log.warning("[safe-apply] section %r missing — creating it and "
                        "placing the edit there (was: silently dropped)", sec)
            return "\n".join(lines + ["", header, "", body])

        start, end = bounds
        # the header line is not part of the editable region
        bstart = start + 1
        body = "\n".join(lines[bstart:end]) if bstart < end else ""

        # a blank-only body (e.g. a seeded skeleton section) counts as empty
        if not body.strip():
            _STATS["empty_append"] = _STATS.get("empty_append", 0) + 1
            return "\n".join(lines[:end] + ["", _strip_header(edit, sec).rstrip()]
                             + lines[end:])

        if op == "replace_in_section":
            old = getattr(edit, "old_text", "") or ""
            # TRANSLATE often prefixes old_text and content with the section
            # header; strip it from both (stripping only old_text would
            # duplicate the header), then re-decide.
            if old and _leads_with_header(old, sec):
                old = _drop_leading_header(old)
                _STATS["header_stripped"] = _STATS.get("header_stripped", 0) + 1
                if not old.strip():
                    # nothing left to match -> this is an append
                    return "\n".join(lines[:end]
                                      + ["", _strip_header(edit, sec).rstrip()]
                                      + lines[end:])
            if old and old in body:
                new = body.replace(old, _strip_header(edit, sec), 1)
            else:
                _STATS["dropped"] += 1
                log.warning("[safe-apply] replace_in_section: old_text not in "
                            "the BODY of %r", sec)
                return content
        elif op in ("insert_after", "insert_before"):
            tgt = getattr(edit, "target_text", "") or ""
            if tgt and tgt in body:
                rep = (tgt + "\n" + (edit.content or "")) if op == "insert_after" \
                      else ((edit.content or "") + "\n" + tgt)
                new = body.replace(tgt, rep, 1)
            else:
                _STATS["dropped"] += 1
                return content
        else:                                    # append_to_section
            tail = body.rstrip("\n")
            new = tail + "\n\n" + (edit.content or "").rstrip()

        _STATS["header_protected"] += 1
        return "\n".join(lines[:bstart] + new.split("\n") + lines[end:])

    def guarded(content: str, edit) -> str:
        out = patched(content, edit)
        out, restored = _protect_frontmatter(content, out)
        if restored:
            _STATS["frontmatter_restored"] = _STATS.get("frontmatter_restored", 0) + 1
            log.warning("[safe-apply] %s on %r removed the YAML frontmatter — "
                        "restored", getattr(edit, "op", "?"),
                        getattr(edit, "target_section", "") or "?")
        return out

    pea._apply_patch_edit_to_content = guarded

    # Edits that still change nothing (an old_text not in the section) are
    # re-translated with the section's real body.
    _install_retry(pea, guarded)

    print("[safe-apply] installed: headers unreachable (body-only edits), "
          "blank-body append, header-prefixed old_text stripped, missing "
          f"sections created, fuzzy header match, + re-translate dropped "
          f"edits (max {MAX_RETRIES})", flush=True)
    return True


MAX_RETRIES = 3


def _retry_feedback(edit, body: str, sec: str) -> str:
    """Tell TRANSLATE exactly why APPLY refused the edit."""
    empty = not body.strip()
    return (
        f"\n\n!! YOUR PREVIOUS EDIT WAS DROPPED BY THE APPLY PHASE and its "
        f"content was lost. op={getattr(edit, 'op', '?')!r} on section {sec!r}: "
        f"the old_text you produced does not occur in that section's BODY.\n"
        f"  1. The section HEADER LINE is not part of the body and can never "
        f"be matched. Never put {sec!r} (or any '## ' line) in old_text.\n"
        f"  2. old_text must be a VERBATIM substring of the text currently "
        f"under that header.\n"
        + (f"That section is EMPTY -- there is nothing to replace. Return the "
           f"edit with op \"append_to_section\", an empty old_text, and the "
           f"body text only.\n" if empty else
           f"The section's exact current body follows; copy old_text from "
           f"inside it, or use op \"append_to_section\" with an empty "
           f"old_text if this is new material:\n---8<---\n{body[:1500]}\n"
           f"---8<---\n")
        + "Keep the substantive content unchanged.")


def _install_retry(pea, apply_fn):
    """Wrap the apply PHASE so dropped edits get re-translated."""
    cls = pea.ParallelSkillEvolver
    orig_phase = cls.run_apply_phase_programmatic

    def phased(self, skill_state, final_patch):
        state = dict(skill_state or {})
        surviving = []
        skill_dir = getattr(self, "skill_dir", None)
        for edit in list(getattr(final_patch, "edits", []) or []):
            # target containment (every op, before any retry call)
            why = unsafe_path_reason(getattr(edit, "file", ""), skill_dir)
            if why:
                _STATS["unsafe_path"] = _STATS.get("unsafe_path", 0) + 1
                log.warning("[safe-apply] dropped %s on %r: %s",
                            getattr(edit, "op", "?"),
                            getattr(edit, "file", ""), why)
                continue
            if getattr(edit, "op", "") in ("create", "delete_file"):
                surviving.append(edit)
                continue
            f = getattr(edit, "file", "") or "SKILL.md"
            cur = state.get(f, "")
            try:
                out = apply_fn(cur, edit)
            except Exception:                                  # noqa: BLE001
                out = cur
            if out != cur:
                state[f] = out
                surviving.append(edit)
                continue

            _STATS["retry_seen"] += 1
            sec = getattr(edit, "target_section", "") or ""
            try:
                ls = cur.split("\n")
                b = pea._find_section_bounds(ls, sec)
                body = "\n".join(ls[b[0] + 1:b[1]]) if b else ""
            except Exception:                                  # noqa: BLE001
                body = ""
            fixed = None
            for attempt in range(1, MAX_RETRIES + 1):
                _STATS["retry_calls"] += 1
                try:
                    msg = self._build_translation_user_message(
                        f, cur, [edit]) + _retry_feedback(edit, body, sec)
                    resp, trace = self._call_llm(
                        self._translation_system_prompt, msg, tag="patch")
                    cand = self._coalesce_patches(self._parse_patches(
                        resp, tag="patch", phase="translation",
                        label="safe_apply_retry", conversation_trace=trace))
                except Exception as exc:                       # noqa: BLE001
                    log.warning("[safe-apply] retry %d errored: %r", attempt, exc)
                    cand = None
                if not (cand and cand.edits):
                    continue
                c = cand.edits[0]
                # the retry's `file` is chosen by the model again
                why = unsafe_path_reason(getattr(c, "file", ""), skill_dir)
                if why:
                    _STATS["unsafe_path"] = _STATS.get("unsafe_path", 0) + 1
                    log.warning("[safe-apply] retry %d rejected: %s on %r: %s",
                                attempt, getattr(c, "op", "?"),
                                getattr(c, "file", ""), why)
                    continue
                try:
                    out2 = apply_fn(cur, c)
                except Exception:                              # noqa: BLE001
                    out2 = cur
                if out2 != cur:
                    log.info("[safe-apply] retry recovered %r on %r after %d "
                             "attempt(s) (op now %r)",
                             getattr(edit, "op", "?"), sec, attempt,
                             getattr(c, "op", "?"))
                    fixed = (c, out2)
                    break
            if fixed:
                _STATS["retry_recovered"] += 1
                state[f] = fixed[1]
                surviving.append(fixed[0])
            else:
                _STATS["retry_failed"] += 1
                log.warning("[safe-apply] retry gave up on %r in %r after %d "
                            "attempts — edit dropped",
                            getattr(edit, "op", "?"), sec, MAX_RETRIES)

        final_patch.edits = surviving
        res = orig_phase(self, skill_state, final_patch)
        if _STATS["retry_seen"]:
            log.info("[safe-apply] retry summary: seen=%d calls=%d "
                     "recovered=%d failed=%d", _STATS["retry_seen"],
                     _STATS["retry_calls"], _STATS["retry_recovered"],
                     _STATS["retry_failed"])
        return res

    cls.run_apply_phase_programmatic = phased


def stats() -> dict:
    return dict(_STATS)
