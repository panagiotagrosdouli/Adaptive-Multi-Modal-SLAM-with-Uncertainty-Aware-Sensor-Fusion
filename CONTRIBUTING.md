# Contributing

Thank you for contributing to Adaptive Multi-Modal SLAM with Uncertainty-Aware Sensor Fusion. This repository is developed as research software, so scientific reproducibility is as important as code quality.

## Principles

1. **No unsupported claims.** Do not add benchmark numbers unless the configuration, command, metric file, and environment are included.
2. **Prefer explicit assumptions.** Sensor models, calibration assumptions, alignment choices, and dataset preprocessing steps must be documented.
3. **Keep algorithms modular.** Estimation, fusion, uncertainty, visualization, and dataset logic should remain separable.
4. **Write tests for mathematical code.** Metrics, covariance operations, timestamp association, and fusion logic require unit tests.
5. **Use typed, readable Python.** Prefer type hints, Google-style docstrings, explicit exceptions, and small functions.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Quality checks

```bash
ruff check src tests scripts
black --check src tests scripts
pytest
```

## Pull request checklist

Before opening a pull request, confirm that:

- the scientific motivation is explained;
- all new claims are backed by reproducible outputs;
- new algorithms include mathematical notes or documentation;
- new configuration files are committed;
- tests pass locally;
- large datasets, model checkpoints, and generated videos are not committed directly.

## Benchmark contributions

A benchmark contribution must include:

- dataset name and sequence;
- sensor configuration;
- backend and version;
- exact command;
- alignment convention for ATE/RPE;
- machine information for runtime measurements;
- metric JSON/CSV output;
- plots generated from scripts.

## Documentation style

Use concise scientific English. Avoid marketing language. The correct tone is: implemented method, assumptions, evidence, limitations, and next steps.
