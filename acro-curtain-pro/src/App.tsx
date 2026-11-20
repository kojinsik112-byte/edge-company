import { useEffect, useRef, useState } from 'react';
import { BlindTab } from './components/BlindTab';
import { CurtainTab } from './components/CurtainTab';
import { QuoteModal } from './components/Quote';
import { useActiveRoom } from './components/RoomParts';
import { SettingsTab } from './components/SettingsTab';
import { RecentModal, SiteBar, SiteSummary } from './components/Site';
import { copyText, Icon, UiLayer } from './components/ui';
import { fmt, fmtMeters, won } from './lib/num';
import { roomText, siteText } from './lib/text';
import type { Tab } from './lib/types';
import { StoreProvider, UiProvider, useStore, useUi } from './store';

const TABS: { value: Tab; label: string; short: string }[] = [
  { value: 'curtain', label: '커튼 계산기', short: '커튼' },
  { value: 'blind', label: '블라인드 계산기', short: '블라인드' },
  { value: 'settings', label: '환경설정', short: '설정' },
];

function Wordmark() {
  return (
    <div className="flex min-w-0 items-center gap-3">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-[11px] bg-primary text-onprimary" aria-hidden="true">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
          <path d="M4 4h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          <path d="M6 5v15M9.5 5v15M14.5 5v15M18 5v15" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" opacity=".85" />
          <path d="M3 20h18" stroke="rgb(var(--gold))" strokeWidth="2" strokeLinecap="round" />
        </svg>
      </div>
      <div className="min-w-0 leading-tight">
        <div className="num flex items-baseline gap-1.5 text-[15px] font-extrabold tracking-[0.16em]">
          ACRO <span className="text-[11px] font-bold tracking-[0.22em] text-gold">CURTAIN PRO</span>
        </div>
        <h1 className="truncate text-[13px] font-semibold text-ink2">커튼·블라인드 실측 계산기</h1>
      </div>
    </div>
  );
}

function MobileBar({ onQuote }: { onQuote: () => void }) {
  const { state, calc } = useStore();
  const curtain = useActiveRoom('curtain');
  const blind = useActiveRoom('blind');
  const tab = state.ui.tab;
  if (tab === 'settings') return null;
  let label = '';
  let key = '입력 전';
  if (tab === 'curtain' && curtain) {
    label = curtain.label;
    const r = curtain.result;
    if (r.ok) key = r.method === 'joined' ? `${r.totalWidths}폭 · ${fmtMeters(r.totalLength)}m` : `광폭 ${fmtMeters(r.totalLength)}m`;
  } else if (tab === 'blind' && blind) {
    label = blind.label;
    const r = blind.result;
    if (r.ok) key = `${fmt(r.orderW, 1)}×${fmt(r.orderH, 1)} · ${fmt(r.billAreaTotal, 2)}㎡`;
  }
  return (
    <div
      className="no-print gutter fixed inset-x-0 bottom-0 z-40 border-t border-line bg-surface/95 backdrop-blur lg:hidden"
      style={{ paddingBottom: 'max(10px, env(safe-area-inset-bottom, 0px))', paddingTop: 10 }}
    >
      <div className="mx-auto flex max-w-[1180px] items-center gap-3">
        <div className="min-w-0 flex-1">
          <div className="truncate text-[12px] font-semibold text-ink3">{label || '공간 없음'}</div>
          <div className="num truncate text-[18px] font-extrabold leading-tight">{key}</div>
        </div>
        <button type="button" onClick={onQuote} className="flex shrink-0 flex-col items-end rounded-[12px] bg-primary px-3.5 py-1.5 text-onprimary">
          <span className="text-[11px] font-semibold opacity-75">현장 합계 · 견적서</span>
          <span className="num text-[16px] font-extrabold leading-tight">{won(calc.totals.total)}</span>
        </button>
      </div>
    </div>
  );
}

