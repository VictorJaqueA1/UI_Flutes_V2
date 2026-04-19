from __future__ import annotations

from typing import List


def generate_equal_cuts(
    total_length_mm: float,
    minimum_length_mm: float,
    count: int = 10,
) -> List[float]:
    if count < 2:
        return [float(total_length_mm)]

    step = (total_length_mm - minimum_length_mm) / (count - 1)
    return [float(total_length_mm - (index * step)) for index in range(count)]
