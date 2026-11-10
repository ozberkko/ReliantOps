"""Audit the 720s pre / 721-row post window claim on local RE2-TT metrics.

Usage:  python scripts/audit_windows.py <data folder>
"""

import sys
from pathlib import Path

import pyarrow.parquet as pq

WINDOW = 720
EXPECTED_ROWS = 1441


def audit(case: Path) -> list[str]:
    inject = int((case / "inject_time.txt").read_text(encoding="utf-8").strip())
    column = pq.read_table(case / "metrics.parquet", columns=["time"]).column("time")
    times = column.to_pylist()

    problems: list[str] = []
    if any(t is None for t in times):
        return ["null values in time column"]

    pre = sum(1 for t in times if inject - WINDOW <= t < inject)
    post = sum(1 for t in times if inject <= t <= inject + WINDOW)

    if len(times) != EXPECTED_ROWS:
        problems.append(f"rows={len(times)}")
    if pre != WINDOW:
        problems.append(f"pre={pre}")
    if post != WINDOW + 1:
        problems.append(f"post={post}")
    if pre + post != len(times):
        problems.append("rows outside both windows")
    if len(set(times)) != len(times):
        problems.append("duplicate timestamps")
    if any(b - a != 1 for a, b in zip(times, times[1:])):
        problems.append("not strictly 1-second spacing")
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