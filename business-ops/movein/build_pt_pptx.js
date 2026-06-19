// 일광노르웨이숲 주관사 PT — 텍스트/배경/타이포 전용 생성기 (이미지 제외, 회장이 추가)
const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.333, height: 7.5 });
p.layout = "W";

const NAVY = "0E1830", GOLD = "C9A961", WHITE = "FFFFFF";
const INK = "1A2235", MUTE = "6B7385", LINE = "E3E6EC", SOFT = "F4F6F9";
const F = "맑은 고딕"; // 안 맞으면 Pretendard로 교체

const W = 13.333, H = 7.5, MX = 0.9;

// 이미지 자리 표시(연한 박스 + 안내문구) — 실제 그림 X
function imgZone(s, x, y, w, h, label) {
  s.addShape(p.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.06, fill: { color: SOFT }, line: { color: LINE, width: 1, dashType: "dash" } });
  s.addText("□  " + (label || "이미지 영역 (직접 추가)"), { x, y, w, h, align: "center", valign: "middle", fontFace: F, fontSize: 12, color: MUTE });
}
function pageNum(s, n) {
  s.addText(String(n).padStart(2, "0"), { x: W - 1.0, y: H - 0.5, w: 0.7, h: 0.3, align: "right", fontFace: F, fontSize: 9, color: MUTE });
  s.addText("ARCO · 엣지컴퍼니", { x: MX, y: H - 0.5, w: 4, h: 0.3, fontFace: F, fontSize: 9, color: MUTE });
}
// 본문(흰 배경) 헤더: 골드 라벨 + 네이비 제목
function head(s, label, title) {
  if (label) s.addText(label, { x: MX, y: 0.6, w: 8, h: 0.35, fontFace: F, fontSize: 13, bold: true, color: GOLD, charSpacing: 2 });
  s.addText(title, { x: MX, y: label ? 0.95 : 0.7, w: W - MX * 2, h: 1.0, fontFace: F, fontSize: 30, bold: true, color: NAVY });
}
function content(bg) { const s = p.addSlide(); s.background = { color: bg || WHITE }; return s; }

/* ===== S1 표지 ===== */
(() => {
  const s = content(NAVY);
  s.addShape(p.ShapeType.rect, { x: 0, y: H - 0.18, w: W, h: 0.18, fill: { color: GOLD } });
  s.addText("입주박람회 주관사 제안", { x: MX, y: 2.5, w: 11, h: 0.5, fontFace: F, fontSize: 18, color: GOLD, charSpacing: 3 });
  s.addText("일광노르웨이숲오션포레", { x: MX, y: 3.0, w: 11.5, h: 1.4, fontFace: F, fontSize: 54, bold: true, color: WHITE });
  s.addText("㈜엣지컴퍼니   |   대표 고진식   |   2026. 6. 14", { x: MX, y: 4.6, w: 11, h: 0.5, fontFace: F, fontSize: 16, color: "C9CEDA" });
  s.addText("LOOK · 보다  ·  끝까지 책임지는 운영사", { x: MX, y: H - 1.0, w: 8, h: 0.4, fontFace: F, fontSize: 12, italic: true, color: GOLD });
})();

/* ===== S2 부산 대표 ===== */
(() => {
  const s = content();
  head(s, "ABOUT", "부산을 대표하는 입주 주관사");
  const cards = [
    ["70%+", "2024·2025 부산\n입주물량 주관"],
    ["13단지 · 22,065세대", "전부 1,000세대 이상\n대단지만 운영"],
    ["부산 · 경남", "본사 울산\n현장까지 차로 20분"],
  ];
  const cw = 3.5, gap = 0.45, x0 = MX, y0 = 2.5, ch = 3.0;
  cards.forEach((c, i) => {
    const x = x0 + i * (cw + gap);
    s.addShape(p.ShapeType.roundRect, { x, y: y0, w: cw, h: ch, rectRadius: 0.08, fill: { color: SOFT }, line: { color: LINE, width: 1 } });
    s.addShape(p.ShapeType.rect, { x, y: y0, w: cw, h: 0.1, fill: { color: GOLD } });
    s.addText(c[0], { x: x + 0.2, y: y0 + 0.6, w: cw - 0.4, h: 1.0, align: "center", fontFace: F, fontSize: 26, bold: true, color: NAVY });
    s.addText(c[1], { x: x + 0.2, y: y0 + 1.7, w: cw - 0.4, h: 1.1, align: "center", fontFace: F, fontSize: 14, color: MUTE });
  });
  pageNum(s, 2);
})();

