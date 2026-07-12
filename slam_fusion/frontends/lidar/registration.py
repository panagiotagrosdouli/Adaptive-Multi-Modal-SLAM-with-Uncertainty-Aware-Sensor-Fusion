"""Transparent point-cloud filtering and point-to-point ICP prototype."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.spatial import cKDTree


@dataclass(slots=True)
class RegistrationResult:
    transformation: np.ndarray
    fitness: float
    rmse: float
    correspondence_count: int
    degeneracy: float
    converged: bool


def filter_points(points: np.ndarray, voxel_size: float = 0.15,
                  min_range: float = 0.2, max_range: float = 80.0) -> np.ndarray:
    cloud = np.asarray(points, dtype=float)
    if cloud.ndim != 2 or cloud.shape[1] < 3:
        raise ValueError("point cloud must have shape (N, >=3)")
    cloud = cloud[:, :3]
    ranges = np.linalg.norm(cloud, axis=1)
    cloud = cloud[(ranges >= min_range) & (ranges <= max_range) & np.isfinite(cloud).all(axis=1)]
    if voxel_size <= 0 or not len(cloud):
        return cloud
    keys = np.floor(cloud / voxel_size).astype(np.int64)
    _, indices = np.unique(keys, axis=0, return_index=True)
    return cloud[np.sort(indices)]


def _rigid_transform(source: np.ndarray, target: np.ndarray) -> np.ndarray:
    source_center = source.mean(axis=0)
    target_center = target.mean(axis=0)
    u, _, vt = np.linalg.svd((source - source_center).T @ (target - target_center))
    rotation = vt.T @ u.T
    if np.linalg.det(rotation) < 0:
        vt[-1] *= -1
        rotation = vt.T @ u.T
    translation = target_center - rotation @ source_center
    transform = np.eye(4)
    transform[:3, :3] = rotation
    transform[:3, 3] = translation
    return transform


def register_icp(source: np.ndarray, target: np.ndarray, max_iterations: int = 30,
                 correspondence_distance: float = 1.0, tolerance: float = 1e-5) -> RegistrationResult:
    source = filter_points(source)
    target = filter_points(target)
    if len(source) < 6 or len(target) < 6:
        return RegistrationResult(np.eye(4), 0.0, float("inf"), 0, 1.0, False)
    tree = cKDTree(target)
    transform = np.eye(4)
    previous_rmse = float("inf")
    converged = False
    count = 0
    distances = np.empty(0)
    matched_source = source
    matched_target = target[: len(source)] if len(target) >= len(source) else target
    for _ in range(max_iterations):
        transformed = (transform[:3, :3] @ source.T).T + transform[:3, 3]
        distances, indices = tree.query(transformed, k=1)
        valid = distances <= correspondence_distance
        count = int(valid.sum())
        if count < 6:
            break
        matched_source = transformed[valid]
        matched_target = target[indices[valid]]
        increment = _rigid_transform(matched_source, matched_target)
        transform = increment @ transform
        rmse = float(np.sqrt(np.mean(distances[valid] ** 2)))
        if abs(previous_rmse - rmse) < tolerance:
            converged = True
            previous_rmse = rmse
            break
        previous_rmse = rmse
    centered = matched_source - matched_source.mean(axis=0)
    eigenvalues = np.linalg.eigvalsh(centered.T @ centered / max(len(centered), 1))
    degeneracy = float(1.0 - eigenvalues[0] / max(eigenvalues[-1], 1e-12))
    fitness = count / max(len(source), 1)
    return RegistrationResult(transform, float(fitness), previous_rmse, count, degeneracy, converged)
