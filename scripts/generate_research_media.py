"""Generate publication-oriented trajectory and uncertainty animations.

The script consumes the JSON output produced by `run_experiment.py` and writes
MP4/GIF animations without inventing new experiment data.  If optional video
writers are unavailable, it still produces an SVG trajectory figure.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter

LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Generate SLAM research media from experiment logs.")
    parser.add_argument("input", type=Path, help="Path to experiment JSON produced by run_experiment.py.")
    parser.add_argument("--output-dir", type=Path, default=Path("results/videos"))
    parser.add_argument("--fps", type=int, default=10)
    parser.add_argument("--dpi", type=int, default=160)
    return parser.parse_args()


def load_steps(path: Path) -> list[dict[str, Any]]:
    """Load experiment steps from a metrics JSON file."""

    if not path.exists():
        raise FileNotFoundError(f"Experiment JSON does not exist: {path}")
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    steps = payload.get("steps", payload if isinstance(payload, list) else None)
    if not isinstance(steps, list) or not steps:
        raise ValueError("Input JSON must contain a non-empty 'steps' list or be a list of steps.")
    return steps


def extract_positions(steps: list[dict[str, Any]]) -> np.ndarray:
    """Extract an Nx3 trajectory array from experiment steps."""

    positions = []
    for index, step in enumerate(steps):
        position = np.asarray(step.get("position"), dtype=np.float64)
        if position.shape != (3,) or not np.all(np.isfinite(position)):
            raise ValueError(f"Step {index} has invalid 3D position: {position}")
        positions.append(position)
    return np.vstack(positions)


def extract_series(steps: list[dict[str, Any]], key: str, default: float = 0.0) -> np.ndarray:
    """Extract a finite scalar series from experiment steps."""

    values = np.asarray([float(step.get(key, default)) for step in steps], dtype=np.float64)
    if not np.all(np.isfinite(values)):
        raise ValueError(f"Series {key!r} contains NaN or infinite values.")
    return values


def save_static_trajectory(positions: np.ndarray, output_path: Path) -> None:
    """Save a vector trajectory plot suitable for documentation."""

    fig, axis = plt.subplots(figsize=(6, 4))
    axis.plot(positions[:, 0], positions[:, 1], linewidth=2)
    axis.scatter(positions[0, 0], positions[0, 1], marker="o", label="start")
    axis.scatter(positions[-1, 0], positions[-1, 1], marker="x", label="end")
    axis.set_xlabel("x [m]")
    axis.set_ylabel("y [m]")
    axis.set_title("Estimated trajectory")
    axis.axis("equal")
    axis.grid(True, alpha=0.3)
    axis.legend()
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def save_animation(
    positions: np.ndarray,
    failure_probability: np.ndarray,
    visual_reliability: np.ndarray,
    output_path: Path,
    *,
    fps: int,
    dpi: int,
) -> None:
    """Save a GIF animation of trajectory evolution and uncertainty signals."""

    fig, (trajectory_axis, signal_axis) = plt.subplots(1, 2, figsize=(10, 4))
    trajectory_axis.set_title("Trajectory evolution")
    trajectory_axis.set_xlabel("x [m]")
    trajectory_axis.set_ylabel("y [m]")
    trajectory_axis.axis("equal")
    trajectory_axis.grid(True, alpha=0.3)

    margin = 0.05 + 0.1 * np.ptp(positions[:, :2], axis=0)
    trajectory_axis.set_xlim(positions[:, 0].min() - margin[0], positions[:, 0].max() + margin[0])
    trajectory_axis.set_ylim(positions[:, 1].min() - margin[1], positions[:, 1].max() + margin[1])

    signal_axis.set_title("Reliability and failure risk")
    signal_axis.set_xlabel("step")
    signal_axis.set_ylabel("score")
    signal_axis.set_ylim(0.0, 1.05)
    signal_axis.grid(True, alpha=0.3)

    trajectory_line, = trajectory_axis.plot([], [], linewidth=2)
    current_point, = trajectory_axis.plot([], [], marker="o")
    visual_line, = signal_axis.plot([], [], label="visual reliability")
    failure_line, = signal_axis.plot([], [], label="failure probability")
    signal_axis.legend(loc="lower right")

    steps = np.arange(len(positions))

    def update(frame: int) -> tuple[Any, ...]:
        end = frame + 1
        trajectory_line.set_data(positions[:end, 0], positions[:end, 1])
        current_point.set_data([positions[frame, 0]], [positions[frame, 1]])
        visual_line.set_data(steps[:end], visual_reliability[:end])
        failure_line.set_data(steps[:end], failure_probability[:end])
        signal_axis.set_xlim(0, max(1, len(positions) - 1))
        return trajectory_line, current_point, visual_line, failure_line

    animation = FuncAnimation(fig, update, frames=len(positions), interval=1000 / fps, blit=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    animation.save(output_path, writer=PillowWriter(fps=fps), dpi=dpi)
    plt.close(fig)


def main() -> None:
    """Generate media artifacts."""

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    steps = load_steps(args.input)
    positions = extract_positions(steps)
    failure_probability = extract_series(steps, "failure_probability")
    visual_reliability = extract_series(steps, "visual_reliability", default=1.0)

    stem = args.input.stem
    svg_path = args.output_dir / f"{stem}_trajectory.svg"
    gif_path = args.output_dir / f"{stem}_slam_uncertainty.gif"

    save_static_trajectory(positions, svg_path)
    LOGGER.info("Saved %s", svg_path)

    try:
        save_animation(
            positions,
            failure_probability,
            visual_reliability,
            gif_path,
            fps=args.fps,
            dpi=args.dpi,
        )
        LOGGER.info("Saved %s", gif_path)
    except Exception as exc:  # pragma: no cover - depends on optional writer stack
        LOGGER.warning("Could not save animation: %s", exc)


if __name__ == "__main__":
    main()
