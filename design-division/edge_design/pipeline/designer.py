"""Designer 단계 — 기획안(섹션 목록)을 만들고, 각 섹션의 이미지를 생성한다.

- ANTHROPIC_API_KEY 가 있으면 Claude(Planner+Writer)가 섹션 구성을 잡는다.
- 없으면 제품 카테고리에 맞는 견고한 기본 골격으로 폴백한다.
이미지는 registry 가 작업별 최강 어댑터로 생성한다.
"""
from __future__ import annotations

import json
from pathlib import Path

from ..config import Config
from ..adapters import build_registry, ImageRequest
from .brief import ProductBrief, Section


def plan_sections(brief: ProductBrief, cfg: Config) -> list[Section]:
    """기획안 = 상세페이지 섹션 목록. Claude 우선, 없으면 기본 골격."""
    if cfg.anthropic_api_key:
        try:
            return _plan_with_claude(brief, cfg)
        except Exception as exc:  # 네트워크/키 문제 시 폴백
            print(f"[planner] Claude 폴백 (사유: {exc})")
    return _default_plan(brief)


def _plan_with_claude(brief: ProductBrief, cfg: Config) -> list[Section]:
    import anthropic

    client = anthropic.Anthropic(api_key=cfg.anthropic_api_key)
    sys = (
        "너는 네이버 스마트스토어 상세페이지 기획·카피 총괄이다. "
        "잘 팔리는 상세페이지의 '구성·후킹·신뢰요소 패턴'을 적용하되 문구는 100% 오리지널로 쓴다. "
        "과대광고/표시광고법 위반 표현(최고, 100%, 유일 등 입증불가 표현)은 쓰지 않는다. "
        "제품 스펙(높이/풍량/소음/색온도/디밍/소비전력 등)은 인포그래픽으로 강조한다. "
        "결과는 반드시 JSON 배열로만 답한다."
    )
    user = (
        f"상품: {brief.name} / 카테고리: {brief.category} / 브랜드: {brief.brand}\n"
        f"타깃: {brief.target}\n혜택: {brief.benefits}\n스펙: {brief.specs}\n"
        f"강조수치: {brief.spec_visuals}\n참고(패턴만 분석): {brief.benchmarks}\n\n"
        "다음 형식의 섹션 6~9개를 JSON 배열로 만들어줘. 각 원소: "
        '{"kind": "hero|scene|feature|spec|infographic|trust|cta", '
        '"title": "", "body": "", "image_prompt": "영문 이미지 생성 프롬프트", '
        '"image_task": "scene|edit|text_banner", "data": {}}'
    )
    msg = client.messages.create(
        model=cfg.anthropic_model,
        max_tokens=4000,
        system=sys,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    text = text[text.find("[") : text.rfind("]") + 1]
    raw = json.loads(text)
    return [
        Section(
            kind=s.get("kind", "feature"),
            title=s.get("title", ""),
            body=s.get("body", ""),
            image_prompt=s.get("image_prompt", ""),
            image_task=s.get("image_task", "scene"),
            data=s.get("data", {}),
        )
        for s in raw
    ]


def _default_plan(brief: ProductBrief) -> list[Section]:
    """Claude 키가 없을 때의 견고한 기본 상세페이지 골격."""
    p = brief.name
    style = "modern Korean interior, soft natural light, photoreal, 4k product photography"
    sections = [
        Section("hero", brief.tagline or f"{p}", "",
                f"hero shot of {p}, {style}, centered, premium mood", "scene"),
        Section("scene", "공간에 더하는 분위기", "",
                f"{p} installed in a cozy living room, lifestyle scene, {style}", "scene"),
    ]
    if brief.is_fan:
        sections.append(Section(
            "infographic", "바람, 숫자로 증명합니다", "",
            "", "edit",
            data={"metrics": brief.spec_visuals or [
                {"label": "풍량", "value": "—", "unit": "m³/min"},
                {"label": "설치 높이", "value": "—", "unit": "mm"},
                {"label": "소음", "value": "—", "unit": "dB"},
            ]}))
    else:
        sections.append(Section(
            "infographic", "빛, 숫자로 증명합니다", "",
            "", "edit",
            data={"metrics": brief.spec_visuals or [
                {"label": "색온도", "value": "—", "unit": "K"},
                {"label": "소비전력", "value": "—", "unit": "W"},
                {"label": "디밍", "value": "—", "unit": "단계"},
            ]}))
    for b in (brief.benefits or ["디테일", "내구성", "설치 편의"])[:3]:
        sections.append(Section("feature", b, "",
                                f"close-up detail of {p} highlighting {b}, {style}", "scene"))
    sections.append(Section("spec", "상세 스펙", "", "", "scene", data={"specs": brief.specs}))
    sections.append(Section("trust", "믿고 쓰는 이유", "KC 인증 · A/S · 정품",
                            "", "scene"))
    sections.append(Section("cta", "지금 만나보세요", "", "", "scene"))
    return sections


def render_images(sections: list[Section], brief: ProductBrief, cfg: Config, outdir: Path) -> None:
    """각 섹션의 image_prompt 로 이미지를 생성해 section.image_path 에 채운다."""
    reg = build_registry(cfg)
    img_dir = outdir / "images"
    for i, sec in enumerate(sections):
        if not sec.image_prompt:
            continue
        req = ImageRequest(
            prompt=sec.image_prompt,
            task=sec.image_task,
            ref_images=brief.product_images[:1],
            width=1080,
            height=1080 if sec.kind != "hero" else 1350,
        )
        res = reg.render(req, img_dir)
        if res.paths:
            sec.image_path = res.paths[0]
            tag = "DRYRUN" if res.dry_run else res.adapter
            print(f"[designer] {i+1:>2}. {sec.kind:<11} → {tag}")
