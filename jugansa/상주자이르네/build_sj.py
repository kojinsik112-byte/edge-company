# -*- coding: utf-8 -*-
"""상주 자이르네 — 입주박람회 주관사 업무 수행 제안서 빌더(상주 자이르네 입주예정자협의회 '입주박람회 주관사 선정 입찰 공고' 2026.10.14 · 5항 9 '업무 수행 제안서').

북수원 빌더(../북수원디에트르더리체2/build_bs.py, 10-20)를 복제·개조했다. 기본틀(요약제안서 v5, ../요약제안서/build.py)은
건드리지 않고 불러와서 고친다. 다른 단지 폴더는 읽기만 한다.
- 표지: 상주 자이르네 입주박람회 주관사 업무 수행 제안서 (주간 투시도 sj_cover — 시행사 광고 문구 잘라냄)
- 목차 바로 뒤 = 공고 업무 ①~⑤ · 제안서 9 ①~⑤ · 참가 자격 4 대응표
- 07장 = 상주 업무 수행: 단지 이해 · ① 시공 단계 품질 · 하자 예방(자문 · 캘린더 7공정 · 중점 4곳 · 전문인력 6분야) · ② 입주 준비 ·
  ③ 가격 검증 · 품목 · 업체 · ④ A/S · 하자 · 신뢰 · ⑤ 협의회 지원 · 요청 관리 · 보고 · 실적 8건(별지3호) · 영주 자이 · 경관 · 일정 · 자격 4 · 이해관계 · 유의사항
- 협약 기간 = 협약 체결일 ~ 공동구매 품목 A/S 종결 시(공고 1) → 기간 표기는 'A/S 종결까지'
- 발전지원 = 세대당 12만원 상당 혜택 패키지(773세대 · 9,276만원 상당) · A · B · C는 예시, 입예협이 골라서(본부장 10-20)

사용: python3 build_sj.py [--no-pdf] [--final] → 엣지컴퍼니_상주자이르네_입주박람회_주관사_업무수행제안서.html/.pdf
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

# 압축본 스위치 — 본부장 10-14 저녁: 기본 = 134쪽 전체본(본부장이 직접 줄임), '--compact' 일 때만 compact.apply(약 109쪽)
# 본부장 10-15: 기본 출력 = 약 120쪽(115 ~ 125, compact.MID) · '--full' = 전체본 133쪽 · '--compact' = 압축본 약 109쪽
COMPACT = "--compact" in sys.argv
FULL = "--full" in sys.argv and not COMPACT
MID = not COMPACT and not FULL

NAME = "엣지컴퍼니_상주자이르네_입주박람회_주관사_업무수행제안서"
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
.rq4 td:last-child{white-space:nowrap}.rq4 td.k{min-width:150px}
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
.cv4>.cvart.cvx{right:0;top:0;bottom:0;height:auto;width:56%}
.cvart.cvx img{object-position:50% 82%}
.cvart.cvx:after{content:'';position:absolute;inset:0;background:
  linear-gradient(90deg,#0D1E33 0%,rgba(13,30,51,.82) 12%,rgba(13,30,51,.35) 28%,rgba(13,30,51,0) 46%),
  linear-gradient(180deg,#0D1E33 0%,rgba(13,30,51,.55) 14%,rgba(13,30,51,0) 34%,rgba(13,30,51,0) 66%,rgba(13,30,51,.7) 84%,#0D1E33 100%),
  linear-gradient(270deg,rgba(13,30,51,.45) 0%,rgba(13,30,51,0) 14%)}
.cvart.cvx .credit{z-index:1;right:40px;bottom:122px;color:rgba(255,255,255,.55)}
.cvart.cvx.osc img{object-position:69% 50%}
.cv4>.cvart.cvx.day{width:60%}.cvart.cvx.day img{object-position:62% 45%}
.cvart.cvx.day:after{background:
  linear-gradient(90deg,#0D1E33 0%,rgba(13,30,51,.78) 10%,rgba(13,30,51,.3) 24%,rgba(13,30,51,0) 38%),
  linear-gradient(180deg,rgba(13,30,51,.6) 0%,rgba(13,30,51,0) 16%,rgba(13,30,51,0) 70%,rgba(13,30,51,.75) 88%,#0D1E33 100%)}
.cv4 h1.cvx{font-size:48px}
.cv4 .gbar{width:150px;height:2px;background:var(--gold2);margin:26px 0 20px}
.cv4 h1{font-size:52px;line-height:1.28;margin-top:24px}
.cv4 .tag2{font-size:19px;line-height:1.6;margin-top:0}
.cv4 .stats{margin-top:34px}
.ctp .mid{width:46%}.ctp .contacts{grid-template-columns:1fr;gap:14px;margin-top:22px}.ctp .contacts b{font-size:27px}.ctp .contacts .me{grid-column:auto}.ctp .contacts .me b{font-size:23px}.ctp .contacts span{font-size:14px}.ctp .mid{width:48%}.ctp .addr{font-size:12.6px;line-height:1.8;margin-top:26px;color:var(--mute)}.ctp .addr b{color:var(--sub);font-weight:700;margin-right:4px}.ctp .gbar{margin:18px 0 6px}.ctp h1.cvx{font-size:46px}
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
.gal figure.cb{display:flex;flex-direction:column}
.gal figure.cb img{flex:1 1 0;min-height:0;height:auto;object-fit:contain;background:#0a1626}
.gal figure.cb figcaption{position:static;padding:8px 12px 9px;background:#0d1b2e}
.gal figure.cb.cv{display:block;position:relative;width:100%;height:100%}.gal figure.cb.cv img{position:absolute;left:0;top:0;width:100%;height:calc(100% - 54px);object-fit:cover;object-position:center}.gal figure.cb.cv figcaption{position:absolute;left:0;right:0;bottom:0;height:54px;box-sizing:border-box}
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
.dgrp{display:grid;gap:20px;flex:1;min-height:0}.dgrp .gp{display:flex;flex-direction:column;min-height:0;border:1px solid rgba(200,168,106,.38);border-top:2px solid var(--gold2);border-radius:14px;padding:12px 18px 14px;background:linear-gradient(180deg,rgba(235,203,143,.08),rgba(255,255,255,.012) 40%)}.dgrp .gh{display:flex;align-items:baseline;gap:10px;margin-bottom:12px;padding-bottom:9px;border-bottom:1px solid rgba(255,255,255,.1)}.dgrp .gh i{font-style:normal;font-size:11.5px;letter-spacing:.24em;color:var(--gold2);font-weight:700}.dgrp .gh b{font-size:19px;color:var(--gold)}.dgrp .gh small{margin-left:auto;font-size:12.5px;color:var(--mute)}.dgrp .docs{gap:18px}
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


# ============================================================ 01장 신설 — 상주 자이르네 업무 수행 제안 (재배치 후 07장)
# 근거: 상주 자이르네 입예협 '입주박람회 주관사 선정 입찰 공고'(2026.10.14) — 1 사업 · 단지 정보 · 협약 기간 · 2 주요 업무 ①~⑤ · 3 참가 자격 4 ·
# 4 일정 · 5 제출 서류 1 ~ 9(9 업무 수행 제안서 ①~⑤) · 6 선정 방식 · 7 유의사항 + 별지1 ~ 4호 + 확인된 단지 사실(data.py).
# → 확인된 사실과 이행할 수 있는 약속만 쓴다(공고 5항 '실현 가능한 내용만' · 7항 제안서 = 협약서의 일부 · 미이행 시 해지).
S0 = f"01. {D.SITE['name']} 맞춤 제안"
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


def slot(key):
    """단지 이미지 슬롯(data.IMG) → (파일명 또는 None, 단지 이미지 여부). 단지 파일이 없으면 대체 이미지(예시) 또는 None(중립 디자인)."""
    own, alt, _ = D.IMG[key]
    if os.path.exists(os.path.join(HERE, "assets_ins", own + ".jpg")):
        return own, True
    if alt and os.path.exists(os.path.join(HERE, "assets_ins", alt + ".jpg")):
        return alt, False   # 대체 이미지 = 타 단지 연출 예시(상주 단지 이미지 아님)
    return None, False


ST = D.SITE
_rec_n, _rec_hh = len(D.RECORDS), sum(r[3] for r in D.RECORDS)
R3 = D.RECENT3_OS
_r3_n, _r3_hh = len(R3), sum(r[3] for r in R3)
R5 = D.RECENT3_500  # 최근 3년 500세대 이상 입주박람회 진행 20개 단지(주관 16 = 1,000세대 이상 8 + 주관사 협약서 3 + 500 ~ 999세대 9 · 본부장 10-19 모두 주관)
_r5_n, _r5_hh = len(R5), sum(r[2] for r in R5)
_types_txt = " · ".join(a for a, _ in ST["types"])
_types_full = " · ".join(f"{a} {n}" for a, n in ST["types"])

T_DIV = "상주 자이르네를 위한 [[업무 수행 제안]]"
T_MAP = "공고 업무 ①~⑤ · 참가 자격, [[이 쪽에]] 있습니다"
T_SITE = f"{ST['name']}, [[이런 단지]]입니다"
T_FIRST = "773세대 · 전 세대 중대형이라 [[먼저 챙길 것]]"
T_C1 = "① 시공 단계 품질 · 하자 예방, [[협약 직후부터]] 시작합니다"
T_C2 = "공정별 자문 캘린더 · [[7개 공정]]"
T_C3 = "단지 맞춤 자문 중점 [[4곳]]"
T_C4 = "분야별 전문인력 [[6개 분야]]"
T_C5 = "② 입주 준비 - 마감재 확인 · [[사전점검]] · 하자점검"
T_R500 = f"공식 입주박람회 주관 실적 [[{len(D.SJ_REC)}건]]"
T_YJ = "경북 북부 자이 단지 [[763세대]] 박람회를 주관했습니다"
T_TRUST = "협약 이행 · [[손해배상]]을 약속하는 장치"
T_STABLE = "브랜드 품질 · [[무상보증기간]]"
T_FACT = "직영 운영 · [[온 · 오프라인 투명 운영]]"
T_CHECK = "③ 품목별 가격 검증 - [[검수하고, 보상합니다]]"
T_ITEMS = "773세대 맞춤 [[품목 구성]] (안)"
T_VENDORS = "품목별 [[예상 참가 업체]]"
T_VMGT = "참여업체, [[선정부터 설치까지]] 관리합니다"
T_REQ = "협의회 요청 · 시공사 협의, [[관리표로]] 끝까지 챙깁니다"
T_AS = "④ A/S 정책 - 주관사 [[한 창구]], 업체 부담은 늘리지 않습니다"
T_DEFECT = "하자 · 민원 접수, [[책임부터]] 나눕니다"
T_SUPPORT = "⑤ 협의회 지원, [[범위를 정해]] 약속합니다"
T_SPECIAL = f"{ST['short']} [[특화 제안]]"
T_LX = "단지 외부 경관조명, [[입주 전에]] 진단합니다"
T_LX2 = "물놀이터 · 정원 · 산책로, [[밤길까지]] 살핍니다"
T_MON1 = "단계별 업무 일정 ① [[협약 ~ 2028.12 시공 단계]]"
T_MON2 = "단계별 업무 일정 ② [[2029.01 ~ A/S 종결]]"
T_PM = "본사는 울산, 대응은 [[상주 현장]]에서"
T_STAFF = "입예협 [[전담 체계]] - 운영 인원 12명"
T_PRIV = "입주민 개인정보 · 단지 정보는 [[제안 목적에만]] 씁니다"
T_REPORT = "정기 보고서, [[항목과 시점]]을 정해 둡니다"
T_EXPO = "입주박람회 [[운영 계획]]"
T_SAFE = "행사장 [[안전 · 현장관리]] 계획"
T_QUAL = "입찰 참가 자격 [[4개 항목]] 대응"
T_CONF = "이해관계 · 청렴, [[먼저 밝힙니다]]"
T_NOTE = "선정 방식 · 유의사항, [[그대로 지킵니다]]"
T_PEOPLE = "대표자 · 핵심 운영인력 [[수행 경험]]"
T_HIST = "엣지컴퍼니 [[연혁]] · 주요 이력"
T_CPL = "입주민 [[컴플레인]], 이렇게 해결합니다"
T_CORE6 = f"{ST['short']}에 드리는 [[핵심 제안 6가지]]"
T_FUNDCH = f"세대당 {D.FUND}만원 상당 발전지원금, [[입예협이 골라서]] 받습니다"
# 07장 순서(reorg.py가 이 목록 하나로) — 대응표(T_MAP)는 목차 바로 뒤로 뺀다(reorg) · 서류 심사 중점(시공 단계 지원 · 전문인력)을 앞에
CH07 = ["T_SITE", "T_FIRST", "T_C1", "T_C2", "T_C3", "T_C4", "T_C5",
        "T_CHECK", "T_ITEMS", "T_VENDORS", "T_VMGT", "T_STABLE", "T_FACT",
        "T_AS", "T_DEFECT", "T_TRUST", "T_SUPPORT", "T_REQ", "T_REPORT",
        "T_R500", "T_YJ", "T_SPECIAL", "T_LX", "T_LX2", "T_MON1", "T_MON2", "T_PM", "T_STAFF", "T_PRIV",
        "T_QUAL", "T_BOND", "T_CONF", "T_NOTE"]
CH07_BL = ["① 시공 단계 품질 · 하자 예방 · 전문인력 6개 분야", "② 입주 준비 · ③ 박람회 · 가격 검증", "④ A/S · 민원 · ⑤ 협의회 지원", "실적 8건 · 영주 자이 · 일정 · 자격 · 청렴"]

new("divider", n="01", title=T_DIV, bl=CH07_BL)

# ------------------------------------------------------------ 공고 2항 주요 업무 ①~⑤ · 5항 9 제안서 ①~⑤ · 3항 참가 자격 ↔ 쪽 대응표(목차 바로 뒤)
MAP11 = [  # (구분, 공고 항목, 엣지컴퍼니 제안 핵심, [PGREF 키])
    ("업무 ①", "시공 단계 품질 · 하자 예방(공정별 자문 · 기술 검토 · 하자 취약 부위 · 근거자료)", "협약 직후 · 7개 공정 은폐 전 자문 · 10영업일 서면 회신", ["c1", "c2", "c3", "c4"]),
    ("업무 ②", "입주 준비(마감재 확인 · 사전점검 · 하자점검 지원)", "마감재 대조표 · 체크리스트 · 현장 지원 · 하자 추적", ["c5", "precheck"]),
    ("업무 ③", "입주박람회 운영(기획 · 운영 · 참여업체 선정 · 품목별 가격 검증)", f"{ST['expo']} 2 ~ 3일(안) · 4단계 심사 · 가격 검수", ["expo", "screen", "vmgt", "check"]),
    ("업무 ④", "사후관리(공동구매 A/S · 하자보수 이행 · 민원 · 분쟁 대응)", "한 창구 · 24시간 1차 회신 · 48시간 하자보수 · 선보상", ["as", "defect", "call", "rule1"]),
    ("업무 ⑤", "협의회 지원(행사 · 홍보 지원 · 협의한 업무)", "행사별 지원 범위 · 요청 관리표 · 정기 보고", ["support", "req", "report"]),
    ("제안서 9", "업무 수행 제안서 ①~⑤(시공 단계 · 입주 준비 · 박람회 · A/S · 협의회)", "업무 ①~⑤와 같은 순서 · 쪽 제목 앞 번호", ["c1", "c5", "check", "as", "support"]),
    ("자격 1", "업종 사업자등록 · 국세 · 지방세 체납 없음", "‘전시, 박람회 및 행사 대행업’ · 완납(제출서류 2 · 3)", ["qual"]),
    ("자격 2", "타 단지 공식 입주박람회(협의회 협약) 주관 실적", f"{len(D.SJ_REC)}건 · 별지3호(제출서류 7) · 영주 자이 763세대", ["r500", "yj"]),
    ("자격 3", "6개 분야 자격 전문가 직접 고용 · 협력 계약", "전기 · 조경 직접 + 4개 분야 협력(별지2호)", ["c4"]),
    ("자격 4", "시행 · 시공 · 분양대행사 · 협의회 임원 이해관계 고지", "해당 없음 · 직영 품목 공개 · 자문 ↔ 영업 분리", ["conf"]),
    ("심사 중점", "시공 단계 지원 계획 · 분야별 전문인력", "자문 캘린더 · 산출물 · 전문인력 표를 07장 앞에", ["c2", "c4"]),
]
new("std", sec=S0, title=T_MAP,
    lead="공고 2항 업무 ①~⑤ · 5항 9 제안서 · 3항 참가 자격을 어느 쪽에서 답하는지 정리했습니다(쪽 = 우측 상단 번호).",
    body=table(["구분", "공고 항목", "엣지컴퍼니 제안 핵심", "제안서 쪽"], "".join(
        f'<tr><td class="n">{a}</td><td class="k">{t(b)}</td><td>{t(c)}</td><td class="pg">{PGS(ks)}</td></tr>'
        for a, b, c, ks in MAP11), "m9 m13"),
    kp=("공고 업무 ①~⑤와 참가 자격을 [[쪽 번호로]] 찾으실 수 있습니다.", "업무 수행 제안의 본문 = 07장(시공 단계 지원 · 전문인력을 앞에) · 회사 역량은 01장"))
B.CSS += (".tbl.m9 td{padding:7px 12px;font-size:14px;line-height:1.3}.tbl.m9 td.k{font-size:15px;width:31%}"
          ".tbl.m9 td.n{width:48px;white-space:nowrap;font-size:13.5px}"
          ".tbl.m9 td.pg{white-space:nowrap;color:var(--gold);font-weight:800;font-size:14px;font-variant-numeric:tabular-nums;width:17%}"
          ".tbl.m13 td{padding:5px 12px;font-size:13.4px;line-height:1.28}.tbl.m13 td.k{font-size:13.8px;width:40%}.tbl.m13 td.n{width:74px;font-size:12.5px}"
          ".tbl.m13 tr:nth-child(7) td{border-top:1.5px solid rgba(200,168,106,.55)}")

# ------------------------------------------------------------ 단지 이해
new("std", sec=S0, title=T_SITE,
    lead="입찰 공고 1 사업 및 단지 정보와 공개 분양 자료 기준 - 입주예정자협의회(이하 입예협)와 시공 단계부터 함께 설계합니다.",
    body=B.cards([
        dict(lb="SCALE", big=f"{ST['households']:,}", unit="세대", nm=f"{ST['buildings']}개 동 · {ST['floors']}",
             ds="전 세대 전용 84 ~ 135㎡ · 84㎡ 565세대([[73.1%]]) · 99㎡ 126 · 125㎡ 78 · 112 · 135㎡ 4"),
        dict(lb="BUILDER", big="자이", nm=f"시공 {ST['builder']} · 자이르네",
             ds="시행수탁 교보자산신탁 · 시행위탁 ㈜고은건설 - 현장 확인 · 질의는 사업주체 · 시공사 협의로"),
        dict(lb="MOVE-IN", big="2029", unit=".04", nm="입주 예정",
             ds=f"공고(2026.10)부터 약 {ST['months']}개월 - 시공 단계 자문부터 시작"),
        dict(lb="LOCATION", big="함창", nm="상주시 함창읍 윤직리", hl=True,
             ds=f"{ST['address']} · 100% 지하주차 · 스카이 커뮤니티(분양 자료)"),
    ]),
    kp=(f"{ST['households']:,}세대 [[전 세대 중대형]] - 품목 · 견적을 84㎡ 표준과 99 ~ 135㎡ 맞춤으로 나눕니다.",
        "공고 단지 정보(773세대 · 2029년 4월 입주 예정) · 타입 · 특화는 공개 분양 자료 기준 · 일정은 변경될 수 있음"))

new("std", sec=S0, title=T_FIRST,
    lead="773세대 · 전 세대 84㎡ 이상 - 중대형 구성과 넓은 계약자 분포, 이미 고른 유상옵션을 운영 계획에 먼저 반영합니다.",
    body=B.rows([
        ("업체 수는 규모에 맞게", "773세대는 품목당 업체 수를 [[수요조사로 정해]] 같은 품목 과밀 출점을 막고, 업체당 계약과 단가를 함께 지킵니다."),
        ("84㎡ 표준 + 중대형 맞춤", "84㎡ 565세대는 타입별 [[표준 견적표]]로, 99 · 112 · 125 · 135㎡ 208세대는 면적별 가구 배치 · 시공 견적을 따로 만듭니다."),
        ("멀리 사는 계약자도", "상주 · 문경 · 구미 · 대구 등으로 계약자가 흩어질 수 있어 [[사전 예약 상담 · 온라인 박람회]]를 같은 공동구매가로 엽니다."),
        ("유상옵션 겹침 확인", "분양 때 고른 유상옵션 · 기본 제공 품목은 권하지 않고 [[미선택 · 추가 수요만]] 모집합니다(모집공고 · 계약 자료로 확인)."),
    ], title_w=230),
    kp="이미 고른 옵션은 권하지 않고, [[남은 수요]]만 같은 조건으로 비교해 드립니다.")

# ------------------------------------------------------------ ① 시공 단계 품질 · 하자 예방 지원(공고 2항 ① · 6항 서류 심사 중점 · 7항 협약 직후 시작)
new("std", sec=S0, title=T_C1,
    lead="공고 2항 ① · 7항 - 시공 단계 지원은 협약 체결 직후 시작합니다. 분야별 전문가가 공정마다 자문하고, 협의회 요청은 기술 검토로 답하며, 하자 취약 부위를 근거자료로 남깁니다.",
    body=('<div class="nb"><div class="c1x">'
          + "".join(f'<div class="c1c{" hl" if i == 0 else ""}"><i>{a}</i><h3>{b}</h3><ul>' + "".join(f"<li>{t(x)}</li>" for x in xs) + f'</ul><p>{t(o)}</p></div>'
                    for i, (a, b, xs, o) in enumerate([
                        ("PROCESS", "공정별 자문", ["7개 공정마다 [[은폐 전]] 1회 이상 - 숨기기 전에 봅니다",
                                                  "공정에 맞는 분야 전문가(건축 · 토목 · 조경 · 전기 · 기계설비 · 소방)가 자문",
                                                  "현장 확인은 사업주체 · 시공사가 승인한 범위 · 일정 안에서"], "산출물: 공정별 자문 보고서 · 사진대장"),
                        ("REVIEW", "협의회 요청 기술 검토", ["협의회 서면 요청 → 담당 분야 지정",
                                                       "[[10영업일 안에 서면 회신]](현장 확인이 필요하면 일정 협의)",
                                                       "시공사 질의서 · 공문 초안을 협의회 이름으로 준비 · 협의 동석"], "산출물: 기술 검토 회신서 · 질의서 초안"),
                        ("DEFECT", "하자 취약 부위 · 근거자료", ["공정별 하자 취약 부위 목록 · 확인 사진 · 위치 표시",
                                                         "시공사 회신 · 보완 여부를 관리표로 추적",
                                                         "목록은 ② 사전점검 체크리스트로 그대로 이어짐"], "산출물: 취약 부위 목록 · 보완 추적표"),
                    ]))
          + '</div><div class="c1n"><b>자문의 범위</b><span>협의회 편에서 보고 기록합니다 - 법정 감리 · 하자 판정 권한이 아니며, 설계 변경 · 공사 지시는 하지 않습니다. 판단은 협의회 · 사업주체 · 시공사 협의로 정합니다.</span></div></div>'),
    kp=("시공 단계 자문 비용은 [[주관사 부담]] - 협의회 · 입주민에게 따로 청구하지 않습니다.",
        "드론 · 열화상 정밀 진단 · 전 타입 도면 분석 보고서는 08장 B 패키지(세대당 " + str(D.FUND) + "만원 상당 범위)에서 입예협이 추가 선택"))
B.CSS += (".c1x{display:grid;grid-template-columns:1.08fr 1fr 1fr;gap:16px;flex:1;min-height:0}"
          ".c1c{border:1px solid var(--line);border-top:2px solid var(--gold2);border-radius:14px;padding:14px 18px;display:flex;flex-direction:column;min-height:0;"
          "background:linear-gradient(180deg,rgba(235,203,143,.08),rgba(255,255,255,.01) 45%)}"
          ".c1c.hl{border-color:rgba(235,203,143,.7);background:linear-gradient(180deg,rgba(235,203,143,.16),rgba(235,203,143,.03))}"
          ".c1c i{font-style:normal;font-size:12px;letter-spacing:.18em;color:var(--gold2);font-weight:700}"
          ".c1c h3{font-size:23px;font-weight:800;color:var(--gold);margin:2px 0 10px}"
          ".c1c ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:13px;flex:1}"
          ".c1c li{font-size:16px;line-height:1.48;padding-left:14px;position:relative}.c1c li:before{content:'';position:absolute;left:0;top:9px;width:6px;height:6px;border-radius:50%;background:var(--gold2)}"
          ".c1c p{margin-top:10px;border-top:1px dashed rgba(200,168,106,.45);padding-top:8px;font-size:14px;color:var(--gold);line-height:1.45}"
          ".c1n{display:grid;grid-template-columns:150px 1fr;gap:14px;align-items:center;border:1px dashed rgba(200,168,106,.55);border-radius:12px;padding:10px 16px;margin-top:14px}"
          ".c1n b{font-size:16px;color:var(--gold)}.c1n span{font-size:14px;color:var(--sub);line-height:1.5}")

C2 = [  # (공정, 자문 시점, 담당 분야, 확인 포인트, 산출물)
    ("1 토공 · 기초", "협약 직후 · 현재 공정 확인", "토목 · 건축", "지반 · 기초 · 배수 계획 · 굴착 안전 · 현재 공정 기록", "1차 자문 보고서 · 현황 사진대장"),
    ("2 지하 골조 · 방수", "지하층 방수 · 되메우기 전", "건축 · 토목", "[[100% 지하주차장]] 구조 · 방수 · 결로 · 차수", "방수 · 결로 취약 부위 목록"),
    ("3 지상 골조", "기준층 골조 중 · 동절기 전", "건축", "29층 골조 · 동절기 콘크리트 양생 · 바닥 차음", "동절기 공정 확인표"),
    ("4 창호 · 외벽 · 최상층", "창호 설치 전후 · 옥상 방수 전", "건축 · 기계설비", "창호 기밀 · 외벽 누수 · [[스카이 커뮤니티]] 최상층 방수 · 단열", "누수 취약 부위 목록"),
    ("5 설비 · 전기 · 소방", "배관 · 배선 [[은폐 전]]", "기계설비 · 전기 · 소방", "배관 경로 · 배선 · 지하주차장 LED · 디밍 · 소방 설비 위치", "분야별 체크리스트"),
    ("6 내부 마감", "마감 착수 전", "건축 · 전기", "마감재 대조(모집공고 · 견본주택) · 세대 조명 · 콘센트", "마감재 대조표 → ② 입주 준비"),
    ("7 조경 · 외부", "식재 · 포장 전", "조경 · 토목 · 전기", "대지 1/4 이상 조경 · 산책로 · 배수 · 수목 · 보행등", "조경 · 외부 체크리스트"),
]
new("std", sec=S0, title=T_C2,
    lead="공고 2항 ① 공정별 자문 - 공정이 덮이기 전에 분야 전문가가 확인합니다. 시점은 시공사 공정표에 맞춰 협의회와 정합니다.",
    body=table(["공정", "자문 시점", "담당 분야", "확인 포인트", "산출물"], "".join(
        f'<tr><td class="k">{t(a)}</td><td class="m">{t(b)}</td><td class="f">{t(c)}</td><td>{t(d)}</td><td class="o">{t(e)}</td></tr>' for a, b, c, d, e in C2), "c2t")
         + '<div class="hflow"><span>공정표 확인</span><i>›</i><span>은폐 전 자문</span><i>›</i><span>보고서 · 사진대장</span><i>›</i>'
           '<span>시공사 질의 · 회신</span><i>›</i><span>보완 추적 · 정기 보고</span></div>',
    kp=("공정 7개마다 [[최소 1회]] - 협의회가 요청하면 그 공정에 수시 자문을 더합니다.", "현장 출입 · 일정은 사업주체 · 시공사 승인 범위 · 공정 순서 · 시점은 실제 공정표 기준으로 조정"))
B.CSS += (".tbl.c2t td{padding:10px 12px;font-size:14.6px;line-height:1.4}.tbl.c2t td.k{width:17%;font-size:15.5px;white-space:nowrap}"
          ".tbl.c2t td.m{width:17%;color:var(--sub)}.tbl.c2t td.f{width:13%;white-space:nowrap}.tbl.c2t td.o{width:20%;color:var(--gold)}")

C3 = [  # (라벨, 이름, 볼 것, 분야)
    ("UNDERGROUND", "100% 지하주차장", "구조 · 방수 · 결로 · 환기 - 지하층은 입주 후 고치기 가장 어려운 곳이라 되메우기 전에 봅니다. 조명은 LED · 디밍 동작까지.", "건축 · 토목 · 전기 · 기계설비"),
    ("FACADE", "29층 외벽 · 창호", "동절기 골조 양생 · 창호 기밀 · 외벽 누수 - 고층 외벽은 누수가 생기면 원인 찾기가 어렵습니다.", "건축"),
    ("ROOFTOP", "스카이 커뮤니티 · 최상층", "옥상 방수 · 단열 · 결로 - 공용시설이 최상층에 있어 방수 하자는 커뮤니티 운영까지 멈춥니다.", "건축 · 기계설비"),
    ("LANDSCAPE", "조경 · 산책로", "대지 1/4 이상 조경 · 약 1.3km 산책로(분양 자료) - 배수 · 수목 하자 · 야간 보행등 밝기.", "조경 · 토목 · 전기"),
]
new("std", sec=S0, title=T_C3,
    lead="공고 2항 ① 하자 취약 부위 확인 - 공개 분양 자료로 본 이 단지의 특징 가운데 하자가 생기면 비용과 불편이 큰 곳 4곳을 먼저 봅니다.",
    body=B.cards([dict(lb=a, nm=b, ds=c + f" · 담당 [[{d}]]") for a, b, c, d in C3])
         + '<div class="gq3"><div><b>자문 보고서</b><span>공정 · 위치 · 확인 내용 · 사진 · 의견 - 협의회에 공유</span></div>'
           '<div><b>취약 부위 목록</b><span>위치 · 유형 · 시공사 회신 · 보완 여부를 끝까지 추적</span></div>'
           '<div><b>질의서 초안</b><span>협의회 이름으로 시공사에 보낼 질의서 · 공문 초안</span></div></div>',
    kp=("하자 예방의 핵심은 [[덮기 전 확인]]입니다.", "특화 내용은 공개 분양 자료 기준 · 실제 설계 도서 · 공정표로 다시 확인"))

_ex_rows = ""
_EXW = {"건축": "골조 · 방수 · 창호 · 외벽 · 마감", "토목": "토공 · 기초 · 지하 구조 · 배수 · 외부",
        "조경": "조경 · 식재 · 산책로 · 수목 하자", "전기": "배선 · 조명 · 지하주차장 LED · 디밍 · 사전점검 전기 항목",
        "기계설비": "급배수 · 환기 · 냉난방 배관 · 최상층 설비", "소방": "소방 설비 · 배관 · 감지기 · 피난 동선"}
for f_, kind, nm, lic, org in D.EXPERTS:
    if nm:
        who = f"{nm} · {lic or ''} · {org or ''}"
    elif kind == "직접":
        who = {"전기": f"사내 전기 기술자 3명 · {D.ELEC_LICENSE}", "조경": "사내 조경 전문 인력(임원)"}.get(f_, "사내 인력")
    else:
        who = "협력 계약 체결 후 성명 · 자격 · 계약서 사본 제출(별지2호)"
    _ex_rows += (f'<tr><td class="k">{f_}</td><td class="c{" d" if kind == "직접" else ""}">{kind}</td>'
                 f'<td>{t(_EXW[f_])}</td><td>{t(who)}</td></tr>')
new("std", sec=S0, title=T_C4,
    lead="공고 3항 · 별지2호 - 건축 · 토목 · 조경 · 전기 · 기계설비 · 소방 6개 분야를 직접 고용 또는 협력 계약으로 확보해, 협의회가 요청하면 자문합니다.",
    body=table(["분야", "고용", "맡는 공정 · 업무", "인력 · 증빙(별지2호 · 제출서류 6)"], _ex_rows, "c4t")
         + '<div class="c4b"><div class="pm"><i>전담 책임자(PM)</i><b>' + D.MANAGER[1] + '</b>'
           '<span>시공 단계 자문 · 박람회 · A/S 전 과정 총괄 · 협의회 단일 창구</span></div>'
           '<div><i>이해관계 없음</i><b>시행 · 시공사와 무관한 전문가</b><span>이 단지 사업주체 · 시공사와 하도급 · 지분 관계 없는 인력만 배치</span></div>'
           '<div><i>자문 ↔ 영업 분리</i><b>판매 권유 금지</b><span>자문 인력은 공동구매 품목을 권하지 않음 · 교체 시 협의회와 사전 협의</span></div></div>',
    kp=("전기는 [[전기공사업 등록 업체]]가 직접 - 6개 분야 가운데 회사 등록으로 증명되는 분야입니다.",
        "자격증 사본 · 재직 · 협력 증빙은 별지2호와 함께 제출 · 인력 교체 시 협의회 사전 협의"))
B.CSS += (".tbl.c4t td{padding:11px 14px;font-size:15px;line-height:1.42}.tbl.c4t td.k{width:12%;font-size:16.5px}"
          ".tbl.c4t td.c{width:9%;text-align:center;white-space:nowrap;color:var(--sub)}.tbl.c4t td.c.d{color:var(--gold);font-weight:800}"
          ".tbl.c4t td:nth-child(3){width:34%}"
          ".c4b{display:grid;grid-template-columns:1.25fr 1fr 1fr;gap:12px;margin-top:16px}"
          ".c4b>div{border:1px solid var(--line);border-radius:12px;padding:11px 16px;display:flex;flex-direction:column;gap:3px}"
          ".c4b>div.pm{border-color:rgba(235,203,143,.7);background:rgba(235,203,143,.08)}"
          ".c4b i{font-style:normal;font-size:11.5px;letter-spacing:.12em;color:var(--gold2);font-weight:700}"
          ".c4b b{font-size:17px;color:var(--gold)}.c4b span{font-size:13.5px;color:var(--sub);line-height:1.45}")

# ------------------------------------------------------------ ② 입주 준비 지원(공고 2항 ②)
C5 = [  # (단계, 시기, 주관사 지원, 산출물)
    ("마감재 확인", "마감 착수 전 ~ 사전점검 전", "모집공고 · 견본주택 마감재 목록과 시공 마감재 대조 · 협의회 확인 동행(시공사 승인 범위)", "마감재 대조표"),
    ("사전점검 준비", "사전점검 1개월 전", "타입별 체크리스트 - [[공정 자문 때 찾은 취약 부위]]를 반영 · 입주민 안내 콘텐츠(입예협 승인)", "체크리스트 · 안내문"),
    ("사전점검 당일", "사전점검 2 ~ 3일", "안내 부스 · 하자 접수 보조 · 동선 안내 · 요청 분야 전문가 현장 지원", "하자 접수 집계"),
    ("하자점검 · 재점검", "사전점검 후 ~ 입주", "접수 하자의 시공사 처리 · 회신 추적 · 재점검 동행 · 미처리 목록 관리", "하자 처리 현황표"),
    ("입주 후 하자", "입주 ~ A/S 종결", "공용부 · 세대 하자 접수 대행 · 시공사 처리 추적 · 정기 보고", "정기 하자 현황 보고"),
]
new("std", sec=S0, title=T_C5,
    lead="공고 2항 ② 입주 준비 지원 - 시공 단계 자문 기록을 그대로 이어받아, 마감재 확인부터 사전점검 · 하자점검까지 같은 담당이 챙깁니다.",
    body=table(["단계", "시기", "주관사 지원", "산출물"], "".join(
        f'<tr><td class="k">{a}</td><td class="m">{t(b)}</td><td>{t(c)}</td><td class="o">{t(d)}</td></tr>' for a, b, c, d in C5), "c5t")
         + '<div class="hflow"><span>① 공정 자문 기록</span><i>›</i><span>마감재 대조</span><i>›</i><span>사전점검 체크리스트</span><i>›</i>'
           '<span>하자 접수 · 추적</span><i>›</i><span>재점검 · 입주</span></div>',
    kp=("사전점검은 [[공정 자문의 결과]]로 준비합니다 - 어디를 볼지 알고 들어갑니다.", "하자 판정 · 보수는 시공사 하자 처리 절차 · 사전점검 대행(유료)은 08장 할인 · 일정은 시공사 · 입주지원센터 일정에 맞춤"))
B.CSS += (".tbl.c5t td{padding:13px 14px;font-size:15.2px;line-height:1.45}.tbl.c5t td.k{width:15%;font-size:16.5px;white-space:nowrap}"
          ".tbl.c5t td.m{width:19%;color:var(--sub)}.tbl.c5t td.o{width:17%;color:var(--gold)}")

# ------------------------------------------------------------ 실적(별지3호) · 영주
_r10 = "".join(f'<tr><td class="n">{i:02d}</td><td class="k">{t(nm)}</td><td>{t(loc)}</td><td class="r">{n:,}</td><td class="m">{t(when)}</td><td class="e">{t(ev)}</td></tr>'
               for i, (nm, loc, n, when, _who, ev) in enumerate(D.SJ_REC, 1))
new("std", sec=S0, title=T_R500,
    lead="공고 3항 실적 · 별지3호 - 해당 단지 입주예정자협의회와 협약한 공식 입주박람회 주관 실적입니다. 별지3호와 같은 값이고, 실적마다 증빙을 붙였습니다(제출서류 7).",
    body=table(["NO", "단지", "소재지", "세대", "행사 기간", "증빙"], _r10
               + f'<tr class="sum"><td></td><td class="k">합계 {len(D.SJ_REC)}건</td><td></td><td class="r">{sum(r[2] for r in D.SJ_REC):,}</td><td colspan="2">세대수 = NICE 연혁 · 단지 공식 세대수 · 레이카운티는 2차 행사</td></tr>', "r10"),
    kp=(f"공식 입주박람회 주관 [[{len(D.SJ_REC)}건 · {sum(r[2] for r in D.SJ_REC):,}세대]] - 모두 증빙을 붙였습니다.",
        "증빙 = 주관사 협약서 · 박람회장 공식 행사일정 · 입주자 카페 공지 · NICE 기업신용평가 연혁 · 실적 확약서 · 허위 기재 시 해지를 받아들입니다"))
B.CSS += (".tbl.r10 td{padding:10px 12px;font-size:14.6px;line-height:1.35}.tbl.r10 td.k{font-size:15.5px}"
          ".tbl.r10 td.n{width:40px;font-size:13px}.tbl.r10 td.r{text-align:right;font-variant-numeric:tabular-nums;font-weight:700;white-space:nowrap;width:70px}"
          ".tbl.r10 td.m{white-space:nowrap;font-variant-numeric:tabular-nums;width:160px}.tbl.r10 td.e{font-size:12.8px;color:var(--sub);width:27%}"
          ".tbl.r10 tr.sum td{border-top:1.5px solid rgba(200,168,106,.6);color:var(--gold);font-weight:800}.tbl.r10 tr.sum td:last-child{font-weight:500;font-size:12.5px;color:var(--sub)}")

new("std", sec=S0, title=T_YJ,
    lead="같은 경북 북부, 비슷한 규모(763세대 ↔ 773세대)의 자이 단지 입주박람회를 입주예정자협의회와 협약해 직접 주관했습니다.",
    body=('<div class="nb"><div class="dtx">'
          '<figure><img src="assets_ins/cafe_yeongju.png" alt="영주자이 시그니처 입주자 공식 카페 엣지컴퍼니 공지사항 게시판">'
          '<figcaption>영주자이 시그니처 입주자 공식 카페 ‘엣지컴퍼니 공지사항’ 게시판 · 입주민 닉네임 가림</figcaption></figure>'
          '<div class="dtc">'
          + "".join(f'<div class="{c}"><i>{a}</i><b>{t(b)}</b><p>{t(d)}</p></div>' for c, a, b, d in [
              ("hl", "DONE · 주관", "영주자이 시그니처 · 763세대", "경북 영주 · 입주예정자협의회와 협약 → 입주박람회 2026.08.29 ~ 30 영주 그랜드컨벤션(2일)"),
              ("", "상주로 옮길 것", "지역 행사장 2일 운영 체크표", "입구 접수 · 혜택 안내 · 행사 후 개인정보 파기 고지 · 경북 · 대구권 참여업체 풀"),
              ("", "상주에서 더할 것", "시공 단계 자문 · 원거리 계약자 대응", "영주에 없던 ① 시공 단계 자문을 새로 넣고, 사전 예약 상담 · 온라인 박람회를 함께 엽니다"),
          ])
          + '</div></div></div>'),
    kp=("경북 북부 자이 단지 [[763세대]] 박람회를 직접 운영해 봤습니다.", "시공사 · 단지 조건은 단지마다 다르므로 상주 기준으로 다시 확인 · 영주 운영 수치는 PT에서 원자료로 설명"))
B.CSS += (".dtx{display:grid;grid-template-columns:1.35fr 1fr;gap:20px;flex:1;min-height:0}"
          ".dtx figure{margin:0;display:flex;flex-direction:column;min-height:0;border:1px solid var(--line);border-radius:12px;padding:10px;background:rgba(0,0,0,.18)}"
          ".dtx figure img{flex:1;min-height:0;width:100%;object-fit:contain;border-radius:4px}"
          ".dtx figcaption{font-size:12px;color:var(--sub);margin-top:8px;line-height:1.4}"
          ".dtc{display:flex;flex-direction:column;gap:12px;min-height:0}"
          ".dtc>div{flex:1;border:1px solid var(--line);border-top:2px solid var(--gold2);border-radius:12px;padding:12px 16px;display:flex;flex-direction:column;gap:4px;justify-content:center}"
          ".dtc>div.hl{border-color:rgba(235,203,143,.7);background:linear-gradient(180deg,rgba(235,203,143,.14),rgba(235,203,143,.03))}"
          ".dtc i{font-style:normal;font-size:11.5px;letter-spacing:.16em;color:var(--gold2);font-weight:700}"
          ".dtc b{font-size:19px;color:var(--gold)}.dtc p{font-size:14px;color:var(--sub);line-height:1.5}")

# ------------------------------------------------------------ ④ 신뢰 · 손해배상
new("std", sec=S0, title=T_TRUST,
    lead="공고 2항 ④ · 7항 - 협약은 문서대로 지키고, 하자 · A/S · 분쟁의 손해배상은 업체가 빠져도 끝까지 이행되도록 구조를 먼저 짰습니다.",
    body=('<div class="nb"><div class="pmx">'
          '<div class="pc"><h3><i>AGREEMENT</i>협약 이행</h3>'
          + B.rows([
              ("같은 조건", "제안서 = 협약서의 일부 - PT에서 [[바꾸거나 더하지 않습니다.]]"),
              ("이행 담보", "[[이행보증보험증권]]은 협약 후 협의회를 피보험자로, 입주 일정에 맞춰 입예협과 발급 시점을 확인해 발급합니다. 보험기간 입주 개시 1년 전 ~ 입주 개시 후 1년(금액은 협약 때 확정)."),
              ("행사 보험", "[[행사배상책임보험]] 박람회 기간 가입 · 증권 사본 제출"),
              ("시정 · 해지", "서면 시정 요청 후에도 개선하지 않으면 협약 해지를 받아들입니다(공고 7항)."),
          ], title_w=110) + '</div>'
          '<div class="pc"><h3><i>DEFECT</i>하자 이행</h3>'
          + B.rows([
              ("업체 서약", "참여업체 전원 특약이행각서 9개 항 - 하자보수 이관 · 보증 기간 · 지연 배상"),
              ("처리 기한", "[[24시간 안에 1차 회신]] · 48시간 하자보수 원칙"),
              ("선보상", "업체가 응하지 않으면 주관사가 먼저 보상하고 업체와 정산"),
              ("업체 도산", "동종업체로 이관 · 그 A/S 비용은 주관사가 전액 부담"),
          ], title_w=110) + '</div></div></div>'),
    kp=("업체가 사라져도 [[하자보수 · 손해배상 책임]]은 남도록 계약으로 묶어 둡니다.", "특약이행각서 · 패널티 · 선보상 재원은 04 · 05장 · 환불 규정 전문은 03장"))

STABLE = [  # (품목군, 브랜드 · 품질 확보 기준, 무상보증 기준)
    ("가전 · 시스템에어컨", "제조사 공식 판매점 · 정품 · [[모델코드 공개]]", "제조사 보증 기간 + 설치 하자는 설치 업체 보증"),
    ("조명 · 전기", "KC 인증 제품 · 전기공사업 등록 업체 시공", "계약서에 품목별 명시 · 최소 2년"),
    ("커튼 · 블라인드 · 전동", "타입별 실측 제작 · 원단 · 모터 사양 공개", "계약서에 품목별 명시 · 최소 2년"),
    ("가구 · 수납 · 중문", "브랜드 대리점 · 친환경 등급 서류 확인", "제조사 보증 + 설치 하자 최소 2년"),
    ("시공 품목", "청소 · 줄눈 · 탄성 · 방충망 · 필름 - 자재 사양 · 인증 서류 확인 · 인근 업체", "재시공 · 재방문 기준을 계약서에 명시"),
]
new("std", sec=S0, title=T_STABLE,
    lead="공고 2항 ③ 참여업체 선정 - 브랜드 · 사양은 박람회 전에 공개하고, 무상보증기간은 계약서에 품목별로 적습니다.",
    body=table(["품목군", "브랜드 · 품질 확보 기준", "무상보증 기준"], "".join(
        f'<tr><td class="k">{t(a)}</td><td>{t(b)}</td><td>{t(c)}</td></tr>' for a, b, c in STABLE), "lgx stb")
         + '<div class="hflow"><span>브랜드 · 모델코드 제출</span><i>›</i><span>4단계 공개 심사</span><i>›</i>'
           '<span>특약이행각서(보증기간)</span><i>›</i><span>계약서에 기간 명시</span><i>›</i><span>입주 후 이행 관리</span></div>',
    kp=("무상 A/S는 [[최소 2년]](업체 · 품목별 상이) - 기간은 계약서에 적어 드립니다.", "제조사 보증이 더 길면 그 기간 · 업체가 입찰 때 낸 기간이 기준"))
B.CSS += ".tbl.stb td{padding:12px 14px;font-size:15.5px}.tbl.stb td.k{width:21%}.tbl.stb td:last-child{width:32%;color:var(--gold)}"

new("std", sec=S0, title=T_FACT,
    lead="주관사 직원이 직접 운영하고(일괄 도급 · 양도 없음), 가격과 진행 상황은 온라인 · 오프라인 모두 같은 내용으로 공개합니다.",
    body=('<div class="nb"><div class="pmx">'
          '<div class="pc"><h3><i>DIRECT</i>직영 운영</h3>'
          + B.rows([
              ("직접 운영", "박람회 기획 · 대관 · 업체 심사 · 콜센터 · 현장 운영을 [[주관사 직원이 직접]] 맡습니다."),
              ("도급 · 양도 없음", "주관 업무의 전부 또는 일부를 타사에 일괄 도급 · 양도하지 않습니다(전문 자문은 협력 계약)."),
              ("직영 품목", "조명 · 커튼 · 실링팬도 다른 업체와 [[같은 심사 · 같은 단가 공개]] - 협의회가 원하면 박람회에서 뺍니다."),
          ], title_w=110) + '</div>'
          '<div class="pc"><h3><i>OPEN</i>온 · 오프라인 투명 운영</h3>'
          + B.rows([
              ("같은 가격", "카페 사전 공개 단가 = 박람회장 단가 = 온라인 박람회 단가 - [[현장 가격 변경 없음]]"),
              ("선정 공개", "업체 공개 입찰 · 4단계 심사 · 입예협 최종 컨펌"),
              ("현황 보고", "계약 · 환불 · A/S · 하자 처리 현황을 정례회의마다 보고"),
              ("원자료 열람", "가격 조사 화면 · 견적서 · 접수 기록을 입예협이 요청하면 열람"),
          ], title_w=110) + '</div></div></div>'),
    kp=("말이 아니라 [[공개된 숫자와 기록]]으로 확인받겠습니다.", "결제 방식(카드 · 현금)과 관계없이 같은 단가"))

# ------------------------------------------------------------ ③ 가격 검증
CHECK5 = [("STEP 01", "단가 제출", "모델코드 · 규격 · 설치 · 철거 · 배송 · A/S 포함 여부"),
          ("STEP 02", "시중가 조사", f"{ST['local']} 오프라인 매장 2곳 이상 견적서"),
          ("STEP 03", "온라인 최저가", "같은 모델 최저 총액 · 조사일 · 화면 캡처 보관"),
          ("STEP 04", "입예협 검수", "비교표 제출 · 입예협이 품목을 골라 직접 확인"),
          ("STEP 05", "공개 · 보상", "박람회 전 카페 공개 · 계약 후 최저가 차액 10배")]
new("std", sec=S0, title=T_CHECK,
    lead="공고 2항 ③ 품목별 가격 검증 - 박람회 전에는 가격을 검수해 공개하고, 계약 뒤에는 더 싼 판매가 확인되면 보상합니다.",
    body=('<div class="nb"><div class="flowx">' + "".join(
        (('<div class="ar">›</div>' if i else "") + f'<div class="st{" hl" if i == 4 else ""}"><i>{a}</i><b>{b}</b><p>{t(c)}</p></div>')
        for i, (a, b, c) in enumerate(CHECK5)) + '</div>'
          + B.rows([
              ("같은 조건 총액으로", "제품가만이 아니라 설치 · 철거 · 배송 · 부가세 · A/S 기간을 맞춘 [[총액]]으로 비교합니다."),
              ("높으면 사유 또는 조정", "박람회 단가가 더 높으면 사유(설치 포함 · A/S 연장 등)를 표기하거나 조정을 요청하고, [[입예협이 승인하지 않으면 재입찰]]합니다."),
              ("계약 후 차액 보상", f"계약 후 7일 안에 같은 브랜드 · 모델의 새 제품이 인근({ST['local']}) 오프라인 매장에서 더 싸게 팔린 사실이 구매 영수증으로 확인되고 주관사가 매장에 확인하면 [[차액의 10배]]를 보상하고 판매가를 조정합니다(1건당 최대 50만원 · 최대 금액은 입예협과 협의 · 세대 · 품목당 1회)."),
              ("보상 대상 밖", "견적서 · 가격표만 있는 경우, 온라인 · 홈쇼핑 판매, 시공 품목, 카드 청구할인 · 사은품 · 전시 · 리퍼 · 한정 수량 행사가는 비교 대상에서 제외합니다(규정 제8조)."),
          ], title_w=200) + '</div>'),
    kp=("검수는 [[박람회 전]], 보상은 [[계약 후]] - 두 번 확인합니다.", "보상은 참여업체가 지급 · 주관사가 접수 후 7일 안에 이행 관리 · 규정 제8조"))

ITEMS = [  # (묶음, 대상, [품목], 기준)
    ("공간 맞춤", "84㎡ 표준 · 중대형 맞춤", ["커튼 · 블라인드 (타입별 실측 제작)", "수납 · 선반 · 가구 (99 ~ 135㎡ 배치안)", "실링팬 (천장 보강 확인 후)"], "84㎡ 표준 견적표 + 중대형 면적별 견적"),
    ("입주 준비", "모든 세대", ["입주청소 · 줄눈 · 새집증후군", "방충망(미세 · 안전) · 단열필름", "포장이사 · 사전점검 대행"], f"{ST['local']} 업체 우선 · 48시간 A/S"),
    ("생활 가전 · 렌탈", "필요 세대", ["가전 (빌트인 · 옵션 품목 제외)", "정수기 · 공기청정 렌탈", "생활 · 주방 소형 가전"], "유상옵션 · 기본 제공 품목과 겹치지 않는 것만"),
    ("조건부 시공", "유상옵션 · 기본 제공 확인 후", ["시스템에어컨 · 인덕션 · 간접조명", "현관 중문 · 붙박이장 · 드레스룸", "탄성코트 · 욕실 환기 · 비데 교체"], "옵션 미선택 세대 · 남은 수요만 · 외부 시공 승인 확인"),
]


def _item_card(nm, who, its, rule):
    li = "".join(f"<li>{t(x)}</li>" for x in its)
    return f'<div class="itc"><i>{t(who)}</i><h3>{t(nm)}</h3><ul>{li}</ul><p>{t(rule)}</p></div>'


new("std", sec=S0, title=T_ITEMS,
    lead="공고 2항 ③ 박람회 기획 - 입주 준비에 필요한 품목을 네 묶음으로 나누고, 유상옵션과 겹치는 품목은 조건부로 둡니다.",
    body=('<div class="nb"><div class="itx">' + "".join(_item_card(*x) for x in ITEMS) + '</div>'
          '<div class="itr"><b>773세대 규모 기준</b><span>품목 수 · 품목당 업체 수는 수요조사 결과와 입예협 승인으로 정합니다. '
          '수요가 많은 품목은 복수 업체 경쟁으로, 적은 품목은 온라인 박람회 · 카카오 상담으로 돌려 업체 부담과 단가를 함께 낮춥니다.</span></div>'
          '<div class="itr g"><b>안심 기준</b><span>설치 품목은 KC 등 법정 인증 서류 확인 · 마감재는 친환경 인증 서류를 낸 업체 우선 · '
          '새집증후군 · 라돈 측정은 B 패키지 항목으로 선택</span></div></div>'),
    kp=("품목 수와 업체 수는 [[수요조사 결과]]로 정합니다.", "품목 · 가격은 입예협과 사전 협의 후 확정"))


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
    kp=("주관사 직영 품목도 [[같은 심사 · 같은 단가 공개 · 같은 가격 보호 규정]] 적용 - 협의회가 원하면 직영 품목은 뺍니다.", "업체 수는 입예협 승인 · ‘참가 협의 중’은 확정 전 업체 · 일괄 도급 없음"))

VMGT = [  # (단계, 관리 방법, 기준)
    ("선정", "수요조사 → 공개 입찰공고 → 4단계 심사 → [[입예협 최종 컨펌]]", "품목별 업체 수는 입예협 승인 · 하청 금지"),
    ("계약", "표준 계약서에 취소·환불 규정 첨부 · 모델코드 · 포함 조건(설치·철거·배송·A/S) 명시", f"계약금 {D.DEPOSIT_MAX}% 이하 · 카드·현금 동일가"),
    ("일정", "세대별 상담 · 계약 · 납품 · 시공 · 설치 [[일정 관리표]] · 동별 일정 충돌 조정", "시공 가능 시점 · 관리사무소 신고 확인"),
    ("검수", "시공 · 설치 후 세대 확인 서명 → 잔금 · 해피콜", "하자 · 미시공은 보수 후 잔금"),
    ("평가", "박람회 후 업체별 민원 · A/S 처리 현황 집계 → 입예협 보고", "패널티 3단계 · 재참여 제한"),
    ("공정", "모든 참여업체에 균등한 기회 · 가격 담합 · 독점 유도 · 비방 금지", "담합 적발 시 즉시 배제"),
]
new("std", sec=S0, title=T_VMGT,
    lead="공고 2항 ③ 참여업체 선정 - 품목 구성 · 업체 모집 · 계약관리부터 납품 · 시공 · 설치 일정까지 주관사가 같은 표로 관리합니다.",
    body=table(["단계", "관리 방법", "기준"], "".join(
        f'<tr><td class="k">{a}</td><td>{t(b)}</td><td>{t(c)}</td></tr>' for a, b, c in VMGT), "lgx vm"),
    kp=("업체는 [[같은 기준]]으로 뽑고, [[같은 표]]로 관리합니다.", "4단계 심사 · 특약이행각서 · 패널티는 03 · 04장"))

# ------------------------------------------------------------ ⑤ 협의회 요청 · 시공사 협의
REQ = [  # 예상 요청 유형 — 실제 항목은 입예협과 정한다
    ("시공 · 품질", "공정 · 마감 · 설비 질의, 하자 취약 부위", "① 기술 검토 회신 · 시공사 질의서 초안 · 사진 · 위치 표시", "회신 확보"),
    ("옵션 · 계약", "유상옵션 · 입주 조건 · 계약 안내", "시공사 안내 정리 · 카페 안내 콘텐츠(입예협 승인)", "공지 게시"),
    ("입주 일정", "사전점검 · 입주지정기간 · 입주지원센터", "공문 작성 · 발송 지원 · 회신 일정 추적", "일정 공유"),
    ("생활 인프라", "통학 · 교통 · 주변 개발 일정", "시청 등 공식 자료 · 회신 이력 정리 · 질의 공문 작성 지원(확정되지 않은 일정은 약속하지 않음)", "기관 회신 공유"),
]
new("std", sec=S0, title=T_REQ,
    lead="공고 2항 ⑤ · ① - 협의회 요청을 접수 → 기술 검토 → 시공사 · 기관 협의 → 반영 · 보류 사유 → 공유까지 기록합니다.",
    body=table(["분야", "요청 예 (유형)", "주관사 지원", "완료 기준"], "".join(
        f'<tr><td class="k">{a}</td><td>{t(b)}</td><td>{t(c)}</td><td>{t(d)}</td></tr>' for a, b, c, d in REQ), "sm rq4")
         + '<div class="hflow" style="margin-top:20px"><span>요청 접수</span><i>›</i><span>기술 검토 · 담당 지정</span><i>›</i>'
           '<span>시공사 · 기관 협의 동석</span><i>›</i><span>반영 / 보류 사유</span><i>›</i><span>입예협 공유 · 기록</span></div>'
         + '<div class="gq3"><div><b>협의 자료</b><span>공문 초안 · 질의서 · 현장 사진 · 도면 표시 - 협의회 이름으로 발송</span></div>'
           '<div><b>협의 동석</b><span>본부장 · 분야 전문가가 협의회 요청 시 동석</span></div>'
           '<div><b>공유 주기</b><span>정례회의마다 · 시공사 회신이 오면 바로 갱신</span></div></div>',
    kp=("협상의 주체는 [[협의회]] - 주관사는 자료와 기록으로 돕습니다.", "‘협의 완료’와 ‘설치 완료’를 구분해 보고 · 공식 근거와 회신 이력으로만 안내 · 요청 유형은 예시"))
B.CSS += (".gq3{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px}"
          ".gq3>div{border:1px solid var(--line);border-radius:11px;padding:12px 16px;display:flex;flex-direction:column;gap:4px}"
          ".gq3 b{font-size:15px;color:var(--gold)}.gq3 span{font-size:14px;color:var(--sub);line-height:1.45}"
          ".tbl.sm.rq4 td{padding-top:10px;padding-bottom:10px}")

# ------------------------------------------------------------ ④ A/S 정책
new("std", sec=S0, title=T_AS,
    lead="공고 2항 ④ 사후관리 - 입주민은 주관사 한 창구로 접수하고(24시간 안에 1차 회신), 참여업체에는 추가 비용 · 추가 인력을 요구하지 않는 구조로 운영합니다.",
    body=('<div class="nb"><div class="pmx">'
          '<div class="pc"><h3><i>POLICY</i>A/S 정책</h3>'
          + B.rows([
              ("접수", f"콜센터 {D.TEL}(평일) · 카페 신문고 · 카카오채널(365일)"),
              ("기한", "[[24시간 1차 회신]] · 48시간 하자보수 원칙"),
              ("기간", "무상 A/S 최소 2년(계약서 명시) · 주관 창구는 공동구매 A/S 종결까지(협약 기간)"),
              ("미응답", "주관사가 먼저 보상 · 업체와 나중에 정산"),
              ("기록", "접수 · 처리 · 지연 사유 기록 · 정례 보고"),
          ], title_w=86) + '</div>'
          '<div class="pc"><h3><i>NO EXTRA BURDEN</i>업체 부담을 늘리지 않는 제도</h3>'
          + B.rows([
              ("창구 비용", "콜센터 운영비는 [[주관사 부담]] - 업체별 상담 인력 요구 없음"),
              ("예치금", "하자 예치금은 주관사 자산 - [[업체 예치금 · 추가 보증금 없음]]"),
              ("보증 기간", "업체 제시 기간 · 제조사 기준 그대로 - 일괄 연장 강요 없음"),
              ("책임 구분", "시공사 하자를 공동구매 업체에 떠넘기지 않음"),
              ("패널티", "홍보정지 → 10% 배상 → 자격박탈 - 단계형"),
          ], title_w=96) + '</div></div></div>'),
    kp=("업체 부담이 늘면 [[단가가 오릅니다]] - 그래서 A/S 비용은 주관사 구조로 해결합니다.", "업체 참가비는 정액 · 공구가와 연동하지 않음"))

FLOWX = ('<div class="hflow"><span>한 창구 접수</span><i>›</i><span>유형 분류</span><i>›</i><span>책임 주체 연결</span><i>›</i>'
         '<span>처리 · 회신 추적</span><i>›</i><span>완료 확인 · 정기 보고</span></div>')
B.CSS += (".tbl.lgx td{padding:17px 14px;font-size:16.5px;line-height:1.5}.tbl.lgx td.k{font-size:18px}"
          ".hflow{display:flex;align-items:center;gap:10px;margin-top:18px}.hflow span{flex:1;text-align:center;border:1px solid rgba(200,168,106,.5);"
          "border-radius:10px;padding:12px 8px;font-size:15.5px;font-weight:700;background:rgba(235,203,143,.06)}"
          ".hflow span:last-child{background:var(--gold);color:#0d1e33;border-color:var(--gold)}.hflow i{font-style:normal;color:var(--gold);font-weight:800;font-size:20px}"
          ".tbl.q10 td{padding:6.5px 12px;font-size:14px;line-height:1.38}.tbl.q10 td.k{font-size:14.5px;width:31%}.tbl.q10 td:last-child{width:15%;white-space:nowrap}"
          ".tbl.q10 td.n{width:38px}.tbl.q10 tr.chk td{background:rgba(255,224,102,.06)}")

new("std", sec=S0, title=T_DEFECT,
    lead="공고 2항 ④ 민원 · 분쟁 대응 - 접수는 한 곳에서 받고, 처리 책임은 유형별로 나눠 끝까지 추적합니다.",
    body=table(["접수 유형", "예", "처리 책임", "주관사 역할"], "".join(
        f'<tr><td class="k">{a}</td><td>{t(b)}</td><td>{t(c)}</td><td>{t(d)}</td></tr>' for a, b, c, d in [
            ("건설사 시공 · 공용부", "세대 마감 · 설비 하자, 공용부 시설", f"시공사({ST['builder']}) 하자 처리 창구", "접수 대행 · 회신 추적 · 현장 확인 지원 · 정기 보고"),
            ("공동구매 납품 · 시공", "박람회에서 계약한 품목의 설치 · 제품 하자", "참여업체 + 주관사 책임(특약이행각서)", "48시간 하자보수 원칙 · 업체 미응답 시 개입 · 선보상"),
            ("업체 부도 · 미시공", "참여업체 폐업 · 연락 두절 · 시공 중단", "주관사 책임 처리", "동종업체 이관 · A/S 비용 주관사 부담 · 하자 예치금"),
            ("분쟁 · 환불", "계약 취소 · 환불 지연 · 가격 분쟁", "참여업체 + 주관사(환불 규정)", "규정 제5 ~ 8조 적용 · 3영업일 환불 · 미이행 시 선보상"),
        ]), "lgx df4") + FLOWX,
    kp=("시공 하자를 [[공동구매 업체에 떠넘기지 않고]], 공동구매 하자를 [[시공사 탓으로 돌리지 않습니다.]]", "접수는 주관 콜센터 · 카카오채널 · 카페 신문고 한 창구"))
B.CSS += ".tbl.df4 td{padding:13px 14px}"

# ------------------------------------------------------------ ⑤ 협의회 지원 — 행사별 지원 범위(안)
SUPPORT = [  # (행사 · 업무, 주관사 지원, 인력 · 비품(안), 비용)
    ("입주예정자 총회", "장소 섭외 지원 · 접수 · 위임 확인 · 진행 보조 · 자료 인쇄", "인력 4명 · 접수대 · 음향 · 현수막", "주관사 부담"),
    ("시공 단계 설명회", "공정 자문 결과 · 취약 부위 · 시공사 회신을 입주예정자에게 설명(협의회 요청 시)", "본부장 · 분야 전문가 · 자료", "주관사 부담"),
    ("점등식 · 입주설명회", "프로그램 · 진행 · 음향 · 안전 관리 · 조명 연출 검토(전기공사업 등록)", "인력 4명 · 안전요원 · 음향", "주관사 부담"),
    ("협의회 홍보", "카페 공지 · 카드뉴스 · 안내문 제작(게시 전 협의회 승인) · 행사 현수막", "이벤트팀 3명", "주관사 부담"),
    ("협의회 활동 지원", "정례회의 자료 · 공문 초안 · 정기 보고서 · 관련 자료 제공", "본부장 · 대외지원팀", "주관사 부담"),
    ("그 밖에 협의한 업무", "서면 요청 → 3영업일 안에 실행안 · 인력 · 비용 산정 → 협의회 협의 후 진행", "요청 내용별", "협의"),
]
new("std", sec=S0, title=T_SUPPORT,
    lead="공고 2항 ⑤ - 협의회 행사 · 홍보마다 무엇을 · 몇 명이 · 누구 비용으로 지원하는지 미리 정했습니다. 횟수 · 일정은 협의회 요청에 맞춥니다.",
    body=table(["행사 · 업무", "주관사 지원", "인력 · 비품 (안)", "비용"], "".join(
        f'<tr><td class="k">{t(a)}</td><td>{t(b)}</td><td>{t(c)}</td><td class="c">{t(d)}</td></tr>' for a, b, c, d in SUPPORT), "lgx sp6")
         + '<div class="hflow"><span>협의회 요청</span><i>›</i><span>담당 · 인력 지정</span><i>›</i><span>준비물 · 일정 확인</span><i>›</i>'
           '<span>당일 지원</span><i>›</i><span>결과 공유 · 기록</span></div>',
    kp=("협의회 지원은 [[행사별 범위]]를 정해 두고, 그 밖의 요청은 [[서면으로 협의]]합니다.", "인력 · 비품은 행사 규모 · 장소에 따라 협의회와 확정 · 시공사 · 관리주체 승인이 필요한 행사는 승인 범위 안에서"))
B.CSS += (".tbl.sp6 td{padding:12px 14px;font-size:15.5px;line-height:1.42}.tbl.sp6 td.k{width:19%;font-size:16.5px}"
          ".tbl.sp6 td:nth-child(3){width:22%}.tbl.sp6 td.c{width:11%;white-space:nowrap;color:var(--gold);font-weight:700}")

# ------------------------------------------------------------ 특화 제안 · 경관
new("std", sec=S0, title=T_SPECIAL,
    lead=f"박람회 운영 경험과 주관사 직영 역량(전기공사업 · 조명 · 커튼)을 {ST['name']} 규모와 조건에 맞게 다시 짰습니다.",
    body=B.tiles([
        dict(lb="01", nm="시공 단계 자문 캘린더", ds="7개 공정을 덮기 전에 분야 전문가가 확인하고, 보고서 · 사진대장 · 취약 부위 목록을 남깁니다."),
        dict(lb="02", nm="84㎡ 표준 + 중대형 견적", ds="84㎡는 표준 견적표, 99 ~ 135㎡는 면적별 배치 · 견적을 박람회 전에 공개합니다."),
        dict(lb="03", nm="가격 비교 한 장", ds="시중가 · 온라인 최저가를 같은 조건 총액으로 비교해 박람회 전에 공개합니다."),
        dict(lb="04", nm="멀리 사는 계약자도 같은 가격", ds="사전 예약 상담 · 온라인 박람회 · 카카오 상담 - 박람회와 같은 공동구매가."),
        dict(lb="05", nm="경북 · 대구권 시공 업체", ds="상주 · 문경 · 구미 · 대구권 업체 우선 - 48시간 A/S가 되는 거리입니다."),
        dict(lb="06", nm="경관조명 진단 · 개선안", ds="동 파사드 → 문주 → 정원 · 물놀이터 순서로 진단해 개선안을 냅니다(전기공사업 등록 업체)."),
    ], cols=3, rows_n=2).replace('class="tiles"', 'class="tiles lg"'),
    kp=("제안 품목 · 혜택은 수요조사 결과에 따라 [[입예협과 최종 확정]]합니다.", "경관조명은 진단 · 개선안까지 - 설치 여부 · 비용은 입예협 · 관리주체 결정"))


def _fig(key, cap, sub_, pos="50% 50%"):
    im, _own = slot(key)
    if not im:
        return ""
    return (f'<figure><img src="assets_ins/{im}.jpg" alt="" style="object-position:{pos}">'
            f'<figcaption>{cap}<small>{sub_}</small></figcaption></figure>')


new("std", sec=S0, title=T_LX,
    lead="전기공사업 등록 업체로서 단지의 밤 얼굴부터 - 동 파사드 → 단지 전체 → 문주 · 진입부 순서로 진단하고 개선안을 냅니다. 공용부 변경은 승인 절차를 먼저 확인합니다.",
    body=('<div class="nb"><div class="lxo"><div class="gal lxa">'
          + _fig("lx_front1", "① 동 파사드 · 정면 야경", "외벽 라인조명 · 최상층 · 도로변 경관", "40% 45%")
          + _fig("lx_front2", "② 단지 조감 야간", "동 간 통일된 색온도 · 산책로 동선", "50% 50%")
          + _fig("lx_gate", "③ 문주 · 진입부", "문주 간접조명 · 보행 동선 밝기", "50% 55%")
          + '</div><div class="lxd">'
          + "".join(f"<div><b>{a}</b><p>{t(b)}</p></div>" for a, b in [
              ("우선 1 · 동 파사드", "외벽 라인조명 · 최상층 스카이 커뮤니티 실루엣 - 기존 경관조명 도면 · 배선 · 조도 · 타이머부터 확인합니다."),
              ("우선 2 · 문주 · 진입부", "문주 사인 간접조명과 진입부 보행 동선의 밝기 · 눈부심을 함께 보고, 기존 조경과 어울리는 선택안을 냅니다."),
              ("산출물", "① 현황 진단 1장 ② 기본 · 개선 · 선택안 비교(물량 · 공사비 · 유지관리비) ③ 협의 기록 ④ 완료 검수 기준"),
              ("결정은 입예협 · 관리주체", "설치 여부 · 범위 · 비용은 도면 검토 뒤 입예협 · 관리주체가 정합니다."),
          ])
          + '</div></div></div>'),
    kp=("단지 가치는 [[밤의 첫인상]]에서 - 외부 경관부터 진단합니다.", D.LX_CAP + " · 전기공사업 등록 제 울산-00821호"))
new("std", sec=S0, title=T_LX2,
    lead="외부 경관 다음은 매일 걷는 곳 - 물놀이터 · 중앙 정원 · 산책로의 야간 밝기와 안전을 살핍니다.",
    body=('<div class="nb"><div class="lxo s2"><div class="gal lxb">'
          + _fig("lx_play", "물놀이터", "볼라드 · 수경 · 바닥 밝기", "50% 50%")
          + _fig("lx_garden", "중앙 정원 · 수경", "수목 업라이트 · 산책로 보행등", "50% 50%")
          + '</div><div class="lxd">'
          + "".join(f"<div><b>{a}</b><p>{t(b)}</p></div>" for a, b in [
              ("보행등 · 볼라드", "산책로 · 계단 · 단차 바닥 밝기를 확보해 야간 보행이 안전합니다."),
              ("수목 업라이트", "주요 수목을 아래에서 비춰 조경 공간을 밤에도 머무는 곳으로 만듭니다."),
              ("빛공해 차단", "세대 창 방향 눈부심 · 빛샘을 배광 각도로 막습니다."),
              ("타이머 · 심야 감광", "시간대별 밝기를 나눠 관리비를 줄입니다."),
              ("승인 후 진행", "기존 도면 대조 뒤 입예협 · 관리주체 승인 범위 안에서만 진행합니다."),
          ])
          + '</div></div></div>'),
    kp=("같은 조명도 [[어디를 · 언제 · 얼마나]] 밝히느냐가 단지의 밤을 바꿉니다.", D.LX_PLAY_CAP + " · 시설 추가는 관리비 · 유지관리 주체 확인 후 판단"))
B.CSS += (".lxo{display:grid;grid-template-columns:1.75fr 1fr;gap:18px;flex:1;min-height:0}"
          ".gal.lxa{grid-template-columns:1.25fr 1fr;grid-template-rows:1fr 1fr;gap:10px;min-height:0}"
          ".gal.lxa figure:first-child{grid-row:span 2}"
          ".gal.lxb{grid-template-columns:1fr 1fr;gap:12px;min-height:0}"
          ".lxo .gal figcaption{font-size:15px;padding:24px 12px 9px}.lxo .gal figcaption small{font-size:12px}"
          ".lxo .lxd{display:flex;flex-direction:column;justify-content:center;gap:12px;min-height:0}"
          ".lxo .lxd>div{border-left:2px solid var(--gold2);padding:2px 0 2px 14px}"
          ".lxo .lxd b{font-size:16.5px}.lxo .lxd p{font-size:14px;color:var(--sub);line-height:1.45;margin-top:3px}"
          ".lxo.s2{grid-template-columns:2.1fr 1fr}")

# ------------------------------------------------------------ 단계별 업무 일정(협약 ~ A/S 종결)
MON = [  # (시기, 주관사 업무, 협의회 보고 · 산출물)
    ("2026.10 ~ 11", "제안서 제출(10.28) · 서류 심사(11.03) · [[PT 11.15]] · 운영위원회 의결 · 협약 체결", "제안 조건 = 협약 조건"),
    ("협약 직후", "전담 PM 지정 · 연락 체계표 · 분야별 전문가 배치 확정 · [[현재 공정 확인 · 1차 자문]] · 요청 관리표 개설", "연락 체계표 · 1차 자문 보고서"),
    ("2027", "지하 골조 · 방수 · 지상 골조 공정 자문(덮기 전) · 협의회 요청 기술 검토 · 정례 보고", "공정별 자문 보고서 · 사진대장"),
    ("2028 상반기", "창호 · 외벽 · 최상층 방수 · 설비 · 전기 · 소방 배관 · 배선 은폐 전 자문 · 품목 수요조사 설계", "취약 부위 목록 · 설문안"),
    ("2028 하반기", "[[수요조사]] · 마감재 대조 · 품목 · 업체 수 확정 · 협력업체 [[공개 입찰]] · 4단계 심사", "수요조사 결과 · 마감재 대조표 · 심사 결과"),
    ("2028.11 ~ 12", "단가 제출 · 시중가 · 온라인 최저가 조사 · [[입예협 가격 검수]] · 행사장 대관 · 조경 · 외부 자문", "가격 비교표 · 안전계획"),
    ("2029.01", "단가표 카페 공개(입예협 승인) · 홍보 · 배치도 확정 · 행사배상책임보험 가입 · 사전점검 체크리스트", "공개 단가표 · 배치도 · 보험 증권"),
    ("2029.01 ~ 02", "[[입주박람회 2 ~ 3일(안)]] · 사전 예약 상담 · 온라인 박람회 · 계약 세대 실측 · 일정 관리표", "박람회 결과보고서"),
    ("2029.02 ~ 03", "사전점검 지원 · 하자 접수 보조 · 재점검 동행 · 점등식 · 입주설명회 지원(일정 확정 시)", "하자 접수 집계 · 행사 지원 결과"),
    ("2029.04", "[[입주]] · 시공 · 설치 · 세대 검수 서명 · 잔금 · 해피콜 · 하자 접수 창구", "입주 지원 결과"),
    ("~ A/S 종결", "공동구매 품목 A/S · 하자보수 이행 관리 · 민원 · 분쟁 대응 · 정기 보고 → 협약 종료 시 최종 결과 보고서", "최종 결과 보고서"),
]


def _mon(rows):
    return table(["시기", "주관사 업무", "협의회 보고 · 산출물"], "".join(
        f'<tr><td class="k">{a}</td><td>{t(b)}</td><td>{t(c)}</td></tr>' for a, b, c in rows), "mon")


new("std", sec=S0, title=T_MON1,
    lead="공고 7항 - 시공 단계 지원은 협약 직후부터. 공정 자문과 박람회 준비를 같은 일정표로 관리하고, 세부 시점은 정례회의에서 협의회와 확정합니다.",
    body=_mon(MON[:6]),
    kp=(f"입주까지 약 [[{ST['months']}개월]] - 시공 단계부터 입주 준비까지 한 일정표입니다.", "공정 일정이 바뀌면 협의회와 협의해 자문 시점 · 박람회 일정을 함께 조정합니다"))
new("std", sec=S0, title=T_MON2,
    lead="박람회 · 사전점검 · 입주와 협약 종료(공동구매 품목 A/S 종결)까지 - 공고 1 협약 기간.",
    body=_mon(MON[6:]),
    kp=("매 단계 [[무엇을 하고 무엇을 보고하는지]] 미리 정해 둡니다.", "박람회는 입주일 확정 후 입주 2 ~ 3개월 전 주말 포함 2 ~ 3일(안) · 일수 · 장소는 협의회와 확정 · 입주 지연 시 함께 조정"))
B.CSS += (".tbl.mon td{padding:17px 14px;font-size:15.5px;line-height:1.45}.tbl.mon td.k{width:14%;white-space:nowrap;font-variant-numeric:tabular-nums}"
          ".tbl.mon td:last-child{width:26%;color:var(--gold)}.tbl.mon tr:nth-child(odd) td{background:rgba(255,255,255,.025)}")

# ------------------------------------------------------------ 전담 · 운영
new("std", sec=S0, title=T_PM,
    lead="본사가 멀어도 협의회 · 입주민은 한 창구로 연락하고, 전담 PM과 분야 전문가 · 현장 인근 업체가 기한 안에 처리합니다.",
    body=('<div class="nb"><div class="pmx">'
          '<div class="pc"><h3><i>CONTACT</i>전담 연락 체계</h3>'
          + B.rows([
              ("총괄 책임", "주관사업 총괄 본부장 · [[" + D.MANAGER[2].replace("-", "⁠-⁠") + "]]"),
              ("전담 PM", "단지 전담 1명 지정 · 전담 PM 성명 · 연락처는 협약 시 제출"),
              ("한 창구 접수", f"주관 콜센터 {D.TEL}(평일 09:00 ~ 18:00) · 온라인 365일(카페 신문고 · 카카오채널 · 홈페이지)"),
              ("회신 · 처리", "[[24시간 안에 1차 회신]] · 기술 검토 10영업일 서면 회신 · 해피콜로 종결"),
          ], title_w=128) + '</div>'
          '<div class="pc"><h3><i>ON SITE</i>거리를 메우는 현장 체계</h3>'
          + B.rows([
              ("정례 · 자문일", "협의회 정례회의 · 공정 자문일 · PT · 박람회 · 사전점검에 본부장 · 분야 전문가가 현장 참석"),
              ("현장 자문", "공정 일정에 맞춰 분야 전문가가 방문 - 현장 출입은 시공사 승인 범위"),
              ("시공 · A/S", f"{ST['local']} 시공업체 우선 선정 - [[48시간 A/S가 가능한 거리]]"),
              ("선정 후 30일", "[[현장 사무소 개설]] · 전담 PM 배치(위치 · 운영 시간은 협약 시 협의회와 확정) · 입주 집중기엔 단지 안 임시 상주 창구"),
          ], title_w=128) + '</div></div></div>'),
    kp=("협의회 · 입주민은 [[한 창구]]로 연락하시면 됩니다.", "콜센터 평일 09:00 ~ 18:00 · 온라인 365일 접수 · 24시간 이내 회신"))
B.CSS += (".pmx{display:grid;grid-template-columns:1fr 1fr;gap:20px;flex:1;min-height:0}"
          ".pmx .pc{border:1px solid var(--line);border-radius:14px;padding:14px 18px;display:flex;flex-direction:column;min-height:0;"
          "background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.01))}"
          ".pmx .pc:first-child{border-color:rgba(235,203,143,.6);background:linear-gradient(180deg,rgba(235,203,143,.12),rgba(235,203,143,.02))}"
          ".pmx h3{font-size:18px;font-weight:800;margin-bottom:8px;display:flex;align-items:baseline;gap:10px}"
          ".pmx h3 i{font-style:normal;font-size:11px;letter-spacing:.2em;color:var(--gold2);font-weight:700}"
          ".pmx .rows{flex:1}")

_stf = {n: (c, r) for n, c, r in D.STAFF}
_n12 = sum(c for _, c, _ in D.STAFF)


def _dcard(no, req, head, items):
    li = "".join(f"<li>{t(x)}</li>" for x in items)
    return f'<div class="dcd"><i>{no}</i><h4>{req}</h4><b>{head}</b><ul>{li}</ul></div>'


new("std", sec=S0, title=T_STAFF,
    lead=f"공고 3항 · 별지2호 - 관리감독(대표이사 · 총괄 본부장) 외에 협의회 요청과 입주민 민원을 직접 처리할 4개 팀 {_n12}명을 {ST['short']} 전담으로 배치합니다(안).",
    body='<div class="nb"><div class="dcx">'
         + _dcard("EXPO · VENDOR", "박람회 · 업체 · 가격 · 일정", f"행사관리 {_stf['행사관리팀'][0]} · 영업 {_stf['영업팀'][0]}명", [
             "박람회 · 대관 · 배치 · 안전 · 편의공간",
             "업체 섭외 · 심사 지원 · 계약 · 설치 일정 관리",
             "시중가 · 온라인 최저가 비교표 작성",
             "협의회 요청은 담당을 지정해 [[24시간 안에 1차 회신]]"])
         + _dcard("COUNCIL · PR", "협의회 행사 · 홍보 · 행정", f"이벤트 {_stf['이벤트팀'][0]} · 대외지원 {_stf['대외지원팀'][0]}명", [
             "카페 · 공지 채널 콘텐츠 · 카드뉴스 · 영상",
             "모든 게시물은 [[협의회 사전 승인 후]] 게시",
             "수요조사 · 사전점검 · 설명회 지원",
             "입주민 개인정보 · DB는 홍보에 쓰지 않음"])
         + _dcard("BUILD · A/S", "시공 단계 자문 · A/S · 하자 · 민원", "본부장 + 대외지원팀 + 분야 전문가", [
             "본부장이 공정 자문 일정 · 이슈 직접 관리 · 동석",
             "전기 · 조명은 전기공사업 등록 업체로 [[직접 검토]]",
             "조경은 사내 조경 전문 인력이 [[직접 자문]]",
             "건축 · 토목 · 기계설비 · 소방은 협력 전문가"])
         + '</div><div class="hflow"><span>협의회 요청</span><i>›</i><span>담당 팀 지정</span><i>›</i><span>기술 · 행정 검토</span><i>›</i>'
           '<span>시공사 · 기관 협의</span><i>›</i><span>회신 · 기록 · 보고</span></div></div>',
    kp=("부서 이름이 아니라 [[누가 무엇을 맡는지]]로 답합니다.", "임직원 14명(정규직 13 + 인턴 1) 중 4개 팀 12명 · 명단은 협약 시 제출 · 인력 교체는 협의회와 사전 협의(별지2호) · 외부 전문가는 자문 협력 계약(일괄 도급 아님)"))
B.CSS += (".dcx{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;flex:1;min-height:0}"
          ".dcd{border:1px solid var(--line);border-top:2px solid var(--gold2);border-radius:14px;padding:14px 18px;background:linear-gradient(180deg,rgba(235,203,143,.08),rgba(255,255,255,.01) 40%);display:flex;flex-direction:column;gap:4px}"
          ".dcd i{font-style:normal;font-size:12px;font-weight:700;letter-spacing:.2em;color:var(--gold2)}"
          ".dcd h4{font-size:15px;color:var(--sub);font-weight:600}.dcd>b{font-size:21px;color:var(--gold);margin-bottom:4px}"
          ".dcd ul{list-style:none;margin:6px 0 0;padding:0;display:flex;flex-direction:column;gap:12px}"
          ".dcd li{font-size:15.5px;line-height:1.5;padding-left:14px;position:relative}.dcd li:before{content:'';position:absolute;left:0;top:8px;width:6px;height:6px;border-radius:50%;background:var(--gold2)}")

new("std", sec=S0, title=T_PRIV,
    lead="공고 7항 · 별지1호 - 입주예정자 개인정보와 협의회의 단지 정보 · 자료를 지킬 관리체계를 미리 정했습니다.",
    body=B.rows([
        ("수집 최소화", "상담 · 계약에 필요한 정보만, 목적 · 보관기간을 정해 [[별도 동의]]를 받습니다."),
        ("영업 이용 금지", "입주예정자 정보를 영업 · 마케팅 · 광고 · 고객유치에 쓰지 않고, [[DB를 만들거나 판매하지 않습니다.]]"),
        ("제3자 제공 금지", "협의회 사전 서면 승인 없이 참여업체 · 제3자에게 제공하지 않습니다. 필요하면 정보주체 동의를 따로 받습니다."),
        ("참여업체 관리", "참여업체의 개인정보 취급을 주관사가 관리 · 감독하고, 보호 의무를 계약 조건에 넣습니다."),
        ("홍보물 사전 승인", "협의회 명칭 · 로고 · 카페 · 공지 채널은 승인 범위에서만 쓰고, 모든 홍보물은 [[게시 전 승인]]받습니다."),
        ("단지 정보 비밀유지", "제안 · 자문 과정에서 받은 단지 정보 · 도면 · 자료는 [[이 업무 목적에만]] 씁니다."),
        ("파기 · 위반 시 조치", "보관기간이 지나면 파기하고, 위반이 확인되면 협약 해지와 손해배상을 받아들입니다."),
    ], title_w=210),
    kp="입주민 명단은 [[업체 영업 명단이 아닙니다.]]")

RPRIN = ('<div class="rprin">' + "".join(f'<div><b>{a}</b><p>{b}</p></div>' for a, b in [
    ("협의 ≠ 설치", "‘협의 완료’와 ‘설치 완료’를 나눠 표시"),
    ("지연은 사유와 함께", "지연 건은 사유 · 다음 일정을 같이 보고"),
    ("최소 정보", "협의회와 공유할 수 있는 범위로 집계"),
    ("원자료 열람", "협의회가 요청하면 근거 자료를 열람"),
]) + '</div>')
B.CSS += (".rprin{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:16px}.rprin div{border:1px solid rgba(200,168,106,.45);"
          "border-radius:12px;padding:12px 14px;background:rgba(235,203,143,.05)}.rprin b{display:block;font-size:16px;color:var(--gold)}"
          ".rprin p{font-size:13.5px;color:var(--sub);margin-top:4px;line-height:1.45}")

new("std", sec=S0, title=T_REPORT,
    lead="공고 2항 ⑤ · ① - 공정 자문 보고서와 박람회 결과보고서 · 정기 보고에 무엇을 담을지 미리 정했습니다.",
    body=table(["보고", "시점", "담는 내용"], "".join(
        f'<tr><td class="k">{a}</td><td>{t(b)}</td><td>{t(c)}</td></tr>' for a, b, c in [
            ("공정 자문 보고서", "공정별 자문 후 · 협의회 요청 시", "자문 일자 · 분야 · 확인 내용 · 사진 · 취약 부위 · 시공사 질의 · 회신 현황"),
            ("정례 진행 보고", "협의회 정례회의마다", "단계별 일정 진행 · 미결 요청 목록 · 다음 일정 · 시공사 회신 현황"),
            ("입주박람회 결과보고서", "박람회 종료 후", "[[공동구매 진행현황 · A/S 접수현황 · 하자처리 현황 · 민원처리 결과]]"),
            ("최종 결과 보고서", "협약 종료(공동구매 품목 A/S 종결) 시", "계약 · 환불 · A/S · 하자 처리 결과 · 선보상 사용 내역"),
        ]), "lgx") + RPRIN,
    kp=("보고서는 협의회와 공유할 수 있는 [[최소 정보]]로 집계합니다.", "개인 연락처 · 동호수는 싣지 않습니다"))

new("std", sec=S0, title=T_EXPO,
    lead="공고 2항 ③ 박람회 기획 · 운영 - 계약을 재촉하는 자리가 아니라, 가족이 함께 확인하고 비교하는 자리로 만듭니다.",
    body=B.tiles([
        dict(lb="WHEN", nm=f"{ST['expo']} 2 ~ 3일 (안)", ds="입주(2029.04) 2 ~ 3개월 전 주말 포함 · 일수 · 날짜는 입주일 · 사전점검 일정에 맞춰 협의회와 확정"),
        dict(lb="WHERE", nm="행사장 후보 3곳", ds="① " + ST["venues"][0] + " ② " + ST["venues"][1] + " ③ " + ST["venues"][2] + " - 협의회와 답사 후 확정"),
        dict(lb="SAFETY", nm="안전계획 · 행사배상책임보험", ds=f"동선 · 대피 · 전기 점검 · 미아 방지 · 응급 대응({PG('safe')}). 행사배상책임보험은 박람회 기간에 맞춰 가입."),
        dict(lb="FAMILY", nm="놀이방 · 휴게 · 수유실", ds="어린이 놀이방 · 수유실 · 유모차 대여와 입구 안내데스크 · 카페테리아를 둡니다."),
        dict(lb="ONLINE", nm="온라인 박람회 · 사전 예약", ds="단지 입주민만 들어오는 폐쇄몰 · 사전 예약 상담. 박람회와 같은 공동구매가."),
        dict(lb="PR", nm="카페 · 공지채널 콘텐츠", ds="카드뉴스 · 영상 · 현수막 · 알림톡 - 게시 전 협의회 사전 승인을 받습니다."),
    ], cols=3, rows_n=2).replace('class="tiles"', 'class="tiles lg"'),
    kp="박람회장 가격 = 사전 공개 단가 - [[결제 방식과 관계없이]] 같습니다.")

SAFE = [  # (구분, 기준)
    ("동선 · 대피", "입구 체크인 → 품목 존 → 상담 → 휴게의 [[한 방향 동선]] · 비상구 · 대피로 표시 · 통로 폭 확보"),
    ("전기 · 화기", "부스 전기는 개장 전 [[전기공사업 등록 업체가 점검]] · 문어발 배선 금지 · 화기 · 가스 사용 금지"),
    ("어린이 · 미아", "놀이방 전담 인력 · 보호자 확인 팔찌 · 미아 발생 시 안내데스크 방송 · 출입구 확인"),
    ("응급 · 질병", "응급 키트 · AED 위치 안내 · 사내 간호사 자격 인력 배치 · 인근 병원 연락 체계"),
    ("인원 · 주차", "현장 운영 약 21명(주차 3 · 체크인 · 안내 5 포함) · 혼잡 시간 입장 조절 · 주차 안내"),
    ("업체 반입 · 철수", "부스 반입 · 철수 시간표 · 부스별 책임자 명찰 · 매일 개장 전 [[안전 점검표]] 서명"),
    ("보험 · 시설 기준", "행사배상책임보험 박람회 기간 가입 · 증권 사본 협의회 제출 · 체육관 등 공공시설은 바닥 보호 · 난방 · 상업행사 사용 기준 확인"),
]
new("std", sec=S0, title=T_SAFE,
    lead="공고 2항 ③ 박람회 운영 - 행사장 안전과 현장관리 기준을 미리 정하고, 행사장이 확정되면 그 시설 기준에 맞춰 협의회와 최종 확정합니다.",
    body=B.rows([(a, b) for a, b in SAFE], title_w=170),
    kp=("안전은 [[개장 전 점검표]]로 매일 확인합니다.", "행사장 · 인원 · 보험 조건은 행사장 확정 후 협의회와 최종 확정 · 인원은 행사 규모에 따라 변동"))

# ------------------------------------------------------------ 참가 자격 4 · 이해관계 · 유의사항
QUAL4 = [  # (자격, 공고 3항, 엣지컴퍼니 현황, 증빙 = 5항 제출서류 번호)
    ("업종 · 납세", "입주박람회 운영에 적합한 업종 사업자등록 · 국세 · 지방세 체납 없음", "종목 ‘전시, 박람회 및 행사 대행업’ · ‘광고대행업’ · 체납 없음", "2 사업자등록증 · 등기부 · 3 납세증명서"),
    ("실적", "타 단지 공식 입주박람회(해당 단지 협의회와 협약한 행사) 주관 실적", f"[[{len(D.SJ_REC)}건 · {sum(r[2] for r in D.SJ_REC):,}세대]] {PG('r500')}", "7 별지3호 · 협약서 사본 등"),
    ("전문인력", "건축 · 토목 · 조경 · 전기 · 기계설비 · 소방 자격 전문가 직접 고용 또는 협력 계약", f"전기 · 조경 직접 · 4개 분야 협력 {PG('c4')}", "6 별지2호 · 자격증 · 재직 · 협력 증빙"),
    ("이해관계 고지", "시행사 · 시공사 · 분양대행사 및 협의회 임원과의 이해관계 고지", f"해당 없음 · 직영 품목 먼저 공개 {PG('conf')}", "4 별지1호 · 5 인감증명서"),
]
SUB9 = ["입찰참가신청서", "사업자등록증 · 법인등기부등본", "국세 · 지방세 납세증명서", "별지1호 이해관계 · 청렴", "법인인감증명서 · 별지4호 사용인감계",
        "별지2호 전문가 명단 · 증빙", "별지3호 주관 실적 · 증빙", "회사소개서", "업무 수행 제안서(이 문서)"]
new("std", sec=S0, title=T_QUAL,
    lead="입찰 공고 3항 참가 자격 4개를 항목마다 현황과 증빙(5항 제출서류 번호)으로 답합니다.",
    body=table(["자격", "공고 3항", "엣지컴퍼니 현황", "증빙(제출서류)"], "".join(
        f'<tr><td class="n">{a}</td><td class="k">{t(b)}</td><td>{t(c)}</td><td>{t(d)}</td></tr>' for a, b, c, d in QUAL4), "q4")
         + '<div class="sb9"><b>제출서류 1 ~ 9 · PDF 1개</b>' + "".join(f'<span><i>{i}</i>{t(x)}</span>' for i, x in enumerate(SUB9, 1)) + '</div>',
    kp=("자격은 말이 아니라 [[제출 서류로]] 확인받겠습니다.", "5항 번호 순서대로 PDF 1개로 병합 · 파일명 ‘[업체명]_상주자이르네_주관사입찰서류.pdf’"))
B.CSS += (".tbl.q4 td{padding:9px 14px;font-size:15px;line-height:1.42}.tbl.q4 td.n{width:12%;font-size:16.5px;font-weight:800;color:var(--gold);white-space:nowrap}"
          ".tbl.q4 td.k{width:33%;font-size:15.5px}.tbl.q4 td:last-child{width:21%;color:var(--sub);font-size:14px}"
          ".sb9{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-top:16px;border:1px dashed rgba(200,168,106,.55);border-radius:12px;padding:12px 14px}"
          ".sb9>b{grid-column:1/-1;font-size:15px;color:var(--gold)}"
          ".sb9 span{font-size:13.2px;color:var(--sub);line-height:1.35;display:flex;gap:6px;align-items:flex-start}"
          ".sb9 i{font-style:normal;flex:0 0 20px;height:20px;border-radius:50%;background:rgba(235,203,143,.18);color:var(--gold);font-weight:800;font-size:12px;display:flex;align-items:center;justify-content:center}")

# 보증보험 · 예치금 이행 이력(분당 p78 · 북수원과 같은 1쪽) — 금액 · 상대방 정보 · 계좌 가림
T_BOND = "보증보험 · 예치금 [[이행 이력]]"
BOND_IMG = "assets_ins/os_sgi_bond_masked.png"   # SGI 계약보증보험증권 1쪽 — 상대방 · 보험료 · 증권번호 뒷자리 · 가입금액 가림(깃 제외)
ESCROW_IMG = "assets_ins/os_escrow.jpg"          # 에스크로(예치금) 약정서 — 단지명 · 날짜 · 금액 · 상대방 대표 · 연락처 · 계좌 가림(깃 제외)


def _bcard(tag, name, img, alt, rows):
    dl = "".join(f"<div><dt>{t(k)}</dt><dd>{t(v)}</dd></div>" for k, v in rows)
    return (f'<div class="cd"><div class="hdr"><i>{tag}</i><b>{t(name)}</b></div>'
            f'<div class="im"><img src="{img}" alt="{alt}"></div><dl>{dl}</dl></div>')


new("std", sec=S0, title=T_BOND,
    lead="보증보험증권 발급과 법무법인을 통한 예치금 약정 - 이행을 담보하는 두 가지 방식을 모두 실제로 해 왔습니다. 금액 · 상대방 정보 · 계좌는 가렸습니다.",
    body=('<div class="bnd2">'
          + _bcard("BOND", "보증보험증권 발급 이력", BOND_IMG, "서울보증보험 계약보증보험증권 1쪽(가림본)",
                   [("발급 기관", "서울보증보험(SGI)"), ("보증 종목", "계약보증보험"), ("발급일", "2026.09.07")])
          + _bcard("DEPOSIT", "예치금 약정 이력", ESCROW_IMG, "에스크로(예치금) 약정서(가림본)",
                   [("약정 당사자", "입주예정자협의회 · 엣지컴퍼니 · 법무법인"), ("담보 내용", "물품지원 이행담보"), ("예치 방식", "법무법인 지정 계좌 예치(에스크로)")])
          + '</div>'),
    kp=("보증보험 발급과 예치금 약정, [[두 방식 모두 실제로 이행]]해 왔습니다.",
        f"{ST['short']} 이행보증보험증권은 협약 후 협의회를 피보험자로 발급(보험기간 입주 개시 1년 전 ~ 입주 개시 후 1년 · 발급 시점은 입예협과 확인) · 위 증권은 다른 용역의 계약보증 · 가림 없는 원본은 요청 시 열람"))
B.CSS += (".bnd2{flex:1;min-height:0;display:grid;grid-template-columns:0.82fr 1.18fr;gap:22px}"
          ".bnd2 .cd{min-height:0;display:flex;flex-direction:column;border:1px solid rgba(200,168,106,.4);border-top:2px solid var(--gold2);border-radius:14px;"
          "background:linear-gradient(180deg,rgba(235,203,143,.08),rgba(255,255,255,.015) 40%);padding:12px 16px 12px}"
          ".bnd2 .hdr{display:flex;align-items:baseline;gap:10px;margin-bottom:10px}.bnd2 .hdr i{font-style:normal;font-size:11.5px;letter-spacing:.24em;color:var(--gold2);font-weight:700}"
          ".bnd2 .hdr b{font-size:18px;color:var(--gold)}"
          ".bnd2 .im{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,.18);border-radius:8px;padding:10px}"
          ".bnd2 .im img{max-width:100%;max-height:100%;object-fit:contain;display:block;border-radius:3px;box-shadow:0 10px 28px rgba(0,0,0,.5);background:#fff}"
          ".bnd2 dl{margin:10px 0 0;display:flex;flex-direction:column;gap:4px}"
          ".bnd2 dl div{display:grid;grid-template-columns:96px 1fr;font-size:13.5px;border-bottom:1px solid rgba(255,255,255,.08);padding:2px 0}"
          ".bnd2 dt{color:var(--sub)}.bnd2 dd{margin:0;color:var(--ink)}")

new("std", sec=S0, title=T_CONF,
    lead="공고 3항 이해관계 고지 · 별지1호 - 신고할 이해관계와 지킬 약속을 제안서에도 그대로 적었습니다.",
    body=B.rows([
        ("시행 · 시공 · 분양대행 · 옵션업체", "하도급 · 협력업체 등록 · 지분 · 친인척 관계 [[없음]](별지1호 1)"),
        ("협의회 임원 · 가족", "이해관계 [[없음]](별지1호 2)"),
        ("직영 품목 먼저 공개", "조명 · 커튼(엣지리브커튼) · 실링팬은 주관사 직영 품목입니다 - 다른 업체와 [[같은 심사 · 외부 최저가 비교]]를 받고, 협의회가 원하면 박람회에서 뺍니다."),
        ("자문 ↔ 영업 분리", "시공 단계 자문 인력은 공동구매 품목을 권하지 않습니다. 기본 사양 개선을 방해하거나 시행 · 시공사 입장을 대변하지 않습니다(별지1호 4)."),
        ("금품 · 개별 접촉 없음", "임원 · 운영위원 개인에게 금품 · 향응 없음 · 공고 이후 임원 · 운영위원 · 입주예정자 · 법무대리인 개별 접촉 · 영업 없음(공고 7항) · 문의는 공식 이메일로만"),
        ("미선정 시", "상주 자이르네 입주예정자 대상 별도 박람회 · 공동구매를 하지 않고, 입찰 비용을 청구하지 않습니다(별지1호 5)."),
    ], title_w=250),
    kp=("사실과 다르거나 서약을 어기면 [[선정 취소 · 협약 해지]]를 받아들입니다.", "별지1호 이해관계 신고 및 청렴 서약서(인감 날인) = 제출서류 4"))

NOTE7 = [  # 공고 6 선정 방식 · 7 기타 유의사항 — (항목, 약속)
    ("서류 심사(11.03)", "참가 자격과 제안서 검토 - 시공 단계 지원 계획과 분야별 전문인력을 중점으로 보신다는 점에 맞춰 ① 시공 단계와 전문인력을 07장 앞에 두었습니다."),
    ("PT 심사(11.15)", "계약 후 실제 업무를 맡을 책임자([[주관사업 총괄 본부장]])와 결정권자(대표이사)가 함께 나옵니다. 발표는 둘 중 한 명이 맡고 질의에는 둘이 함께 답하며, 제안 조건은 대표이사가 그 자리에서 확약합니다. 제출한 조건을 [[바꾸거나 더하지 않습니다.]]"),
    ("제안서 = 협약서의 일부", "실현 가능한 내용만 적었고, 확정 전 사항은 ‘(안)’ · ‘협의’로 구분했습니다."),
    ("시공 단계 지원 = 협약 직후", "정당한 사유 없이 이행하지 않고 서면 시정 요청 후에도 개선하지 않으면 협약 해지를 받아들입니다."),
    ("허위 기재", "제출 서류의 허위 기재가 확인되면 선정 이후라도 협약 해지를 받아들입니다."),
    ("반환 · 이의", "제출 서류 반환을 요구하지 않고, 선정 결과에 이의를 제기하지 않습니다. 명시되지 않은 사항은 운영위원회 결정을 따릅니다."),
]
new("std", sec=S0, title=T_NOTE,
    lead="입찰 공고 6 선정 방식 · 7 기타 유의사항을 제안에 그대로 반영했습니다.",
    body=table(["항목", "엣지컴퍼니 약속"], "".join(
        f'<tr><td class="k">{t(a)}</td><td>{t(b)}</td></tr>' for a, b in NOTE7), "nt7")
         + '<div class="hflow"><span>제안서 제출 (10.28 17:00)</span><i>›</i><span>서류 심사 (11.03)</span><i>›</i><span>PT 심사 (11.15)</span><i>›</i>'
           '<span>운영위원회 의결 · 선정</span><i>›</i><span>협약 · 시공 단계 지원 시작</span></div>',
    kp=("제안서에 쓴 조건 그대로 [[PT에서도, 협약서에서도]] 같습니다.", "입찰참가신청서 · 별지1 ~ 3호는 사용인감 날인 + 별지4호 사용인감계 · 법인인감증명서(3개월 이내) 첨부"))
B.CSS += ".tbl.nt7 td{padding:12px 14px;font-size:15.2px;line-height:1.45}.tbl.nt7 td.k{width:21%;font-size:15.5px;color:var(--ink);font-weight:700}"

# 기존 장에서 쓰던 표 스타일(분당 01장 블록) — 다른 장이 그대로 쓰므로 함께 둔다
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
          ".itr.g{border-style:solid;border-color:rgba(235,203,143,.55);background:rgba(235,203,143,.06)}"
          ".tbl.vm td{padding:14px 14px}.tbl.vm td.k{width:12%}.tbl.vm td:last-child{width:30%}"
          ".tbl.q7 td{padding:11px 14px;font-size:16px;line-height:1.45}.tbl.q7 td.k{font-size:16.5px;width:30%}.tbl.q7 td:last-child{width:22%;white-space:nowrap}")

# ------------------------------------------------------------ 01장으로 보낼 장(심사 1 적합성 — 연혁 · 대표자 · 운영인력)
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
    lead=f"공고 3항 · 회사 연혁 - 법인 설립({D.FOUNDED})부터 지금까지, 등기부 · 등록증 · 인증서 · NICE 연혁 · 협약으로 확인되는 기록만 적었습니다.",
    body=f'<div class="nb"><div class="hist"><ol>{"".join(_items[:_half])}</ol><ol>{"".join(_items[_half:])}</ol></div></div>',
    kp=("2023년부터 [[해마다]] 1,000세대 이상 입주박람회를 맡아 왔습니다.",
        "출처: 법인등기부 · 전기공사업 등록증 · ISO 인증서 · NICE 기업신용평가보고서 연혁 · 세스코 협약"))

_lead_n = getattr(D, "STAFF_LEAD", 2) + sum(c for _, c, _ in D.STAFF)
PRO5 = [("전기", 3), ("도장", 2), ("타일", 1), ("조경", 1), ("간호사", 1)]
new("std", sec=S0, title=T_PEOPLE,
    lead=f"공고 6항 PT · 별지2호 전담 책임자 - 대표자와 핵심 운영인력이 맡아 온 실적과, {ST['short']}에서 맡을 역할입니다.",  # 본부장 10-15 밤: 이 쪽 단지 표기 = 정식 명칭
    # 대표 개인 경력(본부장 10-15) — NICE 기업신용평가보고서(제출서류 14 ③ 발췌) 13쪽 '대표자1' 약력 · 전기공사업 등록증 · ISO 인증서(3종 모두 최초 2025.08.12)로
    # 확인되는 사실만. 현장 총괄 문구는 본부장 10-15 확인. 경영경력 8년 8개월 = NICE 평가 당시(2026.05) 기재값.
    body=('<div class="nb"><div class="ppx">'
          '<div class="pp1 ceo"><i>대표이사</i><h3>고진식</h3><ul>'
          '<li>울산과학대학교 전기과</li>'
          '<li>대한유화 2011 ~ 2018(최종 대리) → 엣지조명 대표 2019 ~ 2021 → <b>㈜엣지컴퍼니 창업 2022.02</b> · 대표 경영경력 8년 8개월(NICE 2026.05 기준)</li>'
          f'<li>전기공사업 등록(제 울산-00821호) 대표자</li>'
          '<li>ISO 9001 · 14001 · 45001 인증 취득 총괄 - 최초 인증 2025.08.12 · 박람회 · 전시회 기획 · 대행 / 전기공사 / 조명공사</li>'
          '<li><b>주관 박람회 전 과정 현장 점검</b>(참여업체 검수 · 부스 배치 · 당일 운영)</li>'  # 본부장 10-15 밤: '진두지휘' 삭제
          '<li>법인 대표이사 · 계약 최종 책임 · 2차 PT 동석</li></ul></div>'
          '<div class="pp1"><i>주관사업 총괄 본부장 · 전담 총괄</i><h3>총괄 본부장</h3><ul>'
          f'<li>{ST["name"]} 총괄 책임 · 2차 PT 참석(발표 · 질의) · <span style="white-space:nowrap">직통 {D.MANAGER[2]}</span></li>'
          # 본부장 10-14 저녁: 개인 현장(송도) 문구 대신 협의회 운영 경험 한 줄 · 단지명은 쓰지 않음(송도는 회사 실적 10개 단지로만)
          '<li><b>입주예정자협의회 회장 3년 역임</b> - 입주민 입장에서 협의회 운영을 직접 겪어 봤습니다</li>'
          '<li>입예협 정례회의 · 박람회 · 사전점검 현장 참석 · 이슈 직접 관리</li></ul></div>'  # 경력 칸은 본부장 10-14 삭제
          '<div class="pp2"><i>핵심 운영인력</i><h3>임직원 ' + str(_lead_n) + '명</h3>'
          + "".join(f'<div><b>{c}<small>명</small></b><span>{n}</span><p>{t(r)}</p></div>' for n, c, r in D.STAFF)
          + '<div class="pro2">' + "".join(f'<span>{f} {c}</span>' for f, c in PRO5) + '<em>자격 · 협회 등록 인력 · 2026.10 기준</em></div></div>'
          '</div><div class="ppb">'
          f'<div><b>{_rec_n}<small>개 단지</small></b><span>1,000세대 이상 주관<br>2023.04 ~ 2026.09 입주</span></div>'
          f'<div><b>{_rec_hh:,}<small>세대</small></b><span>1,000세대 이상<br>주관 세대 합계</span></div>'
          '<div><b>4,470<small>세대</small></b><span>단일 단지 최대<br>레이카운티</span></div>'
          '<div><b>67<small>개 단지</small></b><span>누적 수임 56,361세대<br>(전신 실적 · 입주 예정 포함)</span></div>'
          '</div></div>'),
    # 본부장 10-15 밤: '전기 전공 · 조명 사업 출신 대표가 …' 대신 책임 구조(대표 · 본부장 · 4개 팀 = 이 쪽 카드 그대로 · 입주 후 1년 = 주관 창구 기간)
    kp=("대표 · 총괄 본부장 · 4개 팀이 협약부터 입주 후까지 [[한 창구로]] 책임집니다.",
        "대표 약력은 NICE 보고서 13쪽(신용평가서) · 팀별 담당은 협약 시 명단 제출 · 실적 증빙은 제출서류 7(협약서 · 행사일정 · 카페 공지 · NICE 연혁)"))
B.CSS += (".ppx{display:grid;grid-template-columns:1.22fr .82fr 1.3fr;gap:16px;flex:1;min-height:0}"
          ".ppx>div{border:1px solid var(--line);border-top:2px solid var(--gold2);border-radius:14px;padding:14px 18px;display:flex;flex-direction:column;min-height:0;"
          "background:linear-gradient(180deg,rgba(235,203,143,.08),rgba(255,255,255,.01) 45%)}"
          ".ppx i{font-style:normal;font-size:12px;letter-spacing:.14em;color:var(--gold2);font-weight:700}"
          ".ppx h3{font-size:26px;font-weight:800;color:var(--gold);margin:2px 0 10px}"
          ".pp1 ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:11px}"
          ".pp1 li{font-size:15px;line-height:1.5;padding-left:14px;position:relative}.pp1 li:before{content:'';position:absolute;left:0;top:8px;width:6px;height:6px;border-radius:50%;background:var(--gold2)}"
          ".pp1 li b{color:var(--gold)}"
          ".pp1.ceo ul{gap:6px}.pp1.ceo li{font-size:13.6px;line-height:1.42}.pp1.ceo li:before{top:7px}"
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

# 계약 취소 · 환불 규정 전문(공고 3항 9 · 10 · 신뢰성) — 제안서 03장에 2쪽으로 싣는다.
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
    ("제7조 (불이행 시 조치 및 주관사 책임)", ["참여업체가 취소·환불을 지연하거나 거부하면 계약자는 주관사 콜센터에 접수할 수 있다. 주관사는 사실을 확인한 뒤 계약자에게 피해 금액을 <b>먼저 보상</b>하고, 참여업체와는 계약 조항에 따라 정산한다(참여업체 특약이행각서 준용).",
                                  "불이행 업체에는 1단계 홍보정지, 2단계 총액 10% 배상, 3단계 자격박탈 및 입예협 승인을 받아 전 계약을 대체업체로 이관하는 패널티를 차례로 부과한다.",
                                  "참여업체가 도산한 경우 동종업체로 사후관리를 이관하고, 그 A/S 비용은 주관사가 전액 부담한다.",
                                  # 재검증 10-14: 새 증권 한도(울주대리점)는 확인 전 — 금액은 협약 때 확정(08 방안서 4장 · p89와 같은 조건부)
                                  "주관사의 보상 재원으로 하자 예치금 최대 1억원(엣지컴퍼니 자산으로 예치)과 이행보증보험(2년 · 최대 10억원 범위, 금액은 협약 때 단지 규모에 맞춰 확정)을 둔다."]),
    ("제8조 (가격 보호 — 최저가 차액 10배 보상)", [f"공동구매 품목과 브랜드·모델명이 같은 새 제품이 계약 후 7일 이내에 인근({ST['local']}) 오프라인 매장에서 더 낮은 정상 판매가로 실제 판매된 사실이 구매 영수증(판매 매장 사업자 정보 · 모델명 · 금액 기재)으로 확인되고 주관사가 해당 매장에 판매 사실을 확인하면, 참여업체는 차액의 10배를 보상하고 판매가를 조정한다.",
                                         "보상액은 1건당 50만원(해당 품목 계약금액이 더 적으면 그 금액)을 넘지 않으며, 최대 금액은 협약 시 입예협과 협의해 조정할 수 있다(같은 세대 · 같은 품목에는 1회). 견적서 · 가격표 · 구두 안내 가격은 보상 근거가 되지 않는다.",
                                         "온라인·홈쇼핑 판매, 시공 품목, 카드 청구할인·사은품·결합할인, 전시·리퍼 상품, 법인 특판, 한정 수량 행사가는 비교 대상에서 제외한다.",
                                         "계약자는 주관사 콜센터에 접수하고, 주관사는 사실 확인 후 7일 이내에 보상이 이행되도록 관리한다."]),
    ("제9조 (고지)", ["주관사는 이 규정을 박람회장 · 온라인 박람회에 게시하고, 입주예정자협의회 카페에는 입예협 승인 후 게시하며, 모든 공동구매 계약서에 첨부한다."]),
    ("제10조 (효력)", ["이 규정은 협약 체결일부터 협약 종료일(입주박람회 종료 및 공동구매 하자 A/S 보증 기간 만료 시)까지 체결된 계약에 적용하며, 협약 종료 후에도 해당 계약의 이행·보증 기간 동안 효력을 가진다."]),
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
    lead="공고 2항 ④ 분쟁 대응 - 입주민이 계약을 취소할 때 적용할 계약금 환불 규정입니다. 모든 공동구매 계약서에 이 규정을 첨부합니다.",
    body=f'<div class="rgl">{_arts(_ARTS1)}</div>',
    kp=("기한 안 취소는 [[전액 환불]], 업체 귀책이면 [[기한과 관계없이]] 전액 환불합니다.", "세부 품목 기한은 다음 장 [별표] · 모든 공동구매 계약서에 첨부"))
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
    kp=("환불은 [[3영업일 이내]], 업체가 미루면 [[주관사가 먼저 보상]]합니다.", "협약 체결일부터 협약 종료일(공동구매 품목 A/S 종결)까지 체결된 계약에 적용 · 모든 공동구매 계약서에 첨부"))
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


# 세대 혜택 15만원 상당 ≠ 공구가 인상 — 참가비 정액 + 입예협 가격 검증
T_SEP = f"세대당 {D.FUND}만원 상당, [[공구가와 따로]]입니다"
new("std", sec=S0, title=T_SEP,
    lead=f"‘{D.FUND}만원 상당을 주면 공구가가 오르지 않느냐’는 질문에 구조로 답합니다 - 세대 혜택은 주관사 몫에서 나가고, 공구가는 입예협이 직접 검증합니다(공고 2항 ③).",
    body=('<div class="sepx"><div class="sepf">'
          '<div class="sb1"><i>업체</i><b>참가비 정액제</b><span>업체 참가비는 정액으로 - 공구가와 연동하지 않음</span></div><em>›</em>'
          '<div class="sb1 hl"><i>주관사</i><b>운영비 + 세대 혜택</b><span>박람회 운영비와 세대당 ' + str(D.FUND) + '만원 상당을 주관사 몫에서 부담</span></div><em>›</em>'
          '<div class="sb1"><i>입주민 세대</i><b>세대 혜택 패키지</b><span>패키지 A·B·C · 사용 내역 공개 · 공구단가와 무관</span></div></div>'
          '<div class="sepn">공구가는 이 흐름과 따로 - <b>업체 공개 입찰 경쟁</b>과 <b>시중가 · 온라인 최저가 검수</b>로 정해집니다</div>'
          + B.tiles([
              dict(lb="01 · 정액", nm="참가비 정액제", ds="업체 참가비는 정액으로 받습니다. 세대 혜택을 공구가에 얹는 구조가 아닙니다."),
              dict(lb="02 · 공개", nm="단가표 사전 공개", ds="박람회 전 품목별 단가 · 할인율 · 모델코드를 입예협이 검수합니다. 현장 가격 변경 없음."),
              dict(lb="03 · 검증", nm="시중가 · 온라인 최저가 비교", ds="같은 조건 총액으로 비교하고, 입예협이 품목을 골라 직접 확인합니다."),
              dict(lb="04 · 보상", big="10", unit="배", nm="최저가 차액 보상", ds="인근 매장 동일 제품이 더 싸면 차액 10배 보상(구매 영수증 · 주관사 확인 · 1건당 최대 50만원 · 최대 금액은 입예협과 협의 · 온라인·시공 품목 제외)"),
          ], cols=4) + '</div>'),
    kp=(f"세대 혜택을 0원으로 해도 공구가는 같습니다 - 가격은 [[업체 경쟁과 가격 검수]]로 정해집니다.", "참가비 정액제 · 카드·현금 동일가 · 최저가 차액 10배(온라인·시공 품목 제외)"))
B.CSS += (".sepx{flex:1;min-height:0;display:flex;flex-direction:column;gap:14px}"
          ".sepf{display:grid;grid-template-columns:1fr 30px 1.15fr 30px 1fr;align-items:stretch}"
          ".sepf em{display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:800;color:var(--gold)}"
          ".sepf .sb1{border:1px solid var(--line);border-radius:14px;padding:16px 18px;display:flex;flex-direction:column;gap:4px}"
          ".sepf .sb1.hl{border-color:rgba(235,203,143,.7);background:linear-gradient(180deg,rgba(235,203,143,.14),rgba(235,203,143,.03))}"
          ".sepf i{font-style:normal;font-size:12px;letter-spacing:.18em;color:var(--gold2);font-weight:700}"
          ".sepf b{font-size:21px;font-weight:800}.sepf span{font-size:14.5px;color:var(--sub);line-height:1.45}"
          ".sepn{border:1px dashed rgba(200,168,106,.6);border-radius:10px;padding:10px 16px;font-size:15.5px;color:var(--sub);text-align:center}"
          ".sepn b{color:var(--gold)}")


CPL = [  # 가산점 5 — 입주민 컴플레인 예시와 처리 기준(본 제안서의 약속과 같은 기준)
    ("커튼 · 블라인드", "설치일에 치수가 맞지 않음", "재실측 → 재제작 → 재방문 설치 · 비용은 업체 부담", "48시간 내 재실측"),
    ("입주청소", "청소 상태 미흡(창틀·욕실)", "사진 접수 → 업체 재청소 → 입주민 확인 서명", "48시간 내 재방문"),
    ("시스템에어컨 · 설치 품목", "배관 누수 · 작동 불량", "방문 점검 · 수리 → 업체 미응답 시 주관사가 먼저 보상 후 업체 정산", "48시간 하자보수 원칙"),
    ("업체 사정", "참여업체 폐업 · 연락 두절", "동종업체 이관 · 대체 업체 연결 · A/S 승계(비용 주관사 부담)", "주관사 책임 처리"),
    ("가격", "박람회가보다 싼 판매 확인", "동일 브랜드·동일 제품 확인 → 최저가 차액 10배 보상(온라인 판매·시공 품목 제외)", "규정 기준 지급"),
    ("계약 취소", "시공 전 취소 요청", "품목별 취소 기한 확인 → 위약금 없이 환불", "3영업일 내 환불"),
]
new("std", sec=S0, title=T_CPL,
    lead="공고 2항 ④ 민원 대응 - 박람회 뒤 자주 생기는 컴플레인 예시와 처리 기준, 타 단지 해결 사례입니다. 접수부터 완료까지 주관 콜센터가 기록합니다.",
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
        dict(lb="02", big="10", unit="배", nm="최저가 차액 보상", ds="인근 매장 동일 제품이 더 싸면 차액 10배 보상(구매 영수증 · 주관사 확인 · 1건당 최대 50만원 · 최대 금액은 입예협과 협의 · 온라인·시공 품목 제외)"),
        dict(lb="03", big="추가할인", nm="실적 비례 추가할인", ds="업체 기대매출을 넘기면 계약 세대 잔금에서 추가할인. 할인율은 업체 입찰 조건으로 입예협과 확정."),
        dict(lb="04", big=str(D.DEPOSIT_MAX), unit="%", nm="계약금 상한", ds=f"계약금은 총액의 {D.DEPOSIT_MAX}% 이하, 잔금은 시공·설치 후. 현금·카드 동일가."),
    ]),
    kp="가격은 말이 아니라 [[사전 공개 단가 + 최저가 보장]]으로 검증받습니다.")

# 대응표 쪽 번호 — 재배치 뒤 제목으로 찾는다(reorg에서 바뀐 제목은 바뀐 뒤 제목)
PGREF = {
    "num": "숫자로 보는 [[엣지컴퍼니]]", "hist": T_HIST, "succ": "주관 [[성공사례]] · 수임실적",
    "people": T_PEOPLE, "docs": "회사 개요와 [[법인 서류]]", "ev": "재무·납세·고용 [[증빙 원본]]", "cert": "공인된 [[자격과 신뢰]]",
    "rec": "타 단지가 남긴 [[추천과 협약]]",
    "expo": T_EXPO, "items": T_ITEMS, "vendors": T_VENDORS, "vmgt": T_VMGT, "screen": "[[4단계]] 공개 심사 프로세스",
    "sep": T_SEP, "guard4": "공동구매 단가를 지키는 [[4가지 장치]]",
    "defect": T_DEFECT, "cpl": T_CPL, "rule1": T_RULE1, "rule2": T_RULE2, "wty": "참여업체 [[하자보증]] 체계",
    "req": T_REQ, "qchk": "공용부 [[구조·시공 품질]] 점검", "precheck": "사전점검 당일 [[현장 지원]]",
    "check": T_CHECK, "x10": "[[최저가 차액 10배]] 보상",
    "pm": T_PM, "call": "주관 [[콜센터]]와 선보상", "map": T_MAP,
    "c1": T_C1, "c2": T_C2, "c3": T_C3, "c4": T_C4, "c5": T_C5, "yj": T_YJ, "conf": T_CONF,
    "r500": T_R500, "trust": T_TRUST, "stable": T_STABLE, "fact": T_FACT, "as": T_AS, "special": T_SPECIAL,
    "lx": T_LX, "lx2": T_LX2, "mon1": T_MON1, "mon2": T_MON2, "report": T_REPORT,
    "qual": T_QUAL, "bond": T_BOND, "note": T_NOTE, "safe": T_SAFE, "priv": T_PRIV, "fund": T_FUNDCH,
    "support": T_SUPPORT, "staff": T_STAFF,
    "venue": "행사장 대관과 [[운영 준비]]", "floor": "박람회장 배치와 [[인원 운영]] (안)", "cafe": "입예협 카페 [[홍보 콘텐츠]] 제작", "online": "못 오셔도 [[괜찮습니다]]",
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
# 재검증 10-14: '사옥'은 자가 건물로 읽힘 — NICE 사업장 현황(14 ③ 원본 기준)은 2 · 3층 모두 임차 → '본사 · 쇼룸'(제목은 아래 '재검증 2차' 블록에서 바꿈)
B.PAGES[i][1]["body"] = B.media("assets/사옥.jpg", "엣지컴퍼니 울산 본사 · 쇼룸", [
    ("본사 · 쇼룸 운영", "울산 온산로 615-1(2 · 3층)에서 본사·쇼룸·시공팀을 직접 운영합니다."),
    ("자본금 2억원", "하자 예치금의 재원이 되는 실체입니다."),
    ("현금흐름 A · 부채비율 17.1% / 신용 BB-", "NICE 기업신용평가(2026.06.19). 입예협 제출 증빙 즉시 발급 가능."),
    ("ISO 9001·14001·45001", "품질·환경·안전보건 국제표준 3종 인증 보유."),
])

# 19p 공인된 자격과 신뢰: A → BB- → MOU → ISO 순, 키포인트 교체(4대보험 문구는 18p 발췌 장으로)
i = find("공인된 [[자격과 신뢰]]")
B.PAGES[i][1]["body"] = B.cards([
    dict(lb="CASH FLOW", big="A", nm="현금흐름 등급", ds="박람회 운영 중 자금 흐름 안정성 검증."),
    dict(lb="CREDIT", big="BB-", nm="기업 신용등급", ds="공인 평가기관 기업신용평가 등급."),
    # 재검증 10-14: 삼성 계약서 제목은 '업무제휴 계약서'(MOU 아님) · 상대방 판독 불확실(삼성전자판매㈜로 보임) → '삼성 측 업무제휴'(pages21.json 결정과 같게)
    dict(lb="PARTNERSHIP", big="제휴", nm="삼성 측 업무제휴 · 세스코 MOU", ds="세스코 MOU 2025.11 체결. LX하우시스·에몬스와 제휴 추가 협의 중."),
    dict(lb="ISO", big="3", unit="종", nm="국제표준 인증", ds="ISO 9001 · 14001 · 45001."),
])
B.PAGES[i][1]["kp"] = "재무 평가 · 대기업 제휴 · 국제표준 인증 — [[공인 기관이 검증한 항목]]만 적었습니다."

# 22p 지사망: 직영 4곳 + 협력 8곳 = 전국 12개 지사망(2026.10 확정). 본부장 10-19: 아랫지역(경북 상주) 단지 = 울산 · 부산 · 청주 · 대전 순.
i = find("전국 지사망")
B.PAGES[i][1]["title"] = "전국 지사망 · [[직영 4곳 + 협력 8곳]]"
B.PAGES[i][1]["lead"] = "지역 거점 3곳이 책임지고, 협력 네트워크 9곳이 접수 · 연결을 돕습니다."
# 본부장 10-22 저녁: 경인 · 청주 = 개인사업자 지사의 쇼룸 · 사무실 무상 사용 합의(간판 우리 제작 · 설치) → '직영' 표기 금지 · 대전 · 부산은 주소 · 사용 합의 확인 전까지 협력 네트워크
B.PAGES[i][1]["body"] = B.cards([
    dict(lb="BRANCH 01", big="울산", nm="울산 본사", ds="본사·쇼룸. 시공팀 상주. 경북 · 대구권 거점."),
    dict(lb="BRANCH 02", big="경인", nm="경인 지사(평택)", ds="상설 쇼룸 · 입예협 회의 공간. 수도권 거점."),
    dict(lb="BRANCH 03", big="청주", nm="충북 청주 지사", ds="상설 쇼룸 · 사무실. 충청권 거점."),
    dict(lb="NETWORK", big="9", unit="곳", nm="협력 네트워크", ds="대전 · 부산 등 권역별 접수 · 연결.", hl=True),
], cols=4)

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
                            "사업자등록증·재무제표·완납증명서·특약이행각서를 낸 업체만 입점.")
            _v = _v.replace('<div class="nm">사업자·재무·예치금</div>', '<div class="nm">사업자·재무·이행각서</div>')
            _v = _v.replace("조경 감리 관점에서", "사내 조경 전문 인력(임원)이")  # 본부장 10-12: 조경은 사내 직접
            # 검증 10-14: B 패키지(15만원 상당 범위 · 입예협 선택) 항목에 '무료'를 쓰면 별도 확정 혜택처럼 읽힘
            _v = _v.replace("입주예정자 대상 설명회를 무료 제공합니다.", "입주예정자 대상 설명회를 제공합니다(B\u00a0패키지 · 범위는 입예협 협의).")
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
    ("공인된 [[자격과 신뢰]]", [(15, "[[삼성 측 업무제휴]] 계약서"), (12, "[[ISO 9001 · 14001 · 45001]] 인증서")]),
    ("전국 지사망", [(18, "엣지컴퍼니 전국 지사")]),
    ("[[커뮤니티 시설]] 업그레이드", [(122, "아파트 문주 · [[경관조명 컨설팅]] 사례")]),
    ("참여업체 [[하자보증]] 체계", [(55, "[[특약이행각서]] · 업체 도산 시 처리"), (56, "주요 클레임 품목 · [[품목별 보상 규정]]")]),
    ("주관 [[콜센터]]와 선보상", [(59, "주관 콜센터 프로세스")]),
    ("[[4단계]] 공개 심사 프로세스", [(43, "입주박람회 공동구매 품목 리스트")]),
    ("협의회 전용 [[8가지 무상 단지지원]]", [(103, "공용부 [[철근탐지 · 콘크리트 강도]] 측정"), (115, "[[열화상 드론]] 점검"), (120, "[[라돈 측정]] 지원(B 패키지)")]),
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
            if b.get("capbelow"):
                cls = (cls + " cb").strip()
            if it.get("fit") == "cover":  # 캡션 아래 + 사진은 칸에 꽉 차게(잘림 허용)
                cls = (cls + " cv").strip()
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
    if k == "docgroups":  # 분당 10-16과 같게: 서류를 묶음(제휴 · 면허·인증)별 테두리 안에 나눠 배치
        gs = ""
        for g in b["groups"]:
            gs += (f'<div class="gp"><div class="gh"><i>{g["tag"]}</i><b>{t(g["head"])}</b>'
                   + (f'<small>{t(g["sub"])}</small>' if g.get("sub") else "") + "</div>"
                   + blk({"type": "docs", "items": g["items"]}) + "</div>")
        return f'<div class="dgrp" style="grid-template-columns:{b.get("cols", "1fr 1fr")}">{gs}</div>'
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
    _held = {r[1] for r in D.RECENT3_500}  # 박람회를 이미 치른 단지(영주자이 2026.08 개최 · 2026.12 입주) — '개최 예정'에서 뺀다
    _li = "".join(f'<li class="{"big" if n >= 1000 else ""}{" fut" if m > _now else ""}"><span>{nm} <i>{m}{" 입주 · 주관 개최 예정" if m > _now and nm not in _held else " 입주 예정" if m > _now else ""}</i></span>'
                  f'<b>{n:,}{u}</b></li>' for nm, n, u, m in _rows)
    _cols = [f"<ul>{_li}</ul>"]
    _n1k = sum(1 for r in _rows if r[1] >= 1000)
    _nfut = sum(1 for r in _rows if r[3] > _now and r[0] not in _held)
    _di = next(i for i, (_, k) in enumerate(B.PAGES) if k.get("title") == "[[대단지]] 운영 경험")
    B.PAGES.insert(_di + 1, ("std", dict(sec=B.PAGES[_di][1].get("sec", ""), title=f"2023년 이후 수임 단지 [[{sum(D.DANJI_N.get(r[0], 1) for r in _rows)}곳]]",
        lead="1,000세대 이상(금색)은 세대수 순, 나머지는 입주 순 · 날짜는 입주 연월 · 입주 전 단지는 박람회 주관 개최 예정.",
        body='<div class="ylist">' + "".join(_cols) + "</div>",
        kp=(f"{sum(D.DANJI_N.get(r[0], 1) for r in _rows)}개 단지 · 1,000세대 이상 [[{_n1k}곳]] · 주관 개최 예정 [[{_nfut}곳]]",
            "단지명은 공식 명칭 · 세대수는 NICE 연혁 · 수임 목록 기재 기준 · 양정자이더샵SK VIEW 1·2단지는 2개 단지로 집계"))))
    # 앞으로 주관할 단지(본부장 10-19) — 수임 단지 장 바로 뒤 · 입주 전 단지 = 주관 개최 예정(박람회 시기 = 입주 2 ~ 3개월 전 · 2 ~ 3일)
    def _ym(m, k):
        y, mo = int(m[:4]), int(m[5:]) - k
        return f"{y + (mo - 1) // 12}.{(mo - 1) % 12 + 1:02d}"
    _fu = sorted([r for r in D.SUIM if r[3] > _now and r[0] not in _held], key=lambda r: r[3])
    _ftr = "".join(f'<tr><td class="k">{nm}</td><td style="text-align:right">{n:,}세대</td><td style="text-align:center">{m}</td>'
                   f'<td style="text-align:center">{_ym(m, 3)} ~ {_ym(m, 2)} (안)</td><td style="text-align:center">주관 개최 예정</td></tr>' for nm, n, _u, m in _fu)
    _fh = sum(r[1] for r in _fu)
    _fband = ('<div class="bband" style="margin-top:18px">'
              f'<div><i>주관 개최 예정</i><b>{len(_fu)}<small>개 단지</small></b></div>'
              f'<div><i>예정 세대 합계</i><b>{_fh:,}<small>세대</small></b></div>'
              f'<div><i>1,000세대 이상</i><b>{sum(1 for r in _fu if r[1] >= 1000)}<small>곳</small></b></div>'
              f'<div class="nx"><i>가장 가까운 박람회</i><b>{_ym(_fu[0][3], 3)} ~ {_ym(_fu[0][3], 2)}</b><p>{_fu[0][0]} · {_fu[0][3]} 입주</p></div></div>')
    B.PAGES.insert(_di + 2, ("std", dict(sec=B.PAGES[_di][1].get("sec", ""), title=f"앞으로 주관할 단지 [[{len(_fu)}곳]]",
        lead="이미 수임해 입주를 준비 중인 단지입니다. 박람회는 입주 2 ~ 3개월 전, 2 ~ 3일 동안 엽니다.",
        body='<div class="nb">' + table(["단지", "세대", "입주 예정", "박람회 시기(안)", "구분"], _ftr) + _fband + "</div>",
        kp=(f"{_fh:,}세대의 박람회가 이미 [[예정되어 있습니다]] - 같은 팀이 {D.SITE['name']}도 맡습니다.",
            "입주 일정 · 박람회 날짜는 각 단지 입주예정자협의회와 확정 · 사정에 따라 바뀔 수 있음"))))
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
             '<div class="nx"><i>다음 대단지 · 2027.09 입주 예정</i><b>2,667<small>세대</small></b><p>힐스테이트 더샵 상생공원 1·2단지 합계(999 + 1,668)</p></div></div>')
    _si = next(i for i, (_, k) in enumerate(B.PAGES) if k.get("title") == "주관 [[성공사례]] · 수임실적")
    B.PAGES.insert(_si + 1, ("std", dict(sec=B.PAGES[_si][1].get("sec", ""), title="[[2,000세대 이상]] 초대형 단지를 맡아 왔습니다",
        lead="단일 단지 4,470세대까지 — 대단지 박람회는 규모가 아니라 운영 시스템으로 치릅니다.",
        body='<div class="nb"><div class="bigx">' + _cards + "</div>" + _band + "</div>",
        kp=(f"대단지를 이끈 운영 시스템을 {D.SITE['name']} [[{D.SITE['households']:,}세대]]에 맞춰 옮깁니다.",
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
            dict(lb="최저가 보장", big="10", unit="배", nm="차액 보상", ds="인근 매장 동일 제품이 더 싸면 차액 10배 보상(구매 영수증 · 주관사 확인 · 1건당 최대 50만원 · 최대 금액은 입예협과 협의 · 온라인·시공 품목 제외)"),
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
    assert src_pdf and os.path.exists(src_pdf), "통합제안서 기본틀 PDF 경로를 --src <pdf> 로 주세요 (발췌 장 렌더용)"
    doc = fitz.open(src_pdf)
    for i in missing:
        doc[i].get_pixmap(dpi=FULL_DPI, clip=fitz.Rect(*FULL_CLIP_OVR.get(i, FULL_CLIP))).save(os.path.join(FULL_DIR, f"p{i:03d}.jpg"), jpg_quality=88)
    print(f"발췌 {len(missing)}장 렌더 → {FULL_DIR}")


# ============================================================ 특수 페이지
COVER = dict(kind="stats", pill="입주박람회 주관사 선정 입찰 · 업무 수행 제안서",
             tag=f"박람회를 여는 회사가 아니라, 단지를 완성시키는 회사.<br>{D.SITE['households']:,}세대 단지를 시공 단계부터 A/S 종결까지 책임지겠습니다.")
TITLE_H1 = "상주 자이르네<br><em>입주박람회 주관사<br>업무 수행 제안서</em>"
COVER_TOP = """<div class="top"><div><div class="logo">EG</div><div class="en">EDGE COMPANY</div></div>
<div class="who">주식회사 엣지컴퍼니<br>입주박람회 전문 주관사</div></div>"""


def p_cover():
    sub2 = f'<div class="sub2"><div><i>제출처</i><b>{D.CLIENT}</b></div><div><i>제안사</i><b>{D.COMPANY}</b></div></div>'
    # 표지 이미지 = 슬롯 'cover'(data.IMG) — 네이비 배경에 스며들도록 위·왼쪽을 배경색으로 페이드. 파일이 없으면 이미지 없이 중립 디자인
    im, _own = slot("cover")
    art = (f'<div class="cvart cvx osc day"><img src="assets_ins/{im}.jpg" alt="">'
           f'<span class="credit">{D.SITE["name"]} 투시도 · 분양 홍보용 이미지(광고 문구 제외) · 실제와 다를 수 있음</span></div>') if im else ""
    return f"""<section class="page cv cv4">{art}{COVER_TOP}
