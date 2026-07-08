"""Experiment metric logging utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ExperimentLogger:
    """Persist experiment metrics as JSON files."""

    def __init__(self, output_dir: str | Path = "results") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_metrics(self, name: str, metrics: dict[str, Any]) -> Path:
        """Save metrics and return the written path."""

        output_path = self.output_dir / f"{name}.json"
        with output_path.open("w", encoding="utf-8") as file:
            json.dump(metrics, file, indent=2)
        return output_path
