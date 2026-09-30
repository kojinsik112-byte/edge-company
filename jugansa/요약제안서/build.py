# -*- coding: utf-8 -*-
"""엣지컴퍼니 요약제안서(입주박람회 주관사) 빌더 — v2.

원본(2026-09-29 PDF, 48p)을 동일 디자인(네이비+골드)으로 재구축한 소스.
v2 변경: ①11p 구분페이지 '경관조명은 우리가 책임집니다'(컨설팅·설계→생산→직접시공)
        ②경관조명 페이지를 12p로 당기고 기존 12~13p를 그 뒤로 ③경관조명 일러스트 삽입
        ④제목 제외 본문 글자 전체 확대 ⑤마지막 페이지 주관사업 총괄 본부장 연락처 추가

사용:
  python make_images.py      # 경관조명 일러스트(SVG) 재생성(필요 시)
  python build.py            # HTML 생성 + (크롬 있으면) PDF 출력
  CHROME=/path/to/chrome python build.py
문구 강조 표기: [[골드 강조]]
"""
import html
import os
import pathlib
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_HTML = os.path.join(HERE, "엣지컴퍼니_요약제안서_v2.html")
OUT_PDF = os.path.join(HERE, "엣지컴퍼니_요약제안서_v2.pdf")
QUOTE = "“입주민의 든든한 파트너, 엣지컴퍼니”"


def t(s):
    """escape + [[강조]] → 골드"""
    s = html.escape(s, quote=False)
    return re.sub(r"\[\[(.+?)\]\]", r"<em>\1</em>", s)


