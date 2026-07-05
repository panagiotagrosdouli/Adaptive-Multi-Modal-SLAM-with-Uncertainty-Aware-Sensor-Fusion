from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np


@dataclass
class SlamObservation:
    timestamp: float
    image: Optional[np.ndarray] = None
    imu_accel: Optional[np.ndarray] = None
    imu_gyro: Optional[np.ndarray] = None


@dataclass
class SlamResult:
    timestamp: float
    position: np.ndarray
    orientation_quat: np.ndarray
    tracking_ok: bool
    num_tracked_features: int = 0
    mean_reprojection_error: float = 0.0


class SlamBackend:
    def initialize(self) -> None:
        raise NotImplementedError

    def process(self, observation: SlamObservation) -> SlamResult:
        raise NotImplementedError

    def shutdown(self) -> None:
        pass


class DummySlamBackend(SlamBackend):
    def __init__(self) -> None:
        self.position = np.zeros(3)
        self.orientation = np.array([0.0, 0.0, 0.0, 1.0])

    def initialize(self) -> None:
        self.position = np.zeros(3)

    def process(self, observation: SlamObservation) -> SlamResult:
        self.position = self.position + np.array([0.01, 0.0, 0.0])
        return SlamResult(
            timestamp=observation.timestamp,
            position=self.position.copy(),
            orientation_quat=self.orientation.copy(),
            tracking_ok=True,
            num_tracked_features=150,
            mean_reprojection_error=1.0,
        )
