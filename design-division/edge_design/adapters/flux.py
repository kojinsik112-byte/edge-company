"""Flux (Black Forest Labs) 어댑터 — 워크호스 생성/편집. fal.ai 경유.

FAL_KEY 사용. 브랜드 전속 모델/제품 일관성을 위해 LoRA 학습 결과를
FLUX_MODEL_ID 로 지정해 재사용할 수 있다.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

import requests

from .base import ImageAdapter, ImageRequest, ImageResult


class FluxAdapter(ImageAdapter):
    name = "flux"

    def _run(self, req: ImageRequest, outdir: Path) -> ImageResult:
        model = os.environ.get("FLUX_MODEL_ID", "fal-ai/flux-pro/v1.1")
        url = f"https://fal.run/{model}"
        headers = {"Authorization": f"Key {self.api_key}"}
        body = {
            "prompt": req.prompt,
            "image_size": {"width": req.width, "height": req.height},
            "num_images": req.n,
        }
        if req.ref_images:
            body["image_url"] = _to_data_uri(req.ref_images[0])

        resp = requests.post(url, json=body, headers=headers, timeout=180)
        resp.raise_for_status()
        payload = resp.json()

        paths: list[str] = []
        for i, img in enumerate(payload.get("images", [])):
            blob = _download(img.get("url"))
            if blob:
                out = outdir / f"{req.slug()}_flux_{i}.png"
                out.write_bytes(blob)
                paths.append(str(out))

        if not paths:
            return self._dry_run(req, outdir)
        return ImageResult(paths=paths, adapter=self.name)


def _to_data_uri(path: str) -> str:
    import base64
    data = Path(path).read_bytes()
    return "data:image/png;base64," + base64.b64encode(data).decode()


def _download(url: str | None, retries: int = 3) -> bytes | None:
    if not url:
        return None
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=120)
            r.raise_for_status()
            return r.content
        except Exception:
            if attempt == retries - 1:
                return None
            time.sleep(2 ** attempt)
    return None
