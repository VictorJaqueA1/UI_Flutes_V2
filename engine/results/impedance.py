from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class ImpedanceCurveResult:
    flute_kind: str
    cut_length_mm: float
    frequency_axis_hz: List[float]
    impedance_real: List[float]
    impedance_imag: List[float]
    zc: float
    main_bore: List[List[float | str]]
    holes_valves: List[List[float | str]]
    frequency_axis_rationale: str
    f1_estimate_hz: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
