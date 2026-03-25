# FastAPI Backend Structure - 작업 지시서

> 생성일: 2026-03-20
> 최종 수정: 2026-03-25
> 프로젝트: GiGiGae (AI 기반 브랜드 론칭 자동화 서비스)

---

## 개요

FastAPI 앱의 Clean Architecture 디렉토리 구조, Pydantic 스키마, 서비스/플러그인 계층, 라우터, 설정 파일을 정의한다.

---

## 디렉토리 구조

```
back-end/
├── app/
│   ├── main.py                      # FastAPI 앱 진입점, CORS, 라우터, 정적 파일 서빙
│   ├── api/
│   │   ├── router.py                # API 라우터 통합
│   │   ├── recommend.py             # /recommend/brand, /recommend/domain
│   │   ├── trademark.py             # /trademark/search, /trademark/image-search
│   │   └── domain.py                # /domain/check
│   ├── schemas/
│   │   ├── recommend.py             # 브랜드/도메인 추천 스키마
│   │   ├── trademark.py             # 상표 검색 + 이미지 검색 스키마
│   │   └── domain.py                # 도메인 가용성 확인 스키마
│   ├── services/                    # 비즈니스 로직
│   │   ├── recommend_service.py     # LLM 추천 + 상표 검색 조합 + 카테고리→니스 매핑
│   │   ├── trademark_service.py     # pg_trgm 텍스트 + pgvector 이미지 유사도 검색
│   │   └── domain_service.py        # NHN 도메인 가용성 확인
│   ├── plugins/                     # 외부 도구 (갈아끼울 수 있음)
│   │   ├── ollama_plugin.py         # Ollama LLM 클라이언트
│   │   ├── clip_plugin.py           # CLIP 이미지 임베딩 (ViT-B/32, 싱글톤)
│   │   └── nhn_domain_plugin.py     # NHN Cloud 도메인 API 클라이언트
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
└── Dockerfile                       # 백엔드 컨테이너 (torch CPU + CLIP 포함)
```

---

## 핵심 구현 상세

### 1. Pydantic 스키마

**`schemas/recommend.py`** - 브랜드/도메인 추천:

- `BrandRecommendRequest(brand_idea, brand_category?, brand_tone?, count?, exclude?)` - 브랜드 추천 요청
- `BrandRecommendCandidate(brand_name, brand_description, brand_tags)` - LLM 반환용
- `BrandRecommendLLMResponse(brand_candidates)` - LLM 반환용 응답
- `BrandRecommendResult(brand_name, brand_description, brand_tags, trademark)` - API 응답용 (추천 + 상표 결과)
- `BrandRecommendResponse(brand_candidates)` - 최종 API 응답
- `DomainRecommendRequest(brand_name, exclude?)` - 도메인 추천 요청
- `DomainRecommendCandidate(domain_name, domain_reason)` - 도메인 후보
- `DomainRecommendResponse(domain_candidates)` - 도메인 추천 응답

**`schemas/domain.py`** - 도메인 가용성 확인:

- `DomainCheckRequest(domain_name)` - 단건 가용성 확인 요청
- `DomainCheckResult(domain_name, available, message, price?, promotion_price?)` - NHN API 응답

**`schemas/trademark.py`** - 상표 검색:

- `TrademarkSearchRequest(brand_name, nice_classes?, threshold?)` - 텍스트 상표 검색 요청
- `TrademarkMatch(name, nice_class, legal_status, application_no, similarity)` - 유사 상표
- `TrademarkSearchResponse(brand_name, risk, matches)` - 상표 검색 응답
- `ImageSearchMatch(name, nice_class, legal_status, application_no, similarity, image_path)` - 이미지 유사 상표
- `ImageSearchResponse(matches)` - 이미지 검색 응답

> `count`: `int | None` — 추천 개수 (기본 6개, 최대 10개)
> `brand_category`: `list[str]` — 브랜드 카테고리 (최대 2개). 니스 분류 필터에 사용.
> `brand_tone`: `list[str]` — 브랜드 톤 (최대 3개).
> `exclude`: 재추천 시 이전에 추천된 항목을 제외하기 위한 optional 필드.

