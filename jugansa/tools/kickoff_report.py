"""착수 보고서 PDF(인쇄용 · 5쪽 내외) — 내용 JSON 하나로 만든다. 어느 세션에서나 동작(경산 10-21본 서식 그대로).
사용: python3 jugansa/tools/kickoff_report.py 착수.json  → JSON의 out 경로에 .html · .pdf
JSON: {"title": "단지명", "eyebrow": "EDGE COMPANY · 입찰본부 착수 보고서 · 2026.10.21 · 내부용", "sub": "한 줄 요약",
       "footer": "단지명 · 착수 보고서 · 내부용", "out": "$SP/<약칭>/report/<약칭>_착수보고서_MMDD",
       "pages": [[{"h2": "1. 결론과 결정할 것", "sub": "검증 반영",
                   "blocks": [{"box": "경고 html"}, {"table": {"head": [..], "rows": [[..]], "widths": ["30%", null]}},
                              {"h3": "소제목"}, {"p": "html"}, {"note": "html"}, {"tip": "html"}]}], [...2쪽...]]}
글자는 html로 넣는다(<b> · <br> 허용). 보고서는 내부용 — 깃에 올리지 않는다(인계는 jugansa/착수/<약칭>.md)."""
import json, os, pathlib, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "매뉴얼"))
import build_manual as M  # CSS · 크롬 재사용
import pymupdf as fitz

PRINT = """
@page{margin:13mm 13mm 15mm}
body{font-size:9.2pt;line-height:1.45}
.blk{margin-bottom:4mm}.pb{page-break-after:always;height:0}
.ttl{border-bottom:2.5px solid #C9A24B;padding-bottom:3mm;margin-bottom:4mm}.ttl .eg{font-size:8.5pt;color:#9A7420;letter-spacing:.08em}
.ttl h1{font-size:19pt;margin:1mm 0;color:#0D1E33}.ttl p{margin:0;color:#4A5568;font-size:9pt}
h2{font-size:12.5pt;margin:0 0 2mm;padding-bottom:1.2mm;border-bottom:1.5px solid #C9A24B}h3{font-size:10pt;margin:3mm 0 1.5mm}
th{background:#EEF1F5!important;color:#0D1E33!important;border-bottom:1.5px solid #0D1E33;padding:1.2mm 1.8mm}td{padding:1.1mm 1.8mm}
tr:nth-child(even) td{background:none}table{font-size:8.4pt;margin:1mm 0 2.5mm}
.box{background:#fff!important;color:#1B2433!important;border:1.5px solid #B23A2E;padding:2.5mm 3.5mm}.box b{color:#B23A2E!important}
.tip{background:#fff;padding:2mm 3mm;font-size:8.6pt}.lead{margin:0 0 2mm;font-size:8.8pt}.note{font-size:8.2pt}
"""


def tbl(head, rows, widths=None):
    w = widths or [None] * len(head)
    th = "".join(("<th style='width:%s'>" % x if x else "<th>") + h + "</th>" for h, x in zip(head, w))
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table><tr>{th}</tr>{tr}</table>"


def block(b):
    if "table" in b:
        t = b["table"]
        return tbl(t["head"], t["rows"], t.get("widths"))
    if "box" in b: return f'<div class="box">{b["box"]}</div>'
    if "h3" in b: return f'<h3>{b["h3"]}</h3>'
    if "note" in b: return f'<p class="note">{b["note"]}</p>'
    if "tip" in b: return f'<div class="tip">{b["tip"]}</div>'
    if "p" in b: return f'<p class="lead">{b["p"]}</p>'
    raise ValueError(f"모르는 블록: {list(b)}")


def main(path):
    S = json.load(open(path, encoding="utf-8"))
    out = pathlib.Path(os.path.expandvars(S["out"]))
    out.parent.mkdir(parents=True, exist_ok=True)
    P = [f'<div class="ttl"><div class="eg">{S["eyebrow"]}</div><h1>{S["title"]}</h1><p>{S.get("sub", "")}</p></div>']
    for i, page in enumerate(S["pages"]):
        if i: P.append('<div class="pb"></div>')
        for s in page:
            body = "".join(block(b) for b in s["blocks"])
            P.append(f'<div class="blk"><h2>{s["h2"]}<small>{s.get("sub", "")}</small></h2>{body}</div>')
    doc = f"<!doctype html><html lang='ko'><head><meta charset='utf-8'><title>{S['title']} 착수 보고서</title><style>{M.CSS}{PRINT}</style></head><body>{''.join(P)}</body></html>"
    h = out.with_suffix(".html"); h.write_text(doc, encoding="utf-8")
    tmp = out.with_name(out.name + "_tmp.pdf")
    subprocess.run([M.chrome(), "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={tmp}", h.as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    d = fitz.open(tmp)
    for i, pg in enumerate(d):
        if i:
            r = pg.rect
            pg.insert_text((r.width - 30, r.height - 22), f"{i + 1} / {len(d)}", fontsize=7.5, color=(.5, .55, .62))
            pg.insert_text((42, r.height - 22), S.get("footer", S["title"] + " · 착수 보고서 · 내부용"), fontsize=7.5, fontname="korea", color=(.5, .55, .62))
    pdf = out.with_suffix(".pdf"); d.save(pdf, garbage=3, deflate=True); d.close(); tmp.unlink()
    print(pdf, len(fitz.open(pdf)), "쪽")


if __name__ == "__main__":
    main(sys.argv[1])
