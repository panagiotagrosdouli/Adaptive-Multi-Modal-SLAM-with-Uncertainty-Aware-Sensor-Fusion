from dataclasses import dataclass
from typing import Optional

from src.uncertainty_estimator import ModalityReliability


@dataclass
class FusionWeights:
    visual: float
    inertial: float
    event: Optional[float] = None


class AdaptiveFusionPolicy:
    def __init__(self, minimum_weight: float = 0.05) -> None:
        self.minimum_weight = minimum_weight

    def compute_weights(self, reliability: ModalityReliability) -> FusionWeights:
        visual = max(self.minimum_weight, reliability.visual)
        inertial = max(self.minimum_weight, reliability.inertial)

        if reliability.event is None:
            total = visual + inertial
            return FusionWeights(
                visual=visual / total,
                inertial=inertial / total,
                event=None,
            )

        event = max(self.minimum_weight, reliability.event)
        total = visual + inertial + event

        return FusionWeights(
            visual=visual / total,
            inertial=inertial / total,
            event=event / total,
        )
