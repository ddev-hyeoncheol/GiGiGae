/** 상표 검색 API */

import { api } from './client'
import type { TrademarkSearchRequest, TrademarkSearchResponse } from './types'

const PREFIX = '/v1/trademark'

/** 브랜드명 상표 유사도 검색 */
export function searchTrademark(body: TrademarkSearchRequest) {
  return api.post<TrademarkSearchResponse>(`${PREFIX}/search`, body)
}