# ============================================================ CSS
CSS = r"""
@font-face{font-family:'Gelasio';font-weight:400;src:url(assets/fonts/gelasio-latin-400-normal.woff2) format('woff2')}
@font-face{font-family:'Gelasio';font-weight:700;src:url(assets/fonts/gelasio-latin-700-normal.woff2) format('woff2')}
@page{size:297mm 210mm;margin:0}
:root{
  --gold:#EBCB8F;--gold2:#C8A86A;--ink:#F4F6F9;--sub:#B4BECA;--mute:#8595A8;
  --line:rgba(255,255,255,.13);--sans:'Pretendard','Malgun Gothic','맑은 고딕','Apple SD Gothic Neo',sans-serif;
  --serif:Georgia,'Gelasio','Times New Roman',serif;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#050d18}
body{font-family:var(--sans);color:var(--ink);-webkit-print-color-adjust:exact;print-color-adjust:exact;word-break:keep-all}
em{font-style:normal;color:var(--gold)}
.page{width:297mm;height:210mm;position:relative;overflow:hidden;page-break-after:always;break-after:page;
  background:radial-gradient(120% 95% at 88% -12%,#1c3c61 0%,#10264a 34%,#0a192d 64%,#050e1a 100%);
  display:flex;flex-direction:column;padding:40px 48px 0}
.page:last-child{page-break-after:auto;break-after:auto}
@media screen{body{padding:24px 0}.page{margin:0 auto 24px;box-shadow:0 10px 40px rgba(0,0,0,.5)}}

/* ---- header */
.hd{display:flex;justify-content:space-between;align-items:center;height:30px}
.hd .l{display:flex;align-items:center;gap:16px}
.logo{font-family:var(--serif);font-weight:700;font-size:27px;color:var(--gold);letter-spacing:.02em;line-height:1}
.sec{font-size:13px;font-weight:700;letter-spacing:.34em;color:var(--gold2)}
.hd .r{font-size:12.5px;color:var(--mute);letter-spacing:.02em}
h1{font-size:37px;font-weight:800;letter-spacing:-.01em;margin-top:14px;line-height:1.2}
.lead{font-size:19px;color:var(--sub);margin-top:10px;line-height:1.45}
.rule{height:1.5px;margin:16px 0 20px;background:linear-gradient(90deg,var(--gold2),rgba(200,168,106,.35) 55%,rgba(200,168,106,0))}
.ct{flex:1;min-height:0;display:flex;flex-direction:column}
.kp{margin-top:18px;border:1px solid rgba(200,168,106,.38);background:rgba(18,22,28,.62);border-radius:11px;
  padding:15px 26px;display:flex;align-items:center;gap:24px}
.kp b{font-size:12.5px;letter-spacing:.34em;color:var(--gold2);white-space:nowrap}
.kp span{font-size:18.5px;font-weight:700;line-height:1.4}
.kp small{font-size:15px;font-weight:400;color:var(--mute);margin-left:6px}
.ft{height:44px;display:flex;justify-content:space-between;align-items:center;font-size:12px;color:var(--mute)}

/* ---- cards */
.cards{flex:1;display:grid;gap:16px}
.card{border:1px solid var(--line);border-radius:15px;padding:26px 24px;display:flex;flex-direction:column;justify-content:center;
  background:linear-gradient(180deg,rgba(255,255,255,.075),rgba(255,255,255,.012) 60%,rgba(255,255,255,.02))}
.card.hl{border-color:rgba(235,203,143,.75);background:linear-gradient(180deg,rgba(235,203,143,.16),rgba(235,203,143,.03))}
.lb{font-size:12.5px;font-weight:700;letter-spacing:.3em;color:var(--gold2)}
.big{font-size:46px;font-weight:800;color:var(--gold);line-height:1.1;margin-top:8px;letter-spacing:-.01em}
.big small{font-size:21px;font-weight:700;margin-left:2px}
.nm{font-size:22px;font-weight:700;margin-top:8px;line-height:1.3}
.ds{font-size:17.5px;color:var(--sub);margin-top:10px;line-height:1.55}
.ds em{font-weight:700}

/* ---- rows */
.rows{flex:1;display:flex;flex-direction:column;justify-content:space-evenly}
.row{display:grid;grid-template-columns:46px 268px 1fr;gap:0 22px;align-items:center;padding:0 0 14px;
  border-bottom:1px dashed rgba(255,255,255,.14)}
.row:last-child{border-bottom:0}
.no{width:46px;height:46px;border-radius:9px;border:1px solid rgba(200,168,106,.55);background:rgba(200,168,106,.12);
  color:var(--gold);font-weight:800;font-size:18px;display:flex;align-items:center;justify-content:center}
.row .tt{font-size:22px;font-weight:700;line-height:1.3}
.row .dd{font-size:18.5px;color:var(--sub);line-height:1.55}
.row .dd em{font-weight:700}

/* ---- divider */
.dv{justify-content:center;padding:0 96px}
.dv .n{font-family:var(--serif);font-size:88px;line-height:1;color:#7a6e52;font-weight:400}
.dv h2{font-size:50px;font-weight:800;margin-top:14px;letter-spacing:-.01em}
.dv .bar{width:170px;height:2px;background:var(--gold2);margin:26px 0 24px}
.dv .bl{display:flex;flex-wrap:wrap;gap:10px 30px;font-size:19.5px;color:var(--sub)}
.dv .bl span:before{content:'· ';color:var(--gold2)}

/* ---- media (image + bullets) */
.media{flex:1;display:grid;grid-template-columns:44% 1fr;gap:38px;min-height:0}
.ph{position:relative;border-radius:14px;overflow:hidden;border:1px solid var(--line)}
.ph img{width:100%;height:100%;object-fit:cover;display:block}
.ph .cap{position:absolute;left:0;right:0;bottom:0;padding:12px 18px;font-size:15px;font-weight:700;
  background:linear-gradient(0deg,rgba(5,12,22,.92),rgba(5,12,22,.6))}
.bul{display:flex;flex-direction:column;justify-content:center;gap:24px}
.bul div{position:relative;padding-left:26px}
.bul div:before{content:'';position:absolute;left:0;top:9px;width:10px;height:10px;border-radius:50%;background:var(--gold2)}
.bul b{display:block;font-size:22px;line-height:1.35}
.bul p{font-size:17.5px;color:var(--sub);margin-top:6px;line-height:1.5}

/* ---- bars */
.bars{flex:1;display:grid;grid-template-columns:repeat(5,1fr);gap:26px;align-items:end;padding:0 4px}
.bars .c{display:flex;flex-direction:column;align-items:center;height:100%;justify-content:flex-end}
.bars .v{font-size:28px;font-weight:800;margin-bottom:10px}
.bars .b{width:100%;border-radius:6px 6px 0 0;background:linear-gradient(180deg,#E6C98E,#8E7442)}
.bars .y{font-size:17px;color:var(--sub);margin-top:12px}

/* ---- highlight */
.hi{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.hi .tag{font-size:17px;font-weight:700;letter-spacing:.3em;color:var(--gold2)}
.hi .num{display:flex;align-items:flex-end;gap:14px;margin-top:4px}
.hi .num .pre{font-size:40px;font-weight:800;color:var(--gold2);margin-bottom:26px}
.hi .num .v{font-size:150px;font-weight:800;color:var(--gold);line-height:1;letter-spacing:-.03em}
.hi .num .post{font-size:16.5px;color:var(--sub);margin-bottom:28px}
.hi .nm2{font-size:28px;font-weight:800;margin-top:14px}
.hi p{font-size:19px;color:var(--sub);margin-top:12px;line-height:1.6}
.hi p em{font-weight:700}
.chips{display:flex;gap:12px;margin-top:22px;flex-wrap:wrap;justify-content:center}
.chips span{border:1px solid var(--gold2);border-radius:99px;padding:8px 20px;font-size:16px;font-weight:700;color:var(--gold)}

/* ---- grid tiles */
.tiles{flex:1;display:grid;gap:14px}
.tile{border:1px solid var(--line);border-radius:12px;padding:16px 20px;display:flex;flex-direction:column;justify-content:center;
  background:linear-gradient(180deg,rgba(255,255,255,.07),rgba(255,255,255,.015))}
.tile .lb{font-size:12px}
.tile .nm{font-size:20px;margin-top:6px}
.tile .ds{font-size:16px;margin-top:6px;line-height:1.5}
.tile .big{font-size:36px;margin-top:4px}
.tile .big small{font-size:18px}

/* ---- closing */
.cl{flex:1;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(4,1fr);gap:12px 16px}
.cl .it{border:1px solid var(--line);border-radius:12px;padding:12px 20px;display:flex;align-items:center;gap:18px;
  background:linear-gradient(180deg,rgba(255,255,255,.07),rgba(255,255,255,.015))}
.cl .it b{display:block;font-size:21px;line-height:1.3}
.cl .it p{font-size:16.5px;color:var(--sub);margin-top:4px}
.cl .no{width:40px;height:40px;font-size:16px;flex:none}

/* ---- toc */
.toc{flex:1;display:grid;grid-template-columns:repeat(3,1fr);gap:0}
.toc .col{border-left:1px solid rgba(255,255,255,.16);padding:0 26px;display:flex;flex-direction:column;gap:18px}
.toc .s .sn{font-family:var(--serif);font-size:30px;color:var(--gold2);line-height:1}
.toc .s h3{font-size:23px;font-weight:800;margin:6px 0 10px}
.toc .s li{list-style:none;font-size:17px;color:#D5DCE4;line-height:1.85}
.toc .s li i{font-style:normal;color:var(--mute);font-size:14px;margin-right:12px}

/* ---- cover / contact */
.cv{padding:56px 72px 0}
.cv .top{display:flex;justify-content:space-between}
.cv .logo{font-size:46px}
.cv .en{font-size:13.5px;letter-spacing:.55em;color:var(--gold2);font-weight:700;margin-top:14px}
.cv .who{text-align:right;font-size:15px;color:var(--sub);line-height:1.7}
.cv .mid{flex:1;display:flex;flex-direction:column;justify-content:center}
.pill{display:inline-block;align-self:flex-start;border:1px solid var(--gold2);border-radius:99px;padding:8px 26px;
  font-size:16px;font-weight:700;letter-spacing:.3em;color:var(--gold)}
.cv h1{font-size:54px;line-height:1.25;margin-top:22px}
.cv .tag2{font-size:20px;color:var(--sub);margin-top:16px}
.stats{display:flex;gap:44px;margin-top:30px;flex-wrap:wrap}
.stats div{border-left:2px solid var(--gold2);padding-left:18px}
.stats b{display:block;font-size:32px;font-weight:800;color:var(--gold);line-height:1.2}
.stats b small{font-size:12px;font-weight:400;color:var(--sub);font-style:italic;margin-left:4px}
.stats span{font-size:15.5px;color:var(--sub)}
.cv .bt{height:64px;display:flex;justify-content:space-between;align-items:center;font-size:15px;color:var(--sub)}
.contacts{display:grid;grid-template-columns:repeat(3,auto);gap:22px 48px;margin-top:28px;justify-content:start}
.contacts div{border-left:2px solid var(--gold2);padding-left:18px}
.contacts b{display:block;font-size:31px;font-weight:800;color:var(--gold);line-height:1.2;letter-spacing:-.005em}
.contacts span{font-size:16px;color:var(--sub)}
.contacts .me{grid-column:span 3}
.contacts .me b{font-size:27px}
.addr{font-size:15.5px;color:var(--sub);margin-top:24px;line-height:1.75}

/* ---- 경관조명 */
.dv-lx{background:radial-gradient(120% 95% at 88% -12%,#1c3c61 0%,#10264a 34%,#0a192d 64%,#050e1a 100%)}
.dv-lx .art{position:absolute;right:-30px;bottom:0;width:58%;height:100%;
  background:url('assets/경관조명_야경.svg') right bottom/cover no-repeat;opacity:.9;
  -webkit-mask-image:linear-gradient(90deg,transparent 0%,#000 38%);mask-image:linear-gradient(90deg,transparent 0%,#000 38%)}
.dv-lx .veil{position:absolute;inset:0;background:linear-gradient(90deg,rgba(5,14,26,.92) 0%,rgba(5,14,26,.55) 48%,rgba(5,14,26,.05) 100%)}
.dv-lx .in{position:relative;z-index:1;max-width:640px}
.dv-lx .kick{font-size:23px;font-weight:700;color:var(--ink);margin-top:2px}
.dv-lx .kick em{font-weight:800}
.flow{display:flex;align-items:center;gap:14px;margin-top:22px}
.flow .st{border:1px solid rgba(235,203,143,.7);background:rgba(10,24,42,.78);border-radius:12px;padding:12px 22px;min-width:150px}
.flow .st i{display:block;font-style:normal;font-size:12.5px;font-weight:700;letter-spacing:.28em;color:var(--gold2)}
.flow .st b{display:block;font-size:26px;font-weight:800;color:var(--gold);margin-top:4px}
.flow .ar{font-size:26px;color:var(--gold2)}
.dv-lx .bl{margin-top:26px}
.lx{flex:1;display:grid;grid-template-columns:1fr 34px 1fr 34px 1fr;align-items:stretch;min-height:0}
.lx .card{padding:0;justify-content:flex-start;overflow:hidden}
.lx .card img{width:100%;aspect-ratio:16/10;object-fit:cover;display:block;border-bottom:1px solid var(--line)}
.lx .card .tx{padding:18px 22px 20px;display:flex;flex-direction:column;flex:1;justify-content:center}
.lx .card .big{font-size:40px;margin-top:4px}
.lx .card .nm{font-size:20.5px;margin-top:4px}
.lx .card .ds{font-size:16px;margin-top:8px}
.lx .card.key{border-color:rgba(235,203,143,.75)}
.lx .ar{display:flex;align-items:center;justify-content:center;color:var(--gold);font-size:24px;font-weight:800}
"""


# ============================================================ 공통 틀
PAGES = []


def add(kind, **kw):
    PAGES.append((kind, kw))


def render_std(no, sec, title, lead, body, kp):
    kp_html = ""
    if kp:
        if isinstance(kp, tuple):
            kp_html = f'<div class="kp"><b>KEY POINT</b><span>{t(kp[0])}<small>{t(kp[1])}</small></span></div>'
        else:
            kp_html = f'<div class="kp"><b>KEY POINT</b><span>{t(kp)}</span></div>'
    return f"""<section class="page">
<div class="hd"><div class="l"><span class="logo">EG</span><span class="sec">{sec}</span></div>
<div class="r">{QUOTE} &nbsp;·&nbsp; {no:02d}</div></div>
<h1>{t(title)}</h1>
{f'<div class="lead">{t(lead)}</div>' if lead else ''}
<div class="rule"></div>
<div class="ct">{body}</div>
{kp_html}
<div class="ft"><span>주식회사 엣지컴퍼니 · 대표이사 고진식</span><span>EDGE COMPANY</span></div>
</section>"""


