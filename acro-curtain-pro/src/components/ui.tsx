import { useEffect, useId, useRef, useState, type ReactNode } from 'react';
import { createPortal } from 'react-dom';
import { clean, fmt, fromUnit, isNum, parseNum, toUnit, UNIT_DEC, type Unit } from '../lib/num';
import type { Issue } from '../lib/types';
import { useUi } from '../store';

// ── 아이콘 (선 아이콘, 24 그리드) ─────────────────────────
const PATHS: Record<string, string> = {
  plus: 'M12 5v14M5 12h14',
  copy: 'M9 9h10v10H9zM5 15V5h10',
  trash: 'M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3',
  undo: 'M9 14 4 9l5-5M4 9h10a6 6 0 0 1 0 12h-3',
  reset: 'M4 4v6h6M20 20v-6h-6M5.5 15a7.5 7.5 0 0 0 13 2M18.5 9a7.5 7.5 0 0 0-13-2',
  doc: 'M7 3h7l5 5v13H7zM14 3v5h5M10 13h6M10 17h6',
  print: 'M7 9V3h10v6M7 17H4v-7h16v7h-3M7 14h10v7H7z',
  download: 'M12 4v11m0 0-4-4m4 4 4-4M5 20h14',
  upload: 'M12 20V9m0 0-4 4m4-4 4 4M5 4h14',
  chevron: 'm9 6 6 6-6 6',
  down: 'm6 9 6 6 6-6',
  check: 'm5 12 5 5 9-10',
  alert: 'M12 9v4M12 17h.01M10.3 4.3 2.6 18a2 2 0 0 0 1.7 3h15.4a2 2 0 0 0 1.7-3L13.7 4.3a2 2 0 0 0-3.4 0z',
  info: 'M12 11v6M12 7h.01M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z',
  x: 'M6 6l12 12M18 6 6 18',
  save: 'M5 4h11l3 3v13H5zM8 4v5h7V4M8 20v-6h8v6',
  folder: 'M3 6h6l2 2h10v11H3z',
  clipboard: 'M9 4h6v3H9zM8 5H5v16h14V5h-3',
  sliders: 'M4 7h10M18 7h2M4 17h4M12 17h8M14 4v6M8 14v6',
  ruler: 'M3 17 17 3l4 4L7 21zM7 13l2 2M10 10l2 2M13 7l2 2',
  user: 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21a8 8 0 0 1 16 0',
  shield: 'M12 3 5 6v6c0 4 3 7.5 7 9 4-1.5 7-5 7-9V6z',
  minus: 'M5 12h14',
};

export function Icon({ name, size = 18, className = '' }: { name: keyof typeof PATHS | string; size?: number; className?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden="true">
      <path d={PATHS[name] ?? ''} />
    </svg>
  );
}

// ── 숫자 입력 ─────────────────────────────────────────────
function focusNext(el: HTMLElement) {
  const all = Array.from(document.querySelectorAll<HTMLInputElement>('input[data-nav]'));
  const i = all.indexOf(el as HTMLInputElement);
  if (i >= 0 && all[i + 1]) all[i + 1].focus();
  else (el as HTMLInputElement).blur();
}

interface NumberFieldProps {
  id?: string;
  label?: ReactNode;
  value: number | null;
  onChange: (v: number | null) => void;
  suffix?: string;
  /** 표시값 = value × scale (길이 단위 변환용) */
  scale?: number;
  decimals?: number;
  integer?: boolean;
  min?: number;
  placeholder?: string;
  size?: 'xl' | 'lg' | 'md' | 'sm';
  hint?: ReactNode;
  error?: string | null;
  className?: string;
  ariaLabel?: string;
  nav?: boolean;
}

