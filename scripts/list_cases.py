"""List local RCAEval cases and count them by dataset and fault type.

Usage:  python scripts/list_cases.py <folder containing the case folders>

Fault labels come from case folder names. They are evaluation metadata
(used for splitting and reporting), never model input.
"""

import sys
from collections import Counter
from pathlib import Path

REQUIRED_FILES = ("metrics.parquet", "inject_time.txt")


def main(root: str) -> None:
    root_path = Path(root)
    counts: Counter[tuple[str, str]] = Counter()
    problems: list[str] = []

    case_dirs = sorted(p for p in root_path.iterdir() if p.is_dir())

    for case in case_dirs:
        parts = case.name.split("_")
        if len(parts) != 4:
            problems.append(f"{case.name}: unexpected folder name")
            continue

        dataset, _service, fault, _index = parts
        missing = [f for f in REQUIRED_FILES if not (case / f).is_file()]
        if missing:
            problems.append(f"{case.name}: missing {missing}")
            continue

        counts[(dataset, fault)] += 1

    print(f"folders found : {len(case_dirs)}")
    print(f"usable cases  : {sum(counts.values())}")
    for (dataset, fault), n in sorted(counts.items()):
        print(f"  {dataset:8s} {fault:8s} {n}")

    if problems:
        print("\nproblems:")
        for line in problems:
            print(f"  {line}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])