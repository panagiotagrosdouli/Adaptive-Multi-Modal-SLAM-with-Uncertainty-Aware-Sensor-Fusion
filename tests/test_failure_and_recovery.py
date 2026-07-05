from src.failure_predictor import FailureIndicators, FailurePredictor
from src.recovery_policy import RecoveryPolicy


def test_failure_probability_is_bounded():
    predictor = FailurePredictor()
    indicators = FailureIndicators(
        visual_reliability=0.0,
        inertial_reliability=0.0,
        reprojection_error=100.0,
        tracked_features=0,
    )
    probability = predictor.predict(indicators)
    assert 0.0 <= probability <= 1.0


def test_failure_probability_increases_with_poor_visual_tracking():
    predictor = FailurePredictor()
    healthy = FailureIndicators(
        visual_reliability=0.9,
        inertial_reliability=0.9,
        reprojection_error=1.0,
        tracked_features=200,
    )
    degraded = FailureIndicators(
        visual_reliability=0.1,
        inertial_reliability=0.9,
        reprojection_error=8.0,
        tracked_features=20,
    )
    assert predictor.predict(degraded) > predictor.predict(healthy)


def test_recovery_policy_increases_inertial_weight_when_vision_is_unreliable():
    policy = RecoveryPolicy()
    action = policy.select_action(
        failure_probability=0.5,
        visual_reliability=0.2,
        inertial_reliability=0.8,
    )
    assert action.name == 'increase_inertial_weight'


def test_recovery_policy_triggers_relocalization_when_all_modalities_are_unreliable():
    policy = RecoveryPolicy()
    action = policy.select_action(
        failure_probability=0.5,
        visual_reliability=0.2,
        inertial_reliability=0.2,
    )
    assert action.name == 'trigger_relocalization'
