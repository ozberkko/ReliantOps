"""EWMA detector: max standardized EWMA deviation over metric columns."""

from __future__ import annotations

import numpy as np

from reliantops.detectors.zscore import ZScoreDetector

LAMBDA = 0.2


class EWMADetector(ZScoreDetector):
    name = "ewma"

    def __init__(self, lam: float = LAMBDA) -> None:
        if not 0 < lam <= 1:
            raise ValueError("lam must be in (0, 1]")
        super().__init__()
        self.lam = lam

    def score(self, X: np.ndarray) -> np.ndarray:
        if self.usable_ is None:
            raise RuntimeError("call fit() before score()")
        cols = self.usable_
        x = X[:, cols]
        mean = self.mean_[cols]
        limit = self.std_[cols] * np.sqrt(self.lam / (2 - self.lam))

        state = mean.copy()
        scores = np.zeros(len(X))
        for t in range(len(X)):
            row = x[t]
            state = np.where(
                np.isnan(row), state, self.lam * row + (1 - self.lam) * state
            )
            scores[t] = np.max(np.abs(state - mean) / limit)
        return scores