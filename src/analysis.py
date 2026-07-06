from dataclasses import dataclass

from src.result_aggregation import ExperimentSummary


@dataclass
class ImprovementSummary:
    baseline_name: str
    candidate_name: str
    ate_improvement_percent: float
    rpe_improvement_percent: float


def percentage_improvement(baseline_value: float, candidate_value: float) -> float:
    if baseline_value == 0:
        return 0.0
    return 100.0 * (baseline_value - candidate_value) / baseline_value


def compare_experiments(
    baseline: ExperimentSummary,
    candidate: ExperimentSummary,
) -> ImprovementSummary:
    return ImprovementSummary(
        baseline_name=baseline.experiment_name,
        candidate_name=candidate.experiment_name,
        ate_improvement_percent=percentage_improvement(
            baseline.absolute_trajectory_error,
            candidate.absolute_trajectory_error,
        ),
        rpe_improvement_percent=percentage_improvement(
            baseline.relative_pose_error,
            candidate.relative_pose_error,
        ),
    )
