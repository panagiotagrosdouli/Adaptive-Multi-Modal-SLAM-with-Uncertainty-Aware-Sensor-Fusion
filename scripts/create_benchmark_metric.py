"""Create benchmark metric JSON files with the repository schema.

This utility is useful after a real backend run has produced ATE/RPE values. It
records the metric numbers together with the metadata needed to interpret them.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

VALID_ALIGNMENTS = {"none", "se3", "sim3"}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Create a benchmark metric JSON file.")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--sequence", required=True)
    parser.add_argument("--backend", required=True)
    parser.add_argument("--sensor-setup", required=True)
    parser.add_argument("--alignment", required=True, choices=sorted(VALID_ALIGNMENTS))
    parser.add_argument("--matched-poses", required=True, type=int)
    parser.add_argument("--ate-rmse", required=True, type=float)
    parser.add_argument("--rpe-rmse", required=True, type=float)
    parser.add_argument("--tracking-failures", required=True, type=int)
    parser.add_argument("--fps", type=float, default=None)
    parser.add_argument("--command", default="")
    parser.add_argument("--notes", default="")
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    """Create a benchmark metric JSON file."""

    args = parse_args()
    if args.matched_poses <= 0:
        raise ValueError("matched-poses must be positive for a reportable benchmark.")
    if args.ate_rmse < 0.0 or args.rpe_rmse < 0.0:
        raise ValueError("ATE/RPE RMSE values must be non-negative.")
    if args.tracking_failures < 0:
        raise ValueError("tracking-failures must be non-negative.")
    if args.fps is not None and args.fps < 0.0:
        raise ValueError("fps must be non-negative when provided.")

    payload = {
        "metadata": {
            "dataset": args.dataset,
            "sequence": args.sequence,
            "backend": args.backend,
            "sensor_setup": args.sensor_setup,
            "alignment": args.alignment,
            "command": args.command,
            "notes": args.notes,
        },
        "metrics": {
            "matched_poses": args.matched_poses,
            "ate_rmse": args.ate_rmse,
            "rpe_rmse": args.rpe_rmse,
            "tracking_failures": args.tracking_failures,
            "alignment": args.alignment,
        },
    }
    if args.fps is not None:
        payload["metrics"]["fps"] = args.fps

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
