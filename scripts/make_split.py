"""Create the deterministic calibration/validation/test split for RE2-TT.

Usage:  python scripts/make_split.py <data folder> configs/re2tt_split_v1.json
"""

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

SEED = 42
DATASET = "re2tt"
TARGETS = {"calibration": 2, "validation": 1, "test": 2}  # groups per fault family
PRIMARY_FAULT_FAMILY = "cpu"


def main(root: str, out: str) -> None:
    # (fault, service) -> case names; same group always stays in one split
    groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    for case in sorted(Path(root).iterdir()):
        parts = case.name.split("_")
        usable = (
            len(parts) == 4
            and parts[0] == DATASET
            and (case / "metrics.parquet").is_file()
            and (case / "inject_time.txt").is_file()
        )
        if usable:
            groups[(parts[2], parts[1])].append(case.name)

    by_fault: dict[str, list[list[str]]] = defaultdict(list)
    for (fault, _service), cases in sorted(groups.items()):
        by_fault[fault].append(cases)

    rng = random.Random(SEED)
    split: dict[str, list[str]] = {name: [] for name in TARGETS}

    for _fault, fault_groups in sorted(by_fault.items()):
        rng.shuffle(fault_groups)
        filled = {name: 0 for name in TARGETS}
        for cases in fault_groups:
            # put the group into the split that is furthest below its target
            name = max(TARGETS, key=lambda n: TARGETS[n] - filled[n])
            split[name].extend(cases)
            filled[name] += 1

    result = {
        "dataset": "RE2-TT",
        "seed": SEED,
        "primary_fault_family": PRIMARY_FAULT_FAMILY,
        "rcaeval_revision": "259ea4167160256a74ad30004aa3d96a998c846e",
        "split": {name: sorted(cases) for name, cases in split.items()},
    }
    Path(out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    for name, cases in result["split"].items():
        per_fault: dict[str, int] = defaultdict(int)
        for case in cases:
            per_fault[case.split("_")[2]] += 1
        print(f"{name:12s} {len(cases):3d}  {dict(sorted(per_fault.items()))}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])