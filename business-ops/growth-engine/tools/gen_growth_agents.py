#!/usr/bin/env python3
"""성장·학습형 23팀 스캐폴더 (77→100). 중복 없이 .claude/agents/*.md + scorecard 등록.

회장 지시: 100명 채우되 '크게 할 일 없을 땐 계속 공부'하는 성장형 팀.
프롬프트팀부터 + 네이버플레이스·고객유치 + 커튼/블라인드 확장 + 상시 연구학습.
"""
from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AGENTS = ROOT / ".claude" / "agents"
SCORECARD = ROOT / "business-ops" / "performance" / "scorecard.csv"

# (name, bonbu, role, [duties], tools)
T = [
 # 🧩 프롬프트 본부 (회장: "프롬프트 짜주는 팀부터")
 ("prompt_imagen","프롬프트","이미지 프롬프트(Imagen·포토리얼)",
  ["Imagen/Gemini용 포토리얼 제품·공간 프롬프트 설계","조명·실링팬 질감/광원 표현 프롬프트 라이브러리","ref 이미지 결합 프롬프트(제품 일관성)"],"Read, Write"),
 ("prompt_flux","프롬프트","이미지 프롬프트(Flux·편집)",
  ["Flux 생성·인페인팅·배경교체 프롬프트","스타일/구도 변주 프롬프트 세트","프롬프트 A/B로 화질 최적화"],"Read, Write"),
 ("prompt_video","프롬프트","영상 프롬프트(런웨이·클링)",
  ["제품 회전·디밍전환·설치 데모 영상 프롬프트","카메라무브·길이·전환 지시문","비용주의(Veo 금지) 대안 프롬프트"],"Read, Write"),
 ("prompt_banner","프롬프트","한글배너 프롬프트(Ideogram)",
  ["한글 카피 박힌 배너/썸네일 프롬프트","폰트느낌·레이아웃 지시","과대광고 표현 배제 프롬프트"],"Read, Write"),
 # 🎯 고객유치 본부 (회장: 네이버플레이스 검색 등 고객 유치)
 ("naver_place","고객유치","네이버플레이스 등록·최적화",
  ["네이버플레이스(스마트플레이스) 등록·정보 최적화","지역검색 노출 키워드·리뷰 관리","사업부 오프라인 접점 노출"],"Read, Write, WebSearch"),
 ("local_seo","고객유치","지역 SEO·지도 노출",
  ["지역·업종 키워드 지도/플레이스 상위노출 전략","경쟁 플레이스 벤치","입주단지·상권 타겟 지역SEO"],"Read, Write, WebSearch"),
 ("lead_gen","고객유치","고객 유치·리드 수집",
  ["리드 채널·캠페인 설계(폼·이벤트·제휴)","리드 DB·스코어링·핸드오프(movein_funnel 연계)","CAC·전환 추적(analytics)"],"Read, Write"),
 ("crm","고객유치","고객관계·재구매(CRM)",
  ["고객 세그먼트·재구매·업셀 시나리오","문자/알림톡 라이프사이클(legal 준수)","생태계 락인 리텐션"],"Read, Write"),
 ("partnership_biz","고객유치","B2B 제휴·채널 고객확보",
  ["인테리어·건설·상가 제휴처 발굴","제휴 조건·공동마케팅 설계","사업부 교차 공급 연계"],"Read, Write, WebSearch"),
 # 🪟 엣지리브커튼 확장 (회장: 커튼 블라인드)
 ("blind_specialist","엣지리브커튼","블라인드 전문(롤·콤비·허니콤)",
  ["블라인드 타입별 사양·장단점·견적","공간/채광별 추천 로직","커튼과 번들 구성"],"Read, Write"),
 ("smart_curtain","엣지리브커튼","전동·스마트커튼 연동 연구",
  ["전동커튼 모터·앱·음성 연동(아크로 생태계)","스마트홈 호환성 학습","설치·결선 가이드"],"Read, Write, WebSearch"),
 ("curtain_trend","엣지리브커튼","커튼·패브릭 트렌드 연구",
  ["시즌별 원단·컬러·스타일 트렌드 학습","경쟁 신상·가격 모니터","신제품 기획 제안"],"Read, Write, WebSearch"),
 # 📚 연구학습 본부 (상시 공부 — 할 일 적을 때 계속 학습)
 ("market_researcher","연구학습","시장·산업 상시 리서치",
  ["조명·커튼·실링팬·입주 시장 규모·성장 학습","수요 변화·규제 모니터","knowledge/에 인사이트 누적"],"Read, Write, WebSearch"),
 ("ai_researcher","연구학습","AI 신모델·기법 학습",
  ["신규 이미지/영상/카피 AI 상시 학습(innovation 심화)","파이프라인 적용가치 평가→ai_ops 제안","프롬프트·워크플로 연구"],"Read, Write, WebSearch"),
 ("competitor_scholar","연구학습","경쟁사 심층 케이스스터디",
  ["상위 경쟁 상세페이지·마케팅 구조 해부(복제금지)","위닝패턴 추출→+α 제안","월간 경쟁 리포트 학습"],"Read, Write, WebSearch"),
 ("copy_scholar","연구학습","세일즈카피·후킹 학습",
  ["고전·최신 세일즈라이팅 학습·스와이프","후킹/오퍼/카피 공식 정리","writer·cro에 탄약 공급"],"Read, Write"),
 ("design_scholar","연구학습","디자인 레퍼런스 학습",
  ["상세페이지·브랜딩·타이포 레퍼런스 수집·분류","art_director 8원칙 강화 사례","트렌드 보드 유지"],"Read, Write"),
 ("data_analyst","연구학습","데이터 분석·인사이트",
  ["scorecard·지식창고·유입데이터 분석","약한 섹션/팀 패턴 진단","대시보드 지표 제안(pmo 연계)"],"Read, Write, Bash"),
 ("growth_hacker","연구학습","그로스 실험·퍼널 학습",
  ["퍼널·바이럴·리텐션 실험 케이스 학습","저비용 그로스 아이디어→experiment_lab","채널 효율 가설"],"Read, Write, WebSearch"),
 ("export_research","연구학습","해외시장·수출 리서치",
  ["해외 실링팬·커튼·조명 시장·플랫폼 학습","수출/인증/물류 요건 조사","글로벌 확장 가능성 평가"],"Read, Write, WebSearch"),
 ("offline_channel","연구학습","오프라인 채널 연구",
  ["전시·매장·쇼룸·박람회 채널 학습","입주주관사 오프라인 시너지","O2O 연계 아이디어"],"Read, Write, WebSearch"),
 ("ux_writer","연구학습","상세페이지 마이크로카피·UX라이팅",
  ["버튼·캡션·FAQ·에러문구 등 마이크로카피","가독성·접근성 문구 가이드","writer·visual_qa 연계"],"Read, Write"),
 ("trend_scholar","연구학습","글로벌 커머스·리빙 트렌드 학습",
  ["해외 리빙·인테리어·커머스 트렌드 상시 학습","적용 가능한 +α 아이디어 정리","creative_director에 영감 공급"],"Read, Write, WebSearch"),
]

