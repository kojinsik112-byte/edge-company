// 아크로 앱UI: 화면별 PNG + 바이어용 PDF 추출 (헤드리스 크롬)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const repo = path.join(__dirname, '..', '..');
const outDir = path.join(repo, 'acro', '앱UI_PNG');
fs.mkdirSync(outDir, { recursive: true });

const FULL = path.join(repo, 'acro', 'ACRO_앱UI_전체본.html');
const CN = path.join(repo, 'acro', 'ACRO_앱UI_한중_바이어용.html');
const LAUNDRY = path.join(repo, 'acro', 'ACRO_빨래건조대_앱UI_한중.html');

const NAMES = [
  '01_블루투스권한', '02_홈', '03_유선스위치', '04_전동커튼', '05_콘센트',
  '06_스마트조명', '07_방등', '08_전동블라인드', '09_실링팬조명', '10_욕실환기팬',
  '11_시나리오', '12_장치추가', '13_QR공유', '14_가족공유', '15_마이페이지',
  '16_빨래건조대',
];

const fileUrl = p => 'file:///' + p.replace(/\\/g, '/');

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 }, deviceScaleFactor: 2 });

  async function load(file, hideCaptions) {
    await page.goto(fileUrl(file), { waitUntil: 'networkidle', timeout: 60000 });
    await page.evaluate(() => document.fonts.ready);
    if (hideCaptions) {
      // 캡션·다운로드 버튼이 프레임 캡처 영역에 비치지 않게 숨김 (원본 미닫힘 div 탓에 일부 화면에서 겹침)
      await page.addStyleTag({ content: '.screen-comment,.frame-dl,.dl-toolbar{display:none!important}' });
    }
    await page.waitForTimeout(1200);
  }

  if (process.env.PDF_ONLY) {
    await exportPdfs();
    await browser.close();
    return;
  }

  // ① 전체본 화면별 PNG
  await load(FULL, true);
  const frames = (await page.$$('.screen-wrapper .phone-frame')).slice(0, NAMES.length);
  console.log('frames:', frames.length);
  for (let i = 0; i < frames.length; i++) {
    const nm = NAMES[i] || ('screen_' + (i + 1));
    await frames[i].scrollIntoViewIfNeeded();
    await frames[i].screenshot({ path: path.join(outDir, `ACRO_앱UI_${nm}.png`) });
    console.log('saved', nm);
  }

  await exportPdfs();

  async function exportPdfs() {
  // ③ 한중 바이어용 PDF (통짜 세로 1페이지 아님 — 화면 흐름대로 길게)
  await load(CN);
  await page.emulateMedia({ media: 'print' });
  const h = await page.evaluate(() => document.body.scrollHeight);
  await page.pdf({
    path: path.join(repo, 'acro', 'ACRO_앱UI_한중_바이어용.pdf'),
    printBackground: true, width: '1400px', height: Math.min(h + 60, 20000) + 'px',
    margin: { top: '20px', bottom: '20px', left: '20px', right: '20px' },
  });
  console.log('pdf saved, height', h);

  // ④ 빨래건조대 한중 PDF
  await load(LAUNDRY);
  await page.emulateMedia({ media: 'screen' });
  const h2 = await page.evaluate(() => document.body.scrollHeight);
  await page.pdf({
    path: path.join(repo, 'acro', 'ACRO_빨래건조대_앱UI_한중.pdf'),
    printBackground: true, width: '1400px', height: (h2 + 60) + 'px',
    margin: { top: '20px', bottom: '20px', left: '20px', right: '20px' },
  });
  console.log('laundry pdf saved');
  }

  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
