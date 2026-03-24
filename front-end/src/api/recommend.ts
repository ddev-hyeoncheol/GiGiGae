/** 브랜드/도메인 추천 API */

import { api } from './client'
import type {
  BrandRecommendRequest,
  BrandRecommendResponse,
  DomainRecommendRequest,
  DomainRecommendResponse,
} from './types'

const PREFIX = '/v1/recommend'

/** 브랜드명 추천 + 상표 충돌 검색 */
export function recommendBrand(body: BrandRecommendRequest) {
  return api.post<BrandRecommendResponse>(`${PREFIX}/brand`, body)
}

/** 도메인 후보 추천 */
export function recommendDomain(body: DomainRecommendRequest) {
  return api.post<DomainRecommendResponse>(`${PREFIX}/domain`, body)
}
