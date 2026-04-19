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


class FluteGeometryResponse(BaseModel):
    d: float
    x: float
    y: float
    a: float
    Dt: float
    L: float
    Di: float


class VisualizationFluteResponse(BaseModel):
    instrument_id: int
    flute_kind: str
    geometry: FluteGeometryResponse
    curve_points: list[CurvePointResponse]


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


class FluteVisualizationResponse(BaseModel):
    selected_instrument_id: int
    selected_flute_kind: str
    base_flute: VisualizationFluteResponse | None = None
    inverse_flute: VisualizationFluteResponse | None = None
    pairing: PairingSummaryResponse | None = None


class FluteCatalogResponse(BaseModel):
    base_flutes: list[VisualizationFluteResponse]
    inverse_flutes: list[VisualizationFluteResponse]


class RmseRankingItemResponse(BaseModel):
    rank: int
    base_instrument_id: int
    inverse_instrument_id: int
    rmse: float
    anchor_instrument_id: int


class RmseRankingResponse(BaseModel):
    total: int
    pairs: list[RmseRankingItemResponse]