/* ===== S3 대표·자격 ===== */
(() => {
  const s = content();
  head(s, "CEO", "사람 덕분에, 여기까지 왔습니다");
  imgZone(s, MX, 2.4, 4.2, 4.0, "대표 사진 · 저서 표지");
  const rx = 5.6, rw = W - rx - MX;
  s.addText([
    { text: "대표 고진식", options: { fontSize: 20, bold: true, color: NAVY, breakLine: true } },
    { text: "온산 대한유화 10년 근무 후 창업\n저서 『사람 덕분에 여기까지 왔습니다』", options: { fontSize: 14, color: MUTE, breakLine: true } },
  ], { x: rx, y: 2.5, w: rw, h: 1.4, fontFace: F, valign: "top", lineSpacingMultiple: 1.2 });
  s.addShape(p.ShapeType.line, { x: rx, y: 4.0, w: rw, h: 0, line: { color: LINE, width: 1 } });
  s.addText([
    { text: "서류로 증명하는 신뢰", options: { fontSize: 15, bold: true, color: GOLD, breakLine: true } },
    { text: "· 건설업 · 전기공사업 · 소방시설업 면허\n· ISO 9001 · 14001 · 45001 국제인증\n· 삼성전자 업무협약(MOU)", options: { fontSize: 15, color: INK } },
  ], { x: rx, y: 4.2, w: rw, h: 2.0, fontFace: F, valign: "top", lineSpacingMultiple: 1.35 });
  pageNum(s, 3);
})();

/* ===== S4 4박자 ===== */
(() => {
  const s = content();
  head(s, "WHY EDGE", "동시에 갖기 어려운 네 가지");
  const items = [
    ["01  자체 전기공사 면허", "업체 연결만이 아니라 직접 시공·A/S"],
    ["02  물리적 사무실", "현장 20분 · 60평 사옥(회의실·86\" 전자칠판) 협의회 무료대여"],
    ["03  소유 채널", "유튜브 · 네이버 카페 · 입주민 앱"],
    ["04  트랙레코드", "13개 단지 · 22,065세대 운영 경험"],
  ];
  const cw = 5.6, ch = 1.5, gx = 0.5, gy = 0.4, x0 = MX, y0 = 2.3;
  items.forEach((it, i) => {
    const x = x0 + (i % 2) * (cw + gx), y = y0 + Math.floor(i / 2) * (ch + gy);
    s.addShape(p.ShapeType.roundRect, { x, y, w: cw, h: ch, rectRadius: 0.06, fill: { color: SOFT }, line: { color: LINE, width: 1 } });
    s.addShape(p.ShapeType.rect, { x, y, w: 0.1, h: ch, fill: { color: GOLD } });
    s.addText(it[0], { x: x + 0.35, y: y + 0.25, w: cw - 0.6, h: 0.5, fontFace: F, fontSize: 17, bold: true, color: NAVY });
    s.addText(it[1], { x: x + 0.35, y: y + 0.8, w: cw - 0.6, h: 0.5, fontFace: F, fontSize: 13, color: MUTE });
  });
  s.addShape(p.ShapeType.roundRect, { x: MX, y: 6.4, w: W - MX * 2, h: 0.6, rectRadius: 0.05, fill: { color: NAVY } });
  s.addText("이 네 가지를 동시에 가진 주관사, 부산에 저희뿐입니다.", { x: MX, y: 6.4, w: W - MX * 2, h: 0.6, align: "center", valign: "middle", fontFace: F, fontSize: 15, bold: true, color: GOLD });
  pageNum(s, 4);
})();

