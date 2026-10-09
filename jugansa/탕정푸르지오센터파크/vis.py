# -*- coding: utf-8 -*-
"""탕정 푸르지오 센터파크 제안서 — 쪽별 시각화(본부장 10-08: '이미지 넣을 것·이미지화할 것 확인해서 넣어줘').

글자만 있던 장에 금색 선 아이콘 · 도식 · 기존 사진을 더한다. 숫자는 각 장에 이미 있는 값만 쓴다(새 수치 없음).
reorg.apply() 안에서 재배치 전에 apply(...)로 부른다.
"""
import html as _h
import re

ICONS = {
    "building": '<rect x="5" y="3" width="14" height="18" rx="1"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 15h2M13 15h2M10 21v-3h4v3"/>',
    "door": '<path d="M6 21V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v17"/><path d="M3 21h18"/><circle cx="15" cy="12" r="1"/>',
    "crown": '<path d="M3 8l4 4 5-7 5 7 4-4-2 11H5z"/>',
    "coins": '<ellipse cx="9" cy="7" rx="5" ry="2.5"/><path d="M4 7v4c0 1.4 2.2 2.5 5 2.5s5-1.1 5-2.5V7"/><path d="M14 13c2.8 0 5 1.1 5 2.5v3c0 1.4-2.2 2.5-5 2.5s-5-1.1-5-2.5"/>',
    "report": '<path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4"/><path d="M9 14l2 2 4-4"/>',
    "link": '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
    "badge": '<circle cx="12" cy="9" r="6"/><path d="M9 14l-2 7 5-3 5 3-2-7"/><path d="M9.5 9l1.8 1.8L15 7.5"/>',
    "lockdoc": '<path d="M14 3H6v18h6"/><path d="M14 3l4 4v6"/><rect x="14" y="15" width="7" height="6" rx="1"/><path d="M15.5 15v-2a2 2 0 0 1 4 0v2"/>',
    "coin10": '<circle cx="12" cy="12" r="9"/><text x="12" y="15" text-anchor="middle" font-size="7.5" font-weight="800" fill="currentColor" stroke="none">×10</text>',
    "steps": '<path d="M3 20h18"/><rect x="4" y="14" width="4" height="6"/><rect x="10" y="10" width="4" height="10"/><rect x="16" y="5" width="4" height="15"/>',
    "pie": '<circle cx="12" cy="12" r="9"/><path d="M12 12V3a9 9 0 0 1 5.3 1.7z" fill="currentColor" fill-opacity=".35"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "vault": '<rect x="3" y="4" width="18" height="15" rx="2"/><circle cx="12" cy="11.5" r="3.5"/><path d="M12 8v1M12 14v1M8.5 11.5h1M14.5 11.5h1M6 19v2M18 19v2"/>',
    "house_shield": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M12 12l3 1v2.5c0 1.8-1.3 3-3 3.5-1.7-.5-3-1.7-3-3.5V13z"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "idcard": '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="11" r="2"/><path d="M6 16c.6-1.5 1.7-2.2 3-2.2s2.4.7 3 2.2M14 10h4M14 13h3"/>',
    "monitor": '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M10 8v4l3.5-2z"/><path d="M8 20h8M12 16v4"/>',
    "megaphone": '<path d="M3 10v4h4l7 4V6L7 10z"/><path d="M17 9a4 4 0 0 1 0 6"/>',
    "checklist": '<path d="M10 6h10M10 12h10M10 18h10"/><path d="M3.5 6l1.5 1.5L7.5 5M3.5 12l1.5 1.5L7.5 11M3.5 18l1.5 1.5L7.5 17"/>',
    "streetlight": '<path d="M8 21V6a3 3 0 0 1 3-3h4"/><path d="M15 3l3 3h-6z"/><path d="M5 21h6"/><path d="M13.5 9l-1 2M16.5 9l1 2"/>',
    "tape": '<circle cx="9" cy="12" r="6"/><circle cx="9" cy="12" r="2"/><path d="M15 12h6v4h-6"/><path d="M17 16v-2M19 16v-2"/>',
    "phone_live": '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M10.5 9v4l3.5-2z"/><path d="M11 19h2"/>',
    "member": '<circle cx="12" cy="8" r="4"/><path d="M5 21c1-4 4-6 7-6s6 2 7 6"/>',
    "ban": '<circle cx="12" cy="12" r="9"/><path d="M5.6 5.6l12.8 12.8"/>',
    "coin_pct": '<circle cx="12" cy="12" r="9"/><path d="M9 15l6-6"/><circle cx="9.5" cy="9.5" r="1"/><circle cx="14.5" cy="14.5" r="1"/>',
    "nosub": '<path d="M3 12h9"/><path d="M9 9l3 3-3 3"/><path d="M15 8l6 8M21 8l-6 8"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
    "chat": '<path d="M4 5h16v11H9l-5 4z"/>',
    "bell": '<path d="M6 16v-5a6 6 0 0 1 12 0v5l2 2H4z"/><path d="M10 20a2 2 0 0 0 4 0"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/>',
    "headset": '<path d="M5 13v-1a7 7 0 0 1 14 0v1"/><rect x="3.5" y="13" width="4" height="6" rx="1.5"/><rect x="16.5" y="13" width="4" height="6" rx="1.5"/><path d="M18.5 19c0 1.5-2 2.5-5 2.5"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/>',
    "stamp": '<path d="M9 3h6v5l-1 3h4a2 2 0 0 1 2 2v3H4v-3a2 2 0 0 1 2-2h4L9 8z"/><path d="M4 20h16"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.8-3.5 3.4-5.5 6.5-5.5s5.7 2 6.5 5.5"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18 14.8c1.8.7 3.1 2.5 3.5 5.2"/>',
    "truck": '<path d="M3 6h11v10H3zM14 10h4l3 3v3h-7"/><circle cx="7" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/>',
    "ship": '<path d="M3 14h18l-2.6 5H5.6z"/><path d="M6 14v-4h5v4M11 14v-4h5v4M8.5 10V6.5h5V10"/><path d="M2 21.5c1.7 0 1.7-.9 3.3-.9s1.7.9 3.4.9 1.7-.9 3.3-.9 1.7.9 3.4.9 1.7-.9 3.3-.9 1.7.9 3.3.9"/>',
    "factory": '<path d="M3 21V11l5 3v-3l5 3v-3l5 3V4h3v17z"/><path d="M6.5 18h2M11.5 18h2M16.5 18h2"/>',
    "kc": '<circle cx="12" cy="12" r="9"/><text x="12" y="14.8" text-anchor="middle" font-size="8" font-weight="800" fill="currentColor" stroke="none">KC</text>',
    "ladder": '<path d="M6.5 21L10 3M17.5 21L14 3"/><path d="M8.3 15.5h7.4M9.2 11h5.6M9.9 7h4.2"/>',
    "pen": '<path d="M16 3l5 5L9 20H4v-5z"/><path d="M13 6l5 5"/>',
    "folder": '<path d="M3 6h6l2 2h10v11H3z"/>',
    "bug": '<ellipse cx="12" cy="14" rx="5" ry="6"/><circle cx="12" cy="6" r="2"/><path d="M12 8v12M7 14H3M21 14h-4M8 10L5 7M16 10l3-3M8 18l-3 3M16 18l3 3"/>',
    "person": '<circle cx="12" cy="7" r="3.5"/><path d="M5 21c.8-4.2 3.5-6.5 7-6.5s6.2 2.3 7 6.5"/>',
    "truck2": '<path d="M3 6h11v10H3zM14 10h4l3 3v3h-7"/><circle cx="7" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/>',
    "wrench": '<path d="M14.5 6.5a4 4 0 0 0 5 5L21 13l-8 8-3-3 8-8z" transform="rotate(0)"/><path d="M14 7L4 17l3 3 10-10"/>',
}


