from __future__ import annotations

from fastapi import APIRouter

from backend.schemas.flutes import (
    FluteCatalogResponse,
    FluteComputeRequest,
    FluteComputeResponse,
    RmseRankingResponse,
    StoredCurveResponse,
    FluteVisualizationResponse,
)
from backend.services.flutes import (
    compute_flute_and_build_response,
    get_catalog_response,
    get_rmse_ranking_response,
    get_stored_curve_response,
    get_visualization_response,
)


router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/flutes", response_model=FluteComputeResponse)
def compute_flute(request: FluteComputeRequest) -> FluteComputeResponse:
    return compute_flute_and_build_response(request)


@router.get("/flutes/catalog", response_model=FluteCatalogResponse)
def get_catalog() -> FluteCatalogResponse:
    return get_catalog_response()


@router.get("/flutes/rmse-ranking", response_model=RmseRankingResponse)
def get_rmse_ranking() -> RmseRankingResponse:
    return get_rmse_ranking_response()


@router.get("/flutes/{instrument_id}/curve", response_model=StoredCurveResponse)
def get_curve(instrument_id: int) -> StoredCurveResponse:
    return get_stored_curve_response(instrument_id)


@router.get("/flutes/{instrument_id}/visualization", response_model=FluteVisualizationResponse)
def get_visualization(instrument_id: int) -> FluteVisualizationResponse:
    return get_visualization_response(instrument_id)
