from __future__ import annotations

from engine.cuts import generate_equal_cuts
from engine.models import CutRequest, FluteGeometry, OpenWindOptions
from engine.openwind import (
    build_legacy_global_frequency_axis,
    create_single_cut_impedance_object,
    extract_public_resonances,
)
from engine.results import InharmonicityCurveResult, InharmonicityPoint


def compute_inharmonicity_curve_with_public_resonances(
    flute: FluteGeometry,
    options: OpenWindOptions | None = None,
    cut_count: int = 10,
) -> InharmonicityCurveResult:
    options = options or OpenWindOptions()
    global_axis = build_legacy_global_frequency_axis(flute, options)
    cut_lengths = generate_equal_cuts(flute.L, flute.L / 2.0, cut_count)
    points: list[InharmonicityPoint] = []

    for cut_length_mm in cut_lengths:
        impedance_object = create_single_cut_impedance_object(
            flute=flute,
            cut=CutRequest(length_mm=cut_length_mm),
            options=options,
            override_frequencies_hz=global_axis.values_hz,
        )
        resonances = extract_public_resonances(impedance_object, count=5)
        points.append(
            InharmonicityPoint(
                cut_length_mm=cut_length_mm,
                f1_hint_hz=0.0,
                f1_hz=resonances.f1_hz or 0.0,
                f2_hz=resonances.f2_hz or 0.0,
                delta_cents=resonances.delta_cents or 0.0,
                f1_window_hz=(0.0, 0.0),
                f2_window_hz=(0.0, 0.0),
            )
        )

    return InharmonicityCurveResult(
        flute_kind=flute.kind.value,
        input_geometry={
            "kind": flute.kind.value,
            "d": flute.d,
            "x": flute.x,
            "y": flute.y,
            "a": flute.a,
            "Dt": flute.Dt,
            "L": flute.L,
            "Di": flute.Di,
        },
        frequency_axis_min_hz=global_axis.minimum_hz,
        frequency_axis_max_hz=global_axis.maximum_hz,
        frequency_axis_step_hz=global_axis.step_hz,
        frequency_axis_rationale=(
            f"{global_axis.rationale} "
            "Las resonancias finales se toman con resonance_frequencies()."
        ),
        points=points,
    )
