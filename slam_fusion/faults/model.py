"""Explicit, reproducible sensor-fault definitions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FaultType(str, Enum):
    NOMINAL = "nominal"
    NOISY = "noisy"
    BIASED = "biased"
    DRIFTING = "drifting"
    DELAYED = "delayed"
    INTERMITTENT = "intermittent"
    DROPPED = "dropped"
    SATURATED = "saturated"
    MISCALIBRATED = "miscalibrated"
    GEOMETRICALLY_DEGENERATE = "geometrically_degenerate"
    ADVERSARIALLY_INCONSISTENT = "adversarially_inconsistent"
    PERMANENTLY_FAILED = "permanently_failed"


@dataclass(frozen=True)
class FaultEvent:
    sensor: str
    fault_type: FaultType
    onset_time_s: float
    duration_s: float | None
    severity: float
    seed: int
    recovery: str = "automatic"
    ground_truth_label: str | None = None

    def __post_init__(self) -> None:
        if self.onset_time_s < 0:
            raise ValueError("onset_time_s must be non-negative")
        if self.duration_s is not None and self.duration_s <= 0:
            raise ValueError("duration_s must be positive")
        if not 0.0 <= self.severity <= 1.0:
            raise ValueError("severity must be in [0, 1]")

    def active(self, time_s: float) -> bool:
        if time_s < self.onset_time_s:
            return False
        return self.duration_s is None or time_s < self.onset_time_s + self.duration_s
