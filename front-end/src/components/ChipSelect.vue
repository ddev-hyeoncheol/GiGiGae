<script setup lang="ts">
export interface ChipOption {
  label: string
  emoji?: string
}

const props = withDefaults(defineProps<{
  options: ChipOption[]
  modelValue: string[]
  max?: number
  disabled?: boolean
}>(), {
  max: 0,
  disabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

function isSelected(label: string) {
  return props.modelValue.includes(label)
}

function isLocked(label: string) {
  return props.max > 0 && props.modelValue.length >= props.max && !isSelected(label)
}

function toggle(label: string) {
  if (props.disabled || isLocked(label)) return
  const idx = props.modelValue.indexOf(label)
  const next = [...props.modelValue]
  if (idx >= 0) {
    next.splice(idx, 1)
  } else {
    next.push(label)
  }
  emit('update:modelValue', next)
}
</script>

<template>
  <div class="chip-grid">
    <button
      v-for="opt in options"
      :key="opt.label"
      class="chip"
      :class="{ selected: isSelected(opt.label), locked: isLocked(opt.label) }"
      :disabled="disabled || isLocked(opt.label)"
      @click="toggle(opt.label)"
    >
      <span v-if="opt.emoji" class="chip-emoji">{{ opt.emoji }}</span>
      <span>{{ opt.label }}</span>
    </button>
    <slot />
  </div>
</template>

<style scoped>
.chip-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.chip {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.35rem 0.65rem;
  border: 1px solid var(--color-border);
  border-radius: 100px;
  background: var(--color-bg);
  color: var(--color-text);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.chip:hover:not(.locked) {
  border-color: var(--color-primary);
}

.chip.selected {
  border-color: var(--color-primary);
  background: var(--color-primary);
  color: #fff;
}

.chip.locked {
  opacity: 0.4;
  cursor: not-allowed;
}

.chip-emoji {
  font-size: 0.85rem;
}
</style>
