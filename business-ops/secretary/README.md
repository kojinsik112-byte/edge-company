# 🤖 비서실 (Secretary / JARVIS) — 아침 8:30 카톡 보고

회장이 아이언맨이면 이건 자비스. **매일 아침 8:30, 비서실(supervisor·pmo)이 전 팀 현황을 취합해 회장 카카오톡으로 한 건 보고**한다.

## 보고 내용 (morning_brief.py)
- 📌 **어제 한 일** — 최근 작업한 팀장별 한 줄
- ⚠️ **특이사항** — 아크로 순위/경쟁 가격 변동 등
- 🏆 **성과 좋은 팀** + 🌱 오늘 성장한 팀 + 🔧 코칭 받은 팀
- 👉 **본부장 제안**

데이터는 자가성장 엔진(`growth-engine`)이 매일 쌓는 `performance/scorecard.csv`·`knowledge/`·`reports/`에서 자동으로 취합한다.

## 구성
| 파일 | 역할 |
|---|---|
| `tools/morning_brief.py` | 브리핑 작성 → 카톡 전송(+선택 음성) |
| `tools/kakao_send.py` | 카카오톡 '나에게 보내기' 전송·토큰관리 |
| `tools/voice_brief.py` | (선택) 타입캐스트 음성 브리핑(mp3) |
| `briefs/brief_YYYYMMDD.md` | 그날 보낸 보고 보관 |

## ① 카카오톡 연결 (최초 1회, 회장이 브라우저로 — 비번은 본인만)
1. https://developers.kakao.com → **내 애플리케이션 추가** → [앱 키]의 **REST API 키** 복사
2. [카카오 로그인] **활성화 ON** → [동의항목]에서 **카카오톡 메시지 전송(talk_message)** 사용 설정
3. [카카오 로그인] > **Redirect URI**에 `https://localhost` 등록
4. `design-division/.env`에 입력:
   ```
   KAKAO_REST_API_KEY=발급받은_REST_API_키
   KAKAO_REDIRECT_URI=https://localhost
   ```
5. 동의 URL 생성 → 브라우저로 열어 동의:
   ```
   python business-ops/secretary/tools/kakao_send.py authorize-url
   ```
   동의 후 주소창 `...localhost/?code=XXXXX` 의 **XXXXX(code)** 복사
6. 토큰 발급(이후 자동 갱신됨):
   ```
   python business-ops/secretary/tools/kakao_send.py exchange XXXXX
   ```
7. 테스트 발송:
   ```
   python business-ops/secretary/tools/kakao_send.py send "자비스 테스트 보고 ✅"
   ```
> 토큰은 `secretary/state/kakao_token.json`(gitignore)과 `.env`(gitignore)에만 저장. **깃에 안 올라간다.**
> access_token이 만료돼도 refresh_token으로 자동 갱신해 매일 알아서 보낸다.

## ② (선택) 음성 브리핑 — 타입캐스트
회장 타입캐스트 유료 계정 활용. `.env`에:
```
TYPECAST_API_KEY=타입캐스트_API_토큰
TYPECAST_ACTOR_ID=원하는_보이스_id
```
보이스 id 조회: `python business-ops/secretary/tools/voice_brief.py actors`
→ `morning_brief.py --voice` 면 mp3 생성 후 데스크탑에서 자동 재생(자비스가 읽어줌).

## ③ 아침 8:30 자동 보고 스케줄
**권장: 2개 작업** (데이터 수집 08:00 → 보고 08:30)
```powershell
$py = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$base = "C:\Users\win11\Downloads\에어전트 팀\edge-company-claude-friendly-thompson-NDkKH\business-ops"
# 08:00 자가성장 엔진(데이터 수집·채점·코칭, 웹조사 포함)
schtasks /Create /TN "EdgeGrowthEngine" /TR "`"$py`" `"$base\growth-engine\tools\run_daily.py`" --with-agents" /SC DAILY /ST 08:00 /F
# 08:30 비서 카톡 보고 (원하면 끝에 --voice 추가)
schtasks /Create /TN "EdgeMorningBrief" /TR "`"$py`" `"$base\secretary\tools\morning_brief.py`"" /SC DAILY /ST 08:30 /F
```
- **간단형(1개)**: `morning_brief.py --refresh` 한 줄이면 08:30에 수집→보고를 한 번에. (단 웹조사는 빠짐 — 넣으려면 위 2개 권장)
- 서버(Linux cron): `30 8 * * * cd /repo && python3 business-ops/secretary/tools/morning_brief.py`
- 8:30에 PC가 꺼져 있으면 그날은 건너뜀. 작업 속성 "예약 시간 후 가능한 한 빨리 시작" 체크 시 켜질 때 보냄.

## 동작/한계 (솔직)
- **키 없이도 안 멈춘다**: 카톡 토큰 없으면 브리핑을 파일·콘솔로만 남긴다(드라이런). 키 넣으면 즉시 실발송.
- 카카오 text 메시지 길이 제한 때문에 긴 보고는 **자동 분할(1/2, 2/2)** 전송한다.
- '나에게 보내기'는 회장 본인 톡으로만 간다(다른 사람에게 보내려면 친구 동의/메시지 API 별도).
- 점수는 활동점수 → 실매출 KPI는 네이버 등록·발행 후 analytics 합류 시 승급.
