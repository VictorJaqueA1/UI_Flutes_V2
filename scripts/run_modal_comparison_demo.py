from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.analysis import compute_inharmonicity_curve_with_public_resonances
from engine.models import FluteGeometry, FluteKind, OpenWindOptions
from matching import compute_rmse, compute_rmse_from_curve_results


OUTPUT_DIR = PROJECT_ROOT / "docs" / "generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


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


def deltas(curve):
    return [point.delta_cents for point in curve.points]


def write_json(name: str, payload: dict) -> None:
    with (OUTPUT_DIR / name).open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def main() -> None:
    inverse = build_inverse_demo_flute()
    base = build_base_demo_flute()

    fem_options = OpenWindOptions(compute_method="FEM", losses=True)
    modal_options = OpenWindOptions(compute_method="modal", losses="diffrepr+")

    inverse_fem = compute_inharmonicity_curve_with_public_resonances(inverse, fem_options)
    inverse_modal = compute_inharmonicity_curve_with_public_resonances(inverse, modal_options)
    base_fem = compute_inharmonicity_curve_with_public_resonances(base, fem_options)
    base_modal = compute_inharmonicity_curve_with_public_resonances(base, modal_options)

    payload = {
        "notes": {
            "fem": "compute_method='FEM', losses=True",
            "modal": "compute_method='modal', losses='diffrepr+'",
        },
        "inverse_fem": inverse_fem.to_dict(),
        "inverse_modal": inverse_modal.to_dict(),
        "base_fem": base_fem.to_dict(),
        "base_modal": base_modal.to_dict(),
        "curve_rmse": {
            "fem_base_vs_inverse": compute_rmse_from_curve_results(base_fem, inverse_fem),
            "modal_base_vs_inverse": compute_rmse_from_curve_results(base_modal, inverse_modal),
            "inverse_fem_vs_modal": compute_rmse(deltas(inverse_fem), deltas(inverse_modal)),
            "base_fem_vs_modal": compute_rmse(deltas(base_fem), deltas(base_modal)),
        },
    }
    write_json("modal_comparison_demo.json", payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
