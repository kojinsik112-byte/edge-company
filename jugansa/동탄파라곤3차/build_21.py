# -*- coding: utf-8 -*-
"""동탄2 신동 A58BL 파라곤3차 — 공동구매 입찰 제안서 [2-1] (자유양식, 본편).

통합제안서 기본틀(152p)의 실제 사진·자료를 뽑아(extract_assets.py → assets21/) 동탄 임대 단지에 맞게 새로 구성.
- 순서: 공고 4항 업무범위 · 5항 평가요소(서비스 능력·단가·A/S·사후관리·입주지원)에 맞춤
- 용어: 임예협(임차예정자협의회) · 세대수·실적·주소는 data.py(제출서류 8·별지와 같은 숫자)
- 제외: 견본·AI 등록증, AI 인물 그림, 입증 어려운 표현(최초·최고·전국최저가·200% 등)
밝은 배경(인쇄·PDF 열람용), 네이비·골드는 회사 표준.

사용: python extract_assets.py <통합제안서.pdf>   # 사진 준비(1회)
      python build_21.py                         # HTML + PDF
"""
import html
import os
import pathlib
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "요약제안서")]
import data as D  # noqa: E402
from build import find_chrome  # noqa: E402

NAME = "엣지컴퍼니_동탄파라곤3차_2-1_입찰제안서"
OUT_HTML = os.path.join(HERE, NAME + ".html")
OUT_PDF = os.path.join(HERE, NAME + ".pdf")
A = "assets21/"
SVG = "../요약제안서/assets/"
HH = D.SITE["households"]
FUND = HH * 15  # 만원
FUND_S = f"{FUND // 10000}억 {FUND % 10000:,}만원"


def t(s):
    s = html.escape(s, quote=False)
    return re.sub(r"\[\[(.+?)\]\]", r"<em>\1</em>", s)


# ============================================================ CSS
CSS = r"""
@page{size:297mm 210mm;margin:0}
:root{--bg:#F7F4EE;--paper:#FFFFFF;--navy:#13233A;--navy2:#0D1E33;--gold:#A9864A;--gold2:#C8A86A;--gold3:#E6CF9F;
  --ink:#1B2433;--sub:#4D5868;--mute:#8A93A0;--line:#E2DACB;
  --sans:'Pretendard','Malgun Gothic','맑은 고딕',sans-serif;--serif:Georgia,'Times New Roman',serif}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#d9d4ca}
body{font-family:var(--sans);color:var(--ink);word-break:keep-all;-webkit-print-color-adjust:exact;print-color-adjust:exact}
em{font-style:normal;color:var(--gold);font-weight:inherit}
.page{width:297mm;height:210mm;position:relative;overflow:hidden;page-break-after:always;break-after:page;background:var(--bg);
  display:flex;flex-direction:column;padding:28px 46px 0 46px}
.page:last-child{page-break-after:auto;break-after:auto}
@media screen{body{padding:20px 0}.page{margin:0 auto 20px;box-shadow:0 8px 30px rgba(0,0,0,.25)}}
.page:before{content:'';position:absolute;left:0;top:0;bottom:0;width:8px;background:var(--navy)}
.hd{display:flex;justify-content:space-between;align-items:center;height:26px}
.hd .l{display:flex;align-items:center;gap:14px}
.logo{font-family:var(--serif);font-weight:700;font-size:24px;color:var(--navy);line-height:1}
.sec{font-size:12.5px;font-weight:700;letter-spacing:.28em;color:var(--gold)}
.hd .r{font-size:12px;color:var(--mute)}
.hd .r b{color:var(--navy);margin-left:8px}
h1{font-size:33px;font-weight:800;color:var(--navy);margin-top:12px;line-height:1.22;letter-spacing:-.01em}
.lead{font-size:17.5px;color:var(--sub);margin-top:7px;line-height:1.45}
.rule{height:2px;margin:13px 0 16px;background:linear-gradient(90deg,var(--gold2),rgba(200,168,106,.25) 60%,transparent)}
.ct{flex:1;min-height:0;display:flex;flex-direction:column}
.kp{margin-top:14px;background:var(--navy);border-radius:10px;padding:12px 24px;display:flex;align-items:center;gap:22px;color:#fff}
.kp b{font-size:12px;letter-spacing:.3em;color:var(--gold3);white-space:nowrap}
.kp span{font-size:17.5px;font-weight:700;line-height:1.4}
.kp em{color:var(--gold3)}
.kp small{font-size:14px;font-weight:400;color:#B9C3D0;margin-left:6px}
.ft{height:36px;display:flex;justify-content:space-between;align-items:center;font-size:11.5px;color:var(--mute)}

/* cards */
.cards{flex:1;display:grid;gap:14px;min-height:0}
.card{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:20px 22px;display:flex;flex-direction:column;justify-content:center;min-height:0;overflow:hidden}
.card.hl{border:1.5px solid var(--gold2);background:#FFFCF5}
.card.img{padding:0;justify-content:flex-start}
.card.img img{width:100%;flex:1;min-height:0;object-fit:cover;display:block}
.card.img .tx{padding:13px 18px 15px}
.lb{font-size:12px;font-weight:700;letter-spacing:.24em;color:var(--gold)}
.big{font-size:42px;font-weight:800;color:var(--navy);line-height:1.1;margin-top:6px;letter-spacing:-.01em}
.big small{font-size:19px;font-weight:700;margin-left:2px;color:var(--gold)}
.nm{font-size:20.5px;font-weight:800;color:var(--navy);margin-top:6px;line-height:1.3}
.ds{font-size:16px;color:var(--sub);margin-top:7px;line-height:1.5}
.ds em{font-weight:700}

/* rows */
.rows{flex:1;display:flex;flex-direction:column;justify-content:space-evenly;min-height:0}
.row{display:grid;gap:0 20px;align-items:center;padding:0 0 11px;border-bottom:1px dashed #D6CDBB}
.row:last-child{border-bottom:0;padding-bottom:0}
.no{width:40px;height:40px;border-radius:9px;background:var(--navy);color:var(--gold3);font-weight:800;font-size:16px;display:flex;align-items:center;justify-content:center}
.row .tt{font-size:20px;font-weight:800;color:var(--navy);line-height:1.3}
.row .dd{font-size:16.5px;color:var(--sub);line-height:1.5}
.row .dd em{font-weight:700}

/* photos */
.grid{flex:1;display:grid;gap:10px;min-height:0}
figure{position:relative;border-radius:10px;overflow:hidden;background:#ddd;min-height:0}
figure img{width:100%;height:100%;object-fit:cover;display:block}
.split figure,.ct>figure{flex:1 1 0;min-height:0}
figure.contain{background:#fff;border:1px solid var(--line)}
figure.contain img{object-fit:contain}
figcaption{position:absolute;left:0;right:0;bottom:0;padding:8px 12px;font-size:14px;font-weight:700;color:#fff;
  background:linear-gradient(0deg,rgba(13,30,51,.92),rgba(13,30,51,.55))}
.split{flex:1;display:grid;gap:26px;min-height:0}
.split>div{min-height:0;display:flex;flex-direction:column}
.bul{display:flex;flex-direction:column;justify-content:center;gap:16px;flex:1}
.bul>div{position:relative;padding-left:22px}
.bul>div:before{content:'';position:absolute;left:0;top:8px;width:9px;height:9px;border-radius:50%;background:var(--gold2)}
.bul b{display:block;font-size:19.5px;color:var(--navy);line-height:1.35}
.bul p{font-size:16px;color:var(--sub);margin-top:4px;line-height:1.5}
.bul p em{font-weight:700}

/* table */
.tbl{width:100%;border-collapse:collapse;background:var(--paper);border-radius:10px;overflow:hidden}
.tbl th{background:var(--navy);color:#fff;font-size:14px;font-weight:700;padding:9px 12px;text-align:left;letter-spacing:.04em}
.tbl td{font-size:15.5px;padding:8px 12px;border-bottom:1px solid #ECE5D7;color:var(--sub);line-height:1.42;vertical-align:middle}
.tbl tr:last-child td{border-bottom:0}
.tbl td.k{color:var(--navy);font-weight:800}
.tbl td.g{color:var(--gold);font-weight:800;background:#FBF7EE}
.tbl td.c{text-align:center}
.tbl td.r{text-align:right;font-variant-numeric:tabular-nums}
.tbl tr.sum td{background:#F3ECDD;color:var(--navy);font-weight:800}
.tbl em{font-weight:700}
.tbl.sm td{font-size:14.5px;padding:6px 12px}

/* flow */
.flow{display:flex;align-items:stretch;gap:8px}
.flow .st{flex:1;background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:12px 14px;text-align:center}
.flow .st i{display:block;font-style:normal;font-size:11.5px;font-weight:700;letter-spacing:.2em;color:var(--gold)}
.flow .st b{display:block;font-size:17.5px;color:var(--navy);margin-top:4px;line-height:1.3}
.flow .st p{font-size:14px;color:var(--sub);margin-top:4px;line-height:1.4}
.flow .ar{display:flex;align-items:center;color:var(--gold2);font-size:20px;font-weight:800}

/* tags */
.tags{display:flex;flex-wrap:wrap;gap:8px}
.tags span{background:var(--paper);border:1px solid var(--line);border-radius:99px;padding:6px 14px;font-size:15px;color:var(--navy);font-weight:600}
.tags span.g{border-color:var(--gold2);background:#FFF8EA}
.box{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:16px 20px;min-height:0}
.box h3{font-size:18px;color:var(--navy);font-weight:800;margin-bottom:10px}
.box h3 em{font-weight:800}
.note{font-size:13px;color:var(--mute);margin-top:8px}

/* divider */
.dv{background:var(--navy2);padding:0;flex-direction:row}
.dv:before{display:none}
.dv .tx{width:52%;padding:0 60px 0 76px;display:flex;flex-direction:column;justify-content:center;color:#fff;position:relative;z-index:1}
.dv .n{font-family:var(--serif);font-size:96px;color:var(--gold2);line-height:1}
.dv h2{font-size:44px;font-weight:800;margin-top:14px;line-height:1.25}
.dv h2 em{color:var(--gold3)}
.dv .bar{width:150px;height:2px;background:var(--gold2);margin:24px 0 22px}
.dv .bl{display:flex;flex-direction:column;gap:9px;font-size:18px;color:#C9D2DE}
.dv .bl span:before{content:'· ';color:var(--gold2)}
.dv .pic{position:absolute;right:0;top:0;bottom:0;width:58%}
.dv .pic img{width:100%;height:100%;object-fit:cover;display:block}
.dv .pic:after{content:'';position:absolute;inset:0;background:linear-gradient(90deg,var(--navy2) 0%,rgba(13,30,51,.72) 30%,rgba(13,30,51,.12) 100%)}

/* cover / contact */
.cv{background:var(--navy2);padding:0;flex-direction:row}
.cv:before{display:none}
.cv .tx{width:60%;padding:52px 40px 40px 70px;display:flex;flex-direction:column;color:#fff;position:relative;z-index:1}
.cv .logo{color:var(--gold2);font-size:42px}
.cv .en{font-size:12.5px;letter-spacing:.5em;color:var(--gold2);font-weight:700;margin-top:10px}
.cv .mid{flex:1;display:flex;flex-direction:column;justify-content:center}
.pill{align-self:flex-start;border:1px solid var(--gold2);border-radius:99px;padding:7px 22px;font-size:15px;font-weight:700;letter-spacing:.18em;color:var(--gold3)}
.cv h1{color:#fff;font-size:44px;margin-top:20px;line-height:1.28}
.cv h1 em{color:var(--gold3)}
.cv .tag2{font-size:18px;color:#C9D2DE;margin-top:16px;line-height:1.55}
.stats{display:flex;gap:30px;margin-top:28px;flex-wrap:wrap}
.stats div{border-left:2px solid var(--gold2);padding-left:14px}
.stats b{display:block;font-size:26px;font-weight:800;color:var(--gold3);line-height:1.2}
.stats b small{font-size:11px;font-weight:400;color:#B9C3D0;margin-left:3px}
.stats span{font-size:14px;color:#C9D2DE}
.cv .bt{font-size:14px;color:#B9C3D0;display:flex;justify-content:space-between}
.cv .pic{position:absolute;right:0;top:0;bottom:0;width:50%}
.cv .pic img{width:100%;height:100%;object-fit:cover}
.cv .pic:after{content:'';position:absolute;inset:0;background:linear-gradient(90deg,var(--navy2) 0%,rgba(13,30,51,.55) 35%,rgba(13,30,51,0) 100%)}
.contacts{display:grid;grid-template-columns:repeat(3,auto);gap:18px 40px;margin-top:26px;justify-content:start}
.contacts div{border-left:2px solid var(--gold2);padding-left:14px}
.contacts b{display:block;white-space:nowrap;font-size:24px;font-weight:800;color:var(--gold3);line-height:1.2}
.contacts span{font-size:14.5px;color:#C9D2DE}
.contacts .me{grid-column:span 3}
.addr{font-size:14.5px;color:#C9D2DE;margin-top:22px;line-height:1.7}

/* toc */
.toc{flex:1;display:grid;grid-template-columns:repeat(4,1fr);gap:12px;min-height:0}
.toc .s{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:14px 18px}
.toc .s .sn{font-family:var(--serif);font-size:28px;color:var(--gold);line-height:1}
.toc .s h3{font-size:18.5px;font-weight:800;color:var(--navy);margin:5px 0 6px}
.toc .s li{list-style:none;font-size:14.5px;color:var(--sub);line-height:1.6}
.toc .s li:before{content:'· ';color:var(--gold2)}

/* org */
.org{display:flex;flex-direction:column;align-items:center;gap:10px}
.org .n1{background:var(--navy);color:#fff;border-radius:10px;padding:10px 26px;font-size:18px;font-weight:800;text-align:center}
.org .n1 small{display:block;font-size:12.5px;color:var(--gold3);font-weight:600}
.org .ln{width:2px;height:14px;background:var(--gold2)}
.org .teams{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;width:100%}
.org .teams div{background:var(--paper);border:1px solid var(--line);border-top:3px solid var(--gold2);border-radius:8px;padding:10px 8px;text-align:center}
.org .teams b{display:block;font-size:15.5px;color:var(--navy)}
.org .teams p{font-size:13px;color:var(--sub);margin-top:4px;line-height:1.4}
"""

