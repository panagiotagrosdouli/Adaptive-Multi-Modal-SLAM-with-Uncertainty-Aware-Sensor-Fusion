# Experiments

Experiments should be defined through committed configuration files rather than ad-hoc command-line edits. The goal is to make every reported figure and table reproducible.

## Experiment record

Each experiment should specify:

- name;
- dataset;
- sequence;
- sensor configuration;
- backend;
- backend configuration path;
- degradation model if any;
- random seed;
- output directory;
- evaluation protocol;
- expected artifacts.

## Example naming convention

```text
experiments/
├── euroc/
│   ├── mh01_orbslam3_baseline.yaml
│   ├── mh01_adaptive_fusion.yaml
│   └── mh01_blur_degradation.yaml
├── tum_vi/
└── kitti/
```

## Reproducibility manifest

Every run should generate a manifest under `results/manifests/` containing:

- Git commit;
- config hash;
- command;
- input dataset paths;
- output files;
- environment metadata;
- timestamp;
- metric summary.

## Scientific reporting

An experiment is complete only when it can answer a concrete research question. Example:

> Does adaptive sensor weighting reduce tracking failure under synthetic motion blur compared with fixed visual-inertial fusion on EuRoC MH_01?

Avoid experiments that only produce attractive plots without a falsifiable question.
