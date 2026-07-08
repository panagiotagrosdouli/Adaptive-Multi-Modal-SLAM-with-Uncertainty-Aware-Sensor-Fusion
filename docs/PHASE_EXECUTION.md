# Phase Execution Protocol

This document defines the repository phases that must run before a change can be considered research-grade.

The command is:

```bash
python scripts/run_all_phases.py
```

## Phase 1: Static quality checks

Runs:

```bash
ruff check src tests scripts
black --check src tests scripts
```

Purpose:

- catch syntax errors, unused imports, and maintainability issues;
- enforce consistent formatting;
- prevent unreviewable research code from entering the main branch.

## Phase 2: Unit tests

Runs:

```bash
python -m pytest -q
```

Purpose:

- validate trajectory metrics;
- validate uncertainty utilities;
- validate adaptive sensor weighting;
- prevent numerical regressions.

## Phase 3: Smoke experiment

Runs:

```bash
python run_experiment.py --config configs/example_experiment.yaml
```

Purpose:

- execute the adaptive SLAM supervision loop;
- produce a deterministic experiment JSON;
- ensure the logger, config loader, backend interface, uncertainty estimator, fusion policy, failure predictor, recovery policy, plotting, and manifest code work together.

## Phase 4: Artifact validation

Validates:

- `results/euroc_degraded_adaptive_fusion_baseline.json`;
- `results/plots/euroc_degraded_adaptive_fusion_baseline/failure_probability.png`;
- `results/plots/euroc_degraded_adaptive_fusion_baseline/reliability.png`;
- `results/plots/euroc_degraded_adaptive_fusion_baseline/fusion_weights.png`;
- `results/manifests/euroc_degraded_adaptive_fusion_baseline_manifest.json`.

Purpose:

- make sure every reported smoke experiment leaves reproducible outputs;
- prevent silent plotting or manifest failures.

## Phase 5: Research media generation

Runs:

```bash
python scripts/generate_research_media.py \
  results/euroc_degraded_adaptive_fusion_baseline.json \
  --output-dir results/videos
```

Validates:

- `results/videos/euroc_degraded_adaptive_fusion_baseline_trajectory.svg`.

Purpose:

- generate documentation-ready vector figures from actual experiment logs;
- avoid manually drawn or invented visualizations.

## Phase 6: Benchmark metric schema and table generation

Runs:

```bash
python scripts/validate_benchmark_metrics.py benchmark/example_metric.json
python scripts/generate_benchmark_table.py benchmark/example_metric.json --output-dir results/tables
```

Validates:

- `results/tables/benchmark_table.md`;
- `results/tables/benchmark_table.tex`.

Purpose:

- enforce a metric schema before benchmark values are reported;
- generate Markdown and LaTeX tables from metric JSON files;
- prevent hand-edited benchmark tables that cannot be reproduced.

The committed `benchmark/example_metric.json` is a schema example only. It must not be reported as a real dataset result.

## Phase 7: External dataset benchmark gate

Checks whether an external dataset directory exists.

If datasets are unavailable, the phase is recorded as skipped with a reason. It must not fabricate EuRoC, KITTI, TUM, Replica, ScanNet, or event-camera benchmark numbers.

A real dataset benchmark can be promoted to required only when:

1. the dataset download instructions are documented;
2. the configuration path is committed;
3. the exact command is committed;
4. the metric output is committed or uploaded as a CI artifact;
5. the README cites only those reproducible results.

## Scientific rule

A skipped external dataset phase is acceptable. A fake benchmark is not.
