from dataclasses import dataclass
from typing import List, Tuple

import numpy as np

from src.metrics import absolute_trajectory_error, relative_pose_error
from src.trajectory import TrajectoryPose


@dataclass
class TrajectoryEvaluation:
    matched_poses: int
    ate: float
    rpe: float


def match_trajectories_by_timestamp(
    ground_truth: List[TrajectoryPose],
    estimated: List[TrajectoryPose],
    max_time_difference_ns: int = 10_000_000,
) -> Tuple[np.ndarray, np.ndarray]:
    """Match estimated and ground-truth poses by nearest timestamp.

    Args:
        ground_truth: Ground-truth trajectory poses.
        estimated: Estimated trajectory poses.
        max_time_difference_ns: Maximum allowed timestamp difference for a match.

    Returns:
        Two Nx3 arrays containing matched ground-truth and estimated positions.
    """

    if not ground_truth or not estimated:
        return np.empty((0, 3)), np.empty((0, 3))

    gt_sorted = sorted(ground_truth, key=lambda pose: pose.timestamp_ns)
    est_sorted = sorted(estimated, key=lambda pose: pose.timestamp_ns)

    gt_positions = []
    est_positions = []
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

    return np.asarray(gt_positions), np.asarray(est_positions)


def evaluate_trajectory(
    ground_truth: List[TrajectoryPose],
    estimated: List[TrajectoryPose],
    max_time_difference_ns: int = 10_000_000,
) -> TrajectoryEvaluation:
    gt_positions, est_positions = match_trajectories_by_timestamp(
        ground_truth,
        estimated,
        max_time_difference_ns=max_time_difference_ns,
    )

    if len(gt_positions) == 0:
        return TrajectoryEvaluation(matched_poses=0, ate=float('nan'), rpe=float('nan'))

    return TrajectoryEvaluation(
        matched_poses=len(gt_positions),
        ate=absolute_trajectory_error(gt_positions, est_positions),
        rpe=relative_pose_error(gt_positions, est_positions),
    )
