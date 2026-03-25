<script setup lang="ts">
  import { computed } from 'vue'
  import { useWizardStore } from '@/stores/wizard'
  import { useRouter } from 'vue-router'
  import { useTrademarkChecklist } from '@/composables/useTrademarkChecklist'
  import PageHeader from '@/components/PageHeader.vue'
  import NavButtons from '@/components/NavButtons.vue'

  const wizard = useWizardStore()
  const router = useRouter()
  const result = wizard.trademarkResult ?? wizard.selectedBrand?.trademark ?? null

  const { items } = useTrademarkChecklist(
    computed(() => result),
    computed(() => wizard.imageSearchResult),
    computed(() => wizard.brandCategory),
  )

  function riskClass(risk: string) {
    switch (risk) {
      case 'Low': return 'risk-low'
      case 'Middle': return 'risk-middle'
      case 'High': return 'risk-high'
      default: return 'risk-unchecked'
    }
  }

  function riskLabel(risk: string) {
    switch (risk) {
      case 'Low': return '상표 안심'
      case 'Middle': return '상표 주의'
      case 'High': return '상표 위험'
      default: return '미확인'
    }
  }

  function riskDescription(risk: string) {
    switch (risk) {
      case 'Low': return '현재 기준으로는 충돌 가능성이 낮아 보여요.'
      case 'Middle': return '몇 가지는 괜찮지만, 비슷한 요소가 보여 한 번 더 확인하는 게 좋아요.'
      case 'High': return '동일하거나 매우 유사한 이름이 같은 분류에서 확인돼 주의가 필요해요.'
      default: return '브랜드명 기반 분석이 수행되지 않았어요.'
    }
  }

  function discountPercent(price: string | null, promoPrice: string | null): number {
    if (!price || !promoPrice) return 0
    const p = parseInt(price.replace(/[^0-9]/g, ''))
    const pp = parseInt(promoPrice.replace(/[^0-9]/g, ''))
    if (!p || !pp || p <= pp) return 0
    return Math.round((1 - pp / p) * 100)
  }

  function statusIcon(status: string) {
    switch (status) {
      case 'warning': return 'icon-warning'
      case 'caution': return 'icon-caution'
      default: return 'icon-safe'
    }
  }

  function statusBadge(status: string) {
    switch (status) {
      case 'warning': return 'badge-warning'
      case 'caution': return 'badge-caution'
      default: return 'badge-safe'
    }
  }

  function handleBack() {
    wizard.prevStep()
    router.push('/brand-domain')
  }

  function handleReset() {
    wizard.reset()
    router.push('/')
  }
</script>

