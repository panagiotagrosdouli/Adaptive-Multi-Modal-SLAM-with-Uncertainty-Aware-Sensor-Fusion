import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.slam_backend import SlamBackend, SlamObservation, SlamResult
from src.trajectory import load_euroc_ground_truth


@dataclass
class OrbSlam3Config:
    executable: Path
    vocabulary: Path
    settings: Path
    sequence_path: Path
    output_trajectory: Path
    timeout_seconds: Optional[int] = None


class OrbSlam3Backend(SlamBackend):
    """Thin wrapper around an external ORB-SLAM3 executable.

    This backend is intentionally conservative: it does not assume ORB-SLAM3 is
    installed inside this repository. Instead, it validates external paths and
    provides a reproducible command interface for future EuRoC experiments.
    """

    def __init__(self, config: OrbSlam3Config) -> None:
        self.config = config
        self.last_process: Optional[subprocess.CompletedProcess] = None

    def initialize(self) -> None:
        self._validate_paths()

    def _validate_paths(self) -> None:
        required_paths = {
            'executable': self.config.executable,
            'vocabulary': self.config.vocabulary,
            'settings': self.config.settings,
            'sequence_path': self.config.sequence_path,
        }
        for name, path in required_paths.items():
            if not Path(path).exists():
                raise FileNotFoundError(f'ORB-SLAM3 {name} not found: {path}')

    def build_command(self):
        return [
            str(self.config.executable),
            str(self.config.vocabulary),
            str(self.config.settings),
            str(self.config.sequence_path),
            str(self.config.output_trajectory),
        ]

    def run_sequence(self) -> subprocess.CompletedProcess:
        self.initialize()
        self.config.output_trajectory.parent.mkdir(parents=True, exist_ok=True)
        command = self.build_command()
        self.last_process = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=self.config.timeout_seconds,
        )
        return self.last_process

    def load_estimated_trajectory(self):
        if not self.config.output_trajectory.exists():
            return []
        return load_euroc_ground_truth(self.config.output_trajectory)

    def process(self, observation: SlamObservation) -> SlamResult:
        raise NotImplementedError(
            'ORB-SLAM3 is sequence-based in this wrapper. Use run_sequence() for offline experiments.'
        )
