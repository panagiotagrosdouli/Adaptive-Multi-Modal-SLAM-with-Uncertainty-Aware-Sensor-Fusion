# ORB-SLAM3 EuRoC Setup Guide

This document describes how to run a real ORB-SLAM3 baseline experiment on EuRoC MAV using this repository.

## 1. Build ORB-SLAM3

Install and build ORB-SLAM3 separately from this repository. This project does not vendor ORB-SLAM3 because it is an external SLAM system with its own dependencies and license.

Expected executable example:

```bash
/path/to/ORB_SLAM3/Examples/Stereo-Inertial/stereo_inertial_euroc
```

## 2. Download EuRoC MAV

Download a EuRoC sequence such as `MH_01_easy` and keep the original EuRoC folder structure:

```text
MH_01_easy/
└── mav0/
    ├── cam0/
    ├── cam1/
    ├── imu0/
    └── state_groundtruth_estimate0/
```

## 3. Edit the experiment config

Copy or edit:

```bash
configs/orbslam3_euroc.yaml
```

Update the following paths:

```yaml
orbslam3:
  executable: /path/to/ORB_SLAM3/Examples/Stereo-Inertial/stereo_inertial_euroc
  vocabulary: /path/to/ORB_SLAM3/Vocabulary/ORBvoc.txt
  settings: /path/to/ORB_SLAM3/Examples/Stereo-Inertial/EuRoC.yaml
  sequence_path: /path/to/EuRoC/MH_01_easy
  output_trajectory: results/trajectories/orbslam3_euroc_mh01.csv

dataset:
  ground_truth: /path/to/EuRoC/MH_01_easy/mav0/state_groundtruth_estimate0/data.csv
```

## 4. Run ORB-SLAM3

```bash
python run_orbslam3_experiment.py --config configs/orbslam3_euroc.yaml
```

The script will:

1. Validate the external ORB-SLAM3 paths.
2. Print the exact ORB-SLAM3 command.
3. Run the sequence.
4. Load the estimated trajectory.
5. Load EuRoC ground truth if provided.
6. Compute ATE and RPE.
7. Save an evaluation report under `results/`.

## 5. Expected outputs

```text
results/trajectories/orbslam3_euroc_mh01.csv
results/orbslam3_euroc_mh01_baseline_evaluation.json
```

## Research role

This ORB-SLAM3 baseline is the first real benchmark target. Once baseline metrics are reliable, the next research steps are:

- apply controlled perceptual degradation,
- compare clean vs degraded runs,
- estimate failure likelihood from SLAM signals,
- introduce adaptive fusion and recovery policies,
- evaluate whether self-healing behavior reduces failures and trajectory error.
