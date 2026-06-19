"""Claid.ai 어댑터 — 누끼/배경교체/4K 업스케일 (등록 규격 맞춤).

CLAID_API_KEY 사용. ref_images[0] 을 입력 이미지로 후처리한다.
"""
from __future__ import annotations

import os
from pathlib import Path

import requests

from .base import ImageAdapter, ImageRequest, ImageResult


class ClaidAdapter(ImageAdapter):
    name = "claid"

    def _run(self, req: ImageRequest, outdir: Path) -> ImageResult:
        if not req.ref_images:
            return self._dry_run(req, outdir)

        url = os.environ.get("CLAID_URL", "https://api.claid.ai/v1-ext/image/edit/upload")
        headers = {"Authorization": f"Bearer {self.api_key}"}
        operations = req.extra.get(
            "operations",
            {
                "background": {"remove": True},
                "resizing": {"width": req.width, "height": req.height, "fit": "bounds"},
                "restorations": {"upscale": "smart_enhance"},
            },
        )
        with open(req.ref_images[0], "rb") as f:
            resp = requests.post(
                url,
                headers=headers,
                files={"file": f},
                data={"data": str({"operations": operations})},
                timeout=180,
            )
        resp.raise_for_status()
        out_url = resp.json().get("data", {}).get("output", {}).get("tmp_url")
        blob = _download(out_url)
        if not blob:
            return self._dry_run(req, outdir)
        out = outdir / f"{req.slug()}_claid.png"
        out.write_bytes(blob)
        return ImageResult(paths=[str(out)], adapter=self.name)


def _download(url: str | None) -> bytes | None:
    if not url:
        return None
    try:
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        return r.content
    except Exception:
        return None
