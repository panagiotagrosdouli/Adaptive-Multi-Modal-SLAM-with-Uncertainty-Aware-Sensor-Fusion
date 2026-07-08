# Benchmark Protocol

This directory defines how benchmark results should be produced and reported. It intentionally contains protocol documentation before large benchmark artifacts. Public datasets must be downloaded externally and should not be committed.

## Target datasets

| Dataset | Primary purpose | Notes |
| --- | --- | --- |
| EuRoC MAV | stereo-inertial VIO/SLAM | report sequence-level ATE/RPE and tracking failures |
| TUM-VI | visual-inertial robustness | useful for calibration and fast motion |
| KITTI Odometry | outdoor visual odometry | report sequence-level translation drift where applicable |
| TUM RGB-D | RGB-D SLAM | useful for depth fusion and loop closure |
| Event Camera Dataset | event-based degradation study | useful for event modality reliability |

## Required metrics

Every benchmark table must include:

- dataset and sequence;
- backend and version;
- sensor configuration;
- number of matched poses;
- ATE RMSE;
- RPE RMSE;
- alignment convention;
- FPS or mean processing time;
- CPU/GPU/RAM if measured;
- tracking failures;
- relocalization or loop-closure count if available.

## Alignment policy

- Monocular-only trajectories may report Sim(3) alignment, but this must be stated.
- Stereo, RGB-D, and visual-inertial trajectories should report SE(3) or no-scale alignment to preserve metric-scale accountability.
- Do not compare methods using different alignment conventions in the same table unless explicitly marked.

## File convention

Recommended output layout:

```text
results/
├── metrics/
│   ├── euroc_mh01_orbslam3.json
│   └── euroc_mh01_adaptive.json
├── figures/
│   ├── euroc_mh01_trajectory.svg
│   └── euroc_mh01_uncertainty.svg
├── videos/
│   └── euroc_mh01_tracking.mp4
└── manifests/
    └── euroc_mh01_orbslam3_manifest.json
```

## Claim discipline

A benchmark number is valid only if the repository contains:

1. the configuration file;
2. the exact command;
3. the metric output;
4. the plotting or table-generation script;
5. the environment description.

Do not edit benchmark tables manually.
