"""Visualization utilities for adaptive SLAM experiment logs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt


class VisualizationError(ValueError):
    """Raised when experiment logs cannot be visualized."""


def load_experiment_steps(path: str | Path) -> list[dict[str, Any]]:
    """Load experiment steps from a JSON metrics file."""

    json_path = Path(path)
    if not json_path.exists():
        raise FileNotFoundError(f"Experiment JSON not found: {json_path}")
    with json_path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    steps = data.get("steps", [])
    if not isinstance(steps, list):
        raise VisualizationError("Experiment JSON field 'steps' must be a list.")
    return steps


def _plot_series(
    steps: list[dict[str, Any]],
    keys: list[str],
    title: str,
    ylabel: str,
    output_path: str | Path,
) -> None:
    """Plot one or more scalar series from experiment steps."""

    if not steps:
        raise VisualizationError("Cannot plot an empty experiment log.")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    x_values = [step["step"] for step in steps]

    plt.figure(figsize=(7, 4))
    for key in keys:
        missing = [index for index, step in enumerate(steps) if key not in step]
        if missing:
            raise VisualizationError(f"Missing key {key!r} in steps: {missing[:5]}")
        y_values = [step[key] for step in steps]
        plt.plot(x_values, y_values, label=key)
    plt.xlabel("Step")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output, dpi=200)
    plt.close()


def plot_failure_probability(
    steps: list[dict[str, Any]],
    output_path: str | Path = "results/plots/failure_probability.png",
) -> None:
    """Plot predicted SLAM failure probability."""

    _plot_series(
        steps,
        ["failure_probability"],
        "Predicted SLAM Failure Probability",
        "Probability",
        output_path,
    )


def plot_reliability(
    steps: list[dict[str, Any]],
    output_path: str | Path = "results/plots/reliability.png",
) -> None:
    """Plot visual and inertial reliability estimates."""

    _plot_series(
        steps,
        ["visual_reliability", "inertial_reliability"],
        "Sensor Reliability Estimates",
        "Reliability",
        output_path,
    )


def plot_fusion_weights(
    steps: list[dict[str, Any]],
    output_path: str | Path = "results/plots/fusion_weights.png",
) -> None:
    """Plot adaptive sensor fusion weights."""

    _plot_series(
        steps,
        ["visual_weight", "inertial_weight"],
        "Adaptive Fusion Weights",
        "Weight",
        output_path,
    )


def generate_all_plots(
    experiment_json: str | Path,
    output_dir: str | Path = "results/plots",
) -> None:
    """Generate all standard plots from an experiment JSON file."""

    steps = load_experiment_steps(experiment_json)
    output = Path(output_dir)
    plot_failure_probability(steps, output / "failure_probability.png")
    plot_reliability(steps, output / "reliability.png")
    plot_fusion_weights(steps, output / "fusion_weights.png")
