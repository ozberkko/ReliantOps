"""Audit the 720s pre / 721-row post window claim on local RE2-TT metrics.

Usage:  python scripts/audit_windows.py <data folder>
"""

import sys
from pathlib import Path

import pyarrow.parquet as pq
from reliantops.windows import has_full_windows, validate_regular_axis, window_slices

EXPECTED_ROWS = 1441


def audit(case: Path) -> list[str]:
    inject = int((case / "inject_time.txt").read_text(encoding="utf-8").strip())
    column = pq.read_table(case / "metrics.parquet", columns=["time"]).column("time")
    times = column.to_pylist()

    if any(t is None for t in times):
        return ["null values in time column"]

    try:
        validate_regular_axis(times)
    except ValueError as error:
        return [str(error)]

    problems: list[str] = []
    if len(times) != EXPECTED_ROWS:
        problems.append(f"rows={len(times)}")
    if not has_full_windows(times, inject):
        problems.append("pre/post windows are not 720/721 rows")
    pre, post = window_slices(times, inject)
    if post.stop - pre.start != len(times):
        problems.append("rows outside both windows")
    if not (times[0] <= inject <= times[-1]):
        problems.append("inject_time outside metric range")
    return problems


def main(root: str) -> None:
    cases = sorted(
        p for p in Path(root).iterdir()
        if p.is_dir() and p.name.startswith("re2tt_")
    )
    bad = 0
    for case in cases:
        problems = audit(case)
        if problems:
            bad += 1
            print(f"{case.name}: {', '.join(problems)}")
    print(f"checked={len(cases)} ok={len(cases) - bad} with_problems={bad}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])