// 시험판(127.0.0.1:8091)을 휴대폰 크기로 열어 PT용 화면을 찍는다.
// 사용: node pt_shots.js <저장 폴더> [demo | demo2]   (시연_시작.bat으로 시험판을 먼저 켜 둘 것)
//   demo  = 접수 방식 ① 업체 먼저: 1 첫 화면 · 2 업체 연락처 · 3 요청 · 4 진행 확인 · 5 업체 화면 · 6 해결 확인
//   demo2 = 접수 방식 ② 주관사 한 창구: 1 첫 화면 · 2 접수(품목 · 업체) · 3 접수(내용 · 사진) · 4 진행 확인 · 5 업체 화면 · 6 해결 확인(해피콜 대기) · 7 관리 화면 해피콜
const path = require('path'), fs = require('fs');
const { chromium } = require(path.join('C:/본부장/Claude_Code/edge-company/tools/scraper/node_modules/playwright'));
const OUT = process.argv[2], CODE = process.argv[3] || 'demo', CENTER = CODE === 'demo2', B = 'http://127.0.0.1:8091';
fs.mkdirSync(OUT, { recursive: true });

(async () => {
  const b = await chromium.launch({ headless: true, channel: 'chrome' });
  // 시연용 요청 목록에서 이 단지 링크(토큰) 읽기
  const pc = await b.newPage();
  await pc.goto(B + '/demo.php');
  const rows = (await pc.$$eval('table.dm tbody tr', trs => trs.map(tr => {
    const a = [...tr.querySelectorAll('a')].map(x => x.getAttribute('href'));
    return { no: tr.children[0].innerText, st: tr.children[3].innerText, ven: a.find(h => h.startsWith('v.php')), res: a.find(h => h.includes('k=')) };
  }))).filter(r => r.res && r.res.includes('d=' + CODE + '&'));
  await pc.close();
  const pick = (st) => rows.find(r => r.st.includes(st));

  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true, colorScheme: 'light', locale: 'ko-KR' });
  const p = await ctx.newPage();
  const shot = async (name) => { await p.waitForTimeout(400); await p.screenshot({ path: path.join(OUT, name) }); console.log('찍음', name); };
  const top = async (sel, off = 12) => { await p.evaluate(([s, o]) => { const e = document.querySelector(s); window.scrollTo(0, e.getBoundingClientRect().top + scrollY - o); }, [sel, off]); };

  // ① 첫 화면(안내문 QR로 들어옴)
  await p.goto(B + '/?d=' + CODE, { waitUntil: 'networkidle' });
  await p.evaluate(() => window.scrollTo(0, 0));
  await shot('1_첫화면.png');
  if (!CENTER) {
    // ② 업체 연락처 → ③ '이 업체로 요청' → 2단계 업체 연락 여부
    await top('#vgrid', 16); await shot('2_업체연락처.png');
    await p.click('#vgrid button[data-id]');
    await p.click('#next');
    await p.click('#vc button');
    await top('nav.tabs', 16); await shot('3_요청하기.png');
  } else {
    // ② 바로 접수: 품목 · 계약 업체 고르기 → ③ 내용 · 사진 · 방문 시간
    await p.selectOption('#item', '중문');
    await p.click('#vend button');
    await top('nav.tabs', 16); await shot('2_접수하기.png');
    await p.click('#next');
    await p.fill('#body', '중문 손잡이가 헐거워졌어요. 문을 닫을 때 덜컹거려요.');
    await top('nav.tabs', 16); await shot('3_내용사진.png');
  }
  // ④ 진행 확인: 기한 시계 · 단계
  await p.goto(B + '/' + pick('1차 회신').res, { waitUntil: 'networkidle' });
  await p.waitForSelector('#ckList .item');
  await top('#ckList .item', 16); await shot('4_진행확인.png');
  // ⑤ 업체 화면(문자 링크 하나)
  await p.goto(B + '/' + pick('접수').ven, { waitUntil: 'networkidle' });
  await p.waitForSelector('#vCard .item');
  await shot('5_업체화면.png');
  // ⑥ 처리 완료 뒤 입주민 화면(① '해결됐어요' / ② 해피콜 안내 + 보조 '해결됐어요')
  await p.goto(B + '/' + pick(CENTER ? '해피콜 대기' : '입주민 확인 대기').res, { waitUntil: 'networkidle' });
  await p.waitForSelector('#ckList .confirm');
  await top('#ckList ul.tl', 16); await shot('6_해결확인.png');

  if (CENTER) {
    // ⑦ 관리 화면(PC): 해피콜 대기 건 자세히 → '해피콜 완료 · 마감'
    const pcx = await b.newContext({ viewport: { width: 1280, height: 860 }, deviceScaleFactor: 2, colorScheme: 'light', locale: 'ko-KR' });
    const a = await pcx.newPage();
    await a.goto(B + '/admin.php', { waitUntil: 'networkidle' });
    await a.fill('#lId', 'admin'); await a.fill('#lPw', 'admin'); await a.click('#login button[type=submit]');
    await a.waitForSelector('#admBody tr');
    const no = pick('해피콜 대기').no;
    await a.evaluate((n) => { location.hash = n; }, no);
    await a.reload({ waitUntil: 'networkidle' });
    await a.waitForSelector('#adDetail [data-a="happy"]');
    await a.evaluate(() => { const e = document.querySelector('#adDetail'); window.scrollTo(0, e.getBoundingClientRect().top + scrollY - 12); });
    await a.waitForTimeout(500);
    await a.screenshot({ path: path.join(OUT, '7_관리_해피콜.png') }); console.log('찍음 7_관리_해피콜.png');
    await pcx.close();
  }
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
