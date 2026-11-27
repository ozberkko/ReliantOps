"""Per-service Isolation Forest (post-hoc v2, see ml_detector_rule_v2.md)."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

import numpy as np
from sklearn.ensemble import IsolationForest

from reliantops.detectors.zscore import ZScoreDetector


class ServiceIsolationForestDetector:
    name = "iforest_v2"

    def __init__(
        self,
        columns: Sequence[str],
        n_estimators: int = 100,
        max_samples: int = 256,
        seed: int = 42,
    ) -> None:
        self.columns = list(columns)
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.seed = seed
        self.groups_: list[np.ndarray] = []
        self.models_: list[IsolationForest] = []
        self.median_: np.ndarray | None = None
        self.score_mean_: np.ndarray | None = None
        self.score_std_: np.ndarray | None = None

    def fit(self, X_ref: np.ndarray) -> None:
        usable = ZScoreDetector()
        usable.fit(X_ref)  # same usable-column rule as the other detectors

        by_service: dict[str, list[int]] = defaultdict(list)
        for index, name in enumerate(self.columns):
            if usable.usable_[index]:
                by_service[name.split("_", 1)[0]].append(index)

        median = np.full(X_ref.shape[1], np.nan)
        median[usable.usable_] = np.nanmedian(X_ref[:, usable.usable_], axis=0)
        filled = np.where(np.isnan(X_ref), median, X_ref)

        groups, models, means, stds = [], [], [], []
        for service in sorted(by_service):
            cols = np.array(by_service[service])
            model = IsolationForest(
                n_estimators=self.n_estimators,
                max_samples=self.max_samples,
                random_state=self.seed,
            ).fit(filled[:, cols])
            ref_scores = -model.score_samples(filled[:, cols])
            groups.append(cols)
            models.append(model)
            means.append(ref_scores.mean())
            stds.append(max(ref_scores.std(), 1e-12))

        self.groups_, self.models_, self.median_ = groups, models, median
        self.score_mean_, self.score_std_ = np.array(means), np.array(stds)

    def score(self, X: np.ndarray) -> np.ndarray:
        if not self.models_:
            raise RuntimeError("call fit() before score()")
        filled = np.where(np.isnan(X), self.median_, X)
        per_service = [
            (-model.score_samples(filled[:, cols]) - mean) / std
            for model, cols, mean, std in zip(
                self.models_, self.groups_, self.score_mean_, self.score_std_
            )
        ]
        return np.max(per_service, axis=0)