# -*- coding: utf-8 -*-
"""롯데캐슬 나리벡시티 입주박람회 주관사 입찰 — 공고 7항 제출서류 생성기(A4 세로). 번호 = 공고 7항 01 ~ 14 그대로.

  01 입찰참가 신청서 [별지서식 제1호]          02 입주박람회 입찰 제안서(자유양식 · 밝은 시안 원본)
  03 입주박람회 실적 및 공동구매 증빙 자료(최근 3년간 실적 증명서 + 증빙 안내 + 별첨 1 NICE 연혁 · 2 실적 확약서 · 3 주관사 협약서 · 4 공식 행사일정)
  04 계약 취소 건 환불 규정(자유양식 · 제1 ~ 10조 · 별표)
  05 사업자등록증 · 06 법인등기부등본 · 법인인감증명서 · 07 국세 · 지방세 완납증명서 · 08 4대 보험 가입자 명부 · 완납증명서
  09 기업신용평가서                            → 05 ~ 08 = 공고일(2026.10.19) 이후 발급본만(evidence_nr/ · 없으면 '조치 필요')
                                                  09 = NICE = 재무제표 기준 연 1회 정기 평가(본부장 10-23) → 유효기간 안 최근 평가본 그대로(재출력 · 질의 없음)
  10 확약 및 이행 서약서 [별지 2] · 11 하자 보수 이행각서 [별지 3] · 12 비밀유지 서약서 [별지 4] · 13 청렴계약 이행준수 서약서 [별지 5]
  14 기타(선택) — 요약제안서 · 법인 통장 사본(자격 3) · 2026.10.14 완납증명서(자격 6 공고일 이전 완납) · 보증증권 발급 이력 · 영주자이 도어록 집행 계약서
별지 1 ~ 5는 서식(hwp) 문구를 원문 그대로 옮기고 빈칸만 채운다. 날인 = 서식 '인감' 칸 → 법인인감 실물 날인 스캔(seal_scan/나리벡_별지1-5_법인인감.pdf · 5쪽 1 ~ 5 순).
  스캔이 없으면 '날인 전' 상태로 작업/에만 두고 제출본에 넣지 않는다(법인인감을 디지털로 만들지 않음). 당사 자체 문서(03 · 04 · 09 표지 · 14 안내)는 직인.
출력: 작업/ = 중간 파일 + 서식날인_출력용.pdf + 제출현황.txt(내부용 — 첨부 금지)
      제출본/ = 조치 끝난 서류만 'NN_서류명.pdf' · ZIP = '제안자료_주식회사 엣지컴퍼니.zip'(번호 순 PDF · 공고 7항 '제출자료' 이름)
사용: python3 docs_nr.py <직인.png> [--final]     (결과 PDF · ZIP은 깃 제외 — .gitignore)
"""
import html
import importlib.util
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import zipfile

import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "요약제안서"), os.path.join(HERE, "..", "동탄파라곤3차")]
import data as D  # noqa: E402
from build import find_chrome  # noqa: E402

e = html.escape
PFX = "엣지컴퍼니_롯데캐슬나리벡시티_"
ST = D.SITE
SITE = ST["name"]
FORM_TO = "롯데캐슬 나리벡시티 입주예정자협의회"      # 서식(별지 1 ~ 5) 원문 표기 그대로
TODOS = []

SP = "/tmp/claude-0/-home-user-edge-company/a96d9eb6-5244-5d3f-9f1b-6f379ac2a82c/scratchpad"
EV = f"{SP}/evidence"            # 기존 증빙(2026.10.14 · 10.15 발급 — 공고일 이전) · 깃 제외
EVN = f"{SP}/evidence_nr"        # 공고일(10.19) 이후 재발급본 — 본부장이 받으면 같은 파일 이름으로 여기에(인감증명서는 주민번호 뒷자리 가림본)
ROSTER = f"{SP}/cs_sub/엣지컴퍼니_4대보험_사업장가입자명부_20261023_가림.pdf"   # 2026.10.23 발급 13명 · 가림본 = 공고일 이후
NICE_SRC = f"{EV}/NICE_기업신용평가.pdf"
CAP_DIR = f"{SP}/hw/cap"
SEAL_SCAN = f"{SP}/seal_scan/나리벡_별지1-5_법인인감.pdf"   # 본부장 실물 법인인감 날인 스캔(5쪽 · 별지 1 ~ 5 순)
WORK = os.path.join(HERE, "작업")
SUBMIT = os.path.join(HERE, "제출본")
ZIP = os.path.join(HERE, D.FILE_TITLE + ".zip")
P02 = os.path.join(HERE, PFX + "입주박람회_주관사_제안서_밝은시안.pdf")
P14S = os.path.join(HERE, PFX + "요약제안서_밝은시안.pdf")
NOTICE_DAY = "2026.10.19"

_priv = os.path.join(HERE, "org_private.json")  # 깃 제외(생년월일 · 실명)
PRIV = json.load(open(_priv, encoding="utf-8")) if os.path.exists(_priv) else {}

# 공고일 이후 발급이 필요한 증빙 — (번호, 파일 이름, 설명)
REISSUE = [("05", "사업자등록증.pdf", "사업자등록증"), ("06", "법인등기부등본.pdf", "법인등기부등본"), ("06", "법인인감증명서.pdf", "법인인감증명서(가림본)"),
           ("07", "국세_납세증명서.pdf", "국세 완납증명서"), ("07", "지방세_납세증명서.pdf", "지방세 완납증명서"),
           ("08", "4대보험_완납증명서.pdf", "4대보험 완납증명서(건강 · 연금)"), ("08", "고용산재_완납증명서.pdf", "고용 · 산재 완납증명서")]


def ev(name):
    """공고일 이후 재발급본(evidence_nr/)이 있으면 그것, 없으면 기존본 + '조치 필요'."""
    p = os.path.join(EVN, name)
    return (p, True) if os.path.exists(p) else (os.path.join(EV, name), False)


def todo(x):
    TODOS.append(x)
    return f'<mark class="todo">{e(x)}</mark>'


CSS = r"""
@page{size:A4;margin:14mm 17mm 13mm}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Pretendard','Malgun Gothic','맑은 고딕',sans-serif;color:#1B2433;font-size:10pt;line-height:1.6;
  word-break:keep-all;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.pg{page-break-after:always}.pg:last-child{page-break-after:auto}
mark.todo{background:#FFE066;color:#0D1E33;font-weight:700;padding:0 4pt}
.top{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:2.5pt solid #0D1E33;padding-bottom:6pt}
.top .lb{font-size:9pt;font-weight:700;letter-spacing:.18em;color:#9A7B3F}
.top .co{font-size:9pt;color:#5B6676;text-align:right}
h1{font-size:19pt;font-weight:800;color:#0D1E33;margin-top:12pt;line-height:1.3}
h1.c{text-align:center;font-size:21pt;letter-spacing:.2em;margin-top:16pt}
.case{font-size:9.5pt;color:#5B6676;margin-top:3pt}
.info{width:100%;border-collapse:collapse;margin-top:12pt;font-size:9.8pt}
.info th{width:17%;background:#F1EDE4;color:#0D1E33;font-weight:700;text-align:left;padding:5pt 9pt;border:.6pt solid #D5CCB9;white-space:nowrap}
.info td{padding:5pt 9pt;border:.6pt solid #D5CCB9}
h2{font-size:12pt;font-weight:800;color:#0D1E33;margin:13pt 0 5pt;padding-left:8pt;border-left:3.5pt solid #C8A86A;line-height:1.3;break-after:avoid}
.t{width:100%;border-collapse:collapse;font-size:9.3pt;line-height:1.45}
.t th{background:#0D1E33;color:#fff;font-weight:700;padding:4pt 6pt;border:.6pt solid #0D1E33;text-align:center}
.t td{padding:3.4pt 6pt;border:.6pt solid #C9CED6;text-align:center;vertical-align:middle}
.t td.l{text-align:left}.t td.r{text-align:right;font-variant-numeric:tabular-nums}
.t tr{break-inside:avoid}
.t td.k{font-weight:700;background:#F6F7F9;text-align:left;white-space:nowrap}
.t.ls{font-size:8.7pt;line-height:1.35}ol.pl li.sm{font-size:9.2pt;margin-top:2pt;line-height:1.5}.t.ls td{padding:2pt 5pt}
.t tr.jg td{background:#FBF8F1}.t tr.jg td.g{color:#9A7B3F;font-weight:800}
.t tr.sum td{background:#F1EDE4;font-weight:800}
.t tr.gh td{background:#0D1E33;color:#fff;font-weight:800;text-align:left;font-size:8.6pt;letter-spacing:.02em}
.box{border:1pt solid #C8A86A;background:#FBF8F1;border-radius:4pt;padding:7pt 11pt;margin-top:10pt;font-size:9.8pt;line-height:1.65}
.box b{color:#0D1E33}
p.body{margin-top:12pt;font-size:10.5pt;line-height:1.85}
.note{font-size:8.8pt;color:#5B6676;margin-top:5pt;line-height:1.55}
ol.pl{list-style:none;margin-top:8pt}
ol.pl li{padding-left:16pt;text-indent:-16pt;margin-top:5pt;font-size:10.2pt;line-height:1.72}
.sign{margin-top:16pt;text-align:center;break-inside:avoid}
.sign .d{font-size:11pt;letter-spacing:.06em}
.sign .who{margin-top:6pt;font-size:12pt;font-weight:700}
.sign .seal{color:#5B6676;font-size:10pt;font-weight:400;margin-left:30pt}
.to{margin-top:18pt;text-align:center;font-size:12.5pt;font-weight:800;color:#0D1E33}
/* 공고 별지 서식 — 흑백 */
.form{color:#111;font-size:11pt;line-height:1.85}
.form .no{font-size:10pt;color:#333}
.form h1{text-align:center;font-size:21pt;letter-spacing:.3em;color:#111;margin:14pt 0 16pt}
.form .ft{width:100%;border-collapse:collapse;font-size:10.3pt}
.form .ft th,.form .ft td{border:.8pt solid #333;padding:6.5pt 8pt;vertical-align:middle;line-height:1.5}
.form .ft th{background:#F2F2F2;font-weight:700;text-align:center;white-space:nowrap}
.form .ft td.c{text-align:center}
.form p.tx{margin-top:14pt;text-indent:10pt;text-align:justify}
.form ol{list-style:none;margin-top:8pt}
.form ol li{padding-left:16pt;text-indent:-16pt;margin-top:6pt;text-align:justify}
.form .dt{text-align:center;margin-top:22pt;font-size:12pt;letter-spacing:.15em}
.form .sg{margin:20pt 0 0 50%;font-size:11.5pt;line-height:3.0}
.form .to2{margin-top:44pt;text-align:center;font-size:13pt;font-weight:800;line-height:1.6}
.form .sgx{display:flex;justify-content:center;align-items:center;gap:26pt;margin-top:20pt}
.form .sgx .ln{font-size:11.3pt;line-height:2.25}
.form .sgx .bx{width:80pt;height:80pt;border:1pt solid #333;position:relative;flex:none}
.form .sgx .bx i{position:absolute;left:0;right:0;top:6pt;text-align:center;font-style:normal;font-size:8.5pt;color:#777;line-height:1.25}
.form .sgx .bx b{position:absolute;left:0;right:0;top:44pt;text-align:center;font-weight:400;font-size:10pt;color:#999}
.form .warn{font-size:9pt;color:#444;margin-top:8pt;text-align:center}
.form .ft.r2 th,.form .ft.r2 td{padding:5pt 7pt;font-size:10pt}
.art h3{font-size:10.5pt;font-weight:800;color:#0D1E33;margin-top:7pt}
.art ol{list-style:none;margin-top:2pt}.art li{font-size:9.4pt;line-height:1.6;padding-left:13pt;text-indent:-13pt;margin-top:1pt}
.art p{font-size:9.4pt;line-height:1.6;margin-top:2pt}
/* 조직도(16) — 본부장 칸은 CEO → 4개 팀 줄기에서 오른쪽으로(제안서 조직 구성 쪽과 같은 배치) */
.oc{margin-top:8pt;display:flex;flex-direction:column;align-items:center}
.oc .ceo{border:1.4pt solid #C8A86A;border-radius:50%;width:78pt;height:78pt;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#0D1E33;color:#fff}
.oc .ceo i{font-style:normal;font-size:7.5pt;color:#D9C9A3}.oc .ceo b{font-size:15pt;color:#EBCB8F;line-height:1.1}.oc .ceo span{font-size:9pt;letter-spacing:.2em}
.oc .gmr{position:relative;width:100%;height:30pt}
.oc .gmr:before{content:'';position:absolute;left:50%;top:0;bottom:0;width:1.4pt;background:#C8A86A}
.oc .gm{position:absolute;left:calc(50% + 26pt);top:6pt;border:1.2pt solid #C8A86A;border-radius:5pt;padding:2pt 10pt;font-size:9.5pt;background:#fff}
.oc .gm:before{content:'';position:absolute;right:100%;top:50%;width:26pt;height:1.2pt;background:#C8A86A}
.oc .gm em{font-style:normal;color:#9A7B3F;font-weight:700;margin-right:6pt}
.oc .bar{width:75.6%;height:12pt;border:1.4pt solid #C8A86A;border-bottom:0;border-radius:0}
.oc .tms{display:grid;grid-template-columns:repeat(4,1fr);gap:7pt;width:100%}
.oc .tm{border:.8pt solid #C8A86A;border-radius:5pt;padding:5pt 6pt;text-align:center;background:#FBF8F1}
.oc .tm b{display:block;font-size:10pt;color:#0D1E33}.oc .tm b em{font-style:normal;color:#9A7B3F;margin-left:3pt}
.oc .tm small{display:block;font-size:8pt;color:#5B6676;line-height:1.35;margin-top:2pt}
"""

