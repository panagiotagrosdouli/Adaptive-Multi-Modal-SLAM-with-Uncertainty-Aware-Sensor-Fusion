# Research Overview

## Research question

How can a SLAM system adaptively fuse heterogeneous sensors while explicitly reasoning about uncertainty, reliability, degradation, and failure modes?

## Motivation

Robotic perception pipelines are usually evaluated under nominal sensing assumptions, but field robots experience low texture, illumination shifts, motion blur, dust, rain, LiDAR sparsity, dropped packets, and IMU bias drift. A fixed fusion policy can over-trust a degraded modality and make the state estimator confidently wrong.

## Implemented

- Sensor measurement abstraction with timestamps, covariance, calibration scaffold, and bounded reliability.
- Adaptive pseudo-precision weighting.
- Covariance scaling from reliability.
- Mahalanobis innovation gating.
- NEES/NIS and uncertainty proxies.
- ATE/RPE trajectory metrics.
- Deterministic synthetic demo generation script.

## Prototype

- EKF, factor graph, loop closure, and mapping interfaces.
- ROS2 namespace and launch documentation placeholders.
- LiDAR, RGB-D, and point-cloud integration hooks.

## Planned

- Full tightly coupled visual-inertial or LiDAR-visual-inertial optimizer.
- Real benchmark execution on EuRoC, KITTI, TUM RGB-D, TUM-VI, and nuScenes.
- Calibrated failure probability and reliability calibration curves.
- Learned adaptive weighting compared against transparent baselines.

## Scientific limitations

This repository must not claim state-of-the-art performance until benchmark artifacts include sequence names, timestamps, configs, backend versions, metric files, and reproduction manifests. Synthetic demonstrations are used only to verify software behavior and communicate the method.
