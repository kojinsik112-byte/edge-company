# -*- coding: utf-8 -*-
"""e편한세상 분당 퍼스트빌리지 — 입주박람회 주관사 제안서 빌더 (입예협 공고 제2026-1호 7항 제출서류 2 '입주박람회 주관사 제안서').

지웰 엘리움 양주 덕계역 빌더(../지웰엘리움양주덕계역/build_gwell.py)를 복제·개조했다. 기본틀(요약제안서 v5, ../요약제안서/build.py)은
건드리지 않고 불러와서 고친다.
- 표지: e편한세상 분당 퍼스트빌리지 입주박람회 주관사 제안서 (조감도 bd_cover.jpg — 없으면 남색 자리표시)
- 01장(재배치 후 07장) = 분당 맞춤 제안: 공고 8항 필수 9항목 ↔ 쪽 대응표 · 단지 이해 · 신혼희망타운 품목 · 유상옵션 겹침 확인 ·
  시중가·온라인 최저가 검수 · 혜택·가격 비교 한 장 · 협의회 지원 · 정당계약일 부스 · 전담 PM · 업무 11 · 자격 10 · 제한 10 · 유의사항
- 01 회사소개에 연혁 · 대표자·핵심 운영인력 장 추가(공고 8항 1 · 2)
- 공고 7항에 요약본 · 회사소개서가 없어 제안서(02)만 출력한다.
- 사진·발췌 장은 동탄 폴더 assets_ins / assets_full 을 공유(심볼릭 링크, 깃 제외). 본부장 제공 예정 사진(bd_*)은 파일이 생기면 자동 반영.

사용: python3 build_bd.py [--no-pdf] [--final]
"""
import html as _h
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", "요약제안서"))
sys.path[:0] = [BASE, HERE]
import build as B  # noqa: E402  (기본틀 — import 시 PAGES가 채워짐)
import data as D  # noqa: E402

NAME = "엣지컴퍼니_분당퍼스트빌리지_02_입주박람회_주관사_제안서"
FULL_DIR = os.path.join(HERE, "assets_full")  # 통합제안서 기본틀 발췌 페이지(JPEG, 깃 제외)
FULL_DPI = 170
FULL_CLIP = (196, 34, 850, 600)  # 원본 페이지에서 본문 패널만(좌측 메뉴·상단 띠 제외)
FULL_CLIP_OVR = {
    8: (174, 34, 850, 600),   # 4대보험 액자가 x≈178에서 시작 → 왼쪽까지 포함
    27: (196, 34, 836, 600),  # 사송신도시: 원본 오른쪽 흰 여백 잘라냄
    35: (196, 34, 846, 600),  # 감사패: 오른쪽 끝 흰 선 잘라냄
}
B.OUT_HTML = os.path.join(HERE, NAME + ".html")
B.OUT_PDF = os.path.join(HERE, NAME + ".pdf")
INS = "\x00INS"  # 발췌 페이지 표식(render_std 래퍼가 가로챔)
t = B.t


def sub(s, old, new):
    """기본틀 문구가 바뀌었으면 조용히 넘어가지 않도록 확인 후 교체."""
    assert old in s, f"기본틀에서 문구를 찾지 못함: {old[:40]}"
    return s.replace(old, new)


def term(s):
    """분당 퍼스트빌리지는 입주예정자협의회(입예협) — 기본틀 용어 그대로."""
    return s


# ============================================================ 표 스타일(신규 장)
B.CSS += r"""
.tbl{width:100%;border-collapse:collapse}
.tbl th{font-size:12.5px;font-weight:700;letter-spacing:.24em;color:var(--gold2);text-align:left;
  padding:0 14px 9px;border-bottom:1.5px solid rgba(200,168,106,.55)}
.tbl td{font-size:17px;padding:8.5px 14px;border-bottom:1px dashed rgba(255,255,255,.14);color:var(--sub);line-height:1.42;vertical-align:middle}
.tbl tr:last-child td{border-bottom:0}
.tbl td.k{color:var(--ink);font-weight:700;font-size:17.5px}
.tbl td.n{color:var(--gold);font-weight:800;font-size:15px;width:44px}
.tbl td.g{color:var(--gold);font-weight:700;font-size:14.5px;letter-spacing:.04em;border-right:1px solid rgba(255,255,255,.12)}
.tbl tr.own td{background:rgba(235,203,143,.07)}
.tbl em{font-weight:700}
.tbl.sm td{font-size:15px;padding:6px 14px}
.tbl.sm td.k{font-size:15.5px}
.tjs td:last-child{white-space:nowrap}.tjs td.k{min-width:150px}
.lg .tile{padding:20px 24px}
.lg .tile .nm{font-size:23px}
.lg .tile .ds{font-size:17.5px;line-height:1.55;margin-top:8px}
.ins{flex:1;min-height:0;display:flex;align-items:center;justify-content:center}
.ins img{max-width:100%;max-height:100%;border-radius:14px;box-shadow:0 16px 44px rgba(0,0,0,.5)}
.ins-h{display:flex;justify-content:space-between;align-items:flex-end;margin:12px 0 14px}
.ins-h h1{margin:0}
.ins-h span{font-size:12.5px;letter-spacing:.28em;color:var(--gold2);font-weight:700;white-space:nowrap;padding-bottom:8px}
.cv3{padding:52px 72px 0;background:radial-gradient(120% 60% at 50% 88%,rgba(214,170,98,.20) 0%,rgba(13,30,51,0) 60%),var(--bg)}
.cv3 .mid{flex:1;align-items:center;text-align:center;justify-content:center;padding-bottom:6px}
.cv3 .pill{align-self:center}
.cv3 h1{font-size:50px;line-height:1.28;margin-top:22px}
.orn{display:flex;align-items:center;justify-content:center;gap:14px;margin:24px 0 18px;width:100%}
.orn i{flex:0 0 190px;height:1.5px;background:linear-gradient(90deg,rgba(200,168,106,0),var(--gold2))}
.orn i:last-child{background:linear-gradient(90deg,var(--gold2),rgba(200,168,106,0))}
.orn b{width:9px;height:9px;transform:rotate(45deg);border:1.5px solid var(--gold2);background:rgba(200,168,106,.25)}
.cv3 .tag2{font-size:19px;line-height:1.65;margin-top:0}
.pano{position:relative;height:228px;margin:0 -72px}
.pano img{position:absolute;left:0;right:0;bottom:0;width:100%;height:auto;display:block}
.pano:after{content:'';position:absolute;left:0;right:0;bottom:0;height:1.5px;
  background:linear-gradient(90deg,rgba(200,168,106,0),rgba(230,201,142,.85) 50%,rgba(200,168,106,0))}
.pano .credit{position:absolute;right:76px;bottom:8px;font-size:10.5px;color:rgba(255,255,255,.5);z-index:1}
.cv3 .sub2{justify-content:center;border-top:0;padding:16px 0 14px}
.cv5>.top,.cv5>.mid,.cv5>.sub2,.cv5>.bt{position:relative;z-index:1;width:57%}
.cv5 .mid{justify-content:center;padding-top:22px}
.cv5 .bt{height:40px;margin-bottom:38px}
.cv5 .top .who{display:none}
.cv5 h1{font-size:27px;line-height:1.32;margin-top:14px}
.cv5 h1 em{display:block}
.cvlx{position:absolute;z-index:0;top:0;right:0;bottom:0;width:50%}
.cvlx img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:52% 50%}
.cvlx .fd{position:absolute;inset:0;background:linear-gradient(90deg,var(--bg) 0%,rgba(13,30,51,.75) 18%,rgba(13,30,51,.15) 45%,rgba(13,30,51,0) 70%),
  linear-gradient(0deg,rgba(13,30,51,.55) 0%,rgba(13,30,51,0) 25%)}
.cvlx .cap{position:absolute;right:28px;bottom:30px;font-size:10.5px;color:rgba(255,255,255,.6)}
.hero3{display:grid;grid-template-columns:1fr 1fr;margin-top:24px;border-top:1px solid rgba(200,168,106,.5)}
.hero3>div{padding:16px 0 16px 22px;border-left:1px solid rgba(200,168,106,.28);border-bottom:1px solid rgba(200,168,106,.5)}
.hero3>div.h1x{grid-column:1/-1;border-left:0;padding-left:0}
.hero3>div:nth-child(2){border-left:0;padding-left:0}
.hero3 i{font-style:normal;font-size:12px;letter-spacing:.2em;color:var(--gold2);font-weight:700}
.hero3 b{display:block;font-size:52px;font-weight:800;color:var(--gold);line-height:1;margin-top:8px;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.hero3 .h1x b{font-size:84px}
.hero3 b small{font-size:22px;margin-left:4px;font-weight:700}
.hero3 b small.mx{font-size:17px;margin:0 7px 0 0;color:var(--gold2)}
.hero3 p{font-size:13.5px;color:var(--sub);margin-top:9px;line-height:1.5}
.hero3 p em{color:var(--ink);font-weight:800}
.lxband{margin-top:18px;display:flex;align-items:center;gap:16px;border:1px solid rgba(235,203,143,.55);border-radius:10px;padding:10px 18px;
  background:linear-gradient(90deg,rgba(235,203,143,.16),rgba(235,203,143,.02))}
.lxband b{font-size:15.5px;color:var(--gold);white-space:nowrap;letter-spacing:.04em}
.lxband span{font-size:13.5px;color:var(--ink);line-height:1.45}
.cv5 .sub2{gap:40px}
.cv5 .sub2 b{font-size:15px}
.page.hero{padding:40px 48px 0}
.page.hero>.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 70%}
.page.hero>.veil{position:absolute;inset:0;background:linear-gradient(180deg,rgba(8,18,32,.78) 0%,rgba(8,18,32,0) 16%),linear-gradient(90deg,rgba(8,18,32,.96) 0%,rgba(8,18,32,.86) 34%,rgba(8,18,32,.25) 64%,rgba(8,18,32,.05) 100%),
  linear-gradient(0deg,rgba(8,18,32,.92) 0%,rgba(8,18,32,0) 38%)}
.page.hero>.hd,.page.hero>.ct,.page.hero>.kp,.page.hero>.ft{position:relative;z-index:1}
.page.hero .ct{flex:1}
.page.hero .hin{position:absolute;z-index:1;left:48px;top:96px;width:560px}
.page.hero .hcap{position:absolute;z-index:1;right:52px;bottom:238px;font-size:10.5px;color:rgba(255,255,255,.62)}
.hin .kick{font-size:13px;font-weight:700;letter-spacing:.32em;color:var(--gold2)}
.hin h2{font-size:52px;font-weight:800;line-height:1.22;margin-top:14px;letter-spacing:-.01em}
.hin .bar{width:150px;height:2px;background:var(--gold2);margin:22px 0 18px}
.hin p{font-size:18px;color:var(--ink);line-height:1.6;opacity:.92}
.page.hero .pil{position:absolute;z-index:1;left:48px;right:48px;bottom:126px;display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.pil>div{border:1px solid rgba(235,203,143,.45);border-radius:12px;padding:14px 16px;background:rgba(8,18,32,.72);backdrop-filter:blur(2px)}
.pil i{font-style:normal;font-size:12px;letter-spacing:.24em;color:var(--gold2);font-weight:700}
.pil b{display:block;font-size:19px;margin-top:4px}
.pil span{display:block;font-size:13.5px;color:var(--sub);line-height:1.45;margin-top:4px}
.cv4>*{position:relative;z-index:1}
.cv4>.cvart{position:absolute;z-index:0;right:0;bottom:128px;width:62%;height:400px}
.cvart img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 85%}
.cvart .credit{position:absolute;right:72px;bottom:8px;font-size:10.5px;color:rgba(255,255,255,.55)}
.cv4>.cvart.tj{right:0;top:0;bottom:0;height:auto;width:56%}
.cvart.tj img{object-position:50% 82%}
.cvart.tj:after{content:'';position:absolute;inset:0;background:
  linear-gradient(90deg,#0D1E33 0%,rgba(13,30,51,.82) 12%,rgba(13,30,51,.35) 28%,rgba(13,30,51,0) 46%),
  linear-gradient(180deg,#0D1E33 0%,rgba(13,30,51,.55) 14%,rgba(13,30,51,0) 34%,rgba(13,30,51,0) 66%,rgba(13,30,51,.7) 84%,#0D1E33 100%),
  linear-gradient(270deg,rgba(13,30,51,.45) 0%,rgba(13,30,51,0) 14%)}
.cvart.tj .credit{z-index:1;right:40px;bottom:122px;color:rgba(255,255,255,.55)}
.cv4 h1.tj{font-size:48px}
.cv4 .gbar{width:150px;height:2px;background:var(--gold2);margin:26px 0 20px}
.cv4 h1{font-size:52px;line-height:1.28;margin-top:24px}
.cv4 .tag2{font-size:19px;line-height:1.6;margin-top:0}
.cv4 .stats{margin-top:34px}
.sub2{display:flex;gap:64px;padding:18px 0 20px;border-top:1px solid rgba(200,168,106,.35)}
.sub2 i{display:block;font-style:normal;font-size:12px;letter-spacing:.3em;color:var(--gold2);font-weight:700}
.sub2 b{display:block;font-size:17px;font-weight:700;margin-top:6px}
/* ---- 네이티브 블록(통합제안서 내용을 새로 조판) */
.nb{flex:1;min-height:0;display:flex;flex-direction:column;gap:14px}
.nb>*{min-height:0}
.nb .cards,.nb .tiles,.nb .rows{flex:1 1 auto}
.splitx{display:grid;gap:26px;flex:1;min-height:0}
.splitx>div{display:flex;flex-direction:column;gap:14px;min-height:0}
.stackx{display:flex;flex-direction:column;gap:14px;min-height:0}
.gal{display:grid;gap:12px;flex:1;min-height:0}
.gal figure{position:relative;margin:0;border-radius:12px;overflow:hidden;border:1px solid rgba(200,168,106,.32);background:#0a1626;min-height:0}
.gal img{width:100%;height:100%;object-fit:cover;display:block}
.gal figure.ct img{object-fit:contain;background:#fff}
.gal figcaption{position:absolute;left:0;right:0;bottom:0;padding:22px 14px 9px;font-size:14.5px;font-weight:700;line-height:1.3;
  background:linear-gradient(0deg,rgba(5,12,22,.94) 0%,rgba(5,12,22,.72) 55%,rgba(5,12,22,0) 100%)}
.gal figcaption small{display:block;font-size:12.5px;font-weight:400;color:var(--sub);margin-top:2px}
.docs{display:flex;gap:28px;justify-content:center;align-items:stretch;flex:1;min-height:0}
.docs .d{flex:1 1 0;display:flex;flex-direction:column;align-items:center;min-height:0;min-width:0}
.docs .pp{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;width:100%}
.docs img{max-width:100%;max-height:100%;display:block;background:#fff;box-sizing:border-box;
  padding:7px;border:7px solid transparent;
  background:linear-gradient(#fff,#fff) padding-box,linear-gradient(135deg,#f1dca8 0%,#b8935a 28%,#8a6630 52%,#d9bb7c 76%,#9c773c 100%) border-box;
  box-shadow:0 0 0 1px rgba(0,0,0,.55),0 18px 36px rgba(0,0,0,.55),0 4px 10px rgba(0,0,0,.35)}  /* 금색 액자 + 흰 매트 */
.docs .cap{margin-top:14px;font-size:15.5px;font-weight:700;color:var(--gold);text-align:center;line-height:1.35}
.docs .cap small{display:block;font-size:12.5px;font-weight:400;color:var(--mute);margin-top:2px}
.bulx{display:flex;flex-direction:column;justify-content:center;gap:16px;flex:1;min-height:0}
.bulx>div{position:relative;padding-left:24px}
.bulx>div:before{content:'';position:absolute;left:0;top:9px;width:9px;height:9px;border-radius:50%;background:var(--gold2)}
.bulx b{display:block;font-size:20px;line-height:1.35}
.bulx p{font-size:16.5px;color:var(--sub);margin-top:5px;line-height:1.5}
.bulx p em,.bulx b em{font-weight:700}
.flowx{display:flex;align-items:stretch;gap:0}
.flowx .st{flex:1;border:1px solid var(--line);border-radius:12px;padding:14px 16px;
  background:linear-gradient(180deg,rgba(255,255,255,.075),rgba(255,255,255,.015))}
.flowx .st.hl{border-color:rgba(235,203,143,.75);background:linear-gradient(180deg,rgba(235,203,143,.16),rgba(235,203,143,.03))}
.flowx .st i{display:block;font-style:normal;font-size:12px;font-weight:700;letter-spacing:.24em;color:var(--gold2)}
.flowx .st b{display:block;font-size:18.5px;margin-top:5px;line-height:1.3}
.flowx .st p{font-size:14.5px;color:var(--sub);margin-top:5px;line-height:1.45}
.flowx .ar{display:flex;align-items:center;justify-content:center;width:30px;color:var(--gold);font-size:20px;font-weight:800;flex:none}
.tagx{border:1px solid var(--line);border-radius:12px;padding:14px 18px;background:rgba(255,255,255,.035)}
.tagx h4{font-size:15px;font-weight:700;color:var(--gold);margin-bottom:10px;letter-spacing:.02em}
.tagx .tg{display:flex;flex-wrap:wrap;gap:8px}
.tagx .tg span{border:1px solid rgba(255,255,255,.18);border-radius:99px;padding:5px 13px;font-size:14.5px;color:#DCE3EB}
.tagx .tg span.g{border-color:var(--gold2);color:var(--gold);font-weight:700}
.notex{font-size:13px;color:var(--mute);line-height:1.5}
.bigq{border-left:3px solid var(--gold2);padding:6px 0 6px 20px}
.bigq b{display:block;font-size:24px;line-height:1.4}
.bigq p{font-size:16.5px;color:var(--sub);margin-top:6px;line-height:1.5}
.ylist{flex:1;min-height:0;border:1px solid var(--line);border-radius:14px;padding:12px 22px;background:linear-gradient(180deg,rgba(255,255,255,.07),rgba(255,255,255,.015))}
.ylist ul{column-count:3;column-gap:34px;column-rule:1px solid rgba(255,255,255,.1)}
.ylist li{break-inside:avoid}
.ylist .yc{border:1px solid var(--line);border-radius:14px;padding:10px 14px;background:linear-gradient(180deg,rgba(255,255,255,.07),rgba(255,255,255,.015))}
.ylist h3{font-size:24px;color:var(--gold);margin:0 0 10px;font-weight:800}
.ylist h3 small{display:block;font-size:13px;color:var(--mute);font-weight:500;margin-top:2px}
.ylist ul{list-style:none;margin:0;padding:0}
.ylist li{display:flex;justify-content:space-between;gap:10px;font-size:13px;color:var(--sub);padding:4px 0;line-height:1.28;border-bottom:1px dashed rgba(255,255,255,.12)}
.ylist li:last-child{border-bottom:0}
.ylist li i{font-style:normal;font-size:11.5px;color:var(--mute);white-space:nowrap}
.ylist li b{font-variant-numeric:tabular-nums;color:var(--ink);white-space:nowrap}
.ylist li.big span,.ylist li.big b{color:var(--gold);font-weight:700}
.ylist li.fut i{color:#9fd3c7;font-weight:600}
.bigx{flex:1;display:grid;grid-template-columns:repeat(3,1fr);gap:18px;min-height:0}
.bigx .bc{display:flex;flex-direction:column;border-radius:14px;overflow:hidden;border:1px solid rgba(200,168,106,.45);background:#0b1a2d;min-height:0}
.bigx .ph{position:relative;flex:1;min-height:0}
.bigx .ph img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.bigx .ph .tg{position:absolute;left:12px;top:12px;font-size:12.5px;font-weight:700;color:#0d1e33;background:var(--gold);border-radius:99px;padding:4px 11px}
.bigx .pn{padding:14px 18px 16px;background:linear-gradient(180deg,#132a45,#0d1e33);border-top:2px solid var(--gold2)}
.bigx .n{font-size:44px;font-weight:800;color:var(--gold);line-height:1.05;font-variant-numeric:tabular-nums}
.bigx .n small{font-size:18px;margin-left:3px;font-weight:700}
.bigx .nm{font-size:19px;font-weight:700;margin-top:6px}
.bigx .ds{font-size:14px;color:var(--sub);margin-top:4px}
.bband{display:grid;grid-template-columns:1fr 1fr 1fr 1.5fr;gap:1px;background:rgba(200,168,106,.35);border:1px solid rgba(200,168,106,.35);border-radius:12px;overflow:hidden}
.bband>div{background:#0f2237;padding:10px 18px}
.bband i{display:block;font-style:normal;font-size:12.5px;color:var(--mute);letter-spacing:.04em}
.bband b{display:block;font-size:26px;font-weight:800;color:var(--ink);font-variant-numeric:tabular-nums}
.bband b small{font-size:14px;margin-left:2px}
.bband .nx b{color:var(--gold)}
.bband .nx p{font-size:13px;color:var(--sub);margin-top:1px}
.bars.b7{grid-template-columns:repeat(7,1fr);gap:20px}
.bars.b7 .v small{font-size:15px;margin-left:2px}
.toc4{grid-template-columns:repeat(4,1fr)!important}
.toc4 .col{padding:0 22px}
"""


