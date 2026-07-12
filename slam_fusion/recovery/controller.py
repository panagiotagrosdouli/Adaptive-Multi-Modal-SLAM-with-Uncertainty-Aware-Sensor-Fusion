"""Recovery controller for temporary rejection and gradual modality reactivation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RecoveryState(str, Enum):
    ACTIVE = "active"
    DEGRADED = "degraded"
    COOLDOWN = "cooldown"
    PROBATION = "probation"
    RELOCALIZING = "relocalizing"
    SAFE_HALT = "safe_halt"


@dataclass(slots=True)
class RecoveryDecision:
    state: RecoveryState
    weight_scale: float
    covariance_scale: float
    action: str
    explanation: str


@dataclass(slots=True)
class _SensorState:
    state: RecoveryState = RecoveryState.ACTIVE
    bad_count: int = 0
    good_count: int = 0
    cooldown_left: int = 0
    probation_step: int = 0


class RecoveryController:
    """Finite-state recovery policy that always re-evaluates rejected sensors."""

    def __init__(
        self,
        reject_after: int = 3,
        cooldown_steps: int = 5,
        reactivate_after: int = 3,
        reliability_low: float = 0.25,
        reliability_high: float = 0.65,
        probation_steps: int = 4,
    ):
        self.reject_after = reject_after
        self.cooldown_steps = cooldown_steps
        self.reactivate_after = reactivate_after
        self.reliability_low = reliability_low
        self.reliability_high = reliability_high
        self.probation_steps = probation_steps
        self._states: dict[str, _SensorState] = {}

    def update(
        self,
        sensor: str,
        reliability: float,
        innovation_consistent: bool,
        packet_fresh: bool = True,
        alternative_modalities: int = 1,
    ) -> RecoveryDecision:
        if not 0.0 <= reliability <= 1.0:
            raise ValueError("reliability must be in [0, 1]")

        status = self._states.setdefault(sensor, _SensorState())

        healthy = (
            reliability >= self.reliability_high
            and innovation_consistent
            and packet_fresh
        )
        unhealthy = (
            reliability <= self.reliability_low
            or not innovation_consistent
            or not packet_fresh
        )

        status.good_count = status.good_count + 1 if healthy else 0
        status.bad_count = status.bad_count + 1 if unhealthy else 0

        if status.state in {RecoveryState.ACTIVE, RecoveryState.DEGRADED}:
            if status.bad_count >= self.reject_after:
                status.state = RecoveryState.COOLDOWN
                status.cooldown_left = self.cooldown_steps
            elif unhealthy:
                status.state = RecoveryState.DEGRADED
            elif healthy:
                status.state = RecoveryState.ACTIVE

        elif status.state == RecoveryState.COOLDOWN:
            status.cooldown_left -= 1

            if status.cooldown_left <= 0:
                status.state = RecoveryState.PROBATION
                status.probation_step = 0
                status.good_count = 0

        elif status.state == RecoveryState.PROBATION:
            if unhealthy:
                status.state = RecoveryState.COOLDOWN
                status.cooldown_left = self.cooldown_steps
            elif healthy:
                status.probation_step += 1

                if status.good_count >= self.reactivate_after:
                    status.state = RecoveryState.ACTIVE

        if alternative_modalities <= 0 and status.state == RecoveryState.COOLDOWN:
            status.state = RecoveryState.RELOCALIZING

        if status.state == RecoveryState.ACTIVE:
            return RecoveryDecision(
                state=status.state,
                weight_scale=1.0,
                covariance_scale=1.0,
                action="accept",
                explanation=f"{sensor} is healthy and active",
            )

        if status.state == RecoveryState.DEGRADED:
            scale = max(0.1, reliability)

            return RecoveryDecision(
                state=status.state,
                weight_scale=scale,
                covariance_scale=1.0 / scale**2,
                action="downweight",
                explanation=(
                    f"{sensor} is degraded; reliability or innovation checks failed"
                ),
            )

        if status.state == RecoveryState.COOLDOWN:
            return RecoveryDecision(
                state=status.state,
                weight_scale=0.0,
                covariance_scale=100.0,
                action="temporary_reject",
                explanation=(
                    f"{sensor} is in cooldown for "
                    f"{status.cooldown_left} more updates"
                ),
            )

        if status.state == RecoveryState.PROBATION:
            scale = min(
                0.75,
                (status.probation_step + 1) / max(self.probation_steps, 1),
            )

            return RecoveryDecision(
                state=status.state,
                weight_scale=scale,
                covariance_scale=1.0 / max(scale, 0.1) ** 2,
                action="gradual_reactivation",
                explanation=(
                    f"{sensor} passed "
                    f"{status.good_count} consecutive reactivation checks"
                ),
            )

        return RecoveryDecision(
            state=status.state,
            weight_scale=0.0,
            covariance_scale=100.0,
            action="request_relocalization",
            explanation=(
                f"{sensor} unavailable and no alternative modality remains"
            ),
        )