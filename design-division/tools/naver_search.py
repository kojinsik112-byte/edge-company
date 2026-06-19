#!/usr/bin/env python3
"""네이버 쇼핑 검색 — scout·seo가 봇차단 없이 순위/가격/판매처를 자동 수집.

네이버 개발자센터 '검색 API'(쇼핑) 사용. 키는 .env 의 NAVER_CLIENT_ID / NAVER_CLIENT_SECRET.
키 발급: https://developers.naver.com → 애플리케이션 등록 → "검색" 추가.

사용:
    python tools/naver_search.py "실링팬"
    python tools/naver_search.py "실링팬" --sort asc --count 20   # 가격 낮은순 20개
정렬: sim(정확도, 기본) | date(최신) | asc(가격↑) | dsc(가격↓)
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import requests

# .env 로딩 (design-division/.env)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except Exception:
    pass

API_URL = "https://openapi.naver.com/v1/search/shop.json"
_TAG = re.compile(r"<[^>]+>")


def _clean(text: str) -> str:
    return _TAG.sub("", text or "").replace("&amp;", "&").strip()


def search(query: str, sort: str = "sim", count: int = 10) -> list[dict]:
    cid = os.environ.get("NAVER_CLIENT_ID", "").strip()
    secret = os.environ.get("NAVER_CLIENT_SECRET", "").strip()
    if not cid or not secret:
        raise SystemExit(
            "NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 가 .env 에 없습니다.\n"
            "  발급: https://developers.naver.com -> 애플리케이션 등록 -> '검색' API"
        )
    headers = {"X-Naver-Client-Id": cid, "X-Naver-Client-Secret": secret}
    params = {"query": query, "display": min(count, 100), "sort": sort}
    resp = requests.get(API_URL, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("items", [])


def main() -> None:
    ap = argparse.ArgumentParser(description="네이버 쇼핑 검색 (scout/seo용)")
    ap.add_argument("query", help="검색 키워드 (예: 실링팬)")
    ap.add_argument("--sort", default="sim", choices=["sim", "date", "asc", "dsc"])
    ap.add_argument("--count", type=int, default=10)
    args = ap.parse_args()

    items = search(args.query, args.sort, args.count)
    if not items:
        print("결과 없음")
        return

    print(f"\n[검색] '{args.query}' 네이버 쇼핑 ({args.sort}) — {len(items)}건\n")
    for i, it in enumerate(items, 1):
        title = _clean(it.get("title"))
        price = int(it.get("lprice") or 0)
        mall = it.get("mallName") or "-"
        brand = it.get("brand") or it.get("maker") or ""
        cat = " > ".join(filter(None, [it.get("category3"), it.get("category4")]))
        print(f"{i:>2}. {title}")
        print(f"     {price:,}원 | 판매처: {mall}" + (f" | 브랜드: {brand}" if brand else ""))
        if cat:
            print(f"     카테고리: {cat}")
        print(f"     {it.get('link')}")
    print("\n※ 오픈 검색 API는 정확도(sim)순 기준. 정밀 랭킹/리뷰순은 화면 확인 병행 권장.")


if __name__ == "__main__":
    sys.exit(main())
