"""Analytically transparent IMU preintegration research prototype."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.spatial.transform import Rotation


@dataclass(slots=True)
class IMUNoise:
    accelerometer_density: float = 0.08
    gyroscope_density: float = 0.004
    accelerometer_random_walk: float = 0.0004
    gyroscope_random_walk: float = 0.00002

    def validate(self) -> None:
        if min(self.accelerometer_density, self.gyroscope_density,
               self.accelerometer_random_walk, self.gyroscope_random_walk) <= 0:
            raise ValueError("IMU noise parameters must be positive")


@dataclass(slots=True)
class PreintegratedIMU:
    delta_time: float = 0.0
    delta_position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    delta_velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    delta_rotation: np.ndarray = field(default_factory=lambda: np.eye(3))
    covariance: np.ndarray = field(default_factory=lambda: np.zeros((9, 9)))
    packet_count: int = 0
    lost_packets: int = 0
    saturation_events: int = 0
    jitter_std: float = 0.0


class IMUPreintegrator:
    def __init__(self, noise: IMUNoise | None = None, max_accel: float = 160.0,
                 max_gyro: float = 35.0):
        self.noise = noise or IMUNoise()
        self.noise.validate()
        self.max_accel = max_accel
        self.max_gyro = max_gyro
        self.reset()

    def reset(self) -> None:
        self.result = PreintegratedIMU()
        self._last_timestamp: float | None = None
        self._dts: list[float] = []

    def integrate(self, timestamp: float, acceleration: np.ndarray, angular_velocity: np.ndarray,
                  accel_bias: np.ndarray | None = None, gyro_bias: np.ndarray | None = None) -> None:
        acceleration = np.asarray(acceleration, dtype=float).reshape(3)
        angular_velocity = np.asarray(angular_velocity, dtype=float).reshape(3)
        accel_bias = np.zeros(3) if accel_bias is None else np.asarray(accel_bias, dtype=float)
        gyro_bias = np.zeros(3) if gyro_bias is None else np.asarray(gyro_bias, dtype=float)
        if self._last_timestamp is None:
            self._last_timestamp = float(timestamp)
            return
        dt = float(timestamp) - self._last_timestamp
        if dt <= 0:
            raise ValueError("IMU timestamps must be strictly increasing")
        self._last_timestamp = float(timestamp)
        self._dts.append(dt)

        accel = acceleration - accel_bias
        gyro = angular_velocity - gyro_bias
        if np.linalg.norm(accel) > self.max_accel or np.linalg.norm(gyro) > self.max_gyro:
            self.result.saturation_events += 1

        rotation_increment = Rotation.from_rotvec(gyro * dt).as_matrix()
        acceleration_local = self.result.delta_rotation @ accel
        self.result.delta_position += self.result.delta_velocity * dt + 0.5 * acceleration_local * dt**2
        self.result.delta_velocity += acceleration_local * dt
        self.result.delta_rotation = self.result.delta_rotation @ rotation_increment
        self.result.delta_time += dt
        self.result.packet_count += 1

        q_accel = self.noise.accelerometer_density**2
        q_gyro = self.noise.gyroscope_density**2
        process = np.diag([q_accel * dt**3 / 3] * 3 + [q_accel * dt] * 3 + [q_gyro * dt] * 3)
        self.result.covariance += process
        self.result.covariance = 0.5 * (self.result.covariance + self.result.covariance.T)
        self.result.jitter_std = float(np.std(self._dts)) if len(self._dts) > 1 else 0.0

    def mark_packet_loss(self, count: int = 1) -> None:
        self.result.lost_packets += max(0, int(count))

    def diagnostics(self) -> dict[str, float]:
        total = self.result.packet_count + self.result.lost_packets
        return {
            "packet_count": float(self.result.packet_count),
            "packet_loss_ratio": self.result.lost_packets / max(total, 1),
            "saturation_events": float(self.result.saturation_events),
            "timestamp_jitter_std": self.result.jitter_std,
            "covariance_trace": float(np.trace(self.result.covariance)),
        }
