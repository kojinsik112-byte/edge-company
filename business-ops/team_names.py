#!/usr/bin/env python3
"""팀 한글명 사전 — 관제실·보고서에서 팀을 한글로 보이게.

회장 지시: 팀명을 한글로 적고, 하는 일을 실시간으로 보이게.
영문 키(파일명/내부식별) → 한글 팀명. 역할 한 줄은 scorecard.csv 의 role 사용.
"""
TEAM_KR = {
    # 🔍 리서치
    "scout": "정찰·벤치마킹팀", "seo": "네이버SEO팀", "review_miner": "리뷰인사이트팀", "persona": "페르소나팀",
    # 💡 크리에이티브
    "creative_director": "크리에이티브총괄", "art_director": "아트디렉션팀",
    # ✍️ 기획·카피
    "planner": "상세기획팀", "writer": "카피라이팅팀", "cro": "전환최적화팀",
    # 🎨 디자인
    "designer": "디자인팀", "infographic": "인포그래픽팀", "photo_studio": "제품촬영팀",
    "interior": "공간연출팀", "cgi_3d": "3D·CGI팀", "motion": "모션그래픽팀", "video": "영상팀",
    # 🤖 AI
    "prompt_engineer": "프롬프트엔지니어팀", "model_trainer": "LoRA학습팀", "ai_ops": "AI옵스팀", "innovation": "신기술도입팀",
    # 🛡️ 품질·법무
    "auditor": "검수팀", "legal": "법무팀", "visual_qa": "비주얼QA팀",
    # 🚀 운영·성과
    "operator": "네이버등록팀", "analytics": "성과분석팀", "experiment_lab": "AB실험팀",
    # 📊 전략·인텔리전스
    "competitive_intel": "경쟁정찰팀", "product_strategy": "상품전략팀", "pricing": "가격전략팀", "brand_intel": "자사분석팀",
    # 🔗 커머스
    "ecosystem": "생태계·크로스셀팀",
    # 📦 경영·운영
    "inventory": "재고관리팀", "barcode": "바코드팀", "supervisor": "본부감독팀",
    # 📣 마케팅
    "growth": "광고그로스팀", "thumbnail": "썸네일팀", "influencer": "체험단·인플루언서팀", "cs": "고객응대팀",
    # 💰 경영지원
    "finance": "재무·정산팀",
    # 📹 콘텐츠·소셜
    "content_director": "콘텐츠총괄", "social_trends": "소셜트렌드팀", "publisher": "멀티발행팀",
    "community_manager": "SNS운영팀", "shorts_writer": "숏폼대본팀", "shoot_director": "촬영디렉팅팀", "caption_writer": "캡션팀",
    # 🧠 조직개발
    "pmo": "성과관리(PMO)팀", "team_coach": "팀코치",
    # 💡 조명사업
    "lighting_designer": "조명설계팀", "electrical_contractor": "전기공사팀", "lighting_sales": "조명영업팀",
    "lighting_sourcing": "조명소싱팀", "lighting_estimator": "조명견적팀", "lighting_pm": "조명현장PM팀",
    # 🏠 입주주관사
    "movein_consultant": "입주상담팀", "movein_partnership": "건설사제휴팀", "movein_funnel": "입주깔때기팀",
    "movein_event": "입주행사팀", "movein_data": "입주데이터팀", "movein_cs": "입주민CS팀",
    # 🪟 엣지리브커튼
    "curtain_designer": "커튼디자인팀", "curtain_measure": "커튼실측팀", "curtain_sourcing": "커튼소싱팀",
    "curtain_sales": "커튼영업팀", "curtain_install": "커튼시공팀", "curtain_estimator": "커튼견적팀",
    # 🌀 아크로
    "acro_rnd": "아크로R&D팀", "acro_production": "아크로생산팀", "acro_sourcing": "아크로소싱팀",
    "acro_certification": "아크로인증팀", "acro_sales": "아크로영업팀", "acro_logistics": "아크로물류팀",
    # 📡 채널
    "instagram_ops": "인스타운영팀", "youtube_ops": "유튜브운영팀", "tiktok_ops": "틱톡운영팀",
    "naver_ops": "네이버운영팀", "buffer_ops": "버퍼발행팀",
}


def kr(team: str) -> str:
    """영문 키 → 한글 팀명(없으면 키 그대로)."""
    return TEAM_KR.get(team, team)
