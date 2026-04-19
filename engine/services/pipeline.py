from __future__ import annotations

from engine.cuts import generate_equal_cuts
from engine.models import CutRequest, FluteGeometry, OpenWindOptions
from engine.openwind import (
    build_legacy_global_frequency_axis,
    create_single_cut_impedance_object,
    extract_public_resonances,
)
from engine.results import ImpedanceCurveResult, InharmonicityCurveResult, InharmonicityPoint
from .persistence_models import CutComputationRecord, FluteComputationBundle


def build_modal_public_options() -> OpenWindOptions:
    return OpenWindOptions(
        compute_method="modal",
        losses="diffrepr+",
    )


def run_modal_public_pipeline(
    flute: FluteGeometry,
    options: OpenWindOptions | None = None,
    cut_count: int = 10,
) -> FluteComputationBundle:
    options = options or build_modal_public_options()
    global_axis = build_legacy_global_frequency_axis(flute, options)
    cut_lengths = generate_equal_cuts(flute.L, flute.L / 2.0, cut_count)
    cut_records: list[CutComputationRecord] = []
    points: list[InharmonicityPoint] = []

    for index, cut_length_mm in enumerate(cut_lengths, start=1):
        cut = CutRequest(length_mm=cut_length_mm)
        impedance_object = create_single_cut_impedance_object(
            flute=flute,
            cut=cut,
            options=options,
            override_frequencies_hz=global_axis.values_hz,
        )
        resonance_selection = extract_public_resonances(impedance_object, count=5)
        impedance_values = list(impedance_object.impedance)
        impedance_result = ImpedanceCurveResult(
            flute_kind=flute.kind.value,
            cut_length_mm=cut_length_mm,
            frequency_axis_hz=list(map(float, impedance_object.frequencies)),
            impedance_real=[float(value.real) for value in impedance_values],
            impedance_imag=[float(value.imag) for value in impedance_values],
            zc=float(impedance_object.Zc),
            main_bore=[],
            holes_valves=[],
            frequency_axis_rationale=(
                f"{global_axis.rationale} "
                "Las resonancias finales se toman con resonance_frequencies()."
            ),
            f1_estimate_hz=0.0,
        )
        f1_hz = float(resonance_selection.f1_hz or 0.0)
        f2_hz = float(resonance_selection.f2_hz or 0.0)
        delta_cents = float(resonance_selection.delta_cents or 0.0)

        cut_records.append(
            CutComputationRecord(
                cut_index=index,
                impedance=impedance_result,
                f1_hz=f1_hz,
                f2_hz=f2_hz,
                delta_cents=delta_cents,
                resonance_frequencies_hz=list(resonance_selection.frequencies_hz),
            )
        )
        points.append(
            InharmonicityPoint(
                cut_length_mm=cut_length_mm,
                f1_hint_hz=0.0,
                f1_hz=f1_hz,
                f2_hz=f2_hz,
                delta_cents=delta_cents,
                f1_window_hz=(0.0, 0.0),
                f2_window_hz=(0.0, 0.0),
            )
        )

    return FluteComputationBundle(
        curve=InharmonicityCurveResult(
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
        ),
        cut_records=cut_records,
    )
