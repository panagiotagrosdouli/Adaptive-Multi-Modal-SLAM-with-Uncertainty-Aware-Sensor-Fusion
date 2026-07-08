"""Trajectory metrics for SLAM and visual-inertial odometry evaluation.

The functions in this module intentionally avoid dataset-specific assumptions.  They
operate on NumPy arrays and implement the core quantities reported in SLAM papers:
root-mean-square Absolute Trajectory Error (ATE) and Relative Pose Error (RPE).

For monocular or visual-inertial pipelines, ATE is only meaningful after a clearly
specified alignment convention.  This module provides Umeyama similarity alignment
and rigid SE(3) alignment so benchmark scripts can state exactly what was used.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal

import numpy as np

AlignmentMode = Literal["none", "se3", "sim3"]


class MetricError(ValueError):
    """Raised when metric inputs are malformed or numerically invalid."""


class Alignment(str, Enum):
    """Supported trajectory-alignment conventions."""

    NONE = "none"
    SE3 = "se3"
    SIM3 = "sim3"


@dataclass(frozen=True)
class AlignmentTransform:
    """Similarity transform mapping estimated positions to ground truth.

    Attributes:
        scale: Isotropic scale.  Equals 1.0 for SE(3) alignment.
        rotation: 3x3 rotation matrix.
        translation: 3-vector translation.
    """

    scale: float
    rotation: np.ndarray
    translation: np.ndarray

    def apply(self, points: np.ndarray) -> np.ndarray:
        """Apply the transform to an Nx3 point array."""

        pts = _as_position_array(points, name="points")
        return self.scale * (pts @ self.rotation.T) + self.translation


def _as_position_array(points: np.ndarray, *, name: str) -> np.ndarray:
    """Convert an input to a finite Nx3 floating-point array."""

    array = np.asarray(points, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 3:
        raise MetricError(f"{name} must have shape (N, 3); got {array.shape}.")
    if array.shape[0] == 0:
        raise MetricError(f"{name} must contain at least one pose.")
    if not np.all(np.isfinite(array)):
        raise MetricError(f"{name} contains NaN or infinite values.")
    return array


def _validate_pair(ground_truth: np.ndarray, estimated: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Validate and return paired ground-truth and estimated positions."""

    gt = _as_position_array(ground_truth, name="ground_truth")
    est = _as_position_array(estimated, name="estimated")
    if gt.shape != est.shape:
        raise MetricError(
            "ground_truth and estimated must have identical shape after timestamp "
            f"association; got {gt.shape} and {est.shape}."
        )
    return gt, est


def umeyama_alignment(
    source: np.ndarray,
    target: np.ndarray,
    *,
    with_scale: bool = True,
) -> AlignmentTransform:
    """Estimate the least-squares similarity transform from source to target.

    This is the closed-form Umeyama alignment used by many SLAM evaluation tools.
    Given paired points x_i from the estimated trajectory and y_i from ground truth,
    it minimizes the squared residual || y_i - (s R x_i + t) ||^2.

    Args:
        source: Estimated Nx3 positions.
        target: Ground-truth Nx3 positions.
        with_scale: If True, estimate Sim(3) scale.  If False, estimate SE(3).

    Returns:
        AlignmentTransform mapping source points into the target frame.

    Raises:
        MetricError: If the input trajectories are degenerate.
    """

    src, dst = _validate_pair(source, target)
    if src.shape[0] < 3:
        raise MetricError("At least three matched poses are required for stable alignment.")

    mu_src = src.mean(axis=0)
    mu_dst = dst.mean(axis=0)
    src_centered = src - mu_src
    dst_centered = dst - mu_dst

    src_var = np.mean(np.sum(src_centered**2, axis=1))
    if src_var <= np.finfo(np.float64).eps:
        raise MetricError("Estimated trajectory is degenerate; source variance is zero.")

    covariance = (dst_centered.T @ src_centered) / src.shape[0]
    u_mat, singular_values, vt_mat = np.linalg.svd(covariance)

    reflection = np.eye(3)
    if np.linalg.det(u_mat) * np.linalg.det(vt_mat) < 0.0:
        reflection[-1, -1] = -1.0

    rotation = u_mat @ reflection @ vt_mat
    scale = float(np.sum(singular_values * np.diag(reflection)) / src_var) if with_scale else 1.0
    translation = mu_dst - scale * (rotation @ mu_src)

    return AlignmentTransform(scale=scale, rotation=rotation, translation=translation)


def align_positions(
    ground_truth: np.ndarray,
    estimated: np.ndarray,
    *,
    mode: AlignmentMode = "sim3",
) -> tuple[np.ndarray, AlignmentTransform | None]:
    """Align estimated positions to ground truth using a documented convention."""

    gt, est = _validate_pair(ground_truth, estimated)
    if mode == Alignment.NONE.value or mode == "none":
        return est.copy(), None
    if mode == Alignment.SE3.value or mode == "se3":
        transform = umeyama_alignment(est, gt, with_scale=False)
        return transform.apply(est), transform
    if mode == Alignment.SIM3.value or mode == "sim3":
        transform = umeyama_alignment(est, gt, with_scale=True)
        return transform.apply(est), transform
    raise MetricError(f"Unsupported alignment mode: {mode!r}.")


def root_mean_square_error(residuals: np.ndarray) -> float:
    """Return RMSE for an NxD residual matrix."""

    residuals = np.asarray(residuals, dtype=np.float64)
    if residuals.ndim != 2:
        raise MetricError(f"residuals must be two-dimensional; got {residuals.shape}.")
    if residuals.shape[0] == 0:
        raise MetricError("residuals must not be empty.")
    if not np.all(np.isfinite(residuals)):
        raise MetricError("residuals contain NaN or infinite values.")
    return float(np.sqrt(np.mean(np.sum(residuals**2, axis=1))))


def absolute_trajectory_error(
    ground_truth: np.ndarray,
    estimated: np.ndarray,
    *,
    alignment: AlignmentMode = "none",
) -> float:
    """Compute translational RMSE Absolute Trajectory Error.

    Args:
        ground_truth: Ground-truth Nx3 positions.
        estimated: Estimated Nx3 positions associated to the ground-truth stamps.
        alignment: ``"none"``, ``"se3"`` or ``"sim3"`` alignment applied before
            error computation.  The default preserves backward compatibility.

    Returns:
        Translational RMSE ATE in the same length unit as the input trajectories.
    """

    gt, est = _validate_pair(ground_truth, estimated)
    aligned_est, _ = align_positions(gt, est, mode=alignment)
    return root_mean_square_error(gt - aligned_est)


def relative_pose_error(
    ground_truth: np.ndarray,
    estimated: np.ndarray,
    *,
    delta: int = 1,
    alignment: AlignmentMode = "none",
) -> float:
    """Compute translational RMSE Relative Pose Error over a fixed index delta.

    Args:
        ground_truth: Ground-truth Nx3 positions.
        estimated: Estimated Nx3 positions.
        delta: Pose spacing used for relative translation increments.
        alignment: Optional trajectory alignment before computing increments.

    Returns:
        RMSE of relative translation-increment error.
    """

    if delta < 1:
        raise MetricError("delta must be a positive integer.")
    gt, est = _validate_pair(ground_truth, estimated)
    if gt.shape[0] <= delta:
        return 0.0

    aligned_est, _ = align_positions(gt, est, mode=alignment)
    gt_delta = gt[delta:] - gt[:-delta]
    est_delta = aligned_est[delta:] - aligned_est[:-delta]
    return root_mean_square_error(gt_delta - est_delta)
