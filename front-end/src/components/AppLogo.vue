<template>
  <button class="app-logo-btn" @click="goHome">
    <img src="/favicon.svg" :width="size" :height="size" alt="NameCraft" />
    <span class="app-logo-title">
      <span class="title-name">Name</span><span class="title-craft">CRAFT</span>
    </span>
  </button>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

withDefaults(defineProps<{ size?: number }>(), { size: 28 })

const router = useRouter()
const goHome = () => router.push('/')
</script>

<style scoped>
  .app-logo-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: none;
    border: none;
    padding: 0;
    cursor: pointer;
  }

  .app-logo-title {
    font-size: 1.35rem;
    letter-spacing: -0.03em;
    line-height: 1;
  }

  .title-name {
    font-weight: 300;
    color: var(--color-text);
    letter-spacing: 0.04em;
    font-size: 0.85em;
    margin-right: 1px;
  }

  .title-craft {
    font-weight: 800;
    background: linear-gradient(135deg, var(--color-primary), var(--color-accent, #f59e0b));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
  }

  @media (max-width: 640px) {
    .app-logo-title {
      display: none;
    }
  }
</style>