# ------------------------------------------------------------ 본문 블록
def cards(items, cols=None):
    cols = cols or len(items)
    out = []
    for it in items:
        big = ""
        if it.get("big"):
            unit = f'<small>{t(it["unit"])}</small>' if it.get("unit") else ""
            big = f'<div class="big">{t(it["big"])}{unit}</div>'
        out.append(f'<div class="card{" hl" if it.get("hl") else ""}">'
                   f'<div class="lb">{t(it["lb"])}</div>{big}'
                   + (f'<div class="nm">{t(it["nm"])}</div>' if it.get("nm") else "")
                   + (f'<div class="ds">{t(it["ds"])}</div>' if it.get("ds") else "")
                   + '</div>')
    return f'<div class="cards" style="grid-template-columns:repeat({cols},1fr)">{"".join(out)}</div>'


def rows(items, title_w=268):
    out = []
    for i, (tt, dd) in enumerate(items, 1):
        out.append(f'<div class="row" style="grid-template-columns:46px {title_w}px 1fr">'
                   f'<div class="no">{i:02d}</div><div class="tt">{t(tt)}</div><div class="dd">{t(dd)}</div></div>')
    return f'<div class="rows">{"".join(out)}</div>'


def tiles(items, cols, rows_n=None):
    out = []
    for it in items:
        big = ""
        if it.get("big"):
            unit = f'<small>{t(it["unit"])}</small>' if it.get("unit") else ""
            big = f'<div class="big">{t(it["big"])}{unit}</div>'
        out.append(f'<div class="tile"><div class="lb">{t(it["lb"])}</div>{big}'
                   + (f'<div class="nm">{t(it["nm"])}</div>' if it.get("nm") else "")
                   + (f'<div class="ds">{t(it["ds"])}</div>' if it.get("ds") else "")
                   + '</div>')
    rs = f";grid-template-rows:repeat({rows_n},1fr)" if rows_n else ""
    return f'<div class="tiles" style="grid-template-columns:repeat({cols},1fr){rs}">{"".join(out)}</div>'


def media(img, cap, bullets):
    bl = "".join(f'<div><b>{t(a)}</b><p>{t(b)}</p></div>' for a, b in bullets)
    return (f'<div class="media"><div class="ph"><img src="{img}" alt=""><div class="cap">{t(cap)}</div></div>'
            f'<div class="bul">{bl}</div></div>')


# ============================================================ 페이지 정의
# 01 표지
add("cover")
# 02 목차
add("toc")
# 03 구분
add("divider", n="01", title="엣지컴퍼니는 [[이런 회사]]입니다.",
    bl=["80개 단지 운영", "자본금 5억 · 자가 사옥", "신용 B+ · 현금흐름 A", "전국 지사망 · 3개소 직영", "ISO 3종 · 삼성전자 MOU"])
S1 = "01. 회사 역량"
add("std", sec=S1, title="숫자로 보는 [[엣지컴퍼니]]",
    lead="말보다 기록이 먼저입니다. 8년간 쌓인 운영 데이터가 저희를 설명합니다.",
    body=cards([
        dict(lb="PROJECTS", big="80", unit="개 단지", nm="누적 주관 단지", ds="2018년 첫 단지 이후 전국에서 연속 운영."),
        dict(lb="HOUSEHOLDS", big="48,523", unit="세대", nm="함께한 입주민", ds="1,000세대 이상 대단지 운영 경험 다수."),
        dict(lb="LARGEST", big="4,470", unit="세대", nm="최대 단지 규모", ds="레이카운티 단일 단지 주관."),
        dict(lb="GROWTH", big="+178", unit="%", nm="5년 누적 성장", ds="2022년 9단지 → 2026년 25단지 확정."),
    ]),
    kp="80개 단지·48,523세대 — 규모가 곧 운영 매뉴얼입니다.")
add("bars", sec=S1, title="매년 성장하는 [[운영 규모]]",
    lead="정체된 회사가 아니라, 매년 신규 단지가 늘어나는 회사입니다.",
    data=[("2022", 9), ("2023", 12), ("2024", 15), ("2025", 18), ("2026", 25)],
    kp="매년 최소 3개 이상 신규 단지 — 신규 영업이 아닌 [[입소문 기반 성장]]입니다.")
add("std", sec=S1, title="자본금 [[5억 · 자가 사옥]] 보유",
    lead="임대 사무실이 아닌 자사 소유 사옥, 그리고 공인 평가기관의 등급으로 증명합니다.",
    body=media("assets/사옥.jpg", "엣지컴퍼니 자가 사옥 · 본사/쇼룸 운영", [
        ("자본금 5억원", "하자 예치금·이행보증의 재원이 되는 실체입니다."),
        ("자가 사옥 보유", "사옥에서 본사·쇼룸·시공팀을 직접 운영합니다."),
        ("기업 신용등급 B+ / 현금흐름 A", "공인 평가기관 평가. 협의회 제출 증빙 즉시 발급 가능."),
        ("ISO 9001·14001·45001", "품질·환경·안전보건 국제표준 3종 인증 보유."),
    ]),
    kp="자본금 5천짜리 임대 사무실 주관사와는 [[체급이 다릅니다.]]")
add("std", sec=S1, title="공인된 [[자격과 신뢰]]", lead="서류로 즉시 증명 가능한 항목만 적었습니다.",
    body=cards([
        dict(lb="CREDIT", big="B+", nm="기업 신용등급", ds="공인 평가기관 기업신용평가 등급."),
        dict(lb="CASH FLOW", big="A", nm="현금흐름 등급", ds="박람회 운영 중 자금 흐름 안정성 검증."),
        dict(lb="ISO", big="3", unit="종", nm="국제표준 인증", ds="ISO 9001 · 14001 · 45001."),
        dict(lb="PARTNERSHIP", big="MOU", nm="삼성전자 공식 MOU", ds="대기업이 직접 검증한 주관사. LX하우시스·에몬스 추가 협의."),
    ]),
    kp="4대보험 증명원 · 납세증명 · 기업신용평가서 — [[원본 스캔으로 첨부]]합니다.")
add("std", sec=S1, title="전국 지사망 · [[부산·울산·대전 직영]]", lead="외주 파트너가 아니라 직영 거점이 단지를 맡습니다.",
    body=cards([
        dict(lb="직영 01", big="부산", nm="부산 직영", ds="해운대 거점. 부산·경남 전 단지 직접 운영."),
        dict(lb="직영 02", big="울산", nm="울산 본사 직영", ds="본사·사옥·쇼룸. 시공팀 상주."),
        dict(lb="직영 03", big="대전", nm="대전 직영", ds="충청권 거점. 세종·아산·청주 커버."),
        dict(lb="NETWORK", big="전국", unit="지사망", nm="그 외 지역", ds="서울·경인·강원·전북·전남·광주·대구·경북·양산 등 네트워크 운영."),
    ]),
    kp="직영은 [[책임 주체가 바뀌지 않습니다.]] 문제가 생기면 본사가 직접 갑니다.")
add("std", sec=S1, title="왜 [[직영]]이어야 합니까",
    lead="지사를 빌려 쓰는 주관사와 직접 운영하는 주관사는 사고 났을 때 완전히 다릅니다.",
    body=rows([
        ("책임 주체가 하나", "현장 담당이 협력사가 아니라 엣지컴퍼니 직원입니다. 책임을 떠넘길 대상이 없습니다."),
        ("48시간 A/S가 가능한 이유", "거점에 시공팀이 상주하기 때문에 하자 접수 후 이동시간이 짧습니다."),
        ("단가가 투명", "중간 마진 단계가 없어 공동구매 단가를 협의회에 그대로 공개할 수 있습니다."),
        ("입주 후에도 남습니다", "박람회가 끝나도 거점이 그대로 있어 장기 A/S가 실제로 작동합니다."),
    ]),
    kp="도망갈 수 없는 회사가, 가장 신뢰할 수 있는 회사입니다.")
