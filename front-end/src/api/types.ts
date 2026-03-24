/** 백엔드 API 요청/응답 타입 (Pydantic 스키마 미러링) */

// ── 상표 검색 ──
export interface TrademarkMatch {
  name: string
  nice_class: string | null
  legal_status: string | null
  application_no: string
  similarity: number
}

export interface TrademarkSearchRequest {
  brand_name: string
  nice_classes?: string[]
  threshold?: number
}

export interface TrademarkSearchResponse {
  brand_name: string
  risk: 'Low' | 'Middle' | 'High' | 'unchecked'
  matches: TrademarkMatch[]
}

// ── 브랜드 추천 ──
export interface BrandRecommendRequest {
  brand_idea: string
  brand_category?: string[]
  brand_tone?: string[]
  exclude?: string[]
}

export interface BrandRecommendResult {
  brand_name: string
  brand_description: string
  brand_tags: string[]
  trademark: TrademarkSearchResponse
}

export interface BrandRecommendResponse {
  brand_candidates: BrandRecommendResult[]
}

// ── 도메인 추천 ──
export interface DomainRecommendRequest {
  brand_name: string
  exclude?: string[]
}

export interface DomainRecommendCandidate {
  domain_name: string
  domain_reason: string
}

export interface DomainRecommendResponse {
  domain_candidates: DomainRecommendCandidate[]
}

// ── 도메인 가용성 확인 ──
export interface DomainCheckRequest {
  domain_name: string
}

export interface DomainCheckResult {
  domain_name: string
  available: boolean
  message: string
  price: string | null
  promotion_price: string | null
}
