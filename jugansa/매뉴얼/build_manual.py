"""AI 입찰본부 사용설명서 PDF 빌더 — python build_manual.py → 같은 폴더에 HTML + PDF.

내용은 이 파일의 데이터(TEAMS · FLOW · PROMPTS …)만 고치면 된다. 개인정보 없음(깃에 올라감).
"""
import html
import os
import pathlib
import shutil
import subprocess

import fitz  # PyMuPDF — 쪽 번호

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "엣지컴퍼니_AI입찰본부_사용설명서"
DATE = "2026.10.20"
e = html.escape

# ------------------------------------------------------------------ 내용
FLOW = [  # 단계 · 팀 · 본부장이 할 일
    ("0", "공고 전", "신규 개척 · 공고 감시", "카페 가입 · 쪽지 보내기 · 미팅"),
    ("1", "착수", "/kickoff — 분석 4팀 + 비주얼", "참여 · 지원금 결정"),
    ("2", "제작", "제안서 빌더 · 제출서류 · 비주얼", "확정 숫자 · 자료 · 사진 주기"),
    ("3", "점검", "미비 점검 · /court", "고칠 것 한 번에 지시"),
    ("4", "날인", "제출서류 담당", "법인인감 실물 날인 · 스캔"),
    ("5", "발송", "접수·발송 · 비주얼(GIF)", "메일 발송"),
    ("6", "PT", "PT 발표 코치", "리허설 · 발표"),
    ("7", "결과", "결과 분석", "결과 한 줄 알려 주기"),
]

