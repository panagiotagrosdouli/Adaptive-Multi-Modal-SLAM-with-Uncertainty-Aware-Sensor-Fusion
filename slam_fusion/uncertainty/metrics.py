"""Uncertainty quantification and estimator consistency metrics."""

from __future__ import annotations

import math

import numpy as np


def ensure_psd(matrix: np.ndarray, jitter: float = 1e-9) -> np.ndarray:
    """Return a symmetrized positive semi-definite approximation."""

    sym = (np.asarray(matrix, dtype=float) + np.asarray(matrix, dtype=float).T) / 2.0
    eigvals, eigvecs = np.linalg.eigh(sym)
    clipped = np.maximum(eigvals, jitter)
    return eigvecs @ np.diag(clipped) @ eigvecs.T


def covariance_trace(covariance: np.ndarray) -> float:
    """Trace-based uncertainty proxy."""

    return float(np.trace(np.asarray(covariance, dtype=float)))


def logdet_uncertainty(covariance: np.ndarray, jitter: float = 1e-9) -> float:
    """Log-determinant uncertainty proxy for Gaussian covariance."""

    cov = ensure_psd(covariance, jitter=jitter)
    sign, value = np.linalg.slogdet(cov)
    if sign <= 0:
        raise ValueError("covariance is not positive definite after jitter")
    return float(value)


def gaussian_entropy(covariance: np.ndarray) -> float:
    """Differential entropy of a multivariate Gaussian up to covariance validity."""

    cov = ensure_psd(covariance)
    dim = cov.shape[0]
    return 0.5 * (dim * (1.0 + math.log(2.0 * math.pi)) + logdet_uncertainty(cov))


def mahalanobis_distance_squared(residual: np.ndarray, covariance: np.ndarray) -> float:
    """Squared Mahalanobis distance r^T S^-1 r."""

    residual = np.asarray(residual, dtype=float)
    covariance = np.asarray(covariance, dtype=float)
    return float(residual.T @ np.linalg.pinv(covariance) @ residual)


def nees(error: np.ndarray, covariance: np.ndarray) -> float:
    """Normalized estimation error squared."""

    return mahalanobis_distance_squared(error, covariance)


def nis(innovation: np.ndarray, innovation_covariance: np.ndarray) -> float:
    """Normalized innovation squared."""

    return mahalanobis_distance_squared(innovation, innovation_covariance)


def risk_score(
    covariance: np.ndarray,
    min_reliability: float,
    innovation_distance: float,
    gate_threshold: float,
) -> float:
    """Transparent risk score in [0, 1] from uncertainty, reliability, and innovation."""

    unc = math.tanh(max(0.0, covariance_trace(covariance)) / 10.0)
    rel = 1.0 - min(1.0, max(0.0, min_reliability))
    innov = min(1.0, max(0.0, innovation_distance / max(gate_threshold, 1e-9)))
    return float(np.clip((unc + rel + innov) / 3.0, 0.0, 1.0))
