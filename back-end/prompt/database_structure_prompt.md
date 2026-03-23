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
- `db-data` named volume으로 데이터 영속화
- `back-end` 서비스에 `depends_on: db` 및 `DATABASE_URL` 환경변수 주입
- `back-end/app/core/config.py`에 `database_url: str | None = None` 설정 추가

### 2단계: 테이블 스키마 + xlsx 적재 스크립트 `[미구현]`

- `db/init.sql` 생성 (PostgreSQL 초기화 시 자동 실행)
- `scripts/load_data.py` 생성 (xlsx → PostgreSQL 적재)

### 3단계: 백엔드 상표 검색 API 통합 `[미구현]`

- `app/services/trademark_service.py` 생성
- `/recommend/brand` 엔드포인트에서 LLM 추천 후 DB 조회로 상표 충돌 판별

---

## 데이터 소스

- 위치: `data/*.xlsx` (21개 파일, 파일당 약 5,000행, 총 약 10만 건)
- 출처: KIPRIS 상표권 검색 결과
- 검색 조건: `TC=[35~45]*RD=[20250101~20260321]` (니스분류 35~45류, 2025.01~2026.03 출원)

---

## 목표 디렉토리 구조

```
back-end/
├── app/
│   ├── core/
│   │   └── config.py            # database_url 설정 추가
│   └── services/
│       └── trademark_service.py # 상표 검색 서비스 (3단계)
├── db/
│   └── init.sql                 # 테이블 생성 DDL (2단계)
└── scripts/
    └── load_data.py             # xlsx → PostgreSQL 적재 (2단계)
```

---

## 핵심 구현 상세

### 1. 테이블 스키마 (`db/init.sql`)

```sql
CREATE TABLE IF NOT EXISTS trademarks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL,         -- 상표명칭 (컬럼 B)
    nice_class VARCHAR(100),            -- 상품분류/니스분류 (컬럼 C)
    application_no VARCHAR(50),         -- 출원번호 (컬럼 D)
    application_date DATE,              -- 출원일자 (컬럼 E)
    registration_no VARCHAR(50),        -- 등록번호 (컬럼 G)
    registration_date DATE,             -- 등록일자 (컬럼 H)
    legal_status VARCHAR(50),           -- 법적상태 (컬럼 P)
    trademark_type VARCHAR(50),         -- 상표유형 (컬럼 S) - 한글상표/영문상표
    english_name VARCHAR(500)           -- 영문명칭 (컬럼 Y)
);

CREATE INDEX idx_trademarks_name ON trademarks (name);
CREATE INDEX idx_trademarks_english_name ON trademarks (english_name);
CREATE INDEX idx_trademarks_legal_status ON trademarks (legal_status);
```

### 2. xlsx 컬럼 매핑

| xlsx 컬럼 | DB 컬럼 | 설명 |
|---|---|---|
| B (상표명칭) | name | 한글 상표명 |
| C (상품분류) | nice_class | 니스분류 코드 (파이프 구분) |
| D (출원번호) | application_no | 출원 고유번호 |
| E (출원일자) | application_date | 출원일 |
| G (등록번호) | registration_no | 등록 고유번호 |
| H (등록일자) | registration_date | 등록일 |
| P (법적상태) | legal_status | 등록/출원/거절 등 |
| S (상표유형) | trademark_type | 한글상표/영문상표 |
| Y (영문명칭) | english_name | 영문 상표명 |

### 3. 적재 스크립트 (`scripts/load_data.py`)

- `openpyxl`로 xlsx 파일 파싱 (zipfile + XML 직접 파싱으로 스타일 오류 우회)
- 헤더 행(1~8행) 스킵, 데이터 행부터 추출
- `psycopg`(또는 `asyncpg`)로 PostgreSQL COPY/배치 INSERT
- 출원번호 기준 중복 체크

### 4. 상표 검색 서비스 (`app/services/trademark_service.py`)

- `asyncpg` 또는 `SQLAlchemy[asyncio]`로 비동기 DB 접근
- 브랜드명 유사도 검색: `LIKE`, `pg_trgm` trigram 확장 활용
- 검색 결과를 `BrandCandidate`에 반영 (충돌 상표 정보)

### 5. 의존성 추가 (`requirements.txt`)

```
asyncpg
sqlalchemy[asyncio]
openpyxl
```

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
      - db-data:/var/lib/postgresql/data

  back-end:
    environment:
      - DATABASE_URL=postgresql+asyncpg://gigigae:${DB_PASSWORD}@db:5432/gigigae
    depends_on:
      - db
```

---

## 실행 방법

```bash
# DB 컨테이너 시작
docker compose up db -d

# 데이터 적재 (2단계 구현 후)
cd back-end
python scripts/load_data.py

# 백엔드 시작
docker compose up back-end -d
```
