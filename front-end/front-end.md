## Task 1: 프로젝트 초기화

`/front-end` 디렉토리에 Vite + Vue 3 + TypeScript 기반 SPA를 구성하십시오.

1. `src/api/`: API 호출 함수 (`client.ts` 단일 파일).
2. `src/stores/`: Pinia 위자드 상태 관리 (`wizard.ts`).
3. `src/types/`: 백엔드 스키마 미러링 TypeScript 타입 (`api.ts`).
4. `src/components/layout/`: 공통 레이아웃 (AppHeader, StepIndicator, WizardLayout).
5. `src/components/common/`: 재사용 컴포넌트 (AppButton, LoadingProgress, ErrorAlert, RiskBadge).
6. `src/components/steps/`: 위자드 5단계 컴포넌트 (Step1~Step5).
7. `src/styles/`: Tailwind CSS 진입점 (`index.css`).
8. `public/mock/`: Mock 로고 이미지 5개.

## Task 2: API 명세 연동

백엔드(localhost:9000)의 RESTful API와 1:1 연동하십시오.

1. **브랜드 추천** (`POST /api/v1/recommend/brand`)
   - Input: `BrandRecommendRequest` (brand_idea: string max 250, brand_category?: string, exclude?: string[])
   - Output: `BrandRecommendResponse` → `brand_candidates: BrandRecommendResult[]`
     - 각 결과: `brand_name`, `brand_description`(슬로건), `brand_tags`, `trademark`(상표 검색 결과)
   - 후보 수: **5개** (백엔드 `BRAND_CANDIDATE_COUNT = 5`)
2. **도메인 추천** (`POST /api/v1/recommend/domain`)
   - Input: `DomainRecommendRequest` (brand_name: string, exclude?: string[])
   - Output: `DomainRecommendResponse` → `domain_candidates: DomainRecommendCandidate[]`
     - 각 결과: `domain_name`, `domain_reason`
3. **상표 검색** (`POST /api/v1/trademark/search`) - 직접 호출하지 않음 (브랜드 추천에 포함)

> `exclude` 필드: 재추천 시 현재 표시된 모든 후보의 이름을 배열로 전달하여 중복 방지.
> 재추천은 기존 결과를 **전체 교체**하며, 이전 선택은 초기화됨.

## Task 3: 에러 응답 처리

백엔드 에러 응답 형식에 맞춘 처리를 구현하십시오.

```
{ "error_code": string, "message": string, "detail": string | null }
```

- `LLM_TIMEOUT` (504): "AI 응답 시간이 초과되었습니다. 다시 시도해주세요."
- `LLM_GENERATION_ERROR` (502): "AI 응답 생성 중 오류가 발생했습니다."
- `EXTERNAL_API_ERROR` (502): "외부 서비스 오류가 발생했습니다."
- 네트워크 에러: "서버에 연결할 수 없습니다. 백엔드가 실행 중인지 확인해주세요."

## Task 4: 구현 전략

- **위자드 패턴**: Vue Router 없이 Pinia `currentStep` 기반 `<component :is>` 동적 렌더링.
- **상태 지속**: pinia-plugin-persistedstate로 localStorage에 저장 (새로고침 시 복구).
- **로딩 UX**: 단순 스피너가 아닌 단계별 진행 메시지 + 경과 시간 표시 (LLM 호출 최대 120초).
- **Mock 로고**: `public/mock/`의 placeholder SVG 이미지 5개 사용. 실제 로고 생성은 추후 구현.
- **Step5 가이드**: 프론트엔드에서 마크다운 템플릿에 선택 데이터를 삽입하여 클라이언트 사이드 생성.
