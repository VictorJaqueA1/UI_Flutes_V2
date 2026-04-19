from __future__ import annotations

import hashlib
import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SCHEMA_PATH = (
    Path(__file__).resolve().parents[1] / "schema" / "schema.sql"
)
DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "platform_operational.sqlite3"


@dataclass(frozen=True)
class PlatformInstrumentRecord:
    kind: str
    d_mm: float
    x_mm: float
    y_mm: float
    a_mm: float
    dt_mm: float
    l_mm: float
    di_mm: float
    calculation_method: str
    loss_model: str
    resonance_method: str
    frequency_axis_min_hz: float
    frequency_axis_max_hz: float
    frequency_axis_step_hz: float

    def calculation_signature(self) -> str:
        raw = "|".join(
            [
                self.kind,
                f"{self.d_mm:.12f}",
                f"{self.x_mm:.12f}",
                f"{self.y_mm:.12f}",
                f"{self.a_mm:.12f}",
                f"{self.dt_mm:.12f}",
                f"{self.l_mm:.12f}",
                f"{self.di_mm:.12f}",
                self.calculation_method,
                self.loss_model,
                self.resonance_method,
                f"{self.frequency_axis_min_hz:.12f}",
                f"{self.frequency_axis_max_hz:.12f}",
                f"{self.frequency_axis_step_hz:.12f}",
            ]
        )
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()


