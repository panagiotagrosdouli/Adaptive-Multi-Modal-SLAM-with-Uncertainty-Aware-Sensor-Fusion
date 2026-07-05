# Research Proposal

## Title

Adaptive Multi-Modal SLAM with Uncertainty-Aware Sensor Fusion for Robust Autonomous Navigation

## Abstract

Visual SLAM and visual-inertial odometry are central components of autonomous robotics, yet their reliability can deteriorate under perceptually challenging conditions such as low illumination, motion blur, dynamic objects, texture scarcity, and rapid camera motion. This project investigates an adaptive multi-modal SLAM framework that estimates the reliability of different sensing modalities online and dynamically adjusts their influence during state estimation. The initial focus is on RGB and IMU fusion, with optional extension to event-camera sensing. The long-term direction is Self-Healing SLAM: a system capable of predicting tracking degradation, diagnosing failure causes, and activating recovery strategies before catastrophic localization failure.

## Problem Statement

Most SLAM pipelines assume that sensor models and fusion weights remain valid across a wide range of operating conditions. In practice, the reliability of each modality changes over time. RGB cameras are affected by lighting, blur, and texture scarcity. IMU integration drifts over time and can be corrupted by bias or aggressive motion. Event cameras are robust to high dynamic range and fast motion, but introduce different noise and representation challenges.

A robust autonomous system should not treat these modalities as static sources of information. It should estimate their reliability online and adapt the estimation pipeline accordingly.

## Hypothesis

A SLAM system that explicitly estimates modality-specific uncertainty and adapts fusion weights online will be more robust than a fixed-fusion baseline under controlled perceptual degradation.

## Research Objectives

1. Build a reproducible SLAM robustness benchmark using public visual-inertial datasets.
2. Introduce controlled perceptual degradation such as blur, low light, image noise, texture reduction, and sensor dropout.
3. Develop an uncertainty estimator for visual and inertial reliability.
4. Use this estimator to dynamically adapt sensor fusion during pose estimation.
5. Evaluate whether adaptive fusion reduces trajectory error and tracking failures.
6. Extend the framework toward failure prediction and Self-Healing SLAM.

## Methodology

### Baseline System

The project will begin with an existing visual or visual-inertial SLAM system such as ORB-SLAM3, VINS-Fusion, or OpenVINS. The baseline will be evaluated without adaptive fusion to establish reference performance.

### Degradation Benchmark

A degradation module will generate controlled variants of dataset sequences. Examples include:

- Gaussian and motion blur,
- brightness reduction,
- contrast reduction,
- image noise,
- feature sparsification,
- frame dropout,
- IMU noise injection.

This creates a controlled evaluation environment for studying robustness.

### Uncertainty Estimation

The uncertainty estimator may combine analytical and learned signals, including:

- feature count,
- feature spatial distribution,
- reprojection residuals,
- optical flow consistency,
- keyframe tracking score,
- IMU preintegration residuals,
- innovation magnitude,
- image quality indicators.

The estimator should produce a modality reliability score or uncertainty estimate at each timestep.

### Adaptive Fusion

The adaptive fusion layer will use the estimated uncertainty to modify the contribution of visual, inertial, and optional event-camera measurements. Initial strategies may include:

- heuristic weighting,
- covariance inflation,
- residual gating,
- learned fusion policies,
- failure-aware keyframe insertion.

### Evaluation

The system will be evaluated against fixed-fusion baselines using:

- Absolute Trajectory Error,
- Relative Pose Error,
- number of tracking failures,
- time to recovery,
- robustness under increasing degradation,
- uncertainty calibration.

## Expected Contribution

The project aims to contribute a modular research framework for uncertainty-aware adaptive SLAM, with a clear experimental protocol and a path toward Self-Healing SLAM.

## Extension: Self-Healing SLAM

Once adaptive fusion is implemented, the next research direction is to add a failure prediction and recovery layer. This layer should answer three questions:

1. Is the SLAM system likely to fail soon?
2. What is the probable cause of degradation?
3. Which recovery action should be triggered?

Possible recovery actions include relocalization, sensor reweighting, keyframe policy adjustment, active viewpoint selection, or switching to a more robust representation.

## Research Impact

A successful system would be relevant to UAV navigation, autonomous inspection, search-and-rescue robotics, and field robotics, where perception conditions are unpredictable and localization failure can compromise mission safety.
