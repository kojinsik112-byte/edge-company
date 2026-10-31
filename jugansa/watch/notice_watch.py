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


def node_exe():
    """node 위치: PATH → tools/scraper/.node 휴대용 Node(관리자 권한 없이 설치 · 본부장 10-31)."""
    import shutil
    n = shutil.which("node")
    if n: return n
    local = CAFE_JS.parent / ".node" / "node.exe"          # tools/scraper/.node (깃 제외) — 예약 작업에서도 같은 위치
    return str(local) if local.exists() else "node"

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
    if not any(c.get("search_url") or c.get("home") for c in CFG["cafes"]) and not CFG.get("section_search"):
        return []
    try:
        p = subprocess.run([node_exe(), str(CAFE_JS), str(HERE / "watch_config.json")], cwd=str(CAFE_JS.parent),
                           capture_output=True, text=True, encoding="utf-8", timeout=300)
        rows = json.loads(p.stdout or "[]")
    except Exception as e:
        print(f"[②] 카페 검색 실패: {e}")
        return []
    for r in rows:
        if r.get("error"):
            print(f"[②] {r['cafe']}: {r['error']} (로그인 만료면 node cafe_watch.js --login)")
    return [{"src": "카페", "cafe": r["cafe"], "title": r["title"], "desc": r.get("desc", ""), "date": r.get("date", ""), "link": r["link"]}
            for r in rows if not r.get("error") and r.get("title")]


def hit(it):
    t = it["title"] if it.get("src") == "카페" else f"{it['title']} {it['desc']}"      # 카페 글은 제목만 (본문에 '주관사'만 있는 잡글 제외)
    return (any(k in t for k in CFG["must_any"]) and any(k in t for k in CFG["also_any"])
            and not any(k in t for k in CFG["exclude_any"]))


def key(it):
    """같은 글이 검색 · 카페 안 검색에서 주소 모양이 달라도 하나로 — 카페명 + 제목(공백 · 기호 제거)."""
    return re.sub(r"[\s\W_]+", "", f"{it['cafe']}|{it['title']}").lower()


