"""Dependency-light relocalization research prototype.

Descriptor similarity proposes candidates; a geometric consistency test must pass
before a pose hypothesis is accepted.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class RelocalizationResult:
    success: bool
    keyframe_id: str | None
    pose: np.ndarray | None
    confidence: float
    inliers: int
    reason: str


@dataclass(frozen=True, slots=True)
class KeyframeRecord:
    keyframe_id: str
    descriptor: np.ndarray
    points_3d: np.ndarray
    pose: np.ndarray


class Relocalizer:
    """Retrieve keyframes and verify a rigid 3-D alignment hypothesis."""

    def __init__(self, min_inliers: int = 6, max_rmse: float = 0.25):
        self.min_inliers = min_inliers
        self.max_rmse = max_rmse
        self._records: list[KeyframeRecord] = []

    def add(self, record: KeyframeRecord) -> None:
        if record.pose.shape != (4, 4):
            raise ValueError("pose must be 4x4")
        if record.points_3d.ndim != 2 or record.points_3d.shape[1] != 3:
            raise ValueError("points_3d must have shape (N, 3)")
        self._records.append(record)

    def relocalize(self, descriptor: np.ndarray, points_3d: np.ndarray) -> RelocalizationResult:
        if not self._records:
            return RelocalizationResult(False, None, None, 0.0, 0, "empty keyframe database")
        if points_3d.ndim != 2 or points_3d.shape[1] != 3:
            raise ValueError("points_3d must have shape (N, 3)")
        descriptor = np.asarray(descriptor, dtype=float).ravel()
        scored = sorted(self._records, key=lambda r: self._cosine_distance(descriptor, r.descriptor))
        for candidate in scored[:5]:
            n = min(len(points_3d), len(candidate.points_3d))
            if n < self.min_inliers:
                continue
            rotation, translation = self._align(points_3d[:n], candidate.points_3d[:n])
            transformed = (rotation @ points_3d[:n].T).T + translation
            errors = np.linalg.norm(transformed - candidate.points_3d[:n], axis=1)
            inliers = int(np.sum(errors <= self.max_rmse))
            rmse = float(np.sqrt(np.mean(errors**2)))
            if inliers >= self.min_inliers and rmse <= self.max_rmse:
                relative = np.eye(4)
                relative[:3, :3] = rotation
                relative[:3, 3] = translation
                pose = candidate.pose @ relative
                confidence = float(np.clip((inliers / n) * np.exp(-rmse / self.max_rmse), 0.0, 1.0))
                return RelocalizationResult(True, candidate.keyframe_id, pose, confidence, inliers, "geometric verification passed")
        return RelocalizationResult(False, None, None, 0.0, 0, "no geometrically consistent candidate")

    @staticmethod
    def _cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
        b = np.asarray(b, dtype=float).ravel()
        if a.shape != b.shape:
            return float("inf")
        denominator = np.linalg.norm(a) * np.linalg.norm(b)
        return 1.0 if denominator == 0.0 else float(1.0 - np.dot(a, b) / denominator)

    @staticmethod
    def _align(source: np.ndarray, target: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        source_center = source.mean(axis=0)
        target_center = target.mean(axis=0)
        u, _, vt = np.linalg.svd((source - source_center).T @ (target - target_center))
        rotation = vt.T @ u.T
        if np.linalg.det(rotation) < 0.0:
            vt[-1] *= -1.0
            rotation = vt.T @ u.T
        translation = target_center - rotation @ source_center
        return rotation, translation
