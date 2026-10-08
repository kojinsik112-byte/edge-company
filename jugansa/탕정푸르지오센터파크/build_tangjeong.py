# -*- coding: utf-8 -*-
"""탕정 푸르지오 센터파크 — 입주박람회 주관사 제안서 빌더 (공고 필수서류 9).

동탄 파라곤3차 2-1 빌더를 토대로 한다. 기본틀(요약제안서 v5, ../요약제안서/build.py)은 건드리지 않고 불러와서 고친다.
- 표지: 탕정 푸르지오 센터파크 입주박람회 주관사 제안서 (조감도 없음 → 핵심 수치 표지)
- 01장 = 탕정 푸르지오 센터파크 맞춤 제안(단지 이해 · 입주민 건의 · 조경·경관조명 · 업무범위 8 · 자격 22 · 개인정보 · 일정 · 운영 · 참가 업체)
- 실적: 2023.01~2026.10 1,000세대 이상(본부장 지시), 날짜는 입주 연월
- 사진·발췌 장은 동탄 폴더 assets_ins / assets_full 을 공유(심볼릭 링크, 깃 제외)

사용: python build_cheolsan.py
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

NAME = "엣지컴퍼니_탕정푸르지오센터파크_05_입주박람회_입찰제안서"
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
    """탕정 푸르지오 센터파크는 입주예정자협의회(입예협) — 기본틀 용어 그대로."""
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
.cvlx .cap{position:absolute;right:28px;bottom:16px;font-size:10.5px;color:rgba(255,255,255,.6)}
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


# ============================================================ 01장 신설 — 탕정 푸르지오 센터파크 맞춤 제안
# 근거: 입찰 공고문(2026.10.06 접수 시작) · 단지 세부분석(엣지 내부, 2026.10.08) · 웹 교차확인(2026.10.08).
# 공고 8항: 제안서 내용은 계약서와 같은 효력 — 확인된 사실과 이미 하고 있는 약속만 쓴다.
S0 = "01. 탕정 푸르지오 센터파크 맞춤 제안"
NEW = []


def new(kind, **kw):
    NEW.append((kind, kw))


ST = D.SITE
_tp = dict(ST["types"])
_n59, _n84, _n109, _n136 = _tp["59A"] + _tp["59B"], _tp["84A"] + _tp["84B"] + _tp["84C"], _tp["109"], _tp["136PH"]
new("divider", n="01", title="탕정 푸르지오 센터파크를 위한 [[맞춤 제안]]",
    bl=["단지 이해 · 입주민 건의", "공고 업무 8개 · 자격 22개 대응", "추진 일정 · 17개월 관리", "조경·경관조명 특화"])

new("std", sec=S0, title="탕정 푸르지오 센터파크, [[이런 단지]]입니다",
    lead="입찰 공고문 단지개요 · 최초 입주자모집공고(2024.12.20) 기준 — 입주예정자협의회(이하 입예협)와 함께 설계합니다.",
    body=B.cards([
        dict(lb="SCALE", big=f"{ST['households']:,}", unit="세대", nm=f"{ST['buildings']}개동 · {ST['floors']}",
             ds="전 세대가 박람회·혜택 대상입니다. 동별 입주 일정에 맞춰 설치·반입을 나눕니다."),
        dict(lb="TYPE", big=f"{100 * _n84 / ST['households']:.1f}", unit="%", nm=f"전용 84㎡ {_n84}세대 중심",
             ds=f"59㎡ {_n59} · 84㎡ A·B·C {_n84} · 109㎡ {_n109} · 136㎡PH {_n136}세대. 같은 84㎡도 [[타입별로]] 견적합니다."),
        dict(lb="MOVE-IN", big="2028", unit=".03", nm="입주 예정",
             ds="입주까지 약 17개월. 사전점검 일정은 미정 — 확정되는 대로 박람회·지원 일정을 맞춥니다."),
        dict(lb="BRAND TOWN", big="C1BL", nm=f"시공 {ST['builder']}", hl=True,
             ds="아산탕정테크노 일반산업단지. 인접 리버파크(1,626세대)와 함께 푸르지오 브랜드타운을 이룹니다."),
    ]),
    kp=f"{ST['households']:,}세대 · 84㎡ 중심 · 입주까지 17개월 — [[타입별 맞춤 견적]]과 [[입주민 건의 관리]]가 핵심입니다.")

new("std", sec=S0, title="이 단지라서 [[먼저 챙길 것]]",
    lead="대단지 · 3개 84㎡ 타입 · 지하 진입 높이 제한 — 공동구매 전에 확인할 것부터 정리했습니다.",
    body=B.rows([
        ("유상옵션 중복 확인", "시공사 유상옵션 선택 여부·설치 호환을 확인한 뒤 품목을 권합니다. [[이미 선택한 것은 권하지 않습니다.]]"),
        ("84㎡ 3개 타입 견적", "84A·84B·84C는 창호·수납·설치 면적이 다릅니다. 일괄 가격이 아니라 [[타입별 견적·실측 데이터]]로 안내합니다."),
        ("반입 동선 사전 실측", "지하 1층 차로 2.7m · 지하 2층 2.3m 이상, 모집공고상 택배차량 지하 진입 불가 — 화물차 규격·동별 승강기·이사차량 대기 위치를 미리 짭니다."),
        ("가전 설치 호환", "인덕션 전용 콘센트·냉장고 급수 등 세대 설비를 타입별로 확인해 공동구매 가전의 [[전력·급배수·마감]] 책임을 정합니다."),
        ("가격 공개표", "품목·모델코드·물량·부가세·설치·철거·추가금을 한 장에 맞춰 [[같은 조건으로 비교]]할 수 있게 공개합니다."),
    ], title_w=230),
    kp="같은 84㎡라도 [[타입마다 다르게]] — 견적·실측·반입을 타입별로 준비합니다.")

TJ_REQ = [  # 입예협 카페 건의 목록·9차 회의록(2026.07.15) 기준 — 건의 '제목' 확인 수준, 처리 결과는 확인 후 갱신
    ("생활 · 안전", "초·중학교 사이 보행로 · 주차대수 · 전기차 충전기 · 차수시설", "통학·보행 현장 점검표 · 주차·충전 배치 검토 · 담당기관·조치 일정 정리", "기관·시공사 회신 확보"),
    ("품질 · 편의", "1층·지하로비 냉방 · 승강기 냉방 · 인덕션 설치 마감·콘센트", "기본 설계와 반영 내용 대조 · 시공과 공급 책임 구분 · 실물 검수", "라인별 사양·설치 확인"),
    ("단지 가치", "중앙광장 · 물의정원 조경 개선 · 조명 · 바닥분수 · 수목", "기존 설계·야간 현장 진단 → 개선 대안별 비용·관리비 비교", "반영 도면 확보"),
    ("커뮤니티", "골프 GDR · 피트니스·GX 동선 · 게스트하우스 집기 · 물놀이터", "설계·납품·운영 목록 대조 · 부족 집기 우선순위", "납품·설치 검수"),
    ("선택 편의", "수납 · 자재·마감 · 콘센트 · 입주 시기", "중복 건 통합 · 비용·실현 가능성 검토 · 건별 회신", "건별 회신 공유"),
]
new("std", sec=S0, title="입주민 건의, [[관리표로]] 끝까지 챙깁니다",
    lead="입예협 카페·회의에 올라온 건의를 접수 → 기술 검토 → 시공사·기관 협의 → 반영·보류 사유 → 공유까지 기록합니다.",
    body=table(["분야", "입주민 건의 (카페·회의록)", "주관사 지원", "완료 기준"], "".join(
        f'<tr><td class="k">{a}</td><td>{t(b)}</td><td>{t(c)}</td><td>{t(d)}</td></tr>' for a, b, c, d in TJ_REQ), "sm"),
    kp=("‘협의 완료’와 ‘설치 완료’를 [[구분해서]] 보고합니다.", "건의 제목 기준 · 처리 결과는 시공사 회신으로 갱신"))

new("std", sec=S0, title="중앙광장 · 물의정원, [[밤까지]] 살피겠습니다",
    lead="입주민이 요청한 조경·조명 개선을 도면·현장·예산으로 바꿉니다 — 전기공사업 면허를 갖춘 주관사의 방식입니다.",
    body=B.rows([
        ("우선 1 · 조명 · 보행", "중앙광장·물의정원 동선 조명, 수목 강조, 눈부심·빛샘·타이머 조정 — 기존 경관조명 도면·배선·조도부터 확인합니다."),
        ("우선 2 · 조경 · 체류", "수목·식재 보완, 휴게공간, 동선과 시설 연결 — 토심·관수·배수·유지관리와 인접 세대 영향을 함께 봅니다."),
        ("조건부 · 수경시설", "바닥분수·물놀이 확대는 구조·방수·전기·배수·수질·동절기 관리·관리비를 [[모두 확인한 뒤]] 판단합니다."),
        ("산출물 4가지", "① 현황 진단 1장 ② 기본·개선·선택안 비교(물량·공사비·유지관리비) ③ 협의 기록 ④ 완료 검수(수량·위치·사양·A/S)"),
    ], title_w=210),
    kp=("공사 범위·금액은 [[도면 검토와 비용 승인 후]] 확정합니다.", "전기공사업 등록 제 울산-00821호"))

new("std", sec=S0, title="입주까지 17개월, [[빈틈없이]] 관리합니다",
    lead="선정부터 입주까지 1년 반 — 그사이 바뀔 수 있는 것을 미리 약속해 둡니다.",
    body=B.cards([
        dict(lb="FACT", big="17", unit="개월", nm="선정 ~ 입주", ds="2026.10 선정 → 2028.03 입주 예정. 가격·모델·업체 사정이 바뀔 수 있어 [[변경 기준]]을 협약에 넣습니다."),
        dict(lb="ANSWER 01", big="정례", nm="정례 진행 보고", ds="입예협 정례회의에 맞춰 진행 상황 · 미결 건의 목록 · 다음 일정을 보고합니다."),
        dict(lb="ANSWER 02", big="대체", nm="업체·모델 변경 기준", ds="단종·폐업 시 동급 이상 모델·대체 업체를 입예협 승인으로 정합니다. 단가 인상은 [[승인 없이 하지 않습니다.]]"),
        dict(lb="ANSWER 03", big="연기", nm="입주 지연 대응", ds="입주·사전점검이 늦어지면 박람회·시공 일정을 함께 조정하고, 계약 세대에 변경 일정을 개별 안내합니다."),
    ]),
    kp="남은 일정이 짧을수록 [[준비 순서]]가 곧 약속입니다.")

new("std", sec=S0, title="탕정 푸르지오 센터파크 [[특화 제안]]",
    lead="박람회 운영 경험과 주관사 직영 품목(조명·커튼·실링팬)을 이 단지에 맞게 다시 짰습니다.",
    body=B.tiles([
        dict(lb="01", nm="유상옵션 중복 확인", ds="세대별 유상옵션 선택 여부를 확인해 겹치는 품목은 안내 단계에서 걸러 드립니다."),
        dict(lb="02", nm="84㎡ 타입별 표준 견적", ds="84A·B·C 타입별 실측 데이터로 커튼·블라인드·조명을 미리 제작해 입주일에 설치합니다."),
        dict(lb="03", nm="중앙광장 · 물의정원 조명 진단", ds="야간 보행·조경 조명을 진단해 개선안을 제출합니다. 설치는 입예협·관리주체 승인 후 선택."),
        dict(lb="04", nm="통학 · 생활권 안내", ds="탕정7초(2028.09 개교 목표)와 입주 사이 통학 정보를 교육지원청 답변 기준으로 정리합니다."),
        dict(lb="05", nm="커뮤니티 집기 검토", ds="게스트하우스·골프·GX 집기와 동선을 설계·납품 목록과 대조해 부족분 우선순위를 제안합니다."),
        dict(lb="06", nm="반입 동선 · 설치 예약", ds="지하 진입 높이 제한을 반영해 동별 설치 날짜·시간을 예약받아 같은 날 같은 동에 몰리지 않게 합니다."),
    ], cols=3, rows_n=2).replace('class="tiles"', 'class="tiles lg"'),
    kp=("제안 품목·혜택은 수요조사 결과에 따라 [[입예협과 최종 확정]]합니다.", "학교 개교·배정은 교육청 결정 사항 — 주관사가 보장하지 않습니다"))

TJ_SCOPE = [  # 공고 4항 업무 범위 1) ~ 8)
    ("입주박람회 개최 · 운영", "4단계 공개 심사로 참여업체 선정·사전 검증 · 품목별 가격 비교표 · 계약·결제·취소·환불·A/S 절차 · 종료 후 결과 보고서 · 분쟁 시 1차 관리책임", "03 · 04 · 06장"),
    ("입주지원 업무", "입주 행정 지원 · 사전점검 지원·전문인력 배치 · 입주지원센터 운영 지원 · 공용물품 지원 · 입주 민원 지원", "08장 B"),
    ("입예협 주관 행사 지원", "박람회·사전점검·설명회·총회·간담회 인력·장비·비품 · 현장 운영·행정 지원 · 홍보물 제작", "02 · 08장"),
    ("전문분야 컨설팅 · 행정지원", "전기·조명 분야 직접 자문(전기공사업 면허) · 도면·하자 분석 · 시공사·기관 협의 동석 · 단지 품질 개선 자문", "08장 B·C · 09장"),
    ("하자점검 · 품질관리 지원", "공용부·전용부 하자점검 지원 · 하자 접수 전용 창구 · 진행 상황 관리 · 하자처리 현황 정기 보고", "04 · 05장"),
    ("개인정보 보호 · 홍보 관리", "영업·마케팅 이용 금지 · 입예협 승인 없는 제3자 제공 금지 · 참여업체 관리·감독 · 홍보물 사전 승인", "07장"),
    ("민원 · 고객지원 체계", "주관 콜센터 · 카카오채널 · 홈페이지 접수 · 처리 절차·기한 · 선보상", "05장"),
    ("기타 업무", "입예협이 요청하는 사업 관련 업무 · 입주민 권익 보호·편익 증진 제안 — 협의해 협약서에 반영", "협약서"),
]
new("std", sec=S0, title="공고 업무 범위 [[8개 항목]] 대응",
    lead="공고 4항 업무 범위를 빠짐없이 맡고, 각 항목을 제안서의 어느 장에서 설명하는지 함께 적었습니다.",
    body=table(["NO", "공고 업무 범위", "엣지컴퍼니 수행 내용", "제안서"], "".join(
        f'<tr><td class="n">{i:02d}</td><td class="k">{t(a)}</td><td>{t(b)}</td><td>{t(c)}</td></tr>'
        for i, (a, b, c) in enumerate(TJ_SCOPE, 1)), "sm"),
    kp="업무 범위가 바뀌어도 [[입예협과 협의해]] 협약서에 그대로 옮깁니다.")

_r3 = D.RECENT3


def TODO(x):
    """본부장 확인 전 칸 — 노란 표시로 남기고, 빌드 끝에 개수를 알린다(제출본 빌드 전 0이어야 함). t() 이스케이프를 피해 finish()에서 태그로 바꾼다."""
    return f"⟦{x}⟧"


B.CSS += ".todo{background:#FFE066;color:#0D1E33;font-weight:700;padding:0 5px;border-radius:3px}"
_nice7 = sum(1 for h in D.HISTORY if "주관" in h[1])
QUAL22 = [  # 공고 5항 입찰자격 1) ~ 22) — (요건 요약, 엣지컴퍼니 현황, 증빙) · 문구는 자격 대조(2026.10.08) 결과 기준
    ("1년 이상 사업 영위 · 대표자 본인 명의", "법인 개업 2022.02.28 — 공고일 기준 4년 7개월 · 대표이사 고진식 본인 명의", "사업자등록증 · 등기부"),
    ("박람회 기획·운영 업태·종목", "종목 ‘전시, 박람회 및 행사 대행업’ · 등기 목적 ‘전시 박람회 사업 · 행사대행업 · 이벤트 기획 및 대행업’", "사업자등록증 · 등기부"),
    ("5개 단지 이상 주관사 선정 이력 · 유상옵션 행사 실적", f"입주박람회 주관 [[{_nice7}개 단지]] (NICE 연혁 2023.03 ~ 2026.07) · " + TODO("유상옵션 행사 실적 — 대표 확인 후 기입"), "실적 증명 · NICE 연혁"),
    ("최근 5년 벌금 이상 형사처분 없음", "해당 사항 없음", "대표이사 확약"),
    ("국세·지방세 완납", "체납 없음 — 공고일 이후 발급 납세증명서 제출", "국세·지방세 완납증명서"),
    ("입주예정자·입예협 분쟁·소송 없음", "해당 사항 없음", "대표이사 확약"),
    ("A/S 대책 · 사후 보증기간 명확", "주관사 단일 창구 · 48시간 하자보수 원칙 · 무상 A/S [[최소 2년]](업체·품목별 상이)", "사후관리 방안 · 각서(별지 2호)"),
    ("이행보증보험 발행 가능", "계약이행 · 하자보수 보증증권 — 2년 · 최대 10억, 협약 시 증권 실물 제출", "제안서 04장"),
    ("비밀유지 · 이의제기 금지", "선정 과정 비밀유지 · 선정 결과 이의 제기 없음", "서약서(별지 3호)"),
    ("계약 취소 시 환불 규정 첨부", "품목별 취소 기한(시공일 7일·15일 전) · 3영업일 내 환불 · 업체 지연 시 주관사 선보상", "환불 규정"),
    ("파손·변형 등 손해배상 이행", "참여업체와 연대해 하자보수·원상복구·손해배상 · 확인 시 주관사 선보상 후 업체 정산", "각서(별지 2호)"),
    ("법무법인과 행정·총회 지원", "입예협 지정·협의 법무법인과 협력 — 법무 자문은 법무법인, 총회·설명회 실무는 주관사", "제안서 08장 B"),
    ("각종 증명서 제출 가능", "입예협 요청 시 각종 증명서를 최신 발급본으로 제출", "-"),
    ("공동구매 업체 분쟁 손해배상", "주관사가 1차 관리책임자로 중재 · 선보상 후 업체 정산", "각서(별지 2호) · 05장"),
    ("입주민 자율 구매 제한 요구 없음", "박람회 밖 개별 구매·업체 선택을 제한·요구하지 않음", "제안서 명시"),
    ("혜택 · 입예협 지원 · 최저가 · A/S 제안", f"세대당 {D.FUND}만원 · 최저가 차액 10배 · A/S 정책 명시", "제안서 03 · 08장"),
    ("1,000세대 이상 3개 단지 이상 실적", f"최근 3년 1,000세대 이상 [[{len(_r3)}건]] · {sum(r[3] for r in _r3):,}세대 (NICE 연혁)", "실적 증명 · NICE 연혁 · " + TODO("계약서")),
    ("컨설팅 부서 세분화", "4개 팀 분업 — 대외지원팀 3명 행정지원 전담 · 행사관리팀 4명 · 영업팀 2명", "조직 구성 · 전담 체계"),
    ("커뮤니티 홍보 마케팅 전문 부서", "이벤트팀 3명 — 카페·오픈채팅 콘텐츠 · 카드뉴스 · 영상, 입예협 승인 범위에서만", "전담 체계 · 02장"),
    ("자본금 1억원 이상", "자본금 [[2억원]] (2026.04.30 등기)", "등기부"),
    ("타 주관사와 다른 차별점", "전기공사업 등록 업체의 경관조명 검토·시공 · 직영 품목 · 온라인 박람회", "전기공사업 등록증 · 09장"),
    ("행정 전문인력 · 부서 직접 대응", "본부장 + 대외지원팀 전담 · 외부 전문 7명(건축·조경·설비·하자진단) · 전기 직접", "전담 체계 · 등록증"),
]
for _part, (_a, _b) in enumerate([(0, 11), (11, 22)], 1):
    new("std", sec=S0, title=f"입찰 참가 자격 [[22개 항목]] 대응 {'①②'[_part - 1]}",
        lead=f"공고 5항 입찰자격 {_a + 1} ~ {_b}번을 항목마다 현황과 증빙으로 답합니다.",
        body=table(["NO", "공고 입찰자격 (요약)", "엣지컴퍼니 현황", "증빙"], "".join(
            f'<tr><td class="n">{i:02d}</td><td class="k">{t(a)}</td><td>{t(b)}</td><td>{t(c)}</td></tr>'
            for i, (a, b, c) in enumerate(QUAL22[_a:_b], _a + 1)), "sm q22"),
        kp="자격은 말이 아니라 [[제출 서류로]] 확인받겠습니다.")

_stf = {n: (c, r) for n, c, r in D.STAFF}
_next = sum(c for _, c in D.STAFF_EXT)


def _dcard(no, req, head, items):
    li = "".join(f"<li>{t(x)}</li>" for x in items)
    return f'<div class="dcd"><i>공고 자격 {no}</i><h4>{req}</h4><b>{head}</b><ul>{li}</ul></div>'


new("std", sec=S0, title="입예협 [[전담 체계]] — 자격 18 · 19 · 22 대응",
    lead="탕정 전담 인원 배치(안)를 바탕으로, 공고가 요구한 부서·전문인력을 업무별로 나눠 맡깁니다.",
    body='<div class="nb"><div class="dcx">'
         + _dcard("18", "컨설팅 부서 세분화", "업무별 4개 팀 분업", [
             f"행정 — 대외지원팀 {_stf['대외지원팀'][0]}명: 공문·민원·하자 접수, 시공사 협의 자료",
             f"현장 — 행사관리팀 {_stf['행사관리팀'][0]}명: 박람회·사전점검·입주지원센터",
             f"소통 — 영업팀 {_stf['영업팀'][0]}명: 입예협 창구 · 참여업체 심사 지원",
             "입예협 요청은 담당 팀을 지정해 [[24시간 안에 1차 회신]]"])
         + _dcard("19", "커뮤니티 홍보 전문 부서", f"이벤트팀 {_stf['이벤트팀'][0]}명 전담", [
             "카페·오픈채팅 콘텐츠 캘린더 · 카드뉴스 · 영상 · 드론",
             "모든 게시물은 [[입예협 사전 승인 후]] 게시",
             "카페 밖 세대까지 — 동별 안내문 · 공지채널로 전 세대 도달",
             "입주민 개인정보 · DB는 홍보에 쓰지 않음"])
         + _dcard("22", "단지 이슈 직접 대응", f"본부장 + 대외지원팀 + 외부 전문 {_next}명", [
             "주관사업 총괄 본부장이 이슈를 직접 관리",
             "건축·구조 · 조경 · 설비 · 하자진단은 외부 전문 협력 자문",
             "전기·조명은 전기공사업 등록 업체로 [[직접 검토·시공]]",
             "시공사·기관 협의에 자료 준비 · 동석"])
         + '</div><div class="hflow"><span>입예협 요청</span><i>›</i><span>담당 팀 지정</span><i>›</i><span>기술·행정 검토</span><i>›</i>'
           '<span>시공사 · 기관 협의</span><i>›</i><span>회신 · 기록 · 보고</span></div></div>',
    kp=("부서 이름이 아니라 [[누가 무엇을 맡는지]]로 답합니다.", "인원·담당은 협약 시 명단 제출 · 외부 협력은 자문·촬영 등 전문 업무"))
B.CSS += (".dcx{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;flex:1;min-height:0}"
          ".dcd{border:1px solid var(--line);border-top:2px solid var(--gold2);border-radius:14px;padding:14px 18px;background:linear-gradient(180deg,rgba(235,203,143,.08),rgba(255,255,255,.01) 40%);display:flex;flex-direction:column;gap:4px}"
          ".dcd i{font-style:normal;font-size:12px;font-weight:700;letter-spacing:.2em;color:var(--gold2)}"
          ".dcd h4{font-size:15px;color:var(--sub);font-weight:600}.dcd>b{font-size:21px;color:var(--gold);margin-bottom:4px}"
          ".dcd ul{list-style:none;margin:6px 0 0;padding:0;display:flex;flex-direction:column;gap:12px}"
          ".dcd li{font-size:15.5px;line-height:1.5;padding-left:14px;position:relative}.dcd li:before{content:'';position:absolute;left:0;top:8px;width:6px;height:6px;border-radius:50%;background:var(--gold2)}")

new("std", sec=S0, title="입주민 개인정보는 [[행사 운영에만]] 씁니다",
    lead="공고 4항 6) 개인정보 보호·홍보 관리 — 주관사와 참여업체가 지킬 기준을 미리 정했습니다.",
    body=B.rows([
        ("수집 최소화", "상담·계약에 필요한 정보만, 목적·보관기간을 정해 [[별도 동의]]를 받습니다."),
        ("영업 이용 금지", "입주예정자 정보를 영업·마케팅·광고·고객유치에 쓰지 않고, [[DB를 만들거나 판매하지 않습니다.]]"),
        ("제3자 제공 금지", "입예협 사전 서면 승인 없이 참여업체·제3자에게 제공하지 않습니다. 필요하면 정보주체 동의를 따로 받습니다."),
        ("참여업체 관리", "참여업체의 개인정보 취급을 주관사가 관리·감독하고, 보호 의무를 계약 조건에 넣습니다."),
        ("홍보물 사전 승인", "입예협 명칭·로고·카페·오픈채팅은 승인 범위에서만 쓰고, 모든 홍보물은 [[게시 전 승인]]받습니다."),
        ("파기 · 위반 시 조치", "보관기간이 지나면 파기하고, 위반이 확인되면 계약 해지·손해배상 등 공고의 조치를 따릅니다."),
    ], title_w=210),
    kp="입주민 명단은 [[업체 영업 명단이 아닙니다.]]")

FLOWX = ('<div class="hflow"><span>한 창구 접수</span><i>›</i><span>유형 분류</span><i>›</i><span>책임 주체 연결</span><i>›</i>'
         '<span>처리 · 회신 추적</span><i>›</i><span>완료 확인 · 정기 보고</span></div>')
B.CSS += (".tbl.lgx td{padding:17px 14px;font-size:16.5px;line-height:1.5}.tbl.lgx td.k{font-size:18px}"
          ".hflow{display:flex;align-items:center;gap:10px;margin-top:18px}.hflow span{flex:1;text-align:center;border:1px solid rgba(200,168,106,.5);"
          "border-radius:10px;padding:12px 8px;font-size:15.5px;font-weight:700;background:rgba(235,203,143,.06)}"
          ".hflow span:last-child{background:var(--gold);color:#0d1e33;border-color:var(--gold)}.hflow i{font-style:normal;color:var(--gold);font-weight:800;font-size:20px}")

new("std", sec=S0, title="하자 접수, [[책임부터]] 나눕니다",
    lead="공고 4항 5) 하자 접수 전용 창구 — 접수는 한 곳에서 받고, 처리 책임은 유형별로 나눠 끝까지 추적합니다.",
    body=table(["접수 유형", "예", "처리 책임", "주관사 역할"], "".join(
        f'<tr><td class="k">{a}</td><td>{t(b)}</td><td>{t(c)}</td><td>{t(d)}</td></tr>' for a, b, c, d in [
            ("건설사 시공 · 공용부", "세대 마감·설비 하자, 공용부 시설", f"시공사({ST['builder']})·사업주체 하자 처리 창구", "접수 대행 · 회신 추적 · 현장 확인 지원 · 정기 보고"),
            ("공동구매 납품 · 시공", "박람회에서 계약한 품목의 설치·제품 하자", "참여업체 + 주관사 연대(별지 2호)", "48시간 하자보수 원칙 · 업체 미응답 시 개입 · 선보상"),
            ("성능 향상 · 추가 설치", "조경·조명·집기 개선, 시설 추가", "입예협·관리주체 결정 사항", "하자와 구분 · 도면·예산·운영비 검토 후 추진"),
        ]), "lgx") + FLOWX,
    kp=("시공 하자를 [[공동구매 업체에 떠넘기지 않고]], 공동구매 하자를 [[시공사 탓으로 돌리지 않습니다.]]", "접수는 주관 콜센터·카카오채널·홈페이지 한 창구"))

RPRIN = ('<div class="rprin">' + "".join(f'<div><b>{a}</b><p>{b}</p></div>' for a, b in [
    ("협의 ≠ 설치", "‘협의 완료’와 ‘설치 완료’를 나눠 표시"),
    ("지연은 사유와 함께", "지연 건은 사유·다음 일정을 같이 보고"),
    ("최소 정보", "입예협과 공유할 수 있는 범위로 집계"),
    ("원자료 열람", "입예협이 요청하면 근거 자료를 열람"),
]) + '</div>')
B.CSS += (".rprin{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:16px}.rprin div{border:1px solid rgba(200,168,106,.45);"
          "border-radius:12px;padding:12px 14px;background:rgba(235,203,143,.05)}.rprin b{display:block;font-size:16px;color:var(--gold)}"
          ".rprin p{font-size:13.5px;color:var(--sub);margin-top:4px;line-height:1.45}")

new("std", sec=S0, title="보고는 [[항목과 시점]]을 정해 둡니다",
    lead="공고 4항 1)·5)·7) — 결과보고서와 정기 보고에 무엇을 담을지 미리 정했습니다.",
    body=table(["보고", "시점", "담는 내용"], "".join(
        f'<tr><td class="k">{a}</td><td>{t(b)}</td><td>{t(c)}</td></tr>' for a, b, c in [
            ("정례 진행 보고", "입예협 정례회의마다", "진행 상황 · 미결 건의 목록 · 다음 일정 · 시공사 회신 현황"),
            ("하자처리 현황 보고", "입주 후 정기(주기는 입예협과 협의)", "하자 접수 · 처리 완료 · 지연 건과 사유 · 재접수"),
            ("입주박람회 결과보고서", "박람회 종료 후", "[[공동구매 진행현황 · A/S 접수현황 · 하자처리 현황 · 민원처리 결과]]"),
            ("최종 결과 보고서", "입주 후 1년 운영 관리 종료 시", "계약 · 환불 · A/S · 하자 처리 결과 · 하자 예치금 사용 내역"),
        ]), "lgx") + RPRIN,
    kp=("보고서는 입예협과 공유할 수 있는 [[최소 정보]]로 집계합니다.", "개인 연락처·동호수는 싣지 않습니다"))

new("std", sec=S0, title="선정부터 입주까지 [[추진 일정]] (안)",
    lead="입주 2028.03에서 거꾸로 짰습니다. 17개월을 ‘대기’가 아니라 ‘준비’로 씁니다.",
    body=B.rows([
        ("2026.10~11", "주관사 선정·협약 체결 · 입예협 카페/공지채널 지원 시작 · [[유상옵션·기본 제공 품목]] 목록 확보 · 건의 관리표 개설"),
        ("2026.12~2027.08", "정례 진행 보고 · 조경·경관조명 현황 진단 · 커뮤니티 집기 검토 · 통학·생활권 정보 정리 · 품목 시장가 점검"),
        ("2027.07~09", "[[품목 수요조사]] 설문 · 타입별(84A·B·C 등) 실측 데이터 준비 · 행사장 후보 답사"),
        ("2027.09~11", "참여업체 [[공개 입찰공고]] · 4단계 심사 → [[입예협 최종 컨펌]] · 특약이행각서 징구"),
        ("2027.12~2028.01", "단가표 사전 공개 · [[입주박람회 금·토·일 3일]] · 온라인 박람회 오픈 · 사전점검 행사 지원"),
        ("2028.03~", "입주 지원 · 입주지원센터 운영 지원 · 하자 접수 창구 → 입주 후 1년 운영 관리 · [[결과 보고서]] (품목 A/S는 최소 2년 · 업체별 상이)"),
    ], title_w=170),
    kp="세부 일정은 사전점검·입주지원센터 일정에 맞춰 [[입예협과 확정]]합니다.")

new("std", sec=S0, title="입주박람회 [[운영 계획]]",
    lead="계약을 재촉하는 자리가 아니라, 확인하고 비교하는 자리로 만듭니다.",
    body=B.tiles([
        dict(lb="WHEN", nm="2027.12 ~ 2028.01 금·토·일", ds="입주 2~3개월 전 3일간, 사전점검 일정에 맞춰 확정합니다."),
        dict(lb="WHERE", nm="단지 인근 전시장", ds="단지에서 가까운 전시·컨벤션 시설을 후보로, 입예협과 답사한 뒤 확정합니다."),
        dict(lb="SAFETY", nm="행사 배상책임보험 가입", ds="안전요원·동선·비상구 계획 수립. 화재·상해 예방 수칙은 참여업체 서약."),
        dict(lb="MEMBERS", nm="정회원 사전예약 · 체크인", ds="정회원 우선 입장·혜택. 입구 체크인 옆에 입예협 부스를 둡니다."),
        dict(lb="ONLINE", nm="온라인 박람회 · 라이브", ds="단지 입주민만 들어오는 폐쇄몰. 박람회와 같은 공동구매가."),
        dict(lb="PR", nm="카페·공지채널 콘텐츠", ds="카드뉴스·영상·현수막·알림톡 — 게시 전 입예협 사전 승인을 받습니다."),
    ], cols=3, rows_n=2).replace('class="tiles"', 'class="tiles lg"'),
    kp="박람회장 가격 = 사전 공개 단가 — [[현장에서 가격이 바뀌지 않습니다.]]")


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


new("std", sec=S0, title="품목별 [[예상 참가 업체]]",
    lead="확정은 입예협 공개 입찰·심사 후 — 시공 품목은 인근 지역(아산·천안권) 업체가 우선입니다.",
    body=table(["구분", "품목", "예상 참가 업체", "비고"], vendor_rows(), "sm"),
    kp=("주관사 직영 품목도 [[같은 심사 · 같은 단가 공개 · 같은 최저가 보장]].", "하도급·타 주관사 연동 계약 없음"))

new("std", sec=S0, title="공동구매 단가를 지키는 [[4가지 장치]]",
    lead="‘행사비 때문에 오르는 단가’를 구조로 막습니다.",
    body=B.cards([
        dict(lb="01", big="공개", nm="단가표 사전 공개", ds="박람회 전 품목별 단가·할인율을 입예협에 제출해 검수받습니다. 현장 가격 변경 없음."),
        dict(lb="02", big="10", unit="배", nm="최저가 차액 보상", ds="동일 브랜드·동일 제품이 더 싸면 차액의 10배 보상. (온라인 판매·시공 품목 제외)"),
        dict(lb="03", big="추가할인", nm="실적 비례 추가할인", ds="업체 기대매출을 넘기면 계약 세대 잔금에서 추가할인. 할인율은 업체 입찰 조건으로 입예협과 확정."),
        dict(lb="04", big=str(D.DEPOSIT_MAX), unit="%", nm="계약금 상한", ds=f"계약금은 총액의 {D.DEPOSIT_MAX}% 이하, 잔금은 시공·설치 후. 현금·카드 동일가."),
    ]),
    kp="가격은 말이 아니라 [[사전 공개 단가 + 최저가 보장]]으로 검증받습니다.")


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
    dict(lb="BRANCH 01", big="대전", nm="대전 지사", ds="충청권 거점. 세종·아산 커버."),
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

# 입증하기 어려운 표현 정리(공고 9-2 허위·과장 금지)
i = find("정회원 전용")
B.PAGES[i][1]["lead"] = "공동구매가에 더해지는 정회원 전용 혜택입니다."

# 재개발: 협의 상대는 입예협·시공사
i = find("[[조경·착공]] 분석보고서")
kw = B.PAGES[i][1]
kw["lead"] = sub(kw["lead"], "시공사와 협상할 때", "입예협·시공사와 협의할 때")
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
            "공식 단지명·총세대수 기준"))))
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
        kp=(f"2,000세대 이상 대단지를 이끈 경험을 탕정 푸르지오 센터파크 [[{D.SITE['households']:,}세대]]에 그대로 옮깁니다.",
            "사진은 조감·외관 이미지"))))
    # 핵심 혜택 한 장(본부장 지시 10-07: 표지 수치 대신 뒤쪽에 임팩트 있게) — 마무리 약속 장 바로 앞
    _ci = next(i for i, (k, _) in enumerate(B.PAGES) if k == "closing")
    _hh = D.SITE["households"]
    B.PAGES.insert(_ci, ("std", dict(sec=B.PAGES[_ci][1].get("sec", ""), title="탕정 푸르지오 센터파크에 드리는 [[핵심 혜택 6가지]]",
        lead="숫자로 약속하고, 협약서로 지킵니다.",
        body=B.tiles([
            dict(lb="발전지원금", big=f"{D.FUND}", unit="만원", nm="세대당 발전지원금",
                 ds=f"{_hh:,}세대 기준 총 {_hh * D.FUND // 10000}억 {_hh * D.FUND % 10000:,}만원 (부가세 포함)"),
            dict(lb="하자 예치금", big="1", unit="억원", nm="현금 예치", ds="엣지컴퍼니 자산으로 입예협 공동통장에 직접 예치"),
            dict(lb="이행보증보험", big="10", unit="억원", nm="2년 보증", ds="증권 실물을 입예협에 전달"),
            dict(lb="최저가 보장", big="10", unit="배", nm="차액 보상", ds="동일 제품이 더 싸면 차액의 10배 보상"),
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
TITLE_H1 = "탕정 푸르지오 센터파크<br><em>입주박람회 주관사 제안서</em>"
COVER_TOP = """<div class="top"><div><div class="logo">EG</div><div class="en">EDGE COMPANY</div></div>
<div class="who">주식회사 엣지컴퍼니<br>입주박람회 전문 주관사</div></div>"""


def p_cover_impact():
    """요약본 [2-2] 표지 — 숫자(15만원 · 10억 · 1억)로 시작, 오른쪽은 단지 경관조명(본부장 10-07)."""
    hh = D.SITE["households"]
    sub2 = f'<div class="sub2"><div><i>제출처</i><b>{D.CLIENT}</b></div><div><i>제안사</i><b>{D.COMPANY}</b></div></div>'
    return f"""<section class="page cv cv5"><div class="cvlx"><img src="assets_ins/tj_facade_night.jpg" alt=""><div class="fd"></div>
