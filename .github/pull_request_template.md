## Research-software change summary

Describe what changed and whether it affects code, documentation, experiments, datasets, figures, website, or claims.

## Scientific motivation

Explain why this change is needed for adaptive multi-modal SLAM, uncertainty-aware fusion, robust state estimation, failure-aware perception, or reproducibility.

## Mathematical / algorithmic notes

Document the formulation, assumptions, numerical stability considerations, covariance assumptions, residual definitions, and limitations. Link to `docs/` updates when applicable.

## Engineering motivation

Explain how this improves architecture, testing, CI, maintainability, reproducibility, dataset handling, or usability.

## Claim status

Mark every applicable item:

- [ ] Implemented feature with source code and tests
- [ ] Prototype / scaffold only
- [ ] Planned documentation only
- [ ] Synthetic experiment only
- [ ] Real-dataset benchmark result
- [ ] Website or paper text update

## Evidence

Link the supporting evidence:

- Source files:
- Tests:
- Configs:
- Result manifests:
- Figures:
- Documentation:
- Citations:

## Benchmark honesty checklist

- [ ] No state-of-the-art claim is added without verified comparison.
- [ ] No real benchmark number is added without committed metrics and manifest.
- [ ] Synthetic results are labeled synthetic.
- [ ] Prototype features are not described as complete systems.
- [ ] Limitations are stated near claims.
- [ ] Dataset redistribution and licensing assumptions are respected.

## Limitations

State what remains incomplete after this PR.

## Reproducibility commands

```bash
pytest
python run_experiment.py --config configs/example_experiment.yaml
python scripts/make_demo_gif.py
```
