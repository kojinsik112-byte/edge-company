import { useEffect, useRef, useState, type ReactNode } from 'react';
import { newBlindRoom, newCurtainRoom, roomLabel, structuredCloneSafe } from '../lib/defaults';
import { fmt, fmtMeters, uid, won } from '../lib/num';
import type { QuoteLine, RoomCalc, RoomQuote } from '../lib/quote';
import type { Discount, OptionItem, Room, SpaceName } from '../lib/types';
import { SPACES } from '../lib/types';
import { useStore, useUi } from '../store';
import { Icon, NumberField, Seg } from './ui';

/** 공간 선택 띠 + 추가·복제·초기화·삭제 */
export function RoomStrip({ kind }: { kind: Room['kind'] }) {
  const { state, calc, update } = useStore();
  const { confirm, toast } = useUi();
  const activeId = kind === 'curtain' ? state.ui.activeCurtain : state.ui.activeBlind;
  const rooms = calc.rooms.filter((r) => r.kind === kind);
  const [adding, setAdding] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!adding) return;
    const close = (e: MouseEvent) => !menuRef.current?.contains(e.target as Node) && setAdding(false);
    window.addEventListener('mousedown', close);
    return () => window.removeEventListener('mousedown', close);
  }, [adding]);

  const setActive = (id: string | null) =>
    update((d) => {
      if (kind === 'curtain') d.ui.activeCurtain = id;
      else d.ui.activeBlind = id;
    }, 'none');

  const add = (space: SpaceName) => {
    setAdding(false);
    update((d) => {
      const sameSpace = d.site.rooms.filter((r) => r.space === space).length;
      const location = sameSpace ? `${space} ${sameSpace + 1}` : '';
      const room = kind === 'curtain' ? newCurtainRoom(d.settings, space, location) : newBlindRoom(d.settings, space, location);
      d.site.rooms.push(room);
      if (kind === 'curtain') d.ui.activeCurtain = room.id;
      else d.ui.activeBlind = room.id;
    }, 'force');
  };

  const active = rooms.find((r) => r.room.id === activeId) ?? rooms[0];

  const duplicate = () => {
    if (!active) return;
    update((d) => {
      const i = d.site.rooms.findIndex((r) => r.id === active.room.id);
      const copy = structuredCloneSafe(d.site.rooms[i]);
      copy.id = uid(kind === 'curtain' ? 'c' : 'b');
      copy.location = `${roomLabel(copy)} 복사본`;
      d.site.rooms.splice(i + 1, 0, copy);
      if (kind === 'curtain') d.ui.activeCurtain = copy.id;
      else d.ui.activeBlind = copy.id;
    }, 'force');
    toast('공간을 복제했습니다.');
  };

  const remove = async () => {
    if (!active) return;
    const ok = await confirm({
      title: `「${active.label}」 공간을 삭제할까요?`,
      body: '이 공간의 실측값과 단가가 지워집니다. 상단 되돌리기로 바로 복구할 수 있습니다.',
      confirmLabel: '삭제',
      danger: true,
    });
    if (!ok) return;
    update((d) => {
      const i = d.site.rooms.findIndex((r) => r.id === active.room.id);
      d.site.rooms.splice(i, 1);
      const next = d.site.rooms.filter((r) => r.kind === kind);
      const pick = next[Math.max(0, Math.min(next.length - 1, rooms.indexOf(active) - 1))]?.id ?? null;
      if (kind === 'curtain') d.ui.activeCurtain = pick;
      else d.ui.activeBlind = pick;
    }, 'force');
    toast('공간을 삭제했습니다.');
  };

  const reset = async () => {
    if (!active) return;
    const ok = await confirm({
      title: '이 공간의 입력값을 초기화할까요?',
      body: '실측값·주름·원단·단가가 환경설정 기본값으로 돌아갑니다. 공간명은 유지됩니다.',
      confirmLabel: '초기화',
    });
    if (!ok) return;
    update((d) => {
      const i = d.site.rooms.findIndex((r) => r.id === active.room.id);
      const old = d.site.rooms[i];
      const fresh = kind === 'curtain' ? newCurtainRoom(d.settings, old.space, old.location) : newBlindRoom(d.settings, old.space, old.location);
      fresh.id = old.id;
      fresh.spaceCustom = old.spaceCustom;
      d.site.rooms[i] = fresh;
    }, 'force');
    toast('입력값을 초기화했습니다.');
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-2">
        <div className="scroll-x -mx-1 flex min-w-0 flex-1 gap-2 px-1 py-0.5">
          {rooms.map((rc) => {
            const on = rc.room.id === active?.room.id;
            const key =
              rc.kind === 'curtain'
                ? rc.result.ok
                  ? rc.result.method === 'joined'
                    ? `${rc.result.totalWidths}폭`
                    : `${fmtMeters(rc.result.totalLength)}m`
                  : '입력 전'
                : rc.result.ok
                  ? `${fmt(rc.result.billAreaTotal, 2)}㎡`
                  : '입력 전';
            const warn = rc.result.ok && !rc.result.producible;
            return (
              <button
                key={rc.room.id}
                type="button"
                onClick={() => setActive(rc.room.id)}
                aria-pressed={on}
                className={`flex shrink-0 flex-col items-start rounded-[12px] border px-3.5 py-2 text-left transition ${
                  on ? 'border-primary bg-primary text-onprimary' : 'border-line bg-surface hover:border-ink3'
                }`}
              >
                <span className="max-w-[9.5rem] truncate text-[14px] font-bold">{rc.label}</span>
                <span className={`num text-[12.5px] font-semibold ${on ? 'text-onprimary/75' : warn ? 'text-err' : 'text-ink3'}`}>
                  {warn ? '확인 필요' : key}
                </span>
              </button>
            );
          })}
        </div>
        <div className="relative shrink-0" ref={menuRef}>
          <button type="button" className="btn btn-ghost h-[52px] px-3" onClick={() => setAdding(!adding)} aria-expanded={adding}>
            <Icon name="plus" />
            <span className="hidden sm:inline">공간 추가</span>
          </button>
          {adding && (
            <div className="rise absolute right-0 top-full z-30 mt-2 w-48 rounded-[12px] border border-line bg-surface p-1.5 shadow-card">
              <div className="eyebrow px-2.5 pb-1 pt-1.5">어느 공간인가요</div>
              {SPACES.map((s) => (
                <button key={s} type="button" onClick={() => add(s)} className="block w-full rounded-[8px] px-2.5 py-2 text-left text-[14.5px] font-semibold hover:bg-sunk">
                  {s}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
      {active && (
        <div className="flex flex-wrap items-center gap-1 text-[13px]">
          <button type="button" className="btn btn-quiet min-h-[34px] px-2.5 text-[13px]" onClick={duplicate}>
            <Icon name="copy" size={16} />
            복제
          </button>
          <button type="button" className="btn btn-quiet min-h-[34px] px-2.5 text-[13px]" onClick={reset}>
            <Icon name="reset" size={16} />
            입력 초기화
          </button>
          <button type="button" className="btn btn-quiet min-h-[34px] px-2.5 text-[13px] text-err hover:text-err" onClick={remove}>
            <Icon name="trash" size={16} />
            삭제
          </button>
        </div>
      )}
    </div>
  );
}

export function useActiveRoom<K extends Room['kind']>(kind: K): Extract<RoomCalc, { kind: K }> | null {
  const { state, calc } = useStore();
  const id = kind === 'curtain' ? state.ui.activeCurtain : state.ui.activeBlind;
  const list = calc.rooms.filter((r) => r.kind === kind) as Extract<RoomCalc, { kind: K }>[];
  return list.find((r) => r.room.id === id) ?? list[0] ?? null;
}

export function EmptyRooms({ kind }: { kind: Room['kind'] }) {
  const { update } = useStore();
  const add = () =>
    update((d) => {
      const room = kind === 'curtain' ? newCurtainRoom(d.settings) : newBlindRoom(d.settings);
      d.site.rooms.push(room);
      if (kind === 'curtain') d.ui.activeCurtain = room.id;
      else d.ui.activeBlind = room.id;
    }, 'force');
  return (
    <div className="card flex flex-col items-center gap-3 px-6 py-12 text-center">
      <Icon name="ruler" size={28} className="text-gold" />
      <p className="text-[15px] font-semibold">{kind === 'curtain' ? '커튼 공간이 없습니다' : '블라인드 공간이 없습니다'}</p>
      <p className="max-w-sm text-[13.5px] text-ink3">공간을 추가하고 실측 가로·세로를 입력하면 바로 계산됩니다.</p>
      <button type="button" className="btn btn-primary mt-1" onClick={add}>
        <Icon name="plus" />
        공간 추가
      </button>
    </div>
  );
}

// ── 견적 편집 공통 ────────────────────────────────────────
export function PriceRow<M extends string>({
  label,
  modes,
  mode,
  onMode,
  price,
  onPrice,
  cost,
  onCost,
  admin,
  hint,
}: {
  label: string;
  modes?: { value: M; label: string; disabled?: boolean }[];
  mode?: M;
  onMode?: (m: M) => void;
  price: number | null;
  onPrice: (v: number | null) => void;
  cost?: number | null;
  onCost?: (v: number | null) => void;
  admin: boolean;
  hint?: ReactNode;
}) {
  return (
    <div className="grid grid-cols-1 gap-2 border-b border-line/70 py-3 last:border-0 sm:grid-cols-[7.5rem_minmax(0,1fr)] sm:items-start">
      <div className="pt-0 text-[14px] font-semibold sm:pt-2.5">{label}</div>
      <div className="flex min-w-0 flex-col gap-2">
        {modes && mode && onMode && <Seg value={mode} options={modes} onChange={onMode} label={`${label} 계산 방식`} />}
        <div className={`grid gap-2 ${admin && onCost ? 'grid-cols-2' : 'grid-cols-1'}`}>
          <NumberField value={price} onChange={onPrice} suffix="원" min={0} placeholder="미입력" ariaLabel={`${label} 판매 단가`} hint={admin ? '판매가' : hint} />
          {admin && onCost && <NumberField value={cost ?? null} onChange={onCost} suffix="원" min={0} placeholder="원가" ariaLabel={`${label} 원가`} hint="원가 (고객 비노출)" />}
        </div>
      </div>
    </div>
  );
}

export function OptionsEditor({ options, onChange, admin }: { options: OptionItem[]; onChange: (o: OptionItem[]) => void; admin: boolean }) {
  return (
    <div className="flex flex-col gap-2 py-3">
      <div className="flex items-center justify-between">
        <span className="text-[14px] font-semibold">추가 옵션</span>
        <button type="button" className="btn btn-quiet min-h-[34px] px-2 text-[13px]" onClick={() => onChange([...options, { id: uid('o'), label: '', amount: null, cost: null }])}>
          <Icon name="plus" size={16} />
          옵션 추가
        </button>
      </div>
      {options.length === 0 && <p className="text-[12.5px] text-ink3">전동 모터·리모컨·타공 등 별도 항목을 추가하세요.</p>}
      {options.map((o, i) => (
        <div key={o.id} className="flex items-start gap-2">
          <div className="field min-w-0 flex-1">
            <input
              value={o.label}
              onChange={(e) => onChange(options.map((x, k) => (k === i ? { ...x, label: e.target.value } : x)))}
              placeholder="항목명 (예: 전동 모터)"
              aria-label="옵션 항목명"
              className="h-11 w-full min-w-0 bg-transparent px-3 text-[15px] outline-none placeholder:text-ink3/60"
            />
          </div>
          <NumberField className="w-32 shrink-0" value={o.amount} onChange={(v) => onChange(options.map((x, k) => (k === i ? { ...x, amount: v } : x)))} suffix="원" min={0} ariaLabel="옵션 금액" />
          {admin && <NumberField className="w-28 shrink-0" value={o.cost ?? null} onChange={(v) => onChange(options.map((x, k) => (k === i ? { ...x, cost: v } : x)))} suffix="원" placeholder="원가" ariaLabel="옵션 원가" />}
          <button type="button" className="btn btn-quiet h-11 px-2" aria-label="옵션 삭제" onClick={() => onChange(options.filter((_, k) => k !== i))}>
            <Icon name="x" size={16} />
          </button>
        </div>
      ))}
    </div>
  );
}

export function DiscountEditor({ value, onChange, label = '할인' }: { value: Discount; onChange: (d: Discount) => void; label?: string }) {
  return (
    <div className="grid grid-cols-1 gap-2 py-3 sm:grid-cols-[7.5rem_minmax(0,1fr)] sm:items-center">
      <div className="text-[14px] font-semibold">{label}</div>
      <div className="grid grid-cols-[minmax(0,9rem)_minmax(0,1fr)] gap-2">
        <Seg
          value={value.type}
          options={[
            { value: 'rate', label: '할인율' },
            { value: 'amount', label: '금액' },
          ]}
          onChange={(t) => onChange({ type: t, value: null })}
          label="할인 방식"
        />
        <NumberField value={value.value} onChange={(v) => onChange({ ...value, value: v })} suffix={value.type === 'rate' ? '%' : '원'} min={0} placeholder="없음" ariaLabel="할인 값" />
      </div>
    </div>
  );
}

export function QuoteBreakdown({ quote, admin, note }: { quote: RoomQuote; admin: boolean; note?: ReactNode }) {
  if (!quote.lines.length)
    return <p className="rounded-[10px] bg-sunk px-3.5 py-3 text-[13.5px] text-ink3">단가를 입력하면 이 공간 견적이 계산됩니다.</p>;
  return (
    <div className="rounded-[12px] bg-sunk px-3.5 py-3">
      <ul className="flex flex-col">
        {quote.lines.map((l: QuoteLine) => (
          <li key={l.key} className="flex items-baseline justify-between gap-3 py-1.5">
            <span className="min-w-0">
              <span className="text-[14px] font-semibold">{l.label}</span>
              <span className="mono ml-2 text-[12px] text-ink3">{l.basis}</span>
            </span>
            <span className="num shrink-0 text-[15px] font-bold">{won(l.amount)}</span>
          </li>
        ))}
      </ul>
      <div className="mt-2 flex flex-col gap-1 border-t border-line pt-2.5 text-[14px]">
        {quote.discount > 0 && (
          <div className="flex justify-between text-ink2">
            <span>할인</span>
            <span className="num font-semibold">−{won(quote.discount)}</span>
          </div>
        )}
        <div className="flex items-baseline justify-between">
          <span className="font-semibold">공간 견적 (부가세 전)</span>
          <span className="num text-[19px] font-extrabold">{won(quote.total)}</span>
        </div>
        {admin && (
          <div className="flex justify-between text-[12.5px] text-ink3">
            <span>원가 {quote.costKnown ? '' : '(일부 미입력)'}</span>
            <span className="num">
              {won(quote.costTotal)} · 마진 {won(quote.total - quote.costTotal)}
            </span>
          </div>
        )}
        {note && <p className="text-[12px] text-ink3">{note}</p>}
      </div>
    </div>
  );
}

export function Metric({
  label,
  value,
  unit,
  caption,
  hero,
  tone,
}: {
  label: string;
  value: string;
  unit?: string;
  caption?: ReactNode;
  hero?: boolean;
  tone?: 'err' | 'gold';
}) {
  return (
    <div className="min-w-0">
      <div className="text-[13px] font-semibold text-ink2">{label}</div>
      <div className={`num mt-0.5 flex items-baseline gap-1 ${tone === 'err' ? 'text-err' : tone === 'gold' ? 'text-gold' : ''}`}>
        <span className={hero ? 'text-[42px] font-extrabold leading-none sm:text-[56px]' : 'text-[26px] font-extrabold leading-tight sm:text-[30px]'}>{value}</span>
        {unit && <span className={hero ? 'text-[18px] font-bold sm:text-[22px]' : 'text-[15px] font-bold text-ink2'}>{unit}</span>}
      </div>
      {caption && <div className="mono mt-1 text-[12px] leading-snug text-ink3">{caption}</div>}
    </div>
  );
}
