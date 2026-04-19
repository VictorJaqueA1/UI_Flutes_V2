from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.analysis import (
    compare_manual_and_public_resonances,
    compute_inharmonicity_curve_with_legacy_windows,
)
from engine.models import FluteGeometry, FluteKind, OpenWindOptions


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


def write_json(name: str, payload: dict) -> None:
    with (OUTPUT_DIR / name).open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def main() -> None:
    options = OpenWindOptions()
    inverse_flute = build_inverse_demo_flute()
    base_flute = build_base_demo_flute()

    inverse_curve = compute_inharmonicity_curve_with_legacy_windows(
        inverse_flute,
        options,
    )
    base_curve = compute_inharmonicity_curve_with_legacy_windows(
        base_flute,
        options,
    )
    inverse_comparison = compare_manual_and_public_resonances(
        inverse_flute,
        options,
    )
    base_comparison = compare_manual_and_public_resonances(
        base_flute,
        options,
    )

    payload = {
        "inverse_curve": inverse_curve.to_dict(),
        "base_curve": base_curve.to_dict(),
        "inverse_comparison": inverse_comparison.to_dict(),
        "base_comparison": base_comparison.to_dict(),
    }

    write_json("resonance_method_comparison_demo.json", payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
