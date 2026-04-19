from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db.platform.repositories import PlatformDatabase, PlatformInstrumentRecord
from engine.analysis import compute_inharmonicity_curve_with_public_resonances
from engine.models import FluteGeometry, FluteKind, OpenWindOptions
from matching import compute_rmse_from_curve_results


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


def to_record(curve_result, calculation_method: str, loss_model: str) -> PlatformInstrumentRecord:
    geom = curve_result.input_geometry
    return PlatformInstrumentRecord(
        kind=str(geom["kind"]),
        d_mm=float(geom["d"]),
        x_mm=float(geom["x"]),
        y_mm=float(geom["y"]),
        a_mm=float(geom["a"]),
        dt_mm=float(geom["Dt"]),
        l_mm=float(geom["L"]),
        di_mm=float(geom["Di"]),
        calculation_method=calculation_method,
        loss_model=loss_model,
        resonance_method="resonance_frequencies",
        frequency_axis_min_hz=float(curve_result.frequency_axis_min_hz),
        frequency_axis_max_hz=float(curve_result.frequency_axis_max_hz),
        frequency_axis_step_hz=float(curve_result.frequency_axis_step_hz),
    )


def main() -> None:
    database = PlatformDatabase()
    database.initialize()

    options = OpenWindOptions(compute_method="modal", losses="diffrepr+")
    inverse_curve = compute_inharmonicity_curve_with_public_resonances(build_inverse_demo_flute(), options)
    base_curve = compute_inharmonicity_curve_with_public_resonances(build_base_demo_flute(), options)
    rmse_value = compute_rmse_from_curve_results(base_curve, inverse_curve)

    inverse_id = database.get_or_create_instrument_id(
        to_record(inverse_curve, options.compute_method, str(options.losses))
    )
    base_id = database.get_or_create_instrument_id(
        to_record(base_curve, options.compute_method, str(options.losses))
    )

    database.replace_curve_points(inverse_id, [point.__dict__ for point in inverse_curve.points])
    database.replace_curve_points(base_id, [point.__dict__ for point in base_curve.points])
    database.upsert_rmse_pair(base_id, inverse_id, rmse_value)
    database.refresh_best_inverse_for_base(base_id)
    database.refresh_best_base_for_inverse(inverse_id)

    payload = {
        "database_path": str(database.db_path),
        "base_id": base_id,
        "inverse_id": inverse_id,
        "rmse": rmse_value,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