<template>
  <div class="page">
    <main class="content">
      <PageHeader title="최종 가이드">
        기본 상표 검토와 도메인 확인이 끝났어요.<br/>이제 실제 상표 출원과 도메인 등록으로 이어갈 수 있어요.
      </PageHeader>

      <div class="content-body">
        <!-- CTA -->
        <div class="cta-section">
          <div class="cta-buttons">
            <a class="cta-card cta-card-primary" href="https://www.kipris.or.kr" target="_blank">
              <div class="cta-card-left">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </div>
              <div class="cta-card-content">
                <span class="cta-card-label">상표 출원하기</span>
                <span class="cta-card-sub">변리사 연계 출원 서비스</span>
              </div>
              <svg class="cta-external" width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6M15 3h6v6M10 14L21 3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </a>
            <a class="cta-card cta-card-primary" href="https://domain.nhn.com" target="_blank">
              <div class="cta-card-left">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/><path d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z" stroke="currentColor" stroke-width="2"/></svg>
              </div>
              <div class="cta-card-content">
                <span class="cta-card-label">도메인 등록하기</span>
                <span class="cta-card-sub">{{ wizard.selectedDomain?.domain_name ?? '도메인 검색' }}</span>
              </div>
              <svg class="cta-external" width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6M15 3h6v6M10 14L21 3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </a>
          </div>
        </div>

        <!-- 브랜드 정보 + 선택 도메인 (2열) -->
        <div class="summary-row">
          <div class="section-card surface">
            <div class="section-card-header">
              <h4 class="section-card-title">브랜드 정보</h4>
              <p class="section-card-sub text-muted">선택한 브랜드의 기본 정보예요.</p>
            </div>
            <div class="brand-row">
              <img v-if="wizard.logoPreview" :src="wizard.logoPreview" alt="브랜드 로고" class="brand-logo" />
              <div class="brand-info">
                <span class="report-brand-name">{{ wizard.selectedBrand?.brand_name }}</span>
                <p v-if="wizard.selectedBrand?.brand_description" class="report-brand-desc text-muted">{{ wizard.selectedBrand.brand_description }}</p>
                <p v-else class="report-brand-desc text-muted">직접 입력한 브랜드예요.</p>
                <div v-if="wizard.selectedBrand?.brand_tags?.length" class="report-tags">
                  <span v-for="tag in wizard.selectedBrand.brand_tags" :key="tag" class="report-tag">#{{ tag }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="section-card surface">
            <div class="section-card-header">
              <h4 class="section-card-title">도메인 정보</h4>
              <p class="section-card-sub text-muted">등록 가능 여부와 가격 정보예요.</p>
            </div>
            <div v-if="wizard.selectedDomain" class="report-domain-col">
              <div class="report-domain-name-row">
                <span class="report-domain-name">{{ wizard.selectedDomain.domain_name }}</span>
                <span class="badge-success">등록 가능</span>
              </div>
              <p v-if="wizard.selectedDomain.domain_reason" class="report-domain-reason text-muted">{{ wizard.selectedDomain.domain_reason }}</p>
              <div v-if="wizard.selectedDomain.price" class="report-domain-price-row">
                <template v-if="wizard.selectedDomain.promotion_price && wizard.selectedDomain.promotion_price !== wizard.selectedDomain.price">
                  <span class="price-original">연 {{ wizard.selectedDomain.price }}</span>
                  <span class="price-arrow">→</span>
                  <span class="price-promo">연 {{ wizard.selectedDomain.promotion_price }}</span>
                  <span class="price-discount">-{{ discountPercent(wizard.selectedDomain.price, wizard.selectedDomain.promotion_price) }}%</span>
                </template>
                <span v-else class="price-normal">연 {{ wizard.selectedDomain.price }}</span>
              </div>
            </div>
            <span v-else class="text-muted">도메인이 선택되지 않았어요.</span>
          </div>
        </div>

        <!-- 상표 분석 결과 -->
        <div class="section-card surface">
          <div class="section-card-header">
            <h4 class="section-card-title">상표 분석 결과</h4>
            <p class="section-card-sub text-muted">NameCraft가 6개 항목을 종합해서 등록 가능성을 판단했어요.</p>
          </div>
          <div v-if="result" class="risk-mini" :class="riskClass(result.risk)">
            <span class="risk-mini-badge" :class="riskClass(result.risk)">{{ riskLabel(result.risk) }}</span>
            <span class="risk-mini-text">{{ riskDescription(result.risk) }}</span>
          </div>
          <div class="review-badges">
            <div v-for="item in items" :key="item.id" class="review-badge" :class="item.disabled ? 'badge-disabled' : statusBadge(item.status)">
              <span class="review-badge-icon" :class="item.disabled ? 'icon-disabled' : statusIcon(item.status)">
                <svg v-if="item.disabled" width="14" height="14" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="2"/><path d="M6 10h8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
                <svg v-else-if="item.status === 'warning'" width="14" height="14" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="2"/><path d="M7 7l6 6M13 7l-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
                <svg v-else-if="item.status === 'caution'" width="14" height="14" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="2"/><path d="M6 10h8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
                <svg v-else width="14" height="14" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="2"/><path d="M6 10l3 3 5-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </span>
              <span class="review-badge-label">{{ item.label }}</span>
              <span class="review-badge-status">{{ item.statusLabel }}</span>
            </div>
          </div>
          <p class="report-disclaimer text-muted"><span class="disclaimer-icon">i</span> 본 분석은 특허청 공개 데이터 기반의 참고 자료예요. 최종 출원 여부는 변리사 검토를 권장해요.</p>
        </div>

        <!-- NHN Cloud 가이드 -->
        <div class="section-card surface">
          <div class="section-card-header">
            <h4 class="section-card-title">이제 브랜드를 실제로 시작해볼까요</h4>
            <p class="section-card-sub text-muted">NHN Cloud를 이용하면 홈페이지 배포, 메일 설정, 보안까지 한 곳에서 해결할 수 있어요.</p>
          </div>
          <div class="nhn-steps">
            <div class="nhn-step">
              <div class="nhn-step-number">01</div>
              <div class="nhn-step-content">
                <h5 class="nhn-step-title">도메인 연결 준비</h5>
                <p class="nhn-step-desc text-muted">등록한 도메인을 NHN Cloud DNS 서비스에 등록하고, 서버 IP 또는 로드밸런서에 연결해요.</p>
                <span class="nhn-step-path text-muted">→ NHN Cloud > DNS Plus > 레코드 추가</span>
              </div>
            </div>
            <div class="nhn-step">
              <div class="nhn-step-number">02</div>
              <div class="nhn-step-content">
                <h5 class="nhn-step-title">홈페이지 또는 스토어 배포</h5>
                <p class="nhn-step-desc text-muted">Object Storage 정적 웹사이트 기능으로 랜딩 페이지를, Compute 인스턴스로 웹 서버를 띄울 수 있어요.</p>
                <span class="nhn-step-path text-muted">→ Object Storage > 컨테이너 > 정적 웹사이트 설정</span>
              </div>
            </div>
            <div class="nhn-step">
              <div class="nhn-step-number">03</div>
              <div class="nhn-step-content">
                <h5 class="nhn-step-title">메일 · 운영 도구 설정</h5>
                <p class="nhn-step-desc text-muted">NHN Cloud Email 서비스에 메일 도메인을 등록하고, 브랜드 도메인 기반 이메일 발송 환경을 만들어요.</p>
                <span class="nhn-step-path text-muted">→ Notification > Email > 메일 도메인 관리</span>
              </div>
            </div>
            <div class="nhn-step">
              <div class="nhn-step-number">04</div>
              <div class="nhn-step-content">
                <h5 class="nhn-step-title">오픈 전 체크</h5>
                <p class="nhn-step-desc text-muted">SSL 인증서(HTTPS)를 적용하고, 실제 사용자 기기에서 주소 접속과 속도를 확인해 보세요.</p>
                <span class="nhn-step-path text-muted">→ Certificate Manager > 인증서 발급</span>
              </div>
            </div>
          </div>
        </div>

        <NavButtons
          back-label="이전으로"
          next-label="처음으로"
          @next="handleReset"
          @back="handleBack"
        />
      </div>
    </main>
  </div>
