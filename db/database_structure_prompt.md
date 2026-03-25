# Database Structure - 작업 지시서

> 생성일: 2026-03-23
> 최종 수정: 2026-03-26
> 프로젝트: GiGiGae (AI 기반 브랜드 론칭 자동화 서비스)

---

## 개요

상표권 데이터를 PostgreSQL(pgvector)에 적재하고, 백엔드에서 pg_trgm 텍스트 유사도 + pgvector 이미지 유사도 검색을 제공한다.

---

## 단계별 구현 계획

### 1단계: Docker Compose에 PostgreSQL 컨테이너 추가 `[구현 완료]`

- `docker-compose.yml`에 `pgvector/pgvector:pg16` 서비스 추가
- `./db/pgdata` 로컬 바인드 마운트로 데이터 영속화
- `./db/init.sql`을 `/docker-entrypoint-initdb.d/init.sql`로 마운트 (최초 기동 시 자동 실행)
- `./image` → `/data/image` 공유 볼륨 (back-end, db 컨테이너 공유)
- `./model` → `/data/model` 공유 볼륨 (CLIP 모델 캐시, back-end 전용)
- `back-end` 서비스에 `depends_on: db` 및 `DATABASE_URL` 환경변수 주입

### 2단계: 테이블 스키마 + 데이터 적재 `[구현 완료]`

- `db/init.sql` 생성 (pg_trgm + vector 확장 + 테이블 DDL + 인덱스)
- 데이터 적재 스크립트 3단계로 분리:
  - `db/seed_trademarks_lite.py`: 텍스트 데이터만 빠르게 적재 (이미지/임베딩 제외)
  - `db/seed_images.py`: 이미지 추출 + DB `image_path` 업데이트
  - `db/seed_embeddings.py`: `image_path` 있는 레코드 대상 CLIP 임베딩 배치 생성
  - `db/seed_trademarks.py`: 텍스트 + 이미지 + 임베딩 일괄 적재 (기존 통합 버전)

### 3단계: 백엔드 상표 검색 API 통합 `[구현 완료]`

- `app/core/database.py`에서 asyncpg 커넥션 풀 관리
- `app/services/trademark_service.py`에서 pg_trgm 텍스트 유사도 + pgvector 이미지 유사도 검색 + 위험도 판별 (Low / Middle / High)
- `app/api/trademark.py`에서 `POST /api/v1/trademark/search` + `POST /api/v1/trademark/image-search` 엔드포인트 제공
- `app/services/recommend_service.py`에서 LLM 추천 후 각 후보별 상표 검색 자동 수행 (카테고리 → 니스 분류 필터)
- 니스 분류 필터 결과 0건 시 전체 검색 폴백
- 18만건 상표 데이터 + 이미지 + 임베딩 적재 완료

---

## 디렉토리 구조

```
db/
├── init.sql                 # pg_trgm + vector 확장 + 테이블 생성 DDL + 인덱스
├── seed_trademarks_lite.py  # xlsx → 텍스트 데이터만 DB 적재 (빠른 적재용)
├── seed_images.py           # xlsx → 이미지 추출 + DB image_path 업데이트
├── seed_embeddings.py       # image_path 있는 레코드에 CLIP 임베딩 배치 생성
├── seed_trademarks.py       # xlsx → 이미지 추출 + CLIP 임베딩 + DB 적재 (통합)
├── requirements.txt         # 적재 스크립트 의존성
├── data/                    # xlsx 원본 데이터 (.gitignore)
└── pgdata/                  # PostgreSQL 데이터 디렉토리 (.gitignore)

image/                       # 상표 이미지 (Docker 공유 볼륨, .gitignore)
model/                       # CLIP 모델 캐시 (Docker 공유 볼륨, .gitignore)
```

---

## 핵심 구현 상세

### 1. 테이블 스키마 (`db/init.sql`)

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS vector;

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
    applicant VARCHAR(500),
    final_right_holder VARCHAR(500),
    publication_no VARCHAR(50),
    publication_date DATE,
    design_code VARCHAR(200),
    image_path VARCHAR(500),
    image_embedding vector(512)          -- CLIP 이미지 임베딩
);

