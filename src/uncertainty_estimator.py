"""Uncertainty estimation for adaptive multi-modal SLAM.

This module converts frontend health signals into modality reliability estimates
and provides small probabilistic utilities used by benchmark and visualization
code.  The reliability estimator remains intentionally transparent: it is a
research baseline that should be compared against calibrated Bayesian or learned
uncertainty models, not a black-box claim of optimality.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


class UncertaintyEstimationError(ValueError):
    """Raised when uncertainty inputs are invalid."""


@dataclass(frozen=True)
class VisualQualitySignals:
    """Signals that describe the reliability of the visual frontend.

    Attributes:
        tracked_features: Number of successfully tracked map/image features.
        mean_reprojection_error: Mean reprojection residual in pixels.
        image_brightness: Normalized image brightness in [0, 1].
        image_sharpness: Normalized sharpness or blur score in [0, 1].
        optical_flow_consistency: Optional normalized flow consistency in [0, 1].
    """

    tracked_features: int
    mean_reprojection_error: float
    image_brightness: float
    image_sharpness: float
    optical_flow_consistency: Optional[float] = None


@dataclass(frozen=True)
class InertialQualitySignals:
    """Signals that describe the reliability of inertial integration.

    Attributes:
        acceleration_norm: Magnitude of measured acceleration in m/s^2.
        gyro_norm: Magnitude of measured angular velocity in rad/s.
        preintegration_residual: Optional normalized IMU preintegration residual.
        estimated_bias_norm: Optional normalized bias magnitude or instability.
    """

    acceleration_norm: float
    gyro_norm: float
    preintegration_residual: Optional[float] = None
    estimated_bias_norm: Optional[float] = None


@dataclass(frozen=True)
class ModalityReliability:
    """Reliability scores used by the adaptive fusion module."""

    visual: float
    inertial: float
    event: Optional[float] = None


@dataclass(frozen=True)
class GaussianUncertainty:
    """Differential-entropy and Mahalanobis summary for a covariance matrix."""

    dimension: int
    log_determinant: float
    differential_entropy: float
    condition_number: float


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    """Clamp a finite value into a fixed numeric interval."""

    value = float(value)
    if not np.isfinite(value):
        raise UncertaintyEstimationError("Cannot clamp NaN or infinite value.")
    if lower > upper:
        raise UncertaintyEstimationError("lower must be <= upper.")
    return max(lower, min(upper, value))


def _finite_non_negative(value: float, *, name: str) -> float:
    value = float(value)
    if not np.isfinite(value) or value < 0.0:
        raise UncertaintyEstimationError(f"{name} must be finite and non-negative.")
    return value


def _bounded_optional(value: Optional[float], *, name: str) -> Optional[float]:
    if value is None:
        return None
    return clamp(value)


def ensure_positive_definite(
    covariance: np.ndarray,
    *,
    jitter: float = 1e-9,
) -> np.ndarray:
    """Return a symmetric positive-definite covariance with minimal jitter.

    Args:
        covariance: Square covariance matrix.
        jitter: Initial diagonal regularization used if the matrix is nearly
            singular.

    Returns:
        Symmetric positive-definite covariance matrix.
    """

    cov = np.asarray(covariance, dtype=np.float64)
    if cov.ndim != 2 or cov.shape[0] != cov.shape[1]:
        raise UncertaintyEstimationError("covariance must be square.")
    if not np.all(np.isfinite(cov)):
        raise UncertaintyEstimationError("covariance contains NaN or infinite values.")

    cov = 0.5 * (cov + cov.T)
    eye = np.eye(cov.shape[0], dtype=np.float64)
    regularization = float(jitter)
    for _ in range(8):
        try:
            np.linalg.cholesky(cov + regularization * eye)
            return cov + regularization * eye
        except np.linalg.LinAlgError:
            regularization *= 10.0
    raise UncertaintyEstimationError("covariance is not positive definite after regularization.")


def mahalanobis_distance(residual: np.ndarray, covariance: np.ndarray) -> float:
    """Compute sqrt(r^T Sigma^{-1} r) with Cholesky-based solves."""

    residual = np.asarray(residual, dtype=np.float64).reshape(-1)
    cov = ensure_positive_definite(covariance)
    if residual.shape[0] != cov.shape[0]:
        raise UncertaintyEstimationError(
            f"residual dimension {residual.shape[0]} does not match covariance {cov.shape[0]}."
        )
    if not np.all(np.isfinite(residual)):
        raise UncertaintyEstimationError("residual contains NaN or infinite values.")

    chol = np.linalg.cholesky(cov)
    whitened = np.linalg.solve(chol, residual)
    return float(np.linalg.norm(whitened))


def gaussian_uncertainty(covariance: np.ndarray) -> GaussianUncertainty:
    """Summarize a Gaussian covariance through entropy and conditioning."""

    cov = ensure_positive_definite(covariance)
    dimension = cov.shape[0]
    sign, logdet = np.linalg.slogdet(cov)
    if sign <= 0.0:
        raise UncertaintyEstimationError("covariance determinant is not positive.")
    entropy = 0.5 * (dimension * (1.0 + np.log(2.0 * np.pi)) + logdet)
    return GaussianUncertainty(
        dimension=dimension,
        log_determinant=float(logdet),
        differential_entropy=float(entropy),
        condition_number=float(np.linalg.cond(cov)),
    )


class UncertaintyEstimator:
    """Estimate modality reliability from visual and inertial quality signals.

    Visual reliability combines feature support, reprojection quality, brightness,
    sharpness, and optional optical-flow consistency.  Inertial reliability uses
    motion plausibility, optional preintegration residuals, and optional bias
    stability.  All scores are bounded and validated so downstream fusion cannot
    silently consume invalid numerical values.
    """

    def __init__(
        self,
        min_features: int = 50,
        target_features: int = 200,
        max_reprojection_error: float = 5.0,
        nominal_acceleration_norm: float = 9.81,
        max_gyro_norm: float = 5.0,
    ) -> None:
        if min_features < 0:
            raise UncertaintyEstimationError("min_features must be non-negative.")
        if target_features <= min_features:
            raise UncertaintyEstimationError("target_features must be greater than min_features.")
        if max_reprojection_error <= 0.0:
            raise UncertaintyEstimationError("max_reprojection_error must be positive.")
        if nominal_acceleration_norm <= 0.0:
            raise UncertaintyEstimationError("nominal_acceleration_norm must be positive.")
        if max_gyro_norm <= 0.0:
            raise UncertaintyEstimationError("max_gyro_norm must be positive.")

        self.min_features = int(min_features)
        self.target_features = int(target_features)
        self.max_reprojection_error = float(max_reprojection_error)
        self.nominal_acceleration_norm = float(nominal_acceleration_norm)
        self.max_gyro_norm = float(max_gyro_norm)

    def estimate_visual_reliability(self, signals: VisualQualitySignals) -> float:
        """Estimate a visual reliability score in [0, 1]."""

        tracked_features = _finite_non_negative(signals.tracked_features, name="tracked_features")
        reprojection_error = _finite_non_negative(
            signals.mean_reprojection_error,
            name="mean_reprojection_error",
        )
        brightness_score = clamp(signals.image_brightness)
        sharpness_score = clamp(signals.image_sharpness)

        feature_score = clamp(
            (tracked_features - self.min_features) / (self.target_features - self.min_features)
        )
        reprojection_score = 1.0 - clamp(reprojection_error / self.max_reprojection_error)

        scores = [feature_score, reprojection_score, brightness_score, sharpness_score]
        optical_flow = _bounded_optional(
            signals.optical_flow_consistency,
            name="optical_flow_consistency",
        )
        if optical_flow is not None:
            scores.append(optical_flow)

        return float(np.mean(scores))

    def estimate_inertial_reliability(self, signals: InertialQualitySignals) -> float:
        """Estimate an inertial reliability score in [0, 1]."""

        acceleration_norm = _finite_non_negative(signals.acceleration_norm, name="acceleration_norm")
        gyro_norm = _finite_non_negative(signals.gyro_norm, name="gyro_norm")

        gravity_deviation = abs(acceleration_norm - self.nominal_acceleration_norm)
        acceleration_score = 1.0 - clamp(gravity_deviation / self.nominal_acceleration_norm)
        gyro_score = 1.0 - clamp(gyro_norm / self.max_gyro_norm)

        scores = [acceleration_score, gyro_score]
        if signals.preintegration_residual is not None:
            residual = _finite_non_negative(
                signals.preintegration_residual,
                name="preintegration_residual",
            )
            scores.append(1.0 - clamp(residual))

        if signals.estimated_bias_norm is not None:
            bias = _finite_non_negative(signals.estimated_bias_norm, name="estimated_bias_norm")
            scores.append(1.0 - clamp(bias))

        return float(np.mean(scores))

    def estimate(
        self,
        visual_signals: VisualQualitySignals,
        inertial_signals: InertialQualitySignals,
        event_reliability: Optional[float] = None,
    ) -> ModalityReliability:
        """Estimate reliability for all available modalities."""

        return ModalityReliability(
            visual=self.estimate_visual_reliability(visual_signals),
            inertial=self.estimate_inertial_reliability(inertial_signals),
            event=clamp(event_reliability) if event_reliability is not None else None,
        )
