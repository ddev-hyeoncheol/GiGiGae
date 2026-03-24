# Vue Frontend Structure - 작업 지시서

> 생성일: 2026-03-23
> 프로젝트: NameCraft (AI 기반 브랜드 론칭 자동화 서비스)

---

## 개요

Vite + Vue 3 + TypeScript SPA. 5단계 위자드 형태로 브랜드 론칭 파이프라인을 안내한다.
백엔드(localhost:9000)와 REST API 통신, Pinia(persist)로 위자드 상태 관리, Tailwind CSS로 스타일링.

---

## 기술 스택

- **빌드**: Vite 6 + Vue 3 (Composition API + `<script setup>`) + TypeScript
- **스타일링**: Tailwind CSS 4
- **상태 관리**: Pinia + pinia-plugin-persistedstate (localStorage)
- **HTTP 클라이언트**: fetch API (별도 라이브러리 불필요)
- **아이콘**: Lucide Vue Next
- **마크다운 렌더링**: markdown-it (Final Guide View 용)

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
├── public/
│   └── mock/                          # Mock 로고 이미지 5개
│       ├── logo-1.svg
│       ├── logo-2.svg
│       ├── logo-3.svg
│       ├── logo-4.svg
│       └── logo-5.svg
├── src/
│   ├── main.ts                        # Vue 앱 진입점 (createApp + Pinia 등록)
│   ├── App.vue                        # 위자드 컨테이너 + <component :is> 동적 렌더링
│   ├── api/
│   │   └── client.ts                  # API 호출 함수 (BASE_URL="/api/v1")
│   ├── stores/
│   │   └── wizard.ts                  # Pinia + persist 위자드 상태
│   ├── types/
│   │   └── api.ts                     # 백엔드 Pydantic 스키마 미러링 타입
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppHeader.vue          # 로고 + 프로젝트명 + "처음으로" 버튼
│   │   │   ├── StepIndicator.vue      # 5단계 진행 표시 바
│   │   │   └── WizardLayout.vue       # 공통 레이아웃 (Header + StepIndicator + <slot>)
│   │   ├── common/
│   │   │   ├── AppButton.vue          # 공통 버튼 (Primary / Secondary / Ghost)
│   │   │   ├── LoadingProgress.vue    # 단계별 진행 메시지 + 경과 시간 표시
│   │   │   ├── ErrorAlert.vue         # 에러 메시지 + 재시도 버튼
│   │   │   └── RiskBadge.vue          # 상표 위험도 배지 (Low/Middle/High/unchecked)
│   │   └── steps/
│   │       ├── Step1IdeaInput.vue     # Landing: 아이디어 입력 폼
│   │       ├── Step2BrandNames.vue    # Brand Name View: 후보 카드 목록 (5개)
│   │       ├── Step3BrandLogo.vue     # Brand Logo View: Mock 로고 그리드
│   │       ├── Step4Domain.vue        # Brand Domain View: 도메인 후보 목록
│   │       └── Step5FinalGuide.vue    # Final Guide View: 요약 + 마크다운 리포트
│   └── styles/
│       └── index.css                  # Tailwind @import
└── Dockerfile                         # multi-stage: node build + nginx serve
```

---

## 핵심 구현 상세

### 1. 프로젝트 설정

**`package.json`** 주요 의존성:
```json
{
  "dependencies": {
    "vue": "^3.5.0",
    "pinia": "^2.2.0",
    "pinia-plugin-persistedstate": "^4.0.0",
    "lucide-vue-next": "^0.400.0",
    "markdown-it": "^14.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "tailwindcss": "^4.0.0",
    "@tailwindcss/vite": "^4.0.0",
    "typescript": "^5.5.0",
    "vue-tsc": "^2.0.0",
    "vite": "^6.0.0"
  }
}
```

**`vite.config.ts`**:
- Vue 플러그인 + Tailwind 플러그인
- 개발 서버 프록시: `/api` → `http://localhost:9000`
- 포트: 5173 (Vite 기본값, 백엔드 CORS에서 이미 허용)

> Docker 환경에서는 port 3000 매핑 (docker-compose.yml). 백엔드 CORS에서 두 포트 모두 허용됨.

**`tsconfig.json`**:
- `strict: true`
- `paths` alias: `@/*` → `src/*`