/* ===== S5 리조트+유리난간 ===== */
(() => {
  const s = content();
  head(s, "FIT", "이 단지를 완성하는 마지막 한 조각");
  s.addText([
    { text: "삼성물산 에버랜드 조경 1만 평  ·  노르딕하우스  ·  거대 폰드  ·  오션뷰", options: { fontSize: 15, color: INK, breakLine: true } },
    { text: "부산에서 보기 드문 리조트형 단지", options: { fontSize: 13, color: MUTE } },
  ], { x: MX, y: 2.3, w: W - MX * 2, h: 1.0, fontFace: F, lineSpacingMultiple: 1.3 });
  imgZone(s, MX, 3.4, W - MX * 2, 2.4, "유리난간 비포 → 애프터 비교 이미지");
  s.addShape(p.ShapeType.roundRect, { x: MX, y: 6.05, w: W - MX * 2, h: 0.75, rectRadius: 0.05, fill: { color: SOFT }, line: { color: GOLD, width: 1.5 } });
  s.addText("여기에 ‘유리난간’ 하나만 더해지면 — 부산 최고가 되겠다.", { x: MX, y: 6.05, w: W - MX * 2, h: 0.75, align: "center", valign: "middle", fontFace: F, fontSize: 17, bold: true, color: NAVY });
  pageNum(s, 5);
})();

/* ===== S6 왜 못하나 ===== */
(() => {
  const s = content();
  head(s, "BARRIER", "다들 말합니다. 그런데 왜 못 할까요?");
  const bars = [
    ["동의", "동(棟)별 입주민\n2/3 이상 동의"],
    ["인허가", "구조 안전검토 +\n구청 신고 · 인허가"],
    ["안전기준", "높이 90cm · 하중 100kg\n접합유리 8+8"],
  ];
  const cw = 3.5, gap = 0.45, x0 = MX, y0 = 2.4, ch = 2.7;
  bars.forEach((b, i) => {
    const x = x0 + i * (cw + gap);
    s.addShape(p.ShapeType.roundRect, { x, y: y0, w: cw, h: ch, rectRadius: 0.08, fill: { color: SOFT }, line: { color: LINE, width: 1 } });
    s.addText(b[0], { x, y: y0 + 0.45, w: cw, h: 0.6, align: "center", fontFace: F, fontSize: 20, bold: true, color: MUTE });
    s.addText(b[1], { x: x + 0.2, y: y0 + 1.3, w: cw - 0.4, h: 1.1, align: "center", fontFace: F, fontSize: 14, color: INK });
  });
  s.addText("까다로워서 — 다들 ‘하겠다’ 말만 하고, 실제로는 못 합니다.", { x: MX, y: 5.7, w: W - MX * 2, h: 0.6, align: "center", fontFace: F, fontSize: 16, bold: true, color: NAVY });
  pageNum(s, 6);
})();

/* ===== S7 우리는 뚫었다 ===== */
(() => {
  const s = content();
  head(s, "FIRST IN BUSAN", "부산에서 실제로 해낸 건, 엣지컴퍼니가 처음입니다");
  imgZone(s, MX, 2.5, 5.2, 3.7, "푸르지오린 유리난간 실사진");
  const rx = 6.6, rw = W - rx - MX;
  s.addText([
    { text: "에코델타시티 푸르지오린 (886세대)", options: { fontSize: 16, bold: true, color: NAVY, breakLine: true } },
    { text: "테스트 3세대 → ", options: { fontSize: 15, color: INK } },
    { text: "120세대 공동구매 완료", options: { fontSize: 15, bold: true, color: GOLD, breakLine: true } },
  ], { x: rx, y: 2.5, w: rw, h: 1.2, fontFace: F, valign: "top", lineSpacingMultiple: 1.3 });
  s.addText([
    { text: "다음 — 자이 · 이편한세상 · 대성베르힐 · 디에트르\n(이제 준비 중 = 우리를 뒤따름)", options: { color: MUTE, breakLine: true } },
    { text: "\n유리난간 공동구매 부산 첫 = 엣지\n이 단지 시행사도 같은 공동구매 검토 中", options: { color: INK } },
  ], { x: rx, y: 3.9, w: rw, h: 2.4, fontFace: F, fontSize: 14, valign: "top", lineSpacingMultiple: 1.35 });
  pageNum(s, 7);
})();

