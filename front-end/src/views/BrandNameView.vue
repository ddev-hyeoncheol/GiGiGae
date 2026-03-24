<script setup lang="ts">
  import { useWizardStore } from '@/stores/wizard'
  import { useRouter } from 'vue-router'
  import type { BrandCandidate } from '@/stores/wizard'
  import PageHeader from '@/components/PageHeader.vue'
  import NavButtons from '@/components/NavButtons.vue'

  const wizard = useWizardStore()
  const router = useRouter()

  /* 데이터 없이 직접 접근한 경우 홈으로 리다이렉트 */
  if (wizard.brandCandidates.length === 0) {
    router.replace('/')
  }

  function selectBrand(candidate: BrandCandidate) {
    if (wizard.selectedBrand?.brand_name !== candidate.brand_name) {
      wizard.domainCandidates = []
      wizard.selectedDomain = null
    }
    wizard.selectedBrand = candidate
  }

  function riskLabel(risk: string) {
    switch (risk) {
      case 'Low': return 'Low'
      case 'Middle': return 'Middle'
      case 'High': return 'High'
      default: return 'unchecked'
    }
  }

  function riskClass(risk: string) {
    switch (risk) {
      case 'Low': return 'badge-success'
      case 'Middle': return 'badge-warning'
      case 'High': return 'badge-danger'
      default: return 'badge-muted'
    }
  }

  function handleNext() {
    if (wizard.selectedBrand) {
      wizard.trademarkResult = wizard.selectedBrand.trademark
      wizard.nextStep()
      router.push('/trademark')
    }
  }

  function handleBack() {
    wizard.prevStep()
    router.push('/')
  }
</script>

<template>
  <div class="page">
    <main class="content">
      <PageHeader title="브랜드명 추천">
        "{{ wizard.idea }}" 에 대한 브랜드 후보입니다. 하나를 선택하세요.
      </PageHeader>

      <div class="content-body">
        <ul class="candidate-list">
          <li
            v-for="candidate in wizard.brandCandidates"
            :key="candidate.brand_name"
            class="candidate-card surface"
            :class="{ selected: wizard.selectedBrand?.brand_name === candidate.brand_name }"
            @click="selectBrand(candidate)"
          >
            <div class="card-top">
              <span class="brand-name">{{ candidate.brand_name }}</span>
              <span :class="riskClass(candidate.trademark.risk)">
                {{ riskLabel(candidate.trademark.risk) }}
              </span>
            </div>
            <p class="brand-desc text-muted">{{ candidate.brand_description }}</p>
            <div class="brand-tags">
              <span v-for="tag in candidate.brand_tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </li>
        </ul>

        <NavButtons
          back-label="이전으로"
          next-label="상표권 확인하기"
          :next-disabled="!wizard.canGoNext"
          @next="handleNext"
          @back="handleBack"
        />
      </div>
    </main>
  </div>
</template>

<style scoped>
  .page {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .content {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 1rem 1rem 2rem;
    gap: 1.5rem;
  }

  .content-body {
    width: 100%;
    max-width: 720px;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .candidate-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 0.75rem;
    width: 100%;
    list-style: none;
  }

  .candidate-card {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 1rem 1.25rem;
    cursor: pointer;
    transition:
      border-color 0.2s ease,
      transform 0.15s ease;
  }

  .candidate-card:hover {
    transform: translateY(-2px);
  }

  .candidate-card.selected {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 2px var(--color-primary);
  }

  .card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .brand-name {
    font-weight: 600;
    font-size: 1.05rem;
  }

  .brand-desc {
    font-size: 0.85rem;
    margin: 0;
    line-height: 1.4;
  }

  .brand-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
  }

  .tag {
    font-size: 0.75rem;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    background-color: var(--color-surface-alt, var(--color-border));
    color: var(--color-text-muted, var(--color-text));
  }

</style>
