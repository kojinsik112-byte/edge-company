# -*- coding: utf-8 -*-
"""탕정 밝은 바탕 제출본 — 디자인 레이어(10-21 본부장: '최고의 디자이너로 분석해서 고급스럽게'). tjlight.py가 색을 바꾼 뒤 적용.

방향 = 고급 주거 브로슈어(아이보리 종이 · 깊은 남색 · 샴페인 금색 · 명조 대제목 · 가는 금색 선 · 흰 카드)
  대제목      : 모든 쪽 제목 · 간지 · 표지 = Noto Serif KR(명조) · 장 번호 · 큰 숫자 = Cormorant Garamond
  표지 · 마지막: 금색 안쪽 테두리 · 명조 제목 · 금색 선 라벨
  간지        : 깊은 남색 + 은은한 빛 · 금색 테두리 · 큰 외곽선 장 번호 · 2열 목록 · 아래 띠
  15만원 쪽   : 증서(이중 금테 · 모서리 장식 · 큰 세리프 숫자 · 대상 / 총 규모 / 받는 방식)
  배치도 · 콜센터 : 흰 카드 + 샴페인 금색(남색 판 없앰)
  사진 캡션   : 어두운 띠 → 밝은 라벨 띠(금색 윗선)
  KEY POINT  : 남색 유지 · 왼쪽 금색 선 · 세리프 라벨
글꼴 = ../_fonts/fonts.css(구글 폰트 OFL · 로컬 사본 — 없으면 ensure_fonts()가 받음 · PDF에 내장)
"""
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "..", "_fonts")
FONT_LINK = '<link rel="stylesheet" href="../_fonts/fonts.css">'
GF = "https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@600;700;900&family=Cormorant+Garamond:wght@500;600;700&display=swap"

SERIF = "'Noto Serif KR','Nanum Myeongjo','AppleMyungjo',serif"
DISPLAY = "'Cormorant Garamond','Noto Serif KR',Georgia,serif"
NAVY, INK, PAPER = "#0D1E33", "#14243A", "#FAF7F0"
CHAMP, GOLD_HEAD, GOLD_TXT, GOLD_LT = "#B8955A", "#93702F", "#7A5716", "#E2C58C"


def ensure_fonts():
    """로컬 글꼴 사본이 없으면 구글 폰트에서 받아 상대 경로 CSS로 저장(본부장 PC에서도 같은 결과)."""
    css_path = os.path.join(FONT_DIR, "fonts.css")
    if os.path.exists(css_path) and len(os.listdir(FONT_DIR)) > 50:
        return
    os.makedirs(FONT_DIR, exist_ok=True)
    ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
    css = urllib.request.urlopen(urllib.request.Request(GF, headers=ua), timeout=60).read().decode()
    for u in sorted(set(re.findall(r"https://fonts\.gstatic\.com/s/[^)]+", css))):
        f = os.path.join(FONT_DIR, u.split("/s/", 1)[1].replace("/", "_"))
        if not os.path.exists(f):
            open(f, "wb").write(urllib.request.urlopen(urllib.request.Request(u, headers=ua), timeout=60).read())
    css = re.sub(r"url\(https://fonts\.gstatic\.com/s/([^)]+)\)", lambda m: "url(" + m.group(1).replace("/", "_") + ")", css)
    open(css_path, "w").write(css)