/* ===== S8 단지 공감 (절제) ===== */
(() => {
  const s = content();
  head(s, "EMPATHY", "이 단지를, 그리고 지금 이 상황을 — 저희는 압니다");
  s.addText("1,294세대 평형별 맞춤 운영  ·  노르딕 무드 연계", { x: MX, y: 2.3, w: W - MX * 2, h: 0.5, fontFace: F, fontSize: 15, color: MUTE });
  const pr = [
    "필요한 정보는 투명하게 정리해 공유하겠습니다",
    "협의회와 함께, 입주민 편에서 도울 수 있는 일이라면 끝까지",
    "저희가 책임지는 시공 · 하자 · A/S는, 어떤 일이 있어도 확실하게",
  ];
  pr.forEach((t, i) => {
    const y = 3.2 + i * 0.95;
    s.addShape(p.ShapeType.roundRect, { x: MX, y, w: W - MX * 2, h: 0.75, rectRadius: 0.05, fill: { color: SOFT } });
    s.addText(String(i + 1), { x: MX + 0.25, y, w: 0.6, h: 0.75, align: "center", valign: "middle", fontFace: F, fontSize: 20, bold: true, color: GOLD });
    s.addText(t, { x: MX + 1.0, y, w: W - MX * 2 - 1.3, h: 0.75, valign: "middle", fontFace: F, fontSize: 15, color: INK });
  });
  s.addText("‘입주민 편에 서는 주관사’ — 말이 아니라, 그렇게 보여드리겠습니다.", { x: MX, y: 6.3, w: W - MX * 2, h: 0.5, fontFace: F, fontSize: 14, italic: true, color: NAVY });
  pageNum(s, 8);
})();

/* ===== S9 83만 패키지 ===== */
(() => {
  const s = content();
  head(s, "BENEFIT", "입장만 하면 카운트 — 83만원 상당, 신청·계약 NO");
  s.addText("입주박람회 입장(체크인)만 해도 카운트  ·  정회원/준회원 구분 없이 전 세대 동일", { x: MX, y: 1.95, w: W - MX * 2, h: 0.4, fontFace: F, fontSize: 13, color: GOLD });
  const items = [["전동커튼", "28만"], ["간접조명", "20만"], ["거실 미세방충망", "20만"], ["박람회 상품권", "15만"]];
  const cw = 2.75, gap = 0.22, x0 = MX, y0 = 2.5, ch = 1.45;
  items.forEach((it, i) => {
    const x = x0 + i * (cw + gap);
    s.addShape(p.ShapeType.roundRect, { x, y: y0, w: cw, h: ch, rectRadius: 0.06, fill: { color: SOFT }, line: { color: LINE, width: 1 } });
    s.addText(it[0], { x: x + 0.1, y: y0 + 0.28, w: cw - 0.2, h: 0.55, align: "center", fontFace: F, fontSize: 14, color: INK });
    s.addText(it[1], { x: x + 0.1, y: y0 + 0.82, w: cw - 0.2, h: 0.5, align: "center", fontFace: F, fontSize: 18, bold: true, color: GOLD });
  });
  s.addText([
    { text: "소계 약 83만원 상당", options: { fontSize: 18, bold: true, color: NAVY } },
    { text: "    +  화재보험 무료  ·  조건 없음(계약 불필요)", options: { fontSize: 13, color: MUTE } },
  ], { x: MX, y: 4.2, w: W - MX * 2, h: 0.5, fontFace: F });
  s.addShape(p.ShapeType.roundRect, { x: MX, y: 4.85, w: W - MX * 2, h: 1.95, rectRadius: 0.06, fill: { color: NAVY } });
  s.addText([
    { text: "＋ 전 세대 추가 무상\n", options: { fontSize: 13, bold: true, color: GOLD } },
    { text: "드론촬영 · 점등식 행사 · 온라인 카페 이벤트\n공용부 실링팬+간접조명 3개소 무료시공(호텔 로비풍) · 세스코 세균소독 무료\n하자점검 — 전국 1위 ‘우리홈’(공용부 무료 / 세대 단지특가) · 바디프랜드 포함 대규모 경품\n유리난간 공동구매 — 부산 첫 공동구매 진행 사례", options: { fontSize: 13, color: WHITE } },
  ], { x: MX + 0.4, y: 4.95, w: W - MX * 2 - 0.8, h: 1.75, fontFace: F, valign: "top", lineSpacingMultiple: 1.25 });
  pageNum(s, 9);
})();

