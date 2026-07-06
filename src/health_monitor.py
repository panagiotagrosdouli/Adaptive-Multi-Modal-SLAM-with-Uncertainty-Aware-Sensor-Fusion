from dataclasses import dataclass


@dataclass
class SlamHealthSignals:
    tracking_ok: bool
    tracked_features: int
    mean_reprojection_error: float
    visual_reliability: float
    inertial_reliability: float
    failure_probability: float


@dataclass
class SlamHealthStatus:
    score: float
    level: str
    reason: str


class SlamHealthMonitor:
    def __init__(self, warning_threshold: float = 0.55, critical_threshold: float = 0.3) -> None:
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold

    def evaluate(self, signals: SlamHealthSignals) -> SlamHealthStatus:
        feature_score = min(signals.tracked_features / 200.0, 1.0)
        reprojection_score = max(0.0, 1.0 - signals.mean_reprojection_error / 8.0)
        reliability_score = 0.5 * signals.visual_reliability + 0.5 * signals.inertial_reliability
        failure_score = 1.0 - signals.failure_probability
        tracking_score = 1.0 if signals.tracking_ok else 0.0

        score = (
            0.20 * feature_score
            + 0.20 * reprojection_score
            + 0.25 * reliability_score
            + 0.25 * failure_score
            + 0.10 * tracking_score
        )

        if score < self.critical_threshold:
            return SlamHealthStatus(score=score, level='critical', reason='tracking health is critically degraded')
        if score < self.warning_threshold:
            return SlamHealthStatus(score=score, level='warning', reason='tracking health is degraded')
        return SlamHealthStatus(score=score, level='healthy', reason='tracking health is acceptable')