TEAMS = [  # (구역, 이름, 영문, 하는 일, 이렇게 말하세요, 결과물, 본부장 몫)
    ("공고 전", "신규 개척팀", "bid_outreach",
     "입예협 · 입주 카페 찾기 → 가입 답변 → 운영진 인사 3안 → 소개 요약본 → 미팅 대본 · 질문지 → 감사 · 후속",
     "[단지] 개척팩 만들어줘 (카페 주소 · 아는 정보)\n[단지] 미팅 잡혔어 (날짜)",
     "jugansa/개척/[단지]/개척팩.md · 요약본 6쪽", "가입 · 쪽지 발송 · 미팅(직접)"),
    ("공고 전", "공고 감시팀", "bid_watch",
     "네이버 카페 전체검색('주관사 공고' 등 6개) + 지정 카페 4곳을 하루 4번(09 · 12 · 15 · 18시) 찾아 새 공고만 카톡",
     "감시 결과 보여줘\n검색어 추가해줘 ○○",
     "카톡 알림 · jugansa/watch/state/log.md", "사무실 PC에 1회 설치 · 네이버 로그인 1회"),
    ("착수", "/kickoff (착수)", "skill",
     "공고를 받으면 5팀(공고 · 단지 · 카페 · 손익 · 비주얼)을 동시에 돌려 착수 보고서 1장",
     "/kickoff [단지]  (+공고 첨부)\n착수해줘 · 공고 분석해줘",
     "착수 보고서(결론 · 점수 · 지원금 상한 · 체크리스트 · 함정 · 질의 메일 · 질문 5)", "참여 여부 · 지원금 결정"),
    ("착수", "공고분석관", "bid_notice_analyst",
     "공고 · 지침서 해부 → 제출서류 · 자격 · 평가표 · 날인 · 발급일 조건 · 함정 조항 · 질의 메일", "(/kickoff가 부름)", "공고 체크리스트", "—"),
    ("착수", "단지분석", "realestate_analyst",
     "세대 · 타입 · 시공사 · 입주 시기 · 분양 현황 · '실제 찰 세대'", "(/kickoff가 부름)", "단지 카드", "—"),
    ("착수", "카페인사이트", "cafe_insight",
     "입주 카페 관심사(하자 · 옵션 · 공구 · 일정) 상위 5", "(/kickoff가 부름)", "관심사 + 제안서 한 줄", "—"),
    ("착수", "손익분석관", "bid_economist",
     "사업성 100점 · 순익 3안(보수 · 기준 · 상단) · 지원금 상한", "(/kickoff가 부름)\n[단지] 지원금 얼마까지 돼?", "손익표 · 상한 권고", "—"),
    ("제작", "PT·제안서 빌더", "pt_builder",
     "기존 단지 빌더 복제 → 07장 단지 맞춤(공고 대응표 · 일정 · 자격 · 실적)", "[기존 단지] 복제해서 [단지] 전체 만들어줘. 지원금 N만원 · 작성일 ○○. 업로드는 하지마",
     "제안서 PDF · 요약제안서", "확정 숫자 · 단지 사진"),
    ("제작", "단지 비주얼팀", "bid_visual",
     "조감도 수집(출처) · 보정 · 경관조명 연출 프롬프트 · 낮 → 밤 → 조명 GIF(10MB 이내)", "[단지] 경관조명 GIF 만들어줘 (사진 첨부)",
     "GIF · 보정 사진 · 연출 프롬프트", "야간 연출 이미지(필요 시 직접 생성)"),
    ("제작", "제출서류 담당", "bid_docs",
     "별지 원문 그대로 · 증빙 발급일 · 가림 · 직인 · 공고 순서대로 PDF 1개", "[단지] 제출서류 만들어줘\n[단지] 사용인감계 스캔 올렸어 — 최종본",
     "제출본 PDF · 제출현황.txt", "법인인감 실물 날인 · 스캔"),
    ("점검", "미비 점검", "bid_docs",
     "공고 기준 빠진 서류 · 발급 기한 · 날인 종류 · 노란 칸 · 증빙 없는 실적", "[단지] 서류 미비 확인해줘", "🔴 탈락 / 🟠 감점 / 🟡 다듬기 표", "—"),
    ("점검", "/court (법정 검토)", "skill",
     "검사(공격) → 변호(반박) → 판사(판결) — 탈락 · 허위 · 지킬 수 없는 약속 · 과장", "/court [단지] 제출본\n/court [단지] 제출본 정밀판",
     "판결표(위험 · 쪽 · 지적 · 고칠 방법 · 담당)", "답이 필요한 항목 결정"),
    ("점검", "검수 · 법무", "auditor · legal", "사실 · 표절 · 표시광고 · 법적 위험", "(/court가 부름)", "검수 의견", "—"),
    ("발송", "행사장 조사관", "bid_venue", "행사장 후보 3곳 · 면적 · 거리 · 요금 · 개관", "[단지] 근처 행사장 후보 3곳", "후보표", "대관 문의"),
    ("발송", "접수·발송 담당", "bid_mail", "메일 제목 · 파일명 공고 형식 · 본문 · 디자인 메일(GIF) · 발송 체크리스트",
     "[단지] 제출 메일 문구 + 디자인 만들어줘", "메일 문구 · HTML · 체크리스트", "메일 발송(직접)"),
    ("관제", "마감 관제팀", "bid_pmo", "마감 순 현황판 · 증빙 유효기간 · 본부장 대기 목록 · 겹치는 마감 경보",
     "현황판 갱신해줘\n이번 주 마감 뭐 있어?", "jugansa/입찰현황판.md", "대기 목록 한 번에 처리"),
    ("PT", "PT 발표 코치", "bid_pt_coach", "발표 쪽 고르기 · 쪽별 대본 · 예상 질문 20 + 답 · 리허설 시트",
     "[단지] PT 준비해줘 (발표 N분 · 질의 N분)", "대본 · 질문지 · 리허설 시트", "리허설 · 발표"),
    ("결과", "결과 분석팀", "bid_retro", "선정 · 탈락 → 평가표 역추적 → 이기는 · 지는 패턴 누적 → 규칙 제안",
     "[단지] 결과 나왔어 — 선정/탈락, 들은 내용", "jugansa/입찰_결과분석.md", "결과 한 줄 알려 주기"),
]

