# Research Audit and Upgrade Plan

This audit records the engineering and scientific changes required for the repository to approach the quality expected from software accompanying an ICRA/RSS-style robotics paper.

## Current strengths

- Clear research question: online sensor reliability estimation and adaptive fusion for robust SLAM.
- Existing experiment runner and YAML-based configuration direction.
- Initial modules for uncertainty estimation, adaptive fusion, failure prediction, logging, trajectory parsing, plotting, and ORB-SLAM3 EuRoC wrapping.
- Honest README language that distinguishes scaffold, baseline wrappers, and planned extensions.

## Critical weaknesses found

### 1. Reliability scores were treated as direct fusion weights

The previous fusion policy normalized modality reliabilities directly. This is not ideal because estimator weighting should be related to measurement precision or covariance. The code has been upgraded to a pseudo-precision model:

```math
p_i = max(ε, r_i)^γ / σ_i^2,
w_i = p_i / Σ_j p_j.
```

This remains a transparent baseline, but it is scientifically closer to weighted least squares and factor-graph information weighting.

### 2. Trajectory metrics lacked alignment conventions

ATE/RPE are only interpretable when timestamp association, alignment convention, and trajectory pairing are specified. The metric implementation now includes input validation and Umeyama SE(3)/Sim(3) alignment. This is essential for fair comparison across monocular, stereo, RGB-D, and visual-inertial systems.

### 3. Failure prediction was an uncalibrated average of penalties

The failure predictor has been replaced by a monotonic logistic-risk model with explicit terms for visual reliability, inertial reliability, reprojection error, and feature depletion. It is still not a learned calibrated model, but it is interpretable and easier to validate statistically.

### 4. Uncertainty utilities were missing

The repository now includes covariance validation, Mahalanobis distance, and Gaussian differential entropy utilities. These are necessary for uncertainty visualization, failure detection, covariance ellipsoids, and innovation-consistency analysis.

## Remaining work before publication-quality release

### Algorithmic work

1. Replace dummy SLAM backend with a typed interface to ORB-SLAM3/OpenVINS outputs.
2. Add dataset adapters for EuRoC, TUM-VI, KITTI, TUM RGB-D, and event-camera data.
3. Add robust visual quality extraction: feature distribution, inlier ratio, blur, brightness, flow consistency, and residual statistics.
4. Add real factor-graph or EKF hooks where modality reliability modifies covariance/information matrices.
5. Add dynamic-object rejection through semantic masks and geometric consistency.
6. Add sliding-window marginalization diagnostics if the system integrates with an optimization backend.
7. Add loop-closure confidence monitoring and loop-outlier rejection.

### Benchmarking work

1. Define fixed dataset sequences and sensor configurations.
2. Export benchmark JSON/CSV files with ATE, RPE, FPS, CPU, GPU, RAM, tracking failure count, and loop-closure events.
3. Generate ICRA-style LaTeX tables from metric files.
4. Store only small example outputs in the repository; keep large datasets external.
5. Require a manifest for every reported experiment.

### Software engineering work

1. Add `pyproject.toml` with Black, Ruff, pytest, and coverage configuration.
2. Add pre-commit hooks.
3. Add GitHub Actions CI.
4. Add typed interfaces and stricter exception handling across all modules.
5. Split CLI entrypoints under `scripts/` and library code under `src/`.
6. Add benchmark and visualization modules with deterministic output paths.

### Documentation work

1. Rewrite README around implemented capabilities, not aspirations.
2. Add architecture diagrams.
3. Add theory documentation for each algorithm.
4. Add dataset setup guides.
5. Add benchmark tables only after experiments are run.
6. Add troubleshooting notes for ORB-SLAM3, EuRoC, and Python dependencies.

## Definition of done

The repository can be called research-grade when a clean user can:

1. install the package in a reproducible environment;
2. run a smoke experiment;
3. run at least one real dataset baseline;
4. regenerate metrics, figures, and manifests;
5. understand the mathematical role of uncertainty in the estimator;
6. reproduce every claim made in the README.

## Claim discipline

No result should be reported in the README unless it is backed by a committed configuration file, metric file, and reproduction command. This rule is non-negotiable for scientific credibility.
