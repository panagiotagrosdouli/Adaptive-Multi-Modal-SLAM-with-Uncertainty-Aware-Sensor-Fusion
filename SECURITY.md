# Security Policy

This repository is research software for SLAM, sensor fusion, and robotics evaluation. It is not safety-certified autonomy software and must not be deployed on physical robots without independent validation.

## Supported versions

Security and correctness fixes should target the `main` branch until formal releases are introduced.

## Reporting a vulnerability

Please report security issues privately through GitHub's security advisory workflow if available, or by contacting the maintainer listed on the GitHub profile.

Include:

- affected commit or release;
- reproduction steps;
- expected and observed behavior;
- possible impact;
- suggested mitigation if known.

## Robotics safety disclaimer

The code may influence perception, localization, or decision-making experiments. Incorrect use can produce unsafe robot behavior. Before any hardware deployment:

1. run in simulation;
2. validate on recorded bags/datasets;
3. test with emergency stop enabled;
4. use conservative velocity limits;
5. keep a human operator in control;
6. verify calibration and timestamp synchronization.

## Dataset and model safety

Do not commit private datasets, unlicensed data, credentials, API keys, or large model checkpoints. Use external storage and document download instructions instead.
