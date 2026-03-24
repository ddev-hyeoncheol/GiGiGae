<script setup lang="ts">
withDefaults(defineProps<{
  nextLabel?: string
  backLabel?: string
  nextDisabled?: boolean
  showBack?: boolean
}>(), {
  nextLabel: '다음',
  backLabel: '이전',
  nextDisabled: false,
  showBack: true,
})

const emit = defineEmits<{
  next: []
  back: []
}>()
</script>

<template>
  <div class="nav-buttons">
    <button v-if="showBack" class="btn-secondary" @click="emit('back')">{{ backLabel }}</button>
    <button class="btn-primary" :disabled="nextDisabled" @click="emit('next')">
      <slot>{{ nextLabel }}</slot>
    </button>
  </div>
</template>

<style scoped>
.nav-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
