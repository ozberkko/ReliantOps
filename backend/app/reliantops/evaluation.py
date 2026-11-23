"""Turn detector step scores into per-case outcomes (see alert_rule_v1)."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from statistics import mean, median

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


@dataclass(frozen=True)
class Summary:
    n_cases: int
    recall: float
    missed: int
    mttd_mean: float | None
    mttd_median: float | None
    fpr: float


def summarize(outcomes: Sequence[CaseOutcome]) -> Summary:
    if not outcomes:
        raise ValueError("no outcomes to summarize")
    mttds = [o.mttd for o in outcomes if o.mttd is not None]
    windows = sum(o.n_windows for o in outcomes)
    false_alarms = sum(o.false_alarm_windows for o in outcomes)
    return Summary(
        n_cases=len(outcomes),
        recall=len(mttds) / len(outcomes),
        missed=len(outcomes) - len(mttds),
        mttd_mean=mean(mttds) if mttds else None,
        mttd_median=median(mttds) if mttds else None,
        fpr=false_alarms / windows,
    )


def fault_family(case_name: str) -> str:
    # re2tt_<service>_<fault>_<index>; service names contain '-', not '_'
    parts = case_name.split("_")
    if len(parts) != 4 or parts[0] != "re2tt":
        raise ValueError(f"unexpected case name: {case_name}")
    return parts[2]


def summarize_by_family(
    outcomes: Mapping[str, CaseOutcome],
) -> dict[str, Summary]:
    groups: dict[str, list[CaseOutcome]] = defaultdict(list)
    for name, outcome in outcomes.items():
        groups[fault_family(name)].append(outcome)
    return {family: summarize(group) for family, group in sorted(groups.items())}