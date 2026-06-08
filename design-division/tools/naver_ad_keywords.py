#!/usr/bin/env python3
"""네이버 검색광고 API — 키워드 '실제 월간 검색량' 조회 (seo·search_director용).

검색 API(naver_search.py)는 순위/가격, 이 도구는 **검색량(수요)**를 준다.
어떤 키워드를 상품명·제목·해시태그에 우선 넣을지 '숫자로' 결정.

■ 키 발급(회장, 1회): https://searchad.naver.com 로그인 → [도구]→[API 사용 관리]
   → '네이버 검색광고 API' 라이선스 발급. 3개 값을 .env 에:
     NAVER_AD_API_KEY=<액세스 라이선스>
     NAVER_AD_SECRET=<비밀키>
     NAVER_AD_CUSTOMER_ID=<고객 ID(내 계정 번호)>

사용:
    python design-division/tools/naver_ad_keywords.py 실링팬 저천장실링팬 슬림실링팬
"""
from __future__ import annotations
import base64
import hashlib
import hmac
import os
import sys
import time
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except Exception:
    pass

BASE = "https://api.searchad.naver.com"


def _sign(ts, method, uri, secret):
    msg = f"{ts}.{method}.{uri}"
    return base64.b64encode(hmac.new(secret.encode(), msg.encode(), hashlib.sha256).digest()).decode()


def _headers(method, uri):
    api = os.environ.get("NAVER_AD_API_KEY", "").strip()
    sec = os.environ.get("NAVER_AD_SECRET", "").strip()
    cid = os.environ.get("NAVER_AD_CUSTOMER_ID", "").strip()
    if not (api and sec and cid):
        raise SystemExit("NAVER_AD_API_KEY / NAVER_AD_SECRET / NAVER_AD_CUSTOMER_ID 가 .env 에 없습니다.\n"
                         "  발급: https://searchad.naver.com → 도구 → API 사용 관리")
    ts = str(round(time.time() * 1000))
    return {"X-Timestamp": ts, "X-API-KEY": api, "X-Customer": cid,
            "X-Signature": _sign(ts, method, uri, sec)}


def _n(v):
    try:
        return int(str(v).replace("<", "").strip())
    except (ValueError, TypeError):
        return 0


def keyword_volumes(seeds: list[str]) -> list[dict]:
    uri = "/keywordstool"
    # 힌트 키워드는 최대 5개 — 초과 시 결과가 비므로 잘라낸다
    params = {"hintKeywords": ",".join(s.replace(" ", "") for s in seeds[:5]), "showDetail": "1"}
    r = requests.get(BASE + uri, params=params, headers=_headers("GET", uri), timeout=20)
    r.raise_for_status()
    out = []
    for k in r.json().get("keywordList", []):
        pc, mo = _n(k.get("monthlyPcQcCnt")), _n(k.get("monthlyMobileQcCnt"))
        out.append({"kw": k.get("relKeyword"), "pc": pc, "mobile": mo, "total": pc + mo,
                    "comp": k.get("compIdx", "")})
    return sorted(out, key=lambda x: -x["total"])


def main():
    seeds = sys.argv[1:]
    if not seeds:
        print(__doc__); return
    rows = keyword_volumes(seeds)
    print(f"\n[ 네이버 월간 검색량 — 시드 {len(seeds)}개 → 연관 {len(rows)}개 ]")
    print(f"{'키워드':<22}{'합계':>9}{'PC':>8}{'모바일':>9}  경쟁")
    print("-" * 62)
    for k in rows[:40]:
        print(f"{k['kw']:<22}{k['total']:>9,}{k['pc']:>8,}{k['mobile']:>9,}  {k['comp']}")
    print("\n※ 합계 높고 경쟁 낮은 키워드를 상품명·제목·해시태그 앞쪽에 배치(search_director 표준).")


if __name__ == "__main__":
    main()
