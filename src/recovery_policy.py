"""Recovery policy for adaptive SLAM supervision."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RecoveryAction:
    """Action selected by the recovery policy."""

    name: str
    reason: str


class RecoveryPolicy:
    """Select conservative recovery actions from reliability and failure risk."""

    def select_action(
        self,
        failure_probability: float,
        visual_reliability: float,
        inertial_reliability: float,
    ) -> RecoveryAction:
        """Choose a high-level recovery action."""

        if failure_probability < 0.3:
            return RecoveryAction("continue_normal_operation", "failure risk is low")
        if visual_reliability < 0.4 and inertial_reliability >= 0.5:
            return RecoveryAction(
                "increase_inertial_weight",
                "visual tracking appears unreliable",
            )
        if visual_reliability < 0.4 and inertial_reliability < 0.4:
            return RecoveryAction(
                "trigger_relocalization",
                "both visual and inertial reliability are low",
            )
        if failure_probability >= 0.7:
            return RecoveryAction(
                "insert_keyframe_and_reduce_visual_residuals",
                "high predicted failure risk",
            )
        return RecoveryAction(
            "adaptive_sensor_reweighting",
            "moderate predicted failure risk",
        )
