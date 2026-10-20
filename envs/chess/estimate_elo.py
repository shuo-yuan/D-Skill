"""Estimated Elo of chess evaluation passes (Table 1b).

Per pass, a maximum-likelihood logistic fit of `solved` on puzzle rating,
P(solved | r) = sigmoid(a + b (r - 1200) / 400); the estimate is the rating where the fit
crosses 50%, 1200 - 400 a / b. Only puzzles rated below --max-rating count (one paper teacher
pass ran on a wider puzzle set). A document's estimate is the mean over its passes.

    python -m envs.chess.estimate_elo runs/<pass_1>/results.jsonl runs/<pass_2>/results.jsonl
"""
import argparse
import json
import statistics
from pathlib import Path

import numpy as np


def load(path, max_rating):
    rows = {}
    for line in open(path):
        if line.strip():
            r = json.loads(line)
            rows[r["puzzle"]] = r                 # a re-run puzzle keeps its last row
    return [r for r in rows.values() if r["rating"] < max_rating]


def fit_elo(rows):
    x = np.array([(r["rating"] - 1200) / 400 for r in rows])
    y = np.array([r["solved"] for r in rows], dtype=float)
    X = np.c_[np.ones_like(x), x]
    w = np.zeros(2)
    for _ in range(100):                          # Newton-Raphson
        p = 1 / (1 + np.exp(-X @ w))
        step = np.linalg.solve((X * (p * (1 - p))[:, None]).T @ X, X.T @ (y - p))
        w += step
        if np.abs(step).max() < 1e-10:
            break
    return 1200 - 400 * w[0] / w[1]


def main():
    ap = argparse.ArgumentParser(description="Estimated Elo of chess evaluation passes.")
    ap.add_argument("results", nargs="+", type=Path, help="results.jsonl of each pass")
    ap.add_argument("--max-rating", type=int, default=2000, help="count puzzles rated below this")
    a = ap.parse_args()
    elos = []
    for path in a.results:
        rows = load(path, a.max_rating)
        elos.append(fit_elo(rows))
        solved = 100 * sum(r["solved"] for r in rows) / len(rows)
        print(f"{path}: {len(rows)} puzzles, solved {solved:.1f}%, Elo {elos[-1]:.0f}")
    if len(elos) > 1:
        print(f"mean over {len(elos)} passes: Elo {statistics.mean(elos):.0f} +/- {statistics.stdev(elos):.0f}")


if __name__ == "__main__":
    main()
