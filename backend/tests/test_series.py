"""Tests for the metric series loader."""

from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from reliantops.series import load_metric_series

START = 1_000
INJECT = START + 720
ROWS = 1441


def ramp() -> list[float | None]:
    return [float(i) for i in range(ROWS)]


def make_case(tmp_path: Path, columns: dict, times: list | None = None) -> Path:
    case = tmp_path / "re2tt_demo_cpu_1"
    case.mkdir(parents=True)
    (case / "inject_time.txt").write_text(f"{INJECT}\n", encoding="utf-8")
    if times is None:
        times = list(range(START, START + ROWS))
    pq.write_table(pa.table({"time": times, **columns}), case / "metrics.parquet")
    return case


def test_loads_sorted_columns_and_windows(tmp_path: Path) -> None:
    case = make_case(tmp_path, {"b_cpu": ramp(), "a_mem": ramp()})
    series = load_metric_series(case)
    assert series.columns == ("a_mem", "b_cpu")
    assert series.values.shape == (ROWS, 2)
    assert series.values.dtype == np.float64
    assert series.inject_time == INJECT
    assert series.pre == slice(0, 720)
    assert series.post == slice(720, 1441)


def test_null_and_inf_become_nan(tmp_path: Path) -> None:
    values = ramp()
    values[5] = None
    values[6] = float("inf")
    series = load_metric_series(make_case(tmp_path, {"a_cpu": values}))
    assert np.isnan(series.values[5, 0])
    assert np.isnan(series.values[6, 0])
    assert int(np.isnan(series.values).sum()) == 2


def test_requested_columns_keep_given_order(tmp_path: Path) -> None:
    case = make_case(tmp_path, {"a_mem": ramp(), "b_cpu": ramp()})
    series = load_metric_series(case, ["b_cpu", "a_mem"])
    assert series.columns == ("b_cpu", "a_mem")


def test_missing_requested_column_raises(tmp_path: Path) -> None:
    case = make_case(tmp_path, {"a_mem": ramp()})
    with pytest.raises(ValueError, match="missing columns"):
        load_metric_series(case, ["a_mem", "zzz_cpu"])


def test_bad_time_axis_raises(tmp_path: Path) -> None:
    gap = list(range(START, START + ROWS))
    gap[100] += 5  # one timestamp jumps ahead -> irregular axis
    with pytest.raises(ValueError, match="irregular"):
        load_metric_series(make_case(tmp_path, {"a_cpu": ramp()}, gap))

    nulls: list = list(range(START, START + ROWS))
    nulls[3] = None
    with pytest.raises(ValueError, match="null"):
        load_metric_series(make_case(tmp_path / "x", {"a_cpu": ramp()}, nulls))