# Project Roadmap

## Stage 0: Repository Foundation

Goal: Create a clear research-facing repository structure.

Deliverables:

- README with research motivation.
- Research proposal.
- Roadmap.
- Initial module skeleton.
- Reproducible experiment philosophy.

## Stage 1: Baseline SLAM Evaluation

Goal: Establish baseline performance before introducing adaptive fusion.

Tasks:

- Select initial baseline: ORB-SLAM3, VINS-Fusion, or OpenVINS.
- Prepare EuRoC MAV and TUM-VI dataset loaders.
- Define evaluation metrics: ATE, RPE, tracking failures, runtime.
- Run baseline under clean conditions.
- Store results in a standardized format.

Expected output:

- Baseline report.
- Clean trajectory plots.
- First comparison table.

## Stage 2: Perceptual Degradation Benchmark

Goal: Create controlled robustness tests.

Degradation types:

- motion blur,
- low illumination,
- contrast reduction,
- Gaussian noise,
- frame dropout,
- texture sparsification,
- IMU noise injection.

Expected output:

- Dataset degradation scripts.
- Benchmark protocol.
- Robustness curves across degradation intensity.

## Stage 3: Uncertainty Estimation

Goal: Estimate the reliability of each sensing modality online.

Candidate signals:

- number of tracked features,
- spatial distribution of features,
- reprojection error,
- optical flow consistency,
- keyframe age,
- IMU residuals,
- image sharpness,
- image brightness,
- innovation residuals.

Expected output:

- Visual reliability score.
- Inertial reliability score.
- Optional event-camera reliability score.
- Calibration against actual tracking quality.

## Stage 4: Adaptive Sensor Fusion

Goal: Adapt measurement weighting based on estimated uncertainty.

Fusion strategies:

- heuristic weighting,
- covariance inflation,
- residual gating,
- adaptive keyframe insertion,
- learned fusion policy.

Expected output:

- Adaptive fusion module.
- Quantitative comparison against fixed-fusion baseline.
- Failure-rate reduction analysis.

## Stage 5: Failure Prediction

Goal: Predict SLAM degradation before failure occurs.

Candidate prediction targets:

- tracking loss within the next N frames,
- large pose drift within a short horizon,
- relocalization requirement,
- map inconsistency.

Expected output:

- Failure predictor.
- Early warning score.
- Prediction precision-recall evaluation.

## Stage 6: Self-Healing SLAM

Goal: Trigger recovery actions before catastrophic failure.

Recovery policies:

- increase inertial weighting,
- reject unreliable visual residuals,
- change keyframe insertion policy,
- activate relocalization,
- switch feature extraction mode,
- request active viewpoint change,
- use event-camera stream when available.

Expected output:

- Closed-loop recovery system.
- Self-healing experiment results.
- Research report suitable for PhD applications.

## Final Target

A modular research framework demonstrating that SLAM systems can become more robust when they explicitly reason about uncertainty, failure risk, and recovery actions.
