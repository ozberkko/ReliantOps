from __future__ import annotations

from typing import Protocol

import numpy as np


class Detector(Protocol):
    name: str

    def fit(self, X_ref: np.ndarray) -> None:
        """Fit on a (T, M) reference matrix of normal metric data."""

    def score(self, X: np.ndarray) -> np.ndarray:
        """Map a (T, M) matrix to a (T,) anomaly score per time step."""