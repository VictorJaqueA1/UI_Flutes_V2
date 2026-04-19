from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.analysis import compute_inharmonicity_curve_with_legacy_windows
from engine.models import FluteGeometry, FluteKind, OpenWindOptions


OUTPUT_DIR = PROJECT_ROOT / "docs" / "generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def build_demo_flute() -> FluteGeometry:
    return FluteGeometry(
        kind=FluteKind.INVERSE,
        d=9.0,
        x=160.0,
        y=6.0,
        a=150.0,
        Dt=12.0,
    )


def write_outputs(payload: dict) -> None:
    json_path = OUTPUT_DIR / "inharmonicity_inverse_demo.json"
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def save_plot(payload: dict) -> None:
    points = payload["points"]
    x_values = [point["cut_length_mm"] for point in points]
    y_values = [point["delta_cents"] for point in points]

    plt.figure(figsize=(8, 4.5))
    plt.plot(x_values, y_values, marker="o", color="#67d5ff", linewidth=2)
    plt.gca().invert_xaxis()
    plt.title("Curva de inarmonicidad demo - flauta inversa")
    plt.xlabel("Longitud de corte Li (mm)")
    plt.ylabel("Delta (cents)")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "inharmonicity_inverse_demo.png", dpi=160)
    plt.close()


def main() -> None:
    flute = build_demo_flute()
    options = OpenWindOptions()
    result = compute_inharmonicity_curve_with_legacy_windows(flute, options)
    payload = result.to_dict()

    write_outputs(payload)
    save_plot(payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
