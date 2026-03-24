<script setup lang="ts">
  import { useWizardStore } from '@/stores/wizard'
  import { useRouter } from 'vue-router'
  import StepIndicator from '@/components/StepIndicator.vue'

  const wizard = useWizardStore()
  const router = useRouter()

  function handleBack() {
    wizard.prevStep()
    router.push('/brand-domain')
  }

  function handleReset() {
    wizard.reset()
    router.push('/')
  }
</script>

<template>
  <div class="page">
    <StepIndicator />
    <main class="content">
      <div class="header">
        <h2>배포 가이드</h2>
        <p class="text-muted">선택하신 정보를 바탕으로 생성된 NHN Cloud 배포 가이드입니다.</p>
      </div>

      <div class="summary surface">
        <h3>선택 요약</h3>
        <dl class="summary-list">
          <div class="summary-item">
            <dt>아이디어</dt>
            <dd>{{ wizard.idea }}</dd>
          </div>
          <div class="summary-item">
            <dt>브랜드명</dt>
            <dd>
              {{ wizard.selectedBrand?.name }}
              <span
                :class="
                  wizard.selectedBrand?.risk === 'Low' ? 'badge-success' : 'badge-danger'
                "
              >
                {{ wizard.selectedBrand?.risk }}
              </span>
            </dd>
          </div>
          <div class="summary-item">
            <dt>로고</dt>
            <dd>{{ wizard.selectedLogo?.label }}</dd>
          </div>
          <div class="summary-item">
            <dt>도메인</dt>
            <dd>{{ wizard.selectedDomain?.domain }}</dd>
          </div>
        </dl>
      </div>

      <div class="report surface">
        <h3>NHN Cloud 배포 가이드</h3>
        <div class="report-placeholder text-muted">
          <p>이 영역에 LLM이 생성한 배포 가이드 리포트가 표시됩니다.</p>
          <p>Markdown 또는 HTML 형식으로 렌더링 예정입니다.</p>
        </div>
      </div>

      <div class="nav-buttons">
        <button class="btn-secondary" @click="handleBack">이전</button>
        <button class="btn-primary" @click="handleReset">처음으로</button>
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
    padding: 1rem 1rem 2rem;
    gap: 1.5rem;
  }

  .header {
    text-align: center;
  }

  .header h2 {
    font-size: 1.8rem;
    font-weight: 700;
  }

  .header p {
    margin-top: 0.4rem;
    font-size: 0.95rem;
  }

  .summary,
  .report {
    width: 100%;
    max-width: 560px;
    padding: 1.5rem;
  }

  .summary h3,
  .report h3 {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--color-border);
  }

  .summary-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .summary-item {
    display: flex;
    gap: 1rem;
  }

  .summary-item dt {
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--color-text-muted);
    min-width: 80px;
    flex-shrink: 0;
  }

  .summary-item dd {
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .report-placeholder {
    text-align: center;
    padding: 2rem 1rem;
    font-size: 0.9rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .nav-buttons {
    display: flex;
    gap: 1rem;
    margin-top: 0.5rem;
  }
</style>