def table(head, rows_html, cls=""):
    th = "".join(f"<th>{h}</th>" for h in head)
    return f'<table class="tbl {cls}"><thead><tr>{th}</tr></thead><tbody>{rows_html}</tbody></table>'


# ============================================================ 01장 신설 — e편한세상 분당 퍼스트빌리지 맞춤 제안 (재배치 후 07장)
# 근거: 입예협 공고 제2026-1호(2026.10.12) 4항 참가자격 · 5항 업무 범위 · 6항 선정 절차(PT 대표자 참석) · 7항 제출서류 ·
# 8항 제안서 필수 포함 9항목 · 9항 참가 제한·무효 · 10항 유의사항(확정되지 않은 혜택 제시 금지) + 확인된 단지 사실(data.py).
# → 확인된 사실과 이행할 수 있는 약속만 쓴다. 확인 전 칸은 TODO("…")(노란 칸).
S0 = "01. e편한세상 분당 퍼스트빌리지 맞춤 제안"
NEW = []


def new(kind, **kw):
    NEW.append((kind, kw))


def TODO(x):
    """본부장 확인 전 칸 — 노란 표시로 남기고, 빌드 끝에 개수를 알린다(제출본 빌드 전 0이어야 함). t() 이스케이프를 피해 finish()에서 태그로 바꾼다."""
    return f"⟦{x}⟧"


B.CSS += ".todo{background:#FFE066;color:#0D1E33;font-weight:700;padding:0 5px;border-radius:3px}"


def PG(key):
    """제안서 쪽 번호 자리(우측 상단 번호) — 재배치가 끝난 뒤 emit()에서 PGREF 제목으로 찾아 채운다."""
    return f"⟪pg:{key}⟫"


def PGS(keys):
    """여러 쪽 — emit()에서 번호 오름차순으로 정렬해 'p.04 · 05 · 18' 꼴로 채운다."""
    return "⟪pgs:" + ",".join(keys) + "⟫"


ST = D.SITE
_tp = dict(ST["types"])
_sale, _rent = ST["sale"], ST["rental"]
SL, RL = ST["sale_label"], ST["rental_label"]
_ap_n, _ap_c, _ap_r = ST["apply"]
_rec_n, _rec_hh = len(D.RECORDS), sum(r[3] for r in D.RECORDS)
_types_txt = " · ".join(a for a, _ in ST["types"])

T_DIV = f"{ST['name']}를 위한 [[맞춤 제안]]"
T_MAP = "공고 8항 [[필수 9항목]], 이 쪽에 있습니다"
T_SITE = f"{ST['name']}, [[이런 단지]]입니다"
T_FIRST = "신혼희망타운이라서 [[먼저 챙길 것]]"
T_OPT = "공식 유상옵션, [[겹침부터]] 확인합니다"
T_ITEMS = "신혼희망타운 맞춤 [[품목 구성]] (안)"
T_VENDORS = "품목별 [[예상 참가 업체]]"
T_VMGT = "입점 업체, [[계약부터 설치까지]] 관리합니다"
T_CHECK = "시중가 · 온라인 최저가 [[대비 검수]]"
T_ONE = "혜택 · 가격 비교, [[한 장]]으로 보여 드립니다"
T_SPECIAL = f"{ST['short']} [[특화 제안]]"
T_SUPPORT = "협의회 지원, [[시기별로]] 약속합니다"
T_BOOTH = "정당계약일 [[부스 지원]]"
T_REQ = "입예협 건의, [[관리표로]] 끝까지 챙깁니다"
T_LX = "단지 야간 경관 · 조경 조명, [[입주 전에]] 진단합니다"
T_PM = "본사는 울산, 대응은 [[분당 현장]]에서"
T_STAFF = "입예협 [[전담 체계]] - 공고 업무별 담당"
T_PRIV = "입주민 개인정보는 [[행사 운영에만]] 씁니다"
T_DEFECT = "하자 접수, [[책임부터]] 나눕니다"
T_REPORT = "보고는 [[항목과 시점]]을 정해 둡니다"
T_MONTHS = f"입주까지 {ST['months']}개월, [[빈틈없이]] 관리합니다"
T_SCHED = "선정부터 입주까지 [[추진 일정]] (안)"
T_SCOPE = "공고 업무 범위 [[11개 항목]] 대응"
T_QUAL = "입찰 참가자격 [[10개 항목]] 대응"
T_LIMIT = "참가 제한 · 무효 [[10개 항목]] 확인"
T_NOTE = "공고 유의사항 · 서약, [[그대로 지킵니다]]"
T_EXPO = "입주박람회 [[운영 계획]]"
T_PEOPLE = "대표자 · 핵심 운영인력 [[수행 경험]]"
T_HIST = "엣지컴퍼니 [[연혁]] · 주요 이력"
T_CPL = "입주민 [[컴플레인]], 이렇게 해결합니다"
T_CORE6 = f"{ST['short']}에 드리는 [[핵심 혜택 6가지]]"

new("divider", n="01", title=T_DIV,
    bl=["공고 8항 필수 9항목 대응표", "신혼희망타운 맞춤 품목 · 유상옵션 확인", "가격 검수 · 혜택 비교 한 장", "업무 11 · 자격 10 · 제한 10 대응"])

# ------------------------------------------------------------ 공고 8항 필수 9항목 ↔ 쪽 대응표(맞춤 장 첫머리)
MUST9 = [  # (공고 8항 필수 포함 항목, 엣지컴퍼니 제안 핵심, [PGREF 키])
    ("회사소개 및 주요 이력 현황", f"자본금 2억 · 연혁 · 1,000세대 이상 주관 {_rec_n}개 단지", ["num", "hist", "succ", "big"]),
    ("대표자 · 핵심 운영인력 수행경험 · 현장 운영 이력", "대표이사 · 총괄 본부장 · 4개 팀 · 전문 인력", ["people", "org"]),
    ("입주박람회 운영 계획", f"{ST['expo']} 3일(안) · 후보 3곳 · 배치 · 인원", ["expo", "venue", "floor", "comfort"]),
    ("품목 구성 및 입점 예정 업체 관리 방안", "맞춤 품목 · 옵션 겹침 확인 · 4단계 심사 · 일정 관리", ["opt", "items", "vendors", "vmgt", "screen"]),
    ("입주민 혜택 및 가격 투명성 확보 방안", f"{D.FUND}만원 상당 패키지 · 비교 한 장 · 단가 장치", ["one", "fund", "sep", "guard4"]),
    ("민원 · 하자 대응 체계 및 사후관리 방안", "3중 안전망 · 책임 구분 · 선보상 · 환불 규정", ["safe3", "defect", "cpl", "rule1"]),
    ("협의회 지원 사항 및 계획", "시기별 지원 · 정당계약일 부스 · B 패키지", ["support", "booth", "req", "pkb"]),
    ("품목별 시중가 · 온라인 최저가 대비 검수 방안", "같은 조건 총액 비교 · 입예협 검수 · 10배 보상", ["check", "x10"]),
    ("A/S 접수창구 또는 전담 연락체계 운영계획", "전담 PM · 한 창구 · 24시간 회신 · 48시간 처리", ["pm", "call", "crm"]),
]
new("std", sec=S0, title=T_MAP,
    lead="공고 8항이 꼭 넣으라고 한 9가지를 어느 쪽에서 설명하는지 정리했습니다(쪽 번호 = 각 장 우측 상단 번호).",
    body=table(["NO", "공고 8항 필수 포함 항목", "엣지컴퍼니 제안 핵심", "제안서 쪽"], "".join(
        f'<tr><td class="n">{i:02d}</td><td class="k">{t(a)}</td><td>{t(b)}</td><td class="pg">{PGS(ks)}</td></tr>'
        for i, (a, b, ks) in enumerate(MUST9, 1)), "m9"),
    kp=("필수 9항목 모두 [[숫자와 기한]]으로 답했습니다.", "자격 · 업무 범위 · 제한 · 유의사항 대응은 이 장 뒤쪽"))
B.CSS += (".tbl.m9 td{padding:9px 14px;font-size:15px;line-height:1.35}.tbl.m9 td.k{font-size:16px;width:37%}"
          ".tbl.m9 td.pg{white-space:nowrap;color:var(--gold);font-weight:800;font-size:15px;font-variant-numeric:tabular-nums;width:22%}"
          ".tbl.m9 tr:nth-child(odd) td{background:rgba(255,255,255,.025)}"
          ".tbl.s11 td{padding:5px 12px;font-size:14px;line-height:1.32}.tbl.s11 td.k{font-size:14.5px;width:34%}"
          ".tbl.s11 td.pg{white-space:nowrap;color:var(--gold);font-weight:800;font-size:14px;width:12%}.tbl.s11 td.n{width:36px}")

# ------------------------------------------------------------ 단지 이해
new("std", sec=S0, title=T_SITE,
    lead="입찰 공고문 단지 개요 · 입주자모집공고 기준 - 입주예정자협의회(이하 입예협)와 함께 설계합니다.",
    body=B.cards([
        dict(lb="SCALE", big=f"{ST['households']:,}", unit="세대", nm=f"{ST['buildings']}개동 · 최고 25층",
             ds=f"{SL} {_sale:,} · {RL} {_rent} · 2026.07 본청약 평균 {_ap_r}:1"),
        dict(lb="TYPE", big="51~59", unit="㎡", nm="전 세대 60㎡ 이하",
             ds=f"{_types_txt} - [[수납 · 커튼 · 조명]]을 타입별 실측으로"),
        dict(lb="MOVE-IN", big="2029", unit=".02", nm="입주 예정",
             ds=f"정당계약 {ST['contract']} · 입주까지 약 {ST['months']}개월"),
        dict(lb="LOCATION", big="성남낙생", nm=f"{ST['developer_short']} · {ST['builder']}", hl=True,
             ds="A-1블록 · 지구 첫 분양 · 판교·분당 업무지구 인접 · 미금역 버스 약 10분"),
    ]),
    kp=("신혼부부 · 영유아 가구가 실거주하는 [[소형 타입 단지]]입니다.", "입찰 공고 · 입주자모집공고 기준"))

new("std", sec=S0, title=T_FIRST,
    lead=f"전 세대 전용 60㎡ 이하 · 공식 유상옵션이 많은 단지 - 공동구매 전에 확인할 것부터 정리했습니다.",
    body=B.rows([
        ("유상옵션 겹침 확인", "시스템에어컨 · 현관 중문 · 탄성코트 · 붙박이장 · 식기세척기는 공식 유상옵션이 있습니다. 선택 결과를 확인한 뒤 [[남은 수요 품목만]] 모집합니다."),
        ("소형 타입 맞춤", f"{_types_txt} - 수납 · 커튼 · 조명은 일괄 가격이 아니라 [[타입별 실측]]으로 사이즈부터 맞춥니다."),
        ("영유아 가족 안심", "설치 품목은 KC 등 법정 인증 서류를 확인하고, 박람회장에는 [[어린이 놀이방 · 수유실 · 유모차 대여]]를 둡니다."),
        ("같은 조건 가격 비교", "제품가 · 설치 · 철거 · 배송 · A/S를 맞춘 [[총액으로]] 시중가 · 온라인 최저가와 비교해 공개합니다."),
    ], title_w=210),
    kp="이미 고른 옵션은 권하지 않고, [[남은 수요]]만 같은 조건으로 비교해 드립니다.")

B.CSS += (".tbl.op5 td{padding:15px 14px;font-size:15.5px;line-height:1.45}.tbl.op5 td.k{font-size:16.5px;width:16%}"
          ".tbl.op5 td:nth-child(2){width:36%}")
new("std", sec=S0, title=T_OPT,
    lead="모집공고의 공식 유상옵션과 겹치는 품목은, 수요조사로 옵션 선택 여부를 확인한 뒤 남은 수요만 모집합니다.",
    body=table(["품목", "공식 유상옵션 (모집공고 기재가 · 부가세 포함)", "외부 업체 설치 시 확인할 조건"], "".join(
        f'<tr><td class="k">{t(a)}</td><td>{t(b)}</td><td>{t(c)}</td></tr>' for a, b, c in D.OPTIONS), "op5")
         + '<div class="hflow"><span>수요조사 · 옵션 문항</span><i>›</i><span>겹치는 품목 걸러내기</span><i>›</i>'
           '<span>남은 수요 품목만 모집</span><i>›</i><span>조건 차이까지 비교 안내</span><i>›</i><span>입예협 승인</span></div>'
         + '<div class="notex" style="margin-top:12px">※ 외부 설치가 공식 옵션과 같은 기능을 제공한다고 안내하지 않습니다(예: 시스템에어컨 월패드 연동). '
           '옵션 금액은 일부 타입·구성 예시이며, 옵션 계약 일정·조건은 사업주체 안내를 따릅니다.</div>',
    kp=("공식 옵션을 고른 세대에는 [[같은 품목을 권하지 않습니다.]]", "옵션 선택 여부는 수요조사 설문으로만 확인 · 개인정보 최소 수집"))

ITEMS = [  # (묶음, 대상, [품목], 기준)
    ("공간 효율", "전용 51 ~ 59㎡", ["커튼 · 블라인드 (타입별 실측 제작)", "수납 · 선반 · 가구", "LED 조명 · 실링팬"], "타입별 실측 데이터로 사이즈부터"),
    ("입주 준비", "모든 세대", ["입주청소 · 줄눈 · 새집증후군", "방충망(미세 · 안전) · 단열필름", "포장이사 · 사전점검 대행"], f"{ST['local']} 업체 우선 · 48시간 A/S"),
    ("생활 가전 · 렌탈", "필요 세대", ["가전 · 식기세척기", "정수기 · 비데 · 공기청정 렌탈", "욕실 환기 가전"], "식기세척기는 콘센트 전기공사 포함 견적"),
    ("조건부 시공", "옵션 겹침 확인 후", ["시스템에어컨", "현관 중문 · 탄성코트", "붙박이장"], "공식 옵션 선택 결과 확인 → 남은 수요만"),
]


def _item_card(nm, who, its, rule):
    li = "".join(f"<li>{t(x)}</li>" for x in its)
    return f'<div class="itc"><i>{t(who)}</i><h3>{t(nm)}</h3><ul>{li}</ul><p>{t(rule)}</p></div>'


new("std", sec=S0, title=T_ITEMS,
    lead="공고 8항 4 - 신혼부부 · 영유아 가구의 실거주에 필요한 품목을 네 묶음으로 나누고, 공식 옵션과 겹치는 품목은 조건부로 둡니다.",
    body=('<div class="nb"><div class="itx">' + "".join(_item_card(*x) for x in ITEMS) + '</div>'
          f'<div class="itr"><b>{RL} {_rent}세대</b><span>운영기관 · 입예협 협의 후 박람회 참여를 안내합니다. 생활 가구 · 가전 · 이사 · 청소 등 '
          '비고정 품목 위주이며, 고정 시설 시공은 임대계약 · 운영기관 승인 · 원상복구 조건을 확인한 뒤에만 안내합니다.</span></div>'
          '<div class="itr g"><b>영유아 가구 안심 기준</b><span>설치 품목은 KC 등 법정 인증 서류 확인 · 마감재는 친환경 인증 서류를 낸 업체 우선 · '
          '새집증후군 · 라돈 측정은 B 패키지 항목으로 선택</span></div></div>'),
    kp=("품목 수와 업체 수는 [[수요조사 결과]]로 정합니다.", "품목 · 가격은 입예협과 사전 협의 후 확정(공고 10항 7)"))
B.CSS += (".itx{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;flex:1;min-height:0}"
          ".itc{border:1px solid var(--line);border-top:2px solid var(--gold2);border-radius:14px;padding:14px 18px;display:flex;flex-direction:column;"
          "background:linear-gradient(180deg,rgba(235,203,143,.08),rgba(255,255,255,.01) 45%)}"
          ".itc i{font-style:normal;font-size:12px;letter-spacing:.14em;color:var(--gold2);font-weight:700}"
          ".itc h3{font-size:23px;font-weight:800;color:var(--gold);margin:2px 0 8px}"
          ".itc ul{list-style:none;margin:6px 0 0;padding:0;display:flex;flex-direction:column;gap:14px;flex:1}"
          ".itc li{font-size:17px;line-height:1.45;padding-left:14px;position:relative}.itc li:before{content:'';position:absolute;left:0;top:8px;width:6px;height:6px;border-radius:50%;background:var(--gold2)}"
          ".itc p{margin-top:10px;border-top:1px dashed rgba(200,168,106,.45);padding-top:8px;font-size:14.5px;color:var(--gold);line-height:1.45}"
          ".itr{display:grid;grid-template-columns:200px 1fr;gap:14px;align-items:center;border:1px dashed rgba(200,168,106,.55);border-radius:12px;padding:10px 16px}"
          ".itr b{font-size:16px;color:var(--gold)}.itr span{font-size:14px;color:var(--sub);line-height:1.5}"
          ".itr.g{border-style:solid;border-color:rgba(235,203,143,.55);background:rgba(235,203,143,.06)}")


def vendor_rows():
    out, groups = [], {}
    for g, *_ in D.VENDORS:
        groups[g] = groups.get(g, 0) + 1
    seen = set()
    for g, item, who, note in D.VENDORS:
        cls = ' class="own"' if g == "주관사 직영" else ""
        gcell = "" if g in seen else f'<td class="g" rowspan="{groups[g]}">{g}</td>'
        seen.add(g)
        out.append(f"<tr{cls}>{gcell}<td class=\"k\">{t(item)}</td><td>{t(who)}</td><td>{t(note)}</td></tr>")
    return "".join(out)


new("std", sec=S0, title=T_VENDORS,
    lead=f"확정은 수요조사와 입예협 공개 입찰 · 심사 후 - 시공 품목은 현장 인근({ST['local']}) 업체가 우선입니다.",
    body=table(["구분", "품목", "예상 참가 업체", "비고"], vendor_rows(), "sm"),
    kp=("주관사 직영 품목도 [[같은 심사 · 같은 단가 공개 · 같은 가격 보호 규정]] 적용.", "‘참가 협의 중’은 확정 전 업체 · 사업 전체 일괄 도급 없음"))

VMGT = [  # 공고 5항 2 · 3 — (단계, 관리 방법, 기준)
    ("선정", "수요조사 → 공개 입찰공고 → 4단계 심사 → [[입예협 최종 컨펌]]", "품목별 업체 수는 입예협 승인 · 하청 금지"),
    ("계약", "표준 계약서에 취소·환불 규정 첨부 · 모델코드 · 포함 조건(설치·철거·배송·A/S) 명시", f"계약금 {D.DEPOSIT_MAX}% 이하 · 카드·현금 동일가"),
    ("일정", "세대별 상담 · 계약 · 납품 · 시공 · 설치 [[일정 관리표]] · 동별 일정 충돌 조정", "시공 가능 시점 · 관리사무소 신고 확인"),
    ("검수", "시공 · 설치 후 세대 확인 서명 → 잔금 · 해피콜", "하자 · 미시공은 보수 후 잔금"),
    ("평가", "박람회 후 업체별 민원 · A/S 처리 현황 집계 → 입예협 보고", "패널티 3단계 · 재참여 제한"),
    ("공정", "모든 참여업체에 균등한 기회 · 가격 담합 · 독점 유도 · 비방 금지", "서식 5 청렴계약 3"),
]
new("std", sec=S0, title=T_VMGT,
    lead="공고 5항 2 · 3 - 품목 구성 · 업체 섭외 · 계약관리부터 납품 · 시공 · 설치 일정까지 주관사가 같은 표로 관리합니다.",
    body=table(["단계", "관리 방법", "기준"], "".join(
        f'<tr><td class="k">{a}</td><td>{t(b)}</td><td>{t(c)}</td></tr>' for a, b, c in VMGT), "lgx vm"),
    kp=("업체는 [[같은 기준]]으로 뽑고, [[같은 표]]로 관리합니다.", "4단계 심사 · 특약이행각서 · 패널티는 03 · 04장"))
B.CSS += ".tbl.vm td{padding:14px 14px}.tbl.vm td.k{width:12%}.tbl.vm td:last-child{width:30%}"

CHECK5 = [("STEP 01", "단가 제출", "모델코드 · 규격 · 설치 · 철거 · 배송 · A/S 포함 여부"),
          ("STEP 02", "시중가 조사", f"{ST['local']} 오프라인 매장 2곳 이상 견적서"),
          ("STEP 03", "온라인 최저가", "같은 모델 최저 총액 · 조사일 · 화면 캡처 보관"),
          ("STEP 04", "입예협 검수", "비교표 제출 · 입예협이 품목을 골라 직접 확인"),
          ("STEP 05", "공개 · 보호", "박람회 전 카페 공개 · 계약 후 최저가 차액 10배")]
