## Task 1: Directory Structure Design
`/back-end` 디렉토리 아래에 다음과 같은 구조를 생성하고 각 역할을 정의하십시오.

1. `app/api/v1/`: 엔드포인트 라우터 (`recommend.py` 하나에 brand, logo, domain, guide 통합).
2. `app/schemas/`: Pydantic을 이용한 Request/Response 데이터 모델 (`recommend.py` 단일 파일).
3. `app/services/`: 비즈니스 로직 및 인터페이스 (`BaseLLMService`, `BaseImageService`).
4. `app/core/`: 설정(config.py), 상수, 예외 처리.
5. `app/utils/`: 공통 유틸리티 (프롬프트 템플릿, 로거).

## Task 2: API Specification Definition
다음 사용자 시나리오를 충족하는 RESTful API 명세를 작성하십시오.

1. **Brand Recommendation** (`POST /api/v1/recommend/brand`)
   - Input: `BrandRequest` (user_idea: string max 250, industry: string, exclude?: list[str])
   - Output: `BrandResponse` → `list[BrandCandidate]` (name, tags)
2. **Logo Generation (Mock)** (`POST /api/v1/recommend/logo`)
   - Input: `LogoRequest` (selected_name: string)
   - Output: `LogoResponse` → `list[LogoUrl]` (url, style)
3. **Domain Recommendation** (`POST /api/v1/recommend/domain`)
   - Input: `DomainRequest` (selected_name: string, exclude?: list[str])
   - Output: `DomainResponse` → `list[DomainCandidate]` (domain, reason)
4. **Final Report Generation** (`POST /api/v1/recommend/guide`) `[미구현]`
   - Input: 최종 선택 데이터 (brand, logo, domain 등)
   - Output: NHN Cloud 기반 배포 가이드 리포트 (Markdown)
   - 추후 `recommend.py` 내에서 구현 예정

> `exclude` 필드: 재추천 시 프론트엔드가 이전 결과를 전달하면 LLM 프롬프트에서 제외

## Task 3: Implementation Strategy
- **BaseService Interface**: ABC를 사용한 `BaseLLMService` 설계, Ollama `OllamaService` 구현체.
- **Error Handling**: 전역 예외 처리기를 통해 `AppException` 계층의 규격화된 에러 JSON 반환.
- **Mock Logic**: `.env` API Key 존재 여부에 따라 실제/Mock 서비스를 교체하는 DI 패턴 적용.
- **Logger**: `settings.debug` 값에 따른 로그 레벨 자동 분기 (DEBUG / INFO).
