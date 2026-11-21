"""Load a RE2-TT case's metrics as a plain numpy matrix (no event objects)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

from reliantops.windows import validate_regular_axis, window_slices


@dataclass(frozen=True)
class MetricSeries:
    case: str
    times: np.ndarray  # (T,) int64 unix seconds
    columns: tuple[str, ...]  # M metric names, sorted
    values: np.ndarray  # (T, M) float64, NaN = missing
    inject_time: int
    pre: slice  # rows in [t0 - 720, t0)
    post: slice  # rows in [t0, t0 + 720]


def load_metric_series(
    case_dir: Path, columns: Sequence[str] | None = None
) -> MetricSeries:
    case_dir = Path(case_dir)
    inject = int((case_dir / "inject_time.txt").read_text(encoding="utf-8").strip())
    table = pq.read_table(case_dir / "metrics.parquet")

    times = table.column("time").to_pylist()
    if any(t is None for t in times):
        raise ValueError(f"{case_dir.name}: null values in time column")
    validate_regular_axis(times)
    pre, post = window_slices(times, inject)

    available = {n for n in table.column_names if n != "time"}
    if columns is None:
        columns = tuple(sorted(available))
    else:
        missing = sorted(set(columns) - available)
        if missing:
            raise ValueError(f"{case_dir.name}: missing columns {missing[:3]}")
        columns = tuple(columns)
    values = np.column_stack(
        [table.column(n).to_numpy(zero_copy_only=False) for n in columns]
    ).astype(np.float64)
    values[~np.isfinite(values)] = np.nan

    return MetricSeries(
        case=case_dir.name,
        times=np.asarray(times, dtype=np.int64),
        columns=columns,
        values=values,
        inject_time=inject,
        pre=pre,
        post=post,
    )