add("std", sec=S1, title="대표가 [[직접]] 카메라 앞에 섭니다", lead="채널 이름이 곧 약속입니다 — “대한민국 주관사 기준”.",
    body=media("assets/본사_쇼룸.jpg", "엣지컴퍼니 본사 · 쇼룸", [
        ("유튜브 구독자 15,000+", "대표가 직접 운영. 매주 박람회 현장과 결과를 공개합니다."),
        ("검색하면 다 나옵니다", "단지 카페에 검색 한 번이면 대표의 말과 시공 결과가 모두 공개되어 있습니다."),
        ("공식 카페·알림톡·콜센터", "입주민과 끊기지 않는 채널을 회사가 직접 운영합니다."),
        ("대표이사 고진식", "제조업 10년 근무 후 창업. 저서 『사람 덕분에 여기까지 왔습니다』."),
    ]),
    kp="말로 하는 약속이 아니라 [[기록으로 남는 약속]]입니다.")

# 11 구분 — 경관조명 (v2 신규)
add("divider_lx")
S2 = "02. 조명 특화"
# 12 경관조명 (기존 14p → 앞으로)
add("landscape", sec=S2)
# 13 수직계열화 (기존 12p)
add("std", sec=S2, title="주관사 중 유일한 [[조명 수직계열화]]",
    lead="기획 → 직수입/생산 → 인증 → 시공까지 한 회사 안에서 끝납니다.",
    body=cards([
        dict(lb="STEP 01", big="직수입", nm="해외 직수입 라인", ds="중국 상해·중산 무역 라인 직접 보유. 국내 유통 단계를 거치지 않습니다."),
        dict(lb="STEP 02", big="생산", nm="생산 및 제작", ds="단지 사양에 맞춰 제품을 직접 기획·생산합니다. 규격 맞춤 가능."),
        dict(lb="STEP 03", big="KC", nm="KC 인증", ds="전기용품 안전 KC 인증을 갖춘 제품만 단지에 들어갑니다."),
        dict(lb="STEP 04", big="시공", nm="면허 기반 시공", ds="전기공사업 등록업체로서 결선·설치까지 직접 책임집니다."),
    ]),
    kp="유통 단계를 뺀 만큼 [[그대로 입주민 단가]]가 됩니다.")
# 14 같은 물건 (기존 13p)
add("std", sec=S2, title="같은 물건, [[다른 가격]]", lead="한국 유통 단계를 모두 빼고 단지에 도착합니다.",
    body=rows([
        ("해외 직수입", "중국 상해·중산 라인 무역 체결 완료. 실링팬·조명·가구 등 품목을 입주민 투표로 정해 최저가 직수입 공동구매를 진행합니다."),
        ("자체 생산·제작", "단지 도면과 천장 사양에 맞춘 규격으로 제작 가능. 재고 상품을 파는 방식이 아닙니다."),
        ("KC 인증 확보", "전기용품 안전관리법 기준 KC 인증 제품만 취급. 인증서 사본을 협의회에 제출합니다."),
        ("직접 시공·A/S", "전기공사업 면허 보유. 시공 하자가 나도 다른 업체를 찾을 필요가 없습니다."),
    ]),
    kp="“업체가 안 해줘요”라는 말이 나올 수 없는 구조입니다.")
add("std", sec=S2, title="[[커뮤니티 시설]] 업그레이드", lead="입주민이 매일 쓰는 공간부터 손봅니다.",
    body=rows([
        ("커뮤니티 조명 개선", "피트니스·독서실·경로당 등 조도가 부족한 공간을 재설계해 개선안을 제시합니다."),
        ("공용부 조명 교체 검토", "지하주차장·계단실 조도와 에너지 효율을 함께 검토해 관리비 절감안을 제안합니다."),
        ("입주 기념 점등식", "단지 전체가 함께하는 점등식 행사를 기획·운영합니다."),
        ("단지 사인·조형 조명", "단지명 사인 조명, 진입부 조형 조명 등 브랜드 요소를 제안합니다."),
    ]),
    kp="조명은 우리 본업입니다. [[제안만 하고 끝내지 않습니다.]]")

# 16 구분 — 안전망
add("divider", n="03", title="말이 아니라 [[증명]]입니다.",
    bl=["하자 예치금 현금 1억", "이행보증보험 2년 10억", "업체 하자보증·도산 대응", "48시간 하자보수 · 10년 A/S", "현장 베이스캠프"])
S3 = "03. 안전망"
add("std", sec=S3, title="입주민을 지키는 [[4중 안전망]]", lead="한 가지라도 빠지면 입주민이 피해를 봅니다. 저희는 네 겹으로 막습니다.",
    body=cards([
        dict(lb="01", big="1", unit="억", nm="하자 예치금 현금", ds="엣지 순수 자산으로 거치. 업체에게 받은 돈이 아닙니다."),
        dict(lb="02", big="10", unit="억", nm="이행보증보험 2년", ds="업체 도산 시 엣지가 100% 지급 + 동종업체 이관."),
        dict(lb="03", big="48", unit="시간", nm="하자보수 원칙", ds="미해결 시 하자지연 패널티 부과."),
        dict(lb="04", big="10", unit="년", nm="장기 사후관리", ds="최소 2년 무상 A/S, 최대 10년 장기 관리."),
    ]),
    kp="안전망은 [[계약서]]와 [[증권으로]] 제출합니다.")
add("hi_money", sec=S3)
add("std", sec=S3, title="예치금은 [[어디에]] 두느냐가 핵심입니다", lead="금액보다 집행 속도가 중요합니다.",
    body=rows([
        ("공동통장 예치", "법무법인 통장이 아니라 [[입예협 + 주관사 공동통장]]에 예치합니다."),
        ("즉시 집행", "법무법인 예치는 송달에 1주~10일이 걸립니다. 공동통장은 협의회 판단으로 즉시 집행됩니다."),
        ("순수 자사 자산", "참여 업체에게 걷은 돈이 아니므로, 업체가 빠져도 예치금이 줄지 않습니다."),
        ("사용 내역 공개", "집행 시 사용 내역을 협의회에 전액 공개합니다."),
    ]),
    kp="“입주민은 기다려주지 않습니다.” 그래서 [[즉시 집행]] 구조를 택했습니다.")
add("std", sec=S3, title="이행보증보험 [[2년 · 10억]]", lead="주관사가 약속을 안 지키면 보험이 대신 지급합니다.",
    body=cards([
        dict(lb="COVER", big="10", unit="억원", nm="보증 금액", ds="제안 내용 미이행·업체 도산·검증 미비에 대한 주관사 책임 범위."),
        dict(lb="TERM", big="2", unit="년", nm="보증 기간", ds="입주 종료 후에도 유효. 증권 사본을 협의회에 제출합니다."),
        dict(lb="SCOPE", big="전액", nm="업체 도산 시", ds="엣지컴퍼니가 비용 전액 지불 및 동종업체 하자보수 이관."),
    ]),
    kp="증권은 [[협약식 때 실물로]] 제출합니다.")
add("std", sec=S3, title="참여업체 [[하자보증]] 체계", lead="업체를 믿는 게 아니라, 업체를 묶어둡니다.",
    body=rows([
        ("하자보수 이행각서", "박람회 참여 모든 업체로부터 하자보수 이행각서를 받습니다."),
        ("특약이행각서 9개 항", "현금·카드 동일가, 별도 박람회 금지, 차액 10배 보상, 비방 금지, 과대홍보 금지 등 위반 시 자격박탈."),
        ("업체 도산 시", "동종업체로 사후관리 의무 이관. A/S 비용은 주관사가 100% 지급·처리."),
        ("선보상 제도", "업체가 회피·지연하면 주관사가 입주민께 먼저 보상하고, 이후 업체와 정산합니다."),
        ("패널티 3단계", "① 홍보정지 ② 총액 10% 배상 ③ 자격박탈 및 전 계약 이관."),
    ]),
    kp="입주민과 업체가 싸우지 않게 — [[주관사가 사이에 섭니다.]]")
add("std", sec=S3, title="현장 [[베이스캠프]] 구축", lead="48시간 A/S는 거리에서 결정됩니다.",
    body=cards([
        dict(lb="BASE", big="현장", nm="단지 인근 베이스캠프", ds="입주 기간 중 단지 인근에 상주 거점을 운영합니다."),
        dict(lb="PERIOD", big="45", unit="일", nm="운영 기간", ds="입주 집중 기간 동안 상주. 단지 규모에 따라 조정."),
        dict(lb="RESULT", big="0", unit="%", nm="하자율 도전", ds="에코델타 이편한세상·강서자이 운영 사례 — 명지 오피스텔 베이스캠프."),
        dict(lb="CS", big="24h", nm="CRM 피드백", ds="VOC 접수 24시간 내 회신 원칙, 하자 48시간 내 처리."),
    ]),
    kp="“오늘 접수, 내일 해결”이 가능한 [[물리적 조건]]을 먼저 만듭니다.")
