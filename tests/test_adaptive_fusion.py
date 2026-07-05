from src.adaptive_fusion import AdaptiveFusionPolicy
from src.uncertainty_estimator import ModalityReliability


def test_fusion_weights_sum_to_one_without_event():
    policy = AdaptiveFusionPolicy()
    weights = policy.compute_weights(ModalityReliability(visual=0.7, inertial=0.3))
    assert abs((weights.visual + weights.inertial) - 1.0) < 1e-6


def test_fusion_weights_are_positive():
    policy = AdaptiveFusionPolicy()
    weights = policy.compute_weights(ModalityReliability(visual=0.0, inertial=0.0))
    assert weights.visual > 0.0
    assert weights.inertial > 0.0