# ============================================================ 블록
PAGES = []


def add(html_fn):
    PAGES.append(html_fn)


def render(no, sec, title, lead, body, kp=None):
    if True:
        kp_html = ""
        if kp:
            if isinstance(kp, tuple):
                kp_html = f'<div class="kp"><b>KEY POINT</b><span>{t(kp[0])}<small>{t(kp[1])}</small></span></div>'
            else:
                kp_html = f'<div class="kp"><b>KEY POINT</b><span>{t(kp)}</span></div>'
        return f"""<section class="page">
<div class="hd"><div class="l"><span class="logo">EG</span><span class="sec">{sec}</span></div>
<div class="r">동탄2 신동 A58BL 파라곤 3차 · 임차예정자협의회 주관사 제안 <b>{no:02d}</b></div></div>
<h1>{t(title)}</h1>{f'<div class="lead">{t(lead)}</div>' if lead else ''}
<div class="rule"></div><div class="ct">{body}</div>{kp_html}
<div class="ft"><span>{D.COMPANY} · 대표이사 {D.CEO}</span><span>EDGE COMPANY · 공동구매 입찰 제안서 [2-1]</span></div>
</section>"""


def std(sec, title, lead, body, kp=None):
    add(lambda no: render(no, sec, title, lead, body, kp))


def divider(n, title, bl, img):
    b = "".join(f"<span>{html.escape(x)}</span>" for x in bl)
    add(lambda no: f"""<section class="page dv"><div class="pic"><img src="{A}{img}.jpg" alt=""></div>
<div class="tx"><div class="n">{n}</div><h2>{t(title)}</h2><div class="bar"></div><div class="bl">{b}</div></div></section>""")


def cards(items, cols=None, rows_n=None):
    cols = cols or len(items)
    out = []
    for it in items:
        big = ""
        if it.get("big"):
            u = f'<small>{t(it["unit"])}</small>' if it.get("unit") else ""
            big = f'<div class="big">{t(it["big"])}{u}</div>'
        inner = (f'<div class="lb">{t(it["lb"])}</div>' if it.get("lb") else "") + big \
            + (f'<div class="nm">{t(it["nm"])}</div>' if it.get("nm") else "") \
            + (f'<div class="ds">{t(it["ds"])}</div>' if it.get("ds") else "")
        if it.get("img"):
            out.append(f'<div class="card img"><img src="{A}{it["img"]}.jpg" alt=""><div class="tx">{inner}</div></div>')
        else:
            out.append(f'<div class="card{" hl" if it.get("hl") else ""}">{inner}</div>')
    rs = f";grid-template-rows:repeat({rows_n},1fr)" if rows_n else ""
    return f'<div class="cards" style="grid-template-columns:repeat({cols},1fr){rs}">{"".join(out)}</div>'


def rows(items, tw=230):
    out = "".join(f'<div class="row" style="grid-template-columns:40px {tw}px 1fr"><div class="no">{i:02d}</div>'
                  f'<div class="tt">{t(a)}</div><div class="dd">{t(b)}</div></div>' for i, (a, b) in enumerate(items, 1))
    return f'<div class="rows">{out}</div>'


def fig(img, cap=None, contain=False, style=""):
    c = f"<figcaption>{t(cap)}</figcaption>" if cap else ""
    return f'<figure class="{"contain" if contain else ""}" style="{style}"><img src="{A}{img}.jpg" alt="">{c}</figure>'


def grid(items, cols, rows_n=None, contain=False):
    rs = f";grid-template-rows:repeat({rows_n},1fr)" if rows_n else ""
    figs = "".join(fig(i, c, contain) for i, c in items)
    return f'<div class="grid" style="grid-template-columns:repeat({cols},1fr){rs}">{figs}</div>'


def bullets(items):
    return '<div class="bul">' + "".join(f"<div><b>{t(a)}</b><p>{t(b)}</p></div>" for a, b in items) + "</div>"


def split(left, right, cols="46% 1fr"):
    return f'<div class="split" style="grid-template-columns:{cols}"><div>{left}</div><div>{right}</div></div>'


def table(head, body_rows, cls="", widths=None):
    th = "".join(f'<th style="width:{widths[i]}">{h}</th>' if widths and widths[i] else f"<th>{h}</th>"
                 for i, h in enumerate(head))
    trs = []
    for r in body_rows:
        cls_r, cells = (r[0], r[1:]) if isinstance(r[0], str) and r[0].startswith("@") else ("", r)
        tds = []
        for c in cells:
            if isinstance(c, tuple):
                tds.append(f'<td class="{c[1]}">{t(c[0])}</td>')
            else:
                tds.append(f"<td>{t(c)}</td>")
        trs.append(f'<tr class="{cls_r[1:]}">{"".join(tds)}</tr>')
    return f'<table class="tbl {cls}"><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table>'


def flow(steps):
    out = []
    for i, (lb, b, p) in enumerate(steps):
        if i:
            out.append('<div class="ar">›</div>')
        out.append(f'<div class="st"><i>{t(lb)}</i><b>{t(b)}</b>{f"<p>{t(p)}</p>" if p else ""}</div>')
    return f'<div class="flow">{"".join(out)}</div>'


def box(title, inner, style=""):
    return f'<div class="box" style="{style}"><h3>{t(title)}</h3>{inner}</div>'


def tags(items, gold=()):
    return '<div class="tags">' + "".join(f'<span class="{"g" if x in gold else ""}">{html.escape(x)}</span>' for x in items) + "</div>"


def col(*parts, gap=12):
    return f'<div style="display:flex;flex-direction:column;gap:{gap}px;flex:1;min-height:0">{"".join(parts)}</div>'


# ============================================================ 페이지
# --- 표지
add(lambda no: f"""<section class="page cv"><div class="pic"><img src="{A}cover_1.jpg" alt=""></div>
<div class="tx"><div><div class="logo">EG</div><div class="en">EDGE COMPANY</div></div>
<div class="mid"><span class="pill">공동구매 입찰 제안서 [2-1]</span>
<h1>동탄2 신동 A58BL 파라곤 3차<br><em>임차예정자협의회 주관사 선정</em></h1>
<div class="tag2">{HH:,}세대의 10년이 시작되는 자리 — 박람회부터 입주 후 1년까지,<br>임차인의 눈높이로 준비했습니다.</div>
<div class="stats">
<div><b>15만원<small>(VAT 포함)</small></b><span>세대당 발전지원금</span></div>
<div><b>현금 1억</b><span>하자 예치금</span></div>
<div><b>10억 · 2년</b><span>이행보증보험</span></div>
<div><b>48시간</b><span>하자 처리 원칙</span></div></div></div>
<div class="bt"><span>{D.COMPANY} · 대표이사 {D.CEO}</span><span>2026. 10.</span></div></div></section>""")

# --- 인사말
std("GREETING", "믿어주신 순간부터, [[여러분의 10년]]은 저희의 약속이 됩니다",
    "좋은 집은 좋은 선택에서 시작되고, 좋은 선택은 신뢰로 완성됩니다.",
    split(fig("hq_2", "엣지컴퍼니 본사 사옥 (울산 울주군 청량읍 온산로 615-1)"),
          col(bullets([
              ("전문가 집단이 직접 관리합니다", "박람회 기획부터 업체 검증·계약·A/S까지 외주 없이 엣지컴퍼니 인력이 직접 맡습니다."),
              ("임차인이 직접 확인하는 투명한 공동구매", "단가표 사전 공개, 임예협·주관사 양쪽 이메일 동시 접수, 임예협 최종 컨펌."),
              ("입주 후에도 끊기지 않습니다", "콜센터·공식카페 신문고·카카오채널로 입주 후 1년(협약기간) 이상 연결됩니다."),
              ("임대 단지를 이해합니다", "원상복구·임대사업자 승인·분양전환까지 — 임차인의 10년을 기준으로 품목과 혜택을 설계했습니다."),
          ])), "42% 1fr"),
    "말로 하는 약속이 아니라 [[협약서와 증권으로 남는 약속]]을 드립니다.")

