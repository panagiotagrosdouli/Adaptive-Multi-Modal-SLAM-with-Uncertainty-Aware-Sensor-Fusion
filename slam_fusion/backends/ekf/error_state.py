"""Dependency-light error-state EKF prototype for multi-modal fusion.

The nominal state is position, velocity, quaternion, accelerometer bias, and gyroscope
bias. The 15D covariance uses errors [dp, dv, dtheta, dba, dbg].
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


def _skew(vector: np.ndarray) -> np.ndarray:
    x, y, z = vector
    return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])


def _quat_multiply(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    w1, x1, y1, z1 = left
    w2, x2, y2, z2 = right
    return np.array(
        [
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        ]
    )


def _quat_to_rotation(quaternion: np.ndarray) -> np.ndarray:
    w, x, y, z = quaternion
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ]
    )


@dataclass(slots=True)
class ErrorState:
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    quaternion_wxyz: np.ndarray = field(default_factory=lambda: np.array([1.0, 0.0, 0.0, 0.0]))
    accel_bias: np.ndarray = field(default_factory=lambda: np.zeros(3))
    gyro_bias: np.ndarray = field(default_factory=lambda: np.zeros(3))
    covariance: np.ndarray = field(default_factory=lambda: np.eye(15) * 1e-3)
    timestamp: float = 0.0


@dataclass(frozen=True, slots=True)
class UpdateResult:
    accepted: bool
    nis: float
    innovation: np.ndarray


class ErrorStateEKF:
    """Working research EKF with IMU propagation and generic linear updates."""

    def __init__(
        self,
        state: ErrorState | None = None,
        gravity: np.ndarray | None = None,
        accel_noise: float = 0.08,
        gyro_noise: float = 0.01,
        accel_bias_rw: float = 0.001,
        gyro_bias_rw: float = 0.0001,
    ) -> None:
        self.state = state or ErrorState()
        self.gravity = np.asarray(gravity if gravity is not None else [0.0, 0.0, -9.81], dtype=float)
        noises = (accel_noise, gyro_noise, accel_bias_rw, gyro_bias_rw)
        if any(value <= 0 for value in noises):
            raise ValueError("process noise values must be positive")
        self.noises = noises

    def propagate(self, timestamp: float, acceleration: np.ndarray, angular_rate: np.ndarray) -> None:
        dt = float(timestamp - self.state.timestamp)
        if dt <= 0:
            raise ValueError("IMU timestamps must be strictly increasing")
        acceleration = np.asarray(acceleration, dtype=float).reshape(3) - self.state.accel_bias
        angular_rate = np.asarray(angular_rate, dtype=float).reshape(3) - self.state.gyro_bias
        rotation = _quat_to_rotation(self.state.quaternion_wxyz)
        world_acceleration = rotation @ acceleration + self.gravity
        self.state.position += self.state.velocity * dt + 0.5 * world_acceleration * dt * dt
        self.state.velocity += world_acceleration * dt
        angle = float(np.linalg.norm(angular_rate) * dt)
        if angle > 1e-12:
            axis = angular_rate / np.linalg.norm(angular_rate)
            delta_q = np.concatenate(([np.cos(angle / 2)], axis * np.sin(angle / 2)))
            self.state.quaternion_wxyz = _quat_multiply(self.state.quaternion_wxyz, delta_q)
            self.state.quaternion_wxyz /= np.linalg.norm(self.state.quaternion_wxyz)
        transition = np.eye(15)
        transition[0:3, 3:6] = np.eye(3) * dt
        transition[3:6, 6:9] = -rotation @ _skew(acceleration) * dt
        transition[3:6, 9:12] = -rotation * dt
        transition[6:9, 12:15] = -np.eye(3) * dt
        accel_noise, gyro_noise, accel_rw, gyro_rw = self.noises
        spectral = np.diag(
            [accel_noise**2] * 3
            + [gyro_noise**2] * 3
            + [accel_rw**2] * 3
            + [gyro_rw**2] * 3
        )
        noise_map = np.zeros((15, 12))
        noise_map[3:6, 0:3] = rotation
        noise_map[6:9, 3:6] = np.eye(3)
        noise_map[9:12, 6:9] = np.eye(3)
        noise_map[12:15, 9:12] = np.eye(3)
        self.state.covariance = transition @ self.state.covariance @ transition.T + noise_map @ spectral @ noise_map.T * dt
        self.state.covariance = 0.5 * (self.state.covariance + self.state.covariance.T)
        self.state.timestamp = float(timestamp)

    def update(
        self,
        measurement: np.ndarray,
        prediction: np.ndarray,
        jacobian: np.ndarray,
        covariance: np.ndarray,
        *,
        gate_threshold: float | None = None,
    ) -> UpdateResult:
        measurement = np.asarray(measurement, dtype=float).reshape(-1)
        prediction = np.asarray(prediction, dtype=float).reshape(-1)
        jacobian = np.asarray(jacobian, dtype=float)
        covariance = np.asarray(covariance, dtype=float)
        innovation = measurement - prediction
        innovation_covariance = jacobian @ self.state.covariance @ jacobian.T + covariance
        nis = float(innovation @ np.linalg.solve(innovation_covariance, innovation))
        if gate_threshold is not None and nis > gate_threshold:
            return UpdateResult(False, nis, innovation)
        gain = np.linalg.solve(innovation_covariance, jacobian @ self.state.covariance).T
        error = gain @ innovation
        self._inject(error)
        identity = np.eye(15)
        residual_map = identity - gain @ jacobian
        self.state.covariance = residual_map @ self.state.covariance @ residual_map.T + gain @ covariance @ gain.T
        self.state.covariance = 0.5 * (self.state.covariance + self.state.covariance.T)
        return UpdateResult(True, nis, innovation)

    def update_position(
        self, position: np.ndarray, covariance: np.ndarray, gate_threshold: float | None = None
    ) -> UpdateResult:
        jacobian = np.zeros((3, 15))
        jacobian[:, 0:3] = np.eye(3)
        return self.update(position, self.state.position, jacobian, covariance, gate_threshold=gate_threshold)

    def update_velocity(
        self, velocity: np.ndarray, covariance: np.ndarray, gate_threshold: float | None = None
    ) -> UpdateResult:
        jacobian = np.zeros((3, 15))
        jacobian[:, 3:6] = np.eye(3)
        return self.update(velocity, self.state.velocity, jacobian, covariance, gate_threshold=gate_threshold)

    def _inject(self, error: np.ndarray) -> None:
        self.state.position += error[0:3]
        self.state.velocity += error[3:6]
        rotation_error = error[6:9]
        delta_q = np.concatenate(([1.0], 0.5 * rotation_error))
        self.state.quaternion_wxyz = _quat_multiply(self.state.quaternion_wxyz, delta_q)
        self.state.quaternion_wxyz /= np.linalg.norm(self.state.quaternion_wxyz)
        self.state.accel_bias += error[9:12]
        self.state.gyro_bias += error[12:15]
