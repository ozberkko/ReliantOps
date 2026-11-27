"""Tests for the per-service Isolation Forest detector."""

import numpy as np
import pytest
from reliantops.detectors.iforest_service import ServiceIsolationForestDetector

COLUMNS = [f"svc{s}_m{m}" for s in range(3) for m in range(3)]


def reference() -> np.ndarray:
    rng = np.random.default_rng(0)
    return rng.normal(size=(500, 9))


def test_columns_are_grouped_by_service() -> None:
    detector = ServiceIsolationForestDetector(COLUMNS)
    detector.fit(reference())
    assert [len(g) for g in detector.groups_] == [3, 3, 3]


def test_single_column_shift_is_scored_above_normal() -> None:
    detector = ServiceIsolationForestDetector(COLUMNS)
    X = reference()
    detector.fit(X)
    shifted = X[:50].copy()
    shifted[:, 4] += 8.0
    assert detector.score(shifted).mean() > detector.score(X[:50]).mean() + 1.0


def test_same_seed_gives_same_scores() -> None:
    X = reference()
    a = ServiceIsolationForestDetector(COLUMNS)
    b = ServiceIsolationForestDetector(COLUMNS)
    a.fit(X)
    b.fit(X)
    assert np.array_equal(a.score(X[:50]), b.score(X[:50]))


def test_nan_row_is_finite_and_unfitted_raises() -> None:
    detector = ServiceIsolationForestDetector(COLUMNS)
    with pytest.raises(RuntimeError):
        detector.score(reference())
    detector.fit(reference())
    assert np.isfinite(detector.score(np.full((2, 9), np.nan))).all()