**`env.d.ts`**:
```typescript
/// <reference types="vite/client" />
```

### 2. Vue 앱 진입점 (`main.ts`)

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import App from './App.vue'
import './styles/index.css'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

createApp(App).use(pinia).mount('#app')
```

### 3. TypeScript 타입 (`types/api.ts`)

백엔드 Pydantic 스키마와 1:1 매칭:

```typescript
// --- 에러 응답 ---
export interface ApiErrorResponse {
  error_code: string
  message: string
  detail: string | null
}

// --- 상표 검색 ---
export interface TrademarkMatch {
  name: string
  nice_class: string | null
  legal_status: string | null
  application_no: string
  similarity: number
}

export interface TrademarkSearchResponse {
  brand_name: string
  risk: 'Low' | 'Middle' | 'High' | 'unchecked'
  matches: TrademarkMatch[]
}

// --- 브랜드 추천 ---
export interface BrandRecommendRequest {
  brand_idea: string           // max 250
  brand_category?: string
  exclude?: string[]
}

export interface BrandRecommendResult {
  brand_name: string
  brand_description: string    // 슬로건 (1줄, 명사형)
  brand_tags: string[]
  trademark: TrademarkSearchResponse
}

export interface BrandRecommendResponse {
  brand_candidates: BrandRecommendResult[]  // 5개
}

// --- 도메인 추천 ---
export interface DomainRecommendRequest {
  brand_name: string
  exclude?: string[]
}

export interface DomainRecommendCandidate {
  domain_name: string
  domain_reason: string
}

export interface DomainRecommendResponse {
  domain_candidates: DomainRecommendCandidate[]
}
```

### 4. API 클라이언트 (`api/client.ts`)

```typescript
import type { ApiErrorResponse, BrandRecommendRequest, BrandRecommendResponse, DomainRecommendRequest, DomainRecommendResponse } from '@/types/api'

const BASE_URL = '/api/v1'

async function apiFetch<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err: ApiErrorResponse = await res.json().catch(() => ({
      error_code: 'NETWORK_ERROR',
      message: '서버에 연결할 수 없습니다.',
      detail: null,
    }))
    throw new Error(err.message)
  }
  return res.json()
}

export function recommendBrand(req: BrandRecommendRequest): Promise<BrandRecommendResponse> {
  return apiFetch('/recommend/brand', req)
}

export function recommendDomain(req: DomainRecommendRequest): Promise<DomainRecommendResponse> {
  return apiFetch('/recommend/domain', req)
}
```

### 5. Pinia 위자드 스토어 (`stores/wizard.ts`)

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { BrandRecommendResponse, BrandRecommendResult, DomainRecommendResponse, DomainRecommendCandidate } from '@/types/api'

export const useWizardStore = defineStore('wizard', () => {
  // State
  const currentStep = ref(1)
  const ideaInput = ref({ brand_idea: '', brand_category: '' })
  const brandResult = ref<BrandRecommendResponse | null>(null)
  const selectedBrand = ref<BrandRecommendResult | null>(null)
  const selectedLogo = ref<string | null>(null)
  const domainResult = ref<DomainRecommendResponse | null>(null)
  const selectedDomain = ref<DomainRecommendCandidate | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  function nextStep() { if (currentStep.value < 5) currentStep.value++ }
  function prevStep() { if (currentStep.value > 1) currentStep.value-- }
  function setStep(step: number) { currentStep.value = step }

  function reset() {
    currentStep.value = 1
    ideaInput.value = { brand_idea: '', brand_category: '' }
    brandResult.value = null
    selectedBrand.value = null
    selectedLogo.value = null
    domainResult.value = null
    selectedDomain.value = null
    isLoading.value = false
    error.value = null
  }

  return {
    currentStep, ideaInput, brandResult, selectedBrand,
    selectedLogo, domainResult, selectedDomain, isLoading, error,
    nextStep, prevStep, setStep, reset,
  }
}, {
  persist: true,  // pinia-plugin-persistedstate
})
```

- `persist: true`로 localStorage에 자동 저장
- 새로고침 시 마지막 상태에서 복구
- `reset()` 호출 시 모든 상태 초기화 (localStorage 포함)

### 6. 레이아웃 컴포넌트

