"""Tests for per-case evaluation."""

import numpy as np
import pytest
from reliantops.evaluation import (
    CaseOutcome,
    evaluate_case,
    fault_family,
    select_tau,
    summarize,
    summarize_by_family,
    window_maxima,
)

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

def outcome(mttd: int | None, false_alarms: int = 0) -> CaseOutcome:
    return CaseOutcome(mttd is not None, mttd, false_alarms, 12)


def test_summary_ignores_missed_cases_in_mttd() -> None:
    s = summarize([outcome(10), outcome(30), outcome(None)])
    assert s.recall == pytest.approx(2 / 3)
    assert s.missed == 1
    assert s.mttd_mean == 20
    assert s.mttd_median == 20


def test_fpr_pools_windows_across_cases() -> None:
    s = summarize([outcome(1, 3), outcome(1, 0)])
    assert s.fpr == pytest.approx(3 / 24)


def test_all_missed_has_no_mttd() -> None:
    s = summarize([outcome(None)])
    assert s.recall == 0
    assert s.mttd_mean is None


def test_fault_family_and_grouping() -> None:
    assert fault_family("re2tt_ts-auth-service_cpu_2") == "cpu"
    with pytest.raises(ValueError):
        fault_family("bad_name")
    result = summarize_by_family(
        {
            "re2tt_ts-a-service_cpu_1": outcome(5),
            "re2tt_ts-a-service_mem_1": outcome(None),
        }
    )
    assert list(result) == ["cpu", "mem"]
    assert result["mem"].recall == 0

def test_window_maxima_takes_max_of_each_60s_window() -> None:
    scores = np.zeros(720)
    scores[5] = 2.0
    scores[130] = 7.0
    maxima = window_maxima(scores)
    assert len(maxima) == 12
    assert maxima[0] == 2.0
    assert maxima[2] == 7.0


def test_select_tau_gives_smallest_threshold_within_limit() -> None:
    maxima = np.arange(100, dtype=float)
    tau = select_tau(maxima)
    assert tau == 95.0
    assert np.mean(maxima >= tau) <= 0.05
    assert np.mean(maxima >= tau - 1) > 0.05


def test_select_tau_with_ties_goes_above_the_maximum() -> None:
    tau = select_tau(np.ones(100))
    assert tau > 1.0