"""Bounded online temporal calibration for cross-modal sensor streams.

This module is intentionally backend-independent.  It estimates a scalar time
 offset from paired residual traces and refuses updates when excitation is
insufficient.  The estimator is a research prototype, not a safety guarantee.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

import numpy as np


class CalibrationState(str, Enum):
    UNCALIBRATED = "UNCALIBRATED"
    CALIBRATING = "CALIBRATING"
    CALIBRATED = "CALIBRATED"
    DRIFTING = "DRIFTING"
    UNOBSERVABLE = "UNOBSERVABLE"
    FAILED = "FAILED"


@dataclass(frozen=True)
class TemporalCalibrationConfig:
    initial_offset_s: float = 0.0
    max_abs_offset_s: float = 0.25
    max_update_s: float = 0.005
    min_observability: float = 0.15
    convergence_tolerance_s: float = 0.001
    convergence_updates: int = 5
    rollback_window: int = 4
    instability_ratio: float = 1.5
    smoothing: float = 0.25


@dataclass(frozen=True)
class TemporalCalibrationResult:
    offset_s: float
    uncertainty_s: float
    observability: float
    state: CalibrationState
    updated: bool
    rolled_back: bool
    residual_before: float
    residual_after: float


@dataclass
class TemporalOffsetEstimator:
    config: TemporalCalibrationConfig = field(default_factory=TemporalCalibrationConfig)
    offset_s: float = field(init=False)
    uncertainty_s: float = field(default=float("inf"), init=False)
    state: CalibrationState = field(default=CalibrationState.UNCALIBRATED, init=False)
    _stable_updates: int = field(default=0, init=False)
    _bad_updates: int = field(default=0, init=False)
    _last_stable_offset_s: float = field(init=False)

    def __post_init__(self) -> None:
        self.offset_s = float(self.config.initial_offset_s)
        self._last_stable_offset_s = self.offset_s

    @staticmethod
    def _normalized_correlation(a: np.ndarray, b: np.ndarray) -> float:
        a0 = a - np.mean(a)
        b0 = b - np.mean(b)
        denom = float(np.linalg.norm(a0) * np.linalg.norm(b0))
        return 0.0 if denom <= 1e-12 else float(np.dot(a0, b0) / denom)

    def estimate_from_traces(
        self,
        reference: Iterable[float],
        target: Iterable[float],
        sample_period_s: float,
        max_lag_samples: int = 20,
    ) -> TemporalCalibrationResult:
        ref = np.asarray(tuple(reference), dtype=float)
        tgt = np.asarray(tuple(target), dtype=float)
        if ref.ndim != 1 or tgt.ndim != 1 or ref.size != tgt.size or ref.size < 8:
            self.state = CalibrationState.FAILED
            raise ValueError("reference and target must be equal-length 1-D traces with >= 8 samples")
        if sample_period_s <= 0:
            raise ValueError("sample_period_s must be positive")

        excitation = min(float(np.std(ref)), float(np.std(tgt)))
        scale = max(float(np.std(ref)), float(np.std(tgt)), 1e-12)
        observability = float(np.clip(excitation / scale, 0.0, 1.0))
        if excitation <= 1e-8 or observability < self.config.min_observability:
            self.state = CalibrationState.UNOBSERVABLE
            return TemporalCalibrationResult(
                self.offset_s,
                self.uncertainty_s,
                observability,
                self.state,
                False,
                False,
                1.0,
                1.0,
            )

        lags = range(-max_lag_samples, max_lag_samples + 1)
        scored: list[tuple[int, float]] = []
        for lag in lags:
            if lag < 0:
                a, b = ref[-lag:], tgt[:lag]
            elif lag > 0:
                a, b = ref[:-lag], tgt[lag:]
            else:
                a, b = ref, tgt
            if a.size >= 6:
                scored.append((lag, self._normalized_correlation(a, b)))
        if not scored:
            self.state = CalibrationState.UNOBSERVABLE
            return TemporalCalibrationResult(
                self.offset_s,
                self.uncertainty_s,
                observability,
                self.state,
                False,
                False,
                1.0,
                1.0,
            )

        scored.sort(key=lambda item: item[1], reverse=True)
        best_lag, best_corr = scored[0]
        second_corr = scored[1][1] if len(scored) > 1 else -1.0
        margin = max(best_corr - second_corr, 0.0)
        observability = float(np.clip(0.5 * observability + 0.5 * margin * 10.0, 0.0, 1.0))
        if best_corr <= 0.0 or observability < self.config.min_observability:
            self.state = CalibrationState.UNOBSERVABLE
            return TemporalCalibrationResult(
                self.offset_s,
                self.uncertainty_s,
                observability,
                self.state,
                False,
                False,
                1.0 - max(best_corr, 0.0),
                1.0 - max(best_corr, 0.0),
            )

        proposed = float(best_lag * sample_period_s)
        delta = float(np.clip(proposed - self.offset_s, -self.config.max_update_s, self.config.max_update_s))
        candidate = float(
            np.clip(
                self.offset_s + self.config.smoothing * delta,
                -self.config.max_abs_offset_s,
                self.config.max_abs_offset_s,
            )
        )
        residual_before = 1.0 - max(best_corr, 0.0)
        residual_after = abs(proposed - candidate) / max(self.config.max_abs_offset_s, 1e-12)

        rolled_back = False
        if residual_after > self.config.instability_ratio * max(residual_before, 1e-6):
            self._bad_updates += 1
        else:
            self._bad_updates = 0
            self.offset_s = candidate
            self.uncertainty_s = max(sample_period_s * (1.0 - observability), sample_period_s / ref.size)

        if self._bad_updates >= self.config.rollback_window:
            self.offset_s = self._last_stable_offset_s
            self.state = CalibrationState.FAILED
            self._bad_updates = 0
            rolled_back = True
        elif abs(proposed - self.offset_s) <= self.config.convergence_tolerance_s:
            self._stable_updates += 1
            if self._stable_updates >= self.config.convergence_updates:
                self.state = CalibrationState.CALIBRATED
                self._last_stable_offset_s = self.offset_s
            else:
                self.state = CalibrationState.CALIBRATING
        else:
            self._stable_updates = 0
            self.state = (
                CalibrationState.DRIFTING
                if self.state is CalibrationState.CALIBRATED
                else CalibrationState.CALIBRATING
            )

        return TemporalCalibrationResult(
            offset_s=self.offset_s,
            uncertainty_s=self.uncertainty_s,
            observability=observability,
            state=self.state,
            updated=not rolled_back and self._bad_updates == 0,
            rolled_back=rolled_back,
            residual_before=residual_before,
            residual_after=residual_after,
        )
