# Adaptive Multi-Modal SLAM with Uncertainty-Aware Sensor Fusion

A research-oriented robotics project investigating how autonomous systems can adaptively fuse visual, inertial, and event-based sensing under challenging conditions such as motion blur, low illumination, texture scarcity, and rapid camera motion.

The long-term objective is to evolve this system into **Self-Healing SLAM**: a SLAM pipeline that can anticipate tracking degradation, diagnose the likely cause, and adapt its sensing or estimation strategy before catastrophic failure.

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

## Initial System Concept

The first version of the system will use:

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

The project will evaluate robustness and accuracy using:

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

## Repository Structure

```text
.
├── docs/                  # Research notes, design documents, and experiment plans
├── scripts/               # Dataset preparation and degradation tools
├── src/                   # Core research modules
├── configs/               # Experiment configurations
├── results/               # Evaluation summaries and plots
└── README.md
```

## Status

This repository is at the initial research-planning stage.

The immediate next step is to implement the benchmark and degradation pipeline before adding the adaptive uncertainty-aware fusion module.

## Long-Term Vision

The final ambition is a robust autonomous perception system that does not passively fail when visual conditions degrade, but actively detects, anticipates, and mitigates failure.

This is the foundation for **Self-Healing SLAM**.
