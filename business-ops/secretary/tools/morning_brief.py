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
    return f"{m.group(1)}({m.group(2)}점)" if m else ""


def _know_summary(fname: str) -> str:
    """지식창고 파일 최신 블록에서 대표 1줄 요약 추출."""
    blk = _last_block(fname)
    for ln in blk.splitlines()[1:]:
        s = ln.strip().lstrip("-*> ").strip()
        if s and not s.startswith("|") and not s.startswith("##") and "수집 예약" not in s:
            return s.replace("**", "")[:70]
    # 폴백(예약 등)도 한 줄
    for ln in blk.splitlines()[1:]:
        s = ln.strip().lstrip("-*> ").strip()
        if s and not s.startswith("|"):
            return s.replace("**", "")[:70]
    return "기록 없음"


def _top_competitor() -> str:
    """competitors.md 최신 블록의 '실링팬' 표 1위 추출."""
    blk = _last_block("competitors.md")
    in_fan = False
    for ln in blk.splitlines():
        if "[실링팬]" in ln:
            in_fan = True
            continue
        if in_fan and ln.startswith("| 1 |"):
            c = [x.strip() for x in ln.split("|")]
            if len(c) >= 5:
                return f"1위 {c[2][:18]} {c[3]}원"
    return ""


def _bonbu_avg(rows: list[dict]) -> list[tuple]:
    agg = {}
    for r in rows:
        s = _i(r["last_score"])
        if s is None:
            continue
        agg.setdefault(r["bonbu"], []).append(s)
    out = [(b, sum(v) / len(v), len(v)) for b, v in agg.items()]
    return sorted(out, key=lambda x: -x[1])


# 사업부 본부명(공통본부와 구분)
_DIVISIONS = {"조명사업", "입주주관사", "엣지리브커튼", "아크로", "채널"}

# 펜딩(회장 헌법 8번) — 다음 할 일 우선순위
_PENDING = [
    "신형 슬림 실링팬 판매가 확정(pricing) — 원가 ~70k, 미끼전략",
    "Buffer 어댑터 연동 → 인스타·유튜브 자동발행(publisher·buffer_ops)",
    "슬림 실링팬 1호 상세페이지 + 숏폼 제작(실물사진 확보 시 퀄↑)",
]
_NEED_HELP = [
    "네이버 로그인 필요 작업 발생 시 → 카톡으로 실시간 요청드림",
    "회장만 줄 수 있는 것: 실측 dB·소비전력, 추가 실물사진, 슬림 판매가 결정",
]


def compose() -> str:
    rows = _rows()
    scored = [r for r in rows if _i(r["last_score"]) is not None]
    top = sorted(scored, key=lambda r: -_i(r["last_score"]))[:5]
    grown = sorted([r for r in scored if (_i(r["prev_score"]) is not None
                    and _i(r["last_score"]) - _i(r["prev_score"]) > 0)],
                   key=lambda r: -(_i(r["last_score"]) - _i(r["prev_score"])))[:4]
    weak = sorted(scored, key=lambda r: _i(r["last_score"]))[:3]
    worked = [r for r in scored if r.get("updated") and _i(r["tasks_done"]) and r["last_task"]]
    worked_sorted = sorted(worked, key=lambda r: r.get("updated", ""), reverse=True)[:8]
    wd = ["월", "화", "수", "목", "금", "토", "일"][datetime.now().weekday()]

    L = []
    L.append(f"🤖 엣지컴퍼니 아침보고 — {datetime.now().strftime('%m/%d')}({wd})")
    L.append("비서실(supervisor·pmo)이 전 팀 현황을 취합했습니다, 회장님.")
    L.append("")
    L.append(f"━━ 한눈에 ━━")
    L.append(f"· 총 {len(scored)}팀 가동 · 어제 작업 {len(worked)}팀 · 오늘 성장 {len(grown)}팀")
    L.append("")

    L.append("📌 어제 한 일 (최근 작업)")
    if worked_sorted:
        for r in worked_sorted:
            L.append(f"· [{r['bonbu']}] {r['team']} — {r['last_task'][:26]}")
    else:
        L.append("· 기록된 작업 없음 (run_daily 먼저 실행)")
    L.append("")

    L.append("🧠 지식창고 업데이트 (매일 누적)")
    L.append(f"· 경쟁: {_know_summary('competitors.md')}")
    L.append(f"· 트렌드: {_know_summary('trends.md')}")
    L.append(f"· 시장/키워드: {_know_summary('market.md')}")
    L.append(f"· 신규AI: {_know_summary('ai_tools.md')}")
    L.append("")

    L.append("⚠️ 특이사항")
    acro = _acro_line()
    if acro:
        L.append(f"· {acro[:60]}")
    tc = _top_competitor()
    if tc:
        L.append(f"· 실링팬 검색 {tc} (경쟁 최상위)")
    L.append("· 상세 변동은 knowledge/competitors.md")
    L.append("")

    L.append("🏆 성과 좋은 팀 TOP5")
    for r in top:
        L.append(f"· {r['team']} {r['last_score']} ({r['bonbu']})")
    if grown:
        L.append("🌱 오늘 성장: " + " / ".join(
            f"{r['team']} ▲{_i(r['last_score'])-_i(r['prev_score'])}" for r in grown))
    coach = _coach_line()
    if coach or weak:
        wt = coach or f"{weak[0]['team']}({weak[0]['last_score']}점)"
        L.append(f"🔧 오늘 육성(최저): {wt} → team_coach 플레이북 개선")
    L.append("")

    L.append("🏢 본부/사업부 평균점수")
    for b, avg, n in _bonbu_avg(rows):
        tag = "🏭" if b in _DIVISIONS else "🏢"
        L.append(f"· {tag} {b} {avg:.0f}점 ({n}팀)")
    L.append("")

    L.append("🚩 막힌 것·회장님 도움 필요")
    for x in _NEED_HELP:
        L.append(f"· {x}")
    L.append("")

    L.append("👉 오늘 본부장 제안 (펜딩 우선순위)")
    for i, x in enumerate(_PENDING, 1):
        L.append(f"{i}. {x}")
    L.append("")
    L.append("— 데이터 출처: scorecard·knowledge·reports (자가성장 엔진)")
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