<div class="mid"><span class="pill">{COVER['pill']}</span>
<h1 class="cvx">{TITLE_H1}</h1>
<div class="gbar"></div>
<div class="tag2">{COVER['tag']}</div>
</div>
{sub2}
<div class="bt"><span>입주박람회 주관사 업무 수행 제안서</span><span>2026.10</span></div>
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
    # 본부장 10-17: 환영 문장 삭제 · 표지와 같은 사진 배치로 마무리(경관조명 시뮬레이션) · 연락처 세로 정렬
    _im, _own = slot("lx_front1")
    _cr = f'{D.SITE["name"]} 경관조명 시뮬레이션 · 실제와 다를 수 있음' if _own else D.LX_CAP
    art = (f'<div class="cvart cvx osc"><img src="assets_ins/{_im}.jpg" alt="" style="object-position:62% 50%">'
           f'<span class="credit">{_cr}</span></div>') if _im else ""
    return f"""<section class="page cv cv4 ctp">{art}{COVER_TOP}
<div class="mid"><span class="pill">CONTACT</span>
<h1 class="cvx">단지가 끝날 때까지,<br><em>끝까지 함께하겠습니다.</em></h1>
<div class="gbar"></div>
<div class="contacts">
<div><b>1533-3210</b><span>본사 대표번호 · 주관 콜센터</span></div>
<div><b>010-3345-6107</b><span>대표이사 직통</span></div>
<div><b>010-7273-9901</b><span>주관사업 총괄 본부장</span></div>
<div class="me"><b>edgecompany1@naver.com</b><span>이메일</span></div>
</div>
<div class="addr"><b>울산 본사</b> {D.ADDRESS}<br><b>지역 거점</b> 경인 평택 비전동 866-3(상설 쇼룸 · 입예협 회의 공간) · 청주 흥덕구 직지대로 642(상설 쇼룸) · 협력 네트워크 9곳<br>
<b>콜센터</b> 평일 09:00 ~ 18:00 · 온라인 365일 접수 · 24시간 이내 회신<br>
<b>등록 · 인증</b> {D.ELEC_LICENSE} · ISO 9001 / 14001 / 45001<br><b>제휴</b> 삼성 측 업무제휴 · 세스코 MOU</div>
</div>
<div class="bt"><span>입주박람회 주관사 제안서 · {D.SITE['name']}</span><span>주식회사 엣지컴퍼니</span></div>
</section>"""


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
               f"{D.SITE['sale_label']} {hh:,}세대 × {D.FUND}만원 상당 = <em>{won(n)} 상당</em>(부가세 포함)")


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
    # 재검증 10-14: 14,500 → 9,450원(본부장 확정 가격)은 34.8% 할인 → '약 35%'(가격은 그대로)
    s = sub(s, '<div class="lb">STANDARD</div><div class="big">35<small>% 할인</small></div>',
            '<div class="lb">STANDARD</div><div class="big"><small class="mx">약</small>35<small>% 할인</small></div>')
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
             ("최저가 차액 10배 보상", "온라인·시공 품목 제외 · 단가표 사전 공개 · 현장 가격 변경 없음"),
             ("48시간 하자보수 · 무상 A/S 최소 2년", "업체·품목별 기간 상이 · 주관 창구 A/S 종결까지 · 접수 365일 · 24시간 내 회신"),
             ("경관조명 컨설팅 · 설계 · 생산 · 직접시공", "전기공사업 면허 기반 직접 시공 · KC 인증 제품")]
    its = "".join(f'<div class="it"><div class="no">{i:02d}</div><div><b>{B.html.escape(a)}</b><p>{B.html.escape(b)}</p></div></div>'
                  for i, (a, b) in enumerate(items, 1))
    return B.render_std(no, sec, "엣지컴퍼니가 [[약속드리는 것]]", "제안서에 쓴 것은 전부 협약서와 증빙으로 남깁니다.",
                        f'<div class="cl">{its}</div>', ("확정된 약속은 [[협약서에 그대로 옮겨]] 끝까지 이행하겠습니다.", "‘(안)’ 항목은 참여업체 확정 후 입예협 승인으로 협약서에 반영"))


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

