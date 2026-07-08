# Baselines and Ablations

This document defines the comparison protocol for the repository. It is a protocol and registry, not a report of completed benchmark results.

## Principle

Adaptive sensor fusion is scientifically meaningful only when compared against simpler alternatives under identical trajectories, timestamps, measurement models, backend assumptions, and evaluation metrics.

## Baseline set

| Baseline | Status | Scientific role | Reporting rule |
| --- | --- | --- | --- |
| Visual-only odometry | Prototype | Tests camera dependence under visual degradation. | Report only after visual frontend/backend metrics exist. |
| IMU-only dead reckoning | Prototype | Quantifies inertial drift and exteroceptive recovery. | Treat as failure-mode baseline, not competitive SLAM. |
| LiDAR-only odometry | Planned | Separates geometric constraints from camera/IMU constraints. | Pending until implementation and metrics are committed. |
| Fixed-weight fusion | Prototype | Main ablation against adaptive reliability weighting. | Must share the same backend as adaptive fusion. |
| Adaptive uncertainty-aware fusion | Implemented baseline | Tests reliability-to-covariance and pseudo-precision weighting. | Reliability must be described as heuristic unless calibrated. |
| Oracle reliability | Planned | Synthetic upper bound with known degradation masks. | Never use for real online deployment claims. |

## Required metrics

- Absolute Trajectory Error (ATE RMSE)
- Relative Pose Error (RPE RMSE)
- Final drift
- Tracking failure rate
- NEES when ground truth state error and covariance are available
- NIS for innovation consistency
- Reliability calibration curves
- Runtime FPS and resource usage when measured

## Required artifacts before reporting a number

Every reported metric must be accompanied by:

1. Experiment YAML.
2. Dataset manifest or synthetic-generation seed.
3. Commit hash.
4. `results/<experiment>/metrics.json`.
5. Figure-generation command, when a figure is shown.
6. A statement of whether the backend is Implemented, Prototype, or Planned.

## Non-claims

The repository must not claim state-of-the-art performance, real-world safety, calibrated failure probability, or complete SLAM deployment unless the relevant implementation, validation, and citations are present.
