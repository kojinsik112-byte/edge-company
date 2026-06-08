"""Imagen (Google) 어댑터 — 포토리얼리즘 1순위. 제품/공간 연출샷.

GOOGLE_API_KEY 사용. 모델명은 IMAGEN_MODEL 로 오버라이드 가능.
"""
from __future__ import annotations

import base64
import os
from pathlib import Path

import requests

from .base import ImageAdapter, ImageRequest, ImageResult


class ImagenAdapter(ImageAdapter):
    name = "imagen"

    def _run(self, req: ImageRequest, outdir: Path) -> ImageResult:
        model = os.environ.get("IMAGEN_MODEL", "imagen-4.0-ultra-generate-001")
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:predict?key={self.api_key}"
        )
        body = {
            "instances": [{"prompt": req.prompt}],
            "parameters": {
                "sampleCount": req.n,
                "aspectRatio": _aspect(req.width, req.height),
            },
        }
        resp = requests.post(url, json=body, timeout=120)
        resp.raise_for_status()
        payload = resp.json()

        paths: list[str] = []
        for i, pred in enumerate(payload.get("predictions", [])):
            blob = pred.get("bytesBase64Encoded") or pred.get("image")
            if blob:
                out = outdir / f"{req.slug()}_imagen_{i}.png"
                out.write_bytes(base64.b64decode(blob))
                paths.append(str(out))

        if not paths:
            return self._dry_run(req, outdir)
        return ImageResult(paths=paths, adapter=self.name)


def _aspect(w: int, h: int) -> str:
    ratio = w / h if h else 1
    if ratio > 1.4:
        return "16:9"
    if ratio < 0.7:
        return "9:16"
    if ratio < 0.95:
        return "3:4"
    if ratio > 1.05:
        return "4:3"
    return "1:1"
