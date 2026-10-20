"""Apply-phase guards for dskill.consolidate (--safe-apply, --safe-translate)."""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath


def unsafe_path_reason(file, skill_dir=None) -> str | None:
    """Why a model-chosen edit target must not be written, or None if it may.

    Upstream apply writes `skill_dir / file` unchecked; this rejects targets
    that could land outside the skill folder. An empty target returns None.
    """
    if file is None or file == "":
        return None
    if not isinstance(file, str):
        return f"file is a {type(file).__name__}, not a path"
    if "\x00" in file:
        return "path contains a NUL byte"
    if os.path.isabs(file):
        return "absolute path"
    if ".." in PurePosixPath(file).parts:
        return "path contains '..'"
    if skill_dir is not None:
        try:
            root = Path(skill_dir).resolve()
            (root / file).resolve().relative_to(root)
        except (ValueError, OSError, RuntimeError):
            return "path resolves outside the skill dir"
    return None
