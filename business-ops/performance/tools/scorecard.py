#!/usr/bin/env python3
"""팀 성과·성장률 관리 — pmo팀 운용.

각 팀이 일을 끝내면 점수를 기록한다. 새 점수를 넣으면 이전 점수가 prev로 밀려
**성장률(이번-이전)**이 계산된다. 회장이 "누가 잘하고 얼마나 성장했나"를 본다.

사용:
    python tools/scorecard.py list           # 전체 성적표(성장률 포함)
    python tools/scorecard.py score scout 82 "1~3위 전수해부 완료"
    python tools/scorecard.py growth          # 성장률 순
    python tools/scorecard.py bonbu           # 본부별 평균
"""
from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path

CSV = Path(__file__).resolve().parent.parent / "scorecard.csv"
FIELDS = ["team", "bonbu", "role", "prev_score", "last_score", "tasks_done", "last_task", "updated"]


def _load():
    with open(CSV, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _save(rows):
    with open(CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)


def _i(v):
    try: return int(float(v))
    except (ValueError, TypeError): return None


def _growth(r):
    p, l = _i(r["prev_score"]), _i(r["last_score"])
    return (l - p) if (p is not None and l is not None) else None


def cmd_list(rows, key=None):
    if key == "growth":
        rows = sorted(rows, key=lambda r: (_growth(r) is None, -(_growth(r) or 0)))
        title = "성장률 순"
    else:
        rows = sorted(rows, key=lambda r: -( _i(r["last_score"]) or 0))
        title = "점수 순"
    print(f"\n[ 엣지컴퍼니 팀 성적표 — {title} ]")
    print(f"{'팀':<18}{'본부':<8}{'점수':>5}{'성장':>7}{'작업':>5}  최근 작업")
    print("-" * 78)
    for r in rows:
        g = _growth(r)
        gtxt = ("▲%d" % g) if g and g > 0 else ("▼%d" % -g) if g and g < 0 else ("–" if g == 0 else "·")
        print(f"{r['team']:<18}{r['bonbu']:<8}{(_i(r['last_score']) or 0):>5}{gtxt:>7}{r['tasks_done']:>5}  {r['last_task'][:28]}")
    print()


def cmd_score(rows, team, score, task):
    for r in rows:
        if r["team"] == team:
            r["prev_score"] = r["last_score"] or ""
            r["last_score"] = str(int(score))
            r["tasks_done"] = str((_i(r["tasks_done"]) or 0) + 1)
            r["last_task"] = task
            r["updated"] = date.today().isoformat()
            _save(rows)
            g = _growth(r)
            print(f"✅ {team}: {r['prev_score'] or '–'} → {r['last_score']}  (성장 {'+' if (g or 0)>=0 else ''}{g if g is not None else '?'})")
            return
    sys.exit(f"팀 없음: {team}")


def cmd_bonbu(rows):
    agg = {}
    for r in rows:
        s = _i(r["last_score"]) or 0
        agg.setdefault(r["bonbu"], []).append(s)
    print("\n[ 본부별 평균 점수 ]")
    for b, ss in sorted(agg.items(), key=lambda x: -sum(x[1])/len(x[1])):
        print(f"  {b:<10} {sum(ss)/len(ss):.1f}점  ({len(ss)}팀)")
    print()


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return
    rows = _load()
    if a[0] == "list":
        cmd_list(rows)
    elif a[0] == "growth":
        cmd_list(rows, "growth")
    elif a[0] == "bonbu":
        cmd_bonbu(rows)
    elif a[0] == "score":
        if len(a) < 4:
            sys.exit('사용: score <team> <0-100> "작업내용"')
        cmd_score(rows, a[1], a[2], " ".join(a[3:]))
    else:
        sys.exit("명령: list | growth | bonbu | score")


if __name__ == "__main__":
    main()
