# Result Aggregation Workflow

After running clean, degraded, and self-healing experiments, evaluation reports can be aggregated into a single markdown table.

## Input

Each input file should be an evaluation JSON report containing:

```json
{
  "experiment_name": "orbslam3_clean_mh01",
  "matched_poses": 1200,
  "absolute_trajectory_error": 0.12,
  "relative_pose_error": 0.03
}
```

## Usage

```bash
python aggregate_results.py \
  results/orbslam3_clean_mh01_evaluation.json \
  results/orbslam3_degraded_mh01_evaluation.json \
  results/self_healing_mh01_evaluation.json \
  --output results/summary_table.md
```

## Output

The output is a markdown table suitable for README updates, reports, and early paper drafts:

```text
| Experiment | Matched Poses | ATE | RPE |
|---|---:|---:|---:|
| orbslam3_clean_mh01 | 1200 | 0.120000 | 0.030000 |
```

## Research use

This makes it possible to compare:

- clean baseline SLAM,
- degraded baseline SLAM,
- adaptive fusion,
- failure-aware recovery,
- self-healing SLAM.

The long-term goal is to turn these summaries into paper-ready tables for ablation studies.
