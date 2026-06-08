#!/usr/bin/env python3
"""네이버 상세페이지 소스화 — 봇차단 우회용 (회장이 가져온 HTML을 분석 데이터로 변환).

네이버는 봇 직접 크롤링을 막는다. 그래서:
  1) 회장(실제 사용자)이 브라우저에서 상품 페이지를 연다.
  2) 페이지 저장(Ctrl+S '웹페이지, HTML만') 하거나 소스보기(Ctrl+U) 전체 복사.
  3) 그 .html 파일을 이 도구에 넣으면 → scout가 해부할 수 있는 구조 데이터로 변환.

추출: 상품명/대표이미지/가격/상세이미지 URL 목록/리뷰·스펙 텍스트/섹션 수(이미지 수 기준).
* 결과는 '구조 분석'용. 경쟁사 콘텐츠 복제가 아니라 위닝 패턴 파악에 쓴다(결과물은 100% 오리지널).

사용:
    python tools/naver_page_parser.py 저장한페이지.html
    python tools/naver_page_parser.py 저장한페이지.html -o teardown.md
"""
from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class _Extract(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta = {}
        self.imgs: list[str] = []
        self._text: list[str] = []
        self._skip = 0
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style", "noscript"):
            self._skip += 1
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = a.get("property") or a.get("name")
            if key and a.get("content"):
                self.meta[key] = a["content"]
        elif tag == "img":
            src = a.get("src") or a.get("data-src") or a.get("data-original")
            if src:
                self.imgs.append(src)

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self._skip:
            self._skip -= 1
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data.strip()
        elif self._skip == 0:
            t = data.strip()
            if t:
                self._text.append(t)


def parse(html: str) -> dict:
    p = _Extract()
    p.feed(html)
    text = "\n".join(p._text)

    # 상세이미지로 보이는 것만(네이버 이미지 CDN 위주)
    detail = [u for u in p.imgs if any(k in u for k in ("phinf", "pstatic", "shop", "naver"))]
    prices = sorted(set(int(x.replace(",", "")) for x in re.findall(r"([0-9]{1,3}(?:,[0-9]{3})+)\s*원", text)))

    return {
        "title": p.meta.get("og:title") or p.title,
        "og_image": p.meta.get("og:image", ""),
        "desc": p.meta.get("description", ""),
        "prices": prices,
        "img_total": len(p.imgs),
        "detail_imgs": detail,
        "text": text,
    }


def report(d: dict) -> str:
    L = ["# 네이버 상세페이지 소스화 결과 (scout 해부용)", ""]
    L.append(f"- **상품명**: {d['title']}")
    if d["prices"]:
        L.append(f"- **노출 가격(추정)**: {', '.join(f'{p:,}원' for p in d['prices'][:6])}")
    L.append(f"- **대표이미지**: {d['og_image']}")
    L.append(f"- **상세이미지 수(≈섹션 수 가늠)**: {len(d['detail_imgs'])}개 (전체 img {d['img_total']})")
    L.append("")
    L.append("## 상세이미지 URL (다운받아 비주얼 분석)")
    for i, u in enumerate(d["detail_imgs"][:40], 1):
        L.append(f"{i:>2}. {u}")
    L.append("")
    L.append("## 추출 텍스트 (리뷰·스펙·옵션·Q&A 등)")
    txt = d["text"]
    L.append(txt[:4000] + ("\n...(생략)" if len(txt) > 4000 else ""))
    L.append("")
    L.append("> scout: 위 이미지 수로 페이지 길이/섹션 수를 가늠하고, 텍스트에서 후킹·리뷰·스펙·FAQ를 뽑아 해부하라. 결과물은 100% 오리지널.")
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser(description="네이버 상세페이지 HTML → scout 해부 데이터")
    ap.add_argument("html_file", help="브라우저에서 저장한 .html 파일")
    ap.add_argument("-o", "--out", help="결과 저장 경로(.md). 없으면 화면 출력")
    args = ap.parse_args()

    path = Path(args.html_file)
    if not path.exists():
        sys.exit(f"파일 없음: {path}")
    html = path.read_text(encoding="utf-8", errors="ignore")
    out = report(parse(html))
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
        print(f"저장 완료 → {args.out}")
    else:
        print(out)


if __name__ == "__main__":
    main()