export function NumberField({
  id,
  label,
  value,
  onChange,
  suffix,
  scale = 1,
  integer,
  min,
  placeholder,
  size = 'md',
  hint,
  error,
  className = '',
  ariaLabel,
  nav = true,
}: NumberFieldProps) {
  const autoId = useId();
  const fid = id ?? autoId;
  const display = (v: number | null) => (v === null || !isNum(v) ? '' : String(clean(v * scale)));
  const [text, setText] = useState(display(value));
  const [localErr, setLocalErr] = useState<string | null>(null);
  const focused = useRef(false);
  const ref = useRef<HTMLInputElement>(null);

  // 바깥 값이 바뀌면(단위 변경·불러오기·초기화) 표시를 맞춘다
  useEffect(() => {
    const parsed = parseNum(text);
    const cur = parsed === null || Number.isNaN(parsed) ? null : clean(parsed / scale);
    const same = cur === null ? value === null : value !== null && Math.abs(cur - value) < 1e-9;
    if (!same && !(focused.current && Number.isNaN(parsed))) {
      setText(display(value));
      setLocalErr(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value, scale]);

  const commit = (t: string) => {
    setText(t);
    const v = parseNum(t);
    if (v === null) {
      setLocalErr(null);
      onChange(null);
      return;
    }
    if (Number.isNaN(v)) {
      setLocalErr('숫자만 입력할 수 있습니다.');
      return;
    }
    if (integer && !Number.isInteger(v)) setLocalErr('정수로 입력하세요.');
    else if (min !== undefined && v < min) setLocalErr(`${fmt(min, 2)} 이상 입력하세요.`);
    else setLocalErr(null);
    onChange(clean(v / scale));
  };

  const err = localErr ?? error ?? null;
  const sizes = {
    xl: 'h-16 text-[30px] font-bold px-4',
    lg: 'h-14 text-[22px] font-bold px-3.5',
    md: 'h-11 text-[16px] font-semibold px-3',
    sm: 'h-10 text-[15px] font-semibold px-2.5',
  }[size];

  return (
    <div className={`min-w-0 ${className}`}>
      {label && (
        <label htmlFor={fid} className="mb-1.5 block text-[13px] font-semibold text-ink2">
          {label}
        </label>
      )}
      <div className="field flex items-center" data-invalid={err ? 'true' : 'false'}>
        <input
          ref={ref}
          id={fid}
          data-nav={nav ? '' : undefined}
          aria-label={ariaLabel}
          aria-invalid={!!err}
          type="text"
          inputMode={integer ? 'numeric' : 'decimal'}
          enterKeyHint="next"
          autoComplete="off"
          spellCheck={false}
          placeholder={placeholder}
          value={text}
          onChange={(e) => commit(e.target.value)}
          onFocus={(e) => {
            focused.current = true;
            const el = e.currentTarget;
            requestAnimationFrame(() => el.select());
            if (window.innerWidth < 768) setTimeout(() => el.scrollIntoView({ block: 'center', behavior: 'smooth' }), 280);
          }}
          onBlur={() => {
            focused.current = false;
            if (!localErr) setText(display(value));
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
              focusNext(e.currentTarget);
            }
          }}
          className={`num w-full min-w-0 bg-transparent outline-none placeholder:text-ink3/60 placeholder:font-medium ${sizes}`}
        />
        {suffix && <span className="shrink-0 pr-3 text-[13px] font-semibold text-ink3">{suffix}</span>}
      </div>
      {err ? (
        <p className="mt-1 text-[12.5px] font-medium text-err">{err}</p>
      ) : hint ? (
        <p className="mt-1 text-[12.5px] text-ink3">{hint}</p>
      ) : null}
    </div>
  );
}

/** cm로 저장, 화면은 설정 단위로 */
export function LengthField(props: Omit<NumberFieldProps, 'scale' | 'suffix'> & { unit: Unit }) {
  const { unit, ...rest } = props;
  return <NumberField {...rest} scale={toUnit(1, unit)} suffix={unit} decimals={UNIT_DEC[unit]} />;
}

export function lenFromInput(v: number, unit: Unit) {
  return fromUnit(v, unit);
}

// ── 텍스트 입력 ───────────────────────────────────────────
export function TextField({
  label,
  value,
  onChange,
  placeholder,
  type = 'text',
  multiline,
  className = '',
  inputMode,
}: {
  label: ReactNode;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  type?: string;
  multiline?: boolean;
  className?: string;
  inputMode?: 'text' | 'tel' | 'numeric';
}) {
  const id = useId();
  return (
    <div className={`min-w-0 ${className}`}>
      <label htmlFor={id} className="mb-1.5 block text-[13px] font-semibold text-ink2">
        {label}
      </label>
      <div className="field">
        {multiline ? (
          <textarea
            id={id}
            rows={3}
            value={value}
            placeholder={placeholder}
            onChange={(e) => onChange(e.target.value)}
            className="block w-full resize-y bg-transparent px-3 py-2.5 text-[15px] outline-none placeholder:text-ink3/60"
          />
        ) : (
          <input
            id={id}
            type={type}
            inputMode={inputMode}
            value={value}
            placeholder={placeholder}
            autoComplete="off"
            onChange={(e) => onChange(e.target.value)}
            className="h-11 w-full min-w-0 bg-transparent px-3 text-[15px] outline-none placeholder:text-ink3/60"
          />
        )}
      </div>
    </div>
  );
}

export function SelectField<T extends string>({
  label,
  value,
  options,
  onChange,
  className = '',
}: {
  label: ReactNode;
  value: T;
  options: readonly T[] | { value: T; label: string }[];
  onChange: (v: T) => void;
  className?: string;
}) {
  const id = useId();
  const opts = (options as (T | { value: T; label: string })[]).map((o) => (typeof o === 'string' ? { value: o, label: o } : o));
  return (
    <div className={`min-w-0 ${className}`}>
      {label && (
        <label htmlFor={id} className="mb-1.5 block text-[13px] font-semibold text-ink2">
          {label}
        </label>
      )}
      <div className="field relative">
        <select
          id={id}
          value={value}
          onChange={(e) => onChange(e.target.value as T)}
          className="h-11 w-full appearance-none bg-transparent pl-3 pr-9 text-[15px] font-medium outline-none"
        >
          {opts.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <Icon name="down" size={16} className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-ink3" />
      </div>
    </div>
  );
}

// ── 선택 컨트롤 ───────────────────────────────────────────
export function Seg<T extends string>({
  value,
  options,
  onChange,
  label,
  className = '',
}: {
  value: T;
  options: { value: T; label: ReactNode; disabled?: boolean }[];
  onChange: (v: T) => void;
  label?: string;
  className?: string;
}) {
  return (
    <div role="group" aria-label={label} className={`seg ${className}`}>
      {options.map((o) => (
        <button key={o.value} type="button" aria-pressed={value === o.value} disabled={o.disabled} onClick={() => onChange(o.value)} className="disabled:opacity-40">
          {o.label}
        </button>
      ))}
    </div>
  );
}

export function Toggle({ checked, onChange, label, hint }: { checked: boolean; onChange: (v: boolean) => void; label: ReactNode; hint?: ReactNode }) {
  const id = useId();
  return (
    <label htmlFor={id} className="flex cursor-pointer items-start justify-between gap-4">
      <span className="min-w-0">
        <span className="block text-[14.5px] font-semibold">{label}</span>
        {hint && <span className="mt-0.5 block text-[12.5px] text-ink3">{hint}</span>}
      </span>
      <span className="relative mt-0.5 inline-flex shrink-0">
        <input id={id} type="checkbox" className="peer sr-only" checked={checked} onChange={(e) => onChange(e.target.checked)} />
        <span className="h-6 w-11 rounded-full bg-line transition peer-checked:bg-primary peer-focus-visible:ring-2 peer-focus-visible:ring-gold" />
        <span className="absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-surface shadow transition peer-checked:translate-x-5" />
      </span>
    </label>
  );
}

export function Disclosure({ title, sub, children, defaultOpen = false, badge }: { title: ReactNode; sub?: ReactNode; children: ReactNode; defaultOpen?: boolean; badge?: ReactNode }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border-t border-line">
      <button type="button" aria-expanded={open} onClick={() => setOpen(!open)} className="flex w-full items-center gap-3 py-3.5 text-left">
        <span className="min-w-0 flex-1">
          <span className="flex items-center gap-2 text-[14.5px] font-semibold">
            {title}
            {badge}
          </span>
          {sub && <span className="mt-0.5 block truncate text-[12.5px] text-ink3">{sub}</span>}
        </span>
        <Icon name="down" size={18} className={`shrink-0 text-ink3 transition ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && <div className="pb-4">{children}</div>}
    </div>
  );
}

export function Card({ children, className = '', title, eyebrow, action, id }: { children: ReactNode; className?: string; title?: ReactNode; eyebrow?: ReactNode; action?: ReactNode; id?: string }) {
  return (
    <section id={id} className={`card min-w-0 p-4 sm:p-5 ${className}`}>
      {(title || action) && (
        <header className="mb-4 flex items-start justify-between gap-3">
          <div className="min-w-0">
            {eyebrow && <div className="eyebrow mb-1">{eyebrow}</div>}
            {title && <h2 className="text-[17px] font-bold leading-snug">{title}</h2>}
          </div>
          {action && <div className="flex shrink-0 items-center gap-1">{action}</div>}
        </header>
      )}
      {children}
    </section>
  );
}

export function Pill({ tone = 'neutral', children }: { tone?: 'neutral' | 'ok' | 'warn' | 'err' | 'gold'; children: ReactNode }) {
  const cls = {
    neutral: 'bg-sunk text-ink2',
    ok: 'bg-ok/10 text-ok',
    warn: 'bg-warnsoft text-warn',
    err: 'bg-errsoft text-err',
    gold: 'bg-goldsoft text-gold',
  }[tone];
  return <span className={`inline-flex items-center gap-1 whitespace-nowrap rounded-full px-2.5 py-0.5 text-[12px] font-semibold ${cls}`}>{children}</span>;
}

export function IssueList({ issues, skip = [] }: { issues: Issue[]; skip?: string[] }) {
  const list = issues.filter((i) => i.code !== 'empty' && !skip.includes(i.code ?? ''));
  if (!list.length) return null;
  const order = { error: 0, critical: 1, warning: 2, info: 3 };
  return (
    <ul className="flex flex-col gap-2">
      {[...list]
        .sort((a, b) => order[a.level] - order[b.level])
        .map((i, k) => {
          const tone =
            i.level === 'error' || i.level === 'critical'
              ? 'border-err/30 bg-errsoft text-err'
              : i.level === 'warning'
                ? 'border-warn/30 bg-warnsoft text-warn'
                : 'border-line bg-sunk text-ink2';
          return (
            <li key={k} className={`flex items-start gap-2 rounded-[10px] border px-3 py-2.5 text-[13.5px] font-medium leading-snug ${tone}`}>
              <Icon name={i.level === 'info' ? 'info' : 'alert'} size={16} className="mt-0.5 shrink-0" />
              <span className="min-w-0">{i.message}</span>
            </li>
          );
        })}
    </ul>
  );
}

// ── 모달·토스트·확인창 ────────────────────────────────────
export function Modal({ open, onClose, title, children, wide, footer }: { open: boolean; onClose: () => void; title: ReactNode; children: ReactNode; wide?: boolean; footer?: ReactNode }) {
  useEffect(() => {
    if (!open) return;
    const k = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', k);
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      window.removeEventListener('keydown', k);
      document.body.style.overflow = prev;
    };
  }, [open, onClose]);
  if (!open) return null;
  return createPortal(
    <div className="fixed inset-0 z-[70] flex items-end justify-center bg-black/40 sm:items-center sm:p-6" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div
        role="dialog"
        aria-modal="true"
        className={`rise flex max-h-[92dvh] w-full flex-col overflow-hidden rounded-t-[18px] bg-surface shadow-card sm:rounded-[16px] ${wide ? 'sm:max-w-[920px]' : 'sm:max-w-[520px]'}`}
        style={{ paddingBottom: 'env(safe-area-inset-bottom, 0px)' }}
      >
        <header className="gutter flex items-center justify-between gap-3 border-b border-line py-3.5">
          <h2 className="text-[16.5px] font-bold">{title}</h2>
          <button type="button" onClick={onClose} className="btn btn-quiet -mr-2 px-2" aria-label="닫기">
            <Icon name="x" />
          </button>
        </header>
        <div className="gutter min-h-0 flex-1 overflow-y-auto py-4">{children}</div>
        {footer && <footer className="gutter flex flex-wrap justify-end gap-2 border-t border-line py-3">{footer}</footer>}
      </div>
    </div>,
    document.body,
  );
}

export function UiLayer() {
  const { toastState, confirmState, closeConfirm } = useUi();
  return (
    <>
      {toastState && (
        <div
          key={toastState.key}
          role="status"
          className="rise fixed left-1/2 z-[80] max-w-[90vw] -translate-x-1/2 rounded-full bg-primary px-4 py-2.5 text-[14px] font-semibold text-onprimary shadow-card"
          style={{ bottom: 'calc(88px + env(safe-area-inset-bottom, 0px))' }}
        >
          {toastState.msg}
        </div>
      )}
      <Modal
        open={!!confirmState}
        onClose={() => closeConfirm(false)}
        title={confirmState?.title ?? ''}
        footer={
          <>
            <button type="button" className="btn btn-ghost" onClick={() => closeConfirm(false)}>
              취소
            </button>
            <button type="button" className={`btn ${confirmState?.danger ? 'bg-err text-white hover:bg-err/90' : 'btn-primary'}`} onClick={() => closeConfirm(true)}>
              {confirmState?.confirmLabel ?? '확인'}
            </button>
          </>
        }
      >
        <p className="text-[14.5px] leading-relaxed text-ink2">{confirmState?.body}</p>
      </Modal>
    </>
  );
}

/** 클립보드 복사 — 실패 시 선택 영역 방식으로 폴백 */
export async function copyText(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    try {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      const ok = document.execCommand('copy');
      document.body.removeChild(ta);
      return ok;
    } catch {
      return false;
    }
  }
}
