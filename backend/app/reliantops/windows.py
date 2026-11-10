"""Split a metric time axis into the protocol's pre/post injection windows."""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections.abc import Sequence

PRE_SECONDS = 720
POST_SECONDS = 720


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
    if any(b < a for a, b in zip(times, times[1:])):
        raise ValueError("times must be sorted ascending")

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