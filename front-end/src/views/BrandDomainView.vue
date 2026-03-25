<script setup lang="ts">
  import { ref, reactive, onMounted } from 'vue'
  import { useWizardStore } from '@/stores/wizard'
  import { useRouter } from 'vue-router'
  import type { DomainCandidate } from '@/stores/wizard'
  import { recommendDomain, checkDomain } from '@/api'
  import PageHeader from '@/components/PageHeader.vue'
  import NavButtons from '@/components/NavButtons.vue'

  const wizard = useWizardStore()
  const router = useRouter()
  const error = ref('')

  const ALT_TLDS = ['.co.kr', '.kr', '.net', '.org', '.biz', '.shop']

  // 대체 TLD 결과 저장: { 'brandname.com': DomainCandidate[] }
  const altResults = reactive<Record<string, DomainCandidate[]>>({})
  const altLoading = reactive<Record<string, boolean>>({})
  const altExpanded = reactive<Record<string, boolean>>({})

  const loadingMessages = [
    '브랜드에 어울리는 도메인을 추천하고 있어요.',
    '도메인 등록 가능 여부를 확인하고 있어요.',
    '가격 정보를 가져오고 있어요.',
    '거의 다 됐어요. 조금만 기다려 주세요.',
  ]

  if (!wizard.selectedBrand) {
    router.replace('/')
  }

  onMounted(async () => {
    if (wizard.domainCandidates.length > 0) return

    wizard.startLoading(loadingMessages)
    error.value = ''

    try {
      const brandName = wizard.selectedBrand?.brand_name ?? ''
      const res = await recommendDomain({ brand_name: brandName })

      const checkResults = await Promise.allSettled(
        res.domain_candidates.map(async (candidate) => {
          const domainName = `${candidate.domain_name}.com`
          try {
            const check = await checkDomain({ domain_name: domainName })
            return {
              domain_name: domainName,
              domain_reason: candidate.domain_reason,
              available: check.available,
              price: check.price,
              promotion_price: check.promotion_price,
            } as DomainCandidate
          } catch {
            return {
              domain_name: domainName,
              domain_reason: candidate.domain_reason,
              available: false,
              price: null,
              promotion_price: null,
            } as DomainCandidate
          }
        })
      )

      wizard.domainCandidates = checkResults
        .filter((r): r is PromiseFulfilledResult<DomainCandidate> => r.status === 'fulfilled')
        .map(r => r.value)
    } catch (e) {
      error.value = e instanceof Error ? e.message : '도메인 추천 중 오류가 발생했습니다.'
    } finally {
      wizard.stopLoading()
    }
  })

  function discountPercent(price: string | null, promoPrice: string | null): number | null {
    if (!price || !promoPrice || price === promoPrice) return null
    const p = parseInt(price.replace(/[^0-9]/g, ''))
    const pp = parseInt(promoPrice.replace(/[^0-9]/g, ''))
    if (!p || !pp || p <= pp) return null
    return Math.round((1 - pp / p) * 100)
  }

  function selectDomain(domain: DomainCandidate) {
    if (domain.available) {
      wizard.selectedDomain = domain
    }
  }

  function handleCardClick(domain: DomainCandidate) {
    selectDomain(domain)
    loadAltTlds(domain)
  }

  async function loadAltTlds(domain: DomainCandidate) {
    const key = domain.domain_name
    if (altExpanded[key]) {
      altExpanded[key] = false
      return
    }

    altExpanded[key] = true

    if (altResults[key]) return

    altLoading[key] = true
    const baseName = key.split('.')[0]

    try {
      const results = await Promise.allSettled(
        ALT_TLDS.map(async (tld) => {
          const name = `${baseName}${tld}`
          try {
            const check = await checkDomain({ domain_name: name })
            return {
              domain_name: name,
              domain_reason: domain.domain_reason,
              available: check.available,
              price: check.price,
              promotion_price: check.promotion_price,
            } as DomainCandidate
          } catch {
            return {
              domain_name: name,
              domain_reason: '',
              available: false,
              price: null,
              promotion_price: null,
            } as DomainCandidate
          }
        })
      )

      altResults[key] = results
        .filter((r): r is PromiseFulfilledResult<DomainCandidate> => r.status === 'fulfilled')
        .map(r => r.value)
    } finally {
      altLoading[key] = false
    }
  }

  function handleNext() {
    if (wizard.selectedDomain) {
      wizard.nextStep()
      router.push('/final-guide')
    }
  }

  function handleBack() {
    wizard.prevStep()
    router.push('/trademark')
  }
