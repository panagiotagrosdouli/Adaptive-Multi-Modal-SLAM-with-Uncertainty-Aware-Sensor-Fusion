import numpy as np

from src.adaptive_fusion import AdaptiveFusionPolicy
from src.failure_predictor import FailureIndicators, FailurePredictor
from src.logger import ExperimentLogger
from src.recovery_policy import RecoveryPolicy
from src.slam_backend import DummySlamBackend, SlamObservation
from src.system_state import SystemState
from src.uncertainty_estimator import (
    InertialQualitySignals,
    UncertaintyEstimator,
    VisualQualitySignals,
)


def main():
    backend = DummySlamBackend()
    uncertainty = UncertaintyEstimator()
    fusion = AdaptiveFusionPolicy()
    predictor = FailurePredictor()
    recovery = RecoveryPolicy()
    logger = ExperimentLogger()

    backend.initialize()
    state = SystemState()
    experiment_log = []

    for step in range(20):
        observation = SlamObservation(timestamp=float(step))
        slam_result = backend.process(observation)

        visual_signals = VisualQualitySignals(
            tracked_features=slam_result.num_tracked_features,
            mean_reprojection_error=slam_result.mean_reprojection_error,
            image_brightness=0.8,
            image_sharpness=0.8,
        )
        inertial_signals = InertialQualitySignals(
            acceleration_norm=9.81,
            gyro_norm=0.05,
        )

        reliability = uncertainty.estimate(visual_signals, inertial_signals)
        weights = fusion.compute_weights(reliability)

        indicators = FailureIndicators(
            visual_reliability=reliability.visual,
            inertial_reliability=reliability.inertial,
            reprojection_error=slam_result.mean_reprojection_error,
            tracked_features=slam_result.num_tracked_features,
        )
        failure_probability = predictor.predict(indicators)

        state.visual_reliability = reliability.visual
        state.inertial_reliability = reliability.inertial
        state.failure_probability = failure_probability
        state.tracking_ok = slam_result.tracking_ok
        state.update_mode()

        action = recovery.select_action(
            failure_probability=failure_probability,
            visual_reliability=reliability.visual,
            inertial_reliability=reliability.inertial,
        )

        experiment_log.append(
            {
                'step': step,
                'timestamp': slam_result.timestamp,
                'position': slam_result.position.tolist(),
                'mode': state.active_mode,
                'visual_reliability': reliability.visual,
                'inertial_reliability': reliability.inertial,
                'visual_weight': weights.visual,
                'inertial_weight': weights.inertial,
                'failure_probability': failure_probability,
                'recovery_action': action.name,
                'recovery_reason': action.reason,
            }
        )

    logger.save_metrics('dummy_adaptive_slam_run', {'steps': experiment_log})
    backend.shutdown()
    print('End-to-end adaptive SLAM experiment completed.')


if __name__ == '__main__':
    main()
