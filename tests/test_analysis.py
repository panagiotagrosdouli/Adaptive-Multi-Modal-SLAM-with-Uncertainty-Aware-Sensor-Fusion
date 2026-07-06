from src.analysis import compare_experiments, percentage_improvement
from src.result_aggregation import ExperimentSummary


def test_percentage_improvement_basic():
    value = percentage_improvement(10.0, 8.0)
    assert value == 20.0


def test_percentage_improvement_zero_baseline():
    value = percentage_improvement(0.0, 8.0)
    assert value == 0.0


def test_compare_experiments_basic():
    baseline = ExperimentSummary('baseline', 10, 10.0, 5.0)
    candidate = ExperimentSummary('candidate', 10, 8.0, 2.5)
    result = compare_experiments(baseline, candidate)
    assert result.ate_improvement_percent == 20.0
    assert result.rpe_improvement_percent == 50.0
