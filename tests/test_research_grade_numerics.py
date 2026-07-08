import math

import numpy as np
import pytest

from slam_fusion.fusion.adaptive import AdaptiveFusionError, AdaptiveSensorFusion
from slam_fusion.uncertainty.metrics import (
    UncertaintyMetricError,
    gaussian_entropy,
    logdet_uncertainty,
    mahalanobis_distance_squared,
    nis,
    risk_score,
)


def test_mahalanobis_distance_uses_cholesky_equivalent_solution():
    residual = np.array([1.0, -2.0])
    covariance = np.array([[4.0, 0.5], [0.5, 2.0]])

    distance = mahalanobis_distance_squared(residual, covariance)
    expected = float(residual.T @ np.linalg.solve(covariance, residual))

    assert math.isclose(distance, expected, rel_tol=1e-12, abs_tol=1e-12)


def test_singular_covariance_is_regularized_for_consistency_metrics():
    residual = np.array([1.0, 0.0])
    singular_covariance = np.diag([1.0, 0.0])

    distance = nis(residual, singular_covariance)

    assert math.isfinite(distance)
    assert distance > 0.0


def test_indefinite_covariance_is_rejected():
    residual = np.array([1.0, 0.0])
    indefinite_covariance = np.array([[1.0, 0.0], [0.0, -1.0]])

    with pytest.raises(UncertaintyMetricError):
        mahalanobis_distance_squared(residual, indefinite_covariance)


def test_adaptive_gate_rejects_dimension_mismatch():
    fusion = AdaptiveSensorFusion()

    with pytest.raises(AdaptiveFusionError):
        fusion.mahalanobis_gate(np.array([1.0, 2.0, 3.0]), np.eye(2))


def test_covariance_based_uncertainty_metrics_are_finite_for_spd_matrix():
    covariance = np.array([[2.0, 0.1], [0.1, 1.0]])

    assert math.isfinite(logdet_uncertainty(covariance))
    assert math.isfinite(gaussian_entropy(covariance))


def test_risk_score_validates_gate_threshold():
    with pytest.raises(UncertaintyMetricError):
        risk_score(np.eye(2), min_reliability=0.5, innovation_distance=1.0, gate_threshold=0.0)
