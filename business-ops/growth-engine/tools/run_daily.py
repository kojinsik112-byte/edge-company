#!/usr/bin/env python3
"""에지 컴퍼니 자가성장 엔진 — 일일 자동 루틴 (run_daily).

회장이 시키지 않아도 매일 한 번 돌면서:
  ① competitive_intel  네이버 검색API로 실링팬·조명·스위치·커튼 순위/가격 → knowledge/competitors.md
  ② social_trends      인스타·틱톡·유튜브 숏츠 트렌드/해시태그        → knowledge/trends.md
  ③ seo·brand_intel    키워드 수요·시장 변화                          → knowledge/market.md
  ④ innovation         새 AI 모델/도구 소식                           → knowledge/ai_tools.md
  ⑤ pmo                팀 활동 채점 + 성장률 계산 (scorecard)
  ⑥ team_coach         저점/저성장 팀의 플레이북(.md)을 실제로 개선   → knowledge/learnings.md
  ⑦ supervisor         하루 요약 → business-ops/reports/daily_YYYYMMDD.md

실행 중엔 관제실(team_status)에 각 팀 working/done 을 실시간 표시한다.

사용:
    python business-ops/growth-engine/tools/run_daily.py          # 전체 루틴
    python business-ops/growth-engine/tools/run_daily.py --with-agents   # ②④⑥ 를 claude 헤드리스로 실웹조사/실코칭
    python business-ops/growth-engine/tools/run_daily.py --step 1        # 특정 단계만

①은 네이버 검색API(.env 키)로 항상 실데이터를 모은다. ②④⑥의 '사고형' 단계는
claude CLI(헤드리스)가 있고 --with-agents(또는 env GROWTH_USE_CLAUDE=1)일 때 실제로 웹을 검색/코칭한다.
키/CLI가 없으면 그 단계는 '수집 예약' 엔트리를 남기고 루틴은 끝까지 돈다(절대 멈추지 않음).
"""
from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

# ── 경로 ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[3]              # repo 루트
BIZ = ROOT / "business-ops"
KNOW = BIZ / "knowledge"
REPORTS = BIZ / "reports"
STATE = ROOT / "business-ops" / "growth-engine" / "state"
TEAM_STATUS = BIZ / "dashboard" / "tools" / "team_status.py"
SCORECARD_PY = BIZ / "performance" / "tools" / "scorecard.py"
SCORECARD_CSV = BIZ / "performance" / "scorecard.csv"
NAVER_TOOLS = ROOT / "design-division" / "tools"

PY = sys.executable or "python"
TODAY = date.today().isoformat()
NOW = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

for d in (KNOW, REPORTS, STATE):
    d.mkdir(parents=True, exist_ok=True)

USE_CLAUDE = False   # --with-agents 또는 GROWTH_USE_CLAUDE=1 에서 켜짐


# ── 공통 헬퍼 ───────────────────────────────────────────────────────────
def status(team: str, state: str, msg: str = "") -> None:
    """관제실(team_status)에 팀 상태 실시간 표시."""
    try:
        subprocess.run([PY, str(TEAM_STATUS), "set", team, state, msg],
                       cwd=str(TEAM_STATUS.parent), capture_output=True, timeout=20)
    except Exception:
        pass


def score(team: str, value: int, task: str) -> None:
    """pmo 채점 — scorecard에 점수 기록(성장률 자동 계산)."""
    try:
        subprocess.run([PY, str(SCORECARD_PY), "score", team, str(value), task],
                       cwd=str(SCORECARD_PY.parent), capture_output=True, timeout=20)
    except Exception:
        pass


def append_knowledge(fname: str, title: str, body: str) -> None:
    """지식창고에 날짜별 append (계속 축적)."""
    f = KNOW / fname
    if not f.exists():
        f.write_text(f"# {title}\n> 자가성장 엔진이 매일 자동 축적하는 지식창고. (run_daily.py)\n",
                     encoding="utf-8")
    with open(f, "a", encoding="utf-8") as fh:
        fh.write(f"\n\n## {TODAY} ({NOW})\n{body.rstrip()}\n")


