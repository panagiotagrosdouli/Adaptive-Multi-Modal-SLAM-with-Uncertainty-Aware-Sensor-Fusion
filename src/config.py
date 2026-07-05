from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


@dataclass
class ExperimentConfig:
    name: str
    raw: Dict[str, Any]

    @property
    def dataset_name(self) -> str:
        return self.raw.get('dataset', {}).get('name', 'unknown')

    @property
    def baseline_system(self) -> str:
        return self.raw.get('baseline', {}).get('system', 'unknown')

    @property
    def adaptive_fusion_enabled(self) -> bool:
        return bool(self.raw.get('adaptive_fusion', {}).get('enabled', False))


def load_config(path: str | Path) -> ExperimentConfig:
    path = Path(path)
    with path.open('r', encoding='utf-8') as file:
        raw = yaml.safe_load(file) or {}
    name = raw.get('experiment_name', path.stem)
    return ExperimentConfig(name=name, raw=raw)
