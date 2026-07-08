"""Dataset manifest utilities.

The project never redistributes benchmark datasets. Manifests describe local
paths, sequence identifiers, expected modalities, and citation/licensing notes
so that experiments can be reproduced without committing dataset bytes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True, slots=True)
class DatasetManifest:
    """Metadata required to run a dataset-backed experiment."""

    name: str
    sequence: str
    root: Path
    modalities: tuple[str, ...]
    citation: str
    license_note: str
    status: str = "Pending"

    def validate(self) -> list[str]:
        """Return validation errors without touching dataset contents deeply."""

        errors: list[str] = []
        if not self.name:
            errors.append("dataset name is required")
        if not self.sequence:
            errors.append("sequence is required")
        if not self.modalities:
            errors.append("at least one modality is required")
        if not self.citation:
            errors.append("dataset citation note is required")
        if not self.license_note:
            errors.append("dataset license note is required")
        if not self.root.exists():
            errors.append(f"dataset root does not exist: {self.root}")
        return errors


def load_manifest(path: str | Path) -> DatasetManifest:
    """Load a YAML dataset manifest."""

    data: dict[str, Any] = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return DatasetManifest(
        name=str(data["name"]),
        sequence=str(data["sequence"]),
        root=Path(data["root"]),
        modalities=tuple(str(item) for item in data.get("modalities", ())),
        citation=str(data.get("citation", "")),
        license_note=str(data.get("license_note", "")),
        status=str(data.get("status", "Pending")),
    )


def write_manifest_template(path: str | Path, *, dataset: str, sequence: str) -> None:
    """Write a conservative manifest template for a local benchmark sequence."""

    template = {
        "name": dataset,
        "sequence": sequence,
        "root": f"/absolute/path/to/{dataset}/{sequence}",
        "modalities": ["camera", "imu"],
        "citation": "Add the official dataset citation before publishing results.",
        "license_note": "Do not redistribute dataset files; follow the official dataset license.",
        "status": "Pending",
    }
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(yaml.safe_dump(template, sort_keys=False), encoding="utf-8")
