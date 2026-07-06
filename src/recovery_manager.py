from dataclasses import dataclass

from src.health_monitor import SlamHealthStatus
from src.recovery_policy import RecoveryAction


@dataclass
class RecoveryDecision:
    action: str
    priority: int
    reason: str


class RecoveryManager:
    def decide(self, health: SlamHealthStatus, policy_action: RecoveryAction) -> RecoveryDecision:
        if health.level == 'critical':
            return RecoveryDecision(
                action='emergency_relocalization',
                priority=3,
                reason=f'{health.reason}; overriding policy action {policy_action.name}',
            )

        if health.level == 'warning':
            return RecoveryDecision(
                action=policy_action.name,
                priority=2,
                reason=f'{health.reason}; applying policy action',
            )

        return RecoveryDecision(
            action='continue_normal_operation',
            priority=1,
            reason='SLAM health is stable',
        )
