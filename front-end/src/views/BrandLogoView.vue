<script setup lang="ts">
  import { useWizardStore } from '@/stores/wizard'
  import { useRouter } from 'vue-router'
  import type { LogoCandidate } from '@/stores/wizard'
  import PageHeader from '@/components/PageHeader.vue'
  import NavButtons from '@/components/NavButtons.vue'

  const wizard = useWizardStore()
  const router = useRouter()

  /* TODO: MockImageService 또는 실제 API 연동 시 교체 */
  const mockLogos: LogoCandidate[] = [
    { id: 1, url: '', label: 'Style A - Minimal' },
    { id: 2, url: '', label: 'Style B - Bold' },
    { id: 3, url: '', label: 'Style C - Organic' },
    { id: 4, url: '', label: 'Style D - Geometric' },
  ]

  if (wizard.logoCandidates.length === 0) {
    wizard.logoCandidates = mockLogos
  }

  function selectLogo(logo: LogoCandidate) {
    wizard.selectedLogo = logo
  }

  function handleNext() {
    if (wizard.selectedLogo) {
      wizard.nextStep()
      router.push('/brand-domain')
    }
  }

  function handleBack() {
    wizard.prevStep()
    router.push('/brand-name')
  }
</script>

<template>
  <div class="page">
    <main class="content">
      <PageHeader title="로고 후보">
        <strong>{{ wizard.selectedBrand?.brand_name }}</strong> 에 대한 로고 후보입니다.
      </PageHeader>

      <div class="logo-grid">
        <div
          v-for="logo in wizard.logoCandidates"
          :key="logo.id"
          class="logo-card surface"
          :class="{ selected: wizard.selectedLogo?.id === logo.id }"
          @click="selectLogo(logo)"
        >
          <div class="logo-placeholder">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <polyline points="21 15 16 10 5 21" />
            </svg>
          </div>
          <span class="logo-label">{{ logo.label }}</span>
        </div>
      </div>

      <NavButtons
        :next-disabled="!wizard.canGoNext"
        @next="handleNext"
        @back="handleBack"
      />
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

  .logo-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    width: 100%;
    max-width: 480px;
  }

  .logo-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    padding: 1.5rem 1rem;
    cursor: pointer;
    transition:
      border-color 0.2s ease,
      transform 0.15s ease;
  }

  .logo-card:hover {
    transform: translateY(-2px);
  }

  .logo-card.selected {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 2px var(--color-primary);
  }

  .logo-placeholder {
    width: 80px;
    height: 80px;
    border-radius: var(--radius);
    background-color: var(--color-bg);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--color-text-muted);
  }

  .logo-label {
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--color-text-muted);
  }
</style>
