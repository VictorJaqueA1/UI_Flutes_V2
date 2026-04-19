from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.models import CutRequest, FluteGeometry, FluteKind, OpenWindOptions
from engine.openwind import run_single_cut_impedance


def build_demo_flute() -> FluteGeometry:
    return FluteGeometry(
        kind=FluteKind.INVERSE,
        d=9.0,
        x=160.0,
        y=6.0,
        a=150.0,
        Dt=12.0,
    )


def main() -> None:
    flute = build_demo_flute()
    cut = CutRequest(length_mm=570.0)
    options = OpenWindOptions()

    result = run_single_cut_impedance(flute, cut, options)

    payload = {
        "inputs": {
            "flute": flute.__dict__,
            "cut": cut.__dict__,
            "options": options.__dict__,
        },
        "outputs_summary": {
            "sample_count": len(result.frequency_axis_hz),
            "frequency_min_hz": result.frequency_axis_hz[0],
            "frequency_max_hz": result.frequency_axis_hz[-1],
            "zc": result.zc,
            "first_real_values": result.impedance_real[:5],
            "first_imag_values": result.impedance_imag[:5],
        },
        "frequency_axis_rationale": result.frequency_axis_rationale,
        "main_bore": result.main_bore,
        "holes_valves": result.holes_valves,
    }

    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()
