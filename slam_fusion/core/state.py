"""State definitions used by the adaptive SLAM prototypes."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


def _eye(n: int, scale: float = 1.0) -> np.ndarray:
    return np.eye(n, dtype=float) * scale


@dataclass(slots=True)
class RobotState:
    """Minimal metric SLAM state.

    Attributes:
        timestamp: State timestamp in seconds.
        pose: Homogeneous transform T_WB in SE(3), mapping body coordinates to world.
        velocity: Body velocity expressed in world coordinates.
        gyro_bias: IMU gyroscope bias.
        accel_bias: IMU accelerometer bias.
        covariance: Error-state covariance over pose, velocity, and IMU biases.
    """

    timestamp: float
    pose: np.ndarray = field(default_factory=lambda: _eye(4))
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=float))
    gyro_bias: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=float))
    accel_bias: np.ndarray = field(default_factory=lambda: np.zeros(3, dtype=float))
    covariance: np.ndarray = field(default_factory=lambda: _eye(15, 1e-3))

    def validate(self) -> None:
        """Raise ValueError if the state has inconsistent dimensions or covariance."""

        if self.pose.shape != (4, 4):
            raise ValueError("pose must be a 4x4 homogeneous matrix")
        if self.velocity.shape != (3,):
            raise ValueError("velocity must be a 3-vector")
        if self.gyro_bias.shape != (3,) or self.accel_bias.shape != (3,):
            raise ValueError("IMU biases must be 3-vectors")
        if self.covariance.shape != (15, 15):
            raise ValueError("covariance must be 15x15")
        eigvals = np.linalg.eigvalsh((self.covariance + self.covariance.T) / 2.0)
        if np.min(eigvals) < -1e-10:
            raise ValueError("covariance must be positive semi-definite")

    @property
    def position(self) -> np.ndarray:
        """Return the translational component of ``T_WB``."""

        return self.pose[:3, 3]
