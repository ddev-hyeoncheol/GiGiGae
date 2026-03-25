<script setup lang="ts">
  import { ref, onMounted } from 'vue'
  import { useWizardStore } from '@/stores/wizard'
  import { useRouter } from 'vue-router'
  import type { DomainCandidate } from '@/stores/wizard'
  import { recommendDomain, checkDomain } from '@/api'
  import PageHeader from '@/components/PageHeader.vue'
  import NavButtons from '@/components/NavButtons.vue'

  const wizard = useWizardStore()
  const router = useRouter()

  const error = ref('')

  const loadingMessages = [
    '브랜드에 어울리는 도메인을 추천하고 있어요.',
    '추천된 도메인의 등록 가능 여부를 확인하고 있어요.',
    '가격 정보를 가져오고 있어요.',
    '이제 거의 다 됐어요.',
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

  function selectDomain(domain: DomainCandidate) {
    if (domain.available) {
      wizard.selectedDomain = domain
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
        <strong>{{ wizard.selectedBrand?.brand_name }}</strong> 에 사용할 도메인을 선택하세요.
      </PageHeader>

      <div class="content-body">
        <p v-if="error" class="error-msg">{{ error }}</p>

        <ul v-if="wizard.domainCandidates.length > 0" class="domain-list">
          <li
            v-for="domain in wizard.domainCandidates"
            :key="domain.domain_name"
            class="domain-card surface"
            :class="{
              selected: wizard.selectedDomain?.domain_name === domain.domain_name,
              unavailable: !domain.available,
            }"
            @click="selectDomain(domain)"
          >
            <div class="domain-info">
              <span class="domain-name">{{ domain.domain_name }}</span>
              <span class="domain-reason text-muted">{{ domain.domain_reason }}</span>
            </div>
            <div class="domain-right">
              <span v-if="domain.available" class="domain-price">
                {{ domain.promotion_price ?? domain.price ?? '' }}
              </span>
              <span v-if="domain.available" class="badge-success">등록 가능</span>
              <span v-else class="badge-danger">등록 불가</span>
            </div>
          </li>
        </ul>

        <NavButtons
          back-label="이전으로"
          next-label="배포 가이드 보기"
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
    position: relative;
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
    max-width: 600px;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .domain-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    width: 100%;
    list-style: none;
  }

  .domain-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.25rem;
    cursor: pointer;
    transition:
      border-color 0.2s ease,
      transform 0.15s ease;
  }

  .domain-card:hover:not(.unavailable) {
    transform: translateY(-2px);
  }

  .domain-card.selected {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 2px var(--color-primary);
  }

  .domain-card.unavailable {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .domain-info {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
  }

  .domain-name {
    font-weight: 600;
    font-size: 1rem;
  }

  .domain-reason {
    font-size: 0.8rem;
  }

  .domain-right {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .domain-price {
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--color-text-muted);
  }

  .error-msg {
    color: var(--color-danger, #e74c3c);
    font-size: 0.85rem;
    margin: 0;
  }
</style>
