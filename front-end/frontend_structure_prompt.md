# Vue Frontend Structure - 작업 지시서

> 생성일: 2026-03-23
> 최종 수정: 2026-03-24
> 프로젝트: NameCraft (AI 기반 브랜드 론칭 자동화 서비스)

---

## 개요

Vite + Vue 3 + TypeScript SPA. 5단계 위자드 형태로 브랜드 론칭 파이프라인을 안내한다.
Vue Router로 뷰 전환, Pinia로 위자드 상태 관리, CSS 변수 기반 자체 스타일링 + 다크모드 지원.
백엔드(localhost:9000)와 REST API 통신.

---

## 기술 스택

- **빌드**: Vite 6 + Vue 3 (Composition API + `<script setup>`) + TypeScript
- **라우팅**: Vue Router 4 (History Mode)
- **스타일링**: CSS 변수 기반 자체 테마 시스템 (라이트/다크 모드)
- **상태 관리**: Pinia (persist 미사용)
- **HTTP 클라이언트**: fetch API (별도 라이브러리 불필요)

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
│   ├── App.vue                        # StepIndicator + RouterView + DarkModeToggle
│   ├── style.css                      # CSS 변수 테마 + 글로벌 스타일
│   ├── api/
│   │   ├── client.ts                  # fetch 래퍼 (BASE_URL="/api/v1")
│   │   ├── types.ts                   # 백엔드 Pydantic 스키마 미러링 타입
│   │   ├── recommend.ts               # 브랜드/도메인 추천 API 함수
│   │   ├── trademark.ts               # 상표 검색 API 함수
│   │   └── index.ts                   # 모듈 통합 export
│   ├── router/
│   │   └── index.ts                   # Vue Router 라우트 정의 (5개 뷰)
│   ├── stores/
│   │   ├── index.ts                   # Pinia 인스턴스 생성
│   │   └── wizard.ts                  # 위자드 상태 관리
│   ├── composables/
│   │   └── useDarkMode.ts             # 다크모드 토글 composable
│   ├── components/
│   │   ├── AppLogo.vue                # 로고 + 타이포그래피 (클릭 시 홈 이동)
│   │   ├── ChipSelect.vue             # 칩 다중선택 (v-model + max 제한)
│   │   ├── NavButtons.vue             # 이전/다음 네비게이션 버튼
│   │   ├── PageHeader.vue             # 페이지 제목 + 설명
│   │   ├── StepIndicator.vue          # 세그먼트 바 형태 진행 표시
│   │   └── DarkModeToggle.vue         # 다크모드 토글 버튼
│   └── views/
│       ├── HomeView.vue               # Step 1: 아이디어 입력
│       ├── BrandNameView.vue          # Step 2: 브랜드명 추천 (6개)
│       ├── BrandLogoView.vue          # Step 3: 로고 선택 (Mock)
│       ├── BrandDomainView.vue        # Step 4: 도메인 추천
│       └── FinalGuideView.vue         # Step 5: 최종 가이드
└── Dockerfile                         # multi-stage: node build + nginx serve
```

---

## 핵심 구현 상세

### 1. 프로젝트 설정

**`vite.config.ts`**:
- Vue 플러그인
- `@` alias → `src/`
- 개발 서버 프록시: `/api` → `http://localhost:9000`
- 포트: 5173, `host: '0.0.0.0'` (외부 접근 허용)

### 2. Vue 앱 진입점 (`main.ts`)

- `createApp(App).use(pinia).use(router).mount('#app')`
- Pinia + Vue Router 등록

### 3. App.vue

- 3-column grid 헤더: `<AppLogo />` | `<StepIndicator />` | 빈 영역
- `<main class="app-main">` 스크롤 영역으로 `<RouterView />` 감쌈
- `<DarkModeToggle />`

### 4. 라우팅 (`router/index.ts`)

| 경로 | name | 컴포넌트 | Step |
|---|---|---|---|
| `/` | home | HomeView | 1 |
| `/brand-name` | brand-name | BrandNameView | 2 |
| `/brand-logo` | brand-logo | BrandLogoView | 3 |
| `/brand-domain` | brand-domain | BrandDomainView | 4 |
| `/final-guide` | final-guide | FinalGuideView | 5 |

