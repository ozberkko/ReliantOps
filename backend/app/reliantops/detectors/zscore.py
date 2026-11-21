"""Z-score detector: max absolute z-score over metric columns."""

from __future__ import annotations

import numpy as np


class ZScoreDetector:
    name = "zscore"

    def __init__(self) -> None:
        self.mean_: np.ndarray | None = None
        self.std_: np.ndarray | None = None
        self.usable_: np.ndarray | None = None

    def fit(self, X_ref: np.ndarray) -> None:
        valid = ~np.isnan(X_ref)
        n = valid.sum(axis=0)
        safe_n = np.maximum(n, 1)
        mean = np.where(valid, X_ref, 0.0).sum(axis=0) / safe_n
        centered = np.where(valid, X_ref - mean, 0.0)
        std = np.sqrt((centered**2).sum(axis=0) / safe_n)

        usable = (n >= 2) & (std > 0)
        if not usable.any():
            raise ValueError("no usable columns in reference data")
        self.mean_, self.std_, self.usable_ = mean, std, usable

    def score(self, X: np.ndarray) -> np.ndarray:
        if self.usable_ is None:
            raise RuntimeError("call fit() before score()")
        cols = self.usable_
        z = np.abs(X[:, cols] - self.mean_[cols]) / self.std_[cols]
        return np.nan_to_num(z, nan=0.0).max(axis=1)