new("std", sec=S0, title=T_CHECK,
    lead="공고 8항 8 - 박람회 전에 품목별로 시중가 · 온라인 최저가와 비교하고, 입예협 검수를 거친 단가만 공개합니다.",
    body=('<div class="nb"><div class="flowx">' + "".join(
        (('<div class="ar">›</div>' if i else "") + f'<div class="st{" hl" if i == 3 else ""}"><i>{a}</i><b>{b}</b><p>{t(c)}</p></div>')
        for i, (a, b, c) in enumerate(CHECK5)) + '</div>'
          + B.rows([
              ("같은 조건 총액으로", "제품가만이 아니라 설치 · 철거 · 배송 · 부가세 · A/S 기간을 맞춘 [[총액]]으로 비교합니다."),
              ("높으면 사유 또는 조정", "박람회 단가가 시중가 · 온라인 최저가보다 높으면 사유(설치 포함 · A/S 연장 등)를 표기하거나 단가 조정을 요청하고, [[입예협이 승인하지 않으면 재입찰]]합니다."),
              ("공식 옵션과도 비교", "시스템에어컨 · 중문 · 탄성코트 · 붙박이장 · 식기세척기는 모집공고 옵션가와 조건 차이(연동 · 콘센트 등)까지 표기합니다."),
              ("기록 보관 · 열람", "조사 화면 · 견적서는 협약 기간 동안 보관하고, 입예협이 요청하면 원자료를 열람합니다."),
          ], title_w=210) + '</div>'),
    kp=("검수는 [[박람회 전]], 보상은 [[계약 후]] - 두 번 확인합니다.", "최저가 차액 10배 보상은 인근 오프라인 매장 동일 제품 기준(온라인 · 시공 품목 제외) · 규정 제8조"))

ONE_L = [  # (숫자, 단위, 혜택, 조건)
    (f"{D.FUND}", "만원 상당", "세대당 혜택 패키지", f"{SL} {D.FUND_HH:,}세대 · 현금 아님 · A·B·C 또는 입예협 지정"),
    ("30", "만원", "정회원 박람회 상품권", "일반 20 + 정회원 10 · 업체 계약 시 품목당 1매"),
    ("10", "%", "현장 특별할인 (최대)", "사전 공개 단가표에 적은 품목만"),
    ("10", "배", "최저가 차액 보상", "인근 오프라인 동일 제품 · 계약 후 7일 · 온라인·시공 제외"),
    (f"{D.DEPOSIT_MAX}", "%", "계약금 상한", "잔금은 시공 · 설치 후 · 카드 · 현금 동일가"),
    ("3", "영업일", "환불", "취소 기한 안이면 위약금 없이 전액"),
    ("2", "년 이상", "무상 A/S", "업체 · 품목별 상이 · 48시간 하자보수 원칙"),
]
_ph = '<span class="ph0">조사 후 기입</span>'
ONE_R = [("식기세척기 · 14인용", "전기공사 포함", "165만원 (콘센트 포함)"),
         ("현관 중문 · 슬라이딩", "55A 기준", "150만원"),
         ("커튼 · 블라인드", "55A 거실 · 실측", "옵션 없음")]
new("std", sec=S0, title=T_ONE,
    lead="정회원 온라인 투표 전에 한눈에 보시도록 - 왼쪽은 우리 집이 받는 혜택과 조건, 오른쪽은 박람회 전에 공개할 가격 비교표 양식입니다.",
    body=('<div class="nb"><div class="one">'
          '<div class="ol"><h3><i>BENEFIT</i>우리 집이 받는 혜택 · 조건까지</h3><div class="obx">' + "".join(
              f'<div><b>{a}<small>{u}</small></b><div><strong>{t(n)}</strong><span>{t(c)}</span></div></div>' for a, u, n, c in ONE_L)
          + '</div></div>'
          '<div class="orr"><h3><i>PRICE</i>가격 비교표 · 공개 양식</h3>'
          '<table class="ocmp"><thead><tr><th>품목</th><th>시중가<small>' + ST["local"] + ' 매장</small></th><th>온라인 최저가<small>배송·설치 포함</small></th>'
          '<th>공식 유상옵션가<small>모집공고</small></th><th class="ex">박람회 단가<small>사전 공개</small></th></tr></thead><tbody>'
          + "".join(f'<tr><td><b>{a}</b><small>{b}</small></td><td>{_ph}</td><td>{_ph}</td><td>{c}</td><td class="ex">{_ph}</td></tr>' for a, b, c in ONE_R)
          + '</tbody></table>'
          '<ul class="ont"><li>같은 모델코드 · 같은 포함 조건(설치 · 철거 · 배송 · A/S)의 <b>총액</b>으로 비교</li>'
          '<li>박람회 전 <b>입예협 검수 · 승인 후 카페 공개</b> · 박람회장 가격 변경 없음</li>'
          '<li>공식 옵션과 기능 차이가 있으면 함께 표기(예: 외부 시스템에어컨 월패드 연동 불가)</li></ul></div>'
          '</div></div>'),
    kp=("혜택은 [[조건까지]], 가격은 [[같은 조건 총액]]으로 보여 드립니다.", "공고 10항 2 - 확정되지 않은 혜택은 적지 않았습니다 · 표의 빈칸은 업체 선정 후 기입"))
B.CSS += (".one{display:grid;grid-template-columns:1fr 1.25fr;gap:20px;flex:1;min-height:0}"
          ".one h3{font-size:17px;font-weight:800;margin-bottom:10px;display:flex;align-items:baseline;gap:10px}"
          ".one h3 i{font-style:normal;font-size:11px;letter-spacing:.2em;color:var(--gold2);font-weight:700}"
          ".one .ol,.one .orr{border:1px solid var(--line);border-radius:14px;padding:14px 18px;display:flex;flex-direction:column;min-height:0;"
          "background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.01))}"
          ".one .ol{border-color:rgba(235,203,143,.6);background:linear-gradient(180deg,rgba(235,203,143,.12),rgba(235,203,143,.02))}"
          ".obx{display:flex;flex-direction:column;justify-content:space-between;flex:1}"
          ".obx>div{display:grid;grid-template-columns:108px 1fr;gap:12px;align-items:center;padding:4px 0;border-bottom:1px dashed rgba(255,255,255,.12)}"
          ".obx>div:last-child{border-bottom:0}"
          ".obx b{font-size:30px;font-weight:800;color:var(--gold);line-height:1;text-align:right;white-space:nowrap}.obx b small{font-size:13px;margin-left:2px}"
          ".obx strong{display:block;font-size:15.5px}.obx span{display:block;font-size:12.8px;color:var(--sub);line-height:1.4}"
          ".ocmp{width:100%;border-collapse:collapse;flex:1}"
          ".ocmp th{font-size:12.5px;font-weight:700;color:var(--gold2);text-align:center;padding:0 6px 8px;border-bottom:1.5px solid rgba(200,168,106,.55);line-height:1.3}"
          ".ocmp th small{display:block;font-size:10.5px;color:var(--mute);font-weight:400}"
          ".ocmp th:first-child{text-align:left}"
          ".ocmp td{font-size:14px;padding:10px 6px;border-bottom:1px dashed rgba(255,255,255,.14);text-align:center;color:var(--sub)}"
          ".ocmp td:first-child{text-align:left}.ocmp td b{display:block;color:var(--ink);font-size:15px}.ocmp td small{font-size:12px;color:var(--mute)}"
          ".ocmp .ex{background:rgba(235,203,143,.08)}"
          ".ph0{display:inline-block;border:1px dashed rgba(235,203,143,.55);border-radius:6px;padding:4px 8px;font-size:11.5px;color:var(--gold2)}"
          ".ont{list-style:none;margin:12px 0 0;padding:10px 0 0;border-top:1px solid rgba(200,168,106,.35);display:flex;flex-direction:column;gap:6px}"
          ".ont li{font-size:13.5px;color:var(--sub);line-height:1.45;padding-left:14px;position:relative}.ont li:before{content:'·';position:absolute;left:2px;color:var(--gold2);font-weight:800}"
          ".ont b{color:var(--ink)}")

new("std", sec=S0, title=T_SPECIAL,
    lead="박람회 운영 경험과 주관사 직영 품목(조명 · 커튼 · 실링팬)을 신혼희망타운에 맞게 다시 짰습니다.",
    body=B.tiles([
        dict(lb="01", nm="유상옵션 겹침 확인", ds="옵션 선택 여부를 수요조사로 확인해, 겹치는 품목은 권하지 않고 남은 수요만 모집합니다."),
        dict(lb="02", nm="타입별 표준 견적", ds=f"{_types_txt} 타입별 실측 데이터로 커튼 · 수납 · 조명을 사이즈부터 맞춥니다."),
        dict(lb="03", nm="가격 비교 한 장", ds="시중가 · 온라인 최저가 · 공식 옵션가를 같은 조건 총액으로 비교해 박람회 전에 공개합니다."),
        dict(lb="04", nm="영유아 가족 박람회", ds="어린이 놀이방 · 수유실 · 유모차 대여를 두고, 가족이 함께 비교 · 상담하도록 운영합니다."),
        dict(lb="05", nm="온라인 박람회 · 카카오 상담", ds="박람회장에 오기 어려운 세대도 폐쇄몰과 카카오채널로 같은 공동구매가에 상담합니다."),
        dict(lb="06", nm="단지 야간 경관 진단", ds="전기공사업 등록 업체로서 공용부 · 경관조명 개선안을 제출합니다. 설치는 입예협 · 관리주체 승인 후 선택."),
    ], cols=3, rows_n=2).replace('class="tiles"', 'class="tiles lg"'),
    kp=("제안 품목 · 혜택은 수요조사 결과에 따라 [[입예협과 최종 확정]]합니다.", "공고 10항 7 - 품목 · 가격은 입예협과 사전 협의 후 확정"))

SUPPORT = [  # (시기, 기본 업무 — 공고 5항, 비용 주관사, 선택 지원 — 15만원 상당 패키지 B)
    ("선정 직후 · 2026.11", "[[정당계약일 부스 지원]](입예협 요청 시) · 협약 · 카페/공지 채널 콘텐츠 지원 시작", "온라인 위임장 · 민원 양식"),
    ("계약 후 ~ 옵션 선택", "유상옵션 일정 · 조건 안내 콘텐츠 · 옵션 선택 여부 설문 지원", "도면 분석보고서"),
    ("2027 ~ 2028 상반기", "정례 진행 보고 · 건의 관리표 · 공문 작성 · 시공사 협의 자료", "공용부 품질 점검 · 협상 미팅 동석"),
    ("2028 하반기", "품목 수요조사 · 업체 공개 입찰 · 가격 검수 · 사전점검 체크리스트 · 입주설명회 지원", "세미나 영상 · 일조 시뮬레이션"),
    ("사전점검 · 박람회", "입주박람회 3일 운영 · 사전점검 행사 인력 · 비품 · 안내물", "사전점검 당일 지원 · 열화상 드론 · 라돈"),
    ("입주 후 1년", "하자 접수 창구 · 하자처리 현황 보고 · 결과 보고서", "공용 · 조경 하자진단 · 세스코 점검"),
]
new("std", sec=S0, title=T_SUPPORT,
    lead="공고 8항 7 - 공고 업무 범위의 기본 지원은 주관사 비용으로 하고, 15만원 상당 패키지 B는 입예협이 골라 더합니다.",
    body=table(["시기", "기본 지원 · 공고 5항 (주관사 부담)", "선택 지원 · 패키지 B (입예협 선택)"], "".join(
        f'<tr><td class="k">{a}</td><td>{t(b)}</td><td>{t(c)}</td></tr>' for a, b, c in SUPPORT), "lgx sp6"),
    kp=("기본 지원은 [[15만원과 별도]]로 합니다 - 패키지는 입예협이 더 고르는 몫입니다.", "B 패키지 항목은 08장 · 일정은 입예협 정례회의에서 확정"))
B.CSS += ".tbl.sp6 td{padding:12px 14px;font-size:15.5px}.tbl.sp6 td.k{width:17%;white-space:nowrap}.tbl.sp6 td:last-child{width:30%;color:var(--gold)}"

new("std", sec=S0, title=T_BOOTH,
    lead=f"공고 5항 11 - 정당계약({ST['contract']}) 부스 지원. 선정 통보 후 입예협 요청에 맞춰 남은 계약 기간에 지원합니다.",
    body=B.tiles([
        dict(lb="01 · BOOTH", nm="안내 부스 지원", ds="테이블 · 의자 · 현수막 · X배너 · 안내물을 준비합니다. 문구는 입예협 승인 후 제작합니다."),
        dict(lb="02 · MEMBER", nm="정회원 · 위임장 안내", ds="입예협 양식 · 절차 그대로 안내합니다. 개인정보는 입예협이 직접 받고, 주관사는 보관하지 않습니다."),
        dict(lb="03 · STAFF", nm="도우미 지원", ds="인원 · 일수는 입예협 요청에 맞춰 협의합니다. 전 인원 명찰(직책 · 이름)을 답니다."),
        dict(lb="04 · COMFORT", nm="대기 편의", ds="생수 · 음료 등 대기 편의를 계약 장소 운영 주체의 승인 범위 안에서 준비합니다."),
        dict(lb="05 · NO SALES", nm="판매 · 영업 없음", ds="공동구매 안내 · 업체 홍보 · 사전 예약을 하지 않습니다. 입예협 안내를 돕는 자리입니다."),
        dict(lb="06 · COST", nm="비용은 주관사 부담", ds="부스 지원 비용은 주관사가 부담하며, 세대당 15만원 상당 패키지와 별개입니다."),
    ], cols=3, rows_n=2).replace('class="tiles"', 'class="tiles lg"'),
    kp=("계약일 부스는 [[입예협 안내]]를 돕는 자리 - 영업하지 않습니다.", "계약 장소 운영 주체의 승인 범위 안에서 · 일정 · 인원은 입예협과 협의"))

REQ = [  # 예상 건의 유형 — 실제 항목은 입예협과 정한다
    ("품질 · 시공", "사전점검 하자 · 마감 · 설비 질의", "점검 체크리스트 반영 · 시공사 질의서 작성 지원", "시공사 회신 확보"),
    ("옵션 · 계약", "유상옵션 일정 · 조건 · 계약 안내", "사업주체 안내 정리 · 카페 안내 콘텐츠(입예협 승인)", "공지 게시"),
    ("생활 인프라", "국공립어린이집 · 다함께돌봄센터 · 교통 · 상가 일정", "기관 발표 자료 확인 · 질의 공문 작성 지원", "기관 회신 공유"),
    ("정보 · 일정", "사업 일정 · 사전점검 · 입주 일정", "공문 작성 · 발송 지원 · 회신 일정 추적", "일정 공유"),
]
new("std", sec=S0, title=T_REQ,
    lead="입예협에 들어오는 건의를 접수 → 기술 검토 → 시공사 · 기관 협의 → 반영 · 보류 사유 → 공유까지 기록합니다.",
    body=table(["분야", "건의 예 (유형)", "주관사 지원", "완료 기준"], "".join(
        f'<tr><td class="k">{a}</td><td>{t(b)}</td><td>{t(c)}</td><td>{t(d)}</td></tr>' for a, b, c, d in REQ), "sm tjs")
         + '<div class="hflow" style="margin-top:20px"><span>건의 접수</span><i>›</i><span>기술 검토 · 담당 지정</span><i>›</i>'
           '<span>시공사 · 기관 협의</span><i>›</i><span>반영 / 보류 사유</span><i>›</i><span>입예협 공유 · 기록</span></div>'
         + '<div class="gq3"><div><b>관리표 칸</b><span>건의 번호 · 제목 · 담당 · 기한 · 회신 · 상태</span></div>'
           '<div><b>상태 구분</b><span>접수 → 검토 중 → 협의 완료 → 설치 완료 · 보류(사유 기재)</span></div>'
           '<div><b>공유 주기</b><span>입예협 정례회의마다 · 시공사 회신이 오면 바로 갱신</span></div></div>',
    kp=("‘협의 완료’와 ‘설치 완료’를 [[구분해서]] 보고합니다.", "건의 유형은 예시 · 실제 항목은 입예협과 정합니다"))
B.CSS += (".gq3{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px}"
          ".gq3>div{border:1px solid var(--line);border-radius:11px;padding:12px 16px;display:flex;flex-direction:column;gap:4px}"
          ".gq3 b{font-size:15px;color:var(--gold)}.gq3 span{font-size:14px;color:var(--sub);line-height:1.45}"
          ".tbl.sm.tjs td{padding-top:16px;padding-bottom:16px}")

new("std", sec=S0, title=T_LX,
    lead="전기공사업 등록 업체이자 사내 조경 전문 인력을 둔 주관사로서, 단지의 밤길과 조경을 도면 · 현장 · 예산으로 살핍니다.",
    body=B.rows([
        ("우선 1 · 조명 · 보행", "주 동선 · 산책로 야간 밝기, 눈부심 · 빛샘 · 타이머 조정 - 기존 경관조명 도면 · 배선 · 조도부터 확인합니다."),
        ("우선 2 · 어린이 동선", "어린이집 · 놀이터 주변 보행 동선과 계단 · 단차 바닥 밝기를 함께 봅니다."),
        ("조건부 · 시설 추가", "조명 · 시설 추가는 관리비 · 유지관리 주체 · 인접 세대 눈부심을 [[모두 확인한 뒤]] 판단합니다."),
        ("산출물 4가지", "① 현황 진단 1장 ② 기본 · 개선 · 선택안 비교(물량 · 공사비 · 유지관리비) ③ 협의 기록 ④ 완료 검수(수량 · 위치 · 사양 · A/S)"),
    ], title_w=210),
    kp=("공사 범위 · 금액은 [[도면 검토와 비용 승인 후]] 확정합니다.", "전기공사업 등록 제 울산-00821호"))

new("std", sec=S0, title=T_PM,
    lead="공고 8항 9 · 4항 5 - 본사가 멀어도 입주민은 한 창구로 연락하고, 전담 PM과 현장 인근 업체가 기한 안에 처리합니다.",
    body=('<div class="nb"><div class="pmx">'
          '<div class="pc"><h3><i>CONTACT</i>전담 연락 체계</h3>'
          + B.rows([
              ("총괄 책임", "주관사업 총괄 본부장 · [[" + D.MANAGER[2].replace("-", "\u2060-\u2060") + "]]"),
              ("전담 PM", f"{ST['short']} 전담 1명 지정 · 협약 시 성명 · 연락처 제출"),
              ("한 창구 접수", f"주관 콜센터 {D.TEL}(평일 09:00 ~ 18:00) · 온라인 365일(카페 신문고 · 카카오채널 · 홈페이지)"),
              ("회신 · 처리", "[[24시간 안에 1차 회신]] · 48시간 하자보수 원칙 · 해피콜로 종결"),
          ], title_w=128) + '</div>'
          '<div class="pc"><h3><i>ON SITE</i>거리를 메우는 현장 체계</h3>'
          + B.rows([
              ("정례 · 행사", "입예협 정례회의 · PT · 박람회 · 사전점검에 본부장 · 운영팀이 현장 참석"),
              ("입주 집중기", "단지 안 임시 상주 창구(입예협 · 관리주체 협의)"),
              ("시공 · A/S", f"{ST['local']} 시공업체 우선 선정 - [[48시간 A/S가 가능한 거리]]"),
              ("수도권 거점", TODO("수도권 현장 거점 · 상주 인원 - 확정 시 기재")),
          ], title_w=128) + '</div></div></div>'),
    kp=("입주민은 [[한 창구]]로 연락하시면 됩니다.", "콜센터 평일 09:00 ~ 18:00 · 온라인 365일 접수 · 24시간 이내 회신"))
B.CSS += (".pmx{display:grid;grid-template-columns:1fr 1fr;gap:20px;flex:1;min-height:0}"
          ".pmx .pc{border:1px solid var(--line);border-radius:14px;padding:14px 18px;display:flex;flex-direction:column;min-height:0;"
          "background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.01))}"
          ".pmx .pc:first-child{border-color:rgba(235,203,143,.6);background:linear-gradient(180deg,rgba(235,203,143,.12),rgba(235,203,143,.02))}"
          ".pmx h3{font-size:18px;font-weight:800;margin-bottom:8px;display:flex;align-items:baseline;gap:10px}"
          ".pmx h3 i{font-style:normal;font-size:11px;letter-spacing:.2em;color:var(--gold2);font-weight:700}"
          ".pmx .rows{flex:1}")

_stf = {n: (c, r) for n, c, r in D.STAFF}


def _dcard(no, req, head, items):
    li = "".join(f"<li>{t(x)}</li>" for x in items)
    return f'<div class="dcd"><i>공고 업무 {no}</i><h4>{req}</h4><b>{head}</b><ul>{li}</ul></div>'


