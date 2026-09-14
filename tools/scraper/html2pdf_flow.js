// 연속 문서(계약서 등) HTML → A4 PDF, 여백+페이지번호 자동 (사용: node html2pdf_flow.js <입력.html> <출력.pdf>)
const { chromium } = require('playwright');
const path = require('path');

const [src, out] = process.argv.slice(2);
if (!src || !out) { console.error('usage: node html2pdf_flow.js <src.html> <out.pdf>'); process.exit(1); }

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage();
  await page.goto('file:///' + path.resolve(src).replace(/\\/g, '/'), { waitUntil: 'networkidle', timeout: 60000 });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(500);
  await page.emulateMedia({ media: 'print' });
  await page.pdf({
    path: out, format: 'A4', printBackground: true,
    margin: { top: '30mm', bottom: '26mm', left: '0', right: '0' },
    displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate: '<div style="width:100%;text-align:center;font-size:9px;color:#888;font-family:sans-serif">- <span class="pageNumber"></span> -</div>',
  });
  console.log('pdf saved:', out);
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
