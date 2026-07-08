# Uncertainty Quantification

## Implemented uncertainty signals

- Covariance trace: simple scalar proxy for total variance.
- Log-determinant: volume proxy for Gaussian uncertainty.
- Gaussian entropy: information-theoretic proxy under Gaussian assumptions.
- NEES: state-estimation consistency when ground truth is available.
- NIS: innovation consistency for measurements.
- Mahalanobis gating: residual rejection under predicted innovation covariance.
- Risk score: bounded diagnostic combining uncertainty, reliability, and innovation consistency.

## Interpretation

A low covariance trace does not guarantee correctness. A system can be overconfident and wrong. Therefore uncertainty metrics must be evaluated with NEES/NIS and trajectory error when ground truth exists.

## Calibration plan

Future experiments should plot reliability against ATE/RPE, NIS exceedance rate, tracking status, and degradation type. Only after held-out validation should risk scores be called probabilities.
