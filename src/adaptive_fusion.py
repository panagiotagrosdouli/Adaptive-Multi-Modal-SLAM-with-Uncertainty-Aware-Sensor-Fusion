"""Adaptive modality weighting for uncertainty-aware SLAM.

The fusion policy maps modality reliabilities to normalized measurement weights.
A reliability score r in [0, 1] is interpreted as a proxy for measurement
precision, not as a probability that should be averaged directly.  This is a
research baseline rather than a substitute for a full factor-graph covariance
model, but it preserves the correct qualitative behavior: unreliable sensors
receive lower precision, and all active weights remain normalized and bounded.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from src.uncertainty_estimator import ModalityReliability


class FusionPolicyError(ValueError):
    """Raised when an adaptive-fusion configuration is invalid."""


@dataclass(frozen=True)
class FusionWeights:
    """Normalized weights used by the estimator or backend wrapper.

    Attributes:
        visual: Weight assigned to visual measurements.
        inertial: Weight assigned to inertial measurements.
        event: Optional weight assigned to event-camera measurements.
    """

    visual: float
    inertial: float
    event: Optional[float] = None

    def as_dict(self) -> dict[str, float]:
        """Return active weights as a plain dictionary."""

        values = {"visual": self.visual, "inertial": self.inertial}
        if self.event is not None:
            values["event"] = self.event
        return values


class AdaptiveFusionPolicy:
    """Compute modality weights from online reliability estimates.

    Mathematical formulation:
        Let r_i be a bounded reliability score for modality i.  We map it to a
        positive pseudo-precision p_i = max(epsilon, r_i)^gamma / sigma_i^2,
        where sigma_i is a configurable nominal noise scale and gamma controls
        how aggressively unreliable sensors are down-weighted.  The normalized
        fusion weight is w_i = p_i / sum_j p_j.

    This is compatible with weighted least squares intuition: measurements with
    higher precision contribute more strongly.  The policy is deliberately
    deterministic and transparent so it can serve as a reproducible baseline
    against learned uncertainty weighting.
    """

    def __init__(
        self,
        minimum_weight: float = 0.05,
        reliability_exponent: float = 2.0,
        visual_noise_scale: float = 1.0,
        inertial_noise_scale: float = 1.0,
        event_noise_scale: float = 1.0,
    ) -> None:
        if not 0.0 <= minimum_weight < 1.0:
            raise FusionPolicyError("minimum_weight must be in [0, 1).")
        if reliability_exponent <= 0.0:
            raise FusionPolicyError("reliability_exponent must be positive.")
        for name, scale in {
            "visual_noise_scale": visual_noise_scale,
            "inertial_noise_scale": inertial_noise_scale,
            "event_noise_scale": event_noise_scale,
        }.items():
            if scale <= 0.0 or not np.isfinite(scale):
                raise FusionPolicyError(f"{name} must be a finite positive value.")

        self.minimum_weight = float(minimum_weight)
        self.reliability_exponent = float(reliability_exponent)
        self.noise_scales = {
            "visual": float(visual_noise_scale),
            "inertial": float(inertial_noise_scale),
            "event": float(event_noise_scale),
        }

    @staticmethod
    def _validate_reliability(value: float, *, name: str) -> float:
        """Validate a bounded reliability score."""

        value = float(value)
        if not np.isfinite(value):
            raise FusionPolicyError(f"{name} reliability must be finite.")
        if value < 0.0 or value > 1.0:
            raise FusionPolicyError(f"{name} reliability must be in [0, 1]; got {value}.")
        return value

    def _pseudo_precision(self, reliability: float, *, modality: str) -> float:
        """Convert bounded reliability into a positive pseudo-precision."""

        rel = max(self.minimum_weight, reliability)
        variance = self.noise_scales[modality] ** 2
        return float((rel**self.reliability_exponent) / variance)

    def compute_weights(self, reliability: ModalityReliability) -> FusionWeights:
        """Compute normalized adaptive weights for the active modalities."""

        reliabilities = {
            "visual": self._validate_reliability(reliability.visual, name="visual"),
            "inertial": self._validate_reliability(reliability.inertial, name="inertial"),
        }
        if reliability.event is not None:
            reliabilities["event"] = self._validate_reliability(
                reliability.event,
                name="event",
            )

        precisions = {
            modality: self._pseudo_precision(value, modality=modality)
            for modality, value in reliabilities.items()
        }
        total_precision = float(sum(precisions.values()))
        if total_precision <= 0.0 or not np.isfinite(total_precision):
            raise FusionPolicyError("Total precision is numerically invalid.")

        weights = {name: value / total_precision for name, value in precisions.items()}
        return FusionWeights(
            visual=weights["visual"],
            inertial=weights["inertial"],
            event=weights.get("event"),
        )
