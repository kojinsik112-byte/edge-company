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
                }
    return out


def _load_status() -> dict:
    if STATUS.exists():
        return json.loads(STATUS.read_text(encoding="utf-8"))
    return {}


def _save_status(s: dict) -> None:
    STATUS.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")


def _render() -> None:
    cards, status = _scorecard(), _load_status()
    teams = []
    working = 0
    for team, sc in cards.items():
        st = status.get(team, {})
        if st.get("state") == "working":
            working += 1
        teams.append({
            "team": team, "kr": _kr(team), "bonbu": sc["bonbu"], "role": sc["role"],
            "score": sc["score"], "growth": sc["growth"],
            "state": st.get("state", "idle"), "msg": st.get("msg", ""),
        })
    now = datetime.now()
    mantra = (f"오늘은 {now.month}월 {now.day}일. 엣지컴퍼니 {len(teams)}개 팀 모두 "
              + (f"열심히 일하고 있습니다 ({working}팀 작업 중) 💪" if working else "대기 중입니다. 곧 움직입니다 ⚡"))
    board = {"updated": now.strftime("%Y-%m-%d %H:%M:%S"), "mantra": mantra, "teams": teams}
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
    else:
        sys.exit("명령: set | board | reset")


if __name__ == "__main__":
    main()
