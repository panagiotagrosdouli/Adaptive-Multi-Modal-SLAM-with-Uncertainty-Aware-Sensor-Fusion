from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml


@dataclass
class BenchmarkRun:
    name: str
    config: str
    kind: str
    enabled: bool = True


@dataclass
class BenchmarkPlan:
    name: str
    runs: List[BenchmarkRun]

    @property
    def enabled_runs(self) -> List[BenchmarkRun]:
        return [run for run in self.runs if run.enabled]


def load_benchmark_plan(path: str | Path) -> BenchmarkPlan:
    path = Path(path)
    raw: Dict[str, Any] = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    runs = [
        BenchmarkRun(
            name=item['name'],
            config=item['config'],
            kind=item.get('kind', 'experiment'),
            enabled=bool(item.get('enabled', True)),
        )
        for item in raw.get('runs', [])
    ]
    return BenchmarkPlan(name=raw.get('name', path.stem), runs=runs)
