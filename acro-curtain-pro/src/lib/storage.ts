// 로컬 저장소 — 모든 데이터는 이 기기 브라우저에만 저장된다. 외부 전송 없음.
import { DEFAULT_CUT, defaultSettings, emptySite, initialState, newBlindRoom, newCurtainRoom } from './defaults';
import { isNum } from './num';
import type { AppState, BlindRule, RecentSite, Room, Settings, SettingsProfile, Site } from './types';
import { BLIND_TYPES, CURTAIN_TYPES, SPACES } from './types';

export const STORAGE_KEY = 'acro-curtain-pro:v1';
export const HISTORY_KEY = 'acro-curtain-pro:v1:history';

const ENUMS: Record<string, readonly string[]> = {
  mode: ['perMeter', 'perWidth', 'fixed'],
  opening: ['single', 'double'],
  method: ['joined', 'wide'],
  unit: ['cm', 'mm', 'm'],
  theme: ['system', 'light', 'dark'],
  vatMode: ['add', 'included', 'none'],
  detail: ['itemized', 'room'],
  roundMode: ['ceil', 'round', 'floor'],
  basis: ['order', 'measured'],
  priceMode: ['area', 'each'],
  mount: ['inside', 'outside', 'ceiling'],
  type: ['rate', 'amount'],
  gatherSide: ['left', 'right'],
  space: SPACES,
  curtainType: CURTAIN_TYPES,
  blindType: BLIND_TYPES,
};

const OPTION_TEMPLATE = { id: '', label: '', amount: null, cost: null };
const RULE_TEMPLATE: BlindRule = {
  deductW: 0,
  addW: 0,
  deductH: 0,
  addH: 0,
  minW: 0,
  maxW: 0,
  minH: 0,
  maxH: 0,
  roundUnit: 0,
  roundMode: 'round',
};
const NULLABLE_OBJECT: Record<string, unknown> = { cutOverride: DEFAULT_CUT, customRule: RULE_TEMPLATE };

const isObj = (v: unknown): v is Record<string, unknown> => typeof v === 'object' && v !== null && !Array.isArray(v);

/** 기본값(def)의 모양에 맞춰 raw를 정리한다. 모르는 키는 버리고, 형식이 틀린 값은 기본값으로. */
export function shape<T>(def: T, raw: unknown, key = ''): T {
  if (key in NULLABLE_OBJECT) {
    if (raw === null || raw === undefined) return null as T;
    return (isObj(raw) ? shape(NULLABLE_OBJECT[key], raw) : null) as T;
  }
  if (def === null) return (raw === null ? null : isNum(raw) ? raw : null) as T;
  if (typeof def === 'number') return (isNum(raw) ? raw : def) as T;
  if (typeof def === 'boolean') return (typeof raw === 'boolean' ? raw : def) as T;
  if (typeof def === 'string') {
    if (typeof raw !== 'string') return def;
    if (ENUMS[key] && !ENUMS[key].includes(raw)) return def;
    return raw.slice(0, 4000) as T;
  }
  if (Array.isArray(def)) {
    if (!Array.isArray(raw)) return def;
    if (key === 'options') return raw.filter(isObj).slice(0, 50).map((o) => shape(OPTION_TEMPLATE, o)) as T;
    return def;
  }
  if (isObj(def)) {
    const src = isObj(raw) ? raw : {};
    const out: Record<string, unknown> = {};
    for (const k of Object.keys(def)) out[k] = shape((def as Record<string, unknown>)[k], src[k], k);
    return out as T;
  }
  return def;
}

export function sanitizeSettings(raw: unknown): Settings {
  return shape(defaultSettings(), raw);
}

export function sanitizeRoom(raw: unknown, s: Settings): Room | null {
  if (!isObj(raw)) return null;
  const id = typeof raw.id === 'string' && raw.id ? raw.id : null;
  if (raw.kind === 'curtain') {
    const r = shape(newCurtainRoom(s), raw);
    return id ? { ...r, id } : r;
  }
  if (raw.kind === 'blind') {
    const r = shape(newBlindRoom(s), raw);
    return id ? { ...r, id } : r;
  }
  return null;
}

export function sanitizeSite(raw: unknown, s: Settings): Site {
  const base = emptySite(s);
  if (!isObj(raw)) return base;
  const out = shape({ ...base, rooms: [] as Room[] }, raw);
  out.id = typeof raw.id === 'string' && raw.id ? raw.id : base.id;
  const rooms = Array.isArray(raw.rooms) ? raw.rooms.map((r) => sanitizeRoom(r, s)).filter((r): r is Room => r !== null) : [];
  out.rooms = rooms.slice(0, 80);
  if (!out.rooms.length) out.rooms = base.rooms;
  return out;
}

