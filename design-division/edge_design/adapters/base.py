"""어댑터 공통 인터페이스.

모든 이미지 모델(Imagen/Gemini/Flux/Ideogram/FASHN/Claid)은 이 인터페이스를 구현한다.
이렇게 감싸두면 '레알 마드리드 선수'를 자유롭게 갈아끼울 수 있다.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ImageRequest:
    """이미지 한 컷 요청."""

    prompt: str
    task: str = "scene"            # scene | edit | text_banner | cleanup | tryon
    ref_images: list[str] = field(default_factory=list)  # 참고/입력 이미지 경로
    width: int = 1024
    height: int = 1024
    n: int = 1
    extra: dict = field(default_factory=dict)

    def slug(self) -> str:
        h = hashlib.sha1(f"{self.task}:{self.prompt}".encode()).hexdigest()[:8]
        return f"{self.task}_{h}"


@dataclass
class ImageResult:
    paths: list[str]
    adapter: str
    dry_run: bool = False
    meta: dict = field(default_factory=dict)


class ImageAdapter:
    """이미지 어댑터 베이스. 하위 클래스는 name 과 _run 을 구현한다."""

    name: str = "base"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    def available(self) -> bool:
        return bool(self.api_key)

    def run(self, req: ImageRequest, outdir: Path) -> ImageResult:
        outdir.mkdir(parents=True, exist_ok=True)
        if not self.available():
            return self._dry_run(req, outdir)
        return self._run(req, outdir)

    # 하위 클래스 구현부 ----------------------------------------------------
    def _run(self, req: ImageRequest, outdir: Path) -> ImageResult:  # pragma: no cover
        raise NotImplementedError

    # 드라이런: 키 없이도 파이프라인이 끝까지 돌도록 placeholder PNG 생성 ----
    def _dry_run(self, req: ImageRequest, outdir: Path) -> ImageResult:
        path = outdir / f"{req.slug()}_{self.name}.png"
        _placeholder_png(path, req.width, req.height, f"[{self.name}] {req.task}\n{req.prompt[:60]}")
        return ImageResult(paths=[str(path)], adapter=self.name, dry_run=True)


def _placeholder_png(path: Path, w: int, h: int, label: str) -> None:
    """키가 없을 때 자리표시용 이미지. 실제 호출 시엔 쓰이지 않는다."""
    try:
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (w, h), (28, 30, 38))
        d = ImageDraw.Draw(img)
        d.rectangle([8, 8, w - 8, h - 8], outline=(90, 100, 120), width=3)
        y = 20
        for line in label.split("\n"):
            d.text((24, y), line, fill=(200, 210, 230))
            y += 18
        img.save(path)
    except Exception:
        path.write_bytes(b"")