add("std", sec=S3, title="주관 [[콜센터]]와 선보상", lead="입주민은 업체가 아니라 주관사에 전화하면 됩니다.",
    body=rows([
        ("접수 채널 4종", "상담 콜센터 · 공식카페 신문고 · 카카오채널 · 홈페이지. 365일 운영."),
        ("24시간 내 피드백", "VOC 접수 시 24시간 내 회신. 업체 미응답 시 주관사가 직접 개입."),
        ("48시간 내 처리", "주관사 관리·감독 하에 48시간 내 하자보수 의무 이행."),
        ("선보상 후 정산", "업체 책임이 확인되면 입주민께 먼저 보상하고, 업체와는 나중에 정산합니다."),
        ("해피콜 검수", "보수 완료 후 주관사가 직접 확인 전화를 드립니다."),
    ]),
    kp="입주민이 업체를 쫓아다니지 않아도 되는 구조입니다.")

# 24 구분 — 업체선정
add("divider", n="04", title="업체 선정이 [[주관사의 본질]]입니다.",
    bl=["4단계 공개 심사", "지역업체 95% 선정", "최저가 보장 차액 10배", "계약금 5% 상한제", "시공 전 100% 환불"])
S4 = "04. 업체선정"
add("std", sec=S4, title="[[4단계]] 공개 심사 프로세스", lead="주관사 단독 결정이 아닙니다. 협의회가 마지막에 컨펌합니다.",
    body=rows([
        ("자율경쟁 입찰공고", "공식 카페·협력업체 밴드·홈페이지에 공개 모집. 입찰서류는 [[주관사와 협의회 양쪽 이메일]]로 동시 접수."),
        ("1차 서류심사", "사업개시 2년 경과 · 근거리 업체 · 타단지 공구이력 20회 이상 · 국세지방세 완납 · 사후관리 시스템 완비."),
        ("2차 세부심사", "다세대 시공물량 소화 가능 여부, A/S 대책 증명, 입주민 평가도 확인. 대기업·브랜드·본사직영 우선."),
        ("협의회 최종 컨펌", "후보업체 서류 최종 검토 후 [[협의회 승인으로 확정]]. 물품공급계약서·청렴이행서약서·하자보수이행각서 징구."),
    ], title_w=230),
    kp="입찰 과정 전체를 협의회와 [[공유]]합니다.")
add("std", sec=S4, title="[[지역업체 95%]] 선정 원칙", lead="A/S는 거리가 결정합니다.",
    body=cards([
        dict(lb="LOCAL", big="95", unit="%", nm="지역업체 비중", ds="타 지역 업체는 48시간 내 A/S 처리·관리가 현실적으로 불가능합니다."),
        dict(lb="CHECK", big="검증", nm="사업자·재무·예치금", ds="사업자등록증·재무제표·완납증명서·예치금 통과 업체만 입점."),
        dict(lb="NO SUB", big="외주 X", nm="미검증·외주 배제", ds="선정 업체가 다른 업체에 하청 주는 행위를 계약으로 금지합니다."),
    ]),
    kp="못 지키면 [[주관사 자격 철회 동의서]]를 쓰겠습니다.")
add("std", sec=S4, title="[[최저가 보장]] · 차액 10배 보상", lead="가격 경쟁력을 말이 아니라 제도로 만듭니다.",
    body=cards([
        dict(lb="공동구매가", big="33", unit="만원", ds="박람회 제시 가격"),
        dict(lb="동일제품 오프라인", big="26", unit="만원", ds="입주민이 발견한 더 싼 가격"),
        dict(lb="차액", big="7", unit="만원", ds="차액 발생"),
        dict(lb="보상 10배", big="70", unit="만원", ds="보상 + 판매가 26만원으로 조정", hl=True),
    ]),
    kp=("동일 브랜드·동일 제품 확인 시 [[차액의 10배]] 보상.", "(온라인 판매·시공 품목 제외)"))
add("std", sec=S4, title="입주민 [[자금]]을 먼저 지킵니다", lead="업체가 선수금을 많이 받지 못하게 계약으로 막습니다.",
    body=cards([
        dict(lb="01", big="5", unit="%", nm="계약금 상한제", ds="계약금은 총액의 5% 이하. 잔금은 시공·설치 후 납부."),
        dict(lb="02", big="100", unit="%", nm="시공 전 환불", ds="제작·시공 전에는 100% 해약 가능."),
        dict(lb="03", big="동일", nm="현금·카드 동일가", ds="카드 결제도 현금가와 동일. 현금영수증 발행 가능."),
        dict(lb="04", big="7/15", nm="취소·환불 규정", ds="품목별 시공일 기준 7일·15일 전 취소 가능. 해피콜 미이행 시 당일 취소 가능."),
    ]),
    kp="불이행 업체는 주관사 콜센터 접수 → [[즉시 패널티.]]")

# 29 구분 — 협의회 지원
add("divider", n="05", title="협의회 전용 [[단지 지원]]",
    bl=["세대당 17만원 상당 발전지원금", "8가지 무상 단지지원", "조경·착공 분석보고서", "커뮤니티 시설 업그레이드", "협상 미팅 동석"])
S5 = "05. 협의회 지원"
add("hi_fund", sec=S5)
add("std", sec=S5, title="발전지원금은 [[이렇게 쓰입니다]]", lead="현금만 드리고 끝나는 게 아니라, 단지에 남는 형태로 집행합니다.",
    body=rows([
        ("단지 시설 투자", "커뮤니티 시설 업그레이드, 경관조명, 공용부 개선 등 [[입주 후에도 남는 곳]]에 우선 집행."),
        ("협의회 활동 지원", "협의회 운영·행사·회의 등 활동에 필요한 지원."),
        ("입주민 직접 혜택", "상품권·사은품·무상 시공 등 세대에 직접 돌아가는 혜택."),
        ("집행 내역 공개", "항목·금액·시점을 협의회와 사전 협의하고, 집행 후 내역을 공개합니다."),
    ]),
    kp=("구체 배분은 [[협의회 협의 후 단지 맞춤]]으로 확정합니다.", "표기 금액은 부가세 포함 상당액"))
add("std", sec=S5, title="협의회 전용 [[8가지 무상 단지지원]]", lead="박람회와 별개로, 단지의 발전을 위해 무상 제공합니다.",
    body=tiles([
        dict(lb="01", nm="공용부 철근탐지 · 콘크리트 강도 측정", ds="건설현장 시공품질 정밀 검증. 입주 전 안전 진단 무상."),
        dict(lb="02", nm="열화상 드론 공용부 촬영", ds="육안으로 안 보이는 누수·단열 결함을 드론으로 잡아냅니다."),
        dict(lb="03", nm="일조량 시뮬레이션 분석", ds="세대별 일조 시간을 사전 분석. 협의회 협상 자료로 활용."),
        dict(lb="04", nm="라돈 측정 무료 지원", ds="1급 발암물질 라돈 농도 측정. 측정기 10대 렌탈 지원."),
        dict(lb="05", nm="공용부 항균 나노코팅", ds="엘리베이터·계단실 등 다중이용 공간 항균 처리."),
        dict(lb="06", nm="세스코 무료 점검", ds="해충·위생 전문 진단 협력 패키지 제공."),
        dict(lb="07", nm="공정·하자 분석 솔루션", ds="착공·조경 설계도면 검토 및 개선안 분석 지원."),
        dict(lb="08", nm="협의회 협상 미팅 지원", ds="시공사·시행사 협상 자리에 전문 엔지니어가 동석합니다."),
    ], cols=4, rows_n=2),
    kp="별도 비용 없음 · 외주 아닌 [[자체 인력 운영]] · 협의회 전용.")
