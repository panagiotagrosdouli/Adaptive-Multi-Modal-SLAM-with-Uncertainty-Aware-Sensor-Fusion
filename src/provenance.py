"""Experiment provenance and manifest utilities."""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class ExperimentManifest:
    """Reproducibility manifest for one experiment run."""

    experiment_name: str
    config_path: str
    created_utc: str
    git_commit: str | None
    outputs: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        """Convert the manifest to a JSON-serializable dictionary."""

        return asdict(self)


def current_git_commit() -> str | None:
    """Return the current Git commit SHA when the repository is available."""

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def create_manifest(
    experiment_name: str,
    config_path: str,
    outputs: list[str] | None = None,
    metadata: dict[str, str] | None = None,
) -> ExperimentManifest:
    """Create an experiment manifest."""

    return ExperimentManifest(
        experiment_name=experiment_name,
        config_path=config_path,
        created_utc=datetime.now(timezone.utc).isoformat(),
        git_commit=current_git_commit(),
        outputs=outputs or [],
        metadata=metadata or {},
    )


def save_manifest(manifest: ExperimentManifest, path: str | Path) -> None:
    """Save a manifest to disk."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")


def load_manifest(path: str | Path) -> ExperimentManifest:
    """Load a manifest from disk."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return ExperimentManifest(**data)
