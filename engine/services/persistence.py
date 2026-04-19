from __future__ import annotations

import json
from typing import Iterable

from db.platform.repositories import PlatformDatabase, PlatformInstrumentRecord
from db.replication.repositories import (
    ReplicationDatabase,
    ReplicationInstrumentRecord,
    ReplicationRunRecord,
)
from engine.geometry import build_embouchure_hole_table, build_main_bore_for_cut
from engine.models import CutRequest, FluteGeometry, FluteKind, OpenWindOptions
from matching import compute_rmse

from .persistence_models import FluteComputationBundle, PersistedFluteResult
from .pipeline import build_modal_public_options, run_modal_public_pipeline


ENGINE_VERSION = "modal-public-persistence-v1"
RESONANCE_METHOD = "resonance_frequencies"


def compute_and_store_flute(
    flute: FluteGeometry,
    options: OpenWindOptions | None = None,
    platform_db: PlatformDatabase | None = None,
    replication_db: ReplicationDatabase | None = None,
) -> PersistedFluteResult:
    options = options or build_modal_public_options()
    platform_db = platform_db or PlatformDatabase()
    replication_db = replication_db or ReplicationDatabase()
    platform_db.initialize()
    replication_db.initialize()

    bundle = run_modal_public_pipeline(flute=flute, options=options)
    instrument_id = _persist_platform(bundle, flute, options, platform_db)
    run_id = _persist_replication(bundle, flute, instrument_id, options, replication_db)
    pairings_updated = _update_pairings(bundle, instrument_id, flute.kind, platform_db)

    return PersistedFluteResult(
        instrument_id=instrument_id,
        run_id=run_id,
        flute_kind=flute.kind.value,
        pairings_updated=pairings_updated,
    )


def _persist_platform(
    bundle: FluteComputationBundle,
    flute: FluteGeometry,
    options: OpenWindOptions,
    database: PlatformDatabase,
) -> int:
    curve = bundle.curve
    record = PlatformInstrumentRecord(
        kind=flute.kind.value,
        d_mm=flute.d,
        x_mm=flute.x,
        y_mm=flute.y,
        a_mm=flute.a,
        dt_mm=flute.Dt,
        l_mm=flute.L,
        di_mm=flute.Di,
        calculation_method=options.compute_method,
        loss_model=str(options.losses),
        resonance_method=RESONANCE_METHOD,
        frequency_axis_min_hz=float(curve.frequency_axis_min_hz),
        frequency_axis_max_hz=float(curve.frequency_axis_max_hz),
        frequency_axis_step_hz=float(curve.frequency_axis_step_hz),
    )
    instrument_id = database.get_or_create_instrument_id(record)
    database.replace_curve_points(
        instrument_id,
        [
            {
                "cut_length_mm": point.cut_length_mm,
                "f1_hz": point.f1_hz,
                "f2_hz": point.f2_hz,
                "delta_cents": point.delta_cents,
            }
            for point in curve.points
        ],
    )
    return instrument_id


