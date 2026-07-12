"""Calibration tools for reliability scores.

Raw reliability is treated as a score, never as a probability, until evaluated or
mapped by a fitted calibrator.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class CalibrationMetrics:
    brier_score: float
    expected_calibration_error: float
    overconfidence: float
    underconfidence: float
    precision: float
    recall: float
    f1: float


def calibration_metrics(
    scores: np.ndarray,
    outcomes: np.ndarray,
    *,
    bins: int = 10,
    threshold: float = 0.5,
) -> CalibrationMetrics:
    """Evaluate calibrated probabilities against binary healthy outcomes."""
    scores = np.asarray(scores, dtype=float).reshape(-1)
    outcomes = np.asarray(outcomes, dtype=float).reshape(-1)
    if scores.shape != outcomes.shape or scores.size == 0:
        raise ValueError("scores and outcomes must be non-empty and equally sized")
    if np.any((scores < 0) | (scores > 1)) or np.any((outcomes != 0) & (outcomes != 1)):
        raise ValueError("scores must be in [0,1] and outcomes binary")
    edges = np.linspace(0.0, 1.0, bins + 1)
    ece = over = under = 0.0
    for index in range(bins):
        upper_closed = index == bins - 1
        mask = (scores >= edges[index]) & (
            (scores <= edges[index + 1]) if upper_closed else (scores < edges[index + 1])
        )
        if not np.any(mask):
            continue
        confidence = float(scores[mask].mean())
        accuracy = float(outcomes[mask].mean())
        weight = float(mask.mean())
        gap = confidence - accuracy
        ece += weight * abs(gap)
        over += weight * max(gap, 0.0)
        under += weight * max(-gap, 0.0)
    predicted = scores >= threshold
    positive = outcomes == 1
    tp = int(np.sum(predicted & positive))
    fp = int(np.sum(predicted & ~positive))
    fn = int(np.sum(~predicted & positive))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return CalibrationMetrics(
        brier_score=float(np.mean((scores - outcomes) ** 2)),
        expected_calibration_error=float(ece),
        overconfidence=float(over),
        underconfidence=float(under),
        precision=float(precision),
        recall=float(recall),
        f1=float(f1),
    )


class MonotonicReliabilityCalibrator:
    """Dependency-light isotonic regression using pair-adjacent violators."""

    def __init__(self) -> None:
        self._x: np.ndarray | None = None
        self._y: np.ndarray | None = None

    def fit(self, scores: np.ndarray, outcomes: np.ndarray) -> MonotonicReliabilityCalibrator:
        scores = np.asarray(scores, dtype=float).reshape(-1)
        outcomes = np.asarray(outcomes, dtype=float).reshape(-1)
        if scores.shape != outcomes.shape or scores.size < 2:
            raise ValueError("at least two paired samples are required")
        order = np.argsort(scores, kind="stable")
        x = scores[order]
        y = outcomes[order]
        values = [float(value) for value in y]
        weights = [1.0] * len(values)
        starts = list(range(len(values)))
        ends = list(range(len(values)))
        index = 0
        while index < len(values) - 1:
            if values[index] <= values[index + 1]:
                index += 1
                continue
            total = weights[index] + weights[index + 1]
            merged = (values[index] * weights[index] + values[index + 1] * weights[index + 1]) / total
            values[index : index + 2] = [merged]
            weights[index : index + 2] = [total]
            ends[index : index + 2] = [ends[index + 1]]
            starts[index : index + 2] = [starts[index]]
            index = max(index - 1, 0)
        fitted = np.empty_like(y)
        for value, start, end in zip(values, starts, ends, strict=True):
            fitted[start : end + 1] = value
        unique_x, inverse = np.unique(x, return_inverse=True)
        unique_y = np.asarray([fitted[inverse == i].mean() for i in range(len(unique_x))])
        self._x = unique_x
        self._y = np.clip(unique_y, 0.0, 1.0)
        return self

    def predict(self, scores: np.ndarray) -> np.ndarray:
        if self._x is None or self._y is None:
            raise RuntimeError("calibrator must be fitted before prediction")
        scores = np.asarray(scores, dtype=float)
        return np.interp(scores, self._x, self._y, left=self._y[0], right=self._y[-1])
