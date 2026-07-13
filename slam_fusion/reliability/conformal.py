"""Distribution-free split-conformal intervals for scalar reliability targets.

Coverage is empirical and assumes exchangeability between calibration and test
samples. The implementation does not claim formal safety guarantees under
unmeasured distribution shift.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True, slots=True)
class ConformalEvaluation:
    coverage_target: float
    empirical_coverage: float
    mean_width: float
    sample_count: int


@dataclass
class SplitConformalRegressor:
    """Symmetric split-conformal interval around scalar point predictions."""

    coverage: float = 0.95
    quantile_: float | None = None
    calibration_size_: int = 0

    def __post_init__(self) -> None:
        if not 0.0 < self.coverage < 1.0:
            raise ValueError("coverage must be in (0, 1)")

    @staticmethod
    def _paired(
        predictions: Iterable[float], targets: Iterable[float]
    ) -> tuple[np.ndarray, np.ndarray]:
        pred = np.asarray(tuple(predictions), dtype=float)
        truth = np.asarray(tuple(targets), dtype=float)
        if pred.ndim != 1 or truth.ndim != 1 or pred.size != truth.size or pred.size == 0:
            raise ValueError("predictions and targets must be non-empty equal-length 1-D arrays")
        if not np.all(np.isfinite(pred)) or not np.all(np.isfinite(truth)):
            raise ValueError("predictions and targets must be finite")
        return pred, truth

    def fit(
        self, calibration_predictions: Iterable[float], calibration_targets: Iterable[float]
    ) -> "SplitConformalRegressor":
        predictions, targets = self._paired(calibration_predictions, calibration_targets)
        residuals = np.abs(targets - predictions)
        count = residuals.size
        rank = int(np.ceil((count + 1) * self.coverage))
        rank = min(max(rank, 1), count)
        self.quantile_ = float(np.partition(residuals, rank - 1)[rank - 1])
        self.calibration_size_ = int(count)
        return self

    def predict_interval(self, predictions: Iterable[float]) -> tuple[np.ndarray, np.ndarray]:
        if self.quantile_ is None:
            raise RuntimeError("conformal regressor must be fitted before prediction")
        center = np.asarray(tuple(predictions), dtype=float)
        if center.ndim != 1 or center.size == 0 or not np.all(np.isfinite(center)):
            raise ValueError("predictions must be a non-empty finite 1-D array")
        return center - self.quantile_, center + self.quantile_

    def evaluate(
        self, predictions: Iterable[float], targets: Iterable[float]
    ) -> ConformalEvaluation:
        center, truth = self._paired(predictions, targets)
        lower, upper = self.predict_interval(center)
        covered = (truth >= lower) & (truth <= upper)
        return ConformalEvaluation(
            coverage_target=self.coverage,
            empirical_coverage=float(np.mean(covered)),
            mean_width=float(np.mean(upper - lower)),
            sample_count=int(truth.size),
        )


@dataclass
class RollingConformalRegressor:
    """Rolling-window scaffold for shift-sensitive empirical intervals."""

    coverage: float = 0.95
    window_size: int = 200
    _residuals: list[float] | None = None

    def __post_init__(self) -> None:
        if self.window_size < 8:
            raise ValueError("window_size must be at least 8")
        if not 0.0 < self.coverage < 1.0:
            raise ValueError("coverage must be in (0, 1)")
        self._residuals = []

    def update(self, prediction: float, target: float) -> None:
        if not np.isfinite(prediction) or not np.isfinite(target):
            raise ValueError("prediction and target must be finite")
        assert self._residuals is not None
        self._residuals.append(abs(float(target) - float(prediction)))
        if len(self._residuals) > self.window_size:
            del self._residuals[0]

    @property
    def ready(self) -> bool:
        return self._residuals is not None and len(self._residuals) >= 8

    def interval(self, prediction: float) -> tuple[float, float]:
        if not self.ready:
            raise RuntimeError("at least 8 rolling residuals are required")
        assert self._residuals is not None
        residuals = np.asarray(self._residuals, dtype=float)
        count = residuals.size
        rank = min(int(np.ceil((count + 1) * self.coverage)), count)
        quantile = float(np.partition(residuals, rank - 1)[rank - 1])
        return float(prediction - quantile), float(prediction + quantile)
