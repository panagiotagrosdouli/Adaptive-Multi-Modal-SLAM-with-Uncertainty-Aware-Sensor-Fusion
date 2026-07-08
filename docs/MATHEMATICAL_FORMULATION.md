# Mathematical Formulation

This document defines the research model used by the repository. It is a formulation and software scaffold, not a claim that a complete production SLAM backend is implemented.

## State

The nominal robot state at time `k` is

```math
x_k = \{T_{WB,k}, v_{W,k}, b^g_k, b^a_k\},
```

where `T_WB in SE(3)` is the body pose in the world frame, `v_W` is metric velocity, and `b^g`, `b^a` are gyroscope and accelerometer biases. The local error state uses a 15D vector containing orientation, position, velocity, and bias perturbations.

## Measurements

Camera, LiDAR, depth, and IMU streams are modeled as conditionally independent factors given the state and calibration:

```math
z^i_k = h_i(x_k, \theta_i) + n^i_k, \quad n^i_k \sim \mathcal{N}(0, \Sigma^i_k).
```

The repository represents the nominal covariance `Sigma_i` and an online reliability score `r_i(k) in [0, 1]` for each modality.

## Innovation and residual consistency

For an innovation or residual

```math
\nu^i_k = z^i_k - h_i(\hat{x}_k),
```

the normalized innovation squared is

```math
NIS_i = (\nu^i_k)^T (S^i_k)^{-1} \nu^i_k,
```

where `S_i` is innovation covariance. Large NIS values indicate inconsistency between the predicted uncertainty and observed residual.

The normalized estimation error squared is

```math
NEES = e_k^T P_k^{-1} e_k,
```

where `e_k` is the state error and `P_k` is state covariance. NEES requires ground truth and is therefore mainly used for synthetic simulation or calibrated benchmark evaluation.

## Adaptive fusion

Fixed fusion assumes constant measurement covariances. This is insufficient when cameras suffer blur or low light, LiDAR returns are sparse, depth saturates, or IMU bias/noise changes. The implemented baseline converts reliability into pseudo-precision:

```math
p_i(k) = \frac{\max(r_i(k), \epsilon)^\gamma}{\sigma_i^2}, \quad
w_i(k) = \frac{p_i(k)}{\sum_j p_j(k)}.
```

Equivalently, reliability can inflate covariance:

```math
\tilde{\Sigma}_i(k) = \frac{1}{\max(r_i(k), \epsilon)^\gamma} \Sigma_i.
```

This does not prove optimality; it provides a transparent baseline that can later be compared against calibrated Bayesian, learned, or factor-graph information-weighting policies.

## Failure probability and risk

The current code exposes a bounded risk score derived from covariance trace, minimum modality reliability, and innovation consistency. It should be interpreted as a diagnostic score, not a calibrated probability, until validated on held-out sequences.
