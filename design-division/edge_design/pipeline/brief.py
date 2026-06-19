"""상품 브리프 — 회장이 던지는 '상품 + 스펙'을 담는 입력 모델.

아크로 조명/실링팬에 맞춰 스펙 시각화에 필요한 필드를 포함한다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Section:
    """상세페이지 한 섹션 (Planner 산출물)."""

    kind: str                       # hero | scene | spec | feature | infographic | trust | cta
    title: str = ""
    body: str = ""
    image_prompt: str = ""
    image_task: str = "scene"
    image_path: str | None = None
    data: dict = field(default_factory=dict)  # 인포그래픽용 수치 등


@dataclass
class ProductBrief:
    name: str
    category: str = "조명"          # 조명 | 실링팬 | 스위치 ...
    brand: str = "ARCO"
    tagline: str = ""
    target: str = ""
    benefits: list[str] = field(default_factory=list)
    specs: dict[str, str] = field(default_factory=dict)   # 표시용 스펙 (높이, 풍량, dB, 색온도...)
    spec_visuals: list[dict] = field(default_factory=list) # 인포그래픽으로 강조할 수치
    product_images: list[str] = field(default_factory=list)
    benchmarks: list[str] = field(default_factory=list)    # 참고(벤치마킹)할 상세페이지 URL
    notes: str = ""

    @property
    def is_fan(self) -> bool:
        return "팬" in self.category or "fan" in self.category.lower()


def load_brief(path: str | Path) -> ProductBrief:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    return ProductBrief(
        name=data.get("name", "제품"),
        category=data.get("category", "조명"),
        brand=data.get("brand", "ARCO"),
        tagline=data.get("tagline", ""),
        target=data.get("target", ""),
        benefits=data.get("benefits", []),
        specs=data.get("specs", {}),
        spec_visuals=data.get("spec_visuals", []),
        product_images=data.get("product_images", []),
        benchmarks=data.get("benchmarks", []),
        notes=data.get("notes", ""),
    )