</script>

<template>
  <div class="page">
    <main class="content">
      <PageHeader title="도메인 추천">
        <strong>{{ wizard.selectedBrand?.brand_name }}</strong> 에 사용할 도메인을 선택해 주세요.
      </PageHeader>

      <div class="content-body">
        <p v-if="error" class="error-msg">{{ error }}</p>

        <ul v-if="wizard.domainCandidates.length > 0" class="domain-list">
          <li v-for="domain in wizard.domainCandidates" :key="domain.domain_name" class="domain-group">
            <!-- 메인 카드 -->
            <div
              class="domain-card surface"
              :class="{
                selected: wizard.selectedDomain?.domain_name === domain.domain_name,
                unavailable: !domain.available,
              }"
              @click="handleCardClick(domain)"
            >
              <div class="domain-info">
                <span class="domain-name">{{ domain.domain_name }}</span>
                <span class="domain-reason text-muted">{{ domain.domain_reason }}</span>
              </div>
              <div class="domain-right">
                <template v-if="domain.available">
                  <div v-if="domain.promotion_price && domain.price && domain.promotion_price !== domain.price" class="domain-prices">
                    <span class="domain-price-original">연 {{ domain.price }}</span>
                    <div class="domain-promo-row">
                      <span class="domain-price-promo">연 {{ domain.promotion_price }}</span>
                      <span v-if="discountPercent(domain.price, domain.promotion_price)" class="discount-badge">-{{ discountPercent(domain.price, domain.promotion_price) }}%</span>
                    </div>
                  </div>
                  <span v-else-if="domain.price" class="domain-price">연 {{ domain.price }}</span>
                  <span v-if="altLoading[domain.domain_name]" class="alt-spinner"></span>
                  <span v-else class="badge-success">등록 가능</span>
                </template>
                <template v-else>
                  <span v-if="altLoading[domain.domain_name]" class="alt-spinner"></span>
                  <span v-else class="badge-alt">등록 불가</span>
                </template>
              </div>
            </div>

            <!-- 대체 TLD 카드들 -->
            <Transition name="alt-expand">
              <div v-if="altExpanded[domain.domain_name] && altResults[domain.domain_name]" class="alt-tld-list">
                <template v-if="altResults[domain.domain_name]">
                  <div
                    v-for="alt in altResults[domain.domain_name]"
                    :key="alt.domain_name"
                    class="domain-card domain-card-alt surface"
                    :class="{
                      selected: wizard.selectedDomain?.domain_name === alt.domain_name,
                      unavailable: !alt.available,
                    }"
                    @click="selectDomain(alt)"
                  >
                    <div class="domain-info">
                      <span class="domain-name">{{ alt.domain_name }}</span>
                    </div>
                    <div class="domain-right">
                      <template v-if="alt.available">
                        <div v-if="alt.promotion_price && alt.price && alt.promotion_price !== alt.price" class="domain-prices">
                          <span class="domain-price-original">연 {{ alt.price }}</span>
                          <span class="price-arrow">→</span>
                          <div class="domain-promo-row">
                            <span class="domain-price-promo">연 {{ alt.promotion_price }}</span>
                            <span v-if="discountPercent(alt.price, alt.promotion_price)" class="discount-badge">-{{ discountPercent(alt.price, alt.promotion_price) }}%</span>
                          </div>
                        </div>
                        <span v-else-if="alt.price" class="domain-price">연 {{ alt.price }}</span>
                        <span class="badge-success">등록 가능</span>
                      </template>
                      <span v-else class="badge-unavailable">등록 불가</span>
                    </div>
                  </div>
                </template>
              </div>
            </Transition>
          </li>
        </ul>

        <NavButtons
          back-label="이전으로"
          next-label="최종 가이드 보기"
          :next-disabled="!wizard.canGoNext"
          @next="handleNext"
          @back="handleBack"
        />
      </div>
    </main>
  </div>
