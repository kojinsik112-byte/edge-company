import { describe, expect, it } from 'vitest';
import { calcBlind } from './blind';
import { calcCurtain, type CurtainInput } from './curtain';
import { DEFAULT_CUT, defaultSettings, newBlindRoom, newCurtainRoom, sampleSite } from './defaults';
import { ceilSafe, fmtMeters, koreanWon, parseNum } from './num';
import { calcBlindRoom, calcCurtainRoom, calcSite } from './quote';
import { exportJson, importJson, parseState } from './storage';
import type { BlindRule, CutSettings } from './types';

const CUT20: CutSettings = { ...DEFAULT_CUT, top: 10, bottom: 10 }; // 상하 재단 여유 합계 20cm, 나머지 0

const base = (o: Partial<CurtainInput>): CurtainInput => ({
  width: 360,
  height: 240,
  fabricWidth: 145,
  fullness: 1.5,
  opening: 'single',
  splitLeft: 50,
  splitRight: 50,
  method: 'joined',
  cut: CUT20,
  ...o,
});

describe('커튼 기본 산식 — 명세 테스트 A~E', () => {
  it('테스트 A: 360×240, 145폭, 1.5배, 편개', () => {
    const r = calcCurtain(base({}));
    expect(r.ok).toBe(true);
    expect(r.requiredWidthTotal).toBe(540);
    expect(r.totalWidths).toBe(4);
    expect(r.cut.final).toBe(260);
    expect(r.totalLength).toBe(1040);
    expect(fmtMeters(r.totalLength)).toBe('10.4');
  });

  it('테스트 B: 300×230, 145폭, 2배, 편개', () => {
    const r = calcCurtain(base({ width: 300, height: 230, fullness: 2 }));
    expect(r.requiredWidthTotal).toBe(600);
    expect(r.totalWidths).toBe(5);
    expect(r.cut.final).toBe(250);
    expect(r.totalLength).toBe(1250);
    expect(fmtMeters(r.totalLength)).toBe('12.5');
  });

  it('테스트 C: 420×240, 145폭, 1.5배, 편개', () => {
    const r = calcCurtain(base({ width: 420, height: 240 }));
    expect(r.requiredWidthTotal).toBe(630);
    expect(r.totalWidths).toBe(5);
    expect(r.cut.final).toBe(260);
    expect(r.totalLength).toBe(1300);
    expect(fmtMeters(r.totalLength)).toBe('13.0');
  });

  it('테스트 D: 양개 50:50 독립 올림 — 300×230, 1.5배', () => {
    const r = calcCurtain(base({ width: 300, height: 230, opening: 'double' }));
    expect(r.requiredWidthTotal).toBe(450);
    expect(r.panels.map((p) => p.requiredWidth)).toEqual([225, 225]);
    expect(r.panels.map((p) => p.widths)).toEqual([2, 2]);
    expect(r.totalWidths).toBe(4);
    expect(r.totalLength).toBe(1000);
    expect(fmtMeters(r.totalLength)).toBe('10.0');
  });

  it('테스트 E: 양개 올림 차이 — 200×230, 2배 → 전체 3폭이 아니라 4폭', () => {
    const r = calcCurtain(base({ width: 200, height: 230, fullness: 2, opening: 'double' }));
    expect(r.requiredWidthTotal).toBe(400);
    expect(r.panels.map((p) => p.requiredWidth)).toEqual([200, 200]);
    expect(r.panels.map((p) => p.widths)).toEqual([2, 2]);
    expect(r.naiveWidths).toBe(3);
    expect(r.totalWidths).toBe(4);
    expect(r.issues.some((i) => i.code === 'split-rounding')).toBe(true);
  });
});

