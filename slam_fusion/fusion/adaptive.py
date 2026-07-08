"""Adaptive sensor-fusion policies for uncertainty-aware SLAM.

The policy implemented here is intentionally auditable. Reliability scores are not
interpreted as calibrated probabilities; they are bounded diagnostic quantities that
modify measurement information. This makes the module suitable as a reproducible
baseline for comparing fixed-covariance fusion, adaptive covariance inflation, and
learned reliability models.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


class AdaptiveFusionError(ValueError):
    """Raised when adaptive-fusion inputs are physically or numerically invalid."""


@dataclass(frozen=True, slots=True)
class AdaptiveFusionConfig:
    """Configuration for reliability-to-information conversion.

    Attributes:
        reliability_exponent: Exponent :math:`\gamma` in the reliability precision model.
        min_reliability: Lower bound that prevents infinite covariance inflation.
        max_covariance_scale: Upper bound on reliability-induced covariance inflation.
        mahalanobis_threshold: Squared Mahalanobis gate. The default corresponds to a
            99% chi-square gate for a two-dimensional innovation.
        covariance_jitter: Initial diagonal jitter used only for numerically singular
            positive-semidefinite covariance matrices.
        max_jitter_attempts: Number of geometric jitter increases before failing.
    """

    reliability_exponent: float = 2.0
    min_reliability: float = 1e-3
    max_covariance_scale: float = 1e3
    mahalanobis_threshold: float = 9.21
    covariance_jitter: float = 1e-9
    max_jitter_attempts: int = 6

    def __post_init__(self) -> None:
        """Validate configuration ranges that affect estimator consistency."""

        if not np.isfinite(self.reliability_exponent) or self.reliability_exponent <= 0.0:
            raise AdaptiveFusionError("reliability_exponent must be finite and positive")
        if not np.isfinite(self.min_reliability) or not 0.0 < self.min_reliability <= 1.0:
            raise AdaptiveFusionError("min_reliability must be finite and in (0, 1]")
        if not np.isfinite(self.max_covariance_scale) or self.max_covariance_scale < 1.0:
            raise AdaptiveFusionError("max_covariance_scale must be finite and >= 1")
        if not np.isfinite(self.mahalanobis_threshold) or self.mahalanobis_threshold <= 0.0:
            raise AdaptiveFusionError("mahalanobis_threshold must be finite and positive")
        if not np.isfinite(self.covariance_jitter) or self.covariance_jitter <= 0.0:
            raise AdaptiveFusionError("covariance_jitter must be finite and positive")
        if self.max_jitter_attempts < 0:
            raise AdaptiveFusionError("max_jitter_attempts must be non-negative")


class AdaptiveSensorFusion:
    """Compute adaptive fusion weights, covariance inflation, and consistency gates.

    Mathematical model:
        For modality :math:`i`, a bounded reliability estimate :math:`r_i \in [0, 1]`
        modifies a nominal variance :math:`\sigma_i^2` through the pseudo-precision

        .. math::

            p_i = \frac{\max(r_i, \epsilon)^\gamma}{\sigma_i^2},\quad
            w_i = \frac{p_i}{\sum_j p_j}.

        For covariance-based estimators, this is equivalent to inflating the
        measurement covariance by

        .. math::

            \tilde{\Sigma}_i = \Sigma_i / \max(r_i, \epsilon)^\gamma.

    Probabilistic interpretation:
        The weights approximate relative information contributions under Gaussian
        residual assumptions. The implementation deliberately avoids pseudo-inverse
        gates because pseudo-inverses can silently accept rank-deficient innovation
        covariances and produce overconfident consistency decisions.

    Complexity:
        Weight computation is :math:`O(M)` for :math:`M` modalities. Mahalanobis
        gating is :math:`O(d^3)` because it uses a Cholesky factorization of the
        :math:`d \times d` innovation covariance.
    """

    def __init__(self, config: AdaptiveFusionConfig | None = None) -> None:
        self.config = config or AdaptiveFusionConfig()

    @staticmethod
    def _validate_reliability(value: float, *, name: str) -> float:
        """Return a finite reliability value clipped to the physically valid interval."""

        reliability = float(value)
        if not np.isfinite(reliability):
            raise AdaptiveFusionError(f"reliability for {name} must be finite")
        return min(1.0, max(0.0, reliability))

    @staticmethod
    def _validate_variance(value: float, *, name: str) -> float:
        """Return a finite positive scalar variance."""

        variance = float(value)
        if not np.isfinite(variance) or variance <= 0.0:
            raise AdaptiveFusionError(f"variance for {name} must be finite and positive")
        return variance

    @staticmethod
    def _validate_covariance(covariance: np.ndarray, residual_dim: int | None = None) -> np.ndarray:
        """Return a finite square covariance matrix with optional residual-dimension check."""

        cov = np.asarray(covariance, dtype=float)
        if cov.ndim != 2 or cov.shape[0] != cov.shape[1]:
            raise AdaptiveFusionError("covariance must be a square matrix")
        if residual_dim is not None and cov.shape[0] != residual_dim:
            raise AdaptiveFusionError("residual and covariance dimensions are inconsistent")
        if not np.all(np.isfinite(cov)):
            raise AdaptiveFusionError("covariance contains non-finite values")
        return 0.5 * (cov + cov.T)

    def _regularized_cholesky(self, covariance: np.ndarray) -> tuple[np.ndarray, float]:
        """Compute a Cholesky factor, adding minimal diagonal jitter if necessary.

        The jitter path is reserved for matrices that are theoretically positive
        semidefinite but numerically singular. Strongly indefinite matrices are rejected
        because accepting them would invalidate the Gaussian innovation model.
        """

        cov = self._validate_covariance(covariance)
        identity = np.eye(cov.shape[0], dtype=float)
        jitter = 0.0
        for attempt in range(self.config.max_jitter_attempts + 1):
            try:
                factor = np.linalg.cholesky(cov + jitter * identity)
                return factor, jitter
            except np.linalg.LinAlgError as exc:
                if attempt == self.config.max_jitter_attempts:
                    raise AdaptiveFusionError(
                        "covariance is not positive definite after adaptive jitter"
                    ) from exc
                jitter = self.config.covariance_jitter if jitter == 0.0 else jitter * 10.0
        raise AdaptiveFusionError("unreachable Cholesky regularization failure")

    def precision_weights(
        self, reliabilities: dict[str, float], variances: dict[str, float]
    ) -> dict[str, float]:
        """Return normalized pseudo-precision weights for active modalities.

        Args:
            reliabilities: Mapping from modality name to reliability score.
            variances: Mapping from modality name to nominal scalar variance.

        Returns:
            A dictionary whose values are non-negative and sum to one.

        Raises:
            AdaptiveFusionError: If modality keys, reliabilities, or variances are invalid.
        """

        if not reliabilities:
            raise AdaptiveFusionError("at least one modality is required")
        if set(reliabilities) != set(variances):
            raise AdaptiveFusionError("reliabilities and variances must share identical modality keys")

        scores: dict[str, float] = {}
        for key, reliability in reliabilities.items():
            clipped = max(
                self.config.min_reliability,
                self._validate_reliability(reliability, name=key),
            )
            variance = self._validate_variance(variances[key], name=key)
            scores[key] = clipped**self.config.reliability_exponent / variance

        total = float(sum(scores.values()))
        if total <= 0.0 or not np.isfinite(total):
            raise AdaptiveFusionError("precision scores collapsed to a non-finite value")
        return {key: value / total for key, value in scores.items()}

    def covariance_scale(self, reliability: float) -> float:
        """Return multiplicative covariance inflation from a bounded reliability score."""

        clipped = max(
            self.config.min_reliability,
            self._validate_reliability(reliability, name="measurement"),
        )
        scale = 1.0 / (clipped**self.config.reliability_exponent)
        return min(float(scale), self.config.max_covariance_scale)

    def scaled_covariance(self, covariance: np.ndarray, reliability: float) -> np.ndarray:
        """Inflate a covariance matrix according to reliability and preserve symmetry."""

        cov = self._validate_covariance(covariance)
        return cov * self.covariance_scale(reliability)

    def mahalanobis_distance_squared(self, residual: np.ndarray, covariance: np.ndarray) -> float:
        """Compute :math:`r^T S^{-1} r` using Cholesky solves instead of a pseudo-inverse."""

        r = np.asarray(residual, dtype=float).reshape(-1)
        if r.ndim != 1 or not np.all(np.isfinite(r)):
            raise AdaptiveFusionError("residual must be a finite vector")
        cov = self._validate_covariance(covariance, residual_dim=r.shape[0])
        factor, _ = self._regularized_cholesky(cov)
        whitened = np.linalg.solve(factor, r)
        return float(whitened.T @ whitened)

    def mahalanobis_gate(self, residual: np.ndarray, covariance: np.ndarray) -> tuple[bool, float]:
        """Apply innovation consistency gating.

        Returns:
            A pair ``(accepted, distance_squared)``. Acceptance means that the
            innovation lies inside the configured chi-square consistency gate.
        """

        distance = self.mahalanobis_distance_squared(residual, covariance)
        return distance <= self.config.mahalanobis_threshold, distance

    def dropout_weights(
        self, reliabilities: dict[str, float], variances: dict[str, float]
    ) -> dict[str, float]:
        """Handle complete modality dropout by assigning zero weight to inactive sensors."""

        active_reliabilities = {
            key: value
            for key, value in reliabilities.items()
            if self._validate_reliability(value, name=key) > 0.0
        }
        if not active_reliabilities:
            return {key: 0.0 for key in reliabilities}
        active_variances = {key: variances[key] for key in active_reliabilities}
        active_weights = self.precision_weights(active_reliabilities, active_variances)
        return {key: active_weights.get(key, 0.0) for key in reliabilities}