<span class="cap">단지 경관조명 · 연출 예시 이미지</span></div>{COVER_TOP}
<div class="mid"><span class="pill">{COVER['pill']}</span>
<h1>탕정 푸르지오 센터파크 <em>입주박람회 주관사 요약 제안서</em></h1>
<div class="hero3">
<div class="h1x"><i>세대당 발전지원금</i><b>{D.FUND}<small>만원</small></b>
<p>{hh:,}세대 × {D.FUND}만원 = <em>총 {won(hh * D.FUND)}</em> (부가세 포함) · {'현금 또는 같은 금액의 혜택 패키지 중 선택' if getattr(D, 'FUND_CASH', False) else '혜택 패키지 또는 입예협이 고른 항목으로 직접 제공'}</p></div>
<div><i>이행보증보험 2년</i><b><small class="mx">최대</small>10<small>억</small></b><p>증권 실물 제출</p></div>
<div><i>하자 예치금</i><b><small class="mx">최대</small>1<small>억</small></b><p>하자 시 입주민 선보상</p></div>
</div>
<div class="lxband"><b>전기공사업 면허 주관사</b><span>경관조명·공용부 조명 개선을 제안에서 직접 시공까지<br>전기공사업 등록 제 울산-00821호</span></div>
</div>
{sub2}
<div class="bt"><span>BID PROPOSAL · 요약 제안서</span><span>2026.10</span></div>
</section>"""


def p_cover():
    if COVER.get("kind") == "impact":
        return p_cover_impact()
    if COVER.get("kind") == "company":
        return p_cover_company()
    sub2 = f'<div class="sub2"><div><i>제출처</i><b>{D.CLIENT}</b></div><div><i>제안사</i><b>{D.COMPANY}</b></div></div>'
    # 조감도(본부장 제공 2026-10-07) — 네이비 배경에 스며들도록 위·왼쪽을 배경색으로 페이드
    art = ('<div class="cvart tj"><img src="assets_ins/tj_cover_art.jpg" alt="">'
           '<span class="credit">탕정 푸르지오 센터파크 투시도 · 홍보용 이미지</span></div>')
    return f"""<section class="page cv cv4">{art}{COVER_TOP}
