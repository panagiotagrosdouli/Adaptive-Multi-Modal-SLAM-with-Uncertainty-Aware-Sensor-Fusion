"""Run all repository phases required for research-grade validation.

This script is intentionally strict for phases that are executable without
external datasets. Dataset-heavy phases are represented by explicit checks and
clear skip reasons rather than fake benchmark results.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class PhaseResult:
    """Result for one validation phase."""

    name: str
    status: str
    command: str
    reason: str = ""


class PhaseFailure(RuntimeError):
    """Raised when a required phase fails."""


def run_command(command: list[str], *, required: bool = True) -> PhaseResult:
    """Run a command and return a phase result."""

    printable = " ".join(command)
    completed = subprocess.run(command, check=False, text=True)
    if completed.returncode == 0:
        return PhaseResult(name=command[0], status="passed", command=printable)
    if required:
        raise PhaseFailure(f"Required phase failed: {printable}")
    return PhaseResult(
        name=command[0],
        status="skipped_or_failed_optional",
        command=printable,
        reason=f"exit code {completed.returncode}",
    )


def assert_exists(path: Path, *, label: str) -> PhaseResult:
    """Validate that an expected artifact exists."""

    if not path.exists():
        raise PhaseFailure(f"Missing expected {label}: {path}")
    return PhaseResult(name=label, status="passed", command=f"test -e {path}")


def validate_experiment_json(path: Path) -> PhaseResult:
    """Validate the smoke experiment output schema."""

    if not path.exists():
        raise PhaseFailure(f"Experiment output missing: {path}")
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    steps = payload.get("steps")
    if not isinstance(steps, list) or len(steps) == 0:
        raise PhaseFailure("Experiment JSON must contain a non-empty 'steps' list.")
    required_keys = {
        "step",
        "timestamp",
        "position",
        "visual_reliability",
        "inertial_reliability",
        "visual_weight",
        "inertial_weight",
        "failure_probability",
    }
    missing = required_keys.difference(steps[0])
    if missing:
        raise PhaseFailure(f"Experiment step is missing keys: {sorted(missing)}")
    return PhaseResult(name="experiment_json_schema", status="passed", command=str(path))


def dataset_phase(dataset_root: Path) -> PhaseResult:
    """Report whether external dataset-backed benchmarks can be executed."""

    if dataset_root.exists():
        return PhaseResult(
            name="external_dataset_available",
            status="passed",
            command=f"test -d {dataset_root}",
        )
    return PhaseResult(
        name="external_dataset_benchmark",
        status="skipped_with_reason",
        command=f"test -d {dataset_root}",
        reason="External datasets are not committed. Run EuRoC/KITTI/TUM benchmarks after downloading datasets and configuring paths.",
    )


def write_report(results: list[PhaseResult], output_path: Path) -> None:
    """Write a machine-readable phase report."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "passed": [asdict(result) for result in results if result.status == "passed"],
        "skipped": [asdict(result) for result in results if result.status != "passed"],
        "all_required_phases_passed": True,
    }
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description="Run all executable validation phases.")
    parser.add_argument("--config", default="configs/example_experiment.yaml")
    parser.add_argument("--dataset-root", default="data")
    parser.add_argument("--skip-lint", action="store_true")
    parser.add_argument("--skip-media", action="store_true")
    return parser.parse_args()


def main() -> None:
    """Run all executable phases."""

    args = parse_args()
    results: list[PhaseResult] = []

    if not args.skip_lint:
        if shutil.which("ruff"):
            results.append(run_command(["ruff", "check", "src", "tests", "scripts"]))
        else:
            results.append(
                PhaseResult(
                    name="ruff",
                    status="skipped_with_reason",
                    command="ruff check src tests scripts",
                    reason="Ruff is not installed in this environment.",
                )
            )
        if shutil.which("black"):
            results.append(run_command(["black", "--check", "src", "tests", "scripts"]))
        else:
            results.append(
                PhaseResult(
                    name="black",
                    status="skipped_with_reason",
                    command="black --check src tests scripts",
                    reason="Black is not installed in this environment.",
                )
            )

    results.append(run_command([sys.executable, "-m", "pytest", "-q"]))
    results.append(run_command([sys.executable, "run_experiment.py", "--config", args.config]))

    result_json = Path("results") / "euroc_degraded_adaptive_fusion_baseline.json"
    results.append(validate_experiment_json(result_json))
    results.append(assert_exists(Path("results/plots/euroc_degraded_adaptive_fusion_baseline/failure_probability.png"), label="failure_probability_plot"))
    results.append(assert_exists(Path("results/plots/euroc_degraded_adaptive_fusion_baseline/reliability.png"), label="reliability_plot"))
    results.append(assert_exists(Path("results/plots/euroc_degraded_adaptive_fusion_baseline/fusion_weights.png"), label="fusion_weights_plot"))
    results.append(assert_exists(Path("results/manifests/euroc_degraded_adaptive_fusion_baseline_manifest.json"), label="experiment_manifest"))

    if not args.skip_media:
        results.append(
            run_command(
                [
                    sys.executable,
                    "scripts/generate_research_media.py",
                    str(result_json),
                    "--output-dir",
                    "results/videos",
                ],
                required=True,
            )
        )
        results.append(assert_exists(Path("results/videos/euroc_degraded_adaptive_fusion_baseline_trajectory.svg"), label="trajectory_svg"))

    results.append(dataset_phase(Path(args.dataset_root)))

    report_path = Path("results/phase_report.json")
    write_report(results, report_path)
    print(f"All required executable phases passed. Report: {report_path}")


if __name__ == "__main__":
    main()
