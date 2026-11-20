import { uid } from './num';
import type {
  AppState,
  BlindPreset,
  BlindRoom,
  BlindRule,
  BlindType,
  CurtainPricing,
  CurtainRoom,
  CutSettings,
  Settings,
  Site,
  SpaceName,
} from './types';
import { BLIND_TYPES } from './types';

/** 기본 재단 여유: 상단 10 + 하단 10 = 20cm (임시 기본값). 나머지는 0 = 미적용 */
export const DEFAULT_CUT: CutSettings = {
  top: 10,
  bottom: 10,
  other: 0,
  seamLoss: 0,
  sideHem: 0,
  shrinkPct: 0,
  patternRepeat: 0,
  roundUnit: 0,
};

export const EMPTY_CURTAIN_PRICING: CurtainPricing = {
  fabric: { mode: 'perMeter', price: null, cost: null },
  sewing: { mode: 'perWidth', price: null, cost: null },
  hardware: { mode: 'fixed', price: null, cost: null },
  rail: { mode: 'perMeter', price: null, cost: null },
  install: { mode: 'fixed', price: null, cost: null },
  options: [],
};

const zeroAdjust = { deductW: 0, addW: 0, deductH: 0, addH: 0 };

/** 블라인드 프리셋 — 제조사 기준은 확정하지 않는다. 모두 0·미확인 상태로 시작 */
export function makeBlindPreset(): BlindPreset {
  return {
    verified: false,
    makerNote: '',
    byMount: { inside: { ...zeroAdjust }, outside: { ...zeroAdjust }, ceiling: { ...zeroAdjust } },
    minW: 0,
    maxW: 0,
    minH: 0,
    maxH: 0,
    roundUnit: 0,
    roundMode: 'round',
    billing: { basis: 'order', minBillW: 0, minBillH: 0, minBillArea: 0, areaRoundUnit: 0, minCharge: 0 },
    priceMode: 'area',
    unitPrice: null,
    unitCost: null,
    install: null,
  };
}

export function defaultSettings(): Settings {
  const blindPresets = {} as Record<BlindType, BlindPreset>;
  BLIND_TYPES.forEach((t) => (blindPresets[t] = makeBlindPreset()));
  return {
    unit: 'cm',
    theme: 'system',
    curtain: {
      fabricWidth: 145,
      fullness: 1.5,
      opening: 'double',
      method: 'joined',
      curtainType: '겉커튼',
      wideThreshold: 250,
      widthMode: 'field',
      dropFraction: 0.2,
      pricing: structuredCloneSafe(EMPTY_CURTAIN_PRICING),
    },
    cut: { ...DEFAULT_CUT },
    blindPresets,
    vatRate: 10,
    vatMode: 'add',
    quote: {
      companyName: 'ACRO',
      companyContact: '',
      companyAddress: '',
      bizNumber: '',
      validDays: 14,
      footer: '본 견적은 실측 기준이며, 원단 재고·제조사 사정에 따라 변경될 수 있습니다.',
      detail: 'itemized',
      showNotes: false,
      roundDown: 1,
    },
    adminMode: false,
    marginRate: 30,
  };
}

export function structuredCloneSafe<T>(v: T): T {
  return JSON.parse(JSON.stringify(v)) as T;
}

export function ruleFromPreset(p: BlindPreset, mount: keyof BlindPreset['byMount']): BlindRule {
  return {
    ...p.byMount[mount],
    minW: p.minW,
    maxW: p.maxW,
    minH: p.minH,
    maxH: p.maxH,
    roundUnit: p.roundUnit,
    roundMode: p.roundMode,
  };
}

export function newCurtainRoom(s: Settings, space: SpaceName = '거실', location = ''): CurtainRoom {
  const c = s.curtain;
  return {
    id: uid('c'),
    kind: 'curtain',
    space,
    spaceCustom: '',
    location,
    width: null,
    height: null,
    fabricWidth: c.fabricWidth,
    fullness: c.fullness,
    curtainType: c.curtainType,
    curtainTypeCustom: '',
    opening: c.opening,
    gatherSide: 'left',
    splitLeft: 50,
    splitRight: 50,
    method: c.method,
    cutOverride: null,
    pricing: structuredCloneSafe(c.pricing),
    discount: { type: 'rate', value: null },
    memo: '',
  };
}

