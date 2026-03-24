<script setup lang="ts">
  import { ref } from 'vue'
  import { useWizardStore } from '@/stores/wizard'
  import { useRouter } from 'vue-router'
  import { recommendBrand } from '@/api'

  const wizard = useWizardStore()
  const router = useRouter()

  const loading = ref(false)
  const error = ref('')

  async function handleStart() {
    const idea = wizard.idea.trim()
    if (!idea) return

    loading.value = true
    error.value = ''

    try {
      const res = await recommendBrand({ brand_idea: idea })
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
        <h1 class="title">NameCraft</h1>
        <p class="subtitle text-muted">AI 기반 브랜드 론칭 자동화 서비스</p>
      </div>

      <div class="input-section surface">
        <label for="idea" class="input-label">브랜드 아이디어를 입력하세요</label>
        <textarea
          id="idea"
          v-model="wizard.idea"
          class="idea-input"
          placeholder="예: 친환경 반려동물 용품을 판매하는 감성 브랜드"
          maxlength="250"
          rows="4"
          :disabled="loading"
        />
        <div class="input-footer">
          <span class="char-count text-muted">{{ wizard.idea.length }} / 250</span>
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
    min-height: 100vh;
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

  .title {
    font-size: 3rem;
    font-weight: 700;
    color: var(--color-primary);
  }

  .subtitle {
    font-size: 1.1rem;
    margin-top: 0.5rem;
  }

  .input-section {
    width: 100%;
    max-width: 520px;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .input-label {
    font-weight: 600;
    font-size: 0.9rem;
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

  .input-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .char-count {
    font-size: 0.8rem;
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
