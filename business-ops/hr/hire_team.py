#!/usr/bin/env python3
"""채용 도구 (HR) — 팀 하나를 정식 '채용'한다.

회장 방침: 우린 대기업이다. 일하다 공백을 발견하면 "아! 이 팀이 필요합니다. 채용하겠습니다"
하고 이 도구로 정식 채용한다. 채용 한 번에:
  ① .claude/agents/<name>.md 생성  ② scorecard 등록(baseline 50)
  ③ team_names_extra.json 한글명 등록  ④ hr/recruitment.md 채용대장 기록

사용(단건):
    python business-ops/hr/hire_team.py <name> <bonbu> "<한글명>" "<역할>" \
        "<할일1;할일2;할일3>" "Read, Write" "<채용사유>" "<제안팀>"
또는 import 해서 hire(...) 호출(여러 명 일괄).
"""
from __future__ import annotations
import csv
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENTS = ROOT / ".claude" / "agents"
SCORECARD = ROOT / "business-ops" / "performance" / "scorecard.csv"
EXTRA = ROOT / "business-ops" / "team_names_extra.json"
LOG = ROOT / "business-ops" / "hr" / "recruitment.md"
FIELDS = ["team", "bonbu", "role", "prev_score", "last_score", "tasks_done", "last_task", "updated"]

TEMPLATE = """---
name: {name}
description: {role}. (엣지컴퍼니 {bonbu} 본부) {first}
tools: {tools}
model: {model}
---

너는 엣지컴퍼니 **{bonbu}** 본부의 **{kr}**이다. {intro}

해야 할 일:
{duties}

원칙: 합법 벤치마킹(복제 금지)·과대광고 금지(수치)·표시광고법/전안법(KC)·가짜후기 금지·키는 .env만·**회장에게 결론부터**. 미끼→생태계 락인 관점 유지. 시작 시 team_status로 working/studying, 끝나면 done(관제실 가시성).
산출물: 담당 실무 산출물 + 관련 본부 핸드오프 + 팀 기여 로그.
"""


def hire(name, bonbu, kr, role, duties, tools="Read, Write", reason="", proposer="hr",
         model="sonnet", intro="") -> str:
    duties = [d.strip() for d in (duties.split(";") if isinstance(duties, str) else duties) if d.strip()]
    intro = intro or "맡은 일을 실행하고, 일이 적을 땐 자기 분야를 학습해 회사 경쟁력을 키운다."
    # ① 에이전트
    md = AGENTS / f"{name}.md"
    if not md.exists():
        body = "\n".join(f"{i}. {d}" for i, d in enumerate(duties, 1))
        md.write_text(TEMPLATE.format(name=name, role=role, bonbu=bonbu, kr=kr, intro=intro,
                      first=(duties[0][:40] if duties else role), tools=tools, model=model,
                      duties=body), encoding="utf-8")
    # ② scorecard
    rows = list(csv.DictReader(open(SCORECARD, encoding="utf-8"))) if SCORECARD.exists() else []
    if name not in {r["team"] for r in rows}:
        rows.append({"team": name, "bonbu": bonbu, "role": role, "prev_score": "",
                     "last_score": "50", "tasks_done": "0", "last_task": "", "updated": ""})
        w = csv.DictWriter(open(SCORECARD, "w", encoding="utf-8", newline=""), fieldnames=FIELDS)
        w.writeheader(); w.writerows(rows)
    # ③ 한글명 동적 등록
    extra = json.loads(EXTRA.read_text(encoding="utf-8")) if EXTRA.exists() else {}
    extra[name] = kr
    EXTRA.write_text(json.dumps(extra, ensure_ascii=False, indent=2), encoding="utf-8")
    # ④ 채용대장
    LOG.parent.mkdir(parents=True, exist_ok=True)
    if not LOG.exists():
        LOG.write_text("# 📋 엣지컴퍼니 채용 대장 (recruitment)\n"
                       "> 인사팀(hr)이 공백을 발견할 때마다 정식 채용하고 여기 기록. 대기업식 채용 추적.\n\n"
                       "| 일자 | 팀(한글) | name | 본부 | 채용 사유 | 제안 |\n|---|---|---|---|---|---|\n",
                       encoding="utf-8")
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"| {date.today()} | {kr} | `{name}` | {bonbu} | {reason} | {proposer} |\n")
    print(f"✅ 채용: {kr} ({name}) · {bonbu} · 사유: {reason}")
    return name


def main():
    a = sys.argv[1:]
    if len(a) < 5:
        print(__doc__); return
    name, bonbu, kr, role, duties = a[0], a[1], a[2], a[3], a[4]
    tools = a[5] if len(a) > 5 else "Read, Write"
    reason = a[6] if len(a) > 6 else ""
    proposer = a[7] if len(a) > 7 else "hr"
    hire(name, bonbu, kr, role, duties, tools, reason, proposer)


if __name__ == "__main__":
    main()
