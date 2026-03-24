<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<template>
  <div class="page-header">
    <h2>{{ title }}</h2>
    <p v-if="description" class="text-muted">{{ description }}</p>
    <p v-if="$slots.default" class="text-muted"><slot /></p>
  </div>
</template>

<style scoped>
.page-header {
  text-align: center;
}

.page-header h2 {
  font-size: 1.8rem;
  font-weight: 700;
}

.page-header p {
  margin-top: 0.4rem;
  font-size: 0.95rem;
  max-width: 480px;
}
</style>
