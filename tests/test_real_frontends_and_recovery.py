from __future__ import annotations

import cv2
import numpy as np

from slam_fusion.frontends.imu.preintegration import IMUPreintegrator
from slam_fusion.frontends.lidar.registration import register_icp
from slam_fusion.frontends.rgbd.depth import RGBDFrontend
from slam_fusion.frontends.vision.tracker import VisualFrontend
from slam_fusion.recovery.controller import RecoveryController, RecoveryState


def test_visual_frontend_detects_and_tracks_features() -> None:
    image = np.zeros((160, 240), dtype=np.uint8)
    for y in range(20, 150, 30):
        for x in range(20, 230, 30):
            cv2.circle(image, (x, y), 3, 255, -1)
    shifted = np.roll(image, 2, axis=1)
    frontend = VisualFrontend(max_features=150, min_features=40)
    first = frontend.process(image)
    second = frontend.process(shifted)
    assert first.diagnostics["feature_count"] >= 20
    assert second.diagnostics["track_survival"] > 0.5
    assert second.diagnostics["parallax_pixels"] > 0.5


def test_imu_preintegration_constant_acceleration() -> None:
    preintegrator = IMUPreintegrator()
    for index in range(11):
        preintegrator.integrate(index * 0.1, np.array([1.0, 0.0, 0.0]), np.zeros(3))
    assert np.isclose(preintegrator.result.delta_time, 1.0)
    assert np.allclose(preintegrator.result.delta_velocity, [1.0, 0.0, 0.0], atol=1e-6)
    assert np.allclose(preintegrator.result.delta_position, [0.5, 0.0, 0.0], atol=1e-6)
    assert np.all(np.linalg.eigvalsh(preintegrator.result.covariance) >= -1e-12)


def test_lidar_icp_recovers_translation() -> None:
    rng = np.random.default_rng(4)
    target = rng.normal(size=(250, 3))
    source = target - np.array([0.25, -0.15, 0.1])
    result = register_icp(source, target, correspondence_distance=0.8)
    assert result.correspondence_count > 150
    assert result.fitness > 0.7
    assert np.allclose(result.transformation[:3, 3], [0.25, -0.15, 0.1], atol=0.05)


def test_rgbd_projection_and_invalid_depth_handling() -> None:
    depth = np.full((6, 8), 2000, dtype=np.uint16)
    depth[0, 0] = 0
    intrinsics = np.array([[100.0, 0.0, 4.0], [0.0, 100.0, 3.0], [0.0, 0.0, 1.0]])
    result = RGBDFrontend().process(depth, intrinsics, stride=1)
    assert len(result.points) == 47
    assert np.allclose(result.points[:, 2], 2.0)
    assert result.diagnostics["invalid_depth_ratio"] > 0.0
    assert np.all(result.variance > 0.0)


def test_recovery_rejects_then_reactivates_sensor() -> None:
    controller = RecoveryController(reject_after=2, cooldown_steps=2, reactivate_after=2)
    decision = controller.update("camera", 0.1, False)
    assert decision.state == RecoveryState.DEGRADED
    decision = controller.update("camera", 0.1, False)
    assert decision.state == RecoveryState.COOLDOWN
    controller.update("camera", 0.9, True)
    decision = controller.update("camera", 0.9, True)
    assert decision.state == RecoveryState.PROBATION
    controller.update("camera", 0.9, True)
    decision = controller.update("camera", 0.9, True)
    assert decision.state == RecoveryState.ACTIVE
    assert decision.weight_scale == 1.0
