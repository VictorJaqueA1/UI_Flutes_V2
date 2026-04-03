from __future__ import annotations

from pydantic import BaseModel, Field


class FluteComputeRequest(BaseModel):
    kind: str = Field(description="Tipo de flauta: base o inverse.")
    d: float
    x: float
    y: float
    a: float
    Dt: float
    L: float = 570.0
    Di: float = 18.0


class CurvePointResponse(BaseModel):
    cut_index: int
    cut_length_mm: float
    f1_hz: float
    f2_hz: float
    delta_cents: float


class PairingSummaryResponse(BaseModel):
    related_instrument_id: int
    rmse: float
    selected_at: str


class FluteComputeResponse(BaseModel):
    instrument_id: int
    run_id: int
    flute_kind: str
    pairings_updated: int
    curve_points: list[CurvePointResponse]
    best_pairing: PairingSummaryResponse | None = None


class StoredCurveResponse(BaseModel):
    instrument_id: int
    flute_kind: str
    curve_points: list[CurvePointResponse]
    best_pairing: PairingSummaryResponse | None = None
