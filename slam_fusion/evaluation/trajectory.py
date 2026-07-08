"""Trajectory evaluation utilities for SLAM experiments."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class TrajectoryMetrics:
    """Common trajectory metrics."""

    ate_rmse: float
    rpe_rmse: float
    drift_final: float
    matched_poses: int


def absolute_trajectory_error(estimated: np.ndarray, ground_truth: np.ndarray) -> float:
    """Compute translational ATE RMSE after external alignment/association."""

    estimated = np.asarray(estimated, dtype=float)
    ground_truth = np.asarray(ground_truth, dtype=float)
    if estimated.shape != ground_truth.shape or estimated.ndim != 2 or estimated.shape[1] != 3:
        raise ValueError("trajectories must have shape (N, 3) and match")
    errors = estimated - ground_truth
    return float(np.sqrt(np.mean(np.sum(errors**2, axis=1))))


def relative_pose_error(estimated: np.ndarray, ground_truth: np.ndarray, delta: int = 1) -> float:
    """Compute translational RPE RMSE over a fixed index interval."""

    if delta <= 0:
        raise ValueError("delta must be positive")
    estimated = np.asarray(estimated, dtype=float)
    ground_truth = np.asarray(ground_truth, dtype=float)
    if estimated.shape != ground_truth.shape or estimated.shape[0] <= delta:
        raise ValueError("trajectories must match and contain more samples than delta")
    est_rel = estimated[delta:] - estimated[:-delta]
    gt_rel = ground_truth[delta:] - ground_truth[:-delta]
    errors = est_rel - gt_rel
    return float(np.sqrt(np.mean(np.sum(errors**2, axis=1))))


def final_drift(estimated: np.ndarray, ground_truth: np.ndarray) -> float:
    """Final-position drift in meters."""

    estimated = np.asarray(estimated, dtype=float)
    ground_truth = np.asarray(ground_truth, dtype=float)
    if estimated.shape != ground_truth.shape or estimated.shape[0] == 0:
        raise ValueError("trajectories must be non-empty and match")
    return float(np.linalg.norm(estimated[-1] - ground_truth[-1]))


def summarize_trajectory(estimated: np.ndarray, ground_truth: np.ndarray, delta: int = 1) -> TrajectoryMetrics:
    """Compute ATE, RPE, final drift, and matched-pose count."""

    return TrajectoryMetrics(
        ate_rmse=absolute_trajectory_error(estimated, ground_truth),
        rpe_rmse=relative_pose_error(estimated, ground_truth, delta=delta),
        drift_final=final_drift(estimated, ground_truth),
        matched_poses=int(np.asarray(estimated).shape[0]),
    )
