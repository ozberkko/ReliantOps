"""Seed stability of Isolation Forest v2 on validation (read-only).

Seeds are fixed in advance; the frozen v2 (seed 42) is not changed.
The test split is never loaded.

Usage:  python scripts/seed_check_v2.py <data folder>
"""

import json
import sys
from pathlib import Path

import numpy as np
from reliantops.detectors.iforest_service import ServiceIsolationForestDetector
from reliantops.evaluation import (
    evaluate_case,
    select_tau,
    summarize,
    summarize_by_family,
    window_maxima,
)
from reliantops.series import load_metric_series

SEEDS = [1, 2, 3, 4, 5]


def main(root: str) -> None:
    features = json.loads(
        Path("configs/re2tt_features_v1.json").read_text(encoding="utf-8")
    )["columns"]
    split = json.loads(
        Path("configs/re2tt_split_v1.json").read_text(encoding="utf-8")
    )["split"]
    base = Path(root)

    def load(names: list[str]) -> dict:
        return {n: load_metric_series(base / n, features) for n in names}

    calibration = load(split["calibration"])
    validation = load(split["validation"])
    reference = np.vstack([s.values[s.pre] for s in calibration.values()])

    for seed in SEEDS:
        detector = ServiceIsolationForestDetector(features, seed=seed)
        detector.fit(reference)
        scores = {n: detector.score(s.values) for n, s in validation.items()}
        maxima = np.concatenate(
            [window_maxima(scores[n][s.pre]) for n, s in validation.items()]
        )
        tau = select_tau(maxima)
        outcomes = {
            n: evaluate_case(scores[n], s.pre, s.post, tau)
            for n, s in validation.items()
        }
        total = summarize(list(outcomes.values()))
        families = " ".join(
            f"{f}={s.recall:.2f}" for f, s in summarize_by_family(outcomes).items()
        )
        print(
            f"seed={seed} tau={tau:.3f} fpr={total.fpr:.3f} "
            f"recall={total.recall:.2f} missed={total.missed} | {families}"
        )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])