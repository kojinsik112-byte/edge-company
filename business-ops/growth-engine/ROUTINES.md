# 🔁 자기개발 루프 — 하루 2회 루틴

회장 지시: 자기개발 루프를 하루 2회 자동 실행. PC 켜져 있을 때 실행. 시간은 회장이 바꿀 수 있게.

## 두 루틴
| 작업명 | 시각 | 스크립트 | 하는 일 |
|---|---|---|---|
| **EdgeMorningRoutine** | **08:30** | `morning_routine.py` | ①competitive_intel·social_trends·innovation 자료수집→`knowledge/*.md` ②pmo 어제 작업 채점 ③supervisor JARVIS **카톡 브리핑**+**음성** ④git push |
| **EdgeEveningRoutine** | **21:00** | `evening_routine.py` | ①pmo 오늘 작업 채점 ②team_coach 저점팀 1개 **플레이북 개선** ③supervisor 하루 요약→`reports/` ④git push |

- 각 단계는 **관제실**(`business-ops/dashboard/dashboard.html`)에 team_status로 실시간 표시. 루틴 시작 시 대시보드를 자동으로 연다.
- **자비스 음성**: 타입캐스트 키 있으면 그 목소리로, 없으면 **윈도우 내장 음성**으로 "오늘은 N월 N일… 모두 열심히 일하고 있습니다…" 멘트.
- PC가 그 시각에 꺼져 있으면 그날은 건너뜀(작업 속성 "예약 시간 후 가능한 한 빨리 시작" 체크 시 켜질 때 실행).

## ⏰ 시간 바꾸기 (회장이 직접)
**방법 A — 명령어 한 줄** (PowerShell):
```powershell
# 아침을 07:50으로
schtasks /Change /TN "EdgeMorningRoutine" /ST 07:50
# 저녁을 22:30으로
schtasks /Change /TN "EdgeEveningRoutine" /ST 22:30
```
**방법 B — 작업 스케줄러 GUI**: 시작 → "작업 스케줄러" → 작업 스케줄러 라이브러리 → `EdgeMorningRoutine`/`EdgeEveningRoutine` → 우클릭 속성 → 트리거 → 편집 → 시간 변경.

## 수동 실행 / 확인
```powershell
schtasks /Run /TN "EdgeMorningRoutine"      # 지금 한 번 실행
Get-ScheduledTaskInfo -TaskName "EdgeMorningRoutine"   # 마지막 실행 결과(0=성공)
```
직접 실행: `python business-ops/growth-engine/tools/morning_routine.py`

## 끄기 / 다시 켜기
```powershell
Disable-ScheduledTask -TaskName "EdgeMorningRoutine"   # 잠시 끄기
Enable-ScheduledTask  -TaskName "EdgeMorningRoutine"   # 다시 켜기
```
