import type { RoundMode, Unit } from './num';

// ── 공통 ──────────────────────────────────────────────────
export type IssueLevel = 'error' | 'critical' | 'warning' | 'info';
/**
 * error    : 입력값이 잘못되어 계산 불가 (결과 숫자 표시 안 함)
 * critical : 계산은 되지만 이대로는 제작 불가 (원단 높이 부족·제작 범위 초과)
 * warning  : 확인 권장 (단위 실수 의심 등)
 * info     : 참고 안내
 */
export interface Issue {
  level: IssueLevel;
  message: string;
  field?: string;
  code?: string;
}

export const SPACES = ['거실', '안방', '작은방', '드레스룸', '주방', '기타'] as const;
export type SpaceName = (typeof SPACES)[number];

export interface Discount {
  type: 'rate' | 'amount';
  value: number | null;
}

export interface OptionItem {
  id: string;
  label: string;
  amount: number | null;
  cost?: number | null;
}

// ── 커튼 ──────────────────────────────────────────────────
export type Opening = 'single' | 'double'; // 편개 / 양개
export type CurtainMethod = 'joined' | 'wide'; // 폭 연결형 / 광폭 원단형
export const CURTAIN_TYPES = ['겉커튼', '속커튼', '암막커튼', '기타'] as const;
export type CurtainType = (typeof CURTAIN_TYPES)[number];

/** 재단·제작 여유 (모두 cm, 수축만 %) — 서로 독립, 중복 계산 없음 */
export interface CutSettings {
  top: number; // 상단 재단 여유
  bottom: number; // 하단 재단 여유
  other: number; // 기타 제조 여유 (세로 방향 추가)
  seamLoss: number; // 폭 연결 시 이음 1곳당 봉제 손실
  sideHem: number; // 커튼 한 장의 좌·우 옆단 여유 (한쪽당)
  shrinkPct: number; // 수축 여유율 %
  patternRepeat: number; // 무늬 반복 길이 (0 = 무지)
  roundUnit: number; // 재단 길이 올림 단위 (0 = 올림 없음)
}

export interface PriceLine<M extends string> {
  mode: M;
  price: number | null;
  cost?: number | null; // 관리자 원가 (고객 출력물에 절대 노출 안 함)
}

export interface CurtainPricing {
  fabric: PriceLine<'perMeter' | 'perWidth'>;
  sewing: PriceLine<'perWidth' | 'perMeter' | 'fixed'>;
  hardware: PriceLine<'fixed'>;
  rail: PriceLine<'perMeter' | 'fixed'>;
  install: PriceLine<'fixed'>;
  options: OptionItem[];
}

export interface CurtainRoom {
  id: string;
  kind: 'curtain';
  space: SpaceName;
  spaceCustom: string;
  location: string;
  width: number | null; // 실측 가로 cm
  height: number | null; // 실측 세로 cm
  fabricWidth: number | null; // 원단 1폭 cm (광폭형에서는 롤 폭)
  fullness: number | null; // 주름 배수
  curtainType: CurtainType;
  curtainTypeCustom: string;
  opening: Opening;
  gatherSide: 'left' | 'right'; // 편개: 커튼이 모이는 쪽
  splitLeft: number | null; // 양개 좌측 %
  splitRight: number | null; // 양개 우측 %
  method: CurtainMethod;
  cutOverride: CutSettings | null; // null = 환경설정 값 사용
  pricing: CurtainPricing;
  discount: Discount;
  memo: string;
}

// ── 블라인드 ──────────────────────────────────────────────
export const BLIND_TYPES = [
  '콤비블라인드',
  '롤스크린',
  '암막 롤스크린',
  '우드블라인드',
  '알루미늄블라인드',
  '허니콤블라인드',
  '기타',
] as const;
export type BlindType = (typeof BLIND_TYPES)[number];

export type Mount = 'inside' | 'outside' | 'ceiling';
export const MOUNTS: { value: Mount; label: string }[] = [
  { value: 'inside', label: '창틀 안쪽' },
  { value: 'outside', label: '창틀 바깥쪽' },
  { value: 'ceiling', label: '천장 설치' },
];

export interface SizeAdjust {
  deductW: number;
  addW: number;
  deductH: number;
  addH: number;
}

