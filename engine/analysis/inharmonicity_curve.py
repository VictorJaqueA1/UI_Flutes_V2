from __future__ import annotations

from engine.cuts import generate_equal_cuts
from engine.models import CutRequest, FluteGeometry, OpenWindOptions
from engine.openwind import (
    build_legacy_global_frequency_axis,
    run_single_cut_impedance,
    select_resonances_with_legacy_windows,
)
from engine.results import InharmonicityCurveResult, InharmonicityPoint


def compute_inharmonicity_curve_with_legacy_windows(
    flute: FluteGeometry,
    options: OpenWindOptions | None = None,
    cut_count: int = 10,
) -> InharmonicityCurveResult:
    options = options or OpenWindOptions()
    global_axis = build_legacy_global_frequency_axis(flute, options)
    cut_lengths = generate_equal_cuts(flute.L, flute.L / 2.0, cut_count)
    points: list[InharmonicityPoint] = []

    for cut_length_mm in cut_lengths:
        impedance_result = run_single_cut_impedance(
            flute=flute,
            cut=CutRequest(length_mm=cut_length_mm),
            options=options,
            override_frequencies_hz=global_axis.values_hz,
            frequency_axis_rationale=global_axis.rationale,
        )

        impedance_magnitude = [
            (real ** 2 + imag ** 2) ** 0.5
            for real, imag in zip(
                impedance_result.impedance_real,
                impedance_result.impedance_imag,
            )
        ]
        selection = select_resonances_with_legacy_windows(
            frequencies_hz=impedance_result.frequency_axis_hz,
            impedance_magnitude=impedance_magnitude,
            cut_length_mm=cut_length_mm,
            temperature_c=options.temperature_c,
        )
        points.append(
            InharmonicityPoint(
                cut_length_mm=cut_length_mm,
                f1_hint_hz=selection.f1_hint_hz,
                f1_hz=selection.f1_hz,
                f2_hz=selection.f2_hz,
                delta_cents=selection.delta_cents,
                f1_window_hz=selection.f1_window_hz,
                f2_window_hz=selection.f2_window_hz,
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
        frequency_axis_rationale=global_axis.rationale,
        points=points,
    )
