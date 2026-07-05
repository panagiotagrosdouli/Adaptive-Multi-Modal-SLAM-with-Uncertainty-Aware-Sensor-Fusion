import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class EurocImageFrame:
    timestamp_ns: int
    path: Path

    @property
    def timestamp_s(self) -> float:
        return self.timestamp_ns * 1e-9


@dataclass
class EurocImuMeasurement:
    timestamp_ns: int
    gyro_x: float
    gyro_y: float
    gyro_z: float
    accel_x: float
    accel_y: float
    accel_z: float

    @property
    def timestamp_s(self) -> float:
        return self.timestamp_ns * 1e-9


class EurocDataset:
    def __init__(self, root):
        self.root = Path(root)
        self.cam0 = self.root / 'mav0' / 'cam0' / 'data'
        self.cam1 = self.root / 'mav0' / 'cam1' / 'data'
        self.imu = self.root / 'mav0' / 'imu0'
        self.imu_csv = self.imu / 'data.csv'

    def image_files(self):
        return sorted(self.cam0.glob('*.png'))

    def image_frames(self) -> List[EurocImageFrame]:
        frames = []
        for image_path in self.image_files():
            try:
                timestamp_ns = int(image_path.stem)
            except ValueError:
                continue
            frames.append(EurocImageFrame(timestamp_ns=timestamp_ns, path=image_path))
        return frames

    def imu_measurements(self) -> List[EurocImuMeasurement]:
        if not self.imu_csv.exists():
            return []

        measurements = []
        with self.imu_csv.open('r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if not row or row[0].startswith('#'):
                    continue
                measurements.append(
                    EurocImuMeasurement(
                        timestamp_ns=int(row[0]),
                        gyro_x=float(row[1]),
                        gyro_y=float(row[2]),
                        gyro_z=float(row[3]),
                        accel_x=float(row[4]),
                        accel_y=float(row[5]),
                        accel_z=float(row[6]),
                    )
                )
        return measurements

    def summary(self):
        return {
            'root': str(self.root),
            'num_cam0_images': len(self.image_files()),
            'num_imu_measurements': len(self.imu_measurements()),
        }

    def __len__(self):
        return len(self.image_files())
