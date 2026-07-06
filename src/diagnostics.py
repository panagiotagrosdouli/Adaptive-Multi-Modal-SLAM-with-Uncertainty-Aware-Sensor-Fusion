import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List


@dataclass
class DiagnosticEvent:
    step: int
    timestamp: float
    state: str
    health_level: str
    health_score: float
    recovery_action: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DiagnosticsLogger:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write_event(self, event: DiagnosticEvent) -> None:
        with self.path.open('a', encoding='utf-8') as file:
            file.write(json.dumps(event.to_dict()) + '\n')


def load_diagnostic_events(path: str | Path) -> List[DiagnosticEvent]:
    events = []
    path = Path(path)
    if not path.exists():
        return events

    with path.open('r', encoding='utf-8') as file:
        for line in file:
            if not line.strip():
                continue
            events.append(DiagnosticEvent(**json.loads(line)))
    return events


def summarize_diagnostics(events: Iterable[DiagnosticEvent]) -> Dict[str, Any]:
    events = list(events)
    if not events:
        return {
            'num_events': 0,
            'num_warnings': 0,
            'num_critical': 0,
            'num_recovery_actions': 0,
        }

    return {
        'num_events': len(events),
        'num_warnings': sum(event.health_level == 'warning' for event in events),
        'num_critical': sum(event.health_level == 'critical' for event in events),
        'num_recovery_actions': sum(event.state == 'recovery' for event in events),
    }
