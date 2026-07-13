# Phase 2 Repository Audit

Status date: 2026-07-13

This audit is based on repository content inspected through the GitHub API. The execution environment could not resolve `github.com` for a local clone, so local installation, linting, pytest, experiment execution, ROS2 replay, dataset execution, GIF generation, and MP4 generation remain unverified in this checkpoint.

## Existing capabilities verified from repository content

| Capability | Status | Evidence | Limitation / next action |
|---|---|---|---|
| Sensor abstractions | Implemented (previous phase) | README repository capability table | Inspect implementation and tests locally when execution is available. |
| Adaptive modality weighting | Implemented (previous phase) | README mathematical definition and capability table | Do not recreate; verify regression only. |
| Covariance inflation | Implemented (previous phase) | README mathematical definition | Do not recreate; verify regression only. |
| Mahalanobis gating, NIS, NEES | Implemented (previous phase) | README capability and evaluation sections | Verify code and avoid NEES when valid covariance truth is unavailable. |
| ATE/RPE and synthetic degradation | Implemented (previous phase) | README executable evidence path | Preserve and reuse for Phase 2 comparisons. |
| EKF/factor graph | Research prototype / scaffold | README limitations | Extend only after interface-level audit. |
| Dataset execution | Pending Dataset Execution | README dataset status | Validate loaders with fixtures, then run real sequences. |
| ROS2 | Pending ROS2 Validation | README limitations | No execution claim permitted. |

## Phase 2 changes in this branch

| Capability | Status | Evidence | Limitation / next action |
|---|---|---|---|
| Online temporal calibration | Research Prototype | `slam_fusion/calibration/temporal.py`; `tests/test_phase2_core.py` | Correlation-based scalar offset only; integrate residual sources and execute tests. |
| Explicit fault schedule | Implemented core model | `slam_fusion/faults/model.py`; `tests/test_phase2_core.py` | Injection transforms for each sensor type remain pending. |
| Multiple-hypothesis isolation | Research Prototype | `slam_fusion/faults/isolation.py`; `tests/test_phase2_core.py` | Evidence is normalized heuristic score, not calibrated probability. |

## Critical pending work

1. Execute baseline install, lint, formatting, tests, and existing experiments.
2. Inspect all source modules and generated outputs rather than relying on README claims.
3. Add bounded extrinsic refinement with observability and rollback.
4. Add reliability calibration, conformal coverage, shift detection, robust fusion, predictive risk, map health, active sensing, adaptive compute, and closed-loop state machine.
5. Integrate Phase 2 decisions into existing EKF/factor-graph pathways without replacing working Phase 1 functionality.
6. Run multiple-seed baselines and ablations and generate artifacts only from actual outputs.
7. Validate dataset and ROS2 paths where dependencies are available.

No performance, real-time, dataset, ROS2, or safety claim is made by this checkpoint.