add("std", sec=S5, title="[[조경·착공]] 분석보고서", lead="시공사와 협상할 때 쓰는 무기를 드립니다.",
    body=rows([
        ("착공설계 도면 분석", "특급기술자가 착공도면을 검토해 하자·오적출 분석보고서를 제공합니다."),
        ("조경 도면 분석", "조경 감리 관점에서 도면을 검토하고, 입주예정자 대상 설명회를 무료 제공합니다."),
        ("조경 검수 체크리스트", "조경식재 하자, 고사목 검수, 공용부 중복 검수, 부대토목 하자 검수."),
        ("개선안 비교 제안", "커뮤니티 광장·키즈플레이스·텃밭 등 주요 공간의 개선안을 도면으로 비교 제시."),
        ("협상 미팅 동석", "전문 엔지니어가 시공사 협상 자리에 함께 갑니다. 지역구 의원 협의 참관도 지원."),
    ]),
    kp="“보기 좋은 제안”이 아니라 [[협상에서 실제로 먹히는 자료]]를 만듭니다.")
add("std", sec=S5, title="[[커뮤니티 시설]] 업그레이드 제안", lead="입주민이 가장 오래 쓰는 공간부터 봅니다.",
    body=cards([
        dict(lb="SPACE 01", nm="커뮤니티 광장", ds="중하중 한계를 고려한 수경시설 안전 시공, 경관 개선안 제시."),
        dict(lb="SPACE 02", nm="키즈·헬스 플레이스", ds="아이 동선과 안전을 고려한 배치 개선안."),
        dict(lb="SPACE 03", nm="휴게·티하우스", ds="포장 최소화, 녹음 속 휴게공간 조성 제안."),
        dict(lb="SPACE 04", nm="텃밭 · 야외 캠핑장", ds="입주민 소통 공간으로 활용 가능한 부대시설 제안."),
    ]),
    kp="조경 트레이너를 통한 [[맞춤설계 지원.]]")
add("std", sec=S5, title="입주 전부터 [[끝까지]] 붙어 있습니다", lead="협의회 실무 부담을 실제로 덜어드립니다.",
    body=rows([
        ("온라인 위임장", "가입·앱 설치 없이 카카오톡·이메일로 전자서명. 서명 이미지·일시·필압까지 저장."),
        ("민원업무 처리 지원", "국민신문고 등 민원 양식과 접수 프로세스를 단지 컨셉에 맞게 지원."),
        ("시위현장 컨설팅", "입주민 의견이 긍정적으로 반영되도록 피켓·현수막·동선을 컨설팅합니다."),
        ("사전점검 행사 지원", "현수막·X배너·서류자료·도우미 인력, 라돈측정기 10대, 커피차, 냉·난방용품 지원."),
        ("공용/조경 하자진단 보고서", "사전점검 당일 공용부·조경 하자진단 보고서를 제공합니다."),
    ]),
    kp="협의회가 직접 하실 일을 [[주관사가 대신]] 합니다.")

# 36 구분 — 입주민 혜택
add("divider", n="06", title="입주민에게 [[직접]] 돌아가는 혜택",
    bl=["박람회 상품권 1+1", "백화점 상품권 무상 증정", "정회원 세대당 60만원 상당", "사전점검 대행 최대 50%", "경품·사은품·편의시설"])
S6 = "06. 입주민 혜택"
add("std", sec=S6, title="박람회 [[상품권]] 1+1", lead="방문만 해도 받습니다. 계약을 강요하지 않습니다.",
    body=cards([
        dict(lb="GIFT 01", big="30", unit="만원", nm="계약금 사용 상품권", ds="일반회원 20만원 / 정회원 10만원 추가 지급. 품목(업체)당 1매 사용."),
        dict(lb="GIFT 02", big="5", unit="만원", nm="특정 입주민 추가 지원", ds="소년·소녀가장, 80세 이상 노부모 부양, 장애인, 다자녀(3자녀↑), 다문화, 임산부."),
        dict(lb="GIFT 03", big="백화점", nm="백화점 상품권", ds="박람회 방문·신청 시 무상 제공. 1세대 1회 교부, 행사장 내 현금처럼 사용 가능."),
        dict(lb="GIFT 04", big="10", unit="%", nm="현장 특별할인", ds="박람회 기간 품목별 현장 할인 특가 최대 10% 추가할인."),
    ]),
    kp="[[방문(체크인)만 해도 받는 혜택]] 중심으로 구성합니다.")
add("std", sec=S6, title="정회원 전용 [[세대당 60만원 상당]]", lead="공동구매가보다 더 저렴한 혜택은 오직 엣지컴퍼니에서.",
    body=tiles([dict(lb=f"{i:02d}", nm=n) for i, n in enumerate([
        "백화점 상품권", "도어락 나노코팅", "실링팬 50% 특가", "우물 간접조명", "갤러리조명 2구", "피톤치드 항균",
        "인테리어 30% 할인", "미세촘촘망 거실창", "홈케어 진드기 박멸", "욕실케어 1회", "현관 줄눈 무상",
        "프리미엄 중문", "욕실 휴젠뜨", "화재보험 2년", "사전점검 할인", "경품 응모"], 1)], cols=4, rows_n=4),
    kp=("박람회장 방문 시 세대당 [[600,000원 상당]]의 혜택.", "(품목은 단지 협의 후 확정)"))
add("pricing", sec=S6)
add("std", sec=S6, title="하루가 [[즐거운]] 박람회", lead="계약하러 오는 자리가 아니라, 가족이 놀러 오는 자리로 만듭니다.",
    body=cards([
        dict(lb="EVENT", nm="경품 이벤트", ds="대형가전부터 소형가전까지. 그 외 200여 개 업체 경품."),
        dict(lb="GIFT", nm="사은품 무상 증정", ds="원터치 자동 말발굽(현관 스토퍼) 전 방문 세대. 품목 계약 시 업체 사은품."),
        dict(lb="KIDS", nm="아이 프로그램", ds="키즈 매직쇼 · 페이스페인팅 · 캐리커처 · 네일아트."),
        dict(lb="FACILITY", nm="편의시설", ds="에어바운스 · 영화상영회 · 카페테리아 · 수유실 · 휴게실 · 유모차 대여 · 안마의자."),
    ]),
    kp="협의회 전용 부스를 [[행사장 중앙]]에 배치합니다.")
add("std", sec=S6, title="못 오셔도 [[괜찮습니다]]", lead="온라인 박람회와 사전 서비스로 전 세대를 커버합니다.",
    body=rows([
        ("온라인 박람회 (폐쇄몰)", "오프라인 박람회를 그대로 옮긴 쇼핑몰. 해당 단지 입주민만 입장 가능. 동일 공동구매가 적용."),
        ("라이브 커머스", "행사장 라이브 방송과 영상 제작으로 현장에 못 오신 분들께 그대로 전달."),
        ("평형별 실측 사이즈 제공", "타입별 실측 데이터를 제공해 가구·커튼 사이즈 고민을 줄입니다."),
        ("샘플하우스 운영", "실제 제품을 보고 결정하실 수 있도록 샘플하우스를 운영합니다."),
        ("VR 촬영 · 3D 홈스타일링", "아파트 주변 항공 VR 촬영, 전문가 3D 홈스타일링 제안."),
    ]),
    kp="“박람회 날 일정이 안 돼서”라는 말이 [[손해가 되지 않게]] 합니다.")

# 42 구분 — 주관 실적
add("divider", n="07", title="기록이 [[증명]]합니다.",
    bl=["80개 단지 · 48,523세대", "사송 88% · 에코델타 93%", "레이카운티 4,470세대", "2026년 25개 단지 확정"])
S7 = "07. 주관 실적"
add("std", sec=S7, title="주관 [[성공사례]] · 수임실적", lead="2018년 첫 단지부터 지금까지, 전국에서 이어지고 있습니다.",
    body=cards([
        dict(lb="2025", big="18", nm="진행 단지", ds="양정자이 SK뷰 2,276 · 두산위브 오션시티 2,205 · 에코델타 이편한세상 953 등."),
        dict(lb="2024", big="15", nm="진행 단지", ds="에코델타 대성베르힐 1,120 · 사송 데시앙 1차 1,712 · 힐스테이트 포항 1,717 등."),
        dict(lb="2023", big="12", nm="진행 단지", ds="두산위브 더제니스 센트럴 사하 1,643 · 사상중흥 S-클래스 1,572 등."),
        dict(lb="2026", big="25", nm="확정 단지", ds="이미 일정 확정. 입주박람회 업계 최대 규모 운영 예정."),
    ]),
    kp="전부 [[1,000세대 이상 대단지]] 운영 경험 포함.")
