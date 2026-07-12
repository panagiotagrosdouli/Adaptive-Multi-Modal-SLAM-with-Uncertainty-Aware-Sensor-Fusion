"""Buffered multi-modal synchronization with explicit health diagnostics.

Status: Implemented research component. LiDAR deskewing remains a scaffold because it
requires per-point timestamps and a motion model supplied by a dataset/front end.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Iterable

import numpy as np

from slam_fusion.sensors.base import SensorMeasurement, SensorModality


@dataclass(slots=True)
class SynchronizationHealth:
    accepted: int = 0
    stale_rejected: int = 0
    out_of_order: int = 0
    missing_modalities: tuple[SensorModality, ...] = ()
    offsets: dict[SensorModality, float] = field(default_factory=dict)
    drift_s_per_s: dict[SensorModality, float] = field(default_factory=dict)


@dataclass(slots=True)
class SynchronizedBundle:
    reference_time: float
    measurements: dict[SensorModality, SensorMeasurement]
    health: SynchronizationHealth


class MeasurementSynchronizer:
    """Timestamp-ordered sensor buffers with exact or approximate matching."""

    def __init__(
        self,
        modalities: Iterable[SensorModality],
        tolerance_s: float = 0.02,
        stale_after_s: float = 0.25,
        max_buffer: int = 2048,
    ) -> None:
        if tolerance_s < 0 or stale_after_s <= 0 or max_buffer < 2:
            raise ValueError("invalid synchronization configuration")
        self.modalities = tuple(dict.fromkeys(modalities))
        self.tolerance_s = float(tolerance_s)
        self.stale_after_s = float(stale_after_s)
        self.buffers: dict[SensorModality, deque[SensorMeasurement]] = {
            modality: deque(maxlen=max_buffer) for modality in self.modalities
        }
        self._last_timestamp: dict[SensorModality, float] = {}
        self._offset_history: dict[SensorModality, deque[tuple[float, float]]] = defaultdict(
            lambda: deque(maxlen=50)
        )
        self._out_of_order = 0
        self._stale_rejected = 0

    def push(self, measurement: SensorMeasurement) -> None:
        measurement.validate()
        if measurement.modality not in self.buffers:
            raise KeyError(f"unregistered modality: {measurement.modality}")
        previous = self._last_timestamp.get(measurement.modality)
        if previous is not None and measurement.timestamp < previous:
            self._out_of_order += 1
        self._last_timestamp[measurement.modality] = max(measurement.timestamp, previous or 0.0)
        buffer = self.buffers[measurement.modality]
        buffer.append(measurement)
        if len(buffer) > 1 and buffer[-2].timestamp > buffer[-1].timestamp:
            ordered = sorted(buffer, key=lambda item: item.timestamp)
            buffer.clear()
            buffer.extend(ordered)

    def synchronize(
        self,
        reference_time: float,
        *,
        exact: bool = False,
        required: Iterable[SensorModality] | None = None,
    ) -> SynchronizedBundle:
        required_set = set(required or self.modalities)
        selected: dict[SensorModality, SensorMeasurement] = {}
        offsets: dict[SensorModality, float] = {}
        for modality, buffer in self.buffers.items():
            while buffer and reference_time - buffer[0].timestamp > self.stale_after_s:
                buffer.popleft()
                self._stale_rejected += 1
            if not buffer:
                continue
            candidate = min(buffer, key=lambda item: abs(item.timestamp - reference_time))
            offset = candidate.timestamp - reference_time
            within_gate = offset == 0.0 if exact else abs(offset) <= self.tolerance_s
            if within_gate:
                selected[modality] = candidate
                offsets[modality] = offset
                self._offset_history[modality].append((reference_time, offset))
        missing = tuple(sorted(required_set - selected.keys(), key=lambda item: item.value))
        health = SynchronizationHealth(
            accepted=len(selected),
            stale_rejected=self._stale_rejected,
            out_of_order=self._out_of_order,
            missing_modalities=missing,
            offsets=offsets,
            drift_s_per_s={m: self._estimate_drift(m) for m in selected},
        )
        return SynchronizedBundle(reference_time, selected, health)

    def interpolate_vector(
        self, modality: SensorModality, timestamp: float
    ) -> SensorMeasurement | None:
        """Linearly interpolate vector-valued packets and covariance."""
        buffer = self.buffers[modality]
        before = [item for item in buffer if item.timestamp <= timestamp]
        after = [item for item in buffer if item.timestamp >= timestamp]
        if not before or not after:
            return None
        left, right = before[-1], after[0]
        if left.timestamp == right.timestamp:
            return left
        left_data = np.asarray(left.data, dtype=float)
        right_data = np.asarray(right.data, dtype=float)
        if left_data.shape != right_data.shape:
            raise ValueError("interpolation requires matching vector shapes")
        alpha = (timestamp - left.timestamp) / (right.timestamp - left.timestamp)
        return SensorMeasurement(
            timestamp=timestamp,
            modality=modality,
            data=(1.0 - alpha) * left_data + alpha * right_data,
            covariance=(1.0 - alpha) * left.covariance + alpha * right.covariance,
            reliability=min(left.reliability, right.reliability),
            metadata={"interpolated": True, "source_times": [left.timestamp, right.timestamp]},
        )

    def _estimate_drift(self, modality: SensorModality) -> float:
        history = self._offset_history[modality]
        if len(history) < 3:
            return 0.0
        times = np.asarray([sample[0] for sample in history], dtype=float)
        offsets = np.asarray([sample[1] for sample in history], dtype=float)
        centered = times - times.mean()
        denominator = float(centered @ centered)
        return 0.0 if denominator < 1e-12 else float(centered @ offsets / denominator)


def lidar_deskew_scaffold(
    points: np.ndarray, point_times: np.ndarray, body_twist: np.ndarray
) -> np.ndarray:
    """First-order constant-twist deskew scaffold for Nx3 point clouds."""
    points = np.asarray(points, dtype=float)
    point_times = np.asarray(point_times, dtype=float)
    body_twist = np.asarray(body_twist, dtype=float)
    if points.ndim != 2 or points.shape[1] != 3 or point_times.shape != (len(points),):
        raise ValueError("expected Nx3 points and N point timestamps")
    if body_twist.shape != (6,):
        raise ValueError("body_twist must contain linear and angular velocity")
    corrected = points.copy()
    corrected -= point_times[:, None] * body_twist[:3]
    return corrected
