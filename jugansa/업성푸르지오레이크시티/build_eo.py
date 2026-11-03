# -*- coding: utf-8 -*-
"""업성 푸르지오 레이크시티 1BL — 공동구매 주관사 제안서(입주박람회 운영계획 포함) 빌더(공고 7항 라 운영제안서 · 제안설명 자료 겸).
신분평 빌더(../신분평제일풍경채/build_sb.py, 10-31)를 복제(11-01)해 맞춤 장을 공고 5항 가 ~ 자로 새로 쓰고, build() 끝에서 eo.py가 5항 순서 + 부록으로 재배치한다.
아래 신분평 설명은 출발점 기록:

청주 빌더(../청주센트럴파크/build_cj.py, 10-31)를 복제해 맞춤 장(약속 10 · 바 1) ~ 7) 대응 · 다 1) ~ 8) · 가격 · 에스크로 · 소비자 보호 ·
취소 · 연기 · 면허 확인 · 청주 지역 업체 · 정산 보고 · 공정 원칙 · 자격 1) ~ 11) · 제출 1) ~ 10) · 개인정보 · 독점권)을 새로 쓰고,
build() 끝에서 sb.py가 평가표 8항목 순서(혜택 → 소비자 보호 → 서류 → 운영 → 협력업체 → 지역 실적 → 투명성 → 업무지원)로 재배치한다.
- 세대 혜택 = 세대당 15만원 상당(안) × data.FUND_TARGET(기본 'sale' = 일반분양 655세대) · 주관사가 직접 사서 세대에 현물 · 서비스로(공고 자 5)
- 거점 = 청주 지사(쇼룸 · 사무실 운영) · '직영' 금지 · 등기 지사 수에 넣지 않음(본부장 10-30)

사용: python build_sb.py --no-pdf --no-summary [--src <기본틀 PDF>] → python ../tools/light_build.py 신분평제일풍경채 → 엣지컴퍼니_신분평제일풍경채_입주박람회_주관사_제안서(_밝은시안).html/.pdf
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

NAME = "엣지컴퍼니_업성푸르지오레이크시티_공동구매_주관사_제안서"
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
.cv4 .tag2{font-size:19px;line-height:1.6;margin-top:0;max-width:520px;text-shadow:0 1px 8px rgba(13,30,51,.9)}
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
S0 = "제안 개요"
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
        return alt, alt.startswith("eo_")  # 업성: 대체 이미지는 타 단지 연출 예시(단지 이미지 아님)
    return None, False


ST = D.SITE
_rec_n, _rec_hh = len(D.RECORDS), sum(r[3] for r in D.RECORDS)
R3 = D.RECENT3_OS
_r3_n, _r3_hh = len(R3), sum(r[3] for r in R3)
R5 = D.R5Y  # 업성 검수 11-02: 최근 5년(22개 단지) · 옛 메모 — 최근 3년 500세대 이상 입주박람회 진행 20개 단지(주관 16 = 1,000세대 이상 8 + 주관사 협약서 3 + 500 ~ 999세대 9 · 본부장 10-19 모두 주관)
_r5_n, _r5_hh = len(R5), sum(r[2] for r in R5)
_types_txt = " · ".join(a for a, _ in ST["types"])
_types_full = " · ".join(f"{a} {n}" for a, n in ST["types"])

T_DIV = f"{ST['name']}을 위한 [[맞춤 제안]]"
T_MAP = "공고 제안서 [[주요내용 11개]], 이 쪽에 있습니다"
T_SITE = f"{ST['name']}, [[이런 단지]]입니다"
T_FIRST = "759세대 공공분양이라 [[먼저 챙길 것]]"
T_VOICE = "입주예정자가 먼저 묻는 [[다섯 가지]]"
T_FIT = "운영 실적 · 연혁 · [[기업신용평가]]"
T_R500 = f"최근 5년 500세대 이상 입주박람회 [[주관 {_r5_n}개 단지]]"
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
T_PEOPLE = "회사 수행 실적과 [[운영책임자 역할]]"
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
    ("03", "분양가 · 자금 부담", f"현장 가격 변경 없음 · 시중가 · 온라인 최저가 비교자료 · 계약금 {D.DEPOSIT_MAX}% 상한(맞춤 제작 · 본사 규정 품목 예외) · 카드 · 현금 동일가 · 설치 · 철거 · 배송을 포함한 확정 견적으로 추가 비용을 막습니다.", ["check", "x10", "rule1"]),
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
    lead="공고 5항 가 · 제출서류 나 운영 실적 - 최근 5년(공고일 2026.10.31 기준 · 박람회 개최 기준 · 입주 2023.04 ~ 2026.12) 500세대 이상 공동주택 중 당사가 입주박람회를 주관한 단지입니다. 2027년 입주 예정 단지는 넣지 않았습니다.",
    body=('<div class="nb"><div class="r5x">' + _r5tb(R5[:_half5], 1) + _r5tb(R5[_half5:], _half5 + 1) + '</div>'
          '<div class="r5b">'
          f'<div><b>{_r5_n}<small>개 단지</small></b><span>500세대 이상 입주박람회 주관</span></div>'
          f'<div><b>{_r5_hh:,}<small>세대</small></b><span>{_r5_n}개 단지 세대 합계</span></div>'
          f'<div><b>{len(D.R5Y_1000)}<small>개 단지</small></b><span>그중 1,000세대 이상 · 나머지 {len(R5) - len(D.R5Y_1000)}개 단지는 500 ~ 999세대</span></div>'
          f'<div><b>{D._EV_N5}<small>개 단지</small></b><span>증빙 첨부(제출서류 나 · NICE 연혁 · 공식 행사일정 · 카페 공지 · 협약서) · 나머지 요청 시 제출</span></div>'
          '</div></div>'),
    kp=(f"최근 5년 500세대 이상 [[{_r5_n}개 단지]]에서 입주박람회를 주관했습니다.",
        "단지명 · 세대수는 당사 실적 목록 기준 · 날짜는 입주 연월 · 실적 증명 · 협약서 · 행사일정 등 증빙은 제출서류 나"))
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
    ("계약", "표준 계약서에 취소·환불 규정 첨부 · 모델코드 · 포함 조건(설치·철거·배송·A/S) 명시", f"계약금 {D.DEPOSIT_MAX}% 이하(맞춤 제작 · 본사 규정 품목 예외) · 카드·현금 동일가"),
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
    lead="공고 5항 사 민원 접수 · 처리기한 - 입주민은 주관사 한 창구로 접수하고, 참여업체에는 추가 비용 · 추가 인력을 요구하지 않는 구조로 운영합니다.",
    body=('<div class="nb"><div class="pmx">'
          '<div class="pc"><h3><i>POLICY</i>A/S 정책</h3>'
          + B.rows([
              ("접수", f"콜센터 {D.TEL}(평일) · 카페 신문고 · 카카오채널(365일)"),
              ("기한", "[[24시간 안 1차 회신]](주말 · 공휴일 = 다음 영업일 12시) · 48시간 안 방문 일정 확정 · 긴급 하자 우선 배정"),
              ("기간", "시공 품목 무상 A/S 최소 2년(계약서 명시) · 주관 창구 = 협약 종료일(품목별 무상 A/S 만료일 중 가장 늦은 날)까지"),
              ("미응답", "업체가 24시간 무응답이면 주관사 개입 · 사실 확인 뒤 먼저 보상 · 업체와 나중에 정산"),
              ("기록", "접수 · 처리 · 지연 사유 기록 · 입주 지정기간 주 1회 · 이후 월 1회 보고"),
          ], title_w=86) + '</div>'
          '<div class="pc"><h3><i>NO EXTRA BURDEN</i>업체 부담을 늘리지 않는 제도</h3>'
          + B.rows([
              ("창구 비용", "콜센터 한 창구로 운영 - 업체별 상담 인력 · 창구 비용을 [[업체에 요구하지 않음]]"),
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
    lead="부록 · 입주박람회 운영계획(안)(공고 3항 마) - 계약을 재촉하는 자리가 아니라, 가족이 함께 확인하고 비교하는 자리로 만듭니다.",
    body=B.tiles([
        dict(lb="WHEN", nm="주말 포함 2 ~ 3일", ds=f"{ST['expo']}(예정) · 입주 3 ~ 2개월 전 · 날짜는 사전점검 일정에 맞춰 협의회 승인으로 확정"),
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
    ("응급 · 질병", "응급 키트 · AED 위치 안내 · 구급요원 배치 · 119 · 인근 병원 연락 체계"),
    ("인원 · 주차", "현장 운영 약 21명(주차 3 · 체크인 · 안내 5 포함) · 혼잡 시간 입장 조절 · 주차 안내"),
    ("업체 반입 · 철수", "부스 반입 · 철수 시간표 · 부스별 책임자 명찰 · 매일 개장 전 [[안전 점검표]] 서명"),
    ("보험", "영업배상책임보험 가입(증서 제출 · 만료 전 갱신) · 박람회 기간 행사장 기준 행사주최자배상책임보험 가입 · 개장 전 증권 사본 제출"),
]
new("std", sec=S0, title=T_SAFE,
    lead="부록 · 동선 · 주차 · 혼잡 · 안전관리(개최 시) - 행사장 안전과 현장관리 기준을 미리 정하고, 행사장이 확정되면 그 시설 기준에 맞춰 입예협과 최종 확정합니다.",
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
    lead=f"공고 5항 가 회사 현황 - 법인 설립({D.FOUNDED})부터 지금까지, 등기부 · 등록증 · 인증서 · NICE 연혁 · 협약으로 확인되는 기록만 적었습니다.",
    body=f'<div class="nb"><div class="hist"><ol>{"".join(_items[:_half])}</ol><ol>{"".join(_items[_half:])}</ol></div></div>',
    kp=("2023년부터 [[해마다]] 1,000세대 이상 입주박람회를 맡아 왔습니다.",
        "날짜 = NICE 연혁 기재 연월 · 출처: 법인등기부 · 전기공사업 등록증 · ISO 인증서 · NICE 연혁 · 세스코 협약"))

_lead_n = getattr(D, "STAFF_LEAD", 2) + sum(c for _, c, _ in D.STAFF)
PRO5 = [("전기", 3), ("도장", 2), ("조경", 1), ("간호사 · 협력(행사 시)", 1)]  # 신분평 법정: 타일 = 4대보험 명부에 없음(상주 10-26과 같게) → 뺌
new("std", sec=S0, title=T_PEOPLE,
    lead=f"공고 5항 가 담당 인력의 경력과 역할 - 회사가 수행해 온 실적과, 운영책임자가 {ST['name']}에서 맡을 역할입니다.",  # 본부장 10-15 밤: 이 쪽 단지 표기 = 정식 명칭
    # 대표 개인 경력(본부장 10-15) — NICE 기업신용평가보고서(제출서류 14 ③ 발췌) 13쪽 '대표자1' 약력 · 전기공사업 등록증 · ISO 인증서(3종 모두 최초 2025.08.12)로
    # 확인되는 사실만. 현장 총괄 문구는 본부장 10-15 확인. 경영경력 8년 8개월 = NICE 평가 당시(2026.05) 기재값.
    body=('<div class="nb"><div class="ppx">'
          '<div class="pp1 ceo"><i>대표이사</i><h3>고진식</h3><ul>'
          '<li><b>대표이사 고진식</b> - 울산과학대학교 전기과</li>'
          '<li>대한유화 2011 ~ 2018(최종 대리) → 엣지조명 대표 2019 ~ 2021 → <b>㈜엣지컴퍼니 창업 2022.02</b></li>'
          f'<li>전기공사업 등록(제 울산-00821호) 대표자</li>'
          '<li>ISO 9001 · 14001 · 45001 인증 취득 총괄 - 첫 인증 2025.08.12 · 박람회 · 전시회 기획 · 대행 / 전기공사 / 조명공사</li>'
          '<li><b>주관 박람회 전 과정 현장 점검</b>(참여업체 검수 · 부스 배치 · 당일 운영)</li>'  # 본부장 10-15 밤: '진두지휘' 삭제
          '<li>법인 대표이사 · 계약 최종 책임 · PT 동석</li></ul></div>'
          f'<div class="pp1"><i>주관사업 총괄 본부장 · 전담 총괄</i><h3>{D.MANAGER[0]}</h3><ul>'
          f'<li><b>총괄 본부장 {D.MANAGER[0]}</b> - {ST["name"]} 총괄 책임 · PT 참석(발표 · 질의) · <span style="white-space:nowrap">직통 {D.MANAGER[2]}</span></li>'
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
          f'<div><b>{D.cumulative()[-1][3]}<small>개 단지</small></b><span>누적 수임 {D.cumulative()[-1][4]:,}세대<br>(전신 실적 · 입주 예정 포함)</span></div>'
          '</div></div>'),
    # 본부장 10-15 밤: '전기 전공 · 조명 사업 출신 대표가 …' 대신 책임 구조(대표 · 본부장 · 4개 팀 = 이 쪽 카드 그대로 · 입주 후 1년 = 주관 창구 기간)
    kp=("대표 · 총괄 본부장 · 4개 팀이 협약부터 입주 후까지 [[한 팀으로]] 책임집니다.",
        "대표 약력 · 실적 증빙 = 제출서류 나(회사소개 · 실적 확인자료 · NICE 원본은 요청 시 열람) · 팀별 담당은 계약 시 명단 제출 · 실적 증빙은 제출서류 나(NICE 연혁 · 카페 공지 · BEXCO 행사일정 · 협약서)"))
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
    ("제3조 (계약금)", [f"계약금은 계약 총액의 <b>{D.DEPOSIT_MAX}% 이하</b>로 한다(계약금 {D.DEPOSIT_MAX}% 상한제). 다만 세대 실측 후 제작하는 맞춤 제작 품목({_CU} 등)과 제2조 ③의 본사 규정 품목(브랜드 본사 계약 · 렌탈 · 보험 · 통신 · 사전점검 대행)은 예외로 하며, 적용 품목과 계약금은 업체 선정 때 입예협 승인을 받아 단가표 · 계약서에 미리 표시한다.",
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
                                  "참여업체가 도산하거나 연락이 두절된 경우 협의회 승인과 계약자 동의를 받아 동종업체로 사후관리를 이관하고, 무상 A/S 기간 안의 이관 비용은 주관사가 전액 부담한다.",
                                  # 재검증 10-14: 새 증권 한도(울주대리점)는 확인 전 — 금액은 협약 때 확정(08 방안서 4장 · p89와 같은 조건부)
                                  "주관사의 보상 재원으로 하자 예치금 최대 1억원(엣지컴퍼니 자산으로 예치)과 계약이행 · 하자보증보험(보증기간 24개월 · 금액은 협약 시 확정 · 보증 대상 · 기산일은 계약서에 명시)을 둔다. 주관사의 추가 책임은 공동구매 품목에 한하며 건설 하자는 사업주체 · 시공사 책임으로 한다."]),
    ("제8조 (가격 보호 — 최저가 차액 10배 보상)", [f"공동구매 품목과 브랜드·모델명이 같은 새 제품이 계약 후 7일 이내에 인근({ST['local']}) 오프라인 매장에서 더 낮은 정상 판매가로 실제 판매된 사실이 구매 영수증(판매 매장 사업자 정보 · 모델명 · 금액 기재)으로 확인되고 주관사가 해당 매장에 판매 사실을 확인하면, 주관사는 차액의 10배를 보상하고 참여업체는 판매가를 조정한다(보상금은 주관사 부담 · 참여업체 부담을 늘리지 않음).",
                                         "보상액은 1건당 50만원(해당 품목 계약금액이 더 적으면 그 금액)을 넘지 않는다(같은 세대 · 같은 품목에는 1회). 견적서 · 가격표 · 구두 안내 가격은 보상 근거가 되지 않는다.",
                                         "온라인·홈쇼핑 판매, 시공 품목, 카드 청구할인·사은품·결합할인, 전시·리퍼 상품, 법인 특판, 한정 수량 행사가는 비교 대상에서 제외한다.",
                                         "계약자는 주관사 콜센터에 접수하고, 주관사는 사실 확인 후 7일 이내에 보상한다."]),
    ("제9조 (고지)", ["주관사는 이 규정을 박람회장 · 온라인 박람회에 게시하고, 입주예정자협의회 카페에는 입예협 승인 후 게시하며, 모든 공동구매 계약서에 첨부한다."]),
    ("제10조 (효력)", ["이 규정은 공동구매 운영기간(계약 체결일 ~ 입주 지정기간 종료일)에 체결된 계약에 적용하며, 사후관리 기간(품목별 무상 A/S 만료일까지) 동안 효력을 가진다."]),
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
    lead="공고 5항 바 단계별 취소 조건 · 환불 금액 · 처리기한 - 참여 품목별 계약 취소 및 환불 규정입니다. 모든 공동구매 계약서에 이 규정을 첨부합니다.",
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
    kp=("환불은 [[3영업일 이내]], 업체가 미루면 주관사가 [[사실 확인 뒤 먼저 보상]]합니다.", "공동구매 운영기간에 체결된 계약에 적용 · 사후관리 기간(품목별 무상 A/S 만료일)까지 효력"))
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
T_SEP = "발전기금, [[공구가와 따로]]입니다"
new("std", sec=S0, title=T_SEP,
    lead="‘발전기금을 내면 공구가가 오르지 않느냐’는 질문에 구조로 답합니다 - 발전기금은 주관사 몫에서 나가고, 공구가는 협의회가 직접 검증합니다.",
    body=('<div class="sepx"><div class="sepf">'
          '<div class="sb1"><i>업체</i><b>참가비 정액제</b><span>업체 참가비는 정액으로 - 공구가와 연동하지 않음</span></div><em>›</em>'
          '<div class="sb1 hl"><i>주관사</i><b>운영비 + 발전기금</b><span>박람회 운영비와 발전기금(세대당 ' + str(D.FUND) + '만원 기준 · 안)을 주관사 몫에서 부담</span></div><em>›</em>'
          '<div class="sb1"><i>협의회</i><b>발전기금</b><span>협의 시 금액 · 지급 시기 확정 · 공증 · 공구단가와 무관</span></div></div>'
          '<div class="sepn">공구가는 이 흐름과 따로 - <b>업체 공개 입찰 경쟁</b>과 <b>시중가 · 온라인 최저가 검수</b>로 정해집니다</div>'
          + B.tiles([
              dict(lb="01 · 정액", nm="참가비 정액제", ds="업체 참가비는 정액으로 받습니다. 발전기금을 공구가에 얹는 구조가 아닙니다."),
              dict(lb="02 · 공개", nm="단가표 사전 공개", ds="박람회 전 품목별 단가 · 할인율 · 모델코드를 입예협이 검수합니다. 현장 가격 변경 없음."),
              dict(lb="03 · 검증", nm="시중가 · 온라인 최저가 비교", ds="같은 조건 총액으로 비교하고, 입예협이 품목을 골라 직접 확인합니다."),
              dict(lb="04 · 보상", big="10", unit="배", nm="최저가 차액 보상", ds="인근 매장 동일 제품이 더 싸면 차액 10배 보상(구매 영수증 · 주관사 확인 · 1건당 최대 50만원 · 온라인·시공 품목 제외)"),
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
    lead="공고 5항 사 민원 · 지연 · 불량 · 폐업 대응 - 박람회 뒤 자주 생기는 컴플레인 예시와 처리 기준, 타 단지 해결 사례입니다. 접수부터 완료까지 주관 콜센터가 기록합니다.",
    body=table(["품목", "컴플레인 예시", "해결 방법", "처리 기준"], "".join(
        f'<tr><td class="k">{a}</td><td>{t(b)}</td><td>{t(c)}</td><td>{t(d)}</td></tr>' for a, b, c, d in CPL), "sm")
         + '<div class="hflow"><span>접수 · 콜센터 · 카카오</span><i>›</i><span>업체 연결</span><i>›</i><span>기한 추적</span><i>›</i>'
           '<span>미응답 시 주관사 선보상</span><i>›</i><span>완료 확인 · 결과 보고</span></div>'
         + '<div class="gcase"><div class="gch"><i>해결 우수 사례</i><b>타 단지 실제 응대</b><span>입주민 글 · 원문 재구성(닉네임 가림)</span></div>'
           '<div><i>입주민 카페 글 · 2024.10</i><b>A/S · 하자 즉시 처리</b><span>주관사와 청소 업체가 함께 처리 - 입주민이 카페에 감사 글을 남김</span></div>'
           '<div><i>단지 단톡방</i><b>입주 전날 긴급 재청소 연결</b><span>외부 업체 청소 뒤 생긴 문제도 입주 전날 재청소 업체를 연결</span></div>'
           '<div><i>타 단지 협의회</i><b>업체 응대 공유 · 감사 인사</b><span>업체 응대 내용을 협의회와 공유 - 협의회 측이 감사 인사를 전함</span></div></div>',
    kp=("컴플레인은 [[기한 안에 끝까지]] - 처리 결과를 입예협 결과보고서에 담습니다.", "처리 기준은 본 제안서 06 · 07장과 같습니다"))
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
        dict(lb="02", big="10", unit="배", nm="최저가 차액 보상", ds="인근 매장 동일 제품이 더 싸면 차액 10배 보상(구매 영수증 · 주관사 확인 · 1건당 최대 50만원 · 온라인·시공 품목 제외)"),
        dict(lb="03", big="추가할인", nm="실적 비례 추가할인", ds="업체 기대매출을 넘기면 계약 세대 잔금에서 추가할인. 할인율은 업체 입찰 조건으로 입예협과 확정."),
        dict(lb="04", big=str(D.DEPOSIT_MAX), unit="%", nm="계약금 상한", ds=f"계약금은 총액의 {D.DEPOSIT_MAX}% 이하(맞춤 제작 · 본사 규정 품목 예외), 잔금은 시공·설치 후. 현금·카드 동일가."),
    ]),
    kp="가격은 말이 아니라 [[사전 공개 단가 + 최저가 보장]]으로 검증받습니다.")


# ============================================================ 업성 푸르지오 레이크시티 1BL 맞춤 장 (착수 11-01 · 세대 혜택 = 계약 세대 기준 · 경인 지사 = 관리 거점)
# 공고 = 3항 업무 범위 가 ~ 바 · 4항 참가자격 가 ~ 사 · 5항 제안서 기재사항 가 ~ 자 · 7항 제출서류 가 ~ 아 · 9항 무효 · 10항 계약 · 유의사항.
# 장 순서 = 5항 가 ~ 자(eo.py가 마지막에 재배치) + 부록 입주박람회 운영계획(안)(3항 마) · 여기서는 장을 만들고 PGREF 키만 단다.
# 나가는 문서 = 유리한 것만: 분양가 · 청약 · 경쟁률 · 미달 · 미분양 · 무순위 · 계약률 · 본전 · 업체 수 · 카페 회원 수 · 임원 이름 쓰지 않음(finish 검사).
# 세대 혜택(5항 마 '발전기금') = 신청 기한까지 계약한 세대 기준 · 주관사가 직접 사서 드리는 선택 항목 15만원 상당(안) · 금액 · 방식은 협상 · 공증 때 확정 — 총액 · 전 세대 · 현금 표기 없음.
def _won(man):
    eok, rest = divmod(man, 10000)
    return (f"{eok}억 {rest:,}만원" if rest else f"{eok}억원") if eok else f"{rest:,}만원"


def ftable(head, widths, rows_html, cls=""):
    """열 폭을 고정(table-layout:fixed)한 표 — 밝은 시안에서 첫 열이 좁아지는 문제 방지."""
    cg = "".join(f'<col style="width:{w}">' for w in widths)
    th = "".join(f"<th>{h}</th>" for h in head)
    return f'<table class="tbl {cls}" style="table-layout:fixed"><colgroup>{cg}</colgroup><thead><tr>{th}</tr></thead><tbody>{rows_html}</tbody></table>'


def YN(flag, ok_text, ask):
    """본부장 확인 칸 — True면 문구, 아니면 노란 빈칸(확인본에만 · '--final'이면 멈춤). 사실을 지어내지 않는다."""
    return ok_text if flag else TODO(ask)


HH = ST["households"]
_cum = D.cumulative()[-1]
_tp = dict(ST["types"])
_t72 = sum(_tp[k] for k in ("72A", "72B", "72C", "72D"))
_t84 = sum(_tp[k] for k in ("84A", "84B", "84C", "84D"))
_t95 = _tp["95A"] + _tp["95B"]
assert _t72 + _t84 + _t95 == HH, (_t72, _t84, _t95)
BR = "경인 지사(평택)"   # 관리 · 출동 거점(탕정과 같은 생활권) · '직영' 금지 · 지사는 '확장 중 · 2026.11 초 등기 예정'까지
FUND_TXT = f"세대당 {D.FUND}만원 기준(안)"
FB = D.FUND_BASIS        # 신청 기한까지 계약한 세대
FD = D.FUND_DECIDE       # 금액 · 방식은 협상 · 공증 때 확정
SPLIT1, SPLIT2 = D.CONTRACT_SPLIT
CONSULT_TXT = YN(D.CONSULT, D.CONSULT or "", "상담 담당자 지정 - 본부장 확인")

# 5항 가 ~ 자 장(eo.py가 간지를 이 제목으로 만든다 · 목차 · 한 장 요약 쪽 번호도 이 제목으로 찾음)
EVAL = [  # (키, 장 번호, 장 이름, 간지 제목, 간지 소항목)
    ("ch1", "01", "회사 · 실적 · 인력 (5항 가)", "기록으로 확인되는 [[회사와 사람]]",
     ["회사 현황 · 법인 서류 · 재무", "최근 5년 운영 단지와 담당 업무", "실적 확인자료(NICE · 공식 행사일정 · 협약서)", "담당 인력 경력과 역할 · 운영책임자"]),
    ("ch2", "02", "일정 · 품목 · 업체 선정 · 교체 (5항 나)", "계약부터 사후관리까지 [[일정과 기준]]",
     ["계약 → 입주 → 사후관리 일정", "공동구매 운영기간 · 사후관리 기간 구분", "취급 품목 · 유상옵션 겹침 확인", "업체 선정기준 · 교체 방법 · 모집계획"]),
    ("ch3", "03", "대표 품목 가격 · 총 부담액 (5항 다)", "제품가가 아니라 [[총 부담액]]으로",
     ["모델 · 규격 · 시공 범위", "부가세 · 배송비 · 설치비 칸", "참고가격(타 단지 공개 단가)", "구매자 총 부담액 표기"]),
    ("ch4", "04", "가격 확정 시점 · 비교 방법 (5항 라)", "가격은 [[먼저 공개]]하고, 더 싸면 보상합니다",
     ["참고가격 → 실제 판매가 확정 시점", "판매 전 가격 비교 방법", "가격 적용기간", "최저가 차액 10배"]),
    ("ch5", "05", "입점비 · 수수료 · 광고비 · 발전기금 (5항 마)", "받는 것과 드리는 것을 [[먼저 밝힙니다]]",
     ["입점비 · 판매수수료 · 광고비", "부과 대상 · 방식 · 상한", "발전기금 = 협의회 지급 · 공증", "업체 제공 혜택은 별도"]),
    ("ch6", "06", "계약 · 대금 · 취소 · 환불 (5항 바)", "계약금부터 환불까지 [[입주민 편에서]]",
     ["품목별 계약 상대방 · 대금 수령자", "계약금 10% 상한 · 잔금 지급시기", "주문 · 시공 단계별 취소 조건", "환불 금액 · 처리기한"]),
    ("ch7", "07", "민원 · 지연 · 불량 · 폐업 대응 (5항 사)", "업체가 1차로, [[주관사가 끝까지]]",
     ["민원 접수 · 처리기한(24 · 48시간)", "납품 지연 · 시공 불량", "업체 폐업 · 연락 두절 시 이관", "참여업체 1차 책임 · 주관사 추가 책임"]),
    ("ch8", "08", "보험 · 보증 (5항 아)", "보험은 [[종류 그대로]], 보증은 [[계약서로]]",
     ["영업배상책임보험(현재 가입)", "행사배상책임보험(박람회 확정 시)", "계약 후 보증 제공계획", "청구 대상 · 증서 제출시기"]),
    ("ch9", "09", "카페 · 개인정보 · 재위탁 · 인계 (5항 자)", "카페는 [[참여업체만]], 정보는 [[운영에만]]",
     ["카페 홍보 · 계약 안내 · 모집 · 후기", "개인정보 수집 · 보관 · 이용 · 파기", "재위탁 절차 · 업체 변경", "미처리 업무 인계"]),
]
APPX = ("app", "10", "부록 · 입주박람회 운영계획(안)", "개최를 전제로 한 [[운영계획(안)]]",
        ["기본안 = 참가업체 참가비 운영 · 협의회 비용 청구 없음", f"주말 포함 2 ~ 3일(안) · {ST['expo']}(예정)", "동선 · 주차 · 안전 · 취소 · 연기", "경관조명 진단 · 핵심 제안"])
T_CH = {k: tt for k, _n, _nm, tt, _bl in EVAL + [APPX]}
T_CH9 = T_CH["app"]

T_ONE = f"한 장으로 보는 [[{ST['short']} 제안]] - 공고 5항 가 ~ 자"
T_PROM = f"{ST['short']}에 드리는 [[약속 10가지]]"
T_VOICE = "입주예정자가 먼저 묻는 [[다섯 가지]]"
T_MAPA = "공고 대응표 ① 업무 범위 [[3항 가 ~ 바]] · 참가자격 [[4항 가 ~ 사]]"
T_DOCS = "공고 대응표 ② 제출서류 [[7항 가 ~ 아]], 번호별로"
T_SITE = f"{ST['name']}, [[이런 단지]]입니다"
T_ITEMS = "72 · 84 · 95㎡ 타입에 맞춘 [[취급 품목]]"
T_OPT = "유상옵션과 [[겹치는 품목]]부터 확인합니다"
T_PRICE = "대표 품목 [[모델 · 규격 · 총 부담액]], 이렇게 적습니다"
T_EXPOPLAN = "입주박람회 운영계획(안) - [[횟수 · 일정 · 장소 · 규모 · 인력]]"
T_CANCEL = "행사 취소 · 연기, [[미리 정해 둡니다]]"
T_RECS = "최근 5년 운영 단지와 [[담당 업무]] · 실적 확인자료"
T_CAFE = "카페 운영 - [[참여업체만]] · 협의회 승인 · 후기 기준"
T_CHECK = "참고가격에서 [[확정가까지]] - 시점 · 비교 방법 · 적용기간"
T_CARE = "품목별 [[계약 상대방 · 대금 수령자]] · 단계별 취소 · 환불"
T_ESCROW = "계약금은 [[10%까지]], 잔금은 [[확인 뒤에]]"
T_DESK = "하자는 [[책임부터]] 나눕니다"
T_LICENSE = "업체 선정기준 · 확인은 [[원본으로]], 부실업체는 [[바로 교체]]"
T_LOCAL = "참여 예정 업체 - [[모집계획 · 확인 절차]] · 천안 · 아산권 우선"
T_ROLE = "협의회 · 사업주체 · 시공사 · 주관사, [[할 일을 나눕니다]]"
T_LX = "단지 외부 경관조명, [[입주 전에]] 진단합니다"
T_PM = "경인 지사 관리 · [[찾아가는 책임자]]"
T_STAFF7 = f"{ST['short']} [[담당 인력]] - 운영책임자 · 상담 담당자 · 역할"
T_MON1 = "계약부터 박람회 준비까지 ① [[2026.11 ~ 2028.12]]"
T_MON2 = "박람회 · 입주 · 사후관리까지 ② [[2029.01 ~ 사후관리 종료]]"
T_INCOME = "입점비 · 판매수수료 · 광고비 · 발전기금 [[명세]]"
T_REPORT = "정산 · 보고 · 인계, [[항목과 시점]]을 정해 둡니다"
T_FAIR = "입찰 무효 · 계약 유의사항, [[그대로 지킵니다]]"
T_QUAL = "참가자격 [[4항 가 ~ 사]], 공고일 현재 충족"
T_BOND = "참여업체 1차 책임 · [[주관사 추가 책임]] 이행방안"
T_INS = "보험 · 보증의 [[종류 · 금액 · 기간 · 청구 대상]]"
T_PRIV = "개인정보 수집 · 보관 · 이용 · 파기, [[이렇게 지킵니다]]"
T_TERMS = "재위탁 · 업체 변경 · 미처리 업무 [[인계 방법]]"
FEE_NOTE = "받지 않음 - 판매 · 소개 수수료(렌탈 · 통신 · 보험 · 대행 포함) 없음"
T_DIV = T_CH["ch1"]   # reorg가 찾는 간지(재배치 전 자리) — eo.py가 장마다 새로 만든다

new("divider", n="01", title=T_DIV, bl=EVAL[0][4])

# ------------------------------------------------------------ 한 장 요약 = 5항 가 ~ 자 ↔ 장 · 쪽
ONE = [
    ("ch1", "가", "회사 현황 · 최근 5년 운영 단지와 담당 업무 · 실적 확인자료 · 담당 인력 경력과 역할", "법인 서류 · 재무 · 최근 5년 주관 단지 · NICE 연혁 · 공식 행사일정 · 운영책임자(총괄 본부장) · 전담 PM"),
    ("ch2", "나", "계약 ~ 입주 ~ 사후관리 일정 · 취급 품목 · 참여업체 선정기준 · 교체 방법", "월별 일정 · 운영기간 / 사후관리 기간 구분(1항 바) · 타입별 품목 · 4단계 공개 심사 · 3단계 교체"),
    ("ch3", "다", "대표 품목 모델 · 규격 · 시공 범위별 가격 · 부가세 · 배송비 · 설치비 · 총 부담액", "품목별 표기 칸 · 참고가격(타 단지 2026.10 공개 단가) · 총 부담액 한 칸"),
    ("ch4", "라", "참고가격 · 실제 판매가 확정 시점 · 판매 전 비교 방법 · 가격 적용기간", "D-30 협의회 검수 · D-14 확정가 · 비교자료 공개 · 운영기간 내 같은 가격 · 차액 10배"),
    ("ch5", "마", "입점비 · 판매수수료 · 광고비 · 발전기금(공증)", "항목 · 부과 대상 · 방식 · 상한 · 발전기금 세대당 15만원 기준(안) · 협의회 지급 · 협의 시 확정 · 공증"),
    ("ch6", "바", "계약 상대방 · 대금 수령자 · 계약금 · 잔금 시기 · 단계별 취소 · 환불 금액 · 처리기한", "업체 명의 계약 · 계약금 10% 상한 · 잔금은 시공 확인 뒤 · 기한 안 전액 환불 · 3영업일"),
    ("ch7", "사", "민원 처리기한 · 납품 지연 · 시공 불량 · 폐업 · 연락 두절 · 1차 책임 · 추가 책임", "24시간 1차 회신 · 48시간 방문 일정 확정 · 선보상 · 이관 · 추가 책임 범위 · 한도"),
    ("ch8", "아", "보험 · 보증의 종류 · 금액 · 기간 · 보장내용 · 청구 대상 · 증서 제출시기", "영업배상책임보험(가입 중 · 증권 사본) · 행사배상(박람회 확정 시) · 계약 후 보증(금액 협약 시 확정)"),
    ("ch9", "자", "카페 홍보 · 계약 안내 · 모집 · 후기 · 개인정보 · 재위탁 · 미처리 업무 인계", "참여업체만 · 협의회 승인 · 명부 영업 이용 없음 · 재위탁 사전 승인 · 인계 목록 30일"),
]
new("std", sec="제안 개요", title=T_ONE,
    lead="공고 ‘5. 제안서 기재사항’ 가 ~ 자 순서 그대로 장을 나눴습니다. 기재사항을 위에서부터 보시면 같은 순서로 찾으실 수 있습니다.",
    body=('<div class="nb">' + ftable(["장", "5항", "기재사항", "엣지컴퍼니가 드리는 것", "쪽"], ["6%", "6%", "38%", "38%", "12%"], "".join(
        f'<tr><td class="n">{k[2:].zfill(2)}</td><td class="g">{g}</td><td class="k">{t(a)}</td><td>{t(b)}</td><td class="pg">{PG(k)} ~</td></tr>' for k, g, a, b in ONE)
        + f'<tr><td class="n">10</td><td class="g">3항 마</td><td class="k">입주박람회 운영계획(개최 여부 · 횟수 · 장소 · 비용 부담은 별도로 정함)</td><td>기본안 = 참가업체 참가비 운영 · 협의회 비용 청구 없음 · 개최 여부 · 횟수 · 장소는 협의회와 정함</td><td class="pg">{PG("app")} ~</td></tr>', "one8")
          + '</div>'),
    kp=("5항 [[가 ~ 자 순서]] 그대로 - 항목마다 쪽 번호를 붙였습니다.", "쪽 번호 = 슬라이드 오른쪽 위 번호 · 이 제안서는 제안설명 자료를 겸합니다(7항 라) · 협상 내용은 서면으로 계약에 반영(10항 차)"))
B.CSS += (".tbl.one8 td{padding:8px 10px;font-size:13.5px;line-height:1.38;vertical-align:middle}.tbl.one8 td.k{font-size:14px}"
          ".tbl.one8 td.n{font-weight:800;color:var(--gold);text-align:center}.tbl.one8 td.g{font-weight:800;color:var(--gold);text-align:center;white-space:nowrap}"
          ".tbl.one8 td.pg{white-space:nowrap;color:var(--gold);font-weight:800}")

# ------------------------------------------------------------ 약속 10가지
PROM10 = [
    ("발전기금 · 세대당 15만원 기준(안)", f"협의회에 지급 · {FD} · 공구가에 얹지 않음 · 공식 절차 밖 약속 없음", ["fund", "menu"]),
    ("같은 기준 · 선택권 보장", f"{HH:,}세대 모두 공구가 · 박람회 초대 · A/S 기준이 같음 · 특정 제품 · 업체 구매를 권하거나 끼워 팔지 않음", ["site", "priv"]),
    ("가격 먼저 공개 · 총 부담액", "박람회 30일 전 협의회 단가 검수 · 14일 전 확정가와 같은 조건 일반 판매가 비교자료 공개(협의회 승인 후) · 부가세 · 배송 · 설치 포함 총액", ["price", "check"]),
    ("최저가 차액 10배 보상", "인근 매장 · 구매 영수증 · 주관사 확인 · 1건당 최대 50만원 · 온라인 · 시공 품목 제외 · 주관사 지급", ["check", "x10"]),
    (f"계약금 {D.DEPOSIT_MAX}% 상한 · 잔금은 확인 뒤", "맞춤 제작 · 본사 규정 품목 예외 · 대금은 계약서에 적힌 업체 명의로만 · 잔금은 시공 · 설치 · 계약자 확인 뒤", ["rule1", "escrow"]),
    ("24시간 · 48시간", "24시간 안 1차 회신(주말 · 공휴일 = 다음 영업일 12시) · 48시간 안 방문 일정 확정 · 업체가 24시간 무응답이면 주관사 개입", ["call", "as"]),
    ("무상 A/S · 업체 이관", "시공 품목 최소 2년(브랜드는 제조사 보증) · 업체 폐업 · 연락 두절 시 대체 업체로 이관(협의회 승인 · 계약자 동의)", ["care", "rule2"]),
    ("주관사 추가 책임", "업체 미이행 · 폐업 · 연락 두절 시 공동구매 품목에 한해 계약서에 정한 보증 금액 안에서 주관사가 처리 · 건설 하자 = 사업주체 · 시공사", ["bond", "desk"]),
    ("기간을 나눠 계약", "공동구매 운영기간(계약 ~ 입주 지정기간 종료)과 사후관리 기간(~ 품목별 무상 A/S 만료)을 나눠 계약서에 적음(공고 1항 바)", ["mon2", "care"]),
    ("수수료 · 정산 공개", "입점비 · 수수료 · 광고비 · 발전기금의 항목 · 부과 대상 · 방식 · 상한 공개 · 판매 수수료 없음 · 정산 보고 항목 · 시점 사전 확정", ["income", "report"]),
]
new("std", sec="제안 개요", title=T_PROM,
    lead="심사하시는 분이 먼저 보실 한 장입니다. 모든 숫자에 근거 쪽을 함께 적었고, 협상 내용은 서면으로 남겨 계약에 반영합니다(공고 10항 차).",
    body=table(["NO", "약속", "조건 · 기준", "근거"], "".join(
        f'<tr><td class="n">{i:02d}</td><td class="k">{t(a)}</td><td>{t(b)}</td><td class="pg">{PGS(ks)}</td></tr>'
        for i, (a, b, ks) in enumerate(PROM10, 1)), "m9 pr10"),
    kp=("[[지킬 수 있는 숫자]]만 적었습니다 - 숫자마다 근거 쪽이 있습니다.",
        "증명할 수 없는 과장 표현은 쓰지 않았습니다 · 발전기금 금액 · 지급 시기는 협의 시 확정 · 공증"))
B.CSS += ".tbl.pr10 td{padding:6.5px 12px;font-size:14px}.tbl.pr10 td.k{width:22%;font-size:15px}"

# ------------------------------------------------------------ 공고 대응표 ① 3항 업무 범위 · 4항 참가자격
MAP_A = [
    ("3항 가", "수요 조사 · 공동구매 품목 · 운영일정 제안", "수요조사 → 타입별 품목 · 유상옵션 겹침표 → 월별 일정", ["items", "opt", "mon1"]),
    ("3항 나", "업체 모집 · 사업자등록 · 자격 · 실적 · 사후관리 능력 확인", "공개 모집(천안 · 아산권 우선) · 4단계 심사 · 원본 대조 · 공공 조회", ["screen", "license", "local"]),
    ("3항 다", "가격 · 사양 · 시공 범위 · 추가비용 협의 · 안내", "모델 · 규격 · 총 부담액 칸 · D-30 검수 · D-14 공개", ["price", "check"]),
    ("3항 라", "카페 홍보 · 계약 안내 · 모집 · 후기(참여업체 한정) · 납품 · 시공 일정 관리", "협의회 승인 후 게시 · 참여업체만 · 시공 일정표 · 주 1회 보고", ["cafe", "mon2"]),
    ("3항 마", "입주박람회 운영계획 제안(개최 여부 · 횟수 · 장소 · 비용은 별도)", "기본안 = 참가업체 참가비 운영 · 협의회 비용 청구 없음 · 개최 여부 · 횟수 · 장소는 협의회와 정함", ["expoplan", "cancel"]),
    ("3항 바", "취소 · 환불 · 하자 민원 접수 · 업체 처리 확인 · 협의회 통보", "주관 콜센터 한 창구 · 처리 추적 · 월 1회(입주 지정기간 주 1회) 보고", ["as", "care", "report"]),
    ("4항 가", "관련 사업자등록 · 최근 5년 공동구매 · 박람회 운영 실적", f"법인 설립 2022.02 · 최근 5년 500세대 이상 주관 {len(D.R5Y)}개 단지 · " + YN(D.BIZ_ITEM_OK, "사업자등록 업태 · 종목 해당", "사업자등록 종목(공동구매 · 행사 대행) 해당 여부 - 본부장 확인"), ["qual", "recs"]),
    ("4항 나", "운영책임자 · 상담 담당자 지정 · 참여업체 업무 · 사후관리 관리", f"운영책임자 = 주관사업 총괄 본부장 {D.MANAGER[0]} · 상담 담당자 = " + CONSULT_TXT, ["staff", "pm"]),
    ("4항 다", "국세 · 지방세 체납 없음", f"국세 · 지방세 납세증명서({D.ISSUE['tax']} 발급)", "제출서류 다(03)"),
    ("4항 라", "개인정보 수집 · 보관 · 이용 · 파기 관리방안", "본인 입력 · 동의 범위만 · 명부 영업 이용 없음 · 파기 확인서", ["priv"]),
    ("4항 마", "협의회 운영진 · 사업관계자와의 이해관계 공개", YN(D.CONFLICT_OK, "이해관계 없음 · 확약서로 공개(제출서류 바)", "이해관계 '없음' - 본부장 확인"), ["fair"]),
    ("4항 바", "계약이행 · 피해보상 보험 또는 보증 제공계획", "영업배상책임보험 가입 중 · 행사배상 박람회 확정 시 · 보증 금액은 협약 시 확정", ["ins", "bond24"]),
    ("4항 사", "협의회 계약상 해지 이력 · 소송 이력(진행 중 포함) 없음", YN(D.HISTORY_OK, "해지 · 소송 이력 없음 · 확인서(제출서류 아)", "해지 · 소송 이력 '없음' - 본부장 확인"), ["fair"]),
]


def _map_tbl(rows, head="공고"):
    return ftable([head, "공고 내용", "엣지컴퍼니 답", "쪽"], ["10%", "36%", "40%", "14%"], "".join(
        f'<tr><td class="g">{a}</td><td class="k">{t(b)}</td><td>{t(c) if "⟦" not in c else c}</td><td class="pg">{ks if isinstance(ks, str) else PGS(ks)}</td></tr>' for a, b, c, ks in rows), "m9 mpv")


new("std", sec="제안 개요", title=T_MAPA,
    lead="공고 3항(업무 범위) 가 ~ 바와 4항(참가자격) 가 ~ 사를 빠짐없이 담았습니다 - 항목마다 답과 쪽 번호입니다.",
    body=_map_tbl(MAP_A),
    kp=("업무 범위 [[6개]] · 참가자격 [[7개]] - 모두 답했습니다.", "5항 기재사항 가 ~ 자 = 한 장 요약 쪽 · 7항 제출서류 = 다음 쪽 · 쪽 번호 = 각 장 우측 상단"))
B.CSS += ".tbl.mpv td.g{white-space:nowrap;font-size:13px;font-weight:800;color:var(--gold)}.tbl.mpv td{padding:7px 11px;font-size:13.5px;line-height:1.36}.tbl.mpv td.k{font-size:14px}"

# ------------------------------------------------------------ 공고 대응표 ② 7항 제출서류 가 ~ 아(번호별 PDF)
DOCS7 = [  # (파일 번호, 7항, 서류, 엣지컴퍼니 제출 내용)
    ("00", "-", "자료 목록", "파일 번호 · 이름 · 쪽 · 발급일(6항 나 '파일을 나누면 자료 목록 첨부')"),
    ("01", "가", "입찰참가 신청서 · 사업자등록증 사본 · 법인등기사항증명서", f"신청서(자체 양식 · 대표이사 직인) · 등록증 · 등기({D.ISSUE['reg']} 발급 · 개인정보 가림)"),
    ("02", "나", "회사소개서 · 담당 인력 현황 · 최근 5년 운영 실적표 · 실적 확인자료", f"회사 개요 · 인력 현황(4대보험 명부 {D.ROSTER_DATE} · 가림) · 실적표 · NICE 연혁 · 공식 행사일정 · 협약서"),
    ("03", "다", "국세 · 지방세 납세증명서", f"{D.ISSUE['tax']} 발급 · 유효기간 안 · 휴대번호 가림"),
    ("04", "라", "운영제안서 · 제안설명 자료 · 대표 품목 가격표 · 추가비용 및 수수료 명세서", "이 제안서(제안설명 자료 겸) · 가격표 · 수수료 명세서 · 붙임 타 단지 공개 단가표(참고)"),
    ("05", "마", "취소 · 환불 · 사후관리 계획서 · 보험 가입증명서 · 계약 후 보증 제공계획", "계획서 · 영업배상책임보험 증권 사본(종류 그대로) · 보증 제공계획(금액 협약 시 확정)"),
    ("06", "바", "청렴 · 이해관계 공개 · 개인정보 보호 · 비밀유지 확약서", "확약서 1부(대표이사 직인)"),
    ("07", "사", "참여 예정 업체 현황 · 자격자료(미정 → 모집계획 · 확인 절차)", "업체는 선정 뒤 공개 모집 → 모집계획 · 확인 절차 · 천안 · 아산권 우선"),
    ("08", "아", "입주예정자협의회 계약 해지 · 소송 이력 확인서", "확인서 1부(대표이사 직인)"),
]
new("std", sec="제안 개요", title=T_DOCS,
    lead="공고 7항 제출서류 가 ~ 아를 서류 번호별 PDF로 나누고, 자료 목록(00)을 함께 냅니다. 별도 서식이 없어 자체 양식으로 작성했습니다.",
    body=('<div class="nb">' + ftable(["파일", "7항", "서류", "제출 내용"], ["8%", "7%", "42%", "43%"], "".join(
        f'<tr><td class="n">{a}</td><td class="g">{b}</td><td class="k">{t(c)}</td><td>{t(d)}</td></tr>' for a, b, c, d in DOCS7), "m9 d17")
          + '<div class="itr" style="margin-top:10px"><b>추가 증빙</b><span>협의회가 사실 확인을 위해 요청하시면 NICE 기업신용평가 · ISO 인증서 · 전기공사업 등록증 원본 · 보험 증권 원본을 바로 드립니다(요청받은 보완자료만 기한 안에 · 6항 라).</span></div></div>'),
    kp=("8종 모두 [[7항 순서 · 번호별 PDF]]로 - 서류마다 발급일을 적었습니다.", "작성 서류 = 대표이사 직인(서명 또는 날인 · 6항 나) · 개인정보는 가림본 · 원본 열람은 요청 시"))
B.CSS += ".tbl.d17 td{padding:8px 10px;font-size:13.5px;line-height:1.38}.tbl.d17 td.n{font-weight:800;color:var(--gold);text-align:center;font-size:15px}.tbl.d17 td.g{text-align:center;font-weight:800;color:var(--gold)}.tbl.d17 td.k{font-size:14px}"

# ------------------------------------------------------------ 먼저 묻는 다섯 가지
VOICE = [
    ("01", "옵션으로 고른 걸 또 파나요?", "중문 · 침실3 붙박이장 · 드레스룸 특화 · 조명특화 · 시스템에어컨처럼 분양 유상옵션과 겹치는 품목은 고른 세대에 권하지 않습니다. 선택 집계는 협의회를 통해 요청하고, 미선택 세대 · 추가 실만 안내합니다.", ["opt"]),
    ("02", "가격이 정말 싼지 어떻게 아나요?", "지금은 참고가격만 드립니다. 업체 선정 뒤 박람회 30일 전 협의회가 단가를 검수하고, 14일 전 같은 모델 · 같은 조건 총액으로 매장 · 온라인 가격과 비교한 자료를 공개합니다. 계약 뒤 더 싼 판매가 확인되면 차액 10배를 보상합니다.", ["price", "check"]),
    ("03", "업체가 문을 닫으면 A/S는요?", "1차 책임은 판매 · 시공업체에 있습니다. 업체가 이행하지 않거나 폐업 · 연락 두절이면 주관사가 사실 확인 뒤 먼저 처리하고, 대체 업체로 이관합니다(협의회 승인 · 계약자 동의 · 계약서에 정한 보증 금액 안).", ["bond", "care"]),
    ("04", "발전기금은 어떻게 하나요?", "세대당 15만원 기준(안)으로 협의회에 드립니다. 금액 · 대상 세대 · 지급 시기는 협의 시 확정하고, 공고대로 공증으로 진행합니다(10항 아). 공구가에는 얹지 않습니다.", ["fund", "menu"]),
    ("05", "입주까지 3년 가까이 남았는데요?", "계약 직후 전담 PM이 연락 창구가 되고 월 1회 진행을 보고합니다. 공동구매 운영기간과 사후관리 기간을 나눠 계약서에 적어, 끝이 열린 약속으로 남기지 않습니다.", ["mon1", "mon2"]),
]
new("std", sec="제안 개요", title=T_VOICE,
    lead="공고 · 공개 자료(단지 개요 · 유상옵션 · 입주 일정)에서 입주예정자가 먼저 물을 다섯 가지를 골라, 우리 답과 근거 쪽을 한 장에 모았습니다.",
    body=table(["NO", "먼저 묻는 것", "엣지컴퍼니 답", "근거"], "".join(
        f'<tr><td class="n">{n}</td><td class="k">{t(q)}</td><td>{t(a)}</td><td style="white-space:nowrap">{PGS(ks)}</td></tr>' for n, q, a, ks in VOICE), "vc5"),
    kp=("겹치지 않게, 먼저 보여 주고, 끝까지 - [[다섯 가지]]에 먼저 답합니다.",
        "질문은 공고 · 공개 자료 기준(2026.10) · 카페 글 집계 아님 · 협의회와 다시 확인합니다"))
B.CSS += ".tbl.vc5 td{padding:9px 12px !important;font-size:14.5px !important;line-height:1.45}.tbl.vc5 td.k{width:19%;font-size:15.5px !important}.tbl.vc5 td:last-child{width:12%;font-size:13.5px}"

# ------------------------------------------------------------ 단지 이해
new("std", sec="제안 개요", title=T_SITE,
    lead=f"공고 2항 단지 개요 기준 - {ST['dong']} {HH:,}세대가 대상입니다. 공구가 · 박람회 초대 · A/S는 모든 세대에 같은 기준으로 하고, 품목 · 견적은 타입별로 나눕니다.",
    body=B.cards([
        dict(lb="TOTAL", big=f"{HH:,}", unit="세대", nm=f"{ST['dong']} · {ST['buildings']}개 동",
             ds=f"{ST['floors']} · 시공 {ST['builder']}"),
        dict(lb="TYPES", big="10", unit="타입", nm="72 · 84 · 95㎡",
             ds=f"72㎡ {_t72:,} · 84㎡ {_t84:,} · 95㎡ {_t95:,}세대"),
        dict(lb="MOVE-IN", big="2029.09", nm="입주 예정",
             ds="공사 일정에 따라 바뀔 수 있음(공고 2항) · 바뀌면 운영일정을 서면 조정"),
        dict(lb="LOCATION", big="업성동", nm="천안시 서북구", hl=True,
             ds=f"업성3도시개발구역 A1BL · {ST['lake']} 인접"),
    ])
    + B.rows([
        ("같은 기준", f"{HH:,}세대 모두 [[같은 공구가 · 같은 A/S 기준]]입니다."),
        ("입주 일정", f"{ST['movein']} · 입주박람회는 개최 시 {ST['expo']}(안) · 사전점검 일정이 확정되면 협의회와 날짜를 다시 맞춥니다."),
    ], title_w=150),
    kp=(f"성성호수공원 곁 {HH:,}세대 · 10개 타입 - [[같은 기준]]으로 모시고, [[타입별로]] 견적을 나눕니다 · 천안 · 아산 생활권 업체가 가까이에서.", f"단지 사실 = 공고 2항 단지 개요 · 시공 {ST['builder']} · 세부 사양은 협의회와 다시 맞춥니다"))

# ------------------------------------------------------------ 타입별 품목(5항 나 취급 품목)
ITEMS_EO = [  # (묶음, 대상, [품목], 기준)
    ("공간 · 수납", "72 · 84㎡", ["수납 · 선반 · 팬트리 시스템", "커튼 · 블라인드(타입별 실측)", "실링팬 · 조명(조명특화 미선택 세대)"], "타입별 표준 견적표로 사이즈부터"),
    ("가족 · 생활", "84 · 95㎡", ["가전 · 가구 · 렌탈", "방충망(미세 · 안전) · 단열필름", "탄성코트 · 줄눈 · 새집증후군"], "자재 사양 · 인증 서류 확인"),
    ("입주 준비", "모든 세대", ["입주청소 · 포장이사", "사전점검 대행", "유리막코팅 · 입주 정리"], "천안 · 아산권 업체 우선 · 48시간 안 방문 일정 확정"),
    ("조건부", "유상옵션 확인 후", ["시스템에어컨 · 조명 교체", "현관 중문 · 침실3 붙박이장", "드레스룸 시스템"], "옵션 미선택 세대 · 추가 수요만"),
]
_ITX = globals().get("_item_card")
new("std", sec="제안 개요", title=T_ITEMS,
    lead="72㎡부터 95㎡까지 10개 타입입니다. ‘무엇을 더 넣느냐’보다 ‘우리 집 타입에 무엇이 맞느냐’가 먼저입니다. 품목은 수요조사로 확정하고, 아래는 출발 목록입니다.",
    body=('<div class="nb"><div class="itx">' + "".join(_item_card(*x) for x in ITEMS_EO) + '</div>'
          + '<div style="display:flex;flex-direction:column;gap:8px;margin-top:12px">'
          + '<div class="itr g"><b>타입별 표준 견적표</b><span>72A ~ 72D · 84A ~ 84D · 95A · 95B - 커튼 · 수납 · 조명은 타입별 견적을 박람회 전에 공개합니다.</span></div>'
          + '<div class="itr"><b>품목 확정</b><span>수요조사 결과 → 협의회 승인 → 업체 공개 모집. 수요가 적은 품목은 넣지 않고, 요청이 많은 품목은 추가 모집합니다.</span></div>'
          + '</div></div>'),
    kp=("우리 집 타입에 맞는 품목부터 - [[타입별 표준 견적표]]를 박람회 전에 공개합니다.", f"품목 · 업체 구성 = 수요조사 뒤 협의회 승인 · 품목별 참여 업체 구성(안) {PG('vendors')}"))

# ------------------------------------------------------------ 유상옵션 겹침
OPT = [  # (품목, 분양 옵션 구분, 박람회 기준, 상담 전 확인)
    ("조명특화", "유상옵션(일괄 선택형)", "선택 세대에는 조명 교체를 권하지 않음 · 미선택 세대만", "천장 · 배선 · 스위치 사양"),
    ("시스템에어컨", "유상옵션(해당 타입)", "미선택 세대 · 추가 실만", "배관 · 실외기 연결 조건"),
    ("현관 중문", "유상옵션(해당 타입)", "미선택 세대만", "중문틀 · 바닥 마감"),
    ("침실3 붙박이장", "유상옵션(해당 타입)", "미선택 세대 · 옵션이 없는 실만", "실측 후 견적"),
    ("드레스룸 특화", "유상옵션(해당 타입)", "미선택 세대만 · 수납 보강은 실측 뒤", "선반 · 행거 구성"),
]
new("std", sec="제안 개요", title=T_OPT,
    lead="‘이미 옵션으로 산 걸 또 파나’ - 분양 유상옵션과 겹치는 품목을 먼저 표시하고, 옵션을 고른 세대에는 같은 품목을 권하지 않습니다.",
    body=('<div class="nb">' + table(["품목", "옵션 구분", "공동구매 기준", "상담 전 확인"], "".join(
        f'<tr><td class="k">{t(a)}</td><td>{t(b)}</td><td>{t(c)}</td><td>{t(d)}</td></tr>' for a, b, c, d in OPT), "lgx op6")
          + B.rows([
              ("선택 집계", "기준일이 있는 옵션 선택 집계를 협의회를 통해 사업주체 · 시공사에 요청하고, 그 결과로 품목 · 업체 구성을 정합니다."),
              ("직영 품목도 같은 심사", "조명 · 실링팬 · 커튼 · 욕실 환기(휴젠뜨) 직영 품목도 같은 공개 심사 · 같은 단가 사전 공개 · 같은 가격 보호 규정(제8조)을 거칩니다."),
              ("하지 않는 것", "중복 설치 권유 · 옵션을 고른 세대에 같은 품목 다시 권하기."),
          ], title_w=170) + '</div>'),
    kp=("유상옵션과 [[겹치는 품목]]은 미선택 세대만 - 중복 설치를 권하지 않습니다.", "옵션 구분 = 분양 유상옵션 안내 기준 · 타입별 해당 여부와 세대별 선택 결과는 협의회를 통해 다시 확인"))
B.CSS += ".tbl.op6 td{padding:9px 12px;font-size:15px}.tbl.op6 td.k{width:20%}"

# ------------------------------------------------------------ 대표 품목 · 총 부담액(5항 다) — 참고가격 = 타 단지 2026.10 공개 단가(84㎡ 기준) · 이 단지 확정가 아님
PRICE = [  # (품목, 모델 · 규격 표기, 시공 범위, 참고가격, 총 부담액 칸)
    ("줄눈", "자재명(폴리우레아 · 케라폭시) · 시공 면적", "현관 · 욕실 2곳 바닥 · 실리콘", "34 ~ 35만원 / 상위 55 ~ 60만원", "부가세 · 재시공 기준"),
    ("탄성코트", "자재 계열(세라믹 · 실리카) · 도막 횟수", "베란다 · 다용도실 2곳", "35 ~ 38만원 / 상위 45 ~ 48만원", "부가세 · 추가 면적 단가"),
    ("창호 필름", "필름 제품명 · 등급(단열 · 열차단)", "거실 + 안방 창", "42 ~ 50만원 / 상위 75 ~ 85만원", "부가세 · 시공비 포함 여부"),
    ("입주청소", "공정 · 범위표 · 타입별 면적", "바닥 · 주방 · 욕실 · 창틀 · 베란다", "3.3㎡당 1.3 ~ 1.4만원", "부가세 · 재방문 기준"),
    ("커튼 · 블라인드", "원단 등급 · 타입별 창 크기", "거실 이중 · 안방 암막 · 작은방 2곳", "88 ~ 100만원", "부가세 · 실측 · 레일 · 설치"),
    ("현관 중문(미선택 세대)", "형식(3연동 등) · 프레임 · 유리 사양", "실측 · 설치 · 마감", "80 ~ 90만원", "부가세 · 설치비 · 배송"),
    ("시스템에어컨(미선택 세대)", "제조사 · 모델명 · 출시연도 · 실내기 대수", "4대(거실 + 방 3) 추가 설치", "650만원(타 단지 1곳 공개가)", "부가세 · 배관 · 타공 · 철거 칸"),
]
new("std", sec="제안 개요", title=T_PRICE,
    lead="공고 5항 다 - 업체가 선정되기 전이라 지금 드리는 금액은 참고가격입니다. 확정 단가는 업체 공개 모집 뒤 아래 칸 그대로, 구매자 총 부담액(제품 + 부가세 + 배송비 + 설치비)으로 공개합니다.",
    body=('<div class="nb">' + ftable(["품목", "모델 · 규격 표기", "시공 범위", "참고가격(타 단지 공개 단가표 2026.10)", "총 부담액에 넣는 칸"], ["17%", "25%", "21%", "20%", "17%"], "".join(
        f'<tr><td class="k">{t(a)}</td><td>{t(b)}</td><td>{t(c)}</td><td class="v">{t(d)}</td><td>{t(e)}</td></tr>' for a, b, c, d, e in PRICE), "pz6")
          + B.rows([
              ("참고가격이란", "타 단지 공개 단가표(2026.10 · 84㎡ 기준 · 참고)의 범위입니다. [[이 단지 확정가가 아니며]], 근거 자료는 제출서류 라 붙임(가림본)입니다."),
              ("부가세 표기", "참고가격은 타 단지 표기 그대로(부가세 포함 여부 미표기) - 확정 단가표에는 품목마다 [[부가세 포함 / 별도]]를 한 칸에 적습니다."),
              ("총 부담액 한 칸", "제품가 · 부가세 · 배송비 · 설치비 · 철거 · 추가 자재를 따로 적고 합계를 한 칸에 - 현장에서 처음 보는 추가 비용은 받지 않습니다."),
          ], title_w=140) + '</div>'),
    kp=("공구가 · 추가 비용 · 일반가를 [[같은 칸]]에 - 총 부담액으로 비교하실 수 있게 합니다.",
        "참고가격 = 타 단지 공개 단가(84㎡ · 2026.10) · 확정 시점과 비교 방법은 다음 장 · 유상옵션 품목은 미선택 세대만"))
B.CSS += ".tbl.pz6 td{padding:8px 10px;font-size:13.5px;line-height:1.38;vertical-align:middle}.tbl.pz6 td.k{font-size:14px}.tbl.pz6 td.v{color:var(--gold);font-weight:700}"

# ------------------------------------------------------------ 가격 확정 시점 · 비교 방법 · 적용기간(5항 라)
CHECK5 = [("지금", "참고가격", "타 단지 공개 단가 범위 - 이 단지 확정가 아님"),
          ("업체 선정 뒤", "단가 제출", "모델명 · 출시연도 · 규격 · 설치 · 배송 · 부가세 칸을 채운 견적 제출"),
          ("D-30", "협의회 검수", "같은 모델 · 같은 조건 총액으로 매장 2곳 + 온라인 1곳 비교 · 높으면 조정 요청"),
          ("D-14", "확정가 공개", "확정 단가 · 비교자료를 카페에 공개(협의회 승인 후) · 현장 가격 변경 없음"),
          ("계약 후 7일", "10배 보상", "같은 브랜드 · 모델 새 제품이 인근 매장에서 더 싸면 차액 10배")]
new("std", sec="제안 개요", title=T_CHECK,
    lead="공고 5항 라 · 10항 사 - 참고가격이 언제 실제 판매가가 되는지, 판매 전에 어떻게 비교하는지, 그 가격이 언제까지 유지되는지를 정합니다.",
    body=('<div class="nb"><div class="flowx">' + "".join(
        (('<div class="ar">›</div>' if i else "") + f'<div class="st{" hl" if i == 3 else ""}"><i>{a}</i><b>{b}</b><p>{t(c)}</p></div>')
        for i, (a, b, c) in enumerate(CHECK5)) + '</div>'
          + B.rows([
              ("가격 적용기간", "D-14 공개일부터 공동구매 운영기간 종료일(입주 지정기간 종료)까지 [[같은 모델 · 같은 조건 · 같은 가격]] - 단종 · 품절은 같은 등급 이상 대체 모델을 협의회 승인 후 같은 가격 이하로."),
              ("판매 전 재확인", "판매 시작 전에 품목 · 가격을 다시 확인하고(10항 사), 입주 일정이 바뀌면 운영일정 · 가격 적용기간을 서면으로 조정합니다."),
              ("높으면 조정 또는 재모집", "공개 단가가 더 높으면 사유(설치 포함 · A/S 연장 등)를 적거나 조정을 요청하고, 협의회가 승인하지 않으면 다시 모집합니다."),
              ("10배 보상 조건", "구매 영수증 + 주관사 매장 확인 · 1건당 최대 50만원(계약금액이 더 적으면 그 금액) · 세대 · 품목당 1회 · 보상금은 주관사 지급 · 온라인 · 시공 품목 제외(환불 규정 제8조)."),
          ], title_w=170) + '</div>'),
    kp=("참고가격 → [[D-30 검수 → D-14 확정 공개]] → 운영기간 내내 같은 가격.",
        "예) 공구가 35만 → 인근 매장 32만 → 차액 3만 × 10 = 보상 30만원 + 판매가 32만원 조정"))

# ------------------------------------------------------------ 운영계획(부록 · 3항 마)
EXPO_PLAN = [
    ("전제 · 비용", "기본안 = 참가업체 참가비로 운영 · 협의회 비용 청구 없음 · 개최 여부 · 횟수 · 장소는 협의회와 정함(공고 3항 마). 아래는 개최를 전제로 한 운영계획(안)입니다."),
    ("횟수 · 일정", f"1회 · {ST['expo']}(예정) · 주말 포함 2 ~ 3일(안) · 입주 3 ~ 2개월 전 - 날짜는 사전점검 일정 확정 뒤 협의회 승인으로 정함"),
    ("장소 후보", "① " + ST["venues"][0] + " ② " + ST["venues"][1] + " ③ " + ST["venues"][2] + " - 답사 후 협의회 승인"),
    ("규모 · 업체 구성", f"초대 = {HH:,}세대 · 업체 구성은 수요조사 뒤 협의회 승인 · 주관사 직영 + 브랜드 + 천안 · 아산권 시공 · 공개 모집"),
    ("존 배치", "입구 체크인 · 협의회 부스 → 품목 존(가전 · 가구 · 인테리어 · 시공) → 상담 · 계약 → 휴게 · 놀이방 · 수유실"),
    ("전담인력", "전담 PM 1명(정규직) · 현장 책임자 1명 + 운영 인력(예시) · 매일 개장 전 안전 점검표"),
    ("보험 · 보고", "행사(주최자)배상책임보험 = 개최 확정 시 가입 · 개장 전 증권 사본 · 결과보고서 = 종료 후 30일 안"),
]
new("std", sec="제안 개요", title=T_EXPOPLAN,
    lead="공고 3항 마 - 박람회는 계약을 재촉하는 자리가 아니라, 가족이 함께 와서 확인하고 비교하는 자리로 만듭니다.",
    body=('<div class="nb">' + B.rows(EXPO_PLAN, title_w=140) + '</div>'),
    kp=("개최 여부는 [[협의회가]] 정하고, 개최하면 [[확인하고 비교하는]] 박람회로 운영합니다.",
        f"세부 운영 = 운영 계획 {PG('expo')} · 행사장 안전 {PG('safe')} · 장소 ①은 개관 일정 확인 후 협의"))

# ------------------------------------------------------------ 취소 · 연기(부록)
CANCEL = [  # (사유, 판단 · 고지, 대응)
    ("천재지변 · 감염병 · 기상 특보", "관계기관 발표 기준 · 확인 즉시 협의회 보고 · 카페 · 문자 안내(협의회 승인 문구)", "대체 주말로 연기 또는 온라인 상담으로 전환 · 같은 공구가 · 같은 A/S 기준"),
    ("행사장 사정(대관 취소 · 시설 고장)", "대관 계약에 취소 · 변경 조건 명시 · 확인 즉시 협의회 보고", "후보 2 · 3순위 시설로 대체 · 날짜 유지를 우선"),
    ("사전점검 · 입주 일정 변경", "시공사 공지 확인 뒤 협의회와 새 날짜 협의", "입주 3 ~ 2개월 전 원칙 안에서 다시 정함 · 업체 계약 일정도 서면 조정"),
    ("주관사 사정", "사유와 대체안을 서면으로 협의회 승인", "주관사 귀책 비용은 주관사가 정리 · 대체 일정 확정까지 매주 진행 보고"),
]
new("std", sec="제안 개요", title=T_CANCEL,
    lead="날씨 · 감염병 · 행사장 · 공정 일정처럼 행사를 바꾸게 만드는 사유를 미리 나누고, 사유별로 누가 · 언제 · 무엇을 하는지 정해 둡니다.",
    body=('<div class="nb">' + ftable(["사유", "판단 · 고지", "대응"], ["26%", "38%", "36%"], "".join(
        f'<tr><td class="k">{t(a)}</td><td>{t(b)}</td><td>{t(c)}</td></tr>' for a, b, c in CANCEL), "cn4")
          + B.rows([
              ("이미 맺은 계약", "연기 · 취소로 시공 일정이 바뀌면 위약금 없이 다시 잡고, 계약자가 원하면 환불 규정 기한과 관계없이 전액 환불합니다."),
              ("발전기금", "행사가 연기 · 온라인으로 바뀌어도 협의한 발전기금 기준은 그대로입니다."),
              ("업체 · 행사장", "업체 참가 계약 · 대관 계약에 연기 · 대체 조항을 넣어, 바뀐 일정에도 같은 업체 · 같은 단가가 유지되게 합니다."),
          ], title_w=140) + '</div>'),
    kp=("행사가 바뀌어도 [[가격 · 혜택 · 계약]]은 그대로 지킵니다.", "고지 문구 · 게시는 협의회 승인 후 · 대체 일정은 협의회가 정함"))
B.CSS += ".tbl.cn4 td{padding:10px 12px;font-size:14.5px;line-height:1.42;vertical-align:middle}.tbl.cn4 td.k{font-size:15px}"

# ------------------------------------------------------------ 최근 5년 운영 단지 · 담당 업무 · 실적 확인자료(5항 가)
_RNOTE = {  # 특이사항 · 증빙(당사 운영 기록 · NICE 연혁 · 공식 행사일정)
    "레이카운티": ("1 · 2차 박람회 2회 · 단일 단지 최대 4,470세대", "NICE 연혁"),
    "e편한세상 송도 더퍼스트비치": ("BEXCO 공식 행사일정 주최 / 주관 엣지컴퍼니", "BEXCO 공식 행사일정"),
    "두산위브더제니스 센트럴사하": ("1 · 2차 박람회 2회", "NICE 연혁"),
    "양정자이더샵SK VIEW 1·2단지": ("두 단지를 한 박람회로 운영", "NICE 연혁"),
    "춘천 학곡지구 중해마루힐 포레스트": ("강원권 · 호텔 행사장 운영", "NICE 연혁"),
    "에코델타 대성베르힐": ("같은 신도시 연속 운영", "BEXCO 공식 행사일정"),
    "두산위브더제니스 오션시티": ("2,813세대 대단지", "NICE 연혁"),
    "창원 센트럴 아이파크": ("CECO 공식 행사일정 주최 엣지컴퍼니", "CECO 공식 행사일정 · NICE 연혁"),
    "힐스테이트 포항": ("경북권 1,717세대", "NICE 연혁"),
    "부산사상 중흥S-클래스 그랜드센트럴": ("수요조사 · 입주 설명회 · 박람회 안내를 카페 주관사 게시판에서 운영", "카페 주관사 게시판(B-0)"),
}
_rec_rows = "".join(
    f'<tr><td class="n">{m}</td><td class="k">{t(nm)}</td><td class="r">{n:,}</td>'
    f'<td>{t(D.EXPO_VENUE[nm][0].replace(chr(10), " · "))}<br><small>{t(D.EXPO_VENUE[nm][1])}</small></td>'
    f'<td>주관 - 업체 모집 · 심사 · 단가 검수 · 박람회 운영 · 공동구매 A/S 창구<br><small>{t(_RNOTE[nm][0])}</small></td><td class="ev">{t(_RNOTE[nm][1])}</td></tr>' for m, nm, _a, n in D.R5Y_1000)
new("std", sec="제안 개요", title=T_RECS,
    lead="공고 5항 가 · 7항 나 - 최근 5년 1,000세대 이상 주관 단지와 담당 업무입니다. 같은 업무(업체 공개 모집 · 심사, 단가 검수, 박람회 운영, 공동구매 A/S 창구)를 이 단지에서 맡습니다.",
    body=('<div class="nb">' + ftable(["입주", "단지", "세대", "박람회 일정 · 장소", "담당 업무", "증빙"], ["8%", "22%", "7%", "21%", "29%", "13%"], _rec_rows, "rc8") + '</div>'),
    kp=(f"최근 5년 1,000세대 이상 [[{len(D.R5Y_1000)}개 단지 · {sum(r[3] for r in D.R5Y_1000):,}세대]]를 주관했습니다.",
        f"입주 2023.04 이후 · 증빙 = 제출서류 나(NICE 연혁 · 공식 행사일정 · 주관사 협약서) · NICE 연혁은 기재 연월 · 개최일은 이 표 기준 · 500세대 이상 {_r5_n}개 단지 {PG('r500')}"))
B.CSS += (".tbl.rc8 td{padding:8px 9px;font-size:13.5px;line-height:1.36;vertical-align:middle}.tbl.rc8 td.k{font-size:14px}"
          ".tbl.rc8 td.r{text-align:right;font-variant-numeric:tabular-nums}.tbl.rc8 td small{color:var(--sub);font-size:11.5px}"
          ".tbl.rc8 td.ev{font-size:12px;color:var(--gold);font-weight:700}")

# ------------------------------------------------------------ 카페 운영(5항 자 · 3항 라 · 10항 나 · 마 · 9항 마)
CAFE_A = [
    ("게시 범위", "카페의 업체 홍보 · 계약 안내 · 모집 · 이용 후기는 [[참여업체에 한해]] 게시합니다(10항 나) - 비참여 업체 홍보는 하지 않습니다."),
    ("게시 절차", "게시물 · 공지 문구는 협의회 승인 후 게시 · 협의회 명칭과 카페 이용방법은 계약서에 적은 범위 안에서만(10항 마)."),
    ("선정 전", "선정 전에는 공식 주관사처럼 홍보하지 않고, 사전 설문 · 개인정보 수집을 하지 않습니다(9항 마)."),
]
CAFE_B = [
    ("계약 안내", "품목별 단가표 · 총 부담액 · 계약 상대방 · 계약금 · 취소 기한 · A/S 기간을 같은 형식으로 안내합니다."),
    ("모집", "사전 등록 · 상담 신청은 본인이 직접 입력한 항목만 · 수신 동의 세대에만 알림(D-30 · D-14 · D-7 · D-1)."),
    ("후기", "실제 구매 · 시공 세대만 작성 · 업체가 대가를 주고 쓰게 하는 후기 금지 · 불만 후기도 지우지 않고 처리 결과를 답글로."),
    ("회원명부", "회원명부는 영업용으로 받지 않으며(10항 마), 업체에 넘기지 않습니다."),
]
new("std", sec="제안 개요", title=T_CAFE,
    lead="공고 5항 자 · 3항 라 - 카페 안의 공동구매 홍보 · 계약 안내 · 모집 · 후기를 어떻게 운영하는지 정해 둡니다.",
    body=('<div class="nb"><div class="pmx">'
          '<div class="pc"><h3><i>RULES</i>누가 · 무엇을 게시하나</h3>' + B.rows(CAFE_A, title_w=96) + '</div>'
          '<div class="pc"><h3><i>OPERATION</i>안내 · 모집 · 후기 운영</h3>' + B.rows(CAFE_B, title_w=96) + '</div></div></div>'),
    kp=("카페는 [[참여업체만 · 협의회 승인 뒤]] - 명부는 영업에 쓰지 않습니다.", "게시 · 알림 문구는 협의회 승인 후 · 수신 동의 세대에만 · 카페 이용방법은 계약서에 기재(10항 마)"))

# ------------------------------------------------------------ 계약 상대방 · 대금 수령자 · 단계별 취소(5항 바)
CARE = [  # (구분, 계약 상대방 · 대금 수령자, 계약금 · 잔금, 단계별 취소 · 환불, 처리기한)
    ("시공 품목", "참여 시공업체(계약서 명의) · 업체 명의 사업자 계좌 · 카드", f"계약금 {D.DEPOSIT_MAX}% 이하 · 잔금 = 시공 완료 · 계약자 확인 뒤", "시공일 7 · 15일 전(별표) 전액 환불 · 이후 실제 자재비만 공제(내역 서면)", "취소 확정 3영업일"),
    ("맞춤 제작 품목", "참여업체(계약서 명의) · 업체 명의 계좌 · 카드", "계약금 예외(업체 선정 때 협의회 승인 · 단가표에 표시) · 잔금 = 설치 확인 뒤", "출고 지시 전 = 협의 취소 · 제작 뒤 = 실제 제작비만 공제", "취소 확정 3영업일"),
    ("브랜드 · 본사 규정 품목", "브랜드 본사 · 대리점 · 렌탈 · 통신사(각 계약 주체)", "각 본사 결제 조건(계약 전 서면 고지)", "미출고 · 미설치 = 전액 · 렌탈 · 통신은 본사 약관", "본사 규정 · 주관사 추적"),
    ("주관사 직영 품목", "㈜엣지컴퍼니(계약 상대방 · 대금 수령자)", f"계약금 {D.DEPOSIT_MAX}% 이하 · 잔금 = 시공 확인 뒤", "다른 업체와 같은 규정 · 같은 기한", "취소 확정 3영업일"),
    ("업체 귀책", "-", "-", "시공 지연 · 다른 제품 · 하자 미보수 = 기한과 관계없이 전액 환불", "업체 미이행 시 주관사 선보상"),
]
new("std", sec="제안 개요", title=T_CARE,
    lead="공고 5항 바 - 품목별로 누구와 계약하고 누구에게 돈을 내는지, 계약금 · 잔금은 언제, 단계별로 취소하면 얼마를 언제 돌려받는지 한 장에 적었습니다.",
    body=('<div class="nb">' + ftable(["구분", "계약 상대방 · 대금 수령자", "계약금 · 잔금", "주문 · 시공 단계별 취소 · 환불", "처리기한"], ["14%", "25%", "22%", "25%", "14%"], "".join(
        f'<tr><td class="k">{t(a)}</td><td>{t(b)}</td><td>{t(c)}</td><td>{t(d)}</td><td class="v">{t(e)}</td></tr>' for a, b, c, d, e in CARE), "cr5")
          + f'<div class="itr" style="margin-top:10px"><b>대금은 업체에게만</b><span>대금은 계약서에 적힌 계약 상대방 명의(사업자 계좌 · 카드 가맹점)로만 냅니다. 주관사는 직영 품목 외에는 대금을 받지 않고, 개인 계좌 송금은 금지합니다. 전문 = 환불 규정 {PGS(["rule1", "rule2"])}</span></div></div>'),
    kp=("누구와 · 누구에게 · 언제 · 얼마 - [[단계별로 숫자로]] 정했습니다.", "취소 기한 = 환불 규정 [별표] · 카드 · 현금 같은 단가 · 환불은 취소 확정 후 3영업일 안"))
B.CSS += (".tbl.cr5 td{padding:9px 10px;font-size:13.5px;line-height:1.4;vertical-align:middle}.tbl.cr5 td.k{font-size:14.5px}"
          ".tbl.cr5 td.v{color:var(--gold);font-weight:700}")

# ------------------------------------------------------------ 계약금 · 잔금 흐름(5항 바)
ESC5 = [("01", "계약", "업체 명의 계약서 · 환불 규정 첨부 · 모델명 · 총 부담액 기재"),
        ("02", "계약금", f"총액의 {D.DEPOSIT_MAX}% 이하 · 업체 명의 계좌 · 카드"),
        ("03", "시공 · 설치", "약속한 날짜 · 사양대로 · 해피콜로 일정 확인"),
        ("04", "확인", "계약자 확인(서명 · 문자) · 하자 · 미시공은 보수 뒤"),
        ("05", "잔금", "확인된 뒤 업체에 지급")]
new("std", sec="제안 개요", title=T_ESCROW,
    lead="공고 5항 바 - 계약금은 적게, 잔금은 확인한 뒤에. 문제가 생기면 남은 돈을 내지 않아도 되도록 순서를 정합니다.",
    body=('<div class="nb"><div class="flowx">' + "".join(
        (('<div class="ar">›</div>' if i else "") + f'<div class="st{" hl" if i == 4 else ""}"><i>{a}</i><b>{b}</b><p>{t(c)}</p></div>')
        for i, (a, b, c) in enumerate(ESC5)) + '</div>'
          + B.rows([
              ("계약금 상한", f"계약 총액의 {D.DEPOSIT_MAX}% 이하 - 맞춤 제작 · 본사 규정 품목만 예외(업체 선정 때 협의회 승인 · 단가표에 미리 표시)."),
              ("결제 방식", "카드 · 현금 같은 단가 · 현금은 현금영수증 · 업체 명의 사업자 계좌만."),
              ("잔금 보류", "하자 · 미시공 부분이 있으면 보수가 끝난 뒤 잔금을 냅니다(환불 규정 제4조 ③)."),
              ("업체가 미루면", "취소 · 환불을 미루거나 거부하면 주관사가 사실 확인 뒤 먼저 보상하고 업체와 나중에 정산합니다(제7조 ①)."),
          ], title_w=130) + '</div>'),
    kp=("계약금은 [[10%까지]], 잔금은 [[확인 뒤에]] - 순서로 입주민을 지킵니다.", "적용 품목 · 계약금 예외는 업체 선정 때 협의회 승인 · 계약서 · 단가표에 표시"))

# ------------------------------------------------------------ 하자 책임 구분(5항 사 · 규칙 18)
new("std", sec="제안 개요", title=T_DESK,
    lead="공동구매 품목 하자는 참여업체 1차 · 주관사 추가 책임, 건설 하자는 사업주체 · 시공사 책임입니다. 주관사는 건설 하자도 정리 · 전달 · 추적을 돕습니다.",
    body=('<div class="nb"><div class="pmx">'
          '<div class="pc"><h3><i>GROUP BUY</i>공동구매 품목 하자</h3>'
          + B.rows([
              ("1차 책임", "판매 · 시공업체 - 하자보수 · 교환 · A/S(특약이행각서)."),
              ("주관사", "콜센터 접수 · 24시간 1차 회신 · 48시간 방문 일정 확정 · 업체 무응답 · 폐업 시 추가 책임."),
              ("무상 기간", "시공 품목 최소 2년 · 브랜드는 제조사 보증."),
          ], title_w=96) + '</div>'
          '<div class="pc"><h3><i>CONSTRUCTION</i>건설 하자</h3>'
          + B.rows([
              ("책임", f"세대 · 공용부 건설 하자 = [[사업주체 · 시공사({ST['builder']}) 책임]] · 접수는 사업주체 · 시공사 하자 접수 창구."),
              ("주관사 역할", "입주 지정기간 동안 협의회가 모은 목록 정리 · 보수 요청 공문 초안 · 전달 · 진행 추적."),
              ("하지 않는 일", "건설 하자의 판정 · 보수 책임 · 소송 대리."),
          ], title_w=96) + '</div></div></div>'),
    kp=("공동구매 하자는 [[업체 1차 · 주관사 추가]], 건설 하자는 [[사업주체 · 시공사]] - 책임을 먼저 나눕니다.", "주관사의 건설 하자 지원 = 정리 · 공문 초안 · 전달 · 추적(판정 · 보수 · 소송 대리 아님)"))

# ------------------------------------------------------------ 업체 선정기준 · 확인 · 교체(5항 나 · 3항 나)
LIC = [  # (확인 대상, 방법)
    ("사업자 · 통신판매", "사업자등록증 원본 대조 · 국세청 사업자 상태(휴 · 폐업) 조회 · 온라인 판매 업체는 통신판매업 신고 확인"),
    ("면허 · 등록 · 자격", "품목에 법정 면허 · 등록이 있으면 등록증 원본 대조 + 발급 기관 공공 조회(예: 전기공사업 · 건설업 · 소독업)"),
    ("실적 · 사후관리 능력", "공동구매 이력 또는 동종 시공 실적 · A/S 인력 · 연락 체계 · 하자보수 기간"),
    ("보험 · 재무", "영업배상책임보험 증권 · 국세 · 지방세 완납 · 특약이행각서 · 서류 유효기간 관리표(만료 30일 전 갱신)"),
]
BAD = [("1단계 · 경고", "민원 · 지연 확인 즉시 서면 경고 · 시정 기한"), ("2단계 · 판매 중단", "기한 안 미시정 · 서류 위조 · 무자격 시공 확인 시 즉시 판매 · 홍보 중단(협의회 보고)"),
       ("3단계 · 교체 · 이관", "협의회 사전 승인으로 대체 업체 지정 · 기존 구매계약 · 사후관리 이관(계약자 동의 · 10항 바)"), ("피해 대응", "주관사가 사실 확인 뒤 먼저 보상 · 업체와 정산 · 페널티(홍보정지 → 총액 10% 배상 → 자격박탈)")]
new("std", sec="제안 개요", title=T_LICENSE,
    lead="공고 5항 나 · 3항 나 - 서류는 사본이 아니라 원본 대조와 공공 조회로 확인하고, 문제가 생긴 업체는 단계별로 판매를 멈추고 바꿉니다.",
    body=('<div class="nb"><div class="pmx">'
          '<div class="pc"><h3><i>CHECK</i>선정기준 · 확인 방법</h3>' + B.rows(LIC, title_w=104) + '</div>'
          '<div class="pc"><h3><i>REPLACE</i>판매 중단 · 교체 방법</h3>' + B.rows(BAD, title_w=118) + '</div></div></div>'),
    kp=("확인은 [[원본 · 공공 조회]]로, 교체는 [[단계별로]] - 바뀐 뒤에도 기존 계약 · 사후관리는 이어집니다.", "확인 결과는 업체 심사표와 함께 협의회에 보고 · 업체 변경은 협의회 사전 승인(10항 바)"))

# ------------------------------------------------------------ 참여 예정 업체 모집계획 · 확인 절차(7항 사 · 지역업체 보장 + 목표)
LOC = [  # (단계, 내용)
    ("1 · 수요조사", "협약 뒤 수요조사로 품목을 확정하고 협의회 승인을 받습니다."),
    ("2 · 공개 모집", "품목별 업체 모집 공고(천안 · 아산권 업체 우선 공지 · 협의회 승인 후) - 참여 예정 업체는 지금 정하지 않고 선정 뒤 공개 모집합니다."),
    ("3 · 4단계 심사", "서류(원본 대조 · 공공 조회) → 단가 · 조건 → 품질 · 사후관리 → 협의회 승인. 지역 업체도 같은 기준."),
    ("4 · 확정 · 보고", "확정 명단 · 사업자등록증 · 자격자료 · 지역 비율을 협의회에 보고 · 업체가 바뀌면 다시 보고."),
]
new("std", sec="제안 개요", title=T_LOCAL,
    lead="공고 7항 사 - 참여 예정 업체가 아직 정해지지 않았으므로 모집계획과 확인 절차를 냅니다. 가까운 업체가 맡아야 A/S가 빨라지므로 시공 품목은 천안 · 아산권 업체를 먼저 찾습니다.",
    body=('<div class="nb">' + B.cards([
        dict(lb="GUARANTEE", big="50", unit="% 이상", nm="천안 · 아산권 시공업체 보장", ds="시공 품목 참여업체 수 기준 · 이행각서에 명시"),
        dict(lb="TARGET", big="70", unit="% 이상", nm="목표", ds="선정 후 천안 · 아산권 우선 공개 모집으로 채움", hl=True),
        dict(lb="BASE", big="경인", nm=BR, ds="상담 · 접수 · 시공 관리 · A/S 출동"),
    ], cols=3)
          + B.rows(LOC, title_w=130) + '</div>'),
    kp=("업체는 [[선정 뒤 공개 모집]] - 시공 품목은 천안 · 아산권 업체를 먼저 찾습니다.", "비율 산정 = 사업장 소재지(사업자등록증) · 시공 품목 참여업체 수 기준 · 브랜드 품목은 본사 · 공식 판매점"))

# ------------------------------------------------------------ 역할 구분
ROLE = [  # (일, 협의회 · 사업주체 · 시공사, 엣지컴퍼니)
    ("협상 · 의사결정", "협의회", "회의 자료 · 회의록 · 회의 배석"),
    ("건설 하자 판정 · 보수", f"사업주체 · 시공사({ST['builder']})", "협의회가 모은 목록 정리 · 공문 초안 · 전달 · 추적"),
    ("공동구매 하자 · A/S", "-", "참여업체 1차 · 주관사 추가 책임(접수 · 선보상 · 이관)"),
    ("박람회 개최 여부 · 횟수 · 장소", "협의회(공고 3항 마)", "운영계획(안) · 기본안 = 참가업체 참가비로 운영 · 협의회 비용 청구 없음"),
    ("카페 게시 · 공지", "협의회 승인", "참여업체 게시물 정리 · 승인 요청"),
    ("법률 · 세무 판단", "협의회가 정한 전문가", "필요한 자료를 정리해 전달"),
]
new("std", sec="제안 개요", title=T_ROLE,
    lead="공동구매 운영은 법률 · 건설 하자 영역과 맞닿습니다 - 겹치거나 충돌하지 않게 할 일을 먼저 나눕니다.",
    body=table(["일", "협의회 · 사업주체 · 시공사", "엣지컴퍼니"], "".join(
        f'<tr><td class="k">{t(a)}</td><td>{t(b)}</td><td>{t(c)}</td></tr>' for a, b, c in ROLE), "lgx rl7"),
    kp=("의사결정은 [[협의회]], 건설 하자는 [[사업주체 · 시공사]], 공동구매 운영 · 자료는 [[주관사]].", "외부 전문가 활용은 협의회 사전 승인 시에만 · 사업 전체 재위탁 없음"))
B.CSS += ".tbl.rl7 td{padding:14px 15px;font-size:16px}.tbl.rl7 td.k{width:28%}"

# ------------------------------------------------------------ 외부 경관조명(부록 · 협의회 요청 시)
_LXPT = [
    ("우선 1 · 동 파사드", "외벽 라인조명 · 실루엣 - 기존 경관조명 도면 · 배선 · 조도 · 타이머부터 확인합니다."),
    ("우선 2 · 수변 · 조경", f"{ST['lake']} 쪽 보행 동선 · 수목 · 산책로의 밝기 · 눈부심을 함께 봅니다."),
    ("산출물", "① 현황 진단 ② 기본 · 개선 · 선택안 비교(물량 · 공사비 · 유지관리비) ③ 협의 기록"),
    ("결정은 협의회 · 관리주체", "설치 여부 · 범위 · 비용은 도면 검토 뒤 협의회 · 관리주체 · 사업주체 승인 범위 안에서 정합니다."),
]
_lxo = slot("lx_front1")[1]
_lxx = "시뮬레이션" if _lxo else "타 단지 예시"
_lxg = (_fig("lx_front1", "① 동 파사드", f"외벽 라인조명 · 도로변 경관 · {_lxx}", "50% 45%")
        + _fig("lx_front2", "② 단지 조감 야간", f"동 간 통일된 색온도 · 산책로 동선 · {_lxx}", "50% 50%")
        + _fig("lx_gate", "③ 문주 · 진입부", f"{'문주 디자인 제안 · ' if _lxo else ''}진입부 보행 동선 · 간접광 · {_lxx}", "45% 100%"))  # 본부장 11-02 문주 = 신규 디자인 제안(실제 문주 아님)
if _lxg:
    _lx_body = ('<div class="nb"><div class="lxo"><div class="gal lxa">' + _lxg + '</div><div class="lxd">'
                + "".join(f"<div><b>{a}</b><p>{t(b)}</p></div>" for a, b in _LXPT) + '</div></div></div>')
    _lx_lead = ("전기공사업 등록 업체로서 단지의 밤 얼굴을 입주 전에 진단하고 개선안을 냅니다 - 협의회가 요청하시면 진행"
                + (f"(아래 사진은 {ST['name']} 경관조명 연출 시뮬레이션 · 실제와 다를 수 있음)." if _lxo else f"(아래 사진은 타 단지 경관조명 연출 예시 · {ST['name']} 실제 모습 아님)."))
else:      # 단지 사진 대기 → 글 카드 + 진행 단계(사진 자리표시 없음)
    _lx_body = ('<div class="nb"><div class="lxt">' + "".join(f'<div><i>{k:02d}</i><b>{a}</b><p>{t(b)}</p></div>' for k, (a, b) in enumerate(_LXPT, 1))
                + '</div><div class="lxstep">'
                '<div><i>STEP 01</i><b>진단</b><span>현황 조도 · 눈부심 · 사각지대 측정</span></div><em>›</em>'
                '<div><i>STEP 02</i><b>설계</b><span>조도 · 색온도 · 배광을 도면으로</span></div><em>›</em>'
                '<div><i>STEP 03</i><b>생산</b><span>단지 맞춤 제작 · KC 인증 제품</span></div><em>›</em>'
                '<div><i>STEP 04</i><b>시공 · A/S</b><span>전기공사업 등록 업체 직접 시공</span></div></div></div>')
    _lx_lead = "전기공사업 등록 업체로서 단지의 밤 얼굴을 입주 전에 진단하고 개선안을 냅니다 - 협의회가 요청하시면 진행합니다."
B.CSS += (".lxt{display:grid;grid-template-columns:1fr 1fr;gap:16px;flex:1;min-height:0}"
          ".lxt>div{border:1px solid var(--line);border-top:2px solid var(--gold2);border-radius:14px;padding:18px 22px;display:flex;flex-direction:column;gap:6px;"
          "background:linear-gradient(180deg,rgba(235,203,143,.08),rgba(255,255,255,.01) 45%)}"
          ".lxt i{font-style:normal;font-size:13px;letter-spacing:.16em;color:var(--gold2);font-weight:700}"
          ".lxt b{font-size:21px;color:var(--gold)}.lxt p{font-size:16px;line-height:1.5;color:var(--sub)}"
          ".lxstep{display:flex;align-items:stretch;gap:8px;margin-top:12px}"
          ".lxstep>div{flex:1;border:1px solid rgba(200,168,106,.45);border-radius:11px;padding:8px 12px;background:rgba(235,203,143,.05)}"
          ".lxstep i{font-style:normal;font-size:10.5px;letter-spacing:.18em;color:var(--gold2);font-weight:700}"
          ".lxstep b{display:block;font-size:15px;margin-top:2px}.lxstep span{display:block;font-size:12.5px;color:var(--sub);line-height:1.4;margin-top:2px}"
          ".lxstep em{align-self:center;color:var(--gold);font-weight:800;font-style:normal}")
new("std", sec="제안 개요", title=T_LX, lead=_lx_lead, body=_lx_body,
    kp=("단지 가치는 [[밤의 첫인상]]에서 - 협의회가 요청하시면 진단합니다.", (D.LX_CAP + " · " if _lxg else "") + D.ELEC_LICENSE))

# ------------------------------------------------------------ 담당 체계 · 경인 지사
new("std", sec="제안 개요", title=T_PM,
    lead=f"시공 · A/S는 {BR}가 관리 · 출동하고, 회의는 책임자가 단지로 찾아갑니다. 계약과 책임은 울산 본사입니다.",
    body=('<div class="nb"><div class="pmx">'
          '<div class="pc"><h3><i>PEOPLE</i>담당 체계</h3>'
          + B.rows([
              ("운영책임자", f"주관사업 총괄 본부장 {D.MANAGER[0]} - 계약 후 실제 업무를 맡을 책임자"),
              ("결정권자", "대표이사 - 제안 조건 확약 · 제안설명 직접 참석"),
              ("전담 PM", f"행사관리팀 정규직 1명(4대보험 명부 등재) · 실명은 계약 시 제출 {PG('staff')}"),
              ("상담 담당자", CONSULT_TXT),
          ], title_w=104) + '</div>'
          '<div class="pc"><h3><i>FIELD</i>현장 대응</h3>'
          + B.rows([
              ("관리 거점", f"{BR} - 상설 쇼룸 · 상담 · 접수 · 시공 관리 · A/S 출동"),
              ("직접 방문", "대면 회의 · 현장 답사 · 설명회 · 제안설명에 책임자가 직접 참석"),
              ("출동", "경인 지사 + 천안 · 아산권 참여 시공업체 · 업체 미응답 건은 주관사가 맡습니다."),
              ("입주 지정기간", "단지 안 상주 창구(위치 · 시간은 협의회 · 관리주체가 정함)"),
          ], title_w=96) + '</div></div></div>'),
    kp=("책임자가 [[찾아가고]], 경인 지사가 [[관리 · 출동]]합니다.", "운영책임자 · 주요 협력업체 변경 = 협의회 사전 승인(10항 바) · 계약과 책임은 울산 본사 · 지사 7곳 확장 중 · 2026.11 초 법인등기 예정(진행 중)"))

STAFF7 = [  # (구분, 인원, 역할, 기간)
    ("운영책임자", "1명", f"주관사업 총괄 본부장 {D.MANAGER[0]} · 관리감독 · 계약 · 제안설명", "계약 ~ 사후관리 종료"),
    ("상담 담당자", "1명", CONSULT_TXT, "계약 ~ 사후관리 종료"),
    ("전담 PM", "1명 · 정규직", "협의회 연락 · 일정 · 보고 · 업체 일정 관리 - 이 단지의 연락 창구", "계약 ~ 사후관리 종료"),
    ("업무 분담", "4개 팀 12명", "영업 2 · 행사관리 4 · 이벤트 3 · 대외지원 3 - 업무 시기별로 나눠 맡음", "업무 시기별"),
    ("연락체계", "콜센터 · PM · 책임자", "평일 09:00 ~ 18:00 콜센터 · 온라인 365일 접수 · 긴급 건 책임자 직통", "계약 ~ 사후관리 종료"),
]
new("std", sec="제안 개요", title=T_STAFF7,
    lead="공고 5항 가 · 4항 나 - 4대보험 사업장 가입자 13명(대표 포함 · 2026.10.23 명부) 가운데 이 단지를 맡을 사람과 역할입니다.",
    body=table(["구분", "인원", "역할", "기간"], "".join(
        f'<tr><td class="k">{t(a)}</td><td class="nb2">{t(b)}</td><td>{t(c) if "⟦" not in c else c}</td><td>{t(d)}</td></tr>' for a, b, c, d in STAFF7), "lgx st5"),
    kp=("운영책임자 · 상담 담당자 · [[전담 PM]] - 계약기간 내내 같은 창구입니다.", "변경 시 협의회 사전 승인 · 명단은 계약 시 제출 · 인력 현황 = 제출서류 나"))
B.CSS += ".tbl.st5 td{padding:13px 15px;font-size:15.5px}.tbl.st5 td.k{width:16%}.tbl.st5 td.nb2{width:20%;color:var(--gold);font-weight:700}"

# ------------------------------------------------------------ 일정(5항 나 · 1항 바 기간 구분)
MON = [  # (시기, 주관사 업무, 협의회 보고 · 산출물)
    ("2026.11", "제안서 제출 · 제안설명(통보 시 · 책임자 · 대표이사 참석) · 협상 · 계약(운영기간 · 사후관리 기간 구분 기재)", "협상 내용 서면 · 계약서"),
    ("2026.12", "전담 PM 연락 개시 · 연락 체계표 · 유상옵션 선택 집계 요청(협의회 경유) · 카페 이용방법 확정", "연락 체계표"),
    ("2027.01 ~ 2028.09", "월 1회 진행 보고 · 공정 · 입주 일정 확인 · 카페 안내 콘텐츠(협의회 승인) · 중간 점검(10항 사)", "월간 진행 보고"),
    ("2028.10 ~ 12", "품목 수요조사 · 겹침표 확정 · 업체 공개 모집 공고(천안 · 아산권 우선)", "수요조사 결과 · 모집 공고안"),
]
MON2 = [
    ("2029.01 ~ 03", "4단계 심사 · 업체 확정 · 특약이행각서 · 단가 제출 · 지역 비율 보고", "심사 결과 · 확정 명단"),
    ("2029.04 ~ 05", "매장 · 온라인 가격 조사 · D-30 검수 · 대관 · 안전계획(개최 시) · 행사배상책임보험(개최 시)", "검수 단가표"),
    ("2029.06 ~ 07", "D-14 확정가 · 비교자료 공개 · [[입주박람회(개최 시 · 주말 포함 2 ~ 3일(안))]] · 온라인 상담", "결과보고서(종료 후 30일 안)"),
    ("2029.09 ~", "[[입주 지정기간]] · 시공 · 설치 · 세대 확인 · 잔금 · 공동구매 A/S 접수 · 건설 하자 정리 · 전달(주 1회 보고)", "공동구매 운영기간 종료"),
    ("사후관리 기간", "운영기간 종료 다음 날 ~ 품목별 무상 A/S 만료 · 콜센터 · 카페 접수 · 업체 미응답 건 선보상 · 이관", "월 1회 보고"),
    ("종료 · 인계", "미처리 주문 · 환불 · A/S · 정산자료 인계(10항 자) · 제조사 장기 보증은 제조사 창구로 연결", "최종 보고서(종료 후 30일 안)"),
]


def _mon_tbl(rows):
    return table(["시기", "주관사 업무", "협의회 보고 · 산출물"], "".join(
        f'<tr><td class="n" style="width:170px;white-space:nowrap">{a}</td><td>{t(b)}</td><td class="k">{t(c)}</td></tr>' for a, b, c in rows), "lgx mn8")


new("std", sec="제안 개요", title=T_MON1,
    lead=f"공고 5항 나 - 계약부터 박람회 준비 전까지. 입주가 {ST['months']}개월 뒤라 이 기간에는 연락 창구 · 진행 보고 · 수요조사 준비가 중심입니다.",
    body=_mon_tbl(MON),
    kp=("입주 전 [[2년 넘는 기간]]에도 연락 창구와 월간 보고가 이어집니다.", "일정은 공정 · 사전점검 일정에 따라 협의회와 서면 조정(10항 사) · 중간 점검 시점과 해지 조건은 계약서에"))
new("std", sec="제안 개요", title=T_MON2,
    lead="수요조사 · 업체 확정부터 입주 · 사후관리 종료까지 - 공고 1항 바에 따라 공동구매 운영기간과 사후관리 기간을 나눕니다.",
    body=('<div class="nb">' + _mon_tbl(MON2)
          + f'<div class="itr g" style="margin-top:10px"><b>계약기간 구분</b><span>{t(SPLIT1)}<br>{t(SPLIT2)}</span></div></div>'),
    kp=("[[운영기간 / 사후관리 기간]]을 나눠 계약서에 - 끝이 열린 약속으로 남기지 않습니다.", "입주 지정기간 주 1회 · 이후 월 1회 보고 · 박람회 결과보고서 + 최종 보고서 · 날짜는 계약 때 확정"))
B.CSS += ".tbl.mn8 td{padding:11px 14px;font-size:15px}.tbl.mn8 td.k{width:24%;font-size:14.5px;color:var(--gold)}"

# ------------------------------------------------------------ 입점비 · 수수료 · 광고비 · 발전기금 명세(5항 마) — 항목 · 부과 대상 · 방식 · 상한만(세부 금액은 업체 모집 뒤 확정)
INCOME = [  # (항목, 부과 대상, 방식, 상한 · 공개)
    ("입점비(참가비)", "참여업체", "정액 · 같은 품목군은 같은 기준 · 공구가와 연동하지 않음", "업체 모집 공고 전에 협의회가 승인한 금액 이내 · 모집 공고에 공개"),
    ("판매수수료", "-", FEE_NOTE, "계약 건 · 매출 비례 수수료 없음"),
    ("광고비", "-", "별도로 받지 않음 · 카페 · 홍보물 제작은 입점비 안에서", "협의회 승인 후 게시"),
    ("발전기금", "업체에게 걷지 않음 · 주관사 부담", "협의회에 지급 · 공구가에 얹지 않음", f"{FUND_TXT} · {FD}"),
    ("업체 제공 혜택", "참여업체(별도)", "박람회 상품권 · 사은품 · 경품 · 현장 할인", "업체 확정 후 협의회 승인 · 발전기금과 별도"),
    ("임원 · 관계자 개인", "-", "금전 · 물품 · 향응 · 협찬금 제공 없음", "공고 9항 다 · 라 · 발전기금은 이 제안서 · 공식 협상 · 공증으로만"),
]
new("std", sec="제안 개요", title=T_INCOME,
    lead="공고 5항 마 - 무엇을 누구에게 어떤 방식으로 받는지, 상한은 어떻게 정하는지 적었습니다. 업체별 세부 금액은 업체 모집 전에 협의회 승인으로 확정합니다.",
    body=ftable(["항목", "부과 대상", "방식", "상한 · 공개"], ["20%", "20%", "34%", "26%"], "".join(
        f'<tr><td class="k">{t(a)}</td><td class="v">{t(b)}</td><td>{t(c)}</td><td>{t(d)}</td></tr>' for a, b, c, d in INCOME), "ic7"),
    kp=("주관사 수입은 [[입점비(정액) + 직영 품목 판매]] - 판매 · 소개 수수료와 별도 광고비는 받지 않습니다.", f"발전기금 = 협의회 지급 · 공증으로 진행(10항 아) · 공구가와 따로 {PG('sep')} · 업체 제공 혜택은 별도 표시"))
B.CSS += (".tbl.ic7 td{padding:12px 13px;font-size:14.5px;line-height:1.42;vertical-align:middle}.tbl.ic7 td.k{font-size:15.5px}"
          ".tbl.ic7 td.v{font-weight:700;color:var(--ink)}")

# ------------------------------------------------------------ 정산 · 보고 · 인계
REPORT = [  # (보고, 시점, 내용)
    ("연락 체계표", "계약 후 30일 안", "운영책임자 · 상담 담당자 · 전담 PM · 연락처 · 보고 양식"),
    ("월간 진행 보고", "매월(입주 지정기간은 주 1회)", "진행 · 일정 · 민원 처리 · A/S 처리 현황"),
    ("업체 모집 · 심사 결과", "업체 확정 시", "참여업체 명단 · 심사표 · 입점비 기준 · 지역 비율"),
    ("박람회 결과보고서", "종료 후 30일 안(개최 시)", "방문 · 상담 · 계약 · 민원 · 가격 비교 결과"),
    ("발전기금 지급 내역", "지급 후 30일 안", "지급일 · 금액 · 공증 내용 대비 이행 확인"),
    ("최종 보고서 · 인계", "사후관리 종료 · 해지 후 30일 안", "전체 정산 · A/S 처리 결과 · 미처리 업무 인계 목록 · 남은 제조사 보증 안내"),
]
new("std", sec="제안 개요", title=T_REPORT,
    lead="공고 3항 바 · 10항 자 - 무엇을 언제 보고하고, 끝날 때 무엇을 넘기는지 미리 정해 둡니다.",
    body=('<div class="nb">' + ftable(["보고", "시점", "내용"], ["28%", "26%", "46%"], "".join(
        f'<tr><td class="k">{t(a)}</td><td class="v">{t(b)}</td><td>{t(c)}</td></tr>' for a, b, c in REPORT), "rp7") + '</div>'),
    kp=("보고 [[6가지]]의 항목과 시점을 정해 두었습니다 - 계약서에 그대로 옮깁니다.", "보고 양식은 계약 후 30일 안 협의회와 확정"))
B.CSS += (".tbl.rp7 td{padding:11px 12px;font-size:14.5px;line-height:1.42;vertical-align:middle}.tbl.rp7 td.k{font-size:15px}"
          ".tbl.rp7 td.v{color:var(--gold);font-weight:700}")

# ------------------------------------------------------------ 9항 · 10항 지킬 것
FAIR = [
    ("9항 다 · 라", "금품 · 향응 · 담합 · 공식 절차 밖 약속", "하지 않음 · 발전기금 · 수수료는 이 제안서와 공식 협상으로만"),
    ("4항 마 · 9항 라", "이해관계 공개", YN(D.CONFLICT_OK, "이해관계 없음 · 확약서(제출서류 바)", "이해관계 '없음' - 본부장 확인")),
    ("4항 사 · 9항 바", "협의회 계약 해지 · 소송 이력", YN(D.HISTORY_OK, "없음 · 확인서(제출서류 아)", "해지 · 소송 이력 '없음' - 본부장 확인")),
    ("6항 바 · 9항 사", "공고일 이후 사전 만남 · 개별 연락", "하지 않음 - 지정 이메일 · 공식 통보한 제안설명 · 협상만"),
    ("9항 마", "선정 전 공식 주관사 홍보 · 개인정보 수집", "하지 않음"),
    ("9항 나", "자격 · 실적 · 인력 · 보험 · 가격 자료", "사실대로 · 보험은 종류 그대로 · 가격은 참고가격으로 표시"),
    ("10항 라 · 차", "추가 책임 · 보험 · 보증 · 협상 내용", "범위 · 절차 · 금액 · 기간을 계약서에 · 협상 내용은 서면으로"),
]
new("std", sec="제안 개요", title=T_FAIR,
    lead="공고 9항(입찰 무효 · 선정 취소)과 10항(계약 · 유의사항)을 확인했습니다. 선정 결과와 관계없이 지킵니다.",
    body=ftable(["공고", "원칙", "엣지컴퍼니 확인"], ["16%", "36%", "48%"], "".join(
        f'<tr><td class="g">{a}</td><td class="k">{t(b)}</td><td>{t(c) if "⟦" not in c else c}</td></tr>' for a, b, c in FAIR), "m9 mpv"),
    kp=("금품 없이, 개별 연락 없이, [[제안한 그대로]] - 선정 결과와 관계없이 지킵니다.", "청렴 · 이해관계 · 개인정보 · 비밀유지 확약서 = 제출서류 바 · 해지 · 소송 이력 확인서 = 제출서류 아"))

# ------------------------------------------------------------ 참가자격 4항 가 ~ 사
QUAL = [  # (공고 4항, 엣지컴퍼니 현황, 증빙 = 제출서류)
    ("가) 관련 사업자등록 · 최근 5년 운영 실적", f"법인 설립 · 개업 {D.FOUNDED} · " + YN(D.BIZ_ITEM_OK, "업태 · 종목 해당(사업자등록증)", "사업자등록 종목(공동구매 · 행사 대행) 해당 여부 - 본부장 확인") + f" · 최근 5년 500세대 이상 입주박람회 주관 {len(D.R5Y)}개 단지(1,000세대 이상 {len(D.R5Y_1000)}개 단지) {PG('recs')}", "가 · 나"),
    ("나) 운영책임자 · 상담 담당자 지정", f"운영책임자 = 총괄 본부장 {D.MANAGER[0]} · 상담 담당자 = " + CONSULT_TXT + f" · 전담 PM {PG('staff')}", "나"),
    ("다) 국세 · 지방세 체납 없음", f"국세 · 지방세 납세증명서({D.ISSUE['tax']})", "다"),
    ("라) 개인정보 관리방안", f"수집 · 보관 · 이용 · 파기 절차 {PG('priv')}", "라 · 바"),
    ("마) 이해관계 공개", YN(D.CONFLICT_OK, "이해관계 없음 · 확약서로 공개", "이해관계 '없음' - 본부장 확인"), "바"),
    ("바) 보험 또는 보증 제공계획", f"영업배상책임보험 가입 중 · 행사배상 박람회 확정 시 · 계약 후 보증 {PG('ins')}", "마"),
    ("사) 해지 · 소송 이력(진행 중 포함) 없음", YN(D.HISTORY_OK, "없음 · 확인서", "해지 · 소송 이력 '없음' - 본부장 확인"), "아"),
]
new("std", sec="제안 개요", title=T_QUAL,
    lead="공고 4항 참가자격 가 ~ 사 - 요건마다 엣지컴퍼니 현황과 증빙 서류(7항 번호)를 맞췄습니다.",
    body=ftable(["참가자격", "엣지컴퍼니 현황", "서류"], ["32%", "58%", "10%"], "".join(
        f'<tr><td class="k">{t(a)}</td><td>{t(b) if "⟦" not in b else b}</td><td class="ev">{t(c)}</td></tr>' for a, b, c in QUAL), "q17"),
    kp=("참가자격 [[가 ~ 사 모두]] - 요건마다 증빙 서류를 붙였습니다.", f"자본금 = 법인등기 기재 2억원 · 누적 수임 {_cum[3]}개 단지 · {_cum[4]:,}세대는 ‘수임’ 표기(전신 실적 · 입주 예정 포함 · 주관 아님)"))
B.CSS += (".tbl.q17 td{padding:10px 12px;font-size:14px;line-height:1.4;vertical-align:middle}.tbl.q17 td.k{font-size:14.5px}"
          ".tbl.q17 td.ev{font-size:14px;color:var(--gold);font-weight:700;text-align:center}")

# ------------------------------------------------------------ 1차 책임 · 주관사 추가 책임(5항 사 · 10항 다 · 라)
GUARD6 = [
    ("1차 책임", "납품 · 시공 · 취소 · 환불 · 사후관리 = 판매 · 시공업체(10항 다) - 참여업체 전원 특약이행각서"),
    ("추가 책임이 생기는 때", "업체가 기한 안에 이행하지 않거나(미이행) 폐업 · 연락 두절로 처리가 어려울 때 - 주관사가 사실을 확인한 뒤"),
    ("추가 책임 범위", "공동구매로 계약한 품목의 환불 · 하자보수 · A/S · 대체 시공 · 이관 - 건설 하자는 사업주체 · 시공사 책임(제외)"),
    ("한도", "계약서에 정한 보증 금액 안 · 최저가 차액 10배 보상은 1건당 최대 50만원(주관사 지급) · 무상 A/S 기간 안 이관 비용"),
    ("절차", "접수 → 업체 통보 · 24시간 회신 요구 → 미이행 확인 → 주관사 선보상 또는 대체 업체 이관(협의회 승인 · 계약자 동의) → 업체 정산 · 페널티 → 협의회 보고"),
    ("계약서 명시", "추가 책임 이행범위 · 절차 · 보험 · 보증 금액 · 기간 · 보장 대상을 계약서에 적습니다(10항 라)."),
]
new("std", sec="제안 개요", title=T_BOND,
    lead="공고 5항 사 · 10항 다 - 1차 책임은 참여업체가 집니다. 업체가 이행하지 않거나 폐업 등으로 처리가 어려우면 주관사가 추가 책임을 지고 처리합니다. 그 범위와 한도를 먼저 밝힙니다.",
    body=('<div class="nb">' + B.rows(GUARD6, title_w=190) + '</div>'),
    kp=("업체가 사라져도 [[공동구매 품목의 책임은 남도록]] - 범위 · 한도 · 절차를 계약서에 적습니다.", f"건설 하자 = 사업주체 · 시공사 · 보증 금액은 협약 시 확정 {PG('ins')} · 하자 예치금 {PG('deposit')}"))

# ------------------------------------------------------------ 보험 · 보증(5항 아) — 보험은 종류 그대로(영업배상 = 본사 시설 기준 · 피해보상 보험으로 쓰지 않음)
INS = [  # (종류, 금액, 기간, 보장내용, 청구 대상, 증서 제출시기)
    ("계약 후 보증(계약이행 · 하자보증보험)", "협약 시 금액 확정", "24개월 · 운영기간부터 무상 A/S 종료까지 공백 없게 기산일을 협약 때 정함", "주관사 계약상 의무 · 추가 책임 이행", "협의회(피보험자)", "협약 체결 시 보증보험사 심사를 거쳐 발급 · 제출일은 계약서에"),
    ("행사(주최자)배상책임보험", "행사 규모에 맞춰 협의회와 정함", "박람회 설치 ~ 철거 기간", "박람회장 관람객 등 제3자 신체 · 재물 사고", "피해를 입은 관람객 등", "개최 확정 시 가입 · 개장 전 증권 사본"),
    ("하자 예치금(주관사 자산)", "최대 1억원 · 금액은 계약 때 확정", "사후관리 기간", "선보상 재원(업체 미이행 · 폐업 건)", "계약자(주관사 선보상)", "예치 방식 · 확인 자료는 계약 때"),
    ("영업배상책임보험(시설소유관리자배상책임 · KB손해보험 · 가입 중)", "대인 1인당 1억 · 1사고당 3억 · 대물 1사고당 1억 · 구내치료비 1인당 100만원", "2026.10.14 ~ 2027.10.14(매년 갱신)", "본사 사업장 시설 소유 · 관리 중 제3자 신체 · 재물 사고", "피해를 입은 제3자", "증권 사본 = 지금(제출서류 마)"),
]
new("std", sec="제안 개요", title=T_INS,
    lead="공고 5항 아 · 4항 바 - 지금 가입한 보험은 종류 그대로 적고, 박람회 · 계약 뒤에 더하는 보험 · 보증은 언제 무엇을 내는지 적었습니다.",
    body=('<div class="nb">' + ftable(["종류", "금액", "기간", "보장내용", "청구 대상", "증서 제출시기"], ["21%", "19%", "15%", "18%", "12%", "15%"], "".join(
        f'<tr><td class="k">{t(a)}</td><td class="v">{t(b)}</td><td>{t(c)}</td><td>{t(d)}</td><td>{t(e)}</td><td>{t(f)}</td></tr>' for a, b, c, d, e, f in INS), "is6")
          + '<div class="itr" style="margin-top:10px"><b>순서</b><span>계약 후 보증 = 협약 체결 시 보증보험사 심사를 거쳐 협의회를 피보험자로 발급(금액은 협약 시 확정) → 박람회 행사배상 = 개최 확정 시 가입 → 현재 가입 = 영업배상책임보험(시설소유관리자배상책임 · 본사 사업장).</span></div></div>'),
    kp=("보증은 [[금액 · 기간 · 대상을 계약서에]], 보험은 [[종류 그대로]] 적습니다.", "참고 · 다른 용역 계약보증 1건(SGI · 입주박람회 이행보증 아님 · 제출서류 마 붙임) · 영업배상 증권 사본 = 제출서류 마"))
B.CSS += (".tbl.is6 td{padding:9px 9px;font-size:13px;line-height:1.38;vertical-align:middle}.tbl.is6 td.k{font-size:13.5px}"
          ".tbl.is6 td.v{color:var(--gold);font-weight:700}")

# ------------------------------------------------------------ 개인정보(5항 자 · 4항 라 · 10항 마)
PRIV = [
    ("수집", "사전 등록 · 상담 신청 때 본인이 직접 입력한 항목만(이름 · 동 · 호 · 연락처) · 필수 / 선택 동의를 나눠 받음 · 회원명부는 받지 않음"),
    ("보관", "접근 권한자 지정(운영책임자 · 전담 PM) · 잠금 저장 · 출력물 반출 금지"),
    ("이용 · 제공", "안내 · 상담 · 계약 이행 · A/S 연락에만 · 계약한 업체에 그 계약 이행에 필요한 항목만 · 다른 영업 · 광고 · 제3자 제공 없음"),
    ("파기", "목적 달성(사후관리 종료) 후 지체 없이 파기 · 업체 보유분도 파기 확인서 회수 · 결과를 협의회에 보고"),
]
CHOICE = [
    ("강제 없음", "특정 제품 · 업체 구매를 권하거나 끼워 팔지 않음"),
    ("비교 먼저", "같은 품목은 복수 업체 · 단가 사전 공개 · 일반 판매가 비교자료"),
    ("겹침 안내", "유상옵션을 고른 세대에는 같은 품목을 권하지 않음"),
    ("숙려 · 취소", "품목별 취소 기한 안에는 이유 없이 전액 환불 · 해피콜 미이행 시 당일 취소"),
]
new("std", sec="제안 개요", title=T_PRIV,
    lead="공고 5항 자 · 4항 라 · 10항 마 - 입주예정자의 개인정보는 공동구매 운영에만 쓰고, 사는 것도 사지 않는 것도 입주예정자가 정합니다.",
    body=('<div class="nb"><div class="pmx">'
          '<div class="pc"><h3><i>PRIVACY</i>수집 · 보관 · 이용 · 파기</h3>' + B.rows(PRIV, title_w=86) + '</div>'
          '<div class="pc"><h3><i>CHOICE</i>구매 선택권 보장</h3>' + B.rows(CHOICE, title_w=96) + '</div></div></div>'),
    kp=("개인정보는 [[운영에만]], 선택은 [[입주예정자가]].", "개인정보 처리는 관련 법령 절차에 따름 · 회원명부 영업 이용 없음 · 개인정보 보호 확약 = 제출서류 바"))

# ------------------------------------------------------------ 재위탁 · 업체 변경 · 인계(5항 자 · 10항 바 · 자)
TERMS = [
    ("재위탁", "사업 전체 재위탁 없음", "행사장 설치 · 촬영 등 전문 업무만 협의회 사전 승인 뒤 범위를 정해 맡김 · 책임은 주관사(10항 바)"),
    ("업체 변경", "협의회 사전 승인", "변경 후에도 기존 구매계약 · 사후관리를 새 업체가 이어받음(계약자 동의) · 변경 내역 보고"),
    ("미처리 업무 인계", "종료 · 해지 후 30일 안", "미처리 주문 · 환불 · A/S 접수 목록 · 업체 연락처 · 정산자료를 합의한 방법으로 협의회(또는 지정 주관사)에 인계 · 인계 확인서(10항 자)"),
    ("독점권 · 비용 요청", "요청하지 않음", "품목 · 기간 독점 요청 없음 · 협의회에 운영 비용 청구 없음(박람회 기본안 = 참가업체 참가비로 운영) · 바라는 것은 공지 승인 · 일정 공유"),
]
new("std", sec="제안 개요", title=T_TERMS,
    lead="공고 5항 자 · 10항 바 · 자 - 맡긴 일을 다른 데 넘기지 않고, 끝날 때 남은 일을 빠짐없이 넘기는 방법입니다.",
    body=ftable(["구분", "엣지컴퍼니", "범위 · 방법"], ["18%", "22%", "60%"], "".join(
        f'<tr><td class="g">{a}</td><td class="k">{t(b)}</td><td>{t(c)}</td></tr>' for a, b, c in TERMS), "m9 tm4"),
    kp=("재위탁은 [[사전 승인]], 인계는 [[30일 안 목록으로]] - 계약서에 범위를 적습니다.", "인계 대상 = 미처리 주문 · 환불 · 사후관리 · 정산자료(10항 자)"))
B.CSS += ".tbl.tm4 td{padding:15px 15px;font-size:15.5px;line-height:1.45}.tbl.tm4 td.k{color:var(--gold)}.tbl.tm4 td.g{white-space:nowrap;font-weight:800;color:var(--gold)}"


# ------------------------------------------------------------ 세대 혜택 선택 항목 가격표(세대당 15만원 기준 · 총액 없음)
T_MENU = "선택 항목 [[가격표]] · 세대당 담는 예시 3가지"
_TAG = {"차감": ("15만원에서 셈", "tg-c"), "할인": ("할인 혜택 · 15만원에서 빼지 않음", "tg-f"), "업체": ("업체 제공 · 별도", "tg-v"), "견적": ("설치 시 별도 견적", "tg-e")}
MENU_ROWS = [  # (구분, 항목, 기준, 세대당, 꼬리표) — 주관사가 직접 사서 세대에 드리는 항목만(규칙 9)
    ("A", "백화점 상품권", "세대당 5만원 또는 10만원 · 세대에 현물 직접 · 세대 수령 확인 · 집행 내역 공개", "5만 / 10만원", "차감"),
    ("A", "방문 선물 · 실측 · 샘플하우스 · VR · 3D", "계약 세대 · 타입별 · 대표 타입", "단가 · 수량 협상 때 정함", "차감"),
    ("A", "사전점검 대행 할인", "참고 예시(타 단지 대행업체 조건) · 업성 할인율은 모집 조건(안)", "0원", "할인"),
    ("C", "공용부 · 경관조명 진단 뒤 시공", "협의회 · 관리주체 승인 시", "별도 견적", "견적"),
    ("업체", "박람회 상품권 · 계약 사은품 · 경품 · 현장 할인", "참여업체 확정 후 협의회 승인", "0원", "업체"),
]


def _menu_tbl():
    return table(["구분", "항목", "기준", "세대당", "15만원 계산"], "".join(
        f'<tr><td class="g">{a}</td><td class="k">{t(b)}</td><td>{t(c)}</td><td class="r">{t(d)}</td>'
        f'<td><span class="tgx {_TAG[e][1]}">{_TAG[e][0]}</span></td></tr>' for a, b, c, d, e in MENU_ROWS), "mnu")


def _mix(no, name, gift, rest):
    w = round(100 * gift / D.FUND) if gift else 0
    bar = (f'<div class="mbar"><div class="mf" style="width:{w}%"></div>'
           f'<div class="ml">{"상품권 " + str(gift) + "만원 · " if gift else ""}남은 {D.FUND - gift}만원</div></div>')
    return f'<div class="mx"><div class="mh"><em>{no}</em><b>{name}</b></div>{bar}<p>{t(rest)}</p></div>'


new("std", sec="제안 개요", title=T_MENU,
    lead=f"세대당 15만원 상당(안) 안에서 협의회가 골라 담습니다. 대상은 {FB}이며, 주관사가 직접 사서 세대에 드리고 협의회 · 임원에게 금전 · 물품은 드리지 않습니다.",
    body=('<div class="nb"><div class="mnx"><div class="mnl">' + _menu_tbl() + '</div><div class="mnr"><h4>세대당 담는 예시 3가지</h4>'
          + _mix("①", "상품권형", 10, "상품권 10만원 · 남은 금액으로 방문 선물 · 실측")
          + _mix("②", "균형형", 5, "상품권 5만원 · 남은 금액으로 실측 · VR · 3D · 방문 선물")
          + _mix("③", "서비스형", 0, "상품권 없이 실측 · VR · 3D · 방문 선물로 구성")
          + '</div></div></div>'),
    kp=("고른 항목의 합계가 [[세대당 15만원 상당]] 안에 들어오도록 맞춥니다 - 집행 내역은 공개합니다.",
        f"{FB} 기준 · {FD} · 할인 항목은 15만원에서 빼지 않음 · 업체 제공 혜택은 별도"))
B.CSS += (".mnx{display:grid;grid-template-columns:1.62fr 1fr;gap:18px;flex:1;min-height:0}"
          ".tbl.mnu td{padding:8px 9px;font-size:13.5px;line-height:1.38}.tbl.mnu td.g{width:42px;text-align:center;font-weight:800}.tbl.mnu td.k{font-size:14px;width:33%}"
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
          ".mx p{font-size:12.5px;color:var(--sub);line-height:1.4}"
          ".mnr{gap:8px!important}.mnr .mx{flex:0 0 auto!important;padding:8px 12px!important;gap:5px!important}.mnr .mbar{height:24px!important;flex:0 0 24px!important}")


# 대응표 쪽 번호 — 재배치 뒤 제목으로 찾는다(reorg에서 바뀐 제목은 바뀐 뒤 제목)
PGREF = {
    "hist": T_HIST, "people": T_PEOPLE, "r500": T_R500, "vendors": T_VENDORS,
    "guard4": "공동구매 단가를 지키는 [[4가지 장치]]", "x10": "[[최저가 차액 10배]] 보상",
    "rule1": T_RULE1, "rule2": T_RULE2, "cpl": T_CPL, "as": T_AS, "safe": T_SAFE, "expo": T_EXPO,
    "fund": T_INCOME, "menu": T_SEP, "sep": T_SEP,   # 본부장 11-03: 세대 혜택 장 뺌 → 발전기금 명세 · 공구가와 따로
    "one": T_ONE, "prom": T_PROM, "voice": T_VOICE, "mapa": T_MAPA, "site": T_SITE, "items": T_ITEMS, "opt": T_OPT,
    "price": T_PRICE, "expoplan": T_EXPOPLAN, "cancel": T_CANCEL, "recs": T_RECS, "cafe": T_CAFE, "check": T_CHECK, "care": T_CARE, "escrow": T_ESCROW,
    "desk": T_DESK, "license": T_LICENSE, "local": T_LOCAL, "role": T_ROLE, "lx": T_LX,
    "pm": T_PM, "staff": T_STAFF7, "mon1": T_MON1, "mon2": T_MON2, "income": T_INCOME, "report": T_REPORT, "fair": T_FAIR,
    "qual": T_QUAL, "docs": T_DOCS, "bond": T_BOND, "ins": T_INS, "priv": T_PRIV, "terms": T_TERMS,
    "call": "주관 [[콜센터]]와 선보상", "flow": "클레임 [[처리 흐름]]과 CRM 관리", "bond24": "계약이행 · 하자보증 [[24개월]]", "k1000": "1,000세대 이상 [[주관 단지]]",
    "city": "한 신도시의 여러 단지를 [[연속으로]] 맡았습니다",
    "floor": "박람회장 배치와 [[인원 운영]] (안)", "crit": "업체 [[심사 기준]]과 계약 원칙", "screen": "[[4단계]] 공개 심사 프로세스",
    "deposit": "선보상 재원 · 하자 예치금 [[최대 1억원]]",
    **{k: T_CH[k] for k in T_CH},
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
B.PAGES[i][1]["kp"] = f"누적 수임 [[{D.cumulative()[-1][3]}개 단지 · {D.cumulative()[-1][4]:,}세대]] - 전신 실적 · 입주 예정 포함(주관 실적과 구분)"

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
    _suim = D.SUIM  # 본부장 10-24: 엘크루(중복)는 아래 목록 줄에서만 뺌 · 제목 43곳 · 누계 숫자는 그대로('다른 거 손대지 마')
    _rows = (sorted([r for r in _suim if r[1] >= 1000], key=lambda r: -r[1])
             + sorted([r for r in _suim if r[1] < 1000], key=lambda r: r[3]))
    _now = "2026.10"
    _held = {r[1] for r in D.RECENT3_500}  # 박람회를 이미 치른 단지(영주자이 2026.08 개최 · 2026.12 입주) — '개최 예정'에서 뺀다
    _li = "".join(f'<li class="{"big" if n >= 1000 else ""}{" fut" if m > _now else ""}"><span>{nm} <i>{m}{" 입주 · 주관 개최 예정" if m > _now and nm not in _held else " 입주 예정" if m > _now else ""}</i></span>'
                  f'<b>{n:,}{u}</b></li>' for nm, n, u, m in _rows if nm not in getattr(D, "SUIM_HIDE", ()))
    _cols = [f"<ul>{_li}</ul>"]
    _n1k = sum(1 for r in _rows if r[1] >= 1000)
    _nfut = sum(1 for r in _rows if r[3] > _now and r[0] not in _held)
    _di = next(i for i, (_, k) in enumerate(B.PAGES) if k.get("title") == "[[대단지]] 운영 경험")
    B.PAGES.insert(_di + 1, ("std", dict(sec=B.PAGES[_di][1].get("sec", ""), title=f"2023년 이후 수임 단지 [[{sum(D.DANJI_N.get(r[0], 1) for r in _rows)}곳]]",
        lead="1,000세대 이상(금색)은 세대수 순, 나머지는 입주 순 · 날짜는 입주 연월 · 입주 전 단지는 박람회 주관 개최 예정.",
        body='<div class="ylist">' + "".join(_cols) + "</div>",
        kp=(f"{sum(D.DANJI_N.get(r[0], 1) for r in _rows)}개 단지 · 1,000세대 이상 [[{_n1k}곳]](입주 예정 포함) · 주관 개최 예정 [[{_nfut}곳]]",
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
    B.PAGES.insert(_ci, ("std", dict(sec=B.PAGES[_ci][1].get("sec", ""), title=T_CORE6,
        lead="숫자로 약속하고, 협약서로 지킵니다.",
        body=B.tiles([
            dict(lb="발전기금", big=f"{D.FUND}", unit="만원", nm="세대당 기준(안)",
                 ds=f"협의회 지급 · {D.FUND_DECIDE}"),
            dict(lb="하자 예치금", big="1", unit="억원", nm="현금 예치", ds="엣지컴퍼니 자산으로 입예협 공동통장에 직접 예치"),
            dict(lb="이행보증보험", big="10", unit="억원", nm="2년 보증", ds="증권 실물을 입예협에 전달"),
            dict(lb="최저가 보장", big="10", unit="배", nm="차액 보상", ds="인근 매장 동일 제품이 더 싸면 차액 10배 보상(구매 영수증 · 주관사 확인 · 1건당 최대 50만원 · 온라인·시공 품목 제외)"),
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
COVER = dict(kind="stats", pill="공동구매 주관사 제안서 · 입주박람회 운영계획 포함",
             tag=f"성성호수공원 곁 업성3도시개발구역 {D.SITE['households']:,}세대의 공구가 · 가격 공개 · A/S를 같은 기준으로.<br>천안 · 아산 생활권 업체와 함께, 사후관리 기간이 끝날 때까지 책임지겠습니다.")
TITLE_H1 = "업성 푸르지오<br>레이크시티<br><em>공동구매 주관사 제안서</em>"
COVER_TOP = """<div class="top"><div><div class="logo">EG</div><div class="en">EDGE COMPANY</div></div>
<div class="who">주식회사 엣지컴퍼니<br>공동구매 · 입주박람회 주관사</div></div>"""


def p_cover():
    sub2 = f'<div class="sub2"><div><i>제출처</i><b>{D.CLIENT}</b></div><div><i>제안사</i><b>{D.COMPANY}</b></div></div>'
    # 표지 이미지 = 슬롯 'cover'(data.IMG) — 네이비 배경에 스며들도록 위·왼쪽을 배경색으로 페이드. 파일이 없으면 이미지 없이 중립 디자인
    im, _own = slot("cover")
    art = (f'<div class="cvart cvx osc day"><img src="assets_ins/{im}.jpg" alt="">'
           f'<span class="credit">{D.SITE["name"] + " 단지 전체 투시도 · 홍보용 이미지 · 실제와 다를 수 있음" if _own else "타 단지 연출 예시 이미지 · 이 단지 실제 모습 아님"}</span></div>') if im else ""
    return f"""<section class="page cv cv4">{art}{COVER_TOP}
