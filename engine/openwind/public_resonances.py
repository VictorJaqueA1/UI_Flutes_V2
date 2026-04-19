from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class PublicResonanceSelection:
    frequencies_hz: list[float]
    f1_hz: float | None
    f2_hz: float | None
    delta_cents: float | None


def extract_public_resonances(result, count: int = 5) -> PublicResonanceSelection:
    resonance_values = list(map(float, result.resonance_frequencies(k=count)))
    f1_hz = resonance_values[0] if len(resonance_values) >= 1 else None
    f2_hz = resonance_values[1] if len(resonance_values) >= 2 else None
    delta_cents = None

    if f1_hz and f2_hz:
        delta_cents = 1200.0 * math.log2(f2_hz / (2.0 * f1_hz))

    return PublicResonanceSelection(
        frequencies_hz=resonance_values,
        f1_hz=f1_hz,
        f2_hz=f2_hz,
        delta_cents=delta_cents,
    )
