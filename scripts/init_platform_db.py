from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db.platform.repositories import PlatformDatabase


def main() -> None:
    database = PlatformDatabase()
    database.initialize()
    print(f"Platform DB initialized at: {database.db_path}")


if __name__ == "__main__":
    main()