PROMPTS = [  # 상황 · 그대로 복사
    ("새 공고", "/kickoff 상주자이르네  (+공고 · 별지 양식 첨부)"),
    ("전체 만들기", "북수원 빌더 복제해서 [단지] 전체 만들어줘(제안서 + 제출서류 PDF 1개). 지원금 12만원 · 작성일 10.26 · 실적은 북수원 방식. 업로드는 하지마."),
    ("한 번에 고치기", "[단지] 수정: 1) 43쪽 ○○ → △△ 2) 70쪽 03행 ○○ 3) 작성일 10.22. 다 반영하고 업로드는 하지마."),
    ("미비 점검", "[단지] 공고 기준으로 서류 미비 확인해줘 — 발급 기한, 날인 종류, 증빙 없는 실적, 노란 칸."),
    ("법정 검토", "/court [단지] 제출본"),
    ("날인 반영", "[단지] 사용인감계 날인 스캔 올렸어. 최종본 만들어줘."),
    ("GIF + 메일", "[단지] 경관조명 GIF 만들어줘. 그다음 제출 메일 문구 + 디자인도."),
    ("현황 확인", "현황판 갱신해줘 · 이번 주 본부장 할 일만 뽑아줘."),
    ("개척", "[단지] 개척팩 만들어줘. 카페 주소 ○○, 입주 2028.05, 세대 1,200."),
    ("PT", "[단지] PT 준비해줘. 발표 25분 · 질의 25분 · 대표 발표."),
    ("결과", "[단지] 결과 나왔어 — 탈락, 1위는 지원금 18만원이었대."),
    ("규칙 고정", "앞으로 항상 [규칙] 해줘. 메모에 적어줘."),
    ("업로드", "[단지] 제출 준비 — 보관함에 올려줘."),
]

RULES = [
    ("법인인감은 디지털로 만들지 않습니다", "출력용 PDF → 실물 날인 → 스캔만. 직인(사용인감)만 투명 PNG로 찍습니다."),
    ("메일용(저용량) PDF는 만들지 않습니다", "원본 그대로 네이버 대용량 첨부로 보냅니다(10-20 지시)."),
    ("업로드는 말씀하실 때만", "'올려줘'는 그 회차 한 번만 유효. 보관함 업로드는 하루 200개 한도(KST 09:00 초기화)."),
    ("허위 · 견본 금지", "견본 등록증 · 없는 보증 가입 실적 · 수임 누계를 주관 실적으로 쓰지 않습니다."),
    ("지킬 수 있는 숫자만", "제안서 = 협약서 효력. '최대 10년' 같은 약속은 넣지 않습니다(탕정 10-20 정정)."),
    ("과장 표현 금지", "최고 · 유일 · 100% · 완벽 대신 숫자로."),
    ("개인정보는 깃에 올리지 않습니다", "제출본 · 증빙 · 명부 · 운영진 연락처는 작업 공간에만. 입주민 닉네임은 가립니다."),
    ("입주민 사칭 금지", "카페에서는 업체임을 밝히고 운영진 쪽지 · 제휴 게시판으로만."),
    ("네이버 비밀번호는 주지 않습니다", "로그인은 본부장님이 PC 브라우저에서 직접 1번 — 이후 자동."),
]

ROUTINE = [
    ("매일 아침", ["카톡: 공고 감시 알림 확인(새 공고 → '/kickoff [단지]')", "'현황판 갱신해줘' → 오늘 할 일 3줄 확인", "지시는 단지별로 묶어서 한 번에"]),
    ("매주 월요일", ["'이번 주 마감 · 날인 · 재발급 뽑아줘'", "날인 스캔은 한 번에 모아서(출력 → 날인 → 스캔)", "개척 단지 후속 연락(1주 규칙)"]),
    ("매달 초", ["사업자등록증 · 등기 · 국세 · 지방세 · 인감증명서 재발급(공고마다 '1개월 이내')", "4대보험 명부(입사 · 퇴사 반영)", "NICE 등급확인서 필요 여부"]),
    ("공고 1건 (D-14 → D-0)", ["D-14 /kickoff · 참여 결정 · 질의 메일", "D-10 전체 빌드 · 노란 칸 채우기", "D-5 미비 점검 · /court · 한 번에 고치기", "D-3 법인인감 날인 · 스캔 → 최종본", "D-1 GIF · 메일 · 체크리스트 · 보관함 보관", "D-0 발송 · 수신 확인 · 현황판 '발송 완료'"]),
]

DEVICES = [
    ("아무 컴퓨터 · 휴대폰", "claude.ai/code 또는 Claude 앱", "제안서 · 서류 빌드 · 문구 · GIF · 분석 — 작업은 저장소에 저장돼 어디서나 같음"),
    ("사무실 컴퓨터(본부)", "Claude 데스크탑 앱 또는 저장소 폴더에서 'claude remote-control'", "위 전부 + 네이버 로그인 작업 · 공고 감시기(이 한 대에만 설치)"),
    ("개인 PC · 휴대폰 → 사무실", "사무실 세션이 Claude 앱에 뜸 → 이어서 조작", "외부에서도 사무실 PC로 네이버 작업 지시(사무실 PC 켜 두기)"),
]

