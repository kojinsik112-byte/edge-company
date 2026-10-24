// 시공 단계 기술 자문 협력 계약서 — 공고의 '분야별 전문인력(직접 고용 또는 협력 계약)' 요건용 양식.
// 같은 내용(BLOCKS)으로 ① .docx(상대방이 채워 날인) ② .html(출력 · PDF 미리보기)을 만든다.
// 사용: NODE_PATH=<docx 모듈 경로> node advisory_contract.js <출력 이름(확장자 없이)>
// 단지가 바뀌면 CFG만 고친다. 을(협력사 · 자문인) 칸은 빈칸.
const fs = require("fs");
const D = require("docx");

const CFG = {
  site: "상주 자이르네",
  council: "상주 자이르네 입주예정자협의회",
  duty: "「시공 단계 품질 · 하자 예방 지원」(협의회 입찰공고 2항 ①)",
  related: "교보자산신탁㈜ · ㈜고은건설 · 자이에스앤디㈜",
  form: "[별지2호] 전담 책임자 및 분야별 전문가 명단",
  fields: ["건축", "토목", "기계설비", "소방"],
  reply: 7, // 영업일 — 제안서의 '10영업일 서면 회신'보다 짧게(주관사 검토 여유)
  co: { name: "주식회사 엣지컴퍼니", biz: "508-81-42798", addr: "울산광역시 울주군 청량읍 온산로 615-1, 2층, 3층", ceo: "대표이사  고 진 식" },
};