export function newBlindRoom(s: Settings, space: SpaceName = '작은방', location = '', type: BlindType = '콤비블라인드'): BlindRoom {
  const p = s.blindPresets[type];
  return {
    id: uid('b'),
    kind: 'blind',
    space,
    spaceCustom: '',
    location,
    width: null,
    height: null,
    mount: 'inside',
    blindType: type,
    blindTypeCustom: '',
    qty: 1,
    priceMode: p.priceMode,
    unitPrice: p.unitPrice,
    unitCost: p.unitCost,
    install: p.install,
    installCost: null,
    customRule: null,
    options: [],
    discount: { type: 'rate', value: null },
    memo: '',
  };
}

export function emptySite(s: Settings): Site {
  const now = Date.now();
  return {
    id: uid('site'),
    info: { apartment: '', dongho: '', customer: '', phone: '', surveyor: '', date: today(), notes: '' },
    rooms: [newCurtainRoom(s, '거실')],
    common: { travelFee: null, shippingFee: null, travelCost: null, shippingCost: null, discount: { type: 'amount', value: null } },
    isSample: false,
    createdAt: now,
    updatedAt: now,
  };
}

export function today(): string {
  const d = new Date();
  const p = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

/** 처음 실행 시 보여주는 예시 현장 (예시 단가 포함 — 화면에 '예시'로 표시) */
export function sampleSite(s: Settings): Site {
  const site = emptySite(s);
  site.isSample = true;
  site.info = {
    apartment: '예시 아파트',
    dongho: '101동 1203호',
    customer: '홍길동',
    phone: '',
    surveyor: '',
    date: today(),
    notes: '예시 데이터입니다. 상단 「새 현장」으로 비우고 시작하세요.',
  };
  const examplePricing: CurtainPricing = {
    fabric: { mode: 'perMeter', price: 18000, cost: null },
    sewing: { mode: 'perWidth', price: 12000, cost: null },
    hardware: { mode: 'fixed', price: 15000, cost: null },
    rail: { mode: 'perMeter', price: 9000, cost: null },
    install: { mode: 'fixed', price: 30000, cost: null },
    options: [],
  };
  const living = newCurtainRoom(s, '거실', '거실 전면창');
  Object.assign(living, { width: 420, height: 240, fullness: 1.5, curtainType: '암막커튼', pricing: structuredCloneSafe(examplePricing) });
  const master = newCurtainRoom(s, '안방', '안방 창');
  Object.assign(master, { width: 300, height: 230, fullness: 2.0, curtainType: '겉커튼', pricing: structuredCloneSafe(examplePricing) });
  const small1 = newBlindRoom(s, '작은방', '작은방 1', '콤비블라인드');
  Object.assign(small1, { width: 180, height: 220, priceMode: 'area', unitPrice: 32000, install: 10000 });
  const small2 = newBlindRoom(s, '작은방', '작은방 2', '롤스크린');
  Object.assign(small2, { width: 160, height: 220, priceMode: 'area', unitPrice: 26000, install: 10000 });
  site.rooms = [living, master, small1, small2];
  site.common = { ...site.common, travelFee: 0, shippingFee: 0 };
  return site;
}

export function initialState(): AppState {
  const settings = defaultSettings();
  const site = sampleSite(settings);
  return {
    version: 1,
    settings,
    site,
    recent: [],
    profiles: [],
    ui: {
      tab: 'curtain',
      activeCurtain: site.rooms.find((r) => r.kind === 'curtain')?.id ?? null,
      activeBlind: site.rooms.find((r) => r.kind === 'blind')?.id ?? null,
      siteOpen: false,
    },
  };
}

export function roomLabel(r: { space: SpaceName; spaceCustom: string; location: string }): string {
  if (r.location.trim()) return r.location.trim();
  if (r.space === '기타') return r.spaceCustom.trim() || '기타 공간';
  return r.space;
}