/* ===== S10 온라인특가·부스·운영 ===== */
(() => {
  const s = content();
  head(s, "PLUS", "온라인 특가 · 부스 지원 · 운영 약속");
  s.addShape(p.ShapeType.roundRect, { x: MX, y: 2.4, w: 5.6, h: 2.3, rectRadius: 0.06, fill: { color: SOFT }, line: { color: LINE, width: 1 } });
  s.addShape(p.ShapeType.rect, { x: MX, y: 2.4, w: 5.6, h: 0.55, fill: { color: NAVY } });
  s.addText("온라인 특가 (원가·특가)", { x: MX, y: 2.4, w: 5.6, h: 0.55, align: "center", valign: "middle", fontFace: F, fontSize: 15, bold: true, color: GOLD });
  s.addText([
    { text: "실링팬  30만원대 → 10만원대 원가\n", options: { fontSize: 15, bold: true, color: NAVY } },
    { text: "네이버 스토어 5위권 상품\n\n", options: { fontSize: 12, color: MUTE } },
    { text: "휴젠트  인터넷가 77만 → 우리 49만\n", options: { fontSize: 15, bold: true, color: NAVY } },
    { text: "에코델타시티 누적 1,400대 판매", options: { fontSize: 12, color: MUTE } },
  ], { x: MX + 0.35, y: 3.15, w: 5.0, h: 1.4, fontFace: F, valign: "top", lineSpacingMultiple: 1.1 });
  const rx = 6.6, rw = W - rx - MX;
  s.addShape(p.ShapeType.roundRect, { x: rx, y: 2.4, w: rw, h: 2.3, rectRadius: 0.06, fill: { color: SOFT }, line: { color: LINE, width: 1 } });
  s.addShape(p.ShapeType.rect, { x: rx, y: 2.4, w: rw, h: 0.55, fill: { color: NAVY } });
  s.addText("박람회장 부스 지원", { x: rx, y: 2.4, w: rw, h: 0.55, align: "center", valign: "middle", fontFace: F, fontSize: 15, bold: true, color: GOLD });
  s.addText([
    { text: "· 말굽 서비스\n", options: {} },
    { text: "· 안방 화장대 무료 코팅\n\n", options: {} },
    { text: "※ 입주청소·새집증후군 등은\n   박람회 참여 업체 부스 운영", options: { color: MUTE, fontSize: 12 } },
  ], { x: rx + 0.35, y: 3.15, w: rw - 0.6, h: 1.4, fontFace: F, fontSize: 15, color: INK, valign: "top", lineSpacingMultiple: 1.15 });
  s.addShape(p.ShapeType.roundRect, { x: MX, y: 5.0, w: W - MX * 2, h: 1.3, rectRadius: 0.06, fill: { color: NAVY } });
  s.addText("＋ 운영 약속", { x: MX + 0.4, y: 5.15, w: 4, h: 0.4, fontFace: F, fontSize: 14, bold: true, color: GOLD });
  s.addText("시공 100% 보장제(입주일 넘기면 하루 5만원) · 10년 무상 A/S · 단지 내 베이스캠프 1개월 · 혜택→입주민 지원금 전환", { x: MX + 0.4, y: 5.55, w: W - MX * 2 - 0.8, h: 0.6, fontFace: F, fontSize: 14, color: WHITE });
  pageNum(s, 10);
})();

