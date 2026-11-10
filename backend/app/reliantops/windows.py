"""Split a metric time axis into the protocol's pre/post injection windows."""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections.abc import Sequence

PRE_SECONDS = 720
POST_SECONDS = 720

STEP_SECONDS = 1


def validate_regular_axis(times: Sequence[int], step: int = STEP_SECONDS) -> None:
    """Raise ValueError unless times are strictly ascending with a fixed step.

    One check covers all failure modes: unsorted values, duplicate timestamps
    and missing seconds all show up as a gap that differs from `step`.
    """
    for previous, current in zip(times, times[1:]):
        gap = current - previous
        if gap == step:
            continue
        if gap == 0:
            raise ValueError(f"duplicate timestamp {current}")
        if gap < 0:
            raise ValueError(f"timestamps not ascending at {current}")
        raise ValueError(
            f"irregular time axis: gap of {gap}s after {previous} (expected {step}s)"
        )


def window_slices(
    times: Sequence[int],
    inject_time: int,
    pre_seconds: int = PRE_SECONDS,
    post_seconds: int = POST_SECONDS,
) -> tuple[slice, slice]:
    """Return (pre, post) slices over a sorted list of unix-second timestamps.

    pre  = [inject_time - pre_seconds, inject_time)
    post = [inject_time, inject_time + post_seconds]  (both ends included)
    """
    validate_regular_axis(times)

    start = bisect_left(times, inject_time - pre_seconds)
    middle = bisect_left(times, inject_time)
    end = bisect_right(times, inject_time + post_seconds)
    return slice(start, middle), slice(middle, end)


def has_full_windows(
    times: Sequence[int],
    inject_time: int,
    pre_seconds: int = PRE_SECONDS,
    post_seconds: int = POST_SECONDS,
) -> bool:
    """True if one-second data fills both windows (720 pre rows, 721 post rows)."""
    pre, post = window_slices(times, inject_time, pre_seconds, post_seconds)
    return (
        pre.stop - pre.start == pre_seconds
        and post.stop - post.start == post_seconds + 1
    )