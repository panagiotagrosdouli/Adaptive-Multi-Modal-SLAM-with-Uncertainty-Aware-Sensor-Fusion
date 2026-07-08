# Adaptive Multi-Modal SLAM with Uncertainty-Aware Sensor Fusion

Research software for studying **online sensor reliability estimation** and **adaptive fusion policies** in visual, inertial, and event/depth-enabled SLAM pipelines.

The project investigates a concrete question:

> Can a SLAM system estimate modality reliability online and adapt its fusion strategy before perceptual degradation becomes catastrophic tracking failure?

This repository is intentionally claim-disciplined. It provides reusable modules, evaluation utilities, documentation, and experiment structure for adaptive SLAM research. It does **not** claim state-of-the-art benchmark performance until results are backed by committed configurations, metric files, and reproduction commands.

---

## Research motivation

Visual and visual-inertial SLAM systems often fail when their frontend assumptions are violated: motion blur, weak texture, poor illumination, dynamic objects, sensor dropout, timestamp errors, or aggressive motion. Classical pipelines typically process measurements with fixed noise assumptions, even when the current sensor stream is visibly unreliable.

This project studies an adaptive alternative:

```math
Ω_i(k) = α_i(k) Σ_i^{-1},
```

where `Σ_i` is a nominal modality covariance and `α_i(k)` is an online reliability-derived information weight. The goal is to make sensor trust an explicit, measurable quantity in the estimation pipeline.

---

## Implemented capabilities

The repository currently includes:

- YAML-based experiment execution;
- uncertainty and reliability estimation for visual and inertial modalities;
- precision-based adaptive fusion weights;
- interpretable logistic failure-risk prediction;
- covariance utilities including Mahalanobis distance and Gaussian entropy;
- trajectory association and evaluation with ATE/RPE;
- Umeyama SE(3)/Sim(3) alignment for trajectory metrics;
- EuRoC parsing and ORB-SLAM3 wrapper direction;
- plotting utilities for reliability, fusion weights, and failure risk;
- reproducibility manifest support;
- research documentation, benchmark protocol, CI, and tests.

---

## Repository structure

```text
.
├── benchmark/             # Benchmark protocol and reporting conventions
├── configs/               # Experiment configurations
├── docs/                  # Theory, audit, setup, and research notes
├── experiments/           # Experiment registry guidance
├── paper/                 # Paper scaffold
├── scripts/               # Dataset preparation and degradation utilities
├── src/                   # Core research modules
├── tests/                 # Unit and smoke tests
├── .github/               # CI, PR template, issue templates
├── CONTRIBUTING.md        # Research software contribution policy
├── SECURITY.md            # Safety and responsible-use policy
├── pyproject.toml         # Black, Ruff, pytest, coverage configuration
├── run_experiment.py      # Adaptive SLAM experiment runner
└── run_orbslam3_experiment.py
```

Planned top-level directories for future extensions include `datasets/`, `examples/`, `visualization/`, `notebooks/`, `assets/`, `docker/`, and `website/`. Large datasets and generated videos should remain outside Git history unless they are small illustrative artifacts.

---

## Installation

