"""Dependency-light visual frontend with interpretable diagnostics."""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(slots=True)
class VisualFrontendResult:
    points: np.ndarray
    track_ids: np.ndarray
    descriptors: np.ndarray | None
    diagnostics: dict[str, float]
    relative_translation: np.ndarray | None = None


class VisualFrontend:
    """Shi-Tomasi/optical-flow frontend suitable for fixture and dataset runs."""

    def __init__(self, max_features: int = 400, min_features: int = 120, grid: tuple[int, int] = (4, 6)):
        self.max_features = max_features
        self.min_features = min_features
        self.grid = grid
        self._previous_image: np.ndarray | None = None
        self._points = np.empty((0, 2), dtype=np.float32)
        self._ids = np.empty(0, dtype=np.int64)
        self._next_id = 0
        self._orb = cv2.ORB_create(nfeatures=max_features)

    @staticmethod
    def _gray(image: np.ndarray) -> np.ndarray:
        array = np.asarray(image)
        if array.ndim == 3:
            array = cv2.cvtColor(array, cv2.COLOR_BGR2GRAY)
        if array.ndim != 2:
            raise ValueError("image must be grayscale or BGR")
        return np.asarray(array, dtype=np.uint8)

    def _detect_balanced(self, image: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
        rows, cols = self.grid
        height, width = image.shape
        quota = max(1, self.max_features // (rows * cols))
        collected: list[np.ndarray] = []
        for row in range(rows):
            for col in range(cols):
                y0, y1 = row * height // rows, (row + 1) * height // rows
                x0, x1 = col * width // cols, (col + 1) * width // cols
                local_mask = None if mask is None else mask[y0:y1, x0:x1]
                pts = cv2.goodFeaturesToTrack(
                    image[y0:y1, x0:x1], quota, 0.01, 7, mask=local_mask
                )
                if pts is not None:
                    shifted = pts.reshape(-1, 2) + np.array([x0, y0], dtype=np.float32)
                    collected.append(shifted)
        return np.vstack(collected).astype(np.float32) if collected else np.empty((0, 2), np.float32)

    def process(self, image: np.ndarray, camera_matrix: np.ndarray | None = None) -> VisualFrontendResult:
        current = self._gray(image)
        previous_count = len(self._points)
        flow_error = np.empty(0, dtype=float)
        tracked_previous = np.empty((0, 2), dtype=np.float32)
        tracked_current = np.empty((0, 2), dtype=np.float32)
        tracked_ids = np.empty(0, dtype=np.int64)

        if self._previous_image is not None and previous_count:
            nxt, status, error = cv2.calcOpticalFlowPyrLK(
                self._previous_image, current, self._points.reshape(-1, 1, 2), None
            )
            back, back_status, _ = cv2.calcOpticalFlowPyrLK(
                current, self._previous_image, nxt, None
            )
            fb = np.linalg.norm(back.reshape(-1, 2) - self._points, axis=1)
            valid = (status.ravel() == 1) & (back_status.ravel() == 1) & (fb < 1.5)
            tracked_previous = self._points[valid]
            tracked_current = nxt.reshape(-1, 2)[valid]
            tracked_ids = self._ids[valid]
            flow_error = error.ravel()[valid]

            if len(tracked_current) >= 8:
                _, ransac = cv2.findFundamentalMat(
                    tracked_previous, tracked_current, cv2.FM_RANSAC, 1.5, 0.99
                )
                if ransac is not None:
                    inlier = ransac.ravel().astype(bool)
                    tracked_previous = tracked_previous[inlier]
                    tracked_current = tracked_current[inlier]
                    tracked_ids = tracked_ids[inlier]
                    flow_error = flow_error[inlier]

        points, ids = tracked_current, tracked_ids
        if len(points) < self.min_features:
            mask = np.full(current.shape, 255, dtype=np.uint8)
            for point in points.astype(int):
                cv2.circle(mask, tuple(point), 8, 0, -1)
            new_points = self._detect_balanced(current, mask)
            room = max(0, self.max_features - len(points))
            new_points = new_points[:room]
            new_ids = np.arange(self._next_id, self._next_id + len(new_points), dtype=np.int64)
            self._next_id += len(new_points)
            points = np.vstack([points, new_points]) if len(points) else new_points
            ids = np.concatenate([ids, new_ids])

        keypoints = [cv2.KeyPoint(float(x), float(y), 15) for x, y in points]
        keypoints, descriptors = self._orb.compute(current, keypoints)
        if keypoints:
            descriptor_points = np.array([kp.pt for kp in keypoints], dtype=np.float32)
        else:
            descriptor_points = points

        brightness = float(np.mean(current) / 255.0)
        contrast = float(np.std(current) / 255.0)
        sharpness = float(cv2.Laplacian(current, cv2.CV_64F).var())
        survival = float(len(tracked_current) / max(previous_count, 1))
        parallax = (
            float(np.median(np.linalg.norm(tracked_current - tracked_previous, axis=1)))
            if len(tracked_current)
            else 0.0
        )
        diagnostics = {
            "feature_count": float(len(points)),
            "track_survival": survival,
            "brightness": brightness,
            "contrast": contrast,
            "blur_variance": sharpness,
            "flow_error": float(np.mean(flow_error)) if len(flow_error) else 0.0,
            "parallax_pixels": parallax,
            "outlier_ratio": 1.0 - len(tracked_current) / max(previous_count, 1),
        }
        self._previous_image = current
        self._points = points.astype(np.float32)
        self._ids = ids
        return VisualFrontendResult(descriptor_points, ids, descriptors, diagnostics)
