from slam_fusion.faults.consistency_graph import (
    ConsistencyState,
    CrossModalConsistencyGraph,
)
from slam_fusion.prediction.estimator_failure import (
    FailureFeatures,
    PredictiveFailureEstimator,
)


def test_consistency_graph_tracks_edges_and_attribution():
    graph = CrossModalConsistencyGraph()
    edge = graph.update("camera", "imu", residual=0.5, uncertainty=0.1)
    assert edge.state is ConsistencyState.INCONSISTENT
    graph.update("camera", "lidar", residual=0.45, uncertainty=0.1)
    graph.update("imu", "lidar", residual=0.02, uncertainty=0.1)
    suspect, evidence = graph.suspect_sensor()
    assert suspect == "camera"
    assert evidence["camera"] > evidence["imu"]


def test_predictive_failure_risk_increases_for_degradation():
    estimator = PredictiveFailureEstimator()
    nominal = FailureFeatures(0.95, 0.0, 0.8, 0.05, 0.95, 0.9, 1.0, 0.0, 0.05)
    degraded = FailureFeatures(0.2, -0.8, 3.0, 0.9, 0.15, 0.2, 0.1, 0.9, 0.95)
    nominal_prediction = estimator.predict(nominal, horizon_s=2.0)
    degraded_prediction = estimator.predict(degraded, horizon_s=5.0)
    assert degraded_prediction.risk > nominal_prediction.risk
    assert degraded_prediction.level in {"WARNING", "CRITICAL"}
    assert degraded_prediction.recommended_action != "continue"


def test_predictive_failure_validates_horizon():
    estimator = PredictiveFailureEstimator()
    features = FailureFeatures(1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0)
    try:
        estimator.predict(features, horizon_s=0.0)
    except ValueError:
        pass
    else:
        raise AssertionError("non-positive prediction horizon must fail")
