import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass
class ExperimentSummary:
    experiment_name: str
    matched_poses: int
    absolute_trajectory_error: float
    relative_pose_error: float

    def to_markdown_row(self) -> str:
        return (
            f'| {self.experiment_name} | {self.matched_poses} | '
            f'{self.absolute_trajectory_error:.6f} | {self.relative_pose_error:.6f} |'
        )


def load_evaluation_report(path: str | Path) -> ExperimentSummary:
    path = Path(path)
    data = json.loads(path.read_text(encoding='utf-8'))
    return ExperimentSummary(
        experiment_name=data.get('experiment_name', path.stem),
        matched_poses=int(data.get('matched_poses', 0)),
        absolute_trajectory_error=float(data.get('absolute_trajectory_error', float('nan'))),
        relative_pose_error=float(data.get('relative_pose_error', float('nan'))),
    )


def aggregate_reports(paths: Iterable[str | Path]) -> List[ExperimentSummary]:
    return [load_evaluation_report(path) for path in paths]


def summaries_to_markdown(summaries: Iterable[ExperimentSummary]) -> str:
    lines = [
        '| Experiment | Matched Poses | ATE | RPE |',
        '|---|---:|---:|---:|',
    ]
    lines.extend(summary.to_markdown_row() for summary in summaries)
    return '\n'.join(lines) + '\n'
