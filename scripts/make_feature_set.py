"""Write the v1 feature set: metric columns present in every local RE2-TT case.

Usage:  python scripts/make_feature_set.py <data folder>
"""

import json
import sys
from pathlib import Path

import pyarrow.parquet as pq

OUTPUT = Path("configs/re2tt_features_v1.json")


def main(root: str) -> None:
    cases = sorted(
        p for p in Path(root).iterdir()
        if p.is_dir() and p.name.startswith("re2tt_")
    )

    if not cases:
        raise SystemExit(f"no re2tt_* case folders found in {root}")
        
    common: set[str] | None = None
    for case in cases:
        names = pq.ParquetFile(case / "metrics.parquet").schema_arrow.names
        columns = {n for n in names if n != "time"}
        common = columns if common is None else common & columns

    result = {
        "dataset": "RE2-TT",
        "rule": "metric columns present in all cases, by column name only",
        "n_cases": len(cases),
        "columns": sorted(common or ()),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"cases={len(cases)} columns={len(result['columns'])} -> {OUTPUT}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])