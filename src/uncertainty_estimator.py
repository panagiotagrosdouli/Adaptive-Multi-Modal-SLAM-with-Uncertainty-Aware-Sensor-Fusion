"""Uncertainty estimation module for adaptive multi-modal SLAM.

This module contains the initial research skeleton for estimating visual and
inertial reliability signals. The implementation is intentionally lightweight
at this stage so that it can later be connected to ORB-SLAM3, VINS-Fusion,
OpenVINS, ROS 2, or offline dataset evaluation scripts.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class VisualQualitySignals:
    """Signals that describe the reliability of the visual frontend."""

    tracked_features: int
    mean_reprojection_error: float
    image_brightness: float
    image_sharpness: float
    optical_flow_consistency: Optional[float] = None


@dataclass
class InertialQualitySignals:
    """Signals that describe the reliability of inertial integration."""

    acceleration_norm: float
    gyro_norm: float
    preintegration_residual: Optional[float] = None
    estimated_bias_norm: Optional[float] = None


@dataclass
class ModalityReliability:
    """Reliability scores used by the adaptive fusion module."""

    visual: float
    inertial: float
    event: Optional[float] = None


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    """Clamp a value into a fixed numeric interval."""

    return max(lower, min(upper, value))


class UncertaintyEstimator:
    """Estimate modality reliability from visual and inertial quality signals.

    The current implementation is a transparent heuristic baseline. Future
    versions should compare this with probabilistic calibration and learned
    uncertainty estimation.
    """

    def __init__(
        self,
        min_features: int = 50,
        target_features: int = 200,
        max_reprojection_error: float = 5.0,
    ) -> None:
        self.min_features = min_features
        self.target_features = target_features
        self.max_reprojection_error = max_reprojection_error

    def estimate_visual_reliability(self, signals: VisualQualitySignals) -> float:
        """Estimate a visual reliability score in [0, 1]."""

        feature_score = clamp(
            (signals.tracked_features - self.min_features)
            / max(1, self.target_features - self.min_features)
        )
        reprojection_score = 1.0 - clamp(
            signals.mean_reprojection_error / self.max_reprojection_error
        )
        brightness_score = clamp(signals.image_brightness)
        sharpness_score = clamp(signals.image_sharpness)

        scores = [feature_score, reprojection_score, brightness_score, sharpness_score]

        if signals.optical_flow_consistency is not None:
            scores.append(clamp(signals.optical_flow_consistency))

        return sum(scores) / len(scores)

    def estimate_inertial_reliability(self, signals: InertialQualitySignals) -> float:
        """Estimate an inertial reliability score in [0, 1]."""

        # This is a placeholder heuristic. It should later be replaced by a
        # model that uses IMU residuals, bias stability, and motion regime.
        motion_score = 1.0 - clamp((signals.gyro_norm + signals.acceleration_norm) / 100.0)

        scores = [motion_score]

        if signals.preintegration_residual is not None:
            scores.append(1.0 - clamp(signals.preintegration_residual))

        if signals.estimated_bias_norm is not None:
            scores.append(1.0 - clamp(signals.estimated_bias_norm))

        return sum(scores) / len(scores)

    def estimate(
        self,
        visual_signals: VisualQualitySignals,
        inertial_signals: InertialQualitySignals,
        event_reliability: Optional[float] = None,
    ) -> ModalityReliability:
        """Estimate reliability for all available modalities."""

        return ModalityReliability(
            visual=self.estimate_visual_reliability(visual_signals),
            inertial=self.estimate_inertial_reliability(inertial_signals),
            event=clamp(event_reliability) if event_reliability is not None else None,
        )
