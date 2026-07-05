from dataclasses import dataclass

@dataclass
class SystemState:
    tracking_ok: bool=True
    failure_probability: float=0.0
    visual_reliability: float=1.0
    inertial_reliability: float=1.0
    active_mode: str='normal'

    def update_mode(self):
        if self.failure_probability>0.7:
            self.active_mode='recovery'
        elif self.failure_probability>0.3:
            self.active_mode='adaptive'
        else:
            self.active_mode='normal'
