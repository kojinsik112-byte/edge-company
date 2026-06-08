#!/usr/bin/env python3
"""에이전트 관제실 — 팀 실시간 상태 갱신.

각 팀(에이전트)이 일을 시작/끝낼 때 이 도구로 상태를 바꾸면,
dashboard.html(3초 자동 새로고침)에 실시간으로 보인다.

상태: idle(대기) | working(작업중) | done(완료) | blocked(막힘)

사용:
    python tools/team_status.py set scout working "실링팬 1~3위 해부 중"
    python tools/team_status.py set designer done "히어로+8컷 생성 완료"
    python tools/team_status.py board     # status.js 재생성(점수 동기화)
    python tools/team_status.py reset      # 전부 대기로
"""
from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # business-ops/dashboard
PERF = ROOT.parent / "performance" / "scorecard.csv"   # 점수 원장
STATUS = ROOT / "status.json"
STATUS_JS = ROOT / "status.js"

sys.path.insert(0, str(ROOT.parent))                   # business-ops (team_names)
try:
    from team_names import kr as _kr
except Exception:
    def _kr(t):  # 폴백
        return t


def _scorecard() -> dict:
    out = {}
    if PERF.exists():
        with open(PERF, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                prev = r["prev_score"].strip()
                last = r["last_score"].strip()
                growth = (int(last) - int(prev)) if (prev and last) else 0
                out[r["team"]] = {
                    "bonbu": r["bonbu"], "role": r["role"],
                    "score": int(last) if last else 0, "growth": growth,
                    "last_task": r.get("last_task", ""),
                }
    return out


# 본부 → 부문(상위 조직) 매핑 — 관제실 '조직도 쫙' 2단 구성
BUMUN = {
    "리서치": "🏛 본사 공통본부", "크리에이티브": "🏛 본사 공통본부", "기획카피": "🏛 본사 공통본부",
    "디자인": "🏛 본사 공통본부", "AI": "🏛 본사 공통본부", "품질법무": "🏛 본사 공통본부",
    "운영성과": "🏛 본사 공통본부", "전략": "🏛 본사 공통본부", "커머스": "🏛 본사 공통본부",
    "경영운영": "🏛 본사 공통본부", "마케팅": "🏛 본사 공통본부", "경영지원": "🏛 본사 공통본부",
    "콘텐츠소셜": "🏛 본사 공통본부",
    "조직개발": "🧠 조직·인사", "인사": "🧠 조직·인사",
    "조명사업": "🏢 사업부", "입주주관사": "🏢 사업부", "엣지리브커튼": "🏢 사업부", "아크로": "🏢 사업부",
    "프롬프트": "🧩 성장·학습", "고객유치": "🧩 성장·학습", "연구학습": "🧩 성장·학습",
    "제품개발": "🛠 제품·개발",
    "채널": "📡 채널",
}
BUMUN_ORDER = ["🏛 본사 공통본부", "🏢 사업부", "🛠 제품·개발", "🧩 성장·학습", "📡 채널", "🧠 조직·인사"]


def _weather() -> dict:
    """실시간 날씨·온도(서울) — wttr.in, 30분 캐시. 자비스 헤더용."""
    cache = ROOT / "weather.json"
    try:
        if cache.exists():
            d = json.loads(cache.read_text(encoding="utf-8"))
            if datetime.now().timestamp() - d.get("ts", 0) < 1800:
                return d
    except Exception:
        pass
    try:
        import urllib.request
        url = "https://wttr.in/Ulsan?format=%c|%t|%C|%h&m&lang=ko"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
        raw = urllib.request.urlopen(req, timeout=8).read().decode("utf-8").strip()
        ic, temp, cond, hum = (raw.split("|") + ["", "", "", ""])[:4]
        d = {"icon": ic.strip(), "temp": temp.strip().replace("+", ""), "cond": cond.strip(),
             "hum": hum.strip(), "ts": datetime.now().timestamp()}
        cache.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        return d
    except Exception:
        return {"icon": "", "temp": "", "cond": "", "hum": ""}


def _agent_meta(team_keys: list) -> dict:
    """각 팀 .md에서 설명(description) + 협업팀(본문에 등장하는 다른 팀 키) 추출."""
    import re
    adir = ROOT.parent.parent / ".claude" / "agents"
    keyset = set(team_keys)
    meta = {}
    for t in team_keys:
        f = adir / f"{t}.md"
        desc, links = "", []
        if f.exists():
            txt = f.read_text(encoding="utf-8")
            m = re.search(r"^description:\s*(.+)$", txt, re.M)
            if m:
                desc = m.group(1).strip()
            parts = txt.split("---")
            body = "---".join(parts[2:]) if len(parts) >= 3 else txt
            for k in keyset:
                if k != t and re.search(r"\b" + re.escape(k) + r"\b", body):
                    links.append(k)
        meta[t] = {"desc": desc, "links": links[:6]}
    return meta


def _load_status() -> dict:
    if STATUS.exists():
        return json.loads(STATUS.read_text(encoding="utf-8"))
    return {}


def _save_status(s: dict) -> None:
    STATUS.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")


def _render() -> None:
    cards, status = _scorecard(), _load_status()
    meta = _agent_meta(list(cards.keys()))
    teams = []
    working = studying = 0
    for team, sc in cards.items():
        st = status.get(team, {})
        if st.get("state") == "working":
            working += 1
        elif st.get("state") == "studying":
            studying += 1
        mt = meta.get(team, {})
        teams.append({
            "team": team, "kr": _kr(team), "bonbu": sc["bonbu"],
            "bumun": BUMUN.get(sc["bonbu"], "🏛 본사 공통본부"), "role": sc["role"],
            "score": sc["score"], "growth": sc["growth"],
            "state": st.get("state", "idle"), "msg": st.get("msg", ""),
            "last_task": sc.get("last_task", ""), "desc": mt.get("desc", ""),
            "links": [{"team": k, "kr": _kr(k)} for k in mt.get("links", [])],
        })
    now = datetime.now()
    active = working + studying
    mantra = (f"오늘은 {now.month}월 {now.day}일. 엣지컴퍼니 {len(teams)}개 팀 "
              + (f"모두 열심히 — {working}팀 작업 중, {studying}팀 학습·공유 중 💪" if active
                 else "대기 중입니다. 곧 움직입니다 ⚡"))
    board = {"updated": now.strftime("%Y-%m-%d %H:%M:%S"), "mantra": mantra,
             "weather": _weather(), "bumun_order": BUMUN_ORDER, "teams": teams}
    STATUS_JS.write_text("window.TEAM_BOARD = " + json.dumps(board, ensure_ascii=False) + ";\n", encoding="utf-8")


def main() -> None:
    a = sys.argv[1:]
    if not a:
        print(__doc__); return
    cmd = a[0]
    if cmd == "set":
        if len(a) < 3:
            sys.exit("사용: set <team> <state> [메시지]")
        s = _load_status()
        s[a[1]] = {"state": a[2], "msg": " ".join(a[3:]), "ts": datetime.now().isoformat(timespec="seconds")}
        _save_status(s); _render()
        print(f"✅ {a[1]} → {a[2]} : {' '.join(a[3:])}")
    elif cmd == "reset":
        _save_status({}); _render(); print("전부 대기(idle)로 초기화")
    elif cmd == "board":
        _render(); print(f"status.js 재생성 완료 → {STATUS_JS}")
    elif cmd == "studyall":
        # 유휴(working/done 아닌) 팀 전체에 오늘의 학습주제 배정 → 관제실에 '학습중' 표시
        try:
            import study_topics  # business-ops (path 등록됨)
        except Exception as e:
            sys.exit(f"study_topics 로드 실패: {e}")
        s, cards, n = _load_status(), _scorecard(), 0
        for team, sc in cards.items():
            if s.get(team, {}).get("state") in ("working", "done"):
                continue
            topic = study_topics.pick(team, sc.get("role", ""))
            s[team] = {"state": "studying", "msg": f"📚 {topic}",
                       "ts": datetime.now().isoformat(timespec="seconds")}
            n += 1
        _save_status(s); _render()
        print(f"studyall: {n}개 유휴 팀에 학습주제 배정 완료")
    else:
        sys.exit("명령: set | board | reset | studyall")


if __name__ == "__main__":
    main()