/* ===== S11 업체선정 ===== */
(() => {
  const s = content();
  head(s, "CORE", "주관사의 본질은 ‘업체 선정’입니다");
  s.addText("1년 뒤 하자 났을 때 — 그 업체가 부산에 있느냐, 서울이냐, 사라졌느냐.\n그게 입주민의 삶을 가릅니다.", { x: MX, y: 2.3, w: W - MX * 2, h: 1.0, fontFace: F, fontSize: 15, color: INK, lineSpacingMultiple: 1.3 });
  s.addShape(p.ShapeType.roundRect, { x: MX, y: 3.6, w: W - MX * 2, h: 1.1, rectRadius: 0.06, fill: { color: SOFT }, line: { color: LINE, width: 1 } });
  s.addText("부산 · 경남 지역업체 100% 구성", { x: MX, y: 3.7, w: W - MX * 2, h: 0.6, align: "center", fontFace: F, fontSize: 22, bold: true, color: NAVY });
  s.addText("멀리서 와 빠지는 외주가 아니라, 차로 닿는 거리에서 끝까지 책임지는 지역업체로만", { x: MX, y: 4.25, w: W - MX * 2, h: 0.4, align: "center", fontFace: F, fontSize: 13, color: MUTE });
  s.addShape(p.ShapeType.roundRect, { x: MX, y: 5.0, w: W - MX * 2, h: 1.2, rectRadius: 0.06, fill: { color: NAVY } });
  s.addText([
    { text: "못 지키면 — 입주주관사 자격 철회 동의서 작성\n", options: { fontSize: 19, bold: true, color: GOLD } },
    { text: "스스로 배수의 진을 치고 시작합니다", options: { fontSize: 14, color: "C9CEDA" } },
  ], { x: MX, y: 5.0, w: W - MX * 2, h: 1.2, align: "center", valign: "middle", fontFace: F, lineSpacingMultiple: 1.2 });
  pageNum(s, 11);
})();

/* ===== S12 안전망① (네이비 클라이맥스) ===== */
(() => {
  const s = content(NAVY);
  s.addText("CLIMAX", { x: MX, y: 0.6, w: 8, h: 0.35, fontFace: F, fontSize: 13, bold: true, color: GOLD, charSpacing: 2 });
  s.addText("예치금은 누구나 말합니다. 우리는 다릅니다.", { x: MX, y: 0.95, w: W - MX * 2, h: 0.9, fontFace: F, fontSize: 30, bold: true, color: WHITE });
  const rows = [
    [{ text: "", options: {} }, { text: "다른 주관사", options: { color: "AAB0BE", bold: true } }, { text: "엣지컴퍼니", options: { color: GOLD, bold: true } }],
    [{ text: "누구 돈?", options: { bold: true, color: WHITE } }, { text: "업체에게 받은 돈", options: { color: "AAB0BE" } }, { text: "순수 자산 현금 1억", options: { color: WHITE, bold: true } }],
    [{ text: "어느 통장?", options: { bold: true, color: WHITE } }, { text: "법무법인 통장", options: { color: "AAB0BE" } }, { text: "협의회 + 주관사 공동통장", options: { color: WHITE, bold: true } }],
    [{ text: "집행 속도?", options: { bold: true, color: WHITE } }, { text: "송달 1주 ~ 10일", options: { color: "AAB0BE" } }, { text: "즉시 (협의회 단독집행)", options: { color: WHITE, bold: true } }],
  ];
  s.addTable(rows, { x: MX, y: 2.4, w: W - MX * 2, rowH: 0.85, fontFace: F, fontSize: 16, valign: "middle", align: "center", border: { type: "solid", color: "2A3550", pt: 1 }, fill: { color: "16203A" } });
  s.addText("다른 곳은 ‘믿어달라’ — 저희는 우리 돈을 먼저 맡기고 시작합니다.", { x: MX, y: 6.5, w: W - MX * 2, h: 0.5, align: "center", fontFace: F, fontSize: 15, italic: true, color: GOLD });
})();

