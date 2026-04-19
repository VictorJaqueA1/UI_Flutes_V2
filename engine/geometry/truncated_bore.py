from __future__ import annotations

from typing import List

from engine.models import CutRequest, FluteGeometry, FluteKind


EPS = 1e-9


def validate_cut_request(flute: FluteGeometry, cut: CutRequest) -> None:
    if not (flute.L / 2.0 <= cut.length_mm <= flute.L):
        raise ValueError(
            "El corte debe estar entre la mitad de la flauta y la longitud total."
        )


def _diameter_for_base_cut(flute: FluteGeometry, cut_length_mm: float) -> float:
    if flute.a >= cut_length_mm:
        return flute.Di

    fraction = (cut_length_mm - flute.a) / max(flute.L - flute.a, EPS)
    return flute.Di + (flute.Dt - flute.Di) * fraction


def _diameter_for_inverse_cut(flute: FluteGeometry, cut_length_mm: float) -> float:
    if flute.a <= 0.0:
        return flute.Di

    if cut_length_mm <= flute.a:
        fraction = cut_length_mm / max(flute.a, EPS)
        return flute.Dt + (flute.Di - flute.Dt) * fraction

    return flute.Di


def build_main_bore_for_cut(
    flute: FluteGeometry,
    cut: CutRequest,
) -> List[List[float | str]]:
    validate_cut_request(flute, cut)
    cut_length_mm = cut.length_mm

    if flute.kind == FluteKind.BASE:
        if flute.a >= cut_length_mm:
            return [[0.0, cut_length_mm, flute.Di, flute.Di, "linear"]]

        cut_diameter = _diameter_for_base_cut(flute, cut_length_mm)
        return [
            [0.0, flute.a, flute.Di, flute.Di, "linear"],
            [flute.a, cut_length_mm, flute.Di, cut_diameter, "linear"],
        ]

    if flute.a <= 0.0:
        return [[0.0, cut_length_mm, flute.Di, flute.Di, "linear"]]

    if cut_length_mm <= flute.a:
        cut_diameter = _diameter_for_inverse_cut(flute, cut_length_mm)
        return [[0.0, cut_length_mm, flute.Dt, cut_diameter, "linear"]]

    return [
        [0.0, flute.a, flute.Dt, flute.Di, "linear"],
        [flute.a, cut_length_mm, flute.Di, flute.Di, "linear"],
    ]


def build_embouchure_hole_table(flute: FluteGeometry) -> List[List[float | str]]:
    return [
        ["label", "location", "diameter", "chimney"],
        ["embouchure", flute.x, flute.d, flute.y],
    ]
