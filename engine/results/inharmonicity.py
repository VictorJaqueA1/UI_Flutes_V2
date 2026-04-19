from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class InharmonicityPoint:
    cut_length_mm: float
    f1_hint_hz: float
    f1_hz: float
    f2_hz: float
    delta_cents: float
    f1_window_hz: tuple[float, float]
    f2_window_hz: tuple[float, float]


@dataclass(frozen=True)
class InharmonicityCurveResult:
    flute_kind: str
    input_geometry: Dict[str, float | str]
    frequency_axis_min_hz: float
    frequency_axis_max_hz: float
    frequency_axis_step_hz: float
    frequency_axis_rationale: str
    points: List[InharmonicityPoint]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
