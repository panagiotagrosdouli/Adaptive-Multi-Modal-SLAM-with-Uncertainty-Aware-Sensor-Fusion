from pathlib import Path
from typing import Iterable

from src.result_aggregation import ExperimentSummary


def write_markdown_results_table(summaries: Iterable[ExperimentSummary], output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        '| Experiment | Matched poses | ATE | RPE |',
        '|---|---:|---:|---:|',
    ]
    for summary in summaries:
        lines.append(
            f'| {summary.experiment_name} | {summary.matched_poses} | '
            f'{summary.absolute_trajectory_error:.6f} | {summary.relative_pose_error:.6f} |'
        )
    output_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def write_csv_results_table(summaries: Iterable[ExperimentSummary], output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ['experiment_name,matched_poses,absolute_trajectory_error,relative_pose_error']
    for summary in summaries:
        lines.append(
            f'{summary.experiment_name},{summary.matched_poses},'
            f'{summary.absolute_trajectory_error:.6f},{summary.relative_pose_error:.6f}'
        )
    output_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
