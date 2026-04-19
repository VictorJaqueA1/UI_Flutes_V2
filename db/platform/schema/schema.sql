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
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    calculation_method TEXT NOT NULL,
    loss_model TEXT NOT NULL,
    resonance_method TEXT NOT NULL,
    frequency_axis_min_hz REAL NOT NULL,
    frequency_axis_max_hz REAL NOT NULL,
    frequency_axis_step_hz REAL NOT NULL,
    calculation_signature TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_instruments_signature
ON instruments(kind, d_mm, x_mm, y_mm, a_mm, dt_mm, l_mm, di_mm, calculation_signature);

CREATE INDEX IF NOT EXISTS idx_instruments_kind
ON instruments(kind);

CREATE TABLE IF NOT EXISTS curve_points (
    instrument_id INTEGER NOT NULL REFERENCES instruments(instrument_id) ON DELETE CASCADE,
    cut_index INTEGER NOT NULL,
    cut_length_mm REAL NOT NULL,
    f1_hz REAL NOT NULL,
    f2_hz REAL NOT NULL,
    delta_cents REAL NOT NULL,
    PRIMARY KEY (instrument_id, cut_index)
);

CREATE INDEX IF NOT EXISTS idx_curve_points_instrument
ON curve_points(instrument_id);

CREATE TABLE IF NOT EXISTS rmse_pairs (
    base_instrument_id INTEGER NOT NULL REFERENCES instruments(instrument_id) ON DELETE CASCADE,
    inverse_instrument_id INTEGER NOT NULL REFERENCES instruments(instrument_id) ON DELETE CASCADE,
    rmse REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (base_instrument_id, inverse_instrument_id)
);

CREATE INDEX IF NOT EXISTS idx_rmse_pairs_inverse
ON rmse_pairs(inverse_instrument_id);

CREATE TABLE IF NOT EXISTS best_inverse_for_base (
    base_instrument_id INTEGER PRIMARY KEY REFERENCES instruments(instrument_id) ON DELETE CASCADE,
    inverse_instrument_id INTEGER NOT NULL REFERENCES instruments(instrument_id) ON DELETE CASCADE,
    rmse REAL NOT NULL,
    selected_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS best_base_for_inverse (
    inverse_instrument_id INTEGER PRIMARY KEY REFERENCES instruments(instrument_id) ON DELETE CASCADE,
    base_instrument_id INTEGER NOT NULL REFERENCES instruments(instrument_id) ON DELETE CASCADE,
    rmse REAL NOT NULL,
    selected_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
