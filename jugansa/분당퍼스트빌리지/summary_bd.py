# -*- coding: utf-8 -*-
"""e편한세상 분당 퍼스트빌리지 — 14 요약제안서(공고 7항 14 '기타 입예협이 필요하다고 인정하는 자료', 선택 제출).

build_bd.py build() 가 제안서(02)를 만든 뒤 emit_summary(globals()) 로 부른다(--no-summary 면 생략).
대상: 정회원 온라인 투표(50점) - 입주민이 한눈에 보는 혜택 · 가격 투명성 · 환불 · A/S · 박람회 · 협의회 지원 · 실적 · 공고 대응.
원칙
- 숫자 · 문구는 제안서와 같은 값(D · ST · ONE_L · CHECK5 · SUPPORT · MUST9 · _C7 등)을 그대로 불러 쓴다 - 여기서 새 숫자를 만들지 않는다.
- 제안서 쪽 번호는 방금 만든 제안서의 PGNO(대응표와 같은 계산)로 적는다 → 압축본(--compact)으로 만들면 압축본 쪽 번호.
- 노란 칸(TODO) 없음 · 확정 안 된 혜택은 '(안)' · 과거 이행보증 가입 실적 표현 없음(보증은 협약 시 제출 약속).
- 표지 = bd_cover(조감도) · 사진 = bd_garden_night(연출 이미지) · 마지막 = 연락처.
쪽수: 표지 + 본문 9 + 연락처 = 11쪽(8 ~ 12쪽 범위, 빌드에서 assert).
"""
import os
import re
import sys

NAME14 = "엣지컴퍼니_분당퍼스트빌리지_14_요약제안서"

