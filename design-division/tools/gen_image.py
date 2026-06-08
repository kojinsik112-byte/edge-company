#!/usr/bin/env python3
"""Gemini 2.5 Flash Image (Nano Banana)로 제품/연출 이미지 생성.

사용:
    python tools/gen_image.py "<영문 프롬프트>" <출력파일.png> [참조이미지.png]
참조이미지를 주면 그 제품을 유지한 채 새 장면을 만든다(제품 일관성).
"""
from __future__ import annotations
import base64, json, os, sys, mimetypes
from pathlib import Path
import urllib.request

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except Exception:
    pass

KEY = os.environ.get("GOOGLE_API_KEY", "").strip()
MODEL = "gemini-2.5-flash-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"


def gen(prompt: str, out: str, ref: str | None = None) -> None:
    if not KEY:
        raise SystemExit("GOOGLE_API_KEY 없음 (.env 확인)")
    parts = [{"text": prompt}]
    if ref and Path(ref).exists():
        mime = mimetypes.guess_type(ref)[0] or "image/png"
        data = base64.b64encode(Path(ref).read_bytes()).decode()
        parts.insert(0, {"inline_data": {"mime_type": mime, "data": data}})
    body = {"contents": [{"parts": parts}], "generationConfig": {"responseModalities": ["IMAGE"]}}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        res = json.load(r)
    cand = (res.get("candidates") or [{}])[0]
    for p in cand.get("content", {}).get("parts", []):
        inline = p.get("inlineData") or p.get("inline_data")
        if inline and inline.get("data"):
            Path(out).parent.mkdir(parents=True, exist_ok=True)
            Path(out).write_bytes(base64.b64decode(inline["data"]))
            print(f"OK -> {out} ({Path(out).stat().st_size//1024}KB)")
            return
    # 실패 시 텍스트/오류 출력
    print("NO IMAGE. response:", json.dumps(res)[:800])
    raise SystemExit(1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit("usage: gen_image.py <prompt> <out.png> [ref.png]")
    gen(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
