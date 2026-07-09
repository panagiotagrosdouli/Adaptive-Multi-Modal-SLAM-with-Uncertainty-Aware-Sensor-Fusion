"""Run only the synthetic SLAM simulation and metrics export."""
from __future__ import annotations

from slam_fusion.simulation.synthetic_slam import run_synthetic_slam

if __name__ == "__main__":
    print(run_synthetic_slam())
