"""Check that all local RE2-TT cases load with one shared metric column set.

Usage:  python scripts/check_series.py <data folder>
"""

import json
import sys
from pathlib import Path

import numpy as np
from reliantops.series import load_metric_series


def main(root: str) -> None:
    cases = sorted(
        p for p in Path(root).iterdir()
        if p.is_dir() and p.name.startswith("re2tt_")
    )
    reference = None
    mismatched = 0
    nan_cells = 0
    dead_columns = 0  # columns that are entirely NaN in a case's pre window

    features = json.loads(
        Path("configs/re2tt_features_v1.json").read_text(encoding="utf-8")
    )["columns"]

    for case in cases:
        series = load_metric_series(case, features)
        if reference is None:
            reference = series.columns
        elif series.columns != reference:
            mismatched += 1
            print(f"{case.name}: different columns")
        nan_cells += int(np.isnan(series.values).sum())
        pre = series.values[series.pre]
        dead_columns += int(np.isnan(pre).all(axis=0).sum())

    print(f"cases={len(cases)} columns={len(reference)} mismatched={mismatched}")
    print(f"nan_cells={nan_cells} all_nan_pre_columns={dead_columns}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])