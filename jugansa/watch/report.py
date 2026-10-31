# 주관사 공고 감시 보고서 — 한 장(HTML · PNG) + 카톡 글 (본부장 10-31 '보고 양식을 만들어서 제대로')
# 사용: python report.py <data.json> [-o 저장폴더]   → report_YYYYMMDD_HHMM.html · .png
# data.json = {"at": "2026-10-31 11:00", "scope": {...}, "new": [...], "ongoing": [...], "ref": [...], "next": "14:00"}
#   new[i]  = {"site", "region", "posted", "cafe", "due", "due_date"(YYYY-MM-DD), "qna", "pt", "result", "mail", "how", "hh", "note", "link", "todo"}
#   ongoing = [{"site", "due", "status"}] · ref = [{"site", "note"}]
import html, json, sys, subprocess, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
E = lambda s: html.escape(str(s or ""))


def dday(d, today):
    if not d: return ""
    try: n = (datetime.date.fromisoformat(d) - today).days
    except ValueError: return ""
    return "마감" if n < 0 else "D-DAY" if n == 0 else f"D-{n}"


def build(data):
    at = datetime.datetime.strptime(data["at"], "%Y-%m-%d %H:%M"); today = at.date()
    sc = data.get("scope", {}); new = data.get("new", []); ong = data.get("ongoing", []); ref = data.get("ref", [])
    urgent = [n for n in new if dday(n.get("due_date"), today).startswith("D-") and int(dday(n.get("due_date"), today)[2:] or 99) <= 7]
    head = f"새 공고 <b>{len(new)}건</b>" + (f" · 마감 7일 이내 <b class='red'>{len(urgent)}건</b>" if urgent else "") if new else "새 공고 <b>없음</b>"
    cards = ""
    for i, n in enumerate(new, 1):
        dd = dday(n.get("due_date"), today)
        rows = [("서류 마감", n.get("due")), ("질의 마감", n.get("qna")), ("PT", n.get("pt")), ("결과", n.get("result")),
                ("접수", n.get("mail")), ("방법", n.get("how")), ("세대 · 입주", n.get("hh")), ("참고", n.get("note"))]
        rows = "".join(f"<tr><th>{E(k)}</th><td>{E(v)}</td></tr>" for k, v in rows if v)
        cards += (f"<div class='card'><div class='ct'><span class='no'>{i}</span><div class='nm'>{E(n['site'])}<small>{E(n.get('region'))}</small></div>"
                  + (f"<span class='dd {'red' if dd and dd != '마감' and int(dd[2:] or 99) <= 7 else ''}'>{E(dd)}</span>" if dd else "<span class='dd gray'>마감 확인 필요</span>")
                  + f"</div><div class='meta'>{E(n.get('posted'))} 게시 · {E(n.get('cafe'))}</div><table>{rows}</table>"
                  + (f"<div class='todo'>▶ {E(n['todo'])}</div>" if n.get("todo") else "")
                  + (f"<div class='lk'>{E(n['link'][:90])}…</div>" if n.get("link") else "") + "</div>")
    ong_rows = "".join(f"<tr><td class='b'>{E(o['site'])}</td><td>{E(o.get('due'))}</td><td>{E(o.get('status'))}</td></tr>" for o in ong)
    ref_rows = "".join(f"<li><b>{E(r['site'])}</b> — {E(r.get('note'))}</li>" for r in ref)
    scope = " · ".join(f"{k} {v}" for k, v in sc.items())
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;background:#eef1f5;font-family:"Malgun Gothic",sans-serif;color:#1b2433}}
.wrap{{width:760px;margin:0 auto;padding:22px 22px 26px;box-sizing:border-box}}
.hd{{background:linear-gradient(#1b2433,#2a3550);color:#fff;border-radius:16px;padding:18px 22px;border-bottom:3px solid #c9a45c}}
.hd .t{{font-size:24px;font-weight:800}} .hd .s{{color:#c9a45c;font-size:14px;margin-top:4px}}
.sum{{margin:14px 0;background:#fff;border-radius:14px;padding:14px 20px;font-size:21px;border-left:6px solid #2f9a5a}}
.sum.has{{border-left-color:#d8352e}} .red{{color:#d8352e}}
.sec{{font-size:17px;font-weight:800;margin:20px 4px 10px}}
.card{{background:#fff;border-radius:14px;padding:16px 18px;margin-bottom:12px;box-shadow:0 2px 6px rgba(0,0,0,.06)}}
.ct{{display:flex;align-items:center;gap:12px}} .no{{background:#1b2433;color:#ffe7a6;border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;font-weight:800}}
.nm{{flex:1;font-size:20px;font-weight:800}} .nm small{{display:block;font-size:13px;color:#7a8394;font-weight:400;margin-top:2px}}
.dd{{background:#2f6fd0;color:#fff;font-weight:800;border-radius:12px;padding:5px 12px;font-size:16px}} .dd.red{{background:#d8352e}} .dd.gray{{background:#8a909c;font-size:13px}}
.meta{{color:#7a8394;font-size:13px;margin:8px 0 6px}}
table{{width:100%;border-collapse:collapse;font-size:15px}} th{{width:96px;text-align:left;color:#5a6273;font-weight:700;padding:5px 0;vertical-align:top}} td{{padding:5px 0}}
.card tr+tr th,.card tr+tr td{{border-top:1px solid #eef0f3}}
.todo{{margin-top:10px;background:#fff6dc;border-radius:10px;padding:9px 12px;font-weight:700;color:#7a5410}}
.lk{{margin-top:8px;font-size:11px;color:#9aa0aa;word-break:break-all}}
.box{{background:#fff;border-radius:14px;padding:6px 18px}} .box td{{padding:8px 4px;border-top:1px solid #eef0f3;font-size:14px}} .box tr:first-child td{{border-top:0}} .b{{font-weight:800}}
ul{{margin:0;padding:12px 18px 12px 34px;background:#fff;border-radius:14px;font-size:14px;line-height:1.7}}
.ft{{margin-top:16px;color:#7a8394;font-size:13px;text-align:center}}
</style></head><body><div class="wrap">
<div class="hd"><div class="t">주관사 공고 감시 보고</div><div class="s">{E(at.strftime("%m.%d"))}({"월화수목금토일"[at.weekday()]}) {E(at.strftime("%H:%M"))} · 개척팀(공고 감시)</div></div>
<div class="sum {'has' if new else ''}">{head}</div>
{f'<div class="sec">🆕 새 공고</div>{cards}' if new else ''}
{f'<div class="sec">📌 우리가 진행 중인 단지 (목록에서 다시 확인됨)</div><div class="box"><table>{ong_rows}</table></div>' if ong else ''}
{f'<div class="sec">📎 참고</div><ul>{ref_rows}</ul>' if ref else ''}
<div class="ft">확인 범위: {E(scope)}{(' · 다음 확인 ' + E(data['next'])) if data.get('next') else ''}</div>
</div></body></html>'''


def kakao_text(data):
    at = data["at"]; new = data.get("new", []); today = datetime.datetime.strptime(at, "%Y-%m-%d %H:%M").date()
    lines = [f"[주관사 공고 감시] {at[5:].replace('-', '.')}", f"새 공고 {len(new)}건" if new else "새 공고 없음"]
    for i, n in enumerate(new, 1):
        lines += ["", f"{i}. {n['site']}" + (f" ({n['region']})" if n.get("region") else "") + f" {dday(n.get('due_date'), today)}".rstrip()]
        for k, key in (("마감", "due"), ("PT", "pt"), ("접수", "mail")):
            if n.get(key): lines.append(f" · {k}: {n[key]}")
        if n.get("todo"): lines.append(f" ▶ {n['todo']}")
    return "\n".join(lines)


def render(data, outdir):
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    stem = "report_" + data["at"].replace("-", "").replace(" ", "_").replace(":", "")
    hp = outdir / f"{stem}.html"; hp.write_text(build(data), encoding="utf-8")
    pp = outdir / f"{stem}.png"
    n = len(data.get("new", [])); h = 330 + n * 330 + len(data.get("ongoing", [])) * 42 + len(data.get("ref", [])) * 30 + 120
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2", f"--window-size=760,{h}",
                    f"--screenshot={pp}", hp.as_uri()], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return hp, pp


if __name__ == "__main__":
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = sys.argv[sys.argv.index("-o") + 1] if "-o" in sys.argv else HERE / "state"
    print(*render(data, out)); print(kakao_text(data))
