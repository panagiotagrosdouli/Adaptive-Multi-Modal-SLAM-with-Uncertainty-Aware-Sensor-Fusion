# Synthetic Demo

This repository includes a working deterministic **Synthetic Demo** for adaptive multi-modal SLAM. The demo simulates a lightweight 2D robot trajectory, landmarks, camera-like observations, IMU-like observations, LiDAR-like observations, RGB-D-like observations, sensor degradation, dropout, adaptive confidence, fusion weights, uncertainty diagnostics, figures, GIF, and MP4.

These results are not real-world benchmark results. They are generated from code for reproducibility, smoke testing, and research prototyping.

## Run

```bash
python scripts/run_all.py
```

## Outputs

- `results/ground_truth.csv`
- `results/estimated_trajectory.csv`
- `results/landmarks.csv`
- `results/sensor_measurements.json`
- `results/sensor_confidence.csv`
- `results/fusion_weights.csv`
- `results/uncertainty.csv`
- `results/degradation_events.csv`
- `results/mapping_summary.json`
- `results/metrics/summary.json`
- `results/metrics/metrics.csv`
- `results/metrics/uncertainty.csv`
- `results/figures/*.png`
- `assets/figures/*.png`
- `assets/gifs/demo.gif`
- `assets/videos/demo.mp4`
- `results/videos/adaptive_multimodal_slam_demo.gif`
- `results/videos/adaptive_multimodal_slam_demo.mp4`

## Scientific role

The demo directly tests the central research question: how can a SLAM system adaptively fuse heterogeneous sensors while explicitly reasoning about uncertainty, reliability, degradation, and failure modes?

Implemented parts are intentionally modest but executable. Factor-graph optimization, real image front-ends, ROS2 runtime nodes, and real-dataset benchmarks remain prototype or planned components until validated with real data.
