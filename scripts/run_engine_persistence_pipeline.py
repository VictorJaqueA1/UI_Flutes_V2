from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.models import FluteGeometry, FluteKind
from engine.services import build_modal_public_options, compute_and_store_flute


def build_base_demo_flute() -> FluteGeometry:
    return FluteGeometry(
        kind=FluteKind.BASE,
        d=9.0,
        x=160.0,
        y=6.0,
        a=150.0,
        Dt=12.0,
    )


def build_inverse_demo_flute() -> FluteGeometry:
    return FluteGeometry(
        kind=FluteKind.INVERSE,
        d=9.0,
        x=160.0,
        y=6.0,
        a=150.0,
        Dt=12.0,
    )


def main() -> None:
    options = build_modal_public_options()
    base_result = compute_and_store_flute(build_base_demo_flute(), options=options)
    inverse_result = compute_and_store_flute(build_inverse_demo_flute(), options=options)
    print(
        json.dumps(
            {
                "base": base_result.__dict__,
                "inverse": inverse_result.__dict__,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
