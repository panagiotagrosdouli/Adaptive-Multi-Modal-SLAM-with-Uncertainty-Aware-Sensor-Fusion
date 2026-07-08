# System Architecture

```text
Sensors -> Time synchronization -> Frontend quality signals -> Reliability estimation
       -> Adaptive covariance / information scaling -> Backend update / factor graph
       -> Mapping + uncertainty diagnostics -> Evaluation + visualization
```

## Sensor layer

The sensor layer exposes `SensorMeasurement` objects with timestamp, modality, data payload, covariance, reliability, and metadata. This keeps raw camera, IMU, LiDAR, and RGB-D measurements separate from estimator-specific factors.

## Frontend layer

The frontend extracts interpretable quality signals such as feature count, inlier ratio, reprojection error, brightness, sharpness, feature dropout, LiDAR feature availability, and depth association validity.

## Fusion layer

The fusion layer maps reliability to either normalized precision weights or covariance inflation. The implemented policy is transparent and deterministic so it can be audited and compared against fixed-weight and oracle-reliability baselines.

## Backend layer

The backend currently provides scaffolds for EKF, factor graph, loop closure, pose graph optimization, sliding-window optimization, and marginalization. A production-grade optimizer is planned and must be evaluated separately.

## Evaluation layer

Evaluation reports ATE, RPE, drift, NEES, NIS, tracking failure rate, runtime, and reliability calibration. Pending benchmark rows must remain marked `Pending`.
