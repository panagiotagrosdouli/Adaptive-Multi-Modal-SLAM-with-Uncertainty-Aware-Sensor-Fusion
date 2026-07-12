import numpy as np

from slam_fusion.frontends.rgbd.depth import RGBDFrontend
from slam_fusion.recovery.controller import RecoveryController, RecoveryState


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
    assert controller.update("camera", 0.1, False).state == RecoveryState.DEGRADED
    assert controller.update("camera", 0.1, False).state == RecoveryState.COOLDOWN
    controller.update("camera", 0.9, True)
    assert controller.update("camera", 0.9, True).state == RecoveryState.PROBATION
    controller.update("camera", 0.9, True)
    decision = controller.update("camera", 0.9, True)
    assert decision.state == RecoveryState.ACTIVE
    assert decision.weight_scale == 1.0
