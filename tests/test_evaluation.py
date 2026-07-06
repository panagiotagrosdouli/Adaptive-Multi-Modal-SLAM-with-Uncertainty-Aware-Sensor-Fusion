import math

from src.evaluation import evaluate_trajectory, match_trajectories_by_timestamp
from src.trajectory import TrajectoryPose


def pose(timestamp_ns, x, y=0.0, z=0.0):
    return TrajectoryPose(
        timestamp_ns=timestamp_ns,
        tx=x,
        ty=y,
        tz=z,
        qx=0.0,
        qy=0.0,
        qz=0.0,
        qw=1.0,
    )


def test_match_trajectories_by_timestamp():
    ground_truth = [pose(100, 0.0), pose(200, 1.0), pose(300, 2.0)]
    estimated = [pose(102, 0.1), pose(198, 1.1), pose(400, 10.0)]

    gt_positions, est_positions = match_trajectories_by_timestamp(
        ground_truth,
        estimated,
        max_time_difference_ns=5,
    )

    assert gt_positions.shape == (2, 3)
    assert est_positions.shape == (2, 3)


def test_evaluate_trajectory_returns_ate_and_rpe():
    ground_truth = [pose(100, 0.0), pose(200, 1.0), pose(300, 2.0)]
    estimated = [pose(100, 0.1), pose(200, 1.1), pose(300, 2.1)]

    evaluation = evaluate_trajectory(ground_truth, estimated)

    assert evaluation.matched_poses == 3
    assert evaluation.ate > 0.0
    assert evaluation.rpe < 1e-6


def test_evaluate_trajectory_handles_no_matches():
    ground_truth = [pose(100, 0.0)]
    estimated = [pose(1_000_000_000, 0.0)]

    evaluation = evaluate_trajectory(
        ground_truth,
        estimated,
        max_time_difference_ns=5,
    )

    assert evaluation.matched_poses == 0
    assert math.isnan(evaluation.ate)
    assert math.isnan(evaluation.rpe)
