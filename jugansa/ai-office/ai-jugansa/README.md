# AI 주관사업부 오피스

본부장이 Claude Code로 주관사 입찰 일을 할 때, **어느 단계에서 어느 팀이 일하는지**를 2D 오피스로 보여 준다.
일이 흐르는 순서대로 방을 놓았다: ① 개척실 → ② 착수분석실 → ③ 제작실 → ④ 검증실 → ⑤ 발송실 → ⑥ PT실 → ⑦ 결과·관제실 + 본부장실 + 휴게 코너.

| 방 | 들어오는 팀(서브에이전트) | 본부장이 직접 할 때 잡는 기준 |
|---|---|---|
| 개척실 | bid_watch · bid_outreach | watch/ · 개척 · 공고 |
| 착수분석실 | bid_notice_analyst · realestate_analyst · cafe_insight · bid_economist · bid_venue · jugansa_scholar | 착수/ · kickoff · notice.txt · 분석 |
| 제작실 | pt_builder · bid_docs · bid_visual | build_xx.py · docs_xx.py · data.py · reorg · polish · vis · light_build |
| 검증실 | auditor · legal · visual_qa · (court 스킬) | court · 검증 · 법정 · GPT_검증 |
| 발송실 | bid_mail | mail_ · 메일 · GIF · assemble · 보관함 |
| PT실 | bid_pt_coach | PT_ · 발표 |
| 결과·관제실 | bid_retro · bid_pmo | 입찰_결과분석 · 입찰현황판 · scorecard |
| 본부장실 | — | 위에 안 걸리는 모든 것 |

규칙은 `server.py` 맨 위 `TEAM_ROOM` · `PATH_RULES` 두 표에만 있다. 팀을 새로 만들면 `TEAM_ROOM` · `TEAM_KR` 에 한 줄씩 추가.

## 설치 (3분 · Windows)
1. 이 폴더(ai-jugansa)를 통째로 `%USERPROFILE%\.claude\skills\ai-jugansa\` 에 둔다.
2. `%USERPROFILE%\.claude\settings.json` 에 `hooks.settings.json` 의 `"hooks"` 내용을 넣는다(이미 hooks 가 있으면 이벤트별 배열에 항목만 추가).
3. Claude Code에서 `/ai-jugansa` → 브라우저 http://127.0.0.1:8790 (또는 이 폴더에서 `python server.py`).
4. 주관사 작업을 시키면 움직인다. [시뮬레이션 시작]은 서버 없이도 한 단지 흐름을 보여 준다.

## 안 될 때
- 캐릭터가 안 움직임 → settings.json 저장 뒤 새 지시 1번(재시작 불필요). `/hooks` 에 8790 주소가 보이는지. 폴더 안 `events.log` 가 쌓이면 서버까지는 온 것.
- "서버 연결 끊김" → `/ai-jugansa` 또는 `python server.py`.
- **클라우드(claude.ai/code) 세션은 PC settings.json 을 읽지 않는다** → 로컬 Claude Code(터미널 · 데스크톱 앱 Code 탭)에서만 움직인다.
- 기존 4방 오피스(ai-office · 8787)와 같이 켜도 충돌하지 않는다(포트가 다름).

## 바꾸기
- 방 이름 · 자리 · 색: `index.html` 맨 위 `ROOMS`
- 캐릭터 이름: `index.html` `PEOPLE` · 그림은 `static/c_<id>_stand.png` · `_walk.png` 를 같은 이름으로 교체
- 배경은 코드로 그린다(그림 파일 없음). 그림으로 바꾸려면 `drawBackground()` 대신 이미지를 그리면 된다.
