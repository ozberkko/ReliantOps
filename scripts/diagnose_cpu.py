"""Diagnose why the baselines miss cpu cases (validation split only).

Read-only: changes no detector, threshold or split.

Usage:  python scripts/diagnose_cpu.py <data folder>
"""

import json
import sys
from pathlib import Path

import numpy as np
from reliantops.detectors.zscore import ZScoreDetector
from reliantops.series import load_metric_series


def main(root: str) -> None:
    features = json.loads(
        Path("configs/re2tt_features_v1.json").read_text(encoding="utf-8")
    )["columns"]
    split = json.loads(
        Path("configs/re2tt_split_v1.json").read_text(encoding="utf-8")
    )["split"]
    tau = json.loads(
        Path("configs/baseline_tau_v1.json").read_text(encoding="utf-8")
    )["tau"]["zscore"]
    base = Path(root)

    def load(name: str):
        return load_metric_series(base / name, features)

    calibration = [load(n) for n in split["calibration"]]
    reference = np.vstack([s.values[s.pre] for s in calibration])
    detector = ZScoreDetector()
    detector.fit(reference)
    use = detector.usable_
    cols = np.array(features)[use]

    def zscores(values: np.ndarray) -> np.ndarray:
        z = np.abs(values[:, use] - detector.mean_[use]) / detector.std_[use]
        return np.nan_to_num(z, nan=0.0)

    print(f"zscore tau={tau:.3f}")
    pre_peaks = []
    for name in split["validation"]:
        s = load(name)
        z = zscores(s.values)
        post = z[s.post]
        _, col = np.unravel_index(post.argmax(), post.shape)
        own = np.flatnonzero(cols == f"{name.split('_')[1]}_cpu")
        own_z = post[:, own[0]].max() if own.size else float("nan")
        print(
            f"{name:34s} post_peak={post.max():7.1f} {cols[col]:34s} "
            f"own_cpu={own_z:6.1f}"
        )
        windows = z[s.pre].reshape(12, 60, -1).max(axis=1)
        for w in range(12):
            pre_peaks.append((windows[w].max(), name, cols[windows[w].argmax()]))

    print("\nhighest pre-window peaks (these decide tau):")
    for peak, name, column in sorted(pre_peaks, reverse=True)[:12]:
        print(f"{peak:7.1f}  {name:34s} {column}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])