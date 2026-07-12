"""Public-dataset metadata adapters.

These adapters validate canonical exported layouts and yield timestamped records.
They do not download or redistribute datasets and are not complete SLAM systems.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass(frozen=True, slots=True)
class DatasetRecord:
    timestamp: float
    modality: str
    path: Path | None
    values: tuple[float, ...] = ()


class DatasetLayoutError(RuntimeError):
    pass


def _rows(path: Path) -> Iterator[list[str]]:
    if not path.is_file():
        raise DatasetLayoutError(f"missing required file: {path}")
    with path.open("r", encoding="utf-8") as stream:
        for row in csv.reader(line for line in stream if line.strip() and not line.startswith("#")):
            yield [item.strip() for item in row]


class EurocAdapter:
    """Read EuRoC MAV camera and IMU CSV exports."""

    def __init__(self, root: str | Path):
        self.root = Path(root)

    def records(self) -> Iterator[DatasetRecord]:
        camera_dir = self.root / "mav0" / "cam0"
        for row in _rows(camera_dir / "data.csv"):
            timestamp_ns, filename = row[:2]
            yield DatasetRecord(float(timestamp_ns) * 1e-9, "camera", camera_dir / "data" / filename)
        for row in _rows(self.root / "mav0" / "imu0" / "data.csv"):
            values = tuple(float(value) for value in row[1:7])
            yield DatasetRecord(float(row[0]) * 1e-9, "imu", None, values)


class TumRgbdAdapter:
    """Read TUM RGB-D association files."""

    def __init__(self, root: str | Path, association_file: str = "associations.txt"):
        self.root = Path(root)
        self.association_file = association_file

    def records(self) -> Iterator[DatasetRecord]:
        path = self.root / self.association_file
        if not path.is_file():
            raise DatasetLayoutError(f"missing required file: {path}")
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            rgb_time, rgb_path, depth_time, depth_path = line.split()[:4]
            yield DatasetRecord(float(rgb_time), "camera", self.root / rgb_path)
            yield DatasetRecord(float(depth_time), "rgbd", self.root / depth_path)


class KittiOdometryAdapter:
    """Read KITTI odometry image and timestamp exports."""

    def __init__(self, root: str | Path, sequence: str):
        self.root = Path(root)
        self.sequence = sequence

    def records(self) -> Iterator[DatasetRecord]:
        sequence_dir = self.root / "sequences" / self.sequence
        times = sequence_dir / "times.txt"
        image_dir = sequence_dir / "image_0"
        if not times.is_file() or not image_dir.is_dir():
            raise DatasetLayoutError(f"invalid KITTI sequence layout: {sequence_dir}")
        for index, line in enumerate(times.read_text(encoding="utf-8").splitlines()):
            yield DatasetRecord(float(line), "camera", image_dir / f"{index:06d}.png")


def merge_chronologically(*streams: Iterator[DatasetRecord]) -> list[DatasetRecord]:
    """Materialize fixture-scale streams in timestamp order."""
    records = [record for stream in streams for record in stream]
    return sorted(records, key=lambda record: record.timestamp)