new("std", sec=S0, title=T_STAFF,
    lead="분당 전담 인원 배치(안)를 바탕으로, 공고 5항 업무 11개를 팀별로 나눠 맡깁니다.",
    body='<div class="nb"><div class="dcx">'
         + _dcard("1 · 2 · 3 · 6 · 9", "박람회 · 업체 · 일정 · 대관 · 안전", "행사관리 · 영업 분업", [
             f"현장 - 행사관리팀 {_stf['행사관리팀'][0]}명: 박람회 · 대관 · 배치 · 안전 · 편의공간",
             f"업체 - 영업팀 {_stf['영업팀'][0]}명: 섭외 · 심사 지원 · 계약 · 설치 일정 관리",
             "가격 검수 - 시중가 · 온라인 최저가 비교표 작성",
             "입예협 요청은 담당 팀을 지정해 [[24시간 안에 1차 회신]]"])
         + _dcard("5 · 7 · 11", "입예협 행사 · 홍보 · 요청 업무", f"이벤트 {_stf['이벤트팀'][0]} · 대외지원 {_stf['대외지원팀'][0]}명", [
             "카페 · 공지 채널 콘텐츠 · 카드뉴스 · 영상",
             "모든 게시물은 [[입예협 사전 승인 후]] 게시",
             "사전점검 · 입주설명회 · 정당계약일 부스 지원",
             "입주민 개인정보 · DB는 홍보에 쓰지 않음"])
         + _dcard("4 · 8 · 10", "수요조사 · A/S · 하자 · 민원", "본부장 + 대외지원팀 + 전문 인력", [
             "본부장이 이슈 직접 관리 · 시공사 · 기관 협의 자료 준비 · 동석",
             "전기 · 조명은 전기공사업 등록 업체로 [[직접 검토 · 시공]]",
             "조경 · 도장 · 타일은 사내 자격 · 협회 등록 인력이 [[직접 점검 · 자문]]",
             "업체 부도 · 미시공은 동종업체 이관 · 비용 주관사 부담"])
         + '</div><div class="hflow"><span>입예협 요청</span><i>›</i><span>담당 팀 지정</span><i>›</i><span>기술 · 행정 검토</span><i>›</i>'
           '<span>시공사 · 기관 협의</span><i>›</i><span>회신 · 기록 · 보고</span></div></div>',
    kp=("부서 이름이 아니라 [[누가 무엇을 맡는지]]로 답합니다.", "인원 · 담당은 협약 시 명단 제출 · 외부 협력은 자문 · 촬영 등 전문 업무(재위탁 아님)"))
B.CSS += (".dcx{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;flex:1;min-height:0}"
          ".dcd{border:1px solid var(--line);border-top:2px solid var(--gold2);border-radius:14px;padding:14px 18px;background:linear-gradient(180deg,rgba(235,203,143,.08),rgba(255,255,255,.01) 40%);display:flex;flex-direction:column;gap:4px}"
          ".dcd i{font-style:normal;font-size:12px;font-weight:700;letter-spacing:.2em;color:var(--gold2)}"
          ".dcd h4{font-size:15px;color:var(--sub);font-weight:600}.dcd>b{font-size:21px;color:var(--gold);margin-bottom:4px}"
          ".dcd ul{list-style:none;margin:6px 0 0;padding:0;display:flex;flex-direction:column;gap:12px}"
          ".dcd li{font-size:15.5px;line-height:1.5;padding-left:14px;position:relative}.dcd li:before{content:'';position:absolute;left:0;top:8px;width:6px;height:6px;border-radius:50%;background:var(--gold2)}")

new("std", sec=S0, title=T_PRIV,
    lead="공고 9항 8 · 서식 3 비밀유지 서약서 - 입주예정자 개인정보와 협의회 운영정보를 지킬 기준을 미리 정했습니다.",
    body=B.rows([
        ("수집 최소화", "상담 · 계약에 필요한 정보만, 목적 · 보관기간을 정해 [[별도 동의]]를 받습니다."),
        ("영업 이용 금지", "입주예정자 정보를 영업 · 마케팅 · 광고 · 고객유치에 쓰지 않고, [[DB를 만들거나 판매하지 않습니다.]]"),
        ("제3자 제공 금지", "입예협 사전 서면 승인 없이 참여업체 · 제3자에게 제공하지 않습니다. 필요하면 정보주체 동의를 따로 받습니다."),
        ("참여업체 관리", "참여업체의 개인정보 취급을 주관사가 관리 · 감독하고, 보호 의무를 계약 조건에 넣습니다."),
        ("홍보물 사전 승인", "입예협 명칭 · 로고 · 카페 · 공지 채널은 승인 범위에서만 쓰고, 모든 홍보물은 [[게시 전 승인]]받습니다."),
        ("파기 · 위반 시 조치", "보관기간이 지나면 파기하고, 위반이 확인되면 서식 3에 따른 입찰 · 협약 제외와 손해배상을 받아들입니다."),
    ], title_w=210),
    kp="입주민 명단은 [[업체 영업 명단이 아닙니다.]]")

FLOWX = ('<div class="hflow"><span>한 창구 접수</span><i>›</i><span>유형 분류</span><i>›</i><span>책임 주체 연결</span><i>›</i>'
         '<span>처리 · 회신 추적</span><i>›</i><span>완료 확인 · 정기 보고</span></div>')
B.CSS += (".tbl.lgx td{padding:17px 14px;font-size:16.5px;line-height:1.5}.tbl.lgx td.k{font-size:18px}"
          ".hflow{display:flex;align-items:center;gap:10px;margin-top:18px}.hflow span{flex:1;text-align:center;border:1px solid rgba(200,168,106,.5);"
          "border-radius:10px;padding:12px 8px;font-size:15.5px;font-weight:700;background:rgba(235,203,143,.06)}"
          ".hflow span:last-child{background:var(--gold);color:#0d1e33;border-color:var(--gold)}.hflow i{font-style:normal;color:var(--gold);font-weight:800;font-size:20px}"
          ".tbl.q7 td{padding:11px 14px;font-size:16px;line-height:1.45}.tbl.q7 td.k{font-size:16.5px;width:30%}.tbl.q7 td:last-child{width:22%;white-space:nowrap}"
          ".tbl.q10 td{padding:7.5px 12px;font-size:14.5px;line-height:1.4}.tbl.q10 td.k{font-size:15px;width:30%}.tbl.q10 td:last-child{width:17%;white-space:nowrap}"
          ".tbl.q10 td.n{width:38px}")

new("std", sec=S0, title=T_DEFECT,
    lead="공고 5항 4 · 10 - 접수는 한 곳에서 받고, 처리 책임은 유형별로 나눠 끝까지 추적합니다.",
    body=table(["접수 유형", "예", "처리 책임", "주관사 역할"], "".join(
        f'<tr><td class="k">{a}</td><td>{t(b)}</td><td>{t(c)}</td><td>{t(d)}</td></tr>' for a, b, c, d in [
            ("건설사 시공 · 공용부", "세대 마감 · 설비 하자, 공용부 시설", f"시공사({ST['builder']}) · 사업주체({ST['developer_short']}) 하자 처리 창구", "접수 대행 · 회신 추적 · 현장 확인 지원 · 정기 보고"),
            ("공동구매 납품 · 시공", "박람회에서 계약한 품목의 설치 · 제품 하자", "참여업체 + 주관사 책임(서식 2)", "48시간 하자보수 원칙 · 업체 미응답 시 개입 · 선보상"),
            ("업체 부도 · 미시공", "참여업체 폐업 · 연락 두절 · 시공 중단", "주관사 책임 처리", "동종업체 이관 · A/S 비용 주관사 부담 · 이행보증 · 예치금"),
            ("성능 향상 · 추가 설치", "조경 · 조명 · 집기 개선, 시설 추가", "입예협 · 관리주체 결정 사항", "하자와 구분 · 도면 · 예산 · 운영비 검토 후 추진"),
        ]), "lgx df4") + FLOWX,
    kp=("시공 하자를 [[공동구매 업체에 떠넘기지 않고]], 공동구매 하자를 [[시공사 탓으로 돌리지 않습니다.]]", "접수는 주관 콜센터 · 카카오채널 · 홈페이지 한 창구"))
B.CSS += ".tbl.df4 td{padding:13px 14px}"

RPRIN = ('<div class="rprin">' + "".join(f'<div><b>{a}</b><p>{b}</p></div>' for a, b in [
    ("협의 ≠ 설치", "‘협의 완료’와 ‘설치 완료’를 나눠 표시"),
    ("지연은 사유와 함께", "지연 건은 사유 · 다음 일정을 같이 보고"),
    ("최소 정보", "입예협과 공유할 수 있는 범위로 집계"),
    ("원자료 열람", "입예협이 요청하면 근거 자료를 열람"),
]) + '</div>')
B.CSS += (".rprin{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:16px}.rprin div{border:1px solid rgba(200,168,106,.45);"
          "border-radius:12px;padding:12px 14px;background:rgba(235,203,143,.05)}.rprin b{display:block;font-size:16px;color:var(--gold)}"
          ".rprin p{font-size:13.5px;color:var(--sub);margin-top:4px;line-height:1.45}")

new("std", sec=S0, title=T_REPORT,
    lead="공고 5항 4 · 8항 6 - 결과보고서와 정기 보고에 무엇을 담을지 미리 정했습니다.",
    body=table(["보고", "시점", "담는 내용"], "".join(
        f'<tr><td class="k">{a}</td><td>{t(b)}</td><td>{t(c)}</td></tr>' for a, b, c in [
            ("정례 진행 보고", "입예협 정례회의마다", "진행 상황 · 미결 건의 목록 · 다음 일정 · 시공사 회신 현황"),
            ("하자처리 현황 보고", "입주 후 정기(주기는 입예협과 협의)", "하자 접수 · 처리 완료 · 지연 건과 사유 · 재접수"),
            ("입주박람회 결과보고서", "박람회 종료 후", "[[공동구매 진행현황 · A/S 접수현황 · 하자처리 현황 · 민원처리 결과]]"),
            ("최종 결과 보고서", "입주 후 1년 운영 관리 종료 시", "계약 · 환불 · A/S · 하자 처리 결과 · 하자 예치금 사용 내역"),
        ]), "lgx") + RPRIN,
    kp=("보고서는 입예협과 공유할 수 있는 [[최소 정보]]로 집계합니다.", "개인 연락처 · 동호수는 싣지 않습니다"))

new("std", sec=S0, title=T_MONTHS,
    lead=f"공고부터 입주까지 약 {ST['months']}개월 - 그사이 바뀔 수 있는 것을 미리 약속해 둡니다.",
    body=B.cards([
        dict(lb="FACT", big=str(ST["months"]), unit="개월", nm="공고 ~ 입주", ds="2026.10 공고 → 2029.02 입주 예정. 가격 · 모델 · 업체 사정이 바뀔 수 있어 [[변경 기준]]을 협약에 넣습니다."),
        dict(lb="ANSWER 01", big="정례", nm="정례 진행 보고", ds="입예협 정례회의에 맞춰 진행 상황 · 미결 건의 목록 · 다음 일정을 보고합니다."),
        dict(lb="ANSWER 02", big="대체", nm="업체 · 모델 변경 기준", ds="단종 · 폐업 시 동급 이상 모델 · 대체 업체를 입예협 승인으로 정합니다. 단가 인상은 [[승인 없이 하지 않습니다.]]"),
        dict(lb="ANSWER 03", big="연기", nm="입주 지연 대응", ds="입주 · 사전점검이 늦어지면 박람회 · 시공 일정을 함께 조정하고, 계약 세대에 변경 일정을 개별 안내합니다."),
    ]),
    kp="기간이 길수록 [[변경 기준]]을 먼저 정해 두는 것이 약속입니다.")

new("std", sec=S0, title=T_SCHED,
    lead="입주 2029.02에서 거꾸로 짰습니다. 약 28개월을 ‘대기’가 아니라 ‘준비’로 씁니다.",
    body=B.rows([
        ("2026.10 ~ 11", "PT(대표이사 참석) · 선정 · 협약 · [[정당계약일 부스 지원]](입예협 요청 시) · 카페/공지 채널 지원 시작"),
        ("2026.12 ~ 2027", "유상옵션 일정 · 조건 안내 · [[옵션 선택 여부 설문]] · 정례 진행 보고 · 건의 관리표"),
        ("2028.01 ~ 06", "단지 야간 경관 · 조경 조명 진단 · 품목 시장가 점검 · 행사장 후보 답사(SETEC · aT센터 · 수원메쎄)"),
        ("2028.06 ~ 10", f"[[품목 수요조사]] · 타입별({_types_txt}) 실측 · 참여업체 [[공개 입찰]] · 4단계 심사 → 입예협 컨펌 · 가격 검수 · 카페 공개"),
        ("2028.11 ~ 12", "[[입주박람회 금·토·일 3일]] · 온라인 박람회 오픈 · 사전점검 행사 지원(일정 확정 시)"),
        ("2029.02 ~", "입주 지원 · 하자 접수 창구 → 입주 후 1년 운영 관리 · [[결과 보고서]] (품목 A/S는 최소 2년 · 업체별 상이)"),
    ], title_w=170),
    kp="세부 일정은 사전점검 · 입주지원센터 일정에 맞춰 [[입예협과 확정]]합니다.")

new("std", sec=S0, title=T_EXPO,
    lead="계약을 재촉하는 자리가 아니라, 신혼 가족이 함께 확인하고 비교하는 자리로 만듭니다.",
    body=B.tiles([
        dict(lb="WHEN", nm=f"{ST['expo']} 금·토·일 (안)", ds="입주(2029.02) 2 ~ 3개월 전 3일간, 사전점검 일정에 맞춰 협의회와 확정합니다."),
        dict(lb="WHERE", nm="행사장 후보 3곳", ds="① " + ST["venues"][0] + " ② " + ST["venues"][1] + " ③ " + ST["venues"][2] + " - 입예협과 답사한 뒤 확정합니다."),
        dict(lb="SAFETY", nm="행사(영업)배상책임보험 가입", ds="박람회 개최 전 가입 · 안전요원 · 동선 · 비상구 계획 수립. 화재 · 상해 예방 수칙은 참여업체 서약."),
        dict(lb="FAMILY", nm="놀이방 · 수유실 · 유모차", ds="영유아 가족을 위해 어린이 놀이방 · 수유실 · 유모차 대여와 입구 안내데스크 · 카페테리아를 둡니다."),
        dict(lb="ONLINE", nm="온라인 박람회 · 라이브", ds="단지 입주민만 들어오는 폐쇄몰. 박람회와 같은 공동구매가."),
        dict(lb="PR", nm="카페 · 공지채널 콘텐츠", ds="카드뉴스 · 영상 · 현수막 · 알림톡 - 게시 전 입예협 사전 승인을 받습니다."),
    ], cols=3, rows_n=2).replace('class="tiles"', 'class="tiles lg"'),
    kp="박람회장 가격 = 사전 공개 단가 - [[결제 방식과 관계없이]] 같습니다.")

# ------------------------------------------------------------ 공고 대응표(5항 · 4항 · 9항 · 10항)
SCOPE11 = [  # 공고 5항 주요 업무 범위 1 ~ 11 — (업무, 수행 내용, [PGREF 키])
    ("입주박람회 개최 및 운영 업무 일체", "기획 · 대관 · 배치 · 인원 · 안전 · 홍보 · 금·토·일 3일 · 온라인 박람회", ["expo"]),
    ("품목 구성 · 업체 섭외 · 계약관리 · 가격 및 조건 검수", "수요조사 → 공개 입찰 → 4단계 심사 → 입예협 컨펌 · [[시중가 · 온라인 최저가 검수]]", ["items", "check"]),
    ("상담 · 계약 · 납품 · 시공 · 설치 일정 관리 지원", "세대별 일정 관리표 · 시공 가능 시점 · 관리사무소 신고 확인", ["vmgt"]),
    ("입주 후 A/S · 하자보수 접수 및 이행관리", "주관 콜센터 한 창구 · 48시간 원칙 · 업체 미응답 시 선보상", ["call", "defect"]),
    ("사전점검 · 입주지원 · 입주설명회 등 행사 지원", "행사 인력 · 비품 · 안내물 · 점검 체크리스트 · 세미나 영상", ["support", "pre"]),
    ("대관 · 부스 배치 · 동선 · 안전 · 안내 인력 · 비품 · 홍보물", "후보 답사 · 대관 · 배치도 · 구역별 담당 인원 · 배상책임보험 가입", ["venue", "floor"]),
    ("입예협 카페 · 공지 채널 홍보 · 안내 콘텐츠", "카드뉴스 · 영상 · 안내문 · [[게시 전 입예협 승인]]", ["cafe"]),
    ("품목 · 업체 선정 전 수요조사", "옵션 선택 여부 문항 포함 설문 · 남은 수요 품목만 모집", ["opt"]),
    ("안전사고 예방계획 · 방문객 편의공간", "보안 · 구급 · 119 연계 · 놀이방 · 수유실 · 카페테리아", ["floor", "comfort"]),
    ("참여업체 부도 · 미시공 · 하자 피해 시 민원 · 사후관리", "동종업체 이관 · A/S 비용 주관사 부담 · 이행보증 · 예치금", ["wty", "defect"]),
    ("기타 입예협 요청 업무 (정당계약일 부스 등)", "[[정당계약일 부스 지원]] · 추가 요청은 범위 · 일정 협의 후 협약 반영", ["booth"]),
]
new("std", sec=S0, title=T_SCOPE,
    lead="공고 5항 주요 업무 범위 11개를 빠짐없이 맡고, 각 항목을 제안서의 어느 쪽에서 설명하는지 함께 적었습니다.",
    body=table(["NO", "공고 업무 범위", "엣지컴퍼니 수행 내용", "제안서 쪽"], "".join(
        f'<tr><td class="n">{i:02d}</td><td class="k">{t(a)}</td><td>{t(b)}</td><td class="pg">{PGS(ks)}</td></tr>'
        for i, (a, b, ks) in enumerate(SCOPE11, 1)), "s11"),
    kp="업무 범위가 바뀌어도 [[입예협과 협의해]] 협약서에 그대로 옮깁니다.")

QUAL10 = [  # 공고 4항 입찰 참가자격 1 ~ 10 — (요건, 현황, 증빙)
    ("정상 영업 중인 법인사업자", f"법인 설립 · 개업 {D.FOUNDED} · 사업자등록번호 {D.BIZ_NO} · 공고일 현재 정상 영업", "제출서류 3 · 4"),
    ("등기부상 자본금 1억원 이상", "자본금 [[2억원]] (2026.04 증자 등기)", "제출서류 4"),
    ("입주박람회 · 행사기획 · 전시 관련 업태 · 종목", "종목 ‘전시, 박람회 및 행사 대행업’ · 등기 목적 ‘전시 박람회 사업 · 행사대행업 · 이벤트 기획 및 대행업’", "제출서류 3 · 4"),
    ("법인 · 대표자 · 핵심 인력의 실무 수행경험 · 현장 운영 역량", f"1,000세대 이상 주관 [[{_rec_n}개 단지 · {_rec_hh:,}세대]] · 대표자 · 핵심 운영인력 쪽", "제안서 01장"),
    ("전담 PM과 운영체계 구성", "전담 PM 지정 · 4개 팀 12명 + 대표 · 본부장 · 공고 업무별 담당", "제안서 07장"),
    ("국세 · 지방세 · 4대보험 체납 없음", "체납 없음 - 유효기간 내 완납증명서 제출", "제출서류 5 · 6"),
    ("금품 · 담합 · 중대 위반 · 분쟁으로 해지 · 취소 이력 없음", "해당 없음", "서식 1 · 5"),
    ("계약이행보증보험 등 보증증권 발행 가능", "협약 시 이행보증보험증권 제출(최대 10억 · 2년) · " + TODO("보증보험사 발급 한도 확인"), "협약 시 제출"),
    ("취소 · 환불 기준과 하자 · 분쟁 대응 절차", "계약 취소 · 환불 규정 전문(제1 ~ 10조 · 별표) · 하자 접수 책임 구분", "03장 · 제출서류 8"),
    ("A/S 대책 · 사후보증기간 · 손해배상 이행", "무상 A/S 최소 2년(업체 · 품목별 상이) · 48시간 하자보수 · 하자 예치금 최대 1억 선보상", "04 · 05장 · 서식 2"),
]
new("std", sec=S0, title=T_QUAL,
    lead="공고 4항 입찰 참가자격 10개를 항목마다 현황과 객관적 증빙으로 답합니다.",
    body=table(["NO", "공고 참가자격", "엣지컴퍼니 현황", "증빙"], "".join(
        f'<tr><td class="n">{i:02d}</td><td class="k">{t(a)}</td><td>{t(b)}</td><td>{t(c)}</td></tr>'
        for i, (a, b, c) in enumerate(QUAL10, 1)), "q10"),
    kp="자격은 말이 아니라 [[제출 서류로]] 확인받겠습니다.")