def _persist_replication(
    bundle: FluteComputationBundle,
    flute: FluteGeometry,
    instrument_id: int,
    options: OpenWindOptions,
    database: ReplicationDatabase,
) -> int:
    try:
        import openwind

        openwind_version = getattr(openwind, "__version__", "unknown")
    except ImportError:
        openwind_version = "unknown"

    database.insert_instrument(
        ReplicationInstrumentRecord(
            instrument_id=instrument_id,
            kind=flute.kind.value,
            d_mm=flute.d,
            x_mm=flute.x,
            y_mm=flute.y,
            a_mm=flute.a,
            dt_mm=flute.Dt,
            l_mm=flute.L,
            di_mm=flute.Di,
        )
    )

    run_id = database.insert_run(
        ReplicationRunRecord(
            instrument_id=instrument_id,
            engine_version=ENGINE_VERSION,
            openwind_version=openwind_version,
            calculation_method=options.compute_method,
            loss_model=str(options.losses),
            resonance_method=RESONANCE_METHOD,
            source_location=options.source_location,
            notes="Corrida persistida automaticamente desde el engine.",
        )
    )

    database.replace_input_parameters(
        run_id,
        _build_replication_input_parameters(flute, options, bundle),
    )
    database.replace_input_payloads(
        run_id,
        _build_replication_input_payloads(flute, bundle),
    )
    database.replace_cut_runs(
        run_id,
        [point.cut_length_mm for point in bundle.curve.points],
    )
    database.upsert_run_output_core(
        run_id,
        zc=float(bundle.cut_records[0].impedance.zc if bundle.cut_records else 0.0),
    )
    database.replace_cut_output_resonances(
        run_id,
        [
            {
                "cut_index": record.cut_index,
                "f1_hz": record.f1_hz,
                "f2_hz": record.f2_hz,
                "delta_cents": record.delta_cents,
            }
            for record in bundle.cut_records
        ],
    )
    database.replace_cut_output_impedance(
        run_id,
        [
            {
                "cut_index": record.cut_index,
                "frequencies_json": json.dumps(record.impedance.frequency_axis_hz),
                "impedance_real_json": json.dumps(record.impedance.impedance_real),
                "impedance_imag_json": json.dumps(record.impedance.impedance_imag),
            }
            for record in bundle.cut_records
        ],
    )
    return run_id


def _build_replication_input_parameters(
    flute: FluteGeometry,
    options: OpenWindOptions,
    bundle: FluteComputationBundle,
) -> list[dict]:
    curve = bundle.curve
    rows: list[dict] = []

    flute_rows = [
        ("kind", flute.kind.value, None, "derived", False, False, "Tipo de flauta."),
        ("d", flute.d, "mm", "explicit", True, False, "Diametro de embocadura."),
        ("x", flute.x, "mm", "explicit", True, False, "Posicion de embocadura."),
        ("y", flute.y, "mm", "explicit", True, False, "Altura de chimenea."),
        ("a", flute.a, "mm", "explicit", True, False, "Breakpoint geometrico."),
        ("Dt", flute.Dt, "mm", "explicit", True, False, "Diametro extremo variable."),
        ("L", flute.L, "mm", "explicit", True, False, "Longitud total."),
        ("Di", flute.Di, "mm", "explicit", True, False, "Diametro interno fijo."),
    ]
    for name, value, unit, origin, was_provided, used_default, description in flute_rows:
        rows.append(
            {
                "input_name": name,
                "input_value": str(value),
                "input_unit": unit,
                "input_origin": origin,
                "was_provided": was_provided,
                "used_default": used_default,
                "description": description,
            }
        )

    openwind_rows = [
        ("frequencies", _axis_summary(curve), "Hz", "derived", False, False, "Barrido frecuencial generado por el pipeline."),
        ("main_bore", "stored in payloads", None, "derived", False, False, "Geometria efectiva construida para cada corte."),
        ("holes_valves", "stored in payloads", None, "derived", False, False, "Embocadura entregada a OpenWind."),
        ("holes_valves_chart", "[]", None, "default", False, True, "No se entrega chart operacional; OpenWind usa el default vacio."),
        ("unit", options.unit, None, "explicit", True, False, "Unidad entregada a ImpedanceComputation."),
        ("diameter", str(options.diameter), None, "explicit", True, False, "Indica que la geometria se entrega como diametros."),
        ("temperature", str(options.temperature_c), "C", "explicit", True, False, "Temperatura de simulacion."),
        ("humidity", str(options.humidity), None, "explicit", True, False, "Humedad relativa de simulacion."),
        ("losses", str(options.losses), None, "explicit", True, False, "Modelo de perdidas."),
        ("compute_method", options.compute_method, None, "explicit", True, False, "Metodo numerico usado por OpenWind."),
        ("source_location", options.source_location, None, "explicit", True, False, "Ubicacion de la fuente en la embocadura."),
        ("radiation_category", options.radiation_category, None, "explicit", True, False, "Modelo de radiacion."),
        ("player", "Player()", None, "default", False, True, "Player no entregado explicitamente."),
        ("nondim", "True", None, "default", False, True, "Parametro default de OpenWind."),
        ("spherical_waves", "False", None, "default", False, True, "Parametro default de OpenWind."),
        ("discontinuity_mass", "True", None, "default", False, True, "Parametro default de OpenWind."),
        ("matching_volume", "False", None, "default", False, True, "Parametro default de OpenWind."),
        ("l_ele", "None", None, "default", False, True, "Parametro default de OpenWind."),
        ("order", "None", None, "default", False, True, "Parametro default de OpenWind."),
        ("nb_sub", "1", None, "default", False, True, "Parametro default de OpenWind."),
        ("note", "None", None, "default", False, True, "Parametro default de OpenWind."),
        ("use_rad1dof", "auto/by OpenWind if required", None, "default", False, True, "En modal OpenWind puede ajustarlo automaticamente."),
        ("diff_repr_vars", "False", None, "default", False, True, "Parametro default de OpenWind."),
        ("interp", "False", None, "default", False, True, "No se usa interpolacion en el pipeline principal."),
        ("interp_grid", "'original'", None, "default", False, True, "Parametro default de OpenWind."),
    ]
    for name, value, unit, origin, was_provided, used_default, description in openwind_rows:
        rows.append(
            {
                "input_name": name,
                "input_value": str(value),
                "input_unit": unit,
                "input_origin": origin,
                "was_provided": was_provided,
                "used_default": used_default,
                "description": description,
            }
        )

    return rows


