from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.analysis import compute_inharmonicity_curve_with_public_resonances
from engine.models import FluteGeometry, FluteKind, OpenWindOptions
from matching import compute_rmse_from_curve_results


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


def save_plot(inverse_curve, base_curve) -> None:
    x_inverse = [point.cut_length_mm for point in inverse_curve.points]
    y_inverse = [point.delta_cents for point in inverse_curve.points]
    x_base = [point.cut_length_mm for point in base_curve.points]
    y_base = [point.delta_cents for point in base_curve.points]

    plt.figure(figsize=(8, 4.5))
    plt.plot(x_inverse, y_inverse, marker="o", color="#67d5ff", linewidth=2, label="Inversa")
    plt.plot(x_base, y_base, marker="o", color="#ff9a4d", linewidth=2, label="Base")
    plt.gca().invert_xaxis()
    plt.title("Curvas de inarmonicidad demo con resonance_frequencies()")
    plt.xlabel("Longitud de corte Li (mm)")
    plt.ylabel("Delta (cents)")
    plt.grid(True, alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "public_inharmonicity_demo.png", dpi=160)
    plt.close()


def main() -> None:
    options = OpenWindOptions()
    inverse_curve = compute_inharmonicity_curve_with_public_resonances(
        build_inverse_demo_flute(),
        options,
    )
    base_curve = compute_inharmonicity_curve_with_public_resonances(
        build_base_demo_flute(),
        options,
    )
    rmse_value = compute_rmse_from_curve_results(base_curve, inverse_curve)

    payload = {
        "inverse_curve": inverse_curve.to_dict(),
        "base_curve": base_curve.to_dict(),
        "rmse": rmse_value,
        "inharmonicity_formula": "delta = 1200 * log2(f2 / (2 * f1))",
        "rmse_formula": "rmse = sqrt(mean((delta_base_i - delta_inv_i)^2))",
    }

    write_json("public_inharmonicity_demo.json", payload)
    save_plot(inverse_curve, base_curve)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