# 본부장 10-15(분당): p24 '한 신도시' 막대 + p25 '사송 · 에코델타 단지별 주관 현황' 조감 사진 → 1쪽. 수도권 입예협에겐 지역 자체보다
# '한 신도시의 여러 단지를 연속으로 맡은 운영 체력'이 메시지 — 사진은 카드 위 작은 띠로만. 압축본(compact.py)도 이 1쪽을 그대로 쓴다.
T_CITY = "한 신도시의 여러 단지를 [[연속으로]] 맡았습니다"
if not os.environ.get("NO_NATIVE"):
    _ct = [i for i, (_, kw) in enumerate(B.PAGES) if kw.get("title") == "한 단지가 아니라 [[한 신도시]]를 맡습니다"]
    _ph = [i for i, (_, kw) in enumerate(B.PAGES) if kw.get("title") == "[[사송 · 에코델타]] 단지별 주관 현황"]
    assert len(_ct) == 1 and len(_ph) == 1 and _ph[0] == _ct[0] + 1, ("신도시 2쪽 합치기 — 위치 확인", _ct, _ph)
    _kw = B.PAGES[_ct[0]][1]
    _imgs = iter([("g13_sasong_u", "양산 사송신도시 · 조감"), ("g13_eco_u", "부산 에코델타시티 · 조감")])
    _body, _n = re.subn(r'<div><div class="dn">',
                        lambda m: (lambda im: f'<div><div class="cph"><img src="assets_ins/{im[0]}.jpg" alt=""><span>{im[1]}</span></div><div class="dn">')(next(_imgs)),
                        _kw["body"])
    assert _n == 2, _n
    _kw.update(title=T_CITY, body=_body.replace('<div class="ct2">', '<div class="ct2 cm">'),
               lead="양산 사송 5개 단지 · 부산 에코델타 5개 단지 - 같은 신도시에서 단지를 이어 맡으며 운영을 다듬었습니다.",
               kp=("한 신도시의 여러 단지를 연속으로 맡아 온 [[운영 체력]]입니다.", "사진은 각 신도시 조감 이미지 · 단지명은 정식 명칭을 줄여 표기"))
    del B.PAGES[_ph[0]]
    B.CSS += (".ct2.cm>div{grid-template-rows:auto 1fr;padding:14px 22px 18px;row-gap:14px;align-items:center}"
              ".ct2.cm .cph{grid-column:1/-1;position:relative;height:150px;border-radius:10px;overflow:hidden;border:1px solid var(--line)}"
              ".ct2.cm .cph img{width:100%;height:100%;object-fit:cover;display:block;opacity:.9}"
              ".ct2.cm .cph span{position:absolute;left:10px;bottom:8px;font-size:11.5px;color:#fff;background:rgba(11,26,45,.72);border-radius:99px;padding:3px 10px}"
              ".ct2.cm .hb{margin-bottom:9px}.ct2.cm .sb2{margin-bottom:12px}")