/* ===== S13 안전망② ===== */
(() => {
  const s = content();
  head(s, "SAFETY NET", "우리 돈을 먼저 맡기고 시작합니다");
  const items = [
    ["현금 1억", "약 100~150세대 즉시 재시공 규모"],
    ["업체 도산·잠적 시", "그 돈으로 A/S 승계"],
    ["하자 이행보증 5억", "업체 무너져도 엣지 100% 책임 · 동종업체 이관"],
  ];
  items.forEach((it, i) => {
    const y = 2.5 + i * 1.15;
    s.addShape(p.ShapeType.roundRect, { x: MX, y, w: W - MX * 2, h: 0.95, rectRadius: 0.06, fill: { color: SOFT } });
    s.addShape(p.ShapeType.rect, { x: MX, y, w: 0.1, h: 0.95, fill: { color: GOLD } });
    s.addText(it[0], { x: MX + 0.35, y, w: 3.6, h: 0.95, valign: "middle", fontFace: F, fontSize: 18, bold: true, color: NAVY });
    s.addText(it[1], { x: MX + 4.1, y, w: W - MX * 2 - 4.3, h: 0.95, valign: "middle", fontFace: F, fontSize: 15, color: INK });
  });
  s.addText("이게 엣지컴퍼니가 사라질 수 없는 이유입니다.", { x: MX, y: 6.2, w: W - MX * 2, h: 0.5, align: "center", fontFace: F, fontSize: 15, bold: true, color: NAVY });
  pageNum(s, 13);
})();

/* ===== S14 로드맵 ===== */
(() => {
  const s = content();
  head(s, "ROADMAP", "행사 3일이 아니라, D-9개월부터 입주 후까지");
  const steps = ["협력사 검증\n(2026.6)", "부스 설계\n카탈로그", "입주박람회", "사전점검", "입주", "베이스캠프\n1개월", "장기 A/S"];
  const n = steps.length, gap = 0.25, sw = (W - MX * 2 - gap * (n - 1)) / n, y0 = 3.0, sh = 1.3;
  steps.forEach((t, i) => {
    const x = MX + i * (sw + gap);
    const hl = (i === 5);
    s.addShape(p.ShapeType.roundRect, { x, y: y0, w: sw, h: sh, rectRadius: 0.06, fill: { color: hl ? NAVY : SOFT }, line: { color: hl ? NAVY : LINE, width: 1 } });
    s.addText(String(i + 1), { x, y: y0 + 0.15, w: sw, h: 0.4, align: "center", fontFace: F, fontSize: 14, bold: true, color: GOLD });
    s.addText(t, { x: x + 0.05, y: y0 + 0.55, w: sw - 0.1, h: 0.7, align: "center", fontFace: F, fontSize: 11, color: hl ? WHITE : INK });
  });
  s.addText("남들 D-3개월 시작할 때 — 우리는 D-9개월부터.", { x: MX, y: 4.7, w: W - MX * 2, h: 0.5, align: "center", fontFace: F, fontSize: 16, bold: true, color: NAVY });
  pageNum(s, 14);
})();

