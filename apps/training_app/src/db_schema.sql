CREATE TABLE IF NOT EXISTS training_history (
    run_id SERIAL PRIMARY KEY,
    batch_id UUID NOT NULL,         -- unique ID to group all 11x11 jobs from one "run"
    source_table TEXT NOT NULL,     -- e.g. 'sensor_data_1'
    target_column TEXT NOT NULL,    -- e.g. 'temperature'
    
    -- Data Context
    rows_limit INTEGER NOT NULL,
    time_start TIMESTAMP,           -- Training job start time
    time_end TIMESTAMP,             -- Training job end time
    
    -- Model Artifacts
    algorithm TEXT DEFAULT 'LSTM',
    model_object BYTEA,             -- Stores Python ML model object
    model_weights JSONB,            -- Stores ML model's weights
    metrics JSONB,                  -- Stores ML model's metrics
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast data selection
CREATE INDEX IF NOT EXISTS idx_model_lookup ON training_history (batch_id, source_table, target_column);