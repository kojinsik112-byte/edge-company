"""Gemini (Google) 이미지 어댑터 — 합성/편집/일관성 강점 ('Nano Banana' 계열).

엔드포인트/모델명은 환경에 따라 다를 수 있으니 GEMINI_IMAGE_MODEL 로 오버라이드 가능.
키가 없으면 자동으로 드라이런된다.
"""
from __future__ import annotations

import base64
import os
from pathlib import Path

import requests

from .base import ImageAdapter, ImageRequest, ImageResult


class GeminiAdapter(ImageAdapter):
    name = "gemini"

    def _run(self, req: ImageRequest, outdir: Path) -> ImageResult:
        model = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-3-pro-image")
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={self.api_key}"
        )
        parts: list[dict] = [{"text": req.prompt}]
        for ref in req.ref_images:
            data = Path(ref).read_bytes()
            parts.append(
                {
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": base64.b64encode(data).decode(),
                    }
                }
            )

        resp = requests.post(
            url,
            json={"contents": [{"parts": parts}]},
            timeout=120,
        )
        resp.raise_for_status()
        payload = resp.json()

        paths: list[str] = []
        for i, cand in enumerate(payload.get("candidates", [])):
            for part in cand.get("content", {}).get("parts", []):
                blob = part.get("inline_data", {}).get("data")
                if blob:
                    out = outdir / f"{req.slug()}_gemini_{i}.png"
                    out.write_bytes(base64.b64decode(blob))
                    paths.append(str(out))

        if not paths:  # 모델이 텍스트만 반환한 경우 등
            return self._dry_run(req, outdir)
        return ImageResult(paths=paths, adapter=self.name)
