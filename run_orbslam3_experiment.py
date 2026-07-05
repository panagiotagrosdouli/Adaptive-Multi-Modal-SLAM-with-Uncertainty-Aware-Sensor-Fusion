import argparse
from pathlib import Path

from src.backends.orbslam3_backend import OrbSlam3Backend, OrbSlam3Config
from src.config import load_config


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


def main():
    args = parse_args()
    config = load_config(args.config)
    backend_config = build_orbslam3_config(config.raw)
    backend = OrbSlam3Backend(backend_config)

    print(f'Running experiment: {config.name}')
    print('ORB-SLAM3 command:')
    print(' '.join(backend.build_command()))

    backend.run_sequence()
    trajectory = backend.load_estimated_trajectory()

    print(f'Estimated trajectory poses: {len(trajectory)}')
    print(f'Output trajectory: {backend_config.output_trajectory}')


if __name__ == '__main__':
    main()
