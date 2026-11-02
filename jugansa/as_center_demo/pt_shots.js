// 시험판(127.0.0.1:8091)을 휴대폰 크기로 열어 PT용 화면 5장을 찍는다.
// 사용: node pt_shots.js <저장 폴더>   (시연_시작.bat으로 시험판을 먼저 켜 둘 것)
const path = require('path'), fs = require('fs');
const { chromium } = require(path.join('C:/본부장/Claude_Code/edge-company/tools/scraper/node_modules/playwright'));
const OUT = process.argv[2]; const B = 'http://127.0.0.1:8091';
fs.mkdirSync(OUT, { recursive: true });

(async () => {
  const b = await chromium.launch({ headless: true, channel: 'chrome' });
  // 시연용 요청 목록에서 링크(토큰) 읽기
  const pc = await b.newPage();
  await pc.goto(B + '/demo.php');
  const rows = await pc.$$eval('table.dm tbody tr', trs => trs.map(tr => {
    const a = [...tr.querySelectorAll('a')].map(x => x.getAttribute('href'));
    return { item: tr.children[2].innerText, st: tr.children[3].innerText, ven: a.find(h => h.startsWith('v.php')), res: a.find(h => h.includes('k=')) };
  }));
  await pc.close();
  const pick = (st) => rows.find(r => r.st.includes(st));

  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true, colorScheme: 'light', locale: 'ko-KR' });
  const p = await ctx.newPage();
  const shot = async (name) => { await p.waitForTimeout(400); await p.screenshot({ path: path.join(OUT, name) }); console.log('찍음', name); };
  const top = async (sel, off = 12) => { await p.evaluate(([s, o]) => { const e = document.querySelector(s); window.scrollTo(0, e.getBoundingClientRect().top + scrollY - o); }, [sel, off]); };

  // ① 첫 화면(안내문 QR로 들어옴)
  await p.goto(B + '/?d=demo', { waitUntil: 'networkidle' });
  await shot('1_첫화면.png');
  // ② 업체 연락처
  await top('#vgrid', 16); await shot('2_업체연락처.png');
  // ③ 주관사에 요청: '이 업체로 요청' → 1단계(품목 · 업체 골라 둠) → 2단계 업체 연락 여부
  await p.click('#vgrid button[data-id]');
  await p.click('#next');
  await p.click('#vc button');
  await top('nav.tabs', 16); await shot('3_요청하기.png');
  // ④ 진행 확인: 기한 시계 · 단계
  await p.goto(B + '/' + pick('1차 회신').res, { waitUntil: 'networkidle' });
  await p.waitForSelector('#ckList .item');
  await top('#ckList .item', 16); await shot('4_진행확인.png');
  // ⑤ 업체 화면(문자 링크 하나)
  await p.goto(B + '/' + pick('접수').ven, { waitUntil: 'networkidle' });
  await p.waitForSelector('#vCard .item');
  await shot('5_업체화면.png');
  // 덤: 처리 완료 뒤 입주민 '해결됐어요'
  await p.goto(B + '/' + pick('입주민 확인 대기').res, { waitUntil: 'networkidle' });
  await p.waitForSelector('#ckList .confirm');
  await top('#ckList ul.tl', 16); await shot('6_해결확인.png');
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
