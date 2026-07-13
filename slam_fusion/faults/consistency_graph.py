"""Cross-modal consistency graph for transparent fault attribution."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ConsistencyState(str, Enum):
    CONSISTENT = "CONSISTENT"
    SUSPECT = "SUSPECT"
    INCONSISTENT = "INCONSISTENT"


@dataclass(frozen=True, slots=True)
class ConsistencyEdge:
    source: str
    target: str
    residual: float
    uncertainty: float
    confidence: float
    state: ConsistencyState
    trend: float


@dataclass
class CrossModalConsistencyGraph:
    suspect_z: float = 2.0
    inconsistent_z: float = 3.5
    _edges: dict[tuple[str, str], ConsistencyEdge] = field(default_factory=dict, init=False)

    def update(
        self,
        source: str,
        target: str,
        residual: float,
        uncertainty: float,
        trend: float = 0.0,
    ) -> ConsistencyEdge:
        if source == target:
            raise ValueError("consistency edges require distinct modalities")
        if uncertainty <= 0.0:
            raise ValueError("uncertainty must be positive")
        z_score = abs(float(residual)) / float(uncertainty)
        if z_score >= self.inconsistent_z:
            state = ConsistencyState.INCONSISTENT
        elif z_score >= self.suspect_z:
            state = ConsistencyState.SUSPECT
        else:
            state = ConsistencyState.CONSISTENT
        confidence = max(0.0, min(1.0, 1.0 - z_score / (2.0 * self.inconsistent_z)))
        edge = ConsistencyEdge(
            source=source,
            target=target,
            residual=float(residual),
            uncertainty=float(uncertainty),
            confidence=confidence,
            state=state,
            trend=float(trend),
        )
        self._edges[tuple(sorted((source, target)))] = edge
        return edge

    def suspect_sensor(self) -> tuple[str | None, dict[str, float]]:
        """Return the modality with strongest incident contradiction evidence."""
        evidence: dict[str, float] = {}
        for edge in self._edges.values():
            severity = 1.0 - edge.confidence
            if edge.state is ConsistencyState.SUSPECT:
                severity *= 1.25
            elif edge.state is ConsistencyState.INCONSISTENT:
                severity *= 2.0
            evidence[edge.source] = evidence.get(edge.source, 0.0) + severity
            evidence[edge.target] = evidence.get(edge.target, 0.0) + severity
        if not evidence:
            return None, {}
        ranked = dict(sorted(evidence.items(), key=lambda item: item[1], reverse=True))
        return next(iter(ranked)), ranked

    @property
    def edges(self) -> tuple[ConsistencyEdge, ...]:
        return tuple(self._edges.values())
