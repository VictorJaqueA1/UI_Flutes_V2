from __future__ import annotations

import json
import sys
from pathlib import Path

import openwind


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db.replication.repositories import (
    ReplicationDatabase,
    ReplicationInstrumentRecord,
    ReplicationRunRecord,
)
from engine.cuts import generate_equal_cuts
from engine.geometry import build_embouchure_hole_table, build_main_bore_for_cut
from engine.models import CutRequest, FluteGeometry, FluteKind, OpenWindOptions
from engine.openwind import (
    build_legacy_global_frequency_axis,
    create_single_cut_impedance_object,
    extract_public_resonances,
)


def build_inverse_demo_flute() -> FluteGeometry:
    return FluteGeometry(
        kind=FluteKind.INVERSE,
        d=9.0,
        x=160.0,
        y=6.0,
        a=150.0,
        Dt=12.0,
    )


def build_base_demo_flute() -> FluteGeometry:
    return FluteGeometry(
        kind=FluteKind.BASE,
        d=9.0,
        x=160.0,
        y=6.0,
        a=150.0,
        Dt=12.0,
    )


def build_input_parameters(flute: FluteGeometry, options: OpenWindOptions, global_axis) -> list[dict]:
    rows = []

    explicit_scalars = {
        "frequencies": ("derived", False, False, "Hz", "Barrido frecuencial generado por el pipeline."),
        "main_bore": ("derived", False, False, None, "Geometria efectiva construida para cada corte."),
        "holes_valves": ("derived", False, False, None, "Embocadura y side holes entregados a OpenWind."),
        "unit": ("explicit", True, False, None, "Unidad entregada a ImpedanceComputation."),
        "diameter": ("explicit", True, False, None, "Indica que los valores geometricos son diametros."),
        "temperature": ("explicit", True, False, "C", "Temperatura de simulacion."),
        "humidity": ("explicit", True, False, None, "Humedad relativa de simulacion."),
        "radiation_category": ("explicit", True, False, None, "Modelo de radiacion usado."),
        "losses": ("explicit", True, False, None, "Modelo de perdidas usado."),
        "compute_method": ("explicit", True, False, None, "Metodo numerico usado por OpenWind."),
        "source_location": ("explicit", True, False, None, "Punto fuente en la embocadura."),
        "holes_chart": ("default", False, True, None, "No se entrego fingering chart operativo; se usa el default vacio."),
        "player": ("default", False, True, None, "Player no entregado explicitamente."),
        "nondim": ("default", False, True, None, "Parametro default de OpenWind."),
        "spherical_waves": ("default", False, True, None, "Parametro default de OpenWind."),
        "discontinuity_mass": ("default", False, True, None, "Parametro default de OpenWind."),
        "matching_volume": ("default", False, True, None, "Parametro default de OpenWind."),
        "l_ele": ("default", False, True, None, "Parametro default de OpenWind."),
        "order": ("default", False, True, None, "Parametro default de OpenWind."),
        "nb_sub": ("default", False, True, None, "Parametro default de OpenWind."),
        "note": ("default", False, True, None, "Parametro default de OpenWind."),
        "use_rad1dof": ("default", False, True, None, "OpenWind puede ajustarlo automaticamente en modal."),
        "diff_repr_vars": ("default", False, True, None, "Parametro default de OpenWind."),
        "interp": ("default", False, True, None, "Parametro default de OpenWind."),
        "interp_grid": ("default", False, True, None, "Parametro default de OpenWind."),
    }

    values = {
        "frequencies": f"[{global_axis.minimum_hz}, {global_axis.maximum_hz}, step={global_axis.step_hz}]",
        "main_bore": "stored in payloads",
        "holes_valves": "stored in payloads",
        "unit": options.unit,
        "diameter": str(options.diameter),
        "temperature": str(options.temperature_c),
        "humidity": str(options.humidity),
        "radiation_category": options.radiation_category,
        "losses": str(options.losses),
        "compute_method": options.compute_method,
        "source_location": options.source_location,
        "holes_chart": "[]",
        "player": "Player()",
        "nondim": "True",
        "spherical_waves": "False",
        "discontinuity_mass": "True",
        "matching_volume": "False",
        "l_ele": "None",
        "order": "None",
        "nb_sub": "1",
        "note": "None",
        "use_rad1dof": "auto/by OpenWind if required",
        "diff_repr_vars": "False",
        "interp": "False",
        "interp_grid": "'original'",
    }

    flute_rows = [
        ("kind", flute.kind.value, None, "derived", False, False, "Tipo de flauta."),
        ("d", flute.d, "mm", "explicit", True, False, "Diametro de embocadura."),
        ("x", flute.x, "mm", "explicit", True, False, "Posicion de embocadura."),
        ("y", flute.y, "mm", "explicit", True, False, "Altura de chimenea."),
        ("a", flute.a, "mm", "explicit", True, False, "Breakpoint."),
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

    for name, (origin, was_provided, used_default, unit, description) in explicit_scalars.items():
        rows.append(
            {
                "input_name": name,
                "input_value": str(values[name]),
                "input_unit": unit,
                "input_origin": origin,
                "was_provided": was_provided,
                "used_default": used_default,
                "description": description,
            }
        )

    return rows


def build_payloads(flute: FluteGeometry, options: OpenWindOptions, global_axis, cut_lengths: list[float]) -> list[dict]:
    per_cut_bores = {
        str(index): build_main_bore_for_cut(flute, CutRequest(length_mm=cut_length))
        for index, cut_length in enumerate(cut_lengths, start=1)
    }
    return [
        {
            "payload_name": "frequencies",
            "payload_format": "json",
            "payload_value": json.dumps(global_axis.values_hz),
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
            "payload_value": json.dumps(per_cut_bores),
            "description": "main_bore efectivo construido para cada uno de los 10 cortes.",
        },
    ]


def persist_demo_flute(database: ReplicationDatabase, flute: FluteGeometry, instrument_id: int) -> int:
    options = OpenWindOptions(compute_method="modal", losses="diffrepr+")
    global_axis = build_legacy_global_frequency_axis(flute, options)
    cut_lengths = generate_equal_cuts(flute.L, flute.L / 2.0, 10)

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
            engine_version="prototype-modal-v1",
            openwind_version=getattr(openwind, "__version__", "unknown"),
            calculation_method=options.compute_method,
            loss_model=str(options.losses),
            resonance_method="resonance_frequencies",
            source_location=options.source_location,
            notes="Demo de persistencia de inputs para una corrida modal.",
        )
    )

    database.replace_input_parameters(
        run_id,
        build_input_parameters(flute, options, global_axis),
    )
    database.replace_input_payloads(
        run_id,
        build_payloads(flute, options, global_axis, cut_lengths),
    )
    database.replace_cut_runs(run_id, cut_lengths)

    impedance_rows = []
    resonance_rows = []
    first_zc = None
    for index, cut_length in enumerate(cut_lengths, start=1):
        obj = create_single_cut_impedance_object(
            flute=flute,
            cut=CutRequest(length_mm=cut_length),
            options=options,
            override_frequencies_hz=global_axis.values_hz,
        )
        resonances = extract_public_resonances(obj, count=5)
        if first_zc is None:
            first_zc = float(obj.Zc)
        impedance_rows.append(
            {
                "cut_index": index,
                "frequencies_json": json.dumps(list(map(float, obj.frequencies))),
                "impedance_real_json": json.dumps([float(value.real) for value in obj.impedance]),
                "impedance_imag_json": json.dumps([float(value.imag) for value in obj.impedance]),
            }
        )
        resonance_rows.append(
            {
                "cut_index": index,
                "f1_hz": float(resonances.f1_hz or 0.0),
                "f2_hz": float(resonances.f2_hz or 0.0),
                "delta_cents": float(resonances.delta_cents or 0.0),
            }
        )

    database.upsert_run_output_core(run_id, zc=float(first_zc or 0.0))
    database.replace_cut_output_resonances(run_id, resonance_rows)
    database.replace_cut_output_impedance(run_id, impedance_rows)
    return run_id


def main() -> None:
    database = ReplicationDatabase()
    database.initialize()

    inverse_run_id = persist_demo_flute(database, build_inverse_demo_flute(), instrument_id=1)
    base_run_id = persist_demo_flute(database, build_base_demo_flute(), instrument_id=2)

    print(
        json.dumps(
            {
                "database_path": str(database.db_path),
                "inverse_run_id": inverse_run_id,
                "base_run_id": base_run_id,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
