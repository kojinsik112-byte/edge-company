const { chromium } = require('playwright');
(async () => {
  try {
    const b = await chromium.launch({ headless: false, channel: 'chrome' });
    const p = await b.newPage();
    await p.goto('https://example.com', { timeout: 20000 });
    console.log('HEADED OK:', await p.title());
    await b.close();
  } catch (e) { console.log('HEADED FAIL:', e.message.split('\n')[0]); }
})();