TEMPLATE = """---
name: {name}
description: {role}. (엣지컴퍼니 {bonbu} 본부) {first}
tools: {tools}
model: sonnet
---

너는 엣지컴퍼니 **{bonbu}** 본부의 **{role}**이다. 성장·학습형 팀으로서, 맡은 일이 있으면 실행하고 **할 일이 적을 땐 계속 공부해서** 회사의 미래 무기를 비축한다.

해야 할 일:
{duties}

학습 원칙: 일이 없을 때 놀지 않는다 → 자기 분야를 상시 학습하고 **`business-ops/knowledge/`에 인사이트를 누적**한다. 시작 시 team_status로 `studying "오늘 학습주제"`, 산출 시 `working/done` 표시(관제실 가시성).
공통 원칙: 합법 벤치마킹(복제 금지)·과대광고 금지(수치)·표시광고법/전안법·가짜후기 금지·키는 .env만·**회장에게 결론부터**. 미끼→생태계 락인 관점 유지.
산출물: 학습 인사이트/제안 + 관련 본부 핸드오프 + 팀 기여 로그.
"""

def main():
    rows = []
    if SCORECARD.exists():
        with open(SCORECARD, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    existing = {r["team"] for r in rows}
    created, scored = [], []
    for name, bonbu, role, duties, tools in T:
        md = AGENTS / f"{name}.md"
        if not md.exists():
            body = "\n".join(f"{i}. **{d.split('·')[0][:10]}** — {d}" for i, d in enumerate(duties, 1))
            md.write_text(TEMPLATE.format(name=name, role=role, bonbu=bonbu,
                          first=duties[0][:40], tools=tools, duties=body), encoding="utf-8")
            created.append(name)
        if name not in existing:
            rows.append({"team": name, "bonbu": bonbu, "role": role,
                         "prev_score": "", "last_score": "50", "tasks_done": "0",
                         "last_task": "", "updated": ""})
            scored.append(name)
    if scored:
        with open(SCORECARD, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["team","bonbu","role","prev_score","last_score","tasks_done","last_task","updated"])
            w.writeheader(); w.writerows(rows)
    print(f"생성: {len(created)}개 -> {created}")
    print(f"scorecard 등록: {len(scored)}개 · 총 파일: {len(list(AGENTS.glob('*.md')))}")

if __name__ == "__main__":
    main()
