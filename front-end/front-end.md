## Task 1: 프로젝트 초기화

`/front-end` 디렉토리에 Vite + Vue 3 + TypeScript 기반 SPA를 구성하십시오.

1. `src/api/`: API 호출 함수 (`client.ts`, `recommend.ts`, `trademark.ts`, `domain.ts`, `types.ts`, `index.ts`).
2. `src/stores/`: Pinia 위자드 상태 관리 (`wizard.ts`).
3. `src/components/`: 공통 컴포넌트 (AppLogo, ChipSelect, LoadingOverlay, NavButtons, PageHeader, StepIndicator, DarkModeToggle).
4. `src/views/`: 위자드 뷰 (HomeView, BrandNameView, BrandTrademarkView, BrandDomainView, FinalGuideView).
5. `src/composables/`: 다크모드 토글 (`useDarkMode.ts`).
6. `src/style.css`: CSS 변수 기반 자체 테마 시스템.

## Task 2: API 명세 연동

백엔드(localhost:9000)의 RESTful API와 1:1 연동하십시오.

1. **브랜드 추천** (`POST /api/v1/recommend/brand`)
   - Input: `BrandRecommendRequest` (brand_idea, brand_category?, brand_tone?, count?, exclude?)
   - Output: `BrandRecommendResponse` → `brand_candidates: BrandRecommendResult[]`
   - 기본 6개 (count 파라미터로 조정 가능, 최대 10개)
2. **도메인 추천** (`POST /api/v1/recommend/domain`)
   - Input: `DomainRecommendRequest` (brand_name, exclude?)
   - Output: `DomainRecommendResponse` → `domain_candidates: DomainRecommendCandidate[]`
3. **상표 검색** (`POST /api/v1/trademark/search`)
   - Input: `TrademarkSearchRequest` (brand_name, nice_classes?, threshold?)
   - Output: `TrademarkSearchResponse` (brand_name, risk, matches)
4. **이미지 상표 검색** (`POST /api/v1/trademark/image-search`)
   - Input: FormData (file: 이미지)
   - Output: `ImageSearchResponse` (matches: ImageSearchMatch[])
5. **도메인 가용성** (`POST /api/v1/domain/check`)
   - Input: `DomainCheckRequest` (domain_name)
   - Output: `DomainCheckResult` (available, price 등)

> `exclude` 필드: 재추천 시 현재 표시된 모든 후보의 이름을 배열로 전달하여 중복 방지.
> 재추천은 기존 결과 뒤에 **추가(Pending)** 되며, 최대 2회까지 가능.

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

- **두 가지 진입 모드**: 아이디어 모드 (Step 1→2→3→4→5), 브랜드명 모드 (Step 1→3→4→5, Step 2 스킵).
- **글로벌 로딩**: App.vue 레벨 LoadingOverlay. wizard store에서 `startLoading(messages)` / `stopLoading()` 제어.
- **API 클라이언트**: fetch 래퍼에서 JSON / FormData 자동 분기 (`Content-Type` 자동 설정).
- **Vite Proxy**: `/api` → localhost:9000, `/image` → localhost:9000 (상표 이미지 서빙).
- **재추천**: BrandNameView에서 최대 2회 재추천, exclude 파라미터로 중복 방지.
- **이미지 업로드**: HomeView 브랜드명 모드에서 로고 이미지 업로드 (클릭 + 드래그앤드롭).
- **분쟁 사례**: BrandTrademarkView에서 오버레이 모달로 상표 분쟁 사례 제공.
