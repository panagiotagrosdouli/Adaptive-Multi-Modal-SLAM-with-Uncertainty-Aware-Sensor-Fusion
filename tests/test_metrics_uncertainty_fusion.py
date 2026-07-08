import numpy as np

from src.adaptive_fusion import AdaptiveFusionPolicy
from src.metrics import absolute_trajectory_error, relative_pose_error, umeyama_alignment
from src.uncertainty_estimator import (
    InertialQualitySignals,
    ModalityReliability,
    UncertaintyEstimator,
    gaussian_uncertainty,
    mahalanobis_distance,
)


def test_sim3_alignment_recovers_scaled_translated_trajectory():
    ground_truth = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [2.0, 1.0, 0.0],
        ]
    )
    estimated = 2.0 * ground_truth + np.array([3.0, -1.0, 0.5])

    transform = umeyama_alignment(estimated, ground_truth, with_scale=True)
    aligned = transform.apply(estimated)

    assert np.allclose(aligned, ground_truth, atol=1e-9)
    assert absolute_trajectory_error(ground_truth, estimated, alignment="sim3") < 1e-9


def test_rpe_is_zero_for_consistent_translation_increment():
    ground_truth = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0]])
    estimated = np.array([[10.0, 1.0, 0.0], [11.0, 1.0, 0.0], [12.0, 1.0, 0.0]])

    assert relative_pose_error(ground_truth, estimated) == 0.0


def test_uncertainty_utilities_are_numerically_stable():
    covariance = np.diag([0.04, 0.09, 0.16])
    residual = np.array([0.2, 0.3, 0.4])

    assert np.isclose(mahalanobis_distance(residual, covariance), np.sqrt(3.0))
    summary = gaussian_uncertainty(covariance)
    assert summary.dimension == 3
    assert np.isfinite(summary.differential_entropy)


def test_adaptive_fusion_downweights_low_reliability_visual_modality():
    policy = AdaptiveFusionPolicy(minimum_weight=0.05, reliability_exponent=2.0)
    weights = policy.compute_weights(ModalityReliability(visual=0.2, inertial=0.9))

    assert weights.inertial > weights.visual
    assert np.isclose(weights.visual + weights.inertial, 1.0)


def test_uncertainty_estimator_returns_bounded_scores():
    estimator = UncertaintyEstimator()
    reliability = estimator.estimate(
        visual_signals=type(
            "VisualSignals",
            (),
            {
                "tracked_features": 150,
                "mean_reprojection_error": 1.0,
                "image_brightness": 0.8,
                "image_sharpness": 0.9,
                "optical_flow_consistency": 0.7,
            },
        )(),
        inertial_signals=InertialQualitySignals(acceleration_norm=9.81, gyro_norm=0.1),
    )

    assert 0.0 <= reliability.visual <= 1.0
    assert 0.0 <= reliability.inertial <= 1.0
