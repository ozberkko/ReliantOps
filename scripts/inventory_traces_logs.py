"""Inventory of RE2-TT traces and logs: structural metadata only.

Counts rows, time coverage, services and service edges. Reads no metric
values and computes no scores. Writes docs/research/re2tt_trace_log_inventory_v1.csv.

Usage:  python scripts/inventory_traces_logs.py <data folder>
"""

import csv
import statistics
import sys
from pathlib import Path

import pyarrow.compute as pc
import pyarrow.parquet as pq

OUTPUT = Path("docs/research/re2tt_trace_log_inventory_v1.csv")
PRE = POST = 720
TOLERANCE = 5
FIELDS = [
    "case", "trace_rows", "trace_first_s", "trace_last_s", "trace_pre_rows",
    "trace_post_rows", "trace_services", "parent_resolved", "service_edges",
    "log_rows", "log_first_s", "log_last_s", "log_pre_rows", "log_post_rows",
    "log_containers",
]


def window_counts(seconds, t0: int) -> tuple[int, int]:
    pre = int(((seconds >= t0 - PRE) & (seconds < t0)).sum())
    post = int(((seconds >= t0) & (seconds <= t0 + POST)).sum())
    return pre, post


def trace_stats(path: Path, t0: int) -> dict:
    columns = ["spanID", "parentSpanID", "serviceName", "startTimeMillis"]
    table = pq.read_table(path, columns=columns)
    seconds = table["startTimeMillis"].to_numpy() // 1000
    pre, post = window_counts(seconds, t0)

    children = table.filter(pc.is_valid(table["parentSpanID"])).select(
        ["parentSpanID", "serviceName"]
    )
    parents = table.select(["spanID", "serviceName"]).rename_columns(
        ["parentSpanID", "parent_service"]
    )
    joined = children.join(parents, keys="parentSpanID", join_type="inner")
    cross = joined.filter(
        pc.not_equal(joined["serviceName"], joined["parent_service"])
    )
    edges = cross.group_by(["parent_service", "serviceName"]).aggregate([])
    resolved = joined.num_rows / children.num_rows if children.num_rows else 0.0
    return {
        "trace_rows": table.num_rows,
        "trace_first_s": int(seconds.min()) - t0,
        "trace_last_s": int(seconds.max()) - t0,
        "trace_pre_rows": pre,
        "trace_post_rows": post,
        "trace_services": len(pc.unique(table["serviceName"])),
        "parent_resolved": round(resolved, 3),
        "service_edges": edges.num_rows,
    }


def log_stats(path: Path, t0: int) -> dict:
    if not path.is_file():
        return {}
    table = pq.read_table(path, columns=["timestamp", "container_name"])
    seconds = table["timestamp"].to_numpy()
    pre, post = window_counts(seconds, t0)
    return {
        "log_rows": table.num_rows,
        "log_first_s": int(seconds.min()) - t0,
        "log_last_s": int(seconds.max()) - t0,
        "log_pre_rows": pre,
        "log_post_rows": post,
        "log_containers": len(pc.unique(table["container_name"])),
    }


def describe(name: str, values: list) -> None:
    print(
        f"{name}: min={min(values)} median={statistics.median(values)} "
        f"max={max(values)}"
    )


def main(root: str) -> None:
    cases = sorted(
        p for p in Path(root).iterdir()
        if p.is_dir() and p.name.startswith("re2tt_")
    )
    if not cases:
        raise SystemExit(f"no re2tt_* case folders found in {root}")

    rows = []
    for index, case in enumerate(cases, start=1):
        t0 = int((case / "inject_time.txt").read_text(encoding="utf-8").strip())
        row = {"case": case.name}
        row.update(trace_stats(case / "traces.parquet", t0))
        row.update(log_stats(case / "logs.parquet", t0))
        rows.append(row)
        if index % 10 == 0:
            print(f"{index}/{len(cases)} cases")

    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    with_logs = [r for r in rows if "log_rows" in r]
    print(f"cases={len(rows)} with_logs={len(with_logs)} -> {OUTPUT}")
    describe("trace rows", [r["trace_rows"] for r in rows])
    describe("trace services", [r["trace_services"] for r in rows])
    describe("parent resolved", [r["parent_resolved"] for r in rows])
    describe("service edges", [r["service_edges"] for r in rows])
    full_traces = sum(
        r["trace_first_s"] <= -PRE + TOLERANCE
        and r["trace_last_s"] >= POST - TOLERANCE
        for r in rows
    )
    full_logs = sum(
        r["log_first_s"] <= -PRE + TOLERANCE
        and r["log_last_s"] >= POST - TOLERANCE
        for r in with_logs
    )
    print(f"traces cover both windows: {full_traces}/{len(rows)}")
    print(f"logs cover both windows: {full_logs}/{len(with_logs)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])