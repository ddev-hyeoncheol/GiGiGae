# Vue Frontend Structure - 작업 지시서

> 생성일: 2026-03-23
> 최종 수정: 2026-03-25
> 프로젝트: GiGiGae (AI 기반 브랜드 론칭 자동화 서비스)

---

## 개요

Vite + Vue 3 + TypeScript SPA. 5~6단계 위자드 형태로 브랜드 론칭 파이프라인을 안내한다.
Vue Router로 뷰 전환, Pinia로 위자드 상태 관리, CSS 변수 기반 자체 스타일링 + 다크모드 지원.
백엔드(localhost:9000)와 REST API 통신.

---

## 기술 스택

- **빌드**: Vite 6 + Vue 3 (Composition API + `<script setup>`) + TypeScript
- **라우팅**: Vue Router 4 (History Mode)
- **스타일링**: CSS 변수 기반 자체 테마 시스템 (라이트/다크 모드)
- **상태 관리**: Pinia (persist 미사용)
- **HTTP 클라이언트**: fetch API (JSON + FormData 자동 분기)

---

## 디렉토리 구조

```
front-end/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tsconfig.app.json
├── env.d.ts                           # Vue 타입 선언
├── src/
│   ├── main.ts                        # Vue 앱 진입점 (createApp + Pinia + Router)
│   ├── App.vue                        # AppHeader + LoadingOverlay + RouterView
│   ├── style.css                      # CSS 변수 테마 + 글로벌 스타일 + 배경 블롭
│   ├── api/
│   │   ├── client.ts                  # fetch 래퍼 (JSON/FormData 자동 분기)
│   │   ├── types.ts                   # 백엔드 Pydantic 스키마 미러링 타입
│   │   ├── recommend.ts               # 브랜드/도메인 추천 API 함수
│   │   ├── trademark.ts               # 상표 검색 + 이미지 검색 API 함수
│   │   ├── domain.ts                  # 도메인 가용성 확인 API 함수
│   │   └── index.ts                   # 모듈 통합 export
│   ├── router/
│   │   └── index.ts                   # Vue Router 라우트 정의
│   ├── stores/
│   │   ├── index.ts                   # Pinia 인스턴스 생성
│   │   └── wizard.ts                  # 위자드 상태 관리 (글로벌 로딩 포함)
│   ├── composables/
│   │   └── useDarkMode.ts             # 다크모드 토글 composable
│   ├── components/
│   │   ├── AppLogo.vue                # 로고 + 타이포그래피 (클릭 시 홈 이동 + 상태 초기화)
│   │   ├── ChipSelect.vue             # 칩 다중선택 (v-model + max 제한)
│   │   ├── LoadingOverlay.vue         # 단계별 메시지 로딩 오버레이
│   │   ├── NavButtons.vue             # 이전/다음 네비게이션 버튼
│   │   ├── PageHeader.vue             # 페이지 제목 + 설명
│   │   ├── StepIndicator.vue          # 세그먼트 바 형태 진행 표시 (hidden 애니메이션)
│   │   └── DarkModeToggle.vue         # 다크모드 토글 버튼
│   └── views/
│       ├── HomeView.vue               # Step 1: 아이디어 입력 / 브랜드명 직접 검토 (탭 모드, 로고 업로드)
│       ├── BrandNameView.vue          # Step 2: 브랜드명 추천 (재추천 2회, 카드 선택)
│       ├── BrandTrademarkView.vue     # Step 3: 상표권 분석 (텍스트/이미지 유사 상표, 분쟁 사례 오버레이)
│       ├── BrandDomainView.vue        # Step 4: 도메인 추천 + 가용성 확인
│       └── FinalGuideView.vue         # Step 5: 최종 가이드
└── Dockerfile                         # multi-stage: node build + nginx serve
```

---

## 핵심 구현 상세

### 1. 프로젝트 설정

**`vite.config.ts`**:
- Vue 플러그인
- `@` alias → `src/`
- 개발 서버 프록시: `/api` → `http://localhost:9000`, `/image` → `http://localhost:9000`
- 포트: 5173, `host: '0.0.0.0'`

### 2. App.vue

- 3-column grid 헤더: `<AppLogo />` | `<StepIndicator />` | 빈 영역
- `<div class="app-body">`: `<main class="app-main">` (스크롤 영역) + `<LoadingOverlay />` (글로벌)
- `<DarkModeToggle />`
- LoadingOverlay는 app-main과 형제 레벨, position: absolute로 헤더 아래만 커버

### 3. 라우팅 (`router/index.ts`)

| 경로 | name | 컴포넌트 | Step |
|---|---|---|---|
| `/` | home | HomeView | 1 |
| `/brand-name` | brand-name | BrandNameView | 2 |
| `/trademark` | trademark | BrandTrademarkView | 3 |
| `/brand-domain` | brand-domain | BrandDomainView | 4 |
| `/final-guide` | final-guide | FinalGuideView | 5 |