def p_toc_bd(no):
    """목차 아래 띠: 공고 제안서 주요내용 대응표 쪽(평가위원이 목차에서 바로 찾도록)."""
    s = p_toc(no)
    band = (f'<div class="kp"><b>KEY POINT</b><span>공고 업무 ①~⑤ · 참가 자격 대응표 · <em>{PG("map")}</em>'
            f'<small>① 시공 단계 · 전문인력 {PGS(["c1", "c4"])} · 참가 자격 · 이해관계 · 유의사항 {PGS(["qual", "conf", "note"])}</small></span></div>')
    return sub(s, '<div class="ft">', band + '\n<div class="ft">')


B.p_toc = p_toc_bd


# 07장 간지 — 단지 이미지 슬롯(data.IMG['div07'])이 있으면 오른쪽 배경으로(없으면 기본 단색 간지)
B_p_divider = B.p_divider


def p_divider_os(n, title, bl):
    s = B_p_divider(n, title, bl)
    im, _own = slot("div07")
    if n != "07" or not im:
        return s
    art = (f'<div class="dvim"><img src="assets_ins/{im}.jpg" alt=""><div class="vl"></div>'
           f'<span class="cap">{D.LX_CAP}</span></div>')
    return sub(s, '<section class="page dv">', '<section class="page dv dvo">' + art)


