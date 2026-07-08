"""Generate paper-style benchmark tables from metric JSON files.

The script never invents benchmark values. It only reads committed or generated
metric files and renders Markdown and LaTeX tables from those values.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BenchmarkRow:
    """One benchmark row rendered into paper-style tables."""

    dataset: str
    sequence: str
    backend: str
    alignment: str
    matched_poses: str
    ate_rmse: str
    rpe_rmse: str
    fps: str
    tracking_failures: str
    source: str


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Generate benchmark tables from metric JSON files.")
    parser.add_argument(
        "inputs",
        nargs="+",
        type=Path,
        help="Metric JSON files or directories containing metric JSON files.",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("results/tables"))
    return parser.parse_args()


def discover_json_files(inputs: list[Path]) -> list[Path]:
    """Return JSON metric files from explicit files or directories."""

    files: list[Path] = []
    for item in inputs:
        if item.is_dir():
            files.extend(sorted(item.glob("*.json")))
        elif item.is_file() and item.suffix == ".json":
            files.append(item)
        else:
            raise FileNotFoundError(f"Benchmark input is not a JSON file or directory: {item}")
    if not files:
        raise ValueError("No JSON metric files found.")
    return files


def _format_float(value: Any, digits: int = 4) -> str:
    """Format a numeric metric or return an em dash for missing values."""

    if value is None:
        return "—"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{numeric:.{digits}f}"


def _format_int(value: Any) -> str:
    """Format an integer-like metric or return an em dash for missing values."""

    if value is None:
        return "—"
    try:
        return str(int(value))
    except (TypeError, ValueError):
        return str(value)


def load_benchmark_row(path: Path) -> BenchmarkRow:
    """Load one benchmark row from a metric JSON file."""

    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    metrics = payload.get("metrics", payload)
    metadata = payload.get("metadata", {})
    if "steps" in payload and "metrics" not in payload:
        raise ValueError(
            f"{path} looks like a smoke-experiment log, not a benchmark metric file. "
            "Create benchmark metrics with dataset, sequence, backend, alignment, ATE, and RPE."
        )

    return BenchmarkRow(
        dataset=str(metadata.get("dataset", metrics.get("dataset", "unknown"))),
        sequence=str(metadata.get("sequence", metrics.get("sequence", "unknown"))),
        backend=str(metadata.get("backend", metrics.get("backend", "unknown"))),
        alignment=str(metrics.get("alignment", metadata.get("alignment", "unknown"))),
        matched_poses=_format_int(metrics.get("matched_poses")),
        ate_rmse=_format_float(metrics.get("ate_rmse", metrics.get("ate"))),
        rpe_rmse=_format_float(metrics.get("rpe_rmse", metrics.get("rpe"))),
        fps=_format_float(metrics.get("fps"), digits=2),
        tracking_failures=_format_int(metrics.get("tracking_failures")),
        source=str(path),
    )


def render_markdown(rows: list[BenchmarkRow]) -> str:
    """Render rows as a Markdown table."""

    header = (
        "| Dataset | Sequence | Backend | Align | Matched | ATE RMSE | RPE RMSE | FPS | Failures | Source |\n"
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |"
    )
    body = [
        "| "
        + " | ".join(
            [
                row.dataset,
                row.sequence,
                row.backend,
                row.alignment,
                row.matched_poses,
                row.ate_rmse,
                row.rpe_rmse,
                row.fps,
                row.tracking_failures,
                f"`{row.source}`",
            ]
        )
        + " |"
        for row in rows
    ]
    return "\n".join([header, *body]) + "\n"


def render_latex(rows: list[BenchmarkRow]) -> str:
    """Render rows as a compact LaTeX table."""

    lines = [
        "\\begin{tabular}{llllrrrr}",
        "\\toprule",
        "Dataset & Sequence & Backend & Align & Matched & ATE & RPE & FPS \\\",
        "\\midrule",
    ]
    for row in rows:
        lines.append(
            " & ".join(
                [
                    row.dataset,
                    row.sequence,
                    row.backend,
                    row.alignment,
                    row.matched_poses,
                    row.ate_rmse,
                    row.rpe_rmse,
                    row.fps,
                ]
            )
            + " \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    return "\n".join(lines) + "\n"


def main() -> None:
    """Generate benchmark tables."""

    args = parse_args()
    files = discover_json_files(args.inputs)
    rows = [load_benchmark_row(path) for path in files]
    args.output_dir.mkdir(parents=True, exist_ok=True)

    markdown_path = args.output_dir / "benchmark_table.md"
    latex_path = args.output_dir / "benchmark_table.tex"
    markdown_path.write_text(render_markdown(rows), encoding="utf-8")
    latex_path.write_text(render_latex(rows), encoding="utf-8")

    print(f"Wrote {markdown_path}")
    print(f"Wrote {latex_path}")


if __name__ == "__main__":
    main()
