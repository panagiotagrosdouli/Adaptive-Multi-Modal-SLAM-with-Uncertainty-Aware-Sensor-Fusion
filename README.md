# Adaptive Multi-Modal SLAM

Reliability-aware sensor fusion for state estimation under changing measurement quality.

This research prototype studies how camera, IMU, LiDAR, and RGB-D measurements can be weighted and filtered when sensor quality changes online. It includes modality-health diagnostics, adaptive covariance, innovation gating, consistency metrics, and deterministic synthetic degradation experiments.

## Method

The current implementation provides:

- modality-specific quality diagnostics
- reliability-aware fusion weights
- adaptive covariance inflation
- Mahalanobis gating
- NIS and NEES consistency utilities
- ATE, RPE, drift, and recovery metrics
- deterministic sensor and timing degradations

## Reproduce

```bash
git clone https://github.com/panagiotagrosdouli/Adaptive-Multi-Modal-SLAM-with-Uncertainty-Aware-Sensor-Fusion.git
cd Adaptive-Multi-Modal-SLAM-with-Uncertainty-Aware-Sensor-Fusion
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python run_experiment.py --config configs/example_experiment.yaml
python scripts/run_all_phases.py
pytest
```

## Scope

The implemented baseline is validated with deterministic synthetic experiments. EKF, factor-graph, dataset, ROS 2, and hardware integrations remain experimental or incomplete. Reliability values are engineering diagnostics rather than calibrated probabilities.

This repository does not claim production readiness, state-of-the-art SLAM performance, formal safety guarantees, or physical-robot validation.

[Greek documentation](README_GR.md)