WATCH_SETUP = [
    "네이버 검색 API 키 → design-division/.env (NAVER_CLIENT_ID · SECRET)",
    "카톡 인증 1번 → business-ops/secretary/tools/kakao_send.py 안내대로(본부장 계정)",
    "카페 4곳: 카페 안에서 '주관사' 검색 → 주소 복사 → jugansa/watch/watch_config.json",
    "로그인 1번: tools/scraper 에서 npm install → node cafe_watch.js --login → 직접 로그인 → 창 닫기",
    "첫 실행: python jugansa/watch/notice_watch.py --init",
    "예약 등록: powershell -ExecutionPolicy Bypass -File jugansa/watch/register_watch.ps1",
]

EFFORT = [
    ("Opus 5.5 (전 팀 기본 · 본부장 10-20 확정)", "노력도 high 기본 · /court · 제출 전 최종 검토는 xhigh"),
    ("재조립 · 파일 정리", "medium 이하로 충분"),
    ("모델 · 노력도 바꾸기", "Claude Code에서 /model"),
]

FAQ = [
    ("카톡 알림이 안 와요", "사무실 PC가 꺼져 있었거나 카톡 인증 만료 → 'python notice_watch.py --dry'로 확인, 인증은 kakao_send.py 다시"),
    ("카페 감시만 안 돼요", "네이버 로그인이 풀림 → node cafe_watch.js --login 다시(감시기 화면에 안내가 뜸)"),
    ("제출본 파일이 없어졌어요", "작업 공간은 오래 쉬면 비워짐 → 빌더로 다시 만들 수 있음. 스캔 · 증빙 원본은 다시 받아야 하니 발송 전 '보관함에 올려줘'"),
    ("파일이 너무 커요", "실제 제출본 크기와 보관함 업로드 합계(조각 중복)는 다름 — '실제 제출본 크기 알려줘'"),
    ("업로드가 안 돼요", "하루 200개 한도 → KST 09:00 이후 다시. 바뀐 파일만 올림"),
    ("팀 이름을 몰라요", "몰라도 됩니다 — 하고 싶은 일을 말씀하시면 맞는 팀을 부릅니다"),
]

FILES = [
    ("단지 폴더", "jugansa/[단지]/ — build_xx.py(제안서) · docs_xx.py(제출서류) · data.py(숫자는 여기 한 곳)"),
    ("현황 · 결과", "jugansa/입찰현황판.md · jugansa/입찰_결과분석.md"),
    ("개척 · 감시", "jugansa/개척/_기본문구.md · jugansa/watch/(README · 설정 · 기록)"),
    ("규칙 · 팀", "jugansa/CLAUDE.md · .claude/agents/bid_*.md · .claude/skills/kickoff · court"),
    ("GIF 도구", "jugansa/tools/lx_gif.py · align_pair.py"),
]

