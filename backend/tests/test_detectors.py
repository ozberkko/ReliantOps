"""Tests for the z-score detector."""

import numpy as np
import pytest
from reliantops.detectors.zscore import ZScoreDetector


def reference() -> np.ndarray:
    rng = np.random.default_rng(0)
    return rng.normal(size=(500, 3))


def test_spike_scores_higher_than_normal_data() -> None:
    detector = ZScoreDetector()
    detector.fit(reference())
    scores = detector.score(np.array([[0.0, 0.0, 0.0], [0.0, 10.0, 0.0]]))
    assert scores[1] > 5 > scores[0]


def test_nan_is_ignored_and_all_nan_row_scores_zero() -> None:
    detector = ZScoreDetector()
    detector.fit(reference())
    scores = detector.score(np.array([[np.nan, 10.0, np.nan], [np.nan] * 3]))
    assert scores[0] > 5
    assert scores[1] == 0.0


def test_constant_column_is_not_used() -> None:
    X = np.column_stack([reference()[:, 0], np.ones(500)])
    detector = ZScoreDetector()
    detector.fit(X)
    assert detector.usable_.tolist() == [True, False]
    with pytest.raises(ValueError):
        ZScoreDetector().fit(np.ones((10, 2)))