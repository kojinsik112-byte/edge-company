# 인수인계서 (HANDOVER) — 아크로 슬림 상세페이지 프로젝트
> 작성: 본부장(Claude) · 2026-06-08 · 새 세션이 이 문서 + `memory/`를 읽고 그대로 이어받는다.

## 0. 회장 지시 (최신 방향)
- **팀 가시성 필수**: "어느 팀이 어떤 일을 했는지" 보여야 한다. 뭉뚱그린 결과물 = 감점(75점). → **모든 결과물에 '팀 기여 로그'를 붙인다.**
- **팀 확장**: 현재 **39팀** → 30·50·100팀으로 키운다. (회장은 1인 대표, 팀=에이전트)
- 과대광고 금지, 결론부터 솔직히, 실사·실데이터 우선(AI는 임시).

## 1. 현재 산출물 (아크로 슬림 상세페이지)
- 본 파일: `design-division/output/슬림아크로/slim_final.html` → 렌더 `slim_final.png` (약 30섹션, 화이트·시원 톤, ARCO 단독)
- 모션: `arco_motor_spin.gif`(BLDC, 채택) / `arco_slim_spin.gif`(팬, 약함→페이지서 제외)
- 실사: `ai/real_install.jpg`(시공) `real_blades.jpg`(오크·월넛) `real_chrome.jpg` — 회장 제공, Downloads에서 복사
- 색상 4종(실사 기준 생성): `ai/r_white/r_oak/r_walnut/r_chrome.png`

## 2. 팀 기여 로그 (이번 프로젝트 — 누가 뭘 했나)
| 팀 | 한 일 | 산출물 |
|---|---|---|
| scout | 네이버 경쟁사 9곳 직접 정독(CDP) + 갭 분석 | `scout_reports/competitors/`, `competitor_sove_ver3.md` |
| planner | 30섹션 롱폼 구조·배치 설계 | 페이지 섹션 순서 |
| writer | 전 섹션 카피(오리지널), 실Q&A 기반 FAQ | 본문 카피 |
| art_director | 화이트·시원 톤 디자인시스템(Pretendard·틸) | 브랜드킷 적용 |
| designer | AI 이미지(제품/연출/모터) + 모션 GIF | `ai/*.png`, `*.gif` |
| infographic | 14.5 하우징 3단비교·dB·스펙 | 인포그래픽 섹션 |
| cro | 가격 앵커링(309↔159), 저렴반론, 신뢰배지 | 전환 섹션 |
| product_strategy/ecosystem | 생태계 Before/After, ONLY ARCO | 차별화 섹션 |
| scout+창의 | 선풍기vs실링팬·계절별·전기료 아이디어 | 신규 섹션 |
| auditor/legal | 과대광고 0 검수, 엣지컴퍼니 표기 제거 | 컴플라이언스 |

## 2-B. 소셜·콘텐츠 본부 신설 + 첫 콘텐츠팩 (2026-06-08 추가)
회장 지시("촬영 대본·검색어분석·1인촬영지원·바로업로드 팀이 필요")로 **6팀 신설(39→45팀)**, 즉시 아크로 슬림 런칭 콘텐츠팩 제작.

| 팀(신규) | 한 일 | 산출물 |
|---|---|---|
| content_director | 5기둥 전략 + 8편 캘린더 + batch촬영 설계 | `content/calendar_2026-W23.md` |
| social_trend | IG/틱톡/유튜브숏츠/네이버 실웹조사(해시태그·포맷) | `content/trend/2026-W23_trendpack.md` |
| shorts_writer | 런칭3편 컷대본(후킹3안·컷시트·자막·CTA) | `content/scripts/01·02·05*.md` |
| shoot_director | 1인 폰촬영 샷리스트·조명·체크리스트 | `content/shootlist/batchA·B*.md` |
| caption_writer | 3편×4플랫폼 복붙 캡션·해시태그 | `content/captions/*.md` |
| social_publisher | 규격·업로드패키지·자동발행 가이드(현실판) | `content/publish/PUBLISH_GUIDE.md` |

**회장 결정/제공 필요(콘텐츠 발행 막는 2개):**
- ⚠️ 자동발행 연동: 인스타 Graph API(프로계정+페북+토큰)·유튜브 Data API(OAuth) 먼저. 미연동 시 수동 패키지로 발행은 가능.
- ⚠️ 실측 콘텐츠(소음dB·전기료 ASMR/정보영상)는 실측값 받아야 촬영 가능.

## 3. 남은 일 (TODO)
- [ ] 실데이터: 소음 dB·소비전력 **실측값**, 시공비 정확단가, **실제 구매후기**
- [ ] 회장 실사 추가 촬영 → AI 이미지 100% 실물 교체 (제품단독/4색상/설치과정/공간연출)
- [ ] 실제 동영상 파일 → 영상 섹션 삽입
- [ ] operator: 네이버 등록 패키지(SEO 상품명·태그·옵션·필수표기) ← **다음 우선순위**
- [ ] 소셜 자동발행 연동(인스타 Graph API → 유튜브 Data API) + 실측 콘텐츠 촬영
- [~] 팀 확장(39→**45** 완료, 목표 100) / 팀 가시성=팀기여로그 운영 중

## 4. 핵심 인프라 (작동 확인됨 — `memory/` 참조)
- 네이버 접근: 디버그 Chrome(포트 9222) + Playwright `connectOverCDP` → `tools/scraper/naver_cdp.js` ([[naver-data-infra]])
- AI 이미지: Gemini 결제키(`.env GOOGLE_API_KEY`) + `tools/gen_image.py`, 한글은 HTML로 ([[ai-image-pipeline]])
- 검색 API: `tools/naver_search.py`
- 비용원칙: 이미지 생성만 결제 OK, **Veo 영상 금지**

## 5. 새 세션 시작 시
1. 이 문서 + `CLAUDE.md` + `memory/MEMORY.md` 읽기
2. `git pull`로 팀 최신 동기화 (현재 45팀)
3. 회장에게 "어디서 이어갈지" 확인 후 진행