<div class="mid"><span class="pill">{COVER['pill']}</span>
<h1 class="tj">{TITLE_H1}</h1>
<div class="gbar"></div>
<div class="tag2">{COVER['tag']}</div>
</div>
{sub2}
<div class="bt"><span>BID PROPOSAL · 입주박람회 주관사 제안서</span><span>2026.10</span></div>
</section>"""


def p_cover_company():
    """제출서류 07 회사소개서 표지 — 제안서 표지 틀 그대로, 제목·띠만 회사소개서로."""
    art = ('<div class="cvart"><img src="assets_ins/tj_cover_art.jpg" alt="">'
           '<span class="credit">탕정 푸르지오 센터파크 조감도 · 홍보용 이미지</span></div>')
    sub2 = f'<div class="sub2"><div><i>제출처</i><b>{D.CLIENT}</b></div><div><i>제출서류</i><b>07 회사소개서 (연혁 · 조직도 포함)</b></div></div>'
    return f"""<section class="page cv cv4">{art}{COVER_TOP}
<div class="mid"><span class="pill">회사소개서</span>
<h1>{D.COMPANY}<br><em>회사소개서</em></h1>
<div class="gbar"></div>
<div class="tag2">연혁 · 조직도 · 주관 실적 · 자격과 증빙<br>전기공사업 면허를 갖춘 입주박람회 주관사</div>
</div>
{sub2}
<div class="bt"><span>COMPANY PROFILE · 탕정 푸르지오 센터파크</span><span>2026.10</span></div>
</section>"""


TOC4 = [
    [("01", "탕정 푸르지오 센터파크 맞춤 제안", ["단지 이해 · 입주민 건의", "업무 8개 · 자격 22개", "일정 · 17개월 관리", "참가 업체 · 품목"]),
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
            "부산 해운대 지사 · 해운대구 아르파나 B1<br>직영 4곳 + 협력 8곳 = 전국 12개 지사망 · 평일 09:00–18:00 · 24시간 이내 회신<br>")
    s = sub(s, "삼성전자 MOU 체결</div>", "삼성전자 · 세스코 MOU 체결</div>")
    s = sub(s, '<div class="who">주식회사 엣지컴퍼니<br>대표이사 고진식</div>', "")
    s = sub(s, '<div class="addr">', '<div class="addr" style="font-size:14.2px">')
    label = "COMPANY PROFILE · 탕정 푸르지오 센터파크" if COVER.get("kind") == "company" else "BID PROPOSAL · 탕정 푸르지오 센터파크"
    return sub(s, "SUMMARY PROPOSAL · 요약제안서", label)


B_p_contact = B.p_contact


def won(man):
    """만원 → '2억 1,199만원'"""
    eok, rest = divmod(man, 10000)
    if not eok:
        return f"{rest:,}만원"
    return f"{eok}억 {rest:,}만원" if rest else f"{eok}억원"


def p_hi_fund(no, sec):
    hh = D.SITE["households"]
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
    n = D.SITE["households"] * D.FUND
    items = [(f"세대당 {D.FUND}만원 발전지원금", f"전 세대 {D.SITE['households']:,}세대 기준 · 총 {won(n)}(부가세 포함)"),
             ("하자 예치금 1억 · 이행보증보험 10억", "엣지컴퍼니 자산으로 공동통장 예치 · 증권 실물 제출"),
             ("입예협 전용 8가지 무상 지원", "별도 비용 없음 · 자체 인력"),
             ("유상옵션 중복 확인 · 가격 공개표", "유상옵션과 겹치는 품목 사전 확인 · 시공비·추가금 포함 공개"),
             ("시공 품목 인근 지역업체 90% 선정", "48시간 A/S가 가능한 거리"),
             ("최저가 차액 10배 보상", "단가표 사전 공개 · 현장 가격 변경 없음"),
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
    doc = doc.replace("url(assets/", "url(../요약제안서/assets/").replace("url('assets/", "url('../요약제안서/assets/")
    doc = doc.replace('src="assets/', 'src="../요약제안서/assets/')
    i = doc.index("<body")
    body = doc[i:].replace("—", "-")  # 본부장 10-07: 굵은 긴 줄표 → 하이픈
    body = re.sub(r"(\d)\s*[–~]\s*(\d)", r"\1 ~ \2", body)  # 본부장 10-07: 범위는 '2018 ~ 2022'(띄어쓰기 + 물결)
    doc = doc[:i] + body
    doc = sub(doc, "<title>엣지컴퍼니 요약제안서</title>", f"<title>{title}</title>")
    doc = sub(doc, "</body>", ALIGN_JS + "</body>")
    left = re.findall(r".{0,12}(?:동탄|임예협|임차|임대사업자|철산|광명|조합|1,395|aT센터|SETEC|수원메쎄|GS건설).{0,6}", re.sub(r"<style.*?</style>", "", doc, flags=re.S))
    assert not left, left  # 동탄·철산 문구가 남지 않게(탕정은 일반 분양 단지 — '조합' 없음)
    doc = re.sub(r"⟦(.*?)⟧", r'<mark class="todo">\1</mark>', doc)
    _todo = re.findall(r'<mark class="todo">(.*?)</mark>', doc)
    if _todo:
        print(f"[확인 필요 {len(_todo)}칸] " + " / ".join(dict.fromkeys(_todo)))
    if "--final" in sys.argv:
        assert not _todo, "제출본에는 '확인 필요' 칸이 없어야 합니다"
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)


def emit(pages, out_html, title):
    keep = list(B.PAGES)
    B.PAGES[:] = pages
    B.OUT_HTML, B.OUT_PDF = out_html, out_html[:-5] + ".pdf"
    B.build_html()
    B.PAGES[:] = keep
    finish(out_html, title)
    if "--no-pdf" not in sys.argv:
        B.build_pdf()


NAME22 = "엣지컴퍼니_탕정푸르지오센터파크_요약제안서"
NAME07 = "엣지컴퍼니_탕정푸르지오센터파크_회사소개서"

HIST_CSS = r"""
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


