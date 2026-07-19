from __future__ import annotations

import numpy as np

from slam_fusion.evaluation.trajectory import absolute_trajectory_error, relative_pose_error
from slam_fusion.fusion.adaptive import AdaptiveFusionConfig, AdaptiveSensorFusion
from slam_fusion.sensors.base import SensorMeasurement, SensorModality, synchronize_measurements
from slam_fusion.uncertainty.metrics import ensure_psd, nees, nis


def test_timestamp_synchronization_gate() -> None:
    measurements = [
        SensorMeasurement(0.95, SensorModality.CAMERA, None, np.eye(2)),
        SensorMeasurement(1.02, SensorModality.IMU, None, np.eye(2)),
        SensorMeasurement(1.30, SensorModality.LIDAR, None, np.eye(2)),
    ]
    synced = synchronize_measurements(measurements, reference_time=1.0, tolerance=0.06)
    assert [m.modality for m in synced] == [SensorModality.CAMERA, SensorModality.IMU]


def test_adaptive_weights_sum_to_one_and_downweight_degradation() -> None:
    fusion = AdaptiveSensorFusion()
    weights = fusion.precision_weights(
        {"camera": 0.2, "imu": 0.9}, {"camera": 0.04, "imu": 0.04}
    )
    assert np.isclose(sum(weights.values()), 1.0)
    assert weights["imu"] > weights["camera"]


def test_covariance_psd_projection() -> None:
    cov = np.array([[1.0, 2.0], [2.0, 1.0]])
    fixed = ensure_psd(cov)
    assert np.min(np.linalg.eigvalsh(fixed)) > 0.0


def test_mahalanobis_gating() -> None:
    fusion = AdaptiveSensorFusion(AdaptiveFusionConfig(mahalanobis_threshold=5.0))
    accepted, distance = fusion.mahalanobis_gate(np.array([1.0, 0.0]), np.eye(2))
    assert accepted
    assert np.isclose(distance, 1.0)


def test_nees_nis() -> None:
    assert np.isclose(nees(np.array([1.0, 0.0]), np.eye(2)), 1.0)
    assert np.isclose(nis(np.array([0.0, 2.0]), np.eye(2)), 4.0)


def test_trajectory_metrics() -> None:
    gt = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0]])
    est = gt + np.array([0.1, 0.0, 0.0])
    assert np.isclose(absolute_trajectory_error(est, gt), 0.1)
    assert np.isclose(relative_pose_error(est, gt), 0.0)