B.p_divider = p_divider_os
B.CSS += (".dvo>*{position:relative;z-index:1}.dvo>.dvim{position:absolute;z-index:0;top:0;right:0;bottom:0;width:58%}"
          ".dvim img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:60% 50%}"
          ".dvim .vl{position:absolute;inset:0;background:linear-gradient(90deg,var(--bg) 0%,rgba(13,30,51,.82) 22%,rgba(13,30,51,.25) 55%,rgba(13,30,51,0) 80%)}"
          ".dvim .cap{position:absolute;right:24px;bottom:18px;font-size:10.5px;color:rgba(255,255,255,.6)}"
          ".dvo h2{font-size:42px;max-width:66%}.dvo .bl{max-width:60%}")

# 압축본(--compact) — reorg.apply → vis.apply 가 끝난 최종 B.PAGES에서 뺀다(vis가 빠질 장 제목을 take()하므로 그 뒤에).
# 뺄 장 · 합칠 장 · 문구 수정은 모두 compact.py 한 곳에 있다. 기본(전체본 134쪽)은 이 단계를 건너뛴다.
# 오산: 뺄 장은 reorg.py drop 목록에서 한 번에 정한다(약 105쪽) — compact 단계 없음

# ============================================================ 재검증 2차(10-14 밤) — 제목 · 띠 표현
# reorg · vis · compact가 제목으로 장을 찾으므로 그 뒤(최종 B.PAGES)에서 바꾼다.
# - 67개 단지 · 56,361세대 = 수임 누계(전신 실적 · 2027 입주 예정 7곳 포함) → '주관'이라 부르지 않음(주관 실적 = 1,000세대 이상 10개 단지)
# - '사옥' = 자가 건물로 읽힘(NICE 사업장 현황은 임차) → '본사 · 쇼룸'
# - 삼성 계약서 = '업무제휴 계약서'(MOU 아님 · 상대방 판독 불확실) → '삼성 측 업무제휴'
RETITLE = {"해마다 쌓이는 [[누적 주관 단지]]": "해마다 쌓이는 [[누적 수임 단지]]",
           "[[대단지]] 운영 경험": "1,000세대 이상 [[주관 단지]]",  # 오산 433세대 — '대단지' 강조 대신 실적 그대로
           "[[본사 사옥]] 운영 · 자본금 2억": "[[본사 · 쇼룸]] 운영 · 자본금 2억",
           # 본부장 10-15: 정회원 혜택도 세대당 15만원 상당 범위 안에서 배분 — '추가 혜택'은 따로 더 주는 것으로 읽힘
           "정회원 전용 [[추가 혜택]] (안)": "정회원 전용 [[혜택]] (안)"}
