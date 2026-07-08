# Repository Audit

This audit records the scientific and engineering state of the repository before deeper experimental claims are made. It is intentionally conservative: missing evidence is reported as missing rather than filled with invented results.

## Scope inspected

The current repository already contains a research-oriented README, Python packaging metadata, core adaptive-fusion utilities, uncertainty metrics, trajectory metrics, synthetic/demo scaffolding, documentation stubs, and CI-facing development dependencies. The audit therefore focuses on turning the repository from a strong scaffold into a reproducible research system.

## Severity scale

- **Critical**: blocks scientific validity or reproducibility.
- **High**: blocks reliable engineering use or fair comparison.
- **Medium**: limits usability, extensibility, or presentation.
- **Low**: polish or long-term maintainability.

## Scientific audit

| Severity | Finding | Why it matters | Required action |
| --- | --- | --- | --- |
| Critical | Real benchmark results are not yet committed for EuRoC, KITTI, TUM RGB-D, TUM-VI, or nuScenes. | A SLAM paper-style repository must not claim performance without metric files, sequence manifests, configs, and reproduction commands. | Keep benchmark tables marked **Pending** until experiments exist. |
| Critical | Backend is a scaffold rather than a complete tightly coupled VIO/LVI/RGB-D SLAM estimator. | Adaptive fusion cannot be evaluated as a full SLAM system until estimator assumptions and update equations are executable. | Implement EKF/factor-graph backends incrementally and compare against baselines. |
| High | Reliability scores are heuristics, not calibrated probabilities. | Safety claims require calibration against held-out degradations and consistency statistics. | Report them as diagnostic scores; add calibration experiments. |
| High | Dataset loaders are scaffold-level. | Without loaders, real-sequence experiments are not reproducible. | Add explicit dataset preparation docs, manifests, and loader tests. |
| Medium | No systematic ablation matrix yet. | Adaptive fusion must be compared against visual-only, IMU-only, fixed-fusion, dropout, and oracle-reliability baselines. | Add baseline registry and YAML experiment suite. |

## Engineering audit

| Severity | Finding | Why it matters | Required action |
| --- | --- | --- | --- |
| High | Package APIs need stable boundaries between sensors, frontend, fusion, backend, mapping, evaluation, and visualization. | Research code becomes fragile when experiments directly depend on scripts. | Keep core logic in `slam_fusion/` and scripts thin. |
| High | Some functionality is scaffolded without smoke tests. | Future refactors may silently break reproducibility. | Add tests for baselines, dataset manifests, reliability diagnostics, and generated artifacts. |
| Medium | Runtime profiling is not yet implemented. | SLAM robustness claims need computational context. | Add CPU/GPU/FPS scaffold and document it as pending until measured. |
| Medium | ROS2 integration is not production-ready. | Users may assume deployability from the project title. | Mark ROS2 as **Prototype** and document topics/launch plans. |

## Documentation audit

| Severity | Finding | Why it matters | Required action |
| --- | --- | --- | --- |
| High | Existing documentation must keep separating Implemented, Prototype, and Planned. | Prevents overclaiming and improves reviewer trust. | Maintain status tables in README and docs. |
| Medium | Dataset pages should link only to official download/preparation instructions. | Avoids redistribution/licensing problems. | Store scripts/manifests, not datasets. |
| Medium | Mathematical formulation should map directly to code modules. | Readers need traceability from equations to implementation. | Add module references beside equations over time. |

## Reproducibility audit

| Severity | Finding | Why it matters | Required action |
| --- | --- | --- | --- |
| Critical | No real benchmark metric artifacts should be shown until generated from code. | Prevents fabricated or irreproducible numbers. | Require `results/<experiment>/metrics.json` and config snapshots. |
| High | Random seeds must be present in every synthetic config. | Robustness and uncertainty experiments are sensitive to noise realizations. | Enforce deterministic config fields. |
| Medium | Generated figures should include provenance metadata. | Publication figures must be traceable. | Add manifests for plots and videos. |

## Visual presentation audit

| Severity | Finding | Why it matters | Required action |
| --- | --- | --- | --- |
| Medium | Architecture and pipeline diagrams are text-first. | Robotics project pages benefit from visual clarity. | Generate diagrams under `assets/` from scripts. |
| Medium | Demo animation is synthetic. | It is useful for explaining the method but not evidence of real-world performance. | Label it clearly as synthetic and non-benchmark. |

## Immediate remediation plan

1. Add baseline registry and honest status metadata.
2. Add YAML experiment configs for nominal and degraded synthetic conditions.
3. Add dataset manifest validation utilities.
4. Add risk/reliability diagnostics that remain explicitly non-calibrated.
5. Add tests around scientific invariants: positive covariance, valid weights, deterministic manifests, metric sanity.
6. Preserve all real benchmark results as **Pending** until generated from committed code and data manifests.
