# Research Software Audit

This audit records concrete gaps between the current repository and research-grade SLAM software expected to accompany an ICRA, IROS, RSS, or CVPR-style paper. It is deliberately conservative: implemented components are separated from prototypes and future work.

## Scope of this audit

The first pass focuses on numerical consistency in uncertainty-aware fusion. In probabilistic SLAM, measurement residuals are meaningful only if the associated covariance is symmetric positive definite or carefully regularized from a positive-semidefinite estimate. Silent pseudo-inverse use can hide rank deficiency and make an estimator appear more consistent than it is.

## Finding 1: Mahalanobis gates used pseudo-inverses

### Scientific motivation

For a residual vector \(r\) with innovation covariance \(S\), the normalized innovation squared is

```math
\mathrm{NIS} = r^\top S^{-1} r.
```

Under a correctly specified Gaussian model, NIS follows a chi-square distribution with degrees of freedom equal to the residual dimension. This interpretation requires \(S\) to be positive definite. A Moore-Penrose pseudo-inverse changes the metric when \(S\) is rank deficient, suppresses uncertainty directions with zero singular values, and can therefore accept innovations that should trigger estimator diagnostics.

### Engineering motivation

The updated implementation validates finite inputs, symmetrizes covariance matrices, and evaluates Mahalanobis distances by solving the Cholesky-whitened system. If the covariance is numerically singular but semidefinite, bounded diagonal jitter is applied. Strongly invalid matrices fail loudly.

### Expected impact

- More reliable NEES/NIS diagnostics.
- Better failure visibility during benchmark runs.
- Reduced risk of overconfident acceptance of degenerate residuals.
- Clearer separation between numerical regularization and algorithmic covariance modeling.

### Possible drawbacks

- Cholesky factorization costs \(O(d^3)\), whereas pseudo-inverse also costs cubic time but may be slower for small dense matrices depending on LAPACK implementation.
- Strict covariance validation may expose previously hidden test or runtime bugs.
- Jitter magnitude must be reported for full reproducibility in future benchmark artifacts.

## Finding 2: Diagnostic risk is not calibrated probability

The bounded risk score combines covariance trace, minimum reliability, and innovation inconsistency. It is useful as a monitoring signal, but it should not be reported as a calibrated failure probability unless validated against held-out tracking-failure events using calibration curves, expected calibration error, and sequence-level failure labels.

## Finding 3: Backend status remains prototype

The README correctly states that EKF, factor graph, pose graph, LiDAR odometry, RGB-D SLAM, and ROS2 runtime support are not complete production systems. The next research-grade step is to implement one complete estimator path end-to-end before expanding the public claims.

## Recommended next implementation order

1. Add a complete synthetic benchmark harness with fixed random seeds, degradation schedules, and JSON manifests.
2. Implement a minimal but mathematically complete EKF path with explicit prediction, update, covariance propagation, and NIS logging.
3. Add pose-trajectory alignment and ATE/RPE tables generated from saved result files.
4. Add factor-graph interfaces only after defining factor residuals, Jacobians, robust losses, and marginalization policy.
5. Add dataset loaders only with documented association, calibration, and timestamp assumptions.

## Literature anchors

- Thrun, Burgard, and Fox, *Probabilistic Robotics*, 2005.
- Barfoot, *State Estimation for Robotics*, 2017.
- Forster et al., IMU preintegration on manifold, RSS 2015.
- Leutenegger et al., OKVIS, IJRR 2015.
- Qin et al., VINS-Mono, T-RO 2018.
- Shan et al., LIO-SAM, IROS 2020.
- Campos et al., ORB-SLAM3, T-RO 2021.

## Current patch summary

- `slam_fusion/fusion/adaptive.py`: strict configuration validation, finite input validation, symmetric covariance handling, Cholesky Mahalanobis distance, bounded jitter, and explicit failure modes.
- `slam_fusion/uncertainty/metrics.py`: Cholesky-based NEES/NIS, SPD validation, entropy/log-determinant diagnostics, and stricter risk-score validation.
- `tests/test_research_grade_numerics.py`: regression tests for Cholesky-equivalent distances, singular covariance regularization, indefinite covariance rejection, dimension mismatch detection, finite entropy/logdet, and risk-score validation.
