CREATE TABLE IF NOT EXISTS trademarks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    nice_class VARCHAR(100),
    application_no VARCHAR(50) UNIQUE,
    application_date DATE,
    registration_no VARCHAR(50),
    registration_date DATE,
    legal_status VARCHAR(50),
    trademark_type VARCHAR(50),
    english_name VARCHAR(500)
);

CREATE INDEX IF NOT EXISTS idx_trademarks_name ON trademarks (name);
CREATE INDEX IF NOT EXISTS idx_trademarks_english_name ON trademarks (english_name);
CREATE INDEX IF NOT EXISTS idx_trademarks_legal_status ON trademarks (legal_status);
