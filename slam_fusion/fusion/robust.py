"""Conservative fusion when reliability estimates are uncertain or shifted."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np


@dataclass(frozen=True, slots=True)
class RobustFusionResult:
    weights: dict[str, float]
    effective_reliability: dict[str, float]
    rejected: tuple[str, ...]
    method: str


def robust_reliability_weights(
    reliability: Mapping[str, float],
    uncertainty: Mapping[str, float] | None = None,
    shift_confidence: Mapping[str, float] | None = None,
    *,
    risk_aversion: float = 1.0,
    rejection_floor: float = 0.05,
) -> RobustFusionResult:
    """Return normalized lower-confidence reliability weights.

    The approximation uses a bounded lower confidence score
    ``r_eff = clip(r - risk_aversion * uncertainty, 0, 1) * shift_confidence``.
    It is a transparent robust baseline, not an exact distributionally robust optimizer.
    """

    if not reliability:
        raise ValueError("reliability must not be empty")
    if risk_aversion < 0:
        raise ValueError("risk_aversion must be non-negative")
    if not 0.0 <= rejection_floor < 1.0:
        raise ValueError("rejection_floor must be in [0, 1)")

    uncertainty = uncertainty or {}
    shift_confidence = shift_confidence or {}
    effective: dict[str, float] = {}
    rejected: list[str] = []

    for sensor, raw_value in reliability.items():
        value = float(raw_value)
        spread = float(uncertainty.get(sensor, 0.0))
        confidence = float(shift_confidence.get(sensor, 1.0))
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"reliability for {sensor} must be in [0, 1]")
        if spread < 0.0:
            raise ValueError(f"uncertainty for {sensor} must be non-negative")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"shift confidence for {sensor} must be in [0, 1]")
        conservative = float(np.clip(value - risk_aversion * spread, 0.0, 1.0))
        effective[sensor] = conservative * confidence
        if effective[sensor] < rejection_floor:
            rejected.append(sensor)

    accepted = {sensor: score for sensor, score in effective.items() if sensor not in rejected}
    normalizer = float(sum(accepted.values()))
    if normalizer <= 0.0:
        weights = {sensor: 0.0 for sensor in effective}
    else:
        weights = {
            sensor: (score / normalizer if sensor in accepted else 0.0)
            for sensor, score in effective.items()
        }
    return RobustFusionResult(
        weights=weights,
        effective_reliability=effective,
        rejected=tuple(sorted(rejected)),
        method="lower-confidence-shift-aware",
    )
