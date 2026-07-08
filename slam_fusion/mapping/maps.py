"""Mapping structures for SLAM outputs and uncertainty diagnostics."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass(slots=True)
class SparseLandmarkMap:
    """Sparse landmark map with optional per-landmark covariance."""

    points: np.ndarray = field(default_factory=lambda: np.empty((0, 3), dtype=float))
    covariances: list[np.ndarray] = field(default_factory=list)

    def add_landmark(self, point: np.ndarray, covariance: np.ndarray | None = None) -> None:
        """Add a 3D landmark."""

        point = np.asarray(point, dtype=float).reshape(1, 3)
        self.points = np.vstack([self.points, point])
        if covariance is not None:
            if covariance.shape != (3, 3):
                raise ValueError("landmark covariance must be 3x3")
            self.covariances.append(covariance)


@dataclass(slots=True)
class TrajectoryMap:
    """Trajectory map containing estimated poses or positions."""

    positions: np.ndarray
    uncertainty_trace: np.ndarray | None = None


@dataclass(slots=True)
class OccupancyMapScaffold:
    """Prototype occupancy-map metadata; no occupancy integration claim yet."""

    resolution_m: float = 0.1
    status: str = "prototype"


@dataclass(slots=True)
class SemanticMapPlaceholder:
    """Explicit placeholder for future semantic mapping."""

    status: str = "planned"
