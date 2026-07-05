# Research Questions

This project is designed around research questions rather than only software features.

## Primary Question

Can online uncertainty estimation improve the robustness of visual-inertial SLAM under perceptual degradation?

## Secondary Questions

1. Which visual quality signals best predict tracking degradation?
2. Can modality-specific reliability estimates improve adaptive sensor fusion?
3. Can localization failure be predicted before catastrophic tracking loss?
4. Which recovery actions are most effective under different failure modes?
5. How does adaptive fusion compare against fixed-fusion SLAM baselines on degraded sequences?

## Long-Term Question

Can SLAM systems become self-healing by anticipating failure, diagnosing degradation, and activating recovery policies online?

## Hypothesis

A SLAM system that explicitly estimates uncertainty and adapts its fusion strategy online will reduce tracking failures and trajectory error compared with a fixed-fusion baseline under controlled visual degradation.

## Expected Evidence

The hypothesis should be supported by:

- lower Absolute Trajectory Error,
- lower Relative Pose Error,
- fewer tracking failures,
- faster recovery after degradation,
- calibrated uncertainty estimates,
- clear ablation studies.