# --- 목차
TOC = [("01", "동탄 파라곤 3차 이해", ["단지 개요", "임대 단지의 차이", "임예협이 원하는 것"]),
       ("02", "회사 소개", ["회사 개요·본사", "재무·신용·인증", "조직·네트워크"]),
       ("03", "주관 실적", ["1,000세대 이상 7건", "신도시 연속 주관", "현장·추천서·감사패"]),
       ("04", "박람회·공동구매 계획", ["추진 일정", "품목·임대 맞춤 분류", "업체 선정·예상 참가 업체", "단가·계약 보호"]),
       ("05", "입주박람회 운영", ["장소·안전·인력", "편의시설·이벤트", "온라인 박람회"]),
       ("06", "A/S·하자보증", ["4중 안전망", "업체 책임·도산 대응", "클레임 데이터·패널티"]),
       ("07", "콜센터·사후관리", ["접수·처리 프로세스", "CRM·베이스캠프", "하자 창구 분리"]),
       ("08", "임예협 업무 지원", ["발전지원금", "카페·홍보 지원", "사전점검·품질 검증", "행정·단지 컨설팅"]),
       ("09", "입주민 혜택", ["박람회 혜택", "정회원 혜택", "실측·샘플하우스"]),
       ("10", "동탄 특화 제안", ["임대 맞춤 5가지", "조명·실링팬 특화", "약속·연락처"])]


def p_toc(no):
    ss = "".join(f'<div class="s"><div class="sn">{n}</div><h3>{html.escape(nm)}</h3><ul>'
                 + "".join(f"<li>{html.escape(x)}</li>" for x in its) + "</ul></div>" for n, nm, its in TOC)
    body = f'<div class="toc" style="grid-template-rows:repeat(3,1fr)">{ss}<div class="s" style="grid-column:span 2;background:var(--navy);color:#fff">' \
           f'<div class="sn" style="color:var(--gold3)">2-2</div><h3 style="color:#fff">제안내용 요약본(별도)</h3>' \
           f'<ul><li style="color:#C9D2DE">박람회·공동구매 계획 / 품목별 예상 참가 업체 / 박람회 특화 제안을 요약한 별도 제출본</li></ul></div></div>'
    return render(no, "CONTENTS", "제안서 [[목차]]", None, body)


add(p_toc)

# --- 읽는 법: 공고 ↔ 제안서
std("HOW TO READ", "공고 요구사항 → [[이 제안서의 답]]", "공고문 4항(업무범위)·5항(평가요소)을 이 제안서의 어느 장에서 답하는지 정리했습니다.",
    split(table(["공고 4항 업무범위", "답하는 장"], [
        ("① 박람회 기획·공동구매 총괄", ("04 · 05", "c")),
        ("② 품목 구성·업체 섭외·계약·가격 검수", ("04", "c")),
        ("③ 입주 후 A/S·하자 접수·이행관리", ("06 · 07", "c")),
        ("④ 사전점검·입주지원·입주설명회 지원", ("08 · 10", "c")),
        ("⑤ 대관·동선·안전·인력·비품·홍보물", ("05", "c")),
        ("⑥ 입주 전·후 전문분야 검토·행정지원", ("08", "c")),
        ("⑦ 카페·공지채널 홍보 콘텐츠", ("08", "c")),
        ("⑧ 기타 임예협 요청 업무 · ⑨ 이벤트", ("05 · 08 · 09", "c")),
    ], "sm", ["70%", None]),
        col(table(["공고 5항 평가요소", "핵심 답"], [
            ("서비스 제공 능력", "1,000세대 이상 주관 7건 · 본사 직접 운영"),
            ("공동구매 단가", "단가표 사전 공개 · 최저가 차액 10배"),
            ("A/S 처리 및 대책", "48시간 처리 · 선보상 · 예치금 1억"),
            ("사후관리", "콜센터·CRM · 최소 2년 무상 A/S"),
            ("입주지원", "사전점검 지원 · 입주설명회 · 베이스캠프"),
        ], "sm", ["38%", None]),
            box("제출서류 연계", '<div class="ds" style="margin:0">8) 실적 증빙 = 03장 · 9) 취소·환불 규정 = 04장 · 별지 #3 A/S 이행각서 = 06장</div>')),
        "52% 1fr"),
    "제안서 내용은 협약서와 같은 효력(공고 9-3) — [[지킬 수 있는 것만]] 적었습니다.")

# ============================================================ 01 단지 이해
divider("01", "동탄 파라곤 3차를 [[먼저 이해]]했습니다", ["단지 개요", "임대 단지 박람회의 차이", "임예협이 원하는 5가지"], "apt_7")
std("01. 단지 이해", "동탄2 신동 A58BL [[파라곤 3차]]", "공고문 단지개요와 공개 분양 자료를 기준으로 정리했습니다.",
    split(table(["항목", "내용"], [
        (("단지명", "k"), "동탄2 신도시 신동 A58BL 파라곤 3차 (민간임대)"),
        (("규모", "k"), f"총 {HH:,}세대 · 18개동 · 지하 2층~지상 20층"),
        (("타입", "k"), "82㎡ 835세대 · 108㎡ 411세대 (2개 타입)"),
        (("입주", "k"), "2027년 2월 28일 예정"),
        (("유형", "k"), "공공지원 민간임대 — 최장 10년 거주 · 최초 계약 시 분양전환 권리 확정 가능"),
        (("시행 · 시공", "k"), "㈜바우하우스 · ㈜라인건설"),
        (("협약기간", "k"), "협약 체결일 ~ 입주 후 1년"),
    ], "", ["22%", None]),
        cards([dict(lb="SCALE", big=f"{HH:,}", unit="세대", ds="1,000세대 이상 주관 경험 그대로"),
               dict(lb="TYPE", big="2", unit="개 타입", ds="커튼·조명 [[규격화]] → 단가 협상력"),
               dict(lb="LEASE", big="10", unit="년", ds="임차인의 10년 = 사후관리 기준", hl=True),
               dict(lb="MOVE-IN", big="2.28", ds="설 연휴 전 박람회로 시공 일정 확보")], cols=2, rows_n=2), "55% 1fr"),
    "타입 2개 · 임대 10년 — [[규격화된 공동구매]]와 [[원상복구 걱정 없는 시공]]이 핵심입니다.")

std("01. 단지 이해", "분양 단지와 [[임대 단지]]는 박람회가 다릅니다", "같은 품목이라도 임차인에게는 판단 기준이 다릅니다.",
    table(["구분", "일반 분양 단지", "동탄 파라곤 3차 (공공지원 민간임대)"], [
        (("시공 결정", "k"), "소유자가 자유롭게 결정", ("임대사업자 승인 · 퇴거 시 [[원상복구]] 고려", "g")),
        (("품목 수요", "k"), "영구 시공(중문·줄눈·붙박이) 중심", ("분양전환 확정 세대 = 영구 시공 / 거주형 세대 = [[무타공·이동식·렌탈]]", "g")),
        (("하자 책임", "k"), "시공사 · 공동구매 업체", ("건물 하자 = 임대사업자 / 공동구매 하자 = 업체·주관사 — [[창구 분리]] 필요", "g")),
        (("의사결정", "k"), "입주예정자협의회", ("임차예정자협의회 + 정회원 임차예정자 평가", "g")),
        (("가격 민감도", "k"), "옵션·브랜드 선호", ("무주택 실수요 — [[단가 투명성]]과 계약금 부담이 핵심", "g")),
        (("사후관리 기간", "k"), "보통 입주 후 2년 내외", ("최장 10년 거주 — [[장기 A/S]]가 실제로 필요", "g")),
    ], "", ["14%", "30%", None]),
    "임차인의 시공은 ‘얼마나 싸게’보다 [[‘나갈 때 문제없나’]]가 먼저입니다.")

std("01. 단지 이해", "공고문에서 읽은 [[임예협이 원하는 5가지]]", "공고 조항마다 임예협의 걱정이 담겨 있습니다. 그 걱정에 하나씩 답합니다.",
    rows([
        ("단가가 오르지 않을 것", "7항 7호 ‘과도한 행사비로 인한 단가 상승’ → 단가표 사전 공개 · 최저가 차액 10배 · 현장 가격 변경 없음 [[(04장)]]"),
        ("A/S를 끝까지 책임질 것", "6항 11호 · 별지 #3 → 48시간 처리 · 주관사 선보상 · 예치금 1억 · 이행보증 10억 [[(06·07장)]]"),
        ("취소·환불이 명확할 것", "6항 10호 · 제출서류 9) → 계약금 5% 상한 · 시공 전 100% 해약 · 3영업일 환불 [[(04장)]]"),
        ("하도급·연동 계약이 없을 것", "9항 9호 · 별지 #4 → 일괄 도급 없음 · 업체 하청 금지 계약 · 공개 입찰 [[(04장)]]"),
        ("임차인에게 실질 혜택이 갈 것", "4항 4·7·9호 → 사전점검·입주설명회 지원 · 정회원 혜택 · 임대 맞춤 시공 가이드 [[(08~10장)]]"),
    ], 230),
    "평가표의 다섯 칸 — [[서비스 능력 · 단가 · A/S · 사후관리 · 입주지원]]에 모두 답했습니다.")

# ============================================================ 02 회사 소개
divider("02", "엣지컴퍼니는 [[이런 회사]]입니다", ["본사·쇼룸 직접 운영", "자본금 2억 · 현금흐름 A", "ISO 3종 · 삼성전자 MOU", "임직원 10명 + 인턴 4명"], "hq_1")
std("02. 회사 소개", "회사 [[개요]]", "사업자등록증·법인등기부·NICE 기업신용평가 기준입니다.",
    split(table(["항목", "내용"], [
        (("상호 · 대표", "k"), f"{D.COMPANY} · 대표이사 {D.CEO}"),
        (("설립", "k"), "2022년 2월 28일 (법인)"),
        (("본사", "k"), D.ADDRESS),
        (("업태 · 종목", "k"), "건설업 · 도소매 · 서비스 / 전기공사 · 조명 · [[전시·박람회 및 행사 대행업]] · 광고 대행업"),
        (("자본금", "k"), "2억원"),
        (("인원", "k"), "임직원 10명 + 인턴 4명 (4대보험 가입자 명부 기준)"),
        (("인증 · 제휴", "k"), "ISO 9001 · 14001 · 45001 / 삼성전자 MOU"),
        (("면허", "k"), "전기공사업 등록 (울산-00821호)"),
    ], "", ["20%", None]), fig("hq_1", "본사 사옥 — 본사·쇼룸·시공팀 운영"), "62% 1fr"),
    ("공고 참가자격 6-2 ‘행사대행·전시·광고기획’ 업종 — [[사업자등록증에 등록]]되어 있습니다.", ""))

std("02. 회사 소개", "본사·쇼룸을 [[직접]] 운영합니다", "외주 파트너가 아니라 본사 인력과 공간에서 상담·전시·회의가 이뤄집니다.",
    grid([("hq_in_2", "제품 쇼룸"), ("hq_in_3", "전시 갤러리"), ("hq_in_4", "회의실"),
          ("hq_in_6", "본사 로비"), ("hq_in_7", "상담 공간"), ("hq_in_5", "본사 사인 · 유튜브 채널")], 3, 2),
    "임예협 회의·업체 PT를 [[본사에서 직접]] 진행할 수 있습니다.")

