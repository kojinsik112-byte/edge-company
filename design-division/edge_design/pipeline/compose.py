"""Compose 단계 — 섹션들을 긴 상세페이지 HTML 로 조판하고, 가능하면 PNG 로 렌더한다.

Playwright 가 설치돼 있으면 단일 PNG 로 캡처하고, 없으면 HTML 만 저장한다.
"""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..config import TEMPLATES_DIR
from .brief import ProductBrief, Section


def compose_html(brief: ProductBrief, sections: list[Section], outdir: Path) -> Path:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    tpl = env.get_template("detail_page.html.j2")

    # 이미지 경로를 HTML 기준 상대경로로
    for sec in sections:
        if sec.image_path:
            try:
                sec.image_path = str(Path(sec.image_path).resolve().relative_to(outdir.resolve()))
            except ValueError:
                sec.image_path = str(Path(sec.image_path).resolve())

    html = tpl.render(brief=brief, sections=sections)
    out = outdir / "detail_page.html"
    out.write_text(html, encoding="utf-8")
    print(f"[compose] HTML → {out}")
    return out


def render_png(html_path: Path, outdir: Path, width: int = 860) -> Path | None:
    """Playwright 로 풀페이지 캡처. 미설치 시 None."""
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        print("[compose] playwright 미설치 — HTML만 생성 (PNG 원하면 requirements 주석 해제)")
        return None

    out = outdir / "detail_page.png"
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": 1200})
        page.goto(html_path.resolve().as_uri())
        page.screenshot(path=str(out), full_page=True)
        browser.close()
    print(f"[compose] PNG → {out}")
    return out
