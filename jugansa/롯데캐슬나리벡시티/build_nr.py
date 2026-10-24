# -*- coding: utf-8 -*-
"""고양창릉 S-5BL — 입주박람회 주관사 입찰제안서 빌더(입예협 공고 · '입주박람회 주관사 제안서' · PDF + 제출서류 폴더별 ZIP).

오산세교아테라 빌더(../오산세교아테라/build_os.py, 10-17 최신)를 복제·개조했다. 기본틀(요약제안서 v5, ../요약제안서/build.py)은
건드리지 않고 불러와서 고친다. 다른 단지 폴더는 읽기만 한다.
- 표지: 고양창릉 S-5BL 입주박람회 주관사 제안서 (이미지 = data.IMG 슬롯 — 본부장 제공 주간 조감도)
- 07장 = 고양 맞춤: 공고 '제안서 주요내용' 11개 대응표 · 단지 이해 · 실적 · 신뢰 · 품질 · 직영 · 가격경쟁력 · 품목 · 업체 ·
  A/S · 특화(경관조명 2쪽) · 월별 타임테이블 2쪽 · 안전 · 전담 · 개인정보 · 참가자격 7 · 참가 제한 10 · 선정 절차 · 주의사항
- 발전지원 = 세대당 15만원 상당 혜택 패키지(759세대 · 1억 1,385만원 상당) · A · B · C는 예시, 입예협이 골라서(본부장 10-17)
- 놀이터 경관 이미지는 가상 연출(실제 단지 놀이터 아님 · 본부장 10-17) — 캡션에 그대로 적는다.

사용: python3 build_gy.py [--no-pdf] [--final] → 엣지컴퍼니_롯데캐슬나리벡시티_입주박람회_주관사_제안서.html/.pdf
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

NAME = "엣지컴퍼니_롯데캐슬나리벡시티_입주박람회_주관사_제안서"
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
.hero3 b small.mxs{font-size:17px;margin:0 7px 0 0;color:var(--gold2)}
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
/* 본부장 10-24: 표지 · 마지막 장 사진을 줄여 단지 경관이 더 보이게(원본 1274px 확대로 흐림 → 축소 + 선명화본) */
.cv4:not(.ctp)>.cvart.cvx.day{top:auto;bottom:56px;height:640px;width:64%}.cv4:not(.ctp)>.cvart.cvx.day .credit{bottom:66px}.cv4:not(.ctp)>.cvart.cvx.day img{object-position:55% 60%}
.ctp>.cvart.cvx{top:auto;height:610px;width:60%}
.cv4:not(.ctp)>.cvart.cvx.day:after{background:linear-gradient(90deg,#0D1E33 0%,rgba(13,30,51,.78) 10%,rgba(13,30,51,.3) 24%,rgba(13,30,51,0) 38%),linear-gradient(180deg,#0D1E33 0%,rgba(13,30,51,.75) 9%,rgba(13,30,51,.25) 22%,rgba(13,30,51,0) 34%,rgba(13,30,51,0) 70%,rgba(13,30,51,.75) 88%,#0D1E33 100%)!important}
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


# ============================================================ 01장 신설 — 고양창릉 S-5BL 맞춤 제안 (재배치 후 07장)
# 근거: 고양창릉 S-5BL 입예협 '입주박람회 주관사 입찰공고'(10-17본) — 심사 및 선정절차(1차 서류 · 2차 PT · 우선협상 30일 계약) ·
# 입찰 참가자격 7 · 제안서 주요내용 11 · 입찰 참가 제한 10 · 필수 제출서류 · 주의사항 + 서식(별지 1 ~ 6) + 확인된 단지 사실(data.py).
# → 확인된 사실과 이행할 수 있는 약속만 쓴다(참가 제한 8 허위사실). 공고에 번호가 없어 '공고 ◆ 항목명 + 순번'으로 가리킨다.
S0 = "01. 고양창릉 S-5BL 맞춤 제안"
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
        return alt, alt.startswith("nr_")  # 나리벡: gy_ · tj_ 대체 이미지는 타 단지 연출 예시(단지 이미지 아님)
    return None, False


ST = D.SITE
_rec_n, _rec_hh = len(D.RECORDS), sum(r[3] for r in D.RECORDS)
R3 = D.RECENT3_OS
_r3_n, _r3_hh = len(R3), sum(r[3] for r in R3)
R5 = D.RECENT3_500  # 최근 3년 500세대 이상 입주박람회 진행 20개 단지(주관 16 = 1,000세대 이상 8 + 주관사 협약서 3 + 500 ~ 999세대 9 · 본부장 10-19 모두 주관)
_r5_n, _r5_hh = len(R5), sum(r[2] for r in R5)
_types_txt = " · ".join(a for a, _ in ST["types"])
_types_full = " · ".join(f"{a} {n}" for a, n in ST["types"])

T_DIV = f"{ST['name']}을 위한 [[맞춤 제안]]"
T_MAP = "공고 제안서 [[주요내용 11개]], 이 쪽에 있습니다"
T_SITE = f"{ST['name']}, [[이런 단지]]입니다"
T_FIRST = "759세대 공공분양이라 [[먼저 챙길 것]]"
T_VOICE = "입주예정자가 먼저 묻는 [[다섯 가지]]"
T_FIT = "운영 실적 · 연혁 · [[기업신용평가]]"
T_R500 = f"최근 3년 500세대 이상 입주박람회 [[주관 {_r5_n}개 단지]]"
T_TRUST = "계약 이행 · [[하자 이행]]을 약속하는 장치"
T_STABLE = "브랜드 품질 · [[무상보증기간]]"
T_FACT = "직영 운영 · [[온 · 오프라인 투명 운영]]"
T_CHECK = "공동구매 가격경쟁력 - [[검수하고, 보상합니다]]"
T_ITEMS = "759세대 맞춤 [[품목 구성]] (안)"
T_VENDORS = "품목별 [[예상 참가 업체]]"
T_VMGT = "입점 업체, [[계약부터 설치까지]] 관리합니다"
T_REQ = "LH · 시공사 협의와 현안, [[관리표로]] 끝까지 챙깁니다"
T_AS = "A/S 정책 - 주관사 [[한 창구]], 업체 부담은 늘리지 않습니다"
T_DEFECT = "하자 접수, [[책임부터]] 나눕니다"
T_SPECIAL = f"{ST['short']} [[특화 제안]]"
T_LX = "단지 외부 경관조명, [[입주 전에]] 진단합니다"
T_MON1 = "월별 업무 타임테이블 ① [[2026.10 ~ 2027.06]]"
T_MON2 = "월별 업무 타임테이블 ② [[2027.07 ~ 입주 완료]]"
T_PM = "본사는 울산, 대응은 [[고양 현장]]에서"
T_STAFF = "입예협 [[전담 체계]] - 운영 인원 12명"
T_PRIV = "입주민 개인정보는 [[행사 운영에만]] 씁니다"
T_REPORT = "보고는 [[항목과 시점]]을 정해 둡니다"
T_EXPO = "입주박람회 [[운영 계획]]"
T_SAFE = "행사장 [[안전 · 현장관리]] 계획"
T_QUAL = "입찰 참가자격 [[7개 항목]] 대응"
T_LIMIT = "입찰 참가 제한 [[10개 사유]] 확인"
T_NOTE = "선정 절차 · 주의사항, [[그대로 지킵니다]]"
T_PEOPLE = "대표자 · 핵심 운영인력 [[수행 경험]]"
T_HIST = "엣지컴퍼니 [[연혁]] · 주요 이력"
T_CPL = "입주민 [[컴플레인]], 이렇게 해결합니다"
T_CORE6 = f"{ST['short']}에 드리는 [[핵심 제안 6가지]]"
T_FUNDCH = f"세대당 {D.FUND}만원 상당 세대 혜택, [[입예협이 골라서]] 받습니다"  # 법정 10-23: '발전지원금'은 협의회 현금으로 읽힘


# ------------------------------------------------------------ 공고 '제안서 주요내용' 11개 ↔ 쪽 대응표(맞춤 장 첫머리)
MAP11 = [  # (순번, 공고 제안서 주요내용, 엣지컴퍼니 제안 핵심, [PGREF 키])
    ("01", "입주박람회 개최 및 운영계획", f"{ST['expo']} 주말 포함 2 ~ 3일(안) · 월별 타임테이블 · 결과보고서", ["expo", "mon1", "mon2", "report"]),
    ("02", "행사장 선정 및 운영계획", "행사장 후보 3곳(KINTEX 우선 검토) · 대관 · 배치 · 편의시설", ["expo", "venue", "floor"]),
    ("03", "참가업체 모집 및 품목별 구성계획", "수요조사로 품목 · 업체 수 결정 · 공개 입찰 공고 · 예상 참가 업체", ["items", "vendors", "screen"]),
    ("04", "공동구매 가격경쟁력 및 입주민 혜택 제공방안", "시중가 · 온라인 최저가 검수 · 차액 10배 · 세대당 15만원 상당 패키지", ["check", "x10", "guard4", "fund"]),
    ("05", "참가업체 선정기준 및 입점업체 관리방안", "4단계 공개 심사 · 특약이행각서 · 계약~설치 관리표 · 패널티", ["screen", "vmgt", "wty"]),
    ("06", "행사 홍보 및 입주민 참여방안", "카페 콘텐츠(입예협 승인 후 게시) · 온라인 박람회 · 카카오 상담", ["cafe", "online"]),
    ("07", "행사장 안전 및 현장관리계획", "동선 · 대피 · 전기 점검 · 미아 방지 · 응급 · 배상책임보험", ["safe", "floor"]),
    ("08", "계약업체 및 입주민 민원관리 방안", "주관 콜센터 한 창구 · 24시간 회신 · 선보상 · 컴플레인 처리 기준", ["call", "cpl", "defect"]),
    ("09", "A/S 및 사후관리계획", "48시간 하자보수 원칙 · 무상 A/S 최소 2년 · 입주 후 1년 관리", ["as", "wty", "rule1"]),
    ("10", "타 단지와 차별화되는 운영방안", "직영 조명 · 커튼 · 전기공사업 등록 업체 · 경관조명 진단", ["special", "lx", "lx2"]),
    ("11", "기타 입주민을 위한 제안사항", "LH · 시공사 협의 지원 · 개인정보 보호 · 혜택 항목은 입예협이 선택", ["req", "priv", "fund"]),
]
B.CSS += (".tbl.m9 td{padding:7px 12px;font-size:14px;line-height:1.3}.tbl.m9 td.k{font-size:15px;width:31%}"
          ".tbl.m9 td.n{width:48px;white-space:nowrap;font-size:13.5px}"
          ".tbl.m9 td.pg{white-space:nowrap;color:var(--gold);font-weight:800;font-size:14px;font-variant-numeric:tabular-nums;width:19%}")

# ------------------------------------------------------------ 단지 이해
_site_img, _site_own = slot("site")


# 10-22 착수 분석(카페 인사이트 · 공개 보도 기준 — 카페 글 집계 아님): 입주예정자 관심사 5 → 우리 답 · 쪽(본부장 '분석 결과로 제안서에 반영')
#  시공사 이력 · 하자는 언급하지 않는다(공개 근거 없음 · 단정 금지)
VOICE = [
    ("01", "하자 · 안전", "사전점검 동행 · 체크리스트 · 하자 접수 · 처리 추적까지 돕습니다. 시공사 하자 책임을 대신 약속하지 않고, 입예협 · 법무 대리인과 역할을 나눕니다.", ["defect", "pre1", "pre2"]),
    ("02", "유상옵션과 실제 시공", "LH 유상옵션(중문 · 붙박이장 · 시스템에어컨 · 인덕션 · 간접조명)과 겹치는 품목은 권하지 않고, 사전점검 때 모집공고 옵션표와 실제 설치를 대조하는 점검표를 드립니다.", ["pre1", "pre2"]),
    ("03", "분양가 · 자금 부담", "현장 가격 변경 없음 · 시중가 · 온라인 최저가 비교자료 · 계약금 5% 상한(맞춤 제작 품목 예외) · 카드 · 현금 동일가 · 설치 · 철거 · 배송을 포함한 확정 견적으로 추가 비용을 막습니다.", ["check", "x10", "rule1"]),
    ("04", "입주 초기 일정 · 교통 공백", "입주 · 사전점검 일정이 바뀌면 시공 · 배송 일정을 위약금 없이 다시 잡고, 입주 지정기간 단지 안 상주 창구(협의)와 고양 · 파주권 시공업체로 대응합니다.", ["mon2", "pm"]),
    ("05", "업체 잠적 · A/S", "참여업체 명단(상호 · 사업자등록번호 · 품목)을 카페에 공개하고, 4단계 공개 심사 · 이행보증 · 예치금 · 업체 도산 시 동종업체 이관(비용 주관사 부담)으로 지킵니다.", ["screen", "bond", "defect"]),
]
B.CSS += ".tbl.vc5 td{padding:10px 12px !important;font-size:15px !important;line-height:1.45}.tbl.vc5 td.k{width:15%;font-size:16px !important}.tbl.vc5 td:last-child{width:13%;font-size:13.5px}"

# ------------------------------------------------------------ 심사 1 · 적합성
_r3_rows = "".join(f'<tr><td class="n">{d}</td><td class="k">{t(nm)}</td><td class="r">{n:,}</td></tr>' for d, nm, _, n in R3)
_half5 = (len(R5) + 1) // 2


def _r5tb(rows, s0):
    return ('<table class="r5"><thead><tr><th>NO</th><th>입주</th><th>단지</th><th>세대</th><th>구분</th></tr></thead><tbody>'
            + "".join(f'<tr{" class=jg" if j else ""}><td class="n">{i:02d}</td><td class="m">{m}</td><td class="k">{t(nm)}</td>'
                      f'<td class="r">{n:,}</td><td class="g">주관</td></tr>' for i, (m, nm, n, j) in enumerate(rows, s0))
            + '</tbody></table>')


new("std", sec=S0, title=T_R500,
    lead="공고 제출서류 03(최근 3년간 실적 증명서) - 최근 3년(입주 2023.10 ~ 2026.12) 500세대 이상 공동주택 중 당사가 입주박람회를 주관한 단지입니다. 2027년 입주 예정 단지는 넣지 않았습니다.",
    body=('<div class="nb"><div class="r5x">' + _r5tb(R5[:_half5], 1) + _r5tb(R5[_half5:], _half5 + 1) + '</div>'
          '<div class="r5b">'
          f'<div><b>{_r5_n}<small>개 단지</small></b><span>500세대 이상 입주박람회 주관</span></div>'
          f'<div><b>{_r5_hh:,}<small>세대</small></b><span>{_r5_n}개 단지 세대 합계</span></div>'
          f'<div><b>{_r3_n}<small>개 단지</small></b><span>그중 1,000세대 이상 · 나머지 {len(R5) - _r3_n}개 단지는 500 ~ 999세대</span></div>'
          f'<div><b>{D._EV_N}<small>개 단지</small></b><span>증빙 첨부(NICE · 확약서 · 협약서 · 행사일정) · 나머지 요청 시 제출</span></div>'
          '</div></div>'),
    kp=(f"최근 3년 500세대 이상 [[{_r5_n}개 단지]]에서 입주박람회를 주관했습니다.",
        "단지명 · 세대수는 당사 실적 목록 기준 · 날짜는 입주 연월 · 실적 증명 · 협약서 · 행사일정 등 증빙은 제출서류 03"))
B.CSS += (".r5x{display:grid;grid-template-columns:1fr 1fr;gap:22px;flex:1;min-height:0}"
          ".r5{width:100%;border-collapse:collapse}"
          ".r5 th{font-size:11.5px;font-weight:700;letter-spacing:.16em;color:var(--gold2);text-align:left;padding:0 8px 7px;border-bottom:1.5px solid rgba(200,168,106,.55)}"
          ".r5 td{font-size:14.5px;padding:6.5px 8px;border-bottom:1px dashed rgba(255,255,255,.12);color:var(--sub)}"
          ".r5 td.n{width:34px;color:var(--mute);font-size:12.5px}.r5 td.m{width:72px;font-variant-numeric:tabular-nums}"
          ".r5 td.k{color:var(--ink);font-weight:600}.r5 td.r{text-align:right;font-variant-numeric:tabular-nums;color:var(--ink);white-space:nowrap}"
          ".r5 td.g{width:46px;text-align:center;font-size:12px}"
          ".r5 tr.jg td.k,.r5 tr.jg td.r,.r5 tr.jg td.g{color:var(--gold);font-weight:700}"
          ".r5b{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid rgba(200,168,106,.5);border-radius:12px;background:rgba(235,203,143,.05)}"
          ".r5b>div{padding:9px 16px;border-left:1px solid rgba(200,168,106,.25)}.r5b>div:first-child{border-left:0}"
          ".r5b b{font-size:26px;font-weight:800;color:var(--gold);line-height:1.1;white-space:nowrap}.r5b b small{font-size:13px;margin-left:2px}"
          ".r5b span{display:block;font-size:12.5px;color:var(--sub);margin-top:2px}")
B.CSS += (".fitx{display:grid;grid-template-columns:1fr 1.35fr 1fr;gap:16px;flex:1;min-height:0}"
          ".fitx .fc{border:1px solid var(--line);border-top:2px solid var(--gold2);border-radius:14px;padding:14px 18px;display:flex;flex-direction:column;min-height:0;"
          "background:linear-gradient(180deg,rgba(235,203,143,.08),rgba(255,255,255,.01) 45%)}"
          ".fitx i{font-style:normal;font-size:12px;letter-spacing:.14em;color:var(--gold2);font-weight:700}"
          ".fitx h3{font-size:25px;font-weight:800;color:var(--gold);margin:2px 0 10px}"
          ".fitx ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:12px;flex:1}"
          ".fitx li{font-size:15px;line-height:1.4;color:var(--sub);display:grid;grid-template-columns:88px 1fr;gap:8px}.fitx li b{color:var(--ink)}"
          ".fitx p{margin-top:auto;padding-top:8px;border-top:1px dashed rgba(200,168,106,.45);font-size:12.5px;color:var(--mute);line-height:1.45}"
          ".fitx .r3{width:100%;border-collapse:collapse;margin-bottom:8px}"
          ".fitx .r3 td{font-size:14px;padding:5px 6px;border-bottom:1px dashed rgba(255,255,255,.12);color:var(--sub)}"
          ".fitx .r3 td.n{width:70px;color:var(--gold2);font-variant-numeric:tabular-nums}.fitx .r3 td.k{color:var(--ink)}"
          ".fitx .r3 td.r{text-align:right;font-variant-numeric:tabular-nums;color:var(--ink);font-weight:700;white-space:nowrap}"
          ".fitx .r3 tfoot td{border-bottom:0;border-top:1.5px solid rgba(200,168,106,.55);color:var(--gold);font-weight:800;font-size:15px}")

# ------------------------------------------------------------ 심사 2 · 신뢰성

# ------------------------------------------------------------ 심사 3 · 안정성
STABLE = [  # (품목군, 브랜드 · 품질 확보 기준, 무상보증 기준)
    ("가전 · 시스템에어컨", "제조사 공식 판매점 · 정품 · [[모델코드 공개]]", "제조사 보증 기간 + 설치 하자는 설치 업체 보증"),
    ("조명 · 전기", "KC 인증 제품 · 전기공사업 등록 업체 시공", "계약서에 품목별 명시 · 최소 2년"),
    ("커튼 · 블라인드 · 전동", "타입별 실측 제작 · 원단 · 모터 사양 공개", "계약서에 품목별 명시 · 최소 2년"),
    ("가구 · 수납 · 중문", "브랜드 대리점 · 친환경 등급 서류 확인", "제조사 보증 + 설치 하자 최소 2년"),
    ("시공 품목", "청소 · 줄눈 · 탄성 · 방충망 · 필름 - 자재 사양 · 인증 서류 확인 · 인근 업체", "재시공 · 재방문 기준을 계약서에 명시"),
]
B.CSS += ".tbl.stb td{padding:12px 14px;font-size:15.5px}.tbl.stb td.k{width:21%}.tbl.stb td:last-child{width:32%;color:var(--gold)}"

# ------------------------------------------------------------ 심사 4 · 사실성

# ------------------------------------------------------------ 가산점 1 · 최저가 보상
CHECK5 = [("STEP 01", "단가 제출", "모델코드 · 규격 · 설치 · 철거 · 배송 · A/S 포함 여부"),
          ("STEP 02", "시중가 조사", f"{ST['local']} 오프라인 매장 2곳 이상 견적서"),
          ("STEP 03", "온라인 최저가", "같은 모델 최저 총액 · 조사일 · 화면 캡처 보관"),
          ("STEP 04", "입예협 검수", "비교표 제출 · 입예협이 품목을 골라 직접 확인"),
          ("STEP 05", "공개 · 보상", "박람회 전 카페 공개 · 계약 후 최저가 차액 10배")]

# ------------------------------------------------------------ 품목 · 업체
ITEMS = [  # (묶음, 대상, [품목], 기준)
    ("공간 맞춤", "타입별 실측", ["커튼 · 블라인드 (타입별 실측 제작)", "수납 · 선반 · 가구", "실링팬 (천장 보강 확인 후)"], "타입별 표준 견적표로 사이즈부터"),
    ("입주 준비", "모든 세대", ["입주청소 · 줄눈 · 새집증후군", "방충망(미세 · 안전) · 단열필름", "포장이사 · 사전점검 대행"], f"{ST['local']} 업체 우선 · 48시간 A/S"),
    ("생활 가전 · 렌탈", "필요 세대", ["가전 (빌트인 · 옵션 품목 제외)", "정수기 · 공기청정 렌탈", "생활 · 주방 소형 가전"], "유상옵션 · 기본 제공 품목과 겹치지 않는 것만"),
    ("조건부 시공", "LH 옵션 · 기본 제공 확인 후", ["시스템에어컨 · 인덕션 · 간접조명", "현관 중문 · 붙박이장 · 드레스룸", "탄성코트 · 욕실 환기 · 비데 교체"], "옵션 미선택 세대 · 남은 수요만 · 외부 시공 승인 확인"),
]


def _item_card(nm, who, its, rule):
    li = "".join(f"<li>{t(x)}</li>" for x in its)
    return f'<div class="itc"><i>{t(who)}</i><h3>{t(nm)}</h3><ul>{li}</ul><p>{t(rule)}</p></div>'




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
    kp=("주관사 직영 품목도 [[같은 심사 · 같은 단가 공개 · 같은 가격 보호 규정]] 적용 - 같은 품목에 다른 업체도 공개 입찰로 참여합니다.", "업체 수는 입예협 승인 · ‘참가 협의 중’은 확정 전 업체 · 일괄 도급 없음"))

VMGT = [  # (단계, 관리 방법, 기준)
    ("선정", "수요조사 → 공개 입찰공고 → 4단계 심사 → [[입예협 최종 컨펌]]", "품목별 업체 수는 입예협 승인 · 하청 금지"),
    ("계약", "표준 계약서에 취소·환불 규정 첨부 · 모델코드 · 포함 조건(설치·철거·배송·A/S) 명시", f"계약금 {D.DEPOSIT_MAX}% 이하(맞춤 제작 품목 예외) · 카드·현금 동일가"),
    ("일정", "세대별 상담 · 계약 · 납품 · 시공 · 설치 [[일정 관리표]] · 동별 일정 충돌 조정", "시공 가능 시점 · 관리사무소 신고 확인"),
    ("검수", "시공 · 설치 후 세대 확인 서명 → 잔금 · 해피콜", "하자 · 미시공은 보수 후 잔금"),
    ("평가", "박람회 후 업체별 민원 · A/S 처리 현황 집계 → 입예협 보고", "패널티 3단계 · 재참여 제한"),
    ("공정", "모든 참여업체에 균등한 기회 · 가격 담합 · 독점 유도 · 비방 금지", "참가 제한 2 담합 금지"),
]

# ------------------------------------------------------------ 가산점 4 · 시행 · 시공사 협의
REQ = [  # 예상 건의 유형 — 실제 항목은 입예협과 정한다
    ("품질 · 시공", "사전점검 하자 · 마감 · 설비 질의", "점검 체크리스트 반영 · LH · 시공사 질의서 · 품질 점검 자료", "회신 확보"),
    ("옵션 · 계약", "유상옵션 일정 · 조건 · 계약 안내", "LH 안내 정리 · 카페 안내 콘텐츠(입예협 승인)", "공지 게시"),
    ("입주 일정", "사전점검 · 입주지정기간 · 입주지원센터", "공문 작성 · 발송 지원 · 회신 일정 추적", "일정 공유"),
    ("생활 인프라", "교통 · 학교 · 상가 · 주변 공사 일정", "기관 발표 자료 확인 · 질의 공문 작성 지원", "기관 회신 공유"),
]
B.CSS += (".gq3{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px}"
          ".gq3>div{border:1px solid var(--line);border-radius:11px;padding:12px 16px;display:flex;flex-direction:column;gap:4px}"
          ".gq3 b{font-size:15px;color:var(--gold)}.gq3 span{font-size:14px;color:var(--sub);line-height:1.45}"
          ".tbl.sm.rq4 td{padding-top:15px;padding-bottom:15px}")

# ------------------------------------------------------------ 가산점 5 · A/S 정책
new("std", sec=S0, title=T_AS,
    lead="공고 업무범위 6) · 우대 17 ‘A/S 정책’ - 입주민은 주관사 한 창구로 접수하고, 참여업체에는 추가 비용 · 추가 인력을 요구하지 않는 구조로 운영합니다.",
    body=('<div class="nb"><div class="pmx">'
          '<div class="pc"><h3><i>POLICY</i>A/S 정책</h3>'
          + B.rows([
              ("접수", f"콜센터 {D.TEL}(평일) · 카페 신문고 · 카카오채널(365일)"),
              ("기한", "[[24시간 1차 회신]] · 48시간 하자보수 원칙"),
              ("기간", "시공 품목 무상 A/S 최소 2년(계약서 명시) · 주관 창구 입주 후 1년"),
              ("미응답", "주관사가 먼저 보상 · 업체와 나중에 정산"),
              ("기록", "접수 · 처리 · 지연 사유 기록 · 정례 보고"),
          ], title_w=86) + '</div>'
          '<div class="pc"><h3><i>NO EXTRA BURDEN</i>업체 부담을 늘리지 않는 제도</h3>'
          + B.rows([
              ("창구 비용", "콜센터 운영비는 [[주관사 부담]] - 업체별 상담 인력 요구 없음"),
              ("예치금", "하자 예치금은 주관사 자산 - [[업체 예치금 · 추가 보증금 없음]]"),
              ("보증 기간", "시공 품목 최소 2년(계약서 명시) · 브랜드는 제조사 보증 · 청소 등 용역은 재시공 기준"),
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

B.CSS += ".tbl.df4 td{padding:13px 14px}"

# ------------------------------------------------------------ 가산점 6 · 특화 제안

def _fig(key, cap, sub_, pos="50% 50%"):
    im, _own = slot(key)
    if not im:
        return ""
    return (f'<figure><img src="assets_ins/{im}.jpg" alt="" style="object-position:{pos}">'
            f'<figcaption>{cap}<small>{sub_}</small></figcaption></figure>')


T_LX2 = "단지 안 놀이터 · 운동시설 · 산책로, [[밤길까지]] 살핍니다"
B.CSS += (".lxo{display:grid;grid-template-columns:1.75fr 1fr;gap:18px;flex:1;min-height:0}"
          ".gal.lxa{grid-template-columns:1.25fr 1fr;grid-template-rows:1fr 1fr;gap:10px;min-height:0}"
          ".gal.lxa figure:first-child{grid-row:span 2}"
          ".gal.lxb{grid-template-columns:1fr;gap:12px;min-height:0}"
          ".lxo .gal figcaption{font-size:15px;padding:24px 12px 9px}.lxo .gal figcaption small{font-size:12px}"
          ".lxo .lxd{display:flex;flex-direction:column;justify-content:center;gap:12px;min-height:0}"
          ".lxo .lxd>div{border-left:2px solid var(--gold2);padding:2px 0 2px 14px}"
          ".lxo .lxd b{font-size:16.5px}.lxo .lxd p{font-size:14px;color:var(--sub);line-height:1.45;margin-top:3px}"
          ".lxo.s2{grid-template-columns:1.9fr 1fr}")

# ------------------------------------------------------------ 가산점 7 · 월별 타임테이블
MON = [  # (월, 주관사 업무, 입예협 보고 · 산출물)
    ("2026.10", "제안서 제출(10.25) · 1차 서류심사 · [[2차 PT - 실제 업무 책임자 발표]]", "제안 조건 = PT 조건"),
    ("2026.11", "우선협상 · 통보 후 30일 안에 계약 · 전담 PM 지정 · 카페 지원 시작", "계약서 · 연락 체계표"),
    ("2026.12", "정례회의 일정 확정 · [[건의 관리표]] 개설 · LH · 시공사 연락 창구 정리", "건의 관리표 1차"),
    ("2027.01 ~ 02", "품목 수요조사 설계(유상옵션 선택 여부 문항 포함) · 카페 안내 콘텐츠", "설문안 승인"),
    ("2027.03 ~ 04", "[[수요조사]] 실시 · 유상옵션 · 기본 제공 겹침 확인", "수요조사 결과 보고"),
    ("2027.05", "품목 · 품목당 업체 수 확정 · 참여업체 [[공개 입찰 공고]]", "입찰 공고안 승인"),
    ("2027.06", "업체 4단계 심사 · 입예협 최종 컨펌 · 특약이행각서 징구", "심사 결과 보고"),
    ("2027.07", "단가 제출 · 시중가 · 온라인 최저가 조사 · 외부 경관 현황 진단", "가격 비교표 초안 · 경관 진단 1장"),
    ("2027.08", "[[입예협 가격 검수]] · 행사장 대관 · 안전계획 · 타입별 표준 견적표", "검수 완료 단가표 · 안전계획"),
    ("2027.09", "단가표 카페 공개 · 홍보(카드뉴스 · 현수막 · 알림) · 배치도 확정", "공개 단가표 · 배치도"),
    ("2027.10 ~ 11", "[[입주박람회 2 ~ 3일(안)]] · 온라인 박람회 · 계약 세대 실측 · 일정 관리표", "박람회 결과보고서"),
    ("2027.11 ~ 12", "사전점검 지원(일정 확정 시) · 체크리스트 · 안내 부스 · 납품 · 시공 일정 조정", "사전점검 지원 결과"),
    ("2028.01", "[[입주]] · 시공 · 설치 · 세대 검수 서명 · 잔금 · 해피콜 · 공동구매 A/S 접수 · 건설 하자 전달", "입주 지원 결과"),
    ("입주 후 1년", "A/S · 하자 이행 관리 · 정기 보고 → 최종 결과 보고서", "최종 결과 보고서"),
]

def _mon(rows):
    return table(["월", "주관사 업무", "입예협 보고 · 산출물"], "".join(
        f'<tr><td class="k">{a}</td><td>{t(b)}</td><td>{t(c)}</td></tr>' for a, b, c in rows), "mon")


B.CSS += (".tbl.mon td{padding:14px 14px;font-size:15.5px;line-height:1.42}.tbl.mon td.k{width:15%;white-space:nowrap;font-variant-numeric:tabular-nums}"
          ".tbl.mon td:last-child{width:26%;color:var(--gold)}.tbl.mon tr:nth-child(odd) td{background:rgba(255,255,255,.025)}")

# ------------------------------------------------------------ 전담 · 운영
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


B.CSS += (".dcx{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;flex:1;min-height:0}"
          ".dcd{border:1px solid var(--line);border-top:2px solid var(--gold2);border-radius:14px;padding:14px 18px;background:linear-gradient(180deg,rgba(235,203,143,.08),rgba(255,255,255,.01) 40%);display:flex;flex-direction:column;gap:4px}"
          ".dcd i{font-style:normal;font-size:12px;font-weight:700;letter-spacing:.2em;color:var(--gold2)}"
          ".dcd h4{font-size:15px;color:var(--sub);font-weight:600}.dcd>b{font-size:21px;color:var(--gold);margin-bottom:4px}"
          ".dcd ul{list-style:none;margin:6px 0 0;padding:0;display:flex;flex-direction:column;gap:12px}"
          ".dcd li{font-size:15.5px;line-height:1.5;padding-left:14px;position:relative}.dcd li:before{content:'';position:absolute;left:0;top:8px;width:6px;height:6px;border-radius:50%;background:var(--gold2)}")


RPRIN = ('<div class="rprin">' + "".join(f'<div><b>{a}</b><p>{b}</p></div>' for a, b in [
    ("협의 ≠ 설치", "‘협의 완료’와 ‘설치 완료’를 나눠 표시"),
    ("지연은 사유와 함께", "지연 건은 사유 · 다음 일정을 같이 보고"),
    ("최소 정보", "입예협과 공유할 수 있는 범위로 집계"),
    ("원자료 열람", "입예협이 요청하면 근거 자료를 열람"),
]) + '</div>')
B.CSS += (".rprin{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:16px}.rprin div{border:1px solid rgba(200,168,106,.45);"
          "border-radius:12px;padding:12px 14px;background:rgba(235,203,143,.05)}.rprin b{display:block;font-size:16px;color:var(--gold)}"
          ".rprin p{font-size:13.5px;color:var(--sub);margin-top:4px;line-height:1.45}")


new("std", sec=S0, title=T_EXPO,
    lead="공고 업무범위 1) - 계약을 재촉하는 자리가 아니라, 가족이 함께 확인하고 비교하는 자리로 만듭니다.",
    body=B.tiles([
        dict(lb="WHEN", nm=f"{ST['expo']} 2 ~ 3일 (안)", ds="입주(2027.11) 3 ~ 2개월 전 · 일수 · 날짜는 사전점검 일정에 맞춰 입예협과 확정"),
        dict(lb="WHERE", nm="행사장 후보 3곳", ds="① " + ST["venues"][0] + " ② " + ST["venues"][1] + " ③ " + ST["venues"][2] + " - 입예협과 답사 후 확정"),
        dict(lb="SAFETY", nm="안전계획 · 배상책임보험", ds=f"동선 · 대피 · 전기 점검 · 미아 방지 · 응급 대응({PG('safe')}). 영업배상책임보험 가입(만료 전 갱신) · 박람회 기간 행사장 기준 행사주최자배상책임보험 가입 · 개장 전 증권 사본 제출."),
        dict(lb="FAMILY", nm="놀이방 · 휴게 · 수유실", ds="어린이 놀이방 · 수유실 · 유모차 대여와 입구 안내데스크 · 카페테리아를 둡니다."),
        dict(lb="ONLINE", nm="온라인 박람회 · 라이브", ds="단지 입주민만 들어오는 폐쇄몰. 박람회와 같은 공동구매가."),
        dict(lb="PR", nm="카페 · 공지채널 콘텐츠", ds="카드뉴스 · 영상 · 현수막 · 알림톡 - 게시 전 입예협 사전 승인을 받습니다."),
    ], cols=3, rows_n=2).replace('class="tiles"', 'class="tiles lg"'),
    kp="박람회장 가격 = 사전 공개 단가 - [[결제 방식과 관계없이]] 같습니다.")

SAFE = [  # 공고 주요내용 7 — (구분, 기준)
    ("동선 · 대피", "입구 체크인 → 품목 존 → 상담 → 휴게의 [[한 방향 동선]] · 비상구 · 대피로 표시 · 통로 폭 확보"),
    ("전기 · 화기", "부스 전기는 개장 전 [[전기공사업 등록 업체가 점검]] · 문어발 배선 금지 · 화기 · 가스 사용 금지"),
    ("어린이 · 미아", "놀이방 전담 인력 · 보호자 확인 팔찌 · 미아 발생 시 안내데스크 방송 · 출입구 확인"),
    ("응급 · 질병", "응급 키트 · AED 위치 안내 · 사내 간호사 자격 인력 배치 · 인근 병원 연락 체계"),
    ("인원 · 주차", "현장 운영 약 21명(주차 3 · 체크인 · 안내 5 포함) · 혼잡 시간 입장 조절 · 주차 안내"),
    ("업체 반입 · 철수", "부스 반입 · 철수 시간표 · 부스별 책임자 명찰 · 매일 개장 전 [[안전 점검표]] 서명"),
    ("보험", "영업배상책임보험 가입(증서 제출 · 만료 전 갱신) · 박람회 기간 행사장 기준 행사주최자배상책임보험 가입 · 개장 전 증권 사본 제출"),
]
new("std", sec=S0, title=T_SAFE,
    lead="공고 업무범위 1) · 3) - 행사장 안전과 현장관리 기준을 미리 정하고, 행사장이 확정되면 그 시설 기준에 맞춰 입예협과 최종 확정합니다.",
    body=B.rows([(a, b) for a, b in SAFE], title_w=170),
    kp=("안전은 [[개장 전 점검표]]로 매일 확인합니다.", "행사장 · 인원 · 보험 조건은 행사장 확정 후 입예협과 최종 확정 · 인원은 행사 규모에 따라 변동"))

# ------------------------------------------------------------ 공고 대응표(참가자격 7 · 참가 제한 10 · 선정 절차 · 주의사항)
QUAL7 = [  # (공고 입찰 참가자격, 엣지컴퍼니 현황, 증빙)
    ("사업자등록증상 행사기획 · 전시 · 이벤트 등 입주박람회 관련 사업", "종목 ‘전시, 박람회 및 행사 대행업’ · 등기 목적 ‘전시 박람회 사업 · 행사대행업 · 이벤트 기획 및 대행업’", "사업자등록증 · 등기부"),
    ("최근 3년 이내 500세대 이상 공동주택 입주박람회 주관 또는 운영실적", f"충족 · [[{_r5_n}개 단지]](최근 3년 500세대 이상 · {_r5_hh:,}세대 · 주관 {sum(1 for r in R5 if r[3])}) · 단지 목록 {PG('r500')}", "별지 2 · 협약서 · 수임 증빙"),
    ("행사 운영에 필요한 전문인력 및 현장관리 인력", f"임직원 14명(4대보험 정규직 13 + 인턴 1) · 4개 팀 {_n12}명 · 자격 · 협회 등록 인력(전기 3 · 도장 2 · 타일 1 · 조경 1 · 간호사 1)", "조직현황 · 4대보험 완납"),
    ("국세 및 지방세 체납 없음", "체납 없음 - 완납증명서 제출", "국세 · 지방세 완납"),
    ("계약 및 행사 진행에 필요한 보험 또는 보증 가입 가능", f"영업배상책임보험 가입(증서 제출) · 보증보험증권 발급 이력 {PG('bond')} · 계약이행보증보험은 선정 후 발급", "보험 증서 · 이행보증(선정 후)"),
    ("입주민 개인정보 보호 및 관리체계", f"수집 최소화 · 영업 이용 금지 · 제3자 제공 금지 · 참여업체 관리 · 파기 기준 {PG('priv')}", "제안서"),
    ("기업신용평가자료 또는 재무상태 확인 자료 제출", f"NICE 기업신용평가 BB- · 현금흐름 A · 부채비율 17.1%({D.NICE_DATE})", "신용평가서 상세내역"),
]
B.CSS += ".tbl.q10.q7g td{padding:12px 12px;font-size:15px}.tbl.q10.q7g td.k{font-size:15.5px}"

# 본부장 10-16: 분당 p78과 같은 '보증보험 · 예치금 이행 이력' 1쪽 — 오산은 금액을 넣지 않는다(증권 가입금액 · 예치 금액 모자이크, 글에도 없음)
T_BOND = "보증보험 · 예치금 [[이행 이력]]"
BOND_IMG = "assets_ins/os_sgi_bond_masked.png"   # SGI 계약보증보험증권 1쪽 — 상대방 · 보험료 · 증권번호 뒷자리 · 가입금액 가림(깃 제외)
ESCROW_IMG = "assets_ins/os_escrow.jpg"          # 에스크로(예치금) 약정서 — 단지명 · 날짜 · 금액 · 상대방 대표 · 연락처 · 계좌 가림(깃 제외)
def _bcard(tag, name, img, alt, rows):
    dl = "".join(f"<div><dt>{t(k)}</dt><dd>{t(v)}</dd></div>" for k, v in rows)
    return (f'<div class="cd"><div class="hdr"><i>{tag}</i><b>{t(name)}</b></div>'
            f'<div class="im"><img src="{img}" alt="{alt}"></div><dl>{dl}</dl></div>')
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

LIMIT10 = [  # 공고 입찰 참가 제한 1 ~ 10 — (사유, 확인, 근거)
    ("공정한 계약 이행 · 입찰 진행을 해칠 우려", "해당 없음 - 공고 · 서식 조건 그대로 제출", "제출서류"),
    ("특정 업체 선정을 위한 담합", "해당 없음 - 참여업체 공개 입찰 · 4단계 심사 · 입예협 최종 컨펌", "03장"),
    ("계약 · 선정 목적의 금품 · 향응 제공", "해당 없음 - 청렴계약 이행 준수 서약 · 문의는 접수처 이메일로만", "별지 4"),
    ("이행능력 심사 서류 미제출", "해당 없음 - 목록표대로 제출 · 범죄사실증명서는 서류심사 합격 시", "별지 6"),
    ("입찰 참가자격 미달", f"해당 없음 - 참가자격 7개 대응표 {PG('qual')}", "참가자격"),
    ("계약이행능력 검증 서류 누락", "해당 없음 - 신용평가서 · 완납증명서 · 영업배상책임보험 증서 제출", "제출서류"),
    ("불법 · 부정한 방법의 영업 · 입찰 참여", "해당 없음", "자체 확인"),
    ("제출서류 · 제안내용의 허위사실", "해당 없음 - 실적은 NICE 연혁 · 카페 공지 · BEXCO · 협약서로 증빙 · 미확정 혜택은 ‘(안)’", "별지 2 · 증빙"),
    ("타 단지 입주박람회 중대한 계약불이행", "해당 없음 - 협약 철회 · 계약 해지 이력 없음", "자체 확인"),
    ("타 업체 비방 · 입찰 진행 방해", "해당 없음 - 타 업체를 비교 · 비방하는 문구 없음", "제안서"),
]
B.CSS += ".tbl.q10.l7 td{padding:9px 12px !important;font-size:15px !important;line-height:1.4}.tbl.q10.l7 td.k{font-size:15.5px !important}.tbl.q10.l7 td:last-child{width:12%}"

NOTE7 = [  # 공고 심사 및 선정절차 · 주의사항 · 별지 5 — (공고, 약속)
    ("1차 서류심사", "제안서와 제출서류로 평가받습니다 - 유효기간 안의 발급본만 냅니다(미비 · 만료 시 감점 · 제외 유의)."),
    ("2차 PT", "계약 후 실제 업무를 맡을 책임자([[주관사업 총괄 본부장]])와 결정권자(대표이사)가 함께 나옵니다. 발표는 둘 중 한 명이 맡고 질의에는 둘이 함께 답하며, 제안 조건은 대표이사가 그 자리에서 확약합니다. 제출한 조건을 [[바꾸거나 더하지 않습니다.]]"),
    ("우선협상 · 계약", "선정 통보 후 30일 안에 계약을 맺고, 계약조건 협의가 안 되면 차순위 협상을 받아들입니다."),
    ("계약이행보증보험", "선정 후 협의회를 피보험자로 발급합니다. 보험기간은 입주 개시 1년 전 ~ 입주 개시 후 1년, 금액 · 발급 시점은 입주 일정에 맞춰 입예협과 확인하고 발급 즉시 증권을 제출합니다."),
    ("서류 · 이의 · 도급", "제출 서류는 돌려받지 않으며, 평가 · 선정 결과에 이의를 제기하지 않고 사업 전체를 일괄 도급하지 않습니다(별지 5)."),
    ("미선정 시", f"{ST['name']} 대상 별도 입주박람회 · 공동구매 행사를 열지 않습니다(별지 5)."),
    ("일정 변경 · 기타", "입주 · 사전점검 일정이 바뀌면 박람회 일정과 운영계획을 입예협과 협의해 조정하고, 명시되지 않은 사항은 입예협 결정을 따릅니다."),
]
B.CSS += ".tbl.nt7 td{padding:13px 14px;font-size:15.5px;line-height:1.45}.tbl.nt7 td.k{width:20%;font-size:16px;color:var(--ink);font-weight:700}"

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
    lead=f"공고 참가자격 1 · 2 - 법인 설립({D.FOUNDED})부터 지금까지, 등기부 · 등록증 · 인증서 · NICE 연혁 · 협약으로 확인되는 기록만 적었습니다.",
    body=f'<div class="nb"><div class="hist"><ol>{"".join(_items[:_half])}</ol><ol>{"".join(_items[_half:])}</ol></div></div>',
    kp=("2023년부터 [[해마다]] 1,000세대 이상 입주박람회를 맡아 왔습니다.",
        "날짜 = 박람회 개최 연월(NICE 연혁 기재) · 출처: 법인등기부 · 전기공사업 등록증 · ISO 인증서 · NICE 연혁 · 세스코 협약"))

_lead_n = getattr(D, "STAFF_LEAD", 2) + sum(c for _, c, _ in D.STAFF)
PRO5 = [("전기", 3), ("도장", 2), ("타일", 1), ("조경", 1), ("간호사", 1)]
new("std", sec=S0, title=T_PEOPLE,
    lead=f"공고 참가자격 4(정직원 5명 · 실행 인원 7인 이상) · 2차 제안설명회(PT) - 대표자와 핵심 운영인력이 맡아 온 실적과, {ST['name']}에서 맡을 역할입니다.",  # 본부장 10-15 밤: 이 쪽 단지 표기 = 정식 명칭
    # 대표 개인 경력(본부장 10-15) — NICE 기업신용평가보고서(제출서류 14 ③ 발췌) 13쪽 '대표자1' 약력 · 전기공사업 등록증 · ISO 인증서(3종 모두 최초 2025.08.12)로
    # 확인되는 사실만. 현장 총괄 문구는 본부장 10-15 확인. 경영경력 8년 8개월 = NICE 평가 당시(2026.05) 기재값.
    body=('<div class="nb"><div class="ppx">'
          '<div class="pp1 ceo"><i>대표이사</i><h3>고진식</h3><ul>'
          '<li>울산과학대학교 전기과</li>'
          '<li>대한유화 2011 ~ 2018(최종 대리) → 엣지조명 대표 2019 ~ 2021 → <b>㈜엣지컴퍼니 창업 2022.02</b></li>'
          f'<li>전기공사업 등록(제 울산-00821호) 대표자</li>'
          '<li>ISO 9001 · 14001 · 45001 인증 취득 총괄 - 첫 인증 2025.08.12 · 박람회 · 전시회 기획 · 대행 / 전기공사 / 조명공사</li>'
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
    kp=("대표 · 총괄 본부장 · 4개 팀이 협약부터 입주 후까지 [[한 팀으로]] 책임집니다.",
        "대표 약력은 NICE 보고서 13쪽(신용평가서) · 팀별 담당은 계약 시 명단 제출 · 실적 증빙은 제출서류 03(NICE 연혁 · 카페 공지 · BEXCO 행사일정 · 협약서)"))
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
                       "브랜드 본사가 계약 주체인 품목(본사 직영 가전·가구 등), 렌탈·보험·통신, 사전점검 대행은 각 본사 계약 규정을 따르되, 그 내용을 계약 전에 서면으로 고지하여야 한다."]),
    ("제3조 (계약금)", [f"계약금은 계약 총액의 <b>{D.DEPOSIT_MAX}% 이하</b>로 한다(계약금 {D.DEPOSIT_MAX}% 상한제). 다만 세대 실측 후 제작하는 맞춤 제작 품목({_CU} 등)은 예외로 하며, 적용 품목과 계약금은 업체 선정 때 입예협 승인을 받아 단가표 · 계약서에 미리 표시한다.",
                     "계약금과 잔금 모두 카드 결제 시 현금가와 <b>동일한 가격</b>을 적용하며(결제 방식에 따른 단가 변동 없음), 현금 결제 시 현금영수증을 발행한다."]),
    ("제4조 (잔금 지급 조건)", ["잔금은 <b>시공·설치가 끝나고 계약자가 확인한 후</b> 지급한다. 제품만 납품하는 품목은 납품·설치 확인 후 지급한다.",
                          "참여업체가 입찰 때 약속한 기대매출을 넘긴 경우의 실적 비례 추가할인은 잔금에서 차감한다. 품목별 할인율은 입예협과 검토해 정한다.",
                          "시공 결과 확인 시 하자·미시공 부분이 있으면 계약자는 해당 부분의 보수가 끝난 후 잔금을 지급할 수 있다."]),
    ("제5조 (취소·환불 기준)", ["품목별 취소 가능 기한은 [별표]와 같다. 기한 안에 취소하면 납부한 금액 <b>전액</b>을 환불한다.",
                          f"맞춤 제작 품목({_CU})은 출고 지시 전까지 참여업체와 협의하여 취소한다. 참여업체(대리점)가 계약 주체인 브랜드 가전·가구는 미제작·출고 지시 전에는 전액 취소·환불한다.",
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
                                  "참여업체가 도산한 경우 동종업체로 사후관리를 이관하고, 무상 A/S 기간 안의 A/S 비용은 주관사가 전액 부담한다.",
                                  # 재검증 10-14: 새 증권 한도(울주대리점)는 확인 전 — 금액은 협약 때 확정(08 방안서 4장 · p89와 같은 조건부)
                                  "주관사의 보상 재원으로 하자 예치금 최대 1억원(엣지컴퍼니 자산으로 예치)과 계약이행 · 하자보증보험(보증기간 24개월, 금액 · 기산일은 협약 때 확정)을 둔다."]),
    ("제8조 (가격 보호 — 최저가 차액 10배 보상)", [f"공동구매 품목과 브랜드·모델명이 같은 새 제품이 계약 후 7일 이내에 인근({ST['local']}) 오프라인 매장에서 더 낮은 정상 판매가로 실제 판매된 사실이 구매 영수증(판매 매장 사업자 정보 · 모델명 · 금액 기재)으로 확인되고 주관사가 해당 매장에 판매 사실을 확인하면, 주관사는 차액의 10배를 보상하고 참여업체는 판매가를 조정한다(보상금은 주관사 부담 · 참여업체 부담을 늘리지 않음).",
                                         "보상액은 1건당 50만원(해당 품목 계약금액이 더 적으면 그 금액)을 넘지 않으며, 최대 금액은 협약 시 입예협과 협의해 조정할 수 있다(같은 세대 · 같은 품목에는 1회). 견적서 · 가격표 · 구두 안내 가격은 보상 근거가 되지 않는다.",
                                         "온라인·홈쇼핑 판매, 시공 품목, 카드 청구할인·사은품·결합할인, 전시·리퍼 상품, 법인 특판, 한정 수량 행사가는 비교 대상에서 제외한다.",
                                         "계약자는 주관사 콜센터에 접수하고, 주관사는 사실 확인 후 7일 이내에 보상한다."]),
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
    lead="공고 참가자격 9) · 10) · 11) · 하자 보수 이행각서(별지 3) - 참여 품목별 계약 취소 및 환불 규정입니다. 모든 공동구매 계약서에 이 규정을 첨부합니다.",
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


# 세대 혜택 15만원 상당 ≠ 공구가 인상 — 참가비 정액 + 입예협 가격 검증
T_SEP = f"세대당 {D.FUND}만원 상당, [[공구가와 따로]]입니다"
new("std", sec=S0, title=T_SEP,
    lead=f"‘{D.FUND}만원 상당을 주면 공구가가 오르지 않느냐’는 질문에 구조로 답합니다 - 세대 혜택은 주관사 몫에서 나가고, 공구가는 입예협이 직접 검증합니다(공고 1차 종합평가 · 공동구매 단가).",
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
    lead="공고 업무범위 6) · 참가자격 9) ~ 11) - 박람회 뒤 자주 생기는 컴플레인 예시와 처리 기준, 타 단지 해결 사례입니다. 접수부터 완료까지 주관 콜센터가 기록합니다.",
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
        dict(lb="04", big=str(D.DEPOSIT_MAX), unit="%", nm="계약금 상한", ds=f"계약금은 총액의 {D.DEPOSIT_MAX}% 이하(맞춤 제작 품목 예외), 잔금은 시공·설치 후. 현금·카드 동일가."),
    ]),
    kp="가격은 말이 아니라 [[사전 공개 단가 + 최저가 보장]]으로 검증받습니다.")


# ============================================================ 07장 · 롯데캐슬 나리벡시티 맞춤 (착수 strategy 4-3 · 본부장 10-23 결정)
# 메시지 = 같은 기준 · 먼저 공개 · 한 창구. 약속 숫자는 econ 원가 하단(합계 약 3,600만원)에 맞춘 숫자 하나 + 조건(공고 8항 1 · 2 — 제안서 = 계약서 효력 · 협의회 유리 해석).
# 공개 문서 금지어: 분양가 · 청약 · 계약률 · 미분양 · 부지 이력 · 업체당 참가비 · 카페 회원 수(finish 검사).
def _won(man):
    eok, rest = divmod(man, 10000)
    return (f"{eok}억 {rest:,}만원" if rest else f"{eok}억원") if eok else f"{rest:,}만원"


FT = _won(D.FUND_TOTAL)   # 1억 65만원
HH = ST["households"]
T_DIV = f"{ST['name']}에 [[맞춘 약속]]"
T_PROM = f"{ST['short']}에 드리는 [[약속 10가지]]"
T_VOICE = "입주예정자가 먼저 묻는 [[다섯 가지]]"
T_MAP = "평가 요소 · 우대사항, [[이 쪽에]] 있습니다"
T_WORK1 = "공고 업무범위 ① [[1) ~ 4)]] 이렇게 합니다"
T_WORK2 = "공고 업무범위 ② [[5) ~ 8)]] 이렇게 합니다"
T_SITE = f"{ST['name']}, [[이런 단지]]입니다"
T_SAME = "671세대 모두 [[같은 기준]]입니다"
T_CHECK = "가격은 [[먼저 공개]]하고, 더 싸면 보상합니다"
T_DESK = "사전점검 · 하자, [[책임부터]] 나눕니다"
T_EXPERT = "전문분야 지원, [[역할부터]] 정했습니다"
T_REQ = "입예협 활동, [[주관사가 함께]] 합니다"
T_COMM = "커뮤니티 시설, [[진단하고 개선안]]을 드립니다"
T_LX = "단지 외부 경관조명, [[입주 전에]] 진단합니다"
T_SAMEQ = "같은 시기 입주, [[우리 단지 일정 먼저]]"
T_PM = "경인 지사 관리 · [[찾아가는 책임자]]"
T_MON1 = "협약부터 입주 후 12개월까지 [[일정]]"
T_QUAL = "입찰 참가자격 17개 항목 대응 ① [[1) ~ 9)]]"
T_QUAL2 = "입찰 참가자격 17개 항목 대응 ② [[10) ~ 17)]]"
T_LIMIT = "참가 제한 · 제안서 효력 · [[서약]], 그대로 지킵니다"

new("divider", n="01", title=T_DIV,
    bl=["약속 10가지 · 먼저 묻는 다섯 가지", "평가 요소 · 업무범위 1) ~ 8) 대응", "같은 기준 · 가격 공개 · 하자 · A/S", "전문분야 · 커뮤니티 · 일정 · 참가자격 17"])

# ------------------------------------------------------------ 07-01 약속 10가지
PROM10 = [
    ("세대 혜택 · 세대당 15만원 상당", f"{HH}세대 모두 같은 기준 · 총 {FT} 상당 · 주관사가 직접 사서 드리는 항목만(업체 제공 혜택은 별도)", ["same", "fund"]),
    ("가격 먼저 공개", "단가표는 박람회 30일 전 입예협과 검수 · 가격 비교자료는 14일 전 카페 공개(입예협 승인 후)", ["check"]),
    ("최저가 차액 10배 보상", "인근 매장 · 구매 영수증 · 주관사 확인 · 1건당 최대 50만원 · 온라인 · 시공 품목 제외 · 주관사 부담", ["check", "x10"]),
    ("계약금 5% 상한", "맞춤 제작 품목 예외 · 잔금은 시공 · 설치 확인 후 · 카드 · 현금 같은 단가", ["rule1"]),
    ("24시간 · 48시간", "24시간 안 1차 회신 · 48시간 안 방문 일정 확정 · 업체가 24시간 무응답이면 주관사 개입", ["call", "as"]),
    ("무상 A/S · 업체 이관", "시공 품목 최소 2년(브랜드는 제조사 보증) · 업체 도산 · 연락 두절 시 대체 업체로 이관(계약자 동의)", ["rule2", "work2"]),
    ("사전점검 · 행사 지원", "사전점검 당일 입예협 부스(현수막 · 체크리스트 · 도우미) · 총회 · 설명회 등 입예협 행사 인력 · 비품 지원", ["desk", "council"]),
    ("하자 책임 구분", "공동구매 품목 하자 = 주관사 · 업체 책임(콜센터 · 선보상) · 건설 하자 = 시공사 책임 · 주관사는 입예협이 모은 목록을 공문으로 전달 · 진행 추적(입주 지정기간)", ["desk", "as"]),
    ("행정 지원 · 전문분야", "공문 초안 · 회의록 · 월 1회 정기 방문 · 서면 질의 10영업일 회신 · 전문가 자문 · 공용부 점검 · 경관 진단은 입예협 요청 시", ["work1", "expert"]),
    ("보증 24개월", "계약이행 · 하자보증보험 보증기간 24개월 · 피보험자 입예협 · 금액과 기산일은 협약 때 확정", ["bond24", "qual2"]),
]
new("std", sec=S0, title=T_PROM,
    lead="정회원이 먼저 보시는 한 장입니다. 모든 숫자에 근거 쪽을 함께 적었고, 제안서는 계약서와 같은 효력을 갖습니다(공고 8항).",
    body=table(["NO", "약속", "조건 · 기준", "근거"], "".join(
        f'<tr><td class="n">{i:02d}</td><td class="k">{t(a)}</td><td>{t(b)}</td><td class="pg">{PGS(ks)}</td></tr>'
        for i, (a, b, ks) in enumerate(PROM10, 1)), "m9 pr10"),
    kp=("같은 기준 · 먼저 공개 · 한 창구 - [[지킬 수 있는 숫자]]만 적었습니다.",
        "증명할 수 없는 과장 표현은 쓰지 않았습니다(별지 5 서약) · 공사 · 설치 · 법률 대리 등 업무범위 밖 요청은 범위 · 비용을 서면으로 정합니다"))
B.CSS += ".tbl.pr10 td{padding:6.5px 12px;font-size:14px}.tbl.pr10 td.k{width:24%;font-size:15px}"

# ------------------------------------------------------------ 07-02 먼저 묻는 다섯 가지
VOICE = [
    ("01", "모든 세대가 같은 기준인가요?", f"{HH}세대 모두, 계약 시기 · 조건과 관계없이 같은 세대 혜택 · 같은 공개 단가 · 같은 정보를 드립니다(정회원 혜택(안)은 입예협이 정함).", ["same", "fund"]),
    ("02", "공동구매 가격은 믿을 수 있나요?", "단가표를 박람회 30일 전 입예협과 검수하고, 14일 전 가격 비교자료를 카페에 먼저 공개합니다. 인근 매장의 더 싼 판매가 영수증으로 확인되면 차액 10배(1건당 최대 50만원 · 온라인 · 시공 품목 제외)를 보상합니다.", ["check", "x10"]),
    ("03", "하자는 누가 챙기나요?", "공동구매 품목 하자는 주관사 · 참여업체가 책임집니다(접수 · 선보상 = 주관사 · 수리 = 업체). 건설 하자는 시공사 책임입니다 - 주관사는 입주 지정기간 동안 입예협이 모은 하자 목록을 정리해 공문으로 시공사에 전달하고 진행을 추적합니다.", ["desk"]),
    ("04", "같은 시기 입주 단지가 많은데 업체가 올까요?", "우리 단지 업체 모집과 시공 일정을 먼저 확정하고, 경기북부(의정부 · 양주권)에 A/S 거점이 있는 업체를 우선 배정합니다.", ["sameq", "pm"]),
    ("05", "진행 상황은 어떻게 알 수 있나요?", "월 1회 진행 보고 · 30일 전 / 14일 전 가격 자료 · 공동구매 A/S · 건설 하자 전달 현황을 입예협 승인 후 카페에 공개합니다. 공동구매 A/S 문의 창구는 한 곳입니다.", ["work2", "council"]),
]
new("std", sec=S0, title=T_VOICE,
    lead="공고 업무범위 · 우대사항과 공개 자료에서 입주예정자가 먼저 물을 다섯 가지를 골라, 우리 답과 근거 쪽을 한 장에 모았습니다.",
    body=table(["NO", "먼저 묻는 것", "엣지컴퍼니 답", "근거"], "".join(
        f'<tr><td class="n">{n}</td><td class="k">{t(q)}</td><td>{t(a)}</td><td style="white-space:nowrap">{PGS(ks)}</td></tr>' for n, q, a, ks in VOICE), "vc5"),
    kp=("비싸고, 늦고, 연락이 끊기는 입주 준비가 되지 않게 - [[다섯 가지]]에 먼저 답합니다.",
        "질문은 공고 · 공개 자료 기준(2026.10) · 카페 글 집계 아님 · 입예협과 다시 확인합니다"))
B.CSS += ".tbl.vc5 td{padding:10px 12px !important;font-size:15px !important;line-height:1.45}.tbl.vc5 td.k{width:19%;font-size:16px !important}.tbl.vc5 td:last-child{width:13%;font-size:13.5px}"

# ------------------------------------------------------------ 07-03 평가 요소 찾아보기
MAP_EV = [
    ("1차 서류", "참가자격 · 제한사항 · 제출서류 적격", "자격 17 대응표 · 제한 · 효력 · 서약 · 제출서류 14종", ["qual", "ban"]),
    ("종합평가", "공동구매 단가", "가격 먼저 공개 · 10배 보상 · 단가를 지키는 장치 · 환불 규정 전문", ["check", "x10", "guard4", "rule1"]),
    ("종합평가", "사후관리(A/S 처리)", "한 창구 A/S 정책 · 처리 기한 · 업체 이관 · 컴플레인 처리", ["as", "desk", "cpl"]),
    ("종합평가", "입주지원", "업무범위 1) ~ 8) 대응 · 사전점검 · 하자 책임 구분 · 전문분야 지원", ["work1", "work2", "desk", "expert"]),
    ("우대 17", "입주민 혜택 · 특화 제안", f"세대당 15만원 상당 · {HH}세대 같은 기준 · 선택 항목 가격표", ["same", "fund", "menu"]),
    ("우대 17", "커뮤니티 시설 업그레이드", "커뮤니티 · 경관조명 진단 → 개선안 → 입예협 승인 시 설치", ["comm", "lx"]),
    ("우대 17", "입예협 활동 지원", "행사 · 정기 방문 · 공문 · 회의록 · 법무법인 자료 협력", ["council"]),
    ("우대 17", "최저가 보상 · A/S 정책", "차액 10배(1건당 최대 50만원 · 주관사 부담) · 업체 부담을 늘리지 않는 A/S", ["x10", "as"]),
    ("3차 투표", "정회원이 보는 한 장", "약속 10가지 · 먼저 묻는 다섯 가지 · 요약제안서(제출서류 14)", ["prom", "voice"]),
]
new("std", sec=S0, title=T_MAP,
    lead="공고 3항 선정방법(1차 서류 종합평가 · 3차 정회원 투표)과 5항 참가자격 17 우대사항을 어느 쪽에서 답하는지 정리했습니다(쪽 번호 = 각 장 우측 상단).",
    body=table(["단계", "평가 요소", "엣지컴퍼니 답", "쪽"], "".join(
        f'<tr><td class="g">{a}</td><td class="k">{t(b)}</td><td>{t(c)}</td><td class="pg">{PGS(ks)}</td></tr>'
        for a, b, c, ks in MAP_EV), "m9 mpv"),
    kp=("공고가 보는 [[평가 요소 모두]] 쪽 번호로 찾으실 수 있습니다.", "공고에 배점 표는 없습니다 · 1차 서류 종합평가 = 공동구매 단가 · 사후관리(A/S 처리) · 입주지원"))
B.CSS += ".tbl.mpv td.g{width:84px;white-space:nowrap;font-size:13px}"

# ------------------------------------------------------------ 07-04 · 05 업무범위 1) ~ 8)
WORK = [  # (공고 업무, 방식 태그, 엣지컴퍼니가 하는 일, 지킬 숫자 · 조건)
    ("1) 입주박람회 개최 · 총괄 운영 (최신 사양 보장)", "직접",
     "박람회 시점에 판매 중인 현행 모델 기준 · 이월 · 전시 상품은 계약서에 따로 표시합니다. 모든 계약서에 모델명 · 출시연도를 적고 박람회 30일 전 단가표를 입예협과 검수합니다. 현장에서 모델을 바꾸려면 입주민 서면 동의가 있어야 하며 차액은 돌려드립니다.",
     f"박람회 주말 포함 2 ~ 3일 · {ST['expo']} 예정(입주 3 ~ 2개월 전) · 날짜는 사전점검 일정 확정 뒤 입예협과 결정"),
    ("2) 입주 행정 · 사전점검 · 공용물품 지원", "직접",
     "사전점검 당일 입예협 부스에 현수막 · X배너 · 체크리스트 · 도우미를 지원합니다. 공용물품은 세대 혜택 범위 안에서 입예협이 고른 품목을 주관사가 사서 드립니다.",
     f"사전점검 당일 부스 지원 · 공용물품 = 세대 혜택({FT} 상당) 안에서 입예협이 선택"),
    ("3) 박람회 · 사전점검 · 입예협 행사 지원 (인력 · 비품)", "직접",
     "총회 · 설명회 등 입예협이 여는 행사에 진행 인력과 테이블 · 의자 · 음향 비품을 지원합니다. 박람회와 사전점검은 1) · 2)에 포함됩니다.",
     "총회 · 설명회 등 회차 제한 없이 요청하시는 만큼 인력 · 비품 지원"),  # 본부장 10-23: 횟수 제한 없음 · 추가분은 세대 혜택에서
    ("4) 건축 · 토목 · 조경 · 경관 전문분야 컨설팅 · 행정지원", "직접 + 전문가(승인)",
     "공문 초안 · 회의록 · 자료 정리 등 행정 지원은 엣지컴퍼니가 직접 합니다. 건축 · 토목 · 조경 현장 자문과 경관 · 커뮤니티 진단은 입예협이 요청하시면 진행합니다(외부 전문가는 입예협 서면 승인). 법률 판단은 협의회 지정 법무법인 영역입니다.",
     "행정 지원 · 월 1회 정기 방문 · 서면 질의 10영업일 안 회신 · 현장 자문 · 진단은 입예협 요청 시"),
    ("5) 공용 · 전용부 하자 점검 · 품질 검수 · 하자대응 · 대리", "직접 + 전문업체(승인)",
     "공동구매 품목 하자는 주관사 · 참여업체가 책임집니다(창구 · 선보상 = 주관사 · 수리 = 업체). 건설 하자(공용부 · 전용부)는 시공사 책임이며, 주관사는 입예협이 모은 하자를 정리해 하자보수 요청 공문 초안 · 시공사 전달 · 처리 진행 추적 · 하자 회의 배석을 맡습니다(판정 · 보수 책임 · 소송 대리 아님). 공용부 정밀 점검은 입예협이 요청하시면 전문업체(입예협 서면 승인)와 진행합니다. 소송 · 청구는 법무법인 업무입니다.",
     "건설 하자 = 시공사 책임 · 주관사 정리 · 전달 · 추적(입주 지정기간 · 보고 주 1회) · 공용부 정밀 점검은 입예협 요청 시"),
    ("6) A/S · 하자보수 사후관리 이행 · 지원", "직접 + 참여업체",
     "창구 · 관리는 주관사가, 시공 · 수리는 참여업체가 맡습니다. 업체가 정당한 이유 없이 미루면 시정을 요구하고, 문을 닫거나 연락이 끊기면 대체 업체로 옮깁니다.",
     "24시간 안 1차 회신(주말 · 공휴일 = 다음 영업일 12시) · 48시간 안 방문 일정 확정 · 시공 품목 무상 A/S 최소 2년 · 무상 A/S 기간 안 이관 비용 주관사 부담"),
    ("7) 입예협 카페 활성화 · 홍보 · 안내 콘텐츠", "직접(게시는 승인 후)",
     "카페 운영권은 입예협에 있습니다. 주관사는 정해진 주기의 자료를 만들어 입예협 승인 후 게시합니다.",
     "월 1회 진행 보고 · 30일 전 / 14일 전 가격 자료 · 사전점검 체크리스트 · 건설 하자 전달 · 진행 현황(입주 지정기간 주 1회)"),
    ("8) 기타 협의회가 요청하는 업무", "협의",
     "추가 요청은 수행 방법 · 일정을 먼저 회신하고 진행합니다. 공사 · 설치 · 법률 대리처럼 업무범위 밖 항목만 범위 · 비용을 서면으로 정합니다.",
     "요청 접수 후 3영업일 안 수행 방법 · 일정 회신"),
]


def _work_tbl(rows):
    return table(["공고 업무", "방식", "엣지컴퍼니가 하는 일", "지킬 숫자 · 조건"], "".join(
        f'<tr><td class="k">{t(a)}</td><td class="tg">{t(b)}</td><td>{t(c)}</td><td class="nm">{t(d)}</td></tr>' for a, b, c, d in rows), "wk8")


new("std", sec=S0, title=T_WORK1,
    lead="공고 4항 업무범위를 세 칸으로 나눴습니다 - 엣지컴퍼니가 직접 / 입예협 서면 승인을 받은 전문업체와 함께(결과 책임은 엣지컴퍼니) / 협의회 지정 법무법인 영역.",
    body=_work_tbl(WORK[:4]),
    kp=("공고 업무 1) ~ 4), [[누가 · 무엇을]] 하는지 먼저 정했습니다.", "제안서 = 계약서 효력(공고 8항 1) · 공사 · 설치 · 법률 대리 등 업무범위 밖 요청은 범위 · 비용을 서면으로 정합니다"))
new("std", sec=S0, title=T_WORK2,
    lead="하자 점검 · A/S · 카페 · 기타 요청까지 - 주관사 업무는 하도급 · 재위탁하지 않고, 전문업체 활용은 입예협 사전 서면 승인을 받은 경우에만 합니다(공고 9항 6).",
    body=_work_tbl(WORK[4:]),
    kp=("건설 하자는 [[시공사 책임]](주관사 전달 지원 = 입주 지정기간), 공동구매 품목 A/S는 [[품목별 무상 기간]] 주관사 · 업체 책임입니다.", "두 기간은 따로 운영 · 시공 품목 무상 A/S 최소 2년 · 브랜드는 제조사 보증 · 용역은 재시공 기준"))
B.CSS += (".tbl.wk8 td{padding:9px 11px;font-size:14px;line-height:1.42;vertical-align:top}.tbl.wk8 td.k{width:21%;font-size:14.5px}"
          ".tbl.wk8 td.tg{width:11%;font-size:12.5px;color:var(--gold);font-weight:700}.tbl.wk8 td.nm{width:29%;color:var(--ink);font-size:13.5px}")

# ------------------------------------------------------------ 07-06 단지 이해
_t84 = sum(n for a, n in ST["types"] if a.startswith("84"))
_tbig = HH - _t84
new("std", sec=S0, title=T_SITE,
    lead="공고 단지개요와 공개 보도(2곳 이상 일치) 기준 - 품목 · 업체 구성과 일정을 이 단지에 맞춥니다.",
    body=B.cards([
        dict(lb="SCALE", big=f"{HH:,}", unit="세대", nm=f"{ST['buildings']}개 동 · {ST['floors']}",
             ds=f"84㎡ [[{_t84}세대]](64%) · 102 ~ 155㎡ {_tbig}세대(36%)"),
        dict(lb="BUILDER", big="롯데", nm=f"시공 {ST['builder']} · 시행 {ST['developer']}",
             ds="건설 하자 보수 = 시공사 책임 · 사전점검 · 입주지원센터 일정은 시공사와 협의"),
        dict(lb="MOVE-IN", big="2027", unit=".11", nm="입주 예정",
             ds=f"제출(2026.10)부터 약 {ST['months']}개월 - 월별 일정으로 관리"),
        dict(lb="LOCATION", big="의정부", nm=ST["address"], hl=True,
             ds="경기북부 · 시공 품목은 의정부 · 양주권 업체 우선"),
    ])
    + B.rows([
        ("중대형 36%", "102 ~ 155㎡ 세대는 커튼 · 조명 · 수납 물량이 큽니다 - [[타입별 표준 견적표]]를 박람회 전에 공개합니다."),
        ("옵션 겹침 확인", "시스템에어컨 · 빌트인 가전 · 붙박이장 · 조명 스타일업 · 중문은 시공사 옵션과 겹칠 수 있어 [[미선택 · 추가 수요만]] 모집합니다."),
    ], title_w=150),
    kp=(f"{HH}세대 · 84㎡ 64% · 중대형 36% - [[타입별로]] 품목과 견적을 나눕니다.", "단지 사실 = 공고 단지개요 · 공개 보도 기준 · 옵션 품목은 입주자모집공고로 다시 확인"))

# ------------------------------------------------------------ 07-07 같은 기준
new("std", sec=S0, title=T_SAME,
    lead=f"계약 시기 · 조건과 관계없이 {HH}세대 모두에게 같은 세대 혜택 · 같은 가격 · 같은 정보를 드립니다(정회원 우대 · 특정 입주민 추가 혜택은 입예협이 정함).",
    body=B.cards([
        dict(lb="BENEFIT", big="15", unit="만원 상당", nm="세대 혜택 · 모든 세대",
             ds=f"{HH}세대 × 15만원 상당 = 총 {FT} 상당 · 주관사가 직접 사서 드리는 항목만"),
        dict(lb="PRICE", big="1", unit="가격", nm="같은 단가 · 같은 조건",
             ds="카페 공개 단가 = 박람회장 단가 = 온라인 단가 · 카드 · 현금 같은 단가 · 현장 가격 변경 없음"),
        dict(lb="INFO", big="1", unit="창구", nm="같은 정보 · 한 번에 공개",
             ds="가격 자료 · 진행 보고 · 하자 현황을 입예협 승인 후 카페에 공개 · 개별 안내 없음"),
        dict(lb="REVENUE", big="0", unit="%", nm="공구가 연동 수수료", hl=True,
             ds="주관사 수입 = 업체 참가비(정액) + 직영 품목 판매뿐 · 판매가에 비례하는 수수료를 받지 않음"),
    ])
    + '<div class="sepn" style="margin-top:14px">참여업체 사은품 · 경품 · 정회원 혜택 · 박람회 상품권 = <b>참여업체 제공(안) · 15만원 상당과 별도</b> - 참여업체 확정 후 입예협 승인으로 정합니다</div>',
    kp=("같은 단지, [[같은 기준]] - 세대 혜택 · 단가 · 정보는 모든 세대가 같습니다.", f"세대 혜택 구성 · 선택 항목 가격표 {PGS(['fund', 'menu'])} · 직영 품목도 같은 심사 · 같은 비교표 · 같은 10배 보상"))

# ------------------------------------------------------------ 07-08 가격 검증
CHECK5 = [("D-30", "단가표 검수", "모델명 · 출시연도 · 설치 · 철거 · 배송 · A/S 포함 여부를 입예협과 함께 확인"),
          ("D-14", "비교자료 공개", "같은 모델 · 같은 조건 총액으로 시중 매장 · 온라인 가격과 비교 → 카페 공개(승인 후)"),
          ("D-DAY", "같은 가격", "공개 단가 그대로 · 현장 가격 변경 없음 · 카드 · 현금 같은 단가"),
          ("계약", "모델 고정", "계약서에 모델명 · 출시연도 기재 · A → B 변경은 입주민 서면 동의 · 차액 반환"),
          ("계약 후 7일", "10배 보상", "같은 브랜드 · 모델 새 제품이 인근 매장에서 더 싸면 차액 10배")]
new("std", sec=S0, title=T_CHECK,
    lead="공고 1차 종합평가 ‘공동구매 단가’ · 우대 17 ‘최저가 보상’ - 박람회 전에는 가격을 먼저 보여 드리고, 계약 뒤에는 더 싼 판매가 확인되면 보상합니다.",
    body=('<div class="nb"><div class="flowx">' + "".join(
        (('<div class="ar">›</div>' if i else "") + f'<div class="st{" hl" if i == 4 else ""}"><i>{a}</i><b>{b}</b><p>{t(c)}</p></div>')
        for i, (a, b, c) in enumerate(CHECK5)) + '</div>'
          + B.rows([
              ("같은 조건 총액", "제품가만이 아니라 설치 · 철거 · 배송 · 부가세 · A/S 기간을 맞춘 [[총액]]으로 비교합니다."),
              ("높으면 사유 또는 조정", "공개 단가가 더 높으면 사유(설치 포함 · A/S 연장 등)를 적거나 조정을 요청하고, [[입예협이 승인하지 않으면 재입찰]]합니다."),
              ("10배 보상 조건", f"구매 영수증(판매 매장 사업자 정보 · 모델명 · 금액) + 주관사 매장 확인 · 1건당 최대 50만원(계약금액이 더 적으면 그 금액) · 세대 · 품목당 1회 · [[보상금은 주관사 부담]]"),
              ("보상 대상 밖", "견적서 · 가격표만 있는 경우, 온라인 · 홈쇼핑 판매, 시공 품목, 카드 청구할인 · 사은품 · 전시 · 리퍼 · 한정 수량 행사가(환불 규정 제8조)."),
          ], title_w=190) + '</div>'),
    kp=("가격은 [[박람회 전에 먼저]] 보여 드리고, 계약 뒤에도 한 번 더 지킵니다.",
        "예) 공구가 35만 → 인근 매장 32만 → 차액 3만 × 10 = 보상 30만원 + 판매가 32만원 조정 · 업체 부담을 늘리지 않음(공고 우대 17)"))

# ------------------------------------------------------------ 07-09 사전점검 · 하자 창구
new("std", sec=S0, title=T_DESK,
    lead=f"공고 업무 2) · 5) - 공동구매 품목 하자는 주관사 · 참여업체 책임, 건설 하자는 시공사({ST['builder']}) 책임입니다. 주관사는 건설 하자를 대신 책임지지 않고, 정리 · 전달 · 추적을 돕습니다.",
    body=('<div class="nb"><div class="pmx">'
          '<div class="pc"><h3><i>PRE-INSPECTION</i>사전점검 현장 지원</h3>'
          + B.rows([
              ("당일 부스 지원", "사전점검 당일 입예협 부스에 현수막 · X배너 · 체크리스트 · 도우미를 지원합니다."),
              ("세대 전문 점검", "원하시는 세대는 세대 혜택의 ‘사전점검 할인’으로 전문 점검을 받으실 수 있습니다."),
              ("옵션 대조", "모집공고 옵션표와 실제 설치를 대조하는 점검표를 드립니다."),
          ], title_w=118) + '</div>'
          '<div class="pc"><h3><i>DEFECT</i>하자 - 누구 책임인지 먼저</h3>'
          + B.rows([
              ("공동구매 품목", "박람회 계약 품목 하자 = [[주관사 · 참여업체 책임]] - 콜센터 접수 · 24시간 회신 · 선보상 · 품목별 무상 기간(시공 품목 최소 2년)."),
              ("건설 하자", f"세대 · 공용부 건설 하자 = [[시공사({ST['builder']}) 책임]] · 접수는 시공사 하자 접수 창구."),
              ("주관사 역할", "입주 지정기간 동안 입예협이 모은 건설 하자 목록 정리 · 보수 요청 공문 초안 · 시공사 전달 · 진행 추적 · 주 1회 보고."),
              ("하지 않는 일", "건설 하자의 판정 · 보수 · 보수 책임 · 소송 대리(법률 = 협의회 지정 법무법인)."),
          ], title_w=118) + '</div></div></div>'),
    kp=("공동구매 하자는 [[주관사 · 업체 책임]], 건설 하자는 [[시공사 책임]] - 주관사는 정리 · 전달 · 추적을 돕습니다.", "공용부 정밀 점검은 입예협 요청 시 · 법률 대리는 협의회 지정 법무법인 업무 · 업무범위 밖 요청은 서면 합의"))

# ------------------------------------------------------------ 07-10 전문분야 지원 범위(업무 4 · 5)
EXPERT6 = [  # (구분, 누가, 무엇을, 진행) - 본부장 10-24: 항목별 비용 표시 안 함(업무범위 전부 지원 · 세대 혜택 15만원 안에서) — 요약제안서도 이 값
            ("행정 지원", "엣지컴퍼니 직접", "시행 · 시공사에 요청할 자료 목록 · 공문 초안 · 회의록 · [[월 1회 정기 방문]] 때 회의 배석", "협약 ~ 입주"),
            ("기술 서면 질의", "엣지컴퍼니 접수 · 회신", "입예협 서면 질의에 [[10영업일 안]] 서면 회신", "상시"),
            ("건축 · 토목 · 조경 자문", "외부 전문가(입예협 서면 승인)", "입예협이 요청한 분야 · 시기 현장 자문", "입예협 요청 시"),
            ("공용부 점검", "하자 점검 전문업체(입예협 서면 승인)", "공용부 품질 점검 · 공용 · 조경 하자진단 · 결과 보고서", "입예협 요청 시"),
            ("경관 · 커뮤니티", "엣지컴퍼니 조명사업부 직접(전기공사업 등록 제 울산-00821호)", "경관조명 · 커뮤니티 조명 진단 + 개선안 · 설치는 별도 견적", "입예협 요청 시"),
            ("법률 판단 · 소송", "협의회 지정 법무법인", "엣지컴퍼니는 필요한 자료를 정리해 전달", "법무법인"),
]
new("std", sec=S0, title=T_EXPERT,
    lead="공고 업무 4) · 5) - 상시 하는 일과 입예협이 요청하실 때 하는 일을 나눴습니다. 자문 의견은 법정 감리 · 하자 판정 · 법률 의견이 아닙니다.",
    body=table(["구분", "누가", "무엇을", "진행"], "".join(
        f'<tr><td class="k">{t(a)}</td><td>{t(b)}</td><td>{t(c)}</td><td>{t(d)}</td></tr>' for a, b, c, d in EXPERT6), "lgx ex6"),
    kp=("행정 지원은 [[상시]], 자문 · 점검 · 진단은 [[입예협이 요청하실 때]] 진행합니다.", "외부 전문업체 활용은 공고 9항 6에 따라 입예협 사전 서면 승인 시에만 · 결과 책임은 엣지컴퍼니"))
B.CSS += ".tbl.ex6 td{padding:11px 13px;font-size:14.5px}.tbl.ex6 td.k{width:15%;font-size:15.5px}.tbl.ex6 td:last-child{width:17%;color:var(--gold);font-size:13.5px}"

# ------------------------------------------------------------ 07-11 입예협 활동 지원
REQ6 = [
        dict(lb="EVENT", big="총회", nm="입예협 행사 지원", ds="총회 · 설명회 등 요청하시는 만큼 - 진행 인력 · 테이블 · 의자 · 음향 비품"),
        dict(lb="VISIT", big="월 1", unit="회", nm="정기 방문 · 회의 배석", ds="협약부터 입주까지 - 장소는 입예협이 정한 곳에 책임자가 찾아갑니다"),
        dict(lb="DOCS", big="공문", nm="자료 · 공문 · 회의록", ds="시행 · 시공사에 보낼 자료 정리 · 공문 초안 · 회의록 - 입예협 이름으로 발송"),
        dict(lb="LAW", big="협력", nm="지정 법무법인 자료 협력", ds="협의회가 지정한 법무법인에 필요한 자료를 정리해 전달(자격 14)"),
        dict(lb="CAFE", big="월 1", unit="회", nm="진행 보고 · 카페 공개", ds="가격 자료 · 하자 현황 · 진행 보고 - 입예협 승인 후 게시"),
        dict(lb="REQUEST", big="3", unit="영업일", nm="추가 요청 회신", ds="수행 방법 · 일정을 회신하고 진행(업무 8) · 업무범위 밖 공사 · 설치만 별도 협의"),
]
new("std", sec=S0, title=T_REQ,
    lead="공고 업무 3) · 7) · 8) · 참가자격 14 · 우대 17 - 형평 협의 · 총회 · 법무 협력을 입예협 임원 몇 분이 다 떠안지 않도록 돕습니다.",
    body=('<div class="nb">' + B.tiles(REQ6, cols=3, rows_n=2).replace('class="tiles"', 'class="tiles lg"') + '</div>'),
    kp=("협상의 주체는 [[입예협]] - 주관사는 자료와 일손으로 돕습니다.", "협의 결과는 ‘협의 완료’와 ‘설치 완료’를 나눠 보고 · 회의 장소는 입예협이 정합니다"))

# ------------------------------------------------------------ 07-12 커뮤니티 업그레이드(우대 17)
new("std", sec=S0, title=T_COMM,
    lead="공고 우대 17 ‘커뮤니티 시설 업그레이드 안’ - 조명 · 실링팬 · 커튼을 직접 다루는 주관사가 공간별로 진단하고, 설치 여부와 범위는 입예협 · 관리주체가 정합니다.",
    body=table(["공간", "진단 항목", "개선안 예"], "".join(
        f'<tr><td class="k">{t(a)}</td><td>{t(b)}</td><td>{t(c)}</td></tr>' for a, b, c in [
            ("피트니스 · 실내 운동", "바닥 · 거울면 눈부심 · 조도 · 공기 순환", "디밍 조명 · 실링팬 공기 순환 · 구역별 점등"),
            ("북카페 · 스터디룸", "책상면 조도 · 색온도 · 차광", "독서 구역 조도 보강 · 4000K 전후 · 블라인드"),
            ("키즈룸", "눈부심 · 모서리 · 손 닿는 기구", "간접조명 · 안전 커버 · 항균 마감 검토"),
            ("시니어 · 다목적실", "밝기 균일도 · 동선 · 차광", "균일 조도 · 동선 바닥 밝기 · 전동 블라인드"),
            ("로비 · 커뮤니티 출입부", "첫인상 · 야간 밝기 · 유지관리", "간접조명 · 타이머 · 심야 감광"),
        ]), "lgx cm5")
         + '<div class="hflow"><span>공간별 진단(입예협 요청 시)</span><i>›</i><span>개선안(물량 · 공사비 · 유지관리비)</span><i>›</i>'
           '<span>입예협 · 관리주체 검토</span><i>›</i><span>승인 시 설치 · 별도 견적</span></div>',
    kp=("공용부에 쓰는 돈이 [[관리비 · 공구가로 돌아오지 않게]] - 진단 · 개선안은 입예협이 요청하시면 진행합니다.",
        "커뮤니티 시설 목록은 입주자모집공고 · 시공사 자료로 다시 확인 · 설치비는 별도 견적 · 공용부는 입예협 · 관리주체 결정"))
B.CSS += ".tbl.cm5 td{padding:12px 14px;font-size:15px}.tbl.cm5 td.k{width:22%;font-size:16px}"


def _fig(key, cap, sub_, pos="50% 50%"):
    im, _own = slot(key)
    if not im:
        return ""
    return (f'<figure><img src="assets_ins/{im}.jpg" alt="" style="object-position:{pos}">'
            f'<figcaption>{cap}<small>{sub_}</small></figcaption></figure>')


# ------------------------------------------------------------ 07-13 외부 경관조명(우대 17 · 업무 4)
new("std", sec=S0, title=T_LX,
    lead="공고 업무 4) ‘경관’ - 전기공사업 등록 업체로서 단지의 밤 얼굴을 입주 전에 진단하고 개선안을 냅니다 - 입예협이 요청하시면 진행(아래 사진은 나리벡시티 경관조명 연출 시뮬레이션 · 실제와 다를 수 있음).",
    body=('<div class="nb"><div class="lxo"><div class="gal lxa">'
          + _fig("lx_front1", "① 동 파사드", "외벽 라인조명 · 도로변 경관 · 시뮬레이션", "50% 45%")
          + _fig("lx_front2", "② 단지 조감 야간", "동 간 통일된 색온도 · 산책로 동선 · 시뮬레이션", "50% 50%")
          + _fig("lx_gate", "③ 문주 · 진입부", "진입부 보행 동선 · 문주 간접광 · 시뮬레이션", "50% 55%")
          + '</div><div class="lxd">'
          + "".join(f"<div><b>{a}</b><p>{t(b)}</p></div>" for a, b in [
              ("우선 1 · 동 파사드", "39층 4개 동의 외벽 라인조명 · 실루엣 - 기존 경관조명 도면 · 배선 · 조도 · 타이머부터 확인합니다."),
              ("우선 2 · 진입부 · 조경", "진입부 보행 동선 · 수목 · 놀이터 · 산책로의 밝기 · 눈부심을 함께 봅니다."),
              ("산출물", "① 현황 진단 ② 기본 · 개선 · 선택안 비교(물량 · 공사비 · 유지관리비) ③ 협의 기록"),
              ("결정은 입예협 · 관리주체", "설치 여부 · 범위 · 비용은 도면 검토 뒤 입예협 · 관리주체가 정합니다."),
          ])
          + '</div></div></div>'),
    kp=("단지 가치는 [[밤의 첫인상]]에서 - 입예협이 요청하시면 커뮤니티와 같은 날 묶어 진단합니다.", D.LX_CAP + " · 전기공사업 등록 제 울산-00821호"))
B.CSS += (".lxo{display:grid;grid-template-columns:1.75fr 1fr;gap:18px;flex:1;min-height:0}"
          ".gal.lxa{grid-template-columns:1.25fr 1fr;grid-template-rows:1fr 1fr;gap:10px;min-height:0}"
          ".gal.lxa figure:first-child{grid-row:span 2}"
          ".lxo .gal figcaption{font-size:15px;padding:24px 12px 9px}.lxo .gal figcaption small{font-size:12px}"
          ".lxo .lxd{display:flex;flex-direction:column;justify-content:center;gap:12px;min-height:0}"
          ".lxo .lxd>div{border-left:2px solid var(--gold2);padding:2px 0 2px 14px}"
          ".lxo .lxd b{font-size:16.5px}.lxo .lxd p{font-size:14px;color:var(--sub);line-height:1.45;margin-top:3px}")

# ------------------------------------------------------------ 07-14 같은 시기 입주
new("std", sec=S0, title=T_SAMEQ,
    lead="의정부에서 같은 분기에 여러 단지가 입주합니다 - 좋은 업체와 시공 인력을 우리 단지에 먼저 묶어 둡니다.",
    body=('<div class="nb">' + B.rows([
        ("업체 모집 먼저", "참여업체 공개 모집 · 심사 일정을 협약 직후 확정하고, 품목별 업체를 [[박람회 90일 전]]까지 정합니다."),
        ("시공 일정 배정표", "계약 세대의 납품 · 시공 날짜를 동 · 라인별 배정표로 먼저 잡고, 업체가 다른 단지 일정으로 미루지 못하게 계약서에 적습니다."),
        ("경기북부 A/S 거점 업체", "업체 선정 기준에 ‘의정부 · 양주 · 서울 동북권 A/S 거점’을 넣어 [[가까운 업체를 우선]] 배정합니다."),
        ("입주 집중일 분산", "입주 지정기간 앞쪽에 시공이 몰리지 않게 날짜를 나눠 배정하고, 일정이 바뀌면 위약금 없이 다시 잡습니다."),
        ("겨울 전 입주", "11월 입주 - 줄눈 · 탄성코트 등 습식 시공은 기온 · 양생 시간 기준을 계약서에 적고, 결로 · 단열 품목을 수요조사에 넣습니다."),
    ], title_w=190) + '</div>'),
    kp=("다른 단지와 비교하지 않고, [[우리 단지 일정]]을 먼저 확정합니다.", "업체 · 일정은 입예협 승인 · 시공 일정은 시공사 공정에 따라 조정"))

# ------------------------------------------------------------ 07-15 담당 체계 · 경인 지사
new("std", sec=S0, title=T_PM,
    lead="수도권 단지의 시공 · A/S는 경인 지사(평택)가 관리하고, 회의는 책임자가 단지로 찾아갑니다. 계약과 책임은 울산 본사입니다.",
    body=('<div class="nb"><div class="pmx">'
          '<div class="pc"><h3><i>PEOPLE</i>담당 체계</h3>'
          + B.rows([
              ("책임자", "주관사업 총괄 본부장 - 계약 후 실제 업무를 맡을 책임자"),
              ("결정권자", "대표이사 - 제안 조건 확약"),
              ("운영 인력", f"대표 · 본부장 + 4개 팀 {sum(n for _, n, _ in D.STAFF)}명이 업무를 나눠 맡고, 단지 전담 PM 1명을 지정합니다(명단은 협약 시)."),
              ("외부 전문", "자문 · 점검 · 촬영은 입예협 서면 승인 후 외부 전문가와 함께(하도급 아님)."),
          ], title_w=96) + '</div>'
          '<div class="pc"><h3><i>FIELD</i>현장 대응</h3>'
          + B.rows([
              ("관리 거점", "경인 지사(경기도 평택시 비전동 866-3) - 상설 쇼룸 · 시공 · A/S 관리"),
              ("정기 방문", "협약부터 입주까지 월 1회 + 사전점검 · 박람회 때 현장"),
              ("출동", "의정부 · 양주권 참여업체가 먼저 출동 · 직영 품목 · 업체 미응답 건은 본사가 맡습니다."),
              ("입주 지정기간", "단지 안 상주 창구 운영(위치 · 시간은 입예협 · 관리주체와 협의)"),
          ], title_w=96) + '</div></div></div>'),
    kp=("책임자가 [[찾아가고]], 가까운 업체가 [[먼저 출동]]합니다.", "인력 표기는 업무 분담 기준 · 전담 PM 1명 · 경인 지사는 관리 · 쇼룸 거점이며 출동은 인근 업체 + 본사"))

# ------------------------------------------------------------ 07-16 일정
MON = [  # (시기, 주관사 업무, 입예협 보고 · 산출물)
    ("2026.10 ~ 11", "제안서 제출(10.26) · 1차 서류 · 2차 PT(책임자 · 대표이사 참석) · 3차 정회원 투표", "제안 조건 = PT 조건"),
    ("2026.12", "협약 · 전담 PM 지정 · 연락 체계 · 정기 방문 시작 · 건의 관리표", "협약서 · 연락 체계표"),
    ("2027.01 ~ 03", "품목 수요조사(옵션 선택 여부 문항) · 세대 혜택 선택 항목 확정", "수요조사 결과 · 선택 항목 목록"),
    ("2027.04 ~ 05", "업체 공개 모집 · 4단계 심사 · 업체 확정(박람회 90일 전)", "심사 결과 보고"),
    ("2027.06 ~ 07", "단가 제출 · 시중 / 온라인 가격 조사 · 30일 전 단가 검수", "검수 단가표"),
    ("2027.08 ~ 09", "14일 전 비교자료 공개 · [[입주박람회 2 ~ 3일]]", "박람회 결과보고서(종료 후 30일 안)"),
    ("2027.10 ~ 11", "사전점검 당일 부스 지원 · 입예협 행사 · 납품 · 시공 배정표 · [[입주]]", "사전점검 지원 결과"),
    ("입주 지정기간", "건설 하자 정리 · 시공사 전달 · 추적(주 1회 보고) · 상주 창구(협의)", "전달 · 처리 현황"),
    ("입주 후 12개월", "공동구매 A/S 관리(콜센터)", "최종 결과 보고서(종료 후 30일 안)"),
]
new("std", sec=S0, title=T_MON1,
    lead="입주 2027년 11월 예정 기준 - 박람회는 입주 3 ~ 2개월 전, 날짜는 사전점검 일정 확정 뒤 입예협과 정합니다.",
    body=table(["시기", "주관사 업무", "입예협 보고 · 산출물"], "".join(
        f'<tr><td class="n" style="width:128px;white-space:nowrap">{a}</td><td>{t(b)}</td><td class="k">{t(c)}</td></tr>' for a, b, c in MON), "lgx mn8"),
    kp=("협약부터 [[입주 후 12개월]]까지, 할 일과 보고 시점을 미리 정했습니다.", "일정은 공정 · 사전점검 일정에 따라 입예협과 조정 · 자문 · 점검 · 진단은 입예협이 요청하신 시기에 진행"))
B.CSS += ".tbl.mn8 td{padding:9px 13px;font-size:14.5px}.tbl.mn8 td.k{width:25%;font-size:14px;color:var(--gold)}"

def ftable(head, widths, rows_html, cls=""):
    """열 폭을 고정(table-layout:fixed)한 표 — 밝은 시안에서 첫 열이 좁아지는 문제 방지."""
    cg = "".join(f'<col style="width:{w}">' for w in widths)
    th = "".join(f"<th>{h}</th>" for h in head)
    return f'<table class="tbl {cls}" style="table-layout:fixed"><colgroup>{cg}</colgroup><thead><tr>{th}</tr></thead><tbody>{rows_html}</tbody></table>'


# ------------------------------------------------------------ 07-17 참가자격 17
QUAL17 = [  # (공고 5항, 엣지컴퍼니 현황, 증빙 = 제출서류 번호)
    ("1) 해당 분야 1년 이상 영위", f"법인 설립 · 개업 {D.FOUNDED} · 4년 7개월", "05 사업자등록증"),
    ("2) 입주박람회 기획 · 운영 업태 · 종목", "종목 ‘전시, 박람회 및 행사 대행업’ · 등기 목적 ‘전시 박람회 사업 · 행사대행업’", "05 · 06"),
    ("3) 자본금 1억 이상 · 통장 명의 동일", "자본금 2억원 · 법인 명의 통장", "06 등기부 · 14 통장 사본"),
    ("4) 4대보험 정직원 5명 이상 · 실행 인원 7인 이상", "4대보험 가입자 13명(2026.10.23 명부) · 실행 인원 = 대표 · 본부장 + 4개 팀 12명", "08 명부"),
    ("5) 공고일 현재 국세 · 지방세 체납 없음", "체납 없음", "07 완납증명서"),
    ("6) 체납 이력 없음 · 공고일 이전 완납 증명", "체납 이력 없음 · 2026.10.14 완납증명서(공고일 이전)", "07 · 14"),
    ("7) 최근 3년 벌금 이상 형사처분 없음", "해당 이력 없음(확인 완료)", "13 청렴 서약"),
    ("8) 타 단지 입예협 · 입주예정자 분쟁 · 소송 없음", "해당 이력 없음(확인 완료)", "10 확약 서약"),
    ("9) A/S 대책 · 보증기간 명확 · 손해배상 이행", "한 창구 A/S · 시공 품목 무상 A/S 최소 2년 · 선보상 후 정산", "04 · 11"),
    ("10) 취소 · 환불 기준 · 하자 · 분쟁 절차", "계약 취소 · 환불 규정 전문(제1 ~ 10조 · 별표)", "04 환불 규정"),
    ("11) 물품 파손 · 변형 · 하자 손해배상", "참여업체 특약이행각서 · 업체 미응답 시 주관사 선보상", "11 하자 보수 이행각서"),
    ("12) 이행보증보험 발행 · 손해배상 이행", "보증보험증권 발급 이력 있음(광고대행 용역 계약보증 · 이행보증 아님) · 협약 후 입예협 피보험자로 발급", "14 발급 이력"),
    ("13) 계약이행 · 하자보증 24개월 이상", "보증기간 24개월로 발급 · 금액 · 기산일 · 대상은 협약 때 확정 · 협약 후 발급", "제안서 · 협약"),
    ("14) 지정 법무법인 협력 · 총회 등 행사 지원", f"자료 정리 · 전달 · 입예협 행사 인력 · 비품 지원 {PG('council')}", "제안서"),
    ("15) 증빙 · 자료 제출", "요청 시 원본 열람 · 사본 제출", "제안서"),
    ("16) 비밀유지 · 결과 이의 제기 없음", "비밀유지 서약 · 이의 제기하지 않음", "12 비밀유지 서약"),
    ("17) 우대 - 혜택 · 활동 지원 · 최저가 · A/S", f"평가 요소 찾아보기 {PG('map')}", "제안서"),
]
def _q17(rows):
    return ftable(["공고 참가자격", "엣지컴퍼니 현황", "증빙"], ["31%", "52%", "17%"], "".join(
        f'<tr><td class="k">{t(a)}</td><td>{t(b)}</td><td class="ev">{t(c)}</td></tr>' for a, b, c in rows), "q17")


new("std", sec=S0, title=T_QUAL,
    lead="공고 5항 참가자격 1) ~ 17)을 제출서류 번호(7항 01 ~ 14)와 1:1로 맞췄습니다 - 사업자 현황 · 세금 · 법규 준수.",
    body=_q17(QUAL17[:9]),
    kp=("참가자격 [[17개 항목 모두]] 충족 · 증빙은 제출서류 번호로 찾으실 수 있습니다.", "05 ~ 08 = 공고일(2026.10.19) 이후 발급본 · 09 = 연 1회 정기 평가(재무제표 기준) 최근본 · 개인정보는 가림본"))
new("std", sec=S0, title=T_QUAL2,
    lead="A/S · 사후관리 능력 · 보증보험 · 손해배상 능력 · 요청사항 수행 능력 · 우대사항.",
    body=_q17(QUAL17[9:]),
    kp=("보증은 [[보증기간 24개월]] - 금액 · 기산일 · 대상은 협약 때 입예협과 정하고 협약 후 발급합니다.", "보증보험증권 발급 이력은 다른 용역 계약(광고대행 계약보증) · 입주박람회 이행보증 가입 이력 아님"))
B.CSS += (".tbl.q17 td{padding:10px 12px;font-size:14.5px;line-height:1.42;vertical-align:middle}.tbl.q17 td.k{font-size:14.5px}"
          ".tbl.q17 td.ev{font-size:13.5px;color:var(--gold);font-weight:700}")

# ------------------------------------------------------------ 07-18 참가 제한 · 효력 · 서약
LIM = [
    ("6항 1) · 2) 공정 저해 · 부정 · 불이행 · 담합 · 방해 · 서류 거부 · 손해", "해당 없음"),
    ("6항 3) 과도한 행사비로 단가 상승", "해당 없음 · 업체 참가비 정액 · 공구가 연동 없음 · 행사장은 규모에 맞게"),
    ("6항 4) · 5) 선정 관계자 연관 · 금품 · 향응", "해당 없음"),
    ("6항 6) · 7) 담합 · 허위 서류 · 타 단지 선정 취소", "해당 없음"),
    ("6항 8) 계약 ‘A’ 물품 → 매장 ‘B’ 변경 전례", "전례 없음 · 계약서 모델명 · 출시연도 기재로 예방"),
    ("8항 제안서 효력", "제안서 = 계약서와 같은 효력 · 협의회 유리 해석 · 사전 서면 승인 없이 수정하지 않음"),
    ("9항 1) ~ 4) 서류 반환 · 이의 제기 · 성실 이행 · 협의회 해석", "수락 · 정당한 사유 없는 이의 제기 없음 · 제안 · 협약 조건 성실 이행"),
    ("9항 5) 서류 · PT 영상 카페 게시", "동의 · 개인정보 서류는 가림본으로 제출 · 게시용 공개본이 필요하면 같은 날 제출"),
    ("9항 6) 하도급 · 재위탁 금지", "주관사 업무는 직접 수행 · 하청 · 재수임 없음(별지 2 3항) · 전문업체는 사전 서면 승인 시만"),
    ("별지 2 ~ 5 서약", "확약 및 이행 · 하자 보수 이행 · 비밀유지 · 청렴계약 서약을 원문 그대로 날인 · 선정 여부와 관계없이 지킴"),
]
new("std", sec=S0, title=T_LIMIT,
    lead="공고 6항 참가 제한 · 무효 사유, 8항 제안서 효력, 9항 유의사항과 별지 서약을 확인했습니다.",
    body=ftable(["공고 · 서식", "엣지컴퍼니 확인"], ["40%", "60%"], "".join(
        f'<tr><td class="k">{t(a)}</td><td>{t(b)}</td></tr>' for a, b in LIM), "lm9"),
    kp=("서약서는 [[원문 그대로]] 날인했고, 선정 결과와 관계없이 지킵니다.", "결격 이력(형사처분 · 분쟁 · 소송 · 선정 취소 · 물품 변경 · 체납) 없음 확인 · 적용 범위 질의는 협의회 회신대로 따름"))
B.CSS += ".tbl.lm9 td{padding:9px 12px;font-size:14.5px;line-height:1.4}.tbl.lm9 td.k{width:40%;font-size:14.5px}"

# ------------------------------------------------------------ 08장 · 선택 항목 가격표(본부장 10-23 · 판교 'A 고르면 다 해주냐' 문의 → 인계 규칙 7개)
# 단가는 본부장 확인값만 — 상품권 외 항목은 '협의 단가'(지어내지 않음). 할인형 항목 = 차감 0원(판교 회신과 같은 기준).
T_MENU = "선택 항목 [[가격표]] · 담는 예시 3가지"
_MB = D.FUND_TOTAL                       # 10,065만원
_g5, _g10 = HH * 5, HH * 10              # 상품권 5만 · 10만 × 671세대(만원)
_TAG = {"차감": ("예산 차감", "tg-c"), "무료": ("기본 무료 · 차감 0원", "tg-f"), "할인": ("할인형 · 차감 0원", "tg-f"), "업체": ("업체 제공 · 별도", "tg-v"), "견적": ("설치 시 별도 견적", "tg-e")}
MENU_ROWS = [  # (구분, 항목, 기준, 1억 65만원에서, 꼬리표)
    ("A", "백화점 상품권", "세대당 5만원 또는 10만원 · 세대에 현물 직접", f"{_won(_g5)} / {_won(_g10)}", "차감"),
    ("A", "방문 선물 · 실측 · 샘플하우스 · VR · 3D", "박람회 방문 세대 · 타입별 · 대표 타입", "협의 단가", "차감"),
    ("A", "사전점검 대행 할인", "최대 50% 할인 · 대행업체 제공", "0원", "할인"),
    ("B", "공용물품 · 라돈 측정 · 하자진단 보고서 · 커피차 등", "입예협이 고른 항목 · 수량", "협의 단가", "차감"),
    ("C", "커뮤니티 · 공용부 조명 개선 시공", "진단 · 개선안 뒤 입예협 · 관리주체 승인 시", "별도 견적", "견적"),
    ("업체", "박람회 상품권 · 계약 사은품 · 경품 · 정회원 혜택 · 현장 할인", "참여업체 확정 후 입예협 승인", "0원", "업체"),
]


def _menu_tbl():
    return table(["구분", "항목", "기준", f"{_won(_MB)}에서", "꼬리표"], "".join(
        f'<tr><td class="g">{a}</td><td class="k">{t(b)}</td><td>{t(c)}</td><td class="r">{t(d)}</td>'
        f'<td><span class="tgx {_TAG[e][1]}">{_TAG[e][0]}</span></td></tr>' for a, b, c, d, e in MENU_ROWS), "mnu")


def _mix(no, name, gift, rest):
    w = round(100 * gift / _MB) if gift else 0
    bar = (f'<div class="mbar"><div class="mf" style="width:{w}%"></div>'
           f'<div class="ml">{"상품권 " + _won(gift) + " · " if gift else ""}남은 {_won(_MB - gift)}</div></div>')
    return f'<div class="mx"><div class="mh"><em>{no}</em><b>{name}</b></div>{bar}<p>{t(rest)}</p></div>'


new("std", sec=S0, title=T_MENU,
    lead=f"{HH}세대 × 세대당 15만원 상당 = {_won(_MB)} 상당 안에서 입예협이 골라 담습니다. A · B · C는 세트가 아니라 선택 목록입니다.",
    body=('<div class="nb"><div class="mnx"><div class="mnl">' + _menu_tbl() + '</div><div class="mnr"><h4>담는 예시 3가지</h4>'
          + _mix("①", "상품권형", _g10, "상품권 세대당 10만원 · 남은 금액으로 방문 선물 · B 항목")
          + _mix("②", "균형형", _g5, "상품권 세대당 5만원 · 남은 금액으로 실측 · VR · 3D · 방문 선물 · B 항목")
          + _mix("③", "서비스형", 0, "상품권 없이 B 항목 · 실측 · VR · 3D · 방문 선물로 구성")
          + '</div></div></div>'),
    kp=(f"고른 항목의 합계가 [[{_won(_MB)} 상당]] 안에 들어오도록 맞춥니다 - 사용 내역은 공개합니다.",
        "‘협의 단가’ 항목은 협약 때 입예협과 단가 · 수량을 정함 · 할인으로 드리는 항목은 차감하지 않음 · 업체 제공 혜택은 별도"))
B.CSS += (".mnx{display:grid;grid-template-columns:1.62fr 1fr;gap:18px;flex:1;min-height:0}"
          ".tbl.mnu td{padding:7px 9px;font-size:13px;line-height:1.38}.tbl.mnu td.g{width:42px;text-align:center;font-weight:800}.tbl.mnu td.k{font-size:13.5px;width:33%}"
          ".tbl.mnu td.r{white-space:nowrap;color:var(--gold);font-weight:800;font-variant-numeric:tabular-nums}"
          ".tgx{display:inline-block;font-size:11.5px;font-weight:800;border-radius:99px;padding:3px 9px;white-space:nowrap}"
          ".tgx.tg-c{background:var(--gold);color:#0d1e33}.tgx.tg-f{border:1.5px solid #9fd3c7;color:#9fd3c7}"
          ".tgx.tg-v{border:1.5px dashed rgba(255,255,255,.55);color:var(--sub)}.tgx.tg-e{border:1.5px solid rgba(255,255,255,.35);color:var(--sub)}"
          ".mnr{display:flex;flex-direction:column;gap:12px;min-height:0}.mnr h4{font-size:15px;color:var(--gold);letter-spacing:.04em}"
          ".mx{border:1px solid var(--line);border-radius:12px;padding:11px 14px;display:flex;flex-direction:column;gap:8px}"
          ".mx .mh{display:flex;align-items:baseline;gap:8px}.mx .mh em{font-style:normal;color:var(--gold);font-weight:800}.mx .mh b{font-size:17px}"
          ".mbar{position:relative;height:28px;border-radius:7px;border:1.5px dashed rgba(200,168,106,.7);overflow:hidden}"
          ".mbar .mf{position:absolute;left:0;top:0;bottom:0;background:#C8A86A}"
          ".mbar .ml{position:absolute;right:10px;top:0;bottom:0;display:flex;align-items:center;font-size:12px;font-weight:800;color:var(--ink);white-space:nowrap}"
          ".mx p{font-size:12.5px;color:var(--sub);line-height:1.4}")


# 대응표 쪽 번호 — 재배치 뒤 제목으로 찾는다(reorg에서 바뀐 제목은 바뀐 뒤 제목)
PGREF = {
    "hist": T_HIST, "people": T_PEOPLE, "r500": T_R500,
    "guard4": "공동구매 단가를 지키는 [[4가지 장치]]", "x10": "[[최저가 차액 10배]] 보상",
    "rule1": T_RULE1, "rule2": T_RULE2, "cpl": T_CPL, "as": T_AS, "safe": T_SAFE, "expo": T_EXPO,
    "fund": T_FUNDCH, "menu": T_MENU,
    "prom": T_PROM, "voice": T_VOICE, "map": T_MAP, "work1": T_WORK1, "work2": T_WORK2, "same": T_SAME, "check": T_CHECK,
    "desk": T_DESK, "expert": T_EXPERT, "council": T_REQ, "comm": T_COMM, "lx": T_LX, "sameq": T_SAMEQ, "pm": T_PM,
    "mon": T_MON1, "qual": T_QUAL, "qual2": T_QUAL2, "ban": T_LIMIT,
    "call": "주관 [[콜센터]]와 선보상", "flow": "클레임 [[처리 흐름]]과 CRM 관리", "bond24": "계약이행 · 하자보증 [[24개월]]", "k1000": "1,000세대 이상 [[주관 단지]]",  # 법정 10-23: 약속 10 · 요약 근거 쪽
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

# 22p 지사망: 직영 4곳 + 협력 8곳 = 전국 12개 지사망(2026.10 확정). 본부장 10-19: 청주 지사 1순위(대형 조명 매장 소재지) → 청주 · 대전 순.
i = find("전국 지사망")
B.PAGES[i][1]["title"] = "전국 지사망 · [[직영 4곳 + 협력 8곳]]"
# 본부장 10-22: 경인 지사(평택 비전동 866-3 · 쇼룸 · 입예협 미팅 공간) 추가 → 지역 거점 5곳 + 협력 네트워크 7곳(경인은 협력 → 거점) · 수도권 단지는 경인 지사가 거점
B.PAGES[i][1]["lead"] = "지역 거점 3곳이 책임지고, 협력 네트워크 9곳이 접수 · 연결을 돕습니다."
# 본부장 10-22 저녁: 경인 · 청주 = 개인사업자 지사의 쇼룸 · 사무실 무상 사용 합의(간판 우리 제작 · 설치) → '직영' 표기 금지 · 대전 · 부산은 주소 · 사용 합의 확인 전까지 협력 네트워크
B.PAGES[i][1]["body"] = B.cards([
    dict(lb="BRANCH 01", big="경인", nm="경인 지사(평택)", ds="상설 쇼룸 · 시공 · A/S 출동. 수도권 · 경기 남부 거점."),
    dict(lb="BRANCH 02", big="청주", nm="충북 청주 지사", ds="상설 쇼룸 · 사무실. 충청권 거점."),
    dict(lb="BRANCH 03", big="울산", nm="울산 본사", ds="본사·쇼룸. 시공팀 상주."),
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
COVER = dict(kind="stats", pill="입주박람회 주관사 제안서",
             tag=f"박람회를 여는 회사가 아니라, 단지를 완성시키는 회사.<br>{D.SITE['households']:,}세대 단지의 입주를 입주 후 1년까지 책임지겠습니다.")
TITLE_H1 = "롯데캐슬 나리벡시티<br><em>입주박람회 주관사 제안서</em>"
COVER_TOP = """<div class="top"><div><div class="logo">EG</div><div class="en">EDGE COMPANY</div></div>
<div class="who">주식회사 엣지컴퍼니<br>입주박람회 전문 주관사</div></div>"""


def p_cover():
    sub2 = f'<div class="sub2"><div><i>제출처</i><b>{D.CLIENT}</b></div><div><i>제안사</i><b>{D.COMPANY}</b></div></div>'
    # 표지 이미지 = 슬롯 'cover'(data.IMG) — 네이비 배경에 스며들도록 위·왼쪽을 배경색으로 페이드. 파일이 없으면 이미지 없이 중립 디자인
    im, _own = slot("cover")
    art = (f'<div class="cvart cvx osc day"><img src="assets_ins/{im}.jpg" alt="">'
           f'<span class="credit">{D.SITE["name"]} 조감도 · 홍보용 이미지 · 실제와 다를 수 있음</span></div>') if im else ""
    return f"""<section class="page cv cv4">{art}{COVER_TOP}
