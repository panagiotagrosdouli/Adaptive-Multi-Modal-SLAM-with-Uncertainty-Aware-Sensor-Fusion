"""Validate benchmark metric JSON files before reporting.

This validator is deliberately conservative. It rejects smoke experiment logs and
requires the metadata needed to interpret SLAM benchmark numbers.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_METADATA = {"dataset", "sequence", "backend", "sensor_setup", "alignment"}
REQUIRED_METRICS = {"matched_poses", "ate_rmse", "rpe_rmse", "tracking_failures"}
VALID_ALIGNMENTS = {"none", "se3", "sim3"}


class BenchmarkValidationError(ValueError):
    """Raised when a benchmark metric file is invalid."""


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Validate benchmark metric JSON files.")
    parser.add_argument("inputs", nargs="+", type=Path)
    return parser.parse_args()


def discover_json_files(inputs: list[Path]) -> list[Path]:
    """Return JSON files from files or directories."""

    files: list[Path] = []
    for item in inputs:
        if item.is_dir():
            files.extend(sorted(item.glob("*.json")))
        elif item.is_file() and item.suffix == ".json":
            files.append(item)
        else:
            raise FileNotFoundError(f"Not a JSON file or directory: {item}")
    if not files:
        raise BenchmarkValidationError("No JSON metric files found.")
    return files


def _require_mapping(payload: dict[str, Any], key: str, path: Path) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise BenchmarkValidationError(f"{path}: field {key!r} must be a mapping.")
    return value


def _require_numeric(metrics: dict[str, Any], key: str, path: Path) -> None:
    value = metrics.get(key)
    if value is None:
        raise BenchmarkValidationError(f"{path}: missing numeric metric {key!r}.")
    try:
        float(value)
    except (TypeError, ValueError) as exc:
        raise BenchmarkValidationError(f"{path}: metric {key!r} must be numeric.") from exc


def validate_metric_file(path: Path) -> None:
    """Validate one benchmark metric file."""

    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise BenchmarkValidationError(f"{path}: top-level JSON must be an object.")
    if "steps" in payload:
        raise BenchmarkValidationError(
            f"{path}: smoke experiment logs are not benchmark metric files."
        )

    metadata = _require_mapping(payload, "metadata", path)
    metrics = _require_mapping(payload, "metrics", path)

    missing_metadata = REQUIRED_METADATA.difference(metadata)
    missing_metrics = REQUIRED_METRICS.difference(metrics)
    if missing_metadata:
        raise BenchmarkValidationError(
            f"{path}: missing metadata fields: {sorted(missing_metadata)}"
        )
    if missing_metrics:
        raise BenchmarkValidationError(f"{path}: missing metric fields: {sorted(missing_metrics)}")

    alignment = str(metadata.get("alignment"))
    if alignment not in VALID_ALIGNMENTS:
        raise BenchmarkValidationError(
            f"{path}: alignment must be one of {sorted(VALID_ALIGNMENTS)}; got {alignment!r}."
        )

    for key in ["matched_poses", "ate_rmse", "rpe_rmse", "tracking_failures"]:
        _require_numeric(metrics, key, path)
    if "fps" in metrics:
        _require_numeric(metrics, "fps", path)


def main() -> None:
    """Validate all requested metric files."""

    args = parse_args()
    files = discover_json_files(args.inputs)
    for path in files:
        validate_metric_file(path)
        print(f"valid: {path}")


if __name__ == "__main__":
    main()
