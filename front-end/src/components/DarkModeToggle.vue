<script setup lang="ts">
  import { useDarkMode } from '@/composables/useDarkMode'

  const { isDark, toggle } = useDarkMode()
</script>

<template>
  <button
    class="dark-toggle"
    @click="toggle"
    :aria-label="isDark ? '라이트 모드로 전환' : '다크 모드로 전환'"
  >
    <svg
      v-if="isDark"
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <circle cx="12" cy="12" r="5" />
      <line x1="12" y1="1" x2="12" y2="3" />
      <line x1="12" y1="21" x2="12" y2="23" />
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
      <line x1="1" y1="12" x2="3" y2="12" />
      <line x1="21" y1="12" x2="23" y2="12" />
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
    </svg>
    <svg
      v-else
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </svg>
  </button>
</template>

<style scoped>
  .dark-toggle {
    position: fixed;
    bottom: 1.5rem;
    right: 1.5rem;
    z-index: 999;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    border: 1px solid var(--color-border);
    background-color: var(--color-surface);
    color: var(--color-text);
    box-shadow: var(--shadow-lg);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition:
      background-color var(--transition),
      color var(--transition),
      border-color var(--transition),
      transform var(--transition);
  }

  .dark-toggle:hover {
    transform: scale(1.1);
    background-color: var(--color-primary);
    color: #ffffff;
    border-color: var(--color-primary);
  }
</style>