### 5. API 모듈 (`api/`)

**`client.ts`**: fetch 래퍼 함수 (`apiFetch<T>`)
- BASE_URL: `/api/v1`
- 에러 시 `ApiErrorResponse` 파싱 후 throw

**`types.ts`**: 백엔드 Pydantic 스키마 1:1 미러링
- `TrademarkMatch`, `TrademarkSearchRequest`, `TrademarkSearchResponse`
- `BrandRecommendRequest(brand_idea, brand_category?, brand_tone?, exclude?)`, `BrandRecommendResult`, `BrandRecommendResponse`
- `DomainRecommendRequest`, `DomainRecommendCandidate`, `DomainRecommendResponse`

**`recommend.ts`**: `recommendBrand()`, `recommendDomain()`
**`trademark.ts`**: `searchTrademark()`
**`index.ts`**: 통합 re-export

### 6. Pinia 위자드 스토어 (`stores/wizard.ts`)

```typescript
// State
currentStep: number           // 현재 단계 (1~5)
totalSteps: 5                 // 상수
idea: string                  // 브랜드 아이디어 텍스트
brandCategory: string[]       // 브랜드 카테고리 (최대 2개)
brandTone: string[]           // 브랜드 톤 (최대 3개)
brandCandidates: BrandCandidate[]
selectedBrand: BrandCandidate | null
logoCandidates: LogoCandidate[]
selectedLogo: LogoCandidate | null
domainCandidates: DomainCandidate[]
selectedDomain: DomainCandidate | null
finalReport: string

// Computed
canGoNext: boolean            // 현재 단계 기준 다음 진행 가능 여부
canGoBack: boolean            // currentStep > 1

// Actions
nextStep(), prevStep(), goToStep(step), reset()
```

- **persist 미사용**: 새로고침 시 상태 초기화
- `LogoCandidate`, `DomainCandidate`는 로컬 인터페이스 (스토어 내 정의)

### 7. StepIndicator 컴포넌트

- **세그먼트 바** 형태 (원형 아님)
- Pinia `currentStep` 구독, 라우트 전환에도 유지 (App.vue에 배치)
- 활성 단계: `flex-grow: 3`으로 확대 + `transition` 애니메이션
- 완료 단계: success 색상 (초록), 활성 단계: primary 색상, 미완료: gray
- 라벨: 아이디어 입력 / 브랜드명 추천 / 로고 추천 / 도메인 추천 / 배포 가이드

### 8. View 컴포넌트

| View | 상태 | 백엔드 연동 |
|---|---|---|
| HomeView (Step 1) | 구현 완료 | 연동 완료 (`recommendBrand` 호출, 카테고리/톤 옵션 포함) |
| BrandNameView (Step 2) | 구현 완료 | 연동 완료 (결과 표시 + 선택) |
| BrandLogoView (Step 3) | 구현 완료 | Mock 데이터 |
| BrandDomainView (Step 4) | 구현 완료 | 예정 |
| FinalGuideView (Step 5) | 구현 완료 | 예정 |

### 9. 배경 효과 (`style.css`)

- body에 `radial-gradient` 도트 패턴 배경
- `body::before/after`, `#app::before/after` 4개의 빛 번짐 (blur blob)
- 10~15초 주기 `@keyframes` 애니메이션으로 이동
- `overflow: hidden`으로 전체 스크롤 방지, `#app > .app-main`에서 콘텐츠 스크롤

### 10. 다크모드

- `composables/useDarkMode.ts`: `<html>` 태그에 `data-theme` 속성 토글
- `style.css`: CSS 변수로 라이트/다크 테마 정의
- `DarkModeToggle.vue`: 고정 위치 토글 버튼

---

## 의존성 (`package.json`)

```
vue                              # UI 프레임워크
vue-router                       # 라우팅
pinia                            # 상태 관리
vite, @vitejs/plugin-vue         # 빌드
typescript, vue-tsc              # 타입 체크
```

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
3. ~~Step 1 (입력) + Step 2 (브랜드 추천)~~ — 완료 (백엔드 연동 포함)
4. Step 3 (로고, Mock) + Step 4 (도메인, 백엔드 연동) — 작업 중
5. Step 5 (가이드) + 마무리 — 예정
