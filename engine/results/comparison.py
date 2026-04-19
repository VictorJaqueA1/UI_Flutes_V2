from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class ResonanceMethodComparisonPoint:
    cut_length_mm: float
    manual_f1_hz: float
    manual_f2_hz: float
    manual_delta_cents: float
    openwind_f1_hz: float | None
    openwind_f2_hz: float | None
    openwind_delta_cents: float | None
    difference_f1_hz: float | None
    difference_f2_hz: float | None
    difference_delta_cents: float | None


@dataclass(frozen=True)
class ResonanceMethodComparisonResult:
    flute_kind: str
    input_geometry: Dict[str, float | str]
    points: List[ResonanceMethodComparisonPoint]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
