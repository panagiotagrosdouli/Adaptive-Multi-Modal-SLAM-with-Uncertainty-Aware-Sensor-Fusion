"""Trajectory association and evaluation for SLAM benchmarks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from src.metrics import (
    AlignmentMode,
    MetricError,
    absolute_trajectory_error,
    relative_pose_error,
)
from src.trajectory import TrajectoryPose


@dataclass(frozen=True)
class TrajectoryEvaluation:
    """Summary of timestamp-associated trajectory accuracy."""

    matched_poses: int
    ate: float
    rpe: float
    alignment: AlignmentMode = "none"
    max_time_difference_ns: int = 10_000_000


def match_trajectories_by_timestamp(
    ground_truth: Sequence[TrajectoryPose],
    estimated: Sequence[TrajectoryPose],
    max_time_difference_ns: int = 10_000_000,
) -> tuple[np.ndarray, np.ndarray]:
    """Match estimated and ground-truth poses by nearest timestamp.

    The function performs monotonic nearest-neighbor association under a maximum
    time gate. It is appropriate for already time-synchronized trajectories such
    as EuRoC exports. For asynchronous sensors with clock drift, a dedicated
    time-offset calibration step should be applied before evaluation.
    """

    if max_time_difference_ns < 0:
        raise ValueError("max_time_difference_ns must be non-negative.")
    if not ground_truth or not estimated:
        empty = np.empty((0, 3), dtype=np.float64)
        return empty, empty

    gt_sorted = sorted(ground_truth, key=lambda pose: pose.timestamp_ns)
    est_sorted = sorted(estimated, key=lambda pose: pose.timestamp_ns)

    gt_positions: list[list[float]] = []
    est_positions: list[list[float]] = []
    gt_index = 0

    for est_pose in est_sorted:
        while (
            gt_index + 1 < len(gt_sorted)
            and abs(gt_sorted[gt_index + 1].timestamp_ns - est_pose.timestamp_ns)
            <= abs(gt_sorted[gt_index].timestamp_ns - est_pose.timestamp_ns)
        ):
            gt_index += 1

        gt_pose = gt_sorted[gt_index]
        time_difference = abs(gt_pose.timestamp_ns - est_pose.timestamp_ns)
        if time_difference <= max_time_difference_ns:
            gt_positions.append([gt_pose.tx, gt_pose.ty, gt_pose.tz])
            est_positions.append([est_pose.tx, est_pose.ty, est_pose.tz])

    return np.asarray(gt_positions, dtype=np.float64), np.asarray(est_positions, dtype=np.float64)


def evaluate_trajectory(
    ground_truth: Sequence[TrajectoryPose],
    estimated: Sequence[TrajectoryPose],
    max_time_difference_ns: int = 10_000_000,
    *,
    alignment: AlignmentMode = "none",
    rpe_delta: int = 1,
) -> TrajectoryEvaluation:
    """Evaluate an estimated trajectory using ATE and RPE."""

    gt_positions, est_positions = match_trajectories_by_timestamp(
        ground_truth,
        estimated,
        max_time_difference_ns=max_time_difference_ns,
    )

    if len(gt_positions) == 0:
        return TrajectoryEvaluation(
            matched_poses=0,
            ate=float("nan"),
            rpe=float("nan"),
            alignment=alignment,
            max_time_difference_ns=max_time_difference_ns,
        )

    try:
        ate = absolute_trajectory_error(gt_positions, est_positions, alignment=alignment)
        rpe = relative_pose_error(
            gt_positions,
            est_positions,
            delta=rpe_delta,
            alignment=alignment,
        )
    except MetricError as exc:
        raise ValueError(f"Trajectory evaluation failed: {exc}") from exc

    return TrajectoryEvaluation(
        matched_poses=len(gt_positions),
        ate=ate,
        rpe=rpe,
        alignment=alignment,
        max_time_difference_ns=max_time_difference_ns,
    )