<div class="mid"><span class="pill">{COVER['pill']}</span>
<h1 class="cvx">{TITLE_H1}</h1>
<div class="gbar"></div>
<div class="tag2">{COVER['tag']}</div>
</div>
{sub2}
<div class="bt"><span>공동구매 주관사 제안서(입주박람회 운영계획 포함) · 1BL</span><span>2026.11</span></div>
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
<div class="addr"><b>경인 지사</b> 경기도 평택시 비전동 · 상설 쇼룸(상담 · 시공 관리 · A/S 출동)<br><b>울산 본사</b> {D.ADDRESS}(계약 · 책임)<br>
<b>콜센터</b> 평일 09:00 ~ 18:00 · 온라인 365일 접수 · 24시간 이내 회신<br>
<b>등록 · 인증</b> {D.ELEC_LICENSE} · ISO 9001 / 14001 / 45001<br><b>제휴</b> 삼성 측 업무제휴 · 세스코 MOU</div>
</div>
<div class="bt"><span>공동구매 주관사 제안서 · {D.SITE['name']}</span><span>주식회사 엣지컴퍼니</span></div>
</section>"""


B_p_contact = B.p_contact


def won(man):
    """만원 → '2억 1,199만원'"""
    eok, rest = divmod(man, 10000)
    if not eok:
        return f"{rest:,}만원"
    return f"{eok}억 {rest:,}만원" if rest else f"{eok}억원"


def p_hi_fund(no, sec):
    s = B_p_hi_fund(no, sec)
    s = sub(s, '<span class="v">15만원</span>', f'<span class="v">{D.FUND}만원</span>')
    s = sub(s, "세대수 × 15만원 규모의 발전지원금을 협의회와 협의해 집행합니다.",
            f"<em>{D.FUND_BASIS}</em>에 주관사가 직접 사서 드리는 선택 항목으로 집행합니다.")
    s = sub(s, "<span>현금성 지원</span>", "<span>현물 · 서비스 · 협의회 계좌 거치지 않음</span>")
    return sub(s, "예: 1,000세대 단지 기준 <em>1억 5천만원</em>의 발전지원 규모.",
               f"세대당 {D.FUND}만원 상당(안 · 부가세 포함) · <em>{D.FUND_DECIDE}</em>")


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
    items = [(f"발전기금 세대당 {D.FUND}만원 기준(안)", f"협의회 지급 · {D.FUND_DECIDE}"),
             ("하자 예치금 최대 1억 · 보증보험 24개월", "엣지컴퍼니 자산으로 예치 · 보증 금액은 협약 시 확정"),
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
    band = (f'<div class="kp"><b>KEY POINT</b><span>5항 가 ~ 자 한 장 요약 · <em>{PG("one")}</em> · 약속 10가지 · <em>{PG("prom")}</em> · 3항 · 4항 대응표 · <em>{PG("mapa")}</em>'
            f'<small>7항 제출서류 가 ~ 아 · {PG("docs")} · 부록 입주박람회 운영계획(안) · {PG("app")}</small></span></div>')
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


FIX3 = [
 ["VOC 접수 시 24시간 내 회신. 업체 미응답 시 주관사가 직접 개입.", "VOC 접수 시 24시간 내 1차 회신(주말 · 공휴일 접수는 다음 영업일 12시까지). 업체가 24시간 무응답이면 주관사가 직접 개입."],
 ["업체 책임이 확인되면 입주민께 먼저 보상하고, 업체와는 나중에 정산합니다.", "업체가 무응답이거나 처리를 미루면 주관사가 사실 확인 뒤 입주민께 먼저 보상하고, 업체와는 나중에 정산합니다."],
 ["한 회사 안에서 끝나, 유통 단계 없이 단지에 도착합니다.", "한 회사가 맡아, 중간 유통 마진을 줄여 단지에 도착합니다."],
 ["직접시공을 한 회사가 맡고, 설치 여부 · 비용은 입예협 · 관리주체가 정합니다.", "직접시공을 한 회사가 맡고, 설치 여부 · 비용은 입예협 · 관리주체가 정합니다. 아래 도면은 설명용 예시입니다(단지 진단 뒤 작성)."],

 [
  "담당 책임자를 따로 지정합니다.",
  "전담 PM을 따로 지정하고, 박람회 주말 · 현장 인력이 겹치지 않게 협약 직후 확정합니다."
 ],
 [
  "박람회 시점에 판매 중인 현행 모델 기준 · 이월 · 전시 상품은 계약서에 따로 표시합니다.",
  "박람회 시점 각 브랜드의 최신 출시 모델을 기본으로 올리고, 이월 · 전시 상품은 입주민이 원할 때만 별도 단가로 표시합니다."
 ],
 [
  "<td>24시간 안 1차 회신 · 48시간 안 방문 일정 확정 · 업체가 24시간 무응답이면 주관사 개입</td>",
  "<td>24시간 안 1차 회신(주말 · 공휴일 = 다음 영업일 12시) · 48시간 안 방문 일정 확정 · 업체가 24시간 무응답이면 주관사 개입</td>"
 ],
 [
  "<div class=\"ds\">24시간 안 1차 회신 · 업체가 24시간 무응답이면",
  "<div class=\"ds\">24시간 안 1차 회신(주말 · 공휴일 = 다음 영업일 12시) · 업체가 24시간 무응답이면"
 ],
 [
  "48시간 A/S가 가능한 이유",
  "48시간 방문 일정이 가능한 이유"
 ],
 [
  "가까운 업체일수록 48시간 A/S를 지키기 쉽습니다.",
  "가까운 업체일수록 48시간 안 방문 일정을 지키기 쉽습니다."
 ],
 [
  "<em>48시간 A/S가 실제로 지켜집니다.</em>",
  "<em>48시간 안 방문 일정 확정이 실제로 지켜집니다.</em>"
 ],
 [
  "A/S 승계(비용 주관사 부담)",
  "A/S 승계(무상 A/S 기간 안 이관 비용 주관사 부담)"
 ],
 [
  "그래서 A/S 비용은 주관사 구조로 해결합니다.",
  "그래서 창구 운영비 · 예치금 · 추가 보증금을 업체에 요구하지 않습니다."
 ],
 [
  "<span>차액 10배 보상</span>",
  "<span>최저가 시 판매가 조정</span>"
 ],
 [
  "업무범위 밖 공사 · 설치만 별도 협의",
  "업무범위 밖 공사 · 설치 · 법률 대리만 별도 협의"
 ],
 [
  "세대 혜택을 0원으로 해도 공구가는 같습니다 - 가격은 <em>업체 경쟁과 가격 검수</em>로 정해집니다.",
  "발전기금은 공구가에 얹지 않습니다 - 공구가는 <em>업체 경쟁과 입예협 가격 검수</em>로 정해집니다."
 ],
 [
  "세대당 15만원 상당(총 1억 65만원 상당)을 주관사가 직접 사서 드립니다.",
  "같은 기준입니다. 세대당 15만원 상당(총 1억 65만원 상당) 범위에서 입예협이 고른 항목을 주관사가 직접 사서 제공합니다."
 ],
 [
  "참여업체 의무 조건",
  "참여업체 입찰 조건"
 ],
 [
  "개별 안내 없음",
  "특정 세대에만 주는 정보 없음"
 ],
 [
  "라돈측정기 10대",
  "라돈측정기(수량 협의)"
 ],
 [
  "검색 상위 노출 키워드 광고와 기획 보도로",
  "네이버 키워드 광고와 기획 보도로"
 ],
 [
  "협의회 협의 후 <em>단지 맞춤 경관조명 제안서</em>를 별도 제출합니다.",
  "입예협이 요청하시면 <em>단지 맞춤 경관조명 제안서</em>를 별도로 드립니다."
 ],
 [
  "품목은 입주민 투표로 정해 직수입 공동구매.",
  "품목은 입예협과 협의해 직수입 공동구매."
 ],
 [
  "같은 품목에 다른 업체도 공개 입찰로 참여합니다.",
  "같은 품목에 다른 업체도 공개 입찰로 참여할 수 있습니다."
 ],
 [
  "참가 예정 · 같은 심사 · 기본 제공 환풍기와 겹침 확인",
  "참가 희망 · 공개 모집 · 심사 후 확정 · 기본 제공 환풍기와 겹침 확인"
 ],
 [
  "1:1로 맞췄습니다",
  "항목별로 맞췄습니다"
 ],
 [
  "월 1회 이상 방문",
  "월 1회 방문"
 ],
 [
  "<span>행사배상책임보험 · 박람회 기간 가입</span>",
  "<span>행사주최자배상책임보험 · 박람회 기간 가입</span>"
 ],
 [
  "박람회 운영비와 세대당 15만원 상당을 주관사 몫에서 부담",
  "세대당 15만원 상당을 주관사 몫에서 부담 · 공구가와 분리"
 ],
 [
  "평당 ",
  "3.3㎡당 "
 ],
 [
  "서명 이미지·일시·필압을 기록해",
  "서명 이미지·일시를 기록해"
 ],
 [
  "하청 · 재수임 없음",
  "하도급 · 재위탁 없음"
 ],
 [
  "선택 항목 B 항목 · ",
  "선택 항목 B · "
 ],
 [
  "형평 협의 · 총회",
  "시공사 협의 · 총회"
 ],
 [
  "박람회 참가비가 아니라 <em>단지로 돌아가는 혜택</em>",
  "공구가에 얹는 돈이 아니라 <em>단지로 돌아가는 혜택</em>"
 ],
 [
  "도어락",
  "도어록"
 ],
 [
  "온라인 박람회와 사전 서비스로 전 세대를 커버합니다.",
  "온라인 박람회와 사전 서비스로 박람회에 못 오는 세대까지 챙깁니다."
 ],
 [
  "패널티",
  "페널티"
 ],
 [
  "전시 · 리퍼, 한정 수량 행사가는 제외(규정 제8조)",
  "전시 · 리퍼, 특판 · 한정 수량 행사 등은 제외(규정 제8조)"
 ]
]


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
                   # 10-24 화면 점검: 간지 슬로건이 설치 약속으로 읽히지 않게
                   ("<h2>경관조명은 <em>우리가 책임</em>집니다.</h2>", "<h2>경관조명은<br><em>설계부터 시공까지</em>.</h2>"),
                   ("설계 → 생산 → 직접시공, 한 회사가 끝까지 책임집니다.", "설계 → 생산 → 직접시공을 한 회사가 맡고, 설치 여부 · 비용은 입예협 · 관리주체가 정합니다."),
                   # 10-24 독립 검토: 이관 비용은 무상 A/S 기간 안 · 하자 판정 아님 · 실적 기준 통일 · 체험 서비스 = 선택 항목 A
                   ("업체 미응답 · 도산 건은 본사가 이관하고 비용 부담", "업체 도산 건은 본사가 이관(무상 A/S 기간 안 비용 부담) · 미응답 건은 선보상 후 업체 정산"),
                   ("A/S 비용<br>주관사 전액 부담", "무상 A/S 기간 안<br>이관 비용 주관사 부담"),
                   ("발견된 하자는 원인을 진단하고 보수 방안을 함께 제시합니다.", "발견된 하자는 원인 추정과 보수 참고 의견을 드립니다(하자 판정 아님 · 시공사 협의 자료)."),
                   ("2023년 이후 1,000세대 이상 12곳(입주 예정 포함).", "2023년 이후 1,000세대 이상 주관 10곳 + 입주 예정 2곳."),
                   ("불이행 업체는 주관사 콜센터 접수 → <em>즉시 패널티.</em>", f"계약금은 {D.DEPOSIT_MAX}%까지, 기한 안 취소는 <em>전액 환불</em> - 업체가 미루면 주관사가 사실 확인 뒤 먼저 보상합니다."),
                   ("샘플하우스를 운영합니다.", "샘플하우스를 운영합니다(협의회와 협의 후)."),
                   ("사이즈 고민을 줄입니다.</div>", "사이즈 고민을 줄입니다(협의회와 협의 후).</div>")]:  # 본부장 10-24: '기본 지원 · 주관사 부담' 류 표시 안 함
        doc = doc.replace(_a, _b)
    # 10-24 3차 독립 검수(40건 중 즉시 반영분) — 공용 틀 문구 치환 · 없으면 건너뜀(제안서/요약 공용) · 가운뎃점 띄어쓰기는 아래 body 단계에서 \xa0 · \u2060로 바뀌므로 여기서는 보통 공백
    for _a, _b in FIX3:
        doc = doc.replace(_a, _b)
    doc = doc.replace("<span>주식회사 엣지컴퍼니 · 대표이사 고진식</span>", "<span>주식회사 엣지컴퍼니</span>")
    doc = re.sub(r'(<div class="tt">VR 촬영 · 3D 홈스타일링</div><div class="dd">[^<]*?)\.(</div>)', r"\1(협의회와 협의 후).\2", doc, count=1)
    # 본부장 10-15 밤: 조직 구성 쪽 KEY POINT — '박람회 현장 운영 인력 약 21명 …'은 줄을 바꿔 다음 문단으로(문구 그대로)
    assert doc.count("<small>박람회 현장 운영 인력 약 21명") == (0 if "요약제안서" in path else 1), "조직 구성 쪽 KEY POINT 소문구를 찾지 못함"
    doc = doc.replace("<small>박람회 현장 운영 인력 약 21명", '<small class="kpbr">박람회 현장 운영 인력 약 21명')
    doc = doc.replace("</style>", ".kp small.kpbr{display:block;margin-left:0;margin-top:3px}</style>", 1)
    doc = doc.replace("지역업체", "인근 지역업체").replace("인근 인근", "인근")  # 본부장님 지시: '인근 지역업체'
    # 엘리프 제5조 ① '모호한 표현은 불가능한 것으로 간주' → '(안)'을 걷어내고 결정 주체를 적는다(북수원 제6조 · 판교 6항 2 선례)
    for _a, _b in [("박람회 시기(안)", "박람회 시기(예정)"),
                   ("‘(안)’ = 참여업체 확정 후 입예협 승인", "업체 제공 항목 = 참여업체 확정 후 협의회 승인"),
                   ("‘(안)’ 항목은 참여업체 확정 후 입예협 승인으로 협약서에 반영", "업체 제공 항목은 참여업체 확정 후 협의회 승인으로 협약서에 반영"),
                   ("‘(안)’ · (협의) 항목은 입예협 승인으로 협약서에 반영", "(협의) 항목은 협의회 승인으로 협약서에 반영"),
                   ("운영 기준(안)", "운영 기준 예시")]:
        doc = doc.replace(_a, _b)
    doc = re.sub(r"(\d{4}\.\d\d ~ \d{4}\.\d\d) \(안\)", r"\1 (예정)", doc)  # 앞으로 주관할 단지 박람회 시기
    # 업성: '(안)'을 지우지 않는다 — 세대 혜택 '15만원 상당(안)' · '운영계획(안)'은 협상 · 공증 · 협의회 결정 전이라는 뜻(엘리프 제5조 같은 '모호 표현 불가' 조항 없음)
    print(f"[(안) 유지] {doc.count('(안)')}곳")
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
    _ok = ("사송 LH 신혼희망타운 2차", "LH 신혼희망타운 2차", "기장 신혼희망타운")
    _ok += ("두산위브더제니스 센트럴사하", "두산위브더제니스 오션시티")   # 주관 실적 단지 이름(NICE 연혁)만 허용 — 청주 잔재 '두산'은 아래에서 막음
    for _o in _ok:
        _txt = _txt.replace(_o, "")
    _txt = _txt.replace("2028.08.11", "").replace("주례 롯데캐슬 골드스마트", "")  # ISO 유효기간 · 옛 수임 단지 사진 캡션만 허용
    # 업성(11-01): 신분평 · 청주 · 군포 · 엘리프 · 고양 잔재 · 다른 단지 · 공개 문서 금지어(분양가 · 청약 · 계약률 · 미분양 · 무순위 · 본전) · 2단지 · 옛 이름(업성저수지)
    #   · 경쟁사 · 법무법인 · 카페 숫자 · 과장 표현 · 지사 '직영' · '최대 10억' · 세대 혜택 총액('억 … 만원 상당') · '발전지원(금)'('발전기금'은 공고 용어라 허용)
    left = re.findall(r".{0,14}(?:엘리프|한신|계룡|금곡|당수동|호매실|C3|D3|1,149|elifhanshin|블록별|별지|협약 범위|제4조 ⑤|고양|창릉|S-5|S5|이수건설|759|1억 1,385|파주|shin192004|덕양|KINTEX|킨텍스|오산|세교|아테라|금호|벌음|433|segyoartera|나리벡|의정부|롯데|671|1억 65만|양주|금오동|donjigi|경기북부|동북권|포켓정원|"
                      r"별첨 ?1 ?·|별첨 9\)|입찰자격 \d\)|2029년 5 ~ 6월|분당|퍼스트빌리지|성남|낙생|933|1,400|지웰|덕계|탕정|센터파크|철산|광명|조합 입예협|군포|대야미|신혼희망타운|행복주택|공공분양|55㎡|1,511|1,003|1억 5,045|deyami|의왕|수원메쎄|2029\.08|2029년 8월|미분양관리|본전|임예협|북수원|상주자이르네|상주 자이르네|상주시|경산|판교|"
                      r"신분평|더웨이시티|서원구|장성동|1,448|655|793|민간임대 59|일반분양 6|thewaycity|평가표|평가 항목|청주|직지대로|오스코|레이크시티 2단지|448세대|업성저수지|부성역|공감을더하다|하이홈|872명|59\.7|"
                      r"가산점|단지발전|입예협 지정|커뮤니티 집기|bd_|os_|화재 ·|배상책임보험 개최|"
                      r"미분양|미달|청약|계약률|분양률|분양가|분양중|선착순|무순위|경쟁률|예비자|예비 입주|고압선|지중화|오염|토양|특혜|최초|전국\s?최저가|100%|200%|유일|10\s*억|갈음|직영 지사|전담 배치|12명 전담|현장 사무소|셔틀|태성|995|등기 완료|"
                      r"금·토·일|금 · 토 · 일|코엑스|COEX|씨티|업체당|표본 세대|"
                      r"두산|센트럴파크|흥덕|신봉|운천|1,618|705|조합원|조합 ·|· 조합|재건축|서식 ?1|서식 ?2|kmg07m|입찰 자격 [①-⑨]|제출 서류 [①-⑪]|제출 [①-⑪]|유의 [①-⑧]|유의사항 [①-⑧]|자격 [①-⑨]|"
                      r"지원금|발전지원|완판|1순위|카페 회원|510명|개교|학교 공백|\d억 [\d,]+만원 상당|억원 상당).{0,10}", _txt)
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
    import eo  # noqa: E402  (업성: 공고 5항 가 ~ 자 순서 + 부록으로 장 재배치)
    eo.apply(globals())
    emit(list(B.PAGES), out, f"엣지컴퍼니 {D.SITE['name']} 공동구매 주관사 제안서")
    print(f"업성 공동구매 주관사 제안서 {len(B.PAGES)}쪽 → {out}")
    # 본부장 10-17: 요약제안서 — 고양 공고 제출서류에 없지만 만든다(제출서류 17 · 선택 자료). 숫자 · 문구는 위 제안서와 같은 D · ST 값(summary_el.py)
    if "--no-summary" not in sys.argv and not COMPACT and not FULL:
        import summary_el  # noqa: E402
        summary_el.emit_summary(globals())


if __name__ == "__main__":
    build()
