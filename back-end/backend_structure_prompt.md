# FastAPI Backend Structure - 작업 지시서

> 생성일: 2026-03-20
> 프로젝트: GiGiGae (AI 기반 브랜드 론칭 자동화 서비스)

---

## 개요

back-end.md 명세를 기반으로 FastAPI 앱의 Clean Architecture 디렉토리 구조, Pydantic 스키마, 서비스 추상화 계층, 라우터, 설정 파일을 생성한다.

---

## 목표 디렉토리 구조

```
back-end/
├── app/
│   ├── main.py                  # FastAPI 앱 진입점, CORS, 라우터 연결
│   ├── api/
│   │   └── v1/
│   │       ├── router.py        # v1 라우터 통합
│   │       └── endpoints/
│   │           └── recommend.py # /recommend/brand, /recommend/logo, /recommend/domain
│   ├── schemas/
│   │   └── recommend.py         # 모든 Request/Response 스키마 통합
│   ├── services/
│   │   ├── base_llm.py          # BaseLLMService (ABC)
│   │   ├── ollama_service.py    # OllamaService 구현체
│   │   ├── base_image.py        # BaseImageService (ABC)
│   │   └── mock_image.py        # MockImageService 구현체
│   ├── core/
│   │   ├── config.py            # Settings (pydantic-settings, .env 로드)
│   │   ├── constants.py         # 상수 정의
│   │   └── exceptions.py        # 전역 예외 + 핸들러
│   └── utils/
│       ├── prompts.py           # LLM 프롬프트 템플릿
│       └── logger.py            # 공통 로거 설정
├── .env.example                 # 환경변수 템플릿
├── requirements.txt             # 의존성 목록
└── prompt/
    └── 20260320_fastapi_backend_structure.md  # 본 작업 지시서
```

---

## 핵심 구현 상세

### 1. Pydantic 스키마 (`app/schemas/recommend.py`)

모든 스키마를 `recommend.py` 단일 파일에서 관리:

- `BrandRequest(user_idea, industry, exclude?)`, `BrandCandidate(name, tags)`, `BrandResponse(candidates)`
- `LogoRequest(selected_name)`, `LogoUrl(url, style)`, `LogoResponse(logos)`
- `DomainRequest(selected_name, exclude?)`, `DomainCandidate(domain, reason)`, `DomainResponse(domains)`

> `exclude`: 재추천 시 이전에 추천된 항목을 제외하기 위한 optional 필드. 프론트엔드에서 누적 전달.

### 2. 서비스 추상화 계층 (`app/services/`)

```
BaseLLMService (ABC)
  └── OllamaService        # ollama 패키지 사용, Pydantic Structured Output

BaseImageService (ABC)
  └── MockImageService      # 샘플 이미지 경로 반환
```

- `BaseLLMService`: ABC로 `generate(prompt, system_prompt, schema)` 메서드 강제
- `OllamaService`: `format=schema.model_json_schema()`로 Ollama Structured Output 활용, `httpx.Timeout` 적용
- `BaseImageService`: ABC로 `generate_logos(brand_name, count)` 메서드 강제
- `MockImageService`: 샘플 이미지 경로 반환
- `.env`에 키 존재 여부(falsy 체크)로 실제/Mock 서비스 교체하는 DI 패턴 적용

### 3. API 라우터 (`app/api/v1/endpoints/recommend.py`)

모든 엔드포인트는 `recommend.py` 하나에 통합하여 관리:

| Endpoint | Method | 기능 | 상태 |
|---|---|---|---|
| `/api/v1/recommend/brand` | POST | 브랜드명 추천 + 특성 태그 | 구현 완료 |
| `/api/v1/recommend/logo` | POST | 로고 후보 생성 (Mock) | 구현 완료 |
| `/api/v1/recommend/domain` | POST | 도메인 후보 추천 | 구현 완료 |
| `/api/v1/recommend/guide` | POST | NHN Cloud 배포 가이드 리포트 생성 | 미구현 |

### 4. 핵심 설정 (`app/core/`)

- **config.py**: `pydantic-settings`로 `.env` 로드. Ollama 모델명/URL/Timeout, NHN Cloud API Key, KIPRIS API Key 관리. `use_mock_domain`, `use_mock_trademark` 프로퍼티(falsy 체크)로 Mock 모드 자동 분기
- **constants.py**: `API_V1_PREFIX`, `BRAND_CANDIDATE_COUNT`(5), `DOMAIN_SUFFIXES`, `MOCK_LOGO_STYLES` 등 상수 정의
- **exceptions.py**: `AppException` 기본 클래스 + `LLMTimeoutError`, `LLMGenerationError`, `ExternalAPIError`, `AppValidationError` 정의. `app_exception_handler`로 `error_code`, `message`, `detail` 형태의 에러 JSON 반환

### 5. FastAPI 진입점 (`app/main.py`)

- FastAPI 인스턴스 생성
- CORS 미들웨어 설정 (프론트엔드 연동 대비, localhost:3000/5173)
- v1 라우터 include (`prefix="/api/v1"`)
- 전역 예외 핸들러 등록 (`AppException → app_exception_handler`)
- lifespan 이벤트로 `OllamaService`, `MockImageService` 초기화 (`app_state` 딕셔너리에 저장)
- `/health` Health check 엔드포인트

### 6. 유틸리티 (`app/utils/`)

- **prompts.py**: `BRAND_SYSTEM_PROMPT`, `DOMAIN_SYSTEM_PROMPT` 및 `build_brand_user_prompt(exclude)`, `build_domain_user_prompt(exclude)` 함수. exclude 전달 시 프롬프트에 제외 조건 자동 추가
- **logger.py**: `get_logger()` 공통 Logger 팩토리. `settings.debug` 값에 따라 DEBUG/INFO 레벨 자동 분기

### 7. 의존성 (`requirements.txt`)

```
fastapi
uvicorn[standard]
pydantic
pydantic-settings
ollama
httpx
```

---

## 실행 방법

```bash
cd back-end
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 문서: http://localhost:8000/docs
