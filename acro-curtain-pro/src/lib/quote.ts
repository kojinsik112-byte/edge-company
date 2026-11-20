// 견적 계산 — 공간별 견적과 현장 전체 합계. 금액은 원 단위 정수.
import { calcBlind, type BlindResult } from './blind';
import { calcCurtain, type CurtainResult } from './curtain';
import { ruleFromPreset, roomLabel } from './defaults';
import { clean, fmt, fmtMeters, isNum, n0, won } from './num';
import type { BlindRoom, CurtainRoom, Discount, Issue, OptionItem, Room, Settings, Site } from './types';

export type Category = 'fabric' | 'production' | 'hardware' | 'install' | 'option';
export const CATEGORY_LABEL: Record<Category, string> = {
  fabric: '원단비',
  production: '제작비',
  hardware: '부자재·레일',
  install: '설치비',
  option: '추가 옵션',
};

export interface QuoteLine {
  key: string;
  category: Category;
  label: string;
  basis: string; // 산출 근거 (예: 10.4m × 18,000원)
  amount: number;
  cost: number | null; // 관리자 원가
}

export interface RoomQuote {
  lines: QuoteLine[];
  subtotal: number;
  discount: number;
  total: number; // 할인 후, 부가세 전
  costTotal: number;
  costKnown: boolean;
  issues: Issue[];
}

export interface CurtainCalc {
  kind: 'curtain';
  room: CurtainRoom;
  label: string;
  result: CurtainResult;
  quote: RoomQuote;
}
export interface BlindCalc {
  kind: 'blind';
  room: BlindRoom;
  label: string;
  result: BlindResult;
  quote: RoomQuote;
}
export type RoomCalc = CurtainCalc | BlindCalc;

const money = (v: number) => Math.round(v);

function priceIssue(v: number | null | undefined, name: string, issues: Issue[]): number {
  if (v === null || v === undefined) return 0;
  if (!isNum(v)) {
    issues.push({ level: 'error', message: `${name}: 숫자만 입력할 수 있습니다.` });
    return 0;
  }
  if (v < 0) {
    issues.push({ level: 'error', message: `${name}: 단가는 음수일 수 없습니다.` });
    return 0;
  }
  return v;
}

function costOf(qty: number, cost: number | null | undefined): number | null {
  return isNum(cost) && cost >= 0 ? money(qty * cost) : null;
}

function applyDiscount(subtotal: number, d: Discount, issues: Issue[], scope: string): number {
  const v = d.value;
  if (v === null || v === 0) return 0;
  if (!isNum(v) || v < 0) {
    issues.push({ level: 'error', message: `${scope} 할인 값이 올바르지 않습니다.` });
    return 0;
  }
  if (d.type === 'rate') {
    if (v > 100) {
      issues.push({ level: 'error', message: `${scope} 할인율은 100%를 넘을 수 없습니다.` });
      return 0;
    }
    return money((subtotal * v) / 100);
  }
  if (v > subtotal) {
    issues.push({ level: 'warning', message: `${scope} 할인 금액이 합계보다 커서 합계까지만 할인했습니다.` });
    return subtotal;
  }
  return money(v);
}

function optionLines(options: OptionItem[], issues: Issue[]): QuoteLine[] {
  return options
    .filter((o) => o.amount !== null || o.label.trim())
    .map((o) => {
      const amt = priceIssue(o.amount, o.label || '추가 옵션', issues);
      return {
        key: `opt-${o.id}`,
        category: 'option' as const,
        label: o.label.trim() || '추가 옵션',
        basis: '정액',
        amount: money(amt),
        cost: costOf(1, o.cost),
      };
    });
}

function finishQuote(lines: QuoteLine[], discount: Discount, issues: Issue[]): RoomQuote {
  const subtotal = lines.reduce((s, l) => s + l.amount, 0);
  const disc = applyDiscount(subtotal, discount, issues, '공간');
  const costKnown = lines.length > 0 && lines.every((l) => l.cost !== null);
  return {
    lines,
    subtotal,
    discount: disc,
    total: subtotal - disc,
    costTotal: lines.reduce((s, l) => s + n0(l.cost), 0),
    costKnown,
    issues,
  };
}

export function curtainCut(room: CurtainRoom, s: Settings) {
  return room.cutOverride ?? s.cut;
}