RELABEL = {"본사 사옥 · 자본금 2억": "본사 · 쇼룸 · 자본금 2억", "삼성전자 MOU · ISO 3종": "삼성 측 업무제휴 · ISO 3종"}
if not os.environ.get("NO_NATIVE"):
    _hit = set()
    for _k, _kw in B.PAGES:
        if _kw.get("title") in RETITLE:
            _hit.add(_kw["title"])
            _kw["title"] = RETITLE[_kw["title"]]
        if _kw.get("bl"):
            _hit.update(x for x in _kw["bl"] if x in RELABEL)
            _kw["bl"] = [RELABEL.get(x, x) for x in _kw["bl"]]
    if FULL:
        assert _hit == set(RETITLE) | set(RELABEL), ("재검증 2차 — 바꿀 제목 · 띠를 찾지 못함", (set(RETITLE) | set(RELABEL)) - _hit)
    assert not any(t in (kw.get("title") or "") for _, kw in B.PAGES for t in ("누적 주관", "본사 사옥")), "제목에 '누적 주관' · '본사 사옥'이 남음"

# 본부장 10-15 밤: 데이터 막대(그래프)는 그라데이션 없이 단색 — Chrome PDF는 linear-gradient를 셰이딩 패턴으로 쓰는데, 일부 뷰어(본부장 화면)에서
# 그 막대가 안 보임. 막대 · 띠만 단순 채움으로 덮어쓴다(카드 배경 · 사진 위 그늘 그라데이션은 그대로).
B.CSS += (".ct2 .hb .t i{background:#C8A86A}"
          ".tlb .c i{background:rgba(222,192,132,.8)}.tlb .c.mx i{background:#EBCB8F}"
          ".rw .bar.g{background:rgba(235,203,143,.35)}"
          ".pt3 .tr i.c{background:rgba(235,203,143,.2)}"
          ".qb .r.g i,.pv .r.g i{background:#C8A86A}"
          ".gnt .br.o{background:rgba(235,203,143,.14)}"
          ".stc i{background:#C8A86A}"
          ".bars .b{background:#C8A86A}")

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
    # 본부장 10-15 밤: 조직 구성 쪽 KEY POINT — '박람회 현장 운영 인력 약 21명 …'은 줄을 바꿔 다음 문단으로(문구 그대로)
    assert doc.count("<small>박람회 현장 운영 인력 약 21명") == (0 if "요약제안서" in path else 1), "조직 구성 쪽 KEY POINT 소문구를 찾지 못함"
    doc = doc.replace("<small>박람회 현장 운영 인력 약 21명", '<small class="kpbr">박람회 현장 운영 인력 약 21명')
    doc = doc.replace("</style>", ".kp small.kpbr{display:block;margin-left:0;margin-top:3px}</style>", 1)
    if D.FUND != 15:  # 상주 · 북수원: 패키지 · 08장 문구의 '15만원'(고양 · 탕정 값)을 세대당 지원액으로
        _n15 = doc.count("15만원")
        doc = doc.replace("15만원", f"{D.FUND}만원")
        print(f"[15만원 → {D.FUND}만원] {_n15}곳")
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
    # 재검증 10-14: p90 9행을 정한 CRIME_SUBST 값을 남긴다 — docs_bd.py가 지금 data.py 값과 다르면 02를 제출본에 넣지 않음(다시 빌드 안내)
    doc = sub(doc, "</body>", ALIGN_JS + "</body>")
    # 다른 단지 잔재 검사(분당 · 지웰 · 동탄 · 철산 · 탕정) + 오산 공고에 없는 조항 · 보증 문구(본부장 10-15)
    _txt = re.sub(r"<style.*?</style>", "", doc, flags=re.S)
    _txt = re.sub(r"<[^>]+>", " ", _txt)
    _ok = ("LH 신혼희망타운 2차", "기장 신혼희망타운", "사송 LH 신혼희망타운 2차")
    for _o in _ok:
        _txt = _txt.replace(_o, "")
    left = re.findall(r".{0,14}(?:오산|세교|아테라|금호|벌음|433|segyoartera|고양|창릉|S-5BL|S5|759|이수건설|덕양|KINTEX|파주|서북권|LH|판교|금토|분당|퍼스트빌리지|성남|낙생|933|1,400|행복주택|신혼희망|"
                      r"지웰|양주|덕계|탕정|센터파크|철산|광명|조합|임예협|가산점|무효 7|자격 12|1차 심사 4|"
                      r"발전기금|단지발전|입예협 지정|공용물품|커뮤니티 집기|bd_|os_|gy_|화재 ·|배상책임보험 개최|입주 후 1년|공고 주요내용|참가자격 \d|별지 6|별지 5 서약|북수원|이목|더리체|1,744|theriche|대방건설|수원|화성권|지침서|별지 [1-5]|적격심사|제안참여규정|보증 만료|협약 범위|운영계획서).{0,10}", _txt)
    assert not left, left
    # 대응표 쪽 번호(⟪pg:키⟫) — emit()에서 재배치가 끝난 B.PAGES로 계산
    doc = re.sub(r"⟪pg:(\w+)⟫", lambda m: f"p.{PGNO[m.group(1)]:02d}", doc)
    doc = re.sub(r"⟪pgs:([\w,]+)⟫", lambda m: "p." + " · ".join(f"{n:02d}" for n in sorted({PGNO[k] for k in m.group(1).split(",")})), doc)
    assert "⟪" not in doc
    doc = re.sub(r"⟦(.*?)⟧", r'<mark class="todo">\1</mark>', doc)
    _todo = re.findall(r'<mark class="todo">(.*?)</mark>', doc)
    if _todo:
        print(f"[확인 필요 {len(_todo)}칸] " + " / ".join(dict.fromkeys(_todo)))
    if "--final" in sys.argv:
        assert not _todo, "제출본에는 '확인 필요' 칸이 없어야 합니다"
        assert not PH_MISSING, f"제출본에는 사진 자리표시가 없어야 합니다: {sorted(PH_MISSING)}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)


