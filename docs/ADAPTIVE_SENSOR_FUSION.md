# Adaptive Sensor Fusion

## Why fixed fusion is brittle

Fixed sensor fusion assumes that each modality has stationary noise and reliability. In practice, a camera may lose texture, LiDAR may see sparse geometry, RGB-D depth may saturate, and IMU bias can drift. If the estimator keeps the same measurement covariance, it can over-trust degraded residuals.

## Implemented baseline

The implemented baseline maps reliability to pseudo-precision:

```math
p_i(k) = \max(r_i(k), \epsilon)^\gamma / \sigma_i^2.
```

The normalized fusion weight is

```math
w_i(k) = p_i(k) / \sum_j p_j(k).
```

The same reliability can inflate covariance:

```math
\tilde{\Sigma}_i(k) = \Sigma_i / \max(r_i(k), \epsilon)^\gamma.
```

## Consistency checks

The Mahalanobis distance

```math
d_i^2 = r_i^T S_i^{-1} r_i
```

is used for innovation gating. This rejects residuals that are statistically inconsistent with predicted uncertainty.

## Limitations

The current policy is a transparent research baseline. It is not calibrated, not learned, and not claimed to be optimal. Future work should compare it against fixed fusion, oracle reliability, learned reliability, and full factor-graph information scaling on real datasets.