// ---------------------------------------------------------------- 내용(한 곳)
const H = (cells) => ({ head: true, cells });
const BLOCKS = [
  { k: "title", t: "시공 단계 기술 자문 협력 계약서" },
  { k: "subtitle", t: `${CFG.site} 입주박람회 주관사 업무 — ${CFG.duty.replace(/[「」]/g, "")}` },
  { k: "p", t: `${CFG.co.name}(이하 '갑')와 ______________________(이하 '을')은 ${CFG.council}(이하 '협의회')의 입주박람회 주관사 업무 중 시공 단계 기술 자문에 관하여 다음과 같이 계약을 체결한다.` },

  { k: "art", t: "제1조(목적)" },
  { k: "p", t: `이 계약은 갑이 협의회 주관사로 선정되어 수행하는 업무 중 ${CFG.duty}에 필요한 분야별 기술 자문을 을이 제공하는 데 필요한 사항을 정함을 목적으로 한다.` },

  { k: "art", t: "제2조(자문 분야 및 자문인)" },
  { k: "item", t: "① 을이 맡는 자문 분야와 자문인은 다음과 같다." },
  { k: "table", w: [13, 17, 25, 19, 26], rows: [H(["분야", "자문인 성명", "자격 종목 · 등급", "자격 번호", "소속 · 직위"]), ...CFG.fields.map((f) => [{ t: f, b: true, c: true }, "", "", "", ""])] },
  { k: "note", t: "※ 을이 맡지 않는 분야는 '해당 없음'으로 적는다. 자격 = 국가기술자격 또는 관계 법령에 따른 면허(건축사 · 기술사 · 기사 · 산업기사 · 소방시설관리사 등)." },
  { k: "item", t: "② 을은 자문인이 위 자격을 유지하게 하며, 자문인을 바꿀 때에는 같은 분야에서 같은 등급 이상의 자격자로 하고 미리 갑의 서면 동의를 받는다." },

  { k: "art", t: "제3조(자문 업무)" },
  { k: "item", t: "① 을은 협의회 또는 갑이 요청하면 다음 업무를 수행한다." },
  { k: "sub", t: "1. 공정별 기술 자문 및 협의회 요청 사항에 대한 기술 검토" },
  { k: "sub", t: "2. 하자 취약 부위 확인(필요하면 현장 확인 포함)" },
  { k: "sub", t: "3. 기술 검토 의견서 등 근거자료 작성" },
  { k: "sub", t: "4. 갑이 요청하는 경우 협의회 회의 참석 · 설명" },
  { k: "item", t: "② 자문 횟수는 정하지 않으며, 요청이 있을 때 수행한다." },
  { k: "item", t: "③ 을의 자문은 기술 의견 제공에 한하며 법정 감리 · 하자 판정 · 보수 · 소송 대리를 포함하지 않는다. 건설 하자의 보수 책임은 사업주체와 시공사에 있다." },

  { k: "art", t: "제4조(회신 기한)" },
  { k: "item", t: `① 을은 요청을 받은 날부터 ${CFG.reply}영업일 안에 서면(전자우편 포함)으로 회신한다.` },
  { k: "item", t: "② 현장 확인이 필요하면 갑과 일정을 협의하여 지체 없이 방문한다." },
  { k: "item", t: "③ 기한 안에 회신하기 어려우면 그 사유와 회신 예정일을 즉시 갑에게 알린다." },

  { k: "art", t: "제5조(대가)" },
  { k: "item", t: "① 자문 대가는 건별로 정산하며 갑이 부담한다. 월 고정 보수는 없다." },
  { k: "item", t: "② 단가는 서면 검토 1건당 금 ______________원, 현장 확인 1회당 금 ______________원(부가가치세 별도)으로 하고, 교통비 등 실비는 갑과 협의하여 정한다." },
  { k: "item", t: "③ 을은 자문 대가를 협의회나 입주예정자에게 청구하지 않는다." },
  { k: "item", t: "④ 갑은 을의 의견서 제출 후 세금계산서(또는 계산서)를 받은 날이 속한 달의 다음 달 말일까지 지급한다. 을이 개인이면 관계 법령에 따라 원천징수한다." },

  { k: "art", t: "제6조(효력 및 기간)" },
  { k: "item", t: "① 이 계약은 갑과 을이 기명날인한 날부터 효력이 생긴다. 다만 제3조의 업무는 갑이 협의회 주관사로 선정되어 협의회와 협약을 체결한 뒤 요청에 따라 수행한다." },
  { k: "item", t: "② 갑이 주관사로 선정되지 않으면 이 계약은 선정 결과가 발표된 날 별도 통지 없이 끝나며, 갑과 을은 서로 어떠한 금전도 청구하지 않는다." },
  { k: "item", t: "③ 계약 기간은 갑과 협의회의 협약이 끝나는 날까지로 한다. 다만 갑과 을은 시공 단계 자문이 끝난 뒤 합의하여 기간을 줄일 수 있다." },

  { k: "art", t: "제7조(이해관계 없음)" },
  { k: "item", t: `① 을과 자문인은 계약일 현재 이 단지의 시행 · 시공 · 분양 관계사(${CFG.related} 등), 이 단지 공사의 감리자, 협의회 임원과 고용 · 용역 · 하도급 등 이해관계가 없음을 확인한다.` },
  { k: "item", t: "② 계약 기간 중 제1항의 관계가 생기면 을은 즉시 갑에게 알리고, 갑은 자문인 교체 또는 계약 해지를 요청할 수 있다." },

  { k: "art", t: "제8조(비밀유지 · 개인정보 · 접촉 금지)" },
  { k: "item", t: "① 을과 자문인은 업무 중 알게 된 협의회 · 입주예정자 · 갑의 정보를 이 계약 목적 외에 쓰거나 제3자에게 알리지 않는다. 계약이 끝난 뒤에도 같다." },
  { k: "item", t: "② 을과 자문인은 입주예정자 개인정보를 「개인정보 보호법」에 따라 처리하고, 업무가 끝나면 지체 없이 파기한다." },
  { k: "item", t: "③ 을과 자문인은 갑의 입찰과 관련하여 협의회 임원 · 운영위원 · 입주예정자 · 협의회 법무대리인에게 개별 접촉하거나 영업하지 않는다(협의회 입찰공고 7항)." },

  { k: "art", t: "제9조(자격 증빙 제출 및 기재 동의)" },
  { k: "item", t: "① 을은 자문인의 자격증 사본과 재직(소속) 증빙을 갑에게 제출한다. 주민등록번호 뒷자리는 가린다." },
  { k: "item", t: `② 을과 자문인은 갑이 협의회 입찰 제출서류(${CFG.form}) · 제안서 · 협약서에 자문인의 성명 · 자격 · 소속을 적고 제1항 자료를 첨부하여 제출하는 데 동의한다(붙임 동의서).` },
  { k: "item", t: "③ 자문인은 이 계약에 따라 실제로 자문을 수행하며, 자격증을 빌려주거나 명의만 빌려주는 것이 아님을 확인한다." },

  { k: "art", t: "제10조(해지)" },
  { k: "p", t: "갑 또는 을이 이 계약을 위반하면 상대방은 14일 이상의 기간을 정하여 서면으로 시정을 요구할 수 있고, 그 기간 안에 시정되지 않으면 서면으로 계약을 해지할 수 있다." },

  { k: "art", t: "제11조(기타)" },
  { k: "item", t: "① 이 계약에 정하지 않은 사항은 갑과 을이 협의하여 정한다." },
  { k: "item", t: "② 이 계약에 관한 분쟁의 관할 법원은 갑의 본점 소재지를 관할하는 법원으로 한다." },

  { k: "close", keep: true, t: "이 계약을 증명하기 위하여 계약서 2부를 작성하여 갑과 을이 기명날인하고 각 1부씩 보관한다." },
  { k: "date", t: "2026년  10월  ______일" },
  { k: "sign", parties: [
    ["갑", [["상호", CFG.co.name], ["사업자등록번호", CFG.co.biz], ["주소", CFG.co.addr], ["대표자", `${CFG.co.ceo}          (인)`, "r"]]],
    ["을", [["상호(성명)", ""], ["사업자등록번호(생년월일)", ""], ["주소", ""], ["대표자", "(인)", "r"]]],
  ] },

  { k: "break" },
  { k: "title2", t: "[붙임] 자문인 개인정보 수집 · 이용 동의서" },
  { k: "table", w: [24, 76], rows: [
    [{ t: "수집 · 이용 목적", h: true }, `${CFG.council} 주관사 입찰 서류 제출(${CFG.form}) · 제안서 기재 · 협약 이행`],
    [{ t: "수집 항목", h: true }, "성명, 자격 종목 · 등급 · 번호, 소속 · 직위, 자격증 사본(주민등록번호 뒷자리 가림), 재직 · 소속 증빙"],
    [{ t: "제공받는 자", h: true }, `${CFG.council}(입찰 서류는 공고에 따라 반환되지 않음)`],
    [{ t: "보유 기간", h: true }, "계약이 끝날 때까지. 갑이 주관사로 선정되지 않으면 선정 결과 발표 후 갑이 보관한 자료는 지체 없이 파기"],
    [{ t: "거부 권리", h: true }, "동의를 거부할 수 있으나, 거부하면 입찰 서류에 자문인으로 적을 수 없습니다."],
  ] },
  { k: "close", t: "위 내용을 확인하고 개인정보 수집 · 이용 및 제3자 제공에 동의합니다." },
  { k: "table", w: [14, 21, 34, 31], tall: true, rows: [H(["분야", "성명", "동의 여부", "서명"]),
    ...CFG.fields.map((f) => [{ t: f, b: true, c: true }, "", { t: "□ 동의      □ 미동의", c: true }, ""])] },
  { k: "date", t: "2026년  10월  ______일" },
];

