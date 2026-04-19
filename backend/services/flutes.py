from __future__ import annotations

from fastapi import HTTPException

from db.platform.repositories import PlatformDatabase
from engine.models import FluteGeometry, FluteKind
from engine.services import build_modal_public_options, compute_and_store_flute

from backend.schemas.flutes import (
    FluteCatalogResponse,
    CurvePointResponse,
    FluteComputeRequest,
    FluteComputeResponse,
    FluteGeometryResponse,
    FluteVisualizationResponse,
    PairingSummaryResponse,
    RmseRankingItemResponse,
    RmseRankingResponse,
    StoredCurveResponse,
    VisualizationFluteResponse,
)


def compute_flute_and_build_response(request: FluteComputeRequest) -> FluteComputeResponse:
    database = PlatformDatabase()
    flute = _to_flute_geometry(request)
    result = compute_and_store_flute(
        flute=flute,
        options=build_modal_public_options(),
        platform_db=database,
    )
    return FluteComputeResponse(
        instrument_id=result.instrument_id,
        run_id=result.run_id,
        flute_kind=result.flute_kind,
        pairings_updated=result.pairings_updated,
        curve_points=_load_curve_points(database, result.instrument_id),
        best_pairing=_load_best_pairing(database, result.instrument_id, result.flute_kind),
    )


def get_stored_curve_response(instrument_id: int) -> StoredCurveResponse:
    database = PlatformDatabase()
    instrument = database.get_instrument(instrument_id)
    if instrument is None:
        raise HTTPException(status_code=404, detail="instrument-not-found")

    return StoredCurveResponse(
        instrument_id=instrument_id,
        flute_kind=str(instrument["kind"]),
        curve_points=_load_curve_points(database, instrument_id),
        best_pairing=_load_best_pairing(database, instrument_id, str(instrument["kind"])),
    )


def get_visualization_response(instrument_id: int) -> FluteVisualizationResponse:
    database = PlatformDatabase()
    selected_instrument = database.get_instrument(instrument_id)
    if selected_instrument is None:
        raise HTTPException(status_code=404, detail="instrument-not-found")

    selected_flute_kind = str(selected_instrument["kind"])
    pairing = _load_best_pairing(database, instrument_id, selected_flute_kind)

    if selected_flute_kind == "base":
        base_flute = _build_visualization_flute_from_row(selected_instrument, database)
        inverse_flute = _load_paired_visualization_flute(database, pairing)
    else:
        base_flute = _load_paired_visualization_flute(database, pairing)
        inverse_flute = _build_visualization_flute_from_row(selected_instrument, database)

    return FluteVisualizationResponse(
        selected_instrument_id=instrument_id,
        selected_flute_kind=selected_flute_kind,
        base_flute=base_flute,
        inverse_flute=inverse_flute,
        pairing=pairing,
    )


def get_catalog_response() -> FluteCatalogResponse:
    database = PlatformDatabase()
    instruments = database.list_instruments()
    curve_points_by_instrument = database.get_curve_points_by_instrument_ids(
        int(row["instrument_id"]) for row in instruments
    )

    base_flutes: list[VisualizationFluteResponse] = []
    inverse_flutes: list[VisualizationFluteResponse] = []

    for instrument in instruments:
        visualization_flute = _build_visualization_flute_from_row(
            instrument,
            database,
            curve_points=curve_points_by_instrument.get(int(instrument["instrument_id"]), []),
        )
        if str(instrument["kind"]) == "base":
            base_flutes.append(visualization_flute)
        else:
            inverse_flutes.append(visualization_flute)

    return FluteCatalogResponse(
        base_flutes=base_flutes,
        inverse_flutes=inverse_flutes,
    )


def get_rmse_ranking_response() -> RmseRankingResponse:
    database = PlatformDatabase()
    rows = database.list_best_pairs_sorted()

    pairs = [
        RmseRankingItemResponse(
            rank=index + 1,
            base_instrument_id=int(row["base_instrument_id"]),
            inverse_instrument_id=int(row["inverse_instrument_id"]),
            rmse=float(row["rmse"]),
            anchor_instrument_id=int(row["anchor_instrument_id"]),
        )
        for index, row in enumerate(rows)
    ]

    return RmseRankingResponse(total=len(pairs), pairs=pairs)


def _to_flute_geometry(request: FluteComputeRequest) -> FluteGeometry:
    normalized_kind = request.kind.strip().lower()
    if normalized_kind not in {"base", "inverse"}:
        raise HTTPException(status_code=422, detail="kind must be 'base' or 'inverse'")

    return FluteGeometry(
        kind=FluteKind.BASE if normalized_kind == "base" else FluteKind.INVERSE,
        d=request.d,
        x=request.x,
        y=request.y,
        a=request.a,
        Dt=request.Dt,
        L=request.L,
        Di=request.Di,
    )


def _rows_to_curve_points(rows) -> list[CurvePointResponse]:
    return [
        CurvePointResponse(
            cut_index=int(row["cut_index"]),
            cut_length_mm=float(row["cut_length_mm"]),
            f1_hz=float(row["f1_hz"]),
            f2_hz=float(row["f2_hz"]),
            delta_cents=float(row["delta_cents"]),
        )
        for row in rows
    ]


def _load_curve_points(database: PlatformDatabase, instrument_id: int) -> list[CurvePointResponse]:
    return _rows_to_curve_points(database.get_curve_points(instrument_id))


def _load_best_pairing(
    database: PlatformDatabase,
    instrument_id: int,
    flute_kind: str,
) -> PairingSummaryResponse | None:
    if flute_kind == "base":
        row = database.get_best_inverse_for_base(instrument_id)
        if row is None:
            return None
        return PairingSummaryResponse(
            related_instrument_id=int(row["inverse_instrument_id"]),
            rmse=float(row["rmse"]),
            selected_at=str(row["selected_at"]),
        )

    row = database.get_best_base_for_inverse(instrument_id)
    if row is None:
        return None
    return PairingSummaryResponse(
        related_instrument_id=int(row["base_instrument_id"]),
        rmse=float(row["rmse"]),
        selected_at=str(row["selected_at"]),
    )


def _build_geometry_response(instrument) -> FluteGeometryResponse:
    return FluteGeometryResponse(
        d=float(instrument["d_mm"]),
        x=float(instrument["x_mm"]),
        y=float(instrument["y_mm"]),
        a=float(instrument["a_mm"]),
        Dt=float(instrument["dt_mm"]),
        L=float(instrument["l_mm"]),
        Di=float(instrument["di_mm"]),
    )


def _build_visualization_flute_from_row(
    instrument,
    database: PlatformDatabase,
    curve_points=None,
) -> VisualizationFluteResponse:
    instrument_id = int(instrument["instrument_id"])
    return VisualizationFluteResponse(
        instrument_id=instrument_id,
        flute_kind=str(instrument["kind"]),
        geometry=_build_geometry_response(instrument),
        curve_points=(
            _rows_to_curve_points(curve_points)
            if curve_points is not None
            else _load_curve_points(database, instrument_id)
        ),
    )


def _load_paired_visualization_flute(
    database: PlatformDatabase,
    pairing: PairingSummaryResponse | None,
) -> VisualizationFluteResponse | None:
    if pairing is None:
        return None

    instrument = database.get_instrument(pairing.related_instrument_id)
    if instrument is None:
        raise HTTPException(status_code=404, detail="paired-instrument-not-found")

    return _build_visualization_flute_from_row(instrument, database)