describe('커튼 세부 규칙', () => {
  it('명세 예시: 360cm 양개 → 좌 2폭 · 우 2폭 · 총 4폭', () => {
    const r = calcCurtain(base({ opening: 'double' }));
    expect(r.panels.map((p) => [p.finishedWidth, p.requiredWidth, p.widths])).toEqual([
      [180, 270, 2],
      [180, 270, 2],
    ]);
    expect(r.totalWidths).toBe(4);
  });

  it('양개 60:40 비율', () => {
    const r = calcCurtain(base({ width: 400, opening: 'double', splitLeft: 60, splitRight: 40 }));
    expect(r.panels[0].finishedWidth).toBe(240);
    expect(r.panels[1].finishedWidth).toBe(160);
    expect(r.panels[0].widths).toBe(3); // 360 ÷ 145 = 2.48 → 3
    expect(r.panels[1].widths).toBe(2); // 240 ÷ 145 = 1.66 → 2
  });

  it('좌우 비율 합계가 100%가 아니면 오류', () => {
    const r = calcCurtain(base({ opening: 'double', splitLeft: 60, splitRight: 30 }));
    expect(r.ok).toBe(false);
    expect(r.issues.find((i) => i.field === 'split')?.message).toContain('100%');
  });

  it('원단 1폭·주름 배수를 바꾸면 즉시 재산출', () => {
    expect(calcCurtain(base({ fabricWidth: 140 })).totalWidths).toBe(4); // 540/140 = 3.86
    expect(calcCurtain(base({ fabricWidth: 135 })).totalWidths).toBe(4); // 540/135 = 4.0 → 정확히 4
    expect(calcCurtain(base({ fabricWidth: 130 })).totalWidths).toBe(5);
    expect(calcCurtain(base({ fullness: 2.2 })).requiredWidthTotal).toBe(792);
    expect(calcCurtain(base({ fullness: 2.2 })).totalWidths).toBe(6);
    expect(calcCurtain(base({ fullness: 1.0 })).totalWidths).toBe(3); // 민자 360/145 = 2.48
  });

  it('부동소수 잡음으로 폭이 하나 더 올라가지 않는다', () => {
    expect(Math.ceil(0.1 * 3 * 10)).toBe(4); // 자바스크립트 기본 올림은 잡음 때문에 틀린다
    expect(ceilSafe(0.1 * 3 * 10)).toBe(3);
    expect(ceilSafe(3.0000000000000004)).toBe(3);
    const r = calcCurtain(base({ width: 210, fullness: 1.1, fabricWidth: 77 }));
    expect(r.requiredWidthTotal).toBe(231);
    expect(r.totalWidths).toBe(3);
  });

  it('봉제 손실·옆단 여유 반영 유효 폭', () => {
    // 540 필요, 145폭, 이음 1곳당 2cm, 옆단 한쪽 5cm
    // 4폭: 580 − 3×2 − 2×5 = 564 ≥ 540 → 4폭
    const r = calcCurtain(base({ cut: { ...CUT20, seamLoss: 2, sideHem: 5 } }));
    expect(r.panels[0].widths).toBe(4);
    expect(r.panels[0].usableWidth).toBe(564);
    // 560 필요(400×1.4)라면 4폭 유효 564 → 4폭, 570이면 5폭
    const r2 = calcCurtain(base({ width: 380, fullness: 1.5, cut: { ...CUT20, seamLoss: 2, sideHem: 5 } })); // 570
    expect(r2.panels[0].widths).toBe(5);
  });

  it('잔여 원단 폭과 실제 주름 배수', () => {
    const r = calcCurtain(base({}));
    expect(r.panels[0].usableWidth).toBe(580);
    expect(r.panels[0].surplus).toBe(40);
    expect(r.panels[0].actualFullness).toBeCloseTo(1.611, 3);
  });

  it('수축 여유율·무늬 반복·재단 올림은 각각 한 번만 적용', () => {
    const shrink = calcCurtain(base({ cut: { ...CUT20, shrinkPct: 3 } }));
    expect(shrink.cut.base).toBe(260);
    expect(shrink.cut.final).toBe(267.8);
    const pattern = calcCurtain(base({ cut: { ...CUT20, patternRepeat: 64 } }));
    expect(pattern.cut.final).toBe(320); // 260 → 64×5
    const round = calcCurtain(base({ cut: { ...CUT20, shrinkPct: 3, roundUnit: 5 } }));
    expect(round.cut.final).toBe(270);
    const both = calcCurtain(base({ cut: { ...CUT20, patternRepeat: 64, roundUnit: 5 } }));
    expect(both.cut.final).toBe(320); // 무늬 우선, 재단 올림 중복 없음
    expect(both.cut.roundSkippedByPattern).toBe(true);
  });

  it('입력 검증 — NaN·Infinity가 결과에 나오지 않는다', () => {
    const cases: Partial<CurtainInput>[] = [
      { width: 0 },
      { height: 0 },
      { fabricWidth: 0 },
      { width: -100 },
      { fullness: 0.8 },
      { width: NaN },
      { width: null },
      { width: 1e9 },
      { cut: { ...CUT20, top: -5 } },
      { cut: { ...CUT20, seamLoss: 200 } },
    ];
    for (const c of cases) {
      const r = calcCurtain(base(c));
      expect(r.ok).toBe(false);
      expect(r.issues.some((i) => i.level === 'error')).toBe(true);
      expect(Number.isFinite(r.totalLength)).toBe(true);
      expect(Number.isFinite(r.totalWidths)).toBe(true);
    }
    expect(calcCurtain(base({ fullness: 0.8 })).issues[0].message).toContain('1.0배');
    expect(calcCurtain(base({ fabricWidth: 0 })).issues[0].message).toBe('원단 1폭은 0보다 커야 합니다.');
  });

  it('소수점 입력 허용', () => {
    const r = calcCurtain(base({ width: 360.5, height: 240.5, fullness: 1.55 }));
    expect(r.ok).toBe(true);
    expect(r.requiredWidthTotal).toBe(558.775);
    expect(r.totalWidths).toBe(4);
    expect(r.cut.final).toBe(260.5);
  });

  it('광폭 원단형 — 원단 폭이 높이를 충족', () => {
    const r = calcCurtain(base({ fabricWidth: 280, method: 'wide', opening: 'double' }));
    expect(r.ok).toBe(true);
    expect(r.wide?.requiredHeight).toBe(260);
    expect(r.wide?.heightOk).toBe(true);
    expect(r.panels.map((p) => p.pieceLength)).toEqual([270, 270]);
    expect(r.totalLength).toBe(540);
    expect(r.totalWidths).toBe(0);
  });

  it('광폭 원단형 — 높이 부족 경고', () => {
    const r = calcCurtain(base({ height: 270, fabricWidth: 280, method: 'wide' })); // 필요 290
    expect(r.producible).toBe(false);
    const w = r.issues.find((i) => i.code === 'wide-height');
    expect(w?.level).toBe('critical');
    expect(w?.message).toContain('원단 폭이 제작 높이를 충족하지 않습니다.');
    expect(r.wide?.shortfall).toBe(10);
  });

  it('폭 연결형에 280 광폭 원단을 넣으면 광폭형 안내', () => {
    const r = calcCurtain(base({ fabricWidth: 280, wideThreshold: 250 }));
    expect(r.issues.some((i) => i.code === 'wide-hint')).toBe(true);
    expect(r.totalWidths).toBe(2);
  });
});