# ------------------------------------------------------------------ HTML
CSS = """
@page{size:A4;margin:16mm 15mm 18mm}
*{box-sizing:border-box}body{margin:0;font-family:Pretendard,'Noto Sans KR',sans-serif;color:#1B2433;font-size:10pt;line-height:1.55;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.cover{height:262mm;background:#0D1E33;color:#fff;border-radius:6px;padding:28mm 18mm;display:flex;flex-direction:column;justify-content:space-between;page-break-after:always}
.cover .eg{font:700 13pt Pretendard;color:#E3C47A;letter-spacing:.3em}.cover h1{font-size:30pt;line-height:1.25;margin:0 0 8mm;font-weight:800}.cover h1 b{color:#E3C47A}
.cover p{color:#C9D3E3;font-size:11.5pt;margin:2mm 0}.cover .foot{border-top:1px solid #33465F;padding-top:5mm;color:#9FB0C8;font-size:9.5pt}
h2{font-size:16pt;color:#0D1E33;margin:0 0 4mm;padding-bottom:2mm;border-bottom:2.5px solid #C9A24B;page-break-after:avoid}h2 small{font-size:9.5pt;color:#8A96A8;font-weight:500;margin-left:3mm}
h3{font-size:11.5pt;color:#0D1E33;margin:5mm 0 2mm;page-break-after:avoid}
.sec{page-break-before:always}.lead{color:#4A5568;margin:0 0 4mm}
table{width:100%;border-collapse:collapse;margin:2mm 0 4mm;font-size:9pt;page-break-inside:auto}tr{page-break-inside:avoid}
th{background:#0D1E33;color:#fff;font-weight:600;padding:1.6mm 2.2mm;text-align:left}td{padding:1.5mm 2.2mm;border-bottom:1px solid #E2E6EC;vertical-align:top}
tr:nth-child(even) td{background:#F7F8FA}
.flow{display:grid;grid-template-columns:repeat(4,1fr);gap:3mm;margin:3mm 0 5mm}
.st{border:1px solid #D8DEE7;border-radius:5px;padding:3mm;background:#fff}.st .n{display:inline-block;background:#C9A24B;color:#fff;font-weight:700;border-radius:3px;padding:0 2mm;font-size:9pt}
.st .t{font-weight:700;font-size:11pt;margin:1.5mm 0 1mm;color:#0D1E33}.st .w{font-size:8.6pt;color:#4A5568}.st .m{font-size:8.4pt;color:#9A7420;margin-top:1.5mm;border-top:1px dashed #E3D3A8;padding-top:1.2mm}
.card{border:1px solid #D8DEE7;border-left:4px solid #C9A24B;border-radius:4px;padding:2.6mm 3.2mm;margin:0 0 2.6mm;page-break-inside:avoid}
.card .h{display:flex;align-items:baseline;gap:2mm}.card .h b{font-size:11pt;color:#0D1E33}.card .h code{font-size:8pt;color:#7A8698}.card .h .z{margin-left:auto;font-size:8pt;background:#EEF1F5;border-radius:3px;padding:.3mm 2mm;color:#4A5568}
.card .d{margin:1mm 0 1.5mm;font-size:9.2pt}.kv{display:grid;grid-template-columns:20mm 1fr;gap:.6mm 2mm;font-size:8.8pt}.kv span{color:#7A8698}
pre{margin:0;font:500 8.9pt/1.5 Pretendard,'Noto Sans KR',sans-serif;white-space:pre-wrap;background:#F3F5F8;border-radius:3px;padding:1.2mm 2mm;color:#13213A}
.box{background:#0D1E33;color:#fff;border-radius:5px;padding:4mm 5mm;margin:3mm 0;page-break-inside:avoid}.box b{color:#E3C47A}
.tip{background:#FBF6EA;border:1px solid #EAD9AE;border-radius:4px;padding:3mm 4mm;margin:3mm 0;font-size:9.3pt;page-break-inside:avoid}.tip b{color:#9A7420}
ol,ul{margin:1mm 0 2mm;padding-left:5mm}li{margin:.8mm 0}
.two{display:grid;grid-template-columns:1fr 1fr;gap:4mm}
"""


def br(s):
    return "<br>".join(e(x) for x in s.split("\n"))


