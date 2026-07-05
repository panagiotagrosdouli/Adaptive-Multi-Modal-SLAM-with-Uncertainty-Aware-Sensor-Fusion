import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass
class TrajectoryPose:
    timestamp_ns: int
    tx: float
    ty: float
    tz: float
    qx: float
    qy: float
    qz: float
    qw: float

    @property
    def timestamp_s(self) -> float:
        return self.timestamp_ns * 1e-9

    def as_tum_line(self) -> str:
        return (
            f'{self.timestamp_s:.9f} {self.tx:.9f} {self.ty:.9f} {self.tz:.9f} '
            f'{self.qx:.9f} {self.qy:.9f} {self.qz:.9f} {self.qw:.9f}'
        )


def load_euroc_ground_truth(path: str | Path) -> List[TrajectoryPose]:
    path = Path(path)
    poses = []
    with path.open('r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if not row or row[0].startswith('#'):
                continue
            poses.append(
                TrajectoryPose(
                    timestamp_ns=int(row[0]),
                    tx=float(row[1]),
                    ty=float(row[2]),
                    tz=float(row[3]),
                    qw=float(row[4]),
                    qx=float(row[5]),
                    qy=float(row[6]),
                    qz=float(row[7]),
                )
            )
    return poses


def save_tum_trajectory(poses: Iterable[TrajectoryPose], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as file:
        for pose in poses:
            file.write(pose.as_tum_line() + '\n')
