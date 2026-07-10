from pathlib import Path

import numpy as np

from scripts.generate_figures import generate_figures
from scripts.make_demo_gif import make_demo_gif
from slam_fusion.simulation.synthetic_slam import SyntheticSLAMConfig, adaptive_weights, run_synthetic_slam


def test_adaptive_weights_normalize_and_dropouts() -> None:
    weights = adaptive_weights(
        {"camera": 1.0, "imu": 0.5, "lidar": 0.0, "rgbd": 0.25},
        {"camera": 0.1, "imu": 0.2, "lidar": 1e6, "rgbd": 0.3},
    )
    assert np.isclose(sum(weights.values()), 1.0)
    assert weights["lidar"] < 1e-10
    assert weights["camera"] > weights["rgbd"]


def test_synthetic_demo_outputs_metrics_and_media(tmp_path: Path) -> None:
    result_dir = tmp_path / "results"
    cfg = SyntheticSLAMConfig(seed=3, steps=32, landmark_count=12, output_dir=result_dir)
    result = run_synthetic_slam(cfg)
    assert result["summary"]["label"] == "Synthetic Demo"
    for name in [
        "ground_truth.csv",
        "estimated_trajectory.csv",
        "landmarks.csv",
        "sensor_measurements.json",
        "sensor_confidence.csv",
        "fusion_weights.csv",
        "uncertainty.csv",
        "degradation_events.csv",
        "mapping_summary.json",
        "metrics/summary.json",
        "metrics/metrics.csv",
        "metrics/uncertainty.csv",
    ]:
        assert (result_dir / name).exists()
    figures = generate_figures(result_dir, tmp_path / "assets" / "figures")
    assert any(path.name == "trajectory_map.png" for path in figures)
    media = make_demo_gif(result_dir, tmp_path / "assets")
    assert Path(media["gif"]).exists()
    assert Path(media["mp4"]).exists()