-- 인덱스
CREATE INDEX idx_trademarks_name_trgm ON trademarks USING GIN (name gin_trgm_ops);
CREATE INDEX idx_trademarks_image_embedding ON trademarks USING hnsw (image_embedding vector_cosine_ops);
```

### 2. 데이터 적재 스크립트

**`seed_trademarks_lite.py`** (권장: 빠른 초기 적재):
- `zipfile` + `xml.etree`로 xlsx 직접 XML 파싱 (openpyxl 스타일 오류 우회)
- `psycopg2` + `execute_batch`로 DB 배치 INSERT (500건 단위)
- 출원번호 기준 `ON CONFLICT DO UPDATE` (중복 시 업데이트)
- CLI 옵션: `--reset`
- 이미지/임베딩 없이 텍스트 데이터만 적재

**`seed_images.py`** (이미지 추출):
- xlsx의 `oneCellAnchor` 기반 이미지 추출 → `image/` 디렉토리에 저장 (6자리 시퀀스)
- 출원번호 기준으로 DB `image_path` 컬럼 업데이트
- CLI 옵션: `--reset` (기존 이미지 삭제 후 재추출)

**`seed_embeddings.py`** (CLIP 임베딩):
- `image_path`가 있는 레코드 대상으로 CLIP ViT-B/32 배치 임베딩 생성
- `model/` 디렉토리에서 로컬 모델 우선 로드, 없으면 자동 다운로드
- MPS(Apple Silicon) 자동 감지, 없으면 CPU 사용
- CLI 옵션: `--batch-size`(기본 64), `--reset` (전체 재생성)

**`seed_trademarks.py`** (통합 버전):
- 위 3단계를 한 번에 처리
- CLI 옵션: `--batch-size`, `--reset`, `--skip-embedding`

### 3. 상표 검색 서비스

- **텍스트 유사도**: pg_trgm `similarity()` 함수 (threshold 기본값 0.3), 니스분류 필터 + 법적상태='등록' 필터, `image_path` 포함 반환
- **이미지 유사도**: pgvector 코사인 거리 (`<=>` 연산자), HNSW 인덱스
- **위험도 판별**: 최고 유사도 >= 0.55 → High, >= 0.4 → Middle, 그 외 → Low
- **폴백**: 니스 필터 결과 0건 시 필터 없이 전체 재검색

---

## Docker Compose 구성

```yaml
services:
  db:
    image: pgvector/pgvector:pg16
    volumes:
      - ./db/pgdata:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
      - ./image:/data/image:ro

  back-end:
    volumes:
      - ./back-end:/app
      - ./image:/data/image:ro
      - ./model:/data/model:ro
    environment:
      - DATABASE_URL=postgresql+asyncpg://gigigae:${DB_PASSWORD}@db:5432/gigigae
    depends_on:
      - db
```

---

## 실행 방법

```bash
# 전체 실행 (DB + 백엔드)
docker compose up -d

# 데이터 적재 - 3단계 분리 방식 (권장)
conda activate GiGiGae
python db/seed_trademarks_lite.py              # 1단계: 텍스트 데이터 적재
python db/seed_trademarks_lite.py --reset      # 기존 데이터 삭제 후 재적재
python db/seed_images.py                       # 2단계: 이미지 추출 + 경로 업데이트
python db/seed_embeddings.py                   # 3단계: CLIP 임베딩 생성
python db/seed_embeddings.py --batch-size 64   # 배치 크기 조정
python db/seed_embeddings.py --reset           # 전체 임베딩 재생성

# 데이터 적재 - 통합 방식
python db/seed_trademarks.py                   # 텍스트 + 이미지 + 임베딩 일괄 적재
python db/seed_trademarks.py --skip-embedding  # 임베딩 없이 데이터만 적재

# 상표 검색 테스트
curl -X POST http://localhost:9000/api/v1/trademark/search \
  -H "Content-Type: application/json" \
  -d '{"brand_name": "커피빈", "nice_classes": ["43"]}'
```
