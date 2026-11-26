"""Read-only sanity check: detector response when k columns shift by +30 std.

Uses calibration cases only; changes no detector, threshold or split.

Usage:  python scripts/diagnose_iforest.py <data folder>
"""

import json
import sys
from pathlib import Path

import numpy as np
from reliantops.detectors.iforest import IsolationForestDetector
from reliantops.detectors.zscore import ZScoreDetector
from reliantops.series import load_metric_series

SHIFT_STD = 30.0


def main(root: str) -> None:
    features = json.loads(
        Path("configs/re2tt_features_v1.json").read_text(encoding="utf-8")
    )["columns"]
    split = json.loads(
        Path("configs/re2tt_split_v1.json").read_text(encoding="utf-8")
    )["split"]
    base = Path(root)
    series = [load_metric_series(base / n, features) for n in split["calibration"]]
    reference = np.vstack([s.values[s.pre] for s in series])

    rng = np.random.default_rng(0)
    normal = reference[rng.choice(len(reference), 500, replace=False)]

    for detector in (ZScoreDetector(), IsolationForestDetector()):
        detector.fit(reference)
        usable = np.flatnonzero(detector.usable_)
        normal_scores = detector.score(normal)
        cutoff = np.quantile(normal_scores, 0.95)
        print(
            f"[{detector.name}] normal median={np.median(normal_scores):.3f} "
            f"95th pct={cutoff:.3f}"
        )
        for k in (1, 5, 20, 100):
            cols = rng.choice(usable, size=k, replace=False)
            mean = np.nanmean(reference[:, cols], axis=0)
            std = np.nanstd(reference[:, cols], axis=0)
            shifted = normal.copy()
            shifted[:, cols] = mean + SHIFT_STD * std
            scores = detector.score(shifted)
            print(
                f"    k={k:3d} median score={np.median(scores):.3f} "
                f"above normal 95th pct: {np.mean(scores > cutoff):.2f}"
            )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])