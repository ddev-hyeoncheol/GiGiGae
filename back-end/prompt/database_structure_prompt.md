# Database Structure - 작업 지시서

> 생성일: 2026-03-23
> 프로젝트: GiGiGae (AI 기반 브랜드 론칭 자동화 서비스)

---

## 개요

KIPRIS(한국특허정보원) 상표권 데이터를 PostgreSQL에 적재하고, 백엔드에서 상표 유사도 검색을 제공하기 위한 DB 구조를 설계한다.

---

## 단계별 구현 계획

### 1단계: Docker Compose에 PostgreSQL 컨테이너 추가 `[구현 완료]`

- `docker-compose.yml`에 `postgres:16-alpine` 서비스 추가
- `container_name: db`, `hostname: db`
- `./db/pgdata` 로컬 바인드 마운트로 데이터 영속화
- `./db/init.sql`을 `/docker-entrypoint-initdb.d/init.sql`로 마운트 (최초 기동 시 자동 실행)
- `back-end` 서비스에 `depends_on: db` 및 `DATABASE_URL` 환경변수 주입
- `back-end/app/core/config.py`에 `database_url: str | None = None` 설정 추가

### 2단계: 테이블 스키마 + xlsx 적재 스크립트 `[구현 완료]`

- `db/init.sql` 생성 (PostgreSQL 초기화 시 자동 실행)
- `db/load_data.py` 생성 (xlsx → PostgreSQL 적재)
- 21개 xlsx 파일, 총 101,789건 적재 완료

### 3단계: 백엔드 상표 검색 API 통합 `[미구현]`

- `app/services/trademark_service.py` 생성
- `/recommend/brand` 엔드포인트에서 LLM 추천 후 DB 조회로 상표 충돌 판별

---

## 데이터 소스

- 위치: `db/data/*.xlsx` (21개 파일, 파일당 약 5,000행, 총 약 10만 건)
- 출처: KIPRIS 상표권 검색 결과
- 검색 조건: `TC=[35~45]*RD=[20250101~20260321]` (니스분류 35~45류, 2025.01~2026.03 출원)

---

## 디렉토리 구조

```
db/
├── init.sql          # 테이블 생성 DDL
├── load_data.py      # xlsx → PostgreSQL 적재 스크립트
├── requirements.txt  # 적재 스크립트 의존성 (psycopg)
├── data/             # KIPRIS xlsx 원본 데이터 (.gitignore)
└── pgdata/           # PostgreSQL 데이터 디렉토리 (.gitignore)
```

---

## 핵심 구현 상세

### 1. 테이블 스키마 (`db/init.sql`)

```sql
CREATE SEQUENCE IF NOT EXISTS trademarks_id_seq;

CREATE TABLE IF NOT EXISTS trademarks (
    id BIGINT PRIMARY KEY DEFAULT nextval('trademarks_id_seq'),

    -- 필수: 상표 유사도 검색 핵심
    name VARCHAR(500) NOT NULL,         -- 상표명칭 (컬럼 B)
    nice_class VARCHAR(200),            -- 상품분류/니스분류 (컬럼 C)
    application_no VARCHAR(50) UNIQUE NOT NULL, -- 출원번호 (컬럼 D)
    legal_status VARCHAR(50),           -- 법적상태 (컬럼 Q)

    -- 유용: 분석 품질 향상
    application_date DATE,              -- 출원일자 (컬럼 E)
    name_type VARCHAR(50),              -- 명칭구분 (컬럼 S) - 한글상표/영문상표/도형복합 등
    review_status VARCHAR(50),          -- 심사진행상태 (컬럼 R)
    registration_no VARCHAR(50),        -- 등록번호 (컬럼 G)
    registration_date DATE              -- 등록일자 (컬럼 H)
);

CREATE INDEX IF NOT EXISTS idx_trademarks_name ON trademarks (name);
CREATE INDEX IF NOT EXISTS idx_trademarks_nice_class ON trademarks (nice_class);
CREATE INDEX IF NOT EXISTS idx_trademarks_legal_status ON trademarks (legal_status);
CREATE INDEX IF NOT EXISTS idx_trademarks_name_type ON trademarks (name_type);
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

### 4. 상표 검색 서비스 (`app/services/trademark_service.py`) `[미구현]`

- `asyncpg` 또는 `SQLAlchemy[asyncio]`로 비동기 DB 접근
- 브랜드명 유사도 검색: `LIKE`, `pg_trgm` trigram 확장 활용
- 검색 결과를 `BrandCandidate`에 반영 (충돌 상표 정보)

---

## Docker Compose 구성

```yaml
services:
  db:
    container_name: db
    hostname: db
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: gigigae
      POSTGRES_USER: gigigae
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - ./db/pgdata:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro

  back-end:
    environment:
      - DATABASE_URL=postgresql+asyncpg://gigigae:${DB_PASSWORD}@db:5432/gigigae
    depends_on:
      - db
```

---

## 실행 방법

```bash
# DB 컨테이너 시작 (최초 기동 시 init.sql 자동 실행)
docker compose up db -d

# 데이터 적재 (최초 1회만 실행, pgdata 로컬 마운트로 영속화)
cd db
python load_data.py

# 백엔드 시작
docker compose up back-end -d
```
