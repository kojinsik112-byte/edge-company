import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { calcSite, type SiteCalc } from './lib/quote';
import { loadHistory, loadState, saveHistory, saveState, type LoadResult } from './lib/storage';
import type { AppState, Room, Site } from './lib/types';

export type Checkpoint = 'auto' | 'force' | 'none';

function clone<T>(v: T): T {
  try {
    return structuredClone(v);
  } catch {
    return JSON.parse(JSON.stringify(v)) as T;
  }
}

interface Store {
  state: AppState;
  calc: SiteCalc;
  loadStatus: LoadResult['status'];
  saveFailed: boolean;
  update: (recipe: (d: AppState) => void, cp?: Checkpoint) => void;
  updateRoom: (id: string, recipe: (r: Room) => void, cp?: Checkpoint) => void;
  undo: () => boolean;
  canUndo: boolean;
}

const Ctx = createContext<Store | null>(null);

export function StoreProvider({ children }: { children: ReactNode }) {
  const initial = useMemo(() => loadState(), []);
  const [state, setState] = useState<AppState>(initial.state);
  const [saveFailed, setSaveFailed] = useState(false);
  const history = useRef<Site[]>(loadHistory(initial.state.settings));
  const [histLen, setHistLen] = useState(history.current.length);
  const lastCp = useRef(0);

  // 자동 저장 (0.3초 디바운스)
  useEffect(() => {
    const t = setTimeout(() => setSaveFailed(!saveState(state)), 300);
    return () => clearTimeout(t);
  }, [state]);

  const pushHistory = useCallback((site: Site) => {
    history.current = [clone(site), ...history.current].slice(0, 15);
    setHistLen(history.current.length);
    saveHistory(history.current);
  }, []);

  const update = useCallback(
    (recipe: (d: AppState) => void, cp: Checkpoint = 'auto') => {
      setState((prev) => {
        const next = clone(prev);
        recipe(next);
        const siteChanged = JSON.stringify(prev.site) !== JSON.stringify(next.site);
        if (siteChanged) {
          next.site.updatedAt = Date.now();
          const now = Date.now();
          // 연속 입력은 2초 단위로 하나의 되돌리기 지점으로 묶는다
          if (cp === 'force' || (cp === 'auto' && now - lastCp.current > 2000)) pushHistory(prev.site);
          if (cp !== 'none') lastCp.current = now;
        }
        return next;
      });
    },
    [pushHistory],
  );

  const updateRoom = useCallback(
    (id: string, recipe: (r: Room) => void, cp: Checkpoint = 'auto') =>
      update((d) => {
        const r = d.site.rooms.find((x) => x.id === id);
        if (r) recipe(r);
      }, cp),
    [update],
  );

  const undo = useCallback(() => {
    const [prevSite, ...rest] = history.current;
    if (!prevSite) return false;
    history.current = rest;
    setHistLen(rest.length);
    saveHistory(rest);
    lastCp.current = 0;
    setState((s) => {
      const site = clone(prevSite);
      const has = (id: string | null, kind: Room['kind']) => !!id && site.rooms.some((r) => r.id === id && r.kind === kind);
      return {
        ...s,
        site,
        ui: {
          ...s.ui,
          activeCurtain: has(s.ui.activeCurtain, 'curtain') ? s.ui.activeCurtain : site.rooms.find((r) => r.kind === 'curtain')?.id ?? null,
          activeBlind: has(s.ui.activeBlind, 'blind') ? s.ui.activeBlind : site.rooms.find((r) => r.kind === 'blind')?.id ?? null,
        },
      };
    });
    return true;
  }, []);

  const calc = useMemo(() => calcSite(state.site, state.settings), [state.site, state.settings]);

  const value: Store = {
    state,
    calc,
    loadStatus: initial.status,
    saveFailed,
    update,
    updateRoom,
    undo,
    canUndo: histLen > 0,
  };
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useStore(): Store {
  const s = useContext(Ctx);
  if (!s) throw new Error('StoreProvider missing');
  return s;
}

// ── 토스트·확인창 ─────────────────────────────────────────
interface ConfirmReq {
  title: string;
  body?: string;
  confirmLabel?: string;
  danger?: boolean;
  resolve: (ok: boolean) => void;
}

interface UiCtx {
  toast: (msg: string, tone?: 'ok' | 'warn' | 'err') => void;
  confirm: (o: Omit<ConfirmReq, 'resolve'>) => Promise<boolean>;
  toastState: { msg: string; tone: 'ok' | 'warn' | 'err'; key: number } | null;
  confirmState: ConfirmReq | null;
  closeConfirm: (ok: boolean) => void;
}

const UCtx = createContext<UiCtx | null>(null);

export function UiProvider({ children }: { children: ReactNode }) {
  const [toastState, setToast] = useState<UiCtx['toastState']>(null);
  const [confirmState, setConfirm] = useState<ConfirmReq | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout>>();
  const toast = useCallback((msg: string, tone: 'ok' | 'warn' | 'err' = 'ok') => {
    clearTimeout(timer.current);
    setToast({ msg, tone, key: Date.now() });
    timer.current = setTimeout(() => setToast(null), 2600);
  }, []);
  const confirm = useCallback(
    (o: Omit<ConfirmReq, 'resolve'>) => new Promise<boolean>((resolve) => setConfirm({ ...o, resolve })),
    [],
  );
  const closeConfirm = useCallback(
    (ok: boolean) => {
      confirmState?.resolve(ok);
      setConfirm(null);
    },
    [confirmState],
  );
  return <UCtx.Provider value={{ toast, confirm, toastState, confirmState, closeConfirm }}>{children}</UCtx.Provider>;
}

export function useUi(): UiCtx {
  const u = useContext(UCtx);
  if (!u) throw new Error('UiProvider missing');
  return u;
}

export function useMedia(query: string): boolean {
  const get = () => (typeof window !== 'undefined' && window.matchMedia ? window.matchMedia(query).matches : false);
  const [m, setM] = useState(get);
  useEffect(() => {
    if (!window.matchMedia) return;
    const mq = window.matchMedia(query);
    const on = () => setM(mq.matches);
    on();
    mq.addEventListener?.('change', on);
    return () => mq.removeEventListener?.('change', on);
  }, [query]);
  return m;
}
