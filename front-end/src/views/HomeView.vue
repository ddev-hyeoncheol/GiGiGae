<script setup lang="ts">
  import { useWizardStore } from '@/stores/wizard'
  import { useRouter } from 'vue-router'
  import StepIndicator from '@/components/StepIndicator.vue'

  const wizard = useWizardStore()
  const router = useRouter()

  function handleStart() {
    if (wizard.idea.trim().length > 0) {
      wizard.nextStep()
      router.push('/brand-name')
    }
  }
</script>

<template>
  <div class="page">
    <StepIndicator />
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
        />
        <div class="input-footer">
          <span class="char-count text-muted">{{ wizard.idea.length }} / 250</span>
          <button class="btn-primary" :disabled="!wizard.canGoNext" @click="handleStart">
            시작하기
          </button>
        </div>
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
</style>
