"""Report how metric column sets differ across local RE2-TT cases.

Usage:  python scripts/column_report.py <data folder>
"""

import sys
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq


def main(root: str) -> None:
    cases = sorted(
        p for p in Path(root).iterdir()
        if p.is_dir() and p.name.startswith("re2tt_")
    )
    per_case: dict[str, set[str]] = {}
    for case in cases:
        names = pq.ParquetFile(case / "metrics.parquet").schema_arrow.names
        per_case[case.name] = {n for n in names if n != "time"}

    counts = Counter(n for cols in per_case.values() for n in cols)
    union = set(counts)
    common = {n for n, c in counts.items() if c == len(cases)}
    print(f"cases={len(cases)} union={len(union)} in_all_cases={len(common)}")
    sizes = sorted(Counter(len(c) for c in per_case.values()).items())
    print("columns per case:", sizes)

    partial = sorted(union - common, key=lambda n: (counts[n], n))
    print(f"partial columns: {len(partial)}")
    for name in partial[:40]:
        print(f"  {counts[name]:3d}/{len(cases)}  {name}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])

