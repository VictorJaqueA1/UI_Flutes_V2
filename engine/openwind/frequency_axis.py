from __future__ import annotations

from dataclasses import dataclass
from typing import List

from engine.models import CutRequest, FluteGeometry, OpenWindOptions


@dataclass(frozen=True)
class FrequencyAxis:
    values_hz: List[float]
    f1_estimate_hz: float
    minimum_hz: float
    maximum_hz: float
    step_hz: float
    rationale: str


def build_frequency_axis_for_cut(
    cut: CutRequest,
    options: OpenWindOptions,
    step_hz: float = 2.0,
) -> FrequencyAxis:
    speed_of_sound = 331.0 + (0.6 * options.temperature_c)
    cut_length_m = cut.length_mm / 1000.0
    f1_estimate_hz = speed_of_sound / (2.0 * cut_length_m)

    minimum_hz = max(20.0, 0.50 * f1_estimate_hz)
    maximum_hz = min(5000.0, 5.00 * f1_estimate_hz)

    values_hz: List[float] = []
    current = minimum_hz

    while current <= maximum_hz + 1e-9:
        values_hz.append(round(current, 10))
        current += step_hz

    return FrequencyAxis(
        values_hz=values_hz,
        f1_estimate_hz=f1_estimate_hz,
        minimum_hz=minimum_hz,
        maximum_hz=maximum_hz,
        step_hz=step_hz,
        rationale=(
            "Barrido pragmático basado en una estimación open-open de la "
            "frecuencia fundamental del corte. No son las frecuencias "
            "resonantes finales: son el eje de muestreo para calcular Z(f)."
        ),
    )


def build_legacy_global_frequency_axis(
    flute: FluteGeometry,
    options: OpenWindOptions,
    step_hz: float = 2.0,
) -> FrequencyAxis:
    speed_of_sound = 331.0 + (0.6 * options.temperature_c)
    shortest_cut_m = (flute.L / 2.0) / 1000.0
    f1_max_estimate_hz = speed_of_sound / (2.0 * shortest_cut_m)
    maximum_hz = min(6000.0, max(2200.0, 2.0 * f1_max_estimate_hz * 1.2))
    minimum_hz = 20.0

    values_hz: List[float] = []
    current = minimum_hz

    while current < maximum_hz - 1e-9:
        values_hz.append(round(current, 10))
        current += step_hz

    return FrequencyAxis(
        values_hz=values_hz,
        f1_estimate_hz=f1_max_estimate_hz,
        minimum_hz=minimum_hz,
        maximum_hz=maximum_hz,
        step_hz=step_hz,
        rationale=(
            "Barrido global heredado: 20 Hz hasta un maximo derivado del corte "
            "mas corto (L/2), reutilizado para todos los cortes de una misma flauta."
        ),
    )
