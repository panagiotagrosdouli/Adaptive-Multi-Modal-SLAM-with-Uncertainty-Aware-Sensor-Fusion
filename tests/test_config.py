from pathlib import Path

from src.config import load_config


def test_load_example_experiment_config():
    config = load_config(Path('configs/example_experiment.yaml'))
    assert config.name == 'euroc_degraded_adaptive_fusion_baseline'
    assert config.dataset_name == 'EuRoC MAV'
    assert config.baseline_system == 'ORB-SLAM3'
    assert config.adaptive_fusion_enabled is True
