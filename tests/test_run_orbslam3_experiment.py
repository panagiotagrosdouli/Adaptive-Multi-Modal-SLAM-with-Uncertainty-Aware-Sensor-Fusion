from pathlib import Path

from run_orbslam3_experiment import build_orbslam3_config


def test_build_orbslam3_config_from_raw_dictionary():
    raw = {
        'orbslam3': {
            'executable': '/tmp/orbslam3_euroc',
            'vocabulary': '/tmp/ORBvoc.txt',
            'settings': '/tmp/EuRoC.yaml',
            'sequence_path': '/tmp/MH_01_easy',
            'output_trajectory': 'results/trajectory.csv',
            'timeout_seconds': 123,
        }
    }

    config = build_orbslam3_config(raw)

    assert config.executable == Path('/tmp/orbslam3_euroc')
    assert config.vocabulary == Path('/tmp/ORBvoc.txt')
    assert config.settings == Path('/tmp/EuRoC.yaml')
    assert config.sequence_path == Path('/tmp/MH_01_easy')
    assert config.output_trajectory == Path('results/trajectory.csv')
    assert config.timeout_seconds == 123