std("02. 회사 소개", "재무 건전성 · [[신용]]", "박람회 한 번으로 사라지지 않는 주관사인지, 숫자로 확인하십시오.",
    cards([dict(lb="CAPITAL", big="2", unit="억원", nm="자본금", ds="하자 예치금·이행보증의 재원이 되는 실체."),
           dict(lb="CASH FLOW", big="A", nm="현금흐름 등급", ds="NICE 기업신용평가(2026.06.19)."),
           dict(lb="DEBT RATIO", big="17.1", unit="%", nm="부채비율", ds="안정적 재무구조로 선보상·예치금 운영."),
           dict(lb="CREDIT", big="BB-", nm="기업 신용등급", ds="공인 평가기관 기업신용평가 등급.")]),
    "현금흐름 A · 부채비율 17.1% — [[선보상과 예치금을 실제로 감당할 수 있는 재무]]입니다.")

std("02. 회사 소개", "인증과 [[제휴]]", "국제표준 인증 3종과 대기업 MOU로 운영 체계를 검증받았습니다.",
    split(grid([("iso_1", "ISO 45001 안전보건"), ("iso_2", "ISO 14001 환경"), ("iso_3", "ISO 9001 품질")], 3, contain=True),
          bullets([("ISO 9001 · 14001 · 45001", "품질·환경·안전보건 경영시스템 인증. 박람회 운영·시공 안전 관리에 적용합니다."),
                   ("삼성전자 MOU 체결", "가전·시스템에어컨 품목을 브랜드 공식 판매 채널로 연결합니다."),
                   ("LX하우시스 · 에몬스", "중문·인테리어 자재·가구 제휴 협의 중 — 확정 시 임예협에 공개합니다."),
                   ("전기공사업 등록", "조명·경관조명·실링팬을 면허 기반으로 직접 시공합니다.")]), "58% 1fr"),
    "인증서 사본은 [[원본 스캔]]으로 제출 · 요청 시 원본 대조가 가능합니다.")

std("02. 회사 소개", "동탄 전담 [[운영 조직]]", "본사 조직이 그대로 동탄 단지를 맡고, 전담 PM이 임예협 창구가 됩니다.",
    col('<div class="org"><div class="n1">대표이사 고진식<small>최종 책임 · 협약 체결</small></div><div class="ln"></div>'
        '<div class="n1">주관사업 총괄 본부장<small>동탄 파라곤 3차 총괄 · 임예협 창구</small></div><div class="ln"></div>'
        '<div class="teams">'
        '<div><b>영업팀</b><p>업체 모집·공개 입찰·심사</p></div>'
        '<div><b>행사관리팀</b><p>대관·동선·안전·인력</p></div>'
        '<div><b>이벤트팀</b><p>경품·키즈·편의시설</p></div>'
        '<div><b>대외지원팀</b><p>사전점검·행정·컨설팅</p></div>'
        '<div><b>콜센터·CS</b><p>A/S 접수·CRM·해피콜</p></div>'
        '<div><b>디자인·콘텐츠</b><p>카페·공지·영상 제작</p></div></div></div>',
        box("동탄 운영 원칙", tags(["전담 PM 1인 지정", "임예협 정기 보고", "입주 집중기 현장 베이스캠프", "외주·하도급 없음", "본사 직접 인력"],
                                  gold=["전담 PM 1인 지정", "외주·하도급 없음"])),
        grid([("meeting_1", "협의회·시공사 협의 미팅"), ("expo_2", "박람회 현장 운영"), ("basecamp_1", "현장 베이스캠프·CS")], 3)),
    "임예협은 [[한 명의 담당자]]에게만 연락하시면 됩니다.")

std("02. 회사 소개", "대표가 직접 운영하는 [[채널]]", "검색 한 번이면 엣지컴퍼니가 해 온 일이 모두 공개되어 있습니다.",
    split(grid([("youtube_1", "사전점검 현장 ‘아파트 언박싱’ 촬영"), ("youtube_2", "단지 정보 전달 영상")], 1, 2),
          bullets([("유튜브 채널 구독자 1.5만+", "대표가 직접 운영하며 박람회 현장과 결과를 공개합니다."),
                   ("사전점검 언박싱 영상", "사전점검 당일 단지를 촬영해 정보를 전달하고, 단지 홍보 효과를 만듭니다."),
                   ("공식 카페 · 알림톡 · 콜센터", "입주민과 끊기지 않는 채널을 회사가 직접 운영합니다."),
                   ("대표이사 고진식", "제조업 10년 근무 후 창업. 현장과 결과를 공개하는 것을 원칙으로 합니다.")]), "50% 1fr"),
    "말로 하는 약속이 아니라 [[기록으로 남는 약속]]입니다.")

# ============================================================ 03 주관 실적
divider("03", "기록이 [[증명]]합니다", ["최근 5년 1,000세대 이상 7건", "신도시 연속 주관", "현장·추천서·감사패"], "expo_1")
TOTAL = sum(r[3] for r in D.RECORDS)
std("03. 주관 실적", f"최근 5년 1,000세대 이상 [[{len(D.RECORDS)}건 · {TOTAL:,}세대]]",
    "공고일 기준 최근 5년 · NICE 기업신용평가보고서 ‘연혁’ 기재 내용과 같습니다(제출서류 8 · 별첨 1).",
    split(table(["No", "주관 시기", "단지명", "지역", "세대수"],
                [((str(i), "c"), (d, "c"), (nm, "k"), (reg, "c"), (f"{n:,}", "r")) for i, (d, nm, reg, n) in enumerate(D.RECORDS, 1)]
                + [("@sum", ("", "c"), ("합계", "c"), (f"{len(D.RECORDS)}건", ""), ("", ""), (f"{TOTAL:,}", "r"))],
                "", ["7%", "15%", None, "14%", "13%"]),
          col(cards([dict(lb="REQUIREMENT", big="5", unit="회 이상", nm="공고 참가자격 6-4"),
                     dict(lb="OURS", big=str(len(D.RECORDS)), unit="회", nm=f"합계 {TOTAL:,}세대", hl=True)], cols=1),
              box("임대 아파트 실적 구분", '<div class="ds" style="margin:0">1,000세대 이상 임대 아파트 실적은 없으며, 위 7건은 모두 일반 분양 아파트입니다(공고 6-4 별도 구분).</div>')),
          "62% 1fr"),
    "2018년 첫 단지 이후 누적 80개 단지 — [[대표자 이전 사업체 운영분 포함]] 기준입니다.")

std("03. 주관 실적", "전국에서 이어지는 [[주관 단지]]", "1,000세대 이상 대단지부터 신도시 연속 단지까지, 매년 신규 단지를 맡고 있습니다.",
    grid([(f"apt_{i}", None) for i in [1, 2, 3, 4, 7, 8, 11, 12, 13, 16, 17, 21]], 4, 3),
    "주관 단지 중 일부 — [[단지별 협약서·추천서]]는 요청 시 제출합니다.")

std("03. 주관 실적", "한 단지가 아니라 [[한 신도시]]를 맡습니다", "같은 신도시의 단지를 연속으로 맡는다는 것은, 앞 단지 입주민의 평가가 좋았다는 뜻입니다.",
    split(col(fig("sasong_1", "양산 사송신도시"), fig("ecodelta_1", "부산 강서 에코델타시티")),
          col(box("양산 사송신도시", tags(["데시앙 1차 1,712", "데시앙 3차 672", "LH 신혼희망타운 2차 479", "더샵 3차 533", "제일풍경채 452", "우미린 688"], gold=["데시앙 1차 1,712"])),
              box("부산 강서 에코델타시티", tags(["이편한세상 센터포인트", "강서자이 에코델타", "푸르지오", "대성베르힐 1,120", "대방 디에트르"], gold=["대성베르힐 1,120"])),
              box("동탄에 주는 의미", '<div class="ds" style="margin:0">신도시 단지는 협력업체·자재·A/S 동선이 겹칩니다. 동탄2에서도 [[첫 단지를 기준점]]으로 만들겠습니다.</div>')),
          "44% 1fr"),
    "신도시 전체를 연속으로 맡을 수 있는 [[운영 체력]]입니다.")

std("03. 주관 실적", "입주박람회 [[현장]]", "수천 세대가 몰리는 현장을 매년 운영합니다.",
    grid([("expo_1", "입주박람회 현장"), ("expo_2", "품목별 상담 부스"), ("expo_3", "주말 양일 운영"), ("expo_4", "입주민 집객")], 2, 2),
    "대형 행사장 운영 경험이 그대로 [[동탄 박람회 매뉴얼]]이 됩니다.")

std("03. 주관 실적", "행사관리는 ‘보여주기’보다 [[‘지켜주기’]]", "입주설명회·경품 추첨·키즈 프로그램까지 현장을 직접 운영합니다.",
    split(fig("event_ops", "입주민 박람회 · 설명회 · 경품 추첨 · 키즈 프로그램", contain=True),
          col(fig("snack", "현장 근로자 간식차 지원"), fig("lighting_event", "입주 기념 점등식 이벤트 지원")), "55% 1fr"),
    "행사가 끝나도 [[현장 지원은 계속]]됩니다.")

std("03. 주관 실적", "협의회가 [[직접 써 준]] 추천서와 감사패", "우리를 가장 잘 아는 것은 먼저 함께한 단지의 협의회입니다.",
    split(fig("letters", "주관 단지 협의회·파트너 추천서", contain=True), fig("awards_1", "본사에 보관 중인 감사패"), "55% 1fr"),
    "추천서·감사패 원본은 [[본사 방문 시 확인]] 가능합니다.")

std("03. 주관 실적", "더 나아가 [[나눔]]을 실천합니다", "지역사회 봉사단을 꾸준히 운영하고 있습니다.",
    fig("volunteer_grid", None, contain=True),
    "단지와 함께 [[지역에 남는 회사]]가 되겠습니다.")

# ============================================================ 04 박람회·공동구매 계획
divider("04", "박람회·공동구매 [[계획]]", ["추진 일정", "품목 구성 · 임대 맞춤 분류", "업체 선정 · 예상 참가 업체", "단가·계약 보호"], "expo_2")
std("04. 박람회·공동구매", "추진 [[일정]] (안)", "입주 2027.02.28에서 거꾸로 짰습니다. 설 연휴 전 박람회, 입주 후 1년 사후관리까지.",
    rows([("2026.10", "주관사 선정·협약 체결 · 임예협 카페/공지채널 지원 시작 · [[품목 수요조사]] 설문"),
          ("2026.11", "참여업체 [[공개 입찰공고]] (임예협·주관사 이메일 동시 접수) · 행사장 대관 · 타입별 실측 데이터 준비"),
          ("2026.12", "1·2차 업체 심사 → [[임예협 최종 컨펌]] · 업체 협약식 · 특약이행각서·하자보수 이행각서 징구"),
          ("2027.01", "단가표 사전 공개 · 사전점검 지원 · [[입주박람회 주말 양일]] (설 연휴 전) · 온라인 박람회 오픈"),
          ("2027.02~03", "입주 지원 · 현장 베이스캠프·콜센터 · 시공 일정 관리 · 2차 박람회 (임예협 협의 시)"),
          ("~2028.02", "입주 후 1년 사후관리 — A/S·하자 이행관리, 협약 종료 시 [[결과 보고서]] 제출")], 150),
    "세부 일정은 사전점검·입주지원센터 일정에 맞춰 [[임예협과 확정]]합니다.")

