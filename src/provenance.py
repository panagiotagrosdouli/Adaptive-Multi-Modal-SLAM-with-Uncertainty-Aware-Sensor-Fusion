import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ExperimentManifest:
    experiment_name: str
    config_path: str
    created_utc: str
    git_commit: Optional[str]
    outputs: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


def current_git_commit() -> Optional[str]:
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except Exception:
        return None


def create_manifest(
    experiment_name: str,
    config_path: str,
    outputs: Optional[List[str]] = None,
    metadata: Optional[Dict[str, str]] = None,
) -> ExperimentManifest:
    return ExperimentManifest(
        experiment_name=experiment_name,
        config_path=config_path,
        created_utc=datetime.now(timezone.utc).isoformat(),
        git_commit=current_git_commit(),
        outputs=outputs or [],
        metadata=metadata or {},
    )


def save_manifest(manifest: ExperimentManifest, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest.to_dict(), indent=2), encoding='utf-8')


def load_manifest(path: str | Path) -> ExperimentManifest:
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    return ExperimentManifest(**data)