CSS = f"""
/* ================= 디자인 레이어 ================= */
:root{{--serif:{DISPLAY}}}
.logo{{font-family:{DISPLAY};font-weight:700;letter-spacing:.04em}}
/* 대제목 — 명조 */
.page:not(.cv):not(.dv) h1{{font-family:{SERIF};font-weight:700;font-size:35px;letter-spacing:-.03em;color:#0F2036;line-height:1.22}}
.page:not(.cv):not(.dv) h1 em{{color:{GOLD_HEAD};font-weight:700}}
.toc .s h3{{font-family:{SERIF};font-weight:700;letter-spacing:-.02em}}
.toc .s .sn{{font-family:{DISPLAY};font-weight:600;font-variant-numeric:lining-nums}}
.rule{{height:1px!important;background:linear-gradient(90deg,{CHAMP},rgba(184,149,90,.35) 55%,rgba(184,149,90,0))!important}}
/* KEY POINT — 남색 띠 · 왼쪽 금색 선 · 세리프 라벨 */
.kp{{border-radius:6px!important;box-shadow:inset 4px 0 0 {CHAMP}!important;padding:14px 26px 14px 30px!important}}
.kp b{{font-family:{DISPLAY};font-size:14.5px;font-weight:700;letter-spacing:.3em;color:#D9BC86}}
.kp em{{color:{GOLD_LT}}}
/* 사진 캡션 — 어두운 띠 → 밝은 라벨 띠 */
.gal figcaption{{background:rgba(250,247,240,.95)!important;color:{INK}!important;padding:8px 13px!important;border-top:1.5px solid {CHAMP}}}
.gal figcaption small{{color:#5C6878!important}}
.gal.lxg figcaption,.gal.lxq figcaption{{padding:9px 14px!important}}

/* 박람회장 배치도 — 흰 구역 카드 · 샴페인 금색 */
.fp .z{{background:#FFFFFF!important;border:1px solid rgba(13,30,51,.14)!important;box-shadow:0 8px 18px -14px rgba(13,30,51,.45)}}
.fp .z h4{{color:{INK}!important}}
.fp .z p{{color:#5C6878!important}}
.fp .z .st{{background:{CHAMP}!important;color:{NAVY}!important}}
.fp .z.hl{{background:linear-gradient(180deg,#F8F1E3,#EFE2C8)!important;border:1.5px solid {CHAMP}!important}}
.fp .z.hl h4{{color:{GOLD_TXT}!important}}
.fp .z.hl p{{color:#3B4A5D!important}}
.fp .z.ent{{background:#FBF6EC!important;border:1.5px solid {CHAMP}!important}}
.fp .z.sf{{background:#FFF7F5!important;border:1.5px solid rgba(192,57,43,.45)!important}}
.fp .z.pk{{background:transparent!important;border:1.5px dashed rgba(13,30,51,.3)!important;box-shadow:none}}
.fps .tot{{background:linear-gradient(180deg,#FBF4E6,#FFFFFF)!important;border:1px solid {CHAMP}!important}}
.fps .bdg span{{color:{GOLD_TXT}!important;border-color:rgba(184,149,90,.7)!important;background:#FFFFFF}}

/* 주관 콜센터 다이어그램 — 밝게 */
.hubd{{background:#FFFFFF!important;border:1px solid rgba(13,30,51,.12)!important;box-shadow:0 14px 30px -22px rgba(13,30,51,.45)}}
.hubd .ch{{background:#FBF8F2!important;border:1px solid rgba(13,30,51,.13)!important;color:{INK}!important}}
.hubd .ctr{{background:radial-gradient(circle at 50% 36%,#FFFFFF 0%,#F7F0E2 62%,#ECDDBF 100%)!important;border:2px solid {CHAMP}!important;
  box-shadow:0 0 0 8px rgba(184,149,90,.13),0 16px 30px -14px rgba(122,87,22,.4)!important;color:{INK}!important}}
.hubd .ctr b{{color:{GOLD_TXT}!important}}
.hubd .ctr span{{color:#5C6878!important}}
.hubd .bd span{{background:#FBF6EC!important;border-color:rgba(184,149,90,.75)!important;color:{GOLD_TXT}!important}}
.hubd .vd{{color:#866322!important}}
.hubd .arr{{background:linear-gradient(90deg,rgba(184,149,90,.25),{CHAMP})!important}}

/* 표지 · 마지막 쪽 */
.page.cv:before{{content:'';position:absolute;inset:22px;border:1px solid rgba(200,168,106,.45);z-index:3;pointer-events:none}}
.page.cv:after{{content:'';position:absolute;inset:27px;border:1px solid rgba(200,168,106,.16);z-index:3;pointer-events:none}}
.cv h1.tj{{font-family:{SERIF};font-weight:700;letter-spacing:-.035em;line-height:1.24;color:#F7F4EC}}
.cv4 h1.tj{{font-size:50px}}
.ctp h1.tj{{font-size:44px}}
.cv h1.tj em{{color:{GOLD_LT};font-weight:700}}
.cv .pill{{border:0!important;border-radius:0!important;padding:0!important;font-family:{DISPLAY};font-size:17px;font-weight:600;letter-spacing:.46em;color:#D9BC86;display:flex!important;align-items:center;gap:16px}}
.cv .pill:before{{content:'';width:46px;height:1px;background:#C8A86A}}
.cv4 .gbar{{width:120px!important;height:1px!important;background:linear-gradient(90deg,#C8A86A,rgba(200,168,106,0))!important}}
.cv .tag2{{font-weight:400;color:#C9D1DB;letter-spacing:-.005em}}
.cv .sub2{{border-top:1px solid rgba(200,168,106,.32)}}
.cv .sub2 i{{letter-spacing:.34em}}
.cv .bt{{font-size:12.5px;letter-spacing:.22em;color:#9FB0C3}}
.cv .who{{font-size:13.5px;letter-spacing:.06em;color:#AEBBCB}}
.ctp .pill{{display:none!important}}
.ctp .contacts div{{border-left:1px solid #C8A86A}}
.ctp .contacts b{{font-weight:700;letter-spacing:.01em;color:{GOLD_LT}}}
.ctp .addr b{{color:#D9BC86}}

/* 간지 — 깊은 남색 · 금색 테두리 · 외곽선 장 번호 */
.page.dv{{background:radial-gradient(900px 560px at 80% 30%,#1B3858 0%,#102540 50%,#0B1A2C 100%)!important;padding:0 112px!important}}
.page.dv:before{{content:'';position:absolute;inset:22px;border:1px solid rgba(200,168,106,.4);pointer-events:none}}
.page.dv:after{{content:'';position:absolute;inset:27px;border:1px solid rgba(200,168,106,.14);pointer-events:none}}
.dv .kick{{position:relative;z-index:1;font-family:{DISPLAY};font-size:16px;font-weight:600;letter-spacing:.5em;font-variant-numeric:lining-nums;color:#C8A86A;display:flex;align-items:center;gap:16px}}
.dv .kick:before{{content:'';width:46px;height:1px;background:#C8A86A}}
.dv .bign{{position:absolute;right:92px;top:150px;font-family:{DISPLAY};font-weight:500;font-size:400px;line-height:1;
  color:transparent;-webkit-text-stroke:1.2px rgba(200,168,106,.4);font-variant-numeric:lining-nums;letter-spacing:-.03em;z-index:0}}
.dv h2{{position:relative;z-index:1;font-family:{SERIF};font-weight:700;font-size:54px;letter-spacing:-.035em;line-height:1.25;color:#F4F6F9;margin-top:22px}}
.dv h2 em{{color:{GOLD_LT}}}
.dv .bar{{position:relative;z-index:1;width:120px!important;height:1px!important;background:linear-gradient(90deg,#C8A86A,rgba(200,168,106,0))!important;margin:30px 0 26px!important}}
.dv .bl{{position:relative;z-index:1;counter-reset:b;display:grid!important;grid-template-columns:repeat(2,minmax(0,370px));gap:16px 44px!important;font-size:18px!important;color:#C9D1DB!important}}
.dv .bl span{{counter-increment:b;border-top:1px solid rgba(200,168,106,.28);padding-top:12px}}
.dv .bl span:before{{content:counter(b,decimal-leading-zero)!important;font-family:{DISPLAY};font-weight:600;color:#C8A86A!important;margin-right:14px;font-size:18px;font-variant-numeric:lining-nums}}
.dv .dvft{{position:absolute;left:112px;right:112px;bottom:46px;display:flex;justify-content:space-between;font-size:11.5px;letter-spacing:.3em;color:rgba(214,186,130,.95)}}

/* 사전점검 X배너 모형 — 아래가 잘리지 않게 */
.xbn{{height:150px!important}}
/* 15만원 — 증서 */
.cert{{flex:1;display:flex;align-items:center;justify-content:center;min-height:0;padding:6px 0 2px}}
.cert-in{{position:relative;width:88%;height:100%;max-height:560px;background:#FFFFFF;border:1px solid {CHAMP};
  box-shadow:0 0 0 7px #FFFFFF,0 0 0 8px rgba(184,149,90,.55),0 28px 50px -30px rgba(13,30,51,.45);
  display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:20px 44px 18px}}
.cert-in .cn{{position:absolute;width:26px;height:26px;border-color:{CHAMP};border-style:solid;border-width:0}}
.cert-in .c1{{left:12px;top:12px;border-left-width:2px;border-top-width:2px}}
.cert-in .c2{{right:12px;top:12px;border-right-width:2px;border-top-width:2px}}
.cert-in .c3{{left:12px;bottom:12px;border-left-width:2px;border-bottom-width:2px}}
.cert-in .c4{{right:12px;bottom:12px;border-right-width:2px;border-bottom-width:2px}}
.cert .ck{{font-variant-numeric:lining-nums;font-family:{DISPLAY};font-size:16px;font-weight:600;letter-spacing:.46em;color:#866322;display:flex;align-items:center;gap:14px}}
.cert .ck:before,.cert .ck:after{{content:'';width:40px;height:1px;background:{CHAMP}}}
.cert .ck2{{font-size:13px;font-weight:700;letter-spacing:.32em;color:{GOLD_TXT};margin-top:6px}}
.cert .cnum{{display:flex;align-items:flex-end;justify-content:center;gap:14px;margin-top:2px}}
.cert .cnum .pre{{font-family:{SERIF};font-size:30px;font-weight:700;color:{INK};margin-bottom:34px}}
.cert .cnum .v{{font-family:{DISPLAY};font-weight:600;font-size:200px;line-height:.9;color:{GOLD_HEAD};letter-spacing:-.02em;font-variant-numeric:lining-nums}}
.cert .cnum .u{{display:flex;flex-direction:column;align-items:flex-start;margin-bottom:30px;line-height:1.1}}
.cert .cnum .u b{{font-family:{SERIF};font-size:46px;font-weight:700;color:{GOLD_HEAD}}}
.cert .cnum .u small{{font-size:15px;color:#5C6878;font-weight:600;letter-spacing:.08em;margin-top:4px}}
.cert .cname{{font-family:{SERIF};font-size:27px;font-weight:700;color:{INK};letter-spacing:-.03em}}
.cert .cline{{width:64px;height:1px;background:{CHAMP};margin:14px auto 12px}}
.cert p{{font-size:16.5px;color:#3B4A5D;line-height:1.6}}
.cert p em{{color:{GOLD_TXT};font-weight:700}}
.cert .cgrid{{display:grid;grid-template-columns:1fr 1fr 1.35fr;width:100%;margin-top:18px;border-top:1px solid rgba(184,149,90,.5)}}
.cert .cgrid div{{padding:13px 12px 2px;border-left:1px solid rgba(184,149,90,.3)}}
.cert .cgrid div:first-child{{border-left:0}}
.cert .cgrid i{{display:block;font-style:normal;font-size:12px;letter-spacing:.26em;color:#866322;font-weight:700}}
.cert .cgrid b{{display:block;font-size:19px;color:{INK};margin-top:5px;letter-spacing:-.01em}}
.cert .cgrid small{{display:block;font-size:12.5px;color:#5C6878;margin-top:2px}}
"""


