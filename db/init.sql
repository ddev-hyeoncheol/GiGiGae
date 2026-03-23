CREATE SEQUENCE IF NOT EXISTS trademarks_id_seq;

CREATE TABLE IF NOT EXISTS trademarks (
    id BIGINT PRIMARY KEY DEFAULT nextval('trademarks_id_seq'),

    -- 필수: 상표 유사도 검색 핵심
    name VARCHAR(500) NOT NULL,
    nice_class VARCHAR(200),
    application_no VARCHAR(50) UNIQUE NOT NULL,
    legal_status VARCHAR(50),

    -- 유용: 분석 품질 향상
    application_date DATE,
    name_type VARCHAR(50),
    review_status VARCHAR(50),
    registration_no VARCHAR(50),
    registration_date DATE
);

-- 검색 성능 인덱스
CREATE INDEX IF NOT EXISTS idx_trademarks_name ON trademarks (name);
CREATE INDEX IF NOT EXISTS idx_trademarks_nice_class ON trademarks (nice_class);
CREATE INDEX IF NOT EXISTS idx_trademarks_legal_status ON trademarks (legal_status);
CREATE INDEX IF NOT EXISTS idx_trademarks_name_type ON trademarks (name_type);
