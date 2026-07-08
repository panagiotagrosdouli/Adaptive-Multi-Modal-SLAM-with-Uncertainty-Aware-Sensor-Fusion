"""Uncertainty quantification and estimator consistency metrics.

The functions in this module implement Gaussian covariance diagnostics used in
state-estimation papers: trace, log-determinant, entropy, NEES, and NIS. They are
small by design, but numerically strict: invalid covariance matrices should fail
loudly instead of silently producing optimistic consistency scores.
"""

from __future__ import annotations

import math

import numpy as np


class UncertaintyMetricError(ValueError):
    """Raised when an uncertainty metric receives invalid numerical input."""


def validate_vector(vector: np.ndarray, *, name: str) -> np.ndarray:
    """Return a finite one-dimensional vector.

    Args:
        vector: Array-like input to validate.
        name: Human-readable variable name used in error messages.

    Raises:
        UncertaintyMetricError: If the input is not a finite vector.
    """

    value = np.asarray(vector, dtype=float).reshape(-1)
    if value.ndim != 1 or not np.all(np.isfinite(value)):
        raise UncertaintyMetricError(f"{name} must be a finite vector")
    return value


def symmetrize(matrix: np.ndarray) -> np.ndarray:
    """Return the symmetric part of a finite square matrix."""

    value = np.asarray(matrix, dtype=float)
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise UncertaintyMetricError("covariance must be a square matrix")
    if not np.all(np.isfinite(value)):
        raise UncertaintyMetricError("covariance contains non-finite values")
    return 0.5 * (value + value.T)


def ensure_spd(matrix: np.ndarray, jitter: float = 1e-9, max_attempts: int = 6) -> np.ndarray:
    """Return a symmetric positive-definite covariance matrix.

    A covariance estimated from finite precision arithmetic can be numerically
    positive-semidefinite while failing Cholesky factorization. The function adds
    diagonal jitter geometrically and verifies positive definiteness via Cholesky.
    Indefinite matrices are rejected after bounded attempts.

    Args:
        matrix: Candidate covariance matrix.
        jitter: Initial diagonal regularization.
        max_attempts: Maximum number of geometric jitter increases.

    Returns:
        A symmetric positive-definite matrix.
    """

    if not np.isfinite(jitter) or jitter <= 0.0:
        raise UncertaintyMetricError("jitter must be finite and positive")
    if max_attempts < 0:
        raise UncertaintyMetricError("max_attempts must be non-negative")

    cov = symmetrize(matrix)
    identity = np.eye(cov.shape[0], dtype=float)
    diagonal_jitter = 0.0
    for attempt in range(max_attempts + 1):
        candidate = cov + diagonal_jitter * identity
        try:
            np.linalg.cholesky(candidate)
            return candidate
        except np.linalg.LinAlgError as exc:
            if attempt == max_attempts:
                raise UncertaintyMetricError(
                    "covariance is not positive definite after adaptive jitter"
                ) from exc
            diagonal_jitter = jitter if diagonal_jitter == 0.0 else diagonal_jitter * 10.0
    raise UncertaintyMetricError("unreachable covariance regularization failure")


def ensure_psd(matrix: np.ndarray, jitter: float = 1e-9) -> np.ndarray:
    """Return a symmetrized positive-semidefinite approximation.

    This compatibility helper clips eigenvalues for visualization and legacy callers.
    Estimator consistency metrics should prefer :func:`ensure_spd` so that invalid
    innovation covariance matrices are not hidden by a pseudo-inverse.
    """

    if not np.isfinite(jitter) or jitter <= 0.0:
        raise UncertaintyMetricError("jitter must be finite and positive")
    sym = symmetrize(matrix)
    eigvals, eigvecs = np.linalg.eigh(sym)
    clipped = np.maximum(eigvals, jitter)
    return eigvecs @ np.diag(clipped) @ eigvecs.T


def covariance_trace(covariance: np.ndarray) -> float:
    """Return the trace-based uncertainty proxy :math:`tr(P)`."""

    return float(np.trace(symmetrize(covariance)))


def logdet_uncertainty(covariance: np.ndarray, jitter: float = 1e-9) -> float:
    """Return :math:`\log \det(P)` for a Gaussian covariance matrix."""

    cov = ensure_spd(covariance, jitter=jitter)
    sign, value = np.linalg.slogdet(cov)
    if sign <= 0:
        raise UncertaintyMetricError("covariance is not positive definite")
    return float(value)


def gaussian_entropy(covariance: np.ndarray) -> float:
    """Return the differential entropy of ``N(0, covariance)``.

    For dimension :math:`d`, the entropy is

    .. math::

        H = \frac{1}{2}\left[d(1 + \log(2\pi)) + \log\det(P)\right].
    """

    cov = ensure_spd(covariance)
    dim = cov.shape[0]
    return 0.5 * (dim * (1.0 + math.log(2.0 * math.pi)) + logdet_uncertainty(cov))


def mahalanobis_distance_squared(residual: np.ndarray, covariance: np.ndarray) -> float:
    """Return the squared Mahalanobis distance :math:`r^T S^{-1}r`.

    The computation uses a Cholesky solve. This is mathematically equivalent to
    solving the whitened residual problem and is numerically preferable to forming
    an explicit inverse or pseudo-inverse.
    """

    r = validate_vector(residual, name="residual")
    cov = ensure_spd(covariance)
    if cov.shape[0] != r.shape[0]:
        raise UncertaintyMetricError("residual and covariance dimensions are inconsistent")
    factor = np.linalg.cholesky(cov)
    whitened = np.linalg.solve(factor, r)
    return float(whitened.T @ whitened)


def nees(error: np.ndarray, covariance: np.ndarray) -> float:
    """Return normalized estimation error squared, :math:`e^T P^{-1}e`."""

    return mahalanobis_distance_squared(error, covariance)


def nis(innovation: np.ndarray, innovation_covariance: np.ndarray) -> float:
    """Return normalized innovation squared, :math:`\nu^T S^{-1}\nu`."""

    return mahalanobis_distance_squared(innovation, innovation_covariance)


def risk_score(
    covariance: np.ndarray,
    min_reliability: float,
    innovation_distance: float,
    gate_threshold: float,
) -> float:
    """Return a transparent diagnostic risk score in ``[0, 1]``.

    The score is not a calibrated probability. It combines covariance magnitude,
    worst-modality reliability, and normalized innovation inconsistency as a
    conservative monitoring signal.
    """

    if not np.isfinite(min_reliability):
        raise UncertaintyMetricError("min_reliability must be finite")
    if not np.isfinite(innovation_distance) or innovation_distance < 0.0:
        raise UncertaintyMetricError("innovation_distance must be finite and non-negative")
    if not np.isfinite(gate_threshold) or gate_threshold <= 0.0:
        raise UncertaintyMetricError("gate_threshold must be finite and positive")

    unc = math.tanh(max(0.0, covariance_trace(covariance)) / 10.0)
    rel = 1.0 - min(1.0, max(0.0, min_reliability))
    innov = min(1.0, max(0.0, innovation_distance / gate_threshold))
    return float(np.clip((unc + rel + innov) / 3.0, 0.0, 1.0))
