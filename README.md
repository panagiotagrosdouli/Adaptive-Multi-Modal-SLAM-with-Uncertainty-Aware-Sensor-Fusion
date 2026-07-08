# Adaptive Multi-Modal SLAM with Uncertainty-Aware Sensor Fusion

A research-oriented robotics project investigating how autonomous systems can adaptively fuse visual, inertial, and event-based sensing under challenging conditions such as motion blur, low illumination, texture scarcity, and rapid camera motion.

The long-term objective is to evolve this system into **Self-Healing SLAM**: a SLAM pipeline that can anticipate tracking degradation, diagnose the likely cause, and adapt its sensing or estimation strategy before catastrophic failure.

## PhD-Level Research Positioning

This repository supports a broader research direction in **robust robotic perception under uncertainty**. It is positioned as the SLAM/sensor-fusion counterpart of [`SHIELD-VIO`](https://github.com/panagiotagrosdouli/SHIELD-VIO): while SHIELD-VIO focuses on degradation monitoring and recovery for visual-inertial odometry, this repository focuses on adaptive multi-modal SLAM and uncertainty-aware sensor fusion.

The intended research contribution is not simply another SLAM implementation. The goal is to study whether an autonomous system can estimate the reliability of each sensing modality online and use that estimate to adapt its state-estimation pipeline before severe degradation occurs.

## Core Research Question

> Can a visual-inertial SLAM system estimate sensor reliability online and dynamically adapt its fusion strategy to improve robustness under perceptual degradation?

## Motivation

Classical visual SLAM and visual-inertial odometry systems often degrade sharply when their visual assumptions are violated. Examples include:

- motion blur during aggressive UAV maneuvers,
- poor illumination,
- low-texture environments,
- dynamic objects,
- sensor dropout,
- strong viewpoint changes.

Instead of treating all sensor measurements as equally reliable, this project explores **uncertainty-aware adaptive fusion**, where the system estimates the reliability of each sensing modality and adjusts its contribution to state estimation in real time.

## Current Capabilities

The repository currently includes:

- a reproducible YAML-based experiment runner,
- uncertainty estimation and adaptive fusion modules,
- failure prediction and recovery-policy skeletons,
- EuRoC image, IMU, and ground-truth trajectory parsing,
- trajectory matching and ATE/RPE evaluation,
- plotting utilities for experiment logs,
- an ORB-SLAM3 EuRoC backend wrapper,
- CI tests for core research modules.

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dummy end-to-end adaptive SLAM pipeline:

```bash
python run_experiment.py --config configs/example_experiment.yaml
```

Generate plots from a saved experiment JSON:

```bash
python generate_plots.py results/euroc_degraded_adaptive_fusion_baseline.json
```

Run tests:

```bash
pytest -q
```

## ORB-SLAM3 EuRoC Baseline

This repository does not vendor ORB-SLAM3. Build ORB-SLAM3 separately, download EuRoC MAV, then edit:

```bash
configs/orbslam3_euroc.yaml
```

Run a real ORB-SLAM3 baseline:

```bash
python run_orbslam3_experiment.py --config configs/orbslam3_euroc.yaml
```

If a EuRoC ground-truth CSV is configured, the script computes:

- Absolute Trajectory Error,
- Relative Pose Error,
- number of matched poses.

See `docs/orbslam3_euroc_setup.md` for setup details.

## Initial System Concept

The first version of the system uses:

- RGB camera input,
- IMU measurements,
- optional event-camera input or event-camera simulation,
- a baseline SLAM/VIO backend,
- an uncertainty estimator,
- an adaptive fusion module.

The system should learn or infer when visual tracking is becoming unreliable and compensate by increasing reliance on inertial or event-based information.

## Planned Baselines

Potential baselines include:

- ORB-SLAM3,
- VINS-Fusion,
- OpenVINS,
- DSO or LDSO,
- visual-inertial pipelines evaluated on standard datasets.

## Target Datasets

Initial evaluation will focus on public robotics datasets such as:

- EuRoC MAV,
- TUM-VI,
- ADVIO,
- Event Camera Dataset,
- synthetic degraded sequences generated from existing visual-inertial datasets.

## Evaluation Metrics

The project evaluates robustness and accuracy using:

- Absolute Trajectory Error (ATE),
- Relative Pose Error (RPE),
- tracking failure rate,
- relocalization frequency,
- degradation recovery time,
- uncertainty calibration,
- computational cost.

## Research Contributions

The intended contributions are:

1. A modular SLAM pipeline with uncertainty-aware sensor reliability estimation.
2. A dynamic fusion policy that adapts to degraded visual conditions.
3. A benchmark protocol for testing SLAM robustness under controlled perceptual degradation.
4. A path toward Self-Healing SLAM through failure prediction and recovery strategies.

## Roadmap

### Phase 1: Baseline and Benchmarking

- Set up baseline SLAM/VIO system.
- Run experiments on EuRoC and TUM-VI.
- Create degradation scripts for blur, low light, noise, and texture loss.
- Establish reproducible evaluation metrics.

### Phase 2: Uncertainty Estimation

- Estimate visual tracking confidence from feature quality, reprojection error, optical flow consistency, and IMU residuals.
- Add learned or probabilistic uncertainty estimation.
- Calibrate uncertainty against actual tracking performance.

### Phase 3: Adaptive Fusion

- Dynamically adjust sensor weighting based on uncertainty.
- Compare fixed fusion, heuristic adaptive fusion, and learned adaptive fusion.
- Evaluate robustness under degraded conditions.

### Phase 4: Toward Self-Healing SLAM

- Predict tracking failure before it occurs.
- Diagnose probable failure causes.
- Trigger recovery policies such as relocalization, sensor reweighting, keyframe strategy changes, or active viewpoint adjustment.

## Relationship to Broader Robotics Portfolio

This repository complements:

- [`SHIELD-VIO`](https://github.com/panagiotagrosdouli/SHIELD-VIO), which focuses on degradation diagnosis and recovery for VIO.
- [`DynNav`](https://github.com/panagiotagrosdouli/DynNav-Dynamic-Navigation-Rerouting-in-Unknown-Environments), which studies risk-aware navigation under map uncertainty.
- [`Uncertainty-Aware Navigation`](https://github.com/panagiotagrosdouli/uncertainty-aware-navigation), which provides a focused planning benchmark around uncertainty-weighted navigation.

Together, these repositories form a PhD-oriented research arc from **perception reliability** to **localization robustness** to **risk-aware planning**.

## Repository Structure

```text
.
├── configs/               # Experiment configurations
├── docs/                  # Research notes and setup guides
├── paper/                 # Paper scaffold
├── scripts/               # Dataset preparation and degradation tools
├── src/                   # Core research modules
├── tests/                 # Unit and smoke tests
├── run_experiment.py      # Dummy end-to-end adaptive SLAM experiment
├── run_orbslam3_experiment.py
└── README.md
```

## Status

This repository is transitioning from research scaffold to real benchmark framework. The current priority is robust ORB-SLAM3 EuRoC baseline evaluation before adding adaptive/self-healing behavior to real SLAM outputs.

## Long-Term Vision

The final ambition is a robust autonomous perception system that does not passively fail when visual conditions degrade, but actively detects, anticipates, and mitigates failure.

This is the foundation for **Self-Healing SLAM**.