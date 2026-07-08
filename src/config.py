"""Configuration loading for adaptive SLAM experiments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ExperimentConfig:
    """YAML-backed experiment configuration."""

    name: str
    raw: dict[str, Any]

    @property
    def dataset_name(self) -> str:
        """Return configured dataset name."""

        return str(self.raw.get("dataset", {}).get("name", "unknown"))

    @property
    def baseline_system(self) -> str:
        """Return configured baseline system."""

        return str(self.raw.get("baseline", {}).get("system", "unknown"))

    @property
    def adaptive_fusion_enabled(self) -> bool:
        """Return whether adaptive fusion is enabled."""

        return bool(self.raw.get("adaptive_fusion", {}).get("enabled", False))


def load_config(path: str | Path) -> ExperimentConfig:
    """Load an experiment configuration from YAML."""

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Experiment configuration not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as file:
        raw = yaml.safe_load(file) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"Experiment configuration must be a mapping: {config_path}")
    name = str(raw.get("experiment_name", config_path.stem))
    return ExperimentConfig(name=name, raw=raw)
