<script setup lang="ts">
  import { ref, computed } from 'vue'
  import { useWizardStore } from '@/stores/wizard'
  import { useRouter } from 'vue-router'
  import { useTrademarkChecklist } from '@/composables/useTrademarkChecklist'
  import { resolveCategories } from '@/utils/niceClassMapping'
  import PageHeader from '@/components/PageHeader.vue'
  import NavButtons from '@/components/NavButtons.vue'
  import TrademarkChecklist from '@/components/TrademarkChecklist.vue'
  import TrademarkMatchTable from '@/components/TrademarkMatchTable.vue'

  const wizard = useWizardStore()
  const router = useRouter()
  const showDisputes = ref(false)

  if (!wizard.trademarkResult && !wizard.selectedBrand) {
    router.replace('/')
  }

  const result = wizard.trademarkResult ?? wizard.selectedBrand?.trademark ?? null

  const { items, totalChecked } = useTrademarkChecklist(
    computed(() => result),
    computed(() => wizard.imageSearchResult),
    computed(() => wizard.brandCategory),
  )

  function riskClass(risk: string) {
    switch (risk) {
      case 'Low': return 'risk-low'
      case 'Middle': return 'risk-middle'
      case 'High': return 'risk-high'
      default: return 'risk-unchecked'
    }
  }

  const hasTextSearch = computed(() => {
    const r = result
    if (!r) return false
    if (r.risk === 'unchecked' && r.matches.length === 0) return false
    return true
  })

  function riskTitle(risk: string) {
    switch (risk) {
      case 'Low': return '충돌 가능성이 낮은 상표예요'
      case 'Middle': return '몇 가지 확인이 필요한 상표예요'
      case 'High': return '위험도가 높은 상표예요'
      default: return '로고 기반으로 검토했어요'
    }
  }

  function riskDescription(risk: string) {
    switch (risk) {
      case 'Low': return '현재 기준으로는 충돌 가능성이 낮아 보여요. 같은 분류 또는 유사한 이름이 확인되지 않아 출원에 유리합니다.'
      case 'Middle': return '몇 가지는 괜찮지만, 비슷한 요소가 보여 한 번 더 확인하는 게 좋아요.'
      case 'High': return '동일하거나 매우 유사한 이름이 같은 분류에서 이미 등록 또는 출원돼 있어요. 그대로 사용하면 분쟁 가능성이 있어요.'
      default: return '브랜드명이 입력되지 않아 텍스트 기반 분석은 수행되지 않았어요. 로고 이미지 기반의 시각적 유사도만 검토했습니다.'
    }
  }

  function riskAdvice(risk: string) {
    switch (risk) {
      case 'Middle': return '같은 분류 또는 유사한 이름이 확인돼 그대로 진행하기 전 한 번 더 검토하는 게 좋아요'
      case 'High': return '같은 분류 또는 유사한 이름이 확인돼 그대로 진행하기 전 한 번 더 검토하는 게 좋아요'
      default: return ''
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

  interface DisputeCase { category: string; title: string; parties: string; year: string; issue: string; result: string; lesson: string }
  const disputeCases: DisputeCase[] = [
    { category: '보통명칭화', title: '초코파이 분쟁', parties: '오리온 vs 롯데 등', year: '1997', issue: '오리온이 최초 사용했으나 경쟁사 무대응으로 보통명칭화', result: '오리온 패소, 초코파이는 보통명칭 인정', lesson: '등록 후에도 적극적인 상표 관리가 필수입니다.' },
    { category: '보통명칭화', title: '그립톡 분쟁', parties: '아이버스터 vs 60여 업체', year: '2023', issue: '스마트폰 거치대를 칭하는 보통명칭이 됨', result: '일부 지정상품 무효 심결', lesson: '브랜드명이 상품 자체를 지칭하게 되면 상표 등록이 무효화될 수 있습니다.' },
    { category: '유사 상표', title: '스타벅스 vs 스타프릭스', parties: '스타벅스 vs 스타프릭스', year: '2019', issue: '발음 및 외관의 유사성으로 혼동 가능성 제기', result: '스타벅스 승소, 유사 상표 등록 무효', lesson: '유명 브랜드와 발음이나 외관이 유사하면 분쟁 대상이 됩니다.' },
    { category: '유사 상표', title: '카카오 vs 유사 명칭', parties: '카카오 vs 유사 명칭 사업자', year: '2020', issue: '카카오 브랜드의 광범위한 식별력 인정 범위', result: '카카오 측 승소', lesson: '저명 상표와 유사한 이름은 업종이 달라도 분쟁 위험이 높습니다.' },
    { category: '해외 선점', title: 'K패션 해외 상표 선점', parties: '한국 의류 브랜드 vs 해외 무단 등록자', year: '2023', issue: '한국 의류 브랜드명이 해외에서 무단 등록', result: '피해 5,751건 (2023년 기준)', lesson: '글로벌 진출 시 주요 시장에 상표를 먼저 등록해야 합니다.' },
    { category: '디자인/로고', title: '로고 유사성 분쟁', parties: '다수 기업 간 로고 분쟁', year: '2021', issue: '도형 상표의 외관 유사성으로 인한 혼동 가능성', result: '유사 판정 시 후출원 무효', lesson: '로고 디자인도 기존 등록 상표와 시각적 유사도를 확인해야 합니다.' },
    { category: '업종간 충돌', title: '동일 명칭 타업종 충돌', parties: '동명 브랜드 타업종 사업자', year: '2020', issue: '동일 브랜드명이 다른 업종에서 등록되어 혼동 발생', result: '저명 상표 우선 인정', lesson: '니스 분류가 다르더라도 저명 상표와의 충돌은 피해야 합니다.' },
    { category: '대기업 vs 중소', title: '상표 브로커 분쟁', parties: '중소 사업자 vs 상표 브로커', year: '상시', issue: '사용 의사 없이 상표 대량 등록 후 합의금 요구', result: '불사용취소심판으로 대응 가능', lesson: '브랜드명 확정 후 빠르게 출원해야 선점 피해를 방지할 수 있습니다.' },
  ]
</script>

<template>
  <div class="page">
    <main class="content">
      <PageHeader title="상표 분석">
        <strong>"{{ result?.brand_name }}"</strong> 에 대한 상표 분석 결과예요.
      </PageHeader>

      <button class="btn-disputes" @click="showDisputes = true">
        <span class="btn-disputes-icon">!</span>
        왜 상표권 등록이 중요한가요?
      </button>

      <div class="content-body">
        <!-- A. 위험도 요약 카드 -->
        <div v-if="result" class="risk-summary" :class="riskClass(result.risk)">
          <div class="risk-summary-title">{{ riskTitle(result.risk) }}</div>
          <p class="risk-summary-desc">{{ riskDescription(result.risk) }}</p>
          <p v-if="riskAdvice(result.risk)" class="risk-summary-advice text-muted">{{ riskAdvice(result.risk) }}</p>
          <p class="risk-summary-disclaimer text-muted">본 분석은 특허청 공개 데이터 기반의 참고 자료예요. 최종 출원 여부는 변리사 검토를 권장해요.</p>
        </div>

        <!-- B. 체크리스트 (6개 전체 노출) -->
        <TrademarkChecklist :items="items" :total-checked="totalChecked" />

        <!-- C. 유사 상표 카드 (텍스트 검색 있을 때만) -->
        <template v-if="result && result.matches.length > 0">
          <TrademarkMatchTable :matches="result.matches" title="브랜드명 기반 유사 상표" />
        </template>

        <!-- D. 이미지 기반 유사 상표 -->
        <div v-if="wizard.imageSearchResult?.matches?.length" class="image-section surface">
          <h3 class="section-title">로고 기반 유사 상표 <span class="text-muted">({{ wizard.imageSearchResult.matches.length }}건)</span></h3>
          <p class="section-sub text-muted">업로드한 로고와 시각적으로 유사한 등록 상표예요.</p>
          <div class="image-grid">
            <div v-for="match in wizard.imageSearchResult.matches" :key="match.application_no" class="image-card">
              <div class="image-card-thumb">
                <img v-if="match.image_path" :src="match.image_path" :alt="match.name" />
                <div v-else class="image-placeholder">No Image</div>
              </div>
              <div class="image-card-info">
                <span class="image-card-name">{{ match.name }}</span>
                <span class="image-card-sim">{{ similarityPercent(match.similarity) }}%</span>
              </div>
              <div class="image-card-cats">
                <span v-for="cat in resolveCategories(match.nice_class)" :key="cat" class="category-tag">{{ cat }}</span>
              </div>
            </div>
          </div>
        </div>

        <NavButtons back-label="이전으로" next-label="도메인 조회하기" :next-disabled="false" @next="handleNext" @back="handleBack" />

        <!-- 분쟁 사례 오버레이 -->
        <Transition name="overlay-fade">
          <div v-if="showDisputes" class="disputes-overlay" @click.self="showDisputes = false">
            <div class="disputes-modal">
              <div class="disputes-header">
                <h2 class="disputes-modal-title">왜 상표권 등록이 중요한가요?</h2>
                <button class="disputes-close" @click="showDisputes = false">&times;</button>
              </div>
              <p class="disputes-subtitle text-muted">실제 분쟁 사례를 통해 상표권 등록의 중요성을 확인하세요.</p>
              <div class="disputes-list">
                <div v-for="(d, i) in disputeCases" :key="i" class="dispute-card">
                  <div class="dispute-card-header">
                    <span class="dispute-category">{{ d.category }}</span>
                    <span class="dispute-year text-muted">{{ d.year }}</span>
                  </div>
                  <h4 class="dispute-card-title">{{ d.title }}</h4>
                  <p class="dispute-parties text-muted">{{ d.parties }}</p>
                  <div class="dispute-detail">
                    <div class="dispute-row"><span class="dispute-label">쟁점</span><span>{{ d.issue }}</span></div>
                    <div class="dispute-row"><span class="dispute-label">결과</span><span>{{ d.result }}</span></div>
                  </div>
                  <div class="dispute-lesson">{{ d.lesson }}</div>
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
  .page { display: flex; flex-direction: column; }
  .content { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 1rem 1rem 2rem; gap: 1rem; }
  .content-body { width: 100%; max-width: 720px; display: flex; flex-direction: column; gap: 1rem; }

  /* 위험도 인라인 배지 */
  .risk-badge-inline { font-size: 0.75rem; font-weight: 700; padding: 0.2rem 0.6rem; border-radius: 999px; color: #fff; margin-left: 0.5rem; }
  .risk-badge-inline.risk-low { background: var(--color-success); }
  .risk-badge-inline.risk-middle { background: var(--color-accent); }
  .risk-badge-inline.risk-high { background: var(--color-danger); }
  .risk-badge-inline.risk-unchecked { background: var(--color-border); color: var(--color-text); }

  /* 위험도 요약 카드 */
  .risk-summary { padding: 1.25rem; border-radius: var(--radius); border-left: 4px solid; }
  .risk-summary.risk-low { background: color-mix(in srgb, var(--color-success) 8%, var(--color-surface)); border-left-color: var(--color-success); }
  .risk-summary.risk-middle { background: color-mix(in srgb, var(--color-accent) 8%, var(--color-surface)); border-left-color: var(--color-accent); }
  .risk-summary.risk-high { background: color-mix(in srgb, var(--color-danger) 8%, var(--color-surface)); border-left-color: var(--color-danger); }
  .risk-summary.risk-unchecked { background: var(--color-surface); border-left-color: var(--color-border); }

  .risk-summary-title { font-size: 1rem; font-weight: 700; margin-bottom: 0.5rem; }
  .risk-summary.risk-low .risk-summary-title { color: var(--color-success); }
  .risk-summary.risk-middle .risk-summary-title { color: var(--color-accent); }
  .risk-summary.risk-high .risk-summary-title { color: var(--color-danger); }

  .risk-summary-desc { font-size: 0.85rem; line-height: 1.6; margin: 0; color: var(--color-text); }
  .risk-summary-advice { font-size: 0.8rem; margin: 0.5rem 0 0; }
  .risk-summary-disclaimer { font-size: 0.75rem; margin: 0.75rem 0 0; padding-top: 0.5rem; border-top: 1px solid rgba(0,0,0,0.08); }

  /* 공통 */
  .no-matches { padding: 2rem; text-align: center; border-radius: var(--radius); }
  .category-tag { font-size: 0.7rem; padding: 0.1rem 0.45rem; border-radius: 999px; background-color: var(--color-surface-alt, var(--color-border)); color: var(--color-text-muted); white-space: nowrap; }

  /* 이미지 유사 상표 */
  .image-section { padding: 1.25rem; border-radius: var(--radius); }
  .section-title { font-size: 1rem; font-weight: 700; margin: 0 0 0.25rem; }
  .section-sub { font-size: 0.8rem; margin: 0 0 0.75rem; }
  .image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 0.75rem; }
  .image-card { display: flex; flex-direction: column; gap: 0.4rem; padding: 0.6rem; border: 1px solid var(--color-border); border-radius: var(--radius); background: var(--color-bg); transition: border-color 0.2s; }
  .image-card:hover { border-color: var(--color-primary); }
  .image-card-thumb { width: 100%; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; overflow: hidden; border-radius: calc(var(--radius) - 2px); background: #f9f9f9; }
  .image-card-thumb img { max-width: 100%; max-height: 100%; object-fit: contain; }
  .image-placeholder { font-size: 0.75rem; color: var(--color-text-muted); }
  .image-card-info { display: flex; justify-content: space-between; align-items: center; }
  .image-card-name { font-weight: 600; font-size: 0.8rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; min-width: 0; }
  .image-card-sim { font-size: 0.75rem; font-weight: 600; color: var(--color-primary); flex-shrink: 0; margin-left: 0.3rem; }
  .image-card-cats { display: flex; flex-wrap: wrap; gap: 0.3rem; }

  /* 분쟁 사례 버튼 */
  .btn-disputes { width: 100%; max-width: 720px; display: flex; align-items: center; justify-content: center; gap: 0.5rem; padding: 0.75rem 1rem; border: none; border-radius: var(--radius); background: color-mix(in srgb, var(--color-danger) 10%, transparent); color: var(--color-danger); font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: all 0.2s; }
  .btn-disputes:hover { background: color-mix(in srgb, var(--color-danger) 18%, transparent); }
  .btn-disputes-icon { display: flex; align-items: center; justify-content: center; width: 1.3rem; height: 1.3rem; border-radius: 50%; background: var(--color-danger); color: #fff; font-size: 0.75rem; font-weight: 800; flex-shrink: 0; }

  /* 오버레이 */
  .disputes-overlay { position: fixed; inset: 0; z-index: 1000; background: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; padding: 1rem; }
  .disputes-modal { width: 100%; max-width: 560px; max-height: 80vh; overflow-y: auto; background: var(--color-surface, #fff); border-radius: var(--radius); padding: 1.5rem; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2); }
  .disputes-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem; }
  .disputes-modal-title { font-size: 1.15rem; font-weight: 700; margin: 0; }
  .disputes-close { border: none; background: none; font-size: 1.5rem; color: var(--color-text-muted); cursor: pointer; line-height: 1; padding: 0.25rem; }
  .disputes-close:hover { color: var(--color-text); }
  .disputes-subtitle { font-size: 0.85rem; margin: 0 0 1rem; line-height: 1.5; }
  .disputes-list { display: flex; flex-direction: column; gap: 0.75rem; }
  .dispute-card { padding: 1rem; border: 1px solid var(--color-border); border-radius: var(--radius); display: flex; flex-direction: column; gap: 0.4rem; }
  .dispute-card-header { display: flex; justify-content: space-between; align-items: center; }
  .dispute-category { font-size: 0.7rem; font-weight: 600; padding: 0.15rem 0.5rem; border-radius: 999px; background: var(--color-primary); color: #fff; }
  .dispute-year { font-size: 0.75rem; }
  .dispute-card-title { font-size: 0.95rem; font-weight: 700; margin: 0; }
  .dispute-parties { font-size: 0.8rem; margin: 0; }
  .dispute-detail { display: flex; flex-direction: column; gap: 0.3rem; margin-top: 0.25rem; font-size: 0.8rem; line-height: 1.5; }
  .dispute-row { display: flex; gap: 0.5rem; }
  .dispute-label { font-weight: 600; color: var(--color-text-muted); flex-shrink: 0; min-width: 2.5rem; }
  .dispute-lesson { margin-top: 0.25rem; padding: 0.5rem 0.75rem; background: color-mix(in srgb, var(--color-primary) 8%, transparent); border-radius: calc(var(--radius) - 2px); font-size: 0.8rem; line-height: 1.5; }

  .overlay-fade-enter-active, .overlay-fade-leave-active { transition: opacity 0.25s ease; }
  .overlay-fade-enter-active .disputes-modal, .overlay-fade-leave-active .disputes-modal { transition: transform 0.25s ease; }
  .overlay-fade-enter-from, .overlay-fade-leave-to { opacity: 0; }
  .overlay-fade-enter-from .disputes-modal, .overlay-fade-leave-to .disputes-modal { transform: translateY(20px); }
</style>