std("04. 박람회·공동구매", "공동구매 [[품목]]과 수요조사", "임예협 정회원 설문으로 품목을 정합니다. 많이 원하는 품목부터 단가를 깎습니다.",
    split(box("공동구매 가능 품목 (36종)", tags([
        "가전", "시스템에어컨", "브랜드가구", "디자인가구", "붙박이장", "커튼·블라인드", "전동커튼", "실링팬", "LED·조명", "입주청소", "줄눈", "탄성코트",
        "새집증후군", "피톤치드", "방충망", "단열필름", "중문", "인덕션", "음식물처리기", "벽걸이TV", "욕실 환기", "욕실케어", "선반·수납",
        "공간정리", "렌탈", "이사", "사전점검", "화재보험", "층간소음매트", "인테리어", "비데", "통신", "유리막코팅", "주방", "에어컨 이전", "진드기케어"],
        gold=["커튼·블라인드", "LED·조명", "실링팬", "렌탈", "입주청소", "가전"])),
        col(flow([("STEP 1", "설문", "카페·알림톡 정회원 설문"), ("STEP 2", "분석", "품목·타입별 수요"),
                  ("STEP 3", "공개", "결과를 임예협과 공유")]),
            box("수요조사로 얻는 것", bullets([("품목 확정", "수요 낮은 품목은 빼고, 높은 품목은 업체 수를 늘려 경쟁시킵니다."),
                                            ("단가 협상력", "예상 계약 세대 수를 업체에 제시해 단계별 할인율을 받아냅니다."),
                                            ("타입별 패키지", "82㎡·108㎡ 실측 기준 패키지를 사전 구성합니다.")]), "flex:1")), "50% 1fr"),
    "품목은 주관사가 아니라 [[임차인 수요]]가 정합니다.")

std("04. 박람회·공동구매", "임대 단지 맞춤 [[시공 허용 분류]] (안)", "임대사업자와 사전 협의해 박람회 전에 공개합니다. 퇴거 시 원상복구 분쟁을 막기 위해서입니다.",
    table(["분류", "품목 예시", "임차인 안내"], [
        (("허용", "g"), "가전 · 가구 · 렌탈 · 커튼·블라인드(무타공 우선) · 입주청소 · 새집증후군·피톤치드 · 이사 · 화재보험 · 수납", "원상복구 부담 없음 · 자유 계약"),
        (("조건부", "g"), "줄눈 · 탄성코트 · 실링팬 · 조명 교체 · 중문 · 방충망 · 단열필름 · 붙박이장 · 시스템에어컨", "임대사업자 승인 기준 안내 · 원상복구 조건 계약서 명시"),
        (("협의 필요", "g"), "벽체·바닥 마감 변경 · 인테리어 공사 · 구조물 타공", "개별 승인 후 진행 · 분양전환 확정 세대 위주"),
    ], "", ["12%", "52%", None]) + '<div class="note">※ 최종 분류는 임대사업자 협의 결과에 따라 확정하며, 분양전환 확정 세대와 거주형 세대 패키지를 나눠 안내합니다.</div>',
    "‘살 수 있는 것’보다 [[‘해도 되는 것’]]을 먼저 알려드립니다.")

std("04. 박람회·공동구매", "업체 선정 [[4단계]] 공개 심사", "주관사 단독 결정이 아닙니다. 임예협이 마지막에 컨펌합니다.",
    rows([("자율경쟁 입찰공고", "임예협 카페·협력업체 밴드·홈페이지 공개 모집. 입찰서류는 [[주관사와 임예협 양쪽 이메일]]로 동시 접수."),
          ("1차 서류심사", "사업개시 2년 경과 · 근거리(동탄·화성) 업체 · 타 단지 공동구매 20회 이상 · 국세·지방세 완납 · 사후관리 체계."),
          ("2차 세부심사", "다세대 시공 물량 소화 능력 · A/S 대책 증명 · 타 단지 입주민 평가 · 단계별 할인율. 대기업·브랜드·본사직영 우선."),
          ("임예협 최종 컨펌", "후보 업체 서류를 임예협이 최종 검토해 [[승인으로 확정]]. 물품공급계약서·청렴이행서약서·하자보수 이행각서 징구.")], 200),
    "입찰 과정 전체를 임예협과 [[공유]]합니다.")

std("04. 박람회·공동구매", "[[지역업체 90%]] · 하도급 없음", "A/S는 거리가 결정합니다. 동탄 단지의 A/S는 동탄 가까운 업체가 맡아야 합니다.",
    cards([dict(lb="LOCAL", big="90", unit="%", nm="동탄·화성·오산 지역업체", ds="타 지역 업체는 48시간 내 A/S가 현실적으로 어렵습니다."),
           dict(lb="CHECK", big="검증", nm="사업자·재무·완납·예치", ds="사업자등록증·재무제표·완납증명서 통과 업체만 입점."),
           dict(lb="NO SUB", big="하청 X", nm="하도급·연동 계약 금지", ds="선정 업체의 하청과 타 주관사 연동 계약을 계약으로 금지(공고 9-9)."),
           dict(lb="EDUCATION", big="교육", nm="참여업체 사전 교육", ds="고객 응대·서비스·현장 규칙 교육 후 박람회 입점.", hl=True)]),
    "주관사도 [[일괄 도급하지 않습니다]] — 별지 #4 서약 그대로 이행합니다.")


def vendor_rows():
    groups = {}
    for g, *_ in D.VENDORS:
        groups[g] = groups.get(g, 0) + 1
    seen, out = set(), []
    for g, item, who, note in D.VENDORS:
        gcell = "" if g in seen else f'<td class="g" rowspan="{groups[g]}">{g}</td>'
        seen.add(g)
        out.append(f'<tr>{gcell}<td class="k">{html.escape(item)}</td><td>{html.escape(who)}</td><td>{html.escape(note)}</td></tr>')
    return "".join(out)


std("04. 박람회·공동구매", "품목별 [[예상 참가 업체]]", "확정은 임예협 공개 입찰·심사 후 — 시공 품목은 동탄·화성 지역업체가 우선입니다.",
    '<table class="tbl sm"><thead><tr><th style="width:12%">구분</th><th style="width:30%">품목</th><th style="width:30%">예상 참가 업체</th><th>비고</th></tr></thead>'
    f"<tbody>{vendor_rows()}</tbody></table>",
    ("주관사 직영 품목도 [[같은 심사 · 같은 단가 공개 · 같은 최저가 보장]].", "하도급·타 주관사 연동 계약 없음"))

std("04. 박람회·공동구매", "단가를 지키는 [[최저가 보장]]과 추가할인", "공고문이 우려한 ‘행사비 때문에 오르는 단가’를 구조로 막습니다.",
    split(col(cards([dict(lb="공동구매가", big="33", unit="만원"), dict(lb="동일제품 오프라인", big="26", unit="만원"),
                     dict(lb="차액 7만원 × 10배", big="70", unit="만원", hl=True)]),
              box("최저가 보장제", '<div class="ds" style="margin:0">동일 브랜드·동일 제품이 더 싸게 확인되면 [[차액의 10배 보상]] + 판매가 재조정. (온라인 판매 상품·시공 품목 제외)</div>')),
          col(cards([dict(lb="50세대", big="1", unit="%"), dict(lb="100세대", big="2", unit="%"), dict(lb="150세대", big="3", unit="%", hl=True)]),
              box("실적 비례 추가할인", '<div class="ds" style="margin:0">업체 기대매출을 넘으면 [[잔금에서 추가할인]]. 예) 100만원 품목 100세대 계약 시 세대별 2만원 할인 → 98만원 결제.</div>')), "1fr 1fr"),
    "박람회장 가격 = [[사전 공개 단가]] — 현장에서 가격이 바뀌지 않습니다.")

std("04. 박람회·공동구매", "계약·환불은 [[임차인 중심]]으로", "업체가 선수금을 많이 받지 못하게 계약으로 막습니다. 세부 기준은 제출서류 9) 규정과 같습니다.",
    split(cards([dict(lb="01", big="5", unit="%", nm="계약금 상한", ds="계약금은 총액의 5% 이하."),
                 dict(lb="02", big="후불", nm="잔금은 시공·설치 확인 후", ds="추가할인은 잔금에서 차감."),
                 dict(lb="03", big="100", unit="%", nm="제작·시공 전 해약", ds="납부 금액 전액 환불."),
                 dict(lb="04", big="동일", nm="현금·카드 동일가", ds="현금영수증 발행.")], cols=2, rows_n=2),
          table(["취소 기한(시공일 기준)", "품목"], [
              (("7일 전", "k"), D.CANCEL_7), (("15일 전", "k"), D.CANCEL_15),
              (("출고 지시 전", "k"), "브랜드 가전·가구 (미제작 시 100%)"), (("당일", "k"), "사전 해피콜 미이행 시 모든 품목"),
              (("환불 기한", "k"), "취소 확정일로부터 3영업일 이내")], "sm", ["30%", None]), "44% 1fr"),
    "불이행 업체는 주관사 콜센터 접수 → [[주관사 선보상 + 업체 패널티]].")

# ============================================================ 05 입주박람회 운영
divider("05", "입주박람회 [[운영]]", ["장소·일정", "안전·인력·보험", "편의시설·이벤트", "온라인 박람회·라이브"], "expo_3")
std("05. 입주박람회 운영", "장소와 [[일정]]", "가깝고 넓은 장소를, 사전점검 전후에 맞춰 대관합니다.",
    split(cards([dict(lb="DISTANCE", big="30", unit="분 이내", nm="단지에서 이동 30분 이내"),
                 dict(lb="SPACE", big="1,200", unit="평급", nm="대형 전시홀"),
                 dict(lb="WHEN", big="1~2", unit="달 전", nm="입주일 기준 · 설 연휴 전"),
                 dict(lb="VENUE", big="컨벤션", nm="컨벤션센터 · 체육관", hl=True)], cols=2, rows_n=2),
          fig("expo_4", "주말 양일 운영 — 집객 동선 설계"), "50% 1fr"),
    "후보 장소 2~3곳을 [[임예협과 현장 답사]] 후 확정합니다.")

std("05. 입주박람회 운영", "안전·인력·[[보험]]", "수천 명이 모이는 행사입니다. 사고 대비부터 설계합니다.",
    split(rows([("행사 배상책임보험", "안전사고·화재·상해 보상을 위한 영업배상 책임보험 가입 (공고 6-9 증명서 발행 가능)."),
                ("운영 인력", "주차 안내 5 · 임예협 도우미 3 · 카페테리아 3 · 보안 2 · 어린이 편의 4 · 구급요원 1."),
                ("구급 대비", "행사 기간 구급요원 상주, 구급차 대기 체계."),
                ("대형 접수부스", "체크인·정회원 확인·상품권 교부를 한곳에서 — 대기열 분산.")], 170),
          fig("expo_4", "수천 명 집객 — 동선·대기열 관리"), "56% 1fr"),
    "안전 계획서는 박람회 [[2주 전 임예협에 제출]]합니다.")

std("05. 입주박람회 운영", "편안한 [[행사 환경]]", "온 가족의 나들이가 될 수 있도록 편의시설을 갖춥니다.",
    split(fig("facility", None, contain=True),
          bullets([("아이와 함께", "에어바운스 · 키즈 매직쇼 · 페이스페인팅 · 캐리커처."),
                   ("쉬어 가는 공간", "카페테리아 · 휴게실 · 수유실 · 안마의자."),
                   ("이동 편의", "유모차 대여 · 주차 안내 · 셔틀 운영 검토."),
                   ("임예협 부스", "행사장 중앙 배치 — 정회원 가입·안내 지원.")]), "60% 1fr"),
    "편의시설은 행사 일정과 장소에 맞춰 [[임예협과 확정]]합니다.")