def company_pages():
    """제출서류 07 회사소개서 — 표지 + 01 간지 + 연혁 + 조직 구성(실명 없음) + 제안서 01장 + 연락처."""
    pick = [p for p in B.PAGES if p[1].get("sec") == "01. 회사소개" and p[0] != "divider"]
    d01 = [p for p in B.PAGES if p[0] == "divider" and p[1].get("n") == "01"]
    assert len(d01) == 1 and len(pick) > 15, (len(d01), len(pick))
    key = ("설립", "등록", "ISO", "MOU")
    def keep(t):  # '주관 · 1,643세대'는 한 줄로
        return re.sub(r"(주관 · [\d,]+세대)", r'<span style="white-space:nowrap">\1</span>', _h.escape(t))
    items = "".join(f'<li class="{"k" if any(x in t for x in key) else ""}"><b>{d}</b><span>{keep(t)}</span><i>{src}</i></li>'
                    for d, t, src in D.HISTORY)
    half = (len(D.HISTORY) + 1) // 2
    lis = items.split("</li>")
    left = "</li>".join(lis[:half]) + "</li>"
    right = "</li>".join(lis[half:])
    hist = ("std", dict(sec="01. 회사소개", title="엣지컴퍼니 [[연혁]]",
        lead=f"법인 설립({D.FOUNDED})부터 지금까지 - 등기부 · 등록증 · 인증서 · NICE 연혁 · 협약으로 확인되는 기록만 적었습니다.",
        body=f'<div class="nb"><div class="hist"><ol>{left}</ol><ol>{right}</ol></div></div>',
        kp=("2023년부터 [[해마다]] 1,000세대 이상 입주박람회를 맡아 왔습니다.",
            "출처: 법인등기부 · 전기공사업 등록증 · ISO 인증서 · NICE 기업신용평가보고서 연혁 · 세스코 협약")))
    contact = [p for p in B.PAGES if p[0] == "contact"]
    return [("cover", {})] + d01 + [hist] + pick + contact  # 조직 구성 장은 01장(pick)에 이미 들어 있음


