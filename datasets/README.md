# Datasets

This directory stores dataset documentation, manifests, and preparation scripts only. It must not contain redistributed copies of EuRoC, KITTI, TUM RGB-D, TUM-VI, nuScenes, ROS bags, or other third-party datasets unless their license explicitly permits redistribution.

## Supported targets

| Dataset | Status | Intended modalities | Notes |
| --- | --- | --- | --- |
| Synthetic | Prototype | configurable | Generated from repository code with deterministic seeds. |
| EuRoC MAV | Scaffold | stereo camera, IMU | Use official download source and citation. |
| KITTI Odometry | Scaffold | camera, LiDAR, poses | Use official KITTI terms and cite appropriately. |
| TUM RGB-D | Scaffold | RGB, depth, poses | Use official TUM RGB-D citation. |
| TUM-VI | Planned | camera, IMU | Pending loader and evaluation config. |
| nuScenes | Planned | camera, LiDAR, radar, ego poses | Pending manifest and loader scaffold. |
| Custom ROS2 bag | Prototype | user-defined topics | Use local paths and topic manifests. |

## Manifest format

A manifest should describe local paths and scientific provenance:

```yaml
name: EuRoC MAV
sequence: MH_01_easy
root: /absolute/path/to/EuRoC/MH_01_easy
modalities: [camera, imu]
citation: Use the official EuRoC MAV citation.
license_note: Do not redistribute dataset files; follow the official license.
status: Pending
```

Use `slam_fusion.datasets.manifests.load_manifest` to load and validate manifests before launching experiments.

## Reporting rule

A benchmark number is publishable in this repository only when the corresponding manifest, experiment config, metrics JSON, and command line are committed. Until then, tables must say **Pending**.