std("05. 입주박람회 운영", "이벤트 · 경품 · [[사은품]]", "계약을 재촉하지 않아도 오고 싶은 박람회를 만듭니다.",
    split(fig("promo", "카페·박람회 이벤트 운영 사례", contain=True),
          col(grid([("stopper_1", "전 방문 세대 말발굽(현관 스토퍼)"), ("stopper_2", None)], 2),
              bullets([("경품 이벤트", "대형가전부터 소형가전까지 + 참여업체 경품 200여 개."),
                       ("계약 사은품", "품목 계약 시 업체별 사은품(업체 상황에 따라 변경)."),
                       ("카페 이벤트", "댓글·삼행시·아파트 자랑 이벤트로 정회원 가입을 돕습니다.")])), "52% 1fr"),
    "[[방문만 해도 받는 혜택]] 중심으로 구성합니다.")

std("05. 입주박람회 운영", "못 오셔도 괜찮은 [[온라인 박람회]]", "현장과 같은 공동구매가를 온라인 폐쇄몰과 라이브로 그대로 옮깁니다.",
    split(grid([("expo_3", "박람회 현장 = 온라인 동일가"), ("live_1", "현장 라이브 커머스 · 영상 제작")], 1, 2),
          bullets([("온라인 박람회 (폐쇄몰)", "해당 단지 입주민만 입장. 오프라인 박람회와 [[동일 공동구매가]]."),
                   ("카페 링크 게시", "임예협 카페에 쇼핑몰 링크를 게시하거나 개별 링크로 전달."),
                   ("라이브 커머스", "행사장 라이브 방송으로 현장 분위기와 설명을 그대로 전달."),
                   ("맞벌이·원거리 세대", "박람회 날 일정이 안 맞아도 같은 조건으로 계약할 수 있습니다.")]), "48% 1fr"),
    "“박람회 날 못 가서”가 [[손해가 되지 않게]] 합니다.")

# ============================================================ 06 A/S·하자보증
divider("06", "A/S·하자는 [[증권과 계약]]으로", ["하자 예치금 현금 1억", "이행보증보험 2년 10억", "특약이행각서 9개 항", "패널티 3단계"], "basecamp_1")
std("06. A/S·하자보증", "임차인을 지키는 [[4중 안전망]]", "한 가지라도 빠지면 피해는 입주민에게 갑니다. 네 겹으로 막습니다.",
    cards([dict(lb="01", big="1", unit="억", nm="하자 예치금 현금", ds="주관사 순수 자산 · 임예협+주관사 공동통장 · 즉시 집행."),
           dict(lb="02", big="10", unit="억", nm="이행보증보험 2년", ds="제안 미이행·업체 하청·검증 미비·도산에 대한 주관사 책임."),
           dict(lb="03", big="48", unit="시간", nm="하자 처리 원칙", ds="24시간 회신, 48시간 처리. 미해결 시 하자지연 패널티."),
           dict(lb="04", big="2~10", unit="년", nm="사후관리", ds="최소 2년 무상 A/S, 최대 10년 장기 관리(품목별 상이).", hl=True)]),
    "안전망은 [[협약식 때 증권·통장 사본]]으로 제출합니다.")

std("06. A/S·하자보증", "업체를 믿는 게 아니라 [[업체를 묶어둡니다]]", "박람회 참여 모든 업체는 하자보수 이행각서와 특약이행각서를 씁니다.",
    table(["No", "입주박람회 특약이행각서 (참여업체 필수)"], [
        (("1", "c"), "현금가·카드가 동일 적용 — 위반 시 즉시 자격박탈 및 계약금 반환"),
        (("2", "c"), "주관사 승인 없는 별도 박람회 참여 시 자격박탈"),
        (("3", "c"), "동일 품목 가격차 5~10% 이상 시 동일가 재조정 및 [[차액 10배 보상]]"),
        (("4", "c"), "타 업체 비방 적발 시 홍보정지, 재발 시 공동구매 자격박탈"),
        (("5", "c"), "공동구매 규정에 따른 하자보수 기간 성실 이행"),
        (("6", "c"), "과대홍보·비정품·벌크 판매 적발 시 자격박탈·계약 회수·위약금 배상"),
        (("7", "c"), "화재·상해 예방을 위한 임예협·주관사 이행사항 비준수 시 자격박탈"),
        (("8", "c"), "입주 종료까지 주관사 공지 불이행·불참 시 자격박탈"),
        (("9", "c"), "업체 도산 시 [[동종업체가 사후관리 의무 승계]]"),
    ], "sm", ["7%", None]),
    "입주민과 업체가 싸우지 않게 — [[주관사가 사이에 섭니다.]]")

std("06. A/S·하자보증", "업체 도산·회피 시 [[주관사가 먼저]]", "별지 #3 A/S 이행각서 그대로 — 업체가 못 하면 주관사가 우선 변상합니다.",
    col(flow([("1", "클레임 발생", "입주민 → 업체 접수"), ("2", "업체 회피·지연", "처리 지연 발생"), ("3", "주관사 접수", "콜센터·카페 신문고"),
              ("4", "선보상", "확인 후 피해금액 먼저 보상"), ("5", "업체 정산", "계약 조항에 따라 주관사-업체 해결")]),
        cards([dict(lb="BANKRUPT", nm="업체 도산 시", ds="동종업체로 하자보수 이관, [[A/S 비용 주관사 100% 지급]]."),
               dict(lb="DEPOSIT", nm="예치금 즉시 집행", ds="법무법인 송달 대기 없이 공동통장에서 바로 집행."),
               dict(lb="RECORD", nm="처리 기록 공개", ds="선보상·정산 내역을 임예협에 공유.")])),
    "입주민이 [[업체를 쫓아다니지 않아도]] 되는 구조입니다.")

std("06. A/S·하자보증", "실제 클레임 데이터로 [[예방]]합니다", "입주 시점 주요 클레임 품목을 분석해 품목별 보상 규정을 미리 정했습니다.",
    table(["품목", "주요 클레임", "건수", "보상 규정"], [
        (("청소", "k"), "시공지연 · 시공불량 · 예약누락 · 투입인원 · A/S 지연", ("26건", "c"), "당일 해결 원칙, 최대 다음날까지 보수 · 미해결 시 하자지연금"),
        (("이사", "k"), "포장불량 · 물건파손 · 견적오류 · 예약불가", ("19건", "c"), "입주민과 확인 안 된 파손·오염 전부 수리 (수리 불가 시 보험 보상)"),
        (("줄눈", "k"), "시공지연 · A/S 지연 · 하자 사전고지 미준수 · 타일 파손", ("14건", "c"), "시공 전 확인 안 된 타일 파손·오시공·오염 배상 및 재시공"),
        (("중문", "k"), "시공지연 · 계약상이 · 자재누락 · 바닥/벽지 파손", ("10건", "c"), "계약과 다른 제품은 재시공 · 협의해 다음날까지 재보수"),
        (("인테리어", "k"), "계약상이 · 취소/환불 · A/S 지연", ("8건", "c"), "계약이행증권·하자보증증권·예치금을 담보로 주관사 진행"),
        (("기타", "k"), "불친절 · 취소/환불 · 주문제작 · 제품상이", ("7건", "c"), "접수 즉시 피드백 및 일정 조율"),
    ], "sm", ["10%", "36%", "8%", None]),
    "임대 단지에는 [[원상복구 관련 클레임]]을 추가 관리 항목으로 둡니다.")

std("06. A/S·하자보증", "참여업체 [[패널티 3단계]]", "하자보수 미이행·규정 위반 업체는 단계별로 제재합니다.",
    cards([dict(lb="STEP 1", big="정지", nm="홍보정지", ds="과대광고·허위·규정 위반 적발 시 일정 기간 홍보정지, 개선 후 재개."),
           dict(lb="STEP 2", big="10", unit="%", nm="총액 10% 배상", ds="A/S 전담 운영 미비로 인한 피해는 지연배상제 적용."),
           dict(lb="STEP 3", big="박탈", nm="자격박탈·전 계약 이관", ds="누적 클레임 2회 이상·지시 불이행 시 임예협 승인 후 대체 업체로 전 계약 이관.", hl=True)]),
    "패널티 결정은 [[임예협 승인]]을 거칩니다.")

# ============================================================ 07 콜센터·사후관리
divider("07", "입주 후에도 [[끊기지 않습니다]]", ["접수 채널 4종 · 365일", "24시간 회신 · 48시간 처리", "CRM · 베이스캠프", "임대 단지 하자 창구 분리"], "basecamp_2")
std("07. 콜센터·사후관리", "주관 [[콜센터]] 프로세스", "입주민은 업체가 아니라 주관사에 연락하면 됩니다.",
    col(flow([("01", "접수", "콜센터·카페 신문고·카카오채널·홈페이지 (365일)"), ("02", "24시간 회신", "하자 범위 확인 · 업체 이관"),
              ("03", "48시간 처리", "주관사 관리·감독하에 보수"), ("04", "검수·해피콜", "보수 완료 후 주관사가 직접 확인")]),
        cards([dict(lb="CHANNEL", big="4", unit="종", nm="접수 채널", ds="상담 콜센터 · 공식카페 신문고 · 카카오채널 · 홈페이지."),
               dict(lb="FEEDBACK", big="24", unit="시간", nm="회신 원칙", ds="업체 미응답 시 주관사가 직접 개입."),
               dict(lb="FIX", big="48", unit="시간", nm="처리 원칙", ds="지연·파손 범위에 따라 보상 처리.", hl=True)])),
    "처리 현황은 [[임예협에 정기 공유]]합니다.")

std("07. 콜센터·사후관리", "CRM으로 [[끝까지]] 관리합니다", "접수된 모든 건을 기록해, 누가 받아도 같은 답을 드립니다.",
    rows([("입주민 클레임 발생", "콜센터·홈페이지·카카오채널·카페 신문고로 접수. 박람회 일정·혜택·불편 접수처는 문자 알림으로 사전 안내."),
          ("주관사 접수·정리", "불편 사항을 경청하고 내부 정리 — 입주민의 불안부터 줄입니다."),
          ("CRM 등록", "클레임·입주민·업체 정보를 등록해 2차 접수 시에도 즉시 파악."),
          ("업체 공유·24시간 해결안", "업체 확인 후 24시간 내 해결 방안 제시 요청."),
          ("입주민 보고·재개입", "24시간 내 업체 피드백·이행이 없으면 주관사가 재개입 후 패널티."),
          ("종결 확인", "해결 여부를 입주민과 재확인 후 종결.")], 190),
    "업체별 계약 건수·시공 일정도 [[CRM으로 함께 관리]]합니다.")

