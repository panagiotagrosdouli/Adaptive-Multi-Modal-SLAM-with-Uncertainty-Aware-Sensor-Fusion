"""Publication-oriented figures for adaptive SLAM diagnostics."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot_trajectory(
    estimated: np.ndarray,
    output_path: str | Path,
    ground_truth: np.ndarray | None = None,
) -> Path:
    """Save a 2D trajectory figure."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    estimated = np.asarray(estimated, dtype=float)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(estimated[:, 0], estimated[:, 1], label="estimated")
    if ground_truth is not None:
        gt = np.asarray(ground_truth, dtype=float)
        ax.plot(gt[:, 0], gt[:, 1], label="ground truth")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Trajectory")
    ax.axis("equal")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=200)
    plt.close(fig)
    return output


def plot_timeseries(values: dict[str, np.ndarray], output_path: str | Path, ylabel: str) -> Path:
    """Save a labelled diagnostic time-series plot."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4))
    for label, series in values.items():
        ax.plot(np.asarray(series, dtype=float), label=label)
    ax.set_xlabel("timestep")
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=200)
    plt.close(fig)
    return output
