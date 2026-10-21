"""주관사 모집공고 감시기 (입찰본부 공고 감시팀 `bid_watch`) — 본부장 PC에서 하루 4번.

사용:
  python notice_watch.py            # 검색 → 새 글만 카톡 알림 + state/log.md 기록
  python notice_watch.py --init     # 첫 실행: 지금 보이는 글은 '이미 본 글'로만 저장(알림 폭탄 방지)
  python notice_watch.py --dry      # 알림 · 저장 없이 결과만 출력
  python notice_watch.py --mock x.json   # 시험용(네트워크 없이 글 목록 주입)

두 갈래로 찾는다:
  ① 네이버 검색 API(카페글) — '주관사 공고' 등 키워드 · 최신순. 로그인 불필요, 검색 공개 글만 잡힌다(= 카페 상단 전체검색 대체).
  ② 지정 카페 6곳 — watch_config.json의 home(카페 주소) + keyword('주관사')로 카페 안 검색 결과를 본부장 로그인 프로필로 연다(tools/scraper/cafe_watch.js).
걸러내기: 제목+요약에 must_any 하나 + also_any 하나, exclude_any 없음. 이미 본 링크는 state/seen.json(깃 제외)으로 거른다.
키: design-division/.env 의 NAVER_CLIENT_ID / SECRET · 카톡 = business-ops/secretary/tools/kakao_send.py(나에게 보내기 · 본부장 PC에서 본부장 계정으로 1회 인증).
"""
import html
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CFG = json.loads((HERE / "watch_config.json").read_text(encoding="utf-8"))
STATE = HERE / "state"
SEEN = STATE / "seen.json"
LOG = STATE / "log.md"
KAKAO = ROOT / "business-ops" / "secretary" / "tools" / "kakao_send.py"
CAFE_JS = ROOT / "tools" / "scraper" / "cafe_watch.js"
TAG = re.compile(r"<[^>]+>")

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / "design-division" / ".env")
except Exception:
    pass


def clean(t):
    return html.unescape(TAG.sub("", t or "")).strip()


def api_search():
    """① 네이버 검색 API · 카페글(cafearticle) · 최신순 100개씩."""
    cid, sec = os.environ.get("NAVER_CLIENT_ID", "").strip(), os.environ.get("NAVER_CLIENT_SECRET", "").strip()
    if not (cid and sec):
        print("[①] NAVER_CLIENT_ID/SECRET 없음 — API 검색 건너뜀")
        return []
    import requests
    out = []
    for q in CFG["api_queries"]:
        try:
            r = requests.get("https://openapi.naver.com/v1/search/cafearticle.json",
                             headers={"X-Naver-Client-Id": cid, "X-Naver-Client-Secret": sec},
                             params={"query": q, "display": 100, "sort": "date"}, timeout=20)
            r.raise_for_status()
            for it in r.json().get("items", []):
                out.append({"src": "검색", "cafe": clean(it.get("cafename")), "title": clean(it.get("title")),
                            "desc": clean(it.get("description")), "link": it.get("link", "")})
        except Exception as e:
            print(f"[①] '{q}' 실패: {e}")
    return out


def cafe_search():
    """② 로그인 카페(home 또는 search_url 있는 곳) — Node 스크립트 결과."""
    if not any(c.get("search_url") or c.get("home") for c in CFG["cafes"]):
        return []
    try:
        p = subprocess.run(["node", str(CAFE_JS), str(HERE / "watch_config.json")], cwd=str(CAFE_JS.parent),
                           capture_output=True, text=True, encoding="utf-8", timeout=300)
        rows = json.loads(p.stdout or "[]")
    except Exception as e:
        print(f"[②] 카페 검색 실패: {e}")
        return []
    for r in rows:
        if r.get("error"):
            print(f"[②] {r['cafe']}: {r['error']} (로그인 만료면 node cafe_watch.js --login)")
    return [{"src": "카페", "cafe": r["cafe"], "title": r["title"], "desc": "", "link": r["link"]} for r in rows if not r.get("error")]


def hit(it):
    t = f"{it['title']} {it['desc']}"
    return (any(k in t for k in CFG["must_any"]) and any(k in t for k in CFG["also_any"])
            and not any(k in t for k in CFG["exclude_any"]))


def key(it):
    """같은 글이 검색 · 카페 안 검색에서 주소 모양이 달라도 하나로 — 카페명 + 제목(공백 · 기호 제거)."""
    return re.sub(r"[\s\W_]+", "", f"{it['cafe']}|{it['title']}").lower()


def main():
    args = sys.argv[1:]
    dry, init = "--dry" in args, "--init" in args
    if "--mock" in args:
        items = json.loads(Path(args[args.index("--mock") + 1]).read_text(encoding="utf-8"))
    else:
        items = api_search() + cafe_search()
    STATE.mkdir(exist_ok=True)
    seen = set(json.loads(SEEN.read_text(encoding="utf-8"))) if SEEN.exists() else set()
    hits, new = {}, []
    for it in items:
        if hit(it):
            hits.setdefault(key(it), it)
    for k, it in hits.items():
        if k not in seen:
            new.append(it)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{now}] 전체 {len(items)} · 주관사 공고 후보 {len(hits)} · 새 글 {len(new)}")
    for it in new:
        print(f"  ★ [{it['cafe']}] {it['title']}  {it['link']}")
    if dry:
        return
    seen |= set(hits)
    SEEN.write_text(json.dumps(sorted(seen), ensure_ascii=False, indent=0), encoding="utf-8")
    if init or not new:
        return
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"\n## {now} · 새 글 {len(new)}\n" + "".join(f"- [{it['cafe']}] {it['title']} — {it['link']}\n" for it in new))
    if CFG.get("kakao") and KAKAO.exists():
        msg = f"[주관사 공고 감시] 새 글 {len(new)}건 ({now})\n" + "\n".join(f"- {it['cafe']} · {it['title']}\n  {it['link']}" for it in new[:10])
        subprocess.run([sys.executable, str(KAKAO), "send", msg], cwd=str(KAKAO.parent), timeout=60)


if __name__ == "__main__":
    main()
