"""Edge Design Division CLI.

사용:
    python -m edge_design.cli build briefs/sample_ceiling_fan.yaml -o output
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .config import Config
from .pipeline.brief import load_brief
from .pipeline import designer, compose, mangoboard


def cmd_build(args: argparse.Namespace) -> None:
    cfg = Config()
    brief = load_brief(args.brief)
    outdir = Path(args.out) / _safe(brief.name)
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"== {brief.brand} {brief.name} 상세페이지 빌드 ==")
    _print_status(cfg)

    print("\n[1/3] 기획안 작성 (Planner+Writer)")
    sections = designer.plan_sections(brief, cfg)
    print(f"      섹션 {len(sections)}개 구성됨")

    print("\n[2/3] 이미지 생성 (Designer · 갈락티코 라인업)")
    designer.render_images(sections, brief, cfg, outdir)

    print("\n[3/4] 조판 (Compose · HTML 미리보기)")
    html = compose.compose_html(brief, sections, outdir)
    compose.render_png(html, outdir)

    print("\n[4/4] 망고보드 마감 패키지 (작업지시서 + 슬라이드 + 에셋)")
    mangoboard.export_pack(brief, sections, outdir)

    print(f"\n완료 → {outdir}")
    print("  · HTML 미리보기: detail_page.html")
    print("  · 망고보드 조립: mangoboard/작업지시서.md (+ assets/)")


def _print_status(cfg: Config) -> None:
    brain = "Claude ✓" if cfg.anthropic_api_key else "Claude ✗(드라이런)"
    imgs = [k for k, v in cfg.keys.items() if v] or ["(없음 → 드라이런)"]
    print(f"   두뇌: {brain} | 이미지 키: {', '.join(imgs)}")


def _safe(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_가-힣" else "_" for c in name).strip("_") or "product"


def main() -> None:
    parser = argparse.ArgumentParser(prog="edge-design", description="아크로 상세페이지 자동 생성")
    sub = parser.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="브리프로 상세페이지 한 장 생성")
    b.add_argument("brief", help="상품 브리프 YAML 경로")
    b.add_argument("-o", "--out", default="output", help="출력 폴더 (기본 output)")
    b.set_defaults(func=cmd_build)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
