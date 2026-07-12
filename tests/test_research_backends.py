from __future__ import annotations

import numpy as np

from slam_fusion.backends.ekf import ErrorStateEKF
from slam_fusion.backends.factor_graph import PoseFactor, PoseGraph2D
from slam_fusion.reliability.calibration import (
    MonotonicReliabilityCalibrator,
    calibration_metrics,
)
from slam_fusion.sensors.base import SensorMeasurement, SensorModality
from slam_fusion.synchronization import MeasurementSynchronizer


def measurement(timestamp: float, modality: SensorModality, data: np.ndarray) -> SensorMeasurement:
    return SensorMeasurement(timestamp, modality, data, np.eye(len(data)) * 0.01)


def test_buffered_synchronization_and_interpolation() -> None:
    sync = MeasurementSynchronizer([SensorModality.CAMERA, SensorModality.IMU], tolerance_s=0.02)
    sync.push(measurement(1.0, SensorModality.CAMERA, np.array([1.0])))
    sync.push(measurement(0.99, SensorModality.IMU, np.array([0.0, 0.0, 0.0])))
    sync.push(measurement(1.01, SensorModality.IMU, np.array([2.0, 2.0, 2.0])))
    bundle = sync.synchronize(1.0)
    assert not bundle.health.missing_modalities
    interpolated = sync.interpolate_vector(SensorModality.IMU, 1.0)
    assert interpolated is not None
    assert np.allclose(interpolated.data, np.ones(3))


def test_reliability_calibration_is_monotonic() -> None:
    scores = np.array([0.1, 0.2, 0.3, 0.8, 0.9])
    outcomes = np.array([0, 1, 0, 1, 1])
    calibrator = MonotonicReliabilityCalibrator().fit(scores, outcomes)
    calibrated = calibrator.predict(scores)
    assert np.all(np.diff(calibrated) >= -1e-12)
    metrics = calibration_metrics(calibrated, outcomes, bins=5)
    assert 0.0 <= metrics.expected_calibration_error <= 1.0
    assert 0.0 <= metrics.brier_score <= 1.0


def test_ekf_propagation_and_gated_position_update() -> None:
    ekf = ErrorStateEKF()
    ekf.propagate(0.01, np.array([0.0, 0.0, 9.81]), np.zeros(3))
    accepted = ekf.update_position(np.array([0.1, 0.0, 0.0]), np.eye(3) * 0.1, 20.0)
    rejected = ekf.update_position(np.array([100.0, 0.0, 0.0]), np.eye(3) * 0.01, 20.0)
    assert accepted.accepted
    assert not rejected.accepted
    assert np.all(np.linalg.eigvalsh(ekf.state.covariance) >= -1e-10)
    assert np.isclose(np.linalg.norm(ekf.state.quaternion_wxyz), 1.0)


def test_pose_graph_loop_closure_reduces_error() -> None:
    graph = PoseGraph2D()
    graph.add_pose(0, np.array([0.0, 0.0, 0.0]))
    graph.add_pose(1, np.array([1.1, 0.1, 0.02]))
    graph.add_pose(2, np.array([2.2, 0.2, 0.04]))
    information = np.eye(3) * 100.0
    graph.add_factor(PoseFactor(0, 1, np.array([1.0, 0.0, 0.0]), information))
    graph.add_factor(PoseFactor(1, 2, np.array([1.0, 0.0, 0.0]), information))
    graph.add_factor(PoseFactor(0, 2, np.array([2.0, 0.0, 0.0]), information, kind="loop"))
    before = graph.total_error()
    optimized = graph.optimize()
    after = graph.total_error()
    assert after < before
    assert np.linalg.norm(optimized[2] - np.array([2.0, 0.0, 0.0])) < 0.05