**`AppHeader.vue`**:
- 상단 고정, 좌측 "NameCraft", 우측 "처음으로" 버튼 (`store.reset()` 호출)
- 배경: white, 하단 border

**`StepIndicator.vue`**:
- Props: `currentStep: number`
- 5개 원형 + 연결선
- 단계명: 아이디어 입력 / 브랜드명 추천 / 로고 선택 / 도메인 추천 / 최종 가이드
- 현재 단계: blue 배경, 완료 단계: green 체크, 미완료: gray

**`WizardLayout.vue`**:
- `<AppHeader />` + `<StepIndicator />` + `<slot />`
- max-width 컨테이너 (max-w-5xl), 중앙 정렬, 배경 gray-50

### 7. 공통 컴포넌트

**`AppButton.vue`**:
- Props: `variant` (primary/secondary/ghost), `size` (sm/md/lg), `loading`, `disabled`
- loading 상태 시 스피너 아이콘 + 클릭 비활성화

**`LoadingProgress.vue`**:
- Props: `message?: string`
- 단계별 진행 메시지: "AI가 브랜드를 분석 중입니다..." → "상표 데이터를 검색 중입니다..."
- `onMounted`에서 `setInterval`로 경과 시간 표시 (예: "12초 경과")
- 30초 이후: "조금 더 걸릴 수 있습니다. 잠시만 기다려주세요."
- 백엔드 LLM 타임아웃: 최대 120초

**`ErrorAlert.vue`**:
- Props: `message: string`
- Emits: `retry`
- 에러 메시지 + "다시 시도" 버튼, 빨간 배경

**`RiskBadge.vue`**:
- Props: `risk: 'Low' | 'Middle' | 'High' | 'unchecked'`
- 색상 매핑:
  - `Low`: green (bg-green-100 text-green-800) "안전"
  - `Middle`: yellow (bg-yellow-100 text-yellow-800) "주의"
  - `High`: red (bg-red-100 text-red-800) "위험"
  - `unchecked`: gray (bg-gray-100 text-gray-800) "미확인"

### 8. Step 컴포넌트 상세

**Step1IdeaInput.vue**:
- 히어로 섹션: "당신의 아이디어를 브랜드로" + 부제목
- `<textarea v-model>`: placeholder="예: 환경 친화적인 텀블러를 판매하는 브랜드를 만들고 싶어요", maxlength="250"
- 글자수 카운터: `{{ ideaInput.brand_idea.length }}/250` (우측 하단)
- 카테고리 `<input v-model>`: optional, placeholder="예: 식음료, IT, 패션"
- "브랜드 추천 받기" 버튼 (brand_idea 비어있으면 disabled)
- 제출 → `recommendBrand()` → `store.brandResult = result` → `store.nextStep()`

