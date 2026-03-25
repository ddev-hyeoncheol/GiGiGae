<script setup lang="ts">
  import { ref } from 'vue'
  import type { ChecklistItem } from '@/composables/useTrademarkChecklist'

  defineProps<{
    items: ChecklistItem[]
    totalChecked: number
  }>()

  const showCriteria = ref(false)

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

  const criteriaDetails = [
    {
      label: '동일 상표 여부',
      description: '입력한 브랜드명과 완전히 동일하거나 거의 같은 상표가 이미 등록 또는 출원되어 있는지 확인해요.',
      conditions: [
        { status: '안심', rule: '유사도 70% 미만의 동일 상표가 없는 경우' },
        { status: '주의', rule: '유사도 70% 이상 90% 미만의 상표가 확인된 경우' },
        { status: '위험', rule: '유사도 90% 이상의 동일 상표가 존재하는 경우' },
      ],
    },
    {
      label: '유사 상표 여부',
      description: '발음, 철자, 의미에서 혼동 가능성이 있는 유사 상표가 있는지 검색해요.',
      conditions: [
        { status: '안심', rule: '유사도 40~90% 범위의 상표가 없는 경우' },
        { status: '주의', rule: '유사 상표가 1~2건 확인된 경우' },
        { status: '위험', rule: '유사 상표가 3건 이상 확인된 경우' },
      ],
    },
    {
      label: '업종 / 분류 충돌',
      description: '선택한 카테고리의 니스 분류와 유사 상표의 분류가 겹치는지 확인해요.',
      conditions: [
        { status: '안심', rule: '동일 분류에서 충돌하는 상표가 없는 경우' },
        { status: '주의', rule: '동일 또는 인접 분류에서 1~2건 겹치는 경우' },
        { status: '위험', rule: '동일 분류에서 3건 이상 충돌하는 경우' },
      ],
    },
    {
      label: '식별력',
      description: '브랜드명이 독창적인 조어인지, 일반적인 설명형 표현인지 평가해요.',
      conditions: [
        { status: '안심', rule: '전체 충돌 위험도가 낮아 독창성이 인정되는 경우' },
        { status: '주의', rule: '일부 유사 상표와 혼동 가능성이 있는 경우' },
        { status: '위험', rule: '전체 충돌 위험도가 높아 식별력이 약한 경우' },
      ],
    },
    {
      label: '보통명칭화 위험',
      description: '브랜드명이 업계에서 통용되는 표현이거나 상품명처럼 인식될 가능성을 확인해요.',
      conditions: [
        { status: '안심', rule: '전체 충돌 위험도가 낮은 경우' },
        { status: '주의', rule: '유사 상표가 다수 존재해 보통명칭 요소가 의심되는 경우' },
      ],
    },
    {
      label: '로고 결합 시 충돌',
      description: '업로드한 로고 이미지와 시각적으로 유사한 등록 상표가 있는지 CLIP 모델로 분석해요.',
      conditions: [
        { status: '안심', rule: '시각적으로 유사한 상표가 없는 경우' },
        { status: '주의', rule: '일부 시각적으로 유사한 로고가 확인된 경우' },
        { status: '위험', rule: '유사도 50% 이상의 로고가 확인된 경우' },
      ],
    },
  ]
</script>

