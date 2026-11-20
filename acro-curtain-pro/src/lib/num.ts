// 숫자 처리 공통 규칙 — 모든 계산·표시가 이 파일의 규칙 하나만 따른다.
// 내부 길이 단위는 항상 cm.

/** 부동소수 잡음 제거(소수 6자리). 300 × 1.1 = 330.00000000000006 → 330 */
export function clean(v: number): number {
  return Math.round(v * 1e6) / 1e6;
}

/** 안전한 올림. 3.0000000000000004 같은 잡음이 4로 올라가는 오류를 막는다. */
export function ceilSafe(v: number): number {
  return Math.ceil(clean(v) - 1e-9);
}

export function floorSafe(v: number): number {
  return Math.floor(clean(v) + 1e-9);
}

/** unit 단위로 올림. unit이 0 이하이면 그대로. */
export function ceilTo(v: number, unit: number): number {
  if (!(unit > 0)) return clean(v);
  return clean(ceilSafe(v / unit) * unit);
}

export function floorTo(v: number, unit: number): number {
  if (!(unit > 0)) return clean(v);
  return clean(floorSafe(v / unit) * unit);
}

export function roundTo(v: number, unit: number): number {
  if (!(unit > 0)) return clean(v);
  return clean(Math.round(clean(v / unit)) * unit);
}

export type RoundMode = 'ceil' | 'round' | 'floor';

export function roundBy(v: number, unit: number, mode: RoundMode): number {
  if (mode === 'ceil') return ceilTo(v, unit);
  if (mode === 'floor') return floorTo(v, unit);
  return roundTo(v, unit);
}

export function isNum(v: unknown): v is number {
  return typeof v === 'number' && Number.isFinite(v);
}

/** null·NaN·Infinity를 0으로 */
export function n0(v: number | null | undefined): number {
  return isNum(v) ? v : 0;
}

/**
 * 입력 문자열 해석. 빈 값 → null, 해석 불가 → NaN.
 * "1,234.5" · " 360 " · "２４０"(전각) 허용.
 */
export function parseNum(text: string): number | null {
  const t = text
    .replace(/[０-９]/g, (c) => String.fromCharCode(c.charCodeAt(0) - 0xfee0))
    .replace(/[．。]/g, '.')
    .replace(/[,\s]/g, '')
    .trim();
  if (t === '') return null;
  if (!/^-?(\d+\.?\d*|\.\d+)$/.test(t)) return NaN;
  const v = Number(t);
  return Number.isFinite(v) ? v : NaN;
}

const nf = (min: number, max: number) =>
  new Intl.NumberFormat('ko-KR', { minimumFractionDigits: min, maximumFractionDigits: max });

/** 천 단위 구분 + 소수 최대 dec자리(뒤 0 제거) */
export function fmt(v: number, dec = 1): string {
  if (!isNum(v)) return '–';
  return nf(0, dec).format(clean(v));
}

/** 고정 소수 자리 */
export function fmtFixed(v: number, dec: number): string {
  if (!isNum(v)) return '–';
  return nf(dec, dec).format(clean(v));
}

/** cm → m 표시 (최소 1자리, 최대 2자리). 1040 → "10.4", 1300 → "13.0", 789 → "7.89" */
export function fmtMeters(cm: number): string {
  if (!isNum(cm)) return '–';
  return nf(1, 2).format(clean(cm / 100));
}

export function won(v: number): string {
  if (!isNum(v)) return '–';
  return `${new Intl.NumberFormat('ko-KR').format(Math.round(v))}원`;
}

/** 1,234,000 → "123만 4,000원" */
export function koreanWon(v: number): string {
  if (!isNum(v)) return '–';
  let n = Math.round(Math.abs(v));
  const sign = v < 0 ? '−' : '';
  if (n === 0) return '0원';
  const eok = Math.floor(n / 1e8);
  n %= 1e8;
  const man = Math.floor(n / 1e4);
  const rest = n % 1e4;
  const f = new Intl.NumberFormat('ko-KR');
  const parts: string[] = [];
  if (eok) parts.push(`${f.format(eok)}억`);
  if (man) parts.push(`${f.format(man)}만`);
  if (rest) parts.push(f.format(rest));
  return `${sign}${parts.join(' ')}원`;
}

// ── 측정 단위 ──────────────────────────────────────────────
export type Unit = 'cm' | 'mm' | 'm';

export const UNIT_SCALE: Record<Unit, number> = { mm: 10, cm: 1, m: 0.01 };
export const UNIT_DEC: Record<Unit, number> = { mm: 0, cm: 1, m: 3 };

/** cm 값을 표시 단위 수치로 */
export function toUnit(cm: number, unit: Unit): number {
  return clean(cm * UNIT_SCALE[unit]);
}

/** 표시 단위 수치를 cm로 */
export function fromUnit(v: number, unit: Unit): number {
  return clean(v / UNIT_SCALE[unit]);
}

/** cm 길이를 단위 붙여 표시 */
export function fmtLen(cm: number, unit: Unit, withUnit = true): string {
  if (!isNum(cm)) return '–';
  const s = fmt(toUnit(cm, unit), UNIT_DEC[unit]);
  return withUnit ? `${s}${unit}` : s;
}

export function uid(prefix = 'id'): string {
  return `${prefix}_${Date.now().toString(36)}${Math.random().toString(36).slice(2, 7)}`;
}
