<script setup lang="ts">
  import { ref } from 'vue'
  import { useWizardStore } from '@/stores/wizard'
  import { useRouter } from 'vue-router'
  import PageHeader from '@/components/PageHeader.vue'
  import NavButtons from '@/components/NavButtons.vue'

  const wizard = useWizardStore()
  const router = useRouter()

  const showDisputes = ref(false)

  interface DisputeCase {
    category: string
    title: string
    parties: string
    year: string
    issue: string
    result: string
    lesson: string
  }

  const disputeCases: DisputeCase[] = [
    {
      category: '보통명칭화',
      title: '초코파이 분쟁',
      parties: '오리온 vs 롯데 등',
      year: '1997',
      issue: '오리온이 최초 사용했으나 경쟁사 무대응으로 보통명칭화',
      result: '오리온 패소, 초코파이는 보통명칭 인정',
      lesson: '등록 후에도 적극적인 상표 관리가 필수입니다. 방치하면 상표권을 잃을 수 있습니다.',
    },
    {
      category: '보통명칭화',
      title: '그립톡 분쟁',
      parties: '아이버스터 vs 60여 업체',
      year: '2023',
      issue: '스마트폰 거치대를 칭하는 보통명칭이 됨',
      result: '일부 지정상품 무효 심결',
      lesson: '브랜드명이 상품 자체를 지칭하게 되면 상표 등록이 무효화될 수 있습니다.',
    },
    {
      category: '유사 상표',
      title: '스타벅스 vs 스타프릭스',
      parties: '스타벅스 vs 스타프릭스',
      year: '2019',
      issue: '발음 및 외관의 유사성으로 혼동 가능성 제기',
      result: '스타벅스 승소, 유사 상표 등록 무효',
      lesson: '유명 브랜드와 발음이나 외관이 유사하면 류가 달라도 분쟁 대상이 됩니다.',
    },
    {
      category: '유사 상표',
      title: '카카오 vs 카카오뱅크 계열',
      parties: '카카오 vs 유사 명칭 사업자',
      year: '2020',
      issue: '카카오 브랜드의 광범위한 식별력 인정 범위',
      result: '카카오 측 승소, 유사 상표 사용 금지',
      lesson: '저명 상표와 유사한 이름은 업종이 달라도 분쟁 위험이 높습니다.',
    },
    {
      category: '해외 선점',
      title: 'K패션 해외 상표 선점',
      parties: '한국 의류 브랜드 vs 해외 무단 등록자',
      year: '2023',
      issue: '한국 의류 브랜드명이 해외에서 무단 등록',
      result: '피해 5,751건 (2023년 기준)',
      lesson: '글로벌 진출 시 주요 시장에 상표를 먼저 등록해야 합니다.',
    },
    {
      category: '디자인/로고',
      title: '로고 유사성 분쟁',
      parties: '다수 기업 간 로고 분쟁',
      year: '2021',
      issue: '도형 상표의 외관 유사성으로 인한 혼동 가능성',
      result: '유사 판정 시 후출원 무효',
      lesson: '로고 디자인도 기존 등록 상표와 시각적 유사도를 반드시 확인해야 합니다.',
    },
    {
      category: '업종간 충돌',
      title: '동일 명칭 타업종 충돌',
      parties: '동명 브랜드 타업종 사업자',
      year: '2020',
      issue: '동일 브랜드명이 다른 업종에서 등록되어 혼동 발생',
      result: '저명 상표 우선 인정',
      lesson: '니스 분류가 다르더라도 저명 상표와의 충돌은 피해야 합니다.',
    },
    {
      category: '대기업 vs 중소',
      title: '상표 브로커 분쟁',
      parties: '중소 사업자 vs 상표 브로커',
      year: '상시',
      issue: '사용 의사 없이 상표 대량 등록 후 합의금 요구',
      result: '불사용취소심판으로 대응 가능',
      lesson: '브랜드명 확정 후 빠르게 출원해야 선점 피해를 방지할 수 있습니다.',
    },
  ]

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
      <PageHeader title="상표권 분석">
        <strong>{{ wizard.selectedBrand?.brand_name }}</strong> 에 대한 상표 검색 결과입니다.
      </PageHeader>

      <button class="btn-disputes" @click="showDisputes = true">
        <span class="btn-disputes-icon">!</span>
        왜 상표권 등록이 중요한가요?
      </button>

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

          <!-- 이미지 기반 유사 상표 -->
          <div v-if="wizard.imageSearchResult?.matches?.length" class="matches-section surface">
            <h3 class="matches-title">시각적 유사 상표 <span class="text-muted">({{ wizard.imageSearchResult.matches.length }}건)</span></h3>
            <p class="image-search-desc text-muted">업로드한 로고와 시각적으로 유사한 등록 상표입니다.</p>
            <div class="image-matches-grid">
              <div
                v-for="match in wizard.imageSearchResult.matches"
                :key="match.application_no"
                class="image-match-card"
              >
                <div class="image-match-thumb">
                  <img
                    v-if="match.image_path"
                    :src="match.image_path"
                    :alt="match.name"
                  />
                  <div v-else class="image-match-placeholder">No Image</div>
                </div>
                <div class="image-match-info">
                  <span class="image-match-name">{{ match.name }}</span>
                  <span class="image-match-similarity">{{ similarityPercent(match.similarity) }}%</span>
                </div>
                <div class="match-categories">
                  <span
                    v-for="cat in resolveCategories(match.nice_class)"
                    :key="cat.label"
                    class="category-tag"
                  >{{ cat.label }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <NavButtons
          back-label="이전으로"
          next-label="도메인 조회하기"
          :next-disabled="false"
          @next="handleNext"
          @back="handleBack"
        />

        <!-- 분쟁 사례 오버레이 -->
        <Transition name="overlay-fade">
          <div v-if="showDisputes" class="disputes-overlay" @click.self="showDisputes = false">
            <div class="disputes-modal">
              <div class="disputes-header">
                <h2 class="disputes-title">왜 상표권 등록이 중요한가요?</h2>
                <button class="disputes-close" @click="showDisputes = false">&times;</button>
              </div>
              <p class="disputes-subtitle text-muted">
                실제 분쟁 사례를 통해 상표권 등록의 중요성을 확인하세요.
              </p>
              <div class="disputes-list">
                <div v-for="(d, i) in disputeCases" :key="i" class="dispute-card">
                  <div class="dispute-card-header">
                    <span class="dispute-category">{{ d.category }}</span>
                    <span class="dispute-year text-muted">{{ d.year }}</span>
                  </div>
                  <h4 class="dispute-title">{{ d.title }}</h4>
                  <p class="dispute-parties text-muted">{{ d.parties }}</p>
                  <div class="dispute-detail">
                    <div class="dispute-row">
                      <span class="dispute-label">쟁점</span>
                      <span>{{ d.issue }}</span>
                    </div>
                    <div class="dispute-row">
                      <span class="dispute-label">결과</span>
                      <span>{{ d.result }}</span>
                    </div>
                  </div>
                  <div class="dispute-lesson">
                    <span>{{ d.lesson }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Transition>
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

  .image-search-desc {
    font-size: 0.85rem;
    margin: -0.25rem 0 0.5rem;
  }

  .image-matches-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 0.75rem;
  }

  .image-match-card {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    padding: 0.6rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    background: var(--color-bg);
    transition: border-color 0.2s ease;
  }

  .image-match-card:hover {
    border-color: var(--color-primary);
  }

  .image-match-thumb {
    width: 100%;
    aspect-ratio: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    border-radius: calc(var(--radius) - 2px);
    background: #f9f9f9;
  }

  .image-match-thumb img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
  }

  .image-match-placeholder {
    font-size: 0.75rem;
    color: var(--color-text-muted);
  }

  .image-match-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .image-match-name {
    font-weight: 600;
    font-size: 0.8rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    flex: 1;
    min-width: 0;
  }

  .image-match-similarity {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--color-primary);
    flex-shrink: 0;
    margin-left: 0.3rem;
  }

  /* 분쟁 사례 버튼 */
  .btn-disputes {
    width: 100%;
    max-width: 560px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    border: none;
    border-radius: var(--radius);
    background: color-mix(in srgb, var(--color-danger) 10%, transparent);
    color: var(--color-danger);
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn-disputes:hover {
    background: color-mix(in srgb, var(--color-danger) 18%, transparent);
  }

  .btn-disputes-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 1.3rem;
    height: 1.3rem;
    border-radius: 50%;
    background: var(--color-danger);
    color: #fff;
    font-size: 0.75rem;
    font-weight: 800;
    flex-shrink: 0;
  }

  /* 오버레이 */
  .disputes-overlay {
    position: fixed;
    inset: 0;
    z-index: 1000;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
  }

  .disputes-modal {
    width: 100%;
    max-width: 560px;
    max-height: 80vh;
    overflow-y: auto;
    background: var(--color-surface, #fff);
    border-radius: var(--radius);
    padding: 1.5rem;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  }

  .disputes-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.25rem;
  }

  .disputes-title {
    font-size: 1.15rem;
    font-weight: 700;
    margin: 0;
  }

  .disputes-close {
    border: none;
    background: none;
    font-size: 1.5rem;
    color: var(--color-text-muted);
    cursor: pointer;
    line-height: 1;
    padding: 0.25rem;
  }

  .disputes-close:hover {
    color: var(--color-text);
  }

  .disputes-subtitle {
    font-size: 0.85rem;
    margin: 0 0 1rem;
    line-height: 1.5;
  }

  .disputes-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .dispute-card {
    padding: 1rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .dispute-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .dispute-category {
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    background: var(--color-primary);
    color: #fff;
  }

  .dispute-year {
    font-size: 0.75rem;
  }

  .dispute-title {
    font-size: 0.95rem;
    font-weight: 700;
    margin: 0;
  }

  .dispute-parties {
    font-size: 0.8rem;
    margin: 0;
  }

  .dispute-detail {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    margin-top: 0.25rem;
    font-size: 0.8rem;
    line-height: 1.5;
  }

  .dispute-row {
    display: flex;
    gap: 0.5rem;
  }

  .dispute-label {
    font-weight: 600;
    color: var(--color-text-muted);
    flex-shrink: 0;
    min-width: 2.5rem;
  }

  .dispute-lesson {
    margin-top: 0.25rem;
    padding: 0.5rem 0.75rem;
    background: color-mix(in srgb, var(--color-primary) 8%, transparent);
    border-radius: calc(var(--radius) - 2px);
    font-size: 0.8rem;
    line-height: 1.5;
    color: var(--color-text);
  }

  /* 오버레이 트랜지션 */
  .overlay-fade-enter-active,
  .overlay-fade-leave-active {
    transition: opacity 0.25s ease;
  }

  .overlay-fade-enter-active .disputes-modal,
  .overlay-fade-leave-active .disputes-modal {
    transition: transform 0.25s ease;
  }

  .overlay-fade-enter-from,
  .overlay-fade-leave-to {
    opacity: 0;
  }

  .overlay-fade-enter-from .disputes-modal {
    transform: translateY(20px);
  }

  .overlay-fade-leave-to .disputes-modal {
    transform: translateY(20px);
  }
</style>
