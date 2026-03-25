<script setup lang="ts">
  import { useWizardStore } from '@/stores/wizard'
  import { useRouter } from 'vue-router'
  import PageHeader from '@/components/PageHeader.vue'
  import NavButtons from '@/components/NavButtons.vue'

  const wizard = useWizardStore()
  const router = useRouter()

  if (!wizard.trademarkResult && !wizard.selectedBrand) {
    router.replace('/')
  }

  const result = wizard.trademarkResult ?? wizard.selectedBrand?.trademark

  /* 니스 분류 → 7개 카테고리 매핑 */
  const niceCategoryMap: Record<string, string> = {
    '35': '이커머스 · 온라인스토어',
    '42': '이커머스 · 온라인스토어',
    '29': 'F&B · 카페 · 숙박',
    '30': 'F&B · 카페 · 숙박',
    '32': 'F&B · 카페 · 숙박',
    '43': 'F&B · 카페 · 숙박',
    '9': 'IT · SaaS · 테크',
    '18': '패션 · 의류 브랜드',
    '25': '패션 · 의류 브랜드',
    '26': '패션 · 의류 브랜드',
    '3': '뷰티 · 코스메틱',
    '44': '뷰티 · 코스메틱',
    '11': '디지털 · 전자제품',
    '28': '디지털 · 전자제품',
    '31': '카페 · 베이커리 · 식품',
  }

  const categoryEmoji: Record<string, string> = {
    '이커머스 · 온라인스토어': '🛒',
    'F&B · 카페 · 숙박': '🍽️',
    'IT · SaaS · 테크': '💻',
    '패션 · 의류 브랜드': '👕',
    '뷰티 · 코스메틱': '💄',
    '디지털 · 전자제품': '📱',
    '카페 · 베이커리 · 식품': '🧁',
    '기타': '📦',
  }

  function resolveCategories(niceClass: string | null | undefined): { emoji: string; label: string }[] {
    if (!niceClass) return [{ emoji: '📦', label: '기타' }]
    const classes = niceClass.split('|').map(c => c.trim())
    const seen = new Set<string>()
    const result: { emoji: string; label: string }[] = []
    for (const cls of classes) {
      const cat = niceCategoryMap[cls]
      if (cat && !seen.has(cat)) {
        seen.add(cat)
        result.push({ emoji: categoryEmoji[cat], label: cat })
      }
    }
    if (result.length === 0) result.push({ emoji: '📦', label: '기타' })
    return result
  }

  function riskClass(risk: string) {
    switch (risk) {
      case 'Low': return 'risk-low'
      case 'Middle': return 'risk-middle'
      case 'High': return 'risk-high'
      default: return 'risk-unchecked'
    }
  }

  function riskDescription(risk: string) {
    switch (risk) {
      case 'Low': return '유사한 등록 상표가 거의 없습니다. 출원에 유리합니다.'
      case 'Middle': return '일부 유사 상표가 있습니다. 검토가 필요합니다.'
      case 'High': return '유사한 등록 상표가 많습니다. 출원 시 주의가 필요합니다.'
      default: return '상표 검색 결과를 확인할 수 없습니다.'
    }
  }

  function similarityPercent(score: number) {
    return Math.round(score * 100)
  }

  function handleNext() {
    wizard.goToStep(4)
    router.push('/brand-domain')
  }

  function handleBack() {
    if (wizard.inputMode === 'brand') {
      wizard.goToStep(1)
      router.push('/')
    } else {
      wizard.goToStep(2)
      router.push('/brand-name')
    }
  }
</script>

<template>
  <div class="page">
    <main class="content">
      <PageHeader title="상표권 확인">
        <strong>{{ wizard.selectedBrand?.brand_name }}</strong> 에 대한 상표 검색 결과입니다.
      </PageHeader>

      <div class="content-body">
        <div v-if="result" class="trademark-section">
          <div class="risk-card surface" :class="riskClass(result.risk)">
            <div class="risk-header">
              <span class="risk-label">충돌 위험도</span>
              <span class="risk-badge" :class="riskClass(result.risk)">{{ result.risk }}</span>
            </div>
            <p class="risk-desc text-muted">{{ riskDescription(result.risk) }}</p>
          </div>

          <div v-if="result.matches.length > 0" class="matches-section surface">
            <h3 class="matches-title">유사 상표 목록 <span class="text-muted">({{ result.matches.length }}건)</span></h3>
            <div class="matches-list">
              <div v-for="match in result.matches" :key="match.application_no" class="match-item">
                <div class="match-main">
                  <span class="match-name">{{ match.name }}</span>
                  <span class="match-similarity">{{ similarityPercent(match.similarity) }}%</span>
                </div>
                <div class="match-categories">
                  <span
                    v-for="cat in resolveCategories(match.nice_class)"
                    :key="cat.label"
                    class="category-tag"
                  >{{ cat.label }}</span>
                </div>
                <div class="match-meta text-muted">
                  <span v-if="match.legal_status">{{ match.legal_status }}</span>
                  <span>{{ match.application_no }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="no-matches surface">
            <p class="text-muted">유사한 등록 상표가 발견되지 않았습니다.</p>
          </div>
        </div>

        <NavButtons
          back-label="이전으로"
          next-label="도메인 조회하기"
          :next-disabled="false"
          @next="handleNext"
          @back="handleBack"
        />
      </div>
    </main>
  </div>
</template>

<style scoped>
  .page {
    display: flex;
    flex-direction: column;
  }

  .content {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 1rem 1rem 2rem;
    gap: 1.5rem;
  }

  .content-body {
    width: 100%;
    max-width: 560px;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .trademark-section {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .risk-card {
    padding: 1.25rem;
  }

  .risk-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .risk-label {
    font-weight: 600;
    font-size: 1rem;
  }

  .risk-badge {
    font-size: 0.8rem;
    font-weight: 700;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
  }

  .risk-badge.risk-low {
    background: var(--color-success, #22c55e);
    color: #fff;
  }

  .risk-badge.risk-middle {
    background: #f59e0b;
    color: #fff;
  }

  .risk-badge.risk-high {
    background: var(--color-danger, #e74c3c);
    color: #fff;
  }

  .risk-badge.risk-unchecked {
    background: var(--color-border);
    color: var(--color-text);
  }

  .risk-desc {
    font-size: 0.9rem;
    margin: 0;
    line-height: 1.5;
  }

  .matches-section {
    padding: 1.25rem;
  }

  .matches-title {
    font-size: 0.95rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--color-border);
  }

  .match-categories {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem;
  }

  .category-tag {
    font-size: 0.7rem;
    padding: 0.1rem 0.45rem;
    border-radius: 999px;
    background-color: var(--color-surface-alt, var(--color-border));
    color: var(--color-text-muted);
    white-space: nowrap;
  }

  .matches-list {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
  }

  .match-item {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--color-border);
  }

  .match-item:last-child {
    border-bottom: none;
  }

  .match-main {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .match-name {
    font-weight: 600;
    font-size: 0.95rem;
  }

  .match-similarity {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--color-primary);
  }

  .match-meta {
    display: flex;
    gap: 0.75rem;
    font-size: 0.8rem;
  }

  .no-matches {
    padding: 2rem;
    text-align: center;
  }
</style>
