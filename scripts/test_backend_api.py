from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.api.app import app


def main() -> None:
    client = TestClient(app)

    payload = {
        "kind": "base",
        "d": 9.0,
        "x": 160.0,
        "y": 6.0,
        "a": 150.0,
        "Dt": 12.0,
        "L": 570.0,
        "Di": 18.0,
    }

    compute_response = client.post("/api/flutes", json=payload)
    compute_response.raise_for_status()
    computed = compute_response.json()

    curve_response = client.get(f"/api/flutes/{computed['instrument_id']}/curve")
    curve_response.raise_for_status()
    visualization_response = client.get(
        f"/api/flutes/{computed['instrument_id']}/visualization"
    )
    visualization_response.raise_for_status()

    print(
        json.dumps(
            {
                "compute_status": compute_response.status_code,
                "curve_status": curve_response.status_code,
                "visualization_status": visualization_response.status_code,
                "computed": computed,
                "stored_curve": curve_response.json(),
                "visualization": visualization_response.json(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
