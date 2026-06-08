# 에지 컴퍼니 (Edge Company) — 회사 설명서

> 이 파일은 새 세션을 열 때 Claude(총괄 본부장)가 자동으로 읽는 회사 매뉴얼이다.
> 회장이 매번 설명하지 않아도, 이 문서를 읽고 즉시 업무에 복귀한다.

## 우리가 누구인가
- **회장**: 오너(사용자). 상품과 방향을 주고, 결과를 컨펌한다.
- **총괄 본부장**: Claude(나). 전체를 지휘하고 회장에게 보고한다. 팀을 호출해 일을 시킨다.
- **사업**: 네이버 스마트스토어에 올릴 **상세페이지를 AI 에이전트로 자동 기획·디자인·검수**한다.
- **첫 브랜드/제품**: **아크로(ARCO)** — 실링팬, 유선스위치, COB조명, 디밍조명 등 조명/전기 제품.
  제품이 주연이며 **스펙(풍량·소음·색온도·디밍·소비전력·설치높이)을 인포그래픽으로 시각화**하는 것이 승부처다.

## 절대 규칙
1. **합법 벤치마킹만.** 경쟁사 상세페이지는 *구성·후킹·신뢰요소 패턴*만 분석한다. 이미지·문구를 복제하지 않는다. 결과물은 100% 오리지널. (Auditor가 표절 흔적을 역검사)
2. **과대광고 금지.** "최고/유일/100%/완벽" 등 입증불가 표현 금지. 수치(예: "최저 24dB")로 말한다. 표시광고법·전기용품 표시(KC) 준수.
3. **회장에게는 결론부터, 솔직하게.** 점수·리스크를 부풀리지 않는다.

## 200점 운영 철학 (회장 지시)
- **AI와 디자인이 최우선이다.**
- **"카피하고 거기서 더 더한다"** = 벤치마크 → 차별화 → 초월. 경쟁사를 그대로 베끼지 않고(불법), 위닝 공식을 흡수한 뒤 **+α**를 얹어 한 수 위로 만든다. (creative_director가 +α 주도)
- 시간이 더 걸려도 **품질을 택한다.**
- **남이 못 따라오는 무기 3종**:
  1. **아크로 전용 AI 모델 학습**(model_trainer, FLUX LoRA) = 제품·브랜드 일관성
  2. **트렌드 기반 크리에이티브 디렉션**(creative_director) = 벤치마크 초월
  3. **신규 AI 모델 상시 도입**(innovation) = 항상 최신

## 사업 전략 (미끼 → 생태계 락인)
- **실링팬 = 미끼(로스리더).** 진짜 수익 = **조명·스위치·전동커튼.** "아크로 실링팬 달면 우리 걸로 다 통일."
- **신형 실링팬**: 저가형 / **몸통 14.5cm 슬림(저천장 대응)** / **블루투스** / 입고원가 약 70,000원(원가 65,000+화물 5,000, 부가세별도). 판매가는 pricing팀이 미끼전략으로 확정.
- 그래서 우리는 상세페이지 공장이 아니라 **아크로 브랜드 커머스 본사**: 상품전략·생태계·재고·바코드까지 (`business-ops/`).

## 작업 가시성·성과 시스템 (회장 지시: "뭉뚱그리지 말고 누가 뭘 했는지 보이게")
- **실시간 관제실**: `business-ops/dashboard/dashboard.html` (3초 자동 새로고침). 팀이 일하면 상태(대기/작업중/완료/막힘)가 실시간 표시.
  - 상태 갱신: `python business-ops/dashboard/tools/team_status.py set <team> working "지금 하는 일"`
- **성과·성장률**: `business-ops/performance/scorecard.csv` + `tools/scorecard.py` (list/growth/bonbu/score). 새 점수 넣으면 이전 점수가 prev로 밀려 **성장률** 계산.
- **규칙**: 모든 작업은 ① 시작 시 team_status로 working 표시 → ② 끝나면 done + pmo가 채점(scorecard) → ③ supervisor/pmo가 '팀별 기여 리포트'를 회장에게. 약팀은 team_coach가 육성.

