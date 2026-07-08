"""Validate dataset manifest YAML files.

Dataset manifests describe where external datasets should live and which
sequences are expected. The validator checks structure only; it does not require
large datasets to be committed.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

REQUIRED_DATASET_FIELDS = {"name", "root", "format", "sensor_setup", "sequences"}
REQUIRED_SEQUENCE_FIELDS = {"name", "path"}
VALID_ALIGNMENT_POLICIES = {
    "visual_inertial_systems_should_report_se3_or_none",
    "stereo_systems_should_report_se3_or_none",
    "monocular_systems_may_report_sim3",
}


class DatasetManifestError(ValueError):
    """Raised when a dataset manifest is invalid."""


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Validate dataset manifest YAML files.")
    parser.add_argument("inputs", nargs="+", type=Path)
    return parser.parse_args()


def discover_yaml_files(inputs: list[Path]) -> list[Path]:
    """Return YAML files from explicit files or directories."""

    files: list[Path] = []
    for item in inputs:
        if item.is_dir():
            files.extend(sorted(item.glob("*.yaml")))
            files.extend(sorted(item.glob("*.yml")))
        elif item.is_file() and item.suffix in {".yaml", ".yml"}:
            files.append(item)
        else:
            raise FileNotFoundError(f"Not a YAML file or directory: {item}")
    if not files:
        raise DatasetManifestError("No YAML manifest files found.")
    return files


def _load_mapping(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        payload = yaml.safe_load(file) or {}
    if not isinstance(payload, dict):
        raise DatasetManifestError(f"{path}: top-level YAML must be a mapping.")
    return payload


def validate_manifest(path: Path) -> None:
    """Validate one dataset manifest."""

    payload = _load_mapping(path)
    dataset = payload.get("dataset")
    if not isinstance(dataset, dict):
        raise DatasetManifestError(f"{path}: missing dataset mapping.")

    missing_dataset = REQUIRED_DATASET_FIELDS.difference(dataset)
    if missing_dataset:
        raise DatasetManifestError(f"{path}: missing dataset fields: {sorted(missing_dataset)}")

    sequences = dataset.get("sequences")
    if not isinstance(sequences, list) or not sequences:
        raise DatasetManifestError(f"{path}: dataset.sequences must be a non-empty list.")

    for index, sequence in enumerate(sequences):
        if not isinstance(sequence, dict):
            raise DatasetManifestError(f"{path}: sequence {index} must be a mapping.")
        missing_sequence = REQUIRED_SEQUENCE_FIELDS.difference(sequence)
        if missing_sequence:
            raise DatasetManifestError(
                f"{path}: sequence {index} missing fields: {sorted(missing_sequence)}"
            )

    reporting = payload.get("reporting", {})
    if reporting and not isinstance(reporting, dict):
        raise DatasetManifestError(f"{path}: reporting must be a mapping when present.")
    alignment_policy = reporting.get("alignment_policy") if isinstance(reporting, dict) else None
    if alignment_policy is not None and alignment_policy not in VALID_ALIGNMENT_POLICIES:
        raise DatasetManifestError(
            f"{path}: invalid alignment policy {alignment_policy!r}; "
            f"expected one of {sorted(VALID_ALIGNMENT_POLICIES)}."
        )


def main() -> None:
    """Validate all requested dataset manifests."""

    args = parse_args()
    files = discover_yaml_files(args.inputs)
    for path in files:
        validate_manifest(path)
        print(f"valid: {path}")


if __name__ == "__main__":
    main()
