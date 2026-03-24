<script setup lang="ts">
  import { useWizardStore } from '@/stores/wizard'
  import { useRouter } from 'vue-router'
  import StepIndicator from '@/components/StepIndicator.vue'
  import type { BrandCandidate } from '@/stores/wizard'

  const wizard = useWizardStore()
  const router = useRouter()

  /* TODO: API 연동 시 교체 */
  const mockCandidates: BrandCandidate[] = [
    { name: 'EcoPaw', risk: 'Low' },
    { name: 'GreenTail', risk: 'Low' },
    { name: 'PetLeaf', risk: 'High' },
    { name: 'NaturePet', risk: 'Low' },
    { name: 'PawGreen', risk: 'High' },
    { name: 'BioTail', risk: 'Low' },
    { name: 'EarthPaw', risk: 'Low' },
    { name: 'LeafPet', risk: 'High' },
  ]

  if (wizard.brandCandidates.length === 0) {
    wizard.brandCandidates = mockCandidates
  }

  function selectBrand(candidate: BrandCandidate) {
    wizard.selectedBrand = candidate
  }

  function handleNext() {
    if (wizard.selectedBrand) {
      wizard.nextStep()
      router.push('/brand-logo')
    }
  }

  function handleBack() {
    wizard.prevStep()
    router.push('/')
  }
</script>

<template>
  <div class="page">
    <StepIndicator />
    <main class="content">
      <div class="header">
        <h2>브랜드명 추천</h2>
        <p class="text-muted">
          "{{ wizard.idea }}" 에 대한 브랜드 후보입니다. 하나를 선택하세요.
        </p>
      </div>

      <ul class="candidate-list">
        <li
          v-for="candidate in wizard.brandCandidates"
          :key="candidate.name"
          class="candidate-card surface"
          :class="{ selected: wizard.selectedBrand?.name === candidate.name }"
          @click="selectBrand(candidate)"
        >
          <span class="brand-name">{{ candidate.name }}</span>
          <span :class="candidate.risk === 'Low' ? 'badge-success' : 'badge-danger'">
            {{ candidate.risk }}
          </span>
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
    max-width: 480px;
  }

  .candidate-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.75rem;
    width: 100%;
    max-width: 640px;
    list-style: none;
  }

  .candidate-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
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

  .brand-name {
    font-weight: 600;
    font-size: 1rem;
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
