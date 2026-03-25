<script setup lang="ts">
  import { ref } from 'vue'
  import { useWizardStore } from '@/stores/wizard'
  import { useRouter } from 'vue-router'
  import { recommendBrand, searchTrademark, searchTrademarkByImage } from '@/api'
  import ChipSelect from '@/components/ChipSelect.vue'
  import type { ChipOption } from '@/components/ChipSelect.vue'

  const wizard = useWizardStore()
  const router = useRouter()

  const error = ref('')

  const ideaMessages = [
    '입력하신 아이디어를 분석하고 있어요.',
    '브랜드명 후보를 조합하고 있어요.',
    '유사한 상표가 있는지 확인하고 있어요.',
    '거의 다 됐어요. 조금만 기다려 주세요.',
  ]

  const brandMessages = [
    '동일한 상표가 등록 또는 출원되어 있는지 확인하고 있어요.',
    '유사한 상표가 있는지 검색하고 있어요.',
    '충돌 위험도를 분석하고 있어요.',
    '거의 다 됐어요. 조금만 기다려 주세요.',
  ]
  const showOptions = ref(false)
  const showBrandOptions = ref(false)
  const logoFile = ref<File | null>(null)

  function fileToBase64(file: File): Promise<string> {
    return new Promise((resolve) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result as string)
      reader.readAsDataURL(file)
    })
  }

  async function handleLogoUpload(e: Event) {
    const input = e.target as HTMLInputElement
    const file = input.files?.[0]
    if (!file) return
    logoFile.value = file
    wizard.logoPreview = await fileToBase64(file)
  }

  function removeLogo() {
    logoFile.value = null
    wizard.logoPreview = null
  }

  const dragging = ref(false)

  async function handleDrop(e: DragEvent) {
    dragging.value = false
    const file = e.dataTransfer?.files?.[0]
    if (file && file.type.startsWith('image/')) {
      logoFile.value = file
      wizard.logoPreview = await fileToBase64(file)
    }
  }
  const customCategory = ref(false)
  const customCategoryText = ref('')

  const MAX_CATEGORY = 2
  const MAX_TONE = 3

  const categoryNiceMap: Record<string, string[]> = {
    '이커머스 · 온라인스토어': ['35', '42'],
    'F&B · 카페 · 숙박': ['29', '30', '32', '43'],
    'IT · SaaS · 테크': ['9', '42'],
    '패션 · 의류 브랜드': ['18', '25', '26'],
    '뷰티 · 코스메틱': ['3', '44'],
    '디지털 · 전자제품': ['11', '28'],
    '카페 · 베이커리 · 식품': ['29', '30', '31', '32'],
  }

  function resolveNiceClasses(): string[] {
    const codes = new Set<string>()
    for (const cat of wizard.brandCategory) {
      for (const code of (categoryNiceMap[cat] ?? [])) codes.add(code)
    }
    return [...codes]
  }

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
    error.value = ''
    const messages = wizard.inputMode === 'idea' ? ideaMessages : brandMessages
    wizard.startLoading(messages)

    try {
      if (wizard.inputMode === 'idea') {
        const idea = wizard.idea.trim()
        if (!idea) return

        const allCategories = customCategoryText.value.trim()
          ? [...wizard.brandCategory, customCategoryText.value.trim()]
          : [...wizard.brandCategory]
        const category = allCategories.length ? allCategories : undefined
        const tone = wizard.brandTone.length ? wizard.brandTone : undefined
        const res = await recommendBrand({ brand_idea: idea, brand_category: category, brand_tone: tone, count: 4 })
        wizard.brandCandidates = res.brand_candidates
        wizard.nextStep()
        router.push('/brand-name')
      } else {
        const brandName = wizard.directBrandName.trim()
        if (!brandName) return

        const [trademarkRes, imageRes] = await Promise.all([
          searchTrademark({ brand_name: brandName, nice_classes: resolveNiceClasses() }),
          logoFile.value ? searchTrademarkByImage(logoFile.value) : Promise.resolve(null),
        ])

        wizard.trademarkResult = trademarkRes
        wizard.imageSearchResult = imageRes
        wizard.selectedBrand = {
          brand_name: brandName,
          brand_description: '',
          brand_tags: [],
          trademark: trademarkRes,
        }
        wizard.goToStep(3)
        router.push('/trademark')
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : '요청 처리 중 오류가 발생했습니다.'
    } finally {
      wizard.stopLoading()
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
          />
          <Transition name="slide">
            <div v-if="showOptions" class="options-panel">
              <hr class="divider" />
              <label class="option-label">브랜드 카테고리 <span class="option-hint">(최대 2개)</span></label>
              <ChipSelect
                v-model="wizard.brandCategory"
                :options="categories"
                :max="MAX_CATEGORY"
              >
                <button
                  class="chip"
                  :class="{ selected: customCategory, locked: isCustomLocked() }"
                  :disabled="isCustomLocked()"
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
              />

              <label class="option-label tone-label">브랜드 톤 <span class="option-hint">(최대 3개)</span></label>
              <ChipSelect
                v-model="wizard.brandTone"
                :options="tones"
                :max="MAX_TONE"
              />
            </div>
          </Transition>

          <button class="btn-options" @click="showOptions = !showOptions">
            <span class="btn-options-arrow" :class="{ open: showOptions }">&#8250;</span>
            조금 더 자세히 표현해 볼까요
          </button>
        </template>

        <!-- 브랜드명 모드 -->
        <template v-else>
          <label for="brand-name" class="input-label">브랜드명 <span class="option-hint">(필수)</span></label>
          <input
            id="brand-name"
            v-model="wizard.directBrandName"
            class="brand-input"
            type="text"
            placeholder="분석할 브랜드명을 입력하세요"
            @keyup.enter="handleStart"
          />

          <label class="input-label">로고 이미지 <span class="option-hint">(선택)</span></label>
          <div class="logo-upload">
            <template v-if="wizard.logoPreview">
              <div class="logo-preview">
                <img :src="wizard.logoPreview" alt="로고 미리보기" />
                <button class="logo-remove" @click="removeLogo">&times;</button>
              </div>
            </template>
            <label
              v-else
              class="logo-dropzone"
              :class="{ 'logo-dragging': dragging }"
              @dragenter.prevent="dragging = true"
              @dragover.prevent="dragging = true"
              @dragleave.prevent="dragging = false"
              @drop.prevent="handleDrop"
            >
              <span class="logo-dropzone-icon">+</span>
              <span class="logo-dropzone-text">로고 이미지를 업로드하면<br/>시각적으로 유사한 상표들을 함께 검색해요.</span>
              <input type="file" accept="image/*" hidden @change="handleLogoUpload" />
            </label>
          </div>
          <Transition name="slide">
            <div v-if="showBrandOptions" class="options-panel">
              <hr class="divider" />
              <label class="option-label">브랜드 카테고리 <span class="option-hint">(최대 2개)</span></label>
              <ChipSelect
                v-model="wizard.brandCategory"
                :options="categories"
                :max="MAX_CATEGORY"
              >
                <button
                  class="chip"
                  :class="{ selected: customCategory, locked: isCustomLocked() }"
                  :disabled="isCustomLocked()"
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
              />
            </div>
          </Transition>

          <button class="btn-options" @click="showBrandOptions = !showBrandOptions">
            <span class="btn-options-arrow" :class="{ open: showBrandOptions }">&#8250;</span>
            조금 더 자세히 표현해 볼까요
          </button>
        </template>

        <p v-if="error" class="error-msg">{{ error }}</p>
      </div>

      <button class="btn-primary btn-submit" :disabled="!wizard.canGoNext" @click="handleStart">
        {{ wizard.inputMode === 'idea' ? '브랜드명 추천받기' : '브랜드명 분석하기' }}
      </button>
    </main>

  </div>
</template>

<style scoped>
  .page {
    display: flex;
    flex-direction: column;
    position: relative;
  }

  .content {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    padding: 2rem 1rem;
    gap: 2rem;
    max-width: 600px;
    margin: auto;
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
    font-size: 1.4rem;
    transform: rotate(90deg);
    transition: transform 0.2s ease;
  }

  .btn-options-arrow.open {
    transform: rotate(270deg);
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

  .btn-submit {
    width: 100%;
    margin-top: -0.75rem;
    padding: 0.85rem 1.5rem;
    font-size: 1rem;
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

  .logo-upload {
    width: 100%;
  }

  .logo-dropzone {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 1.5rem;
    border: 2px dashed var(--color-border);
    border-radius: var(--radius);
    background: var(--color-bg);
    cursor: pointer;
    transition: border-color 0.2s ease;
  }

  .logo-dropzone:hover,
  .logo-dropzone.logo-dragging {
    border-color: var(--color-primary);
    background: color-mix(in srgb, var(--color-primary) 5%, transparent);
  }

  .logo-dropzone-icon {
    font-size: 1.8rem;
    color: var(--color-text-muted);
    line-height: 1;
  }

  .logo-dropzone-text {
    font-size: 0.8rem;
    color: var(--color-text-muted);
    text-align: center;
    line-height: 1.5;
  }

  .logo-preview {
    position: relative;
    display: inline-block;
  }

  .logo-preview img {
    max-width: 100%;
    max-height: 120px;
    border-radius: var(--radius);
    border: 1px solid var(--color-border);
    object-fit: contain;
  }

  .logo-remove {
    position: absolute;
    top: -0.4rem;
    right: -0.4rem;
    width: 1.4rem;
    height: 1.4rem;
    border: none;
    border-radius: 50%;
    background: var(--color-danger);
    color: #fff;
    font-size: 0.9rem;
    line-height: 1;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .error-msg {
    color: var(--color-danger);
    font-size: 0.85rem;
    margin: 0;
  }
</style>
