# -*- coding: utf-8 -*-
"""네이티브 페이지 스펙 미리보기 — 스펙(JSON)을 실제 2-1과 같은 CSS로 렌더해 쪽별 PNG + 넘침 검사.

사용: python preview.py <spec.json> <출력폴더>
  spec.json = {"pages": [spec, ...]}  (pages21.json 한 그룹과 같은 모양, after/replaces 없어도 됨)
출력: <출력폴더>/page_1.png …, 표준출력에 넘침(overflow) 보고
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("NO_NATIVE", "1")
import build_dongtan as BD  # noqa: E402

PW = "/root/.npm/_npx/9833c18b2d85bc59/node_modules/playwright-core"
JS = r"""
const { chromium } = require(process.argv[2]);
(async () => {
  const [html, outdir] = process.argv.slice(3);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args:['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 1123, height: 794 }, deviceScaleFactor: 1.4 });
  await p.goto('file://' + html); await p.waitForTimeout(900);
  const pages = await p.$$('.page');
  for (let i = 0; i < pages.length; i++) await pages[i].screenshot({ path: outdir + '/page_' + (i + 1) + '.png' });
  const res = await p.evaluate(() => {
    const out = [];
    document.querySelectorAll('.page').forEach((pg, i) => {
      const pr = pg.getBoundingClientRect(); const issues = [];
      pg.querySelectorAll('.ct,.card,.tile,.row,.kp,.nb,.gal,.docs,.bulx,.flowx,.tbl,.splitx>div,.stackx').forEach(el => {
        if (el.scrollHeight > el.clientHeight + 2) issues.push('overflow ' + el.className + ' (' + el.scrollHeight + '>' + el.clientHeight + ')');
      });
      pg.querySelectorAll('*').forEach(el => { const r = el.getBoundingClientRect();
        if (r.width && (r.bottom > pr.bottom + 1 || r.right > pr.right + 1)) issues.push('OUT ' + el.tagName + '.' + el.className); });
      pg.querySelectorAll('img').forEach(im => { if (!im.complete || !im.naturalWidth) issues.push('MISSING IMG ' + im.getAttribute('src')); });
      out.push('page ' + (i + 1) + ': ' + (issues.length ? [...new Set(issues)].slice(0, 8).join(' | ') : 'OK'));
    });
    return out;
  });
  console.log(res.join('\n')); await b.close();
})();
"""


def main():
    spec_path, outdir = sys.argv[1], os.path.abspath(sys.argv[2])
    os.makedirs(outdir, exist_ok=True)
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)
    pages = spec["pages"] if isinstance(spec, dict) else spec
    html_pages = []
    for n, sp in enumerate(pages, 1):
        sp = dict(sp)
        sp.setdefault("sec", "00. 미리보기")
        k, kw = BD.native_page(sp)
        html_pages.append(BD.B.render_std(n, kw["sec"], kw["title"], kw.get("lead"), kw["body"], kw.get("kp")))
    doc = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>{BD.B.CSS}</style></head><body>{''.join(html_pages)}</body></html>"""
    doc = doc.replace("<span>주식회사 엣지컴퍼니 · 대표이사 고진식</span>", "<span>주식회사 엣지컴퍼니</span>")
    doc = BD.term(doc).replace("지역업체", "인근 지역업체").replace("인근 인근", "인근")
    doc = doc.replace("url(assets/", "url(../요약제안서/assets/").replace('src="assets/', 'src="../요약제안서/assets/')
    doc = doc.replace("</body>", BD.ALIGN_JS + "</body>")
    html = os.path.join(HERE, f".preview_{os.getpid()}.html")
    with open(html, "w", encoding="utf-8") as f:
        f.write(doc)
    js = os.path.join(outdir, "_shot.js")
    with open(js, "w") as f:
        f.write(JS)
    try:
        r = subprocess.run(["node", js, PW, html, outdir], capture_output=True, text=True, timeout=120)
        print(r.stdout.strip() or r.stderr.strip())
    finally:
        os.remove(html)
    print(f"PNG → {outdir}/page_N.png")


if __name__ == "__main__":
    main()
