import { computed, type Ref } from 'vue'
import type { TrademarkSearchResponse, ImageSearchResponse } from '@/api/types'
import { categoryToNiceClasses } from '@/utils/niceClassMapping'

export type CheckStatus = 'safe' | 'caution' | 'warning'

export interface ChecklistItem {
  id: string
  label: string
  status: CheckStatus
  statusLabel: string
  description: string
  disabled: boolean
}

const STATUS_LABELS: Record<CheckStatus, string> = {
  safe: '안심',
  caution: '주의',
  warning: '위험',
}

export function useTrademarkChecklist(
  trademarkResult: Ref<TrademarkSearchResponse | null>,
  imageSearchResult: Ref<ImageSearchResponse | null>,
  brandCategories: Ref<string[]>,
) {
  const matches = computed(() => trademarkResult.value?.matches ?? [])
  const risk = computed(() => trademarkResult.value?.risk ?? 'unchecked')
  const hasTextSearch = computed(() => {
    const r = trademarkResult.value
    if (!r) return false
    // unchecked + matches 0건이면 실제 텍스트 검색이 수행되지 않은 것
    if (r.risk === 'unchecked' && r.matches.length === 0) return false
    return true
  })
  const hasImageSearch = computed(() => (imageSearchResult.value?.matches?.length ?? 0) > 0)

  const userNiceCodes = computed(() => {
    const codes = new Set<string>()
    for (const cat of brandCategories.value) {
      const niceCodes = categoryToNiceClasses[cat]
      if (niceCodes) niceCodes.forEach(c => codes.add(c))
    }
    return codes
  })

  // 1. 동일 상표 여부
  const exactMatch = computed<ChecklistItem>(() => {
    const hasExact = matches.value.some(m => m.similarity >= 0.9)
    const hasNear = matches.value.some(m => m.similarity >= 0.7)
    let status: CheckStatus = 'safe'
    let desc = '같은 업종에서 동일한 이름은 확인되지 않았어요.'
    if (hasExact) {
      status = 'warning'
      desc = '같은 업종에서 동일하거나 거의 같은 이름이 이미 등록 또는 출원돼 있어요.'
    } else if (hasNear) {
      status = 'caution'
      desc = '매우 유사한 이름의 상표가 확인돼 추가 검토가 필요해요.'
    }
    const disabled = !hasTextSearch.value
    if (disabled) return { id: 'exact-match', label: '동일 상표 여부', status: 'safe' as CheckStatus, statusLabel: '검색 안됨', description: '브랜드명이 입력되지 않아 검토하지 못했어요.', disabled: true }
    return { id: 'exact-match', label: '동일 상표 여부', status, statusLabel: STATUS_LABELS[status], description: desc, disabled: false }
  })

  // 2. 유사 상표 여부
  const similarMatch = computed<ChecklistItem>(() => {
    const disabled = !hasTextSearch.value
    if (disabled) return { id: 'similar-match', label: '유사 상표 여부', status: 'safe' as CheckStatus, statusLabel: '검색 안됨', description: '브랜드명이 입력되지 않아 검토하지 못했어요.', disabled: true }
    const count = matches.value.filter(m => m.similarity >= 0.4 && m.similarity < 0.9).length
    let status: CheckStatus = 'safe'
    let desc = '발음·철자·의미에서 유사한 상표가 확인되지 않았어요.'
    if (count >= 3) {
      status = 'warning'
      desc = '발음·철자·의미에서 유사한 상표가 다수 확인됐어요.'
    } else if (count >= 1) {
      status = 'caution'
      desc = '비슷한 발음이나 표기의 상표가 일부 보여요.'
    }
    return { id: 'similar-match', label: '유사 상표 여부', status, statusLabel: STATUS_LABELS[status], description: desc, disabled: false }
  })

  // 3. 업종/분류 충돌
  const niceClassConflict = computed<ChecklistItem>(() => {
    const disabled = !hasTextSearch.value
    if (disabled) return { id: 'nice-conflict', label: '업종 / 분류 충돌', status: 'safe' as CheckStatus, statusLabel: '검색 안됨', description: '브랜드명이 입력되지 않아 검토하지 못했어요.', disabled: true }
    if (userNiceCodes.value.size === 0) {
      return { id: 'nice-conflict', label: '업종 / 분류 충돌', status: 'safe', statusLabel: STATUS_LABELS.safe, description: '선택된 업종 분류가 없어 전체 기준으로 검토했어요.', disabled: false }
    }
    const conflicting = matches.value.filter(m => {
      if (!m.nice_class) return false
      return m.nice_class.split('|').map(c => c.trim()).some(c => userNiceCodes.value.has(c))
    })
    let status: CheckStatus = 'safe'
    let desc = '사용 예정 업종과 동일 분류에서 충돌 가능성이 낮아요.'
    if (conflicting.length >= 3) {
      status = 'warning'
      desc = '사용 예정 분류와 동일 또는 인접 분류에서 충돌 가능성이 있어요.'
    } else if (conflicting.length >= 1) {
      status = 'caution'
      desc = '일부 인접 분류에서 유사 상표가 확인돼요.'
    }
    return { id: 'nice-conflict', label: '업종 / 분류 충돌', status, statusLabel: STATUS_LABELS[status], description: desc, disabled: false }
  })

  // 4. 식별력
  const distinctiveness = computed<ChecklistItem>(() => {
    const disabled = !hasTextSearch.value
    if (disabled) return { id: 'distinctiveness', label: '식별력', status: 'safe' as CheckStatus, statusLabel: '검색 안됨', description: '브랜드명이 입력되지 않아 검토하지 못했어요.', disabled: true }
    let status: CheckStatus = 'safe'
    let desc = '독창적인 조어 또는 임의어로 식별력이 충분해 보여요.'
    if (risk.value === 'High') {
      status = 'warning'
      desc = '일반적이거나 설명적인 명칭에 가까워 식별력이 약할 수 있어요.'
    } else if (risk.value === 'Middle') {
      status = 'caution'
      desc = '이름 자체 식별력은 있지만 기존 상표와 혼동될 수 있어요.'
    }
    return { id: 'distinctiveness', label: '식별력', status, statusLabel: STATUS_LABELS[status], description: desc, disabled: false }
  })

  // 5. 보통명칭화 위험
  const genericization = computed<ChecklistItem>(() => {
    const disabled = !hasTextSearch.value
    if (disabled) return { id: 'genericization', label: '보통명칭화 위험', status: 'safe' as CheckStatus, statusLabel: '검색 안됨', description: '브랜드명이 입력되지 않아 검토하지 못했어요.', disabled: true }
    let status: CheckStatus = 'safe'
    let desc = '브랜드명이 상품명처럼 인식될 가능성이 낮아요.'
    if (risk.value === 'High') {
      status = 'caution'
      desc = '업계에서 통용되는 표현과 유사해 등록 거절 가능성이 있어요.'
    } else if (risk.value === 'Middle') {
      status = 'caution'
      desc = '일부 보통명칭 요소가 포함되어 있을 수 있어요.'
    }
    return { id: 'genericization', label: '보통명칭화 위험', status, statusLabel: STATUS_LABELS[status], description: desc, disabled: false }
  })

  // 6. 로고 결합 시 충돌
  const logoConflict = computed<ChecklistItem>(() => {
    if (!hasImageSearch.value) {
      return { id: 'logo-conflict', label: '로고 결합 시 충돌', status: 'safe' as CheckStatus, statusLabel: '로고 미입력', description: '로고 이미지가 업로드되지 않아 검토하지 못했어요.', disabled: true }
    }
    const imgMatches = imageSearchResult.value?.matches ?? []
    const highSim = imgMatches.some(m => m.similarity >= 0.5)
    const anySim = imgMatches.length > 0
    let status: CheckStatus = 'safe'
    let desc = '로고 이미지 기반 유사 상표는 확인되지 않았어요.'
    if (highSim) {
      status = 'warning'
      desc = '시각적으로 유사한 상표 로고가 확인돼 주의가 필요해요.'
    } else if (anySim) {
      status = 'caution'
      desc = '일부 시각적으로 유사한 로고가 있어 참고해 주세요.'
    }
    return { id: 'logo-conflict', label: '로고 결합 시 충돌', status, statusLabel: STATUS_LABELS[status], description: desc, disabled: false }
  })

  const items = computed(() => [
    exactMatch.value,
    similarMatch.value,
    niceClassConflict.value,
    distinctiveness.value,
    genericization.value,
    logoConflict.value,
  ])

  const totalChecked = computed(() => items.value.length)

  return { items, totalChecked }
}