std("07. 콜센터·사후관리", "48시간은 [[거리]]가 만듭니다 — 현장 베이스캠프", "입주 집중 기간에는 단지 가까이에 상주 거점을 둡니다.",
    split(grid([("basecamp_1", "베이스캠프 사무 공간"), ("basecamp_2", "상담·대기 공간")], 1, 2),
          bullets([("입주 집중 기간 상주", "에코델타 이편한세상·강서자이 입주 시 인근 오피스텔에 45일간 베이스캠프 운영."),
                   ("동탄 적용", "입주(2027.02.28) 전후 집중 기간에 [[동탄 현장 베이스캠프]] 운영 — 기간은 임예협과 협의."),
                   ("현장 접수·즉시 배정", "하자 접수 즉시 지역 업체 배정, 이동시간을 줄입니다."),
                   ("입주 지원 겸용", "입주 안내·서류·시공 일정 상담 창구로 함께 운영합니다.")]), "46% 1fr"),
    "“오늘 접수, 내일 해결”이 가능한 [[물리적 조건]]을 먼저 만듭니다.")

std("07. 콜센터·사후관리", "임대 단지는 [[하자 창구]]를 나눠야 합니다", "공동구매 시공 하자와 건물 하자가 섞이면 임차인만 이리저리 돌게 됩니다.",
    split(col(box("공동구매 시공 하자 → 주관사가 처리", bullets([("접수", "주관사 콜센터 단일 창구."), ("처리", "업체 48시간 처리 · 미이행 시 선보상.")])),
              box("건물 하자 → 임예협을 통해 임대사업자에 일괄 전달", bullets([("접수 대행", "주관사가 접수·사진·위치를 정리."),
                                                                             ("일괄 전달", "임예협 명의로 임대사업자에 묶어서 전달 — 처리 현황 추적.")]))),
          col(box("세대별 시공 이력 카드", bullets([("기록", "시공 품목·자재·사진·보증기간을 세대별로 기록해 드립니다."),
                                               ("활용", "A/S 때 바로 확인, 분양전환·퇴거 때 [[원상복구 증빙]]이 됩니다.")]), "flex:1"),
              box("10년 거주에 맞춘 장기 관리", '<div class="ds" style="margin:0">최소 2년 무상 A/S, 최대 10년 장기 사후관리(품목별 상이) — 임대 기간과 같은 호흡으로 관리합니다.</div>')),
          "1fr 1fr"),
    "임차인은 [[한 번만 접수]]하면 됩니다.")

# ============================================================ 08 임예협 업무 지원
divider("08", "임예협의 일을 [[주관사가 함께]]", [f"세대당 15만원 발전지원금", "카페·홍보 콘텐츠", "사전점검 지원·품질 검증", "행정 지원·단지 컨설팅"], "meeting_1")
std("08. 임예협 지원", "세대당 [[15만원]] 발전지원금", "박람회 참가비가 아니라 단지로 돌아가는 금액입니다(부가세 포함).",
    split(cards([dict(lb="PER HOUSEHOLD", big="15", unit="만원", nm="세대당 발전지원금"),
                 dict(lb=f"{HH:,} 세대 기준", big=FUND_S, nm="발전지원 규모", hl=True)], cols=1),
          rows([("단지 시설 투자", "커뮤니티 시설·경관조명·공용부 개선 등 [[입주 후에도 남는 곳]]에 우선 집행."),
                ("임예협 활동 지원", "임예협 운영·총회·회의 등 활동 지원."),
                ("입주민 직접 혜택", "상품권·사은품·무상 시공 등 세대에 직접 돌아가는 혜택."),
                ("집행 내역 공개", "항목·금액·시점을 임예협과 사전 협의하고 집행 후 내역 공개.")], 170), "34% 1fr"),
    ("구체 배분은 [[임예협 협의 후 단지 맞춤]]으로 확정합니다.", "공동구매 단가에 전가되지 않도록 단가표 사전 공개와 함께 운영"))

std("08. 임예협 지원", "카페·공지채널 [[홍보 콘텐츠]] 지원", "공고 4-7 — 임예협 카페와 공지채널을 주관사가 함께 키웁니다.",
    split(cards([dict(lb="ONLINE 01", nm="공식카페 디자인 지원", ds="홈페이지형 카페 디자인으로 단지 정체성을 높입니다."),
                 dict(lb="ONLINE 02", nm="카페 콘텐츠 활성화", ds="품목 안내 카드뉴스·이벤트·공지 콘텐츠를 주관사가 제작."),
                 dict(lb="ONLINE 03", nm="네이버 노출·언론 보도", ds="검색 상위 노출 마케팅, 기획 보도로 단지 인지도 상승."),
                 dict(lb="OFFLINE", nm="현수막·전단·버스 광고", ds="카페 가입 유도 현수막, 박람회 홍보 전단, 생활 밀착 매체 노출.", hl=True)], cols=2, rows_n=2),
          fig("promo", "카페 이벤트·홍보 콘텐츠 제작 사례", contain=True), "56% 1fr"),
    "정회원이 늘수록 [[임예협의 협상력]]이 커집니다.")

std("08. 임예협 지원", "사전점검 [[당일 지원]]", "공고 4-4 — 사전점검 행사를 임예협이 혼자 준비하지 않도록 돕습니다.",
    split(cards([dict(lb="01", nm="행사 물품·도우미", ds="현수막·X배너·서면 자료, 임예협 도우미 인력 지원."),
                 dict(lb="02", nm="라돈측정기 10대 렌탈", ds="내 집 라돈을 직접 측정할 수 있게 지원."),
                 dict(lb="03", nm="냉·난방용품 · 커피차", ds="계절에 맞춘 부스 용품, 행사 당일 커피차."),
                 dict(lb="04", nm="공용·조경 하자진단 보고서", ds="사전점검 당일 공용부·조경 하자진단 보고서 제공.", hl=True)], cols=2, rows_n=2),
          table(["사전점검 대행", "구성", "할인"], [
              (("BASIC", "k"), "2명 · 정비·육안점검·장비보고서", ("50%", "c")),
              (("STANDARD", "k"), "3명 · + 건축전문가·하자사진", ("35%", "c")),
              (("PREMIUM", "k"), "3명(1차)+2명(2차) · 입주 후 점검 1회", ("35%", "c"))], "sm", ["24%", None, "14%"])
          + '<div class="note">이벤트 당첨 세대 사전점검 동행 무상 · 건설면허 특급기술 인력 지원</div>', "52% 1fr"),
    "사전점검 TIP·체크리스트·셀프체크 영상을 [[사전에 배포]]합니다.")

std("08. 임예협 지원", "입주 전 [[품질 검증]] 지원", "공고 4-6 — 전문 인력과 장비로 공용부를 검증해 임예협의 협의 자료를 만듭니다.",
    grid([("rebar_1", "공용부 철근 탐지 · 오시공 점검"), ("rebar_2", "콘크리트 강도 측정"), ("safety_1", "건설현장 안전점검"),
          ("drone_1", "열화상 드론 촬영"), ("thermal_1", "균열·누수·단열 분석"), ("sun_2", "일조량 시뮬레이션")], 3, 2),
    "검증 결과는 [[임대사업자·시공사 협의 자료]]로 정리해 드립니다.")

std("08. 임예협 지원", "공용부 [[위생·안전]] 지원", "다중이용 공간부터 깨끗하게 시작합니다.",
    grid([("cesco_2", "세스코 특수해충 점검 (동별 대표세대)"), ("sickhouse_1", "공용부 새집증후군 관리"), ("sickhouse_2", "항균·탈취 장비"),
          ("radon_2", "라돈 측정 (동별 대표세대)"), ("sickhouse_3", "공용부 항균 나노코팅"), ("mite_1", "생활 위생 케어")], 3, 2),
    "측정·점검 결과가 기준을 넘으면 [[증빙 자료를 만들어 협의를 지원]]합니다.")

std("08. 임예협 지원", "도면 검토 · [[조경]] 개선안", "보기 좋은 제안이 아니라 협의에서 실제로 쓰이는 자료를 만듭니다.",
    split(fig("drawing_1", "착공·조경 설계 도면 분석", contain=True),
          col(grid([("landscape_1", "커뮤니티 광장 개선안"), ("landscape_2", "체육·휴게 공간 개선안")], 2),
              bullets([("착공 도면 분석", "특급기술자가 하자·오적출 분석보고서를 제공합니다."),
                       ("조경 감리 관점 검토", "임차예정자 대상 설명회를 무료로 진행합니다."),
                       ("개선안 비교", "광장·키즈·휴게 공간 개선안을 도면으로 비교 제시합니다.")])), "44% 1fr"),
    "조경·하자 [[개선안 분석]]까지 한 번에 지원합니다.")

std("08. 임예협 지원", "임예협 [[행정 지원]]", "임예협 실무 부담을 실제로 덜어드립니다.",
    split(col(grid([("protest_1", "집회 현장 컨설팅"), ("meeting_1", "협의 미팅 엔지니어 동석")], 2), "<div style='height:2px'></div>"),
          rows([("온라인 위임장·동의서", "가입·앱 설치 없이 카카오톡·이메일 전자서명. 서명 이미지·일시까지 저장."),
                ("민원 업무 지원", "국민신문고 등 민원 양식과 접수 프로세스를 단지 상황에 맞게 지원."),
                ("집회·현장 컨설팅", "의견이 긍정적으로 반영되도록 피켓·현수막·동선 컨설팅."),
                ("협의 미팅 동석", "임대사업자·시공사 협의 자리에 전문 엔지니어가 함께 갑니다."),
                ("총회·회의 지원", "장소 대관·현수막·도우미 지원 · 주차스티커 시안 지원.")], 160), "44% 1fr"),
    "임예협이 직접 하실 일을 [[주관사가 대신]] 합니다.")

std("08. 임예협 지원", "단지 [[업그레이드]] 컨설팅", "입주 후 오래 쓰는 공간의 가치를 높이는 방안을 제안합니다.",
    grid([("gate_1", "문주·경관조명 컨설팅"), ("fitness_2", "피트니스센터 컨설팅"), ("fitness_4", "골프·GX 시설"),
          ("kids_1", "키즈 커뮤니티 확충"), ("ev_2", "전기차 충전기 설치 컨설팅"), ("meal_1", "커뮤니티 조식 서비스")], 3, 2),
    "입주 초기 [[관리비 절감·단지 수익금 운영]] 컨설팅도 함께 지원합니다.")

# ============================================================ 09 입주민 혜택
divider("09", "입주민에게 [[직접]] 돌아가는 혜택", ["박람회 상품권 1+1", "정회원 전용 혜택", "사전점검 대행 할인", "실측·샘플하우스·VR"], "interior_1")
std("09. 입주민 혜택", "박람회 [[혜택]]", "방문만 해도 받습니다. 계약을 강요하지 않습니다.",
    col(cards([dict(lb="GIFT 01", big="30", unit="만원", nm="계약금 사용 상품권", ds="일반회원 20만원 + 정회원 10만원 추가. 품목(업체)당 1매."),
               dict(lb="GIFT 02", big="5", unit="만원", nm="특정 입주민 추가 지원", ds="장애인 · 다자녀(3자녀↑) · 노부모 부양 · 다문화 · 소년·소녀가장 세대."),
               dict(lb="GIFT 03", big="백화점", nm="백화점 상품권", ds="방문·신청 시 1세대 1회 교부(금액 협의)."),
               dict(lb="GIFT 04", big="10", unit="%", nm="현장 특별할인", ds="박람회 기간 품목별 최대 10% 추가할인.", hl=True)], cols=4),
        grid([("giftcard_1", "박람회 상품권"), ("stopper_1", "전 방문 세대 말발굽"), ("expo_2", "박람회 현장 상담")], 3)),
    "[[방문(체크인)만 해도 받는 혜택]] 중심입니다.")