LIMIT10 = [  # 공고 9항 참가 제한 및 무효 1 ~ 10 — (제한 사유, 확인, 근거)
    ("참가자격 미달 · 필수 제출서류 누락", "해당 없음 - 4항 자격 10개 충족 · 7항 제출서류 1 ~ 13 제출(14 선택)", "제출서류 목록"),
    ("접수기간 · 방법 · 파일명 기준 위반", "PDF 이메일 접수 · 공고 양식 메일 제목 · 10.19 정오 전 제출", "공고 3항"),
    ("허위자료 · 위조 · 실적 과장 · 명의대여 · 담합", "해당 없음 - 실적은 NICE 연혁 · 입예협 카페 공지 · BEXCO 행사일정으로 증빙", "서식 1 · 5"),
    ("금품 · 향응 · 사익 제공 제안 · 부당 접근", "해당 없음 - 문의는 공고 지정 이메일로만", "서식 5"),
    ("선정 후 권리 · 의무 임의 위임 · 양도", "하지 않음 - 외부 협력은 자문 · 촬영 등 전문 업무 · 재위탁은 입예협 사전 승인", "공고 10항 6"),
    ("협약 이행 능력 현저 부족", f"자본금 2억 · NICE BB- · 현금흐름 A · 1,000세대 이상 주관 {_rec_n}개 단지", "제출서류 3 ~ 6"),
    ("입예협 분쟁 중 · 타 단지 해지 · 선정 취소 이력", "해당 없음", "서식 1"),
    ("개인정보 무단 수집 · 이용 · 제공 · 목적 외 사용", "해당 없음 - 행사 운영에만 사용", "서식 3"),
    ("대표자 범죄사실확인서 등 서류 검토 결과 문제", "공고 7항 7 대표자 범죄사실확인서 제출", "제출서류 7"),
    ("대표자 · 배우자 · 직계존비속이 본 단지 당첨자", TODO("해당 없음 - 대표 확인 후 확정"), "대표 확인"),
]
new("std", sec=S0, title=T_LIMIT,
    lead="공고 9항 참가 제한 · 무효 사유 10개에 해당하지 않음을 항목마다 확인했습니다.",
    body=table(["NO", "공고 참가 제한 · 무효", "엣지컴퍼니 확인", "근거"], "".join(
        f'<tr><td class="n">{i:02d}</td><td class="k">{t(a)}</td><td>{t(b)}</td><td>{t(c)}</td></tr>'
        for i, (a, b, c) in enumerate(LIMIT10, 1)), "q10"),
    kp=("사유가 [[선정 이후]] 확인되면 선정 · 협약 무효(9항 11)를 받아들입니다.", "허위 기재 · 중요 사항 누락 시 협약 취소(10항 10) 포함"))

NOTE7 = [  # 공고 6항 · 10항 · 서식 — (공고, 약속)
    ("10항 2 · 미확정 혜택 금지", "혜택은 [[확정 · 이행 가능한 것]]만, 조건과 함께 적었습니다. 참여업체가 정해져야 하는 항목은 ‘(안)’ · ‘참가 협의 중’으로 표기했습니다."),
    ("6항 · PT 발표", "제출한 제안 조건을 [[바꾸거나 추가 혜택을 얹지 않습니다.]] 대표이사가 참석해 질의에 직접 답합니다."),
    ("10항 3 · 공정 경쟁", "담합 · 응찰 포기 유도 · 특정 업체 낙찰을 위한 사전 합의를 하지 않습니다(서식 5)."),
    ("10항 6 · 재위탁 · 양도 금지", "입예협 사전 승인 없이 본 사업의 권리 · 의무를 제3자에게 넘기지 않습니다."),
    ("10항 7 · 품목 · 가격 사전 협의", "품목과 가격은 입예협과 사전 협의한 뒤 확정합니다."),
    ("서식 4 · 패찰 시 영업 금지", "선정되지 않으면 이 단지 대상 별도 박람회 · 사전예약 · 방문판매 · 온라인 단체영업을 하지 않습니다(조명 · 커튼 · 실링팬 사업부 포함)."),
    ("10항 4 · 10 · 성실 이행", "불이행 시 계약 해지, 허위 기재 · 중요 사항 누락이 확인되면 협약 취소를 받아들입니다."),
]
new("std", sec=S0, title=T_NOTE,
    lead="공고 6항 · 10항 유의사항과 서식 1 ~ 5 서약을 제안서 내용에 그대로 반영했습니다.",
    body=table(["공고", "엣지컴퍼니 약속"], "".join(
        f'<tr><td class="k">{t(a)}</td><td>{t(b)}</td></tr>' for a, b in NOTE7), "nt7"),
    kp=("제안서에 쓴 조건 그대로 [[PT에서도, 협약서에서도]] 같습니다.", "서식 1 ~ 5 서약서 제출"))
B.CSS += ".tbl.nt7 td{padding:15px 14px;font-size:16px;line-height:1.5}.tbl.nt7 td.k{width:25%;font-size:16.5px;color:var(--ink);font-weight:700}"

# ------------------------------------------------------------ 01장으로 보낼 장(공고 8항 1 · 2)
B.CSS += r"""
.hist{flex:1;min-height:0;display:grid;grid-template-columns:1fr 1fr;gap:0 34px}
.hist ol{list-style:none;margin:0;padding:0;position:relative;display:flex;flex-direction:column;justify-content:space-between}
.hist ol:before{content:'';position:absolute;left:92px;top:8px;bottom:8px;width:2px;background:linear-gradient(180deg,var(--gold2),rgba(200,168,106,.25))}
.hist li{position:relative;display:grid;grid-template-columns:76px 1fr auto;gap:0 34px;align-items:center;padding:6px 0}
.hist li:before{content:'';position:absolute;left:88px;top:50%;width:10px;height:10px;margin-top:-5px;border-radius:50%;background:#0d1e33;border:2px solid var(--gold2)}
.hist li.k:before{background:var(--gold);box-shadow:0 0 8px rgba(235,203,143,.55)}
.hist li b{font-size:17px;font-weight:800;color:var(--gold);font-variant-numeric:tabular-nums}
.hist li span{font-size:17px;line-height:1.4}
.hist li.k span{font-weight:700}
.hist li i{font-style:normal;font-size:11.5px;color:var(--mute);border:1px solid rgba(255,255,255,.18);border-radius:99px;padding:1px 8px;white-space:nowrap}
"""
_key = ("설립", "등록", "ISO", "MOU")


def _keep1(x):  # '주관 · 1,643세대'는 한 줄로
    return re.sub(r"(주관 · [\d,]+세대)", r'<span style="white-space:nowrap">\1</span>', _h.escape(x))


_items = [f'<li class="{"k" if any(k in x for k in _key) else ""}"><b>{d}</b><span>{_keep1(x)}</span><i>{src}</i></li>' for d, x, src in D.HISTORY]
_half = (len(_items) + 1) // 2
new("std", sec=S0, title=T_HIST,
    lead=f"공고 8항 1 - 법인 설립({D.FOUNDED})부터 지금까지, 등기부 · 등록증 · 인증서 · NICE 연혁 · 협약으로 확인되는 기록만 적었습니다.",
    body=f'<div class="nb"><div class="hist"><ol>{"".join(_items[:_half])}</ol><ol>{"".join(_items[_half:])}</ol></div></div>',
    kp=("2023년부터 [[해마다]] 1,000세대 이상 입주박람회를 맡아 왔습니다.",
        "출처: 법인등기부 · 전기공사업 등록증 · ISO 인증서 · NICE 기업신용평가보고서 연혁 · 세스코 협약"))

_songdo = next(r for r in D.RECORDS if "송도" in r[1])
_lead_n = getattr(D, "STAFF_LEAD", 2) + sum(c for _, c, _ in D.STAFF)
PRO5 = [("전기", 3), ("도장", 2), ("타일", 1), ("조경", 1), ("간호사", 1)]
new("std", sec=S0, title=T_PEOPLE,
    lead="공고 8항 2 · 4항 4 - 대표자와 핵심 운영인력이 직접 맡아 온 현장과, 분당 퍼스트빌리지에서 맡을 역할입니다.",
    body=('<div class="nb"><div class="ppx">'
          '<div class="pp1"><i>대표이사</i><h3>고진식</h3><ul>'
          '<li>대표이사 · 대표자 본인 명의 법인(공고 4항)</li>'
          f'<li>엣지컴퍼니 1,000세대 이상 입주박람회 주관 <b>{_rec_n}개 단지 · {_rec_hh:,}세대</b> 총괄</li>'
          '<li>PT · 질의응답 직접 참석(공고 6항) · 협약 서명</li>'
          f'<li>{TODO("대표 개인 경력 · 주요 현장 - 확인 후 기재")}</li></ul></div>'
          '<div class="pp1"><i>주관사업 총괄 본부장 · 전담 총괄</i><h3>총괄 본부장</h3><ul>'
          f'<li>{ST["short"]} 총괄 책임 · 직통 <span style="white-space:nowrap">{D.MANAGER[2]}</span></li>'
          f'<li>{_songdo[1]}({_songdo[0]} 입주 · {_songdo[3]:,}세대) <b>현장 직접 주관</b></li>'
          '<li>입예협 정례회의 · 박람회 · 사전점검 현장 참석 · 이슈 직접 관리</li>'
          f'<li>{TODO("본부장 경력 연수 · 주요 현장 - 확인 후 기재")}</li></ul></div>'
          '<div class="pp2"><i>핵심 운영인력</i><h3>임직원 ' + str(_lead_n) + '명</h3>'
          + "".join(f'<div><b>{c}<small>명</small></b><span>{n}</span><p>{t(r)}</p></div>' for n, c, r in D.STAFF)
          + '<div class="pro2">' + "".join(f'<span>{f} {c}</span>' for f, c in PRO5) + '<em>자격 · 협회 등록 인력 · 2026.10 기준</em></div></div>'
          '</div><div class="ppb">'
          f'<div><b>{_rec_n}<small>개 단지</small></b><span>1,000세대 이상 주관<br>2023.04 ~ 2026.09 입주</span></div>'
          f'<div><b>{_rec_hh:,}<small>세대</small></b><span>1,000세대 이상<br>주관 세대 합계</span></div>'
          '<div><b>4,470<small>세대</small></b><span>단일 단지 최대<br>레이카운티</span></div>'
          '<div><b>67<small>개 단지</small></b><span>누적 주관 · 수임 56,361세대<br>(전신 실적 · 입주 예정 포함)</span></div>'
          '</div></div>'),
    kp=("박람회 경험은 회사 이름이 아니라 [[현장을 맡은 사람]]에게 있습니다.", "팀별 담당은 협약 시 명단 제출 · 실적 증빙은 제출서류(NICE 연혁 · 카페 공지 · BEXCO 행사일정)"))
B.CSS += (".ppx{display:grid;grid-template-columns:1fr 1fr 1.25fr;gap:16px;flex:1;min-height:0}"
          ".ppx>div{border:1px solid var(--line);border-top:2px solid var(--gold2);border-radius:14px;padding:14px 18px;display:flex;flex-direction:column;min-height:0;"
          "background:linear-gradient(180deg,rgba(235,203,143,.08),rgba(255,255,255,.01) 45%)}"
          ".ppx i{font-style:normal;font-size:12px;letter-spacing:.14em;color:var(--gold2);font-weight:700}"
          ".ppx h3{font-size:26px;font-weight:800;color:var(--gold);margin:2px 0 10px}"
          ".pp1 ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:11px}"
          ".pp1 li{font-size:15px;line-height:1.5;padding-left:14px;position:relative}.pp1 li:before{content:'';position:absolute;left:0;top:8px;width:6px;height:6px;border-radius:50%;background:var(--gold2)}"
          ".pp1 li b{color:var(--gold)}"
          ".pp2>div:not(.pro2){display:grid;grid-template-columns:54px 92px 1fr;gap:8px;align-items:center;padding:5px 0;border-bottom:1px dashed rgba(255,255,255,.12)}"
          ".pp2>div b{font-size:24px;font-weight:800;color:var(--gold);line-height:1}.pp2>div b small{font-size:12px;margin-left:1px}"
          ".pp2>div span{font-size:15px;font-weight:700}.pp2>div p{font-size:12.5px;color:var(--sub);line-height:1.4}"
          ".pro2{margin-top:auto;display:flex;flex-wrap:wrap;gap:6px;align-items:center;padding-top:8px}"
          ".pro2 span{font-size:12.5px;font-weight:700;border:1px solid rgba(200,168,106,.55);border-radius:99px;padding:3px 10px;color:var(--gold)}"
          ".pro2 em{font-style:normal;font-size:11px;color:var(--mute)}"
          ".ppb{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid rgba(200,168,106,.5);border-radius:12px;background:rgba(235,203,143,.05)}"
          ".ppb>div{padding:9px 16px;border-left:1px solid rgba(200,168,106,.25)}.ppb>div:first-child{border-left:0}"
          ".ppb b{font-size:26px;font-weight:800;color:var(--gold);line-height:1.1;white-space:nowrap}.ppb b small{font-size:13px;margin-left:2px}"
          ".ppb span{display:block;font-size:12.5px;color:var(--sub);line-height:1.35;margin-top:2px}")

# 계약 취소 · 환불 규정 전문(공고 4항 9 · 8항 5 · 6) — 제안서 03장에 2쪽으로 싣는다. 제출서류 8(방안서)과 같은 기준.
T_RULE1 = "계약 취소 · 환불 규정 [[전문]] ① 제1 ~ 5조"
T_RULE2 = "계약 취소 · 환불 규정 [[전문]] ② 제6 ~ 10조 · 별표"
_C7 = "청소·줄눈, 탄성코트, 유리막코팅, 선반·잡물, 음식물처리기, 인덕션, 벽걸이TV, LED조명"
_C15 = "미세방충망, 인테리어, 단열필름, 시스템에어컨, 포장이사"
_CU = "커튼·블라인드, 중문, 안전방충망, 맞춤가구"
_ARTS1 = [
    ("제1조 (목적)", [f"이 규정은 {D.COMPANY}(이하 ‘주관사’)가 주관하는 {ST['name']} 입주박람회 및 공동구매에서 입주예정자(이하 ‘계약자’)와 참여업체 사이에 체결되는 계약의 계약금·잔금 지급 조건과 취소·환불 기준을 정하여 계약자의 권리를 보호함을 목적으로 한다."]),
    ("제2조 (적용 범위)", ["공동구매를 통해 체결된 모든 품목의 계약에 적용한다. 박람회 현장 계약과 온라인 박람회(폐쇄몰) 계약을 모두 포함한다.",
                       "참여업체는 이 규정을 계약서에 반영하고 계약 체결 전에 계약자에게 설명하여야 한다.",
                       "브랜드 본사 직영 품목(가전·가구 등), 렌탈·보험·통신, 사전점검 대행은 각 본사 계약 규정을 따르되, 그 내용을 계약 전에 서면으로 고지하여야 한다."]),
    ("제3조 (계약금)", [f"계약금은 계약 총액의 <b>{D.DEPOSIT_MAX}% 이하</b>로 한다(계약금 {D.DEPOSIT_MAX}% 상한제).",
                     "계약금과 잔금 모두 카드 결제 시 현금가와 <b>동일한 가격</b>을 적용하며(결제 방식에 따른 단가 변동 없음), 현금 결제 시 현금영수증을 발행한다."]),
    ("제4조 (잔금 지급 조건)", ["잔금은 <b>시공·설치가 끝나고 계약자가 확인한 후</b> 지급한다. 제품만 납품하는 품목은 납품·설치 확인 후 지급한다.",
                          "참여업체가 입찰 때 약속한 기대매출을 넘긴 경우의 실적 비례 추가할인은 잔금에서 차감한다. 품목별 할인율은 입예협과 검토해 정한다.",
                          "시공 결과 확인 시 하자·미시공 부분이 있으면 계약자는 해당 부분의 보수가 끝난 후 잔금을 지급할 수 있다."]),
    ("제5조 (취소·환불 기준)", ["품목별 취소 가능 기한은 [별표]와 같다. 기한 안에 취소하면 납부한 금액 <b>전액</b>을 환불한다.",
                          f"맞춤 제작 품목({_CU})은 출고 지시 전까지 참여업체와 협의하여 취소한다. 브랜드 가전·가구는 미제작·출고 지시 전에는 전액 취소·환불한다.",
                          "참여업체가 사전 해피콜을 이행하지 않은 경우, 계약자 미동의 주문제작 건을 포함한 <b>모든 품목은 당일 취소·환불</b>할 수 있다(공급사 귀책).",
                          "인테리어는 시공일 15일 전까지 취소할 수 있으며, 세부 조건은 참여업체가 계약 전에 서면으로 고지하여야 한다.",
                          "취소 기한이 지난 뒤의 취소는 실제 발생한 자재·제작 비용만 공제할 수 있으며, 참여업체는 공제 내역을 서면으로 제시하여야 한다. 주관사는 공제 내역의 적정성을 검토한다.",
                          "시공 지연, 계약과 다른 제품·시공, 하자 미보수 등 참여업체 귀책으로 계약을 해지하는 경우에는 기한과 관계없이 납부 금액 전액을 환불한다."]),
]
_ARTS2 = [
    ("제6조 (취소 신청 및 환급)", ["취소는 참여업체 또는 주관사 콜센터 · 공식카페 신문고 · 카카오채널로 신청하며, 문자·메신저 등 기록이 남는 방법으로 한다.",
                            "환불금은 취소 확정일로부터 <b>3영업일 이내</b>에 지급하고, 카드 결제분은 같은 기한 안에 승인 취소한다.",
                            "주관사는 환불 완료 여부를 계약자에게 확인(해피콜)한다."]),
    ("제7조 (불이행 시 조치 및 주관사 책임)", ["참여업체가 취소·환불을 지연하거나 거부하면 계약자는 주관사 콜센터에 접수할 수 있다. 주관사는 사실을 확인한 뒤 계약자에게 피해 금액을 <b>먼저 보상</b>하고, 참여업체와는 계약 조항에 따라 정산한다(하자보수 및 사후관리 이행각서 [서식 2] 준용).",
                                  "불이행 업체에는 1단계 홍보정지, 2단계 총액 10% 배상, 3단계 자격박탈 및 입예협 승인을 받아 전 계약을 대체업체로 이관하는 패널티를 차례로 부과한다.",
                                  "참여업체가 도산한 경우 동종업체로 사후관리를 이관하고, 그 A/S 비용은 주관사가 전액 부담한다.",
                                  "주관사의 보상 재원으로 하자 예치금 최대 1억원(엣지컴퍼니 자산으로 예치)과 이행보증보험(2년 · 최대 10억원)을 둔다."]),
    ("제8조 (가격 보호 — 최저가 차액 10배 보상)", [f"공동구매 품목과 브랜드·모델명이 같은 새 제품이 계약 후 7일 이내에 인근({ST['local']}) 오프라인 매장에서 더 낮은 정상 판매가로 판매된 사실이 견적서·영수증으로 확인되면, 참여업체는 차액의 10배를 보상하고 판매가를 조정한다.",
                                         "온라인·홈쇼핑 판매, 시공 품목, 카드 청구할인·사은품·결합할인, 전시·리퍼 상품, 법인 특판, 한정 수량 행사가는 비교 대상에서 제외한다.",
                                         "계약자는 주관사 콜센터에 접수하고, 주관사는 사실 확인 후 7일 이내에 보상이 이행되도록 관리한다."]),
    ("제9조 (고지)", ["주관사는 이 규정을 박람회장 · 온라인 박람회에 게시하고, 입주예정자협의회 카페에는 입예협 승인 후 게시하며, 모든 공동구매 계약서에 첨부한다."]),
    ("제10조 (효력)", ["이 규정은 협약 체결일부터 협약 종료일(입주 후 1년)까지 체결된 계약에 적용하며, 협약 종료 후에도 해당 계약의 이행·보증 기간 동안 효력을 가진다."]),
]


def _arts(arts):
    out = ""
    for h, items in arts:
        if len(items) == 1:
            out += f'<div class="art"><h4>{h}</h4><p>{items[0]}</p></div>'
        else:
            out += f'<div class="art"><h4>{h}</h4><ol>' + "".join(f"<li><i>{'①②③④⑤⑥⑦⑧'[i]}</i><span>{x}</span></li>" for i, x in enumerate(items)) + "</ol></div>"
    return out


new("std", sec=S0, title=T_RULE1,
    lead="공고 4항 9 · 8항 5 · 6 - 참여 품목별 계약 취소 및 환불 규정입니다. 모든 공동구매 계약서에 이 규정을 첨부합니다.",
    body=f'<div class="rgl">{_arts(_ARTS1)}</div>',
    kp=("기한 안 취소는 [[전액 환불]], 업체 귀책이면 [[기한과 관계없이]] 전액 환불합니다.", "세부 품목 기한은 다음 장 [별표] · 제출서류 8 방안서와 같은 기준"))
