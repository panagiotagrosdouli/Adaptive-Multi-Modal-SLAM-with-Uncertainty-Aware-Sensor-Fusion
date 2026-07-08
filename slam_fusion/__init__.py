"""Adaptive Multi-Modal SLAM with uncertainty-aware sensor fusion.

The package separates implemented research utilities from prototype scaffolds.
Implemented modules are deterministic and covered by tests. Prototype modules expose
interfaces for future ROS2 and benchmark integration without claiming benchmark results.
"""

from slam_fusion.core.state import RobotState
from slam_fusion.fusion.adaptive import AdaptiveFusionConfig, AdaptiveSensorFusion
from slam_fusion.uncertainty.metrics import nees, nis

__all__ = [
    "AdaptiveFusionConfig",
    "AdaptiveSensorFusion",
    "RobotState",
    "nees",
    "nis",
]
