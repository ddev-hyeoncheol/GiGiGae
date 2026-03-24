import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { BrandRecommendResult, TrademarkSearchResponse } from '@/api/types'

export type BrandCandidate = BrandRecommendResult

export type InputMode = 'idea' | 'brand'

export interface LogoCandidate {
  id: number
  url: string
  label: string
}

export interface DomainCandidate {
  domain: string
  available: boolean
  price: string
}

export const useWizardStore = defineStore('wizard', () => {
  const currentStep = ref(1)
  const totalSteps = 5

  const inputMode = ref<InputMode>('idea')
  const idea = ref('')
  const directBrandName = ref('')
  const brandCategory = ref<string[]>([])
  const brandTone = ref<string[]>([])
  const brandCandidates = ref<BrandCandidate[]>([])
  const selectedBrand = ref<BrandCandidate | null>(null)
  const trademarkResult = ref<TrademarkSearchResponse | null>(null)
  const logoCandidates = ref<LogoCandidate[]>([])
  const selectedLogo = ref<LogoCandidate | null>(null)
  const domainCandidates = ref<DomainCandidate[]>([])
  const selectedDomain = ref<DomainCandidate | null>(null)
  const finalReport = ref('')

  const canGoNext = computed(() => {
    switch (currentStep.value) {
      case 1:
        return inputMode.value === 'idea'
          ? idea.value.trim().length > 0
          : directBrandName.value.trim().length > 0
      case 2:
        return selectedBrand.value !== null
      case 3:
        return trademarkResult.value !== null
      case 4:
        return selectedDomain.value !== null
      case 5:
        return false
      default:
        return false
    }
  })

  const canGoBack = computed(() => currentStep.value > 1)

  function nextStep() {
    if (currentStep.value < totalSteps && canGoNext.value) {
      currentStep.value++
    }
  }

  function prevStep() {
    if (currentStep.value > 1) {
      currentStep.value--
    }
  }

  function goToStep(step: number) {
    if (step >= 1 && step <= totalSteps) {
      currentStep.value = step
    }
  }

  function reset() {
    currentStep.value = 1
    inputMode.value = 'idea'
    idea.value = ''
    directBrandName.value = ''
    brandCategory.value = []
    brandTone.value = []
    brandCandidates.value = []
    selectedBrand.value = null
    trademarkResult.value = null
    logoCandidates.value = []
    selectedLogo.value = null
    domainCandidates.value = []
    selectedDomain.value = null
    finalReport.value = ''
  }

  return {
    currentStep,
    totalSteps,
    inputMode,
    idea,
    directBrandName,
    brandCategory,
    brandTone,
    brandCandidates,
    selectedBrand,
    trademarkResult,
    logoCandidates,
    selectedLogo,
    domainCandidates,
    selectedDomain,
    finalReport,
    canGoNext,
    canGoBack,
    nextStep,
    prevStep,
    goToStep,
    reset,
  }
})
