# Database Structure - 작업 지시서

> 생성일: 2026-03-23
> 프로젝트: GiGiGae (AI 기반 브랜드 론칭 자동화 서비스)

---

## 개요

KIPRIS(한국특허정보원) 상표권 데이터를 PostgreSQL에 적재하고, 백엔드에서 pg_trgm 기반 상표 유사도 검색을 제공한다.

---

## 단계별 구현 계획

### 1단계: Docker Compose에 PostgreSQL 컨테이너 추가 `[구현 완료]`

- `docker-compose.yml`에 `postgres:16-alpine` 서비스 추가
- `./db/pgdata` 로컬 바인드 마운트로 데이터 영속화
- `./db/init.sql`을 `/docker-entrypoint-initdb.d/init.sql`로 마운트 (최초 기동 시 자동 실행)
- `back-end` 서비스에 `depends_on: db` 및 `DATABASE_URL` 환경변수 주입

### 2단계: 테이블 스키마 + xlsx 적재 스크립트 `[구현 완료]`

- `db/init.sql` 생성 (pg_trgm 확장 + 테이블 DDL + 인덱스)
- `db/load_data.py` 생성 (xlsx → PostgreSQL 적재)
- 21개 xlsx 파일, 총 101,789건 적재 완료

### 3단계: 백엔드 상표 검색 API 통합 `[구현 완료]`

- `app/core/database.py`에서 asyncpg 커넥션 풀 관리
- `app/services/trademark_service.py`에서 pg_trgm 유사도 검색 + 위험도 판별 (Low / Middle / High)
- `app/api/trademark.py`에서 `POST /api/v1/trademark/search` 엔드포인트 제공
- `app/services/recommend_service.py`에서 LLM 추천 후 각 후보별 상표 검색 자동 수행

---

## 데이터 소스

- 위치: `db/data/*.xlsx` (21개 파일, 파일당 약 5,000행, 총 약 10만 건)
- 출처: KIPRIS 상표권 검색 결과
- 검색 조건: `TC=[35~45]*RD=[20250101~20260321]` (니스분류 35~45류, 2025.01~2026.03 출원)

---

## 디렉토리 구조

```
db/
├── init.sql          # pg_trgm 확장 + 테이블 생성 DDL + 인덱스
├── load_data.py      # xlsx → PostgreSQL 적재 스크립트
├── requirements.txt  # 적재 스크립트 의존성 (psycopg)
├── data/             # KIPRIS xlsx 원본 데이터 (.gitignore)
└── pgdata/           # PostgreSQL 데이터 디렉토리 (.gitignore)
```

---

## 핵심 구현 상세

### 1. 테이블 스키마 (`db/init.sql`)

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

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

CREATE INDEX IF NOT EXISTS idx_trademarks_name ON trademarks (name);
CREATE INDEX IF NOT EXISTS idx_trademarks_nice_class ON trademarks (nice_class);
CREATE INDEX IF NOT EXISTS idx_trademarks_legal_status ON trademarks (legal_status);
CREATE INDEX IF NOT EXISTS idx_trademarks_name_type ON trademarks (name_type);
CREATE INDEX IF NOT EXISTS idx_trademarks_name_trgm ON trademarks USING GIN (name gin_trgm_ops);
```

### 2. xlsx 컬럼 매핑

| xlsx 컬럼 | DB 컬럼 | 분류 | 설명 |
|---|---|---|---|
| B (상표명칭) | name | 필수 | 상표명 (유사도 검색 대상) |
| C (상품분류) | nice_class | 필수 | 니스분류 코드 (파이프 구분) |
| D (출원번호) | application_no | 필수 | 출원 고유번호 (UNIQUE) |
| Q (법적상태) | legal_status | 필수 | 등록/소멸/포기/무효 |
| E (출원일자) | application_date | 유용 | 출원일 |
| S (명칭구분) | name_type | 유용 | 한글상표/영문상표/도형복합 등 |
| R (심사진행상태) | review_status | 유용 | 등록결정(일반) 등 |
| G (등록번호) | registration_no | 유용 | 등록 고유번호 |
| H (등록일자) | registration_date | 유용 | 등록일 |

### 3. 적재 스크립트 (`db/load_data.py`)

- `zipfile` + `xml.etree` 로 xlsx 파일 직접 XML 파싱 (openpyxl 스타일 오류 우회)
- 헤더 행(1~8행) 스킵, 데이터 행부터 추출
- `psycopg`로 PostgreSQL 배치 INSERT (BATCH_SIZE=1000)
- 출원번호 기준 `ON CONFLICT DO NOTHING` 중복 방지

### 4. 상표 검색 서비스 (`app/services/trademark_service.py`)

- `asyncpg` 커넥션 풀을 `core/database.py`에서 DI로 주입받음
- pg_trgm `similarity()` 함수로 유사도 검색 (threshold 기본값 0.3)
- 니스분류 필터, 법적상태 = '등록' 필터 적용
- 위험도 판별: 최고 유사도 >= 0.55 → High, >= 0.4 → Middle, 그 외 → Low

---

## Docker Compose 구성

```yaml
services:
  db:
    image: postgres:16-alpine
    volumes:
      - ./db/pgdata:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro

  back-end:
    volumes:
      - ./back-end:/app
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

# 데이터 적재 (최초 1회만, pgdata 로컬 마운트로 영속화)
cd db
python load_data.py

# 상표 검색 테스트
curl -X POST http://localhost:9000/api/v1/trademark/search \
  -H "Content-Type: application/json" \
  -d '{"brand_name": "커피빈", "nice_classes": ["43"]}'
```
