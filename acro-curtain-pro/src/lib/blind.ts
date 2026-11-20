// 블라인드 제작 사이즈·면적 산출 — 커튼 주름 배수를 쓰지 않는다.
import { ceilTo, clean, isNum, roundBy } from './num';
import { josa } from './josa';
import type { BlindBilling, BlindRule, Issue } from './types';

export interface BlindInput {
  width: number | null;
  height: number | null;
  qty: number | null;
  rule: BlindRule;
  billing: BlindBilling;
  verified: boolean; // 제조사 기준 확인 여부
}

export interface BlindResult {
  ok: boolean;
  producible: boolean;
  issues: Issue[];
  width: number;
  height: number;
  qty: number;
  orderW: number; // 주문 제작 가로
  orderH: number;
  measuredArea: number; // 실측 면적 ㎡ (장당)
  orderArea: number; // 주문 제작 면적 ㎡ (장당)
  billW: number;
  billH: number;
  billArea: number; // 견적 청구 면적 ㎡ (장당)
  billAreaTotal: number; // × 수량
  measuredAreaTotal: number;
  minAreaApplied: boolean;
  minSizeApplied: boolean;
}

const empty = (issues: Issue[]): BlindResult => ({
  ok: false,
  producible: false,
  issues,
  width: 0,
  height: 0,
  qty: 0,
  orderW: 0,
  orderH: 0,
  measuredArea: 0,
  orderArea: 0,
  billW: 0,
  billH: 0,
  billArea: 0,
  billAreaTotal: 0,
  measuredAreaTotal: 0,
  minAreaApplied: false,
  minSizeApplied: false,
});

/** cm × cm → ㎡ */
export const areaM2 = (wCm: number, hCm: number) => clean((wCm / 100) * (hCm / 100));

export function calcBlind(inp: BlindInput): BlindResult {
  const issues: Issue[] = [];
  const dim = (v: number | null, field: string, name: string): v is number => {
    if (v === null) {
      issues.push({ level: 'error', field, code: 'empty', message: `${josa(name, '을/를')} 입력하세요.` });
      return false;
    }
    if (!isNum(v)) {
      issues.push({ level: 'error', field, message: `${name}에는 숫자만 입력할 수 있습니다.` });
      return false;
    }
    if (v <= 0) {
      issues.push({ level: 'error', field, message: `${josa(name, '은/는')} 0보다 커야 합니다.` });
      return false;
    }
    if (v > 5000) {
      issues.push({ level: 'error', field, message: `${josa(name, '이/가')} 50m를 넘습니다. 입력값을 확인하세요.` });
      return false;
    }
    if (v > 800) issues.push({ level: 'warning', field, message: `${josa(name, '이/가')} 8m를 넘습니다. 단위(cm·mm)를 확인하세요.` });
    return true;
  };
  const okW = dim(inp.width, 'width', '실측 가로');
  const okH = dim(inp.height, 'height', '실측 세로');
  let qty = 1;
  if (inp.qty === null || !isNum(inp.qty)) {
    issues.push({ level: 'error', field: 'qty', message: '수량을 입력하세요.' });
  } else if (inp.qty < 1 || !Number.isInteger(inp.qty)) {
    issues.push({ level: 'error', field: 'qty', message: '수량은 1 이상의 정수로 입력하세요.' });
  } else if (inp.qty > 999) {
    issues.push({ level: 'error', field: 'qty', message: '수량이 너무 큽니다. 입력값을 확인하세요.' });
  } else qty = inp.qty;

  const r = inp.rule;
  const numeric: (keyof BlindRule)[] = ['deductW', 'addW', 'deductH', 'addH', 'minW', 'maxW', 'minH', 'maxH', 'roundUnit'];
  for (const k of numeric) {
    const v = r[k] as number;
    if (!isNum(v) || v < 0) issues.push({ level: 'error', field: `rule.${k}`, message: '제작 기준 값은 0 이상의 숫자여야 합니다.' });
  }
  const b = inp.billing;
  for (const v of [b.minBillW, b.minBillH, b.minBillArea, b.areaRoundUnit, b.minCharge]) {
    if (!isNum(v) || v < 0) {
      issues.push({ level: 'error', field: 'billing', message: '청구 기준 값은 0 이상의 숫자여야 합니다.' });
      break;
    }
  }
  if (!okW || !okH || issues.some((i) => i.level === 'error')) return empty(issues);

  const W = inp.width as number;
  const H = inp.height as number;

  const rawW = clean(W - r.deductW + r.addW);
  const rawH = clean(H - r.deductH + r.addH);
  if (rawW <= 0 || rawH <= 0) {
    issues.push({ level: 'error', field: 'rule', message: '공제값이 실측 사이즈보다 커서 제작 사이즈가 0 이하입니다.' });
    return empty(issues);
  }
  const orderW = r.roundUnit > 0 ? roundBy(rawW, r.roundUnit, r.roundMode) : rawW;
  const orderH = r.roundUnit > 0 ? roundBy(rawH, r.roundUnit, r.roundMode) : rawH;

  let producible = true;
  if (r.minW > 0 && orderW < r.minW) {
    producible = false;
    issues.push({ level: 'critical', field: 'width', message: `주문 가로 ${orderW}cm가 최소 제작 폭 ${r.minW}cm보다 작습니다.` });
  }
  if (r.maxW > 0 && orderW > r.maxW) {
    producible = false;
    issues.push({ level: 'critical', field: 'width', message: `주문 가로 ${orderW}cm가 제작 가능 최대 폭 ${r.maxW}cm를 초과합니다.` });
  }
  if (r.minH > 0 && orderH < r.minH) {
    producible = false;
    issues.push({ level: 'critical', field: 'height', message: `주문 세로 ${orderH}cm가 최소 제작 높이 ${r.minH}cm보다 작습니다.` });
  }
  if (r.maxH > 0 && orderH > r.maxH) {
    producible = false;
    issues.push({ level: 'critical', field: 'height', message: `주문 세로 ${orderH}cm가 제작 가능 최대 높이 ${r.maxH}cm를 초과합니다.` });
  }
  if (!inp.verified) {
    issues.push({
      level: 'warning',
      code: 'unverified',
      message: '제작 기준 확인 필요 — 이 제품의 제조사 공제·제작 기준이 아직 설정되지 않았습니다. 입력한 값만 적용했습니다.',
    });
  }

  const measuredArea = areaM2(W, H);
  const orderArea = areaM2(orderW, orderH);
  const basisW = b.basis === 'order' ? orderW : W;
  const basisH = b.basis === 'order' ? orderH : H;
  const billW = Math.max(basisW, b.minBillW);
  const billH = Math.max(basisH, b.minBillH);
  const minSizeApplied = billW !== basisW || billH !== basisH;
  let billArea = areaM2(billW, billH);
  let minAreaApplied = false;
  if (b.minBillArea > 0 && billArea < b.minBillArea) {
    billArea = b.minBillArea;
    minAreaApplied = true;
  }
  if (b.areaRoundUnit > 0) billArea = ceilTo(billArea, b.areaRoundUnit);

  return {
    ok: true,
    producible,
    issues,
    width: W,
    height: H,
    qty,
    orderW,
    orderH,
    measuredArea,
    orderArea,
    billW,
    billH,
    billArea,
    billAreaTotal: clean(billArea * qty),
    measuredAreaTotal: clean(measuredArea * qty),
    minAreaApplied,
    minSizeApplied,
  };
}
