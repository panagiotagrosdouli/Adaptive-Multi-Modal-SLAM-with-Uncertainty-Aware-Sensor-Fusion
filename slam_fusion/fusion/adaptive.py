"""Adaptive sensor fusion policies.

The implemented policy is intentionally simple and auditable: reliability modifies
measurement covariance / information weight; it is not advertised as a learned or
state-of-the-art estimator.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class AdaptiveFusionConfig:
    """Configuration for reliability-to-weight conversion."""

    reliability_exponent: float = 2.0
    min_reliability: float = 1e-3
    max_covariance_scale: float = 1e3
    mahalanobis_threshold: float = 9.21  # chi-square 2D 99% gate by default


class AdaptiveSensorFusion:
    """Compute adaptive fusion weights and covariance inflation factors."""

    def __init__(self, config: AdaptiveFusionConfig | None = None) -> None:
        self.config = config or AdaptiveFusionConfig()

    def precision_weights(
        self, reliabilities: dict[str, float], variances: dict[str, float]
    ) -> dict[str, float]:
        """Return normalized Bayesian-style pseudo-precision weights.

        The score for modality i is ``max(r_i, eps)^gamma / sigma_i^2``.
        """

        if set(reliabilities) != set(variances):
            raise ValueError("reliabilities and variances must share identical modality keys")
        scores: dict[str, float] = {}
        for key, reliability in reliabilities.items():
            variance = variances[key]
            if variance <= 0.0:
                raise ValueError(f"variance for {key} must be positive")
            clipped = min(1.0, max(self.config.min_reliability, float(reliability)))
            scores[key] = clipped**self.config.reliability_exponent / variance
        total = sum(scores.values())
        if total <= 0.0:
            raise ValueError("precision scores collapsed to zero")
        return {key: value / total for key, value in scores.items()}

    def covariance_scale(self, reliability: float) -> float:
        """Return multiplicative covariance inflation from reliability."""

        clipped = min(1.0, max(self.config.min_reliability, float(reliability)))
        scale = 1.0 / (clipped**self.config.reliability_exponent)
        return min(scale, self.config.max_covariance_scale)

    def scaled_covariance(self, covariance: np.ndarray, reliability: float) -> np.ndarray:
        """Inflate a covariance matrix according to reliability."""

        return np.asarray(covariance, dtype=float) * self.covariance_scale(reliability)

    def mahalanobis_gate(self, residual: np.ndarray, covariance: np.ndarray) -> tuple[bool, float]:
        """Apply innovation consistency gating.

        Returns:
            A pair ``(accepted, distance_squared)``.
        """

        residual = np.asarray(residual, dtype=float)
        covariance = np.asarray(covariance, dtype=float)
        if covariance.shape[0] != covariance.shape[1] or covariance.shape[0] != residual.shape[0]:
            raise ValueError("residual and covariance dimensions are inconsistent")
        distance = float(residual.T @ np.linalg.pinv(covariance) @ residual)
        return distance <= self.config.mahalanobis_threshold, distance

    def dropout_weights(
        self, reliabilities: dict[str, float], variances: dict[str, float]
    ) -> dict[str, float]:
        """Handle modality dropout by assigning zero weight to reliability <= 0."""

        active_reliabilities = {k: v for k, v in reliabilities.items() if v > 0.0}
        if not active_reliabilities:
            return {k: 0.0 for k in reliabilities}
        active_variances = {k: variances[k] for k in active_reliabilities}
        active_weights = self.precision_weights(active_reliabilities, active_variances)
        return {k: active_weights.get(k, 0.0) for k in reliabilities}