describe('블라인드', () => {
  const rule: BlindRule = { deductW: 0, addW: 0, deductH: 0, addH: 0, minW: 0, maxW: 0, minH: 0, maxH: 0, roundUnit: 0, roundMode: 'round' };
  const billing = { basis: 'order' as const, minBillW: 0, minBillH: 0, minBillArea: 0, areaRoundUnit: 0, minCharge: 0 };

  it('실측 면적 1.8 × 2.0 = 3.6㎡, 주름 배수 미적용', () => {
    const r = calcBlind({ width: 180, height: 200, qty: 1, rule, billing, verified: true });
    expect(r.measuredArea).toBe(3.6);
    expect(r.orderW).toBe(180);
    expect(r.billArea).toBe(3.6);
  });

  it('공제·추가·반올림 단위로 주문 사이즈 산출, 실측과 구분', () => {
    const r = calcBlind({
      width: 180.4,
      height: 200,
      qty: 2,
      rule: { ...rule, deductW: 1, addH: 5, roundUnit: 0.5, roundMode: 'floor' },
      billing,
      verified: true,
    });
    expect(r.orderW).toBe(179); // 179.4 → 0.5 내림 = 179
    expect(r.orderH).toBe(205);
    expect(r.measuredArea).toBe(3.608);
    expect(r.orderArea).toBe(3.6695);
    expect(r.billAreaTotal).toBe(7.339);
  });

  it('최소 청구 면적·청구 규격', () => {
    const r = calcBlind({ width: 60, height: 100, qty: 1, rule, billing: { ...billing, minBillArea: 1.2 }, verified: true });
    expect(r.measuredArea).toBe(0.6);
    expect(r.billArea).toBe(1.2);
    expect(r.minAreaApplied).toBe(true);
    const r2 = calcBlind({ width: 60, height: 100, qty: 1, rule, billing: { ...billing, minBillW: 100, areaRoundUnit: 0.1 }, verified: true });
    expect(r2.billW).toBe(100);
    expect(r2.billArea).toBe(1);
  });

  it('제작 범위 초과·미설정 기준 경고', () => {
    const r = calcBlind({ width: 320, height: 200, qty: 1, rule: { ...rule, maxW: 300 }, billing, verified: false });
    expect(r.producible).toBe(false);
    expect(r.issues.some((i) => i.level === 'critical' && i.message.includes('최대 폭'))).toBe(true);
    expect(r.issues.some((i) => i.code === 'unverified' && i.message.includes('제작 기준 확인 필요'))).toBe(true);
  });

  it('수량 검증', () => {
    expect(calcBlind({ width: 100, height: 100, qty: 0, rule, billing, verified: true }).ok).toBe(false);
    expect(calcBlind({ width: 100, height: 100, qty: 1.5, rule, billing, verified: true }).ok).toBe(false);
  });
});

