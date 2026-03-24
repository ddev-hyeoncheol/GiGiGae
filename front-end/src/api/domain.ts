/** 도메인 가용성 확인 API */

import { api } from './client'
import type { DomainCheckRequest, DomainCheckResult } from './types'

const PREFIX = '/v1/domain'

/** 단건 도메인 가용성 확인 */
export function checkDomain(body: DomainCheckRequest) {
  return api.post<DomainCheckResult>(`${PREFIX}/check`, body)
}