def ic(name, cls="cic"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def inject(body, names, what="card"):
    """카드/타일 앞머리에 아이콘을 차례로 넣는다(None은 건너뜀)."""
    it = iter(names)

    def rep(m):
        n = next(it, None)
        return m.group(0) + (ic(n) if n else "")
    out, k = re.subn(rf'<div class="{what}(?: hl)?">', rep, body)
    assert k == len(names), (k, len(names))
    return out


CSS = r"""
.cic{display:block;width:34px;height:34px;fill:none;stroke:var(--gold);stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round;margin-bottom:12px;color:var(--gold)}
.card>.cic{width:52px;height:52px;padding:12px;border-radius:14px;background:rgba(235,203,143,.09);border:1px solid rgba(235,203,143,.38);margin-bottom:16px}
.tile .cic{width:28px;height:28px;margin-bottom:6px}
.mbar{display:grid;grid-template-columns:repeat(7,1fr);gap:4px;align-items:end;height:92px;margin-bottom:14px}
.mbar>div{display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%}
.mbar b{font-size:10.5px;color:var(--sub);font-weight:700;margin-bottom:2px}
.mbar i{display:block;width:100%;border-radius:3px 3px 0 0;background:rgba(235,203,143,.45)}
.mbar .p i{background:repeating-linear-gradient(45deg,rgba(235,203,143,.5) 0 3px,rgba(235,203,143,.2) 3px 6px)}
.mbar .g i{background:var(--gold)}.mbar .g b{color:var(--gold)}
.mbar span{font-size:10px;color:var(--mute);margin-top:3px}
.bnr{position:relative;flex:0 0 29%;min-height:0;border-radius:14px;overflow:hidden;border:1px solid rgba(200,168,106,.4)}
.bnr img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 80%}
.bnr:after{content:'';position:absolute;inset:0;background:linear-gradient(0deg,rgba(13,30,51,.85) 0%,rgba(13,30,51,0) 45%)}
.bnr span{position:absolute;z-index:1;right:14px;bottom:10px;font-size:11px;color:rgba(255,255,255,.75)}
.bnr b{position:absolute;z-index:1;left:18px;bottom:10px;font-size:17px;color:var(--gold)}
.sbar{display:flex;height:18px;border-radius:5px;overflow:hidden;margin:6px 0 4px;font-size:10.5px;font-weight:700}
.sbar i{font-style:normal;display:flex;align-items:center;padding-left:6px;white-space:nowrap}
.sbar i:first-child{background:var(--gold);color:#0d1e33}
.sbar i:last-child{background:rgba(255,255,255,.18);color:var(--ink)}
/* 최저가 10배 */
.rw{display:grid;grid-template-columns:1.3fr 96px 1fr;gap:18px;flex:1;min-height:0;align-items:center}
.rw .ch{display:flex;flex-direction:column;gap:34px;padding-right:56px}
.rw .lbl{font-size:16px;color:var(--sub);margin-bottom:8px}
.rw .bar{position:relative;height:62px;border-radius:9px;background:rgba(255,255,255,.14);display:flex;align-items:center;padding-left:18px;font-size:26px;font-weight:800}
.rw .x10{display:flex;flex-direction:column;align-items:center;gap:6px;color:var(--gold)}
.rw .x10 b{font-size:30px;font-weight:800}
.rw .x10 i{display:block;width:100%;height:2px;background:linear-gradient(90deg,rgba(235,203,143,.2),var(--gold));position:relative}
.rw .x10 i:after{content:'';position:absolute;right:-2px;top:-5px;border:6px solid transparent;border-left:9px solid var(--gold)}
.rw .x10 span{font-size:12.5px;color:var(--sub)}
.rw .bar.g{background:linear-gradient(90deg,rgba(235,203,143,.45),rgba(235,203,143,.25))}
.rw .gap{position:absolute;top:-6px;bottom:-6px;border:2px dashed var(--gold);border-radius:6px;
  background:repeating-linear-gradient(45deg,rgba(235,203,143,.25) 0 6px,transparent 6px 12px)}
.rw .gap b{position:absolute;top:-30px;left:50%;transform:translateX(-50%);font-size:15px;color:var(--gold);white-space:nowrap}
.rw .rew{border:2px solid var(--gold2);border-radius:16px;padding:22px 24px;background:linear-gradient(180deg,rgba(235,203,143,.2),rgba(235,203,143,.04));position:relative}
.rw .rew i{font-style:normal;font-size:12px;letter-spacing:.24em;color:var(--gold2);font-weight:700}
.rw .rew .v{font-size:72px;font-weight:800;color:var(--gold);line-height:1.1}
.rw .rew .v small{font-size:24px;margin-left:4px}
.rw .rew p{font-size:15px;color:var(--sub);margin-top:6px}
.rw .rew .chip{display:inline-block;margin-top:10px;border:1px solid rgba(235,203,143,.6);border-radius:99px;padding:4px 12px;font-size:13.5px;color:var(--gold)}
/* 신도시 */
.ct2{display:grid;grid-template-columns:1fr 1fr;gap:20px;flex:1;min-height:0}
.ct2>div{border:1px solid var(--line);border-radius:14px;padding:22px 24px;display:grid;grid-template-columns:132px 1fr;gap:18px;align-items:center;
  background:linear-gradient(180deg,rgba(255,255,255,.07),rgba(255,255,255,.015))}
.ct2 .dn{position:relative;width:132px;height:132px}
.ct2 .dn svg{width:132px;height:132px;transform:rotate(-90deg)}
.ct2 .dn .v{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
.ct2 .dn .v b{font-size:38px;font-weight:800;color:var(--gold);line-height:1}
.ct2 .dn .v b small{font-size:18px}
.ct2 .dn .v span{font-size:12px;color:var(--sub);margin-top:4px}
.ct2 h3{font-size:23px;font-weight:800;margin-bottom:4px}
.ct2 .sb2{font-size:14.5px;color:var(--gold2);margin-bottom:16px}
.ct2 .hb{display:grid;grid-template-columns:128px 1fr 46px;gap:8px;align-items:center;font-size:14px;margin-bottom:13px}
.ct2 .hb .t{height:15px;border-radius:4px;background:rgba(255,255,255,.08)}
.ct2 .hb .t i{display:block;height:100%;border-radius:4px;background:linear-gradient(90deg,var(--gold2),var(--gold))}
.ct2 .hb b{text-align:right;font-variant-numeric:tabular-nums}
/* 대단지 타임라인 막대 */
.tlb{flex:1;min-height:0;display:flex;flex-direction:column}
.tlb .cols{flex:1;min-height:0;display:grid;grid-template-columns:repeat(10,1fr);gap:12px;align-items:end;border-bottom:1.5px solid rgba(200,168,106,.6);padding:0 6px}
.tlb .c{display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%}
.tlb .c b{font-size:15px;font-weight:800;color:var(--ink);margin-bottom:6px;font-variant-numeric:tabular-nums}
.tlb .c i{display:block;width:70%;border-radius:6px 6px 0 0;background:linear-gradient(180deg,rgba(235,203,143,.85),rgba(200,168,106,.35))}
.tlb .c.mx i{background:linear-gradient(180deg,var(--gold),rgba(235,203,143,.5));box-shadow:0 0 14px rgba(235,203,143,.35)}
.tlb .c.mx b{color:var(--gold);font-size:18px}
.tlb .nm{display:grid;grid-template-columns:repeat(10,1fr);gap:12px;padding:8px 6px 0}
.tlb .nm div{text-align:center;font-size:12.5px;line-height:1.3;font-weight:700}
.tlb .nm div small{display:block;font-size:11.5px;color:var(--mute);font-weight:500;margin-top:2px}
/* 카드 사진 */
.cimg{margin:-16px -20px 12px;height:150px;overflow:hidden;border-radius:12px 12px 0 0;border-bottom:2px solid var(--gold2)}
.cimg img{width:100%;height:100%;object-fit:cover}
.cimg.cn img{object-fit:contain;background:#fff}
.icgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:-4px 0 12px;height:142px;align-content:center}
.icgrid div{display:flex;flex-direction:column;align-items:center;gap:4px;font-size:11.5px;color:var(--sub)}
.icgrid .cic{margin:0;width:28px;height:28px}
/* 2단 + 사진 */
.r2{display:grid;grid-template-columns:1.25fr 1fr;gap:22px;flex:1;min-height:0}
.r2 .rows .row{grid-template-columns:40px 30px 190px 1fr !important;align-items:center}
.r2 .rows .row .dd{font-size:14.5px}
.r2 .rows .row .cic{width:26px;height:26px;margin:0}
.r2 .gal{grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr}
/* 17개월 타임라인 */
.tl31{position:relative;height:96px;margin:4px 8px 14px}
.tl31 .ln{position:absolute;left:0;right:60px;top:40px;height:3px;background:linear-gradient(90deg,var(--gold2),var(--gold))}
.tl31 .ext{position:absolute;right:0;width:60px;top:40px;border-top:3px dashed rgba(235,203,143,.6)}
.tl31 .q{position:absolute;top:36px;width:11px;height:11px;margin-left:-5px;border-radius:50%;background:#0d1e33;border:2px solid var(--gold2)}
.tl31 .m{position:absolute;top:0;transform:translateX(-50%);text-align:center;white-space:nowrap}
.tl31 .m b{display:block;font-size:14.5px;color:var(--gold);font-weight:800}
.tl31 .m span{display:block;font-size:12px;color:var(--sub);margin-top:30px}
.tl31 .m:after{content:'';position:absolute;left:50%;top:32px;width:18px;height:18px;margin-left:-9px;border-radius:50%;background:var(--gold);box-shadow:0 0 10px rgba(235,203,143,.6)}
.tl31 .qa{position:absolute;top:64px;left:24%;font-size:12px;color:var(--gold2)}
.tl31 .ex{position:absolute;right:0;top:64px;font-size:12px;color:var(--sub)}
/* 4단계 깔때기 */
.fnw{display:grid;grid-template-columns:200px 1fr;gap:14px;flex:1;min-height:0}
.fnw .pre{position:relative;border:1.5px dashed rgba(235,203,143,.65);border-radius:14px;padding:16px 16px;display:flex;flex-direction:column;background:rgba(235,203,143,.06)}
.fnw .pre .cic{margin-bottom:8px}
.fnw .pre i{font-style:normal;font-size:12px;letter-spacing:.22em;color:var(--gold2);font-weight:700}
.fnw .pre h3{font-size:20px;font-weight:800;margin:4px 0 6px;color:var(--gold)}
.fnw .pre p{font-size:13.5px;color:var(--sub);line-height:1.5}
.fnw .pre em{position:absolute;right:-13px;top:50%;margin-top:-12px;width:24px;height:24px;border-radius:50%;background:#0d1e33;border:1.5px solid var(--gold2);color:var(--gold);font-style:normal;font-weight:800;font-size:16px;line-height:20px;text-align:center;z-index:2}
.fnl{display:grid;grid-template-columns:repeat(4,1fr);gap:0;flex:1;min-height:0}
.fnl .s{position:relative;display:flex;flex-direction:column;padding:16px 30px 16px 24px;clip-path:polygon(0 0,calc(100% - 22px) 0,100% 50%,calc(100% - 22px) 100%,0 100%,22px 50%);
  background:linear-gradient(180deg,rgba(235,203,143,.16),rgba(255,255,255,.03))}
.fnl .s:first-child{clip-path:polygon(0 0,calc(100% - 22px) 0,100% 50%,calc(100% - 22px) 100%,0 100%)}
.fnl .s:nth-child(1){margin:0 -6px 0 0}.fnl .s:nth-child(2){margin:16px -6px 16px 0}.fnl .s:nth-child(3){margin:32px -6px 32px 0}
.fnl .s:nth-child(4){margin:48px 0;background:linear-gradient(180deg,rgba(235,203,143,.36),rgba(235,203,143,.08))}
.fnl .s i{font-style:normal;font-size:12px;letter-spacing:.22em;color:var(--gold2);font-weight:700;padding-left:14px}
.fnl .s h3{font-size:20px;font-weight:800;margin:4px 0 6px;padding-left:14px}
.fnl .s p{font-size:13.5px;color:var(--sub);line-height:1.5;padding-left:14px}
.fnl .s .cic{margin-left:14px;margin-bottom:8px}
.chp{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:12px}
.chp b{font-size:13px;color:var(--gold2);margin-right:4px}
.chp span{font-size:13px;border:1px solid rgba(200,168,106,.55);border-radius:99px;padding:4px 12px;color:var(--gold)}
/* 콜센터 허브 */
.hub{display:grid;grid-template-columns:1.1fr 1fr;gap:22px;flex:1;min-height:0}
.hub .rows .row{grid-template-columns:40px 170px 1fr !important}
.hub .rows .row .dd{font-size:14.5px}
.hubd{position:relative;border:1px solid var(--line);border-radius:14px;background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.01));display:grid;grid-template-columns:1fr 1.15fr 1fr;align-items:center;gap:8px;padding:18px 16px}
.hubd .col{display:flex;flex-direction:column;gap:14px;align-items:center}
.hubd .ch{display:flex;align-items:center;gap:8px;font-size:14.5px;border:1px solid rgba(255,255,255,.18);border-radius:10px;padding:10px 12px;width:100%;background:#0f2237}
.hubd .ch .cic{width:22px;height:22px;margin:0}
.hubd .ctr{position:relative;width:172px;height:172px;margin:0 auto;border-radius:50%;border:2px solid var(--gold2);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;
  background:radial-gradient(circle,#16304f,#0b1a2d);box-shadow:0 0 26px rgba(235,203,143,.25)}
.hubd .ctr .cic{margin:0 0 4px;width:34px;height:34px}
.hubd .ctr b{font-size:18.5px;color:var(--gold)}
.hubd .ctr span{font-size:13.5px;color:var(--sub)}
.hubd .arr{position:absolute;top:50%;height:2px;background:linear-gradient(90deg,rgba(235,203,143,.2),var(--gold2))}
.hubd .bd{display:flex;flex-direction:column;gap:10px;width:100%}
.hubd .bd span{font-size:14px;border:1px solid rgba(235,203,143,.6);border-radius:99px;padding:7px 10px;color:var(--gold);text-align:center;background:rgba(235,203,143,.08)}
.hubd .vd{font-size:14px;color:var(--gold2);text-align:center;margin-top:4px;font-weight:700}
/* 하자보증 체계 */
.wty{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:auto auto;gap:16px;flex:1;min-height:0}
.wty .bx{border:1px solid var(--line);border-radius:14px;padding:14px 18px;background:linear-gradient(180deg,rgba(255,255,255,.07),rgba(255,255,255,.015))}
.wty h4{font-size:15px;color:var(--gold);font-weight:800;margin-bottom:10px;display:flex;align-items:center;gap:8px}
.wty h4 .cic{width:22px;height:22px;margin:0}
.wty .stp{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;align-items:end;height:130px}
.wty .stp div{border-radius:8px 8px 0 0;padding:10px;display:flex;flex-direction:column;justify-content:flex-end;font-size:13.5px;font-weight:700;color:#0d1e33}
.wty .stp div small{display:block;font-size:11px;font-weight:600;opacity:.75}
.wty .stp div:nth-child(1){height:45%;background:rgba(235,203,143,.45)}
.wty .stp div:nth-child(2){height:70%;background:rgba(235,203,143,.7)}
.wty .stp div:nth-child(3){height:100%;background:var(--gold)}
.wty .fl{display:flex;align-items:center;gap:8px}
.wty .fl div{flex:1;text-align:center;border:1px solid rgba(255,255,255,.18);border-radius:10px;padding:10px 6px;font-size:13.5px;background:#0f2237}
.wty .fl div .cic{margin:0 auto 4px;width:24px;height:24px}
.wty .fl em{font-size:18px;color:var(--gold)}
.wty .fl div.g{border-color:var(--gold2);background:rgba(235,203,143,.12)}
.wty p{font-size:14px;color:var(--sub);line-height:1.55}
/* 클레임 표 막대 */
.cbar{display:flex;align-items:center;gap:8px}
.cbar i{display:block;height:8px;border-radius:4px;background:rgba(255,255,255,.25)}
.cbar i.g{background:var(--gold2)}
/* 왜 직영 */
.dvs{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:14px}
.dvs>div{border:1px solid var(--line);border-radius:12px;padding:12px 16px;background:rgba(255,255,255,.03)}
.dvs>div.g{border-color:var(--gold2);background:rgba(235,203,143,.08)}
.dvs h4{font-size:14px;font-weight:800;margin-bottom:8px;color:var(--sub)}
.dvs .g h4{color:var(--gold)}
.dvs .fl{display:flex;align-items:center;gap:6px;font-size:13px}
.dvs .fl span{border:1px solid rgba(255,255,255,.2);border-radius:8px;padding:5px 9px;white-space:nowrap}
.dvs .g .fl span{border-color:rgba(235,203,143,.6);color:var(--gold)}
.dvs .fl em{color:var(--mute);font-style:normal}
.dvs .tg{margin-top:8px;font-size:12.5px;color:var(--mute)}
.dvs .g .tg{color:var(--gold2)}
"""


def apply(B, D, take, sub):
    B.CSS += CSS

    # 숫자로 보는 엣지컴퍼니 — 아이콘 + 누적 스파크라인(5쪽 누적 단지 수 그대로)
    k = take("숫자로 보는 [[엣지컴퍼니]]")[1]
    cum = [(y, nd) for y, _, _, nd, _ in D.cumulative()]
    mx = max(n for _, n in cum)
    spark = ('<div class="mbar">' + "".join(
        f'<div class="{"g" if i == len(cum) - 1 else ""}"><b>{n}</b><i style="height:{100 * n / mx:.0f}%"></i><span>{"~" if i == 0 else ""}{y[2:]}</span></div>'
        for i, (y, n) in enumerate(cum)) + '</div>')
    body = inject(k["body"], ["building", "door", "crown", None])
    k["body"] = body.replace('<div class="card"><div class="lb">GROWTH</div>', '<div class="card">' + spark + '<div class="lb">GROWTH</div>')

    # 아이콘만 더하는 카드 장
    for title, names in [
        ("공인된 [[자격과 신뢰]]", ["coins", "report", "link", "badge"]),
        ("공동구매 단가를 지키는 [[4가지 장치]]", ["lockdoc", "coin10", "steps", "pie"]),
        ("입주민을 지키는 [[3중 안전망]]", ["shield", "clock", "calendar"]),
        ("선보상 재원 · 하자 예치금 [[최대 1억원]]", ["vault", "building", "house_shield"]),
        ("검증된 [[인근 지역업체]] 선정 원칙", ["pin", "report", "nosub"]),
        ("참여업체 [[패널티 3단계]]", ["megaphone", "coin_pct", "ban"]),
        ("입주박람회 [[운영 계획]]", ["calendar", "pin", "shield", "idcard", "monitor", "megaphone"]),
    ]:
        k = take(title)[1]
        k["body"] = inject(k["body"], names, "card" if 'class="card' in k["body"] else "tile")
    k = take("입주박람회 [[운영 계획]]")[1]
    k["body"] = k["body"].replace('class="tiles lg"', 'class="tiles lg opw"', 1)
    B.CSS += ".opw .tile:first-child .nm{font-size:18.5px;letter-spacing:-.02em;white-space:nowrap}"
    k = take("탕정 푸르지오 센터파크 [[특화 제안]]")[1]
    k["body"] = inject(k["body"], ["checklist", "tape", "streetlight", "person", "users", "truck2"], "tile")

    # 탕정 푸르지오 센터파크, 이런 단지입니다 — 야간 경관 배너 + 타입 구성 막대(최초 입주자모집공고 타입별 세대수)
    k = take("탕정 푸르지오 센터파크, [[이런 단지]]입니다")[1]
    hh, tp = D.SITE["households"], dict(D.SITE["types"])
    grp = [("59㎡", tp["59A"] + tp["59B"]), ("84㎡", tp["84A"] + tp["84B"] + tp["84C"]), ("109㎡", tp["109"]), ("136", tp["136PH"])]
    tb = "".join(f'<i style="flex:{n}">{nm} {n:,}</i>' if n > 60 else f'<i style="flex:{max(n, 30)}" class="sm"></i>' for nm, n in grp)
    cards = k["body"].replace(
        f'<div class="big">{hh:,}<small>세대</small></div>',
        f'<div class="big">{hh:,}<small>세대</small></div><div class="sbar t4">{tb}</div>', 1)
    assert cards != k["body"]
    k["body"] = ('<div class="nb"><div class="bnr" style="flex-basis:25%"><img src="assets_ins/tj_aerial_night.jpg" alt="" style="object-position:50% 55%">'
                 f'<b>{D.SITE["official"]} · {hh:,}세대 · {D.SITE["buildings"]}개동</b><span>단지 야간 경관 · 연출 이미지(실제와 다를 수 있습니다)</span></div>'
                 + cards + '</div>')
    B.CSS += (".sbar.t4 i{background:rgba(255,255,255,.14)!important;color:var(--ink)!important;border-right:1px solid #0d1e33;padding-left:5px;font-size:10px}"
              ".sbar.t4 i:nth-child(2){background:var(--gold)!important;color:#0d1e33!important}.sbar.t4 i.sm{padding:0}")

    # 최저가 차액 10배 — 막대 비교
    k = take("[[최저가 차액 10배]] 보상")[1]
    note = re.search(r'<div class="notex">.*?</div>', k["body"]).group(0)
    k["body"] = ('<div class="nb"><div class="rw"><div class="ch">'
                 '<div><div class="lbl">박람회 공동구매가 (예시)</div><div class="bar" style="width:100%">33만원</div></div>'
                 '<div><div class="lbl">인근 매장 동일 제품</div><div class="bar g" style="width:84.8%">28만원'
                 '<span class="gap" style="left:100%;width:17.9%"><b>차액 5만원</b></span></div></div></div>'
                 '<div class="x10"><b>×10</b><i></i><span>차액의 10배</span></div><div class="rew"><i>REWARD</i><div class="v">50<small>만원</small></div><p>차액 5만원 × 10배 보상</p>'
                 '<span class="chip">+ 판매가 28만원으로 조정</span></div></div>' + note + '</div>')

    # 한 단지가 아니라 한 신도시 — 도넛 + 단지별 막대(쪽에 있던 단지·세대수 그대로)
    k = take("한 단지가 아니라 [[한 신도시]]를 맡습니다")[1]
    city = [("양산 사송신도시", 88, "입주 세대 기준 88% 주관",
             [("데시앙 1차", 1712), ("데시앙 3차", 533), ("우미린", 688), ("LH 신혼희망타운 2차", 479), ("제일풍경채", 452)]),
            ("부산 강서 에코델타시티", 93, "입주 세대 기준 93% 진행",
             [("대성베르힐", 1120), ("디에트르 더 퍼스트", 972), ("e편한세상 센터포인트", 953), ("푸르지오 린", 886), ("강서자이", 856)])]
    cmx = max(n for c in city for _, n in c[3])
    blocks = ""
    for nm, pct, cap, cx in city:
        r, cfr = 62, 2 * 3.14159 * 62
        donut = (f'<div class="dn"><svg viewBox="0 0 150 150"><circle cx="75" cy="75" r="{r}" fill="none" stroke="rgba(255,255,255,.12)" stroke-width="14"/>'
                 f'<circle cx="75" cy="75" r="{r}" fill="none" stroke="#EBCB8F" stroke-width="14" stroke-linecap="round" '
                 f'stroke-dasharray="{cfr * pct / 100:.1f} {cfr:.1f}"/></svg><div class="v"><b>{pct}<small>%</small></b><span>입주 단지</span></div></div>')
        bars = "".join(f'<div class="hb"><span>{_h.escape(a)}</span><div class="t"><i style="width:{100 * n / cmx:.1f}%"></i></div><b>{n:,}</b></div>' for a, n in cx)
        blocks += f'<div>{donut}<div><h3>{nm}</h3><div class="sb2">{cap}</div>{bars}</div></div>'
    k["body"] = f'<div class="nb"><div class="ct2">{blocks}</div></div>'

    # 대단지 운영 경험 — 입주 순 막대(세대수 비례)
    k = take("[[대단지]] 운영 경험")[1]
    SHORT = {"부산사상 중흥S-클래스 그랜드센트럴": "사상 중흥S-클래스", "e편한세상 송도 더퍼스트비치": "송도 더퍼스트비치",
             "두산위브더제니스 센트럴사하": "센트럴사하", "양정자이더샵SK VIEW 1·2단지": "양정자이 1·2단지",
             "춘천 학곡지구 중해마루힐 포레스트": "춘천 중해마루힐", "에코델타 대성베르힐": "대성베르힐",
             "두산위브더제니스 오션시티": "오션시티", "창원 센트럴 아이파크": "창원 센트럴 아이파크"}
    recs = sorted(D.RECORDS, key=lambda r: r[0])
    rmx = max(r[3] for r in recs)
    cols = "".join(f'<div class="c{" mx" if n == rmx else ""}"><b>{n:,}</b><i style="height:{max(14, 100 * n / rmx):.1f}%"></i></div>' for _, _, _, n in recs)
    nms = "".join(f'<div>{_h.escape(SHORT.get(nm, nm))}<small>{d} 입주</small></div>' for d, nm, _, _ in recs)
    k["body"] = f'<div class="nb"><div class="tlb"><div class="cols">{cols}</div><div class="nm">{nms}</div></div></div>'

    # 못 오셔도 괜찮습니다 — 목록 + 2×2 사진
    k = take("못 오셔도 [[괜찮습니다]]")[1]
    rows = k["body"]
    for n, name in enumerate(["lockdoc", "phone_live", "tape", "building", "globe"], 1):
        rows = sub(rows, f'<div class="no">{n:02d}</div>', f'<div class="no">{n:02d}</div>{ic(name)}')
    rows = rows.replace("grid-template-columns:46px 268px 1fr", "grid-template-columns:40px 30px 190px 1fr")
    gal = ('<div class="gal">' + "".join(
        f'<figure><img src="assets_ins/{im}.jpg" alt=""><figcaption>{c}<small>{s}</small></figcaption></figure>'
        for im, c, s in [("g12_aerial_u", "항공 VR 촬영", "타 단지 제작 예시"), ("g12_room_a", "3D 홈스타일링", "타 단지 제작 예시"),
                         ("g12_plan_a", "타입별 평면·실측", "타 단지 제작 예시"), ("n01_yt1", "영상 콘텐츠", "타 단지 유튜브 화면")]) + '</div>')
    k["body"] = f'<div class="nb"><div class="r2">{rows}{gal}</div></div>'

    # 입주까지 17개월 — 타임라인 띠
    k = take("입주까지 17개월, [[빈틈없이]] 관리합니다")[1]
    tl = ('<div class="tl31"><div class="ln"></div><div class="ext"></div>'
          + "".join(f'<div class="q" style="left:{x}%"></div>' for x in (14, 24, 34, 44, 54))
          + '<div class="m" style="left:2%"><b>2026.10</b><span>주관사 선정</span></div>'
          + '<div class="m" style="left:66%"><b>2027.12 ~ 2028.01</b><span>입주박람회</span></div>'
          + '<div class="m" style="left:86%"><b>2028.03</b><span>입주</span></div>'
          + '<div class="qa">● 정례회의마다 진행 보고</div><div class="ex">지연 시 일정 재조정</div></div>')
    k["body"] = '<div class="nb">' + tl + k["body"] + '</div>'

    # 4단계 공개 심사 — 깔때기
    k = take("[[4단계]] 공개 심사 프로세스")[1]
    fn = [("STEP 01", "megaphone", "자율경쟁 입찰공고", "공식 카페·협력업체 밴드·홈페이지에 공개 모집. 입찰서류는 주관사·협의회 이메일 동시 접수."),
          ("STEP 02", "report", "1차 서류심사", "사업개시 2년 경과 · 근거리 · 타단지 공구이력 20회 이상 · 국세·지방세 완납 · 사후관리 체계."),
          ("STEP 03", "search", "2차 세부심사", "시공물량 소화 · A/S 대책 · 입주민 평가 확인. 대기업·브랜드·본사직영 우선."),
          ("STEP 04", "stamp", "협의회 최종 컨펌", "후보업체 서류 최종 검토 후 협의회 승인으로 확정.")]
    pre = (f'<div class="pre">{ic("checklist")}<i>사전 단계</i><h3>품목 수요조사</h3>'
           '<p>입주민 설문으로 필요한 품목과 예상 수요를 먼저 조사해 입찰 품목을 정합니다.</p><em>›</em></div>')
    k["body"] = ('<div class="nb"><div class="fnw">' + pre + '<div class="fnl">' + "".join(
        f'<div class="s">{ic(i)}<i>{a}</i><h3>{t}</h3><p>{p}</p></div>' for a, i, t, p in fn) + '</div></div>'
        '<div class="chp"><b>최종 확정 시 징구</b><span>물품공급계약서</span><span>청렴이행서약서</span><span>하자보수이행각서</span></div></div>')

    # 주관 콜센터와 선보상 — 목록 + 허브 도식
    k = take("주관 [[콜센터]]와 선보상")[1]
    rows = k["body"].replace("grid-template-columns:46px 268px 1fr", "grid-template-columns:40px 170px 1fr")
    chs = "".join(f'<div class="ch">{ic(n)}{t}</div>' for n, t in [("phone", "상담 콜센터"), ("bell", "카페 신문고"), ("chat", "카카오채널"), ("globe", "홈페이지")])
    hub = ('<div class="hubd"><div class="col">' + chs + '<div class="vd">입주민 접수</div></div>'
           f'<div class="ctr">{ic("headset")}<b>주관 접수창구</b><span>365일 접수 · 1창구</span></div>'
           '<div class="col"><div class="bd"><span>24시간 내 피드백</span><span>48시간 내 처리</span><span>선보상 후 정산</span><span>해피콜 검수</span></div>'
           '<div class="vd">참여업체 관리·감독</div></div></div>')
    k["body"] = f'<div class="nb"><div class="hub">{rows}{hub}</div></div>'

    # 참여업체 하자보증 체계 — 서약 · 도산 흐름 · 패널티 계단
    k = take("참여업체 [[하자보증]] 체계")[1]
    k["body"] = ('<div class="nb"><div class="wty">'
                 f'<div class="bx"><h4>{ic("report")}01 하자보수 이행각서</h4><p>박람회 참여 모든 업체로부터 하자보수 이행각서를 받습니다.</p></div>'
                 f'<div class="bx"><h4>{ic("lockdoc")}02 참여 특약 서약 · 위반 시 자격박탈</h4><div class="chp" style="margin-top:0">'
                 '<span>현금·카드 동일가</span><span>별도 박람회 금지</span><span>차액 10배 보상</span><span>비방 금지</span><span>과대홍보 금지</span></div></div>'
                 f'<div class="bx"><h4>{ic("ban")}03 업체 도산 시</h4><div class="fl">'
                 f'<div>{ic("ban")}업체 도산</div><em>›</em><div>{ic("users")}동종업체로<br>사후관리 이관</div><em>›</em>'
                 f'<div class="g">{ic("vault")}A/S 비용<br>주관사 전액 부담</div></div></div>'
                 f'<div class="bx"><h4>{ic("steps")}04 패널티 3단계</h4><div class="stp">'
                 '<div><small>1단계</small>홍보정지</div><div><small>2단계</small>총액 10% 배상</div><div><small>3단계</small>자격박탈 · 전 계약 이관</div></div></div>'
                 '</div></div>')

    # 주요 클레임 품목 — 건수 막대
    k = take("주요 클레임 품목과 [[보상 기준]] (예시)")[1]
    cnts = [int(x) for x in re.findall(r'<td class=""><em>(\d+)건</em></td>', k["body"])]
    cmx2 = max(cnts)
    top3 = sorted(cnts, reverse=True)[:3]

    def bar(m):
        n = int(m.group(1))
        return (f'<td class=""><div class="cbar"><em>{n}건</em><i class="{"g" if n in top3 else ""}" '
                f'style="width:{48 * n / cmx2:.0f}px"></i></div></td>')
    k["body"] = re.sub(r'<td class=""><em>(\d+)건</em></td>', bar, k["body"])
    k["body"] = k["body"].replace('<th style="width:9%">건수</th>', '<th style="width:13%">건수</th>').replace('<th style="width:30%">주요 클레임</th>', '<th style="width:27%">주요 클레임</th>')

    # 왜 직영이어야 합니까 — 구조 비교
    k = take("왜 [[직영]]이어야 합니까")[1]
    cmp_ = ('<div class="dvs"><div><h4>지사를 빌려 쓰는 구조</h4><div class="fl"><span>입주민</span><em>›</em><span>주관사</span><em>›</em>'
            '<span>협력 지사</span><em>›</em><span>시공업체</span></div><div class="tg">책임이 단계마다 나뉘고, 중간 마진이 붙습니다.</div></div>'
            '<div class="g"><h4>엣지컴퍼니 직영 구조</h4><div class="fl"><span>입주민</span><em>›</em><span>엣지컴퍼니 직영 거점 · 시공팀</span></div>'
            '<div class="tg">책임 주체 하나 · 단가 그대로 공개 · 거점이 남아 장기 A/S.</div></div></div>')
    k["body"] = '<div class="nb">' + cmp_ + k["body"] + '</div>'

    apply2(B, D, take, sub)


# ============================================================ 2차(감사 순위 상위 · 본부장 10-08 최종 마무리)
CSS2 = r"""
/* 3중 안전망 보호 기간 띠 */
.pt3{border:1px solid var(--line);border-radius:14px;padding:10px 20px 8px;background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.01))}
.pt3 h5{font-size:13px;letter-spacing:.2em;color:var(--gold2);font-weight:700;margin-bottom:6px}
.pt3 h5 small{letter-spacing:0;color:var(--mute);font-weight:400;margin-left:8px;font-size:11.5px}
.pt3 .ln{display:grid;grid-template-columns:30px 1fr;align-items:center;gap:8px;margin-bottom:4px}
.pt3 .ln b{font-size:12px;color:var(--gold);font-weight:800}
.pt3 .tr{position:relative;height:19px;border-radius:5px;background:rgba(255,255,255,.05)}
.pt3 .tr i{position:absolute;top:0;bottom:0;border-radius:5px;font-style:normal;font-size:12px;font-weight:700;display:flex;align-items:center;padding-left:10px;white-space:nowrap;color:#0d1e33}
.pt3 .tr i.a{background:var(--gold)}
.pt3 .tr i.b{background:rgba(235,203,143,.55)}
.pt3 .tr i.c{background:linear-gradient(90deg,rgba(235,203,143,.35),rgba(235,203,143,.08));color:var(--gold)}
.pt3 .tk{position:relative;height:16px;margin-left:38px}
.pt3 .tk span{position:absolute;top:2px;transform:translateX(-50%);font-size:11.5px;color:var(--sub);white-space:nowrap}
.pt3 .tk span:first-child{transform:none}.pt3 .tk span:last-child{transform:translateX(-100%)}
/* 노드 흐름(선보상 재원 · 자금) */
.fl5{display:flex;align-items:stretch;gap:0}
.fl5 .n{flex:1;display:flex;flex-direction:column;align-items:center;text-align:center;gap:4px;border:1px solid rgba(255,255,255,.16);border-radius:12px;padding:10px 8px;background:#0f2237}
.fl5 .n .cic{margin:0 0 2px;width:28px;height:28px}
.fl5 .n b{font-size:14.5px;line-height:1.3}
.fl5 .n span{font-size:12px;color:var(--sub);line-height:1.35}
.fl5 .n.g{border-color:var(--gold2);background:rgba(235,203,143,.13)}
.fl5 .n.g b{color:var(--gold)}
.fl5 em{display:flex;align-items:center;justify-content:center;width:26px;flex:none;color:var(--gold);font-style:normal;font-size:20px;font-weight:800}
/* 자금 흐름 띠 */
.mny{position:relative;border:1px solid var(--line);border-radius:14px;padding:14px 26px 12px;background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.01))}
.mny .rl{position:relative;height:86px}
.mny .ln{position:absolute;left:0;right:0;top:30px;height:2px;background:rgba(255,255,255,.25)}
.mny .zone{position:absolute;top:18px;height:26px;border-radius:6px;background:rgba(235,203,143,.2);border:1px dashed rgba(235,203,143,.7)}
.mny .zone b{position:absolute;left:50%;top:-19px;transform:translateX(-50%);font-size:13.5px;color:var(--gold);white-space:nowrap}
.mny .nd{position:absolute;top:22px;width:18px;height:18px;margin-left:-9px;border-radius:50%;background:#0d1e33;border:2px solid var(--gold2)}
.mny .nd.g{background:var(--gold)}
.mny .lb2{position:absolute;top:46px;transform:translateX(-50%);font-size:15px;white-space:nowrap;text-align:center;font-weight:700}
.mny .lb2 small{display:block;font-weight:400;color:var(--sub);font-size:12.5px;margin-top:2px}
.mny .tk2{position:absolute;top:8px;transform:translateX(-50%);font-size:11px;color:var(--sub);white-space:nowrap}
.mny .tk2:after{content:'';position:absolute;left:50%;top:15px;height:16px;border-left:1px dashed rgba(235,203,143,.8)}
/* 자격 대응: 충족 체크 · 요건 대비 막대 */
.ok svg{width:18px;height:18px;fill:none;stroke:var(--gold);stroke-width:2;stroke-linecap:round;stroke-linejoin:round;display:block;margin:auto}
.okb{display:inline-block;margin-left:10px;border:1px solid var(--gold2);border-radius:99px;padding:1px 10px;font-size:11.5px;letter-spacing:.06em;color:var(--gold)}
.qb{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.qb{flex:1;min-height:0}
.qb>div{border:1px solid var(--line);border-radius:10px;padding:12px 16px;background:rgba(255,255,255,.03);display:flex;flex-direction:column;justify-content:center;gap:4px}
.qb h5{font-size:14px;color:var(--ink);font-weight:700;margin-bottom:6px}
.qb .r{display:grid;grid-template-columns:34px 1fr;align-items:center;gap:6px;font-size:12px;color:var(--mute);margin-top:4px}
.qb .r i{display:flex;align-items:center;justify-content:flex-end;height:21px;border-radius:5px;background:rgba(255,255,255,.22);font-style:normal;font-size:12.5px;font-weight:700;color:var(--ink);padding-right:6px;white-space:nowrap}
.qb .r.g i{background:linear-gradient(90deg,var(--gold2),var(--gold));color:#0d1e33}
/* 간트(추진 일정) */
.q10 td{padding:3px 12px !important;font-size:14.5px !important}
.q10 td.k{font-size:15px !important}
.q10 th{padding-bottom:5px !important}
.q10{table-layout:fixed;width:100%}
.q10 th:nth-child(1){width:5%} .q10 th:nth-child(2){width:23%} .q10 th:nth-child(3){width:45%} .q10 th:nth-child(4){width:20%} .q10 th:nth-child(5){width:7%}
.gnt{position:relative;border:1px solid var(--line);border-radius:14px;padding:10px 22px 6px;background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.01))}
.gnt .ar{position:relative;height:96px;margin:0 6px}
.gnt .yl{position:absolute;top:16px;bottom:16px;border-left:1px dashed rgba(255,255,255,.22)}
.gnt .yl span{position:absolute;bottom:-17px;left:4px;font-size:11px;color:var(--mute)}
.gnt .bk{position:absolute;top:0;height:12px;border:1.5px solid var(--gold2);border-bottom:0;border-radius:4px 4px 0 0}
.gnt .bk b{position:absolute;left:50%;top:-3px;transform:translate(-50%,-50%);background:#12263d;padding:0 8px;font-size:12px;color:var(--gold);white-space:nowrap}
.gnt .br{position:absolute;height:20px;border-radius:5px;display:flex;align-items:center;font-size:11px;font-weight:800;color:#0d1e33;padding-left:6px;white-space:nowrap;overflow:visible}
.gnt .br.l1{top:24px}.gnt .br.l2{top:52px}
.gnt .br.w{background:rgba(235,203,143,.42)}
.gnt .br.s{background:var(--gold);box-shadow:0 0 10px rgba(235,203,143,.35)}
.gnt .br.o{background:linear-gradient(90deg,rgba(235,203,143,.3),rgba(235,203,143,0));border:1.5px solid rgba(235,203,143,.6);border-right:0;color:var(--gold)}
.gnt .br small{position:absolute;left:calc(100% + 6px);font-size:11px;font-weight:600;color:var(--sub);white-space:nowrap}
.gnt .br.o small,.gnt .br.in small{position:static;margin-left:8px;color:#0d1e33;font-weight:700}
.gnt .br.o small{color:var(--gold)}
.gnt .br.up small{position:absolute;left:0;top:-15px;margin:0;color:var(--gold);font-weight:800}
.gnt .pn{position:absolute;top:14px;bottom:10px;border-left:2px solid var(--gold)}
.gnt .pn span{position:absolute;bottom:-4px;left:6px;font-size:11.5px;font-weight:800;color:var(--gold);white-space:nowrap}
.rows.cmp .row{padding-bottom:7px}
.rows.cmp .row .tt{font-size:19px}
.rows.cmp .row .dd{font-size:15.5px;line-height:1.45}
/* 패키지 예시 열 하단 사진 */
.exx .ex .exi{margin-top:auto;position:relative;height:118px;border-radius:9px;overflow:hidden;border-bottom:2px solid var(--gold2)}
.exx .ex .exi img{width:100%;height:100%;object-fit:cover;display:block}
.exx .ex .exi span{position:absolute;left:0;right:0;bottom:0;padding:16px 10px 5px;font-size:11px;color:#fff;background:linear-gradient(0deg,rgba(8,18,32,.85),rgba(8,18,32,0))}
.exx .ex .exi.cs{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;background:rgba(235,203,143,.08);border:1px dashed rgba(235,203,143,.5);border-bottom:2px solid var(--gold2)}
.exx .ex .exi.cs .cic{margin:0;width:30px;height:30px}
.exx .ex .exi.cs b{font-size:22px;color:var(--gold);font-weight:800}
.exx .ex .exi.cs small{font-size:11.5px;color:var(--sub)}
/* C 패키지 썸네일 */
.thm{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-top:auto}
.thm figure{margin:0}
.thm .im{position:relative;aspect-ratio:4/3;border-radius:8px;overflow:hidden;border:1px solid rgba(200,168,106,.5)}
.thm img{width:100%;height:100%;object-fit:cover;display:block}
.thm .im b{position:absolute;left:6px;bottom:6px;width:24px;height:24px;border-radius:50%;background:var(--gold);color:#0d1e33;font-size:11px;font-weight:800;display:flex;align-items:center;justify-content:center}
.thm figcaption{font-size:12px;color:var(--sub);margin-top:5px;text-align:center}
.thc{font-size:11.5px;color:var(--mute);text-align:right}
/* 사진 없는 칸(아이콘 패널) */
.gal figure.ipn{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;background:linear-gradient(180deg,#132a45,#0b1a2d);text-align:center;padding:12px}
.gal figure.ipn .cic{margin:0;width:46px;height:46px}
.gal figure.ipn p{font-size:14px;color:var(--sub);line-height:1.45}
.gal figure.ipn p b{display:block;color:var(--ink);font-size:15.5px;margin-bottom:2px}
/* 추가할인 계단 막대 */
.stc{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;height:206px;align-items:end;padding:26px 10px 0;border-bottom:1.5px solid rgba(200,168,106,.6)}
.stc>div{display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%}
.stc b{font-size:14px;color:var(--gold);margin-bottom:5px;white-space:nowrap}
.stc i{display:block;width:62%;border-radius:6px 6px 0 0;background:linear-gradient(180deg,var(--gold),rgba(200,168,106,.35))}
.stx{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;padding:6px 10px 0;text-align:center}
.stx div{font-size:13.5px;font-weight:700}
.stx span{display:inline-block;margin-top:6px;border-radius:99px;padding:3px 12px;font-size:13px;font-weight:800;color:#0d1e33}
.stx div:nth-child(1) span{background:rgba(235,203,143,.5)}.stx div:nth-child(2) span{background:rgba(235,203,143,.75)}.stx div:nth-child(3) span{background:var(--gold)}
.stx small{display:block;font-size:11px;color:var(--mute);font-weight:400;margin-top:3px}
/* 수직계열화 체인 */
.cards.chain .card{position:relative;overflow:visible}
.cards.chain .card:not(:last-child):after{content:'›';position:absolute;right:-26px;top:50%;width:26px;height:26px;margin-top:-13px;border-radius:50%;
  background:#0d1e33;border:1.5px solid var(--gold2);color:var(--gold);font-weight:800;font-size:17px;line-height:22px;text-align:center;z-index:2}
.chipx{display:inline-block;margin-top:10px;border:1px solid rgba(235,203,143,.6);border-radius:99px;padding:3px 10px;font-size:12px;color:var(--gold)}
/* 단지 특성: 벤 + 진입 높이 */
.vn{display:grid;grid-template-columns:1.35fr 1fr;gap:22px;flex:1;min-height:0}
.vn .rows .row{grid-template-columns:40px 28px 172px 1fr !important;padding-bottom:10px}
.vn .rows .row .cic{width:24px;height:24px;margin:0}
.vn .rows .row .tt{font-size:18.5px}
.vn .rows .row .dd{font-size:14.5px;line-height:1.5}
.vnp{border:1px solid var(--line);border-radius:14px;padding:14px 16px;display:flex;flex-direction:column;gap:10px;background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.01))}
.vnp svg{width:100%;height:auto;display:block}
.vnp h5{font-size:12.5px;letter-spacing:.18em;color:var(--gold2);font-weight:700}
.lns{display:flex;flex-direction:column;gap:6px}
.lns .l{display:grid;grid-template-columns:44px 1fr;align-items:center;gap:8px;font-size:12px;font-weight:700}
.lns .t{position:relative;height:18px;border-radius:4px;background:rgba(255,255,255,.05)}
.lns .t i{position:absolute;top:2px;bottom:2px;border-radius:3px;font-style:normal;font-size:10.5px;font-weight:700;color:#0d1e33;display:flex;align-items:center;justify-content:center;white-space:nowrap}
.lns .t i.a{background:var(--gold)}.lns .t i.b{background:rgba(235,203,143,.6)}.lns .t i.c{background:rgba(255,255,255,.35)}
.vnp .cp{font-size:11.5px;color:var(--mute)}
/* 위임장 휴대폰 화면 */
.phw{flex:1;min-height:0;border:1px solid rgba(200,168,106,.32);border-radius:12px;background:radial-gradient(circle at 50% 40%,#173356,#0b1a2d);position:relative;display:flex;align-items:center;justify-content:center}
.phm{width:172px;border-radius:26px;border:2px solid var(--gold2);background:#0a1626;padding:20px 12px 12px;margin-bottom:14px;position:relative;box-shadow:0 10px 30px rgba(0,0,0,.4)}
.phm:before{content:'';position:absolute;left:50%;top:8px;width:56px;height:6px;margin-left:-28px;border-radius:4px;background:rgba(255,255,255,.18)}
.phm h6{font-size:12.5px;color:var(--gold);font-weight:800;text-align:center;margin-bottom:10px}
.phm .f{border:1px solid rgba(255,255,255,.2);border-radius:6px;padding:5px 8px;font-size:11px;color:var(--mute);margin-bottom:6px}
.phm .ck{font-size:11px;color:var(--sub);margin:4px 0 8px}
.phm .ck b{color:var(--gold)}
.phm .sg{height:52px;border:1px dashed rgba(235,203,143,.6);border-radius:6px;position:relative}
.phm .sg svg{position:absolute;inset:6px 10px;width:calc(100% - 20px);height:calc(100% - 12px);fill:none;stroke:var(--gold);stroke-width:2;stroke-linecap:round}
.phm .bt{margin-top:10px;border-radius:7px;background:var(--gold);color:#0d1e33;font-size:12px;font-weight:800;text-align:center;padding:6px 0}
.phw .pg{position:absolute;right:14px;bottom:30px;width:150px;border:1px solid rgba(255,255,255,.2);border-radius:10px;padding:8px 10px;background:#0f2237;font-size:11px;color:var(--sub)}
.phw .pg i{display:block;height:7px;border-radius:4px;background:rgba(255,255,255,.12);margin-top:6px;overflow:hidden}
.phw .pg i:after{content:'';display:block;width:64%;height:100%;background:var(--gold2)}
.phw .cap{position:absolute;left:12px;bottom:8px;font-size:11px;color:var(--mute)}
.flowx .st .cic{width:24px;height:24px;margin:0 0 6px}
/* 타일 위 사진 */
.tile .tim{margin:-16px -20px 10px;height:96px;overflow:hidden;border-radius:12px 12px 0 0;border-bottom:2px solid var(--gold2);position:relative}
.tile .tim img{width:100%;height:100%;object-fit:cover;display:block}
.tile .tim span{position:absolute;right:6px;bottom:4px;font-size:10px;color:rgba(255,255,255,.8);text-shadow:0 1px 2px #000}
.tile .tim.ipn{display:flex;align-items:center;justify-content:center;gap:10px;background:linear-gradient(180deg,#132a45,#0b1a2d)}
.tile .tim.ipn .cic{margin:0;width:38px;height:38px}
.tile .tim.ipn b{font-size:12px;border:1px solid var(--gold2);border-radius:99px;padding:2px 10px;color:var(--gold)}
/* 연락처: 본사 사옥 */
.cvc>*:not(.cvhq){position:relative;z-index:1}
.cvc .mid{max-width:calc(100% - 300px)}
.cvc .contacts b{white-space:nowrap;font-size:29px}
.cvc .contacts .me b{font-size:25px}
.cvc .tag2{font-size:18px}
.cvc .contacts{grid-template-columns:repeat(2,auto)}
.cvc .contacts .me{grid-column:auto}
.cvc .addr{font-size:14.5px}
.cvhq{position:absolute;z-index:0;right:64px;top:140px;bottom:96px;width:256px;border-radius:16px;overflow:hidden;border:1.5px solid rgba(235,203,143,.55);box-shadow:0 18px 40px rgba(0,0,0,.35)}
.cvhq img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 45%}
.cvhq:after{content:'';position:absolute;inset:0;background:linear-gradient(0deg,rgba(8,18,32,.85) 0%,rgba(8,18,32,0) 22%)}
.cvhq span{position:absolute;z-index:1;left:16px;bottom:12px;font-size:12.5px;font-weight:700;color:#fff}
/* 사전점검 가격 카드 */
.tiles.tp .tim{height:70px}
.tiles.tp .tile .ds{font-size:14.5px;line-height:1.45}
.tiles.tp .tile .nm{font-size:18px;margin-top:4px}
.pv{display:flex;flex-direction:column;gap:8px;margin-bottom:14px}
.pv .pp{display:flex;align-items:center;gap:3px;height:26px}
.pv .pp .cic{width:22px;height:22px;margin:0}
.pv .pp em{width:1px;height:20px;background:rgba(255,255,255,.3);margin:0 6px}
.pv .pp small{font-size:10.5px;color:var(--mute);margin-left:6px}
.pv .r{display:grid;grid-template-columns:44px 1fr;align-items:center;gap:6px;font-size:11px;color:var(--mute)}
.pv .r i{display:flex;align-items:center;justify-content:flex-end;height:16px;border-radius:4px;background:rgba(255,255,255,.2);font-style:normal;font-size:11px;font-weight:700;color:var(--ink);padding-right:6px}
.pv .r.g i{background:linear-gradient(90deg,var(--gold2),var(--gold));color:#0d1e33}
"""


def apply2(B, D, take, sub):
    B.CSS += CSS2

    # 3중 안전망 — 보호 기간 띠(카드 숫자 그대로 · 눈금은 비례 아님)
    k = take("입주민을 지키는 [[3중 안전망]]")[1]
    band = ('<div class="pt3"><h5>보호 기간 한눈에<small>눈금은 기간에 비례하지 않습니다 · 무상 A/S 기간은 업체·품목별로 다를 수 있음</small></h5>'
            '<div class="ln"><b>01</b><div class="tr"><i class="a" style="left:0;width:42%">이행보증보험 2년 · 최대 10억</i></div></div>'
            '<div class="ln"><b>02</b><div class="tr"><i class="a" style="left:0;width:15%">48시간 처리</i></div></div>'
            '<div class="ln"><b>03</b><div class="tr"><i class="b" style="left:0;width:42%">무상 A/S 최소 2년</i><i class="c" style="left:42%;width:58%">장기 관리 최대 10년</i></div></div>'
            '<div class="tk"><span style="left:0">입주</span><span style="left:15%">48시간</span><span style="left:42%">2년</span><span style="left:100%">10년</span></div></div>')
    k["body"] = '<div class="nb">' + band + sub(k["body"], "최소 2년 무상 A/S, 최대 10년 장기 관리.",
                                                "최소 2년 무상 A/S(업체·품목에 따라 기간이 다를 수 있음), 최대 10년 장기 관리.") + '</div>'

    # 선보상 재원 — 돈의 흐름
    k = take("선보상 재원 · 하자 예치금 [[최대 1억원]]")[1]
    fl = ('<div class="fl5">'
          f'<div class="n">{ic("vault")}<b>엣지컴퍼니 자산</b><span>참여 업체 돈이 아님</span></div><em>›</em>'
          f'<div class="n">{ic("coins")}<b>예치금 최대 1억원</b><span>단지 규모·협의로 결정</span></div><em>›</em>'
          f'<div class="n">{ic("headset")}<b>하자 접수</b><span>주관 콜센터</span></div><em>›</em>'
          f'<div class="n g">{ic("house_shield")}<b>입주민 먼저 선보상</b><span>업체 사고·도산 시에도</span></div><em>›</em>'
          f'<div class="n">{ic("report")}<b>사용 내역 공개</b><span>업체와는 나중에 정산</span></div></div>')
    k["body"] = '<div class="nb">' + fl + k["body"] + '</div>'

    # 참여업체 하자보증 체계 — 칸 균형
    k = take("참여업체 [[하자보증]] 체계")[1]
    b = sub(k["body"], '<p>박람회 참여 모든 업체로부터 하자보수 이행각서를 받습니다.</p>',
            '<p>박람회 참여 모든 업체로부터 하자보수 이행각서를 받습니다.</p><div class="chp" style="margin-top:4px">'
            '<span>참여 업체 전원</span><span>최종 확정 시 징구</span><span>물품공급계약서 · 청렴이행서약서와 함께</span></div>')
    k["body"] = b.replace('<div class="wty">', '<div class="wty" style="grid-template-rows:auto 1fr">')
    B.CSS += (".wty .bx{display:flex;flex-direction:column;gap:6px}.wty .bx p{font-size:15.5px}.wty h4{font-size:16.5px}"
              ".wty .stp{flex:1;height:auto;min-height:120px}.wty .fl{flex:1}.wty .fl div{font-size:14.5px;padding:14px 6px}")

    # 입찰 참가 자격 22개(① 1~11 · ② 12~22) — 표 문구 그대로, 열 너비만 고정
    B.CSS += (".q22{table-layout:fixed;width:100%}.q22 td{padding:4px 12px !important;font-size:14px !important;line-height:1.38 !important}"
              ".q22 td.k{font-size:14.5px !important}.q22 th{padding-bottom:6px !important}"
              ".q22 th:nth-child(1){width:5%}.q22 th:nth-child(2){width:27%}.q22 th:nth-child(3){width:46%}.q22 th:nth-child(4){width:22%}")

    # 선정부터 입주까지 추진 일정 — 간트(개월 m: 2026.10=0 … 2029.04=30)
    k = take("선정부터 입주까지 [[추진 일정]] (안)")[1]
    X = lambda m: f"{100 * m / 30:.2f}%"
    W = lambda a, b: f"{100 * (b - a) / 30:.2f}%"
    bars = [("01", 0, 2, "l1", "w", "선정·협약"), ("02", 2, 17, "l2", "w in", "정례 보고 · 건의 관리 · 조경조명 진단"), ("03", 9, 12, "l1", "w in", "수요조사"),
            ("04", 12, 14, "l1", "s in", "심사"), ("05", 14, 16, "l1", "s up", "박람회"), ("06", 17, 29, "l2", "o", "입주 후 1년 관리")]
    g = '<div class="gnt"><div class="ar">'
    g += "".join(f'<div class="yl" style="left:{X(m)}"><span>{y}</span></div>' for y, m in [("2027", 3), ("2028", 15), ("2029", 27)])
    g += f'<div class="bk" style="left:0;width:{W(0, 17)}"><b>선정에서 입주까지 17개월</b></div>'
    g += "".join(f'<div class="br {ln} {c}" style="left:{X(a)};width:{W(a, b)}">{no}{f"<small>{tx}</small>" if tx else ""}</div>'
                 for no, a, b, ln, c, tx in bars)
    g += f'<div class="pn" style="left:{X(17)}"><span>2028.03 입주</span></div>'
    g += '</div></div>'
    k["body"] = '<div class="nb" style="gap:10px">' + g + k["body"].replace('<div class="rows">', '<div class="rows cmp">', 1) + '</div>'

    # 패키지 예시 — 열 하단 대표 사진
    k = take("이렇게 [[패키지로]] 받으실 수 있습니다 (예시)")[1]
    _hh, _f = D.SITE["households"], D.FUND
    _tot = f"{_hh * _f // 10000}억 {_hh * _f % 10000:,}만원" if _hh * _f % 10000 else f"{_hh * _f // 10000}억원"
    tails = [(f'<div class="exi cs">{ic("vault")}<b>{_tot}</b><small>입예협 공식 통장</small></div>' if getattr(D, "FUND_CASH", False) else
              f'<div class="exi cs">{ic("checklist")}<b>{_tot} 상당</b><small>주관사가 직접 구매·제공 · 사용 내역 공개</small></div>'),
             '<div class="exi"><img src="assets_ins/g08_thermal.jpg" alt=""><span>열화상 점검 화면 · 타 단지</span></div>',
             '<div class="exi"><img src="assets_ins/g12_style_after.jpg" alt=""><span>3D 홈스타일링 · 제작 예시</span></div>',
             '<div class="exi"><img src="assets_ins/tj_gate_night.jpg" alt=""><span>문주·경관조명 · 연출 예시 이미지</span></div>']
    it = iter(tails)
    b, n = re.subn(r"</ul></div>", lambda m: "</ul>" + next(it) + "</div>", k["body"])
    assert n == 4, n
    k["body"] = b

    # C 패키지 — 항목 썸네일
    k = take("C 패키지 · [[단지지원 컨설팅]]")[1]
    th = [("n13_fit", "커뮤니티 조명"), ("tj_gate_night", "문주·경관조명"), ("n13_kidsplay", "피트니스·키즈"),
          ("n13_ev1", "전기차 충전"), ("g14_light3", "입주 기념 점등식")]
    thm = ('<div class="thm">' + "".join(f'<figure><div class="im"><img src="assets_ins/{im}.jpg" alt=""><b>{i:02d}</b></div><figcaption>{c}</figcaption></figure>'
                                          for i, (im, c) in enumerate(th, 1))
           + '</div><div class="thc">사진은 타 단지 현장·예시 · 문주 이미지는 연출 예시</div>')
    k["body"] = sub(k["body"], "</li></ul></div></div></div>", "</li></ul>" + thm + "</div></div></div>")

    # 커뮤니티·공용부 조명 개선 — 목록 + 2×2
    k = take("커뮤니티·공용부 [[조명 개선]]")[1]
    rows = k["body"]
    for n_, name in enumerate(["users", "streetlight", "bell", "building"], 1):
        rows = sub(rows, f'<div class="no">{n_:02d}</div>', f'<div class="no">{n_:02d}</div>{ic(name)}')
    rows = rows.replace("grid-template-columns:46px 268px 1fr", "grid-template-columns:40px 30px 190px 1fr")
    gal = ('<div class="gal">'
           '<figure><img src="assets_ins/n13_gx.jpg" alt=""><figcaption>커뮤니티 공간<small>예시 이미지</small></figcaption></figure>'
           '<figure><img src="assets_ins/n03_light.jpg" alt=""><figcaption>등기구 설치 현장<small>엣지컴퍼니 시공팀</small></figcaption></figure>'
           '<figure><img src="assets_ins/g14_light1c.jpg" alt=""><figcaption>입주 기념 점등식<small>타 단지 현장</small></figcaption></figure>'
           f'<figure class="ipn">{ic("streetlight")}<p><b>사인·문주 조명</b>다음 장 · 문주·경관조명 컨설팅</p></figure></div>')
    k["body"] = f'<div class="nb"><div class="r2">{rows}{gal}</div></div>'

    # 실적 비례 추가할인 — 표 → 계단 막대(표 값 그대로)
    k = take("실적 비례 [[추가할인]] 구조")[1]
    b = re.sub(r'<table class="tbl xs">.*?</table>',
               '<div class="stc"><div><b>1% · 1만원</b><i style="height:33%"></i></div><div><b>2% · 2만원</b><i style="height:66%"></i></div>'
               '<div><b>3% · 3만원</b><i style="height:100%"></i></div></div>'
               '<div class="stx"><div>50세대<br><span>99만원</span></div><div>100세대<br><span>98만원</span></div><div>150세대<br><span>97만원</span></div></div>'
               '<div class="stx" style="padding-top:0"><small>계약 세대 수 · 막대 = 추가할인 · 칩 = 최종 결제</small><small></small><small></small></div>', k["body"], flags=re.S)
    assert b != k["body"]
    k["body"] = b.replace('<div class="splitx" style="grid-template-columns:1.15fr 1fr">', '<div class="splitx adx" style="grid-template-columns:1.35fr 1fr">', 1)
    B.CSS += (".adx .bulx{gap:22px}.adx .bulx b{font-size:23px}.adx .bulx p{font-size:18px}"
              ".adx .stc{height:150px;padding-top:22px}.adx .stc b{font-size:13px}.adx .exbox h4{font-size:13px}")

    # 조명 수직계열화 — 아이콘 체인
    k = take("[[조명 수직계열화]] · 유통 단계 없는 공급")[1]
    b = inject(k["body"], ["ship", "factory", "kc", "ladder"])
    b = sub(b, '<div class="cards" style="grid-template-columns:repeat(4,1fr)">', '<div class="cards chain" style="grid-template-columns:repeat(4,1fr);gap:26px">')
    b = sub(b, "하자가 나도 다른 업체를 찾을 필요가 없습니다.</div>", '하자가 나도 다른 업체를 찾을 필요가 없습니다.<br><span class="chipx">전기공사업 등록 제 울산-00821호</span></div>')
    k["body"] = b

    # 이 단지라서 먼저 챙길 것 — 벤(유상옵션 × 공동구매) + 지하 진입 높이(최초 입주자모집공고)
    k = take("이 단지라서 [[먼저 챙길 것]]")[1]
    rows = k["body"]
    for n_, name in enumerate(["checklist", "tape", "truck2", "wrench", "lockdoc"], 1):
        rows = sub(rows, f'<div class="no">{n_:02d}</div>', f'<div class="no">{n_:02d}</div>{ic(name)}')
    venn = ('<svg viewBox="0 0 340 176"><defs><clipPath id="vA"><circle cx="130" cy="88" r="78"/></clipPath></defs>'
            '<circle cx="130" cy="88" r="78" fill="rgba(255,255,255,.05)" stroke="rgba(255,255,255,.45)" stroke-width="1.5"/>'
            '<circle cx="210" cy="88" r="78" fill="rgba(235,203,143,.06)" stroke="#C8A86A" stroke-width="1.5"/>'
            '<circle cx="210" cy="88" r="78" fill="rgba(235,203,143,.38)" clip-path="url(#vA)"/>'
            '<text x="90" y="74" text-anchor="middle" font-size="12.5" font-weight="700" fill="#DCE3EC">유상옵션</text>'
            '<text x="90" y="91" text-anchor="middle" font-size="10.5" fill="#A9B4C2">시공사 선택 ·</text>'
            '<text x="90" y="105" text-anchor="middle" font-size="10.5" fill="#A9B4C2">기본 제공</text>'
            '<text x="170" y="84" text-anchor="middle" font-size="11.5" font-weight="800" fill="#0D1E33">겹치면</text>'
            '<text x="170" y="99" text-anchor="middle" font-size="11.5" font-weight="800" fill="#0D1E33">권하지 않음</text>'
            '<text x="250" y="74" text-anchor="middle" font-size="12.5" font-weight="700" fill="#EBCB8F">공동구매</text>'
            '<text x="250" y="91" text-anchor="middle" font-size="10.5" fill="#A9B4C2">가격 공개표로</text>'
            '<text x="250" y="105" text-anchor="middle" font-size="10.5" fill="#A9B4C2">비교 안내</text></svg>')
    hts = ('<div class="hts">'
           '<div class="h"><b>지하 1층</b><div class="t"><i style="width:100%">차로·주출입구 2.7m 이상</i></div></div>'
           '<div class="h"><b>지하 2층</b><div class="t"><i style="width:85%">차로 2.3m 이상</i></div></div>'
           '<div class="h x"><b>택배차량</b><div class="t"><i>지하 진입 불가 (모집공고)</i></div></div></div>')
    pan = (f'<div class="vnp"><h5>유상옵션 중복 확인</h5>{venn}<h5>지하 진입 높이 · 반입 동선</h5>{hts}'
           '<div class="cp">최초 입주자모집공고 기준 · 현장 실측으로 다시 확인합니다</div></div>')
    k["body"] = f'<div class="nb"><div class="vn">{rows}{pan}</div></div>'
    B.CSS += (".hts{display:flex;flex-direction:column;gap:7px}.hts .h{display:grid;grid-template-columns:62px 1fr;align-items:center;gap:8px;font-size:12px}"
              ".hts .h b{font-weight:700;color:var(--ink)}.hts .t{height:20px;border-radius:4px;background:rgba(255,255,255,.05);position:relative}"
              ".hts .t i{position:absolute;left:0;top:2px;bottom:2px;border-radius:3px;background:var(--gold);color:#0d1e33;font-style:normal;font-size:11px;font-weight:800;display:flex;align-items:center;padding-left:8px;white-space:nowrap}"
              ".hts .h:nth-child(2) .t i{background:rgba(235,203,143,.65)}.hts .h.x .t i{position:static;display:flex;height:100%;background:transparent;border:1.5px dashed rgba(255,255,255,.45);color:var(--sub)}")

    # 중앙광장·물의정원 — 단계 목록 + 경관조명 연출 사진 2장
    k = take("중앙광장 · 물의정원, [[밤까지]] 살피겠습니다")[1]
    rows = k["body"]
    for n_, name in enumerate(["streetlight", "pin", "search", "report"], 1):
        rows = sub(rows, f'<div class="no">{n_:02d}</div>', f'<div class="no">{n_:02d}</div>{ic(name)}')
    gal = ('<div class="gal lx2">'
           '<figure><img src="assets_ins/tj_water_garden.jpg" alt="" style="object-position:50% 70%"><figcaption>물의정원 경관조명<small>수변 라인조명 · 수목 업라이트 · 개선 연출 예시</small></figcaption></figure>'
           '<figure><img src="assets_ins/tj_central_plaza.jpg" alt="" style="object-position:50% 55%"><figcaption>중앙광장 경관조명<small>조형물 조명 · 보행등 · 산책로 간접조명 · 개선 연출 예시</small></figcaption></figure></div>')
    k["body"] = f'<div class="nb"><div class="r2">{rows}{gal}</div></div>'
    B.CSS += ".r2 .gal.lx2{grid-template-columns:1fr;grid-template-rows:1fr 1fr}"

    # 개인정보 — 아이콘 목록
    k = take("입주민 개인정보는 [[행사 운영에만]] 씁니다")[1]
    for n_, name in enumerate(["search", "ban", "lockdoc", "users", "megaphone", "shield"], 1):
        k["body"] = sub(k["body"], f'<div class="no">{n_:02d}</div>', f'<div class="no">{n_:02d}</div>{ic(name)}')
    k["body"] = k["body"].replace("grid-template-columns:46px 210px 1fr", "grid-template-columns:46px 30px 210px 1fr")
    B.CSS += ".rows .row .cic{width:26px;height:26px;margin:0;align-self:center}"

    # 위임장 — 오프라인 회의 사진 → 휴대폰 서명 화면(예시)
    k = take("위임장, 이제 [[휴대폰으로]] 받습니다")[1]
    ph = ('<div class="phw"><div class="phm"><h6>입주예정자협의회 위임장</h6>'
          '<div class="f">동 ○○○</div><div class="f">호 ○○○</div><div class="f">성명 ○○○</div>'
          '<div class="ck"><b>✓</b> 위임 내용을 확인했습니다</div>'
          '<div class="sg"><svg viewBox="0 0 120 50"><path d="M4 34c8-20 14-22 16-12s-4 16 2 12 10-22 16-16-2 16 6 12 8-14 14-10 4 10 10 8 10-8 16-6 8 4 12 2"/></svg></div>'
          '<div class="bt">서명 제출</div></div>'
          '<span class="cap">화면 예시 · 양식·항목은 입예협과 협의</span></div>')
    b = re.sub(r'<div class="gal" style="grid-template-columns:repeat\(1,1fr\);grid-template-rows:repeat\(1,1fr\);flex:1 1 0">.*?</figure></div>', ph, k["body"], flags=re.S)
    assert b != k["body"]
    for i_, name in enumerate(["link", "report", "pen", "folder"], 1):
        b = sub(b, f"<i>STEP 0{i_}</i>", f"{ic(name)}<i>STEP 0{i_}</i>")
    k["body"] = b

    # 입주민 자금 — 결제·해약 흐름 띠(카드 문구 그대로)
    k = take("입주민 [[자금]]을 먼저 지킵니다")[1]
    mny = ('<div class="mny"><div class="rl"><div class="ln"></div>'
           '<div class="zone" style="left:0;width:37%"><b>취소 기한 내 전액 환불</b></div>'
           '<div class="nd g" style="left:0"></div><div class="nd" style="left:37%"></div><div class="nd" style="left:70%"></div><div class="nd g" style="left:100%"></div>'
           '<div class="lb2" style="left:5%">계약<small>계약금 10% 이하</small></div>'
           '<div class="lb2" style="left:37%">취소 기한<small>시공일 7일·15일 전 · 맞춤 제작은 출고 지시 전</small></div>'
           '<div class="lb2" style="left:70%">시공·설치<small>기한 뒤 취소는 실제 자재·제작비만 공제</small></div>'
           '<div class="lb2" style="left:94%">잔금 납부<small>시공·설치 후</small></div>'
           '</div></div>')
    k["body"] = '<div class="nb">' + mny + k["body"] + '</div>'

    # 현장 안전 · 공용부 위생 — 타일 위 사진
    k = take("현장 안전 · 공용부 위생까지 [[함께 챙깁니다]]")[1]
    pics = {"02 · SAFETY": ("g08_safety", "50% 22%", "현장 점검 예시"), "04 · VOICE": ("n12_meeting", "50% 40%", "타 단지 협의회 미팅"),
            "05 · ANALYSIS": ("g08_crack", "50% 50%", "균열 점검 예시"), "13 · COATING": ("g10_doorlock", "50% 45%", "항균 코팅 작업 예시"),
            "15 · AIR": ("g10_phyton", "50% 45%", "분사 작업 예시")}
    b = k["body"]
    for lb, (im, pos, cp) in pics.items():
        b = sub(b, f'<div class="tile"><div class="lb">{lb}</div>',
                f'<div class="tile"><div class="tim"><img src="assets_ins/{im}.jpg" style="object-position:{pos}" alt=""><span>{cp}</span></div><div class="lb">{lb}</div>')
    b = sub(b, '<div class="tile"><div class="lb">14 · CESCO</div>',
            '<div class="tile"><div class="tim"><img src="assets_ins/n94_cesco.jpg" style="object-position:50% 50%" alt=""><span>세스코 · 2025.11 MOU</span></div><div class="lb">14 · CESCO</div>')
    k["body"] = b.replace('<div class="tiles"', '<div class="tiles tp"', 1)

    # 사전점검 당일 현장 지원 — 위: 현수막·X배너 시안(HTML로 그린 예시) / 아래: 사진 카드 5칸
    k = take("사전점검 당일 [[현장 지원]]")[1]
    banner = ('<div class="bnx"><div class="bl"><i>01</i><b>행사 물품</b>'
              '<p>부스용 현수막·X배너·서면 자료 제작</p><small>시안 · 협의 후 확정</small></div>'
              '<div class="hbw"><div class="hbn"><span class="t1">탕정 푸르지오 센터파크 입주예정자협의회</span>'
              '<b>탕정 푸르지오 센터파크 입주민 여러분, <em>사전점검을 환영합니다</em></b>'
              '<span class="t2">입예협 안내 부스 · 라돈 측정 · 하자 체크리스트 배포</span></div><span class="cp">현수막 시안</span></div>'
              '<div class="xbw"><div class="xbn"><div class="xh"><span>탕정 푸르지오 센터파크</span><b>사전점검<br>안내</b></div>'
              '<ol><li>입예협 부스 방문 · 정회원 가입</li><li>라돈 측정 지원</li><li>하자 체크리스트 · 점검 요령</li><li>입주박람회 2027.12 ~ 2028.01(예정)</li></ol>'
              '<div class="xf">탕정 푸르지오 센터파크<br>입주예정자협의회</div></div><span class="cp">X배너 시안</span></div></div>')
    items = [("02", "입예협 도우미", "부스 운영 인력 별도 지원", ("g09_helper_ai", "50% 30%")),
             ("03", "라돈측정기 10대", "입주민이 내 집 라돈을 직접 측정", ("g09_radon_u", "50% 50%")),
             ("04", "냉·난방용품", "점검 시기에 맞춰 부스용 준비", ("g09_heater_ai", "50% 50%")),
             ("05", "커피차 지원", "점검 당일 입예협 부스에 커피차 지원", ("g09_coffee_u2", "50% 50%")),
             ("06", "하자진단 보고서", "공용부·조경 점검 결과를 사진·도면으로", ("n11_report", "50% 40%"))]
    tile = lambda no, nm, ds, ph_: (f'<div class="tile"><div class="tim"><img src="assets_ins/{ph_[0]}.jpg" style="object-position:{ph_[1]}" alt=""></div>'
                                    f'<div class="lb">{no}</div><div class="nm">{nm}</div><div class="ds">{ds}</div></div>')
    k["body"] = (f'<div class="nb"><div class="r91">{banner}{tile(*items[0])}</div>'
                 f'<div class="tiles t5" style="grid-template-columns:repeat(4,1fr);grid-template-rows:1fr">{"".join(tile(*x) for x in items[1:])}</div></div>')
    B.CSS += r"""
.tile .tim+.lb{margin-top:0}
.t5 .tile,.r91 .tile{justify-content:flex-start}.t5 .tile .nm{font-size:17px}.t5 .tile .ds{font-size:13.5px;line-height:1.45}.t5 .tim{height:136px}
.r91{display:grid;grid-template-columns:2.05fr 1fr;gap:14px;flex:0 0 172px}
.r91 .tile .tim{height:70px}.r91 .tile .nm{font-size:17px}.r91 .tile .ds{font-size:13.5px}
.bnx{display:grid;grid-template-columns:128px 1fr 70px;gap:14px;align-items:center;border:1px solid var(--line);border-radius:12px;padding:10px 16px;
  background:radial-gradient(120% 120% at 60% 40%,#173356,#0b1a2d)}
.bnx .bl i{display:block;font-style:normal;font-size:12px;letter-spacing:.22em;color:var(--gold2);font-weight:700}
.bnx .bl b{display:block;font-size:18px;font-weight:800;margin:2px 0 4px}
.bnx .bl p{font-size:12.5px;color:var(--sub);line-height:1.45}
.bnx .bl small{display:inline-block;margin-top:6px;font-size:10.5px;color:var(--gold);border:1px solid rgba(235,203,143,.55);border-radius:99px;padding:2px 10px}
.bnx .cp{display:block;text-align:center;font-size:10px;color:var(--mute);margin-top:5px}
.hbw{position:relative;padding:0 4px}
.hbw:before,.hbw:after{content:'';position:absolute;top:-10px;width:1px;height:14px;background:rgba(255,255,255,.5)}
.hbw:before{left:12px}.hbw:after{right:12px}
.hbn{position:relative;aspect-ratio:4.6/1;border-radius:3px;background:linear-gradient(180deg,#fdfaf2,#f3ead6);box-shadow:0 8px 22px rgba(0,0,0,.45);
  display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;border-top:5px solid #0d1e33;border-bottom:5px solid #c8a86a;padding:0 12px}
.hbn .t1{font-size:9.5px;font-weight:700;color:#8a6630;letter-spacing:.06em}
.hbn b{font-size:16.5px;font-weight:900;color:#0d1e33;letter-spacing:-.02em;margin:2px 0 3px;line-height:1.2}
.hbn b em{color:#b0812f;font-style:normal}
.hbn .t2{font-size:9.5px;color:#334;font-weight:600}
.xbw{position:relative;display:flex;flex-direction:column;align-items:center}
.xbn{width:70px;height:112px;border-radius:3px;background:#fdfaf2;box-shadow:0 8px 22px rgba(0,0,0,.45);overflow:hidden;display:flex;flex-direction:column}
.xbn .xh{background:#0d1e33;color:#fff;text-align:center;padding:5px 3px 4px;border-bottom:3px solid #c8a86a}
.xbn .xh span{display:block;font-size:6.5px;color:#ebcb8f;font-weight:700}
.xbn .xh b{display:block;font-size:10.5px;font-weight:900;line-height:1.15;margin-top:2px}
.xbn ol{list-style:none;margin:0;padding:3px 5px 0;counter-reset:x;flex:1}
.xbn li{counter-increment:x;font-size:5.6px;color:#223;line-height:1.25;padding:2px 0 2px 9px;position:relative;border-bottom:1px dashed #d8ccb0;font-weight:600}
.xbn li:before{content:counter(x);position:absolute;left:0;top:2px;width:7px;height:7px;border-radius:50%;background:#c8a86a;color:#fff;font-size:5px;line-height:7px;text-align:center}
.xbn .xf{font-size:7px;color:#8a6630;text-align:center;padding:5px 2px 7px;font-weight:700;line-height:1.3}
.xbw .leg{width:98px;height:14px;position:relative}
.xbw .leg:before,.xbw .leg:after{content:'';position:absolute;top:0;width:2px;height:16px;background:rgba(255,255,255,.55)}
.xbw .leg:before{left:30px;transform:rotate(25deg)}.xbw .leg:after{right:30px;transform:rotate(-25deg)}
"""

    # 15만원 선택 — 카드 아래: 현금 흐름 / A·B·C 구성
    k = take(B.FUND_CHOICE_TITLE)[1]
    opf = ('<div class="opf">'
           f'<div>{ic("vault")}주관사 지급</div><em>›</em><div>{ic("coins")}입예협 공식 통장</div><em>›</em><div>{ic("checklist")}쓰임새는 입예협 결정</div></div>')
    if not getattr(D, "FUND_CASH", False):
        opf = ('<div class="opf">'
               f'<div>{ic("checklist")}입예협 항목 지정</div><em>›</em><div>{ic("truck")}주관사 직접 구매·제공</div><em>›</em><div>{ic("report")}검수 · 사용 내역 공개</div></div>')
        opk_first = True
    else:
        opk_first = False
    opk = ('<div class="opk"><div><b>A</b>입주민<br>특화서비스</div><div><b>B</b>협의회<br>단지발전지원</div><div><b>C</b>단지지원<br>컨설팅</div></div>')
    if opk_first:  # 패키지안: 왼쪽 = A·B·C, 오른쪽 = 지정 흐름
        b = sub(k["body"], '</li></ul></div><div class="or">', '</li></ul>' + opk + '</div><div class="or">')
        k["body"] = sub(b, '</li></ul></div></div><div class="basex">', '</li></ul>' + opf + '</div></div><div class="basex">')
    else:
        b = sub(k["body"], '</li></ul></div><div class="or">', '</li></ul>' + opf + '</div><div class="or">')
        k["body"] = sub(b, '</li></ul></div></div><div class="basex">', '</li></ul>' + opk + '</div></div><div class="basex">')
    B.CSS += (".opf{margin-top:auto;display:flex;align-items:stretch;gap:4px}"
              ".opf div{flex:1;display:flex;flex-direction:column;align-items:center;gap:6px;border:1px solid rgba(255,255,255,.16);border-radius:12px;padding:12px 6px;background:#0f2237;font-size:14px;text-align:center;line-height:1.3}"
              ".opf .cic{margin:0;width:30px;height:30px}.opf em{display:flex;align-items:center;color:var(--gold);font-style:normal;font-weight:800;font-size:18px}"
              ".opk{margin-top:auto;display:grid;grid-template-columns:repeat(3,1fr);gap:10px}"
              ".opk div{border:1px solid rgba(235,203,143,.5);border-radius:12px;padding:12px 8px;background:rgba(13,30,51,.55);display:flex;flex-direction:column;align-items:center;gap:6px;text-align:center;font-size:14px;line-height:1.3}"
              ".opk b{width:38px;height:38px;border-radius:50%;background:var(--gold);color:#0d1e33;font-size:19px;font-weight:800;display:flex;align-items:center;justify-content:center}")

    # 핵심 혜택 6가지 — 앞 장들과 같은 아이콘을 오른쪽 위에(높이 영향 없음)
    k = take("탕정 푸르지오 센터파크에 드리는 [[핵심 혜택 6가지]]")[1]
    k["body"] = inject(k["body"], ["coins", "shield", "coin10", "lockdoc", "clock", "vault"], "tile").replace('class="tiles lg"', 'class="tiles lg c6"', 1)
    B.CSS += (".c6 .tile{position:relative}.c6 .tile>.cic{position:absolute;right:18px;top:16px;width:44px;height:44px;padding:10px;border-radius:12px;"
              "background:rgba(235,203,143,.09);border:1px solid rgba(235,203,143,.38);margin:0}")