// ---------------------------------------------------------------- .docx
const FONT = "맑은 고딕";
const W = 9638; // A4 본문 폭(DXA) — 여백 좌우 20mm
const run = (text, o = {}) => new D.TextRun({ text, font: FONT, size: o.size || 20, bold: o.bold, color: o.color });
const para = (text, o = {}) => new D.Paragraph({
  children: [run(text, o)], alignment: o.align, keepNext: o.keepNext,
  spacing: { before: o.before || 0, after: o.after ?? 80, line: 300 },
  indent: o.hang ? { left: o.hang, hanging: o.hang } : o.left ? { left: o.left, hanging: 300 } : undefined,
});
const line = { style: D.BorderStyle.SINGLE, size: 4, color: "8A8F99" };
const borders = { top: line, bottom: line, left: line, right: line };
const norm = (c) => (typeof c === "string" ? { t: c } : c);
const dcell = (c, w, o = {}) => new D.TableCell({
  width: { size: w, type: D.WidthType.DXA }, borders, verticalAlign: D.VerticalAlign.CENTER, rowSpan: o.rowSpan,
  shading: c.h || o.head ? { type: D.ShadingType.CLEAR, color: "auto", fill: "E9ECF1" } : undefined,
  margins: { top: o.tall ? 160 : 70, bottom: o.tall ? 160 : 70, left: 100, right: 100 },
  children: [new D.Paragraph({
    alignment: c.r ? D.AlignmentType.RIGHT : c.c || o.head ? D.AlignmentType.CENTER : D.AlignmentType.LEFT,
    children: [run(c.t, { bold: c.b || c.h || o.head, size: o.size || 19 })] })],
});
function docxTable(b) {
  const ws = b.w.map((p) => Math.round((W * p) / 100));
  ws[ws.length - 1] += W - ws.reduce((a, x) => a + x, 0);
  return new D.Table({
    width: { size: W, type: D.WidthType.DXA }, columnWidths: ws,
    rows: b.rows.map((r) => new D.TableRow({ cantSplit: true,
      children: (r.head ? r.cells : r).map((c, i) => dcell(norm(c), ws[i], { head: r.head, tall: b.tall })) })),
  });
}
function docxSign(b) {
  const ws = [900, 2600, W - 3500];
  const rows = [];
  for (const [who, items] of b.parties) items.forEach((it, i) => rows.push(new D.TableRow({ cantSplit: true, children: [
    ...(i === 0 ? [dcell({ t: who, b: true, c: true, h: true }, ws[0], { rowSpan: items.length, size: 21 })] : []),
    dcell({ t: it[0], h: true, c: true }, ws[1]), dcell({ t: it[1], r: it[2] === "r" }, ws[2], { tall: true }),
  ] })));
  return new D.Table({ width: { size: W, type: D.WidthType.DXA }, columnWidths: ws, rows });
}
function toDocx() {
  const out = [];
  for (const b of BLOCKS) {
    if (b.k === "title") out.push(para(b.t, { bold: true, size: 34, align: D.AlignmentType.CENTER, after: 60 }));
    else if (b.k === "subtitle") out.push(para(b.t, { size: 18, color: "555B66", align: D.AlignmentType.CENTER, after: 240 }));
    else if (b.k === "title2") out.push(para(b.t, { bold: true, size: 28, align: D.AlignmentType.CENTER, after: 240 }));
    else if (b.k === "art") out.push(para(b.t, { bold: true, size: 21, before: 160, after: 60, keepNext: true }));
    else if (b.k === "p") out.push(para(b.t));
    else if (b.k === "item") out.push(para(b.t, { hang: 340 }));
    else if (b.k === "sub") out.push(para(b.t, { left: 640 }));
    else if (b.k === "note") out.push(para(b.t, { size: 17, color: "555B66", before: 60 }));
    else if (b.k === "close") out.push(para(b.t, { before: 200, after: 160, keepNext: b.keep }));
    else if (b.k === "date") out.push(para(b.t, { size: 21, align: D.AlignmentType.CENTER, before: 120, after: 200, keepNext: true }));
    else if (b.k === "table") out.push(docxTable(b));
    else if (b.k === "sign") out.push(docxSign(b));
    else if (b.k === "break") out.push(new D.Paragraph({ children: [new D.PageBreak()] }));
  }
  return new D.Document({
    creator: CFG.co.name, title: `시공 단계 기술 자문 협력 계약서 — ${CFG.site}`,
    styles: { default: { document: { run: { font: FONT, size: 20 } } } },
    sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } }, children: out }],
  });
}