new("std", sec=S0, title=T_RULE2,
    lead="환불 절차 · 주관사 책임 · 가격 보호와 품목별 취소 가능 기한[별표]입니다.",
    body=f'<div class="rgl">{_arts(_ARTS2)}<div class="art bt"><h4>[별표] 품목별 취소 가능 기한 (시공일 기준)</h4>'
         '<table class="rtb"><tbody>'
         f'<tr><td>시공일 7일 전까지</td><td>{_C7}</td></tr>'
         f'<tr><td>시공일 15일 전까지</td><td>{_C15}</td></tr>'
         f'<tr><td>출고 지시 전까지</td><td>맞춤 제작 품목({_CU})은 업체와 협의 후 취소 · 브랜드 가전·가구(미제작 시)</td></tr>'
         '<tr><td>본사 규정 품목</td><td>렌탈 · 보험 · 통신 · 사전점검 대행 · 브랜드 본사 직영 품목 - 각 본사 계약 규정(계약 전 서면 고지)</td></tr>'
         '<tr><td>당일 취소</td><td>사전 해피콜 미이행 시 모든 품목(공급사 귀책)</td></tr>'
         '</tbody></table><p class="rn">※ 품목 구성은 입예협 수요조사 결과에 따라 확정되며, 추가 품목의 기한은 성격이 같은 품목의 기한을 따릅니다.</p></div></div>',
    kp=("환불은 [[3영업일 이내]], 업체가 미루면 [[주관사가 먼저 보상]]합니다.", "협약 체결일부터 입주 후 1년까지 체결된 계약에 적용"))
B.CSS += (".rgl{flex:1;min-height:0;column-count:3;column-gap:24px;column-fill:balance;column-rule:1px solid rgba(255,255,255,.08)}"
          ".rgl .art{margin:0 0 9px}.rgl .art h4{break-after:avoid}.rgl li{break-inside:avoid}"
          ".rgl h4{font-size:14px;font-weight:800;color:var(--gold);margin:0 0 3px}"
          ".rgl p,.rgl li{font-size:12px;line-height:1.46;color:var(--sub)}"
          ".rgl ol{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:2px}"
          ".rgl li{display:grid;grid-template-columns:16px 1fr;gap:2px}.rgl li i{font-style:normal;color:var(--gold2)}"
          ".rgl b{color:var(--ink)}"
          ".rgl .rtb{width:100%;border-collapse:collapse;margin-top:2px}"
          ".rgl .art.bt{break-inside:avoid}.rgl .rtb td{font-size:11.8px;line-height:1.4;padding:5px 6px;border-bottom:1px solid var(--line);color:var(--sub);vertical-align:top}"
          ".rgl .rtb td:first-child{color:var(--ink);font-weight:700;white-space:nowrap;width:34%}"
          ".rgl .rn{font-size:11.5px;color:var(--mute);margin-top:5px}")


# 발전지원 15만원 ≠ 공구가 인상 — 참가비 정액·판매 수수료 없음 + 입예협 가격 검증
T_SEP = f"세대당 {D.FUND}만원 상당, [[공구가와 따로]]입니다"
new("std", sec=S0, title=T_SEP,
    lead=f"‘{D.FUND}만원 상당을 주면 공구가가 오르지 않느냐’는 질문에 구조로 답합니다 - 발전지원은 주관사 몫에서 나가고, 공구가는 입예협이 직접 검증합니다.",
    body=('<div class="sepx"><div class="sepf">'
          '<div class="sb1"><i>업체</i><b>참가비 정액제</b><span>업체 참가비는 정액으로 - 공구가와 연동하지 않음</span></div><em>›</em>'
          '<div class="sb1 hl"><i>주관사</i><b>운영비 + 발전지원</b><span>박람회 운영비와 세대당 ' + str(D.FUND) + '만원 상당을 주관사 몫에서 부담</span></div><em>›</em>'
          '<div class="sb1"><i>입예협 · 입주민</i><b>혜택 패키지</b><span>패키지 A·B·C 또는 입예협 지정 · 사용 내역 공개</span></div></div>'
          '<div class="sepn">공구가는 이 흐름과 따로 - <b>업체 공개 입찰 경쟁</b>과 <b>시중가 · 온라인 최저가 검수</b>로 정해집니다</div>'
          + B.tiles([
              dict(lb="01 · 정액", nm="참가비 정액제", ds="업체 참가비는 정액으로 받습니다. 발전지원을 공구가에 얹는 구조가 아닙니다."),
              dict(lb="02 · 공개", nm="단가표 사전 공개", ds="박람회 전 품목별 단가 · 할인율 · 모델코드를 입예협이 검수합니다. 현장 가격 변경 없음."),
              dict(lb="03 · 검증", nm="시중가 · 온라인 최저가 비교", ds="같은 조건 총액으로 비교하고, 입예협이 품목을 골라 직접 확인합니다."),
              dict(lb="04 · 보상", big="10", unit="배", nm="최저가 차액 보상", ds="동일 브랜드·동일 제품이 더 싸면 차액의 10배 보상. (온라인 판매·시공 품목 제외)"),
          ], cols=4) + '</div>'),
    kp=(f"발전지원을 0원으로 해도 공구가는 같습니다 - 가격은 [[업체 경쟁과 가격 검수]]로 정해집니다.", "참가비 정액제 · 카드·현금 동일가 · 최저가 차액 10배(온라인·시공 품목 제외)"))
B.CSS += (".sepx{flex:1;min-height:0;display:flex;flex-direction:column;gap:14px}"
          ".sepf{display:grid;grid-template-columns:1fr 30px 1.15fr 30px 1fr;align-items:stretch}"
          ".sepf em{display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:800;color:var(--gold)}"
          ".sepf .sb1{border:1px solid var(--line);border-radius:14px;padding:16px 18px;display:flex;flex-direction:column;gap:4px}"
          ".sepf .sb1.hl{border-color:rgba(235,203,143,.7);background:linear-gradient(180deg,rgba(235,203,143,.14),rgba(235,203,143,.03))}"
          ".sepf i{font-style:normal;font-size:12px;letter-spacing:.18em;color:var(--gold2);font-weight:700}"
          ".sepf b{font-size:21px;font-weight:800}.sepf span{font-size:14.5px;color:var(--sub);line-height:1.45}"
          ".sepn{border:1px dashed rgba(200,168,106,.6);border-radius:10px;padding:10px 16px;font-size:15.5px;color:var(--sub);text-align:center}"
          ".sepn b{color:var(--gold)}")


CPL = [  # 공고 8항 6 — 입주민 컴플레인 예시와 처리 기준(본 제안서의 약속과 같은 기준)
    ("커튼 · 블라인드", "설치일에 치수가 맞지 않음", "재실측 → 재제작 → 재방문 설치 · 비용은 업체 부담", "48시간 내 재실측"),
    ("입주청소", "청소 상태 미흡(창틀·욕실)", "사진 접수 → 업체 재청소 → 입주민 확인 서명", "48시간 내 재방문"),
    ("시스템에어컨 · 설치 품목", "배관 누수 · 작동 불량", "방문 점검 · 수리 → 업체 미응답 시 주관사가 먼저 보상 후 업체 정산", "48시간 하자보수 원칙"),
    ("업체 사정", "참여업체 폐업 · 연락 두절", "이행보증·하자 예치금으로 대체 업체 연결 · A/S 승계", "주관사 책임 처리"),
    ("가격", "박람회가보다 싼 판매 확인", "동일 브랜드·동일 제품 확인 → 최저가 차액 10배 보상(온라인 판매·시공 품목 제외)", "규정 기준 지급"),
    ("계약 취소", "시공 전 취소 요청", "품목별 취소 기한 확인 → 위약금 없이 환불", "3영업일 내 환불"),
]
new("std", sec=S0, title=T_CPL,
    lead="공고 8항 6 - 박람회 뒤 자주 생기는 컴플레인 예시와 처리 기준, 타 단지 해결 사례입니다. 접수부터 완료까지 주관 콜센터가 기록합니다.",
    body=table(["품목", "컴플레인 예시", "해결 방법", "처리 기준"], "".join(
        f'<tr><td class="k">{a}</td><td>{t(b)}</td><td>{t(c)}</td><td>{t(d)}</td></tr>' for a, b, c, d in CPL), "sm")
         + '<div class="hflow"><span>접수 · 콜센터 · 카카오</span><i>›</i><span>업체 연결</span><i>›</i><span>기한 추적</span><i>›</i>'
           '<span>미응답 시 주관사 선보상</span><i>›</i><span>완료 확인 · 결과 보고</span></div>'
         + '<div class="gcase"><div class="gch"><i>해결 우수 사례</i><b>타 단지 실제 응대</b><span>원문 캡처는 다음 장</span></div>'
           '<div><i>입주민 카페 글 · 2024.10</i><b>A/S · 하자 즉시 처리</b><span>주관사와 청소 업체가 함께 처리 - 입주민이 카페에 감사 글을 남김</span></div>'
           '<div><i>단지 단톡방</i><b>입주 전날 긴급 재청소 연결</b><span>외부 업체 청소 뒤 생긴 문제도 입주 전날 재청소 업체를 연결</span></div>'
           '<div><i>타 단지 협의회</i><b>업체 응대 공유 · 감사 인사</b><span>업체 응대 내용을 협의회와 공유 - 협의회 측이 감사 인사를 전함</span></div></div>',
    kp=("컴플레인은 [[기한 안에 끝까지]] - 처리 결과를 입예협 결과보고서에 담습니다.", "처리 기준은 본 제안서 03 · 04 · 05장과 같습니다"))
B.CSS += (".gcase{display:grid;grid-template-columns:1fr 1.25fr 1.25fr 1.25fr;gap:10px;margin-top:16px}"
          ".gcase>div{border:1px solid var(--line);border-radius:11px;padding:11px 14px;display:flex;flex-direction:column;gap:3px}"
          ".gcase .gch{border-color:rgba(235,203,143,.6);background:rgba(235,203,143,.08);justify-content:center}"
          ".gcase i{font-style:normal;font-size:11px;letter-spacing:.12em;color:var(--gold2);font-weight:700}"
          ".gcase b{font-size:16px;font-weight:800}.gcase .gch b{font-size:18px;color:var(--gold)}"
          ".gcase span{font-size:13.5px;color:var(--sub);line-height:1.45}")

new("std", sec=S0, title="공동구매 단가를 지키는 [[4가지 장치]]",
    lead="‘행사비 때문에 오르는 단가’를 구조로 막습니다.",
    body=B.cards([
        dict(lb="01", big="공개", nm="단가표 사전 공개", ds="박람회 전 품목별 단가·할인율을 입예협에 제출해 검수받습니다. 현장 가격 변경 없음."),
        dict(lb="02", big="10", unit="배", nm="최저가 차액 보상", ds="동일 브랜드·동일 제품이 더 싸면 차액의 10배 보상. (온라인 판매·시공 품목 제외)"),
        dict(lb="03", big="추가할인", nm="실적 비례 추가할인", ds="업체 기대매출을 넘기면 계약 세대 잔금에서 추가할인. 할인율은 업체 입찰 조건으로 입예협과 확정."),
        dict(lb="04", big=str(D.DEPOSIT_MAX), unit="%", nm="계약금 상한", ds=f"계약금은 총액의 {D.DEPOSIT_MAX}% 이하, 잔금은 시공·설치 후. 현금·카드 동일가."),
    ]),
    kp="가격은 말이 아니라 [[사전 공개 단가 + 최저가 보장]]으로 검증받습니다.")

# 대응표 쪽 번호 — 재배치 뒤 제목으로 찾는다(reorg에서 바뀐 제목은 바뀐 뒤 제목)
PGREF = {
    "num": "숫자로 보는 [[엣지컴퍼니]]", "hist": T_HIST, "succ": "주관 [[성공사례]] · 수임실적", "big": "[[대단지]] 운영 경험",
    "people": T_PEOPLE, "org": "회사 [[조직 구성]] · 분당 전담 배치 (안)",
    "expo": T_EXPO, "venue": "행사장 대관과 [[운영 준비]]", "floor": "박람회장 배치와 [[인원 운영]] (안)", "comfort": "가족이 머무는 [[편의시설]]",
    "items": T_ITEMS, "opt": T_OPT, "vendors": T_VENDORS, "vmgt": T_VMGT, "screen": "[[4단계]] 공개 심사 프로세스",
    "one": T_ONE, "fund": "세대당 15만원 상당, [[혜택 패키지]]로 드립니다", "sep": T_SEP, "guard4": "공동구매 단가를 지키는 [[4가지 장치]]",
    "safe3": "입주민을 지키는 [[3중 안전망]]", "defect": T_DEFECT, "cpl": T_CPL, "rule1": T_RULE1, "wty": "참여업체 [[하자보증]] 체계",
    "support": T_SUPPORT, "booth": T_BOOTH, "req": T_REQ, "pkb": "B 패키지 · [[협의회 단지발전지원]]",
    "check": T_CHECK, "x10": "[[최저가 차액 10배]] 보상",
    "pm": T_PM, "call": "주관 [[콜센터]]와 선보상", "crm": "클레임 [[처리 흐름]]과 CRM 관리",
    "pre": "사전점검 당일 [[현장 지원]]", "cafe": "입예협 카페 [[홍보 콘텐츠]] 제작", "map": T_MAP,
}
PGNO = {}


# ============================================================ 기존 장 고치기
def walk(v, f):
    if isinstance(v, str):
        return f(v)
    if isinstance(v, list):
        return [walk(x, f) for x in v]
    if isinstance(v, tuple):
        return tuple(walk(x, f) for x in v)
    if isinstance(v, dict):
        return {k: walk(x, f) for k, x in v.items()}
    return v


def bump(kind, kw):
    """기존 01~07장 → 02~08장."""
    kw = dict(kw)
    if kind == "divider":
        kw["n"] = f"{int(kw['n']) + 1:02d}"
    if "sec" in kw:
        kw["sec"] = re.sub(r"^0(\d)\.", lambda m: f"0{int(m.group(1)) + 1}.", kw["sec"])
    return kw


def find(title_part):
    hits = [i for i, (k, kw) in enumerate(B.PAGES) if title_part in kw.get("title", "")]
    exact = [i for i in hits if B.PAGES[i][1].get("title") == title_part]
    hits = exact or hits
    assert len(hits) == 1, (title_part, hits)
    return hits[0]


# 실적 장 — 제출서류 8)과 같은 숫자(NICE 연혁)로
i = find("성공사례")
# 연도별 카드 = 확인된 단지 목록의 입주 연도 누적(본부장 10-07: 근거 없는 12·15·18·25 → 누적 방식)
_cum = {y: (d, nd) for y, d, _, nd, _ in D.cumulative()}
B.PAGES[i][1]["body"] = B.cards([
    dict(lb="~2022", big=str(_cum["2022"][1]), unit="곳", nm="누적 단지", ds="양산 이지더원 2차 1,768 등"),
    dict(lb="2023", big=str(_cum["2023"][1]), unit="곳", nm=f"누적 단지 · +{_cum['2023'][0]}", ds="레이카운티 4,470 등"),
    dict(lb="2024", big=str(_cum["2024"][1]), unit="곳", nm=f"누적 단지 · +{_cum['2024'][0]}", ds="센트럴사하 1,643 등"),
    dict(lb="2025", big=str(_cum["2025"][1]), unit="곳", nm=f"누적 단지 · +{_cum['2025'][0]}", ds="양정자이 1·2단지 2,272 등"),
    dict(lb="2026", big=str(_cum["2026"][1]), unit="곳", nm=f"누적 단지 · +{_cum['2026'][0]}", ds="오션시티 2,813 등"),
    dict(lb="2027 예정", big=str(_cum["2027"][1]), unit="곳", nm=f"누적 단지 · +{_cum['2027'][0]}", hl=True, ds="상생공원 1·2단지 2,667 등"),
], cols=3)
total = sum(r[3] for r in D.RECORDS)
B.PAGES[i][1]["kp"] = f"2023년 이후 1,000세대 이상 주관 [[{len(D.RECORDS)}건 · {total:,}세대]]"

i = find("[[대단지]] 운영 경험")
big9 = sorted([(d[:4], n, nm) for d, nm, _, n in D.RECORDS]
              + [("2024", 1712, "사송 데시앙 1차"), ("2023", 1572, "사상중흥 S-클래스")], key=lambda r: -r[1])
B.PAGES[i][1]["body"] = B.tiles([dict(lb=y, big=f"{n:,}", unit="세대", nm=nm) for y, n, nm in big9], cols=3, rows_n=3)
B.PAGES[i][1]["kp"] = "최근 5년, 1,000세대 이상 단지만 모아도 [[이 정도]]입니다."

# 현장 베이스캠프 장 삭제(본부장님 지시) — 04장 구분페이지 항목도 교체
del B.PAGES[find("현장 [[베이스캠프]] 구축")]
for k, kw in B.PAGES:
    if k == "divider" and "현장 베이스캠프" in kw.get("bl", []):
        kw["bl"] = [x if x != "현장 베이스캠프" else "콜센터 · 선보상" for x in kw["bl"]]

# 16p 본사 사옥: 본사 사옥 → 자본금 → 현금흐름 → ISO 순
i = find("[[본사 사옥]] 운영 · 자본금 2억")
B.PAGES[i][1]["body"] = B.media("assets/사옥.jpg", "엣지컴퍼니 본사 사옥 · 본사/쇼룸 운영", [
    ("본사 사옥 운영", "사옥에서 본사·쇼룸·시공팀을 직접 운영합니다."),
    ("자본금 2억원", "하자 예치금·이행보증의 재원이 되는 실체입니다."),
    ("현금흐름 A · 부채비율 17.1% / 신용 BB-", "NICE 기업신용평가(2026.06.19). 입예협 제출 증빙 즉시 발급 가능."),
    ("ISO 9001·14001·45001", "품질·환경·안전보건 국제표준 3종 인증 보유."),
])

# 19p 공인된 자격과 신뢰: A → BB- → MOU → ISO 순, 키포인트 교체(4대보험 문구는 18p 발췌 장으로)
i = find("공인된 [[자격과 신뢰]]")
B.PAGES[i][1]["body"] = B.cards([
    dict(lb="CASH FLOW", big="A", nm="현금흐름 등급", ds="박람회 운영 중 자금 흐름 안정성 검증."),
    dict(lb="CREDIT", big="BB-", nm="기업 신용등급", ds="공인 평가기관 기업신용평가 등급."),
    dict(lb="PARTNERSHIP", big="MOU", nm="삼성전자 · 세스코 MOU", ds="세스코 MOU 2025.11 체결. LX하우시스·에몬스와 제휴 추가 협의 중."),
    dict(lb="ISO", big="3", unit="종", nm="국제표준 인증", ds="ISO 9001 · 14001 · 45001."),
])
B.PAGES[i][1]["kp"] = "재무 평가 · 대기업 제휴 · 국제표준 인증 — [[공인 기관이 검증한 항목]]만 적었습니다."

# 22p 지사망: 직영 4곳 + 협력 8곳 = 전국 12개 지사망(2026.10 확정). 대전→청주 순, 특정 지사 부각 없음.
i = find("전국 지사망")
B.PAGES[i][1]["title"] = "전국 지사망 · [[직영 4곳 + 협력 8곳]]"
B.PAGES[i][1]["lead"] = "직영 거점 4곳에 협력 네트워크 8곳을 더해 전국 12개 지사로 운영합니다."
B.PAGES[i][1]["body"] = B.cards([
    dict(lb="BRANCH 01", big="대전", nm="대전 지사", ds="충청권 거점."),
    dict(lb="BRANCH 02", big="청주", nm="충북 청주 지사", ds="충북 거점."),
    dict(lb="BRANCH 03", big="울산", nm="울산 본사", ds="본사·사옥·쇼룸. 시공팀 상주."),
    dict(lb="BRANCH 04", big="부산", nm="부산 해운대 지사", ds="해운대 거점. 부산·경남 단지를 직접 운영합니다."),
    dict(lb="NETWORK", big="8", unit="곳", nm="협력 네트워크", ds="직영 4곳 + 협력 8곳 = 전국 12개 지사망.", hl=True),
], cols=5)

# 45p 지역업체 키포인트
i = find("[[지역업체 90%]] 선정 원칙")
B.PAGES[i][1]["kp"] = "가까운 업체가 맡아야 [[48시간 A/S가 실제로 지켜집니다.]]"

# 74p 운영 일정: 2차 박람회·베이스캠프 문구 삭제
i = find("행사는 [[운영]]이 전부입니다")
B.PAGES[i][1]["body"] = sub(B.PAGES[i][1]["body"], "주말 양일 개최, 2차 박람회 협의.", "주말 양일 개최.")
B.PAGES[i][1]["kp"] = "행사 후에도 콜센터·CRM이 [[계속 돌아갑니다.]]"

