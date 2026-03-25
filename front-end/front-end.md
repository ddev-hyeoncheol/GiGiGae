## Task 1: 프로젝트 초기화

`/front-end` 디렉토리에 Vite + Vue 3 + TypeScript 기반 SPA를 구성하십시오.

1. `src/api/`: API 호출 함수 (`client.ts`, `recommend.ts`, `trademark.ts`, `domain.ts`, `types.ts`, `index.ts`).
2. `src/stores/`: Pinia 위자드 상태 관리 (`wizard.ts`).
3. `src/components/`: 공통 컴포넌트 (AppLogo, ChipSelect, LoadingOverlay, NavButtons, PageHeader, StepIndicator, DarkModeToggle, TrademarkChecklist, TrademarkMatchTable).
4. `src/views/`: 위자드 뷰 (HomeView, BrandNameView, BrandTrademarkView, BrandLogoView, BrandDomainView, FinalGuideView).
5. `src/composables/`: 다크모드 토글 (`useDarkMode.ts`), 상표 체크리스트 (`useTrademarkChecklist.ts`).
6. `src/utils/`: 니스 분류 매핑 (`niceClassMapping.ts`).
7. `src/style.css`: CSS 변수 기반 자체 테마 시스템.

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
   - `TrademarkMatch`에 `image_path?` 필드 포함
4. **이미지 상표 검색** (`POST /api/v1/trademark/image-search`)
   - Input: FormData (file: 이미지)
   - Output: `ImageSearchResponse` (matches: ImageSearchMatch[])
5. **도메인 가용성** (`POST /api/v1/domain/check`)
   - Input: `DomainCheckRequest` (domain_name)
   - Output: `DomainCheckResult` (available, price, promotion_price 등)

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

- **두 가지 진입 모드**: 아이디어 모드 (Step 1→2→3→4→5→6), 브랜드명 모드 (Step 1→3→4→5→6, Step 2 스킵).
- **글로벌 로딩**: App.vue 레벨 LoadingOverlay. wizard store에서 `startLoading(messages)` / `stopLoading()` 제어.
- **API 클라이언트**: fetch 래퍼에서 JSON / FormData 자동 분기 (`Content-Type` 자동 설정).
- **Vite Proxy**: `/api` → localhost:9000, `/image` → localhost:9000 (상표 이미지 서빙).
- **재추천**: BrandNameView에서 최대 2회 재추천, exclude 파라미터로 중복 방지.
- **이미지 업로드**: HomeView 브랜드명 모드에서 로고 이미지 업로드 (클릭 + 드래그앤드롭). `wizard.logoPreview`에 Data URL 저장.
- **분쟁 사례**: BrandTrademarkView에서 오버레이 모달로 상표 분쟁 사례 제공.
- **TrademarkChecklist**: `useTrademarkChecklist` composable로 6개 항목(동일 상표, 유사 상표, 업종 충돌, 식별력, 보통명칭화, 로고 충돌) 자동 계산. `TrademarkChecklist.vue`로 렌더링.
- **TrademarkMatchTable**: 이미지 썸네일 포함 유사 상표 목록. `niceClassMapping.ts`의 `resolveCategories()`로 카테고리명 표시.
- **BrandDomainView**: 도메인 카드 클릭 시 대체 TLD(.co.kr/.kr/.net 등) 조회 및 할인율 계산.
- **FinalGuideView**: CTA 카드(KIPRIS 출원 링크, NHN 도메인 등록 링크) + 브랜드/도메인/상표 분석 섹션 카드 분리. 연 가격 + 할인율 표시. HTML/텍스트 클립보드 복사 기능.
- **StepIndicator 라벨**: 상표권 분석 → **상표 분석**, 가이드 확인 → **최종 가이드**.