</template>

<style scoped>
  .page { display: flex; flex-direction: column; position: relative; }

  .content {
    flex: 1; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 1rem 1rem 2rem; gap: 1.5rem;
  }

  .content-body { width: 100%; max-width: 600px; display: flex; flex-direction: column; gap: 1rem; }

  .domain-list { display: flex; flex-direction: column; gap: 0.75rem; width: 100%; list-style: none; }

  .domain-group { display: flex; flex-direction: column; }

  .domain-card {
    display: flex; justify-content: space-between; align-items: center;
    padding: 1rem 1.25rem; cursor: pointer;
    transition: border-color 0.2s ease, transform 0.15s ease;
  }

  .domain-card:hover { transform: translateY(-2px); }
  .domain-card.selected { border-color: var(--color-primary); box-shadow: 0 0 0 2px var(--color-primary); }
  .domain-card.unavailable { cursor: pointer; }

  .domain-info { display: flex; flex-direction: column; gap: 0.2rem; flex: 1; min-width: 0; }
  .domain-name { font-weight: 600; font-size: 1rem; }
  .domain-reason { font-size: 0.8rem; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }

  .domain-right { display: flex; align-items: center; gap: 0.5rem; flex-shrink: 0; }

  .domain-prices { display: flex; flex-direction: column; align-items: flex-end; gap: 0.1rem; }
  .domain-promo-row { display: flex; align-items: center; gap: 0.3rem; }
  .price-arrow { font-size: 0.75rem; color: var(--color-text-muted); }
  .domain-price-original { font-size: 0.75rem; color: var(--color-text-muted); text-decoration: line-through; }
  .domain-price-promo { font-size: 0.9rem; font-weight: 700; color: var(--color-danger); }
  .discount-badge {
    font-size: 0.65rem; font-weight: 700; padding: 0.1rem 0.35rem;
    border-radius: 4px; background: var(--color-danger); color: #fff;
  }
  .domain-price { font-size: 0.85rem; font-weight: 500; color: var(--color-text-muted); }

  .badge-alt {
    font-size: 0.75rem; font-weight: 600; padding: 0.3rem 0.6rem;
    border-radius: 999px; border: none;
    background: color-mix(in srgb, var(--color-primary) 10%, transparent);
    color: var(--color-primary); cursor: pointer; transition: background 0.2s;
  }
  .badge-alt:hover { background: color-mix(in srgb, var(--color-primary) 20%, transparent); }

  .badge-unavailable {
    font-size: 0.75rem; font-weight: 600; padding: 0.3rem 0.6rem;
    border-radius: 999px; background: var(--color-border); color: var(--color-text-muted);
  }

  /* 대체 TLD 카드 */
  .alt-tld-list {
    display: flex; flex-direction: column; gap: 0.35rem;
    margin-left: 1.5rem; margin-top: 0.35rem;
  }

  .domain-card-alt {
    padding: 0.75rem 1rem;
    border-left: 3px solid var(--color-primary);
  }

  .domain-card-alt .domain-name { font-size: 0.9rem; }
  .domain-card-alt .domain-prices { flex-direction: row; align-items: center; gap: 0.3rem; }

  .alt-spinner {
    width: 20px; height: 20px; border-radius: 50%; margin-right: 0.4rem;
    border: 2px solid var(--color-border);
    border-top-color: var(--color-primary);
    animation: spin 0.6s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  .alt-expand-enter-active, .alt-expand-leave-active { transition: all 0.3s ease; overflow: hidden; }
  .alt-expand-enter-from, .alt-expand-leave-to { opacity: 0; max-height: 0; }
  .alt-expand-enter-to, .alt-expand-leave-from { opacity: 1; max-height: 500px; }

  .error-msg { color: var(--color-danger); font-size: 0.85rem; margin: 0; }
</style>