<template>
  <section class="checklist-section surface">
    <div class="checklist-header">
      <div>
        <h3 class="checklist-title">어떤 기준으로 살펴봤나요</h3>
        <p class="checklist-subtitle text-muted">NameCraft가 {{ totalChecked }}개 항목을 종합해서 등록 가능성을 판단했어요</p>
      </div>
      <button class="checklist-criteria-btn" @click="showCriteria = true">항목별 상세 기준</button>
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

    <!-- 판정 기준 오버레이 -->
    <Transition name="overlay-fade">
      <div v-if="showCriteria" class="criteria-overlay" @click.self="showCriteria = false">
        <div class="criteria-modal">
          <div class="criteria-header">
            <h2 class="criteria-modal-title">항목별 상세 기준</h2>
            <button class="criteria-close" @click="showCriteria = false">&times;</button>
          </div>
          <p class="criteria-subtitle text-muted">각 항목의 안심/주의/위험 판정 기준이에요.</p>
          <div class="criteria-list">
            <div v-for="(c, i) in criteriaDetails" :key="i" class="criteria-card">
              <h4 class="criteria-card-title">{{ c.label }}</h4>
              <p class="criteria-card-desc text-muted">{{ c.description }}</p>
              <div class="criteria-conditions">
                <div v-for="(cond, j) in c.conditions" :key="j" class="criteria-cond">
                  <span class="criteria-cond-status" :class="{
                    'cond-safe': cond.status === '안심',
                    'cond-caution': cond.status === '주의',
                    'cond-warning': cond.status === '위험',
                  }">{{ cond.status }}</span>
                  <span class="criteria-cond-rule">{{ cond.rule }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
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

  .checklist-criteria-btn {
    font-size: 0.85rem;
    font-weight: 600;
    padding: 0.5rem 1rem;
    border-radius: var(--radius);
    background: var(--color-bg);
    border: 1px solid var(--color-border);
    color: var(--color-text-muted);
    white-space: nowrap;
    flex-shrink: 0;
    cursor: pointer;
    transition: all 0.2s;
  }

  .checklist-criteria-btn:hover {
    border-color: var(--color-primary);
    color: var(--color-primary);
    background: color-mix(in srgb, var(--color-primary) 5%, var(--color-bg));
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

  .card-top { display: flex; align-items: center; gap: 0.4rem; }
  .card-icon { flex-shrink: 0; display: flex; align-items: center; }
  .icon-warning { color: var(--color-danger); }
  .icon-caution { color: var(--color-accent); }
  .icon-safe { color: var(--color-success); }
  .icon-disabled { color: var(--color-border); }

  .card-label { font-size: 0.9rem; font-weight: 700; flex: 1; }

  .card-badge {
    font-size: 0.7rem; font-weight: 600; padding: 0.2rem 0.5rem;
    border-radius: 999px; white-space: nowrap; flex-shrink: 0;
  }

  .badge-warning { background: color-mix(in srgb, var(--color-danger) 12%, transparent); color: var(--color-danger); border: 1px solid color-mix(in srgb, var(--color-danger) 30%, transparent); }
  .badge-caution { background: color-mix(in srgb, var(--color-accent) 12%, transparent); color: var(--color-accent); border: 1px solid color-mix(in srgb, var(--color-accent) 30%, transparent); }
  .badge-safe { background: color-mix(in srgb, var(--color-success) 12%, transparent); color: var(--color-success); border: 1px solid color-mix(in srgb, var(--color-success) 30%, transparent); }
  .badge-disabled { background: var(--color-bg); color: var(--color-text-muted); border: 1px solid var(--color-border); }

  .checklist-disabled { opacity: 0.45; }

  .card-desc {
    font-size: 0.8rem; color: var(--color-text-muted); margin: 0; line-height: 1.5;
    min-height: 2.4em; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  }

  /* 오버레이 */
  .criteria-overlay { position: fixed; inset: 0; z-index: 1000; background: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; padding: 1rem; }
  .criteria-modal { width: 100%; max-width: 600px; max-height: 80vh; overflow-y: auto; background: var(--color-surface); border-radius: var(--radius); padding: 1.5rem; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2); }
  .criteria-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem; }
  .criteria-modal-title { font-size: 1.15rem; font-weight: 700; margin: 0; }
  .criteria-close { border: none; background: none; font-size: 1.5rem; color: var(--color-text-muted); cursor: pointer; line-height: 1; padding: 0.25rem; }
  .criteria-close:hover { color: var(--color-text); }
  .criteria-subtitle { font-size: 0.85rem; margin: 0 0 1rem; }
  .criteria-list { display: flex; flex-direction: column; gap: 0.75rem; }

  .criteria-card { padding: 1rem; border: 1px solid var(--color-border); border-radius: var(--radius); }
  .criteria-card-title { font-size: 0.95rem; font-weight: 700; margin: 0 0 0.25rem; }
  .criteria-card-desc { font-size: 0.8rem; margin: 0 0 0.6rem; line-height: 1.5; }
  .criteria-conditions { display: flex; flex-direction: column; gap: 0.35rem; }
  .criteria-cond { display: flex; align-items: baseline; gap: 0.5rem; font-size: 0.8rem; }
  .criteria-cond-status { font-size: 0.7rem; font-weight: 700; padding: 0.1rem 0.4rem; border-radius: 4px; flex-shrink: 0; }
  .cond-safe { background: color-mix(in srgb, var(--color-success) 12%, transparent); color: var(--color-success); }
  .cond-caution { background: color-mix(in srgb, var(--color-accent) 12%, transparent); color: var(--color-accent); }
  .cond-warning { background: color-mix(in srgb, var(--color-danger) 12%, transparent); color: var(--color-danger); }
  .criteria-cond-rule { color: var(--color-text-muted); line-height: 1.4; }

  .overlay-fade-enter-active, .overlay-fade-leave-active { transition: opacity 0.25s ease; }
  .overlay-fade-enter-active .criteria-modal, .overlay-fade-leave-active .criteria-modal { transition: transform 0.25s ease; }
  .overlay-fade-enter-from, .overlay-fade-leave-to { opacity: 0; }
  .overlay-fade-enter-from .criteria-modal, .overlay-fade-leave-to .criteria-modal { transform: translateY(20px); }

  @media (max-width: 520px) {
    .checklist-grid { grid-template-columns: 1fr; }
  }
</style>
