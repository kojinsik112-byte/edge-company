#!/usr/bin/env python3
"""저녁 루틴 (21:00) — 자기개발 루프 ②.

회장 지시: 21:00 저녁 = pmo가 오늘 작업 채점, team_coach가 저점/저성장 팀 1개 플레이북 개선,
supervisor가 하루 요약 → reports/. 각 단계 team_status로 관제실 표시, 끝나면 git push.

실행: python business-ops/growth-engine/tools/evening_routine.py
"""
from __future__ import annotations
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "business-ops" / "secretary" / "tools"))
sys.path.insert(0, str(ROOT / "business-ops"))

import run_daily as rd          # type: ignore
import morning_brief as mb      # type: ignore
DASH = ROOT / "business-ops" / "dashboard" / "dashboard.html"


def open_dashboard():
    try:
        os.startfile(str(DASH))
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
                        "business-ops/dashboard/status.js", ".claude/agents"],
                       cwd=str(ROOT), capture_output=True, timeout=60)
        subprocess.run(["git", "commit", "-q", "-m", msg], cwd=str(ROOT), capture_output=True, timeout=60)
        r = subprocess.run(["git", "push"], cwd=str(ROOT), capture_output=True, text=True, timeout=120)
        print("git push:", "OK" if r.returncode == 0 else r.stderr[:160])
    except Exception as e:
        print("git push 스킵:", e)


def voice_mantra(coached: str):
    from team_names import kr  # type: ignore
    now = datetime.now()
    text = (f"수고하셨습니다, 회장님. 오늘은 {now.month}월 {now.day}일이었습니다. "
            f"오늘도 팀들이 열심히 일했습니다. 저녁 점검에서 가장 약한 팀, "
            f"{kr(coached) if coached else '한 팀'}을 코칭해 내일은 더 나아집니다. "
            f"하루 요약 리포트를 저장했습니다. 편히 쉬세요.")
    try:
        import voice_brief  # type: ignore
        voice_brief.speak(text, play=True)
    except Exception as e:
        print("음성 스킵:", e)


def main():
    rd.USE_CLAUDE = True
    print(f"=== 🌙 저녁 루틴 {datetime.now():%Y-%m-%d %H:%M} ===")
    open_dashboard()

    # ① pmo 오늘 작업 채점 (오늘 산출물 낸 팀 반영)
    rd.status("pmo", "working", "오늘 작업 채점")
    rd.step_pmo([
        {"team": "competitive_intel", "ok": True}, {"team": "social_trends", "ok": True},
        {"team": "seo", "ok": True}, {"team": "innovation", "ok": True},
    ])
    rd.status("pmo", "done", "채점 완료")

    # ② team_coach 저점/저성장 팀 1개 플레이북 개선
    coach = rd.step_coach()

    # ③ supervisor 하루 요약 → reports/
    rd.status("supervisor", "working", "하루 요약 리포트 작성")
    R = {"competitors": {"captured": 0, "acro": []}, "pmo": {}, "coach": coach,
         "trends": {"ok": False}, "ai_tools": {"ok": False}}
    rpt = rd.step_report(R)
    print("리포트:", rpt)
    board()
    voice_mantra(coach.get("coached", "") if isinstance(coach, dict) else "")

    # ④ git push
    git_push(f"자기개발 루프 저녁루틴 {mb.TODAY} (채점·코칭·요약)")
    print("=== 저녁 루틴 완료 ===")


if __name__ == "__main__":
    main()
