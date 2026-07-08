# Evaluation Protocol

## Metrics

| Metric | Purpose | Status |
| --- | --- | --- |
| ATE RMSE | Global trajectory accuracy | Implemented utility |
| RPE RMSE | Local drift | Implemented utility |
| Final drift | Endpoint error | Implemented utility |
| NEES | State consistency with ground truth | Implemented utility |
| NIS | Innovation consistency | Implemented utility |
| Tracking failure rate | Robustness under degradation | Prototype protocol |
| Reliability calibration | Whether confidence predicts error | Planned |
| Runtime FPS | Real-time feasibility | Scaffold |
| CPU/GPU usage | Resource use | Scaffold |

## Required reporting fields

Every benchmark result must include:

- dataset and sequence;
- sensor configuration;
- estimator/backend version;
- random seed where relevant;
- timestamp association tolerance;
- alignment convention: none, SE(3), or Sim(3);
- matched pose count;
- ATE/RPE/drift;
- failure count;
- runtime environment;
- path to the YAML config and metric JSON.

## Baselines

The benchmark table should include visual-only, IMU-only dead reckoning, LiDAR-only scaffold, fixed-weight fusion, adaptive uncertainty-aware fusion, and oracle reliability scaffold. Rows without reproducible artifacts must say `Pending`.
