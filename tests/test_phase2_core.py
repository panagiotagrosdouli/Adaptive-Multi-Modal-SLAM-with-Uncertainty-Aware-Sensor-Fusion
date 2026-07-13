import numpy as np

from slam_fusion.calibration.temporal import CalibrationState, TemporalOffsetEstimator
from slam_fusion.faults.isolation import HypothesisIsolator
from slam_fusion.faults.model import FaultEvent, FaultType


def test_temporal_offset_estimation_is_bounded():
    rng = np.random.default_rng(4)
    reference = rng.normal(size=256)
    target = np.roll(reference, 4)
    estimator = TemporalOffsetEstimator()
    for _ in range(12):
        result = estimator.estimate_from_traces(reference, target, 0.01, max_lag_samples=8)
    assert abs(result.offset_s) <= estimator.config.max_abs_offset_s
    assert result.state in {CalibrationState.CALIBRATING, CalibrationState.CALIBRATED}
    assert result.observability >= estimator.config.min_observability


def test_temporal_calibration_refuses_unobservable_update():
    estimator = TemporalOffsetEstimator()
    result = estimator.estimate_from_traces(np.ones(32), np.ones(32), 0.01)
    assert result.state is CalibrationState.UNOBSERVABLE
    assert not result.updated
    assert result.offset_s == 0.0


def test_fault_event_schedule():
    event = FaultEvent("camera", FaultType.DELAYED, 2.0, 3.0, 0.7, 11)
    assert not event.active(1.9)
    assert event.active(2.0)
    assert not event.active(5.0)


def test_fault_isolator_distinguishes_delay_and_failure():
    isolator = HypothesisIsolator()
    delayed = isolator.infer("camera", {"timing_z": 4.0, "residual_z": 1.0})
    failed = isolator.infer("lidar", {"dropout_rate": 1.0, "residual_z": 2.0})
    assert delayed.suspected_fault_type == "delayed"
    assert delayed.recommended_action == "freeze_measurements_and_recalibrate_time"
    assert failed.suspected_fault_type == "failed"
    assert failed.recommended_action == "isolate_sensor"
