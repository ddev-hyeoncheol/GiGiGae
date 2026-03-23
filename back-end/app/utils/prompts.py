"""LLM 프롬프트 템플릿 및 빌더 함수"""

BRAND_SYSTEM_PROMPT = (
    "너는 브랜드 네이밍 전문가야. "
    "사용자의 아이디어를 바탕으로 창의적인 브랜드명을 추천하고, "
    "각 후보에 대해 짧은 슬로건을 명사형으로 작성하고, "
    "형용사형 특성 태그 2~3개를 붙여. "
    "예: 감각적인, 친근한, 혁신적인.\n"
    "영문 브랜드는 영문 그대로, 한글 브랜드는 한글 그대로 작성해. "
    "예: Brandium, NameScape, 솜솜, 푸른달."
)

DOMAIN_SYSTEM_PROMPT = (
    "너는 도메인 네이밍 전문가야. "
    "브랜드명을 기반으로 등록 가능성이 높은 도메인을 추천해. "
    ".com, .kr, .io, .co 등 다양한 TLD를 활용하고, "
    "브랜드명의 변형(축약, 접미사 추가 등)도 제안해. "
    "추천 이유는 한 문장으로 간결하게 작성해."
)


def build_brand_user_prompt(
    brand_idea: str,
    brand_category: str | None = None,
    count: int = 5,
    exclude: list[str] | None = None,
) -> str:
    """브랜드 추천 요청용 User Prompt 생성"""
    prompt = f"아이디어: {brand_idea}\n"
    if brand_category:
        prompt += f"산업: {brand_category}\n"
    prompt += f"\n" f"브랜드명 {count}개를 추천해."
    if exclude:
        prompt += f"\n\n다음 브랜드명은 이미 추천했으니 제외해: {', '.join(exclude)}"
    return prompt


def build_domain_user_prompt(
    brand_name: str, count: int = 6, exclude: list[str] | None = None
) -> str:
    """도메인 추천 요청용 User Prompt 생성"""
    prompt = (
        f"브랜드명: {brand_name}\n\n "
        f"이 브랜드에 어울리는 도메인을 {count}개 추천해."
    )
    if exclude:
        prompt += f"\n\n다음 도메인은 이미 추천했으니 제외해: {', '.join(exclude)}"
    return prompt