def _build_replication_input_payloads(
    flute: FluteGeometry,
    bundle: FluteComputationBundle,
) -> list[dict]:
    main_bore_by_cut = {
        str(record.cut_index): build_main_bore_for_cut(
            flute,
            CutRequest(length_mm=record.impedance.cut_length_mm),
        )
        for record in bundle.cut_records
    }
    frequencies = bundle.cut_records[0].impedance.frequency_axis_hz if bundle.cut_records else []
    return [
        {
            "payload_name": "frequencies",
            "payload_format": "json",
            "payload_value": json.dumps(frequencies),
            "description": "Barrido frecuencial completo usado en la corrida.",
        },
        {
            "payload_name": "holes_valves",
            "payload_format": "json",
            "payload_value": json.dumps(build_embouchure_hole_table(flute)),
            "description": "Tabla de embocadura entregada a OpenWind.",
        },
        {
            "payload_name": "main_bore_by_cut",
            "payload_format": "json",
            "payload_value": json.dumps(main_bore_by_cut),
            "description": "main_bore efectivo construido para cada uno de los 10 cortes.",
        },
    ]


def _axis_summary(curve) -> str:
    return (
        f"[{curve.frequency_axis_min_hz}, "
        f"{curve.frequency_axis_max_hz}, "
        f"step={curve.frequency_axis_step_hz}]"
    )


def _update_pairings(
    bundle: FluteComputationBundle,
    instrument_id: int,
    flute_kind: FluteKind,
    database: PlatformDatabase,
) -> int:
    current_deltas = [point.delta_cents for point in bundle.curve.points]
    pairings_updated = 0

    if flute_kind == FluteKind.BASE:
        opposite_ids = database.list_instrument_ids_by_kind(FluteKind.INVERSE.value)
        for opposite_id in opposite_ids:
            opposite_deltas = database.get_curve_deltas(opposite_id)
            if not opposite_deltas:
                continue
            rmse = compute_rmse(current_deltas, opposite_deltas)
            database.upsert_rmse_pair(instrument_id, opposite_id, rmse)
            database.refresh_best_base_for_inverse(opposite_id)
            pairings_updated += 1
        database.refresh_best_inverse_for_base(instrument_id)
    else:
        opposite_ids = database.list_instrument_ids_by_kind(FluteKind.BASE.value)
        for opposite_id in opposite_ids:
            opposite_deltas = database.get_curve_deltas(opposite_id)
            if not opposite_deltas:
                continue
            rmse = compute_rmse(opposite_deltas, current_deltas)
            database.upsert_rmse_pair(opposite_id, instrument_id, rmse)
            database.refresh_best_inverse_for_base(opposite_id)
            pairings_updated += 1
        database.refresh_best_base_for_inverse(instrument_id)

    return pairings_updated
