<script setup lang="ts">
  import { RouterView } from 'vue-router'
  import DarkModeToggle from '@/components/DarkModeToggle.vue'
  import StepIndicator from '@/components/StepIndicator.vue'
</script>

<template>
  <StepIndicator />
  <RouterView />
  <DarkModeToggle />
</template>