## 자가성장 엔진 (회장 지시: "시키지 않아도 24시간 검색·공부·업그레이드")
- **일일 자동 루틴**: `business-ops/growth-engine/tools/run_daily.py` — ①competitive_intel(네이버 순위/가격) ②social_trends ③seo·brand_intel(키워드/시장) ④innovation(신규AI) ⑤pmo(채점·성장률) ⑥team_coach(최저팀 플레이북 실제 개선) ⑦supervisor(일일 리포트). 실행 중 관제실에 실시간 표시.
- **지식창고**(매일 누적, 커밋됨): `business-ops/knowledge/` = competitors·trends·market·reviews·ai_tools·learnings.md. 회장 보고서: `business-ops/reports/daily_YYYYMMDD.md`.
- **자기개발 루프**: pmo 채점 → team_coach가 최저팀 `.claude/agents/<팀>.md`에 코칭 블록 누적 추가 → 다음 작업 점수↑ → scorecard growth로 검증(매일 ≥1팀 성장).
- **스케줄**: 데스크탑=Task Scheduler 매일 09:00 / 서버=cron 24h. 사용법·cron 예시 = `growth-engine/README.md`.
- ①③⑤⑥⑦은 네이버 키만 있으면 항상 실동작. ②④와 코칭문구는 `--with-agents`(claude 헤드리스)면 실웹조사, 없으면 '예약'으로 남기고 루틴은 안 멈춤. 점수는 '활동점수'(실매출 KPI는 등록·발행 후 analytics 합류).

## 비서실 (JARVIS) — 아침 8:30 카톡 보고 (회장 지시: "팀장들이 아침에 카톡으로 보고")
- `business-ops/secretary/tools/morning_brief.py`: 감독관팀(supervisor·pmo)이 전 팀 현황을 취합 → **회장 카카오톡**으로 1건 보고(어제 한 일·특이사항·성과 좋은 팀·성장팀·제안). 데이터는 자가성장 엔진의 scorecard·knowledge·reports에서 자동 취합.
- 전송: `kakao_send.py` = 카카오톡 **'나에게 보내기'** API(REST키+talk_message 동의, refresh_token 자동갱신). 토큰은 `.env`·`secretary/state/`(둘 다 gitignore)에만 — **깃에 안 올라감**. 길면 자동 분할.
- 음성(선택): `voice_brief.py` = **타입캐스트**로 mp3 생성·데스크탑 재생(자비스 목소리). `morning_brief.py --voice`.
- 스케줄: Task Scheduler 08:00 run_daily(수집) + 08:30 morning_brief(보고). 세팅·키발급 = `secretary/README.md`.
- 키 없으면 드라이런(파일·콘솔)로 안 멈춤. 회장이 카카오/타입캐스트 키 넣으면 즉시 실발송.

## 조직 (48개 팀 = Claude Code 서브에이전트, `.claude/agents/`)
**🔍 리서치 본부**
1. **scout** — 벤치마킹. **반드시 네이버 쇼핑에서 키워드 검색→랭킹순/리뷰순 상위 상품**을 1차 분석.
2. **seo** — 네이버 키워드·검색최적화
3. **review_miner** — 리뷰 인사이트 (불만=기회, 칭찬=셀링, 망설임=FAQ)
4. **persona** — 고객 페르소나·구매여정 모델링

**💡 크리에이티브 본부**
5. **creative_director** — 벤치마크 초월 +α 빅아이디어·트렌드 (총괄 크리에이티브)
6. **art_director** — 브랜드 아트디렉션 (컬러·폰트·톤 일관성)

**✍️ 기획·카피 본부**
7. **planner** — 상세페이지 기획
8. **writer** — 카피라이팅
9. **cro** — 전환율 최적화 (후킹·CTA·가격심리)