export function calcCurtainRoom(room: CurtainRoom, s: Settings): CurtainCalc {
  const result = calcCurtain({
    width: room.width,
    height: room.height,
    fabricWidth: room.fabricWidth,
    fullness: room.fullness,
    opening: room.opening,
    splitLeft: room.splitLeft,
    splitRight: room.splitRight,
    method: room.method,
    cut: curtainCut(room, s),
    wideThreshold: s.curtain.wideThreshold,
  });
  const issues: Issue[] = [];
  const lines: QuoteLine[] = [];
  const p = room.pricing;
  if (result.ok) {
    const meters = clean(result.totalLength / 100);
    const railM = clean(result.width / 100);
    const wide = result.method === 'wide';

    // 원단비
    if (p.fabric.price !== null) {
      const price = priceIssue(p.fabric.price, '원단 단가', issues);
      if (p.fabric.mode === 'perMeter') {
        lines.push({
          key: 'fabric',
          category: 'fabric',
          label: '원단비',
          basis: `${fmtMeters(result.totalLength)}m × ${won(price)}`,
          amount: money(meters * price),
          cost: costOf(meters, p.fabric.cost),
        });
      } else if (wide) {
        issues.push({ level: 'warning', message: '광폭 원단형은 폭 수가 없어 폭당 원단 단가를 쓸 수 없습니다. m당 단가로 바꿔 주세요.' });
      } else {
        lines.push({
          key: 'fabric',
          category: 'fabric',
          label: '원단비',
          basis: `${result.totalWidths}폭 × ${won(price)}`,
          amount: money(result.totalWidths * price),
          cost: costOf(result.totalWidths, p.fabric.cost),
        });
      }
    }
    // 봉제비(제작비)
    if (p.sewing.price !== null) {
      const price = priceIssue(p.sewing.price, '봉제비', issues);
      if (p.sewing.mode === 'perWidth') {
        if (wide) {
          issues.push({ level: 'warning', message: '광폭 원단형은 폭 수가 없어 폭당 봉제비를 쓸 수 없습니다. 가로 m당 또는 정액으로 바꿔 주세요.' });
        } else {
          lines.push({
            key: 'sewing',
            category: 'production',
            label: '봉제비',
            basis: `${result.totalWidths}폭 × ${won(price)}`,
            amount: money(result.totalWidths * price),
            cost: costOf(result.totalWidths, p.sewing.cost),
          });
        }
      } else if (p.sewing.mode === 'perMeter') {
        lines.push({
          key: 'sewing',
          category: 'production',
          label: '봉제비',
          basis: `가로 ${fmt(railM, 2)}m × ${won(price)}`,
          amount: money(railM * price),
          cost: costOf(railM, p.sewing.cost),
        });
      } else {
        lines.push({ key: 'sewing', category: 'production', label: '봉제비', basis: '정액', amount: money(price), cost: costOf(1, p.sewing.cost) });
      }
    }
    if (p.hardware.price !== null) {
      const price = priceIssue(p.hardware.price, '부자재비', issues);
      lines.push({ key: 'hardware', category: 'hardware', label: '부자재비', basis: '정액', amount: money(price), cost: costOf(1, p.hardware.cost) });
    }
    if (p.rail.price !== null) {
      const price = priceIssue(p.rail.price, '레일비', issues);
      if (p.rail.mode === 'perMeter') {
        lines.push({
          key: 'rail',
          category: 'hardware',
          label: '레일비',
          basis: `가로 ${fmt(railM, 2)}m × ${won(price)}`,
          amount: money(railM * price),
          cost: costOf(railM, p.rail.cost),
        });
      } else {
        lines.push({ key: 'rail', category: 'hardware', label: '레일비', basis: '정액', amount: money(price), cost: costOf(1, p.rail.cost) });
      }
    }
    if (p.install.price !== null) {
      const price = priceIssue(p.install.price, '설치비', issues);
      lines.push({ key: 'install', category: 'install', label: '설치비', basis: '정액', amount: money(price), cost: costOf(1, p.install.cost) });
    }
    lines.push(...optionLines(p.options, issues));
  }
  return { kind: 'curtain', room, label: roomLabel(room), result, quote: finishQuote(lines, room.discount, issues) };
}

export function blindRuleFor(room: BlindRoom, s: Settings) {
  const preset = s.blindPresets[room.blindType];
  return { rule: room.customRule ?? ruleFromPreset(preset, room.mount), preset };
}

export function calcBlindRoom(room: BlindRoom, s: Settings): BlindCalc {
  const { rule, preset } = blindRuleFor(room, s);
  const result = calcBlind({
    width: room.width,
    height: room.height,
    qty: room.qty,
    rule,
    billing: preset.billing,
    verified: preset.verified || room.customRule !== null,
  });
  const issues: Issue[] = [];
  const lines: QuoteLine[] = [];
  if (result.ok) {
    const q = result.qty;
    if (room.unitPrice !== null) {
      const price = priceIssue(room.unitPrice, '제품 단가', issues);
      let perPiece = room.priceMode === 'area' ? result.billArea * price : price;
      const perCost: number | null = isNum(room.unitCost) ? (room.priceMode === 'area' ? result.billArea * room.unitCost : room.unitCost) : null;
      let basis =
        room.priceMode === 'area'
          ? `청구 ${fmt(result.billArea, 2)}㎡ × ${won(price)} × ${q}개`
          : `${won(price)} × ${q}개`;
      const minCharge = preset.billing.minCharge;
      if (minCharge > 0 && perPiece < minCharge) {
        perPiece = minCharge;
        basis = `최소 제작 요금 ${won(minCharge)} × ${q}개`;
      }
      lines.push({
        key: 'product',
        category: 'production',
        label: '제품비',
        basis,
        amount: money(money(perPiece) * q),
        cost: perCost === null ? null : money(money(perCost) * q),
      });
    }
    if (room.install !== null) {
      const price = priceIssue(room.install, '설치비', issues);
      lines.push({
        key: 'install',
        category: 'install',
        label: '설치비',
        basis: `${won(price)} × ${q}개`,
        amount: money(price * q),
        cost: costOf(q, room.installCost),
      });
    }
    lines.push(...optionLines(room.options, issues));
  }
  return { kind: 'blind', room, label: roomLabel(room), result, quote: finishQuote(lines, room.discount, issues) };
}