PH_LABEL = {"bd_cover": "조감도 자리", "bd_gate_night": "문주 경관조명 사진 자리", "bd_aerial_night": "단지 야간 경관 사진 자리",
            "bd_facade_night": "외벽 경관조명 사진 자리", "bd_plaza_night": "단지 조경 경관 사진 자리", "bd_garden_night": "조경 산책로 사진 자리"}
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
    src = sys.argv[sys.argv.index("--src") + 1] if "--src" in sys.argv else None
    render_full_pages(src)
    # 전체본(기본) = NAME.html/.pdf(메일용 mail_lite.py도 이 파일 기준) · 압축본(--compact) = NAME_압축본.html/.pdf
    # 기본(약 120쪽) = NAME.html/.pdf(메일용 · 제출서류 기준) · --full = NAME_전체본 · --compact = NAME_압축본
    out = (os.path.join(HERE, NAME + "_압축본.html") if COMPACT else os.path.join(HERE, NAME + "_전체본.html") if FULL else B.OUT_HTML)
    emit(list(B.PAGES), out, f"엣지컴퍼니 {D.SITE['name']} 입주박람회 주관사 제안서")
    print(f"상주 업무 수행 제안서 {len(B.PAGES)}쪽 → {out}")
    # 요약제안서 — 상주 공고 제출서류(5항 1 ~ 9)에 없음 → PT 참고용으로만 만든다(통합 PDF에 넣지 않음). 숫자 · 문구는 위 제안서와 같은 D · ST 값(summary_sj.py)
    if "--summary" in sys.argv and not COMPACT and not FULL:  # 상주: 요약제안서는 제출서류 밖 → 요청 시만
        import summary_sj  # noqa: E402
        summary_sj.emit_summary(globals())


if __name__ == "__main__":
    build()
