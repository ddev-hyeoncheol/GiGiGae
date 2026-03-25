<script setup lang="ts">
  import { ref } from 'vue'
  import { useWizardStore } from '@/stores/wizard'
  import { useRouter } from 'vue-router'
  import type { BrandCandidate } from '@/stores/wizard'
  import { recommendBrand } from '@/api/recommend'
  import PageHeader from '@/components/PageHeader.vue'
  import NavButtons from '@/components/NavButtons.vue'

  const MAX_REROLL = 2

  const wizard = useWizardStore()
  const router = useRouter()
  const error = ref('')
  const rerollCount = ref(0)

  /* 데이터 없이 직접 접근한 경우 홈으로 리다이렉트 */
  if (wizard.brandCandidates.length === 0) {
    router.replace('/')
  }

  const rerollMessages = [
    '새로운 브랜드명을 구상하고 있어요.',
    '이전 후보를 제외하고 다시 조합 중이에요.',
    '상표 충돌 위험도를 검토하고 있어요.',
    '거의 다 됐어요! 조금만 기다려 주세요.',
  ]

  function selectBrand(candidate: BrandCandidate) {
    if (wizard.selectedBrand?.brand_name !== candidate.brand_name) {
      wizard.domainCandidates = []
      wizard.selectedDomain = null
    }
    wizard.selectedBrand = candidate
  }

  function riskLabel(risk: string) {
    switch (risk) {
      case 'Low': return 'Low'
      case 'Middle': return 'Middle'
      case 'High': return 'High'
      default: return 'unchecked'
    }
  }

  function riskClass(risk: string) {
    switch (risk) {
      case 'Low': return 'badge-success'
      case 'Middle': return 'badge-warning'
      case 'High': return 'badge-danger'
      default: return 'badge-muted'
    }
  }

  async function handleReroll() {
    if (rerollCount.value >= MAX_REROLL) return

    error.value = ''
    const exclude = wizard.brandCandidates.map(c => c.brand_name)
    const category = wizard.brandCategory.length ? wizard.brandCategory : undefined
    const tone = wizard.brandTone.length ? wizard.brandTone : undefined

    wizard.startLoading(rerollMessages)

    try {
      const res = await recommendBrand({
        brand_idea: wizard.idea.trim(),
        brand_category: category,
        brand_tone: tone,
        count: 6,
        exclude,
      })
      wizard.selectedBrand = null
      wizard.brandCandidates = [...wizard.brandCandidates, ...res.brand_candidates]
      rerollCount.value++
    } catch (e) {
      error.value = e instanceof Error ? e.message : '재추천 중 오류가 발생했습니다.'
    } finally {
      wizard.stopLoading()
    }
  }

  function handleNext() {
    if (wizard.selectedBrand) {
      wizard.trademarkResult = wizard.selectedBrand.trademark
      wizard.nextStep()
      router.push('/trademark')
    }
  }

  function handleBack() {
    wizard.prevStep()
    router.push('/')
  }
</script>

<template>
  <div class="page">
    <main class="content">
      <PageHeader title="이런 브랜드명은 어때요?">
        입력하신 아이디어, 카테고리, 톤을 모두 반영하고<br/>상표 충돌 위험까지 미리 분석한 브랜드명 후보들이에요.
      </PageHeader>

      <div class="content-body">
        <ul class="candidate-list">
          <li
            v-for="candidate in wizard.brandCandidates"
            :key="candidate.brand_name"
            class="candidate-card surface"
            :class="{ selected: wizard.selectedBrand?.brand_name === candidate.brand_name }"
            @click="selectBrand(candidate)"
          >
            <div class="card-top">
              <span class="brand-name">{{ candidate.brand_name }}</span>
              <span :class="riskClass(candidate.trademark.risk)">
                {{ riskLabel(candidate.trademark.risk) }}
              </span>
            </div>
            <p class="brand-desc text-muted">{{ candidate.brand_description }}</p>
            <div class="brand-tags">
              <span v-for="tag in candidate.brand_tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </li>
        </ul>

        <p v-if="error" class="error-text">{{ error }}</p>

        <p v-if="rerollCount >= MAX_REROLL" class="reroll-hint">
          마음에 드는 브랜드명이 없다면, 아이디어를 좀 더 구체적으로 입력해 보세요.
        </p>
        <button
          v-else
          class="btn-reroll surface"
          @click="handleReroll"
        >
          <span class="reroll-icon">+</span>
          다른 브랜드명 추천받기 ({{ rerollCount }}/{{ MAX_REROLL }})
        </button>

        <NavButtons
          back-label="이전으로"
          next-label="상표권 확인하기"
          :next-disabled="!wizard.canGoNext"
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
    max-width: 720px;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .candidate-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 0.75rem;
    width: 100%;
    list-style: none;
  }

  .candidate-card {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 1rem 1.25rem;
    cursor: pointer;
    transition:
      border-color 0.2s ease,
      transform 0.15s ease;
  }

  .candidate-card:hover {
    transform: translateY(-2px);
    border-color: var(--color-primary);
  }

  .candidate-card.selected {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 2px var(--color-primary);
  }

  .card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .brand-name {
    font-weight: 600;
    font-size: 1.2rem;
  }

  .brand-desc {
    font-size: 0.85rem;
    margin: 0;
    line-height: 1.4;
  }

  .brand-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
  }

  .tag {
    font-size: 0.75rem;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    background-color: var(--color-surface-alt, var(--color-border));
    color: var(--color-text-muted, var(--color-text));
  }

  .btn-reroll {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
    padding: 0.6rem;
    color: var(--color-text-muted);
    font-size: 0.9rem;
    cursor: pointer;
    transition: border-color 0.2s ease, color 0.2s ease;
  }

  .btn-reroll:not(:disabled):hover {
    border-color: var(--color-primary);
    color: var(--color-primary);
  }

  .reroll-hint {
    text-align: center;
    color: var(--color-text-muted);
    font-size: 0.85rem;
    padding: 0.6rem 0;
  }

  .reroll-icon {
    font-size: 1.5rem;
    font-weight: 300;
    line-height: 1;
  }

  .error-text {
    text-align: center;
    color: var(--color-danger, #ef4444);
    font-size: 0.85rem;
  }

</style>
