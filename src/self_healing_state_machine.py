from dataclasses import dataclass


@dataclass
class StateTransition:
    previous_state: str
    next_state: str
    reason: str


class SelfHealingStateMachine:
    def __init__(self) -> None:
        self.state = 'normal'

    def update(self, health_level: str, recovery_action: str) -> StateTransition:
        previous = self.state

        if health_level == 'critical':
            self.state = 'recovery'
        elif health_level == 'warning':
            self.state = 'adaptive'
        elif recovery_action in {'trigger_relocalization', 'insert_keyframe_and_reduce_visual_residuals'}:
            self.state = 'recovery'
        else:
            self.state = 'normal'

        return StateTransition(
            previous_state=previous,
            next_state=self.state,
            reason=f'health={health_level}, action={recovery_action}',
        )
