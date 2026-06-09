# 인수인계서 (HANDOVER) — 엣지컴퍼니 현황
> 본부장(Claude) · **갱신 2026-06-09** · 새 세션은 이 문서 + `CLAUDE.md` + `memory/MEMORY.md`를 읽고 그대로 이어받는다.
> 빌더 규칙: 데스크탑(나)=유일 빌더. **시작 시 `git pull`, 끝나면 `git push`.** 키는 `.env`(gitignore)에만.

## 0. 한 줄 현황
**116팀·4독립사업부 운영체계(OS) 완성.** 자가성장엔진·JARVIS비서·럭셔리관제실·채용시스템·보안감시·검색API·디자인API(fal.ai) 다 가동. **남은 병목 = 회장님 실제 자산(실측 스펙·실사·가격 결정).**

## 1. 작동 중인 시스템 (전부 git 저장됨)
- **관제실(JARVIS)**: `business-ops/dashboard/dashboard.html` (바탕화면 「JARVIS 관제실」 아이콘). 한눈에/작업중/사업부/전체 탭·KPI·성과랭킹·날씨(울산)·시계·막힘경보·클릭상세·작업🟡/학습🔵/완료🟢 실시간. **file:// 더블클릭 작동**(localStorage 안전래퍼). 팀이 일하면 `team_status.py set <팀> working/done` → 15~20초 내 표시.
- **자가성장엔진 하루 2회**: `growth-engine/tools/morning_routine.py`(08:30 수집·채점·카톡·음성) + `evening_routine.py`(21:00 채점·코칭·요약) + `naver_monitor.py`(2시간마다 순위). 등록=EdgeMorningRoutine/EdgeEveningRoutine/EdgeNaverMonitor.
- **JARVIS 비서**: 아침8:30 카톡 보고(`secretary/morning_brief.py`+`kakao_send.py`). 음성=윈도우SAPI(타입캐스트키 넣으면 성우). 카카오 실연동됨.
- **채용시스템**: `business-ops/hr/hire_team.py` — "아! ○○팀 필요합니다, 채용하겠습니다" → 에이전트·점수판·한글명·채용대장 일괄+관제실 자동반영. 명부=`TEAMS.md`(만들기 전 확인, 중복금지).
- **보안감시팀**: `business-ops/security/key_watch.py` + pre-commit 훅 — 키가 커밋에 섞이면 차단+카톡경보. 새PC=`install_hook.py` 1회.
- **지식창고**: `business-ops/knowledge/`(매일 누적) — competitors·naver_keywords·naver_sweep·naver_monitor·trends·market·ai_tools·learnings·reviews.

## 2. 연동된 API (`.env`, gitignore)
✅ 네이버검색(naver_search) · 네이버검색광고/검색량(naver_ad_keywords) · 카카오(나에게보내기) · 유튜브Data(youtube_search) · 구글Gemini(이미지) · **fal.ai**(Flux실사컷+Ideogram, $10충전, `design-division/output/api_test/`에 검증샷).
⬜ 미연동(필요시): OpenAI·Photoroom/Claid(누끼·4K)·타입캐스트(음성). 인스타=Buffer경유(직접API·브라우저 둘다 차단).
> ⚠️ AI는 **제품을 지어내지 말 것**. 제품 비주얼은 회장 실제자산(`Desktop\아크로 사진` NEW SLIM 흰팬) ref. AI는 배경/공간만. 한글은 HTML/Pillow 오버레이(AI 한글 깨짐).

## 3. 핵심 데이터·인사이트 (실측)
- **검색량**: 실링팬 12.2만 · **실링팬조명 2.7만** · **블라인드 22.8만(실링팬 2배!)** · 거실7.7천·안방4.6천·작은방3.4천·아이방2천. **저천장/블루투스/슬림 = 검색 거의 0**(우리가 밀던 말이 검색 안 됨).
- **우리 아크로 시그니처**: "실링팬" 정확도순 **7위**(8→7 상승), 309,000원=TOP10 최고가. 판매처 edge2050(아크로스튜디오).
- **네이버 캡처**: 우리+경쟁사9곳 상세 풀캡처 `scout_reports/`(원본 로컬, 썸네일 git). 🔴 **상품페이지 캡처는 반드시 "상세정보 펼쳐보기" 클릭**(`tools/scraper/acro_detail.js`, 로그인프로필 `%TEMP%\arco_cdp`).

## 4. 상세페이지 진단(1위 따라잡기) — `naver_listing/아크로_상세페이지_진단서.md`
우리 상세 = 1위의 **1/3 길이**(5,699자/42,961px vs 17,037자/10만px). 빠진것: **숫자 스펙표**(우리 '승부처'인데!)·세일/혜택배너·고객 실사진 리뷰·공간별컷. 강점: **앱·생태계**(1위보다 우월).

## 5. 다음 할 일
**회장님만 제공**: ①실측 dB·풍량(CMM)·소비전력 ②공간별 실사(또는 촬영, 샷리스트 준비됨) ③슬림 판매가 ④가격/조명키트 결정.
**팀이 지금 가능**: 스펙표 레이아웃(132cm·실측칸)·조명키트 혜택배너·앱생태계 히어로·체험단(포토리뷰)·상품명 반영(`아크로_실링팬_랭킹상승.md`)·100→ 추가채용·멀티플랫폼(오늘의집 등) 콘텐츠.

## 6. 새 세션 시작 시
1. 이 문서 + `CLAUDE.md` + `memory/MEMORY.md` 읽기
2. `git pull` (현재 116팀)
3. 회장에게 "어디서 이어갈지" 확인 후 진행
