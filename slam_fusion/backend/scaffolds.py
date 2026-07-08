"""Backend interfaces for EKF, factor graph, and pose graph research prototypes."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import numpy as np


class BackendStatus(str, Enum):
    """Maturity status for backend components."""

    IMPLEMENTED = "implemented"
    PROTOTYPE = "prototype"
    PLANNED = "planned"


@dataclass(slots=True)
class Factor:
    """Generic factor-graph residual block scaffold."""

    keys: tuple[str, ...]
    residual: np.ndarray
    covariance: np.ndarray
    robust_loss: str = "none"


@dataclass(slots=True)
class FactorGraphScaffold:
    """Container documenting factor graph inputs before optimizer integration."""

    factors: list[Factor] = field(default_factory=list)
    status: BackendStatus = BackendStatus.PROTOTYPE

    def add_factor(self, factor: Factor) -> None:
        """Append a factor after basic covariance validation."""

        if factor.covariance.shape[0] != factor.covariance.shape[1]:
            raise ValueError("factor covariance must be square")
        self.factors.append(factor)


@dataclass(slots=True)
class EKFScaffold:
    """EKF update scaffold with innovation gating metadata."""

    status: BackendStatus = BackendStatus.PROTOTYPE
    last_innovation: np.ndarray | None = None
    last_innovation_covariance: np.ndarray | None = None


@dataclass(slots=True)
class LoopClosureScaffold:
    """Loop-closure placeholder with explicit non-claim status."""

    status: BackendStatus = BackendStatus.PLANNED
    descriptor_type: str = "DBoW2/ScanContext placeholder"