CSS = r"""
.sx{flex:1;min-height:0;display:grid;gap:14px}
.sx .col{display:flex;flex-direction:column;gap:14px;min-height:0;min-width:0}
.sx .bx{border:1px solid var(--line);border-radius:14px;padding:13px 18px;background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.012));
  display:flex;flex-direction:column;min-height:0;min-width:0}
.sx .bx.hl{border-color:rgba(235,203,143,.6);background:linear-gradient(180deg,rgba(235,203,143,.13),rgba(235,203,143,.02))}
.sx .bx.fl{flex:1}
.sx h3{font-size:16.5px;font-weight:800;margin:0 0 9px;display:flex;align-items:baseline;gap:10px;color:var(--ink)}
.sx h3 i{font-style:normal;font-size:11px;letter-spacing:.2em;color:var(--gold2);font-weight:700;white-space:nowrap}
.sx h3 small{margin-left:auto;font-size:11.5px;font-weight:500;color:var(--mute)}
.sx strong{color:var(--ink);font-weight:800}
.sx .nt{font-size:12.5px;color:var(--mute);line-height:1.45}
/* 2 - 한눈에 */
.sx .fact{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid rgba(200,168,106,.5);border-radius:12px;background:rgba(235,203,143,.05)}
.sx .fact>div{padding:9px 16px;border-left:1px solid rgba(200,168,106,.25)}
.sx .fact>div:first-child{border-left:0}
.sx .fact b{display:block;font-size:24px;font-weight:800;color:var(--gold);line-height:1.1;white-space:nowrap}
.sx .fact b small{font-size:13px;margin-left:2px}
.sx .fact span{display:block;font-size:12.5px;color:var(--sub);line-height:1.35;margin-top:2px}
.sx .phx{position:relative;border-radius:14px;overflow:hidden;border:1px solid rgba(200,168,106,.4);min-height:0}
.sx .phx img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.sx .phx .cp{position:absolute;left:0;right:0;bottom:0;padding:26px 16px 11px;background:linear-gradient(0deg,rgba(5,12,22,.94),rgba(5,12,22,0))}
.sx .phx .cp b{display:block;font-size:16px;font-weight:800}
.sx .phx .cp span{display:block;font-size:11.5px;color:var(--sub);margin-top:2px}
.sx .ob{display:flex;flex-direction:column;justify-content:space-between;flex:1}
.sx .ob>div{display:grid;grid-template-columns:118px 1fr;gap:14px;align-items:center;padding:3px 0;border-bottom:1px dashed rgba(255,255,255,.12)}
.sx .ob>div:last-child{border-bottom:0}
.sx .ob b{font-size:31px;font-weight:800;color:var(--gold);line-height:1;text-align:right;white-space:nowrap}
.sx .ob b small{font-size:13.5px;margin-left:2px}
.sx .ob strong{display:block;font-size:16px}
.sx .ob span{display:block;font-size:13px;color:var(--sub);line-height:1.4}
/* 3 - 15만원 */
.sx .fx{display:flex;align-items:flex-end;gap:18px;padding-bottom:10px;border-bottom:1px solid rgba(200,168,106,.35)}
.sx .fx .bg{font-size:58px;font-weight:800;color:var(--gold);line-height:.92;white-space:nowrap}
.sx .fx .bg small{font-size:20px;margin-left:3px}
.sx .fx .fm{font-size:15px;line-height:1.5;color:var(--sub)}
.sx .fx .fm em{font-weight:800}
.sx .pk{display:flex;flex-direction:column;gap:9px;flex:1;justify-content:space-around;margin-top:8px}
.sx .pk>div{display:grid;grid-template-columns:34px 1fr;gap:12px;align-items:center}
.sx .pk .L{width:34px;height:34px;border-radius:50%;background:var(--gold);color:#0d1e33;font-weight:800;font-size:16px;display:flex;align-items:center;justify-content:center}
.sx .pk .L.o{background:transparent;border:1.5px solid var(--gold);color:var(--gold);font-size:12px}
.sx .pk strong{font-size:15.5px;display:block}
.sx .pk span{font-size:13px;line-height:1.45;color:var(--sub);display:block}
.sx .sflow{display:flex;flex-direction:column;gap:6px}
.sx .sflow>div{border:1px solid rgba(200,168,106,.45);border-radius:10px;padding:8px 13px;display:grid;grid-template-columns:76px 1fr;gap:10px;align-items:center}
.sx .sflow>div i{font-style:normal;font-size:11px;letter-spacing:.14em;color:var(--gold2);font-weight:700}
.sx .sflow>div b{font-size:14.5px;display:block}
.sx .sflow>div span{font-size:12.5px;color:var(--sub);line-height:1.4;display:block}
.sx .sflow>em{text-align:center;color:var(--gold);font-weight:800;font-size:14px;line-height:1}
.sx .sflow>div.k{background:rgba(235,203,143,.1);border-color:rgba(235,203,143,.7)}
.sx .xl{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:6px}
.sx .xl li{font-size:13px;line-height:1.45;color:var(--sub);padding-left:13px;position:relative}
.sx .xl li:before{content:'·';position:absolute;left:2px;color:var(--gold2);font-weight:800}
.sx .xl li b{color:var(--ink)}
/* 4 - 가격 */
.sx .flw{display:flex;align-items:stretch;gap:6px}
.sx .flw .st{flex:1;border:1px solid var(--line);border-radius:11px;padding:9px 12px;background:rgba(255,255,255,.04)}
.sx .flw .st.hl{border-color:rgba(235,203,143,.75);background:rgba(235,203,143,.13)}
.sx .flw .st i{display:block;font-style:normal;font-size:10.5px;letter-spacing:.18em;color:var(--gold2);font-weight:700}
.sx .flw .st b{display:block;font-size:15.5px;margin-top:3px}
.sx .flw .st span{display:block;font-size:12px;color:var(--sub);line-height:1.4;margin-top:3px}
.sx .flw .ar{align-self:center;color:var(--gold);font-weight:800}
.sx .g4{display:grid;grid-template-columns:1fr 1fr;gap:9px;flex:1}
.sx .g4>div{border:1px solid var(--line);border-radius:10px;padding:9px 13px;display:flex;flex-direction:column;justify-content:center}
.sx .g4 b{font-size:25px;font-weight:800;color:var(--gold);line-height:1.1}
.sx .g4 b small{font-size:13px;margin-left:2px}
.sx .g4 strong{font-size:14.5px;display:block;margin-top:2px}
.sx .g4 span{font-size:12.3px;color:var(--sub);line-height:1.4;display:block;margin-top:2px}
.sx .x10{display:flex;flex-direction:column;gap:10px;flex:1;justify-content:center}
.sx .x10 .lb2{font-size:12.5px;color:var(--sub);margin-bottom:3px}
.sx .x10 .br{height:32px;border-radius:7px;background:rgba(255,255,255,.16);display:flex;align-items:center;padding:0 12px;font-weight:800;font-size:15px}
.sx .x10 .br.g{background:var(--gold);color:#0d1e33}
.sx .x10 .rw2{display:flex;align-items:center;gap:14px;border:1px solid rgba(235,203,143,.6);border-radius:10px;padding:9px 14px;background:rgba(235,203,143,.08)}
.sx .x10 .rw2 b{font-size:34px;font-weight:800;color:var(--gold);line-height:1;white-space:nowrap}
.sx .x10 .rw2 b small{font-size:15px;margin-left:2px}
.sx .x10 .rw2 span{font-size:13px;color:var(--ink);line-height:1.45}
/* 5 - 환불 */
.sx table.rt{width:100%;border-collapse:collapse;flex:1}
.sx table.rt td{font-size:13.5px;line-height:1.42;padding:8px 8px;border-bottom:1px dashed rgba(255,255,255,.13);color:var(--sub);vertical-align:middle}
.sx table.rt tr:last-child td{border-bottom:0}
.sx table.rt td.k{width:122px;white-space:nowrap}
.sx table.rt td.k b{display:inline-block;font-size:13px;color:#0d1e33;background:rgba(235,203,143,.88);border-radius:6px;padding:3px 9px}
.sx table.rt tr.x td.k b{background:transparent;border:1px solid rgba(235,203,143,.65);color:var(--gold)}
.sx table.rt td strong{color:var(--ink)}
.sx .vf{display:flex;flex-direction:column;gap:5px;flex:1;justify-content:space-between}
.sx .vf>div{display:grid;grid-template-columns:84px 1fr;gap:12px;align-items:center;border:1px solid var(--line);border-radius:10px;padding:8px 12px}
.sx .vf>div b{font-size:20px;font-weight:800;color:var(--gold);line-height:1.05;white-space:nowrap}
.sx .vf>div b small{font-size:11.5px;margin-left:1px}
.sx .vf>div strong{display:block;font-size:14.5px}
.sx .vf>div span{display:block;font-size:12.3px;color:var(--sub);line-height:1.4}
.sx .vf>em{text-align:center;color:var(--gold);font-weight:800;font-size:12px;line-height:1}
.sx .vf>div.k{border-color:rgba(235,203,143,.7);background:rgba(235,203,143,.1)}
/* 6 - A/S */
.sx .as5{display:flex;align-items:stretch;gap:6px}
.sx .as5 .st{flex:1;border:1px solid rgba(200,168,106,.5);border-radius:11px;padding:9px 12px;background:rgba(235,203,143,.05)}
.sx .as5 .st b{display:block;font-size:24px;font-weight:800;color:var(--gold);line-height:1.05;white-space:nowrap}
.sx .as5 .st b small{font-size:12.5px;margin-left:2px}
.sx .as5 .st strong{display:block;font-size:14.5px;margin-top:3px}
.sx .as5 .st span{display:block;font-size:12px;color:var(--sub);line-height:1.4;margin-top:2px}
.sx .as5 .st.k{background:var(--gold);border-color:var(--gold)}
.sx .as5 .st.k b,.sx .as5 .st.k strong,.sx .as5 .st.k span{color:#0d1e33}
.sx .as5 .ar{align-self:center;color:var(--gold);font-weight:800}
.sx .sn3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;flex:1;min-height:0}
.sx .sn3 .bx{justify-content:center}
.sx .sn3 .bx b.n{font-size:40px;font-weight:800;color:var(--gold);line-height:1;white-space:nowrap}
.sx .sn3 .bx b.n small{font-size:16px;margin-left:2px}
.sx .sn3 .bx b.n i{font-style:normal;font-size:13px;color:var(--gold2);margin-right:6px}
.sx .sn3 .bx strong{display:block;font-size:17px;margin:8px 0 10px}
.sx .sn3 .xl{gap:9px}
.sx .sn3 .xl li{font-size:13.6px}
.sx .rs2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.sx .rs2>div{border:1px dashed rgba(200,168,106,.55);border-radius:10px;padding:8px 13px}
.sx .rs2 b{font-size:13.5px;color:var(--gold);display:block}
.sx .rs2 span{font-size:12.5px;color:var(--sub);line-height:1.42;display:block;margin-top:2px}
/* 7 - 박람회 */
.sx .t6{display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:1fr 1fr;gap:12px;flex:1;min-height:0}
.sx .t6>div{border:1px solid var(--line);border-top:2px solid var(--gold2);border-radius:13px;padding:12px 16px;background:linear-gradient(180deg,rgba(235,203,143,.08),rgba(255,255,255,.01) 50%);display:flex;flex-direction:column;justify-content:center;min-height:0}
.sx .t6 i{font-style:normal;font-size:11px;letter-spacing:.2em;color:var(--gold2);font-weight:700}
.sx .t6 b{display:block;font-size:18.5px;font-weight:800;margin-top:3px;line-height:1.3}
.sx .t6 span{display:block;font-size:13.5px;color:var(--sub);line-height:1.5;margin-top:5px}
.sx .chips{display:flex;flex-wrap:wrap;gap:7px;align-items:center}
.sx .chips i{font-style:normal;font-size:11px;letter-spacing:.16em;color:var(--gold2);font-weight:700;margin-right:4px}
.sx .chips span{border:1px solid rgba(255,255,255,.2);border-radius:99px;padding:4px 12px;font-size:13px;color:#DCE3EB}
/* 8 - 협의회 */
.sx table.sp{width:100%;border-collapse:collapse;flex:1}
.sx table.sp th{font-size:11.5px;font-weight:700;letter-spacing:.14em;color:var(--gold2);text-align:left;padding:0 10px 7px;border-bottom:1.5px solid rgba(200,168,106,.55)}
.sx table.sp td{font-size:13.3px;line-height:1.42;padding:7.5px 10px;border-bottom:1px dashed rgba(255,255,255,.13);color:var(--sub);vertical-align:middle}
.sx table.sp td.k{color:var(--ink);font-weight:700;white-space:nowrap;width:150px}
.sx table.sp td.g{color:var(--gold);width:29%}
.sx table.sp tr:last-child td{border-bottom:0}
.sx .b3{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.sx .b3>div{border:1px solid rgba(200,168,106,.5);border-radius:11px;padding:9px 14px;background:rgba(235,203,143,.05)}
.sx .b3 b{display:block;font-size:14.5px;color:var(--gold)}
.sx .b3 span{display:block;font-size:12.5px;color:var(--sub);line-height:1.42;margin-top:3px}
/* 9 - 실적 · 사람 */
.sx .hb{display:flex;flex-direction:column;gap:5px;flex:1;justify-content:space-between}
.sx .hb>div{display:grid;grid-template-columns:196px 1fr 52px;gap:10px;align-items:center}
.sx .hb span{font-size:13px;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sx .hb span small{font-size:11px;color:var(--mute);margin-left:5px}
.sx .hb i{display:block;height:15px;border-radius:4px;background:linear-gradient(90deg,rgba(235,203,143,.55),var(--gold))}
.sx .hb b{font-size:13px;font-weight:800;color:var(--gold);text-align:right;font-variant-numeric:tabular-nums}
.sx .ppl{display:flex;flex-direction:column;gap:9px;flex:1;justify-content:space-between}
.sx .ppl>div{border-bottom:1px dashed rgba(255,255,255,.13);padding-bottom:8px}
.sx .ppl>div:last-child{border-bottom:0;padding-bottom:0}
.sx .ppl i{font-style:normal;font-size:11px;letter-spacing:.14em;color:var(--gold2);font-weight:700}
.sx .ppl b{display:block;font-size:17px;font-weight:800;color:var(--gold);margin-top:1px}
.sx .ppl span{display:block;font-size:13px;color:var(--sub);line-height:1.45;margin-top:2px}
.sx .ppl span em{font-weight:800}
.sx .ppl .pro{display:flex;flex-wrap:wrap;gap:5px;margin-top:6px}
.sx .ppl .pro u{text-decoration:none;font-size:12px;font-weight:700;border:1px solid rgba(200,168,106,.55);border-radius:99px;padding:2px 9px;color:var(--gold)}
.sx .rec{display:grid;grid-template-columns:repeat(4,1fr) 1.35fr;border:1px solid rgba(200,168,106,.5);border-radius:12px;background:rgba(235,203,143,.05)}
.sx .rec>div{padding:8px 14px;border-left:1px solid rgba(200,168,106,.25);display:flex;flex-direction:column;justify-content:center}
.sx .rec>div:first-child{border-left:0}
.sx .rec b{font-size:22px;font-weight:800;color:var(--gold);line-height:1.1;white-space:nowrap}
.sx .rec b small{font-size:12px;margin-left:2px}
.sx .rec span{font-size:11.8px;color:var(--sub);line-height:1.35;margin-top:2px}
/* 10 - 공고 대응 */
.sx table.mt{width:100%;border-collapse:collapse;flex:1}
.sx table.mt th{font-size:11.5px;font-weight:700;letter-spacing:.14em;color:var(--gold2);text-align:left;padding:0 9px 7px;border-bottom:1.5px solid rgba(200,168,106,.55)}
.sx table.mt td{font-size:13.6px;line-height:1.3;padding:5px 9px;border-bottom:1px dashed rgba(255,255,255,.13);color:var(--sub);vertical-align:middle}
.sx table.mt td.n{width:30px;color:var(--gold);font-weight:800;font-size:12.5px}
.sx table.mt td.k{color:var(--ink);font-weight:700;width:37%}
.sx table.mt td.pg{white-space:nowrap;color:var(--gold);font-weight:800;font-variant-numeric:tabular-nums;width:20%}
.sx table.mt tr:last-child td{border-bottom:0}
.sx .q4{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.sx .q4>div{border:1px solid rgba(200,168,106,.5);border-radius:11px;padding:9px 14px;background:rgba(235,203,143,.05)}
.sx .q4 i{font-style:normal;font-size:11px;letter-spacing:.14em;color:var(--gold2);font-weight:700}
.sx .q4 b{display:flex;justify-content:space-between;align-items:baseline;gap:8px;font-size:16px;margin-top:2px}
.sx .q4 b em{font-size:13px;font-variant-numeric:tabular-nums;white-space:nowrap}
.sx .q4 span{display:block;font-size:12.5px;color:var(--sub);line-height:1.42;margin-top:3px}
"""


