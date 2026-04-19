PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS instruments (
    instrument_id INTEGER PRIMARY KEY,
    kind TEXT NOT NULL CHECK(kind IN ('base', 'inverse')),
    d_mm REAL NOT NULL,
    x_mm REAL NOT NULL,
    y_mm REAL NOT NULL,
    a_mm REAL NOT NULL,
    dt_mm REAL NOT NULL,
    l_mm REAL NOT NULL,
    di_mm REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS calculation_runs (
    run_id INTEGER PRIMARY KEY,
    instrument_id INTEGER NOT NULL REFERENCES instruments(instrument_id) ON DELETE CASCADE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    engine_version TEXT NOT NULL,
    openwind_version TEXT NOT NULL,
    calculation_method TEXT NOT NULL,
    loss_model TEXT NOT NULL,
    resonance_method TEXT NOT NULL,
    source_location TEXT NOT NULL,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_runs_instrument
ON calculation_runs(instrument_id);

CREATE TABLE IF NOT EXISTS run_input_parameters (
    run_id INTEGER NOT NULL REFERENCES calculation_runs(run_id) ON DELETE CASCADE,
    input_name TEXT NOT NULL,
    input_value TEXT NOT NULL,
    input_unit TEXT,
    input_origin TEXT NOT NULL CHECK(input_origin IN ('explicit', 'default', 'derived')),
    was_provided INTEGER NOT NULL CHECK(was_provided IN (0, 1)),
    used_default INTEGER NOT NULL CHECK(used_default IN (0, 1)),
    description TEXT,
    PRIMARY KEY (run_id, input_name)
);

CREATE TABLE IF NOT EXISTS run_input_payloads (
    run_id INTEGER NOT NULL REFERENCES calculation_runs(run_id) ON DELETE CASCADE,
    payload_name TEXT NOT NULL,
    payload_format TEXT NOT NULL,
    payload_value TEXT NOT NULL,
    description TEXT,
    PRIMARY KEY (run_id, payload_name)
);

CREATE TABLE IF NOT EXISTS cut_runs (
    run_id INTEGER NOT NULL REFERENCES calculation_runs(run_id) ON DELETE CASCADE,
    cut_index INTEGER NOT NULL,
    cut_length_mm REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (run_id, cut_index)
);

CREATE INDEX IF NOT EXISTS idx_cut_runs_run
ON cut_runs(run_id);

CREATE TABLE IF NOT EXISTS run_output_core (
    run_id INTEGER PRIMARY KEY REFERENCES calculation_runs(run_id) ON DELETE CASCADE,
    zc REAL NOT NULL,
    frequencies_payload_name TEXT NOT NULL,
    impedance_storage_mode TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cut_output_resonances (
    run_id INTEGER NOT NULL REFERENCES calculation_runs(run_id) ON DELETE CASCADE,
    cut_index INTEGER NOT NULL,
    f1_hz REAL NOT NULL,
    f2_hz REAL NOT NULL,
    delta_cents REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (run_id, cut_index)
);

CREATE INDEX IF NOT EXISTS idx_cut_output_resonances_run
ON cut_output_resonances(run_id);

CREATE TABLE IF NOT EXISTS cut_output_impedance (
    run_id INTEGER NOT NULL REFERENCES calculation_runs(run_id) ON DELETE CASCADE,
    cut_index INTEGER NOT NULL,
    frequencies_json TEXT NOT NULL,
    impedance_real_json TEXT NOT NULL,
    impedance_imag_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (run_id, cut_index)
);

CREATE INDEX IF NOT EXISTS idx_cut_output_impedance_run
ON cut_output_impedance(run_id);