add("std", sec=S7, title="한 단지가 아니라 [[한 신도시]]를 맡습니다",
    lead="그 동네 입주민·시공사·자재 흐름을 이미 다 알고 있다는 뜻입니다.",
    body=cards([
        dict(lb="양산 사송신도시", big="88", unit="%", nm="단지 입주의 88% 주관",
             ds="데시앙 1차 1,712 · 데시앙 3차 672 · 우미린 688 · 더샵 3차 533 · LH 신혼희망타운 2차 479 · 제일풍경채 452 · 롯데캐슬(진행)"),
        dict(lb="부산 강서 에코델타시티", big="93", unit="%", nm="단지 입주의 93% 진행",
             ds="대성베르힐 1,120 · 이편한세상 953 · 푸르지오린 886 · 강서자이 856 · 대방 디에트르(진행) · 중흥S클래스(예정)"),
    ]),
    kp="신도시 전체를 연속으로 맡을 수 있는 [[운영 체력]]입니다.")
add("std", sec=S7, title="[[대단지]] 운영 경험", lead="규모가 커질수록 운영의 차이가 드러납니다.",
    body=tiles([dict(lb=y, big=n, unit="세대", nm=nm) for y, n, nm in [
        ("2025", "4,470", "레이카운티"), ("2025", "2,276", "양정자이 SK뷰"), ("2025", "2,205", "두산위브 오션시티"),
        ("2021", "1,768", "양산 이지더원 랜드파크"), ("2024", "1,717", "힐스테이트 포항"), ("2024", "1,712", "사송 데시앙 1차"),
        ("2023", "1,643", "두산위브 더제니스 사하"), ("2023", "1,572", "사상중흥 S-클래스"), ("2020", "1,337", "덕계 두산위브 1차")]],
        cols=3, rows_n=3),
    kp="1,000세대 이상 단지만 모아도 [[이 정도]]입니다.")
add("std", sec=S7, title="행사는 [[운영]]이 전부입니다", lead="기획 → 준비 → 당일 → 입주 후까지 하나의 팀이 끝까지 갑니다.",
    body=rows([
        ("D-5개월", "공식 카페 디자인 지원·활성화, 주관사 선정 감사글, 현수막 설치."),
        ("D-4개월", "카페 이벤트 운영, 참여업체 모집 공고(입찰), 행사장 대관(컨벤션·체육관)."),
        ("D-3개월", "업체 선정 PT 및 현장 평가, 공동구매 업체 협약식."),
        ("D-2개월", "사전점검 설명회·공용부 하자점검·열화상 카메라/라돈 검출기 무료 대여·단지별 무료 실측."),
        ("D-1개월 ~ 당일", "입점업체 단가표 공개·A/S 각서 제출, 박람회 세팅, 주말 양일 개최, 2차 박람회 협의."),
    ], title_w=210),
    kp="행사 후에도 콜센터·베이스캠프·CRM이 [[계속 돌아갑니다.]]")
add("closing", sec="CLOSING")
add("contact")


# ============================================================ 특수 페이지
def p_cover():
    return """<section class="page cv">
<div class="top"><div><div class="logo">EG</div><div class="en">EDGE COMPANY</div></div>
<div class="who">주식회사 엣지컴퍼니<br>입주박람회 전문 주관사</div></div>
<div class="mid"><span class="pill">입주박람회 주관사 제안</span>
<h1>박람회를 여는 회사가 아니라,<br><em>단지를 완성시키는 회사.</em></h1>
<div class="tag2">8년 · 80개 단지 · 48,523세대와 함께한 운영 경험을 한 권으로 정리했습니다.</div>
<div class="stats">
<div><b>17만원<small>(VAT 포함)</small></b><span>세대당 발전지원금 상당</span></div>
<div><b>현금 1억</b><span>하자 예치금 거치</span></div>
<div><b>10억 / 2년</b><span>이행보증보험</span></div>
<div><b>8가지</b><span>협의회 전용 무상 단지지원</span></div>
</div></div>
<div class="bt"><span>SUMMARY PROPOSAL · 요약제안서</span><span>2026</span></div>
</section>"""


TOC = [
    [("01", "회사 역량", ["한 장 요약", "실적·성장", "재무·인증", "전국 지사망", "직영 운영", "대표와 채널"]),
     ("02", "조명 특화", ["경관조명 컨설팅", "직수입·생산·시공", "KC 인증·면허", "커뮤니티 업그레이드"])],
    [("03", "안전망", ["하자예치금 1억", "이행보증 10억", "업체 하자보증", "48시간·10년 A/S", "베이스캠프", "콜센터·선보상"]),
     ("04", "업체선정", ["4단계 심사", "지역업체 95%", "최저가 보장", "계약·환불 보호"])],
    [("05", "협의회 지원", ["발전지원금 17만원", "8가지 무상 지원", "조경 분석보고서", "시설 업그레이드"]),
     ("06", "입주민 혜택", ["상품권·백화점권", "정회원 14종", "사전점검", "이벤트·편의"])],
]


def p_toc(no):
    cols = []
    for col in TOC:
        ss = []
        for n, name, items in col:
            li = "".join(f"<li><i>{k:02d}</i>{html.escape(x)}</li>" for k, x in enumerate(items, 1))
            ss.append(f'<div class="s"><div class="sn">{n}</div><h3>{name}</h3><ul>{li}</ul></div>')
        cols.append(f'<div class="col">{"".join(ss)}</div>')
    body = f'<div class="toc">{"".join(cols)}</div>'
    return render_std(no, "CONTENTS · 목차", "요약제안서 [[목차]]", None, body, None)


def p_divider(n, title, bl):
    b = "".join(f"<span>{html.escape(x)}</span>" for x in bl)
    return f"""<section class="page dv"><div class="n">{n}</div><h2>{t(title)}</h2><div class="bar"></div>
<div class="bl">{b}</div></section>"""


def p_divider_lx():
    return """<section class="page dv dv-lx"><div class="art"></div><div class="veil"></div>
<div class="in"><div class="n">02</div>
<h2>경관조명은 <em>우리가 책임</em>집니다.</h2>
<div class="bar"></div>
<div class="kick">아파트 경관조명, <em>컨설팅</em>이 먼저입니다.</div>
<div class="flow">
<div class="st"><i>STEP 01</i><b>설계</b></div><span class="ar">→</span>
<div class="st"><i>STEP 02</i><b>생산</b></div><span class="ar">→</span>
<div class="st"><i>STEP 03</i><b>직접시공</b></div></div>
<div class="bl"><span>해외 직수입 라인</span><span>KC 인증</span><span>전기공사업 면허 시공</span><span>커뮤니티 조명 업그레이드</span></div>
</div></section>"""


def p_landscape(no, sec):
    steps = [
        ("assets/경관조명_1_설계.svg", "STEP 01 · CONSULTING", "설계", "경관조명 컨설팅·설계",
         "조도(lux)·색온도·배광을 단지 동선과 외관에 맞춰 설계하고, [[도면으로 제안]]합니다.", True),
        ("assets/경관조명_2_생산.svg", "STEP 02 · PRODUCTION", "생산", "단지 맞춤 생산",
         "직수입·자체 생산 라인에서 설계 사양 그대로 제작. [[KC 인증 제품]]만 납품합니다.", False),
        ("assets/경관조명_3_시공.svg", "STEP 03 · CONSTRUCTION", "직접시공", "면허 기반 직접 시공",
         "전기공사업 등록업체가 [[외주 없이 직접 시공]]하고, A/S까지 책임집니다.", False),
    ]
    parts = []
    for i, (img, lb, big, nm, ds, key) in enumerate(steps):
        if i:
            parts.append('<div class="ar">→</div>')
        parts.append(f'<div class="card{" key" if key else ""}"><img src="{img}" alt="">'
                     f'<div class="tx"><div class="lb">{lb}</div><div class="big">{big}</div>'
                     f'<div class="nm">{nm}</div><div class="ds">{t(ds)}</div></div></div>')
    body = f'<div class="lx">{"".join(parts)}</div>'
    return render_std(no, sec, "[[아파트 경관조명]] 컨설팅 · 설계 · 생산 · 시공",
                      "단지의 밤 얼굴이 곧 단지 가치입니다. 설계 → 생산 → 직접시공, 한 회사가 끝까지 책임집니다.",
                      body, "협의회 협의 후 [[단지 맞춤 경관조명 제안서]]를 별도 제출합니다.")