/* ===== S15 앱 ===== */
(() => {
  const s = content();
  head(s, "OUR SYSTEM", "카페에 글 하나 더 얹는 주관사 vs 혼란을 정리하는 시스템");
  imgZone(s, MX, 2.5, 3.6, 3.9, "입주민 앱 캡처\n(폰 목업)");
  const rx = 5.0, rw = W - rx - MX;
  const fs = ["실거주 인증 — 동·호수 인증한 입주민만 (가짜 후기 차단)", "검증 협력사만 — 별점 · 후기 · 단지 랭킹", "견적 · A/S를 앱 안에서 (구조화된 양식)", "24시간 미응답 시 — 주관사가 직접 중재"];
  fs.forEach((t, i) => {
    const y = 2.55 + i * 0.8;
    s.addText("✓", { x: rx, y, w: 0.4, h: 0.6, fontFace: F, fontSize: 16, bold: true, color: GOLD });
    s.addText(t, { x: rx + 0.45, y, w: rw - 0.45, h: 0.6, valign: "middle", fontFace: F, fontSize: 14, color: INK });
  });
  s.addShape(p.ShapeType.roundRect, { x: rx, y: 5.9, w: rw, h: 0.7, rectRadius: 0.05, fill: { color: SOFT }, line: { color: GOLD, width: 1.5 } });
  s.addText("단순 추천앱이 아니라 — 질서와 책임을 강제하는 운영 시스템", { x: rx, y: 5.9, w: rw, h: 0.7, align: "center", valign: "middle", fontFace: F, fontSize: 13, bold: true, color: NAVY });
  pageNum(s, 15);
})();

/* ===== S16 클로징 요약 (네이비) ===== */
(() => {
  const s = content(NAVY);
  s.addText("주관사는, 끝까지 책임질 곳을 뽑는 일입니다", { x: MX, y: 0.9, w: W - MX * 2, h: 1.0, fontFace: F, fontSize: 30, bold: true, color: WHITE });
  const keys = ["차로 20분 근접", "직접 시공 면허 법인", "지역업체 100% (안 지키면 철회)", "순수 자산 1억 선예치", "유리난간 부산 첫 사례", "입주민 앱 운영 시스템"];
  const cw = 5.6, ch = 1.0, gx = 0.5, gy = 0.35, x0 = MX, y0 = 2.5;
  keys.forEach((t, i) => {
    const x = x0 + (i % 2) * (cw + gx), y = y0 + Math.floor(i / 2) * (ch + gy);
    s.addShape(p.ShapeType.roundRect, { x, y, w: cw, h: ch, rectRadius: 0.06, fill: { color: "16203A" }, line: { color: "2A3550", width: 1 } });
    s.addText("✦", { x: x + 0.25, y, w: 0.5, h: ch, valign: "middle", fontFace: F, fontSize: 14, color: GOLD });
    s.addText(t, { x: x + 0.8, y, w: cw - 1.0, h: ch, valign: "middle", fontFace: F, fontSize: 16, bold: true, color: WHITE });
  });
})();

/* ===== S17 결정타·마무리 (네이비) ===== */
(() => {
  const s = content(NAVY);
  s.addShape(p.ShapeType.rect, { x: 0, y: 0, w: W, h: 0.18, fill: { color: GOLD } });
  s.addText("같은 시행사, 같은 노르웨이숲", { x: MX, y: 1.6, w: W - MX * 2, h: 0.6, fontFace: F, fontSize: 20, color: GOLD });
  s.addText("저희만큼 아는 주관사는 없습니다", { x: MX, y: 2.2, w: W - MX * 2, h: 1.1, fontFace: F, fontSize: 40, bold: true, color: WHITE });
  s.addText("기장 유림노르웨이숲 기주관 = 같은 시행사(유림) · 같은 브랜드 운영 경험", { x: MX, y: 3.6, w: W - MX * 2, h: 0.5, fontFace: F, fontSize: 15, color: "C9CEDA" });
  s.addText("1,294세대의 첫 입주를, 끝까지 책임지고 함께하겠습니다.", { x: MX, y: 4.6, w: W - MX * 2, h: 0.7, fontFace: F, fontSize: 22, bold: true, color: WHITE });
  s.addText("㈜엣지컴퍼니   ·   대표 고진식", { x: MX, y: 5.6, w: W - MX * 2, h: 0.5, fontFace: F, fontSize: 16, color: GOLD });
})();

const out = "C:\\Users\\win11\\Downloads\\일광노르웨이숲_자료\\일광노르웨이숲_주관사PT_텍스트본.pptx";
p.writeFile({ fileName: out }).then(() => console.log("생성 완료: " + out));
