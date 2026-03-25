<script setup lang="ts">
  import type { TrademarkMatch } from '@/api/types'
  import { resolveCategories } from '@/utils/niceClassMapping'

  withDefaults(defineProps<{
    matches: TrademarkMatch[]
    title?: string
  }>(), {
    title: '브랜드명 기반 유사 상표',
  })

  function statusClass(status: string | null) {
    switch (status) {
      case '등록': return 'status-active'
      case '소멸': return 'status-expired'
      case '포기': return 'status-abandoned'
      case '무효': return 'status-invalid'
      default: return ''
    }
  }
</script>

<template>
  <section class="match-section surface">
    <h3 class="match-title">{{ title }} <span class="text-muted">({{ matches.length }}건)</span></h3>
    <p class="match-sub text-muted">특허청 출원·등록 데이터를 기반으로 참고한 항목이에요.</p>

    <div class="match-list">
      <div v-for="m in matches" :key="m.application_no" class="match-item">
        <div class="match-row">
          <img
            v-if="m.image_path"
            :src="`/image/${m.image_path.split('/').pop()}`"
            :alt="m.name"
            class="match-thumb"
            @error="($event.target as HTMLImageElement).style.display = 'none'"
          />
          <div class="match-info">
            <div class="match-main">
              <div class="match-name-group">
                <span v-if="m.legal_status" class="status-tag" :class="statusClass(m.legal_status)">{{ m.legal_status }}</span>
                <span class="match-name">{{ m.name }}</span>
              </div>
              <span class="match-sim">{{ Math.round(m.similarity * 100) }}%</span>
            </div>
            <div class="match-meta">
              <span class="meta-label">출원번호</span>
              <span class="meta-value text-muted">{{ m.application_no }}</span>
            </div>
            <div class="match-meta">
              <span class="meta-label">카테고리</span>
              <span class="meta-value text-muted">
                {{ resolveCategories(m.nice_class)[0] }}
                <span v-if="resolveCategories(m.nice_class).length > 1"> 외 {{ resolveCategories(m.nice_class).length - 1 }}개</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

  </section>
</template>

<style scoped>
  .match-section { padding: 1.25rem; border-radius: var(--radius); }

  .match-title { font-size: 1rem; font-weight: 700; margin: 0; }
  .match-sub { font-size: 0.8rem; margin: 0.4rem 0 0.75rem; }

  .match-list { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; }

  .match-item { padding: 0.75rem; border: 1px solid var(--color-border); border-radius: 8px; background: var(--color-bg); }

  @media (max-width: 520px) {
    .match-list { grid-template-columns: 1fr; }
  }

  .match-row { display: flex; gap: 0.75rem; align-items: center; }

  .match-thumb {
    width: 64px; height: 64px; object-fit: contain; border-radius: 6px;
    border: 1px solid var(--color-border); background: #fff; flex-shrink: 0;
    cursor: pointer; transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  .match-thumb:hover { transform: scale(3); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15); z-index: 10; position: relative; }

  .match-info { flex: 1; display: flex; flex-direction: column; gap: 0.3rem; }

  .match-main { display: flex; justify-content: space-between; align-items: center; }
  .match-name-group { display: flex; align-items: center; gap: 0.4rem; }
  .match-name { font-weight: 600; font-size: 0.95rem; }
  .match-sim { font-size: 0.85rem; font-weight: 600; color: var(--color-primary); }

  .match-meta { display: flex; gap: 0.4rem; font-size: 0.8rem; align-items: baseline; }
  .meta-label { font-weight: 600; color: var(--color-text-muted); flex-shrink: 0; font-size: 0.75rem; }
  .meta-label::after { content: ':'; }
  .meta-value { font-size: 0.75rem; }

  .status-tag { font-size: 0.75rem; font-weight: 600; padding: 0.2rem 0.5rem; border-radius: 4px; white-space: nowrap; flex-shrink: 0; }
  .status-active { background: color-mix(in srgb, var(--color-success) 12%, transparent); color: var(--color-success); }
  .status-expired { background: color-mix(in srgb, var(--color-danger) 12%, transparent); color: var(--color-danger); }
  .status-abandoned { background: color-mix(in srgb, var(--color-accent) 12%, transparent); color: var(--color-accent); }
  .status-invalid { background: color-mix(in srgb, var(--color-text-muted) 12%, transparent); color: var(--color-text-muted); }

</style>
