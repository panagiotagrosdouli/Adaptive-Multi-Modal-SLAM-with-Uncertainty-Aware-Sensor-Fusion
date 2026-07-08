"""Frontend quality signals for visual SLAM experiments."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class VisualQuality:
    """Interpretable visual frontend health metrics."""

    feature_count: int
    inlier_ratio: float
    mean_reprojection_error: float
    brightness: float
    sharpness: float

    def reliability(self, target_features: int = 200) -> float:
        """Convert quality terms to a bounded reliability heuristic."""

        feature_score = min(1.0, max(0.0, self.feature_count / max(target_features, 1)))
        inlier_score = min(1.0, max(0.0, self.inlier_ratio))
        reproj_score = float(np.exp(-max(0.0, self.mean_reprojection_error) / 3.0))
        brightness_score = float(np.exp(-abs(self.brightness - 0.5) / 0.35))
        sharpness_score = min(1.0, max(0.0, self.sharpness))
        return float(np.clip(np.mean([feature_score, inlier_score, reproj_score, brightness_score, sharpness_score]), 0.0, 1.0))


def detect_feature_dropout(feature_counts: np.ndarray, threshold_fraction: float = 0.35) -> np.ndarray:
    """Detect abrupt feature depletion relative to the running median."""

    counts = np.asarray(feature_counts, dtype=float)
    if counts.ndim != 1:
        raise ValueError("feature_counts must be a 1D array")
    if not 0.0 < threshold_fraction <= 1.0:
        raise ValueError("threshold_fraction must be in (0, 1]")
    median = np.maximum(1.0, np.median(counts))
    return counts < threshold_fraction * median