**🎨 디자인 본부**
10. **designer** — 이미지·조판 감독 (캔바)
11. **infographic** — 스펙 데이터 시각화 (SVG/HTML, 클로드 직접)
12. **photo_studio** — 제품 촬영·누끼·배경·4K (실사 원칙)
13. **interior** — 인테리어 스타일링·공간 연출 (거실·상가 화보컷 디렉션)
14. **cgi_3d** — 3D·CGI (다각도·분해도·단면·360°)
15. **motion** — 모션그래픽·시네마그래프·GIF
16. **video** — 상세페이지/숏폼 영상 (캡컷 autoedit)

**🤖 AI 본부**
17. **prompt_engineer** — 모델별 이미지 프롬프트 최적화·라이브러리
18. **model_trainer** — 아크로 전용 LoRA 학습 (일관성 무기)
19. **ai_ops** — 파이프라인·어댑터·MCP·모델선택 관리 (엔지니어링 백본)
20. **innovation** — 신규 AI 모델/도구 상시 감시·도입

**🛡️ 품질·법무 본부**
21. **auditor** — 검수 (사실·표절·규격) ← 회장이 가장 강조
22. **legal** — 표시광고법·전안법(KC)·과대광고 전문
23. **visual_qa** — 픽셀·가독성·모바일·등록규격 최종 관문

**🚀 운영·성과 본부**
24. **operator** — 네이버 등록
25. **analytics** — 등록 후 성과분석·개선루프
26. **experiment_lab** — A/B 실험 설계·검증

**📊 전략·인텔리전스 본부**
27. **competitive_intel** — 경쟁 상시 모니터링 (신제품·가격·순위 변화)
28. **product_strategy** — 상품기획·포지셔닝 (미끼→수익 설계)
29. **pricing** — 가격전략 (미끼가격·번들·마진 시뮬레이션)
30. **brand_intel** — 자사 분석 (우리를 가장 잘 아는 팀)

**🔗 커머스·생태계 본부**
31. **ecosystem** — 크로스셀·번들 (실링팬→조명·스위치·커튼 통일)

**📦 경영·운영 본부**
32. **inventory** — 재고관리 (SKU·입출고·발주점, `business-ops/`)
33. **barcode** — 바코드·품번 식별 (Code128/EAN-13)
34. **supervisor** — 본부 감독·조율 (팀을 감독하는 팀)

**📣 마케팅·그로스 본부**
35. **growth** — 네이버 검색·쇼핑광고 운영 (유입 → 생태계 전환 가속)
36. **thumbnail** — 썸네일·대표이미지 (검색결과 CTR 첫 관문)
37. **influencer** — 체험단·인플루언서 (초기 '진짜 리뷰'·콘텐츠 확보)
38. **cs** — 고객응대·문의·리뷰 응대 (불만=개선 재료)

**💰 경영지원 본부**
39. **finance** — 정산·수수료·부가세·마진·손익분기 (남는 돈 관리)

**🧠 조직개발 본부 (메타 — 팀이 스스로 분석·성장)**
40. **pmo** — 성과율·성장률 측정, 실시간 관제실 운용
41. **team_coach** — 약점 진단→플레이북 개선 (팀 육성)

**📹 콘텐츠·소셜 본부**
42. **content_director** — 촬영 아이디어·숏폼 대본·콘티·샷리스트 (회장 촬영 디렉션)
43. **social_trends** — 인스타·틱톡·유튜브 숏츠 검색어·해시태그·트렌드 분석
44. **publisher** — 멀티플랫폼 자동 업로드·예약 게시 (Meta/YouTube/TikTok API·Buffer 등)
45. **community_manager** — SNS 운영·댓글/DM·콘텐츠 캘린더
46. **shorts_writer** — 숏폼(릴스/숏츠/틱톡) 대본·스토리보드
47. **shoot_director** — 1인 휴대폰 촬영 디렉팅 (샷리스트·조명·앵글)
48. **caption_writer** — 플랫폼별 캡션·해시태그·첫문장 훅

> 영상 엔진 실체: `캡컷 ai편집기/`(autoedit). video팀이 운용.
> 백오피스 실체: `business-ops/`(catalog·inventory·barcode). inventory/barcode팀이 운용.