describe('견적', () => {
  const s = defaultSettings();

  it('m당 단가: 총 소요 원단(m) × 단가', () => {
    const room = { ...newCurtainRoom(s), width: 360, height: 240, opening: 'single' as const };
    room.pricing.fabric = { mode: 'perMeter', price: 20000 };
    const q = calcCurtainRoom(room, s).quote;
    expect(q.lines[0].amount).toBe(208000); // 10.4m × 20,000
  });

  it('폭당 단가: 필요 폭 수 × 폭당 단가', () => {
    const room = { ...newCurtainRoom(s), width: 360, height: 240, opening: 'single' as const };
    room.pricing.fabric = { mode: 'perWidth', price: 30000 };
    room.pricing.sewing = { mode: 'perWidth', price: 10000 };
    room.pricing.rail = { mode: 'perMeter', price: 8000 };
    room.pricing.install = { mode: 'fixed', price: 30000 };
    const q = calcCurtainRoom(room, s).quote;
    expect(q.lines.map((l) => l.amount)).toEqual([120000, 40000, 28800, 30000]);
    expect(q.subtotal).toBe(218800);
  });

  it('블라인드 ㎡ 단가·최소 제작 요금', () => {
    const room = { ...newBlindRoom(s), width: 180, height: 200, unitPrice: 30000, install: 10000, qty: 2 };
    const q = calcBlindRoom(room, s).quote;
    expect(q.lines[0].amount).toBe(216000); // 3.6 × 30,000 × 2
    expect(q.lines[1].amount).toBe(20000);
    const s2 = defaultSettings();
    s2.blindPresets['콤비블라인드'].billing.minCharge = 150000;
    expect(calcBlindRoom(room, s2).quote.lines[0].amount).toBe(300000);
  });

  it('현장 합계: 할인·부가세·끝전 절사', () => {
    const st = defaultSettings();
    const site = sampleSite(st);
    const t = calcSite(site, st).totals;
    // 거실 420 양개 1.5배: 장당 315 → 3폭 ×2 = 6 / 안방 300 양개 2배: 장당 300 → 3폭 ×2 = 6
    expect(t.curtainWidths).toBe(12);
    expect(t.blindCount).toBe(2);
    expect(t.supply).toBe(t.net);
    expect(t.vat).toBe(Math.round(t.net * 0.1));
    expect(t.total).toBe(t.net + t.vat);

    st.vatMode = 'included';
    const t2 = calcSite(site, st).totals;
    expect(t2.total).toBe(t2.net);
    expect(t2.supply + t2.vat).toBe(t2.net);

    st.vatMode = 'add';
    st.quote.roundDown = 1000;
    site.common.discount = { type: 'rate', value: 10 };
    const t3 = calcSite(site, st).totals;
    expect(t3.siteDiscount).toBe(Math.round((t3.roomsNet + t3.travel + t3.shipping) * 0.1));
    expect(t3.total % 1000).toBe(0);
    expect(t3.gross - t3.total).toBe(t3.roundAdj);
  });
});

describe('저장·숫자 유틸', () => {
  it('손상된 저장 데이터는 기본값으로 복구', () => {
    expect(parseState('{not json').status).toBe('recovered');
    const bad = parseState(JSON.stringify({ version: 1, settings: { curtain: { fabricWidth: 'abc', fullness: -1 } }, site: { rooms: [{ kind: 'x' }] } }));
    expect(bad.state.settings.curtain.fabricWidth).toBe(145);
    expect(bad.state.site.rooms.length).toBeGreaterThan(0);
  });

  it('저장·불러오기에서 현장 정보(동/호수)가 지워지지 않는다', () => {
    const st = parseState(null).state;
    st.site.info.dongho = '101동 1203호';
    st.settings.unit = 'mm';
    const back = parseState(JSON.stringify(st)).state;
    expect(back.site.info.dongho).toBe('101동 1203호');
    expect(back.settings.unit).toBe('mm');
    expect(back.site.rooms.map((r) => r.id)).toEqual(st.site.rooms.map((r) => r.id));
    expect(back.site.rooms[0]).toEqual(st.site.rooms[0]);
  });

  it('JSON 내보내기 → 불러오기 왕복', () => {
    const st = parseState(null).state;
    const back = importJson(exportJson(st));
    expect(back.ok).toBe(true);
    if (back.ok) expect(back.state.site.rooms.length).toBe(st.site.rooms.length);
    expect(importJson('hello').ok).toBe(false);
  });

  it('숫자 해석', () => {
    expect(parseNum('1,234.5')).toBe(1234.5);
    expect(parseNum(' 360 ')).toBe(360);
    expect(parseNum('')).toBe(null);
    expect(Number.isNaN(parseNum('12a') as number)).toBe(true);
    expect(parseNum('２４０')).toBe(240);
    expect(koreanWon(1234000)).toBe('123만 4,000원');
  });
});