export function sanitizeState(raw: unknown): AppState {
  const init = initialState();
  if (!isObj(raw)) return init;
  const settings = sanitizeSettings(raw.settings);
  const site = sanitizeSite(raw.site, settings);
  const recent: RecentSite[] = Array.isArray(raw.recent)
    ? raw.recent
        .filter(isObj)
        .slice(0, 30)
        .map((e) => ({
          id: typeof e.id === 'string' ? e.id : String(Math.random()),
          savedAt: isNum(e.savedAt) ? e.savedAt : Date.now(),
          site: sanitizeSite(e.site, settings),
        }))
    : [];
  const profiles: SettingsProfile[] = Array.isArray(raw.profiles)
    ? raw.profiles
        .filter(isObj)
        .slice(0, 30)
        .map((p) => ({
          id: typeof p.id === 'string' ? p.id : String(Math.random()),
          name: typeof p.name === 'string' ? p.name.slice(0, 60) : '이름 없는 프리셋',
          savedAt: isNum(p.savedAt) ? p.savedAt : Date.now(),
          settings: sanitizeSettings(p.settings),
        }))
    : [];
  const ui = isObj(raw.ui) ? raw.ui : {};
  const has = (id: unknown, kind: Room['kind']) => typeof id === 'string' && site.rooms.some((r) => r.id === id && r.kind === kind);
  return {
    version: 1,
    settings,
    site,
    recent,
    profiles,
    ui: {
      tab: ui.tab === 'blind' || ui.tab === 'settings' ? ui.tab : 'curtain',
      activeCurtain: has(ui.activeCurtain, 'curtain') ? (ui.activeCurtain as string) : site.rooms.find((r) => r.kind === 'curtain')?.id ?? null,
      activeBlind: has(ui.activeBlind, 'blind') ? (ui.activeBlind as string) : site.rooms.find((r) => r.kind === 'blind')?.id ?? null,
      siteOpen: typeof ui.siteOpen === 'boolean' ? ui.siteOpen : false,
    },
  };
}

export function safeGet(key: string): string | null {
  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
}

export function safeSet(key: string, value: string): boolean {
  try {
    window.localStorage.setItem(key, value);
    return true;
  } catch {
    return false;
  }
}

export function safeRemove(key: string) {
  try {
    window.localStorage.removeItem(key);
  } catch {
    /* 저장소 접근 불가 — 무시 */
  }
}

export interface LoadResult {
  state: AppState;
  status: 'fresh' | 'loaded' | 'recovered';
}

export function parseState(text: string | null): LoadResult {
  if (text === null) return { state: initialState(), status: 'fresh' };
  try {
    const raw = JSON.parse(text);
    if (!isObj(raw) || raw.version !== 1) return { state: sanitizeState(raw), status: 'recovered' };
    return { state: sanitizeState(raw), status: 'loaded' };
  } catch {
    return { state: initialState(), status: 'recovered' };
  }
}

export function loadState(): LoadResult {
  return parseState(safeGet(STORAGE_KEY));
}

export function saveState(st: AppState): boolean {
  return safeSet(STORAGE_KEY, JSON.stringify(st));
}

export function loadHistory(s: Settings): Site[] {
  try {
    const raw = JSON.parse(safeGet(HISTORY_KEY) ?? '[]');
    return Array.isArray(raw) ? raw.slice(0, 15).map((x) => sanitizeSite(x, s)) : [];
  } catch {
    return [];
  }
}

export function saveHistory(h: Site[]) {
  safeSet(HISTORY_KEY, JSON.stringify(h.slice(0, 15)));
}

/** 내보내기 파일 형식 */
export interface ExportFile {
  app: 'ACRO CURTAIN PRO';
  format: 1;
  exportedAt: string;
  state: AppState;
}

export function exportJson(st: AppState): string {
  const f: ExportFile = { app: 'ACRO CURTAIN PRO', format: 1, exportedAt: new Date().toISOString(), state: st };
  return JSON.stringify(f, null, 2);
}

export function importJson(text: string): { ok: true; state: AppState } | { ok: false; message: string } {
  let raw: unknown;
  try {
    raw = JSON.parse(text);
  } catch {
    return { ok: false, message: 'JSON 형식이 아닙니다. 내보낸 파일 내용을 그대로 붙여 넣으세요.' };
  }
  if (!isObj(raw)) return { ok: false, message: '파일 내용이 비어 있거나 손상되었습니다.' };
  const body = raw.app === 'ACRO CURTAIN PRO' && isObj(raw.state) ? raw.state : raw;
  if (!isObj(body) || (!isObj(body.site) && !isObj(body.settings)))
    return { ok: false, message: 'ACRO CURTAIN PRO에서 내보낸 데이터가 아닙니다.' };
  return { ok: true, state: sanitizeState({ version: 1, ...body }) };
}
