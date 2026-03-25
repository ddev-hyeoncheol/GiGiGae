CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS vector;

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
    registration_date DATE,

    -- 추가: 상표 출원 분석 강화
    applicant VARCHAR(500),               -- 출원인
    final_right_holder VARCHAR(500),       -- 최종권리자
    publication_no VARCHAR(50),            -- 출원공고번호
    publication_date DATE,                 -- 출원공고일자
    design_code VARCHAR(200),             -- 도형코드 (도형상표 유사도 분석용)
    image_path VARCHAR(500),              -- 대표견본 이미지 경로
    image_embedding vector(512)           -- CLIP 이미지 임베딩 벡터
);

-- 검색 성능 인덱스
CREATE INDEX IF NOT EXISTS idx_trademarks_name ON trademarks (name);
CREATE INDEX IF NOT EXISTS idx_trademarks_nice_class ON trademarks (nice_class);
CREATE INDEX IF NOT EXISTS idx_trademarks_legal_status ON trademarks (legal_status);
CREATE INDEX IF NOT EXISTS idx_trademarks_name_type ON trademarks (name_type);

-- pg_trgm 유사도 검색용 GIN 인덱스
CREATE INDEX IF NOT EXISTS idx_trademarks_name_trgm ON trademarks USING GIN (name gin_trgm_ops);

-- pgvector 이미지 유사도 검색용 HNSW 인덱스
CREATE INDEX IF NOT EXISTS idx_trademarks_image_embedding ON trademarks
    USING hnsw (image_embedding vector_cosine_ops);
