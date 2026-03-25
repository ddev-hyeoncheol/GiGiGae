/** 니스 분류 코드 ↔ 카테고리 매핑 유틸리티 */

export const niceToCategoryMap: Record<string, string> = {
  '35': '이커머스 · 온라인스토어',
  '42': '이커머스 · 온라인스토어',
  '29': 'F&B · 카페 · 숙박',
  '30': 'F&B · 카페 · 숙박',
  '32': 'F&B · 카페 · 숙박',
  '43': 'F&B · 카페 · 숙박',
  '9': 'IT · SaaS · 테크',
  '18': '패션 · 의류 브랜드',
  '25': '패션 · 의류 브랜드',
  '26': '패션 · 의류 브랜드',
  '3': '뷰티 · 코스메틱',
  '44': '뷰티 · 코스메틱',
  '11': '디지털 · 전자제품',
  '28': '디지털 · 전자제품',
  '31': '카페 · 베이커리 · 식품',
}

export const categoryToNiceClasses: Record<string, string[]> = (() => {
  const map: Record<string, Set<string>> = {}
  for (const [code, category] of Object.entries(niceToCategoryMap)) {
    if (!map[category]) map[category] = new Set()
    map[category].add(code)
  }
  const result: Record<string, string[]> = {}
  for (const [category, codes] of Object.entries(map)) {
    result[category] = [...codes]
  }
  return result
})()

export function resolveCategories(niceClass: string | null | undefined): string[] {
  if (!niceClass) return ['기타']
  const classes = niceClass.split('|').map(c => c.trim())
  const seen = new Set<string>()
  const result: string[] = []
  for (const cls of classes) {
    const cat = niceToCategoryMap[cls]
    if (cat && !seen.has(cat)) {
      seen.add(cat)
      result.push(cat)
    }
  }
  return result.length > 0 ? result : ['기타']
}
