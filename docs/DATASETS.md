# Datasets

This repository does not redistribute third-party datasets. Download datasets from their official sources and keep raw data outside Git history.

## Supported / scaffolded datasets

| Dataset | Modality | Repository support | Status |
| --- | --- | --- | --- |
| EuRoC MAV | Stereo + IMU | Parser/wrapper direction | Prototype |
| KITTI Odometry | Stereo/LiDAR depending setup | Config scaffold | Planned |
| TUM RGB-D | RGB-D | Config scaffold | Planned |
| TUM-VI | Visual-inertial | Config scaffold | Planned |
| nuScenes | Camera/LiDAR/radar/IMU | Loader scaffold | Planned |
| Custom ROS2 bag | Arbitrary ROS2 topics | Topic documentation scaffold | Prototype |

## Dataset policy

- Do not commit raw images, LiDAR scans, bags, or proprietary data.
- Commit only small synthetic fixtures and metadata manifests.
- Every result must cite the dataset sequence, calibration source, and preprocessing script.
