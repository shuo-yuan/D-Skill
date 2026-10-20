"""Split an analysis's lessons into chunks for the consolidator.

The task ids that have lessons are shuffled with --seed and dealt round-robin into
max(3, ceil(n / --per-chunk)) batches (batch_001, ...), each holding that subset's
parsed_errors.json and parsed_success.json. Works for every benchmark.

    python -m dskill.make_chunks --src runs/<run>/analysis --dst runs/<run>/chunks --seed 0
"""
import argparse
import json
import math
import random
from pathlib import Path


def make_chunks(src, dst, seed, per_chunk=10):
    """Write the batches; return (number of batches, number of tasks)."""
    src, dst = Path(src), Path(dst)
    if list(dst.glob("batch_*")):
        raise SystemExit(f"{dst} already has batches; choose an empty --dst")
    err = json.loads((src / "parsed_errors.json").read_text())
    suc = json.loads((src / "parsed_success.json").read_text())
    ids = sorted({r["instance_id"] for r in err} | {r["instance_id"] for r in suc})
    random.Random(seed).shuffle(ids)
    n_batches = max(3, math.ceil(len(ids) / per_chunk))
    for k in range(1, n_batches + 1):
        group = set(ids[k - 1::n_batches])
        b = dst / f"batch_{k:03d}"
        b.mkdir(parents=True, exist_ok=True)
        with open(b / "parsed_errors.json", "w") as f:
            json.dump([r for r in err if r["instance_id"] in group], f)
        with open(b / "parsed_success.json", "w") as f:
            json.dump([r for r in suc if r["instance_id"] in group], f)
    return n_batches, len(ids)


def main():
    ap = argparse.ArgumentParser(description="Split an analysis's lessons into chunks.")
    ap.add_argument("--src", type=Path, required=True, help="analysis dir with parsed_*.json")
    ap.add_argument("--dst", type=Path, required=True, help="output dir for batch_NNN/")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--per-chunk", type=int, default=10, help="target tasks per batch")
    a = ap.parse_args()
    n_batches, n_tasks = make_chunks(a.src, a.dst, a.seed, a.per_chunk)
    print(f"{a.dst}: {n_batches} batches over {n_tasks} tasks")


if __name__ == "__main__":
    main()
