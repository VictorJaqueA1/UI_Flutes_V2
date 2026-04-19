from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db.replication.repositories import ReplicationDatabase


def main() -> None:
    database = ReplicationDatabase()
    database.initialize()
    print(f"Replication DB initialized at: {database.db_path}")


if __name__ == "__main__":
    main()