# 입증하기 어려운 표현 정리(공고 9항 3 허위·실적 과장 · 10항 2 확정되지 않은 혜택 금지)
i = find("정회원 전용")
B.PAGES[i][1]["lead"] = "공동구매가에 더해지는 정회원 전용 혜택입니다."

# 검증(10-08) 반영: 기본틀 문구 덮어쓰기
for _i, (_k, _kw) in enumerate(B.PAGES):
    for _f in ("body", "lead"):
        _v = _kw.get(_f)
        if isinstance(_v, str):
            _v = _v.replace("상담 콜센터 · 공식카페 신문고 · 카카오채널 · 홈페이지. 365일 운영.",
                            "상담 콜센터 · 공식카페 신문고 · 카카오채널 · 홈페이지. 온라인 접수 365일 · 콜센터 평일 09:00 ~ 18:00.")
            _v = _v.replace("사업자등록증·재무제표·완납증명서·예치금 통과 업체만 입점.",
                            "사업자등록증·재무제표·완납증명서·보증증권 발행 확인 업체만 입점.")
            _v = _v.replace('<div class="nm">사업자·재무·예치금</div>', '<div class="nm">사업자·재무·보증증권</div>')
            _v = _v.replace("조경 감리 관점에서", "사내 조경 전문 인력(임원)이")  # 본부장 10-12: 조경은 사내 직접
            _kw[_f] = _v
# 재개발: 협의 상대는 입예협·시공사
i = find("[[조경·착공]] 분석보고서")
kw = B.PAGES[i][1]
kw["lead"] = sub(kw["lead"], "시공사와 협상할 때", "입예협이 시공사와 협의할 때")
kw["body"] = sub(kw["body"], "시공사 협상 자리에", "입예협·시공사 협의 자리에")

# 순서: 표지 · 목차 · [01 신설] · 기존(번호 +1)
old = [(k, bump(k, kw)) for k, kw in B.PAGES]
B.PAGES[:] = old[:2] + NEW + old[2:]

# 통합제안서 기본틀 발췌(액자·현장·추천서 등 '그대로 보여주는' 장) — (뒤에 붙일 장 제목, [(기본틀 index, 라벨)])
INSERTS = [
    ("[[본사 사옥]] 운영", [(7, "회사 개요 · [[사업자등록증 · 법인등기부]]"), (8, "[[4대보험 명부 · 납세증명 · 기업신용평가]] 원본",
                              "4대보험 증명원 · 납세증명 · 기업신용평가서 — [[원본 스캔으로 첨부]]합니다.")]),
    ("공인된 [[자격과 신뢰]]", [(15, "[[삼성전자 MOU]] 체결서"), (12, "[[ISO 9001 · 14001 · 45001]] 인증서")]),
    ("전국 지사망", [(18, "엣지컴퍼니 전국 지사")]),
    ("[[커뮤니티 시설]] 업그레이드", [(122, "아파트 문주 · [[경관조명 컨설팅]] 사례")]),
    ("참여업체 [[하자보증]] 체계", [(55, "[[특약이행각서]] · 업체 도산 시 처리"), (56, "주요 클레임 품목 · [[품목별 보상 규정]]")]),
    ("주관 [[콜센터]]와 선보상", [(59, "주관 콜센터 프로세스")]),
    ("[[4단계]] 공개 심사 프로세스", [(43, "입주박람회 공동구매 품목 리스트")]),
    ("협의회 전용 [[8가지 무상 단지지원]]", [(103, "공용부 [[철근탐지 · 콘크리트 강도]] 측정"), (115, "[[열화상 드론]] 점검"), (120, "[[라돈 무료측정]] 지원")]),
    ("입주 전부터 [[끝까지]]", [(113, "사전점검 당일 협의회 지원 서비스")]),
    ("정회원 전용", [(78, "정회원 전용 혜택 14종")]),
    ("하루가 [[즐거운]] 박람회", [(72, "박람회 편의시설")]),
    ("못 오셔도 [[괜찮습니다]]", [(98, "타입별 실측 · 샘플하우스")]),
    ("한 단지가 아니라 [[한 신도시]]", [(27, "양산 [[사송신도시]] 주관 현황"), (28, "부산 [[에코델타시티]] 주관 현황")]),
    ("행사는 [[운영]]이 전부입니다", [(32, "현장 지원 — [[간식차 · 입주 기념 점등식]]"), (34, "타 단지 협의회 · 파트너 [[추천서]]"), (35, "타 단지 협의회 [[감사패]]")]),
]
for after_title, pages in INSERTS:
    i = find(after_title)
    sec = B.PAGES[i][1].get("sec", "")
    B.PAGES[i + 1:i + 1] = [("std", dict(sec=sec, title=INS, lead=None, kp=(rest[0] if rest else None),
                                        body=f'<div class="ins-h"><h1>{t(lb)}</h1><span>통합제안서 발췌</span></div>'
                                             f'<div class="ins"><img src="assets_full/p{idx:03d}.jpg" alt=""></div>'))
                            for idx, lb, *rest in pages]


# ============================================================ 네이티브 페이지(pages21.json)
# 통합제안서에서 가져온 장을 사진만 살려 새로 조판한다. 스펙은 pages21.json, 사진은 crop.py → assets_ins/
NATIVE_JSON = os.path.join(HERE, "pages21.json")


def _sty(b):
    g = b.get("grow")
    return f' style="flex:{g} 1 0;min-height:0"' if g else ""


def blk(b):
    k = b["type"]
    if k == "photos":
        cols, rows_n = b.get("cols", len(b["items"])), b.get("rows")
        rs = f";grid-template-rows:repeat({rows_n},1fr)" if rows_n else ""
        figs = ""
        for it in b["items"]:
            cls = "ct" if (it.get("fit") or b.get("fit")) == "contain" else ""
            span = ";".join(x for x in [f'grid-column:span {it["span"]}' if it.get("span") else "",
                                        f'grid-row:span {it["rspan"]}' if it.get("rspan") else ""] if x)
            span = f' style="{span}"' if span else ""
            cap = ""
            if it.get("cap"):
                sub_ = f'<small>{t(it["sub"])}</small>' if it.get("sub") else ""
                cap = f'<figcaption>{t(it["cap"])}{sub_}</figcaption>'
            pos = f' style="object-position:{it["pos"]}"' if it.get("pos") else ""  # 사진 초점(선택)
            figs += f'<figure class="{cls}"{span}><img src="assets_ins/{it["img"]}.jpg"{pos} alt="">{cap}</figure>'
        g = b.get("grow", 1)
        return f'<div class="gal" style="grid-template-columns:repeat({cols},1fr){rs};flex:{g} 1 0">{figs}</div>'
    if k == "docs":
        ds = "".join(f'<div class="d"><div class="pp"><img src="assets_ins/{it["img"]}.jpg" alt=""></div>'
                     f'<div class="cap">{t(it["cap"])}' + (f'<small>{t(it["sub"])}</small>' if it.get("sub") else "")
                     + "</div></div>" for it in b["items"])
        return f'<div class="docs"{_sty(b)}>{ds}</div>'
    if k == "bullets":
        return f'<div class="bulx"{_sty(b)}>' + "".join(
            f'<div><b>{t(it["t"])}</b>' + (f'<p>{t(it["d"])}</p>' if it.get("d") else "") + "</div>"
            for it in b["items"]) + "</div>"
    if k == "rows":
        return B.rows([(it["t"], it["d"]) for it in b["items"]], title_w=b.get("title_w", 230))
    if k == "cards":
        return B.cards(b["items"], cols=b.get("cols"))
    if k == "tiles":
        return B.tiles(b["items"], cols=b.get("cols", 3), rows_n=b.get("rows"))
    if k == "table":
        w = b.get("widths") or [None] * len(b["head"])
        th = "".join((f'<th style="width:{x}">' if x else "<th>") + f"{t(h)}</th>" for h, x in zip(b["head"], w))
        trs = ""
        for r in b["rows"]:
            tds = []
            for j, c in enumerate(r):
                cls = "k" if j == 0 and b.get("key_col", True) else ""
                tds.append(f'<td class="{cls}">{t(c)}</td>')
            trs += "<tr>" + "".join(tds) + "</tr>"
        return f'<table class="tbl {"sm" if b.get("small") else ""}"{_sty(b)}><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>'
    if k == "flow":
        parts = []
        for i, st in enumerate(b["steps"]):
            if i:
                parts.append('<div class="ar">›</div>')
            parts.append(f'<div class="st{" hl" if st.get("hl") else ""}"><i>{t(st.get("lb", f"STEP {i + 1:02d}"))}</i>'
                         f'<b>{t(st["t"])}</b>' + (f'<p>{t(st["d"])}</p>' if st.get("d") else "") + "</div>")
        return f'<div class="flowx"{_sty(b)}>{"".join(parts)}</div>'
    if k == "tags":
        gold = set(b.get("gold", []))
        sp = "".join(f'<span class="{"g" if x in gold else ""}">{t(x)}</span>' for x in b["items"])
        return f'<div class="tagx"{_sty(b)}>' + (f'<h4>{t(b["title"])}</h4>' if b.get("title") else "") + f'<div class="tg">{sp}</div></div>'
    if k == "quote":
        return f'<div class="bigq"{_sty(b)}><b>{t(b["t"])}</b>' + (f'<p>{t(b["d"])}</p>' if b.get("d") else "") + "</div>"
    if k == "note":
        return f'<div class="notex">{t(b["text"])}</div>'
    if k == "split":
        L = "".join(blk(x) for x in b["left"])
        R = "".join(blk(x) for x in b["right"])
        return f'<div class="splitx" style="grid-template-columns:{b.get("cols", "1fr 1fr")}">' \
               f'<div>{L}</div><div>{R}</div></div>'
    if k == "stack":
        return f'<div class="stackx"{_sty(b)}>' + "".join(blk(x) for x in b["blocks"]) + "</div>"
    raise ValueError(f"알 수 없는 블록: {k}")


def native_page(spec):
    body = '<div class="nb">' + "".join(blk(b) for b in spec["body"]) + "</div>"
    kp = spec.get("kp")
    if isinstance(kp, list):
        kp = tuple(kp)
    return ("std", dict(sec=spec.get("sec", ""), title=spec["title"], lead=spec.get("lead"), body=body, kp=kp))


def load_native():
    """pages21.json: [{after: 기존 장 제목, replaces: [통합제안서 index...], pages: [spec...]}] — 해당 발췌 장을 대체."""
    if not os.path.exists(NATIVE_JSON):
        return
    with open(NATIVE_JSON, encoding="utf-8") as f:
        groups = json.load(f)
    for g in groups:
        drop = set(g.get("replaces", []))
        # 이 그룹이 대체하는 발췌 장(INS) 제거
        keep = []
        for k, kw in B.PAGES:
            if kw.get("title") == INS and any(f"assets_full/p{i:03d}.jpg" in kw.get("body", "") for i in drop):
                continue
            keep.append((k, kw))
        B.PAGES[:] = keep
        if g.get("remove_titles"):
            B.PAGES[:] = [(k, kw) for k, kw in B.PAGES if kw.get("title") not in set(g["remove_titles"])]
        i = find(g["after"])
        sec = B.PAGES[i][1].get("sec", "")
        new_pages = []
        for spec in g["pages"]:
            spec = dict(spec)
            spec.setdefault("sec", sec)
            new_pages.append(native_page(spec))
        B.PAGES[i + 1:i + 1] = new_pages
        NATIVE[g["group"]] = [kw for _, kw in new_pages]


NATIVE = {}  # 그룹 id → 그 그룹이 만든 장(kw dict) — 덱 정리 때 위치 이동용
if not os.environ.get("NO_NATIVE"):
    load_native()
    import polish  # noqa: E402  (중복 정리·순서·문구 — polish.py)
    polish.apply(globals())
    # 수임 단지 전체(본부장 목록 10-07) — 08장 대단지 장 뒤, 입주 연월 최신순 3열(입주 전 = 입주 예정)
    # 정렬(본부장 10-07): 1,000세대 이상은 세대수 많은 순 → 나머지는 입주 오래된 순
    _rows = (sorted([r for r in D.SUIM if r[1] >= 1000], key=lambda r: -r[1])
             + sorted([r for r in D.SUIM if r[1] < 1000], key=lambda r: r[3]))
    _now = "2026.10"
    _li = "".join(f'<li class="{"big" if n >= 1000 else ""}{" fut" if m > _now else ""}"><span>{nm} <i>{m}{" 예정" if m > _now else ""}</i></span>'
                  f'<b>{n:,}{u}</b></li>' for nm, n, u, m in _rows)
    _cols = [f"<ul>{_li}</ul>"]
    _n1k = sum(1 for r in _rows if r[1] >= 1000)
    _nfut = sum(1 for r in _rows if r[3] > _now)
    _di = next(i for i, (_, k) in enumerate(B.PAGES) if k.get("title") == "[[대단지]] 운영 경험")
    B.PAGES.insert(_di + 1, ("std", dict(sec=B.PAGES[_di][1].get("sec", ""), title=f"2023년 이후 수임 단지 [[{sum(D.DANJI_N.get(r[0], 1) for r in _rows)}곳]]",
        lead="1,000세대 이상(금색)은 세대수 순, 나머지는 입주 순 · 날짜는 입주 연월(입주 전은 예정월).",
        body='<div class="ylist">' + "".join(_cols) + "</div>",
        kp=(f"{sum(D.DANJI_N.get(r[0], 1) for r in _rows)}개 단지 · 1,000세대 이상 [[{_n1k}곳]] · 입주 예정 [[{_nfut}곳]] 진행 중",
            "공식 단지명·총세대수 기준 · 양정자이더샵SK VIEW 1·2단지는 2개 단지로 집계"))))
    # 2,000세대 이상 초대형 단지 강조(본부장 지시 10-07, 통합제안서 대단지 장 참고) — 성공사례 장 바로 뒤
    _big = [("n02_raycounty_v2", "레이카운티", 4470, "2023.11 입주", "부산 거제2구역 재개발", "단일 단지 최대 규모"),
            ("n02_oceancity_v2", "두산위브더제니스 오션시티", 2813, "2026.01 입주", "부산 우암2구역 재개발", "대단지 입주 운영"),
            ("n02_yangjung_v2", "양정자이더샵SK VIEW 1·2단지", 2272, "2025.01 입주", "부산진구 양정동", "3개 건설사 컨소시엄 단지")]
    _cards = "".join(
        f'<div class="bc"><div class="ph"><img src="assets_ins/{im}.jpg" alt=""><span class="tg">{tag}</span></div>'
        f'<div class="pn"><div class="n">{n:,}<small>세대</small></div><div class="nm">{nm}</div>'
        f'<div class="ds">{mv} · {ds}</div></div></div>' for im, nm, n, mv, ds, tag in _big)
    _sum = sum(r[2] for r in _big)
    _band = ('<div class="bband">'
             f'<div><i>2,000세대 이상</i><b>{len(_big)}<small>곳</small></b></div>'
             f'<div><i>3개 단지 합계</i><b>{_sum:,}<small>세대</small></b></div>'
             '<div><i>단일 단지 최대</i><b>4,470<small>세대</small></b></div>'
             '<div class="nx"><i>다음 대단지 · 2027.09 입주 예정</i><b>2,667<small>세대</small></b><p>힐스테이트 더샵 상생공원 1·2단지</p></div></div>')
    _si = next(i for i, (_, k) in enumerate(B.PAGES) if k.get("title") == "주관 [[성공사례]] · 수임실적")
    B.PAGES.insert(_si + 1, ("std", dict(sec=B.PAGES[_si][1].get("sec", ""), title="[[2,000세대 이상]] 초대형 단지를 맡아 왔습니다",
        lead="단일 단지 4,470세대까지 — 대단지 박람회는 규모가 아니라 운영 시스템으로 치릅니다.",
        body='<div class="nb"><div class="bigx">' + _cards + "</div>" + _band + "</div>",
        kp=(f"2,000세대 이상 대단지를 이끈 경험을 {D.SITE['name']} [[{D.SITE['households']:,}세대]]에 그대로 옮깁니다.",
            "사진은 조감·외관 이미지"))))
    # 핵심 혜택 한 장(본부장 지시 10-07: 표지 수치 대신 뒤쪽에 임팩트 있게) — 마무리 약속 장 바로 앞
    _ci = next(i for i, (k, _) in enumerate(B.PAGES) if k == "closing")
    _hh = D.FUND_HH
    B.PAGES.insert(_ci, ("std", dict(sec=B.PAGES[_ci][1].get("sec", ""), title=T_CORE6,
        lead="숫자로 약속하고, 협약서로 지킵니다.",
        body=B.tiles([
            dict(lb="발전지원금", big=f"{D.FUND}", unit="만원", nm="세대당 발전지원금",
                 ds=f"{_hh:,}세대 기준 총 {_hh * D.FUND // 10000}억 {_hh * D.FUND % 10000:,}만원 (부가세 포함)"),
            dict(lb="하자 예치금", big="1", unit="억원", nm="현금 예치", ds="엣지컴퍼니 자산으로 입예협 공동통장에 직접 예치"),
            dict(lb="이행보증보험", big="10", unit="억원", nm="2년 보증", ds="증권 실물을 입예협에 전달"),
            dict(lb="최저가 보장", big="10", unit="배", nm="차액 보상", ds="동일 브랜드·동일 제품이 더 싸면 차액의 10배 보상. (온라인 판매·시공 품목 제외)"),
            dict(lb="입예협 지원", big="8", unit="가지", nm="무상 단지지원", ds="사전점검 지원·라돈측정·도면 분석 등 자체 인력"),
            dict(lb="정회원 혜택", big="60", unit="만원 상당", nm="세대당 혜택", ds="정회원 박람회 방문 세대 전용"),
        ], cols=3, rows_n=2).replace('class="tiles"', 'class="tiles lg"'),
        kp="모든 혜택은 [[협약서에 그대로 옮겨]] 끝까지 이행합니다.")))


HERO = "\x00HERO"  # 전면 사진 장(요약본 경관조명) — body가 본문 전체


def render_std(no, sec, title, lead, body, kp):
    if title == HERO:
        return f"""<section class="page hero">{body}
<div class="hd"><div class="l"><span class="logo">EG</span><span class="sec">{sec}</span></div>
<div class="r">{B.QUOTE} &nbsp;·&nbsp; {no:02d}</div></div>
<div class="ct"></div>
{(f'<div class="kp"><b>KEY POINT</b><span>{t(kp[0])}<small>{t(kp[1])}</small></span></div>' if isinstance(kp, tuple) else f'<div class="kp"><b>KEY POINT</b><span>{t(kp)}</span></div>') if kp else ''}
<div class="ft"><span>주식회사 엣지컴퍼니</span><span>EDGE COMPANY</span></div>
</section>"""
    if title != INS:
        return B_render_std(no, sec, title, lead, body, kp)
    return f"""<section class="page">
<div class="hd"><div class="l"><span class="logo">EG</span><span class="sec">{sec}</span></div>
<div class="r">{B.QUOTE} &nbsp;·&nbsp; {no:02d}</div></div>
{body}
{f'<div class="kp"><b>KEY POINT</b><span>{t(kp)}</span></div>' if kp else ''}
<div class="ft"><span>주식회사 엣지컴퍼니</span><span>EDGE COMPANY</span></div>
</section>"""


B_render_std = B.render_std
B.render_std = render_std


def render_full_pages(src_pdf):
    """통합제안서 기본틀 PDF에서 발췌 장을 JPEG로 렌더(assets_full/). 이미 있으면 건너뜀."""
    import pymupdf as fitz
    need = sorted({it[0] for _, pages in INSERTS for it in pages})
    os.makedirs(FULL_DIR, exist_ok=True)
    missing = [i for i in need if not os.path.exists(os.path.join(FULL_DIR, f"p{i:03d}.jpg"))]
    if not missing:
        return
    assert src_pdf and os.path.exists(src_pdf), "통합제안서 기본틀 PDF 경로를 --full <pdf> 로 주세요 (발췌 장 렌더용)"
    doc = fitz.open(src_pdf)
    for i in missing:
        doc[i].get_pixmap(dpi=FULL_DPI, clip=fitz.Rect(*FULL_CLIP_OVR.get(i, FULL_CLIP))).save(os.path.join(FULL_DIR, f"p{i:03d}.jpg"), jpg_quality=88)
    print(f"발췌 {len(missing)}장 렌더 → {FULL_DIR}")


# ============================================================ 특수 페이지
COVER = dict(kind="stats", pill="입주박람회 주관사 제안서",
             tag=f"박람회를 여는 회사가 아니라, 단지를 완성시키는 회사.<br>{D.SITE['households']:,}세대의 입주를 입주 후 1년까지 책임지겠습니다.")
