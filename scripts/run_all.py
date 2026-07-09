"""Run the complete Synthetic Demo pipeline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.generate_figures import generate_figures
from scripts.make_demo_gif import make_demo_gif
from slam_fusion.simulation.synthetic_slam import SyntheticSLAMConfig, run_synthetic_slam


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Synthetic Demo end-to-end.")
    parser.add_argument("--output-dir", default="results")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--steps", type=int, default=160)
    parser.add_argument("--fusion-mode", choices=["adaptive", "fixed"], default="adaptive")
    args = parser.parse_args()
    cfg = SyntheticSLAMConfig(seed=args.seed, steps=args.steps, output_dir=Path(args.output_dir), fusion_mode=args.fusion_mode)
    result = run_synthetic_slam(cfg)
    generate_figures(args.output_dir, "assets/figures")
    media = make_demo_gif(args.output_dir, "assets")
    reports = Path(args.output_dir) / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "synthetic_demo_report.md").write_text(
        "# Synthetic Demo Report\n\n"
        "All metrics and media in this report are generated from the deterministic synthetic simulator.\n\n"
        f"```json\n{json.dumps(result['summary'], indent=2)}\n```\n\n"
        f"Media: `{media['gif']}`, `{media['mp4']}`\n",
        encoding="utf-8",
    )
    print(json.dumps({"summary": result["summary"], "media": media}, indent=2))


if __name__ == "__main__":
    main()
