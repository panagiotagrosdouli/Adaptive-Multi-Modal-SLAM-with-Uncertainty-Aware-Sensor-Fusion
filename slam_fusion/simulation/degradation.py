"""Deterministic sensor-degradation injection for controlled experiments."""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True, slots=True)
class DegradationRecord:
    modality: str
    kind: str
    severity: float
    seed: int


def _severity(value: float) -> float:
    if not 0.0 <= value <= 1.0:
        raise ValueError("severity must be in [0, 1]")
    return float(value)


class DegradationEngine:
    """Apply reproducible degradations without changing estimator logic."""

    def __init__(self, seed: int = 0):
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.records: list[DegradationRecord] = []

    def camera_blur(self, image: np.ndarray, severity: float) -> np.ndarray:
        severity = _severity(severity)
        kernel = max(1, 2 * int(1 + 7 * severity) + 1)
        self.records.append(DegradationRecord("camera", "blur", severity, self.seed))
        return cv2.GaussianBlur(image, (kernel, kernel), 0)

    def camera_dropout(self, image: np.ndarray, severity: float) -> np.ndarray | None:
        severity = _severity(severity)
        self.records.append(DegradationRecord("camera", "dropout", severity, self.seed))
        return None if self.rng.random() < severity else image.copy()

    def imu_bias_drift(self, samples: np.ndarray, severity: float) -> np.ndarray:
        severity = _severity(severity)
        data = np.asarray(samples, dtype=float).copy()
        drift = np.linspace(0.0, severity, len(data), dtype=float)[:, None]
        axis_scale = self.rng.normal(0.0, 0.15, size=(1, data.shape[1]))
        self.records.append(DegradationRecord("imu", "bias_drift", severity, self.seed))
        return data + drift * axis_scale

    def timestamp_jitter(self, timestamps: np.ndarray, severity: float, max_seconds: float = 0.05) -> np.ndarray:
        severity = _severity(severity)
        timestamps = np.asarray(timestamps, dtype=float)
        jitter = self.rng.normal(0.0, severity * max_seconds, size=timestamps.shape)
        self.records.append(DegradationRecord("cross_modal", "timestamp_jitter", severity, self.seed))
        return timestamps + jitter

    def sparse_lidar(self, points: np.ndarray, severity: float) -> np.ndarray:
        severity = _severity(severity)
        points = np.asarray(points)
        keep = self.rng.random(len(points)) >= severity
        self.records.append(DegradationRecord("lidar", "sparse_returns", severity, self.seed))
        return points[keep]

    def corrupt_depth(self, depth: np.ndarray, severity: float, invalid_value: float = 0.0) -> np.ndarray:
        severity = _severity(severity)
        result = np.asarray(depth, dtype=float).copy()
        mask = self.rng.random(result.shape) < severity
        result[mask] = invalid_value
        self.records.append(DegradationRecord("rgbd", "missing_depth", severity, self.seed))
        return result
