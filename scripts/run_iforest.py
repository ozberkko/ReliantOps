"""Evaluate Isolation Forest configurations on the validation split.

Exploratory: writes no frozen file. The test split is never loaded.
Without --all only the default configuration runs
(see docs/research/ml_detector_rule_v1.md).

Usage:  python scripts/run_iforest.py <data folder> [--all]
"""

import json
import sys
from pathlib import Path

import numpy as np
from reliantops.detectors.iforest import IsolationForestDetector
from reliantops.evaluation import (
    evaluate_case,
    select_tau,
    summarize,
    summarize_by_family,
    window_maxima,
)
from reliantops.series import load_metric_series

# The four pre-registered configurations; the first one is the default.
CONFIGS = [(100, 256), (100, 1024), (300, 256), (300, 1024)]


def main(root: str, run_all: bool) -> None:
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
    print(f"reference matrix: {reference.shape}")

    configs = CONFIGS if run_all else CONFIGS[:1]
    for n_estimators, max_samples in configs:
        detector = IsolationForestDetector(n_estimators, max_samples)
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
        print(
            f"[iforest n_estimators={n_estimators} max_samples={max_samples}] "
            f"tau={tau:.4f} window-FPR={total.fpr:.3f} "
            f"recall={total.recall:.2f} missed={total.missed} "
            f"mttd mean={total.mttd_mean} median={total.mttd_median}"
        )
        for family, s in summarize_by_family(outcomes).items():
            print(
                f"    {family:7s} recall={s.recall:.2f} missed={s.missed} "
                f"mttd median={s.mttd_median}"
            )


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) not in (1, 2) or (len(args) == 2 and args[1] != "--all"):
        raise SystemExit(__doc__)
    main(args[0], run_all=len(args) == 2)