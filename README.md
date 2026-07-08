# Adaptive Multi-Modal SLAM with Uncertainty-Aware Sensor Fusion

[![Research Software CI](https://github.com/panagiotagrosdouli/Adaptive-Multi-Modal-SLAM-with-Uncertainty-Aware-Sensor-Fusion/actions/workflows/ci.yml/badge.svg)](https://github.com/panagiotagrosdouli/Adaptive-Multi-Modal-SLAM-with-Uncertainty-Aware-Sensor-Fusion/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/benchmark%20claims-pending-orange)

**Scientific summary:** a research framework for studying how SLAM systems can adaptively fuse camera, IMU, LiDAR, and RGB-D measurements while explicitly reasoning about uncertainty, reliability, degradation, and failure risk.

> Central question: **How can a SLAM system adaptively fuse heterogeneous sensors while explicitly reasoning about uncertainty, reliability, degradation, and failure modes?**

This repository is deliberately claim-disciplined. It contains implemented utilities, prototype scaffolds, documentation, and reproducible synthetic diagnostics. It does **not** claim state-of-the-art performance or real benchmark numbers until metrics, configs, manifests, and reproduction commands are committed.

---

## Research motivation

Visual-inertial, LiDAR-visual-inertial, and RGB-D SLAM pipelines often use fixed measurement covariances even when sensing conditions change. In field robotics, cameras lose texture or suffer motion blur, LiDAR returns become sparse, depth sensors saturate, and IMUs drift. Fixed fusion can over-trust degraded measurements and produce overconfident failures. This project makes sensor reliability an explicit state-estimation signal.

---

## Problem formulation

The robot state is modeled as

```math
x_k = \{T_{WB,k}, v_{W,k}, b^g_k, b^a_k\},
```

where `T_WB` is pose, `v_W` is velocity, and `b^g`, `b^a` are IMU biases. For modality `i`,

```math
z^i_k = h_i(x_k, \theta_i) + n^i_k, \quad n^i_k \sim \mathcal{N}(0, \Sigma^i_k).
```

Reliability `r_i(k) in [0, 1]` adapts the information contribution:

```math
p_i(k) = \frac{\max(r_i(k), \epsilon)^\gamma}{\sigma_i^2}, \quad
w_i(k) = \frac{p_i(k)}{\sum_j p_j(k)}, \quad
\tilde{\Sigma}_i(k)=\Sigma_i / \max(r_i(k),\epsilon)^\gamma.
```

Innovation consistency is checked with

```math
NIS_i = \nu_i^T S_i^{-1}\nu_i,
```

and estimator consistency can be evaluated with NEES when ground truth exists. See `docs/MATHEMATICAL_FORMULATION.md`.

---

## System architecture

```text
Camera / IMU / LiDAR / RGB-D
        │
        ▼
Timestamp synchronization + calibration scaffold
        │
        ▼
Frontend quality: features, inliers, blur, brightness, dropout, depth/LiDAR validity
        │
        ▼
Reliability estimation r_i(k)
        │
        ▼
Adaptive fusion: covariance scaling, pseudo-precision weights, Mahalanobis gating
        │
        ▼
Backend: EKF scaffold / factor graph scaffold / pose graph scaffold
        │
        ▼
Mapping, uncertainty diagnostics, ATE/RPE/NEES/NIS evaluation
```

## Sensor fusion pipeline

1. Validate timestamped sensor packets.
2. Estimate visual/inertial/LiDAR/depth reliability from interpretable diagnostics.
3. Convert reliability into covariance inflation or normalized pseudo-precision.
4. Reject inconsistent residuals with Mahalanobis gates.
5. Track uncertainty using covariance trace, log determinant, entropy, NEES, and NIS.
6. Save configs, metric JSON, plots, and manifests for reproducibility.

## Uncertainty estimation diagram

```text
Residual ν_i + Innovation covariance S_i ──► NIS / Mahalanobis gate
State error e + Covariance P ──────────────► NEES, if ground truth exists
State covariance P ────────────────────────► trace(P), logdet(P), entropy proxy
Reliability r_i + NIS + trace(P) ──────────► failure/risk diagnostic score
```

---

## Demo

The demo is generated from deterministic synthetic data, not manually edited and not a benchmark:

```bash
python scripts/make_demo_gif.py --gif assets/demo.gif --mp4 results/videos/demo.mp4 --seed 7
```

Expected output:

```text
assets/demo.gif
results/videos/demo.mp4
```

The animation shows estimated/ground-truth trajectory, active modalities, confidence values, adaptive fusion weights, uncertainty ellipse, tracking status proxy, and risk score.

---

## Installation

```bash
git clone https://github.com/panagiotagrosdouli/Adaptive-Multi-Modal-SLAM-with-Uncertainty-Aware-Sensor-Fusion.git
cd Adaptive-Multi-Modal-SLAM-with-Uncertainty-Aware-Sensor-Fusion
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Minimal install:

```bash
python -m pip install -r requirements.txt
```

---

## Quick start

Synthetic adaptive-fusion smoke experiment:

```bash
python run_experiment.py --config configs/example_experiment.yaml
```

Run all deterministic research phases:

```bash
python scripts/run_all_phases.py
```

Run tests:

```bash
pytest
```

Generate demo GIF:

```bash
python scripts/make_demo_gif.py
```

---

## Dataset examples

### Synthetic simulation

```bash
python run_experiment.py --config configs/example_experiment.yaml
```

### EuRoC MAV

```bash
python run_orbslam3_experiment.py --config configs/orbslam3_euroc.yaml
```

Real EuRoC results are **Pending** unless metric files and manifests are committed.

### KITTI Odometry

KITTI support is a planned/scaffolded benchmark target. Do not report KITTI numbers until a loader, config, and metric JSON are committed.

### TUM RGB-D

TUM RGB-D support is a planned/scaffolded RGB-D target. Depth association and RGB-D backend integration are not complete.

### ROS2 launch

ROS2 support is currently **Prototype**. Future launch files should document topics such as `/camera/image`, `/imu`, `/points`, `/depth`, `/tf`, and bag playback instructions.

---

## Implemented / Prototype / Planned

| Component | Status | Evidence |
| --- | --- | --- |
| Sensor timestamp abstraction | Implemented | `slam_fusion/sensors/base.py`, tests |
| Adaptive pseudo-precision weights | Implemented | `slam_fusion/fusion/adaptive.py`, tests |
| Adaptive covariance scaling | Implemented | `slam_fusion/fusion/adaptive.py` |
| Mahalanobis gating | Implemented | `slam_fusion/fusion/adaptive.py`, tests |
| NEES / NIS | Implemented | `slam_fusion/uncertainty/metrics.py`, tests |
| ATE / RPE | Implemented | `slam_fusion/evaluation/trajectory.py`, tests |
| Demo GIF generation | Implemented | `scripts/make_demo_gif.py` |
| Visual quality reliability heuristic | Implemented baseline | `slam_fusion/frontend/features.py` |
| EKF backend | Prototype | `slam_fusion/backend/scaffolds.py` |
| Factor graph backend | Prototype | `slam_fusion/backend/scaffolds.py` |
| Pose graph / loop closure | Planned scaffold | no benchmark claim |
| LiDAR-only odometry | Planned | benchmark row pending |
| RGB-D SLAM | Planned | benchmark row pending |
| ROS2 runtime nodes | Prototype/planned | no production claim |
| Website | Scaffold | `website/` |

---

## Evaluation metrics

- Absolute Trajectory Error, ATE.
- Relative Pose Error, RPE.
- Final drift.
- Tracking failure rate.
- NEES and NIS consistency.
- Sensor reliability calibration.
- Runtime FPS.
- CPU/GPU usage scaffold.
- Loop-closure success rate, when loop closure is implemented.

See `docs/EVALUATION_PROTOCOL.md` and `benchmarks/README.md`.

---

## Limitations

- The current estimator backend is not a complete production-grade tightly coupled LVI-SLAM system.
- Real benchmark results on EuRoC, KITTI, TUM RGB-D, TUM-VI, and nuScenes remain pending.
- Risk scores are diagnostics, not calibrated probabilities.
- Synthetic demos verify behavior but do not demonstrate field robustness.
- No dataset is redistributed; users must download datasets from official sources.

---

## Roadmap

1. Complete deterministic synthetic degradation suite.
2. Add EuRoC and TUM RGB-D loaders with manifest generation.
3. Integrate a real backend such as ORB-SLAM3/OpenVINS/VINS-Fusion or a GTSAM factor graph.
4. Compare visual-only, IMU-only, fixed fusion, adaptive fusion, and oracle reliability baselines.
5. Calibrate reliability against NIS/NEES, ATE/RPE, tracking failure, and runtime.
6. Add ROS2 nodes, launch files, rviz config, and bag playback documentation.
7. Publish a clean project website with figures generated from code.

---

## Future MSc/PhD extensions

- Reliability calibration under controlled visual degradation.
- Learning uncertainty-aware fusion weights with conservative safety constraints.
- Multi-modal loop closure under camera/LiDAR dropout.
- Failure prediction before tracking loss.
- Safe navigation policies that respond to SLAM uncertainty.
- Uncertainty maps for exploration and active perception.

---

## Citation

```bibtex
@software{grosdouli_adaptive_multimodal_slam_2026,
  title = {Adaptive Multi-Modal SLAM with Uncertainty-Aware Sensor Fusion},
  author = {Grosdouli, Panagiota},
  year = {2026},
  url = {https://github.com/panagiotagrosdouli/Adaptive-Multi-Modal-SLAM-with-Uncertainty-Aware-Sensor-Fusion}
}
```

## License

MIT License. See `LICENSE`.

## Acknowledgements

This repository is inspired by open research in probabilistic robotics, visual-inertial odometry, LiDAR-visual-inertial SLAM, RGB-D SLAM, robust estimation, and safe autonomous navigation. Any external backend or dataset must be cited according to its own license and citation policy.
