"""OpenAI (GPT-image) 어댑터 — "그냥 AI(챗GPT)로" 이미지 생성.

OPENAI_API_KEY 사용. 인물 모델·거실 연출·무드컷·한글 배너를 AI로 생성.
ref_images가 있으면 편집(images/edits), 없으면 생성(images/generations).
※ 제품 '본체'는 실물/LoRA 권장 (AI는 없는 제품을 지어냄). 배경·인물·연출에 강함.
"""
from __future__ import annotations

import base64
import os
from pathlib import Path

import requests

from .base import ImageAdapter, ImageRequest, ImageResult


class OpenAIImageAdapter(ImageAdapter):
    name = "openai"

    def _run(self, req: ImageRequest, outdir: Path) -> ImageResult:
        model = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-1")
        size = _size(req.width, req.height)
        headers = {"Authorization": f"Bearer {self.api_key}"}

        if req.ref_images:
            files = [("image[]", (Path(p).name, open(p, "rb"), "image/png")) for p in req.ref_images[:4]]
            data = {"model": model, "prompt": req.prompt, "size": size, "n": str(req.n)}
            resp = requests.post(
                "https://api.openai.com/v1/images/edits",
                headers=headers, data=data, files=files, timeout=180,
            )
            for _, f in files:
                f[1].close()
        else:
            body = {"model": model, "prompt": req.prompt, "size": size,
                    "n": req.n, "quality": os.environ.get("OPENAI_IMAGE_QUALITY", "high")}
            resp = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers, json=body, timeout=180,
            )

        resp.raise_for_status()
        payload = resp.json()
        paths: list[str] = []
        for i, item in enumerate(payload.get("data", [])):
            b64 = item.get("b64_json")
            if b64:
                out = outdir / f"{req.slug()}_openai_{i}.png"
                out.write_bytes(base64.b64decode(b64))
                paths.append(str(out))
        if not paths:
            return self._dry_run(req, outdir)
        return ImageResult(paths=paths, adapter=self.name)


def _size(w: int, h: int) -> str:
    ratio = w / h if h else 1
    if ratio > 1.2:
        return "1536x1024"
    if ratio < 0.83:
        return "1024x1536"
    return "1024x1024"
