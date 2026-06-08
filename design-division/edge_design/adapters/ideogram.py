"""Ideogram 어댑터 — 이미지 안에 정확한 '한글 카피'를 박을 때 1순위 (헤드라인 배너).

IDEOGRAM_API_KEY 사용.
"""
from __future__ import annotations

import os
from pathlib import Path

import requests

from .base import ImageAdapter, ImageRequest, ImageResult


class IdeogramAdapter(ImageAdapter):
    name = "ideogram"

    def _run(self, req: ImageRequest, outdir: Path) -> ImageResult:
        url = os.environ.get("IDEOGRAM_URL", "https://api.ideogram.ai/v1/ideogram-v3/generate")
        headers = {"Api-Key": self.api_key}
        body = {
            "prompt": req.prompt,
            "aspect_ratio": _aspect(req.width, req.height),
            "rendering_speed": "QUALITY",
            "num_images": req.n,
        }
        resp = requests.post(url, json=body, headers=headers, timeout=120)
        resp.raise_for_status()
        payload = resp.json()

        paths: list[str] = []
        for i, item in enumerate(payload.get("data", [])):
            blob = _download(item.get("url"))
            if blob:
                out = outdir / f"{req.slug()}_ideogram_{i}.png"
                out.write_bytes(blob)
                paths.append(str(out))

        if not paths:
            return self._dry_run(req, outdir)
        return ImageResult(paths=paths, adapter=self.name)


def _aspect(w: int, h: int) -> str:
    ratio = w / h if h else 1
    if ratio > 1.4:
        return "16x9"
    if ratio < 0.7:
        return "9x16"
    if ratio < 0.95:
        return "3x4"
    if ratio > 1.05:
        return "4x3"
    return "1x1"


def _download(url: str | None) -> bytes | None:
    if not url:
        return None
    try:
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        return r.content
    except Exception:
        return None
