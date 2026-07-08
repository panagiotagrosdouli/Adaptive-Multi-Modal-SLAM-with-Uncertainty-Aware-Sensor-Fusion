# ROS2 Prototype

ROS2 support is currently **Prototype**.

## Planned node graph

| Node | Inputs | Outputs | Status |
| --- | --- | --- | --- |
| `sensor_sync_node` | camera, IMU, LiDAR, RGB-D topics | synchronized packets | Prototype |
| `reliability_node` | frontend diagnostics | reliability scores | Planned |
| `adaptive_fusion_node` | residuals, covariances, reliability | adaptive weights | Planned |
| `slam_backend_node` | adaptive factors | poses, covariance | Planned |
| `risk_monitor_node` | uncertainty + reliability | risk score | Planned |

## Topic conventions

- `/camera/image_raw`
- `/imu/data`
- `/points_raw`
- `/camera/depth/image_raw`
- `/tf`
- `/slam_fusion/pose`
- `/slam_fusion/reliability`
- `/slam_fusion/risk`

No production runtime claim is made until launch files, message definitions, rviz config, and bag playback tests are implemented.