class PlatformDatabase:
    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON;")
        return connection

    def initialize(self) -> None:
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        with self.connect() as connection:
            connection.executescript(schema_sql)
            connection.commit()

    def get_or_create_instrument_id(self, record: PlatformInstrumentRecord) -> int:
        signature = record.calculation_signature()
        with self.connect() as connection:
            existing = connection.execute(
                """
                SELECT instrument_id
                FROM instruments
                WHERE kind = ?
                  AND d_mm = ?
                  AND x_mm = ?
                  AND y_mm = ?
                  AND a_mm = ?
                  AND dt_mm = ?
                  AND l_mm = ?
                  AND di_mm = ?
                  AND calculation_signature = ?
                """,
                (
                    record.kind,
                    record.d_mm,
                    record.x_mm,
                    record.y_mm,
                    record.a_mm,
                    record.dt_mm,
                    record.l_mm,
                    record.di_mm,
                    signature,
                ),
            ).fetchone()
            if existing:
                return int(existing["instrument_id"])

            cursor = connection.execute(
                """
                INSERT INTO instruments (
                    kind, d_mm, x_mm, y_mm, a_mm, dt_mm, l_mm, di_mm,
                    calculation_method, loss_model, resonance_method,
                    frequency_axis_min_hz, frequency_axis_max_hz, frequency_axis_step_hz,
                    calculation_signature
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.kind,
                    record.d_mm,
                    record.x_mm,
                    record.y_mm,
                    record.a_mm,
                    record.dt_mm,
                    record.l_mm,
                    record.di_mm,
                    record.calculation_method,
                    record.loss_model,
                    record.resonance_method,
                    record.frequency_axis_min_hz,
                    record.frequency_axis_max_hz,
                    record.frequency_axis_step_hz,
                    signature,
                ),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def replace_curve_points(self, instrument_id: int, points: Iterable[dict]) -> None:
        with self.connect() as connection:
            connection.execute(
                "DELETE FROM curve_points WHERE instrument_id = ?",
                (instrument_id,),
            )
            connection.executemany(
                """
                INSERT INTO curve_points (
                    instrument_id, cut_index, cut_length_mm, f1_hz, f2_hz, delta_cents
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        instrument_id,
                        index,
                        float(point["cut_length_mm"]),
                        float(point["f1_hz"]),
                        float(point["f2_hz"]),
                        float(point["delta_cents"]),
                    )
                    for index, point in enumerate(points, start=1)
                ],
            )
            connection.commit()

    def upsert_rmse_pair(self, base_instrument_id: int, inverse_instrument_id: int, rmse: float) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO rmse_pairs (
                    base_instrument_id, inverse_instrument_id, rmse, updated_at
                )
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(base_instrument_id, inverse_instrument_id)
                DO UPDATE SET
                    rmse = excluded.rmse,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (base_instrument_id, inverse_instrument_id, float(rmse)),
            )
            connection.commit()

    def refresh_best_inverse_for_base(self, base_instrument_id: int) -> None:
        with self.connect() as connection:
            best = connection.execute(
                """
                SELECT inverse_instrument_id, rmse
                FROM rmse_pairs
                WHERE base_instrument_id = ?
                ORDER BY rmse ASC, inverse_instrument_id ASC
                LIMIT 1
                """,
                (base_instrument_id,),
            ).fetchone()
            if not best:
                return
            connection.execute(
                """
                INSERT INTO best_inverse_for_base (
                    base_instrument_id, inverse_instrument_id, rmse, selected_at
                )
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(base_instrument_id)
                DO UPDATE SET
                    inverse_instrument_id = excluded.inverse_instrument_id,
                    rmse = excluded.rmse,
                    selected_at = CURRENT_TIMESTAMP
                """,
                (
                    base_instrument_id,
                    int(best["inverse_instrument_id"]),
                    float(best["rmse"]),
                ),
            )
            connection.commit()

    def refresh_best_base_for_inverse(self, inverse_instrument_id: int) -> None:
        with self.connect() as connection:
            best = connection.execute(
                """
                SELECT base_instrument_id, rmse
                FROM rmse_pairs
                WHERE inverse_instrument_id = ?
                ORDER BY rmse ASC, base_instrument_id ASC
                LIMIT 1
                """,
                (inverse_instrument_id,),
            ).fetchone()
            if not best:
                return
            connection.execute(
                """
                INSERT INTO best_base_for_inverse (
                    inverse_instrument_id, base_instrument_id, rmse, selected_at
                )
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(inverse_instrument_id)
                DO UPDATE SET
                    base_instrument_id = excluded.base_instrument_id,
                    rmse = excluded.rmse,
                    selected_at = CURRENT_TIMESTAMP
                """,
                (
                    inverse_instrument_id,
                    int(best["base_instrument_id"]),
                    float(best["rmse"]),
                ),
            )
            connection.commit()

    def list_rmse_pairs_sorted(self) -> list[sqlite3.Row]:
        with self.connect() as connection:
            return connection.execute(
                """
                SELECT base_instrument_id, inverse_instrument_id, rmse
                FROM rmse_pairs
                ORDER BY rmse ASC, base_instrument_id ASC, inverse_instrument_id ASC
                """,
            ).fetchall()

    def list_best_pairs_sorted(self) -> list[sqlite3.Row]:
        with self.connect() as connection:
            return connection.execute(
                """
                SELECT
                    base_instrument_id,
                    inverse_instrument_id,
                    MIN(rmse) AS rmse,
                    CASE
                        WHEN MIN(anchor_kind) = 'base'
                        THEN base_instrument_id
                        ELSE inverse_instrument_id
                    END AS anchor_instrument_id
                FROM (
                    SELECT base_instrument_id, inverse_instrument_id, rmse, 'base' AS anchor_kind
                    FROM best_inverse_for_base
                    UNION ALL
                    SELECT base_instrument_id, inverse_instrument_id, rmse, 'inverse' AS anchor_kind
                    FROM best_base_for_inverse
                )
                GROUP BY base_instrument_id, inverse_instrument_id
                ORDER BY MIN(rmse) ASC, base_instrument_id ASC, inverse_instrument_id ASC
                """,
            ).fetchall()

    def list_instrument_ids_by_kind(self, kind: str) -> list[int]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT instrument_id
                FROM instruments
                WHERE kind = ?
                ORDER BY instrument_id ASC
                """,
                (kind,),
            ).fetchall()
            return [int(row["instrument_id"]) for row in rows]

    def list_instruments(self, kind: str | None = None) -> list[sqlite3.Row]:
        with self.connect() as connection:
            if kind is None:
                rows = connection.execute(
                    """
                    SELECT *
                    FROM instruments
                    ORDER BY kind ASC, instrument_id ASC
                    """
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT *
                    FROM instruments
                    WHERE kind = ?
                    ORDER BY instrument_id ASC
                    """,
                    (kind,),
                ).fetchall()
            return list(rows)

    def get_curve_points(self, instrument_id: int) -> list[sqlite3.Row]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT cut_index, cut_length_mm, f1_hz, f2_hz, delta_cents
                FROM curve_points
                WHERE instrument_id = ?
                ORDER BY cut_index ASC
                """,
                (instrument_id,),
            ).fetchall()
            return list(rows)

    def get_curve_points_by_instrument_ids(
        self,
        instrument_ids: Iterable[int],
    ) -> dict[int, list[sqlite3.Row]]:
        normalized_ids = [int(instrument_id) for instrument_id in instrument_ids]
        if not normalized_ids:
            return {}

        placeholders = ", ".join("?" for _ in normalized_ids)
        grouped: dict[int, list[sqlite3.Row]] = defaultdict(list)

        with self.connect() as connection:
            rows = connection.execute(
                f"""
                SELECT instrument_id, cut_index, cut_length_mm, f1_hz, f2_hz, delta_cents
                FROM curve_points
                WHERE instrument_id IN ({placeholders})
                ORDER BY instrument_id ASC, cut_index ASC
                """,
                normalized_ids,
            ).fetchall()

        for row in rows:
            grouped[int(row["instrument_id"])].append(row)

        return dict(grouped)

    def get_curve_deltas(self, instrument_id: int) -> list[float]:
        return [
            float(row["delta_cents"])
            for row in self.get_curve_points(instrument_id)
        ]

    def get_instrument(self, instrument_id: int) -> sqlite3.Row | None:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM instruments
                WHERE instrument_id = ?
                """,
                (instrument_id,),
            ).fetchone()
            return row

    def get_best_inverse_for_base(self, base_instrument_id: int) -> sqlite3.Row | None:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT base_instrument_id, inverse_instrument_id, rmse, selected_at
                FROM best_inverse_for_base
                WHERE base_instrument_id = ?
                """,
                (base_instrument_id,),
            ).fetchone()
            return row

    def get_best_base_for_inverse(self, inverse_instrument_id: int) -> sqlite3.Row | None:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT inverse_instrument_id, base_instrument_id, rmse, selected_at
                FROM best_base_for_inverse
                WHERE inverse_instrument_id = ?
                """,
                (inverse_instrument_id,),
            ).fetchone()
            return row