def agent(team: str, prompt: str, timeout: int = 240) -> str | None:
    """claude 헤드리스로 특정 팀(에이전트)에게 실제 작업을 시킨다.
    가능: --with-agents + claude CLI 설치. 불가하면 None(=상위에서 스텁 처리)."""
    if not USE_CLAUDE:
        return None
    claude = shutil.which("claude")
    if not claude:
        return None
    sysline = f"너는 에지 컴퍼니의 '{team}' 팀이다. 결과만 한국어로 간결히. 추정은 '추정' 표기, 숫자 지어내기 금지."
    try:
        r = subprocess.run(
            [claude, "-p", prompt, "--append-system-prompt", sysline,
             "--allowedTools", "WebSearch", "WebFetch", "--output-format", "text"],
            capture_output=True, text=True, timeout=timeout, encoding="utf-8")
        out = (r.stdout or "").strip()
        return out or None
    except Exception:
        return None


def _load_scorecard() -> list[dict]:
    with open(SCORECARD_CSV, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _i(v):
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return None


# ── ① competitive_intel : 네이버 순위/가격 스냅샷 (항상 실데이터) ────────
def step_competitors() -> dict:
    team = "competitive_intel"
    status(team, "working", "네이버 순위·가격 스냅샷 수집")
    sys.path.insert(0, str(NAVER_TOOLS))
    keywords = ["실링팬", "실링팬 조명", "무선 스위치", "전동커튼"]
    lines, captured, acro_hits = [], 0, []
    try:
        import naver_search  # type: ignore
        for kw in keywords:
            try:
                items = naver_search.search(kw, sort="sim", count=10)
            except SystemExit as e:        # 키 없음
                lines.append(f"- ⚠️ '{kw}' 수집 실패: {e}")
                continue
            except Exception as e:
                lines.append(f"- ⚠️ '{kw}' 오류: {e}")
                continue
            lines.append(f"\n**[{kw}] 정확도순 TOP {len(items)}**")
            lines.append("| 순위 | 상품 | 가격 | 판매처 | 브랜드 |")
            lines.append("|---|---|---|---|---|")
            for i, it in enumerate(items, 1):
                title = naver_search._clean(it.get("title"))[:40]
                price = int(it.get("lprice") or 0)
                mall = it.get("mallName") or "-"
                brand = it.get("brand") or it.get("maker") or ""
                blob = f"{title}{mall}{brand}"
                if ("아크로" in blob) or ("ACRO" in blob.upper()) or ("아크로스튜디오" in mall):
                    acro_hits.append(f"'{kw}' {i}위 {price:,}원 ({mall})")
                lines.append(f"| {i} | {title} | {price:,} | {mall} | {brand} |")
                captured += 1
    except Exception as e:
        lines.append(f"- ⚠️ naver_search 임포트 실패: {e}")

    acro_line = ("**아크로 노출**: " + " · ".join(acro_hits)) if acro_hits else \
        "**아크로 노출**: 이번 스냅샷 TOP10 내 미검출(광고/하위 가능 — 화면 확인 병행)."
    body = acro_line + "\n" + "\n".join(lines)
    append_knowledge("competitors.md", "경쟁사 순위·가격 (competitive_intel)", body)
    status(team, "done", f"{captured}행 수집")
    return {"team": team, "ok": captured > 0, "captured": captured, "acro": acro_hits}


# ── ② social_trends : 트렌드/해시태그 ───────────────────────────────────
def step_trends() -> dict:
    team = "social_trends"
    status(team, "working", "인스타·틱톡·유튜브 트렌드 수집")
    prompt = ("오늘 한국 인스타그램/틱톡/유튜브 숏츠에서 '실링팬·저천장·인테리어·홈데코' 관련 "
              "지금 뜨는 콘텐츠 포맷과 추천 해시태그(플랫폼별 3~5개 롱테일)를 조사해 표로. "
              "확인된 것만, 추정은 '추정' 표기. 검색량 숫자 지어내지 말 것.")
    out = agent(team, prompt)
    ok = bool(out)
    body = out if ok else (
        "_수집 예약_ — claude 헤드리스 미가동(--with-agents 필요) 또는 CLI 없음.\n"
        "최근 운영 기준(2026-06): 인스타 해시태그 3~5개 롱테일(`#저천장실링팬`>`#실링팬`), "
        "검증 포맷 = 저천장 비포애프터·무소음 ASMR·네이버 질문형. 틱톡 사운드는 발행당일 크리에이티브센터 확인.")
    append_knowledge("trends.md", "소셜 트렌드·해시태그 (social_trends)", body)
    status(team, "done", "트렌드 기록" if ok else "예약(헤드리스 off)")
    return {"team": team, "ok": ok}


# ── ③ seo·brand_intel : 키워드 수요·시장 ────────────────────────────────
def step_market() -> dict:
    team = "seo"
    status(team, "working", "키워드 수요·시장 변화 점검")
    sys.path.insert(0, str(NAVER_TOOLS))
    kws = ["저천장 실링팬", "슬림 실링팬", "블루투스 실링팬", "실링팬 조명"]
    lines = []
    try:
        import naver_search  # type: ignore
        for kw in kws:
            try:
                items = naver_search.search(kw, sort="sim", count=5)
                prices = [int(it.get("lprice") or 0) for it in items if it.get("lprice")]
                med = sorted(prices)[len(prices)//2] if prices else 0
                lines.append(f"- **{kw}**: 상위노출 {len(items)}건, 가격중앙값 ~{med:,}원")
            except SystemExit:
                lines.append(f"- ⚠️ '{kw}' 키 없음")
            except Exception as e:
                lines.append(f"- ⚠️ '{kw}' 오류: {e}")
    except Exception as e:
        lines.append(f"- ⚠️ naver_search 임포트 실패: {e}")
    extra = agent("brand_intel",
                  "아크로(실링팬·조명) 관점에서 위 키워드 시장에서 우리가 노릴 빈틈 한 가지만 한 줄로.")
    if extra:
        lines.append(f"- brand_intel: {extra.splitlines()[0][:120]}")
    append_knowledge("market.md", "키워드 수요·시장 변화 (seo·brand_intel)", "\n".join(lines))
    status(team, "done", f"{len(kws)}키워드 점검")
    return {"team": team, "ok": bool(lines)}


# ── ④ innovation : 새 AI 모델/도구 ──────────────────────────────────────
def step_ai_tools() -> dict:
    team = "innovation"
    status(team, "working", "신규 AI 모델/도구 탐색")
    prompt = ("최근 새로 나온/업데이트된 AI 이미지·영상·디자인·카피 생성 모델이나 도구 2~3개를 "
              "한 줄씩, 우리(상세페이지·숏폼 제작) 파이프라인에 쓸모 관점에서. 출처 포함, 확인된 것만.")
    out = agent(team, prompt)
    ok = bool(out)
    body = out if ok else (
        "_수집 예약_ — 헤드리스 off. 도입 후보 상시감시 대상: 이미지(나노바나나/Imagen/Flux), "
        "영상(런웨이/클링/Veo·비용주의), 카피·편집 자동화. ai_ops와 어댑터 검토.")
    append_knowledge("ai_tools.md", "신규 AI 모델·도구 (innovation)", body)
    status(team, "done", "기록" if ok else "예약(헤드리스 off)")
    return {"team": team, "ok": ok}


# ── ⑤ pmo : 활동 채점 + 성장률 ──────────────────────────────────────────
def step_pmo(results: list[dict]) -> dict:
    team = "pmo"
    status(team, "working", "팀 활동 채점·성장률 집계")
    # 파이프라인 산출 기반 '활동점수'(실매출 KPI 아님): 오늘 산출물 낸 팀에 점수 반영
    delivered = {
        "competitive_intel": 78 if any(r["team"] == "competitive_intel" and r["ok"] for r in results) else 58,
        "social_trends": 70 if any(r["team"] == "social_trends" and r["ok"] for r in results) else 60,
        "seo": 68 if any(r["team"] == "seo" and r["ok"] for r in results) else 60,
        "innovation": 68 if any(r["team"] == "innovation" and r["ok"] for r in results) else 60,
    }
    for t, v in delivered.items():
        score(t, v, f"자가성장 루틴 산출 {TODAY}")
    # 성장률 요약 캡처
    growth_txt = ""
    try:
        r = subprocess.run([PY, str(SCORECARD_PY), "growth"], cwd=str(SCORECARD_PY.parent),
                           capture_output=True, text=True, timeout=20, encoding="utf-8")
        growth_txt = (r.stdout or "").strip()
    except Exception:
        pass
    status(team, "done", "채점 완료")
    return {"team": team, "ok": True, "growth_txt": growth_txt, "scored": delivered}


# ── ⑥ team_coach : 저점/저성장 팀 플레이북 실제 개선 ────────────────────
def step_coach() -> dict:
    team = "team_coach"
    status(team, "working", "약점팀 진단·플레이북 개선")
    rows = _load_scorecard()
    # 코칭/측정 메타팀 제외, 최저점 1팀 선정
    cand = [r for r in rows if r["team"] not in ("pmo", "team_coach") and _i(r["last_score"]) is not None]
    cand.sort(key=lambda r: _i(r["last_score"]))
    if not cand:
        status(team, "done", "대상 없음")
        return {"team": team, "ok": False}
    weak = cand[0]
    wt, wscore = weak["team"], _i(weak["last_score"])
    agent_md = ROOT / ".claude" / "agents" / f"{wt}.md"

    tip = agent("team_coach",
                f"'{wt}'팀(역할:{weak['role']}, 현재 {wscore}점)이 더 잘하도록 "
                f"오늘 당장 적용할 구체적 개선 지침 1~2줄만. 군더더기 없이 실행지시로.")
    if not tip:
        tip = (f"[{TODAY} 코칭] {weak['role']} 산출물에 '근거 수치 1개 + 다음 액션 1줄'을 반드시 붙여 "
               f"검증가능성과 실행력을 높일 것. 매 작업 끝에 셀프체크.")

    # 플레이북(.md)에 코칭 블록을 실제로 추가 (자기개발 = 지침 업데이트)
    improved = False
    if agent_md.exists():
        with open(agent_md, "a", encoding="utf-8") as fh:
            fh.write(f"\n\n<!-- team_coach 자동 개선 {TODAY} -->\n"
                     f"> 🔧 **코칭({TODAY})**: {tip.strip()}\n")
        improved = True
    append_knowledge("learnings.md", "작업 회고·개선 교훈 (team_coach)",
                     f"- 대상: **{wt}** ({wscore}점, 최저) → 플레이북 개선 {'반영' if improved else '실패(파일없음)'}\n"
                     f"  - 개선지침: {tip.strip()}")
    # 코칭 받은 팀에 소폭 성장 반영(개선된 역량) — 과도금지 +3 캡
    if improved and wscore is not None:
        score(wt, min(wscore + 3, 100), f"team_coach 플레이북 개선 {TODAY}")
    status(team, "done", f"{wt} 개선")
    return {"team": team, "ok": True, "coached": wt, "tip": tip.strip(), "from": wscore}


# ── ⑦ supervisor : 하루 요약 리포트 ─────────────────────────────────────
def step_report(results: dict) -> Path:
    team = "supervisor"
    status(team, "working", "하루 요약 리포트 작성")
    comp = results.get("competitors", {})
    pmo = results.get("pmo", {})
    coach = results.get("coach", {})
    # 코칭까지 끝난 뒤의 '최신' 성장률을 다시 잡아 리포트 일관성 유지
    try:
        _r = subprocess.run([PY, str(SCORECARD_PY), "growth"], cwd=str(SCORECARD_PY.parent),
                            capture_output=True, text=True, timeout=20, encoding="utf-8")
        if (_r.stdout or "").strip():
            pmo = {**pmo, "growth_txt": _r.stdout.strip()}
    except Exception:
        pass
    acro = comp.get("acro") or []
    rpt = REPORTS / f"daily_{TODAY.replace('-', '')}.md"
    body = [
        f"# 에지 컴퍼니 일일 리포트 — {TODAY}",
        f"> 자가성장 엔진 자동 생성 ({NOW}) · 회장 보고용 · supervisor",
        "",
        "## 1. 오늘 자동 수집 (지식창고에 누적)",
        f"- ① competitive_intel: 경쟁 스냅샷 {comp.get('captured', 0)}행 → `knowledge/competitors.md`",
        f"  - {('아크로 노출: ' + ' · '.join(acro)) if acro else '아크로 TOP10 미검출(화면확인 병행)'}",
        f"- ② social_trends: 트렌드 → `knowledge/trends.md` ({'실조사' if results.get('trends', {}).get('ok') else '예약'})",
        f"- ③ seo·brand_intel: 키워드/시장 → `knowledge/market.md`",
        f"- ④ innovation: 신규 AI → `knowledge/ai_tools.md` ({'실조사' if results.get('ai_tools', {}).get('ok') else '예약'})",
        "",
        "## 2. 조직 성장 (pmo·team_coach)",
    ]
    if coach.get("ok"):
        body.append(f"- 🔧 **오늘 성장팀**: `{coach.get('coached')}` (최저 {coach.get('from')}점) → 플레이북 개선 반영")
        body.append(f"  - 개선지침: {coach.get('tip','')[:160]}")
    body.append("- 📊 성장률 현황(scorecard growth):")
    body.append("```")
    body.append((pmo.get("growth_txt") or "(scorecard 성장률 출력 없음)")[:1600])
    body.append("```")
    body += [
        "",
        "## 3. 본부장 한 줄",
        "- 데이터는 매일 쌓이는 중. 실매출 KPI(전환·매출)는 네이버 등록·발행 후 analytics가 합류해야 본격화.",
        "",
        "## 4. 다음 자동 실행",
        "- 내일 09:00 run_daily 재가동(데스크탑 켜져 있을 때). 켜져있지 않았던 날은 다음 가동일에 누적.",
    ]
    rpt.write_text("\n".join(body), encoding="utf-8")
    status(team, "done", rpt.name)
    score("supervisor", 70, f"일일 리포트 {TODAY}")
    return rpt


# ── 메인 ────────────────────────────────────────────────────────────────
def main() -> None:
    global USE_CLAUDE
    ap = argparse.ArgumentParser(description="에지 컴퍼니 자가성장 엔진 — 일일 루틴")
    ap.add_argument("--with-agents", action="store_true", help="②④⑥를 claude 헤드리스로 실제 실행")
    ap.add_argument("--step", type=int, default=0, help="특정 단계만(1~7), 0=전체")
    args = ap.parse_args()
    USE_CLAUDE = args.with_agents or os.environ.get("GROWTH_USE_CLAUDE") == "1"

    print(f"=== 자가성장 엔진 시작 {NOW} (claude헤드리스={'ON' if USE_CLAUDE else 'OFF'}) ===")
    R: dict = {}
    steps = {
        1: ("competitors", lambda: step_competitors()),
        2: ("trends", lambda: step_trends()),
        3: ("market", lambda: step_market()),
        4: ("ai_tools", lambda: step_ai_tools()),
    }
    order = [args.step] if args.step in steps else [1, 2, 3, 4]
    results_list = []
    for k in order:
        name, fn = steps[k]
        print(f"  [{k}] {name} ...")
        R[name] = fn()
        results_list.append(R[name])

    if args.step in (0,) or args.step == 0:
        print("  [5] pmo 채점 ...")
        R["pmo"] = step_pmo(results_list)
        print("  [6] team_coach 개선 ...")
        R["coach"] = step_coach()
        print("  [7] supervisor 리포트 ...")
        rpt = step_report(R)
        # 관제실 점수 동기화
        try:
            subprocess.run([PY, str(TEAM_STATUS), "board"], cwd=str(TEAM_STATUS.parent),
                           capture_output=True, timeout=20)
        except Exception:
            pass
        print(f"=== 완료. 리포트: {rpt} ===")
    else:
        print("=== 단계 실행 완료(부분) ===")


if __name__ == "__main__":
    main()
