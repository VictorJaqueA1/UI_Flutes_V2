from __future__ import annotations

from engine.geometry import build_embouchure_hole_table, build_main_bore_for_cut
from engine.models import CutRequest, FluteGeometry, OpenWindOptions
from engine.openwind.frequency_axis import build_frequency_axis_for_cut
from engine.results import ImpedanceCurveResult


def run_single_cut_impedance(
    flute: FluteGeometry,
    cut: CutRequest,
    options: OpenWindOptions | None = None,
    override_frequencies_hz: list[float] | None = None,
    frequency_axis_rationale: str | None = None,
) -> ImpedanceCurveResult:
    try:
        from openwind import ImpedanceComputation
    except ImportError as exc:
        raise RuntimeError(
            "OpenWind no está disponible en este entorno de Python."
        ) from exc

    options = options or OpenWindOptions()
    main_bore = build_main_bore_for_cut(flute, cut)
    holes_valves = build_embouchure_hole_table(flute)
    frequency_axis = build_frequency_axis_for_cut(cut, options)
    frequencies_hz = override_frequencies_hz or frequency_axis.values_hz

    result = ImpedanceComputation(
        frequencies=frequencies_hz,
        main_bore=main_bore,
        holes_valves=holes_valves,
        unit=options.unit,
        diameter=options.diameter,
        temperature=options.temperature_c,
        humidity=options.humidity,
        radiation_category=options.radiation_category,
        losses=options.losses,
        compute_method=options.compute_method,
        source_location=options.source_location,
    )

    impedance_values = list(result.impedance)

    return ImpedanceCurveResult(
        flute_kind=flute.kind.value,
        cut_length_mm=cut.length_mm,
        frequency_axis_hz=list(result.frequencies),
        impedance_real=[float(value.real) for value in impedance_values],
        impedance_imag=[float(value.imag) for value in impedance_values],
        zc=float(result.Zc),
        main_bore=main_bore,
        holes_valves=holes_valves,
        frequency_axis_rationale=frequency_axis_rationale or frequency_axis.rationale,
        f1_estimate_hz=frequency_axis.f1_estimate_hz,
    )


def create_single_cut_impedance_object(
    flute: FluteGeometry,
    cut: CutRequest,
    options: OpenWindOptions | None = None,
    override_frequencies_hz: list[float] | None = None,
):
    try:
        from openwind import ImpedanceComputation
    except ImportError as exc:
        raise RuntimeError(
            "OpenWind no está disponible en este entorno de Python."
        ) from exc

    options = options or OpenWindOptions()
    main_bore = build_main_bore_for_cut(flute, cut)
    holes_valves = build_embouchure_hole_table(flute)
    frequency_axis = build_frequency_axis_for_cut(cut, options)
    frequencies_hz = override_frequencies_hz or frequency_axis.values_hz

    result = ImpedanceComputation(
        frequencies=frequencies_hz,
        main_bore=main_bore,
        holes_valves=holes_valves,
        unit=options.unit,
        diameter=options.diameter,
        temperature=options.temperature_c,
        humidity=options.humidity,
        radiation_category=options.radiation_category,
        losses=options.losses,
        compute_method=options.compute_method,
        source_location=options.source_location,
    )
    return result
