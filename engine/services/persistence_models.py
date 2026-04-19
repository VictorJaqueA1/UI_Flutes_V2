from __future__ import annotations

from dataclasses import dataclass

from engine.results import ImpedanceCurveResult, InharmonicityCurveResult


@dataclass(frozen=True)
class CutComputationRecord:
    cut_index: int
    impedance: ImpedanceCurveResult
    f1_hz: float
    f2_hz: float
    delta_cents: float
    resonance_frequencies_hz: list[float]


@dataclass(frozen=True)
class FluteComputationBundle:
    curve: InharmonicityCurveResult
    cut_records: list[CutComputationRecord]


@dataclass(frozen=True)
class PersistedFluteResult:
    instrument_id: int
    run_id: int
    flute_kind: str
    pairings_updated: int
