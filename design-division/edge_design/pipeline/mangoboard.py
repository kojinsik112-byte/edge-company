"""망고보드(Mangoboard) 연동 — 조판 마감 100점 라인업.

망고보드는 공개 API가 없으므로(2026 기준), '완전 무인'이 아니라
**AI가 소재·수치·슬라이드 작업지시서까지 완벽히 만들어 망고보드에 꽂는** 방식으로 붙인다.

산출물(output/<product>/mangoboard/):
  - 작업지시서.md   : 슬라이드별 구성·카피·이미지·인포그래픽 수치 (사람/디자이너가 그대로 조립)
  - manifest.json   : 망고보드 AI 상세페이지 / Chat망고 입력용 구조화 데이터
  - assets/         : 슬라이드에 꽂을 AI 생성 이미지(파이프라인 images에서 복사)

망고보드 자체 'AI 상세페이지' 서비스에 업로드할 때도 이 패키지가 그대로 입력이 된다.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from .brief import ProductBrief, Section


# 망고보드 템플릿 카테고리 추천(제품군 → 결)
def _template_category(brief: ProductBrief) -> str:
    if brief.is_fan:
        return "가전/인테리어 상세페이지 (감성 라이프스타일 + 스펙 인포그래픽)"
    if "스위치" in brief.category:
        return "전기/부자재 상세페이지 (기능·호환·설치 중심)"
    return "조명/인테리어 상세페이지 (무드 연출 + 스펙 인포그래픽)"


def _brand_kit(brief: ProductBrief) -> dict:
    """망고보드에서 통일할 브랜드 키트 (색/폰트 가이드)."""
    return {
        "primary_color": "#0F62FE",
        "ink": "#1C1E26",
        "accent_bg": "#0C0E14",
        "headline_font": "Pretendard Bold",
        "body_font": "Pretendard Regular",
        "mood": "정숙 · 무드 · 에너지 효율" if brief.is_fan else "무드 · 디밍 · 공간감",
    }


def export_pack(brief: ProductBrief, sections: list[Section], outdir: Path) -> Path:
    mb = outdir / "mangoboard"
    assets = mb / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    # 슬라이드 매니페스트 구성
    slides = []
    for i, sec in enumerate(sections, 1):
        asset_name = None
        if sec.image_path:
            src = Path(sec.image_path)
            if not src.is_absolute():
                src = outdir / src
            if src.exists():
                asset_name = f"slide{i:02d}_{sec.kind}.png"
                shutil.copy(src, assets / asset_name)
        slides.append(
            {
                "slide": i,
                "kind": sec.kind,
                "headline": sec.title,
                "copy": sec.body,
                "image_asset": f"assets/{asset_name}" if asset_name else None,
                "image_direction": sec.image_prompt,
                "infographic": sec.data.get("metrics") if sec.kind == "infographic" else None,
                "spec_table": sec.data.get("specs") if sec.kind == "spec" else None,
            }
        )

    manifest = {
        "product": brief.name,
        "brand": brief.brand,
        "template_category": _template_category(brief),
        "brand_kit": _brand_kit(brief),
        "chat_mango_seed": brief.benefits,  # Chat망고 카피 시드 키워드
        "slides": slides,
    }
    (mb / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (mb / "작업지시서.md").write_text(_to_markdown(brief, manifest), encoding="utf-8")
    print(f"[mangoboard] 작업 패키지 → {mb}")
    return mb


def _to_markdown(brief: ProductBrief, m: dict) -> str:
    bk = m["brand_kit"]
    lines = [
        f"# 망고보드 작업지시서 — {brief.brand} {brief.name}",
        "",
        f"- **추천 템플릿**: {m['template_category']}",
        f"- **브랜드 컬러**: 메인 {bk['primary_color']} / 강조배경 {bk['accent_bg']}",
        f"- **폰트**: 제목 {bk['headline_font']} / 본문 {bk['body_font']}",
        f"- **결(무드)**: {bk['mood']}",
        f"- **Chat망고 카피 시드**: {', '.join(m['chat_mango_seed'])}",
        "",
        "> 슬라이드 순서대로 망고보드 상세페이지 템플릿에 조립하세요. "
        "이미지는 `assets/` 의 AI 생성본을 사용하고, 카피는 아래를 그대로 쓰되 Chat망고로 다듬어도 됩니다.",
        "",
        "---",
        "",
    ]
    for s in m["slides"]:
        lines.append(f"## {s['slide']:02d}. [{s['kind']}] {s['headline']}")
        if s["copy"]:
            lines.append(f"- 카피: {s['copy']}")
        if s["image_asset"]:
            lines.append(f"- 이미지: `{s['image_asset']}`")
        elif s["image_direction"]:
            lines.append(f"- 이미지 연출(생성 지시): {s['image_direction']}")
        if s["infographic"]:
            nums = " / ".join(f"{x['label']} {x['value']}{x.get('unit','')}" for x in s["infographic"])
            lines.append(f"- 📊 인포그래픽 수치: {nums}")
        if s["spec_table"]:
            lines.append("- 스펙표:")
            for k, v in s["spec_table"].items():
                lines.append(f"  - {k}: {v}")
        lines.append("")
    return "\n".join(lines)
