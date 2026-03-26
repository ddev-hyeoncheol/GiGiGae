## Task 1: Directory Structure Design
`/back-end` 디렉토리 아래에 다음과 같은 구조를 생성하고 각 역할을 정의하십시오.

1. `app/api/`: 엔드포인트 라우터 (`recommend.py`, `trademark.py`, `domain.py` 분리).
2. `app/schemas/`: Pydantic을 이용한 Request/Response 데이터 모델 (`recommend.py`, `trademark.py`, `domain.py` 분리).
3. `app/services/`: 비즈니스 로직 (`recommend_service.py`, `trademark_service.py`, `domain_service.py`).
4. `app/plugins/`: 외부 도구 플러그인 (`ollama_plugin.py`, `clip_plugin.py`, `nhn_domain_plugin.py`).
5. `app/core/`: 설정(config.py), 상수, 예외 처리, DB 커넥션 풀.
6. `app/utils/`: 공통 유틸리티 (프롬프트 템플릿, 로거).

## Task 2: API Specification Definition
다음 사용자 시나리오를 충족하는 RESTful API 명세를 작성하십시오.

1. **Brand Recommendation** (`POST /api/v1/recommend/brand`)
   - Input: `BrandRecommendRequest` (brand_idea, brand_category?, brand_tone?, count?, exclude?)
   - Output: `BrandRecommendResponse` → `list[BrandRecommendResult]` (brand_name, brand_description, brand_tags, trademark)
2. **Domain Recommendation** (`POST /api/v1/recommend/domain`)
   - Input: `DomainRecommendRequest` (brand_name, exclude?)
   - Output: `DomainRecommendResponse` → `list[DomainRecommendCandidate]` (domain_name, domain_reason)
3. **Trademark Search** (`POST /api/v1/trademark/search`)
   - Input: `TrademarkSearchRequest` (brand_name, nice_classes?, threshold?)
   - Output: `TrademarkSearchResponse` (brand_name, risk, matches)
4. **Trademark Image Search** (`POST /api/v1/trademark/image-search`)
   - Input: multipart/form-data (file: 이미지)
   - Output: `ImageSearchResponse` (matches: ImageSearchMatch[])
5. **Domain Check** (`POST /api/v1/domain/check`)
   - Input: `DomainCheckRequest` (domain_name)
   - Output: `DomainCheckResult` (domain_name, available, message, price?, promotion_price?)
6. **Health Check** (`GET /health`)
   - Output: `{"status": "ok"}`

> `exclude` 필드: 재추천 시 프론트엔드가 이전 결과를 전달하면 LLM 프롬프트에서 제외
> `count` 필드: 추천 개수 지정 (기본 4개, 최대 10개)
> `TrademarkMatch` 및 `ImageSearchMatch`에 `image_path` 필드 포함

## Task 3: Implementation Strategy
- **LLM 모델**: `gemma3:4b` 사용. `num_predict=1024`, `num_ctx=2048` 로 속도 최적화.
- **Plugin Architecture**: `OllamaPlugin`(LLM), `ClipPlugin`(이미지 임베딩), `NhnDomainPlugin`(도메인 API) 플러그인 분리.
- **CLIP 이미지 임베딩**: 싱글톤 패턴으로 ViT-B/32 모델 1회 로딩. 볼륨 마운트(`/data/model/ViT-B-32.pt`)에서 우선 로드, 없으면 자동 다운로드.
- **카테고리 → 니스 분류 매핑**: `recommend_service.py`에서 카테고리를 니스 분류 코드로 변환하여 상표 검색 시 필터링. 결과 0건 시 전체 검색 폴백.
- **병렬 상표 검색**: 브랜드 추천 후 각 후보별 상표 검색은 `asyncio.gather`로 병렬 실행하여 응답 속도를 최소화한다.
- **텍스트 검색 image_path**: `SEARCH_SQL`, `SEARCH_WITH_CLASS_SQL` 모두 `image_path` 컬럼 SELECT.
- **BRAND_SYSTEM_PROMPT**: 브랜드 네이밍 전문가 역할, 보통명사 사용 최소화, 슬로건 명사형, 태그 2~3개, 영문/한글 구분 지시.
- **Error Handling**: 전역 예외 처리기를 통해 `AppException` 계층의 규격화된 에러 JSON 반환 (`error_code`, `message`, `detail`).
- **Logger**: `settings.debug` 값에 따른 로그 레벨 자동 분기 (DEBUG / INFO).
- **app_state**: `main.py`에서 `dict[str, Any]`로 플러그인 인스턴스 관리, `Depends` DI로 각 라우터에 주입.
