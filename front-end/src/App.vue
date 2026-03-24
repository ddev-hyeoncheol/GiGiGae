<script setup lang="ts">
  import { RouterView } from 'vue-router'
  import AppLogo from '@/components/AppLogo.vue'
  import DarkModeToggle from '@/components/DarkModeToggle.vue'
  import StepIndicator from '@/components/StepIndicator.vue'
</script>

<template>
  <header class="app-header">
    <div class="app-header-side">
      <AppLogo />
    </div>
    <StepIndicator />
    <div class="app-header-side" />
  </header>
  <main class="app-main">
    <RouterView />
  </main>
  <DarkModeToggle />
</template>

<style scoped>
  .app-header {
    display: grid;
    grid-template-columns: 1fr minmax(0, 560px) 1fr;
    align-items: center;
    padding: 0.75rem 1.5rem;
    flex-shrink: 0;
  }

  .app-header-side {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .app-header-side:last-child {
    justify-content: flex-end;
  }

</style>