export function calcRoom(room: Room, s: Settings): RoomCalc {
  return room.kind === 'curtain' ? calcCurtainRoom(room, s) : calcBlindRoom(room, s);
}

export interface SiteTotals {
  curtainRooms: number;
  curtainWidths: number;
  curtainLength: number; // cm
  blindRooms: number;
  blindCount: number;
  blindMeasuredArea: number;
  blindBillArea: number;
  cat: Record<Category, number>;
  roomSubtotal: number;
  roomDiscount: number;
  roomsNet: number;
  travel: number;
  shipping: number;
  siteDiscount: number;
  net: number; // 부가세 계산 기준 금액
  supply: number; // 공급가액
  vat: number;
  gross: number;
  roundAdj: number;
  total: number; // 최종 견적 합계
  costTotal: number;
  costKnown: boolean;
  margin: number;
  marginRate: number; // %
  pendingRooms: number; // 계산 미완료 공간 수
  issues: Issue[];
}

export interface SiteCalc {
  rooms: RoomCalc[];
  totals: SiteTotals;
}

export function calcSite(site: Site, s: Settings): SiteCalc {
  const rooms = site.rooms.map((r) => calcRoom(r, s));
  const issues: Issue[] = [];
  const cat: Record<Category, number> = { fabric: 0, production: 0, hardware: 0, install: 0, option: 0 };
  let curtainRooms = 0;
  let curtainWidths = 0;
  let curtainLength = 0;
  let blindRooms = 0;
  let blindCount = 0;
  let blindMeasuredArea = 0;
  let blindBillArea = 0;
  let roomSubtotal = 0;
  let roomDiscount = 0;
  let costTotal = 0;
  let costKnown = true;
  let pendingRooms = 0;
  for (const rc of rooms) {
    if (!rc.result.ok) pendingRooms++;
    if (rc.kind === 'curtain') {
      curtainRooms++;
      if (rc.result.ok) {
        curtainWidths += rc.result.totalWidths;
        curtainLength += rc.result.totalLength;
      }
    } else {
      blindRooms++;
      if (rc.result.ok) {
        blindCount += rc.result.qty;
        blindMeasuredArea += rc.result.measuredAreaTotal;
        blindBillArea += rc.result.billAreaTotal;
      }
    }
    for (const l of rc.quote.lines) cat[l.category] += l.amount;
    roomSubtotal += rc.quote.subtotal;
    roomDiscount += rc.quote.discount;
    costTotal += rc.quote.costTotal;
    if (rc.quote.lines.length && !rc.quote.costKnown) costKnown = false;
  }
  const roomsNet = roomSubtotal - roomDiscount;
  const travel = Math.max(0, money(n0(site.common.travelFee)));
  const shipping = Math.max(0, money(n0(site.common.shippingFee)));
  costTotal += n0(site.common.travelCost) + n0(site.common.shippingCost);
  const beforeSiteDisc = roomsNet + travel + shipping;
  const siteDiscount = applyDiscount(beforeSiteDisc, site.common.discount, issues, '현장 전체');
  const net = beforeSiteDisc - siteDiscount;

  const rate = isNum(s.vatRate) && s.vatRate >= 0 ? s.vatRate : 0;
  let supply = net;
  let vat = 0;
  let gross = net;
  if (s.vatMode === 'add') {
    vat = money((net * rate) / 100);
    gross = net + vat;
  } else if (s.vatMode === 'included') {
    supply = money(net / (1 + rate / 100));
    vat = net - supply;
    gross = net;
  }
  const unit = isNum(s.quote.roundDown) && s.quote.roundDown > 1 ? s.quote.roundDown : 1;
  const total = Math.floor(gross / unit) * unit;
  const margin = supply - money(costTotal);

  return {
    rooms,
    totals: {
      curtainRooms,
      curtainWidths,
      curtainLength: clean(curtainLength),
      blindRooms,
      blindCount,
      blindMeasuredArea: clean(blindMeasuredArea),
      blindBillArea: clean(blindBillArea),
      cat,
      roomSubtotal,
      roomDiscount,
      roomsNet,
      travel,
      shipping,
      siteDiscount,
      net,
      supply,
      vat,
      gross,
      roundAdj: gross - total,
      total,
      costTotal: money(costTotal),
      costKnown,
      margin,
      marginRate: supply > 0 ? clean((margin / supply) * 100) : 0,
      pendingRooms,
      issues,
    },
  };
}