<div class="mid"><span class="pill">{COVER['pill']}</span>
<h1 class="cvx">{TITLE_H1}</h1>
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
     ("04", "안전망", ["예치금 1억·보증 24개월", "업체 하자보증·패널티", "클레임 보상 규정", "콜센터·선보상"])],
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
    _cr = D.LX_CAP  # 나리벡: 단지 이미지 없음 → 타 단지 연출 예시 캡션(단지명 없이)
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
<div class="addr"><b>경인 지사</b> 경기도 평택시 비전동 866-3(상설 쇼룸 · 수도권 시공 · A/S 관리)<br><b>울산 본사</b> {D.ADDRESS}(계약 · 책임)<br>
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
            '<div class="lb">STANDARD</div><div class="big"><small class="mxs">약</small>35<small>% 할인</small></div>')
    return sub(s, '</div></div></div>\n<div class="kp">',
               '</div></div></div>\n<div class="notex" style="margin-top:14px">※ 평당 가격은 2026년 6월 기준 기본 소비자가이며, 변동될 수 있습니다.</div>\n<div class="kp">')


B_p_pricing = B.p_pricing
B.p_pricing = p_pricing


def p_closing(no, sec):
    n = D.FUND_HH * D.FUND
    items = [(f"세대당 {D.FUND}만원 발전지원금", f"전 세대 {D.FUND_HH:,}세대 기준 · 총 {won(n)}(부가세 포함)"),
             ("하자 예치금 1억 · 보증보험 24개월", "엣지컴퍼니 자산으로 예치 · 금액 · 기산일은 협약 때 확정"),
             ("입예협 전용 8가지 무상 지원", "별도 비용 없음 · 자체 인력"),
             ("유상옵션 중복 확인 · 가격 공개표", "유상옵션과 겹치는 품목 사전 확인 · 시공비·추가금 포함 공개"),
             ("시공 품목 인근 지역업체 90% 선정", "48시간 A/S가 가능한 거리"),
             ("최저가 차액 10배 보상", "온라인·시공 품목 제외 · 단가표 사전 공개 · 현장 가격 변경 없음"),
             ("48시간 하자보수 · 무상 A/S 최소 2년", "업체·품목별 기간 상이 · 주관 창구 입주 후 1년 · 접수 365일 · 24시간 내 회신"),
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
    band = (f'<div class="kp"><b>KEY POINT</b><span>약속 10가지 · <em>{PG("prom")}</em> · 평가 요소 찾아보기 · <em>{PG("map")}</em>'
            f'<small>공고 업무범위 1) ~ 8) · 참가자격 17 · 참가 제한 · 제안서 효력 대응 · {PGS(["work1", "qual", "ban"])}</small></span></div>')
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
    # 본부장 10-23(판교 문의): '패키지'는 세트로 읽힘 → '선택 항목'(제목 · 띠 · 본문 · 요약 모두). 남으면 중단
    for _a, _b in [("혜택 패키지 A · B · C", "선택 항목 A · B · C"), ("혜택 패키지 [[A · B · C]]", "선택 항목 [[A · B · C]]"),
                   ("혜택 패키지 예시", "선택 항목 예시"), ("세대 혜택 패키지와", "세대 혜택 선택 항목과"), ("세대 혜택 패키지", "세대 혜택 · 선택 항목"),
                   ("15만원 상당 패키지 A", "15만원 상당 선택 항목 A"), ("15만원 패키지 A", "15만원 선택 항목 A"), ("15만원 패키지 선택 항목", "15만원 상당 선택 항목"),
                   ("혜택 패키지로 받기", "선택 항목으로 받기"), ("혜택 패키지", "선택 항목"), ("패키지별", "항목별"), ("현금 또는 패키지", "현금 또는 선택 항목"),
                   ("세 가지 패키지에서", "세 가지 목록에서"), ("· 패키지 (안)", "· 선택 항목 (안)")]:
        doc = doc.replace(_a, _b)
    doc = re.sub(r"([ABC]) 패키지", r"선택 항목 \1", doc)
    # 법정 10-23(입예협 관점): '발전지원금'은 협의회에 주는 현금으로 읽힘 → 세대 혜택(영주자이 집행 사례 '발전지원으로'는 사실 그대로)
    for _a, _b in [("01 ~ 03 = 발전지원금 범위(주관사)", "01 ~ 03 = 세대 혜택 범위(주관사)"), ("발전지원금 집행 원칙", "세대 혜택 집행 원칙")]:
        doc = doc.replace(_a, _b)
    _fj = re.findall(r".{0,20}발전지원금.{0,20}", re.sub(r"<[^>]+>", " ", re.sub(r"<style.*?</style>|<script.*?</script>", "", doc, flags=re.S)))
    assert not _fj, ("'발전지원금' 남음", _fj[:4])
    doc = re.sub(r"패키지 ([ABC])", r"선택 항목 \1", doc)
    _pk = re.findall(r".{0,20}패키지.{0,20}", re.sub(r"<[^>]+>", " ", re.sub(r"<style.*?</style>|<script.*?</script>", "", doc, flags=re.S)))
    assert not _pk, ("'패키지' 표현 남음", _pk[:6])
    # 10-23 독립 검수(본부장 결정 'OEM 생산'): 기본틀 문구 중 근거가 약한 표현을 사실대로
    for _a, _b in [("직수입·자체 생산 라인에서 설계 사양 그대로 제작.", "직수입 · 전용 OEM 라인(사양 지정)에서 설계 사양 그대로 생산."),
                   ("단지 도면과 천장 사양에 맞춘 규격으로 직접 제작.", "단지 도면과 천장 사양에 맞춘 규격으로 OEM(사양 지정) 생산."),
                   ("선정 업체가 다른 업체에 하청 주는 행위를 계약으로 금지합니다.", "입예협 · 주관사 사전 승인 없는 재하도급을 계약으로 금지합니다."),
                   ("정비점검·육안점검·장비보고서", "장비점검·육안점검·장비보고서"),
                   ("체크리스트는 기본 지원(주관사 부담) · ", "체크리스트는 모든 세대에 · "),
                   ("광고비는 주관사 부담(단가 미전가)", "광고비는 공동구매 단가에 넘기지 않음"),
                   # 10-24 독립 검토: 이관 비용은 무상 A/S 기간 안 · 하자 판정 아님 · 실적 기준 통일 · 체험 서비스 = 선택 항목 A
                   ("업체 미응답 · 도산 건은 본사가 이관하고 비용 부담", "업체 도산 건은 본사가 이관(무상 A/S 기간 안 비용 부담) · 미응답 건은 선보상 후 업체 정산"),
                   ("A/S 비용<br>주관사 전액 부담", "무상 A/S 기간 안<br>이관 비용 주관사 부담"),
                   ("발견된 하자는 원인을 진단하고 보수 방안을 함께 제시합니다.", "발견된 하자는 원인 추정과 보수 참고 의견을 드립니다(하자 판정 아님 · 시공사 협의 자료)."),
                   ("2023년 이후 1,000세대 이상 12곳(입주 예정 포함).", "2023년 이후 1,000세대 이상 주관 10곳 + 입주 예정 2곳."),
                   ("불이행 업체는 주관사 콜센터 접수 → <em>즉시 패널티.</em>", "계약금은 5%까지, 기한 안 취소는 <em>전액 환불</em> - 업체가 미루면 주관사가 먼저 보상합니다."),
                   ("샘플하우스를 운영합니다.", "샘플하우스를 운영합니다(선택 항목 A)."),
                   ("사이즈 고민을 줄입니다.</div>", "사이즈 고민을 줄입니다(선택 항목 A).</div>")]:  # 본부장 10-24: '기본 지원 · 주관사 부담' 류 표시 안 함
        doc = doc.replace(_a, _b)
    doc = doc.replace("<span>주식회사 엣지컴퍼니 · 대표이사 고진식</span>", "<span>주식회사 엣지컴퍼니</span>")
    doc = re.sub(r'(<div class="tt">VR 촬영 · 3D 홈스타일링</div><div class="dd">[^<]*?)\.(</div>)', r"\1(선택 항목 A).\2", doc, count=1)
    # 본부장 10-15 밤: 조직 구성 쪽 KEY POINT — '박람회 현장 운영 인력 약 21명 …'은 줄을 바꿔 다음 문단으로(문구 그대로)
    assert doc.count("<small>박람회 현장 운영 인력 약 21명") == (0 if "요약제안서" in path else 1), "조직 구성 쪽 KEY POINT 소문구를 찾지 못함"
    doc = doc.replace("<small>박람회 현장 운영 인력 약 21명", '<small class="kpbr">박람회 현장 운영 인력 약 21명')
    doc = doc.replace("</style>", ".kp small.kpbr{display:block;margin-left:0;margin-top:3px}</style>", 1)
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
    _txt = _txt.replace("나리벡씨티개발", "").replace("2028.08.11", "")  # 시행사 정식 명칭 · ISO 유효기간만 허용  # 시행사 정식 명칭만 허용('씨티' 표기 금지)
    # 나리벡 착수 strategy 4-4: 고양 잔재 · 다른 단지 · 공개 문서 금지어(분양가 · 청약 · 계약률 · 미분양 · 부지 이력) · 과장 표현 · 지사 '직영' · '최대 10억'
    left = re.findall(r".{0,14}(?:고양|창릉|S-5|S5|LH|이수건설|759|1억 1,385|2028|파주|shin192004|덕양|KINTEX|킨텍스|오산|세교|아테라|금호|벌음|433|segyoartera|수원메쎄|"
                      r"분당|퍼스트빌리지|성남|낙생|933|1,400|행복주택|신혼희망|지웰|덕계|탕정|센터파크|철산|광명|조합원|조합 입예협|임예협|북수원|상주자이르네|상주 자이르네|상주시|경산|판교|"
                      r"가산점|발전기금|단지발전|입예협 지정|커뮤니티 집기|bd_|os_|화재 ·|배상책임보험 개최|"
                      r"미분양|미달|청약|계약률|분양가|오염|토양|특혜|최초|전국\s?최저가|100%|200%|유일|10\s*억|갈음|직영 지사|전담 배치|12명 전담|현장 사무소|셔틀|"
                      r"금·토·일|금 · 토 · 일|코엑스|COEX|씨티|업체당|표본 세대).{0,10}", _txt)
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
    print(f"나리벡 제안서 {len(B.PAGES)}쪽 → {out}")
    # 본부장 10-17: 요약제안서 — 고양 공고 제출서류에 없지만 만든다(제출서류 17 · 선택 자료). 숫자 · 문구는 위 제안서와 같은 D · ST 값(summary_nr.py)
    if "--no-summary" not in sys.argv and not COMPACT and not FULL:
        import summary_nr  # noqa: E402
        summary_nr.emit_summary(globals())


if __name__ == "__main__":
    build()
