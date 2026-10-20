"""Location of SpreadsheetBench-Verified-400 (under data/) and a loader for its dataset.json."""

import json
from pathlib import Path

VERIFIED = (Path(__file__).resolve().parent / "data" / "spreadsheetbench_verified" /
            "spreadsheetbench_verified_400")


def load_verified():
    recs = json.loads((VERIFIED / "dataset.json").read_text())
    ids = [str(r["id"]) for r in recs]
    by_id = {str(r["id"]): r for r in recs}
    return ids, by_id