function Shell() {
  const { state, calc, update, undo, canUndo, loadStatus, saveFailed } = useStore();
  const { toast } = useUi();
  const [quoteOpen, setQuoteOpen] = useState(false);
  const [recentOpen, setRecentOpen] = useState(false);
  const tab = state.ui.tab;
  const theme = state.settings.theme;
  const origTheme = useRef<string | null>(document.documentElement.getAttribute('data-theme'));
  const curtain = useActiveRoom('curtain');
  const blind = useActiveRoom('blind');

  useEffect(() => {
    const el = document.documentElement;
    if (theme === 'system') {
      if (origTheme.current) el.setAttribute('data-theme', origTheme.current);
      else el.removeAttribute('data-theme');
    } else el.setAttribute('data-theme', theme);
  }, [theme]);

  useEffect(() => {
    if (loadStatus === 'recovered') toast('저장 데이터가 손상되어 읽을 수 있는 값만 복구했습니다.', 'warn');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const setTab = (t: Tab) => {
    update((d) => void (d.ui.tab = t), 'none');
    window.scrollTo({ top: 0 });
  };

  const copyCurrent = async () => {
    const rc = tab === 'curtain' ? curtain : tab === 'blind' ? blind : null;
    const text = rc ? roomText(rc, state.settings.unit) : siteText(state.site, calc, state.settings);
    const ok = await copyText(text);
    toast(ok ? '계산 결과를 복사했습니다.' : '복사하지 못했습니다. 다시 시도하세요.', ok ? 'ok' : 'warn');
  };
  const copySite = async () => {
    const ok = await copyText(siteText(state.site, calc, state.settings));
    toast(ok ? '현장 전체 결과를 복사했습니다.' : '복사하지 못했습니다.', ok ? 'ok' : 'warn');
  };

  return (
    <div className="min-h-full">
      <header className="sticky z-50 border-b border-line bg-surface" style={{ top: 'env(safe-area-inset-top, 0px)' }}>
        <div className="gutter mx-auto flex max-w-[1180px] items-center justify-between gap-3 pt-3">
          <Wordmark />
          <div className="flex shrink-0 items-center gap-1">
            <button
              type="button"
              className="btn btn-quiet px-2.5 disabled:opacity-35"
              disabled={!canUndo}
              onClick={() => (undo() ? toast('직전 상태로 되돌렸습니다.') : null)}
              title="직전 계산 복원"
              aria-label="되돌리기 (직전 계산 복원)"
            >
              <Icon name="undo" />
              <span className="hidden md:inline">되돌리기</span>
            </button>
            <button type="button" className="btn btn-quiet px-2.5" onClick={copyCurrent} aria-label="계산 결과 복사" title="계산 결과 복사">
              <Icon name="copy" />
              <span className="hidden md:inline">결과 복사</span>
            </button>
            <button type="button" className="btn btn-ghost hidden px-3 sm:inline-flex" onClick={() => setQuoteOpen(true)}>
              <Icon name="doc" />
              견적서
            </button>
          </div>
        </div>
        <nav className="gutter mx-auto mt-2 flex max-w-[1180px]" aria-label="계산기 메뉴">
          {TABS.map((t) => {
            const on = tab === t.value;
            return (
              <button
                key={t.value}
                type="button"
                onClick={() => setTab(t.value)}
                aria-current={on ? 'page' : undefined}
                className={`relative flex-1 py-3 text-[14.5px] font-bold transition sm:flex-none sm:px-5 ${on ? 'text-ink' : 'text-ink3 hover:text-ink2'}`}
              >
                <span className="sm:hidden">{t.short}</span>
                <span className="hidden sm:inline">{t.label}</span>
                {on && <span className="absolute inset-x-3 bottom-0 h-[3px] rounded-t-full bg-gold" />}
              </button>
            );
          })}
        </nav>
      </header>

      <main className="gutter mx-auto flex max-w-[1180px] flex-col gap-4 pb-32 pt-4 lg:pb-12">
        {saveFailed && (
          <p className="rounded-[10px] border border-warn/30 bg-warnsoft px-3.5 py-2.5 text-[13px] font-medium text-warn">
            이 브라우저에서는 자동 저장이 되지 않습니다(개인정보 보호 모드 등). 작업 후 환경설정에서 JSON으로 내보내 보관하세요.
          </p>
        )}
        {tab !== 'settings' && <SiteBar onOpenRecent={() => setRecentOpen(true)} />}
        {tab === 'curtain' && <CurtainTab />}
        {tab === 'blind' && <BlindTab />}
        {tab === 'settings' && <SettingsTab onOpenRecent={() => setRecentOpen(true)} />}
        {tab !== 'settings' && <SiteSummary onQuote={() => setQuoteOpen(true)} onCopy={copySite} />}
      </main>

      <MobileBar onQuote={() => setQuoteOpen(true)} />
      <QuoteModal open={quoteOpen} onClose={() => setQuoteOpen(false)} />
      <RecentModal open={recentOpen} onClose={() => setRecentOpen(false)} />
      <UiLayer />
    </div>
  );
}

export default function App() {
  return (
    <UiProvider>
      <StoreProvider>
        <Shell />
      </StoreProvider>
    </UiProvider>
  );
}
