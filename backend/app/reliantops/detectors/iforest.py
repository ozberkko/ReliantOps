"""Isolation Forest detector (see docs/research/ml_detector_rule_v1.md)."""

from __future__ import annotations

import numpy as np
from sklearn.ensemble import IsolationForest

from reliantops.detectors.zscore import ZScoreDetector


class IsolationForestDetector:
    name = "iforest"

    def __init__(
        self, n_estimators: int = 100, max_samples: int = 256, seed: int = 42
    ) -> None:
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.seed = seed
        self.usable_: np.ndarray | None = None
        self.median_: np.ndarray | None = None
        self.model_: IsolationForest | None = None

    def fit(self, X_ref: np.ndarray) -> None:
        columns = ZScoreDetector()
        columns.fit(X_ref)  # same usable-column rule as the baselines
        usable = columns.usable_

        ref = X_ref[:, usable]
        median = np.nanmedian(ref, axis=0)
        filled = np.where(np.isnan(ref), median, ref)

        self.model_ = IsolationForest(
            n_estimators=self.n_estimators,
            max_samples=self.max_samples,
            random_state=self.seed,
        ).fit(filled)
        self.usable_, self.median_ = usable, median

    def score(self, X: np.ndarray) -> np.ndarray:
        if self.model_ is None:
            raise RuntimeError("call fit() before score()")
        x = X[:, self.usable_]
        filled = np.where(np.isnan(x), self.median_, x)
        return -self.model_.score_samples(filled)