def won(man):
    eok, rest = divmod(man, 10000)
    if not eok:
        return f"{rest:,}만원"
    return f"{eok}억 {rest:,}만원" if rest else f"{eok}억원"


def cert_html(hh, fund):
    return (f'<div class="ct"><div class="cert"><div class="cert-in">'
            '<i class="cn c1"></i><i class="cn c2"></i><i class="cn c3"></i><i class="cn c4"></i>'
            '<div class="ck">DEVELOPMENT SUPPORT</div><div class="ck2">핵심 제안</div>'
            f'<div class="cnum"><span class="pre">세대당</span><span class="v">{fund}</span><span class="u"><b>만원</b><small>상당 · 부가세 포함</small></span></div>'
            '<div class="cname">발전지원 · 혜택 패키지</div><div class="cline"></div>'
            '<p>박람회 참가비가 아니라 <em>단지로 돌아가는 혜택</em>입니다.<br>공고 업무 범위의 기본 업무는 이와 별도로 수행합니다.</p>'
            '<div class="cgrid">'
            f'<div><i>대상</i><b>전 세대 {hh:,}세대</b><small>전 세대 동일 기준</small></div>'
            f'<div><i>총 규모</i><b>{won(hh * fund)} 상당</b><small>{hh:,}세대 × {fund}만원 · 부가세 포함</small></div>'
            '<div><i>받는 방식</i><b>A · B · C 패키지 또는 입예협 지정</b><small>입예협이 고른 항목을 주관사가 직접 구매 · 제공</small></div>'
            '</div></div></div></div>')


