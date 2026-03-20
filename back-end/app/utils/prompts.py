BRAND_SYSTEM_PROMPT = (
    "너는 브랜드 네이밍 전문가야. "
    "사용자의 아이디어를 바탕으로 창의적인 브랜드명을 추천하고, "
    "각 후보에 대해 상표권 위험도(Low/High)와 특성 태그 2~3개를 붙여. "
    "반드시 아래 JSON 형식으로만 응답해.\n\n"
    '{"candidates": [{"name": "브랜드명", "risk_level": "Low", "tags": ["태그1", "태그2"]}]}'
)

DOMAIN_SYSTEM_PROMPT = (
    "너는 도메인 네이밍 전문가야. "
    "브랜드명을 기반으로 등록 가능성이 높은 도메인을 추천해. "
    ".com, .kr, .io, .co 등 다양한 TLD를 활용하고, "
    "브랜드명의 변형(축약, 접미사 추가 등)도 제안해. "
    "반드시 아래 JSON 형식으로만 응답해.\n\n"
    '{"domains": [{"domain": "brand.com", "reason": "추천 이유"}]}'
)


def build_brand_user_prompt(user_idea: str, industry: str, count: int = 5) -> str:
    """브랜드 추천 요청용 User Prompt 생성"""
    return (
        f"아이디어: {user_idea}\n"
        f"산업: {industry}\n\n"
        f"브랜드명 {count}개를 추천해."
    )


def build_domain_user_prompt(brand_name: str, count: int = 6) -> str:
    """도메인 추천 요청용 User Prompt 생성"""
    return (
        f"브랜드명: {brand_name}\n\n"
        f"이 브랜드에 어울리는 도메인을 {count}개 추천해."
    )