TITLE_H1 = "e편한세상<br>분당 퍼스트빌리지<br><em>입주박람회 주관사 제안서</em>"
COVER_TOP = """<div class="top"><div><div class="logo">EG</div><div class="en">EDGE COMPANY</div></div>
<div class="who">주식회사 엣지컴퍼니<br>입주박람회 전문 주관사</div></div>"""


def p_cover():
    sub2 = f'<div class="sub2"><div><i>제출처</i><b>{D.CLIENT}</b></div><div><i>제안사</i><b>{D.COMPANY}</b></div></div>'
    # 조감도(본부장 제공 예정) — 네이비 배경에 스며들도록 위·왼쪽을 배경색으로 페이드. 파일이 없으면 남색 자리표시(finish)
    art = ('<div class="cvart tj"><img src="assets_ins/bd_cover.jpg" alt="">'
           f'<span class="credit">{D.SITE["name"]} 조감도 · 실제와 다를 수 있음</span></div>')
    return f"""<section class="page cv cv4">{art}{COVER_TOP}
<div class="mid"><span class="pill">{COVER['pill']}</span>
<h1 class="tj">{TITLE_H1}</h1>
<div class="gbar"></div>
<div class="tag2">{COVER['tag']}</div>
</div>
{sub2}
<div class="bt"><span>입주박람회 주관사 제안서</span><span>2026.10</span></div>
</section>"""


TOC4 = [
    [("01", "분당 퍼스트빌리지 맞춤 제안", ["공고 필수 9항목 대응표", "신혼희망타운 품목", "가격 검수 · 비교 한 장", "업무 11 · 자격 10"]),
     ("02", "회사 역량", ["실적·성장", "인증·재무", "지사망", "직영 운영"])],
    [("03", "조명 특화", ["경관조명 컨설팅", "직수입·생산·KC·시공", "공용부 조명·단지 업그레이드"]),
     ("04", "안전망", ["예치금 1억·보증 10억", "업체 하자보증·패널티", "클레임 보상 규정", "콜센터·선보상"])],
    [("05", "업체선정", ["4단계 심사·업체 교육", "인근 지역업체 90%", "단가 보호·차액 10배", "계약·환불 보호"]),
     ("06", "입예협 지원", [f"발전지원금 {D.FUND}만원", "8가지 무상 지원", "도면·하자 분석보고서", "사전점검·온라인 위임장"])],
    [("07", "입주민 혜택", ["상품권·현장 혜택", "정회원 혜택", "사전점검 대행", "편의시설·사은품"]),
     ("08", "주관 실적", ["수임실적·단지 갤러리", "신도시 연속 운영", "박람회 현장·사회공헌"])],
]


TOC_CLS = "toc4"


def p_toc(no):
    B.TOC = TOC4
    html = B_p_toc(no)
    return sub(html, 'class="toc"', f'class="toc {TOC_CLS}"').replace("요약제안서 <em>목차</em>", "제안서 <em>목차</em>")


B_p_toc = B.p_toc


def p_contact():
    s = B_p_contact()
    # 지사: 직영 4곳 + 협력 8곳 = 전국 12개 지사망(2026.10 확정). 본사 주소는 사업자등록증(2026.08.04) 기준.
    s = sub(s, "울산 본사 · 울산광역시 울주군 청량읍 상남1길 28, 2동 &nbsp;|&nbsp; 부산 지사 · 해운대구 &nbsp;|&nbsp; 대전 지사<br>",
            f"울산 본사 · {D.ADDRESS}<br>대전 지사 · 디펠리체 204호 &nbsp;|&nbsp; 청주 지사 · 청주시 흥덕구 직지대로 642 &nbsp;|&nbsp; "
            "부산 해운대 지사 · 해운대구 아르파나 B1<br>직영 4곳 + 협력 8곳 = 전국 12개 지사망 · 콜센터 평일 09:00–18:00 · 온라인 365일 접수 · 24시간 이내 회신<br>")
    s = sub(s, "삼성전자 MOU 체결</div>", "삼성전자 · 세스코 MOU 체결</div>")
    s = sub(s, '<div class="who">주식회사 엣지컴퍼니<br>대표이사 고진식</div>', "")
    s = sub(s, '<div class="addr">', '<div class="addr" style="font-size:14.2px">')
    label = f"입주박람회 주관사 선정 · {D.SITE['name']}"
    return sub(s, "SUMMARY PROPOSAL · 요약제안서", label)


B_p_contact = B.p_contact


def won(man):
    """만원 → '2억 1,199만원'"""
    eok, rest = divmod(man, 10000)
    if not eok:
        return f"{rest:,}만원"
    return f"{eok}억 {rest:,}만원" if rest else f"{eok}억원"


def p_hi_fund(no, sec):
    hh = D.FUND_HH
    n = hh * D.FUND  # 만원
    s = B_p_hi_fund(no, sec)
    s = sub(s, '<span class="v">15만원</span>', f'<span class="v">{D.FUND}만원</span>')
    s = sub(s, "세대수 × 15만원 규모의 발전지원금을 협의회와 협의해 집행합니다.",
            f"<em>공고 단지 전 세대 {hh:,}세대</em>를 기준으로 지급하고, <em>입예협 공식 통장</em>으로 입금합니다.")
    s = sub(s, "<span>현금성 지원</span>", "<span>현금성 지원 · 입예협 공식 통장 입금 가능</span>")  # 본부장 10-07
    return sub(s, "예: 1,000세대 단지 기준 <em>1억 5천만원</em>의 발전지원 규모.",
               f"{hh:,}세대 × {D.FUND}만원 = <em>총 {won(n)}</em>(부가세 포함)의 발전지원 규모.")


B_p_hi_fund = B.p_hi_fund


def p_hi_money(no, sec):
    s = B_p_hi_money(no, sec)
    s = sub(s, "타 주관사는 <em>참여 업체에게 받은 돈</em>으로 예치합니다.<br>엣지컴퍼니는 <em>주관사 순수 자산</em>으로 직접 깔아둡니다.",
            "참여 업체에게 걷은 돈이 아니라, <em>엣지컴퍼니 자산</em>으로 직접 예치합니다.<br>업체가 빠져도 예치금은 줄지 않습니다.")  # 타사 일반화 비교 삭제
    return sub(s, "<span>법무법인 송달 지연 없음</span>", "<span>사용 내역 공개</span>")


B_p_hi_money = B.p_hi_money


def p_pricing(no, sec):
    """사전점검 가격표 — 기본틀 그대로(STANDARD 35% · 14,500 → 9,450원, 본부장 10-08 재확정). 평당가는 2026.06 기준 소비자가."""
    s = B_p_pricing(no, sec)
    # 카드 위: 점검 인원(아이콘) + 정가→할인가 막대(축 25,000원 = 100%, 카드 숫자 그대로)
    import vis
    P = vis.ic("person")
    tiers = [(P * 2, 13500, 6750), (P * 3, 14500, 9450), (P * 3 + "<em></em>" + P * 2 + "<small>1차 + 2차</small>", 25000, 16250)]
    it = iter(tiers)

    def pv(m):
        pp, a, b = next(it)
        return (m.group(0) + f'<div class="pv"><div class="pp">{pp}</div>'
                f'<div class="r"><span>정가</span><i style="width:{100 * a / 25000:.0f}%">{a:,}원</i></div>'
                f'<div class="r g"><span>할인가</span><i style="width:{100 * b / 25000:.0f}%">{b:,}원</i></div></div>')
    s, n = re.subn(r'<div class="card">', pv, s)
    assert n == 3, n
    return sub(s, '</div></div></div>\n<div class="kp">',
               '</div></div></div>\n<div class="notex" style="margin-top:14px">※ 평당 가격은 2026년 6월 기준 기본 소비자가이며, 변동될 수 있습니다.</div>\n<div class="kp">')


B_p_pricing = B.p_pricing
B.p_pricing = p_pricing


def p_closing(no, sec):
    n = D.FUND_HH * D.FUND
    items = [(f"세대당 {D.FUND}만원 발전지원금", f"전 세대 {D.FUND_HH:,}세대 기준 · 총 {won(n)}(부가세 포함)"),
             ("하자 예치금 1억 · 이행보증보험 10억", "엣지컴퍼니 자산으로 공동통장 예치 · 증권 실물 제출"),
             ("입예협 전용 8가지 무상 지원", "별도 비용 없음 · 자체 인력"),
             ("유상옵션 중복 확인 · 가격 공개표", "유상옵션과 겹치는 품목 사전 확인 · 시공비·추가금 포함 공개"),
             ("시공 품목 인근 지역업체 90% 선정", "48시간 A/S가 가능한 거리"),
             ("최저가 차액 10배 보상", "온라인 판매·시공 품목 제외 · 단가표 사전 공개 · 현장 가격 변경 없음"),
             ("48시간 하자보수 · 무상 A/S 최소 2년", "업체·품목별 기간 상이 · 장기관리 최대 10년 · 접수 365일 · 24시간 내 회신"),
             ("경관조명 컨설팅 · 설계 · 생산 · 직접시공", "전기공사업 면허 기반 직접 시공 · KC 인증 제품")]
    its = "".join(f'<div class="it"><div class="no">{i:02d}</div><div><b>{B.html.escape(a)}</b><p>{B.html.escape(b)}</p></div></div>'
                  for i, (a, b) in enumerate(items, 1))
    return B.render_std(no, sec, "엣지컴퍼니가 [[약속드리는 것]]", "제안서에 쓴 것은 전부 협약서와 증빙으로 남깁니다.",
                        f'<div class="cl">{its}</div>', "제안서의 약속은 [[협약서에 그대로 옮겨]] 끝까지 이행하겠습니다.")


B_p_divider_lx = B.p_divider_lx


def p_bars(no, sec, title, lead, data, kp):
    """누적 7개 막대(2021~2027 예정) — 칸 수와 '곳' 단위."""
    s = B_p_bars(no, sec, title, lead, data, kp)
    s = sub(s, 'class="bars"', 'class="bars b7"')
    return re.sub(r'<div class="v">(\d+)</div>', r'<div class="v">\1<small>곳</small></div>', s)


B_p_bars = B.p_bars
B.p_bars = p_bars
B.p_cover, B.p_toc, B.p_contact, B.p_hi_fund, B.p_closing = p_cover, p_toc, p_contact, p_hi_fund, p_closing
B.p_hi_money = p_hi_money
B.p_divider_lx = lambda: sub(B_p_divider_lx(), '<div class="n">02</div>', '<div class="n">03</div>')


if not os.environ.get("NO_NATIVE"):
    import reorg  # noqa: E402  (목차 10장 재배치 · 15만원 현금/패키지 선택 · 특화서비스 요약 — reorg.py)
    reorg.apply(globals())


def p_toc_bd(no):
    """목차 아래 띠: 공고 8항 필수 9항목 대응표 쪽(평가위원이 목차에서 바로 찾도록)."""
    s = p_toc(no)
    band = (f'<div class="kp"><b>KEY POINT</b><span>공고 8항 필수 9항목 대응표 · <em>{PG("map")}</em>'
            '<small>공고 4항 자격 · 5항 업무 범위 · 9항 제한 · 10항 유의사항 대응은 07장</small></span></div>')
    return sub(s, '<div class="ft">', band + '\n<div class="ft">')


B.p_toc = p_toc_bd

CLOSING_DROP = []  # 요약본에서 뺄 약속 번호


def p_closing_drop(no, sec):
    s = B_p_closing_full(no, sec)
    if not CLOSING_DROP:
        return s
    for n in CLOSING_DROP:
        s, k = re.subn(rf'<div class="it"><div class="no">{n}</div><div><b>.*?</b><p>.*?</p></div></div>', "", s, flags=re.S)
        assert k == 1, n
    cnt = iter(range(1, 20))
    s = s.replace('<div class="cl">', f'<div class="cl" style="grid-template-rows:repeat({(8 - len(CLOSING_DROP) + 1) // 2},1fr)">')
    return re.sub(r'<div class="no">\d+</div>', lambda m: f'<div class="no">{next(cnt):02d}</div>', s)


B_p_closing_full = B.p_closing
B.p_closing = p_closing_drop


# ============================================================ 빌드
# 카드·타일 정렬: 같은 줄의 카드 중 내용이 가장 긴 카드를 세로 가운데에 두고,
# 나머지 카드는 그 시작 높이에 맞춰 위로 정렬 → 라벨·숫자·제목·설명 첫 줄이 가로로 일치
ALIGN_JS = """<script>
(function(){
function align(){
  document.querySelectorAll('.cards,.tiles').forEach(function(box){
    var items=[].slice.call(box.children).filter(function(c){return c.classList.contains('card')||c.classList.contains('tile');});
    var rows={};
    items.forEach(function(c){var k=Math.round(c.getBoundingClientRect().top);(rows[k]=rows[k]||[]).push(c);});
    Object.keys(rows).forEach(function(k){
      var row=rows[k],maxH=0,info=[];
      row.forEach(function(c){
        var kids=[].slice.call(c.children);if(!kids.length)return;
        var f=kids[0],l=kids[kids.length-1],cs=getComputedStyle(c);
        var h=(l.getBoundingClientRect().bottom+parseFloat(getComputedStyle(l).marginBottom))
             -(f.getBoundingClientRect().top-parseFloat(getComputedStyle(f).marginTop));
        maxH=Math.max(maxH,h);info.push([c,parseFloat(cs.paddingTop),parseFloat(cs.paddingBottom),c.clientHeight]);
      });
      info.forEach(function(x){var extra=Math.max(0,(x[3]-x[1]-x[2]-maxH)/2);
        x[0].style.justifyContent='flex-start';x[0].style.paddingTop=(x[1]+extra)+'px';});
    });
  });
}
(document.fonts&&document.fonts.ready?document.fonts.ready:Promise.resolve()).then(align);
})();
</script>"""


def finish(path, title):
    with open(path, encoding="utf-8") as f:
        doc = f.read()
    doc = term(doc)
    doc = doc.replace("<span>주식회사 엣지컴퍼니 · 대표이사 고진식</span>", "<span>주식회사 엣지컴퍼니</span>")
    doc = doc.replace("지역업체", "인근 지역업체").replace("인근 인근", "인근")  # 본부장님 지시: '인근 지역업체'
    if getattr(D, "NEW_LOGO", False):  # 새 로고(본부장 10-09) — 남색 배경용 반전본(남색 → 아이보리), 깃 제외 자산
        doc = doc.replace('<div class="logo">EG</div><div class="en">EDGE COMPANY</div>',
                          '<img class="nlg" src="assets_ins/logo_lockup_rev.png" alt="엣지컴퍼니 EDGE COMPANY">')
        doc = doc.replace("</style>", ".nlg{height:64px;width:auto;display:block}</style>", 1)  # 표지·마지막 장만(본부장 10-09 — 중간 쪽 머리글은 EG 그대로)
    # 보유 자격의 법정 명칭은 '전기공사업 등록'(제 울산-00821호) — '면허' 표기 통일(검증 10-08)
    for _a, _b in [("전기공사업 면허를 갖춘 주관사", "전기공사업 등록 업체인 주관사"),
                   ("전기공사업 면허를 갖춘 입주박람회 주관사", "전기공사업 등록 업체인 입주박람회 주관사"),
                   ("전기공사업 면허 주관사", "전기공사업 등록 주관사"), ("전기공사업 면허 기반", "전기공사업 등록 기반"),
                   ("전기공사업 면허 시공", "전기공사업 등록 업체 시공"), ("면허 기반 직접 시공", "등록 업체 직접 시공"),
                   ("면허 범위 안에서", "등록 업종 범위 안에서"), ("<b>면허 시공</b>", "<b>직접 시공</b>")]:
        doc = doc.replace(_a, _b)
    doc = doc.replace("url(assets/", "url(../요약제안서/assets/").replace("url('assets/", "url('../요약제안서/assets/")
    doc = doc.replace('src="assets/', 'src="../요약제안서/assets/')
    i = doc.index("<body")
    body = doc[i:].replace("—", "-")  # 본부장 10-07: 굵은 긴 줄표 → 하이픈
    body = re.sub(r"(\d)\s*[–~]\s*(\d)", r"\1 ~ \2", body)  # 본부장 10-07: 범위는 '2018 ~ 2022'(띄어쓰기 + 물결)
    body = re.sub(r">([^<]+)<", lambda m: ">" + re.sub(r"(?<=[^\s>])·(?=[^\s<])", "\u2060·\u2060", m.group(1).replace(" · ", "\u00a0· ")) + "<", body)  # 줄 첫머리 가운뎃점 방지
    doc = doc[:i] + body
    doc = sub(doc, "<title>엣지컴퍼니 요약제안서</title>", f"<title>{title}</title>")
    doc = sub(doc, "</body>", ALIGN_JS + "</body>")
    left = re.findall(r".{0,12}(?:지웰|양주|덕계|1,595|1,355|대방산업|대방 |대방건설|신영|gwell|gw_|KINTEX|104동|덕정|회천|의정부|경기 북부|30개월|동탄|임예협|임차|임대사업자|철산|광명|조합|1,395|GS건설|탕정|센터파크|아산|천안|세종|OSCO|DCC|유관순|물의정원|중앙광장|1,416|17개월|22개 항목|prugiocenterpark|tj_|대우건설|사전청약|632세대|301세대|1,741|총회장).{0,6}", re.sub(r"<style.*?</style>", "", doc, flags=re.S))
    assert not left, left  # 지웰·동탄·철산·탕정 문구가 남지 않게(분당은 입예협 — '조합' 없음)
    # 대응표 쪽 번호(⟪pg:키⟫) — emit()에서 재배치가 끝난 B.PAGES로 계산
    doc = re.sub(r"⟪pg:(\w+)⟫", lambda m: f"p.{PGNO[m.group(1)]:02d}", doc)
    doc = re.sub(r"⟪pgs:([\w,]+)⟫", lambda m: "p." + " · ".join(f"{n:02d}" for n in sorted({PGNO[k] for k in m.group(1).split(",")})), doc)
    assert "⟪" not in doc
    # 본부장 제공 예정 사진(bd_*) — 파일이 없으면 남색 자리표시(파일을 assets_ins/에 넣으면 다음 빌드에 자동 반영)
    def _ph(m):
        name, attrs = m.group(1), m.group(2)
        if os.path.exists(os.path.join(HERE, "assets_ins", name + ".jpg")):
            return m.group(0)
        PH_MISSING.add(name)
        return f'<div class="phd"><span>{PH_LABEL.get(name, "사진 자리")}</span><small>{name}.jpg</small></div>'
    doc = re.sub(r'<img src="assets_ins/(bd_\w+)\.jpg"([^>]*)>', _ph, doc)
    doc = doc.replace("</style>", ".phd{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;"
                      "background:linear-gradient(160deg,#16314f,#0b1a2d);border:1px dashed rgba(235,203,143,.35)}"
                      ".phd span{font-size:13px;letter-spacing:.12em;color:rgba(235,203,143,.75);font-weight:700}"
                      ".phd small{font-size:10px;color:rgba(255,255,255,.35)}</style>", 1)
    doc = re.sub(r"⟦(.*?)⟧", r'<mark class="todo">\1</mark>', doc)
    _todo = re.findall(r'<mark class="todo">(.*?)</mark>', doc)
    if _todo:
        print(f"[확인 필요 {len(_todo)}칸] " + " / ".join(dict.fromkeys(_todo)))
    if "--final" in sys.argv:
        assert not _todo, "제출본에는 '확인 필요' 칸이 없어야 합니다"
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)


PH_LABEL = {"bd_cover": "조감도 자리", "bd_gate_night": "문주 경관조명 사진 자리", "bd_aerial_night": "단지 야간 경관 사진 자리",
            "bd_facade_night": "외벽 경관조명 사진 자리", "bd_plaza_night": "단지 조경 경관 사진 자리"}
PH_MISSING = set()


def emit(pages, out_html, title):
    keep = list(B.PAGES)
    B.PAGES[:] = pages
    PGNO.clear()
    for k, tt in PGREF.items():
        hits = [i for i, (_, kw) in enumerate(pages) if kw.get("title") == tt]
        assert len(hits) == 1, ("대응표 쪽 번호 — 제목을 찾지 못함", k, tt, hits)
        PGNO[k] = hits[0] + 1
    B.OUT_HTML, B.OUT_PDF = out_html, out_html[:-5] + ".pdf"
    B.build_html()
    B.PAGES[:] = keep
    finish(out_html, title)
    if PH_MISSING:
        print(f"[사진 자리표시 {len(PH_MISSING)}종] " + " / ".join(sorted(PH_MISSING)))
    if "--no-pdf" not in sys.argv:
        B.build_pdf()


def build():
    full = sys.argv[sys.argv.index("--full") + 1] if "--full" in sys.argv else None
    render_full_pages(full)
    # 공고 7항 제출서류에 요약본 · 회사소개서가 없어 제안서(제출서류 2)만 만든다.
    emit(list(B.PAGES), B.OUT_HTML, f"엣지컴퍼니 {D.SITE['name']} 입주박람회 주관사 제안서")


if __name__ == "__main__":
    build()