def emit_summary(G):
    B, D, ST, t = G["B"], G["D"], G["ST"], G["t"]
    PGNO = dict(G["PGNO"])  # 방금 만든 제안서의 쪽 번호(대응표와 같은 값)
    won = G["won"]
    hh, fund = D.FUND_HH, D.FUND
    tot = won(hh * fund)
    sec = "요약제안서"
    main_pages = list(B.PAGES)

    def pg(*keys):
        ns = sorted({PGNO[k] for k in keys})
        return "p." + " · ".join(f"{n:02d}" for n in ns)

    def pg_title(title):
        hits = [i for i, (_, kw) in enumerate(main_pages) if kw.get("title") == title]
        assert len(hits) == 1, ("요약제안서 - 제안서 쪽을 찾지 못함", title, hits)
        return hits[0] + 1

    p_rule2 = pg_title(G["T_RULE2"])

    def std(label, title, lead, body, kp):
        return ("std", dict(sec=f"{sec} · {label}", title=title, lead=lead, body=body, kp=kp))

    # ---------------------------------------------------------------- 2 · 한눈에
    one = G["ONE_L"]
    ob = "".join(f'<div><b>{a}<small>{u}</small></b><div><strong>{t(n)}</strong><span>{t(c)}</span></div></div>' for a, u, n, c in one)
    _tp = " · ".join(a for a, _ in ST["types"])
    p2 = f"""<div class="sx" style="grid-template-rows:auto 1fr">
<div class="fact">
<div><b>{ST['households']:,}<small>세대</small></b><span>{ST['sale_label']} {ST['sale']:,} · {ST['rental_label']} {ST['rental']}<br>{ST['buildings']}개동 · {ST['floors']}</span></div>
<div><b>51 ~ 59<small>㎡</small></b><span>전 세대 전용 60㎡ 이하<br>{_tp}</span></div>
<div><b>2029.02</b><span>입주 예정 · 공고부터 약 {ST['months']}개월<br>정당계약 {ST['contract']}</span></div>
<div><b>{ST['developer_short']} · {ST['builder']}</b><span>시행 · 시공<br>{ST['project']}</span></div>
</div>
<div class="sx" style="grid-template-columns:.78fr 1.22fr;min-height:0">
<div class="phx"><img src="assets_ins/bd_garden_night.jpg" alt="" style="object-position:50% 60%">
<div class="cp"><b>{ST['name']}</b><span>조경 산책로 경관 · 연출 이미지(실제와 다를 수 있습니다)</span></div></div>
<div class="bx hl"><h3><i>BENEFIT</i>우리 집이 받는 혜택 · 조건까지<small>제안서 {pg('one')}</small></h3><div class="ob">{ob}</div></div>
</div></div>"""

    # ---------------------------------------------------------------- 3 · 15만원 상당
    p3 = f"""<div class="sx" style="grid-template-columns:1.18fr 1fr">
<div class="bx hl"><h3><i>FUND</i>세대당 {fund}만원 상당 · 혜택 패키지<small>제안서 {pg('fund', 'sep')}</small></h3>
<div class="fx"><div class="bg">{fund}<small>만원 상당</small></div>
<div class="fm">{ST['sale_label']} {hh:,}세대 × 세대당 {fund}만원 상당<br>= <em>총 {tot} 상당</em> (부가세 포함) · <em>현금 지급 없음</em></div></div>
<div class="pk">
<div><b class="L">A</b><div><strong>입주민 특화서비스 - 세대가 직접 받는 혜택</strong><span>백화점 상품권 5만원 또는 10만원(세대 현물 직접 지급) · 사전점검 대행 최대 50% 할인 · 타입별 실측 · 샘플하우스 · 항공 VR · 3D 홈스타일링</span></div></div>
<div><b class="L">B</b><div><strong>협의회 단지발전지원 - 입예협 업무 · 하자 대응</strong><span>공용부 품질 점검 · 도면 분석보고서 · 열화상 드론 · 라돈 측정 · 사전점검 당일 추가 지원 · 온라인 위임장 · 협상 미팅 동석 등</span></div></div>
<div><b class="L">C</b><div><strong>단지지원 컨설팅 - 공용부 · 커뮤니티 가치</strong><span>커뮤니티 · 공용부 조명 · 문주 · 경관조명 컨설팅 · 피트니스 · 키즈 공간 · 전기차 충전 인프라 · 입주 기념 점등식</span></div></div>
<div><b class="L o">지정</b><div><strong>또는 입예협이 필요한 것을 지정</strong><span>공용물품 · 커뮤니티 집기 · 입주 행사 · 단지 개선 용역(조명 시공 · 조경 설계 · 자문) - 같은 금액({tot}) 범위</span></div></div>
</div>
<div class="nt" style="margin-top:8px;border-top:1px dashed rgba(200,168,106,.35);padding-top:7px">주관사가 직접 구매 · 제공하고 사용 내역을 공개합니다 · 항목 · 금액 환산 · 수량은 협약서로 확정 · 공고 업무 범위의 기본 업무는 이와 별도로 수행</div></div>
<div class="col">
<div class="bx"><h3><i>PRICE</i>{fund}만원 상당, 공구가와 따로입니다</h3>
<div class="sflow">
<div><i>업체</i><div><b>참가비 정액제</b><span>업체 참가비는 정액으로 - 공구가와 연동하지 않음</span></div></div><em>↓</em>
<div><i>주관사</i><div><b>운영비 + 발전지원</b><span>박람회 운영비와 세대당 {fund}만원 상당을 주관사 몫에서 부담</span></div></div><em>↓</em>
<div class="k"><i>입예협</i><div><b>혜택 패키지 · 지정 항목</b><span>A · B · C 또는 입예협 지정 · 사용 내역 공개</span></div></div>
</div>
<div class="nt" style="margin-top:8px">공구가는 이 흐름과 따로 - 업체 공개 입찰 경쟁과 시중가 · 온라인 최저가 검수로 정해집니다.</div></div>
<div class="bx fl"><h3><i>NOTE</i>{fund}만원 환산에 넣지 않은 것</h3>
<ul class="xl">
<li><b>박람회 상품권(정회원 30만원) · 정회원 혜택 · 사은품 · 경품 · 현장 할인</b> - 참여업체 제공(안) · 입예협 승인 후 확정</li>
<li><b>{ST['rental_label']} {ST['rental']}세대</b> - 운영기관 · 입예협 협의 후 박람회 참여를 안내합니다</li>
<li><b>기본 지원</b> - 정당계약일 부스 · 사전점검 행사 물품 · 카페 콘텐츠(주관사 부담)</li>
</ul></div>
</div></div>"""

    # ---------------------------------------------------------------- 4 · 가격 투명성
    ck = G["CHECK5"]
    flw = "".join((('<span class="ar">›</span>' if i else "") + f'<div class="st{" hl" if i == 3 else ""}"><i>{a}</i><b>{b}</b><span>{t(c)}</span></div>')
                  for i, (a, b, c) in enumerate(ck))
    p4 = f"""<div class="sx" style="grid-template-rows:auto 1fr">
<div class="flw">{flw}</div>
<div class="sx" style="grid-template-columns:1fr 1fr;min-height:0">
<div class="bx"><h3><i>GUARD</i>공동구매 단가를 지키는 4가지 장치<small>제안서 {pg('guard4')}</small></h3>
<div class="g4">
<div><b>공개</b><strong>단가표 사전 공개</strong><span>박람회 전 품목별 단가 · 할인율 · 모델코드를 입예협이 검수 · 현장 가격 변경 없음</span></div>
<div><b>10<small>배</small></b><strong>최저가 차액 보상</strong><span>동일 브랜드 · 동일 제품이 더 싸면 차액의 10배 보상(온라인 판매 · 시공 품목 제외)</span></div>
<div><b>{D.DEPOSIT_MAX}<small>%</small></b><strong>계약금 상한</strong><span>계약금은 총액의 {D.DEPOSIT_MAX}% 이하, 잔금은 시공 · 설치 후</span></div>
<div><b>동일</b><strong>현금 · 카드 동일가</strong><span>결제 방식에 따른 단가 차이 없음 · 현금영수증 발행</span></div>
</div></div>
<div class="bx"><h3><i>× 10</i>최저가 차액 10배 보상 (예시)<small>제안서 {pg('x10')}</small></h3>
<div class="x10">
<div><div class="lb2">박람회 공동구매가 (예시)</div><div class="br" style="width:100%">33만원</div></div>
<div><div class="lb2">인근({ST['local']}) 매장 동일 제품</div><div class="br g" style="width:84.8%">28만원</div></div>
<div class="rw2"><b>50<small>만원</small></b><span>차액 5만원 × 10배 보상<br>+ 판매가 28만원으로 조정</span></div>
<div class="nt">동일 모델 새 제품 · 인근 오프라인 매장 정상가 · 계약 후 7일 이내 기준. 온라인 · 홈쇼핑, 시공 품목, 카드할인 · 사은품, 전시 · 리퍼, 특판 · 한정 수량 행사가는 비교 대상에서 제외(규정 제8조).</div>
</div></div>
</div></div>"""

    # ---------------------------------------------------------------- 5 · 취소 · 환불
    C7, C15, CU = G["_C7"], G["_C15"], G["_CU"]
    rt = "".join(f'<tr class="{c}"><td class="k"><b>{a}</b></td><td>{b}</td></tr>' for a, b, c in [
        ("시공일 7일 전", C7, ""),
        ("시공일 15일 전", C15, ""),
        ("출고 지시 전", f"맞춤 제작 품목({CU})은 업체와 협의 후 취소 · 브랜드 가전 · 가구(미제작 시)", ""),
        ("당일 취소", "사전 해피콜을 하지 않았으면 <strong>모든 품목</strong> 당일 취소 · 환불(공급사 귀책)", "x"),
        ("업체 귀책", "시공 지연 · 계약과 다른 제품 · 하자 미보수로 해지하면 <strong>기한과 관계없이 전액 환불</strong>", "x"),
        ("기한 지난 뒤", "실제 든 자재 · 제작비만 공제 - 업체가 내역을 서면으로 제시하고 주관사가 검토", "x"),
    ])
    p5 = f"""<div class="sx" style="grid-template-columns:1.45fr 1fr">
<div class="bx"><h3><i>DEADLINE</i>품목별 취소 가능 기한 (시공일 기준)<small>제안서 {pg('rule1')} · {p_rule2:02d}</small></h3>
<table class="rt"><tbody>{rt}</tbody></table>
<div class="nt" style="margin-top:6px">기한 안에 취소하면 납부한 금액 <b style="color:var(--ink)">전액</b>을 환불합니다 · 추가 품목은 성격이 같은 품목의 기한을 따릅니다.</div></div>
<div class="bx hl"><h3><i>REFUND</i>환불은 이렇게 끝까지</h3>
<div class="vf">
<div><b>신청</b><div><strong>기록이 남는 방법으로</strong><span>업체 · 주관 콜센터 · 카페 신문고 · 카카오채널</span></div></div><em>↓</em>
<div class="k"><b>3<small>영업일</small></b><div><strong>안에 환불</strong><span>취소 확정일부터 · 카드는 같은 기한에 승인 취소</span></div></div><em>↓</em>
<div><b>해피콜</b><div><strong>환불 완료 확인</strong><span>주관사가 계약자에게 직접 확인</span></div></div><em>↓</em>
<div><b>선보상</b><div><strong>업체가 미루면</strong><span>콜센터 접수 → 사실 확인 후 주관사가 먼저 보상</span></div></div>
</div>
<div class="nt" style="margin-top:8px">계약금 {D.DEPOSIT_MAX}% 이하 · 잔금은 시공 · 설치 확인 후 · 규정은 모든 공동구매 계약서에 첨부</div></div>
</div>"""

    # ---------------------------------------------------------------- 6 · A/S · 하자
    as5 = "".join((('<span class="ar">›</span>' if i else "") + f'<div class="st{" k" if k else ""}"><b>{a}</b><strong>{b}</strong><span>{c}</span></div>')
                  for i, (a, b, c, k) in enumerate([
                      ("1<small>창구</small>", "주관 콜센터 접수", f"{D.TEL} 평일 09:00 ~ 18:00 · 온라인 365일(카페 신문고 · 카카오채널 · 홈페이지)", False),
                      ("24<small>시간</small>", "안에 1차 회신", "담당 지정 · 업체 미응답 시 주관사가 직접 개입", False),
                      ("48<small>시간</small>", "하자보수 원칙", "주관사 관리 · 감독 · 미해결 시 하자지연 패널티", False),
                      ("선보상", "업체가 미루면", "입주민께 먼저 보상하고 업체와는 나중에 정산", True),
                      ("해피콜", "완료 확인 후 종결", "결과는 입예협 결과보고서에 담습니다", False),
                  ]))
    p6 = f"""<div class="sx" style="grid-template-rows:auto 1fr auto">
<div class="as5">{as5}</div>
<div class="sn3">
<div class="bx hl"><b class="n"><i>최대</i>10<small>억원</small></b><strong>이행보증보험 2년</strong>
<ul class="xl"><li>계약이행 · 하자보수 이행 보증 - 금액은 협약으로 확정</li><li>협약 시 증권 실물을 입예협에 전달</li><li>업체 도산 시 동종업체로 이관 · 비용은 엣지컴퍼니 부담</li></ul></div>
<div class="bx"><b class="n"><i>최대</i>1<small>억원</small></b><strong>하자 예치금 · 선보상 재원</strong>
<ul class="xl"><li>엣지컴퍼니 자산으로 예치 - 참여업체에게 걷은 돈이 아닙니다</li><li>업체 사고 · 도산 시에도 입주민 먼저 보상</li><li>사용 내역 공개</li></ul></div>
<div class="bx"><b class="n">2<small>년 이상</small></b><strong>무상 A/S · 참여업체 하자보증</strong>
<ul class="xl"><li>무상 A/S 최소 2년(업체 · 품목별 상이) · 주관 창구 입주 후 1년</li><li>하자보수 이행각서 · 특약이행각서 전원 징구</li><li>패널티 3단계: 홍보정지 → 총액 10% 배상 → 자격박탈 · 계약 이관</li></ul></div>
</div>
<div class="rs2">
<div><b>건설사 시공 · 공용부 하자</b><span>시공사({ST['builder']}) · 사업주체({ST['developer_short']}) 하자 창구 - 주관사가 접수 대행 · 회신 추적 · 정기 보고</span></div>
<div><b>공동구매 납품 · 시공 하자</b><span>참여업체 + 주관사 책임(서식 2) - 48시간 원칙 · 업체 미응답 시 개입 · 선보상</span></div>
</div></div>"""

    # ---------------------------------------------------------------- 7 · 입주박람회
    t6 = "".join(f'<div><i>{a}</i><b>{b}</b><span>{c}</span></div>' for a, b, c in [
        ("WHEN", f"{ST['expo']} 금·토·일 (안)", "입주(2029.02) 2 ~ 3개월 전 3일간 - 사전점검 일정에 맞춰 입예협과 확정합니다."),
        ("WHERE", "행사장 후보 3곳", "① " + ST["venues"][0] + " ② " + ST["venues"][1] + " ③ " + ST["venues"][2] + " - 입예협과 답사한 뒤 확정합니다."),
        ("FAMILY", "놀이방 · 수유실 · 유모차", "영유아 가족을 위해 어린이 놀이방 · 수유실 · 유모차 대여와 안내데스크 · 카페테리아를 둡니다."),
        ("PRICE", "사전 공개 단가 그대로", "박람회장 가격 = 입예협이 검수한 사전 공개 단가 - 결제 방식과 관계없이 같습니다."),
        ("ONLINE", "온라인 박람회 · 라이브", "단지 입주민만 들어오는 폐쇄몰 · 박람회와 같은 공동구매가 - 못 오셔도 같은 조건입니다."),
        ("SAFETY", "배상책임보험 · 안전계획", "개최 전 보험 가입 · 미아 방지 · 대피로 · 부스 전기 점검 · 혼잡 시 입장 조절 · 보안 · 구급 · 119 연계."),
    ])
    p7 = f"""<div class="sx" style="grid-template-rows:1fr auto auto">
<div class="t6">{t6}</div>
<div class="chips"><i>편의시설</i><span>에어바운스</span><span>영화 상영회</span><span>입예협 부스</span><span>카페테리아</span><span>수유실</span><span>휴게실</span><span>유모차 대여</span><span>안마의자 체험</span></div>
<div class="chips"><i>미리 보기</i><span>타입별 실측 사이즈</span><span>샘플하우스</span><span>항공 VR 촬영</span><span>3D 홈스타일링</span><span>카페 · 공지채널 콘텐츠(게시 전 입예협 승인)</span></div>
</div>"""

    # ---------------------------------------------------------------- 8 · 협의회 지원
    sp = "".join(f'<tr><td class="k">{a}</td><td>{t(b)}</td><td class="g">{t(c)}</td></tr>' for a, b, c in G["SUPPORT"])
    p8 = f"""<div class="sx" style="grid-template-rows:1fr auto">
<div class="bx"><h3><i>SUPPORT</i>시기별 협의회 지원<small>제안서 {pg('support', 'booth', 'req')}</small></h3>
<table class="sp"><thead><tr><th>시기</th><th>기본 지원 · 공고 5항 (주관사 부담)</th><th>선택 지원 · 패키지 B (입예협 선택)</th></tr></thead><tbody>{sp}</tbody></table></div>
<div class="b3">
<div><b>정당계약일 부스 ({ST['contract']})</b><span>입예협 요청 시 안내 부스 · 도우미 · 대기 편의 - 영업 · 사전 예약 없음 · 비용 주관사 부담</span></div>
<div><b>건의 관리표</b><span>접수 → 기술 검토 → 시공사 · 기관 협의 → 반영 / 보류 사유 → 공유 · ‘협의 완료’와 ‘설치 완료’를 나눠 보고</span></div>
<div><b>보고 · 개인정보</b><span>정례회의마다 진행 보고 · 박람회 결과보고서 · 입주 후 1년 최종 보고 - 입주민 정보는 행사 운영에만</span></div>
</div></div>"""

    # ---------------------------------------------------------------- 9 · 실적 · 사람
    recs = list(D.RECORDS)
    mx = max(r[3] for r in recs)
    # 단지 약칭은 제안서 '대단지 운영 경험' 쪽(vis.py)과 같게
    SHORT = {"부산사상 중흥S-클래스 그랜드센트럴": "사상 중흥S클래스", "e편한세상 송도 더퍼스트비치": "송도 더퍼스트비치",
             "두산위브더제니스 센트럴사하": "센트럴사하", "양정자이더샵SK VIEW 1·2단지": "양정자이 1·2단지",
             "춘천 학곡지구 중해마루힐 포레스트": "춘천 중해마루힐", "에코델타 대성베르힐": "대성베르힐",
             "두산위브더제니스 오션시티": "오션시티", "창원 센트럴 아이파크": "창원 센트럴 아이파크"}
    hb = "".join(f'<div><span>{SHORT.get(nm, nm)}<small>{d}</small></span><i style="width:{100 * n / mx:.1f}%"></i><b>{n:,}</b></div>' for d, nm, _, n in recs)
    rec_n, rec_hh = G["_rec_n"], G["_rec_hh"]
    stf = " · ".join(f"{n} {c}" for n, c, _ in D.STAFF)
    pro = "".join(f"<u>{f} {c}</u>" for f, c in G["PRO5"])
    p9 = f"""<div class="sx" style="grid-template-rows:1fr auto">
<div class="sx" style="grid-template-columns:1.15fr 1fr;min-height:0">
<div class="bx"><h3><i>RECORD</i>1,000세대 이상 주관 {rec_n}개 단지 · {rec_hh:,}세대<small>제안서 {pg('big')}</small></h3>
<div class="hb">{hb}</div><div class="nt" style="margin-top:6px">날짜 = 입주 연월(제출서류 14 ⑤ 실적 확약서의 날짜는 주관 시기)</div></div>
<div class="bx"><h3><i>PEOPLE</i>분당 퍼스트빌리지를 맡을 사람<small>제안서 {pg('people', 'org')}</small></h3>
<div class="ppl">
<div><i>대표이사</i><b>고진식</b><span>협약 최종 책임 · PT · 질의응답 참석(공고 6항) · 1,000세대 이상 주관 {rec_n}개 단지 총괄</span></div>
<div><i>주관사업 총괄 본부장 · 전담 총괄</i><b>총괄 본부장</b><span><em>입주예정자협의회 회장 3년 역임</em> - 입주민 입장에서 협의회 운영을 직접 겪어 봤습니다 · 정례회의 · 박람회 · 사전점검 현장 참석</span></div>
<div><i>핵심 운영인력</i><b>임직원 {G['_lead_n']}명</b><span>대표 · 본부장 + {stf}명 - 이 중 단지 전담 PM 1명 지정(성명 · 연락처는 협약 시 제출)</span>
<div class="pro">{pro}</div></div>
</div></div>
</div>
<div class="rec">
<div><b>67<small>개 단지</small></b><span>누적 주관 · 수임<br>(전신 실적 · 입주 예정 포함)</span></div>
<div><b>56,361<small>세대</small></b><span>누적 주관 · 수임 세대</span></div>
<div><b>4,470<small>세대</small></b><span>단일 단지 최대<br>레이카운티</span></div>
<div><b>2<small>억원</small></b><span>자본금 · NICE BB-<br>현금흐름 A</span></div>
<div><b>ISO 3종</b><span>9001 · 14001 · 45001<br>{D.ELEC_LICENSE}</span></div>
</div></div>"""

    # ---------------------------------------------------------------- 10 · 공고 대응
    mt = "".join(f'<tr><td class="n">{i:02d}</td><td class="k">{t(a)}</td><td>{t(b)}</td><td class="pg">{pg(*ks)}</td></tr>'
                 for i, (a, b, ks) in enumerate(G["MUST9"], 1))
    p10 = f"""<div class="sx" style="grid-template-rows:1fr auto">
<div class="bx"><h3><i>공고 8항</i>제안서 필수 포함 9항목 → 제안서 쪽<small>쪽 번호 = 제안서 우측 상단 번호</small></h3>
<table class="mt"><thead><tr><th>NO</th><th>필수 포함 항목</th><th>엣지컴퍼니 제안 핵심</th><th>제안서 쪽</th></tr></thead><tbody>{mt}</tbody></table></div>
<div class="q4">
<div><i>공고 4항</i><b>입찰 참가자격 10개<em>{pg('qual')}</em></b><span>자본금 2억 · 업종 ‘전시, 박람회 및 행사 대행업’ · 체납 없음 · 보증증권 발행 가능(협약 시 증권 제출)</span></div>
<div><i>공고 5항</i><b>주요 업무 범위 11개<em>{pg('scope')}</em></b><span>박람회 운영 · 품목 · 업체 · 가격 검수 · 일정 · A/S · 행사 지원 · 수요조사 · 정당계약일 부스까지 모두 수행</span></div>
<div><i>공고 9항</i><b>참가 제한 · 무효 10개<em>{pg('ban')}</em></b><span>모두 해당 없음 - 대표자 · 배우자 · 직계존비속 당첨자 아님(대표 확인)</span></div>
<div><i>공고 6 · 10항</i><b>유의사항 · 서식 1 ~ 5<em>{pg('note')}</em></b><span>제출 조건 그대로 PT · 협약 - 추가 혜택을 얹지 않음 · 확정 전 혜택은 ‘(안)’ · 담합 · 재위탁 없음</span></div>
</div></div>"""

    pages = [
        ("cover", {}),
        std("한눈에", "정회원 투표 전에, [[한눈에]] 보시도록",
            f"{ST['name']} {ST['households']:,}세대 - 우리 집이 받는 혜택과 조건을 한 장에 모았습니다.", p2,
            ("혜택은 [[조건까지]], 가격은 [[같은 조건 총액]]으로 보여 드립니다.", "‘(안)’ = 참여업체 확정 후 입예협 승인으로 확정(공고 10항 2)")),
        std("발전지원", f"세대당 {fund}만원 상당, [[혜택 패키지]]로 드립니다",
            "현금으로 드리지 않고, 입예협이 고른 항목을 주관사가 직접 구매 · 제공합니다(전기 · 조명은 직접 시공).", p3,
            (f"{ST['sale_label']} {hh:,}세대 × {fund}만원 상당 = [[{tot} 상당]]", "현금 아님 · 부가세 포함 · 사용 내역 공개 · 협약서로 확정")),
        std("가격 투명성", "가격은 [[박람회 전에]] 검수하고, [[계약 후에도]] 지킵니다",
            "공고 8항 5 · 8 - 시중가 · 온라인 최저가와 같은 조건 총액으로 비교하고, 입예협 검수를 거친 단가만 공개합니다.", p4,
            ("검수는 [[박람회 전]], 보상은 [[계약 후]] - 두 번 확인합니다.", f"공식 유상옵션과 겹치는 품목은 수요조사로 확인 후 남은 수요만 모집 · 제안서 {pg('check', 'opt')}")),
        std("취소 · 환불", "취소는 [[기한 안이면 전액]], 환불은 [[3영업일]] 안에",
            "공고 4항 9 · 8항 5 - 계약 취소 · 환불 규정(제1 ~ 10조 · 별표)을 모든 공동구매 계약서에 첨부합니다.", p5,
            ("기한 안 취소는 [[전액 환불]], 업체 귀책이면 [[기한과 관계없이]] 전액 환불합니다.", "제출서류 8 방안서와 같은 기준")),
        std("A/S · 하자", "입주민은 [[한 창구]]로, 처리는 [[기한으로]] 약속합니다",
            "공고 8항 6 · 9 - 입주민은 업체를 쫓아다니지 않고, 주관사 한 곳에 연락하시면 됩니다.", p6,
            ("접수 → 24시간 회신 → 48시간 처리 → [[선보상]] → 해피콜까지 주관사가 따라갑니다.", f"제안서 {pg('safe3', 'pm', 'call', 'deposit', 'defect')}")),
        std("입주박람회", "신혼 가족이 함께 [[확인하고 비교하는]] 3일",
            "계약을 재촉하는 자리가 아니라, 아이와 함께 와서 쉬고 비교하고 상담하는 박람회로 만듭니다.", p7,
            ("박람회장 가격 = 사전 공개 단가 - [[결제 방식과 관계없이]] 같습니다.", f"일정 · 장소 · 배치는 입예협과 확정 · 제안서 {pg('expo', 'venue', 'floor', 'comfort')}")),
        std("협의회 지원", "협의회 지원, [[시기별로]] 약속합니다",
            "공고 8항 7 - 기본 지원은 주관사 비용으로 하고, 15만원 상당 패키지 B는 입예협이 골라 더합니다.", p8,
            ("기본 지원은 [[15만원과 별도]]로 합니다 - 패키지는 입예협이 더 고르는 몫입니다.", "일정은 입예협 정례회의에서 확정")),
        std("실적 · 사람", "실적은 [[숫자로]], 운영은 [[사람으로]] 보여 드립니다",
            "공고 8항 1 · 2 - NICE 연혁 · 입예협 카페 공지 · BEXCO 행사일정으로 확인되는 주관 실적과 이 단지를 맡을 사람입니다.", p9,
            ("대단지 박람회는 규모가 아니라 [[운영 시스템]]으로 치릅니다.", "실적 증빙은 제출서류(NICE 보고서 · 실적 확약서) · 명단은 협약 시 제출")),
        std("공고 대응", "공고가 요구한 것, [[제안서 쪽 번호]]로 확인하세요",
            "공고 8항 필수 9항목과 4 · 5 · 6 · 9 · 10항 대응을 한 장으로 정리했습니다 - 자세한 내용은 제안서 해당 쪽에 있습니다.", p10,
            ("제안서에 쓴 것은 전부 [[협약서와 증빙]]으로 남깁니다.", "상세는 입주박람회 주관사 제안서(제출서류 2)와 제출서류")),
        ("contact", {}),
    ]
    assert 8 <= len(pages) <= 12, len(pages)

    # 표지: 제안서 표지(bd_cover) 그대로 - 제목 · 띠만 요약제안서로
    cover0 = B.p_cover

    def cover_sum():
        s = cover0()
        s = G["sub"](s, "<em>입주박람회 주관사 제안서</em>", "<em>입주박람회 주관사 요약제안서</em>")
        s = G["sub"](s, f'<span class="pill">{G["COVER"]["pill"]}</span>', '<span class="pill">요약제안서 · 공고 7항 14 기타 자료</span>')
        s = G["sub"](s, f'<div class="tag2">{G["COVER"]["tag"]}</div>',
                     '<div class="tag2">정회원 투표 전에 한눈에 보시도록 -<br>혜택 · 가격 · 환불 · A/S · 실적을 9쪽에 담았습니다.</div>')
        return G["sub"](s, "<span>입주박람회 주관사 제안서</span><span>2026.10</span>", "<span>입주박람회 주관사 요약제안서</span><span>2026.10</span>")

    out = os.path.join(G["HERE"], NAME14 + ".html")
    keep_pages, keep_css = list(B.PAGES), B.CSS
    B.p_cover = cover_sum
    B.CSS += CSS + ".cv4 h1.cvx{font-size:44px}"
    try:
        B.PAGES[:] = pages
        B.OUT_HTML, B.OUT_PDF = out, out[:-5] + ".pdf"
        B.build_html()
        B.PAGES[:] = keep_pages
        G["finish"](out, f"엣지컴퍼니 {D.SITE['name']} 요약제안서")
        doc = open(out, encoding="utf-8").read()
        assert 'class="todo"' not in doc, "요약제안서에는 노란 칸이 없어야 합니다"
        assert not re.search(r"현장 직접 주관|더퍼스트비치\(", doc), "본부장 개인 현장 문구"
        if "--no-pdf" not in sys.argv:
            B.build_pdf()
    finally:
        B.p_cover = cover0
        B.CSS = keep_css
        B.PAGES[:] = keep_pages
    print(f"요약제안서 {len(pages)}쪽 → {out}")
