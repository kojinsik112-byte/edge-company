# 🌱 엣지컴퍼니 자가성장 엔진 (Growth Engine)

회장이 시키지 않아도 **매일 스스로 검색하고, 공부하고, 약한 팀을 키우는** 자동 루틴.

## 무엇을 하나 (run_daily.py 7단계)
| 단계 | 팀 | 하는 일 | 쌓이는 곳 |
|---|---|---|---|
| ① | competitive_intel | 네이버 검색API로 실링팬·조명·스위치·커튼 **순위/가격 스냅샷** | `knowledge/competitors.md` |
| ② | social_trends | 인스타·틱톡·유튜브 숏츠 **트렌드/해시태그** | `knowledge/trends.md` |
| ③ | seo·brand_intel | **키워드 수요·시장 변화** | `knowledge/market.md` |
| ④ | innovation | **새 AI 모델/도구** 소식 | `knowledge/ai_tools.md` |
| ⑤ | pmo | 팀 **활동 채점 + 성장률** 계산 | `performance/scorecard.csv` |
| ⑥ | team_coach | **저점/저성장 팀 플레이북(.md)을 실제로 개선** | `knowledge/learnings.md` + `.claude/agents/<팀>.md` |
| ⑦ | supervisor | **하루 요약 리포트**(회장 보고용) | `reports/daily_YYYYMMDD.md` |

리뷰 인사이트(`knowledge/reviews.md`)는 review_miner가 신규 리뷰 확보 시 같은 형식으로 누적한다.

실행 중엔 **실시간 관제실**(`business-ops/dashboard/dashboard.html`)에 각 팀 working/done이 뜬다.

## 실행
```bash
# 파이썬 경로(회장 PC): %LOCALAPPDATA%\Programs\Python\Python312\python.exe
python business-ops/growth-engine/tools/run_daily.py                # 기본(①③⑤⑦ 실데이터 + ②④⑥ 스텁/예약)
python business-ops/growth-engine/tools/run_daily.py --with-agents  # ②④⑥를 claude 헤드리스로 실제 웹조사/코칭
python business-ops/growth-engine/tools/run_daily.py --step 1       # 1단계만
```
- **①③(네이버)·⑤⑥⑦은 키만 있으면 항상 실제로 동작**한다(.env의 `NAVER_CLIENT_ID/SECRET`).
- **②④(웹 트렌드/신기술)와 ⑥의 코칭문구는** `claude` CLI(헤드리스)가 있고 `--with-agents`일 때 진짜 웹을 검색한다. 없으면 '수집 예약'으로 남기고 루틴은 **절대 멈추지 않는다.**

## 자동 반복 스케줄 (cron)

### A. 데스크탑(Windows) — 컴퓨터 켜져 있을 때 매일 09:00
작업 스케줄러(Task Scheduler) 1줄 등록(관리자 PowerShell):
```powershell
$py = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$job = "C:\Users\win11\Downloads\에어전트 팀\edge-company-claude-friendly-thompson-NDkKH\business-ops\growth-engine\tools\run_daily.py"
schtasks /Create /TN "EdgeGrowthEngine" /TR "`"$py`" `"$job`" --with-agents" /SC DAILY /ST 09:00 /F
# 확인: schtasks /Query /TN EdgeGrowthEngine   |  지금 한 번: schtasks /Run /TN EdgeGrowthEngine
```
> 09:00에 PC가 꺼져 있었으면 그날은 건너뛴다(켜진 날 다음 실행에 누적). 놓친 것도 잡으려면 작업 속성에서 "예약 시간 후 가능한 한 빨리 시작" 체크.

### B. 클라우드/서버(Linux) — 24시간 가능
```cron
# crontab -e  (매일 09:00 KST)
0 9 * * * cd /path/edge-company && /usr/bin/python3 business-ops/growth-engine/tools/run_daily.py --with-agents >> business-ops/growth-engine/state/cron.log 2>&1
```
하루 여러 번도 가능(예: `0 9,21 * * *` = 09시·21시).

## 자기개발 루프 (매일 최소 1팀 성장)
```
pmo 채점(scorecard) → team_coach가 최저점 팀 진단 → 그 팀의 .claude/agents/<팀>.md 에 코칭 블록 자동 추가
   → 다음 작업부터 개선된 지침 적용 → 점수↑ → scorecard growth로 검증
```
- 코칭은 플레이북을 **덮어쓰지 않고 누적 추가**(`<!-- team_coach 자동 개선 날짜 -->` 블록)라 안전하다.
- 점수는 **'파이프라인 산출 기반 활동점수'**(오늘 산출물을 냈는가)다. **실매출 KPI 아님** — 네이버 등록·발행 후 analytics가 전환·매출을 합류시키면 진짜 성과로 승급한다. (회장께 솔직히)

## 커밋 정책
- `knowledge/`·`reports/` 는 **.gitignore 하지 않는다** → 자료가 git에 쌓인다.
- `dashboard/status.json` 등 휘발성 산출물만 ignore.

## 확장 여지
- review_miner→`reviews.md`, growth(광고 성과)→리포트 합류, publisher 발행로그→analytics 연결.
- 헤드리스 비용주의: ②④⑥ claude 호출은 토큰을 쓴다. 영상 생성(Veo 등)은 금지 원칙 유지.
