from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schema" / "schema.sql"
DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "replication_inputs.sqlite3"


@dataclass(frozen=True)
class ReplicationInstrumentRecord:
    instrument_id: int | None
    kind: str
    d_mm: float
    x_mm: float
    y_mm: float
    a_mm: float
    dt_mm: float
    l_mm: float
    di_mm: float


@dataclass(frozen=True)
class ReplicationRunRecord:
    instrument_id: int
    engine_version: str
    openwind_version: str
    calculation_method: str
    loss_model: str
    resonance_method: str
    source_location: str
    notes: str = ""


class ReplicationDatabase:
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

    def insert_instrument(self, record: ReplicationInstrumentRecord) -> int:
        with self.connect() as connection:
            if record.instrument_id is not None:
                connection.execute(
                    """
                    INSERT OR REPLACE INTO instruments (
                        instrument_id, kind, d_mm, x_mm, y_mm, a_mm, dt_mm, l_mm, di_mm
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.instrument_id,
                        record.kind,
                        record.d_mm,
                        record.x_mm,
                        record.y_mm,
                        record.a_mm,
                        record.dt_mm,
                        record.l_mm,
                        record.di_mm,
                    ),
                )
                connection.commit()
                return int(record.instrument_id)

            cursor = connection.execute(
                """
                INSERT INTO instruments (
                    kind, d_mm, x_mm, y_mm, a_mm, dt_mm, l_mm, di_mm
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
                ),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def insert_run(self, record: ReplicationRunRecord) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO calculation_runs (
                    instrument_id, engine_version, openwind_version,
                    calculation_method, loss_model, resonance_method,
                    source_location, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.instrument_id,
                    record.engine_version,
                    record.openwind_version,
                    record.calculation_method,
                    record.loss_model,
                    record.resonance_method,
                    record.source_location,
                    record.notes,
                ),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def replace_input_parameters(self, run_id: int, rows: Iterable[dict]) -> None:
        with self.connect() as connection:
            connection.execute(
                "DELETE FROM run_input_parameters WHERE run_id = ?",
                (run_id,),
            )
            connection.executemany(
                """
                INSERT INTO run_input_parameters (
                    run_id, input_name, input_value, input_unit,
                    input_origin, was_provided, used_default, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        run_id,
                        row["input_name"],
                        row["input_value"],
                        row.get("input_unit"),
                        row["input_origin"],
                        int(bool(row["was_provided"])),
                        int(bool(row["used_default"])),
                        row.get("description"),
                    )
                    for row in rows
                ],
            )
            connection.commit()

    def replace_input_payloads(self, run_id: int, rows: Iterable[dict]) -> None:
        with self.connect() as connection:
            connection.execute(
                "DELETE FROM run_input_payloads WHERE run_id = ?",
                (run_id,),
            )
            connection.executemany(
                """
                INSERT INTO run_input_payloads (
                    run_id, payload_name, payload_format, payload_value, description
                ) VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        run_id,
                        row["payload_name"],
                        row["payload_format"],
                        row["payload_value"],
                        row.get("description"),
                    )
                    for row in rows
                ],
            )
            connection.commit()

    def replace_cut_runs(self, run_id: int, cut_lengths_mm: Iterable[float]) -> None:
        with self.connect() as connection:
            connection.execute(
                "DELETE FROM cut_runs WHERE run_id = ?",
                (run_id,),
            )
            connection.executemany(
                """
                INSERT INTO cut_runs (run_id, cut_index, cut_length_mm)
                VALUES (?, ?, ?)
                """,
                [
                    (run_id, index, float(length_mm))
                    for index, length_mm in enumerate(cut_lengths_mm, start=1)
                ],
            )
            connection.commit()

    def upsert_run_output_core(
        self,
        run_id: int,
        zc: float,
        frequencies_payload_name: str = "frequencies",
        impedance_storage_mode: str = "json_per_cut",
    ) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO run_output_core (
                    run_id, zc, frequencies_payload_name, impedance_storage_mode
                ) VALUES (?, ?, ?, ?)
                ON CONFLICT(run_id)
                DO UPDATE SET
                    zc = excluded.zc,
                    frequencies_payload_name = excluded.frequencies_payload_name,
                    impedance_storage_mode = excluded.impedance_storage_mode
                """,
                (run_id, float(zc), frequencies_payload_name, impedance_storage_mode),
            )
            connection.commit()

    def replace_cut_output_resonances(self, run_id: int, rows: Iterable[dict]) -> None:
        with self.connect() as connection:
            connection.execute(
                "DELETE FROM cut_output_resonances WHERE run_id = ?",
                (run_id,),
            )
            connection.executemany(
                """
                INSERT INTO cut_output_resonances (
                    run_id, cut_index, f1_hz, f2_hz, delta_cents
                ) VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        run_id,
                        int(row["cut_index"]),
                        float(row["f1_hz"]),
                        float(row["f2_hz"]),
                        float(row["delta_cents"]),
                    )
                    for row in rows
                ],
            )
            connection.commit()

    def replace_cut_output_impedance(self, run_id: int, rows: Iterable[dict]) -> None:
        with self.connect() as connection:
            connection.execute(
                "DELETE FROM cut_output_impedance WHERE run_id = ?",
                (run_id,),
            )
            connection.executemany(
                """
                INSERT INTO cut_output_impedance (
                    run_id, cut_index, frequencies_json, impedance_real_json, impedance_imag_json
                ) VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        run_id,
                        int(row["cut_index"]),
                        row["frequencies_json"],
                        row["impedance_real_json"],
                        row["impedance_imag_json"],
                    )
                    for row in rows
                ],
            )
            connection.commit()
