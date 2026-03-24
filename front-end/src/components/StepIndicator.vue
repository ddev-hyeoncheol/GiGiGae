<script setup lang="ts">
  import { useWizardStore } from '@/stores/wizard'

  const wizard = useWizardStore()

  const steps = [
    { number: 1, label: '아이디어' },
    { number: 2, label: '브랜드명' },
    { number: 3, label: '로고' },
    { number: 4, label: '도메인' },
    { number: 5, label: '가이드' },
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
        <div class="step-circle">
          <svg
            v-if="wizard.currentStep > step.number"
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="3"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polyline points="20 6 9 17 4 12" />
          </svg>
          <span v-else>{{ step.number }}</span>
        </div>
        <span class="step-label">{{ step.label }}</span>
      </li>
    </ol>
  </nav>
</template>

<style scoped>
  .step-indicator {
    width: 100%;
    max-width: 640px;
    margin: 0 auto;
    padding: 1.5rem 1rem;
  }

  .step-list {
    display: flex;
    justify-content: space-between;
    align-items: center;
    list-style: none;
    position: relative;
  }

  /* 연결선 */
  .step-list::before {
    content: '';
    position: absolute;
    top: 18px;
    left: 36px;
    right: 36px;
    height: 2px;
    background-color: var(--color-border);
    z-index: 0;
  }

  .step-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    position: relative;
    z-index: 1;
  }

  .step-circle {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    font-weight: 600;
    background-color: var(--color-surface);
    border: 2px solid var(--color-border);
    color: var(--color-text-muted);
    transition:
      background-color 0.2s ease,
      border-color 0.2s ease,
      color 0.2s ease;
  }

  .step-label {
    font-size: 0.75rem;
    color: var(--color-text-muted);
    transition: color 0.2s ease;
  }

  /* Active */
  .step-item.active .step-circle {
    background-color: var(--color-primary);
    border-color: var(--color-primary);
    color: #ffffff;
  }

  .step-item.active .step-label {
    color: var(--color-primary);
    font-weight: 600;
  }

  /* Completed */
  .step-item.completed .step-circle {
    background-color: var(--color-success);
    border-color: var(--color-success);
    color: #ffffff;
  }

  .step-item.completed .step-label {
    color: var(--color-success);
  }
</style>
