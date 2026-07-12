"""Minimal SE(2) pose graph for CPU smoke tests and loop-closure research.

Status: Research Prototype. It is intentionally transparent and is not a replacement
for a production SE(3) optimizer such as GTSAM.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import least_squares


def _wrap(angle: float) -> float:
    return float((angle + np.pi) % (2 * np.pi) - np.pi)


@dataclass(frozen=True, slots=True)
class PoseFactor:
    source: int
    target: int
    measurement: np.ndarray
    information: np.ndarray
    kind: str = "odometry"
    robust_scale: float = 1.0

    def __post_init__(self) -> None:
        measurement = np.asarray(self.measurement, dtype=float)
        information = np.asarray(self.information, dtype=float)
        if measurement.shape != (3,) or information.shape != (3, 3):
            raise ValueError("SE(2) factor expects a 3-vector and 3x3 information")
        if self.source == self.target or self.robust_scale <= 0:
            raise ValueError("invalid pose factor")


class PoseGraph2D:
    """Batch pose graph with fixed first pose and robust least squares."""

    def __init__(self) -> None:
        self.poses: dict[int, np.ndarray] = {}
        self.factors: list[PoseFactor] = []

    def add_pose(self, key: int, pose: np.ndarray) -> None:
        pose = np.asarray(pose, dtype=float).reshape(3)
        self.poses[key] = pose.copy()

    def add_factor(self, factor: PoseFactor) -> None:
        if factor.source not in self.poses or factor.target not in self.poses:
            raise KeyError("factor endpoints must be registered poses")
        self.factors.append(factor)

    @staticmethod
    def relative(source: np.ndarray, target: np.ndarray) -> np.ndarray:
        dx, dy = target[:2] - source[:2]
        c, s = np.cos(source[2]), np.sin(source[2])
        return np.array([c * dx + s * dy, -s * dx + c * dy, _wrap(target[2] - source[2])])

    def optimize(self, max_iterations: int = 100) -> dict[int, np.ndarray]:
        if len(self.poses) < 2 or not self.factors:
            return {key: pose.copy() for key, pose in self.poses.items()}
        keys = sorted(self.poses)
        anchor = keys[0]
        free = keys[1:]
        initial = np.concatenate([self.poses[key] for key in free])

        def unpack(vector: np.ndarray) -> dict[int, np.ndarray]:
            poses = {anchor: self.poses[anchor]}
            for index, key in enumerate(free):
                poses[key] = vector[3 * index : 3 * index + 3]
            return poses

        def residuals(vector: np.ndarray) -> np.ndarray:
            poses = unpack(vector)
            residual_list: list[np.ndarray] = []
            for factor in self.factors:
                error = self.relative(poses[factor.source], poses[factor.target]) - factor.measurement
                error[2] = _wrap(error[2])
                sqrt_information = np.linalg.cholesky(factor.information)
                residual_list.append(sqrt_information @ error / factor.robust_scale)
            return np.concatenate(residual_list)

        result = least_squares(
            residuals,
            initial,
            loss="huber",
            f_scale=1.0,
            max_nfev=max_iterations,
        )
        optimized = unpack(result.x)
        self.poses = {key: pose.copy() for key, pose in optimized.items()}
        return optimized

    def total_error(self) -> float:
        total = 0.0
        for factor in self.factors:
            error = self.relative(self.poses[factor.source], self.poses[factor.target]) - factor.measurement
            error[2] = _wrap(error[2])
            total += float(error @ factor.information @ error)
        return total
