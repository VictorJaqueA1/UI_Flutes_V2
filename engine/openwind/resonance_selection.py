from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class ResonanceSelection:
    f1_hint_hz: float
    f1_hz: float
    f2_hz: float
    f1_window_hz: tuple[float, float]
    f2_window_hz: tuple[float, float]
    delta_cents: float


def _find_minimum_in_window(
    frequencies_hz: Sequence[float],
    impedance_magnitude: Sequence[float],
    low_hz: float,
    high_hz: float,
) -> float | None:
    candidates = [
        (float(freq), float(magnitude))
        for freq, magnitude in zip(frequencies_hz, impedance_magnitude)
        if low_hz <= freq <= high_hz
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda item: item[1])[0]


def _find_global_minimum(
    frequencies_hz: Sequence[float],
    impedance_magnitude: Sequence[float],
) -> float:
    return min(
        zip(frequencies_hz, impedance_magnitude),
        key=lambda item: item[1],
    )[0]


def _find_minimum_above_threshold(
    frequencies_hz: Sequence[float],
    impedance_magnitude: Sequence[float],
    threshold_hz: float,
) -> float | None:
    candidates = [
        (float(freq), float(magnitude))
        for freq, magnitude in zip(frequencies_hz, impedance_magnitude)
        if freq > threshold_hz
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda item: item[1])[0]


def estimate_first_resonance_hint_hz(
    cut_length_mm: float,
    temperature_c: float,
) -> float:
    speed_of_sound = 331.0 + (0.6 * temperature_c)
    return speed_of_sound / (2.0 * (cut_length_mm / 1000.0))


def select_resonances_with_legacy_windows(
    frequencies_hz: Sequence[float],
    impedance_magnitude: Sequence[float],
    cut_length_mm: float,
    temperature_c: float,
) -> ResonanceSelection:
    # Metodo manual legado:
    # conserva la logica del codigo antiguo para comparacion y trazabilidad.
    # No debe considerarse la referencia principal mientras usemos
    # resonance_frequencies() como criterio provisional de trabajo.
    f1_hint_hz = estimate_first_resonance_hint_hz(cut_length_mm, temperature_c)
    f1_window_hz = (0.65 * f1_hint_hz, 1.35 * f1_hint_hz)

    f1_hz = _find_minimum_in_window(
        frequencies_hz,
        impedance_magnitude,
        f1_window_hz[0],
        f1_window_hz[1],
    )
    if f1_hz is None:
        f1_hz = _find_global_minimum(frequencies_hz, impedance_magnitude)

    f2_window_hz = (0.8 * 2.0 * f1_hz, 1.2 * 2.0 * f1_hz)
    f2_hz = _find_minimum_in_window(
        frequencies_hz,
        impedance_magnitude,
        f2_window_hz[0],
        f2_window_hz[1],
    )
    if f2_hz is None:
        f2_hz = _find_minimum_above_threshold(
            frequencies_hz,
            impedance_magnitude,
            1.2 * f1_hz,
        )
    if f2_hz is None:
        f2_hz = 2.0 * f1_hz

    delta_cents = 1200.0 * math.log2(f2_hz / (2.0 * f1_hz))

    # TODO: reemplazar este criterio de mínimos en ventana por una selección
    # explícita basada en métodos públicos de OpenWind o en compute_method='modal'
    # cuando definamos formalmente qué resonancias deben entrar en la inarmonicidad.
    return ResonanceSelection(
        f1_hint_hz=f1_hint_hz,
        f1_hz=f1_hz,
        f2_hz=f2_hz,
        f1_window_hz=f1_window_hz,
        f2_window_hz=f2_window_hz,
        delta_cents=delta_cents,
    )
