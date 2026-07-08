"""Failure prediction for adaptive SLAM supervision.

The predictor implemented here is an interpretable logistic-risk baseline.  It is
not a learned model and it does not claim calibrated probabilities without
validation data.  It converts physically meaningful degradation indicators into a
bounded risk score that can be thresholded by a recovery policy.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


class FailurePredictionError(ValueError):
    """Raised when failure-prediction inputs are invalid."""


@dataclass(frozen=True)
class FailureIndicators:
    """Signals used to estimate the probability of tracking degradation.

    Attributes:
        visual_reliability: Visual reliability in [0, 1].
        inertial_reliability: Inertial reliability in [0, 1].
        reprojection_error: Mean reprojection error in pixels.
        tracked_features: Number of tracked visual features.
    """

    visual_reliability: float
    inertial_reliability: float
    reprojection_error: float
    tracked_features: int


@dataclass(frozen=True)
class FailurePredictorConfig:
    """Configuration for the logistic failure predictor."""

    feature_reference: float = 120.0
    reprojection_reference_px: float = 4.0
    visual_weight: float = 2.2
    inertial_weight: float = 1.2
    reprojection_weight: float = 1.6
    feature_weight: float = 1.4
    bias: float = -2.0


class FailurePredictor:
    """Estimate degradation risk from normalized SLAM health indicators.

    Mathematical formulation:
        z = b + w_v (1 - r_v) + w_i (1 - r_i)
              + w_e min(e / e_ref, 3) + w_f max(0, 1 - n / n_ref)
        p = sigmoid(z)

    where r_v and r_i are modality reliabilities, e is reprojection error, and n
    is tracked feature count.  The terms are monotonic: lower reliability, higher
    reprojection error, and feature depletion increase failure risk.
    """

    def __init__(self, config: FailurePredictorConfig | None = None) -> None:
        self.config = config or FailurePredictorConfig()
        if self.config.feature_reference <= 0.0:
            raise FailurePredictionError("feature_reference must be positive.")
        if self.config.reprojection_reference_px <= 0.0:
            raise FailurePredictionError("reprojection_reference_px must be positive.")

    @staticmethod
    def _bounded(value: float, *, name: str) -> float:
        value = float(value)
        if not np.isfinite(value) or value < 0.0 or value > 1.0:
            raise FailurePredictionError(f"{name} must be finite and in [0, 1].")
        return value

    @staticmethod
    def _non_negative(value: float, *, name: str) -> float:
        value = float(value)
        if not np.isfinite(value) or value < 0.0:
            raise FailurePredictionError(f"{name} must be finite and non-negative.")
        return value

    @staticmethod
    def _sigmoid(logit: float) -> float:
        """Numerically stable logistic sigmoid."""

        if logit >= 0.0:
            exp_neg = np.exp(-logit)
            return float(1.0 / (1.0 + exp_neg))
        exp_pos = np.exp(logit)
        return float(exp_pos / (1.0 + exp_pos))

    def predict(self, indicators: FailureIndicators) -> float:
        """Return an interpretable failure-risk score in [0, 1]."""

        visual = self._bounded(indicators.visual_reliability, name="visual_reliability")
        inertial = self._bounded(indicators.inertial_reliability, name="inertial_reliability")
        reprojection_error = self._non_negative(
            indicators.reprojection_error,
            name="reprojection_error",
        )
        tracked_features = self._non_negative(
            float(indicators.tracked_features),
            name="tracked_features",
        )

        reprojection_term = min(
            reprojection_error / self.config.reprojection_reference_px,
            3.0,
        )
        feature_depletion = max(0.0, 1.0 - tracked_features / self.config.feature_reference)

        logit = (
            self.config.bias
            + self.config.visual_weight * (1.0 - visual)
            + self.config.inertial_weight * (1.0 - inertial)
            + self.config.reprojection_weight * reprojection_term
            + self.config.feature_weight * feature_depletion
        )
        return self._sigmoid(float(logit))
