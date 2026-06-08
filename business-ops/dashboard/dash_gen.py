#!/usr/bin/env python3
"""team_ledger.csv -> dashboard/team_status.json (실시간 모니터 데이터).
status override로 '작업중(work)' 팀을 지정해 라이브 느낌을 준다."""
import csv, json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent      # business-ops/
LEDGER = BASE / "team_ledger.csv"
OUT = BASE / "dashboard" / "team_status.json"

# 지금 '작업중'인 팀 (실시간) — team: 현재작업
WORKING = {
    "ai_ops": "실시간 팀 모니터 대시보드 구축 중",
    "supervisor": "39팀 성과·성장률 집계 중",
    "operator": "네이버 등록 패키지(SEO·태그) 작성 중",
    "analytics": "슬림 페이지 섹션별 효과 분석 중",
    "scout": "경쟁사 가격·신제품 재정찰 중",
}

rows = []
with open(LEDGER, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        team = r["team"]
        status = "standby"
        task = r["recent"] if r["recent"] != "-" else "대기"
        if team in WORKING:
            status, task = "work", WORKING[team]
        elif r["status"] == "active":
            status = "done"
        rows.append({
            "team": team, "division": r["division"],
            "score": int(r["score"]), "baseline": int(r["baseline"]),
            "task": task, "status": status,
        })

OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
w = sum(1 for x in rows if x["status"] == "work")
d = sum(1 for x in rows if x["status"] == "done")
print(f"OK -> {OUT.name}  팀 {len(rows)}  작업중 {w}  완료 {d}  대기 {len(rows)-w-d}")
