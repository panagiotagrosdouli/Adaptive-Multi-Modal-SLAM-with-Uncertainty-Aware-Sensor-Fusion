# Benchmarks

Benchmark numbers are intentionally marked `Pending` until reproducible runs are committed.

| Baseline | EuRoC | KITTI | TUM RGB-D | Status |
| --- | --- | --- | --- | --- |
| Visual-only odometry | Pending | Pending | Pending | Planned |
| IMU-only dead reckoning | Pending | N/A | N/A | Prototype |
| LiDAR-only odometry | N/A | Pending | N/A | Planned |
| Fixed-weight fusion | Pending | Pending | Pending | Prototype |
| Adaptive uncertainty-aware fusion | Pending | Pending | Pending | Implemented policy, pending real backend |
| Oracle sensor reliability | Pending | Pending | Pending | Planned upper-bound scaffold |

A valid benchmark commit must include YAML config, software version, dataset sequence, alignment convention, metric JSON, and plots.