def build():
    p = []
    p.append(f"""<div class="cover"><div><div class="eg">EDGE COMPANY</div></div>
<div><h1>AI 입찰본부<br><b>사용설명서</b></h1>
<p>입주박람회 주관사 입찰 — 공고 전 개척부터 결과 분석까지</p>
<p>{len(TEAMS)}개 팀 · 스킬을 '말 한마디'로 쓰는 법</p></div>
<div class="foot">주관사업 총괄 본부장 윤현욱 · {DATE} · 주식회사 엣지컴퍼니</div></div>""")

    # 1 한눈에
    flow = "".join(f'<div class="st"><span class="n">{n}</span><div class="t">{e(t)}</div><div class="w">{e(w)}</div><div class="m">본부장 · {e(m)}</div></div>' for n, t, w, m in FLOW)
    p.append(f"""<div><h2>1. 한눈에 보기<small>8단계 흐름</small></h2>
<p class="lead">팀 이름을 외울 필요가 없습니다. <b>하고 싶은 일을 말씀하시면</b> Claude 총괄이 맞는 팀을 불러 일을 나눠 줍니다. 본부장님은 <b>결정 · 날인 · 발송 · 만남</b>만 하시면 됩니다.</p>
<div class="flow">{flow}</div>
<div class="box">핵심 원리 3가지 — <b>① 묶어서 지시</b>("1) 2) 3)" 한 번에 → 다시 만드는 횟수가 줄어듦) · <b>② 업로드 여부는 끝에 한마디</b>(말 없으면 만들기만) · <b>③ 확정값은 숫자로</b>("지원금 12만원 · 작성일 10.26" — 애매하면 노란 칸으로 남김)</div>
<h3>조직도</h3>
<pre>              본부장 (결정 · 날인 · 발송 · 만남)
                          │
               Claude 총괄 (지휘 · 빌드 · 검증)
                          │
 공고 전 ── 신규 개척 · 공고 감시
 착수   ── /kickoff → 공고분석 · 단지분석 · 카페인사이트 · 손익분석 · 비주얼
 제작   ── PT·제안서 빌더 · 단지 비주얼 · 제출서류
 점검   ── 미비 점검 · /court(검사 → 변호 → 판사) · 검수 · 법무
 발송   ── 행사장 조사 · 접수·발송
 관제   ── 마감 관제(현황판)
 PT · 결과 ── PT 발표 코치 · 결과 분석</pre></div>""")

    # 2 팀 카드
    cards = []
    zone = None
    for z, name, en, what, say, out, me in TEAMS:
        if z != zone:
            cards.append(f"<h3>{e(z)}</h3>")
            zone = z
        cards.append(f"""<div class="card"><div class="h"><b>{e(name)}</b><code>{e(en)}</code><span class="z">{e(z)}</span></div>
<div class="d">{e(what)}</div><div class="kv"><span>이렇게 말씀</span><pre>{e(say)}</pre><span>결과물</span><div>{e(out)}</div><span>본부장 몫</span><div>{e(me)}</div></div></div>""")
    p.append(f'<div class="sec"><h2>2. 팀별 사용법<small>{len(TEAMS)}개 팀 · 스킬</small></h2>{"".join(cards)}</div>')

    # 3 프롬프트
    rows = "".join(f"<tr><td style='width:22mm'><b>{e(a)}</b></td><td><pre>{e(b)}</pre></td></tr>" for a, b in PROMPTS)
    p.append(f"""<div class="sec"><h2>3. 바로 쓰는 지시문<small>복사해서 단지명만 바꾸기</small></h2>
<table><tr><th>상황</th><th>이렇게 말씀하세요</th></tr>{rows}</table>
<div class="tip"><b>쪽 번호</b>는 슬라이드 <b>오른쪽 위 번호</b> 기준으로 말씀하세요(PDF 몇 번째 장과 다를 수 있음). <b>사진 · 서류</b>는 지시와 <b>같은 메시지</b>에 붙이면 질문이 줄어듭니다.</div></div>""")

    # 4 본부장 가이드
    rt = "".join(f"<h3>{e(t)}</h3><ul>{''.join(f'<li>{e(x)}</li>' for x in xs)}</ul>" for t, xs in ROUTINE)
    p.append(f"""<div class="sec"><h2>4. 본부장 가이드<small>루틴 · 일정 · 잘 쓰는 법</small></h2>
<div class="two"><div>{rt}</div><div>
<h3>이렇게 하면 빨라집니다</h3><ul>
<li><b>날인은 모아서</b> — 단지별 출력용 PDF를 한 번에 출력 → 날인 → 스캔 1묶음</li>
<li><b>결정은 표로</b> — 제가 묻는 질문은 '추천안이 첫 번째'. 그대로면 "추천대로"</li>
<li><b>새 공고는 바로 /kickoff</b> — 착수가 하루 빠르면 질의 · 협력 계약 시간이 생김</li>
<li><b>결과는 꼭 알려 주기</b> — 5건이 쌓이면 지원금 · 실적 표현의 '이기는 공식'이 보임</li>
<li><b>규칙은 고정</b> — 두 번 말한 지시는 "메모에 적어줘"</li></ul>
<h3>피하면 좋은 것</h3><ul>
<li>조각조각 수정 지시(빌드 · 업로드가 늘어남)</li>
<li>발송 직전 큰 수정(점검 · 법정 검토를 다시 해야 함)</li>
<li>비밀번호 · 개인정보를 채팅에 적기</li></ul>
<div class="tip"><b>신규 개척 한 줄 전략</b> — "뽑아 주세요"보다 "이걸 무료로 드립니다"(입주 일정표 · 가격 비교표 · 공고 예시). 자료를 받은 운영진이 공고 때 먼저 연락합니다.</div>
</div></div></div>""")

    # 5 기기 · 설치
    dv = "".join(f"<tr><td><b>{e(a)}</b></td><td>{e(b)}</td><td>{e(c)}</td></tr>" for a, b, c in DEVICES)
    ws = "".join(f"<li>{e(x)}</li>" for x in WATCH_SETUP)
    ef = "".join(f"<tr><td><b>{e(a)}</b></td><td>{e(b)}</td></tr>" for a, b in EFFORT)
    fl = "".join(f"<tr><td><b>{e(a)}</b></td><td>{e(b)}</td></tr>" for a, b in FILES)
    p.append(f"""<div class="sec"><h2>5. 어디서 · 무엇으로<small>기기 · 감시기 설치 · 모델 · 파일</small></h2>
<table><tr><th style="width:36mm">어디서</th><th style="width:58mm">방법</th><th>되는 일</th></tr>{dv}</table>
<h3>공고 감시기 설치 (사무실 PC · 처음 10분)</h3><ol>{ws}</ol>
<div class="tip">감시기는 <b>사무실 PC 한 대에만</b> — 두 대면 카톡이 두 번 옵니다. PC가 꺼져 있던 시간은 켜질 때 이어서 돕니다. 자세히는 <b>jugansa/watch/README.md</b>.</div>
<h3>모델 · 노력도</h3><table><tr><th style="width:62mm">구분</th><th>설정</th></tr>{ef}</table>
<h3>파일 위치</h3><table><tr><th style="width:26mm">무엇</th><th>어디</th></tr>{fl}</table></div>""")

    # 6 규칙 · FAQ · 파일
    rl = "".join(f"<tr><td style='width:62mm'><b>{e(a)}</b></td><td>{e(b)}</td></tr>" for a, b in RULES)
    fq = "".join(f"<tr><td style='width:46mm'><b>{e(a)}</b></td><td>{e(b)}</td></tr>" for a, b in FAQ)
    p.append(f"""<div class="sec"><h2>6. 꼭 지키는 규칙<small>모든 팀 공통</small></h2>
<table><tr><th>규칙</th><th>내용</th></tr>{rl}</table>
<h2 style="margin-top:6mm">7. 자주 묻는 것</h2><table><tr><th>이럴 때</th><th>이렇게</th></tr>{fq}</table>
<div class="box">연락처 — 주관사업 총괄 본부장 <b>010-7273-9901</b> · edgecompany1@naver.com</div></div>""")
    return f"<!doctype html><html lang='ko'><head><meta charset='utf-8'><title>AI 입찰본부 사용설명서</title><style>{CSS}</style></head><body>{''.join(p)}</body></html>"


