from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FluteKind(str, Enum):
    BASE = "base"
    INVERSE = "inverse"


@dataclass(frozen=True)
class FluteGeometry:
    kind: FluteKind
    d: float
    x: float
    y: float
    a: float
    Dt: float
    L: float = 570.0
    Di: float = 18.0


@dataclass(frozen=True)
class CutRequest:
    length_mm: float


@dataclass(frozen=True)
class OpenWindOptions:
    temperature_c: float = 25.0
    humidity: float = 0.50
    unit: str = "mm"
    diameter: bool = True
    source_location: str = "embouchure"
    radiation_category: str = "unflanged"
    losses: bool = True
    compute_method: str = "FEM"