DATE = r"((20\d\d|\d\d)\s*[.\-/년]\s*)?\d{1,2}\s*[.\-/월]\s*\d{1,2}\s*일?"
def read_articles(items):
    """새 글을 열어 본문을 읽고 핵심(세대 · 마감 · 메일 · 제출)만 뽑는다."""
    links = [it["link"] for it in items if it.get("link", "").startswith("http")][:8]
    if not links: return {}
    try:
        p = subprocess.run([node_exe(), str(CAFE_JS), "--read", *links], cwd=str(CAFE_JS.parent),
                           capture_output=True, text=True, encoding="utf-8", timeout=400)
        rows = json.loads((p.stdout or "[]").strip().splitlines()[-1])
    except Exception as e:
        print(f"[본문] 읽기 실패: {e}"); return {}
    out = {}
    for r in rows:
        t = r.get("text", "")
        if not t: continue
        info = {}
        m = re.search(r"([\d,]{3,6})\s*세대", t);                         info["세대"] = m.group(1) + "세대" if m else ""
        lines = [l.strip() for l in t.splitlines() if l.strip()]
        due = next((l for l in lines if re.search(r"마감|접수\s*기간|제출\s*기한|접수\s*마감|제출\s*마감|까지", l) and re.search(DATE, l)), "")
        info["마감"] = re.sub(r"\s+", " ", due)[:70]
        m = re.search(r"[\w.+-]+@[\w-]+(\.[\w-]+)+", t);                info["메일"] = m.group(0) if m else ""
        how = next((l for l in lines if re.search(r"제출\s*방법|접수\s*방법|이메일\s*접수|방문\s*접수|우편", l)), "")
        info["제출"] = re.sub(r"\s+", " ", how)[:60]
        pt = next((l for l in lines if re.search(r"PT|프레젠테이션|발표", l) and re.search(DATE, l)), "")
        info["PT"] = re.sub(r"\s+", " ", pt)[:60]
        out[r["link"]] = {k: v for k, v in info.items() if v}
    return out


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
    detail = read_articles(new) if new and not init and "--no-read" not in args else {}
    for it in new:
        print(f"  ★ [{it['cafe']}] {it['title']}  {it['link']}")
        for k, v in detail.get(it["link"], {}).items(): print(f"      {k}: {v}")
    if dry:
        return
    seen |= set(hits)
    SEEN.write_text(json.dumps(sorted(seen), ensure_ascii=False, indent=0), encoding="utf-8")
    if init or not new:
        return
    # 보고서 한 장 (report.py 양식 · state/report_*.png) + 카톡은 같은 양식의 글 (본부장 10-31)
    try:
        import report as RP
        nxt = next((t for t in sorted(CFG["times"]) if t > now[11:16]), sorted(CFG["times"])[0])
        rdata = {"at": now, "scope": {"지정 카페": f"{len(CFG['cafes'])}곳",
                                      "카페 전체글": " · ".join(f"'{q['query']}' 1 ~ {q.get('pages', 4)}쪽" for q in CFG.get("section_search", []))},
                 "new": [], "next": nxt}
        for it in new:
            d = detail.get(it["link"], {})
            dm = re.search(r"(\d{1,2})\s*[.월/]\s*(\d{1,2})", d.get("마감", "")) if d.get("마감") else None
            due_date = f"{now[:4]}-{int(dm.group(1)):02d}-{int(dm.group(2)):02d}" if dm else ""
            rdata["new"].append({"site": it["title"], "region": "", "posted": it.get("date", ""), "cafe": it["cafe"],
                                 "due": d.get("마감") or "본문에 없음 — 첨부 공고문 확인 필요", "due_date": due_date, "pt": d.get("PT", ""),
                                 "mail": d.get("메일", ""), "how": d.get("제출", ""), "hh": d.get("세대", ""), "link": it["link"],
                                 "todo": "참여할지 결정 → 하면 /kickoff"})
        # 지난 공고(마감이 지났거나 게시 30일 넘고 마감 미확인)는 '참고 · 지난 공고'로 한 번만 보고 — 이후는 seen.json으로 보고 안 함 (본부장 10-31)
        today = now[:10]; keep, past = [], []
        for c in rdata["new"]:
            posted = re.sub(r"[^0-9]", "", c.get("posted", ""))[:8]
            old = len(posted) == 8 and (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(posted, "%Y%m%d")).days > 30
            (past if (c["due_date"] and c["due_date"] < today) or (not c["due_date"] and old) else keep).append(c)
        rdata["new"] = keep
        rdata["ref"] = [{"site": c["site"], "note": f"지난 공고 · {c['due'] if c['due_date'] else (c.get('posted') or '') + ' 게시'} — 이번만 보고, 다음부터 제외"} for c in past]
        RP.render(rdata, STATE)
        report_text = RP.kakao_text(rdata)
    except Exception as e:
        print(f"[보고서] 만들기 실패: {e}"); report_text = ""
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"\n## {now} · 새 글 {len(new)}\n" + "".join(f"- [{it['cafe']}] {it['title']} — {it['link']}\n" + "".join(f"  - {k}: {v}\n" for k, v in detail.get(it["link"], {}).items()) for it in new))
    if CFG.get("kakao") and KAKAO.exists():
        def one(it):
            d = detail.get(it["link"], {})
            extra = "".join(f"\n  · {k}: {v}" for k, v in d.items())
            return f"- {it['cafe']} · {it['title']}{extra}\n  {it['link']}"
        msg = report_text or (f"[주관사 공고 감시] 새 공고 {len(new)}건 ({now})\n" + "\n".join(one(it) for it in new[:10]))
        subprocess.run([sys.executable, str(KAKAO), "send", msg], cwd=str(KAKAO.parent), timeout=60)


if __name__ == "__main__":
    main()