def chrome():
    for c in ("/opt/pw-browsers/chromium", shutil.which("chromium"), shutil.which("google-chrome"),
              r"C:\Program Files\Google\Chrome\Application\chrome.exe"):
        if c and os.path.exists(c):
            return c
    raise SystemExit("크롬을 찾지 못함")


def main():
    h = OUT.with_suffix(".html")
    h.write_text(build(), encoding="utf-8")
    tmp = OUT.with_name(OUT.name + "_tmp.pdf")
    subprocess.run([chrome(), "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={tmp}", h.as_uri()], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    d = fitz.open(tmp)
    for i, pg in enumerate(d):  # 쪽 번호(표지 제외)
        if i:
            r = pg.rect
            pg.insert_text((r.width - 30, r.height - 22), f"{i + 1} / {len(d)}", fontsize=7.5, color=(0.5, 0.55, 0.62))
            pg.insert_text((42, r.height - 22), "EDGE COMPANY · AI 입찰본부 사용설명서", fontsize=7.5, fontname="korea", color=(0.5, 0.55, 0.62))
    d.set_metadata({"title": "AI 입찰본부 사용설명서", "author": "주식회사 엣지컴퍼니"})
    pdf = OUT.with_suffix(".pdf")
    d.save(pdf, garbage=3, deflate=True)
    d.close()
    tmp.unlink()
    print(f"{pdf}  {len(fitz.open(pdf))}쪽 · {pdf.stat().st_size / 1e6:.2f}MB")


if __name__ == "__main__":
    main()