</template>

<style scoped>
  .page { display: flex; flex-direction: column; }
  .content { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 1rem 1rem 2rem; gap: 1rem; }
  .content-body { width: 100%; max-width: 720px; display: flex; flex-direction: column; gap: 1rem; }

  /* CTA */
  .cta-section { display: flex; flex-direction: column; align-items: center; gap: 0.75rem; }
  .cta-buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; width: 100%; }
  .cta-card {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 1rem 1.25rem; border-radius: var(--radius);
    text-decoration: none; cursor: pointer; transition: all 0.2s ease;
  }
  .cta-card-primary {
    background: var(--color-primary); color: #fff;
    box-shadow: 0 4px 12px color-mix(in srgb, var(--color-primary) 30%, transparent);
  }
  .cta-card-primary:hover { box-shadow: 0 6px 20px color-mix(in srgb, var(--color-primary) 40%, transparent); transform: translateY(-2px); }
  .cta-card-primary .cta-card-sub { color: rgba(255, 255, 255, 0.7); }
  .cta-card-left { display: flex; align-items: center; flex-shrink: 0; }
  .cta-card-content { display: flex; flex-direction: column; gap: 0.15rem; flex: 1; }
  .cta-card-label { font-size: 0.95rem; font-weight: 700; }
  .cta-card-sub { font-size: 0.8rem; }
  .cta-external { flex-shrink: 0; opacity: 0.5; }
  .cta-card:hover .cta-external { opacity: 1; }

  /* 2열 레이아웃 */
  .summary-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }

  /* 섹션 카드 */
  .section-card { padding: 1.5rem; border-radius: var(--radius); display: flex; flex-direction: column; gap: 0.75rem; }
  .section-card-header { display: flex; flex-direction: column; gap: 0.2rem; padding-bottom: 0.75rem; margin-bottom: 0.25rem; border-bottom: 1px solid var(--color-border); }
  .section-card-title { font-size: 1.05rem; font-weight: 800; margin: 0; color: var(--color-text); }
  .section-card-sub { font-size: 0.8rem; margin: 0; }
  .report-disclaimer { font-size: 0.75rem; margin: 0.75rem 0 0; padding-top: 0.75rem; border-top: 1px solid var(--color-border); display: flex; align-items: flex-start; gap: 0.4rem; }
  .disclaimer-icon { display: inline-flex; align-items: center; justify-content: center; width: 0.85rem; height: 0.85rem; border-radius: 50%; background: var(--color-text-muted); color: var(--color-surface); font-size: 0.5rem; font-weight: 700; font-style: italic; flex-shrink: 0; margin-top: 0.05rem; }

  /* 브랜드 */
  .brand-row { display: flex; gap: 1rem; align-items: flex-start; }
  .brand-logo { width: 80px; height: 80px; object-fit: contain; border-radius: var(--radius); border: 1px solid var(--color-border); background: #fff; flex-shrink: 0; }
  .brand-info { flex: 1; display: flex; flex-direction: column; gap: 0.4rem; }
  .report-brand-name { font-size: 1.5rem; font-weight: 800; }
  .report-brand-desc { font-size: 0.85rem; margin: 0; line-height: 1.5; }
  .report-tags { display: flex; flex-wrap: wrap; gap: 0.3rem; }
  .report-tag { font-size: 0.7rem; font-weight: 500; padding: 0.15rem 0.45rem; border-radius: 999px; background: color-mix(in srgb, var(--color-primary) 8%, transparent); color: var(--color-primary); }

  /* 도메인 */
  .report-domain-col { display: flex; flex-direction: column; gap: 0.5rem; }
  .report-domain-name-row { display: flex; align-items: center; gap: 0.5rem; }
  .report-domain-price-row { display: flex; align-items: center; gap: 0.4rem; }
  .price-discount { font-size: 0.7rem; font-weight: 700; padding: 0.1rem 0.35rem; border-radius: 4px; background: var(--color-danger); color: #fff; }
  .report-domain-name { font-size: 1.1rem; font-weight: 700; }
  .report-domain-reason { font-size: 0.85rem; margin: 0; line-height: 1.5; }
  .price-arrow { font-size: 0.8rem; color: var(--color-text-muted); }
  .price-original { font-size: 0.8rem; color: var(--color-text-muted); text-decoration: line-through; }
  .price-promo { font-size: 0.95rem; font-weight: 700; color: var(--color-danger); }
  .price-normal { font-size: 0.9rem; font-weight: 600; color: var(--color-text-muted); }

  /* 위험도 미니 */
  .risk-mini {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 0.75rem; border-left: 3px solid;
  }
  .risk-mini.risk-low { background: color-mix(in srgb, var(--color-success) 6%, var(--color-bg)); border-left-color: var(--color-success); }
  .risk-mini.risk-middle { background: color-mix(in srgb, var(--color-accent) 6%, var(--color-bg)); border-left-color: var(--color-accent); }
  .risk-mini.risk-high { background: color-mix(in srgb, var(--color-danger) 6%, var(--color-bg)); border-left-color: var(--color-danger); }
  .risk-mini.risk-unchecked { background: var(--color-bg); border-left-color: var(--color-border); }
  .risk-mini-badge { font-size: 0.7rem; font-weight: 700; padding: 0.2rem 0.55rem; border-radius: 999px; color: #fff; white-space: nowrap; flex-shrink: 0; }
  .risk-mini-badge.risk-low { background: var(--color-success); }
  .risk-mini-badge.risk-middle { background: var(--color-accent); }
  .risk-mini-badge.risk-high { background: var(--color-danger); }
  .risk-mini-badge.risk-unchecked { background: var(--color-border); color: var(--color-text); }
  .risk-mini-text { font-size: 0.85rem; color: var(--color-text); line-height: 1.4; }

  /* 검토 배지 */
  .review-badges { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; }
  .review-badge {
    display: flex; align-items: center; gap: 0.35rem;
    padding: 0.6rem 0.75rem; border-radius: 8px; border: 1px solid var(--color-border); font-size: 0.8rem;
  }
  .review-badge.badge-safe { background: color-mix(in srgb, var(--color-success) 5%, var(--color-bg)); border-color: color-mix(in srgb, var(--color-success) 20%, var(--color-border)); }
  .review-badge.badge-caution { background: color-mix(in srgb, var(--color-accent) 5%, var(--color-bg)); border-color: color-mix(in srgb, var(--color-accent) 20%, var(--color-border)); }
  .review-badge.badge-warning { background: color-mix(in srgb, var(--color-danger) 5%, var(--color-bg)); border-color: color-mix(in srgb, var(--color-danger) 20%, var(--color-border)); }
  .badge-disabled { opacity: 0.45; background: var(--color-bg); }
  .review-badge-icon { flex-shrink: 0; display: flex; }
  .icon-warning { color: var(--color-danger); }
  .icon-caution { color: var(--color-accent); }
  .icon-safe { color: var(--color-success); }
  .icon-disabled { color: var(--color-border); }
  .review-badge-label { font-weight: 600; flex: 1; color: var(--color-text); }
  .review-badge-status { font-size: 0.7rem; font-weight: 600; color: var(--color-text-muted); white-space: nowrap; }

  /* NHN Cloud 가이드 */
  .nhn-steps { display: flex; flex-direction: column; gap: 0; position: relative; }
  .nhn-step {
    display: flex; gap: 1rem; padding: 1rem 0;
    border-bottom: 1px solid var(--color-border);
    position: relative;
  }
  .nhn-step:last-child { border-bottom: none; padding-bottom: 0; }
  .nhn-step:first-child { padding-top: 0; }
  .nhn-step-number {
    width: 2rem; height: 2rem; border-radius: 50%;
    background: var(--color-bg); border: 2px solid var(--color-border);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; font-weight: 700; color: var(--color-text-muted);
    flex-shrink: 0; margin-top: 0.1rem;
  }
  .nhn-step-content { flex: 1; display: flex; flex-direction: column; gap: 0.3rem; }
  .nhn-step-title { font-size: 0.95rem; font-weight: 700; margin: 0; color: var(--color-text); }
  .nhn-step-desc { font-size: 0.8rem; margin: 0; line-height: 1.5; }
  .nhn-step-path {
    font-size: 0.75rem; padding: 0.3rem 0.6rem;
    background: var(--color-bg); border-radius: 4px;
    display: inline-block; width: fit-content;
  }

  @media (max-width: 520px) {
    .summary-row { grid-template-columns: 1fr; }
    .cta-buttons { grid-template-columns: 1fr; }
    .review-badges { grid-template-columns: 1fr 1fr; }
  }
</style>