def p_bars(no, sec, title, lead, data, kp):
    mx = max(v for _, v in data)
    cs = "".join(f'<div class="c"><div class="v">{v}</div><div class="b" style="height:{v/mx*82:.1f}%"></div>'
                 f'<div class="y">{y}</div></div>' for y, v in data)
    return render_std(no, sec, title, lead, f'<div class="bars">{cs}</div>', kp)


def p_hi_money(no, sec):
    body = """<div class="hi"><div class="tag">★ 차별화 포인트</div>
<div class="num"><span class="pre">현금</span><span class="v">1억</span></div>
<div class="nm2">하자 예치금 거치</div>
<p>타 주관사는 <em>참여 업체에게 받은 돈</em>으로 예치합니다.<br>엣지컴퍼니는 <em>주관사 순수 자산</em>으로 직접 깔아둡니다.</p>
<div class="chips"><span>협의회+주관사 공동통장</span><span>하자 시 즉시 집행</span><span>법무법인 송달 지연 없음</span></div></div>"""
    return render_std(no, sec, "", None, body, "업체 사고·도산 시 [[입주민이 먼저 보상]]받습니다.").replace("<h1></h1>\n", "").replace('<div class="rule"></div>', "")


def p_hi_fund(no, sec):
    body = """<div class="hi"><div class="tag">★★ 핵심 제안</div>
<div class="num"><span class="pre">세대당</span><span class="v">17만원</span><span class="post">상당 · 부가세 포함</span></div>
<div class="nm2">발전지원금</div>
<p>박람회 참가비가 아니라 <em>단지로 돌아가는 금액</em>입니다.<br>세대수 × 17만원 규모의 발전지원금을 협의회와 협의해 집행합니다.</p>
<div class="chips"><span>현금성 지원</span><span>단지 시설 투자</span><span>협의회 활동 지원</span></div></div>"""
    return render_std(no, sec, "", None, body, "예: 1,000세대 단지 기준 [[1억 7천만원 상당]]의 발전지원 규모.").replace("<h1></h1>\n", "").replace('<div class="rule"></div>', "")


def p_pricing(no, sec):
    tiers = [("BASIC", "50", "2명 · 1시간 50분", "13,500원", "6,750원", "정비점검·육안점검·장비보고서"),
             ("STANDARD", "35", "3명 · 1시간 50분", "14,500원", "9,450원", "+ 건축전문가·하자사진촬영"),
             ("PREMIUM", "35", "3명(1차)+2명(2차)", "25,000원", "16,250원", "입주 후 점검 1회 포함·보고서 2회")]
    cs = "".join(f'<div class="card"><div class="lb">{a}</div><div class="big">{b}<small>% 할인</small></div>'
                 f'<div class="nm">{c}</div><div class="ds">평당 {d} → <em>{e}</em><br>{f}</div></div>'
                 for a, b, c, d, e, f in tiers)
    body = f'<div class="cards" style="grid-template-columns:repeat(3,1fr)">{cs}</div>'
    return render_std(no, sec, "[[사전점검]] 대행 · 최대 50% 할인", "내 집 하자를 전문가가 대신 봐드립니다.", body,
                      "이벤트 당첨 세대는 [[사전점검 동행 무상]] 서비스.")


def p_closing(no, sec):
    items = [("세대당 17만원 상당 발전지원금", "단지로 돌아가는 금액. 협의회 협의 후 집행"),
             ("하자 예치금 현금 1억 거치", "주관사 순수 자산·공동통장·즉시 집행"),
             ("이행보증보험 2년 10억", "증권 실물 제출"),
             ("협의회 전용 8가지 무상 지원", "별도 비용 없음·자체 인력"),
             ("지역업체 95% 선정", "48시간 A/S가 가능한 거리"),
             ("최저가 보장 차액 10배", "동일 제품 확인 시 보상"),
             ("48시간 하자보수 · 10년 A/S", "베이스캠프·콜센터 상시 운영"),
             ("경관조명 컨설팅 · 설계 · 생산 · 직접시공", "조명 직수입·KC 인증·면허 시공까지 한 회사")]
    its = "".join(f'<div class="it"><div class="no">{i:02d}</div><div><b>{html.escape(a)}</b><p>{html.escape(b)}</p></div></div>'
                  for i, (a, b) in enumerate(items, 1))
    return render_std(no, sec, "엣지컴퍼니가 [[약속드리는 것]]", "제안서에 쓴 것은 전부 계약서와 증빙으로 남깁니다.",
                      f'<div class="cl">{its}</div>', "못 지키면 [[주관사 자격 철회 동의서]]를 쓰겠습니다.")


def p_contact():
    return """<section class="page cv">
<div class="top"><div><div class="logo">EG</div><div class="en">EDGE COMPANY</div></div>
<div class="who">주식회사 엣지컴퍼니<br>대표이사 고진식</div></div>
<div class="mid"><span class="pill">CONTACT</span>
<h1>단지가 끝날 때까지,<br><em>끝까지 함께하겠습니다.</em></h1>
<div class="tag2">입주예정자협의회·시공사·협력업체 모두 환영합니다. 가장 편한 방법으로 연락 주십시오.</div>
<div class="contacts">
<div><b>1533-3210</b><span>본사 대표번호</span></div>
<div><b>010-3345-6107</b><span>대표이사 직통</span></div>
<div><b>010-7273-9901</b><span>주관사업 총괄 본부장</span></div>
<div class="me"><b>EDGE__COMPANY@NAVER.COM</b><span>이메일 문의</span></div>
</div>
<div class="addr">울산 본사 · 울산광역시 울주군 청량읍 상남1길 28, 2동 &nbsp;|&nbsp; 부산 지사 · 해운대구 &nbsp;|&nbsp; 대전 지사<br>
전기공사업 등록 제 울산-00821호 · ISO 9001/14001/45001 · 삼성전자 MOU 체결</div>
</div>
<div class="bt"><span>SUMMARY PROPOSAL · 요약제안서</span><span>주식회사 엣지컴퍼니</span></div>
</section>"""


# ============================================================ 빌드
def build_html():
    out = []
    for no, (kind, kw) in enumerate(PAGES, 1):
        if kind == "cover":
            out.append(p_cover())
        elif kind == "toc":
            out.append(p_toc(no))
        elif kind == "divider":
            out.append(p_divider(**kw))
        elif kind == "divider_lx":
            out.append(p_divider_lx())
        elif kind == "landscape":
            out.append(p_landscape(no, **kw))
        elif kind == "bars":
            out.append(p_bars(no, **kw))
        elif kind == "hi_money":
            out.append(p_hi_money(no, **kw))
        elif kind == "hi_fund":
            out.append(p_hi_fund(no, **kw))
        elif kind == "pricing":
            out.append(p_pricing(no, **kw))
        elif kind == "closing":
            out.append(p_closing(no, **kw))
        elif kind == "contact":
            out.append(p_contact())
        else:
            out.append(render_std(no, kw["sec"], kw["title"], kw.get("lead"), kw["body"], kw.get("kp")))
    doc = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<title>엣지컴퍼니 요약제안서</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>{CSS}</style></head><body>
{chr(10).join(out)}
</body></html>"""
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"HTML: {OUT_HTML} ({len(PAGES)} pages)")


def find_chrome():
    cands = [os.environ.get("CHROME"), "/opt/pw-browsers/chromium",
             shutil.which("chromium"), shutil.which("google-chrome"), shutil.which("chrome"),
             r"C:\Program Files\Google\Chrome\Application\chrome.exe",
             r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
             r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]
    return next((c for c in cands if c and os.path.exists(c)), None)


def build_pdf():
    exe = find_chrome()
    if not exe:
        print("크롬/엣지를 찾지 못해 PDF 생략 (HTML을 브라우저에서 인쇄 → PDF 저장 가능)")
        return
    url = pathlib.Path(OUT_HTML).as_uri()
    subprocess.run([exe, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=8000", f"--print-to-pdf={OUT_PDF}", url],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"PDF : {OUT_PDF}")


if __name__ == "__main__":
    build_html()
    if "--no-pdf" not in sys.argv:
        build_pdf()
