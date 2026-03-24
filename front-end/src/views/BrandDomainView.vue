<script setup lang="ts">
  import { useWizardStore } from '@/stores/wizard'
  import { useRouter } from 'vue-router'
  import type { DomainCandidate } from '@/stores/wizard'

  const wizard = useWizardStore()
  const router = useRouter()

  /* TODO: NHN Cloud API 연동 시 교체 */
  const brandSlug = (wizard.selectedBrand?.name ?? 'brand').toLowerCase()
  const mockDomains: DomainCandidate[] = [
    { domain: `${brandSlug}.com`, available: true, price: '15,000원/년' },
    { domain: `${brandSlug}.co.kr`, available: true, price: '22,000원/년' },
    { domain: `${brandSlug}.kr`, available: false, price: '-' },
    { domain: `${brandSlug}.io`, available: true, price: '45,000원/년' },
    { domain: `${brandSlug}.shop`, available: true, price: '12,000원/년' },
  ]

  if (wizard.domainCandidates.length === 0) {
    wizard.domainCandidates = mockDomains
  }

  function selectDomain(domain: DomainCandidate) {
    if (domain.available) {
      wizard.selectedDomain = domain
    }
  }

  function handleNext() {
    if (wizard.selectedDomain) {
      wizard.nextStep()
      router.push('/final-guide')
    }
  }

  function handleBack() {
    wizard.prevStep()
    router.push('/brand-logo')
  }
</script>

<template>
  <div class="page">
    <main class="content">
      <div class="header">
        <h2>도메인 추천</h2>
        <p class="text-muted">
          <strong>{{ wizard.selectedBrand?.name }}</strong> 에 사용할 도메인을 선택하세요.
        </p>
      </div>

      <ul class="domain-list">
        <li
          v-for="domain in wizard.domainCandidates"
          :key="domain.domain"
          class="domain-card surface"
          :class="{
            selected: wizard.selectedDomain?.domain === domain.domain,
            unavailable: !domain.available,
          }"
          @click="selectDomain(domain)"
        >
          <div class="domain-info">
            <span class="domain-name">{{ domain.domain }}</span>
            <span class="domain-price text-muted">{{ domain.price }}</span>
          </div>
          <span v-if="domain.available" class="badge-success">사용 가능</span>
          <span v-else class="badge-danger">사용 불가</span>
        </li>
      </ul>

      <div class="nav-buttons">
        <button class="btn-secondary" @click="handleBack">이전</button>
        <button class="btn-primary" :disabled="!wizard.canGoNext" @click="handleNext">
          다음
        </button>
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

  .domain-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    width: 100%;
    max-width: 520px;
    list-style: none;
  }

  .domain-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.25rem;
    cursor: pointer;
    transition:
      border-color 0.2s ease,
      transform 0.15s ease;
  }

  .domain-card:hover:not(.unavailable) {
    transform: translateY(-2px);
  }

  .domain-card.selected {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 2px var(--color-primary);
  }

  .domain-card.unavailable {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .domain-info {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
  }

  .domain-name {
    font-weight: 600;
    font-size: 1rem;
  }

  .domain-price {
    font-size: 0.8rem;
  }

  .nav-buttons {
    display: flex;
    gap: 1rem;
    margin-top: 0.5rem;
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