BENEFITS = [("doorlock_1", "도어락 나노코팅", "생활방수 코팅으로 오염·물때 방지", ""),
            ("fan_room_1", "실링팬 특가", "아크로 실링팬 정회원 특가", "조건부"),
            ("well_light_1", "우물 간접조명", "거실 우물천장 간접조명 지원", "조건부"),
            ("gallery_light_1", "갤러리조명 2구", "복도 매입등 2구 시공", "조건부"),
            ("phyton_1", "피톤치드 항균", "편백 추출물 항균 서비스 무상", ""),
            ("interior_1", "인테리어 30% 할인", "분야별 전문가 프로모션", "협의"),
            ("screen_1", "미세촘촘망 거실창", "기능성 방충망 거실창 시공", "조건부"),
            ("mite_1", "진드기 홈케어", "85℃ 열 살균, 약품 미사용", ""),
            ("bath_1", "욕실케어 1회", "곰팡이·물때 전문 장비 제거", ""),
            ("grout_1", "현관 줄눈", "현관 줄눈 무상 시공", "조건부"),
            ("door_1", "프리미엄 중문 특가", "방음·외풍 차단 중문", "조건부"),
            ("hugent_1", "욕실 환기가전", "환기·제습·온풍 휴젠뜨", "조건부")]


def benefit_page(items, first):
    cards_ = []
    for img, nm, ds, flag in items:
        badge = {"조건부": " · [[임대사업자 승인 품목]]", "협의": " · [[개별 승인 후 진행]]"}.get(flag, "")
        cards_.append(dict(img=img, nm=nm, ds=ds + badge))
    std("09. 입주민 혜택", "정회원 전용 [[세대당 60만원 상당]] 혜택" + (" (1)" if first else " (2)"),
        "공동구매가에 더해지는 정회원 전용 혜택입니다. 품목은 단지 협의 후 확정합니다.",
        cards(cards_, cols=3, rows_n=2),
        ("임대 단지는 시공형 혜택에 [[승인 여부]]를 함께 안내합니다.", "화재보험 2년 · 사전점검 할인 · 경품 응모 포함 14종"))


benefit_page(BENEFITS[:6], True)
benefit_page(BENEFITS[6:], False)

std("09. 입주민 혜택", "선택의 확신을 주는 [[실측·샘플하우스]]", "보고, 재고, 미리 배치해 본 뒤 결정하시게 합니다.",
    grid([("sample_1", "타입별 실측 사이즈 제공"), ("sample_2", "샘플하우스 운영"), ("vr_1", "단지 주변 항공 VR 촬영"),
          ("style3d_1", "전문가 3D 홈스타일링")], 2, 2),
    ("82㎡·108㎡ [[두 타입 실측 데이터]]로 커튼·가구 사이즈 고민을 줄입니다.", "실측은 임예협·현장 협조 시 진행"))

# ============================================================ 10 동탄 특화
divider("10", "동탄 파라곤 3차 [[특화 제안]]", ["임대 맞춤 5가지", "조명·경관조명 특화", "실링팬·스마트 조명", "약속 8가지"], "led_3")
std("10. 동탄 특화", "임대 단지라서 [[달라야 하는 것]]", "10년을 살 집, 언젠가 내 집이 될 수도 있는 집 — 두 경우를 모두 설계했습니다.",
    rows([("시공 허용 품목 가이드", "임대사업자와 사전 협의해 품목을 [[허용·조건부·협의]] 3단계로 나눠 박람회 전에 공개합니다."),
          ("두 갈래 패키지", "분양전환 확정 세대는 ‘내 집’ 기준(중문·줄눈·시스템에어컨), 거주형 세대는 [[무타공·이동식·렌탈]] 중심."),
          ("세대별 시공 이력 카드", "시공 품목·자재·사진·보증기간 기록 — A/S·분양전환·퇴거 때 [[증빙]]이 됩니다."),
          ("하자 창구 분리 접수", "공동구매 하자는 주관사, 건물 하자는 [[임예협을 통해 임대사업자에 일괄 전달]]."),
          ("타입 2개 규격화", "82·108㎡ 실측 데이터로 커튼·블라인드·조명을 미리 제작해 입주일에 바로 설치.")], 210),
    "임차인의 시공은 ‘얼마나 싸게’보다 [[‘나갈 때 문제없나’]]가 먼저입니다.")


def p_lighting(no):
    steps = [(SVG + "경관조명_1_설계.svg", "STEP 01", "설계", "조도·색온도·배광을 단지 동선과 외관에 맞춰 설계, [[도면으로 제안]]."),
             (SVG + "경관조명_2_생산.svg", "STEP 02", "생산", "직수입·자체 생산 라인에서 사양 그대로 제작. [[KC 인증 제품]]만 납품."),
             (SVG + "경관조명_3_시공.svg", "STEP 03", "직접시공", "전기공사업 등록업체가 [[외주 없이 직접 시공]], A/S까지 책임.")]
    cs = "".join(f'<div class="card img"><img src="{a}" alt="" style="background:#0D1E33"><div class="tx"><div class="lb">{b}</div>'
                 f'<div class="nm">{c}</div><div class="ds">{t(d)}</div></div></div>' for a, b, c, d in steps)
    body = f'<div class="cards" style="grid-template-columns:repeat(3,1fr)">{cs}</div>'
    return render(no, "10. 동탄 특화", "[[경관조명]] 컨설팅 · 설계 · 생산 · 시공", "단지의 밤 얼굴이 곧 단지 가치입니다. 조명은 엣지컴퍼니의 본업입니다.",
                          body, "임예협 요청 시 [[단지 경관조명·커뮤니티 조도 개선 제안서]]를 무상 제출합니다.")


add(p_lighting)

std("10. 동탄 특화", "실링팬 · [[스마트 조명]]", "본업인 조명·실링팬을 임대 단지 기준으로 다시 구성했습니다.",
    split(grid([("fan_2", "아크로 슬림 실링팬 설치 사례"), ("fan_3", "실링팬 + 간접조명"), ("led_1", "우물 간접조명"), ("led_2", "복도 LED")], 2, 2),
          bullets([("임대 세대: 교체형 조명", "기존 등기구 자리에 교체 설치, 기존 등은 세대에 보관해 퇴거 시 복원할 수 있습니다."),
                   ("실링팬은 승인 품목", "천장 시공이 필요해 임대사업자 승인 기준에 맞춰 안내합니다."),
                   ("앱·리모컨 제어", "6단 풍량·타이머·블루투스 제어 — 조명과 함께 한 앱으로."),
                   ("무타공 전동커튼", "벽·천장 타공 없이 설치하는 방식을 우선 제안합니다.")]), "50% 1fr"),
    "시공은 [[전기공사업 면허]] 기반 직접 시공 · KC 인증 제품만 취급합니다.")

std("10. 동탄 특화", "공동구매 단가를 지키는 [[4가지 장치]]", "공고문이 우려한 ‘행사비 때문에 오르는 단가’를 구조로 막습니다.",
    cards([dict(lb="01", big="공개", nm="단가표 사전 공개", ds="박람회 전 품목별 단가·할인율을 임예협이 검수. 현장 가격 변경 없음."),
           dict(lb="02", big="10", unit="배", nm="최저가 차액 보상", ds="동일 브랜드·동일 제품이 더 싸면 차액의 10배 보상."),
           dict(lb="03", big="1~3", unit="%", nm="실적 비례 추가할인", ds="50·100·150세대 계약 시 잔금에서 1·2·3%."),
           dict(lb="04", big="5", unit="%", nm="계약금 상한", ds="잔금은 시공·설치 후. 현금·카드 동일가.", hl=True)]),
    "가격은 말이 아니라 [[사전 공개 단가 + 최저가 보장]]으로 검증받습니다.")

CLOSING = [("세대당 15만원 발전지원금", f"{HH:,}세대 기준 {FUND_S} · 임예협 협의 후 집행"),
           ("하자 예치금 1억 · 이행보증 10억", "주관사 순수 자산 공동통장 · 증권 실물 제출"),
           ("임예협 전용 무상 지원", "사전점검·품질 검증·행정·컨설팅 — 자체 인력"),
           ("임대 단지 시공 허용 가이드", "원상복구 분쟁 예방 · 세대별 시공 이력 카드"),
           ("지역업체 90% · 하도급 없음", "동탄·화성 지역업체 · 48시간 A/S"),
           ("최저가 보장 차액 10배", "단가표 사전 공개 · 현장 가격 변경 없음"),
           ("48시간 하자보수 · 장기 A/S", "콜센터·CRM·베이스캠프 · 최소 2년 무상"),
           ("경관조명 컨설팅·설계·생산·시공", "전기공사업 면허 · KC 인증 · 직접 시공")]
std("CLOSING", "엣지컴퍼니가 [[약속드리는 것]]", "제안서에 쓴 것은 전부 협약서와 증빙으로 남깁니다.",
    cards([dict(lb=f"{i:02d}", nm=a, ds=b) for i, (a, b) in enumerate(CLOSING, 1)], cols=2, rows_n=4),
    "못 지키면 [[주관사 자격 철회]]에 동의합니다.")

name, title, tel = D.MANAGER
add(lambda no: f"""<section class="page cv"><div class="pic"><img src="{A}hq_2.jpg" alt=""></div>
<div class="tx"><div><div class="logo">EG</div><div class="en">EDGE COMPANY</div></div>
<div class="mid"><span class="pill">CONTACT</span>
<h1>{HH:,}세대의 10년,<br><em>끝까지 함께하겠습니다.</em></h1>
<div class="tag2">임차예정자협의회·시행사·협력업체 모두 환영합니다.</div>
<div class="contacts">
<div><b>1533-3210</b><span>본사 대표번호</span></div>
<div><b>{D.CEO_TEL}</b><span>대표이사 {D.CEO}</span></div>
<div><b>{tel}</b><span>{title} {name}</span></div>
<div class="me"><b>{D.EMAIL}</b><span>이메일 문의</span></div></div>
<div class="addr">본사 · {D.ADDRESS}<br>전기공사업 등록 울산-00821호 · ISO 9001/14001/45001 · 삼성전자 MOU</div></div>
<div class="bt"><span>{D.COMPANY}</span><span>공동구매 입찰 제안서 [2-1]</span></div></div></section>""")


# ============================================================ 빌드
def build():
    out = [f(no) for no, f in enumerate(PAGES, 1)]
    doc = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<title>엣지컴퍼니 동탄 파라곤3차 공동구매 입찰 제안서 [2-1]</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>{CSS}</style></head><body>
{chr(10).join(out)}
</body></html>"""
    bad = re.findall(r".{0,10}(?:입예협|최초(?! 계약)|최고|전국최저|200%|오직).{0,8}", doc)
    assert not bad, bad  # 협의회는 '타 단지 협의회 추천서' 등 과거 실적 문맥에만 사용
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"HTML: {OUT_HTML} ({len(PAGES)} pages)")
    if "--no-pdf" in sys.argv:
        return
    exe = find_chrome()
    subprocess.run([exe, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=15000", f"--print-to-pdf={OUT_PDF}", pathlib.Path(OUT_HTML).as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"PDF : {OUT_PDF} ({os.path.getsize(OUT_PDF) / 1e6:.1f}MB)")


if __name__ == "__main__":
    build()
