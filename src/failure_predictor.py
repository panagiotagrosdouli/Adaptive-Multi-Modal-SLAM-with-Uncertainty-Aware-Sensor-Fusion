from dataclasses import dataclass

@dataclass
class FailureIndicators:
    visual_reliability: float
    inertial_reliability: float
    reprojection_error: float
    tracked_features: int

class FailurePredictor:
    def predict(self, indicators: FailureIndicators) -> float:
        score = 0.0
        score += max(0.0,0.5-indicators.visual_reliability)
        score += max(0.0,0.5-indicators.inertial_reliability)
        score += min(indicators.reprojection_error/10.0,1.0)
        score += max(0.0,(100-indicators.tracked_features)/100.0)
        return min(score/4.0,1.0)