PILL = {"입주박람회 주관사 제안서": "MOVE-IN FAIR PROPOSAL", "요약 제안서": "PROPOSAL SUMMARY", "회사소개서": "COMPANY PROFILE"}


def apply(head, rest, hh, fund, n_dv=10, n_hi=1, label="입주박람회 주관사 제안서"):
    """head = </head> 앞 · rest = 뒤(body). 반환 (head, rest). n_dv · n_hi = 문서에 있어야 할 간지 · 15만원 쪽 수(05 = 10 · 1)."""
    ensure_fonts()
    head = head.replace("<style>", FONT_LINK + "<style>", 1)
    head = head.replace("</style>", CSS + "</style>", 1)
    # 표지 라벨(제목 둘째 줄과 같은 말 → 영문 라벨)
    n_pill = 0
    for a, b in PILL.items():
        n_pill += rest.count(f'<span class="pill">{a}</span>')
        rest = rest.replace(f'<span class="pill">{a}</span>', f'<span class="pill">{b}</span>')
    assert n_pill == 1, ("표지 라벨 수", n_pill)
    # 간지 — 장 번호 라벨 · 큰 외곽선 번호 · 아래 띠
    def dv(m):
        n = m.group(1)
        return (f'<section class="page dv"><div class="bign">{n}</div><div class="kick">CHAPTER {n}</div>'
                + m.group(2)
                + f'<div class="dvft"><span>탕정 푸르지오 센터파크 · {label}</span><span>EDGE COMPANY</span></div></section>')
    rest, n = re.subn(r'<section class="page dv">\s*<div class="n">(\d\d)</div>(.*?)</section>', dv, rest, flags=re.S)
    assert n == n_dv, ("간지 수", n, n_dv)
    # 15만원 쪽 — 증서
    rest, n = re.subn(r'<div class="ct"><div class="hi">.*?</div></div>\s*(?=<div class="kp">)', lambda m: cert_html(hh, fund) + "\n", rest, count=1, flags=re.S)
    assert n == n_hi, ("15만원 쪽 수", n, n_hi)
    return head, rest
