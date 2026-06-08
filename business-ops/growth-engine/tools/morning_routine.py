#!/usr/bin/env python3
"""아침 루틴 (08:30) — 자기개발 루프 ①.

회장 지시: 08:30 아침 = competitive_intel·social_trends·innovation 자료수집 → knowledge/*.md,
pmo가 어제 작업 채점(scorecard), supervisor가 JARVIS 카톡 브리핑 발송(+음성).
각 단계 team_status로 관제실 실시간 표시, 끝나면 git push.

실행: python business-ops/growth-engine/tools/morning_routine.py
"""
from __future__ import annotations
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))                                   # run_daily
sys.path.insert(0, str(ROOT / "business-ops" / "secretary" / "tools"))  # morning_brief, kakao, voice
sys.path.insert(0, str(ROOT / "business-ops"))                  # team_names

import run_daily as rd          # type: ignore
import morning_brief as mb      # type: ignore
DASH = ROOT / "business-ops" / "dashboard" / "dashboard.html"


def open_dashboard():
    try:
        os.startfile(str(DASH))   # 회장이 실시간으로 보게 브라우저로 열기
    except Exception:
        pass


def board():
    try:
        subprocess.run([rd.PY, str(rd.TEAM_STATUS), "board"], cwd=str(rd.TEAM_STATUS.parent),
                       capture_output=True, timeout=20)
    except Exception:
        pass


def git_push(msg: str):
    try:
        subprocess.run(["git", "add",
                        "business-ops/knowledge", "business-ops/reports",
                        "business-ops/secretary/briefs", "business-ops/performance/scorecard.csv",
                        "business-ops/dashboard/status.js"],
                       cwd=str(ROOT), capture_output=True, timeout=60)
        subprocess.run(["git", "commit", "-q", "-m", msg], cwd=str(ROOT), capture_output=True, timeout=60)
        r = subprocess.run(["git", "push"], cwd=str(ROOT), capture_output=True, text=True, timeout=120)
        print("git push:", "OK" if r.returncode == 0 else r.stderr[:160])
    except Exception as e:
        print("git push 스킵:", e)


def voice_mantra():
    """자비스 음성 멘트 — 날짜 + '다들 열심히' + 핵심 한 줄."""
    rows = mb._rows()
    scored = [r for r in rows if mb._i(r["last_score"]) is not None]
    worked = [r for r in scored if r.get("updated") and mb._i(r["tasks_done"])]
    top = sorted(scored, key=lambda r: -(mb._i(r["last_score"]) or 0))[:1]
    from team_names import kr  # type: ignore
    now = datetime.now()
    topname = kr(top[0]["team"]) if top else "여러 팀"
    text = (f"좋은 아침입니다, 회장님. 오늘은 {now.month}월 {now.day}일입니다. "
            f"엣지컴퍼니 {len(scored)}개 팀 모두 열심히 일하고 있습니다. "
            f"어제는 {len(worked)}개 팀이 움직였고, 현재 성과 1위는 {topname}입니다. "
            f"오늘 아침 보고를 카카오톡으로 보내드렸습니다. 오늘도 잘 부탁드립니다.")
    try:
        import voice_brief  # type: ignore
        voice_brief.speak(text, play=True)
    except Exception as e:
        print("음성 스킵:", e)


def main():
    rd.USE_CLAUDE = True  # claude CLI 있으면 실웹조사, 없으면 자동 폴백
    print(f"=== 🌅 아침 루틴 {datetime.now():%Y-%m-%d %H:%M} ===")
    open_dashboard()

    # ① 자료수집 (각 단계가 team_status로 관제실 표시)
    results = [rd.step_competitors(), rd.step_trends(), rd.step_ai_tools()]

    # ② pmo 채점
    rd.status("pmo", "working", "어제 작업 채점")
    rd.step_pmo(results)
    rd.status("pmo", "done", "채점 완료")

    # ③ supervisor JARVIS 카톡 브리핑 + 음성
    rd.status("supervisor", "working", "아침 카톡 브리핑 작성")
    text = mb.compose()
    (mb.BRIEFS / f"brief_{mb.TODAY.replace('-', '')}.md").write_text(text, encoding="utf-8")
    try:
        import kakao_send  # type: ignore
        kakao_send.send_to_me(text)
    except Exception as e:
        print("카톡 스킵:", e)
    rd.status("supervisor", "done", "아침 브리핑 발송")
    board()
    voice_mantra()

    # ④ git push
    git_push(f"자기개발 루프 아침루틴 {mb.TODAY} (수집·채점·브리핑)")
    print("=== 아침 루틴 완료 ===")


if __name__ == "__main__":
    main()
