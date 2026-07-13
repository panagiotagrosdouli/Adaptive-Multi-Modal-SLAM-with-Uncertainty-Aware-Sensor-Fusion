import numpy as np

from slam_fusion.domain_shift.detection import RollingMomentShiftDetector, ShiftState
from slam_fusion.fusion.robust import robust_reliability_weights


def test_shift_detector_flags_unseen_mean_shift() -> None:
    rng = np.random.default_rng(12)
    reference = rng.normal(0.0, 1.0, size=128)
    detector = RollingMomentShiftDetector(reference=reference, window_size=24)

    nominal = detector.update(rng.normal(0.0, 1.0, size=24))
    shifted = detector.update(rng.normal(5.0, 1.0, size=24))

    assert nominal.state in {ShiftState.NOMINAL, ShiftState.SUSPECTED}
    assert shifted.state is ShiftState.DETECTED
    assert shifted.confidence_multiplier < nominal.confidence_multiplier


def test_robust_fusion_reduces_weight_under_reliability_uncertainty() -> None:
    nominal = robust_reliability_weights({"camera": 0.8, "imu": 0.8})
    robust = robust_reliability_weights(
        {"camera": 0.8, "imu": 0.8},
        uncertainty={"camera": 0.5, "imu": 0.05},
        risk_aversion=1.0,
    )

    assert nominal.weights["camera"] == nominal.weights["imu"]
    assert robust.weights["camera"] < robust.weights["imu"]
    assert np.isclose(sum(robust.weights.values()), 1.0)


def test_shift_confidence_can_reject_a_sensor() -> None:
    result = robust_reliability_weights(
        {"camera": 0.9, "imu": 0.7},
        shift_confidence={"camera": 0.02, "imu": 1.0},
        rejection_floor=0.05,
    )

    assert "camera" in result.rejected
    assert result.weights["camera"] == 0.0
    assert result.weights["imu"] == 1.0


def test_invalid_robust_inputs_are_rejected() -> None:
    try:
        robust_reliability_weights({"camera": 1.2})
    except ValueError:
        pass
    else:
        raise AssertionError("invalid reliability must raise ValueError")
