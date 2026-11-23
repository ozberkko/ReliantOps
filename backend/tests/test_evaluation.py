"""Tests for per-case evaluation."""

import numpy as np
import pytest
from reliantops.evaluation import evaluate_case

PRE = slice(0, 720)
POST = slice(720, 1441)


def zeros() -> np.ndarray:
    return np.zeros(1441)


def test_detection_and_mttd() -> None:
    scores = zeros()
    scores[725] = 5.0
    scores[900] = 5.0
    outcome = evaluate_case(scores, PRE, POST, tau=3.0)
    assert outcome.detected
    assert outcome.mttd == 5
    assert outcome.false_alarm_windows == 0


def test_missed_case_has_no_mttd() -> None:
    outcome = evaluate_case(zeros(), PRE, POST, tau=3.0)
    assert not outcome.detected
    assert outcome.mttd is None


def test_false_alarms_are_counted_per_window() -> None:
    scores = zeros()
    scores[10] = scores[11] = 5.0  # same 60 s window
    scores[130] = 5.0  # another window
    outcome = evaluate_case(scores, PRE, POST, tau=3.0)
    assert outcome.false_alarm_windows == 2
    assert outcome.n_windows == 12


def test_score_equal_to_tau_is_an_alert() -> None:
    scores = zeros()
    scores[720] = 3.0
    assert evaluate_case(scores, PRE, POST, tau=3.0).mttd == 0


def test_wrong_pre_length_raises() -> None:
    with pytest.raises(ValueError):
        evaluate_case(zeros(), slice(0, 700), POST, tau=3.0)