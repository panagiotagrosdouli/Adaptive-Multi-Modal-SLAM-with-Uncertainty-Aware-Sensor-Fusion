# Phase 0 Repository Audit

This document records the initial audit for transforming the repository into a serious research-software artifact for adaptive multi-modal SLAM. The purpose is not to inflate claims, but to make the gap between the current implementation and a full PhD-grade SLAM system explicit, actionable, and testable.

## Research question

**How can a SLAM system adaptively fuse heterogeneous sensors while explicitly reasoning about uncertainty, reliability, degradation, and failure modes?**

The repository should therefore prioritize:

- uncertainty-aware multi-modal fusion,
- interpretable reliability estimation,
- estimator consistency diagnostics,
- reproducible degradation experiments,
- honest benchmark reporting,
- safe-navigation relevance without unsupported safety claims.

## Current evidence from the repository

The repository already contains important foundations:

- A research-oriented landing README that states the core question, motivation, mathematical sketch, architecture, quick-start commands, dataset targets, implemented/prototype/planned table, limitations, roadmap, citation, and acknowledgements.
- A Python packaging scaffold through `pyproject.toml` with runtime and development dependencies.
- An adaptive fusion module with reliability-weighted pseudo-precision, covariance scaling, dropout weighting, and Mahalanobis gating.
- A mathematical formulation document that defines the state, measurement model, innovation, NEES/NIS, adaptive weighting, and risk-score limitations.
- Explicit language that real benchmark results are pending and should not be claimed until committed with metrics and manifests.

## Scientific audit

### Strengths

1. **Research identity is clear.** The current framing is centered on adaptive multi-modal SLAM with explicit uncertainty and reliability reasoning.
2. **Claims are mostly disciplined.** The README separates implemented components, prototypes, and planned features instead of claiming a complete LVI-SLAM system.
3. **The fusion baseline is interpretable.** Reliability modifies pseudo-precision and measurement covariance in a way that is easy to inspect and test.
4. **Numerical consistency is being taken seriously.** Cholesky-based Mahalanobis distance and explicit covariance validation are preferable to silently using pseudo-inverses for estimator diagnostics.
5. **Limitations are visible.** The repository correctly avoids benchmark claims for EuRoC, KITTI, TUM RGB-D, TUM-VI, and nuScenes until reproducible results exist.

### Gaps blocking paper-grade claims

1. **No complete estimator path yet.** A full tightly coupled visual-inertial, LiDAR-inertial, or RGB-D backend is not implemented end-to-end.
2. **Real dataset support remains incomplete.** Dataset loaders, synchronization, calibration assumptions, sequence manifests, and benchmark scripts must be completed before reporting public numbers.
3. **Reliability is diagnostic, not calibrated.** Current reliability and risk scores should not be interpreted as probabilities until calibrated on held-out failure labels.
4. **Factor-graph support is scaffold-level.** Residual definitions, Jacobians, robust losses, marginalization, and optimization backends must be implemented before factor-graph claims are made.
5. **ROS2 support is prototype/planned.** Runtime nodes, launch files, topic documentation, bag playback instructions, and rviz configs are needed before ROS2 functionality is described as implemented.
6. **Website should mirror evidence.** The project website must not advertise results that are not generated from committed code.

## Engineering audit

### Strengths

- Package-oriented layout is already present.
- Type hints and docstrings are used in core fusion code.
- Development dependencies include Black, Ruff, pytest, mypy, and pre-commit.
- The README points to deterministic synthetic demo generation.

### Gaps

- CI must run linting, tests, and at least one smoke experiment on every pull request.
- Every experiment should write a machine-readable manifest containing git commit, config path, random seed, dataset identifier, metrics, and generated artifacts.
- Results should be treated as generated artifacts, not manually edited claims.
- Figure generation should be deterministic and scriptable.
- Benchmark tables should use `Pending` until metric JSON files are committed.

## Recommended transformation phases

### Phase 1: Claim discipline and reproducibility infrastructure

- Add a claims-and-evidence ledger.
- Add experiment manifest schema.
- Add benchmark status matrix.
- Add contribution guidance that requires evidence for claims.
- Ensure README links to audit and claim ledger.

### Phase 2: Synthetic degradation benchmark suite

- Implement deterministic synthetic trajectories.
- Add visual degradation, IMU noise, LiDAR dropout, and depth noise schedules.
- Save metrics and manifests under `results/`.
- Generate trajectory, ATE/RPE, NEES/NIS, reliability, weight, and risk plots from code.

### Phase 3: Minimal complete EKF baseline

- Implement prediction, update, covariance propagation, Mahalanobis gating, and NIS logging.
- Compare visual-only, IMU-only, fixed fusion, adaptive fusion, and oracle reliability on synthetic sequences.
- Report only synthetic numbers until real dataset loaders are validated.

### Phase 4: Dataset loader validation

- Add EuRoC MAV loader with timestamp synchronization and calibration documentation.
- Add TUM RGB-D association and depth scaling documentation.
- Add KITTI odometry scaffold with pose-format validation.
- Add dataset manifests without redistributing dataset content.

### Phase 5: Research website and paper assets

- Ensure the website consumes generated figures and demo GIF only.
- Add paper-style abstract, contributions, limitations, and future work.
- Keep all benchmark tables tied to committed result files.

## Definition of done for a research claim

A claim can move from `Planned` or `Prototype` to `Implemented` only if at least one of the following exists:

1. Tested source code implementing the feature.
2. Reproducible experiment config and output manifest.
3. Documentation explicitly describing the implemented assumptions and limitations.
4. Citation to external theory or baseline implementation, where applicable.

Claims without this evidence must remain `Prototype`, `Scaffold`, `Planned`, or `Pending`.

## Immediate next actions

1. Add a claims-and-evidence ledger.
2. Add a benchmark status matrix.
3. Add an experiment manifest schema.
4. Update README to link this audit.
5. Open a draft pull request for review before merging.
