"""Deterministic Synthetic Demo for adaptive multi-modal SLAM.

The generated metrics and media are explicitly **Synthetic Demo** results. They
are useful for reproducibility and smoke testing, not for real-world benchmark
claims.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

SENSORS = ("camera", "imu", "lidar", "rgbd")


@dataclass(frozen=True)
class SyntheticSLAMConfig:
    seed: int = 7
    steps: int = 160
    dt: float = 0.1
    landmark_count: int = 36
    output_dir: Path = Path("results")
    fusion_mode: str = "adaptive"
    dropout_probability: float = 0.03
    noise: dict[str, float] = field(
        default_factory=lambda: {"camera": 0.09, "imu": 0.05, "lidar": 0.07, "rgbd": 0.08}
    )
    degradation_events: dict[str, tuple[int, int]] = field(
        default_factory=lambda: {
            "visual_degradation": (42, 82),
            "lidar_dropout": (72, 106),
            "depth_noise": (102, 136),
            "imu_bias_drift": (118, 155),
        }
    )


def adaptive_weights(confidence: dict[str, float], noise: dict[str, float], mode: str = "adaptive") -> dict[str, float]:
    if mode == "fixed":
        active = {k: 1.0 for k, v in confidence.items() if v > 0.0}
        total = sum(active.values()) or 1.0
        return {k: active.get(k, 0.0) / total for k in confidence}
    precision = {
        k: max(confidence[k], 1e-6) ** 2 / max(noise[k] ** 2, 1e-9)
        for k in confidence
    }
    total = sum(precision.values()) or 1.0
    return {k: float(precision[k] / total) for k in confidence}


def run_synthetic_slam(config: SyntheticSLAMConfig | None = None) -> dict[str, Any]:
    cfg = config or SyntheticSLAMConfig()
    out = Path(cfg.output_dir)
    for folder in (out, out / "metrics", out / "figures", out / "videos"):
        folder.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(cfg.seed)
    time = np.arange(cfg.steps) * cfg.dt
    truth = _truth(time)
    landmarks = _landmarks(rng, cfg.landmark_count)
    estimate = np.zeros_like(truth)
    estimate[0] = truth[0] + rng.normal(0.0, 0.05, 3)
    covariance = np.eye(3) * 0.08
    imu_bias = np.zeros(3)
    measurements: list[dict[str, Any]] = []
    conf_rows: list[dict[str, float]] = []
    weight_rows: list[dict[str, float]] = []
    uncertainty_rows: list[dict[str, float]] = []
    rejected_rows: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    for k in range(cfg.steps):
        if _active(cfg, "imu_bias_drift", k):
            imu_bias += np.array([0.0015, -0.0008, 0.0006])
        cond = _conditions(cfg, k, rng)
        confidence = {s: _confidence(cfg.noise[s], cond[s]["noise"], cond[s]["dropped"]) for s in SENSORS}
        noise = {s: float(cond[s]["noise"] if not cond[s]["dropped"] else 1e6) for s in SENSORS}
        weights = adaptive_weights(confidence, noise, cfg.fusion_mode)
        pred = estimate[k - 1].copy() if k else estimate[0].copy()
        if k:
            pred[:2] += truth[k, :2] - truth[k - 1, :2] + rng.normal(0.0, 0.015, 2)
            pred[2] += truth[k, 2] - truth[k - 1, 2] + rng.normal(0.0, 0.005)
            covariance += np.diag([0.012, 0.012, 0.004])
        fused = pred.copy()
        active_weight = 0.0
        nis_values: list[float] = []
        for sensor in SENSORS:
            z = _measurement(sensor, truth[k], truth[max(k - 1, 0)], cfg.dt, cond[sensor], rng, imu_bias)
            measurements.append({"step": k, "time": float(time[k]), "sensor": sensor, "event": cond[sensor]["event"], "dropped": z is None, "confidence": confidence[sensor]})
            if z is None or weights[sensor] <= 0.0:
                continue
            innovation = z - pred
            nis_sensor = float(innovation.T @ innovation / max(noise[sensor] ** 2, 1e-9))
            if nis_sensor > 16.27 and confidence[sensor] < 0.35:
                rejected_rows.append({"step": k, "time": float(time[k]), "sensor": sensor, "nis": nis_sensor, "reason": "mahalanobis_gate"})
                continue
            fused += weights[sensor] * innovation
            active_weight += weights[sensor]
            nis_values.append(nis_sensor)
        estimate[k] = fused if active_weight > 0.0 else pred
        covariance *= float(np.clip(1.0 - 0.38 * active_weight, 0.45, 1.08))
        covariance = 0.5 * (covariance + covariance.T) + np.eye(3) * 1e-8
        error = estimate[k] - truth[k]
        trace = float(np.trace(covariance))
        nees = float(error.T @ np.linalg.pinv(covariance) @ error)
        uncertainty = float(np.clip(trace / 0.5 + (1.0 - np.mean(list(confidence.values()))), 0.0, 10.0))
        base = {"step": k, "time": float(time[k])}
        conf_rows.append(base | confidence)
        weight_rows.append(base | weights)
        uncertainty_rows.append(base | {"covariance_trace": trace, "log_determinant": float(np.linalg.slogdet(covariance)[1]), "nees": nees, "nis": float(np.mean(nis_values) if nis_values else 0.0), "innovation_norm": float(np.linalg.norm(error)), "uncertainty_score": uncertainty, "failure_risk": float(np.clip(uncertainty / 3.0, 0.0, 1.0))})
        for name, (start, end) in cfg.degradation_events.items():
            if k in (start, end):
                events.append({"step": k, "time": float(time[k]), "event": name, "boundary": "start" if k == start else "end"})
    _write_csv(out / "ground_truth.csv", ["step", "time", "x", "y", "theta"], ((i, time[i], *truth[i]) for i in range(cfg.steps)))
    _write_csv(out / "estimated_trajectory.csv", ["step", "time", "x", "y", "theta"], ((i, time[i], *estimate[i]) for i in range(cfg.steps)))
    _write_csv(out / "landmarks.csv", ["id", "x", "y"], ((i, *landmarks[i]) for i in range(len(landmarks))))
    _write_dict_csv(out / "sensor_confidence.csv", conf_rows)
    _write_dict_csv(out / "fusion_weights.csv", weight_rows)
    _write_dict_csv(out / "uncertainty.csv", uncertainty_rows)
    _write_dict_csv(out / "metrics" / "uncertainty.csv", uncertainty_rows)
    _write_dict_csv(out / "degradation_events.csv", events or [{"step": -1, "time": -1.0, "event": "none", "boundary": "none"}])
    _write_dict_csv(out / "rejected_measurements.csv", rejected_rows or [{"step": -1, "time": -1.0, "sensor": "none", "nis": 0.0, "reason": "none"}])
    (out / "sensor_measurements.json").write_text(json.dumps({"label": "Synthetic Demo", "measurements": measurements}, indent=2), encoding="utf-8")
    summary = _summary(cfg, truth, estimate, uncertainty_rows, len(rejected_rows))
    (out / "metrics" / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_dict_csv(out / "metrics" / "metrics.csv", [{"metric": k, "value": v} for k, v in summary.items() if isinstance(v, int | float | str)])
    (out / "mapping_summary.json").write_text(json.dumps({"label": "Synthetic Demo", "landmarks": len(landmarks), "estimated_poses": cfg.steps}, indent=2), encoding="utf-8")
    return {"output_dir": str(out), "summary": summary}


def _truth(t: np.ndarray) -> np.ndarray:
    x = 0.07 * t + 2.2 * np.cos(0.045 * t)
    y = 1.7 * np.sin(0.055 * t) + 0.25 * np.sin(0.13 * t)
    theta = np.unwrap(np.arctan2(np.gradient(y), np.gradient(x)))
    return np.column_stack([x, y, theta])


def _landmarks(rng: np.random.Generator, n: int) -> np.ndarray:
    angles = rng.uniform(0.0, 2.0 * np.pi, n)
    radii = rng.uniform(1.2, 4.5, n)
    return np.column_stack([radii * np.cos(angles) + 4.8, radii * np.sin(angles)])


def _active(cfg: SyntheticSLAMConfig, event: str, step: int) -> bool:
    start, end = cfg.degradation_events.get(event, (-1, -1))
    return start <= step <= end


def _confidence(base: float, effective: float, dropped: bool) -> float:
    if dropped:
        return 0.0
    return float(np.clip(base / max(effective, 1e-9), 0.02, 1.0))


def _conditions(cfg: SyntheticSLAMConfig, step: int, rng: np.random.Generator) -> dict[str, dict[str, Any]]:
    drop = {s: rng.random() < cfg.dropout_probability for s in SENSORS}
    return {
        "camera": {"noise": cfg.noise["camera"] * (4.0 if _active(cfg, "visual_degradation", step) else 1.0), "dropped": drop["camera"], "event": "visual_degradation" if _active(cfg, "visual_degradation", step) else "nominal"},
        "imu": {"noise": cfg.noise["imu"] * (2.5 if _active(cfg, "imu_bias_drift", step) else 1.0), "dropped": drop["imu"], "event": "imu_bias_drift" if _active(cfg, "imu_bias_drift", step) else "nominal"},
        "lidar": {"noise": cfg.noise["lidar"], "dropped": drop["lidar"] or _active(cfg, "lidar_dropout", step), "event": "lidar_dropout" if _active(cfg, "lidar_dropout", step) else "nominal"},
        "rgbd": {"noise": cfg.noise["rgbd"] * (3.5 if _active(cfg, "depth_noise", step) else 1.0), "dropped": drop["rgbd"], "event": "depth_noise" if _active(cfg, "depth_noise", step) else "nominal"},
    }


def _measurement(sensor: str, truth: np.ndarray, prev_truth: np.ndarray, dt: float, cond: dict[str, Any], rng: np.random.Generator, bias: np.ndarray) -> np.ndarray | None:
    if cond["dropped"]:
        return None
    sigma = cond["noise"]
    if sensor == "imu":
        vel = (truth[:2] - prev_truth[:2]) / dt
        return truth + np.r_[0.35 * vel * dt, 0.02] + bias + rng.normal(0.0, sigma, 3)
    offsets = {"camera": np.zeros(3), "lidar": np.array([0.015, -0.01, 0.0]), "rgbd": np.array([-0.01, 0.01, 0.0])}
    return truth + offsets[sensor] + rng.normal(0.0, sigma, 3)


def _summary(cfg: SyntheticSLAMConfig, truth: np.ndarray, estimate: np.ndarray, uncertainty_rows: list[dict[str, float]], rejected: int) -> dict[str, Any]:
    ate = float(np.sqrt(np.mean(np.sum((estimate[:, :2] - truth[:, :2]) ** 2, axis=1))))
    rpe = float(np.sqrt(np.mean(np.sum(np.diff(estimate[:, :2] - truth[:, :2], axis=0) ** 2, axis=1))))
    drift = float(np.linalg.norm((estimate[-1, :2] - estimate[0, :2]) - (truth[-1, :2] - truth[0, :2])))
    return {"label": "Synthetic Demo", "fusion_mode": cfg.fusion_mode, "seed": cfg.seed, "steps": cfg.steps, "ate_rmse": ate, "rpe_rmse": rpe, "trajectory_drift": drift, "mean_nees": float(np.mean([r["nees"] for r in uncertainty_rows])), "mean_nis": float(np.mean([r["nis"] for r in uncertainty_rows])), "tracking_failure_rate": float(sum(r["failure_risk"] > 0.7 for r in uncertainty_rows) / cfg.steps), "rejected_measurements": rejected, "limitations": "Synthetic 2D demo; not a real-world SLAM benchmark."}


def _write_csv(path: Path, header: list[str], rows: Any) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def _write_dict_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    print(json.dumps(run_synthetic_slam()["summary"], indent=2))
