"""LLM 프롬프트 템플릿 및 빌더 함수"""

BRAND_SYSTEM_PROMPT = (
    "너는 브랜드 네이밍 전문가야. "
    "사용자의 아이디어를 바탕으로 창의적인 브랜드명을 추천하고, "
    "보통 명사의 사용을 최소화하고, "
    "각 후보에 대해 짧은 슬로건을 명사형으로 작성하고, "
    "형용사형 특성 태그 2~3개를 붙여. "
    "예: 감각적인, 친근한, 혁신적인.\n"
    "영문 브랜드는 영문 그대로, 한글 브랜드는 한글 그대로 작성해. "
    "예: Brandium, NameScape, 솜솜, 푸른달."
)

DOMAIN_SYSTEM_PROMPT = (
    "브랜드명으로 도메인 중간 이름만 추천해. TLD(.com 등)는 붙이지 마. "
    "좋은 예: purebrew, getpurebrew, purebrewco. "
    "변형(축약, 접두사/접미사)도 포함하고, 추천 이유를 한 줄로 작성해."
)


def build_brand_user_prompt(
    brand_idea: str,
    brand_category: list[str] | None = None,
    brand_tone: list[str] | None = None,
    count: int = 6,
    exclude: list[str] | None = None,
) -> str:
    """브랜드 추천 요청용 User Prompt 생성"""
    prompt = f"아이디어: {brand_idea}\n"
    if brand_category:
        prompt += f"산업: {', '.join(brand_category)}\n"
    if brand_tone:
        prompt += f"브랜드 톤: {', '.join(brand_tone)}\n"
    prompt += f"\n브랜드명 {count}개를 추천해."
    if exclude:
        prompt += f"\n\n다음 브랜드명은 이미 추천했으니 제외해: {', '.join(exclude)}"
    return prompt


def build_domain_user_prompt(
    brand_name: str, count: int = 10, exclude: list[str] | None = None
) -> str:
    """도메인 추천 요청용 User Prompt 생성"""
    prompt = (
        f"브랜드명: {brand_name}\n\n"
        f"이 브랜드에 어울리는 도메인 중간 이름(TLD 제외)을 {count}개 추천해. "
        f"예: purebrew, getpurebrew (TLD 없이)"
    )
    if exclude:
        prompt += f"\n\n다음 도메인은 이미 추천했으니 제외해: {', '.join(exclude)}"
    return prompt