/** 제작 규칙 — 제조사마다 다르므로 사용자가 입력. 0 = 미설정 */
export interface BlindRule extends SizeAdjust {
  minW: number;
  maxW: number;
  minH: number;
  maxH: number;
  roundUnit: number;
  roundMode: RoundMode;
}

export interface BlindBilling {
  basis: 'order' | 'measured'; // 청구 면적 기준
  minBillW: number; // 최소 청구 가로 cm
  minBillH: number; // 최소 청구 세로 cm
  minBillArea: number; // 최소 청구 면적 ㎡ (장당)
  areaRoundUnit: number; // 청구 면적 올림 단위 ㎡ (0 = 없음)
  minCharge: number; // 최소 제작 요금 (장당 원)
}

export interface BlindPreset {
  verified: boolean; // 제조사 기준을 입력·확인했는가
  makerNote: string; // 기준 출처 메모 (예: OO블라인드 2026 단가표)
  byMount: Record<Mount, SizeAdjust>;
  minW: number;
  maxW: number;
  minH: number;
  maxH: number;
  roundUnit: number;
  roundMode: RoundMode;
  billing: BlindBilling;
  priceMode: 'area' | 'each';
  unitPrice: number | null;
  unitCost: number | null;
  install: number | null; // 장당 설치비
}

export interface BlindRoom {
  id: string;
  kind: 'blind';
  space: SpaceName;
  spaceCustom: string;
  location: string;
  width: number | null;
  height: number | null;
  mount: Mount;
  blindType: BlindType;
  blindTypeCustom: string;
  qty: number | null;
  priceMode: 'area' | 'each';
  unitPrice: number | null;
  unitCost: number | null;
  install: number | null; // 장당 설치비
  installCost: number | null;
  customRule: BlindRule | null; // null = 프리셋 사용
  options: OptionItem[];
  discount: Discount;
  memo: string;
}

export type Room = CurtainRoom | BlindRoom;

// ── 현장 ──────────────────────────────────────────────────
export interface SiteInfo {
  apartment: string;
  dongho: string; // 동/호수
  customer: string;
  phone: string;
  surveyor: string; // 실측 담당자
  date: string; // YYYY-MM-DD
  notes: string;
}

export interface SiteCommon {
  travelFee: number | null; // 출장비 (현장 1회)
  shippingFee: number | null; // 배송비
  travelCost?: number | null;
  shippingCost?: number | null;
  discount: Discount; // 현장 전체 추가 할인
}

export interface Site {
  id: string;
  info: SiteInfo;
  rooms: Room[];
  common: SiteCommon;
  isSample: boolean;
  createdAt: number;
  updatedAt: number;
}

// ── 설정 ──────────────────────────────────────────────────
export type VatMode = 'add' | 'included' | 'none';

export interface CurtainDefaults {
  fabricWidth: number;
  fullness: number;
  opening: Opening;
  method: CurtainMethod;
  curtainType: CurtainType;
  wideThreshold: number; // 이 폭 이상이면 광폭 원단 안내
  pricing: CurtainPricing;
}

export interface QuoteTemplate {
  companyName: string;
  companyContact: string;
  companyAddress: string;
  bizNumber: string;
  validDays: number;
  footer: string;
  detail: 'itemized' | 'room'; // 항목별 상세 / 공간별 합계
  showNotes: boolean; // 특이사항을 견적서에 표시
  roundDown: number; // 최종 금액 끝전 절사 단위 (1 = 없음)
}

export interface Settings {
  unit: Unit;
  theme: 'system' | 'light' | 'dark';
  curtain: CurtainDefaults;
  cut: CutSettings;
  blindPresets: Record<BlindType, BlindPreset>;
  vatRate: number;
  vatMode: VatMode;
  quote: QuoteTemplate;
  adminMode: boolean;
  marginRate: number; // 기본 마진율 %
}

export interface SettingsProfile {
  id: string;
  name: string;
  savedAt: number;
  settings: Settings;
}

export interface RecentSite {
  id: string;
  savedAt: number;
  site: Site;
}

export type Tab = 'curtain' | 'blind' | 'settings';

export interface AppState {
  version: 1;
  settings: Settings;
  site: Site;
  recent: RecentSite[];
  profiles: SettingsProfile[];
  ui: {
    tab: Tab;
    activeCurtain: string | null;
    activeBlind: string | null;
    siteOpen: boolean;
  };
}
