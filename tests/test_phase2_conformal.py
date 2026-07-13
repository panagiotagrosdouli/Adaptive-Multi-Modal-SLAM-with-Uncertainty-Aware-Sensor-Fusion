import numpy as np
import pytest

from slam_fusion.reliability.conformal import RollingConformalRegressor, SplitConformalRegressor


def test_split_conformal_reports_empirical_coverage_and_width():
    rng = np.random.default_rng(12)
    calibration_predictions = np.linspace(-1.0, 1.0, 120)
    calibration_targets = calibration_predictions + rng.normal(0.0, 0.08, size=120)
    test_predictions = np.linspace(-0.8, 0.8, 80)
    test_targets = test_predictions + rng.normal(0.0, 0.08, size=80)

    conformal = SplitConformalRegressor(coverage=0.9).fit(
        calibration_predictions, calibration_targets
    )
    result = conformal.evaluate(test_predictions, test_targets)

    assert conformal.calibration_size_ == 120
    assert conformal.quantile_ is not None
    assert result.sample_count == 80
    assert 0.0 <= result.empirical_coverage <= 1.0
    assert result.empirical_coverage >= 0.8
    assert result.mean_width > 0.0


def test_split_conformal_requires_independent_calibration_data_shape():
    conformal = SplitConformalRegressor()
    with pytest.raises(ValueError):
        conformal.fit([0.0, 1.0], [0.0])
    with pytest.raises(RuntimeError):
        conformal.predict_interval([0.0])


def test_rolling_conformal_becomes_ready_and_bounds_prediction():
    rolling = RollingConformalRegressor(coverage=0.9, window_size=16)
    for index in range(10):
        rolling.update(float(index), float(index) + 0.1)

    assert rolling.ready
    lower, upper = rolling.interval(5.0)
    assert lower <= 5.0 <= upper
    assert upper - lower == pytest.approx(0.2)
