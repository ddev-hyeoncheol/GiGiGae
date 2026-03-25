<script setup lang="ts">
  import type { ChecklistItem } from '@/composables/useTrademarkChecklist'

  defineProps<{
    items: ChecklistItem[]
    totalChecked: number
  }>()

  function badgeClass(status: string) {
    switch (status) {
      case 'warning': return 'badge-warning'
      case 'caution': return 'badge-caution'
      default: return 'badge-safe'
    }
  }

  function iconClass(status: string) {
    switch (status) {
      case 'warning': return 'icon-warning'
      case 'caution': return 'icon-caution'
      default: return 'icon-safe'
    }
  }
</script>

<template>
  <section class="checklist-section surface">
    <div class="checklist-header">
      <div>
        <h3 class="checklist-title">어떤 기준으로 살펴봤나요</h3>
        <p class="checklist-subtitle text-muted">NameCraft가 {{ totalChecked }}개 항목을 종합해서 등록 가능성을 판단했어요</p>
      </div>
      <span class="checklist-count">{{ totalChecked }}개 기준</span>
    </div>

    <div class="checklist-grid">
      <div v-for="item in items" :key="item.id" class="checklist-card" :class="{ 'checklist-disabled': item.disabled }">
        <div class="card-top">
          <span class="card-icon" :class="item.disabled ? 'icon-disabled' : iconClass(item.status)">
            <svg v-if="item.disabled" width="18" height="18" viewBox="0 0 20 20" fill="none">
              <circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="2"/>
              <path d="M6 10h8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <svg v-else-if="item.status === 'warning'" width="18" height="18" viewBox="0 0 20 20" fill="none">
              <circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="2"/>
              <path d="M7 7l6 6M13 7l-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <svg v-else-if="item.status === 'caution'" width="18" height="18" viewBox="0 0 20 20" fill="none">
              <circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="2"/>
              <path d="M6 10h8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <svg v-else width="18" height="18" viewBox="0 0 20 20" fill="none">
              <circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="2"/>
              <path d="M6 10l3 3 5-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
          <span class="card-label">{{ item.label }}</span>
          <span class="card-badge" :class="item.disabled ? 'badge-disabled' : badgeClass(item.status)">{{ item.statusLabel }}</span>
        </div>
        <p class="card-desc">{{ item.description }}</p>
      </div>
    </div>
  </section>
</template>

<style scoped>
  .checklist-section {
    padding: 1.5rem;
    border-radius: var(--radius);
  }

  .checklist-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1.25rem;
  }

  .checklist-title {
    font-size: 1.05rem;
    font-weight: 700;
    margin: 0 0 0.25rem;
  }

  .checklist-subtitle {
    font-size: 0.8rem;
    margin: 0;
  }

  .checklist-count {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.25rem 0.6rem;
    border-radius: 999px;
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    color: var(--color-text-muted);
    white-space: nowrap;
    flex-shrink: 0;
  }

  .checklist-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
  }

  .checklist-card {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid var(--color-border);
    background: var(--color-bg);
  }

  .checklist-card:not(.checklist-disabled):has(.icon-safe) {
    background: color-mix(in srgb, var(--color-success) 4%, var(--color-bg));
    border-color: color-mix(in srgb, var(--color-success) 20%, var(--color-border));
  }

  .checklist-card:not(.checklist-disabled):has(.icon-caution) {
    background: color-mix(in srgb, var(--color-accent) 4%, var(--color-bg));
    border-color: color-mix(in srgb, var(--color-accent) 20%, var(--color-border));
  }

  .checklist-card:not(.checklist-disabled):has(.icon-warning) {
    background: color-mix(in srgb, var(--color-danger) 4%, var(--color-bg));
    border-color: color-mix(in srgb, var(--color-danger) 20%, var(--color-border));
  }

  .card-top {
    display: flex;
    align-items: center;
    gap: 0.4rem;
  }

  .card-icon {
    flex-shrink: 0;
    display: flex;
    align-items: center;
  }

  .icon-warning { color: var(--color-danger); }
  .icon-caution { color: var(--color-accent); }
  .icon-safe { color: var(--color-success); }
  .icon-disabled { color: var(--color-border); }

  .card-label {
    font-size: 0.9rem;
    font-weight: 700;
    flex: 1;
  }

  .card-badge {
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.2rem 0.5rem;
    border-radius: 999px;
    white-space: nowrap;
    flex-shrink: 0;
  }

  .badge-warning {
    background: color-mix(in srgb, var(--color-danger) 12%, transparent);
    color: var(--color-danger);
    border: 1px solid color-mix(in srgb, var(--color-danger) 30%, transparent);
  }

  .badge-caution {
    background: color-mix(in srgb, var(--color-accent) 12%, transparent);
    color: var(--color-accent);
    border: 1px solid color-mix(in srgb, var(--color-accent) 30%, transparent);
  }

  .badge-safe {
    background: color-mix(in srgb, var(--color-success) 12%, transparent);
    color: var(--color-success);
    border: 1px solid color-mix(in srgb, var(--color-success) 30%, transparent);
  }

  .badge-disabled {
    background: var(--color-bg);
    color: var(--color-text-muted);
    border: 1px solid var(--color-border);
  }

  .checklist-disabled {
    opacity: 0.45;
  }

  .card-desc {
    font-size: 0.8rem;
    color: var(--color-text-muted);
    margin: 0;
    line-height: 1.5;
    min-height: 2.4em;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  @media (max-width: 520px) {
    .checklist-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
