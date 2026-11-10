"""Tests for pre/post injection window slicing."""

import pytest
from reliantops.windows import has_full_windows, window_slices

INJECT = 10_000


def make_times(before: int = 720, after: int = 720) -> list[int]:
    return list(range(INJECT - before, INJECT + after + 1))


def test_window_slices_follow_protocol_boundaries() -> None:
    times = make_times()
    pre, post = window_slices(times, INJECT)

    assert len(times[pre]) == 720
    assert len(times[post]) == 721
    assert times[pre][-1] == INJECT - 1
    assert times[post][0] == INJECT
    assert times[post][-1] == INJECT + 720


def test_rows_outside_the_windows_are_excluded() -> None:
    times = make_times(before=900, after=900)
    pre, post = window_slices(times, INJECT)

    assert times[pre][0] == INJECT - 720
    assert times[post][-1] == INJECT + 720


def test_full_windows_are_detected() -> None:
    assert has_full_windows(make_times(), INJECT)
    assert not has_full_windows(make_times(before=600), INJECT)
    assert not has_full_windows(make_times(after=719), INJECT)


def test_unsorted_times_are_rejected() -> None:
    with pytest.raises(ValueError):
        window_slices([3, 2, 1], 2)

def test_duplicate_timestamp_is_rejected() -> None:
    times = make_times()
    times[100] = times[99]

    with pytest.raises(ValueError, match="duplicate"):
        window_slices(times, INJECT)


def test_missing_second_is_rejected() -> None:
    times = make_times()
    del times[100]

    with pytest.raises(ValueError, match="gap of 2s"):
        window_slices(times, INJECT)


def test_duplicate_plus_gap_with_correct_row_count_is_rejected() -> None:
    # same number of rows as a valid axis, but irregular
    times = make_times()
    del times[100]
    times.insert(100, times[100])

    with pytest.raises(ValueError):
        window_slices(times, INJECT)


def test_unsorted_message_names_the_problem() -> None:
    with pytest.raises(ValueError, match="not ascending"):
        window_slices([1, 2, 1, 2], 2)