HEAD = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{t}</title>'
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">'
        '<style>{css}</style></head><body>')


def doc(title, sections, css=CSS):
    return HEAD.format(t=e(title), css=css) + "".join(f'<section class="pg">{s}</section>' for s in sections) + "</body></html>"


def head(label, title, center=False):
    return (f'<div class="top"><div class="lb">{e(label)}</div><div class="co">{D.COMPANY} · 입주박람회 주관사</div></div>'
            f'<h1 class="{"c" if center else ""}">{e(title)}</h1>'
            f'<div class="case" style="{"text-align:center" if center else ""}">건명 : {e(D.NOTICE)}</div>')


# ------------------------------------------------------------------ PDF · 날인 · 병합(오산 docs_os.py와 같은 방식)
GARBAGE = 3  # garbage=4는 크롬 PDF Type3 글꼴 글자가 빠지는 경우가 있음(분당 10-14 확인)


def out(name):
    return os.path.join(WORK, PFX + name)


def to_pdf(html_path, pdf_path):
    subprocess.run([find_chrome(), "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=8000", f"--print-to-pdf={pdf_path}", pathlib.Path(html_path).as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def render(name, html_text):
    h = out(name + ".html")
    pathlib.Path(h).write_text(html_text, encoding="utf-8")
    p = h[:-5] + ".pdf"
    to_pdf(h, p)
    return p


def page_texts(d_or_path):
    d = d_or_path if isinstance(d_or_path, fitz.Document) else fitz.open(d_or_path)
    return [p.get_text() for p in d]


def merge(out_name, parts, title, toc=None):
    o, src = fitz.open(), []
    for p in parts:
        d = p if isinstance(p, fitz.Document) else fitz.open(p)
        src += page_texts(d)
        o.insert_pdf(d)
    o.set_metadata({"title": title, "author": D.COMPANY})
    if toc:
        o.set_toc(toc)
    path = out(out_name + ".pdf")
    o.save(path, garbage=GARBAGE, deflate=True)
    bad = [i + 1 for i, (a, b) in enumerate(zip(src, page_texts(path))) if a != b]
    assert not bad, f"합친 뒤 글자가 달라진 쪽 {bad}: {path}"
    return path


def seal_image(path, px=360):
    """직인 PNG — 배경 투명(알파 있음)이면 그대로, 흰 배경이면 stamp.seal_png로 투명 처리. 360px로 줄여 용량을 줄인다."""
    from PIL import Image
    import stamp as ST_
    im = Image.open(path)
    raw = open(path, "rb").read() if (im.mode == "RGBA" and im.getextrema()[3][0] == 0) else ST_.seal_png(path)
    im = Image.open(io.BytesIO(raw))
    im.thumbnail((px, px), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def stamp(seal, pdf_path):
    """'(인)' 가운데에 직인(54pt) — 저장 garbage=3 · 글자 대조."""
    import stamp as ST_
    d = fitz.open(pdf_path)
    before = page_texts(d)
    n = 0
    for page in d:
        for mark in ST_.MARKS:
            hits = page.search_for(mark)
            if not hits:
                continue
            for r in hits:
                c = fitz.Point((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)
                s = ST_.SIZE / 2
                page.insert_image(fitz.Rect(c.x - s, c.y - s, c.x + s, c.y + s), stream=seal, overlay=True)
                n += 1
            break
    o = pdf_path[:-4] + "_직인.pdf"
    d.save(o, garbage=GARBAGE, deflate=True)
    assert page_texts(o) == before, f"날인 뒤 글자가 달라짐: {o}"
    return o, n


def fit(path, lo, hi=None):
    k = len(fitz.open(path))
    assert lo <= k <= (hi or lo), f"{os.path.basename(path)}: {k}쪽(예상 {lo}{'' if hi is None else f' ~ {hi}'}쪽) — 내용이 넘침"
    return path


# 별첨 1 — NICE 원본 9쪽 연혁 발췌(오산 docs_os.annex12_nice와 같은 방식 · 나리벡 표기)
FONTS = os.path.join(HERE, "..", "통합제안서", "fonts")
NAVY, GOLD, GRAY, LINE = (0.051, 0.118, 0.2), (0.78, 0.66, 0.42), (0.36, 0.4, 0.46), (0.79, 0.81, 0.84)
CLIP_TITLE = fitz.Rect(0, 0, 595, 76)
CLIP_HIST = fitz.Rect(36, 321, 560, 511)
ROWS_RECENT = (398, 506)     # 연혁 표 중 최근 3년 주관 실적 6행(2023/11 ~ 2026/07)
CLIP_FOOT = fitz.Rect(36, 800, 560, 828)


def annex_nice(nice_path, out_path):
    nice = fitz.open(nice_path)
    o = fitz.open()
    pg = o.new_page(width=595.28, height=841.89)
    F = {"r": fitz.Font(fontfile=os.path.join(FONTS, "Pretendard-Regular.ttf")),
         "b": fitz.Font(fontfile=os.path.join(FONTS, "Pretendard-Bold.ttf"))}

    def text(x, y, s, size=9.5, w="r", color=NAVY, align="l"):
        f = F[w]
        if align != "l":
            tl = f.text_length(s, fontsize=size)
            x = x - tl / 2 if align == "c" else x - tl
        tw = fitz.TextWriter(pg.rect)
        tw.append((x, y), s, font=f, fontsize=size)
        tw.write_text(pg, color=color)

    L, R = 48, 547
    pg.draw_rect(fitz.Rect(L, 40, L + 46, 56), color=GOLD, width=1)
    text(L + 23, 51.5, "별첨 1", 8.5, "b", GOLD, "c")
    text(R, 51.5, "제출서류 03 입주박람회 실적 및 공동구매 증빙", 8.5, "r", GRAY, "r")
    pg.draw_line((L, 64), (R, 64), color=NAVY, width=2)
    text(L, 92, "NICE디앤비 기업신용평가보고서 ‘연혁’ 발췌", 17, "b")
    text(L, 110, f"건명 : {D.NOTICE}", 8.8, "r", GRAY)
    top = 126
    cover = fitz.Rect(L, top, L + 168, top + 168 * 842 / 595)
    pg.show_pdf_page(cover, nice, 0)
    pg.draw_rect(cover, color=LINE, width=0.6)
    info = [("보고서명", "CLIP 기업신용평가보고서"), ("발행 기관", "NICE디앤비 (dun & bradstreet)"),
            ("평가 대상", f"{D.COMPANY} ({D.BIZ_NO})"), ("관리번호", "11125949-202605-001"),
            ("평가완료일", D.NICE_DATE), ("발췌 범위", "9쪽 ‘04 영업 현황(기업개요)’ 중 ‘연혁’"),
            ("원본 분량", f"전 {len(nice)}쪽 (전문은 제출서류 09)")]
    x0, x1, xk, rh = L + 186, R, L + 186 + 70, 24
    for i, (k, v) in enumerate(info):
        y = top + i * rh
        pg.draw_rect(fitz.Rect(x0, y, xk, y + rh), color=LINE, fill=(0.945, 0.929, 0.894), width=0.6)
        pg.draw_rect(fitz.Rect(xk, y, x1, y + rh), color=LINE, width=0.6)
        text(x0 + 8, y + 15.5, k, 8.8, "b")
        text(xk + 8, y + 15.5, v, 8.8, "r", (0.1, 0.14, 0.2))
    y = top + len(info) * rh + 18
    text(x0, y, "아래 연혁 중 금색 테두리 6행이 최근 3년", 8.8, "r", GRAY)
    text(x0, y + 13, "1,000세대 이상 입주박람회 주관 실적입니다.", 8.8, "r", GRAY)
    s = (R - L) / 595
    y = cover.y1 + 22
    text(L, y, "■ 원본 9쪽 발췌", 9, "b")
    box_top = y + 8
    y = box_top + 4

    def put(clip, y):
        r = fitz.Rect(L + clip.x0 * s, y, L + clip.x1 * s, y + clip.height * s)
        pg.show_pdf_page(r, nice, 8, clip=clip)
        return r

    put(CLIP_TITLE, y)
    y += CLIP_TITLE.height * s + 2
    text((L + R) / 2, y + 9, "··· (중략: 기업개요) ···", 8, "r", GRAY, "c")
    y += 16
    hist = put(CLIP_HIST, y)
    hy0 = hist.y0 + (ROWS_RECENT[0] - CLIP_HIST.y0) * s
    hy1 = hist.y0 + (ROWS_RECENT[1] - CLIP_HIST.y0) * s
    pg.draw_rect(fitz.Rect(hist.x0 - 3, hy0 - 1, hist.x1 + 3, hy1 + 1), color=GOLD, width=1.6)
    y = hist.y1 + 4
    text((L + R) / 2, y + 9, "··· (이하 생략: 관계회사) ···", 8, "r", GRAY, "c")
    y += 16
    foot = put(CLIP_FOOT, y)
    pg.draw_rect(fitz.Rect(L, box_top, R, foot.y1 + 6), color=LINE, width=0.6)
    y = foot.y1 + 40
    text((L + R) / 2, y, "위 발췌 내용은 원본과 같음을 확인합니다.", 10, "r", (0.1, 0.14, 0.2), "c")
    yy, mm, dd = ymd()
    text((L + R) / 2, y + 26, f"{yy}년 {mm}월 {dd}일", 10, "r", (0.1, 0.14, 0.2), "c")
    who = f"{D.COMPANY}   대표이사   {D.CEO}"
    text((L + R) / 2 - 14, y + 52, who, 11, "b", NAVY, "c")
    sx = (L + R) / 2 - 14 + F["b"].text_length(who, fontsize=11) / 2 + 30
    text(sx, y + 52, "(인)", 10, "r", GRAY)
    o.set_metadata({"title": "별첨 1 NICE 기업신용평가보고서 연혁 발췌", "author": D.COMPANY})
    o.save(out_path, garbage=GARBAGE, deflate=True)
    return out_path


# 별첨 2 — 실적 확약서: 탕정 hwakyak.py의 실적 · 캡처 목록을 읽기만 한다(오산과 같은 방식)
def _hwakyak():
    path = os.path.join(HERE, "..", "탕정푸르지오센터파크", "hwakyak.py")
    saved, dwb = list(sys.path), sys.dont_write_bytecode
    sys.dont_write_bytecode = True  # 탕정 폴더에 캐시 파일을 만들지 않는다
    try:
        spec = importlib.util.spec_from_file_location("_hwakyak_tj", path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
    finally:
        sys.path[:] = saved
        sys.dont_write_bytecode = dwb
    return m


HW_FIT = "p.body{margin:8pt 0 5pt;line-height:1.75}.t td{padding:2.2pt 5pt}ol{margin-top:6pt;line-height:1.6}.sign{margin-top:8pt;line-height:1.85}.to{margin-top:6pt}"


def doc09_hwakyak():
    hw = _hwakyak()
    yy, mm, dd = ymd()
    for f, _t, _u, _w, boxes in hw.CAPS:  # 가림본이 없으면 원본 캡처에서 다시 가림(픽셀로 굳힘)
        dst = os.path.join(HERE, "assets_ins", "cafe_" + f)
        if not os.path.exists(dst):
            hw.mask(os.path.join(CAP_DIR, f), boxes, dst)
    src_fix = {"입예협 카페 공지 (붙임 1)": "입주민 카페 주관사 게시판 (붙임 1)", "입예협 카페 공지 (붙임 2)": "입주자 모임 카페 주관사 공지 (붙임 2)"}
    recs = [(a, b, c, n, src_fix.get(s, s)) for a, b, c, n, s in hw.RECS]
    assert any("입주민 카페" in r[4] for r in recs), "사상 근거 표기 — 탕정 hwakyak.py RECS 문구가 바뀜"
    rows = "".join(f'<tr><td>{i}</td><td>{e(a)}</td><td class="l">{e(b)}</td><td>{e(c)}</td><td class="r">{n:,}</td><td class="l">{e(s)}</td></tr>'
                   for i, (a, b, c, n, s) in enumerate(recs, 1))
    tot = sum(r[3] for r in recs)
    assert (len(recs), tot) == (10, 19563), "실적 확약서 합계가 제안서(10개 단지 · 19,563세대)와 다름"
    p1 = f"""<section class="pg">
<div style="font-size:9pt;color:#9A7B3F;font-weight:700;letter-spacing:.1em">별첨 2 · 제출서류 03</div>
<h1>실 적 확 약 서</h1><div class="sub">1,000세대 이상 공동주택 입주박람회 주관 실적</div>
<table class="info"><tr><th>상호</th><td>{D.COMPANY}</td><th>대표이사</th><td>{D.CEO}</td></tr>
<tr><th>소재지</th><td colspan="3">{D.ADDRESS}</td></tr>
<tr><th>제출처</th><td colspan="3">{FORM_TO}</td></tr></table>
<p class="body">당사는 「{e(D.NOTICE)}」의 입찰 참가자격(주관 · 운영 실적)과 관련하여, 1,000세대 이상 공동주택 단지의 입주박람회 주관 실적을 아래와 같이 제출하며 기재 내용이 사실임을 확약합니다.</p>
<table class="t"><tr><th>연번</th><th>주관 시기</th><th>단지명</th><th>지역</th><th>세대수</th><th>근거</th></tr>{rows}
<tr class="sum"><td colspan="4">합계 {len(recs)}개 단지</td><td class="r">{tot:,}</td><td></td></tr></table>
<div class="note">※ 근거: NICE 기업신용평가보고서(평가일 {D.NICE_DATE}) '연혁'(별첨 1 · 원본 9쪽) · 단지 카페(입주민 · 입주자 모임 카페)의 주관사 명의 공지 · BEXCO 공식 행사일정(붙임). 세대수는 NICE 연혁 기재값(카페 공지 · BEXCO 근거 3개 단지는 단지 공식 총세대수). 최근 3년 밖(2023.10 이전) 2개 단지를 포함한 전체 주관 실적입니다.</div>
<ol><li>위 실적은 당사가 입주박람회 주관사로서 직접 수행한 것입니다.</li>
<li>귀 협의회가 요청하면 계약서, 실적 확인서, 정산 자료 등 증빙을 지체 없이 제출하겠습니다.</li>
<li>기재 내용이 사실과 다른 것으로 밝혀지면 공고 ‘입찰 참가 제한’에 따른 모든 조치를 이의 없이 받아들이겠습니다.</li></ol>
<div class="sign"><div class="d">{yy}년 &nbsp;{mm}월 &nbsp;{dd}일</div>
{D.COMPANY}<br><b>대표이사 &nbsp;{" ".join(D.CEO)}</b><span style="margin-left:48pt">(인)</span></div>
<div class="to">{FORM_TO} 귀하</div></section>"""
    caps = ""
    for f, title, url, what, boxes in hw.CAPS:
        kind = ("전시장 공식 행사일정 캡처" if f.startswith("bexco") else
                "입주민 소통 카페 주관사 게시판 캡처" if f.startswith("sasang") else "입주자 모임 카페 주관사 공지 캡처")
        caps += (f'<section class="pg"><h2>실적 확약서 붙임 · {kind}</h2><div class="cap"><h3>{e(title)}</h3>'
                 f'<div class="u">{e(url)}{" · 입주민 닉네임(동·호수)은 개인정보 보호를 위해 가림" if boxes else ""}</div><div class="k">{e(what)}</div>'
                 f'<img src="../assets_ins/cafe_{f}"></div></section>')  # HTML은 작업/ 아래
    return f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>실적 확약서</title><style>{hw.CSS}{HW_FIT}</style></head><body>{p1}{caps}</body></html>'


def CAP_SRC():
    k = []
    if any(c[2].startswith("BEXCO") for c in D.EXPO_CAPS): k.append("벡스코(BEXCO) 홈페이지 ‘행사일정’ 상세 화면")
    if any("UECO" in c[2] for c in D.EXPO_CAPS): k.append("울산전시컨벤션센터(UECO) 홈페이지 ‘전체일정’ 화면")
    if any("CECO" in c[2] for c in D.EXPO_CAPS): k.append("창원컨벤션센터(CECO) 홈페이지 ‘전체일정’ 화면")
    if any("카페" in c[2] for c in D.EXPO_CAPS): k.append("단지 입주자 공식 카페 ‘엣지컴퍼니 공지사항’ 게시판")
    return " · ".join(k)


def CAP_TITLE():
    return "BEXCO 공식 행사일정 캡처" if all(c[2].startswith("BEXCO") for c in D.EXPO_CAPS) else "박람회장 공식 행사일정 · 카페 공지 캡처"


def doc09_bexco():  # 별첨 4 — 한 장에 2 ~ 3곳(본부장 10-19: 서류 수를 늘리지 않게 묶음 · 안 되면 나눔)
    from PIL import Image
    caps = []
    for k, (nm, f, kind, per, hall) in enumerate(D.EXPO_CAPS, 1):
        w, h = Image.open(os.path.join(HERE, "assets_ins", f)).size
        caps.append((k, nm, f, kind, per, hall, 2 if h > w else 1))  # 세로 캡처 = 2칸
    tot_w = sum(c[-1] for c in caps)
    npg = max(1, -(-tot_w // 3))
    pages, cur, cw, left = [], [], 0, tot_w
    for c in caps:
        tgt = -(-left // (npg - len(pages))) if npg > len(pages) else 3
        if cur and cw + c[-1] > tgt:
            pages.append(cur); left -= cw; cur, cw = [], 0
            tgt = -(-left // max(1, npg - len(pages)))
        cur.append(c); cw += c[-1]
    if cur: pages.append(cur)
    secs = []
    for pi, cs in enumerate(pages):
        items = "".join(
            f'<div class="bxc{" tall" if wt == 2 else ""}"><div class="bh"><b>4-{k}</b> {e(nm)} <span>· {e(kind)} · {e(per)} · {e(hall)}</span></div>'
            f'<img src="../assets_ins/{f}" alt=""></div>' for k, nm, f, kind, per, hall, wt in cs)
        secs.append(head("제출서류 03 · 별첨 4", f"{CAP_TITLE()} ({pi + 1}/{len(pages)})")
                    + f'<p class="note" style="margin-top:4pt">출처: {CAP_SRC()} · 주최 · 주관란 = 주식회사 엣지컴퍼니 · 화면 그대로{"(입주민 닉네임만 가림)" if any("카페" in c[2] for c in D.EXPO_CAPS) else "(가공 없음)"}</p>'
                    + f'<div class="bxs">{items}</div>')
    css = CSS + (".bxs{display:flex;flex-direction:column;gap:7pt;margin-top:6pt}.bxc{border:1px solid #c9ced6;border-radius:3pt;padding:5pt 6pt}"
                 ".bh{font-size:10pt;margin-bottom:4pt}.bh b{color:#9A7B3F;margin-right:4pt}.bh span{color:#555;font-size:9pt}"
                 ".bxc img{display:block;width:100%;max-height:58mm;object-fit:contain;object-position:left top}.bxc.tall img{max-height:130mm}")
    return doc("03 별첨 4 박람회 공식 행사일정 · 카페 공지", secs, css), len(pages)


NICE_MASK = {12: [(170, 148.5, 228, 163.5), (170, 166.5, 228, 181.5)]}  # 원본 13쪽 '주요 경영진' 생년월일 칸 — 대표 외 임직원 2명


def nice_full(nice_path):
    d = fitz.open(nice_path)
    assert len(d) == 24, f"NICE 보고서 {len(d)}쪽 — 가림 좌표 다시 확인"
    for i, rects in NICE_MASK.items():
        pg = d[i]
        assert any(x["width"] == 2477 and x["height"] == 3502 for x in pg.get_image_info()), "NICE 13쪽 이미지가 다름 — 가림 좌표 다시 확인"
        for r in rects:
            pg.add_redact_annot(fitz.Rect(*r), fill=(0.82, 0.82, 0.82))
        pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS)
    p = out("09_2_NICE_전문_가림.pdf")
    d.save(p, garbage=GARBAGE, deflate=True)
    return p


def ymd():
    return D.SIGN_DATE


def sign():
    yy, mm, dd = ymd()
    return (f'<div class="sign"><div class="d">{yy}년 {mm}월 {dd}일</div>'
            f'<div class="who">{D.COMPANY} &nbsp; 대표이사 &nbsp; {D.CEO}<span class="seal">(인)</span></div></div>'
            f'<div class="to">{FORM_TO} 귀하</div>')


def form_tail(fields):
    """별지 서식 꼬리(원문): 항목 줄 + '인감' 칸 → 날짜 → 귀하. 인감 칸은 비워 둔다(실물 법인인감 날인)."""
    yy, mm, dd = ymd()
    ln = "<br>".join(f"{k} : <b>{v}</b>" if i < 2 else f"{k} : {v}" for i, (k, v) in enumerate(fields))
    return (f'<div class="sgx"><div class="ln">{ln}</div><div class="bx"><i>인 감</i></div></div>'
            f'<div class="dt">{yy}년 &nbsp; {mm}월 &nbsp; {dd}일</div>'
            f'<div class="to2">{FORM_TO} 귀하</div>')


# ================================================================== 01 입찰 참가 신청서 [별지서식 제1호]
def f01():
    m = D.MANAGER
    body = f"""<div class="form"><div class="no">[별지서식 제1호]</div><h1>입찰 참가 신청서</h1>
<table class="ft">
<tr><th style="width:15%">입 &nbsp;찰 &nbsp;명</th><td colspan="4">롯데캐슬 나리벡시티 주관사 선정 입찰 공고</td></tr>
<tr><th rowspan="4">신<br>청<br>인</th><th style="width:16%">회 사 명</th><td>{D.COMPANY}</td><th style="width:14%">대표자명</th><td>{D.CEO}</td></tr>
<tr><th>사업자등록번호</th><td>{D.BIZ_NO}</td><th>전화번호</th><td>{D.TEL}</td></tr>
<tr><th>법인등록번호</th><td colspan="3">{D.CORP_NO}</td></tr>
<tr><th>본사주소</th><td colspan="3">{D.ADDRESS}</td></tr>
<tr><th>(입찰)<br>대리인</th><td colspan="4">본 입찰에 관한 일체의 권한을 다음의 자에게 위임합니다.<br>
<span style="display:inline-block;margin-left:150pt;line-height:2">직 위 : {m[1]}<br>성 명 : {m[0]} <span style="margin-left:40pt">(서명)</span></span></td></tr>
</table>
<p class="tx">당사는 롯데캐슬 나리벡시티 입주예정자협의회가 공고한 입주박람회 주관사 선정 입찰에 참가하고자 귀 입주예정자협의회에서 규정한 입찰 공고사항을 모두 수락하며, 주관사로 선정될 경우 관련 조건 및 지시사항을 성실히 이행할 것을 확약하며 입찰참가를 신청합니다.</p>
{form_tail([("회사명", D.COMPANY), ("대표자", "대표이사 " + D.CEO)])}</div>"""
    return doc("01 입찰참가 신청서", [body])


# ================================================================== 10 확약 및 이행 서약서 [별지서식 제2호] — 원문 그대로(본부장 10-23: 6항 · 3항 원문 날인, 범위는 질의 메일로)
def f10():
    items = [
        "당사는 롯데캐슬 나리벡시티 입주예정자협의회의 주관사 선정 공고문에 명시된 모든 내용을 충분히 숙지하고 이해하였으며, 주관사 선정 및 입찰 절차와 그 결과에 대하여 일체의 이의를 제기하지 않을 것을 확약합니다.",
        "당사는 귀 입주예정자협의회에서 공고한 입찰 참가자격 및 제반 조건을 충분히 숙지하고 확인하였습니다, 이에 입찰 관련 제출 서류 일체를 허위 사실 없이 제출할 것이며, 귀 입주예정자협의회에서 추가 자료를 요청할 경우에도 성실히 제줄할 것을 확약합니다.",
        "롯데캐슬 나리벡시티 입주예정자협의회와 협약한 계약 일체에 관하여 하청 및 재수임 하지 않을 것을 확약합니다.",
        "당사는 주관사 선정 절차와 관련하여 제출한 서류에 포함된 개인정보를 귀 입주예정자협의회가 주관사 선정 및 관련 업무 수행을 목적으로 수집·이용하고, 필요한 범위 내에서 제3자에게 제공하는 것에 동의합니다. 또한, 제출한 입찰 관련 서류 및 제안설명회(PT) 동영상 촬영본을 입주예정자들의 주관사 선정 온라인 투표와 평가를 위하여 공식 카페에 일정 기간 게시하고, 정회원들이 이를 열람하는 것에 동의합니다.",
        "당사는 본 확약서 및 이행각서에 명시된 모든 사항을 상호 신뢰와 신의성실의 원칙에 따라 성실히 이행할 것을 확약합니다. 이를 위반할 경우, 귀 롯데캐슬 나리벡시티 입주예정자협의회가 관계 법령 및 협약 조건에 따라 시행하는 협약의 해지·해제·취소 등 제반 조치를 수용하며, 당사의 귀책사유로 인한 정당한 조치에 대하여 손해배상 청구 또는 민·형사상 이의를 제기하지 않을 것을 서약합니다.",
        "당사는 롯데캐슬 나리벡시티 입주박람회 주관사 선정 입찰에서 최종 선정되지 않을 경우, 귀 롯데캐슬 나리벡시티 입주예정자를 대상으로 별도의 입주박람회, 공동구매, 입주 관련 판촉행사 등을 직접 또는 제3자를 통하여 주관·주최·개최하지 않을 것을 서약합니다.",
    ]
    body = f"""<div class="form" style="font-size:10.6pt;line-height:1.72"><div class="no">[별지서식 제2호]</div><h1 style="margin:8pt 0 10pt">확약 및 이행 서약서</h1>
<p class="tx" style="margin-top:0">롯데캐슬 나리벡시티 주관사 선정의 건에 참여하는 당사는 아래 각호의 내용을 확약하고 이행할 것을 서약합니다.</p>
<ol>{"".join(f"<li>{i}. {x}</li>" for i, x in enumerate(items, 1))}</ol>
{form_tail([("회사명", D.COMPANY), ("대표자", "대표이사 " + D.CEO), ("주 &nbsp;소", D.ADDRESS)]).replace('class="sgx"', 'class="sgx" style="margin-top:12pt"').replace('class="dt"', 'class="dt" style="margin-top:12pt"').replace('class="to2"', 'class="to2" style="margin-top:16pt"')}</div>"""
    return doc("10 확약 및 이행 서약서", [body])


# ================================================================== 11 하자 보수 이행각서 [별지서식 제3호]
def f11():
    secs = [("1. 하자보수 및 사후관리 의무", "당사는 주관하는 입주박람회 및 공동구매 행사에 참여한 업체가 공급·시공·설치한 공사 및 물품에 대하여 하자보증기간 내 하자가 발생할 경우, 해당 참여업체가 신속하고 성실하게 하자보수 또는 원상복구를 이행하도록 관리·감독할 것을 확약합니다."),
            ("2. 하자보수 미이행에 따른 책임", "당사는 참여업체가 정당한 사유 없이 하자보수를 지연하거나 이행하지 않을 경우, 해당 업체에 즉시 시정조치를 요구하고, 필요한 경우 주관사로서 하자보수가 정상적으로 이행될 수 있도록 필요한 조치를 취할 것을 확약합니다."),
            ("3. 손해배상 및 비용 부담", "당사는 하자보수의 지연 또는 미이행으로 입주예정자에게 손해가 발생한 경우, 귀 입주예정자협의회의 정당한 요청에 성실히 응하고, 당사 또는 참여업체의 귀책사유와 계약상 책임 범위에 따라 하자보수, 원상복구 및 손해배상 등 필요한 조치를 이행할 것을 확약합니다."),
            ("4. 이행 책임 및 협조 의무", "당사는 참여업체와의 계약 및 관리 과정에서 하자보수에 관한 책임과 의무를 명확히 하고, 참여업체의 폐업, 연락 두절, 하자보수 거부 등으로 입주예정자의 피해가 발생하지 않도록 계약(협약)에서 정한 사후관리 및 하자보수 이행 의무를 성실히 준수할 것을 확약합니다.")]
    body = f"""<div class="form" style="font-size:10.6pt;line-height:1.72"><div class="no">[별지서식 제3호]</div><h1 style="margin:8pt 0 10pt">하자 보수 이행각서</h1>
<p class="tx" style="margin-top:0">당사는 롯데캐슬 나리벡시티 입주예정자협의회에서 선정한 공식 입주박람회 및 공동구매 행사 주관사로서, 행사 운영과 관련하여 발생하는 사후관리 및 하자보수에 대하여 계약(협약) 조건과 관련 규정을 철저히 준수하고, 다음 사항을 성실히 이행할 것을 확약합니다.</p>
{"".join(f'<p style="margin-top:9pt;font-weight:700">{a}</p><p class="tx" style="margin-top:2pt">{b}</p>' for a, b in secs)}
{form_tail([("주관사명", D.COMPANY), ("대표자명", "대표이사 " + D.CEO), ("전화번호", D.TEL), ("본사주소", D.ADDRESS)]).replace('class="sgx"', 'class="sgx" style="margin-top:12pt"').replace('class="dt"', 'class="dt" style="margin-top:12pt"').replace('class="to2"', 'class="to2" style="margin-top:16pt"')}</div>"""
    return doc("11 하자 보수 이행각서", [body])


# ================================================================== 12 비밀유지 서약서 [별지서식 제4호]
def f12():
    ps = ["당사는 귀 롯데캐슬 나리벡시티 입주예정자협의회에서 실시하는 「입주박람회 주관사 선정 입찰공고」에 참가함에 있어, 입찰 및 주관사 선정 과정에서 취득하거나 제공받은 일체의 정보(입주예정자 개인정보, 협의회 내부 운영정보, 타 업체의 제안 내용 및 입찰 관련 자료 등)에 대하여 철저히 비밀을 유지할 것을 서약합니다.",
          "또한, 귀 협의회의 사전 서면 동의 없이 해당 정보를 제3자에게 제공·누설·유출하거나 입찰 참가 목적 외의 용도로 사용하지 않을 것이며, 본 비밀유지 의무는 입찰 종료 및 주관사 선정 여부와 관계없이 지속적으로 준수할 것을 확약합니다.",
          "이를 위반할 경우 귀 협의회가 관련 법령 및 입찰 조건에 따라 시행하는 입찰 참가자격 박탈, 향후 입찰 참가 제한 등 정당한 제재 조치를 수용하고, 당사의 귀책사유로 인하여 발생한 손해에 대한 정당한 배상 책임을 부담할 것을 확약하며, 이에 본 서약서를 제출합니다."]
    body = f"""<div class="form"><div class="no">[별지서식 제4호]</div><h1>비밀유지 서약서</h1>
{"".join(f'<p class="tx">{x}</p>' for x in ps)}
{form_tail([("회사명", D.COMPANY), ("대표자", "대표이사 " + D.CEO), ("연락처", D.TEL), ("주 &nbsp;소", D.ADDRESS)]).replace('class="sgx"', 'class="sgx" style="margin-top:30pt"')}</div>"""
    return doc("12 비밀유지 서약서", [body])


# ================================================================== 13 청렴계약 이행준수 서약서 [별지서식 제5호]
def f13():
    items = ["당사는 타 업체와 사전 협의·담합하거나 특정 업체의 선정을 유도하는 등 공정한 경쟁을 저해하는 일체의 행위를 하지 않겠습니다.",
             "당사는 타 업체에 대한 허위사실 유포, 비방, 흑색선전, 허위·과장 광고 및 정당한 입찰 업무를 방해하는 행위를 하지 않겠습니다.",
             "당사는 입주예정자협의회 관계자 및 선정위원에게 금품·향응 등 부당한 이익을 제공하지 않으며, 하도급업체 및 공동구매 참여업체에 부당한 금품·리베이트를 요구하거나 불공정한 거래를 강요하지 않겠습니다.",
             "당사는 입찰, 계약 체결, 행사 운영 및 사후관리 전 과정에서 협의회의 정당한 자료 제출, 서류 검토, 현장 확인 등의 요청에 적극 협조하고, 계약상 의무를 성실히 이행하겠습니다.",
             "당사는 본 서약사항을 위반하거나 부정행위가 확인될 경우, 입찰 참가자격 박탈, 주관사 선정 취소, 계약 해제·해지 및 향후 입찰 참가 제한 등 협의회의 정당한 조치를 수용하며, 당사의 귀책사유로 발생한 손해에 대하여 관련 법령 및 계약에 따른 배상 책임을 부담하겠습니다."]
    body = f"""<div class="form" style="font-size:10.6pt;line-height:1.72"><div class="no">[별지서식 제5호]</div><h1 style="margin:8pt 0 10pt">청렴계약 이행준수 서약서</h1>
<p class="tx" style="margin-top:0">당사는 롯데캐슬 나리벡시티 입주예정자협의회에서 실시하는「입주박람회 주관사 선정 입찰」에 참가함에 있어, 입찰부터 계약 체결 및 행사 운영·사후관리까지 전 과정에서 공정하고 투명한 경쟁질서를 준수하며, 다음 사항을 성실히 이행할 것을 서약합니다.</p>
<ol>{"".join(f"<li>{i}. {x}</li>" for i, x in enumerate(items, 1))}</ol>
<p class="tx">본 서약은 상호 신뢰와 신의성실의 원칙에 따른 약속으로서 반드시 준수할 것이며, 주관사로 최종 선정될 경우 본 서약사항을 계약(협약) 조건에 포함하여 성실히 이행할 것을 확약합니다.</p>
{form_tail([("회사명", D.COMPANY), ("대표자", "대표이사 " + D.CEO), ("연락처", D.TEL), ("주 &nbsp;소", D.ADDRESS)]).replace('class="sgx"', 'class="sgx" style="margin-top:10pt"').replace('class="dt"', 'class="dt" style="margin-top:10pt"').replace('class="to2"', 'class="to2" style="margin-top:14pt"')}</div>"""
    return doc("13 청렴계약 이행준수 서약서", [body])


# ================================================================== 03 실적 증명서 + 증빙 안내
def _expo(nm):
    sch, plc = D.EXPO_VENUE.get(nm) or (None, None)
    assert sch and plc, ("박람회 일정 · 장소 미확인", nm)
    return e(sch).replace("\n", "<br>"), e(plc)


def doc03_form():
    rs = sorted(D.RECENT3_500, key=lambda r: r[0])
    rows = "".join(f'<tr><td>{e(nm)} <span style="color:#555">({m})</span></td><td class="c">{n:,}</td><td class="c" style="font-size:8.6pt">{_expo(nm)[0]}</td><td class="c">{_expo(nm)[1]}</td></tr>'
                   for m, nm, n, j in rs)
    tot = sum(r[2] for r in rs)
    body = f"""<style>.b2 th,.b2 td{{padding:1.6pt 5pt!important;font-size:8.8pt!important;line-height:1.28!important}}</style>
{head("제출서류 03", "최근 3년간 입주박람회 주관 실적 증명서")}
<table class="ft r2 b2" style="margin-top:8pt;width:100%;border-collapse:collapse"><thead><tr><th>아파트명 (입주 연월)</th><th style="width:10%">세대수</th><th style="width:34%">박람회 일정(입주박람회 · 공동구매)</th><th style="width:20%">행사 장소</th></tr></thead>
<tbody>{rows}<tr><th>합계 {len(rs)}개 단지 · 모두 당사 주관</th><th>{tot:,}</th><th colspan="2"></th></tr></tbody></table>
<div class="note">※ 공고 7항 03 ‘최근 3년간 실적 증명서’ · 공고일({NOTICE_DAY}) 기준 최근 3년 · 500세대 이상 공동주택 · 입주 연월 순 · 단지명 · 세대수는 당사 실적 목록 기준 · 증빙은 다음 쪽 ‘실적 증빙 안내’와 별첨 1 ~ 4.</div>
<p class="body" style="text-align:center;margin-top:6pt">위 실적은 사실과 다름이 없음을 증명합니다.</p>{sign().replace('class="sign"', 'class="sign" style="margin-top:4pt"').replace('class="to"', 'class="to" style="margin-top:22pt"')}"""
    return doc("03 최근 3년간 실적 증명서", [body])


EV_OF = {"e편한세상 송도 더퍼스트비치": "BEXCO 공식 행사일정(별첨 2 붙임 3)", "에코델타 대성베르힐": "입주자 모임 카페 주관사 공지(별첨 2 붙임 2)"}


def doc03_cover():
    r5 = D.RECENT3_500
    nice_names = {r[1] for r in D.RECENT3}
    big = {r[1] for r in D.RECENT3_OS}
    have = sorted(D.R500_HAVE, key=lambda k: D.R500_SIGNED[k])
    bx = {c[0]: k for k, c in enumerate(D.EXPO_CAPS, 1)}
    src = {c[0]: ("UECO 공식 행사일정" if "UECO" in c[2] else "CECO 공식 행사일정" if "CECO" in c[2] else "입주자 공식 카페 공지" if "카페" in c[2] else "BEXCO 공식 행사일정") for c in D.EXPO_CAPS}
    rows, n_ev = "", 0
    for i, (m, nm, n, j) in enumerate(sorted(r5, key=lambda r: r[0]), 1):
        if nm in big:
            ev_ = EV_OF.get(nm) or ("NICE 연혁(별첨 1) · 실적 확약서(별첨 2)" if nm in nice_names else None)
            assert ev_, nm
        elif nm in D.R500_HAVE:
            ev_ = f"주관사 협약서(별첨 3-{have.index(nm) + 1} · 협약 {D.R500_SIGNED[nm]})"
        elif nm in bx:
            ev_ = f"{src[nm]}(별첨 4-{bx[nm]})"
        else:
            ev_ = "요청 시 제출"
        if nm in bx and "별첨 4" not in ev_:
            ev_ += f" · {src[nm].split(' ')[0]}(별첨 4-{bx[nm]})"
        n_ev += 0 if ev_.startswith("요청") else 1
        rows += f'<tr class="jg"><td>{i}</td><td>{m}</td><td class="l">{e(nm)}</td><td class="r">{n:,}</td><td class="g">주관</td><td class="l">{ev_}</td></tr>'
    tot = sum(r[2] for r in r5)
    body = f"""{head("제출서류 03", "입주박람회 실적 및 공동구매 증빙 — 안내")}
<style>.t.ls.r9 td{{padding:.5pt 5pt;font-size:8.5pt;line-height:1.3}}.t.ls.r9 th{{font-size:8.8pt}}.pl li.sm{{font-size:8.6pt!important;margin:0!important}}h1{{font-size:16.5pt!important;margin-top:8pt!important}}.box{{margin-top:6pt!important;padding:5pt 10pt!important;font-size:9.3pt!important}}</style>
<table class="t ls r9" style="margin-top:6pt"><thead><tr><th style="width:5%">No</th><th style="width:10%">입주</th><th>단지명</th><th style="width:10%">세대수</th><th style="width:7%">구분</th><th style="width:36%">증빙</th></tr></thead>
<tbody>{rows}<tr class="sum"><td colspan="3">합계 {len(r5)}개 단지 (모두 주관)</td><td class="r">{tot:,}</td><td></td><td></td></tr></tbody></table>
<div class="box"><b>증빙 첨부 {n_ev}개 단지</b> · 나머지는 요청 시 계약서 · 정산 자료를 지체 없이 추가 제출합니다. 공동구매는 각 단지 입주박람회에서 함께 진행했습니다.</div>
<ol class="pl" style="margin-top:3pt"><li class="sm">별첨 1. NICE디앤비 기업신용평가보고서 ‘연혁’ 발췌 — 1쪽(보고서 전문은 제출서류 09)</li>
<li class="sm">별첨 2. 실적 확약서(1,000세대 이상 입주박람회 주관 10개 단지) — 붙임 1 · 2 단지 카페 주관사 공지 캡처(입주민 닉네임 가림) · 붙임 3 BEXCO 공식 행사일정 캡처</li>
<li class="sm">별첨 3. 주관사 협약서 — {" · ".join(f"3-{k + 1} {e(nm)}" for k, nm in enumerate(have))} — 협약일 순(상대방 대표자 성명 · 서명 가림)</li>
<li class="sm">별첨 4. {CAP_TITLE()}(주최/주관란에 엣지컴퍼니 기재) — {len(D.EXPO_CAPS)}곳</li></ol>
<p class="body" style="font-size:9.6pt;margin-top:4pt;line-height:1.6">위 실적은 사실과 다름이 없음을 확인하며, 허위로 확인될 경우 공고 6항 · 8항 5)에 따른 조치를 이의 없이 따르겠습니다.</p>{sign().replace('class="sign"', 'class="sign" style="margin-top:2pt"').replace('class="to"', 'class="to" style="margin-top:20pt"')}"""
    return doc("03 실적 증빙 안내", [body])


# ================================================================== 04 계약 취소 건 환불 규정(북수원 docs_bs.doc11 기준 · 나리벡 약속으로)
CANCEL_7 = "청소·줄눈, 탄성코트, 유리막코팅, 선반·잡물, 음식물처리기, 인덕션, 벽걸이TV, LED조명"
CANCEL_15 = "미세방충망, 인테리어, 단열필름, 시스템에어컨, 포장이사"
CUSTOM = "커튼·블라인드, 중문, 안전방충망, 맞춤가구"


def doc04():
    arts = [
        ("제1조 (목적)", None, f"이 규정은 {D.COMPANY}(이하 ‘주관사’)가 주관하는 {SITE} 입주박람회 및 공동구매(이하 ‘공동구매’)에서 입주예정자(이하 ‘계약자’)와 참여업체 사이에 체결되는 계약의 계약금·잔금 지급 조건과 취소·환불 기준을 정하여 계약자의 권리를 보호함을 목적으로 한다."),
        ("제2조 (적용 범위)", ["공동구매를 통해 체결된 모든 품목의 계약에 적용한다. 박람회 현장 계약과 온라인 박람회(폐쇄몰) 계약을 모두 포함한다.",
                           "참여업체는 이 규정을 계약서에 반영하고 계약 체결 전에 계약자에게 설명하여야 한다.",
                           "브랜드 본사 직영 품목(가전·가구 등), 렌탈·보험·통신, 사전점검 대행은 각 본사 계약 규정을 따르되, 그 내용을 계약 전에 서면으로 고지하여야 한다."]),
        ("제3조 (계약금)", [f"계약금은 계약 총액의 <b>{D.DEPOSIT_MAX}% 이하</b>로 한다(계약금 {D.DEPOSIT_MAX}% 상한제). 다만 세대 실측 후 제작하는 맞춤 제작 품목({CUSTOM} 등)은 예외로 하며, 적용 품목과 계약금은 업체 선정 때 입예협 승인을 받아 단가표 · 계약서에 미리 표시한다.",
                         "계약금과 잔금 모두 카드 결제 시 현금가와 <b>동일한 가격</b>을 적용하며, 현금 결제 시 현금영수증을 발행한다."]),
        ("제4조 (잔금 지급 조건)", ["잔금은 <b>시공·설치가 끝나고 계약자가 확인한 후</b> 지급한다. 제품만 납품하는 품목은 납품·설치 확인 후 지급한다.",
                             "시공 결과 확인 시 하자·미시공 부분이 있으면 계약자는 해당 부분의 보수가 끝난 후 잔금을 지급할 수 있다."]),
        ("제5조 (취소·환불 기준)", ["품목별 취소 가능 기한은 [별표]와 같다. 기한 안에 취소하면 납부한 금액 <b>전액</b>을 환불한다.",
                             f"맞춤 제작 품목({CUSTOM})은 출고 지시 전까지 참여업체와 협의하여 취소한다. 브랜드 가전·가구는 미제작·출고 지시 전에는 전액 취소·환불한다.",
                             "참여업체가 사전 해피콜을 이행하지 않은 경우, 계약자 미동의 주문제작 건을 포함한 <b>모든 품목은 당일 취소·환불</b>할 수 있다(공급사 귀책).",
                             "취소 기한이 지난 뒤의 취소는 실제 발생한 자재·제작 비용만 공제할 수 있으며, 참여업체는 공제 내역을 서면으로 제시하여야 한다. 주관사는 공제 내역의 적정성을 검토한다.",
                             "시공 지연, 계약과 다른 제품·시공(계약서상 ‘A’ 물품을 ‘B’ 물품으로 바꾼 경우 포함), 하자 미보수 등 참여업체 귀책으로 계약을 해지하는 경우에는 기한과 관계없이 납부 금액 전액을 환불한다."]),
        ("제6조 (취소 신청 및 환급)", ["취소는 참여업체 또는 주관사 콜센터 · 공식카페 신문고 · 카카오채널로 신청하며, 문자·메신저 등 기록이 남는 방법으로 한다.",
                                "환불금은 취소 확정일로부터 <b>3영업일 이내</b>에 지급하고, 카드 결제분은 같은 기한 안에 승인 취소한다.",
                                "주관사는 환불 완료 여부를 계약자에게 확인(해피콜)한다."]),
        ("제7조 (불이행 시 조치 및 주관사 책임)", ["참여업체가 취소·환불을 지연하거나 거부하면 계약자는 주관사 콜센터에 접수할 수 있다. 주관사는 사실을 확인한 뒤 계약자에게 피해 금액을 <b>먼저 보상</b>하고, 참여업체와는 계약 조항에 따라 정산한다(참여업체 특약이행각서 준용).",
                                      "불이행 업체에는 1단계 홍보정지, 2단계 총액 10% 배상, 3단계 자격박탈 및 입예협 승인을 받아 전 계약을 대체업체로 이관하는 패널티를 차례로 부과한다.",
                                      "참여업체가 도산하거나 연락이 끊긴 경우 계약자 동의를 받아 대체 업체로 사후관리를 이관하고, 무상 A/S 기간 안의 그 비용은 주관사가 부담한다.",
                                      "주관사의 보상 재원으로 하자 예치금 최대 1억원(엣지컴퍼니 자산으로 예치)과 계약이행 · 하자보증보험(보증기간 24개월, 금액 · 기산일은 협약 때 확정)을 둔다."]),
        ("제8조 (가격 보호 — 최저가 차액 10배 보상)", [f"공동구매 품목과 브랜드·모델명이 같은 새 제품이 계약 후 7일 이내에 인근({ST['local']}) 오프라인 매장에서 더 낮은 정상 판매가로 실제 판매된 사실이 구매 영수증(판매 매장 사업자 정보 · 모델명 · 금액 기재)으로 확인되고 주관사가 해당 매장에 판매 사실을 확인하면, 주관사는 차액의 10배를 보상하고 참여업체는 판매가를 조정한다(보상금은 주관사 부담 · 참여업체 부담을 늘리지 않음).",
                                             "보상액은 1건당 50만원(해당 품목 계약금액이 더 적으면 그 금액)을 넘지 않으며, 최대 금액은 협약 시 입예협과 협의해 조정할 수 있다(같은 세대 · 같은 품목에는 1회). 견적서 · 가격표 · 구두 안내 가격은 보상 근거가 되지 않는다.",
                                             "온라인·홈쇼핑 판매, 시공 품목, 카드 청구할인·사은품·결합할인, 전시·리퍼 상품, 법인 특판, 한정 수량 행사가는 비교 대상에서 제외한다.",
                                             "계약자는 주관사 콜센터에 접수하고, 주관사는 사실 확인 후 7일 이내에 보상한다."]),
        ("제9조 (고지)", None, "주관사는 이 규정을 박람회장 · 온라인 박람회에 게시하고, 입주예정자협의회 카페에는 입예협 승인 후 게시하며, 모든 공동구매 계약서에 첨부한다."),
        ("제10조 (효력)", None, "이 규정은 협약 체결일부터 협약 종료일까지 체결된 계약에 적용하며, 협약 종료 후에도 해당 계약의 이행·보증 기간 동안 효력을 가진다."),
    ]
    out_ = []
    for a in arts:
        if a[1]:
            out_.append(f'<div class="art"><h3>{a[0]}</h3><ol>' + "".join(f"<li>{'①②③④⑤⑥⑦⑧'[i]} {x}</li>" for i, x in enumerate(a[1])) + "</ol></div>")
        else:
            out_.append(f'<div class="art"><h3>{a[0]}</h3><p>{e(a[2])}</p></div>')
    table = f"""<h2>[별표] 품목별 취소 가능 기한 (시공일 기준)</h2>
<table class="t"><thead><tr><th style="width:24%">취소 가능 기한</th><th>품목</th></tr></thead><tbody>
<tr><td class="k" style="text-align:center">시공일 7일 전까지</td><td class="l">{CANCEL_7}</td></tr>
<tr><td class="k" style="text-align:center">시공일 15일 전까지</td><td class="l">{CANCEL_15}</td></tr>
<tr><td class="k" style="text-align:center">출고 지시 전까지</td><td class="l">맞춤 제작 품목({CUSTOM})은 업체와 협의 후 취소 · 브랜드 가전·가구(미제작 시)</td></tr>
<tr><td class="k" style="text-align:center">본사 규정 품목</td><td class="l">렌탈 · 보험 · 통신 · 사전점검 대행 · 브랜드 본사 직영 품목 - 각 본사 계약 규정(계약 전 서면 고지)</td></tr>
<tr><td class="k" style="text-align:center">당일 취소 가능</td><td class="l">사전 해피콜 미이행 시 모든 품목(공급사 귀책)</td></tr>
</tbody></table>
<p class="note">※ 품목 구성은 입주예정자협의회 수요조사 결과에 따라 확정되며, 추가 품목의 기한은 성격이 같은 품목의 기한을 따른다.</p>"""
    summary = (f'<div class="box"><b>핵심 요약</b> &nbsp; 계약금 {D.DEPOSIT_MAX}% 이하(맞춤 제작 품목 예외) · 현금·카드 동일가 · 잔금은 시공·설치 확인 후 · '
               "품목별 취소 기한 안 전액 환불 · 환불 3영업일 이내 · 업체 불이행 시 주관사 선보상 · 최저가 차액 10배(주관사 부담)</div>")
    return doc("04 계약 취소 건 환불 규정", [head("제출서류 04", "계약 취소 건 환불 규정") + summary + "".join(out_) + table + sign()])


# ================================================================== 09 기업신용평가서 — 표지 + NICE 전문(대표 외 임직원 생년월일 가림)
def doc09_cover(n_pages):
    body = f"""{head("제출서류 09", "기업신용평가서")}
<table class="t" style="margin-top:14pt"><tbody>
<tr><td class="k" style="width:22%">보고서</td><td class="l">NICE디앤비 CLIP 기업신용평가보고서(관리번호 11125949-202605-001) — <b>전문 {n_pages}쪽</b></td></tr>
<tr><td class="k">평가 대상</td><td class="l">{D.COMPANY} ({D.BIZ_NO})</td></tr>
<tr><td class="k">평가일 · 유효기간</td><td class="l">{D.NICE_DATE} · ~2027.06.18 — 재무제표 기준 연 1회 정기 평가의 가장 최근 평가(유효기간 안)</td></tr>
<tr><td class="k">결과</td><td class="l">신용등급 BB- · 현금흐름등급 A</td></tr>
<tr><td class="k">개인정보</td><td class="l">원본 13쪽 ‘경영진 현황’의 대표 외 임직원 2명 생년월일은 개인정보 보호를 위해 가렸습니다(그 밖의 내용은 원본 그대로).</td></tr>
</tbody></table>
<p class="note" style="margin-top:8pt">※ 보고서의 본사 주소는 본점 이전(2026.07.02 등기) 전 주소이고, 종업원 수와 경영진 현황은 평가 당시(2026.05) 기준입니다. 주관사업 총괄 본부장은 평가 이후 합류했습니다. 현재 본점 · 등기 사항은 제출서류 05 · 06, 현재 인원은 제출서류 08(4대보험 가입자 명부)과 같습니다.</p>
<p class="note">※ 실적 근거인 연혁(원본 9쪽)은 제출서류 03 별첨 1에도 발췌해 붙였습니다.</p>"""
    return doc("09 기업신용평가서", [body])


# ================================================================== 14 기타 제안 내용 확인 자료
def doc14_cover(n_sum):
    rows = [("①", "요약제안서", f"{n_sum}쪽 · 정회원 투표 · PT 기본 자료(제안서 02의 요약 · 숫자는 같음)"),
            ("②", "법인 통장 사본", "참가자격 3) — 사업자등록증과 같은 법인 명의 통장"),
            ("③", "국세 · 지방세 · 4대 보험 완납증명서(2026.10.14 발급)", "참가자격 6) ‘공고일 이전 완납을 증명’ — 공고일 이후 발급본은 제출서류 07 · 08"),
            ("④", "보증보험증권 발급 이력(서울보증)", "참가자격 12) · 13) — 광고대행 용역 계약보증보험증권(2026.09.07 발급) · 입주박람회 협약 이행보증 아님 · 이 협약 보증은 협약 후 입예협 피보험자로 보증기간 24개월 발급"),
            ("⑤", "세대 혜택 집행 계약서 사본(영주자이 시그니처)", "우대 17 — 주관사가 약속한 세대 혜택을 실제로 집행한 계약서(전 세대 도어록 지문형 763대) · 안내 1쪽 포함")]
    tb = "".join(f'<tr><td>{a}</td><td class="l"><b>{e(b)}</b></td><td class="l">{e(c)}</td></tr>' for a, b, c in rows)
    body = f"""{head("제출서류 14", "기타 제안 내용 확인에 필요한 자료")}
<table class="t" style="margin-top:12pt"><thead><tr><th style="width:6%">No</th><th style="width:34%">자료</th><th>확인 내용</th></tr></thead><tbody>{tb}</tbody></table>
<p class="note" style="margin-top:8pt">※ 개인정보 · 금융정보가 담긴 자료는 가림본입니다. 카페 게시(공고 9항 5)용 공개본이 따로 필요하시면 요청하신 날 보내 드리겠습니다.</p>"""
    return doc("14 기타 자료 목록", [body])


def doc14_bond():
    img = os.path.join(HERE, "assets_ins", "os_sgi_bond_masked.png")
    body = f"""{head("제출서류 14 · ④", "보증보험증권 발급 이력")}
<table class="t" style="margin-top:10pt"><tbody>
<tr><td class="k" style="width:22%">증권</td><td class="l">서울보증보험 계약보증보험증권 · 2026.09.07 발급 · 울주대리점</td></tr>
<tr><td class="k">주계약</td><td class="l">광고대행 용역(공공 발주) — <b>입주박람회 협약 이행보증이 아닙니다</b></td></tr>
<tr><td class="k">이 협약</td><td class="l">공고 참가자격 12) · 13) — 협약 후 입예협을 피보험자로 계약이행증권 · 하자보증보험증권을 보증기간 24개월로 발급 · 금액 · 기산일 · 보증 대상은 협약 때 확정</td></tr>
<tr><td class="k">가림</td><td class="l">상대방 · 보험료 · 증권번호 뒷자리 · 가입금액은 상대방 계약 정보라 가렸습니다(원본은 PT 때 열람 가능).</td></tr>
</tbody></table>
<div style="margin-top:10pt;text-align:center"><img src="{pathlib.Path(img).as_uri()}" style="max-width:100%;max-height:165mm;border:.6pt solid #C9CED6"></div>"""
    return doc("14 ④ 보증보험증권 발급 이력", [body])


def doc14_door():
    body = f"""{head("제출서류 14 · ⑤", "세대 혜택 집행 계약서 사본 — 안내")}
<table class="t" style="margin-top:14pt"><tbody>
<tr><td class="k" style="width:22%">무엇인가</td><td class="l">주관사가 약속한 세대 혜택을 <b>실제로 집행한 계약서 사본</b>입니다 — 영주자이 시그니처 <b>전 세대 디지털도어록을 지문형으로 사양 변경</b>했습니다.</td></tr>
<tr><td class="k">계약</td><td class="l">물품공급계약서 · 디지털도어록 사양 변경 계약(X120-F → X500-FH(s) · 지문 사양)</td></tr>
<tr><td class="k">현장 · 수량</td><td class="l">영주자이 시그니처 · 763대(전 세대)</td></tr>
<tr><td class="k">금액</td><td class="l">25,179,000원(공급가액 22,890,000원 + 부가세 2,289,000원)</td></tr>
<tr><td class="k">기간</td><td class="l">계약일 2026.07.09 · 공사 기간 2026.08.01 ~ 2026.10.31</td></tr>
<tr><td class="k">당사자</td><td class="l">갑(공급받은자) = {D.COMPANY} — 주관사가 직접 계약 · 을(공급자) = 도어록 공급사</td></tr>
<tr><td class="k">가림</td><td class="l">공급사 상호 · 대표자 · 주소와 대금 지급 · 특약 등 세부 조항은 상대방 영업 정보라 모자이크했습니다. 원본은 2차 PT 때 지참해 열람할 수 있습니다.</td></tr>
</tbody></table>
<p class="note" style="margin-top:8pt">※ {ST['short']} 세대 혜택(세대당 15만원 상당 × {D.FUND_HH}세대)도 입예협이 고른 항목을 주관사가 직접 구매 · 제공하고, 사용 내역을 공개합니다. 이 계약서는 그 방식을 다른 단지에서 실제로 지킨 사례입니다.</p>"""
    return doc("14 ⑤ 세대 혜택 집행 계약서 안내", [body])


# ================================================================== 00 제출서류 목록(참고)
def doc00(st):
    rows = "".join(f'<tr><td>{k}</td><td class="l">{e(nm)}</td><td class="l">{e(cond)}</td><td>{"✓" if st.get(k) else "조치 필요"}</td></tr>' for k, nm, cond in LIST)
    body = f"""{head("제출서류 목록", "제안자료 구성 (공고 7항 순서)")}
<table class="t" style="margin-top:12pt"><thead><tr><th style="width:7%">NO</th><th style="width:35%">제출서류</th><th>비고</th><th style="width:11%">상태</th></tr></thead><tbody>{rows}</tbody></table>
<p class="note" style="margin-top:8pt">※ 05 ~ 08은 공고일({NOTICE_DAY}) 이후 발급본입니다. 09는 재무제표 기준 연 1회 정기 평가의 최근 평가본입니다. 별지 1 ~ 5는 서식 원문 그대로 작성하고 법인인감을 날인했습니다. 개인정보는 가림본입니다.</p>"""
    return doc("00 제출서류 목록", [body])


LIST = [("01", "입찰참가 신청서", "별지서식 제1호 · 법인인감"), ("02", "입주박람회 입찰 제안서", "자유양식"),
        ("03", "입주박람회 실적 및 공동구매 증빙 자료", "최근 3년간 실적 증명서 · 증빙 안내 · 별첨 1 ~ 4"), ("04", "계약 취소 건 환불 규정", "자유양식 · 제1 ~ 10조 · 별표"),
        ("05", "사업자등록증 사본", "공고일 이후 발급본"), ("06", "법인등기부등본 · 법인인감증명서", "공고일 이후 발급본 · 인감증명서 주민번호 뒷자리 가림"),
        ("07", "국세 및 지방세 완납증명서", "공고일 이후 발급본"), ("08", "4대 보험 가입자 명부 및 완납증명서", "공고일 이후 발급본 · 명부 가림"),
        ("09", "기업신용평가서", "연 1회 정기 평가 · 유효기간 안 최근 평가본"), ("10", "확약 및 이행 서약서", "별지서식 제2호 · 법인인감"),
        ("11", "하자 보수 이행각서", "별지서식 제3호 · 법인인감"), ("12", "비밀유지 서약서", "별지서식 제4호 · 법인인감"),
        ("13", "청렴계약 이행 준수 서약서", "별지서식 제5호 · 법인인감"), ("14", "기타 제안 내용 확인에 필요한 자료", "선택 · 요약제안서 · 통장 사본 · 완납증명(공고일 이전) · 보증 이력 · 집행 계약서")]
NAMES = {"00": "00_제출서류_목록", "01": "01_입찰참가_신청서", "02": "02_입주박람회_입찰_제안서", "03": "03_입주박람회_실적_및_공동구매_증빙", "04": "04_계약취소_환불규정",
         "05": "05_사업자등록증", "06": "06_법인등기부등본_법인인감증명서", "07": "07_국세_지방세_완납증명서", "08": "08_4대보험_가입자명부_완납증명서",
         "09": "09_기업신용평가서", "10": "10_확약_및_이행_서약서", "11": "11_하자보수_이행각서", "12": "12_비밀유지_서약서",
         "13": "13_청렴계약_이행준수_서약서", "14": "14_기타_제안_확인자료"}
ORDER = list(NAMES)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    final = "--final" in sys.argv
    if not args:
        sys.exit(__doc__)
    seal = seal_image(args[0])
    for p in (P02, P14S, ROSTER, NICE_SRC, D.R500_DOC, f"{EV}/법인통장_사본.pdf", f"{SP}/yj_door/contract_use.pdf"):
        assert os.path.exists(p), ("없음", p)
    assert len(fitz.open(D.R500_DOC)) == 3, "협약서 3건"
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(SUBMIT, exist_ok=True)

    def stamped(p, n_expect=1):
        o, n = stamp(seal, p)
        assert n == n_expect, f"날인 자리 {n}곳(예상 {n_expect}): {p}"
        return o

    ok, why, res = {}, {}, {}
    # ---- 별지 1 ~ 5(01 · 10 ~ 13): 원문 서식 → 법인인감 실물 날인 스캔이 있으면 그 쪽, 없으면 날인 전(조치 필요)
    forms = [("01", f01), ("10", f10), ("11", f11), ("12", f12), ("13", f13)]
    plain = {k: fit(render(NAMES[k] + "_날인전", fn()), 1) for k, fn in forms}
    scan = fitz.open(SEAL_SCAN) if os.path.exists(SEAL_SCAN) else None
    if scan is not None:
        assert len(scan) == 5, f"법인인감 날인 스캔은 5쪽(별지 1 ~ 5 순)이어야 함: {SEAL_SCAN}"
    for i, (k, _fn) in enumerate(forms):
        if scan is not None:
            o = fitz.open()
            o.insert_pdf(scan, from_page=i, to_page=i)
            res[k] = out(NAMES[k] + ".pdf")
            o.save(res[k], garbage=GARBAGE, deflate=True)
            ok[k] = True
        else:
            res[k], ok[k], why[k] = plain[k], False, "법인인감 실물 날인 스캔 대기(작업/서식날인_출력용.pdf 출력 → 날인 → 스캔 5쪽)"
    # ---- 02 제안서(밝은 시안 원본)
    res["02"] = out(NAMES["02"] + ".pdf")
    shutil.copyfile(P02, res["02"])
    ok["02"] = True
    # ---- 03 실적 증빙
    a1 = stamped(annex_nice(NICE_SRC, out("03_3_별첨1_NICE연혁발췌.pdf")))
    _b4 = doc09_bexco()
    parts3 = [stamped(fit(render("03_1_실적증명서", doc03_form()), 1)), stamped(fit(render("03_2_실적증빙_안내", doc03_cover()), 1)), a1,
              stamped(fit(render("03_4_별첨2_실적확약서", doc09_hwakyak()), 4)), D.R500_DOC, fit(render("03_5_별첨4_행사일정", _b4[0]), _b4[1])]
    names3 = ["최근 3년간 실적 증명서", "실적 증빙 안내", "별첨 1 NICE 연혁 발췌", "별첨 2 실적 확약서 · 붙임 1 ~ 3", f"별첨 3 주관사 협약서 {len(D.R500_HAVE)}건", f"별첨 4 {CAP_TITLE()}"]
    toc, pg0 = [], 1
    for nm, p in zip(names3, parts3):
        toc.append([1, nm, pg0]); pg0 += len(fitz.open(p))
    res["03"] = merge(NAMES["03"], parts3, "03 입주박람회 실적 및 공동구매 증빙 자료", toc)
    ok["03"] = True
    # ---- 04 환불 규정
    res["04"] = stamped(fit(render(NAMES["04"], doc04()), 2, 3))
    ok["04"] = True
    # ---- 05 ~ 08 공고일 이후 발급본 · 09 NICE = 연 1회 정기 평가 → 유효기간 안 최근 평가본
    E = {n: ev(n) for _, n, _ in REISSUE}
    for k in ("05", "06", "07", "08"):
        miss = [lab for kk, n, lab in REISSUE if kk == k and not E[n][1]]
        ok[k] = not miss
        if miss:
            why[k] = "공고일(10.19) 이후 재발급 대기: " + " · ".join(miss) + f" → {EVN}/ 에 같은 이름으로"
    biz = fitz.open(E["사업자등록증.pdf"][0])
    for pg_ in biz:
        for a in list(pg_.annots()):
            pg_.delete_annot(a)
    assert "전시,박람회및행사대행업" in "".join(p.get_text() for p in biz).replace(" ", ""), "사업자등록증 종목(자격 2) 확인 실패"
    res["05"] = merge(NAMES["05"], [biz], "05 사업자등록증")
    res["06"] = merge(NAMES["06"], [E["법인등기부등본.pdf"][0], E["법인인감증명서.pdf"][0]], "06 법인등기부등본 · 법인인감증명서")
    res["07"] = merge(NAMES["07"], [E["국세_납세증명서.pdf"][0], E["지방세_납세증명서.pdf"][0]], "07 국세 · 지방세 완납증명서")
    assert len(fitz.open(ROSTER)) == 2, "4대보험 가입자 명부(2026.10.23 · 가림본) 2쪽"
    res["08"] = merge(NAMES["08"], [ROSTER, E["4대보험_완납증명서.pdf"][0], E["고용산재_완납증명서.pdf"][0]], "08 4대 보험 가입자 명부 · 완납증명서",
                      [[1, "4대보험 사업장 가입자 명부(2026.10.23 · 가림)", 1], [1, "4대 보험 완납증명서", 3]])
    nice9 = nice_full(NICE_SRC)
    ok["09"] = True
    res["09"] = merge(NAMES["09"], [fit(render("09_1_표지", doc09_cover(len(fitz.open(nice9)))), 1), nice9],
                      "09 기업신용평가서(NICE 전문)", [[1, "표지", 1], [1, "NICE디앤비 CLIP 기업신용평가보고서 전문", 2]])
    # ---- 14 기타
    n_sum = len(fitz.open(P14S))
    p14 = [fit(render("14_0_목록", doc14_cover(n_sum)), 1), P14S, f"{EV}/법인통장_사본.pdf",
           f"{EV}/국세_납세증명서.pdf", f"{EV}/지방세_납세증명서.pdf", f"{EV}/4대보험_완납증명서.pdf", f"{EV}/고용산재_완납증명서.pdf",
           fit(render("14_4_보증이력", doc14_bond()), 1), fit(render("14_5_집행계약서_안내", doc14_door()), 1), f"{SP}/yj_door/contract_use.pdf"]
    toc, pg0 = [], 1
    for nm, p in zip(["목록", "① 요약제안서", "② 법인 통장 사본", "③ 국세 완납(10.14)", "③ 지방세 완납(10.14)", "③ 4대보험 완납(10.14)", "③ 고용 · 산재 완납(10.14)",
                      "④ 보증보험증권 발급 이력", "⑤ 세대 혜택 집행 계약서 안내", "⑤ 계약서 사본"], p14):
        toc.append([1, nm, pg0]); pg0 += len(fitz.open(p))
    res["14"] = merge(NAMES["14"], p14, "14 기타 제안 내용 확인에 필요한 자료", toc)
    ok["14"] = True
    # ---- 00 목록
    res["00"] = fit(render(NAMES["00"], doc00(ok)), 1)
    ok["00"] = all(ok.get(k) for k in ORDER if k != "00")

    # ---- 서식 날인 출력본: 별지 1 ~ 5 원문(날인 전) 5쪽 — 출력 → 법인인감 실물 날인 → 스캔(같은 순서)
    pr = fitz.open()
    for k, _fn in forms:
        pr.insert_pdf(fitz.open(plain[k]))
    pr.set_metadata({"title": "별지 1 ~ 5 법인인감 날인 출력용", "author": D.COMPANY})
    pr.save(out("서식날인_출력용.pdf"), garbage=GARBAGE, deflate=True)
    print(f"[출력용] {PFX}서식날인_출력용.pdf {len(pr)}쪽 — 별지 1 · 2 · 3 · 4 · 5 순 · '인감' 칸에 법인인감 실물 날인 · 별지 1 대리인 칸은 본부장 서명")

    # ---- 제출본/ · ZIP
    for f in os.listdir(SUBMIT):
        if f.endswith(".pdf"):
            os.remove(os.path.join(SUBMIT, f))
    lines = [f"[제출 현황 · 내부용 — 첨부 금지] {SITE} · 접수 {D.SUBMIT_TO} · 제목 {D.MAIL_TITLE} · 자료 {D.FILE_TITLE} · 마감 {D.DEADLINE}", ""]
    attach = []
    for k in ORDER:
        v = res[k]
        msg = f"{k} {'제출 가능' if ok[k] else '조치 필요'}  {NAMES[k]}.pdf  {len(fitz.open(v))}p  {os.path.getsize(v) / 1e6:.2f}MB" + ("" if ok[k] else f"  ← {why.get(k, '')}")
        print(msg)
        lines.append(msg)
        if ok[k]:
            dst = os.path.join(SUBMIT, NAMES[k] + ".pdf")
            shutil.copyfile(v, dst)
            attach.append(dst)
    todo_n = [k for k in ORDER if not ok[k]]
    if os.path.exists(ZIP):
        os.remove(ZIP)
    if not todo_n:
        with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
            for p in attach:
                z.write(p, f"{D.FILE_TITLE}/{os.path.basename(p)}")
        lines += ["", f"ZIP: {ZIP}  {os.path.getsize(ZIP) / 1e6:.1f}MB (제출본 {len(attach)}개)"]
    else:
        lines += ["", f"ZIP 만들지 않음 — 조치 필요 {len(todo_n)}건: {' · '.join(todo_n)}"]
        if final:
            pathlib.Path(WORK, "제출현황.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
            sys.exit("--final: 조치 필요 서류가 남아 ZIP을 만들지 않음")
    pathlib.Path(WORK, "제출현황.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(lines[-1])


if __name__ == "__main__":
    main()
