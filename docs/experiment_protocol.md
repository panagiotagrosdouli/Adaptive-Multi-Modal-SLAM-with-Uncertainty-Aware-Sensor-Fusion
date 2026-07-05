# Experiment Protocol

## Objective

Evaluate whether uncertainty-aware adaptive fusion improves SLAM robustness under controlled perceptual degradation.

## Baselines

The initial benchmark should compare:

1. Fixed-fusion visual-inertial SLAM baseline.
2. Heuristic uncertainty-aware adaptive fusion.
3. Failure-aware adaptive fusion with recovery policy.

Potential backend systems:

- ORB-SLAM3,
- OpenVINS,
- VINS-Fusion.

## Datasets

Primary datasets:

- EuRoC MAV,
- TUM-VI.

Optional datasets:

- ADVIO,
- Event Camera Dataset,
- synthetic degraded variants of public sequences.

## Degradation Conditions

Each dataset sequence should be evaluated under:

- clean input,
- low illumination,
- motion blur,
- Gaussian image noise,
- frame dropout,
- reduced texture,
- combined degradation.

Each degradation should be applied at multiple intensity levels.

## Metrics

Core metrics:

- Absolute Trajectory Error,
- Relative Pose Error,
- tracking failure count,
- recovery latency,
- runtime,
- uncertainty calibration.

## Ablation Studies

Recommended ablations:

1. Without adaptive fusion.
2. With visual uncertainty only.
3. With visual and inertial uncertainty.
4. With failure prediction but no recovery.
5. With full self-healing recovery policy.

## Reporting

Every experiment should save:

- configuration file,
- trajectory output,
- evaluation metrics,
- plots,
- logs,
- git commit hash.

This is required for reproducibility and for later paper preparation.