### 2. 플러그인 (`app/plugins/`)

```
OllamaPlugin           # Ollama LLM API 클라이언트, Pydantic Structured Output
ClipPlugin             # CLIP ViT-B/32 이미지 임베딩, 싱글톤 패턴
NhnDomainPlugin        # NHN Cloud 도메인 가용성 확인 클라이언트
```

- **OllamaPlugin**: `generate(prompt, system_prompt, schema)` 메서드로 Pydantic 스키마 기반 Structured Output 반환. `httpx.Timeout` 적용, `LLMTimeoutError`/`LLMGenerationError` 에러 핸들링
- **ClipPlugin**: 싱글톤. `embed_image(PIL.Image)` → 512차원 정규화 벡터. 볼륨 마운트(`/data/model/ViT-B-32.pt`) 우선 로드, 없으면 자동 다운로드
- **NhnDomainPlugin**: `check_availability(domain_name)` 메서드로 NHN API POST 호출. `ExternalAPIError` 에러 핸들링

### 3. 서비스 (`app/services/`) - 비즈니스 로직

- **`recommend_service.py`**: `OllamaPlugin` + `TrademarkService`를 조합하여 브랜드 추천 + 상표 충돌 검색 수행. 카테고리 → 니스 분류 매핑(`CATEGORY_NICE_MAP`)으로 업종별 상표 검색
- **`trademark_service.py`**: pg_trgm 텍스트 유사도 + pgvector 이미지 유사도 검색. 위험도 판별 (Low / Middle / High). 니스 필터 결과 0건 시 전체 검색 폴백
- **`domain_service.py`**: `NhnDomainPlugin`을 사용하여 도메인 가용성 확인

### 4. API 라우터 (`app/api/`)

| Endpoint | Method | 기능 | 상태 |
|---|---|---|---|
| `/api/v1/recommend/brand` | POST | 브랜드명 추천 + 상표 충돌 검색 | 구현 완료 |
| `/api/v1/recommend/domain` | POST | 도메인 중간 이름 추천 (TLD 제외) | 구현 완료 |
| `/api/v1/trademark/search` | POST | 텍스트 상표 유사도 검색 | 구현 완료 |
| `/api/v1/trademark/image-search` | POST | CLIP 이미지 유사 상표 검색 (multipart) | 구현 완료 |
| `/api/v1/domain/check` | POST | NHN Cloud 도메인 가용성 확인 | 구현 완료 |
| `/api/v1/guide/deploy` | POST | NHN Cloud 배포 가이드 생성 | 예정 |

### 5. 핵심 설정 (`app/core/`)

- **config.py**: `pydantic-settings`로 `.env` 로드. Ollama 모델명/URL/Timeout, NHN Domain API URL/Timeout, DATABASE_URL 관리
- **constants.py**: `API_V1_PREFIX`, `BRAND_CANDIDATE_COUNT`(6) 상수 정의
- **database.py**: asyncpg 커넥션 풀 생성/종료/조회. DI로 서비스에 주입
- **exceptions.py**: `AppException` 기본 클래스 + `LLMTimeoutError`, `LLMGenerationError`, `ExternalAPIError` 정의

### 6. FastAPI 진입점 (`app/main.py`)

- FastAPI 인스턴스 생성
- CORS 미들웨어 설정
- API 라우터 include (`prefix="/api/v1"`)
- 정적 파일 서빙: `/image` → `/data/image` (상표 이미지)
- 전역 예외 핸들러 등록
- lifespan 이벤트로 `OllamaPlugin`, `NhnDomainPlugin` 초기화, DB 커넥션 풀 생성/종료
- `/health` Health check 엔드포인트

### 7. 유틸리티 (`app/utils/`)

- **prompts.py**: `BRAND_SYSTEM_PROMPT`, `DOMAIN_SYSTEM_PROMPT` 및 `build_brand_user_prompt(brand_idea, brand_category, brand_tone, count, exclude)`, `build_domain_user_prompt(brand_name, count=10, exclude)` 함수
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
Pillow
python-multipart
```

> torch, torchvision, CLIP은 Dockerfile에서 별도 설치 (CPU 버전)

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
