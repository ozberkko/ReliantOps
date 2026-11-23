"""Fit baselines on calibration cases, select tau on validation cases.

The test split is never loaded here (closed until Week 14).

Usage:  python scripts/run_baselines.py <data folder>
"""

import json
import sys
from pathlib import Path

import numpy as np
from reliantops.detectors.ewma import EWMADetector
from reliantops.detectors.zscore import ZScoreDetector
from reliantops.evaluation import (
    MAX_FPR,
    evaluate_case,
    select_tau,
    summarize,
    summarize_by_family,
    window_maxima,
)
from reliantops.series import load_metric_series


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
    print(f"reference matrix: {reference.shape}")

    taus: dict[str, float] = {}
    n_windows = 0

    for detector in (ZScoreDetector(), EWMADetector()):
        detector.fit(reference)
        scores = {n: detector.score(s.values) for n, s in validation.items()}
        maxima = np.concatenate(
            [window_maxima(scores[n][s.pre]) for n, s in validation.items()]
        )
        tau = select_tau(maxima)
        taus[detector.name] = tau
        n_windows = len(maxima)
        outcomes = {
            n: evaluate_case(scores[n], s.pre, s.post, tau)
            for n, s in validation.items()
        }
        total = summarize(list(outcomes.values()))
        print(
            f"[{detector.name}] tau={tau:.3f} window-FPR={total.fpr:.3f} "
            f"recall={total.recall:.2f} missed={total.missed} "
            f"mttd mean={total.mttd_mean} median={total.mttd_median}"
        )
        for family, s in summarize_by_family(outcomes).items():
            print(
                f"    {family:7s} recall={s.recall:.2f} missed={s.missed} "
                f"mttd median={s.mttd_median}"
            )

        frozen = {
        "rule": "smallest tau with window-level FPR <= max_fpr on pooled "
        "validation pre-windows (all families), chosen per detector",
        "max_fpr": MAX_FPR,
        "n_validation_windows": n_windows,
        "features": "configs/re2tt_features_v1.json",
        "split": "configs/re2tt_split_v1.json",
        "tau": taus,
    }
    Path("configs/baseline_tau_v1.json").write_text(
        json.dumps(frozen, indent=2) + "\n", encoding="utf-8"
    )
    print("wrote configs/baseline_tau_v1.json")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])