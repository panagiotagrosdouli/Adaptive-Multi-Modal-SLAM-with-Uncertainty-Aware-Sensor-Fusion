"""Sensor abstractions for heterogeneous SLAM measurements."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np


class SensorModality(str, Enum):
    """Supported sensing modalities."""

    CAMERA = "camera"
    IMU = "imu"
    LIDAR = "lidar"
    RGBD = "rgbd"


@dataclass(slots=True)
class Calibration:
    """Calibration scaffold for extrinsics, intrinsics, and nominal covariance."""

    sensor_to_body: np.ndarray = field(default_factory=lambda: np.eye(4, dtype=float))
    intrinsics: dict[str, float] = field(default_factory=dict)
    covariance: np.ndarray = field(default_factory=lambda: np.eye(6, dtype=float))


@dataclass(slots=True)
class SensorMeasurement:
    """Timestamped sensor packet with uncertainty metadata."""

    timestamp: float
    modality: SensorModality
    data: Any
    covariance: np.ndarray
    reliability: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate timestamp, reliability bounds, and covariance symmetry."""

        if self.timestamp < 0.0:
            raise ValueError("timestamps must be non-negative seconds")
        if not 0.0 <= self.reliability <= 1.0:
            raise ValueError("reliability must be in [0, 1]")
        if self.covariance.ndim != 2 or self.covariance.shape[0] != self.covariance.shape[1]:
            raise ValueError("covariance must be square")
        if not np.allclose(self.covariance, self.covariance.T, atol=1e-9):
            raise ValueError("covariance must be symmetric")


def synchronize_measurements(
    measurements: list[SensorMeasurement], reference_time: float, tolerance: float
) -> list[SensorMeasurement]:
    """Return measurements inside a timestamp gate around ``reference_time``.

    Args:
        measurements: Candidate sensor measurements.
        reference_time: Synchronization reference timestamp in seconds.
        tolerance: Maximum absolute temporal offset in seconds.

    Returns:
        Measurements sorted by timestamp and accepted by the temporal gate.
    """

    if tolerance < 0.0:
        raise ValueError("tolerance must be non-negative")
    accepted = [m for m in measurements if abs(m.timestamp - reference_time) <= tolerance]
    return sorted(accepted, key=lambda m: m.timestamp)
