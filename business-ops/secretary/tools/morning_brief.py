#!/usr/bin/env python3
"""아침 8:30 비서 보고 (JARVIS) — 감독관팀(supervisor·pmo)이 전 팀 현황을 취합해 회장 카톡으로.

회장이 아이언맨이면 이건 자비스. 매일 아침 한 건의 카톡으로:
  · 어제(최근) 무슨 업무를 했나
  · 특이사항(경쟁 순위/가격 변동 등)
  · 어떤 팀이 성과 좋은가 / 오늘 성장한 팀
  · 팀장별 한 줄 보고
  · 본부장 제안

데이터 출처(자가성장 엔진이 쌓은 것):
  performance/scorecard.csv, knowledge/competitors.md·learnings.md, reports/daily_*.md

사용:
    python morning_brief.py                 # 브리핑 작성 → 카톡 전송(키 없으면 드라이런: 파일+콘솔)
    python morning_brief.py --refresh        # run_daily 먼저 돌려 최신화 후 보고
    python morning_brief.py --voice          # 타입캐스트로 음성(mp3) 브리핑도 생성/재생
    python morning_brief.py --print          # 전송 안 하고 미리보기만
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BIZ = ROOT / "business-ops"
SCORECARD = BIZ / "performance" / "scorecard.csv"
KNOW = BIZ / "knowledge"
REPORTS = BIZ / "reports"
BRIEFS = BIZ / "secretary" / "briefs"
RUN_DAILY = BIZ / "growth-engine" / "tools" / "run_daily.py"
TOOLS = Path(__file__).resolve().parent
PY = sys.executable or "python"
TODAY = date.today().isoformat()
BRIEFS.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(TOOLS))


def _i(v):
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return None


def _rows() -> list[dict]:
    if not SCORECARD.exists():
        return []
    with open(SCORECARD, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _last_block(fname: str) -> str:
    f = KNOW / fname
    if not f.exists():
        return ""
    txt = f.read_text(encoding="utf-8")
    blocks = re.split(r"\n## ", txt)
    return ("## " + blocks[-1]).strip() if len(blocks) > 1 else ""


def _acro_line() -> str:
    blk = _last_block("competitors.md")
    for ln in blk.splitlines():
        if "아크로 노출" in ln:
            return ln.replace("**", "").replace("아크로 노출:", "아크로").strip()
    return ""


def _coach_line() -> str:
    blk = _last_block("learnings.md")
    m = re.search(r"대상: \*\*(\w+)\*\* \((\d+)점", blk)
    return f"{m.group(1)}({m.group(2)}점) 코칭" if m else ""


def compose() -> str:
    rows = _rows()
    scored = [r for r in rows if _i(r["last_score"]) is not None]
    top = sorted(scored, key=lambda r: -_i(r["last_score"]))[:3]
    grown = sorted([r for r in scored if (_i(r["prev_score"]) is not None
                    and _i(r["last_score"]) - _i(r["prev_score"]) > 0)],
                   key=lambda r: -(_i(r["last_score"]) - _i(r["prev_score"])))[:3]
    worked = [r for r in scored if r.get("updated") and _i(r["tasks_done"]) and r["last_task"]]
    # 최근 작업한 팀장 한 줄(최대 5)
    worked_sorted = sorted(worked, key=lambda r: r.get("updated", ""), reverse=True)[:5]

    L = []
    L.append(f"🤖 에지컴퍼니 아침보고 {datetime.now().strftime('%m/%d')}")
    L.append("— 비서실(supervisor·pmo)")
    L.append("")
    L.append("📌 어제 한 일")
    if worked_sorted:
        for r in worked_sorted:
            L.append(f"· {r['team']}: {r['last_task'][:24]}")
    else:
        L.append("· (기록된 작업 없음 — run_daily 먼저)")
    L.append("")
    L.append("⚠️ 특이사항")
    acro = _acro_line()
    if acro:
        L.append(f"· {acro[:60]}")
    L.append("· (경쟁 가격·순위 변동은 knowledge/competitors.md)")
    L.append("")
    L.append("🏆 성과 좋은 팀")
    L.append("· " + " / ".join(f"{r['team']} {r['last_score']}" for r in top))
    if grown:
        g = " / ".join(f"{r['team']} ▲{_i(r['last_score'])-_i(r['prev_score'])}" for r in grown)
        L.append(f"🌱 오늘 성장: {g}")
    coach = _coach_line()
    if coach:
        L.append(f"🔧 코칭: {coach}")
    L.append("")
    L.append("👉 본부장 제안")
    L.append("· 네이버 등록·발행 진행하면 analytics가 실매출 KPI 합류")
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser(description="아침 비서 보고(JARVIS)")
    ap.add_argument("--refresh", action="store_true", help="run_daily 먼저 실행해 최신화")
    ap.add_argument("--voice", action="store_true", help="타입캐스트 음성 브리핑도 생성")
    ap.add_argument("--print", dest="only_print", action="store_true", help="전송 없이 미리보기")
    args = ap.parse_args()

    if args.refresh and RUN_DAILY.exists():
        print("· run_daily 최신화 중...")
        try:
            subprocess.run([PY, str(RUN_DAILY)], timeout=600)
        except Exception as e:
            print(f"  (run_daily 스킵: {e})")

    text = compose()
    brief_file = BRIEFS / f"brief_{TODAY.replace('-', '')}.md"
    brief_file.write_text(text, encoding="utf-8")
    print("\n" + "=" * 50 + "\n" + text + "\n" + "=" * 50)
    print(f"\n💾 저장: {brief_file}")

    if args.only_print:
        return

    # 카톡 전송 (키 없으면 드라이런)
    try:
        import kakao_send  # type: ignore
        kakao_send.send_to_me(text)
    except SystemExit as e:
        print(f"카톡 전송 보류: {e}")
    except Exception as e:
        print(f"카톡 모듈 오류: {e}")

    # 음성 브리핑 (선택)
    if args.voice:
        try:
            import voice_brief  # type: ignore
            voice_brief.speak(text, play=True)
        except Exception as e:
            print(f"음성 브리핑 스킵: {e}")


if __name__ == "__main__":
    main()
