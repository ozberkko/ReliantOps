"""Turn detector step scores into per-case outcomes (see alert_rule_v1)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from reliantops.windows import PRE_SECONDS

FPR_WINDOW_SECONDS = 60


@dataclass(frozen=True)
class CaseOutcome:
    detected: bool
    mttd: int | None  # seconds from injection to first alert; None if missed
    false_alarm_windows: int
    n_windows: int


def evaluate_case(
    scores: np.ndarray, pre: slice, post: slice, tau: float
) -> CaseOutcome:
    post_alerts = np.flatnonzero(scores[post] >= tau)
    detected = post_alerts.size > 0
    mttd = int(post_alerts[0]) if detected else None

    pre_scores = scores[pre]
    if len(pre_scores) != PRE_SECONDS:
        raise ValueError(f"expected {PRE_SECONDS} pre rows, got {len(pre_scores)}")
    windows = pre_scores.reshape(-1, FPR_WINDOW_SECONDS)
    false_alarms = int((windows >= tau).any(axis=1).sum())

    return CaseOutcome(detected, mttd, false_alarms, len(windows))