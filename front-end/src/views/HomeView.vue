<script setup lang="ts">
  import { ref } from 'vue'
  import { useWizardStore } from '@/stores/wizard'
  import { useRouter } from 'vue-router'
  import { recommendBrand, searchTrademark } from '@/api'
  import ChipSelect from '@/components/ChipSelect.vue'
  import type { ChipOption } from '@/components/ChipSelect.vue'
  import LoadingOverlay from '@/components/LoadingOverlay.vue'

  const wizard = useWizardStore()
  const router = useRouter()

  const loading = ref(false)
  const error = ref('')

  const ideaMessages = [
    '아이디어와 어울리는 브랜드명이 무엇인지 고민하고 있어요.',
    '입력하신 정보와 가장 어울리는 브랜드명을 조합하고 있어요.',
    '브랜드명이 이미 출원/등록되어 있는지 확인하고 있어요.',
    '이미 출원된 브랜드명이 있으면 다른 브랜드명을 추천할지 생각하고 있어요.',
    '이제 거의 다 됐어요.',
  ]

  const brandMessages = [
    '브랜드명이 이미 출원/등록되어 있는지 확인하고 있어요.',
    '유사한 상표가 있는지 검색하고 있어요.',
    '위험도를 분석하고 있어요.',
    '이제 거의 다 됐어요.',
  ]
  const showOptions = ref(false)
  const showBrandOptions = ref(false)
  const customCategory = ref(false)
  const customCategoryText = ref('')

  const MAX_CATEGORY = 2
  const MAX_TONE = 3

  const categories: ChipOption[] = [
    { emoji: '🛒', label: '이커머스 · 온라인스토어' },
    { emoji: '🍽️', label: 'F&B · 카페 · 숙박' },
    { emoji: '💻', label: 'IT · SaaS · 테크' },
    { emoji: '👕', label: '패션 · 의류 브랜드' },
    { emoji: '💄', label: '뷰티 · 코스메틱' },
    { emoji: '📱', label: '디지털 · 전자제품' },
    { emoji: '🧁', label: '카페 · 베이커리 · 식품' },
  ]

  const tones: ChipOption[] = [
    '트렌디한', '신뢰감 있는', '모던한', '프리미엄', '시크한',
    '활기찬', '친근한', '미니멀', '따뜻한', '감성적인',
    '격식있는', '캐주얼한',
  ].map(label => ({ label }))

  function isCustomLocked() {
    return !customCategory.value && wizard.brandCategory.length >= MAX_CATEGORY
  }

  function selectCustom() {
    if (customCategory.value) {
      customCategory.value = false
      customCategoryText.value = ''
    } else if (wizard.brandCategory.length < MAX_CATEGORY) {
      customCategory.value = true
    }
  }

  function setMode(mode: 'idea' | 'brand') {
    wizard.inputMode = mode
    error.value = ''
  }

  async function handleStart() {
    loading.value = true
    error.value = ''

    try {
      if (wizard.inputMode === 'idea') {
        const idea = wizard.idea.trim()
        if (!idea) return

        const allCategories = customCategoryText.value.trim()
          ? [...wizard.brandCategory, customCategoryText.value.trim()]
          : [...wizard.brandCategory]
        const category = allCategories.length ? allCategories : undefined
        const tone = wizard.brandTone.length ? wizard.brandTone : undefined
        const res = await recommendBrand({ brand_idea: idea, brand_category: category, brand_tone: tone })
        wizard.brandCandidates = res.brand_candidates
        wizard.nextStep()
        router.push('/brand-name')
      } else {
        const brandName = wizard.directBrandName.trim()
        if (!brandName) return

        const res = await searchTrademark({ brand_name: brandName })
        wizard.trademarkResult = res
        wizard.selectedBrand = {
          brand_name: brandName,
          brand_description: '',
          brand_tags: [],
          trademark: res,
        }
        wizard.goToStep(3)
        router.push('/trademark')
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : '요청 처리 중 오류가 발생했습니다.'
    } finally {
      loading.value = false
    }
  }
</script>

<template>
  <div class="page">
    <main class="content">
      <div class="hero">
        <h1 class="hero-title">어떤 브랜드를<br/>만들고 싶으세요?</h1>
        <p class="subtitle text-muted">아이디어를 입력하면 이름 추천부터<br/>상표와 도메인 확인까지 한 번에 도와드릴게요</p>
      </div>

      <div class="mode-tabs">
        <button
          class="mode-tab"
          :class="{ active: wizard.inputMode === 'idea' }"
          @click="setMode('idea')"
        >
          아이디어로 시작하기
        </button>
        <button
          class="mode-tab"
          :class="{ active: wizard.inputMode === 'brand' }"
          @click="setMode('brand')"
        >
          브랜드명 바로 검토하기
        </button>
      </div>

      <div class="input-section surface">
        <!-- 아이디어 모드 -->
        <template v-if="wizard.inputMode === 'idea'">
          <div class="input-header">
            <label for="idea" class="input-label">브랜드 아이디어 <span class="option-hint">(최대 250자)</span></label>
            <span class="char-count text-muted">{{ wizard.idea.length }}/250</span>
          </div>
          <textarea
            id="idea"
            v-model="wizard.idea"
            class="idea-input"
            placeholder="예: 친환경 반려동물 용품을 판매하는 감성 브랜드"
            maxlength="250"
            rows="3"
            :disabled="loading"
          />
          <Transition name="slide">
            <div v-if="showOptions" class="options-panel">
              <hr class="divider" />
              <label class="option-label">브랜드 카테고리 <span class="option-hint">(최대 2개)</span></label>
              <ChipSelect
                v-model="wizard.brandCategory"
                :options="categories"
                :max="MAX_CATEGORY"
                :disabled="loading"
              >
                <button
                  class="chip"
                  :class="{ selected: customCategory, locked: isCustomLocked() }"
                  :disabled="loading || isCustomLocked()"
                  @click="selectCustom"
                >
                  <span class="chip-emoji">✏️</span>
                  <span>기타 (직접 입력)</span>
                </button>
              </ChipSelect>
              <input
                v-if="customCategory"
                v-model="customCategoryText"
                class="option-input"
                type="text"
                placeholder="카테고리를 직접 입력하세요"
                :disabled="loading"
              />

              <label class="option-label tone-label">브랜드 톤 <span class="option-hint">(최대 3개)</span></label>
              <ChipSelect
                v-model="wizard.brandTone"
                :options="tones"
                :max="MAX_TONE"
                :disabled="loading"
              />
            </div>
          </Transition>

          <div class="input-footer">
            <button class="btn-options" @click="showOptions = !showOptions">
              추가 옵션
              <span class="btn-options-arrow" :class="{ open: showOptions }">&#9662;</span>
            </button>
            <button class="btn-primary" :disabled="!wizard.canGoNext || loading" @click="handleStart">
              <template v-if="loading">
                <span class="spinner" /> 분석 중...
              </template>
              <template v-else>브랜드명 추천</template>
            </button>
          </div>
        </template>

        <!-- 브랜드명 모드 -->
        <template v-else>
          <label for="brand-name" class="input-label">브랜드명</label>
          <input
            id="brand-name"
            v-model="wizard.directBrandName"
            class="brand-input"
            type="text"
            placeholder="검토할 브랜드명을 입력하세요"
            :disabled="loading"
            @keyup.enter="handleStart"
          />
          <Transition name="slide">
            <div v-if="showBrandOptions" class="options-panel">
              <hr class="divider" />
              <label class="option-label">브랜드 카테고리 <span class="option-hint">(최대 2개)</span></label>
              <ChipSelect
                v-model="wizard.brandCategory"
                :options="categories"
                :max="MAX_CATEGORY"
                :disabled="loading"
              >
                <button
                  class="chip"
                  :class="{ selected: customCategory, locked: isCustomLocked() }"
                  :disabled="loading || isCustomLocked()"
                  @click="selectCustom"
                >
                  <span class="chip-emoji">✏️</span>
                  <span>기타 (직접 입력)</span>
                </button>
              </ChipSelect>
              <input
                v-if="customCategory"
                v-model="customCategoryText"
                class="option-input"
                type="text"
                placeholder="카테고리를 직접 입력하세요"
                :disabled="loading"
              />
            </div>
          </Transition>

          <div class="input-footer">
            <button class="btn-options" @click="showBrandOptions = !showBrandOptions">
              추가 옵션
              <span class="btn-options-arrow" :class="{ open: showBrandOptions }">&#9662;</span>
            </button>
            <button class="btn-primary" :disabled="!wizard.canGoNext || loading" @click="handleStart">
              <template v-if="loading">
                <span class="spinner" /> 검토 중...
              </template>
              <template v-else>브랜드명 검토</template>
            </button>
          </div>
        </template>

        <p v-if="error" class="error-msg">{{ error }}</p>
      </div>
    </main>

    <LoadingOverlay
      :visible="loading"
      :messages="wizard.inputMode === 'idea' ? ideaMessages : brandMessages"
      :interval="3000"
    />
  </div>
</template>

<style scoped>
  .page {
    height: 100%;
    display: flex;
    flex-direction: column;
    position: relative;
  }

  .content {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    justify-content: center;
    padding: 2rem 1rem;
    margin-top: -120px;
    gap: 2rem;
    max-width: 600px;
    margin: -120px auto 0;
    width: 100%;
  }

  .hero {
    text-align: center;
  }

  .hero-title {
    font-size: 2.8rem;
    font-weight: 900;
    color: var(--color-text);
    letter-spacing: -0.03em;
    line-height: 1.2;
  }

  .subtitle {
    font-size: 1rem;
    margin-top: 0.75rem;
    line-height: 1.6;
  }

  .input-section {
    width: 100%;
    margin-top: -1.25rem;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  /* 모드 탭 */
  .mode-tabs {
    display: flex;
    gap: 0.35rem;
  }

  .mode-tab {
    flex: 1;
    padding: 0.7rem 1rem;
    border: 1px solid var(--color-primary);
    border-radius: var(--radius);
    background: transparent;
    color: var(--color-primary);
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .mode-tab:hover {
    background: color-mix(in srgb, var(--color-primary) 10%, transparent);
  }

  .mode-tab.active {
    background: var(--color-primary);
    color: #fff;
    font-weight: 600;
  }

  .input-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
  }

  .input-label {
    font-weight: 600;
    font-size: 0.9rem;
  }

  .char-count {
    font-size: 0.75rem;
  }

  .idea-input,
  .brand-input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    background-color: var(--color-bg);
    color: var(--color-text);
    font-family: inherit;
    font-size: 0.95rem;
    transition:
      border-color 0.2s ease,
      background-color 0.2s ease;
  }

  .idea-input {
    resize: vertical;
  }

  .idea-input:focus,
  .brand-input:focus {
    outline: none;
    border-color: var(--color-primary);
  }

  .idea-input:disabled,
  .brand-input:disabled {
    opacity: 0.6;
  }

  .btn-options {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.5rem 0.5rem;
    border: none;
    background: none;
    color: var(--color-text-muted);
    font-size: 0.9rem;
    cursor: pointer;
    transition: color 0.15s ease;
  }

  .btn-options:hover {
    color: var(--color-primary);
  }

  .btn-options-arrow {
    display: inline-block;
    font-size: 1rem;
    transition: transform 0.2s ease;
  }

  .btn-options-arrow.open {
    transform: rotate(180deg);
  }

  .divider {
    border: none;
    border-top: 1px solid var(--color-border);
    margin: 0.4rem 0;
  }

  .options-panel {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    overflow: hidden;
  }

  .option-label {
    font-weight: 600;
    font-size: 0.9rem;
  }

  .option-hint {
    font-weight: 400;
    font-size: 0.8rem;
    color: var(--color-text-muted);
  }

  .tone-label {
    margin-top: 0.5rem;
  }

  .chip {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.35rem 0.65rem;
    border: 1px solid var(--color-border);
    border-radius: 100px;
    background: var(--color-bg);
    color: var(--color-text);
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .chip:hover:not(.locked) {
    border-color: var(--color-primary);
  }

  .chip.selected {
    border-color: var(--color-primary);
    background: var(--color-primary);
    color: #fff;
  }

  .chip.locked {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .chip-emoji {
    font-size: 0.85rem;
  }

  .option-input {
    width: 100%;
    padding: 0.5rem 0.75rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    background-color: var(--color-bg);
    color: var(--color-text);
    font-family: inherit;
    font-size: 0.85rem;
    transition: border-color 0.2s ease;
  }

  .option-input:focus {
    outline: none;
    border-color: var(--color-primary);
  }

  .slide-enter-active,
  .slide-leave-active {
    transition: all 0.3s ease;
  }

  .slide-enter-from,
  .slide-leave-to {
    opacity: 0;
    max-height: 0;
    margin-top: -0.75rem;
  }

  .slide-enter-to,
  .slide-leave-from {
    opacity: 1;
    max-height: 500px;
  }

  .input-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .spinner {
    display: inline-block;
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
    vertical-align: middle;
    margin-right: 0.4rem;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .error-msg {
    color: var(--color-danger, #e74c3c);
    font-size: 0.85rem;
    margin: 0;
  }
</style>
