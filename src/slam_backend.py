"""SLAM backend interfaces and a deterministic smoke-test backend."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SlamObservation:
    """Sensor observation passed to a SLAM backend."""

    timestamp: float
    image: np.ndarray | None = None
    imu_accel: np.ndarray | None = None
    imu_gyro: np.ndarray | None = None


@dataclass(frozen=True)
class SlamResult:
    """Minimal SLAM result consumed by adaptive supervision modules."""

    timestamp: float
    position: np.ndarray
    orientation_quat: np.ndarray
    tracking_ok: bool
    num_tracked_features: int = 0
    mean_reprojection_error: float = 0.0


class SlamBackend:
    """Abstract interface for SLAM/VIO backend wrappers."""

    def initialize(self) -> None:
        """Initialize backend resources."""

        raise NotImplementedError

    def process(self, observation: SlamObservation) -> SlamResult:
        """Process one observation and return the backend result."""

        raise NotImplementedError

    def shutdown(self) -> None:
        """Release backend resources."""


class DummySlamBackend(SlamBackend):
    """Deterministic backend used only for smoke tests and CI phases."""

    def __init__(self) -> None:
        self.position = np.zeros(3)
        self.orientation = np.array([0.0, 0.0, 0.0, 1.0])

    def initialize(self) -> None:
        """Reset the deterministic state."""

        self.position = np.zeros(3)

    def process(self, observation: SlamObservation) -> SlamResult:
        """Return a deterministic forward motion sample."""

        self.position = self.position + np.array([0.01, 0.0, 0.0])
        return SlamResult(
            timestamp=observation.timestamp,
            position=self.position.copy(),
            orientation_quat=self.orientation.copy(),
            tracking_ok=True,
            num_tracked_features=150,
            mean_reprojection_error=1.0,
        )
