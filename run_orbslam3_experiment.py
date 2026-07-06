import argparse
import json
from pathlib import Path

from src.backends.orbslam3_backend import OrbSlam3Backend, OrbSlam3Config
from src.config import load_config
from src.evaluation import evaluate_trajectory
from src.trajectory import load_euroc_ground_truth


def parse_args():
    parser = argparse.ArgumentParser(description='Run ORB-SLAM3 on a EuRoC sequence.')
    parser.add_argument(
        '--config',
        default='configs/orbslam3_euroc.yaml',
        help='Path to ORB-SLAM3 EuRoC experiment configuration.',
    )
    return parser.parse_args()


def build_orbslam3_config(raw_config) -> OrbSlam3Config:
    orbslam_cfg = raw_config.get('orbslam3', {})
    return OrbSlam3Config(
        executable=Path(orbslam_cfg['executable']),
        vocabulary=Path(orbslam_cfg['vocabulary']),
        settings=Path(orbslam_cfg['settings']),
        sequence_path=Path(orbslam_cfg['sequence_path']),
        output_trajectory=Path(orbslam_cfg['output_trajectory']),
        timeout_seconds=orbslam_cfg.get('timeout_seconds'),
    )


def save_evaluation_report(config_name, evaluation, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        'experiment_name': config_name,
        'matched_poses': evaluation.matched_poses,
        'absolute_trajectory_error': evaluation.ate,
        'relative_pose_error': evaluation.rpe,
    }
    output_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


def main():
    args = parse_args()
    config = load_config(args.config)
    backend_config = build_orbslam3_config(config.raw)
    backend = OrbSlam3Backend(backend_config)

    print(f'Running experiment: {config.name}')
    print('ORB-SLAM3 command:')
    print(' '.join(backend.build_command()))

    backend.run_sequence()
    estimated_trajectory = backend.load_estimated_trajectory()

    ground_truth_path = config.raw.get('dataset', {}).get('ground_truth')
    if ground_truth_path:
        ground_truth = load_euroc_ground_truth(ground_truth_path)
        evaluation = evaluate_trajectory(ground_truth, estimated_trajectory)
        report_path = Path('results') / f'{config.name}_evaluation.json'
        report = save_evaluation_report(config.name, evaluation, report_path)
        print(f"Matched poses: {report['matched_poses']}")
        print(f"ATE: {report['absolute_trajectory_error']}")
        print(f"RPE: {report['relative_pose_error']}")
        print(f'Evaluation report: {report_path}')

    print(f'Estimated trajectory poses: {len(estimated_trajectory)}')
    print(f'Output trajectory: {backend_config.output_trajectory}')


if __name__ == '__main__':
    main()
