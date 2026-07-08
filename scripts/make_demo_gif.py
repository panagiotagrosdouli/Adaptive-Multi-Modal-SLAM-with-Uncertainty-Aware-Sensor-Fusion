"""Generate an honest synthetic demo GIF for adaptive fusion diagnostics.

The animation is generated from deterministic synthetic data. It is not a benchmark.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from slam_fusion.fusion.adaptive import AdaptiveSensorFusion


def generate_demo(output_gif: Path, output_mp4: Path, seed: int = 7, steps: int = 80) -> None:
    """Generate synthetic trajectory, weights, uncertainty ellipse, and risk timeline."""

    rng = np.random.default_rng(seed)
    output_gif.parent.mkdir(parents=True, exist_ok=True)
    output_mp4.parent.mkdir(parents=True, exist_ok=True)
    t = np.linspace(0.0, 2.0 * np.pi, steps)
    gt = np.column_stack([np.cos(t), np.sin(t)])
    visual_rel = np.clip(0.9 - 0.65 * np.exp(-0.5 * ((np.arange(steps) - 45) / 9) ** 2), 0.05, 1.0)
    imu_rel = np.clip(0.75 + 0.05 * np.sin(t), 0.05, 1.0)
    lidar_rel = np.clip(0.85 - 0.5 * (np.arange(steps) > 58), 0.05, 1.0)
    fusion = AdaptiveSensorFusion()
    weights = []
    est = []
    current = np.array([1.0, 0.0])
    for k in range(steps):
        w = fusion.dropout_weights(
            {"camera": float(visual_rel[k]), "imu": float(imu_rel[k]), "lidar": float(lidar_rel[k])},
            {"camera": 0.04, "imu": 0.09, "lidar": 0.06},
        )
        weights.append(w)
        noise_scale = 0.02 + 0.08 * (1.0 - max(w.values()))
        current = gt[k] + rng.normal(0.0, noise_scale, size=2)
        est.append(current)
    est_arr = np.asarray(est)
    risk = 1.0 - np.maximum.reduce([visual_rel, imu_rel, lidar_rel])

    fig, ax = plt.subplots(figsize=(6, 6))

    def update(frame: int) -> list[object]:
        ax.clear()
        ax.plot(gt[: frame + 1, 0], gt[: frame + 1, 1], label="ground truth")
        ax.plot(est_arr[: frame + 1, 0], est_arr[: frame + 1, 1], label="estimated")
        ax.scatter(est_arr[frame, 0], est_arr[frame, 1], s=40)
        cov_scale = 0.04 + 0.25 * risk[frame]
        ellipse = plt.Circle(est_arr[frame], cov_scale, fill=False, linestyle="--")
        ax.add_patch(ellipse)
        w = weights[frame]
        text = (
            f"camera r={visual_rel[frame]:.2f}, w={w['camera']:.2f}\n"
            f"imu r={imu_rel[frame]:.2f}, w={w['imu']:.2f}\n"
            f"lidar r={lidar_rel[frame]:.2f}, w={w['lidar']:.2f}\n"
            f"risk={risk[frame]:.2f} | synthetic demo"
        )
        ax.text(0.02, 0.98, text, transform=ax.transAxes, va="top")
        ax.set_xlim(-1.4, 1.4)
        ax.set_ylim(-1.4, 1.4)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="lower left")
        ax.set_title("Adaptive multi-modal SLAM diagnostic demo")
        return []

    ani = animation.FuncAnimation(fig, update, frames=steps, interval=80, blit=False)
    ani.save(output_gif, writer="pillow", fps=12)
    try:
        ani.save(output_mp4, writer="ffmpeg", fps=12)
    except Exception:
        output_mp4.write_text("MP4 generation requires ffmpeg; GIF was generated successfully.\n")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gif", default="assets/demo.gif")
    parser.add_argument("--mp4", default="results/videos/demo.mp4")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    generate_demo(Path(args.gif), Path(args.mp4), seed=args.seed)


if __name__ == "__main__":
    main()
