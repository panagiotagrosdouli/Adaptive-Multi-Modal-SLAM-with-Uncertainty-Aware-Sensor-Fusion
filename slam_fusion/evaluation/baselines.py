"""Baseline registry for honest SLAM comparisons.

The registry separates implemented baselines from prototypes and planned
experiments. It intentionally stores no benchmark numbers; metrics must come
from reproducible experiment outputs under ``results/``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BaselineStatus(str, Enum):
    """Maturity level for a baseline."""

    IMPLEMENTED = "Implemented"
    PROTOTYPE = "Prototype"
    PLANNED = "Planned"
    PENDING_RESULTS = "Pending results"


@dataclass(frozen=True, slots=True)
class BaselineSpec:
    """Description of a baseline or ablation target.

    Attributes:
        name: Human-readable baseline name.
        status: Implementation/result maturity.
        modalities: Sensor modalities used by the baseline.
        purpose: Scientific role in the comparison.
        limitations: Known limitations that must be disclosed when reporting.
    """

    name: str
    status: BaselineStatus
    modalities: tuple[str, ...]
    purpose: str
    limitations: str


BASELINES: tuple[BaselineSpec, ...] = (
    BaselineSpec(
        name="Visual-only odometry",
        status=BaselineStatus.PROTOTYPE,
        modalities=("camera",),
        purpose="Measures how much adaptive fusion improves over camera-only tracking under visual degradation.",
        limitations="Requires a complete visual frontend/backend before real benchmark reporting.",
    ),
    BaselineSpec(
        name="IMU-only dead reckoning",
        status=BaselineStatus.PROTOTYPE,
        modalities=("imu",),
        purpose="Exposes drift when exteroceptive updates are unavailable.",
        limitations="Useful as a failure-mode baseline, not as a competitive SLAM method.",
    ),
    BaselineSpec(
        name="LiDAR-only odometry scaffold",
        status=BaselineStatus.PLANNED,
        modalities=("lidar",),
        purpose="Separates geometric LiDAR constraints from visual and inertial information.",
        limitations="No complete LiDAR odometry implementation or benchmark results committed yet.",
    ),
    BaselineSpec(
        name="Fixed-weight multi-modal fusion",
        status=BaselineStatus.PROTOTYPE,
        modalities=("camera", "imu", "lidar", "rgbd"),
        purpose="Primary ablation for testing whether adaptive reliability weighting helps under degradation.",
        limitations="Needs identical backend and dataset association to adaptive fusion for fair comparison.",
    ),
    BaselineSpec(
        name="Adaptive uncertainty-aware fusion",
        status=BaselineStatus.IMPLEMENTED,
        modalities=("camera", "imu", "lidar", "rgbd"),
        purpose="Transparent reliability-to-covariance and pseudo-precision baseline.",
        limitations="Reliability scores are heuristic diagnostics until calibrated against held-out sequences.",
    ),
    BaselineSpec(
        name="Oracle sensor reliability",
        status=BaselineStatus.PLANNED,
        modalities=("camera", "imu", "lidar", "rgbd"),
        purpose="Upper-bound ablation using known synthetic degradation masks.",
        limitations="Only valid in synthetic or labeled degradation experiments; not deployable online.",
    ),
)


def list_baselines(status: BaselineStatus | None = None) -> tuple[BaselineSpec, ...]:
    """Return registered baselines, optionally filtered by status."""

    if status is None:
        return BASELINES
    return tuple(spec for spec in BASELINES if spec.status == status)


def baseline_status_table() -> list[dict[str, str]]:
    """Return a README/documentation-friendly baseline table."""

    return [
        {
            "name": spec.name,
            "status": spec.status.value,
            "modalities": ", ".join(spec.modalities),
            "purpose": spec.purpose,
            "limitations": spec.limitations,
        }
        for spec in BASELINES
    ]
