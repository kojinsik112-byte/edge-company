# 주관사 모집공고 감시 (공고 감시팀 `bid_watch`)
> 🔴 **2026-10-31 현재 자동 확인 꺼둠** — 로그인 브라우저로 카페를 연달아 읽다가 네이버 아이디(edgecompany1)에 보호조치가 걸림. 네이버 개발자센터 검색 API는 2026-07-31부터 신규 발급 중단(→ 네이버 클라우드 NAVER API HUB · 대표 연락처 · 결제 수단 필요 → 본부장 '안 해'). **지금 방식 = 본부장이 '공고 확인해줘' 하면 그때 확인**(로그인 없이 카페 전체검색 '주관사 공고' 1 ~ 4쪽 · 보고 양식 = `report.py`). 예약(EdgeNoticeWatch_*)은 비활성 상태로 둠.


4시간마다(08:40 · 12:40 · 16:40 · 20:40 · 00:40 · 04:40 · 본부장 10-31) 네이버 카페에서 **주관사 모집공고**를 찾아 **새 글만 카톡**으로 알립니다. 본부장님 PC에서 돌아갑니다(클라우드 세션은 네이버 접속이 막혀 있음).

| 찾는 곳 | 방법 | 로그인 |
|---|---|---|
| ① 네이버 카페 전체검색 ('주관사 공고' 등 6개 검색어) | 네이버 검색 API(카페글 · 최신순) | 필요 없음 — 검색 공개 글만 잡힘 |
| ② 지정 카페 5곳 안 '주관사' 검색 | 본부장 로그인 브라우저로 카페마다 '주관사' 검색 결과 글 목록 읽기(카페 번호 자동 찾기) | 처음 1번 · **가입 카페는 검색 가능, 미가입 · 등급 제한 카페는 0건일 수 있음** |

걸러내기: 제목·요약에 '주관사 · 주관업체 · 박람회 업체' 중 하나 + '공고 · 모집 · 선정 · 입찰 · 제안 · 참가' 중 하나. '선정 결과 · 결과 발표 · 후기'는 뺌. 같은 글은 카페명 + 제목으로 한 번만 알림.

## 처음 1번 설정 (약 10분)
1. **네이버 검색 API 키** — `design-division/.env`에 `NAVER_CLIENT_ID` · `NAVER_CLIENT_SECRET` (developers.naver.com → 애플리케이션 → '검색'). 회장님 PC 키를 같이 써도 됩니다.
2. **카톡** — `business-ops/secretary/tools/kakao_send.py` 맨 위 안내대로 본부장님 카카오 계정으로 1번 인증(나에게 보내기). 안 하면 알림 없이 `state/log.md`에만 기록.
3. **카페 5곳 = 등록 끝(10-21 · 경산 입예협은 본부장 10-31 삭제)** — aptmaster10 · rainup · casa114 · jaegebal · ishift. 카페를 더하려면 `watch_config.json` `cafes`에 `{"name", "home": 카페 주소, "keyword": "주관사"}` 한 줄 추가.
4. **로그인 1번** — `cd tools/scraper` → `npm install`(처음만) → `node cafe_watch.js --login` → 열린 창에서 네이버 로그인 → 창 닫기(비밀번호는 본부장님만 입력).
5. **첫 실행** — `python jugansa/watch/notice_watch.py --init` (지금 있는 글은 '본 글'로만 저장 → 다음부터 새 글만 알림)
5-1. **점검** — `cd tools/scraper` → `node cafe_watch.js ../../jugansa/watch/watch_config.json --show` → 카페마다 창이 열리며 글 목록 JSON이 나오면 정상. `검색 결과 0건`이 나온 카페는 휴대폰에서 그 카페 '주관사' 검색이 되는지 확인(가입 · 등급).
6. **예약 등록** — `powershell -ExecutionPolicy Bypass -File jugansa/watch/register_watch.ps1`

## 평소
- 지금 바로 확인: `python jugansa/watch/notice_watch.py` · 알림 없이 보기: `--dry`
- 기록: `jugansa/watch/state/log.md` (깃 제외)
- 검색어 · 시각 바꾸기: `watch_config.json` 수정 → 시각을 바꿨으면 6번 다시
- 카페 로그인이 풀리면: 4번 다시

## 공고를 잡으면
"[단지] 공고 떴어" + 공고 첨부 → `/kickoff` (착수 보고서) → 현황판 등록.
