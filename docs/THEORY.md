# Theory: Adaptive Multi-Modal SLAM with Uncertainty-Aware Fusion

This note defines the scientific assumptions behind the repository. It is written to keep the codebase aligned with the standards expected from robotics papers accompanying open-source SLAM software.

## 1. Problem formulation

Let the robot state at time step `k` be

```math
x_k = (R_k, p_k, v_k, b^g_k, b^a_k)
```

where `R_k ∈ SO(3)` is orientation, `p_k ∈ R^3` is position, `v_k ∈ R^3` is velocity, and `b^g_k`, `b^a_k` are gyroscope and accelerometer biases. A multi-modal SLAM system receives visual, inertial, depth, semantic, and optionally event-camera measurements:

```math
z_k = {z^v_k, z^i_k, z^d_k, z^s_k, z^e_k}.
```

The ideal estimator solves a maximum-a-posteriori problem:

```math
x^*_{0:K} = argmin_x \sum_i ||r_i(x)||^2_{\Sigma_i^{-1}},
```

where each residual `r_i` is weighted by the inverse covariance `Σ_i^{-1}`. The central research question of this repository is how to estimate or adapt those covariances online when sensing conditions degrade.

## 2. Probabilistic interpretation

For Gaussian residuals,

```math
p(z_i | x) ∝ exp(-1/2 r_i(x)^T Σ_i^{-1} r_i(x)).
```

A modality should not be trusted because it exists; it should be trusted when its residuals, feature support, calibration state, and temporal consistency indicate that its likelihood model is valid. Adaptive fusion therefore modifies the effective information matrix:

```math
Ω_i = α_i Σ_i^{-1},     α_i ∈ [0, 1],
```

where `α_i` is an online reliability-derived weight. This is only defensible when the reliability signal has a measurable relationship to estimation error, tracking failure, or calibration consistency.

## 3. Visual reliability

A feature-based visual frontend is vulnerable to low texture, motion blur, low illumination, dynamic objects, rolling shutter, and repeated structure. Practical reliability signals include:

- number of tracked features;
- spatial feature distribution;
- mean and robust reprojection error;
- inlier ratio after geometric verification;
- optical-flow forward-backward consistency;
- image brightness and sharpness;
- keyframe parallax and triangulation angle;
- loop-closure consistency.

The repository baseline intentionally uses transparent scalar reliability estimates. A research-grade extension should calibrate these estimates against ATE/RPE, tracking loss, or normalized innovation statistics.

## 4. Inertial reliability

Inertial sensing is not automatically reliable. IMU degradation appears through saturation, bias instability, vibration, timestamp errors, and poor excitation. Useful signals include:

- preintegration residuals;
- bias magnitude and bias drift;
- acceleration norm deviation;
- gyro saturation;
- innovation statistics in an EKF or factor graph;
- temporal synchronization error.

The code treats inertial quality as a bounded reliability estimate, but a full VIO implementation should propagate IMU covariance on the manifold and validate consistency through NEES/NIS-style statistics.

## 5. Adaptive fusion baseline

The current fusion policy maps reliability to pseudo-precision:

```math
p_i = max(ε, r_i)^γ / σ_i^2,
w_i = p_i / Σ_j p_j.
```

This is a deterministic baseline. It is preferable to directly averaging reliabilities because it follows weighted least-squares intuition: high-confidence, low-noise modalities contribute more information. Its limitations are clear: it does not replace a calibrated covariance model and it does not model cross-correlations between modalities.

## 6. Failure prediction

Failure prediction is formulated as a monotonic risk model over interpretable indicators:

```math
P(failure) = sigmoid(b + w_v(1-r_v) + w_i(1-r_i) + w_e e/e_ref + w_f max(0, 1-n/n_ref)).
```

This is an interpretable baseline, not a learned failure detector. To claim calibrated failure probability, future work must fit and validate the model on held-out degradation sequences.

## 7. Evaluation metrics

Trajectory evaluation must specify:

- timestamp association tolerance;
- ATE alignment convention: none, SE(3), or Sim(3);
- RPE interval;
- number of matched poses;
- dataset sequence and sensor configuration;
- failure cases and relocalization events.

For monocular systems, Sim(3) alignment may be appropriate when scale is not observable. For stereo-inertial systems, SE(3) or no scale correction should be reported to avoid hiding metric-scale failure.

## 8. Limitations

The repository should not claim state-of-the-art performance until the benchmark scripts have been run on public datasets with fixed configurations. Until then, the correct claim is that the repository provides a modular research framework and a reproducible path toward adaptive multi-modal SLAM evaluation.

## 9. Literature anchor points

This project should be compared against established visual and visual-inertial systems such as ORB-SLAM3, VINS-Mono/VINS-Fusion, OpenVINS/MSCKF-style estimators, and modern VSLAM benchmarking protocols. The purpose is not to replace those systems immediately, but to study reliability estimation and adaptive sensor weighting as an additional supervisory layer.
