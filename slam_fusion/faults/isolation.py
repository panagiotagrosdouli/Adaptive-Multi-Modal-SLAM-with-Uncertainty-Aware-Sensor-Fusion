"""Transparent multiple-hypothesis sensor fault isolation."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping
import math

HYPOTHESES=("nominal","noisy","biased","delayed","miscalibrated","failed")

@dataclass(frozen=True)
class FaultDecision:
    suspected_sensor: str
    suspected_fault_type: str
    confidence: float
    supporting_diagnostics: dict[str,float]
    competing_hypotheses: dict[str,float]
    recommended_action: str

class HypothesisIsolator:
    """Combines residual, trend, timing and dropout evidence via softmax scores.

    Scores are normalized evidence, not calibrated probabilities.
    """
    def infer(self, sensor: str, diagnostics: Mapping[str,float]) -> FaultDecision:
        residual=max(float(diagnostics.get("residual_z",0.0)),0.0)
        trend=abs(float(diagnostics.get("residual_trend",0.0)))
        timing=abs(float(diagnostics.get("timing_z",0.0)))
        calibration=abs(float(diagnostics.get("calibration_z",0.0)))
        dropout=min(max(float(diagnostics.get("dropout_rate",0.0)),0.0),1.0)
        variance=max(float(diagnostics.get("variance_ratio",1.0)),0.0)
        scores={
            "nominal":2.0-0.7*residual-2.0*dropout-0.3*trend,
            "noisy":0.8*max(variance-1.0,0.0)+0.25*residual,
            "biased":0.7*residual+0.9*trend-0.2*timing,
            "delayed":1.4*timing+0.2*residual,
            "miscalibrated":1.2*calibration+0.4*residual,
            "failed":3.0*dropout+0.5*residual,
        }
        m=max(scores.values()); ex={k:math.exp(v-m) for k,v in scores.items()}; z=sum(ex.values())
        evidence={k:v/z for k,v in ex.items()}
        ranked=sorted(evidence.items(),key=lambda item:item[1],reverse=True)
        fault,confidence=ranked[0]
        action={"nominal":"continue","noisy":"inflate_covariance","biased":"suppress_and_reestimate_bias","delayed":"freeze_measurements_and_recalibrate_time","miscalibrated":"freeze_and_refine_extrinsics","failed":"isolate_sensor"}[fault]
        return FaultDecision(sensor,fault,confidence,dict(diagnostics),dict(ranked[1:]),action)