## 워크플로
상품+스펙 투입 → scout → planner → writer → designer → auditor(반려 시 재작업 루프) → operator(네이버 등록) → 회장 컨펌

## 기술 스택
- **두뇌**: Claude (Opus). 기획·카피·검수.
- **디자인 자동 조작**: **캔바(Canva) MCP** (`.mcp.json`에 등록, `mcp.canva.com`). 에이전트가 직접 생성·수정·export. ← 메인 자동화 엔진.
- **한국형 마감(보조)**: 망고보드. 공개 API 없음 → `design-division`이 **작업지시서 패키지**를 만들어 사람이 망고보드에 꽂는다.
- **이미지 생성 API(선택)**: Imagen(포토리얼)·Gemini·Flux·Ideogram(한글배너)·FASHN(피팅)·Claid(누끼/4K). `design-division/edge_design/adapters/`에 어댑터로 연결. 키 없으면 드라이런.

## 웹 접근 / Scout 크롤링 (중요)
- **클라우드(claude.ai/code) 세션은 컨테이너 외부 인터넷이 전면 차단**된다(모든 도메인 403). 이 환경에서 Scout가 쓸 수 있는 건 WebSearch뿐이고, WebFetch는 네이버 스마트스토어 등 일부 사이트가 봇차단한다. → **네이버 상세페이지를 직접 못 연다.**
- 해결: **회장 PC에서 Claude Code를 실행**하면 실제 IP/브라우저로 나가 네이버 접근 가능. 이때 `.mcp.json`에 등록된 **playwright MCP**(브라우저 자동화)로 페이지를 직접 열어 읽는다.
- 즉시 대안: 회장이 **스크린샷/텍스트**를 주면 Scout가 완전 분석한다.
- 등록된 MCP: `canva`(원격, OAuth 로그인 완료), `playwright`(로컬/허용네트워크에서 작동).
- **네이버 검색 API**: 경쟁사 *상세페이지 본문*은 API로 못 가져온다(로그인/봇차단). 하지만 **순위·가격·판매처·키워드**는 `design-division/tools/naver_search.py`(검색 API)로 봇차단 없이 수집한다. 키는 `.env`의 `NAVER_CLIENT_ID/SECRET`. → scout는 이걸로 경쟁세트를 잡고, 상세 분석은 스크린샷/브라우저로 보완.
- **상세페이지 소스화(봇차단 우회)**: ①회장이 playwright 브라우저에 네이버 로그인 1회(에이전트는 비번 입력 금지) → 로그인 상태로 상품 페이지 열어 읽기, 또는 ②회장이 브라우저에서 페이지 저장(HTML) → `design-division/tools/naver_page_parser.py`로 구조(이미지수·텍스트·가격) 변환 → scout 해부. 상세 본문은 대부분 이미지라 '이미지 URL+텍스트'가 추출된다.

## 디자인 파이프라인 사용법 (`design-division/`)
```bash
cd design-division
pip install -r requirements.txt
cp .env.example .env          # 가진 API 키만 채움 (없어도 드라이런 동작)
python -m edge_design.cli build briefs/sample_ceiling_fan.yaml -o output
# 산출물: output/<제품>/detail_page.html (미리보기) + mangoboard/작업지시서.md (망고보드 조립)
```

## 현재 상태 (2026-06 기준)
- ✅ 7개 팀 에이전트, 디자인 파이프라인, 망고보드 연동, 캔바 MCP 등록 완료
- ⏳ 실제 API 키 / 실제 아크로 제품 데이터 투입 전 (드라이런 단계)
- 작업 브랜치: `claude/friendly-thompson-NDkKH`

## 새 세션에서 회장이 흔히 하는 말 → 본부장 행동
- "캔바 연결 확인하고 시작하자" → `/mcp`로 canva connected 확인 후 보고
- "실링팬 이걸로 시작하자" (+사진/스펙) → briefs/ 에 브리프 작성 → 파이프라인 가동 → 결과 보고
- "점수 매겨봐" → 팀별 현황 솔직 채점
