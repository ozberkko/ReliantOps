"""Tests for the Isolation Forest detector."""

import numpy as np
import pytest
from reliantops.detectors.iforest import IsolationForestDetector


def reference() -> np.ndarray:
    rng = np.random.default_rng(0)
    return rng.normal(size=(500, 3))


def test_outlier_scores_higher_than_inlier() -> None:
    detector = IsolationForestDetector()
    detector.fit(reference())
    scores = detector.score(np.array([[0.0, 0.0, 0.0], [8.0, 8.0, 8.0]]))
    assert scores[1] > scores[0]


def test_same_seed_gives_same_scores() -> None:
    X = reference()
    a, b = IsolationForestDetector(), IsolationForestDetector()
    a.fit(X)
    b.fit(X)
    assert np.array_equal(a.score(X[:50]), b.score(X[:50]))


def test_nan_is_filled_with_reference_median() -> None:
    detector = IsolationForestDetector()
    detector.fit(reference())
    nan_row = np.full(3, np.nan)
    scores = detector.score(np.array([nan_row, detector.median_]))
    assert np.isfinite(scores).all()
    assert scores[0] == pytest.approx(scores[1])


def test_constant_column_is_ignored_and_unfitted_raises() -> None:
    X = np.column_stack([reference()[:, 0], np.ones(500)])
    detector = IsolationForestDetector()
    detector.fit(X)
    low = detector.score(np.array([[0.0, 1.0]]))
    high = detector.score(np.array([[0.0, 100.0]]))
    assert low == pytest.approx(high)
    with pytest.raises(RuntimeError):
        IsolationForestDetector().score(X)