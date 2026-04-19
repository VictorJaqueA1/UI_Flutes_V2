from __future__ import annotations

from engine.cuts import generate_equal_cuts
from engine.models import CutRequest, FluteGeometry, OpenWindOptions
from engine.openwind import (
    build_legacy_global_frequency_axis,
    create_single_cut_impedance_object,
    extract_public_resonances,
    run_single_cut_impedance,
    select_resonances_with_legacy_windows,
)
from engine.results import (
    ResonanceMethodComparisonPoint,
    ResonanceMethodComparisonResult,
)


def compare_manual_and_public_resonances(
    flute: FluteGeometry,
    options: OpenWindOptions | None = None,
    cut_count: int = 10,
) -> ResonanceMethodComparisonResult:
    options = options or OpenWindOptions()
    global_axis = build_legacy_global_frequency_axis(flute, options)
    cut_lengths = generate_equal_cuts(flute.L, flute.L / 2.0, cut_count)
    points: list[ResonanceMethodComparisonPoint] = []

    for cut_length_mm in cut_lengths:
        cut = CutRequest(length_mm=cut_length_mm)
        impedance_result = run_single_cut_impedance(
            flute=flute,
            cut=cut,
            options=options,
            override_frequencies_hz=global_axis.values_hz,
            frequency_axis_rationale=global_axis.rationale,
        )
        impedance_object = create_single_cut_impedance_object(
            flute=flute,
            cut=cut,
            options=options,
            override_frequencies_hz=global_axis.values_hz,
        )

        impedance_magnitude = [
            (real ** 2 + imag ** 2) ** 0.5
            for real, imag in zip(
                impedance_result.impedance_real,
                impedance_result.impedance_imag,
            )
        ]
        manual = select_resonances_with_legacy_windows(
            frequencies_hz=impedance_result.frequency_axis_hz,
            impedance_magnitude=impedance_magnitude,
            cut_length_mm=cut_length_mm,
            temperature_c=options.temperature_c,
        )
        public = extract_public_resonances(impedance_object, count=5)

        points.append(
            ResonanceMethodComparisonPoint(
                cut_length_mm=cut_length_mm,
                manual_f1_hz=manual.f1_hz,
                manual_f2_hz=manual.f2_hz,
                manual_delta_cents=manual.delta_cents,
                openwind_f1_hz=public.f1_hz,
                openwind_f2_hz=public.f2_hz,
                openwind_delta_cents=public.delta_cents,
                difference_f1_hz=(
                    None if public.f1_hz is None else manual.f1_hz - public.f1_hz
                ),
                difference_f2_hz=(
                    None if public.f2_hz is None else manual.f2_hz - public.f2_hz
                ),
                difference_delta_cents=(
                    None
                    if public.delta_cents is None
                    else manual.delta_cents - public.delta_cents
                ),
            )
        )

    return ResonanceMethodComparisonResult(
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
        points=points,
    )