**Step2BrandNames.vue**:
- 상단: "추천 브랜드명" + "5개의 후보를 찾았습니다"
- 카드 그리드: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4`
- 각 카드 (`v-for="candidate in brandResult.brand_candidates"`):
  - `brand_name` (text-xl font-bold) — 브랜드명
  - `brand_description` (text-sm text-gray-600, **1줄 슬로건**으로 표시, 절대 여러 줄 아님)
  - `brand_tags` (`v-for` 배지: bg-blue-100 text-blue-800 rounded-full px-2 py-0.5)
  - `<RiskBadge :risk="candidate.trademark.risk" />`
  - 선택 시 `ring-2 ring-blue-500` 테두리 (`:class` 바인딩)
- 하단 버튼:
  - "다시 추천받기" (secondary) → **현재 표시된 5개 전체의 brand_name을 exclude에 넣고 재호출. 결과는 전체 교체, 이전 선택 초기화**
  - "이 브랜드로 계속" (primary, `selectedBrand`가 있을 때만 활성화) → `store.nextStep()`

**Step3BrandLogo.vue**:
- 상단: "로고 후보" + 선택된 브랜드명 표시
- Mock 데이터 (`ref` 배열, 하드코딩):
  ```typescript
  const mockLogos = [
    { url: '/mock/logo-1.svg', style: '미니멀' },
    { url: '/mock/logo-2.svg', style: '모던' },
    { url: '/mock/logo-3.svg', style: '클래식' },
    { url: '/mock/logo-4.svg', style: '볼드' },
    { url: '/mock/logo-5.svg', style: '엘레강트' },
  ]
  ```
- 그리드 표시, 선택 시 ring 강조
- 안내: "실제 로고 생성 기능은 추후 업데이트 예정입니다"
- "이 로고로 계속" / "건너뛰기" (건너뛰기 = 로고 미선택으로 진행, Step5에서 "미선택" 표시)

**Step4Domain.vue**:
- **`onMounted`** 시 자동으로 `recommendDomain({ brand_name: selectedBrand.brand_name })` 호출
- `watch`로 이미 domainResult가 있으면 재호출하지 않음
- 도메인 후보 카드 (`v-for`):
  - `domain_name` (font-mono text-lg) — 도메인명
  - `domain_reason` (text-sm text-gray-600) — 추천 이유
  - 선택 시 ring 강조
- "다른 도메인 추천" → **현재 표시된 모든 domain_name을 exclude에 넣고 재호출. 결과 전체 교체, 이전 선택 초기화**
- "이 도메인으로 계속" (선택 필요)

**Step5FinalGuide.vue**:
- 3개 요약 카드:
  1. 브랜드: 이름, 슬로건, 태그, 위험도 배지
  2. 로고: 선택한 이미지 또는 "미선택"
  3. 도메인: 도메인명 + 추천 이유
- 마크다운 리포트:
  - `computed`로 선택 데이터를 템플릿 리터럴에 삽입하여 **클라이언트 사이드 생성**
  - `markdown-it`으로 HTML 렌더링 (`v-html`)
  - 내용: 서비스 개요, 브랜드 전략, NHN Cloud 배포 가이드 (Instance, 로드밸런서, CDN 등)
- "리포트 복사" → `navigator.clipboard.writeText(markdownString)`
- "처음부터 다시" → `store.reset()`

### 9. App.vue 위자드 라우팅

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { useWizardStore } from '@/stores/wizard'
import WizardLayout from '@/components/layout/WizardLayout.vue'
import Step1IdeaInput from '@/components/steps/Step1IdeaInput.vue'
import Step2BrandNames from '@/components/steps/Step2BrandNames.vue'
import Step3BrandLogo from '@/components/steps/Step3BrandLogo.vue'
import Step4Domain from '@/components/steps/Step4Domain.vue'
import Step5FinalGuide from '@/components/steps/Step5FinalGuide.vue'

const store = useWizardStore()

const stepComponents: Record<number, any> = {
  1: Step1IdeaInput,
  2: Step2BrandNames,
  3: Step3BrandLogo,
  4: Step4Domain,
  5: Step5FinalGuide,
}

const currentComponent = computed(() => stepComponents[store.currentStep])
</script>

<template>
  <WizardLayout>
    <component :is="currentComponent" />
  </WizardLayout>
</template>
```

Vue Router 불필요 — Pinia `currentStep` + `<component :is>`로 동적 렌더링.

### 10. 에러 핸들링 패턴

각 Step 컴포넌트에서 API 호출 시 동일한 패턴:

```typescript
async function handleSubmit() {
  store.isLoading = true
  store.error = null
  try {
    const result = await recommendBrand(payload)
    store.brandResult = result
    store.nextStep()
  } catch (e: any) {
    store.error = e.message
  } finally {
    store.isLoading = false
  }
}
```

`ErrorAlert`는 `store.error`를 구독하여 자동 표시. `@retry` 이벤트로 재호출.

### 11. Dockerfile

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
```

`nginx.conf`: SPA fallback (모든 경로 → index.html) + `/api` 리버스 프록시 → `back-end:9000`

---

## 의존성 (`package.json`)

```
vue                              # UI 프레임워크
pinia                            # 상태 관리
pinia-plugin-persistedstate      # localStorage 지속
lucide-vue-next                  # 아이콘
markdown-it                      # Step5 리포트 렌더링
vite, @vitejs/plugin-vue         # 빌드
tailwindcss, @tailwindcss/vite   # 스타일링
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

1. 프로젝트 초기화 + 타입/API + 스토어 — 기반
2. 레이아웃/공통 컴포넌트 — 뼈대
3. Step 1 (입력) + Step 2 (브랜드 추천) — 핵심 데모 플로우
4. Step 3 (로고) + Step 4 (도메인) — 전체 플로우 완성
5. Step 5 (가이드) + 마무리 — 최종 완성
