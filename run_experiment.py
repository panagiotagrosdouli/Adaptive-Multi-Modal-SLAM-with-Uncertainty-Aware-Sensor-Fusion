import argparse
from pathlib import Path

from src.adaptive_fusion import AdaptiveFusionPolicy
from src.config import load_config
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
from src.visualization import generate_all_plots


def parse_args():
    parser = argparse.ArgumentParser(description='Run adaptive multi-modal SLAM experiment.')
    parser.add_argument(
        '--config',
        default='configs/example_experiment.yaml',
        help='Path to YAML experiment configuration.',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config(args.config)

    uncertainty_cfg = config.raw.get('uncertainty_estimation', {})
    fusion_cfg = config.raw.get('adaptive_fusion', {})

    backend = DummySlamBackend()
    uncertainty = UncertaintyEstimator(
        min_features=uncertainty_cfg.get('min_features', 50),
        target_features=uncertainty_cfg.get('target_features', 200),
        max_reprojection_error=uncertainty_cfg.get('max_reprojection_error', 5.0),
    )
    fusion = AdaptiveFusionPolicy(
        minimum_weight=fusion_cfg.get('minimum_weight', 0.05),
    )
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
                'experiment_name': config.name,
                'dataset': config.dataset_name,
                'baseline': config.baseline_system,
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

    logger.save_metrics(config.name, {'steps': experiment_log})
    result_path = Path('results') / f'{config.name}.json'
    generate_all_plots(result_path, Path('results') / 'plots' / config.name)
    backend.shutdown()
    print(f'Experiment completed: {config.name}')
    print(f'Results written to: {result_path}')


if __name__ == '__main__':
    main()
