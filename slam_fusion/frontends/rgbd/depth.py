"""RGB-D validation, uncertainty, alignment, and 3-D projection utilities."""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(slots=True)
class DepthResult:
    points: np.ndarray
    colors: np.ndarray | None
    variance: np.ndarray
    valid_mask: np.ndarray
    diagnostics: dict[str, float]


class RGBDFrontend:
    def __init__(self, depth_scale: float = 1000.0, min_depth: float = 0.15,
                 max_depth: float = 8.0, noise_a: float = 0.002, noise_b: float = 0.001):
        if depth_scale <= 0 or min_depth <= 0 or max_depth <= min_depth:
            raise ValueError("invalid depth configuration")
        self.depth_scale = depth_scale
        self.min_depth = min_depth
        self.max_depth = max_depth
        self.noise_a = noise_a
        self.noise_b = noise_b

    def process(self, depth: np.ndarray, intrinsics: np.ndarray,
                color: np.ndarray | None = None, stride: int = 2) -> DepthResult:
        raw = np.asarray(depth)
        if raw.ndim != 2:
            raise ValueError("depth image must be two-dimensional")
        metric = raw.astype(float) / self.depth_scale if np.issubdtype(raw.dtype, np.integer) else raw.astype(float)
        valid = np.isfinite(metric) & (metric >= self.min_depth) & (metric <= self.max_depth)
        rows, cols = np.indices(metric.shape)
        sample = valid & (rows % max(stride, 1) == 0) & (cols % max(stride, 1) == 0)
        k = np.asarray(intrinsics, dtype=float)
        if k.shape != (3, 3) or abs(np.linalg.det(k)) < 1e-12:
            raise ValueError("intrinsics must be an invertible 3x3 matrix")
        z = metric[sample]
        x = (cols[sample] - k[0, 2]) * z / k[0, 0]
        y = (rows[sample] - k[1, 2]) * z / k[1, 1]
        points = np.column_stack([x, y, z])
        variance = (self.noise_a + self.noise_b * z**2) ** 2
        colors = None
        if color is not None:
            image = np.asarray(color)
            if image.shape[:2] != metric.shape:
                image = cv2.resize(image, (metric.shape[1], metric.shape[0]), interpolation=cv2.INTER_LINEAR)
            colors = image[sample]
        invalid_ratio = 1.0 - float(valid.mean())
        saturated_ratio = float(((metric <= self.min_depth) | (metric >= self.max_depth)).mean())
        diagnostics = {
            "valid_depth_ratio": float(valid.mean()),
            "invalid_depth_ratio": invalid_ratio,
            "saturation_ratio": saturated_ratio,
            "median_depth_m": float(np.median(z)) if len(z) else float("nan"),
            "mean_depth_variance": float(np.mean(variance)) if len(variance) else float("inf"),
            "point_count": float(len(points)),
        }
        return DepthResult(points, colors, variance, valid, diagnostics)
