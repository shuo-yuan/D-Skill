"""Per-task (soft, hard) scores from the official SpreadsheetBench evaluation
(evaluate_with_official.evaluate_instance), not upstream's file-exists success flag."""

from __future__ import annotations

from pathlib import Path

from envs.spreadsheetbench.dataset import VERIFIED
from envs.spreadsheetbench.evaluate_with_official import evaluate_instance
from envs.spreadsheetbench.spreadsheetbench_support import load_dataset

_INSTANCES = None


def _instances():
    global _INSTANCES
    if _INSTANCES is None:
        _INSTANCES = {str(i["id"]): i for i in load_dataset(str(VERIFIED))}
    return _INSTANCES


def score_instance(tid: str, output_dir: Path, spreadsheet_path: str = ""):
    """(soft, hard) for one instance's produced outputs under <output_dir>
    (a run's outputs/ directory), exactly as the official evaluation scores it."""
    inst = _instances().get(str(tid))
    if inst is None:
        return 0.0, 0
    try:
        r = evaluate_instance(str(VERIFIED), str(output_dir), inst)
    except Exception:
        return 0.0, 0
    if not r or "hard_score" not in r:
        return 0.0, 0
    return float(r["soft_score"]), int(r["hard_score"])
