"""FASHN.ai 어댑터 — 라이프스타일 착장/모델 컷 (조명·실링팬에선 보조 역할).

FASHN_API_KEY 사용. extra={"model_image": ..., "garment_image": ...} 로 입력.
조명 제품에선 '거실에 사람이 있는 연출샷' 정도로 활용.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

import requests

from .base import ImageAdapter, ImageRequest, ImageResult


class FashnAdapter(ImageAdapter):
    name = "fashn"

    def _run(self, req: ImageRequest, outdir: Path) -> ImageResult:
        base = os.environ.get("FASHN_URL", "https://api.fashn.ai/v1")
        headers = {"Authorization": f"Bearer {self.api_key}"}
        body = {
            "model_name": "tryon-v1.6",
            "inputs": {
                "model_image": req.extra.get("model_image"),
                "garment_image": req.extra.get("garment_image") or (req.ref_images[0] if req.ref_images else None),
            },
        }
        run = requests.post(f"{base}/run", json=body, headers=headers, timeout=60)
        run.raise_for_status()
        job_id = run.json().get("id")

        # 폴링
        for _ in range(30):
            time.sleep(3)
            st = requests.get(f"{base}/status/{job_id}", headers=headers, timeout=60)
            st.raise_for_status()
            data = st.json()
            if data.get("status") == "completed":
                paths = []
                for i, url in enumerate(data.get("output", [])):
                    blob = _download(url)
                    if blob:
                        out = outdir / f"{req.slug()}_fashn_{i}.png"
                        out.write_bytes(blob)
                        paths.append(str(out))
                return ImageResult(paths=paths or [], adapter=self.name) if paths else self._dry_run(req, outdir)
            if data.get("status") in {"failed", "error"}:
                break
        return self._dry_run(req, outdir)


def _download(url: str | None) -> bytes | None:
    if not url:
        return None
    try:
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        return r.content
    except Exception:
        return None