```bash
git clone https://github.com/panagiotagrosdouli/Adaptive-Multi-Modal-SLAM-with-Uncertainty-Aware-Sensor-Fusion.git
cd Adaptive-Multi-Modal-SLAM-with-Uncertainty-Aware-Sensor-Fusion
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

For minimal usage without development tools:

```bash
python -m pip install -r requirements.txt
```

---

## Quick start

Run the adaptive SLAM smoke experiment:

```bash
python run_experiment.py --config configs/example_experiment.yaml
```

Generate plots from a saved experiment JSON:

```bash
python generate_plots.py results/euroc_degraded_adaptive_fusion_baseline.json
```

Run tests:

```bash
pytest
```

Run formatting and lint checks:

```bash
ruff check src tests scripts
black --check src tests scripts
```

---

## ORB-SLAM3 EuRoC baseline

This repository does not vendor ORB-SLAM3. Build ORB-SLAM3 separately, download EuRoC MAV, then edit:

```bash
configs/orbslam3_euroc.yaml
```

Run the ORB-SLAM3 EuRoC wrapper:

```bash
python run_orbslam3_experiment.py --config configs/orbslam3_euroc.yaml
```

If ground truth is configured, the script computes:

- matched poses;
- Absolute Trajectory Error;
- Relative Pose Error.

See `docs/orbslam3_euroc_setup.md` for backend setup details.

---

## Method overview

### 1. Reliability estimation

The visual reliability baseline combines feature count, reprojection quality, brightness, sharpness, and optional optical-flow consistency. The inertial reliability baseline uses acceleration plausibility, gyroscope magnitude, optional preintegration residuals, and optional bias stability.

These are transparent reliability signals, not learned uncertainty claims. They are designed to be calibrated later against trajectory error, innovation consistency, and tracking failure.

### 2. Adaptive fusion

Reliability is mapped to pseudo-precision:

```math
p_i = max(ε, r_i)^γ / σ_i^2,
w_i = p_i / Σ_j p_j.
```

This is closer to weighted least-squares intuition than directly normalizing reliabilities. A full estimator should ultimately modify measurement covariances or factor-graph information matrices directly.

### 3. Failure prediction

Failure risk is modeled with an interpretable logistic baseline over visual reliability, inertial reliability, reprojection error, and feature depletion. This model is monotonic and transparent, but it should not be described as calibrated probability until validated on held-out degradation sequences.

### 4. Trajectory evaluation

ATE and RPE must specify timestamp association and alignment:

- `none`: no alignment;
- `se3`: rigid alignment;
- `sim3`: similarity alignment with scale.

Monocular-only systems may report Sim(3) alignment. Stereo, RGB-D, and visual-inertial systems should report SE(3) or no-scale alignment to preserve metric-scale accountability.

---

## Benchmark protocol

See `benchmark/README.md` for the benchmark policy. Target datasets include:

| Dataset | Purpose |
| --- | --- |
| EuRoC MAV | stereo-inertial VIO/SLAM |
| TUM-VI | visual-inertial robustness |
| KITTI Odometry | outdoor visual odometry |
| TUM RGB-D | RGB-D SLAM and depth fusion |
| Event Camera Dataset | event-based reliability studies |

Every reported benchmark should include dataset sequence, backend version, sensor setup, matched poses, ATE, RPE, alignment convention, runtime, failure count, and a reproduction manifest.

---

## Documentation

- `docs/THEORY.md` — mathematical formulation and uncertainty interpretation.
- `docs/RESEARCH_AUDIT.md` — repository weaknesses, upgrades, and remaining work.
- `benchmark/README.md` — benchmark protocol and claim discipline.
- `experiments/README.md` — experiment registry expectations.
- `CONTRIBUTING.md` — contribution rules for research software.
- `SECURITY.md` — safety and responsible-use policy.

---

## Development standards

The repository uses:

- Python 3.10+;
- Black formatting;
- Ruff linting;
- pytest and coverage;
- type hints for new code;
- Google-style docstrings;
- explicit numerical validation for metric and uncertainty code;
- CI for tests and quality checks.

---

## Roadmap

### Phase 1 — Baseline reproducibility

- Run ORB-SLAM3 on EuRoC sequences.
- Store reproducible configs and manifests.
- Generate ATE/RPE tables and trajectory plots.

### Phase 2 — Reliability calibration

- Extract real frontend quality signals from ORB-SLAM3/OpenVINS outputs.
- Calibrate reliability against tracking failure and trajectory error.
- Add uncertainty heatmaps and covariance visualizations.

### Phase 3 — Adaptive fusion in real backends

- Connect reliability to covariance/information weighting.
- Compare fixed fusion, heuristic adaptive fusion, and learned weighting.
- Evaluate under controlled blur, low-light, noise, and feature-drop degradation.

### Phase 4 — Toward self-healing SLAM

- Predict failure before tracking loss.
- Diagnose likely degradation causes.
- Trigger recovery policies such as relocalization, keyframe adjustment, modality reweighting, or active viewpoint changes.

---

## Scope and limitations

The current repository is a research framework and benchmark scaffold. It contains mathematically grounded utilities and experiment infrastructure, but public benchmark claims must wait until real dataset runs are committed with metrics and manifests. This separation protects scientific credibility.

---

## Citation

If this repository supports academic work, cite it as research software:

```bibtex
@software{grosdouli_adaptive_multimodal_slam_2026,
  title = {Adaptive Multi-Modal SLAM with Uncertainty-Aware Sensor Fusion},
  author = {Grosdouli, Panagiota},
  year = {2026},
  url = {https://github.com/panagiotagrosdouli/Adaptive-Multi-Modal-SLAM-with-Uncertainty-Aware-Sensor-Fusion}
}
```

---

## License

See `LICENSE` if present. If no license file is included, add one before external reuse.

---

## Acknowledgements

This repository is conceptually aligned with open research in visual SLAM, visual-inertial odometry, robust perception, and uncertainty-aware robotics. It is designed to interoperate with established systems rather than replace them without evidence.
