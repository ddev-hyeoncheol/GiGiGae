<script setup lang="ts">
  import { ref } from 'vue'
  import { useWizardStore } from '@/stores/wizard'
  import { useRouter } from 'vue-router'
  import { recommendBrand } from '@/api'
  import ChipSelect from '@/components/ChipSelect.vue'
  import type { ChipOption } from '@/components/ChipSelect.vue'

  const wizard = useWizardStore()
  const router = useRouter()

  const loading = ref(false)
  const error = ref('')
  const showOptions = ref(false)
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

  async function handleStart() {
    const idea = wizard.idea.trim()
    if (!idea) return

    loading.value = true
    error.value = ''

    try {
      const allCategories = customCategoryText.value.trim()
        ? [...wizard.brandCategory, customCategoryText.value.trim()]
        : [...wizard.brandCategory]
      const category = allCategories.length ? allCategories : undefined
      const tone = wizard.brandTone.length ? wizard.brandTone : undefined
      const res = await recommendBrand({ brand_idea: idea, brand_category: category, brand_tone: tone })
      wizard.brandCandidates = res.brand_candidates
      wizard.nextStep()
      router.push('/brand-name')
    } catch (e) {
      error.value = e instanceof Error ? e.message : '브랜드 추천 중 오류가 발생했습니다.'
    } finally {
      loading.value = false
    }
  }
</script>

<template>
  <div class="page">
    <main class="content">
      <div class="hero">
        <p class="subtitle text-muted">AI 기반 브랜드 론칭 자동화 서비스</p>
      </div>

      <div class="input-section surface">
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
          rows="4"
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
            <template v-else>시작하기</template>
          </button>
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
  .page {
    min-height: calc(100vh - 120px);
    display: flex;
    flex-direction: column;
  }

  .content {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem 1rem;
    gap: 2rem;
  }

  .hero {
    text-align: center;
  }

  .subtitle {
    font-size: 1.1rem;
    margin-top: 0.5rem;
  }

  .input-section {
    width: 100%;
    max-width: 600px;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
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

  .idea-input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    background-color: var(--color-bg);
    color: var(--color-text);
    font-family: inherit;
    font-size: 0.95rem;
    resize: vertical;
    transition:
      border-color 0.2s ease,
      background-color 0.2s ease;
  }

  .idea-input:focus {
    outline: none;
    border-color: var(--color-primary);
  }

  .idea-input:disabled {
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

  /* 기타 칩 - ChipSelect 내부 slot 용 */
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