def summary_pages():
    """요약본 [2-2] — 본 제안서(B.PAGES, 재배치 후)에서 필요한 장만 골라 압축. 장 표시(sec)만 요약본 기준으로 바꾼다."""
    def take(title=None, kind=None, sec=None, kp=None):
        hits = [(k, kw) for k, kw in B.PAGES if (title and kw.get("title") == title) or (kind and not title and k == kind)]
        assert len(hits) == 1, (title, kind, len(hits))
        k, kw = hits[0]
        kw = dict(kw)
        if sec and "sec" in kw:
            kw["sec"] = sec
        if kp:
            kw["kp"] = kp
        return (k, kw)

    S1, S2, S3, S4, S45, S5, S6 = ("01. 발전지원 15만원", "02. 경관조명 특화", "03. 하자보증 · 안전망",
                                   "04. 업체선정 · 가격 보호", "05. 박람회 운영", "06. 탕정 푸르지오 센터파크 맞춤", "07. 주관 실적")
    hero_body = (
        '<img class="bg" src="assets_ins/tj_gate_night.jpg" alt=""><div class="veil"></div><span class="hcap">문주·진입부 경관조명 · 연출 예시 이미지</span>'
        '<div class="hin"><div class="kick">LANDSCAPE LIGHTING · 전기공사업 면허 주관사</div>'
        '<h2>단지의 밤,<br><em>경관조명이 완성합니다</em></h2><div class="bar"></div>'
        '<p>엣지컴퍼니는 전기공사업 면허를 갖춘 입주박람회 주관사입니다.<br>경관조명은 제안서로 끝내지 않고,<br>컨설팅부터 직접 시공까지 면허 범위 안에서 책임집니다.</p></div>'
        '<div class="pil">'
        '<div><i>01 · CONSULTING</i><b>컨설팅 · 설계</b><span>조도·색온도·배광을 단지 동선과 외관에 맞춰 도면으로 제안</span></div>'
        '<div><i>02 · PRODUCTION</i><b>직수입 · 생산</b><span>설계 사양 그대로 제작 · KC 인증 제품만 납품</span></div>'
        '<div><i>03 · CONSTRUCTION</i><b>면허 시공</b><span>전기공사업 등록 제 울산-00821호 · 외주 없이 직접 시공</span></div>'
        '<div><i>04 · COMMUNITY</i><b>단지 업그레이드</b><span>문주·외벽·커뮤니티 조명 개선안 컨설팅(C 패키지) · 시공은 승인 후 선택</span></div>'
        '</div>')
    pages = [
        ("cover", {}),
        take(B.FUND_CHOICE_TITLE, sec=S1),
        take("혜택 패키지 [[A · B · C]] 구성 항목", sec=S1,
             kp=("다음 장은 받으시는 방식별 [[패키지 구성 예시]]입니다.", "항목별 상세는 본 제안서 08장 · 공용부 항목은 입예협·관리주체 협의 전제")),
        take("이렇게 [[패키지로]] 받으실 수 있습니다 (예시)", sec=S1),
        ("std", dict(sec=S2, title=HERO, lead=None, body=hero_body,
                     kp=("제안한 주관사가 시공까지 맡을 수 있어 [[제안과 시공이 어긋나지 않습니다.]]", "공용부 시공은 입예협·관리주체 승인 후 · 범위·비용 협의"))),
        take(kind="landscape", sec=S2),
        take("[[조명 수직계열화]] · 유통 단계 없는 공급", sec=S2,
             kp=("유통 단계를 뺀 만큼 [[그대로 입주민 단가]]가 됩니다.", "주관사 직영 품목도 같은 4단계 심사 · 같은 단가 공개 · 입예협 최종 컨펌")),
        take("입주민을 지키는 [[3중 안전망]]", sec=S3),
        take("이행보증보험 [[2년 · 최대 10억]]", sec=S3),
        take("선보상 재원 · 하자 예치금 [[최대 1억원]]", sec=S3),
        take("[[4단계]] 공개 심사 프로세스", sec=S4),
        take("공동구매 단가를 지키는 [[4가지 장치]]", sec=S4),
        take("입주박람회 [[운영 계획]]", sec=S45),
        take("박람회장 배치와 [[인원 운영]] (안)", sec=S45),
        take("탕정 푸르지오 센터파크, [[이런 단지]]입니다", sec=S5),
        take("이 단지라서 [[먼저 챙길 것]]", sec=S5),
        take("선정부터 입주까지 [[추진 일정]] (안)", sec=S5),
        take("입찰 참가 자격 [[22개 항목]] 대응 ①", sec=S5), take("입찰 참가 자격 [[22개 항목]] 대응 ②", sec=S5),
        take("숫자로 보는 [[엣지컴퍼니]]", sec=S6),
        take("[[2,000세대 이상]] 초대형 단지를 맡아 왔습니다", sec=S6),
        take("탕정 푸르지오 센터파크에 드리는 [[핵심 혜택 6가지]]", sec="CLOSING"),
        take(kind="closing"),
        take(kind="contact"),
    ]
    return pages


