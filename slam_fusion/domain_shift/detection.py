"""Transparent rolling distribution-shift detection for estimator diagnostics."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

import numpy as np


class ShiftState(str, Enum):
    NOMINAL = "NOMINAL"
    SUSPECTED = "SUSPECTED"
    DETECTED = "DETECTED"


@dataclass(frozen=True, slots=True)
class ShiftResult:
    state: ShiftState
    statistic: float
    threshold: float
    confidence_multiplier: float
    reference_mean: float
    current_mean: float
    reference_std: float
    current_std: float


@dataclass
class RollingMomentShiftDetector:
    """Detect shifts using standardized changes in rolling mean and scale.

    This is a transparent research baseline rather than a calibrated hypothesis test.
    The returned confidence multiplier can conservatively reduce downstream reliability.
    """

    reference: np.ndarray
    window_size: int = 32
    suspected_threshold: float = 1.5
    detected_threshold: float = 3.0
    minimum_confidence: float = 0.2
    _window: deque[float] = field(init=False)

    def __post_init__(self) -> None:
        reference = np.asarray(self.reference, dtype=float).reshape(-1)
        if reference.size < 8 or not np.all(np.isfinite(reference)):
            raise ValueError("reference must contain at least eight finite samples")
        if self.window_size < 4:
            raise ValueError("window_size must be at least four")
        if not 0.0 < self.minimum_confidence <= 1.0:
            raise ValueError("minimum_confidence must be in (0, 1]")
        self.reference = reference
        self._window = deque(maxlen=self.window_size)

    def update(self, values: float | Iterable[float]) -> ShiftResult:
        if np.isscalar(values):
            samples = np.asarray([values], dtype=float)
        else:
            samples = np.asarray(tuple(values), dtype=float).reshape(-1)
        if samples.size == 0 or not np.all(np.isfinite(samples)):
            raise ValueError("values must contain finite samples")
        self._window.extend(float(value) for value in samples)

        reference_mean = float(np.mean(self.reference))
        reference_std = max(float(np.std(self.reference)), 1e-9)
        if len(self._window) < self.window_size:
            return ShiftResult(
                state=ShiftState.NOMINAL,
                statistic=0.0,
                threshold=self.detected_threshold,
                confidence_multiplier=1.0,
                reference_mean=reference_mean,
                current_mean=float(np.mean(self._window)),
                reference_std=reference_std,
                current_std=float(np.std(self._window)),
            )

        current = np.asarray(self._window, dtype=float)
        current_mean = float(np.mean(current))
        current_std = float(np.std(current))
        mean_shift = abs(current_mean - reference_mean) / reference_std
        scale_shift = abs(current_std - reference_std) / reference_std
        statistic = float(np.hypot(mean_shift, scale_shift))

        if statistic >= self.detected_threshold:
            state = ShiftState.DETECTED
        elif statistic >= self.suspected_threshold:
            state = ShiftState.SUSPECTED
        else:
            state = ShiftState.NOMINAL

        confidence_multiplier = float(
            np.clip(1.0 / (1.0 + statistic), self.minimum_confidence, 1.0)
        )
        return ShiftResult(
            state=state,
            statistic=statistic,
            threshold=self.detected_threshold,
            confidence_multiplier=confidence_multiplier,
            reference_mean=reference_mean,
            current_mean=current_mean,
            reference_std=reference_std,
            current_std=current_std,
        )
