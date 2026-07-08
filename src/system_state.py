"""Runtime state machine for adaptive SLAM supervision."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SystemState:
    """Compact state used by the experiment runner."""

    tracking_ok: bool = True
    failure_probability: float = 0.0
    visual_reliability: float = 1.0
    inertial_reliability: float = 1.0
    active_mode: str = "normal"

    def update_mode(self) -> None:
        """Update the active operating mode from predicted failure risk."""

        if self.failure_probability > 0.7:
            self.active_mode = "recovery"
        elif self.failure_probability > 0.3:
            self.active_mode = "adaptive"
        else:
            self.active_mode = "normal"
