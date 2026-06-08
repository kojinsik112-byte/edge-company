#!/usr/bin/env python3
"""유튜브 검색 분석 — 키워드로 상위 영상/채널을 봐서 '유튜브 검색 노출' 경쟁을 읽는다.

검색 결과 상위 제목·채널·조회를 보면, 우리 숏츠 제목/태그를 어떻게 잡을지 나온다.

■ 키: 기존 .env 의 GOOGLE_API_KEY 재사용. 단 해당 Google 프로젝트에서
   'YouTube Data API v3' 를 [사용 설정]해야 함(콘솔 → API 및 서비스 → 라이브러리).
   (Gemini용 키와 같은 프로젝트면 API만 켜면 됨)

사용:
    python design-division/tools/youtube_search.py "저천장 실링팬"
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except Exception:
    pass

API = "https://www.googleapis.com/youtube/v3"


def search(q: str, n: int = 12) -> list[dict]:
    key = os.environ.get("GOOGLE_API_KEY", "").strip()
    if not key:
        raise SystemExit("GOOGLE_API_KEY 가 .env 에 없습니다.")
    r = requests.get(f"{API}/search", params={
        "part": "snippet", "q": q, "type": "video", "maxResults": n,
        "regionCode": "KR", "relevanceLanguage": "ko", "order": "relevance", "key": key}, timeout=20)
    if r.status_code == 403:
        raise SystemExit("403 — Google 프로젝트에서 'YouTube Data API v3'를 사용 설정했는지 확인하세요.")
    r.raise_for_status()
    ids, out = [], []
    for it in r.json().get("items", []):
        sn = it.get("snippet", {})
        vid = it.get("id", {}).get("videoId")
        ids.append(vid)
        out.append({"id": vid, "title": sn.get("title"), "ch": sn.get("channelTitle"), "views": None})
    # 조회수 보강
    if ids:
        rs = requests.get(f"{API}/videos", params={"part": "statistics", "id": ",".join(filter(None, ids)), "key": key}, timeout=20)
        if rs.ok:
            st = {v["id"]: v.get("statistics", {}) for v in rs.json().get("items", [])}
            for o in out:
                o["views"] = int(st.get(o["id"], {}).get("viewCount", 0))
    return out


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return
    q = " ".join(a)
    rows = sorted(search(q), key=lambda x: -(x["views"] or 0))
    print(f"\n[ 유튜브 '{q}' 상위 영상 ]")
    for i, v in enumerate(rows, 1):
        vw = f"{v['views']:,}회" if v["views"] else "-"
        print(f"{i:>2}. {(v['title'] or '')[:42]}  | {v['ch']}  | {vw}")
    print("\n※ 상위 제목 패턴을 보고 우리 숏츠 제목/태그를 잡는다(search_director).")


if __name__ == "__main__":
    main()
