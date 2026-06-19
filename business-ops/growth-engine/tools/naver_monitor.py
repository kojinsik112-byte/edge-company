#!/usr/bin/env python3
"""네이버 실시간 모니터 — 우리 실링팬 순위·경쟁·검색량을 주기적으로 자동 체크.

회장 지시: 네이버에 계속 실시간 들어와 검색. 스케줄(예: 2시간마다)로 돌면서
  · '실링팬' 정확도순에서 아크로 순위
  · 1위 경쟁 + 가격
  · 핵심 키워드 검색량
을 knowledge/naver_monitor.md 에 누적하고, 관제실(team_status)에 반영한다. (카톡 안 보냄 — 조용히 감시)

실행/스케줄:
  python business-ops/growth-engine/tools/naver_monitor.py
  (Task Scheduler: EdgeNaverMonitor, 2시간마다)
"""
from __future__ import annotations
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "design-division" / "tools"))
KNOW = ROOT / "business-ops" / "knowledge" / "naver_monitor.md"
TS = ROOT / "business-ops" / "dashboard" / "tools" / "team_status.py"
PY = sys.executable or "python"


def _status(team, state, msg):
    try:
        subprocess.run([PY, str(TS), "set", team, state, msg], cwd=str(TS.parent),
                       capture_output=True, timeout=15)
    except Exception:
        pass


def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    _status("competitive_intel", "working", "네이버 실링팬 순위 실시간 체크")
    line = f"- {now} | "
    try:
        import naver_search as ns
        items = ns.search("실링팬", "sim", 10)
        our = None
        top = None
        for i, it in enumerate(items, 1):
            t = ns._clean(it.get("title")); mall = it.get("mallName") or ""
            if i == 1:
                top = f"1위 {t[:18]} {int(it.get('lprice') or 0):,}원"
            if ("아크로" in t) or ("아크로" in mall) or ("ACRO" in (it.get("brand") or "")):
                our = f"아크로 {i}위 {int(it.get('lprice') or 0):,}원"
        line += (our or "아크로 TOP10 밖") + " | " + (top or "")
    except SystemExit as e:
        line += f"검색API 키없음({e})"
    except Exception as e:
        line += f"오류 {e}"
    # 키워드 검색량(가능하면)
    try:
        import naver_ad_keywords as ad
        rows = ad.keyword_volumes(["실링팬"])
        m = {r["kw"]: r for r in rows}
        f = m.get("실링팬"); fc = m.get("실링팬조명")
        if f:
            line += f" | 실링팬 {f['total']:,}/월"
        if fc:
            line += f" · 실링팬조명 {fc['total']:,}"
    except Exception:
        pass

    if not KNOW.exists():
        KNOW.write_text("# 네이버 실시간 모니터 (naver_monitor)\n> 2시간마다 자동 체크 — 아크로 실링팬 순위·경쟁·검색량 누적.\n\n",
                        encoding="utf-8")
    with open(KNOW, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")

    rankmsg = line.split("|")[1].strip() if "|" in line else "체크 완료"
    _status("competitive_intel", "done", f"네이버 모니터 {datetime.now():%H:%M} · {rankmsg}")
    try:
        subprocess.run([PY, str(TS), "board"], cwd=str(TS.parent), capture_output=True, timeout=15)
    except Exception:
        pass
    print(line)


if __name__ == "__main__":
    main()
