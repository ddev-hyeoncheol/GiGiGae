<script setup lang="ts">
  import { useWizardStore } from '@/stores/wizard'

  const wizard = useWizardStore()

  const steps = [
    { number: 1, label: '아이디어 입력' },
    { number: 2, label: '브랜드명 추천' },
    { number: 3, label: '로고 추천' },
    { number: 4, label: '도메인 추천' },
    { number: 5, label: '배포 가이드' },
  ]
</script>

<template>
  <nav class="step-indicator">
    <ol class="step-list">
      <li
        v-for="step in steps"
        :key="step.number"
        class="step-item"
        :class="{
          active: wizard.currentStep === step.number,
          completed: wizard.currentStep > step.number,
        }"
      >
        <div class="step-bar" />
        <span class="step-label">{{ step.label }}</span>
      </li>
    </ol>
  </nav>
</template>

<style scoped>
  .step-indicator {
    width: 100%;
    max-width: 560px;
    margin: 0 auto;
    padding: 1.5rem 1rem;
  }

  .step-list {
    display: flex;
    gap: 6px;
    list-style: none;
  }

  .step-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    transition: flex-grow 0.4s ease;
  }

  .step-item.active {
    flex-grow: 3;
  }

  .step-bar {
    width: 100%;
    height: 4px;
    border-radius: 2px;
    background-color: var(--color-border);
    transition:
      background-color 0.3s ease,
      height 0.4s ease;
  }

  .step-item.active .step-bar {
    height: 6px;
  }

  .step-label {
    font-size: 0.75rem;
    color: var(--color-text-muted);
    transition: color 0.3s ease;
  }

  /* Active */
  .step-item.active .step-bar {
    background-color: var(--color-primary);
  }

  .step-item.active .step-label {
    color: var(--color-primary);
    font-weight: 600;
  }

  /* Completed */
  .step-item.completed .step-bar {
    background-color: var(--color-success);
  }

  .step-item.completed .step-label {
    color: var(--color-success);
  }
</style>