// ---------------------------------------------------------------- .html(출력 · PDF 미리보기)
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
function htmlCell(c, o = {}) {
  c = norm(c);
  const tag = c.h || o.head ? "th" : "td";
  const cls = [c.c || o.head ? "c" : "", c.r ? "r" : "", c.b ? "b" : "", o.tall ? "tall" : ""].filter(Boolean).join(" ");
  return `<${tag}${o.rowSpan ? ` rowspan="${o.rowSpan}"` : ""}${cls ? ` class="${cls}"` : ""}>${esc(c.t) || "&nbsp;"}</${tag}>`;
}
function toHtml() {
  const out = BLOCKS.map((b) => {
    if (b.k === "table") return `<table><colgroup>${b.w.map((p) => `<col style="width:${p}%">`).join("")}</colgroup>` +
      b.rows.map((r) => `<tr>${(r.head ? r.cells : r).map((c) => htmlCell(c, { head: r.head, tall: b.tall })).join("")}</tr>`).join("") + "</table>";
    if (b.k === "sign") return `<table class="sign"><colgroup><col style="width:9%"><col style="width:27%"><col></colgroup>` +
      b.parties.map(([who, items]) => items.map((it, i) => `<tr>${i === 0 ? htmlCell({ t: who, h: true, c: true }, { rowSpan: items.length }) : ""}` +
        htmlCell({ t: it[0], h: true, c: true }) + htmlCell({ t: it[1], r: it[2] === "r" }, { tall: true }) + "</tr>").join("")).join("") + "</table></div>";
    if (b.k === "break") return '<div class="pb"></div>';
    if (b.k === "close" && b.keep) return `<div class="keep"><p class="close">${esc(b.t)}</p>`;
    return `<p class="${b.k}">${esc(b.t)}</p>`;
  }).join("\n");
  return `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>시공 단계 기술 자문 협력 계약서</title><style>
@page{size:A4;margin:20mm}
body{font-family:'Malgun Gothic','맑은 고딕','Pretendard',sans-serif;font-size:9.8pt;line-height:1.48;color:#1B2433;margin:0}
p{margin:0 0 4pt}
.title{font-size:17pt;font-weight:700;text-align:center;margin-bottom:3pt;letter-spacing:.5pt}
.subtitle{font-size:9pt;color:#555B66;text-align:center;margin-bottom:12pt}
.title2{font-size:14pt;font-weight:700;text-align:center;margin-bottom:12pt}
.art{font-weight:700;font-size:10.3pt;margin-top:6.5pt;margin-bottom:2pt;break-after:avoid}
.item{padding-left:17pt;text-indent:-17pt}
.sub{padding-left:32pt;text-indent:-15pt}
.note{font-size:8.5pt;color:#555B66;margin-top:3pt}
.close{margin-top:8pt;margin-bottom:4pt}
.keep{break-inside:avoid}
.date{text-align:center;font-size:10.5pt;margin:4pt 0 8pt}
table{width:100%;border-collapse:collapse;table-layout:fixed;margin:2pt 0 4pt;break-inside:avoid}
th,td{border:.6pt solid #8A8F99;padding:3.5pt 5pt;font-size:9.5pt;vertical-align:middle;text-align:left}
th{background:#E9ECF1;font-weight:700}
.c{text-align:center}.r{text-align:right}.b{font-weight:700}
.tall{height:15pt}
.sign th,.sign td{padding:2.5pt 5pt}
.pb{break-after:page}
</style></head><body>${out}</body></html>`;
}

const base = process.argv[2];
fs.writeFileSync(base + ".html", toHtml());
D.Packer.toBuffer(toDocx()).then((buf) => { fs.writeFileSync(base + ".docx", buf); console.log("저장", base + ".docx · .html"); });
