"""Command-line interface for generating experiment plots."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.visualization import generate_all_plots


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Generate plots from an experiment JSON file.")
    parser.add_argument("experiment_json", help="Path to experiment results JSON file.")
    parser.add_argument(
        "--output-dir",
        default="results/plots/manual",
        help="Directory where plots should be written.",
    )
    return parser.parse_args()


def main() -> None:
    """Generate plots from an experiment JSON file."""

    args = parse_args()
    generate_all_plots(Path(args.experiment_json), Path(args.output_dir))
    print(f"Plots written to: {args.output_dir}")


if __name__ == "__main__":
    main()
