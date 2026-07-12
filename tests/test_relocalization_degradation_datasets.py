from pathlib import Path

import numpy as np

from slam_fusion.datasets.public_adapters import EurocAdapter, KittiOdometryAdapter, TumRgbdAdapter
from slam_fusion.relocalization.relocalizer import KeyframeRecord, Relocalizer
from slam_fusion.simulation.degradation import DegradationEngine


def test_relocalizer_requires_geometric_verification():
    points = np.array([[i, i % 2, 0.1 * i] for i in range(8)], dtype=float)
    pose = np.eye(4)
    relocalizer = Relocalizer(min_inliers=6, max_rmse=1e-6)
    relocalizer.add(KeyframeRecord("kf0", np.array([1.0, 0.0, 1.0]), points, pose))
    result = relocalizer.relocalize(np.array([1.0, 0.0, 1.0]), points.copy())
    assert result.success
    assert result.keyframe_id == "kf0"
    bad = relocalizer.relocalize(np.array([1.0, 0.0, 1.0]), points**2)
    assert not bad.success


def test_degradation_is_deterministic():
    image = np.arange(64, dtype=np.uint8).reshape(8, 8)
    points = np.arange(60, dtype=float).reshape(20, 3)
    first = DegradationEngine(seed=4)
    second = DegradationEngine(seed=4)
    assert np.array_equal(first.camera_blur(image, 0.5), second.camera_blur(image, 0.5))
    assert np.array_equal(first.sparse_lidar(points, 0.4), second.sparse_lidar(points, 0.4))


def test_public_dataset_fixture_adapters(tmp_path: Path):
    euroc = tmp_path / "euroc" / "mav0"
    (euroc / "cam0" / "data").mkdir(parents=True)
    (euroc / "imu0").mkdir(parents=True)
    (euroc / "cam0" / "data.csv").write_text("1000000000,000.png\n", encoding="utf-8")
    (euroc / "imu0" / "data.csv").write_text("1000000001,1,2,3,4,5,6\n", encoding="utf-8")
    records = list(EurocAdapter(tmp_path / "euroc").records())
    assert {record.modality for record in records} == {"camera", "imu"}

    tum = tmp_path / "tum"
    tum.mkdir()
    (tum / "associations.txt").write_text("1.0 rgb/1.png 1.01 depth/1.png\n", encoding="utf-8")
    assert len(list(TumRgbdAdapter(tum).records())) == 2

    kitti = tmp_path / "kitti" / "sequences" / "00"
    (kitti / "image_0").mkdir(parents=True)
    (kitti / "times.txt").write_text("0.0\n0.1\n", encoding="utf-8")
    assert len(list(KittiOdometryAdapter(tmp_path / "kitti", "00").records())) == 2