def build():
    full = sys.argv[sys.argv.index("--full") + 1] if "--full" in sys.argv else None
    render_full_pages(full)
    emit(list(B.PAGES), B.OUT_HTML, "엣지컴퍼니 탕정 푸르지오 센터파크 입주박람회 주관사 제안서")
    if not os.environ.get("NO_NATIVE"):
        # 요약본 [2-2] — 본 제안서 틀 그대로, 표지는 숫자(15만원·10억·1억)로
        COVER.update(kind="impact", pill="입주박람회 주관사 요약 제안서")
        CLOSING_DROP[:] = ["03", "04"]  # 요약본 약속 장: 03 A 입주민 특화서비스 · 04 옵션 중복 확인 삭제(본부장 10-07)
        emit(summary_pages(), os.path.join(HERE, NAME22 + ".html"), "엣지컴퍼니 탕정 푸르지오 센터파크 요약 제안서")
        CLOSING_DROP[:] = []
        # 제출서류 07 회사소개서 — 연혁 장 + 제안서 01장(조직도 포함)
        COVER.update(kind="company")
        B.CSS += HIST_CSS
        emit(company_pages(), os.path.join(HERE, NAME07 + ".html"), "엣지컴퍼니 회사소개서")
        COVER.update(kind="stats", pill="입주박람회 주관사 제안서")


if __name__ == "__main__":
    build()
