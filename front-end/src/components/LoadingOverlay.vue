<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'

const props = withDefaults(defineProps<{
  visible: boolean
  messages?: string[]
  interval?: number
}>(), {
  messages: () => [],
  interval: 2000,
})

const currentIndex = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

function startCycle() {
  currentIndex.value = 0
  timer = setInterval(() => {
    if (currentIndex.value < props.messages.length - 1) {
      currentIndex.value++
    }
  }, props.interval)
}

function stopCycle() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

watch(() => props.visible, (val) => {
  if (val) {
    startCycle()
  } else {
    stopCycle()
  }
})

onUnmounted(stopCycle)
</script>

<template>
  <Transition name="fade">
    <div v-if="visible" class="overlay">
      <div class="overlay-content">
        <div class="dots">
          <span class="dot" />
          <span class="dot" />
          <span class="dot" />
        </div>
        <Transition name="msg" mode="out-in">
          <p v-if="messages.length" :key="currentIndex" class="overlay-msg">
            {{ messages[currentIndex] }}
          </p>
        </Transition>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.overlay {
  position: absolute;
  inset: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--color-bg) 85%, transparent);
  backdrop-filter: blur(4px);
  border-radius: var(--radius);
}

.overlay-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.dots {
  display: flex;
  gap: 12px;
}

.dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--color-primary);
  opacity: 0.25;
  animation: blink 1.2s ease-in-out infinite;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes blink {
  0%, 80%, 100% { opacity: 0.25; }
  40% { opacity: 1; }
}

.overlay-msg {
  color: var(--color-text);
  font-size: 1.2rem;
  font-weight: 500;
  text-align: center;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.msg-enter-active,
.msg-leave-active {
  transition: all 0.3s ease;
}

.msg-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.msg-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