> **두 가지 진입 경로:**
> - 아이디어 모드: Step 1 → 2 → 3 → 4 → 5
> - 브랜드명 모드: Step 1 → 3 (Step 2 hidden) → 4 → 5

### 4. API 모듈 (`api/`)

**`client.ts`**: fetch 래퍼 함수
- BASE_URL: `/api`
- FormData 감지 시 Content-Type 자동 처리 (multipart/form-data)
- JSON 요청 시 Content-Type: application/json 설정

**`types.ts`**: 백엔드 Pydantic 스키마 1:1 미러링
- `TrademarkMatch`, `TrademarkSearchRequest`, `TrademarkSearchResponse`
- `ImageSearchMatch`, `ImageSearchResponse`
- `BrandRecommendRequest(brand_idea, brand_category?, brand_tone?, count?, exclude?)`, `BrandRecommendResult`, `BrandRecommendResponse`
- `DomainRecommendRequest`, `DomainRecommendCandidate`, `DomainRecommendResponse`
- `DomainCheckRequest`, `DomainCheckResult`

**`recommend.ts`**: `recommendBrand()`, `recommendDomain()`
**`trademark.ts`**: `searchTrademark()`, `searchTrademarkByImage()` (FormData)
**`domain.ts`**: `checkDomain()`
**`index.ts`**: 통합 re-export

### 5. Pinia 위자드 스토어 (`stores/wizard.ts`)

```typescript
// State
currentStep: number
totalSteps: 5
inputMode: 'idea' | 'brand'
idea: string
directBrandName: string
brandCategory: string[]
brandTone: string[]
brandCandidates: BrandCandidate[]
selectedBrand: BrandCandidate | null
trademarkResult: TrademarkSearchResponse | null
imageSearchResult: ImageSearchResponse | null    // 이미지 유사 상표 검색 결과
domainCandidates: DomainCandidate[]
selectedDomain: DomainCandidate | null
finalReport: string

// 글로벌 로딩
loading: boolean
loadingMessages: string[]
loadingInterval: number
startLoading(messages, interval?), stopLoading()

// Computed
canGoNext: boolean
canGoBack: boolean

// Actions
nextStep(), prevStep(), goToStep(step), reset()
```

### 6. StepIndicator 컴포넌트

- **세그먼트 바** 형태
- 활성 단계: `flex-grow: 3`으로 확대 + `transition` 애니메이션
- 브랜드명 모드에서 Step 2는 **hidden** 클래스로 CSS 전환 (flex: 0, opacity: 0)
- 라벨: 아이디어 입력 / 브랜드명 추천 / 상표권 분석 / 도메인 조회 / 가이드 확인

### 7. View 컴포넌트

| View | 주요 기능 |
|---|---|
| HomeView (Step 1) | 아이디어/브랜드명 탭 모드, 카테고리/톤 옵션, 로고 이미지 업로드 (클릭+드래그앤드롭) |
| BrandNameView (Step 2) | 브랜드명 카드 선택, 재추천 최대 2회, 유사도 프로그레스 바 |
| BrandTrademarkView (Step 3) | 위험도 카드, 텍스트 유사 상표, 이미지 유사 상표 그리드, 분쟁 사례 오버레이 |
| BrandDomainView (Step 4) | LLM 도메인 추천 + NHN 가용성 병렬 확인 |
| FinalGuideView (Step 5) | 배포 가이드 리포트 (예정) |

### 8. 배경 효과 (`style.css`)

- body에 `radial-gradient` 도트 패턴 배경
- `body::before/after`, `#app::before/after` 4개의 빛 번짐 (blur blob)
- 7~10초 주기 `@keyframes` 애니메이션으로 이동
- `overflow: hidden`으로 전체 스크롤 방지, `#app > .app-main`에서 콘텐츠 스크롤

### 9. 다크모드

- `composables/useDarkMode.ts`: `<html>` 태그에 `data-theme` 속성 토글
- `style.css`: CSS 변수로 라이트/다크 테마 정의
- `DarkModeToggle.vue`: 고정 위치 토글 버튼

---

## 실행 방법

```bash
cd front-end
npm install
npm run dev
# → http://localhost:5173
```

백엔드 필요: `docker compose up -d` 또는 로컬 실행 (uvicorn, port 9000)

---

## 구현 우선순위

1. ~~프로젝트 초기화 + 타입/API + 스토어~~ — 완료
2. ~~레이아웃/공통 컴포넌트~~ — 완료
3. ~~Step 1 (입력, 탭 모드, 로고 업로드) + Step 2 (브랜드 추천, 재추천)~~ — 완료
4. ~~Step 3 (상표권 분석, 이미지 유사 상표, 분쟁 사례)~~ — 완료
5. ~~Step 4 (도메인, NHN Cloud API 연동)~~ — 완료
6. Step 5 (가이드) + 마무리 — 예정
