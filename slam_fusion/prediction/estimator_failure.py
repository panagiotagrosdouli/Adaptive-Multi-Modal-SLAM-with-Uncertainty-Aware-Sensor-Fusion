"""Interpretable short-horizon estimator-failure prediction baseline."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FailureFeatures:
    reliability: float
    reliability_trend: float
    nis_ratio: float
    covariance_growth: float
    feature_survival: float
    registration_fitness: float
    timestamp_health: float
    calibration_drift: float
    cross_modal_disagreement: float


@dataclass(frozen=True, slots=True)
class FailurePrediction:
    horizon_s: float
    risk: float
    level: str
    dominant_factors: tuple[str, ...]
    recommended_action: str


@dataclass(frozen=True, slots=True)
class PredictiveFailureEstimator:
    warning_threshold: float = 0.45
    critical_threshold: float = 0.7

    def predict(self, features: FailureFeatures, horizon_s: float) -> FailurePrediction:
        if horizon_s <= 0.0:
            raise ValueError("horizon_s must be positive")
        terms = {
            "low_reliability": 0.22 * (1.0 - self._unit(features.reliability)),
            "reliability_decline": 0.12 * self._unit(-features.reliability_trend),
            "innovation_inconsistency": 0.14 * self._unit((features.nis_ratio - 1.0) / 2.0),
            "covariance_growth": 0.14 * self._unit(features.covariance_growth),
            "feature_loss": 0.09 * (1.0 - self._unit(features.feature_survival)),
            "poor_registration": 0.07 * (1.0 - self._unit(features.registration_fitness)),
            "timestamp_fault": 0.07 * (1.0 - self._unit(features.timestamp_health)),
            "calibration_drift": 0.07 * self._unit(features.calibration_drift),
            "cross_modal_disagreement": 0.08 * self._unit(features.cross_modal_disagreement),
        }
        horizon_factor = min(1.25, 0.75 + 0.05 * horizon_s)
        risk = min(1.0, sum(terms.values()) * horizon_factor)
        dominant = tuple(
            key for key, value in sorted(terms.items(), key=lambda item: item[1], reverse=True)[:3] if value > 0.0
        )
        if risk >= self.critical_threshold:
            level = "CRITICAL"
            action = "reduce_speed_and_relocalize"
        elif risk >= self.warning_threshold:
            level = "WARNING"
            action = "request_active_sensing"
        else:
            level = "NOMINAL"
            action = "continue"
        return FailurePrediction(horizon_s, risk, level, dominant, action)

    @staticmethod
    def _unit(value: float) -> float:
        return max(0.0, min(1.0, float(value)))
