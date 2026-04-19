from __future__ import annotations

import math
from typing import Iterable, Sequence


def compute_rmse(values_a: Sequence[float], values_b: Sequence[float]) -> float:
    if len(values_a) != len(values_b):
        raise ValueError("RMSE requiere vectores del mismo largo.")
    if not values_a:
        raise ValueError("RMSE requiere al menos un valor.")

    mean_square = sum((a - b) ** 2 for a, b in zip(values_a, values_b)) / len(values_a)
    return math.sqrt(mean_square)


def compute_rmse_from_curve_results(curve_a, curve_b) -> float:
    deltas_a = [point.delta_cents for point in curve_a.points]
    deltas_b = [point.delta_cents for point in curve_b.points]
    return compute_rmse(deltas_a, deltas_b)
