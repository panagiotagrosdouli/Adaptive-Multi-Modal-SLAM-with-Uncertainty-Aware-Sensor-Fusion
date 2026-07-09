"""Render Synthetic Demo GIF and MP4 from generated SLAM results."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def _read_csv(path: Path) -> dict[str, np.ndarray]:
    with path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return {key: np.array([float(row[key]) for row in rows]) for key in rows[0]}


def make_demo_gif(results_dir: str | Path = "results", assets_dir: str | Path = "assets") -> dict[str, str]:
    root = Path(results_dir)
    frames_dir = root / "videos" / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    assets = Path(assets_dir)
    (assets / "gifs").mkdir(parents=True, exist_ok=True)
    (assets / "videos").mkdir(parents=True, exist_ok=True)
    gt = _read_csv(root / "ground_truth.csv")
    est = _read_csv(root / "estimated_trajectory.csv")
    landmarks = _read_csv(root / "landmarks.csv")
    conf = _read_csv(root / "sensor_confidence.csv")
    weights = _read_csv(root / "fusion_weights.csv")
    unc = _read_csv(root / "uncertainty.csv")
    stride = max(1, len(gt["x"]) // 80)
    indices = list(range(0, len(gt["x"]), stride))
    if indices[-1] != len(gt["x"]) - 1:
        indices.append(len(gt["x"]) - 1)
    frame_paths: list[Path] = []
    for frame_id, k in enumerate(indices):
        fig = plt.figure(figsize=(9, 5))
        ax = fig.add_axes([0.07, 0.12, 0.56, 0.78])
        panel = fig.add_axes([0.68, 0.12, 0.28, 0.78])
        ax.plot(gt["x"][: k + 1], gt["y"][: k + 1], label="ground truth")
        ax.plot(est["x"][: k + 1], est["y"][: k + 1], label="estimate")
        ax.scatter(landmarks["x"], landmarks["y"], s=10, marker="x", label="landmarks")
        ax.scatter([gt["x"][k]], [gt["y"][k]], s=45, label="robot")
        ax.add_patch(plt.Circle((est["x"][k], est["y"][k]), max(0.05, unc["covariance_trace"][k]), fill=False, linestyle="--"))
        ax.set_title("Adaptive Multi-Modal SLAM with Uncertainty-Aware Sensor Fusion\nSynthetic Demo")
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("x [m]")
        ax.set_ylabel("y [m]")
        ax.legend(fontsize=8)
        panel.axis("off")
        lines = [f"time: {gt['time'][k]:.1f}s", "", "confidence / fusion weight"]
        for sensor in ("camera", "imu", "lidar", "rgbd"):
            lines.append(f"{sensor:6s}: {conf[sensor][k]:.2f} / {weights[sensor][k]:.2f}")
        lines.extend(["", f"uncertainty: {unc['uncertainty_score'][k]:.2f}", f"failure risk: {unc['failure_risk'][k]:.2f}"])
        events = []
        if 42 <= k <= 82:
            events.append("visual degradation")
        if 72 <= k <= 106:
            events.append("LiDAR dropout")
        if 102 <= k <= 136:
            events.append("depth noise")
        if 118 <= k <= 155:
            events.append("IMU bias drift")
        if events:
            lines.extend(["", "events:", *events])
        if k == len(gt["x"]) - 1:
            lines.extend(["", "mission summary:", "Synthetic outputs saved", "metrics + figures + GIF + MP4"])
        panel.text(0.0, 1.0, "\n".join(lines), va="top", family="monospace", fontsize=9)
        frame_path = frames_dir / f"frame_{frame_id:04d}.png"
        fig.savefig(frame_path, dpi=130)
        plt.close(fig)
        frame_paths.append(frame_path)
    images = [Image.open(path).convert("P", palette=Image.Palette.ADAPTIVE) for path in frame_paths]
    gif_asset = assets / "gifs" / "demo.gif"
    gif_results = root / "videos" / "adaptive_multimodal_slam_demo.gif"
    images[0].save(gif_asset, save_all=True, append_images=images[1:], duration=90, loop=0)
    images[0].save(gif_results, save_all=True, append_images=images[1:], duration=90, loop=0)
    first = cv2.imread(str(frame_paths[0]))
    height, width = first.shape[:2]
    mp4_asset = assets / "videos" / "demo.mp4"
    mp4_results = root / "videos" / "adaptive_multimodal_slam_demo.mp4"
    for target in (mp4_asset, mp4_results):
        writer = cv2.VideoWriter(str(target), cv2.VideoWriter_fourcc(*"mp4v"), 12.0, (width, height))
        for frame_path in frame_paths:
            writer.write(cv2.imread(str(frame_path)))
        writer.release()
    return {"gif": str(gif_asset), "mp4": str(mp4_asset), "results_gif": str(gif_results), "results_mp4": str(mp4_results)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default="results")
    parser.add_argument("--assets-dir", default="assets")
    args = parser.parse_args()
    print(make_demo_gif(args.results_dir, args.assets_dir))
