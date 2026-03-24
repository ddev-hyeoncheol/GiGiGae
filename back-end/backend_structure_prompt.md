# FastAPI Backend Structure - 작업 지시서

> 생성일: 2026-03-20
> 최종 수정: 2026-03-24
> 프로젝트: GiGiGae (AI 기반 브랜드 론칭 자동화 서비스)

---

## 개요

FastAPI 앱의 Clean Architecture 디렉토리 구조, Pydantic 스키마, 서비스/플러그인 계층, 라우터, 설정 파일을 정의한다.

---

## 디렉토리 구조

```
back-end/
├── app/
│   ├── main.py                      # FastAPI 앱 진입점, CORS, 라우터 연결
│   ├── api/
│   │   ├── router.py                # API 라우터 통합
│   │   ├── recommend.py             # /recommend/brand, /recommend/domain
│   │   └── trademark.py             # /trademark/search
│   ├── schemas/
│   │   ├── recommend.py             # 브랜드/도메인 추천 스키마
│   │   └── trademark.py             # 상표 검색 스키마
│   ├── services/                    # 비즈니스 로직
│   │   ├── recommend_service.py     # LLM 추천 + 상표 검색 조합
│   │   └── trademark_service.py     # pg_trgm 기반 상표 유사도 검색
│   ├── plugins/                     # 외부 도구 (갈아끼울 수 있음)
│   │   └── ollama_plugin.py         # Ollama LLM 클라이언트
│   ├── core/
│   │   ├── config.py                # Settings (pydantic-settings, .env 로드)
│   │   ├── constants.py             # 상수 정의
│   │   ├── database.py              # asyncpg 커넥션 풀 관리
│   │   └── exceptions.py            # 전역 예외 + 핸들러
│   └── utils/
│       ├── prompts.py               # LLM 프롬프트 템플릿
│       └── logger.py                # 공통 로거 설정
├── .env.example                     # 환경변수 템플릿
├── requirements.txt                 # 의존성 목록
└── Dockerfile                       # 백엔드 컨테이너
```

---

## 핵심 구현 상세

### 1. Pydantic 스키마

**`schemas/recommend.py`** - 브랜드/도메인 추천:

- `BrandRecommendRequest(brand_idea, brand_category?, brand_tone?, exclude?)` - 브랜드 추천 요청
- `BrandRecommendCandidate(brand_name, brand_description, brand_tags)` - LLM 반환용
- `BrandRecommendLLMResponse(brand_candidates)` - LLM 반환용 응답
- `BrandRecommendResult(brand_name, brand_description, brand_tags, trademark)` - API 응답용 (추천 + 상표 결과)
- `BrandRecommendResponse(brand_candidates)` - 최종 API 응답
- `DomainRecommendRequest(brand_name, exclude?)` - 도메인 추천 요청
- `DomainRecommendCandidate(domain_name, domain_reason)` - 도메인 후보
- `DomainRecommendResponse(domain_candidates)` - 도메인 추천 응답

**`schemas/trademark.py`** - 상표 검색:

- `TrademarkSearchRequest(brand_name, nice_classes?, threshold?)` - 상표 검색 요청
- `TrademarkMatch(name, nice_class, legal_status, application_no, similarity)` - 유사 상표
- `TrademarkSearchResponse(brand_name, risk, matches)` - 상표 검색 응답

> `brand_category`: `list[str]` — 브랜드 카테고리 (최대 2개). 프론트엔드에서 칩 선택으로 전달.
> `brand_tone`: `list[str]` — 브랜드 톤 (최대 3개). 프론트엔드에서 칩 선택으로 전달.
> `exclude`: 재추천 시 이전에 추천된 항목을 제외하기 위한 optional 필드. 프론트엔드에서 누적 전달.

### 2. 플러그인 (`app/plugins/`)

```
OllamaPlugin       # Ollama LLM API 클라이언트, Pydantic Structured Output
```

- `generate(prompt, system_prompt, schema)` 메서드로 Pydantic 스키마 기반 Structured Output 반환
- `httpx.Timeout` 적용, `LLMTimeoutError`/`LLMGenerationError` 에러 핸들링

### 3. 서비스 (`app/services/`) - 비즈니스 로직

- **`recommend_service.py`**: `OllamaPlugin` + `TrademarkService`를 조합하여 브랜드 추천 + 상표 충돌 검색 수행
- **`trademark_service.py`**: asyncpg + pg_trgm 기반 상표 유사도 검색, 위험도 판별 (Low / Middle / High)

### 4. API 라우터 (`app/api/`)

| Endpoint | Method | 기능 | 백엔드 | 프론트 연동 |
|---|---|---|---|---|
| `/api/v1/recommend/brand` | POST | 브랜드명 추천 + 상표 충돌 검색 | 구현 완료 | 연동 완료 |
| `/api/v1/recommend/domain` | POST | 도메인 후보 추천 | 구현 완료 | 예정 |
| `/api/v1/trademark/search` | POST | 상표 유사도 검색 | 구현 완료 | 예정 |
| `/api/v1/guide/deploy` | POST | NHN Cloud 배포 가이드 생성 | 예정 | 예정 |

### 5. 핵심 설정 (`app/core/`)

- **config.py**: `pydantic-settings`로 `.env` 로드. Ollama 모델명/URL/Timeout, DATABASE_URL 관리
- **constants.py**: `API_V1_PREFIX`, `BRAND_CANDIDATE_COUNT`(6) 상수 정의
- **database.py**: asyncpg 커넥션 풀 생성/종료/조회. DI로 서비스에 주입
- **exceptions.py**: `AppException` 기본 클래스 + `LLMTimeoutError`, `LLMGenerationError`, `ExternalAPIError` 정의

### 6. FastAPI 진입점 (`app/main.py`)

- FastAPI 인스턴스 생성
- CORS 미들웨어 설정 (프론트엔드 연동 대비, localhost:3000/5173)
- API 라우터 include (`prefix="/api/v1"`)
- 전역 예외 핸들러 등록
- lifespan 이벤트로 `OllamaPlugin` 초기화, DB 커넥션 풀 생성/종료
- `/health` Health check 엔드포인트

### 7. 유틸리티 (`app/utils/`)

- **prompts.py**: `BRAND_SYSTEM_PROMPT`, `DOMAIN_SYSTEM_PROMPT` 및 `build_brand_user_prompt(brand_idea, brand_category, brand_tone, count, exclude)`, `build_domain_user_prompt(brand_name, count, exclude)` 함수
- **logger.py**: `get_logger()` 공통 Logger 팩토리

### 8. 의존성 (`requirements.txt`)

```
fastapi
uvicorn[standard]
pydantic
pydantic-settings
ollama
httpx
asyncpg
```

---

## 실행 방법

```bash
# Docker Compose로 실행 (DB + 백엔드, reload 지원)
docker compose up -d

# 또는 로컬 실행
cd back-end
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 9000
```

API 문서: http://localhost:9000/docs
