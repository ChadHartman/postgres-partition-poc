CREATE TABLE IF NOT EXISTS log_{} PARTITION OF log
    FOR VALUES FROM ('{}') TO ('{}');