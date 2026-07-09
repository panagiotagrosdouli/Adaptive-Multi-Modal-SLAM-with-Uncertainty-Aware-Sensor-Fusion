"""Generate publication-style Synthetic Demo figures from code."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def _read_csv(path: Path) -> dict[str, np.ndarray]:
    with path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return {key: np.array([float(row[key]) for row in rows]) for key in rows[0]}


def generate_figures(results_dir: str | Path = "results", assets_dir: str | Path = "assets/figures") -> list[Path]:
    root = Path(results_dir)
    figures = root / "figures"
    assets = Path(assets_dir)
    figures.mkdir(parents=True, exist_ok=True)
    assets.mkdir(parents=True, exist_ok=True)
    gt = _read_csv(root / "ground_truth.csv")
    est = _read_csv(root / "estimated_trajectory.csv")
    landmarks = _read_csv(root / "landmarks.csv")
    conf = _read_csv(root / "sensor_confidence.csv")
    weights = _read_csv(root / "fusion_weights.csv")
    unc = _read_csv(root / "uncertainty.csv")
    outputs: list[Path] = []

    def save(name: str) -> None:
        for folder in (figures, assets):
            path = folder / name
            plt.savefig(path, dpi=160, bbox_inches="tight")
            outputs.append(path)
        plt.close()

    plt.figure(figsize=(7, 5))
    plt.plot(gt["x"], gt["y"], label="ground truth")
    plt.plot(est["x"], est["y"], label="estimate")
    plt.scatter(landmarks["x"], landmarks["y"], s=14, marker="x", label="landmarks")
    plt.title("Synthetic Demo: trajectory and landmark map")
    plt.axis("equal")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.legend()
    save("trajectory_map.png")

    for table, title, name, ylabel in [
        (conf, "Synthetic Demo: sensor confidence", "sensor_confidence.png", "confidence"),
        (weights, "Synthetic Demo: adaptive fusion weights", "fusion_weights.png", "weight"),
    ]:
        plt.figure(figsize=(8, 4))
        for sensor in ("camera", "imu", "lidar", "rgbd"):
            plt.plot(table["time"], table[sensor], label=sensor)
        plt.ylim(-0.05, 1.05)
        plt.title(title)
        plt.xlabel("time [s]")
        plt.ylabel(ylabel)
        plt.legend(ncol=4)
        save(name)

    plt.figure(figsize=(8, 4))
    plt.plot(unc["time"], unc["covariance_trace"], label="covariance trace")
    plt.plot(unc["time"], unc["uncertainty_score"], label="uncertainty score")
    plt.plot(unc["time"], unc["failure_risk"], label="failure risk")
    plt.title("Synthetic Demo: uncertainty monitoring")
    plt.xlabel("time [s]")
    plt.legend()
    save("uncertainty_monitoring.png")

    plt.figure(figsize=(8, 4))
    plt.plot(unc["time"], unc["nees"], label="NEES")
    plt.plot(unc["time"], unc["nis"], label="NIS")
    plt.title("Synthetic Demo: consistency diagnostics")
    plt.xlabel("time [s]")
    plt.legend()
    save("nees_nis.png")

    err = np.sqrt((est["x"] - gt["x"]) ** 2 + (est["y"] - gt["y"]) ** 2)
    plt.figure(figsize=(8, 4))
    plt.plot(gt["time"], err, label="ATE per step")
    plt.plot(gt["time"][1:], np.abs(np.diff(err)), label="RPE proxy")
    plt.title("Synthetic Demo: ATE/RPE diagnostics")
    plt.xlabel("time [s]")
    plt.ylabel("error [m]")
    plt.legend()
    save("ate_rpe.png")

    plt.figure(figsize=(7, 5))
    scatter = plt.scatter(est["x"], est["y"], c=unc["uncertainty_score"], s=18)
    plt.plot(gt["x"], gt["y"], label="ground truth")
    plt.title("Synthetic Demo: uncertainty heatmap")
    plt.axis("equal")
    plt.colorbar(scatter, label="uncertainty score")
    plt.legend()
    save("uncertainty_heatmap.png")

    plt.figure(figsize=(9, 2.5))
    labels = ["visual degradation", "LiDAR dropout", "depth noise", "IMU bias drift"]
    spans = [(4.2, 8.2), (7.2, 10.6), (10.2, 13.6), (11.8, 15.5)]
    for idx, (label, span) in enumerate(zip(labels, spans, strict=True)):
        plt.hlines(idx, span[0], span[1], linewidth=8)
        plt.text(span[1] + 0.1, idx, label, va="center")
    plt.yticks([])
    plt.xlabel("time [s]")
    plt.title("Synthetic Demo: degradation event timeline")
    save("degradation_timeline.png")
    return outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default="results")
    parser.add_argument("--assets-dir", default="assets/figures")
    args = parser.parse_args()
    for output in generate_figures(args.results_dir, args.assets_dir):
        print(output)
