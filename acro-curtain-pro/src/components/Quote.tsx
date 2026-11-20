import { useEffect, useLayoutEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { fmt, fmtLen, fmtMeters, won } from '../lib/num';
import type { SiteCalc } from '../lib/quote';
import { siteText } from '../lib/text';
import type { Settings, Site } from '../lib/types';
import { MOUNTS } from '../lib/types';
import { useStore, useUi } from '../store';
import { siteTitle } from './Site';
import { copyText, Icon, Modal } from './ui';

const IS_ARTIFACT = __TARGET__ === 'artifact';

/** 1234000 → 일백이십삼만사천 */
export function hangulAmount(n: number): string {
  n = Math.round(Math.abs(n));
  if (n === 0) return '영';
  const d = ['', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구'];
  const u = ['', '십', '백', '천'];
  const big = ['', '만', '억', '조'];
  let out = '';
  let i = 0;
  while (n > 0) {
    let chunk = n % 10000;
    if (chunk) {
      let c = '';
      for (let j = 0; j < 4; j++) {
        const dig = chunk % 10;
        if (dig) c = d[dig] + u[j] + c;
        chunk = Math.floor(chunk / 10);
      }
      out = c + big[i] + out;
    }
    n = Math.floor(n / 10000);
    i++;
  }
  return out;
}

function addDays(date: string, days: number) {
  const d = new Date(date || Date.now());
  if (Number.isNaN(d.getTime())) return '';
  d.setDate(d.getDate() + days);
  return d.toLocaleDateString('ko-KR');
}

export function QuoteSheet({ site, calc, s }: { site: Site; calc: SiteCalc; s: Settings }) {
  const t = calc.totals;
  const info = site.info;
  const q = s.quote;
  const unit = s.unit;
  const issued = new Date().toLocaleDateString('ko-KR');
  const no = `ACP-${(info.date || '').replace(/-/g, '')}-${site.id.slice(-4).toUpperCase()}`;
  const rooms = calc.rooms.filter((r) => r.result.ok);
  const th = 'border-b border-[#1F2023] py-2 text-left text-[11px] font-semibold tracking-wide text-[#55555B]';
  return (
    <div className="sheet mx-auto bg-white text-[#1B1B1E]" style={{ width: '210mm', minHeight: '297mm', padding: '16mm 15mm', boxSizing: 'border-box', fontSize: '12px', lineHeight: 1.5 }}>
      <header className="flex items-start justify-between gap-6 border-b-2 border-[#1F2023] pb-4">
        <div>
          <div className="num text-[11px] font-bold tracking-[0.3em] text-[#A6834E]">{(q.companyName || 'ACRO').toUpperCase()}</div>
          <h1 className="mt-1 text-[30px] font-bold tracking-[0.4em]">견적서</h1>
        </div>
        <dl className="grid grid-cols-[auto_auto] gap-x-4 gap-y-0.5 text-right text-[11.5px]">
          <dt className="text-[#76767B]">견적번호</dt>
          <dd className="num font-semibold">{no}</dd>
          <dt className="text-[#76767B]">견적일</dt>
          <dd className="num font-semibold">{issued}</dd>
          {q.validDays > 0 && (
            <>
              <dt className="text-[#76767B]">유효기간</dt>
              <dd className="num font-semibold">{addDays(new Date().toISOString(), q.validDays)}까지</dd>
            </>
          )}
        </dl>
      </header>

      <section className="mt-5 grid grid-cols-2 gap-6">
        <div>
          <div className="mb-1.5 text-[11px] font-semibold tracking-wide text-[#76767B]">받는 분</div>
          <div className="text-[16px] font-bold">{info.customer ? `${info.customer} 고객님` : '고객님'}</div>
          <div className="mt-1 text-[12px] text-[#44444A]">
            {siteTitle(info)}
            {info.phone && <div>{info.phone}</div>}
            {info.date && <div>실측일 {info.date}</div>}
          </div>
        </div>
        <div>
          <div className="mb-1.5 text-[11px] font-semibold tracking-wide text-[#76767B]">공급자</div>
          <div className="text-[16px] font-bold">{q.companyName || 'ACRO'}</div>
          <div className="mt-1 text-[12px] text-[#44444A]">
            {q.bizNumber && <div>사업자등록번호 {q.bizNumber}</div>}
            {q.companyAddress && <div>{q.companyAddress}</div>}
            {q.companyContact && <div>연락처 {q.companyContact}</div>}
            {info.surveyor && <div>실측 담당 {info.surveyor}</div>}
          </div>
        </div>
      </section>

      <section className="mt-5 flex items-end justify-between gap-4 rounded-[6px] bg-[#F3ECE0] px-5 py-3.5">
        <div>
          <div className="text-[11.5px] font-semibold text-[#55555B]">합계 금액 {s.vatMode === 'none' ? '(부가세 미적용)' : '(부가세 포함)'}</div>
          <div className="mt-0.5 text-[12px] text-[#55555B]">일금 {hangulAmount(t.total)}원정</div>
        </div>
        <div className="num text-[26px] font-extrabold">{won(t.total)}</div>
      </section>

      <table className="mt-5 w-full border-collapse">
        <thead>
          <tr>
            <th className={`${th} w-8`}>No</th>
            <th className={`${th} w-28`}>공간</th>
            <th className={th}>품목 · 규격</th>
            <th className={`${th} w-14 text-right`}>수량</th>
            <th className={`${th} w-28 text-right`}>금액</th>
          </tr>
        </thead>
        <tbody>
          {rooms.map((rc, i) => {
            let item = '';
            let spec = '';
            let qty = '1식';
            if (rc.kind === 'curtain') {
              const r = rc.result;
              const type = rc.room.curtainType === '기타' ? rc.room.curtainTypeCustom || '커튼' : rc.room.curtainType;
              item = `${type} (${rc.room.opening === 'double' ? '양개' : '편개'} · ${rc.room.method === 'joined' ? '폭 연결' : '광폭'})`;
              spec =
                `실측 ${fmtLen(r.width, unit, false)}×${fmtLen(r.height, unit)} · 주름 ${fmt(r.fullness, 2)}배 · ` +
                (r.method === 'joined' ? `원단 ${fmtLen(r.fabricWidth, unit)} ${r.totalWidths}폭 · ${fmtMeters(r.totalLength)}m` : `광폭 ${fmtLen(r.fabricWidth, unit)} · ${fmtMeters(r.totalLength)}m`);
              qty = rc.room.opening === 'double' ? '2장' : '1장';
            } else {
              const r = rc.result;
              const type = rc.room.blindType === '기타' ? rc.room.blindTypeCustom || '블라인드' : rc.room.blindType;
              item = `${type} (${MOUNTS.find((m) => m.value === rc.room.mount)?.label})`;
              spec = `실측 ${fmtLen(r.width, unit, false)}×${fmtLen(r.height, unit)} / 제작 ${fmtLen(r.orderW, unit, false)}×${fmtLen(r.orderH, unit)} · 청구 ${fmt(r.billArea, 2)}㎡`;
              qty = `${r.qty}개`;
            }
            const lines = q.detail === 'itemized' ? rc.quote.lines : [];
            return [
              <tr key={rc.room.id} className="align-top">
                <td className="num border-b border-[#E2E0DB] py-2.5 text-[#76767B]">{i + 1}</td>
                <td className="border-b border-[#E2E0DB] py-2.5 font-semibold">{rc.label}</td>
                <td className="border-b border-[#E2E0DB] py-2.5">
                  <div className="font-semibold">{item}</div>
                  <div className="num text-[11px] text-[#66666B]">{spec}</div>
                  {lines.length > 0 && (
                    <ul className="mt-1.5 text-[11px] text-[#55555B]">
                      {lines.map((l) => (
                        <li key={l.key} className="flex justify-between gap-3">
                          <span>
                            · {l.label} <span className="num text-[#8A8A8F]">{l.basis}</span>
                          </span>
                          <span className="num">{won(l.amount)}</span>
                        </li>
                      ))}
                      {rc.quote.discount > 0 && (
                        <li className="flex justify-between gap-3">
                          <span>· 할인</span>
                          <span className="num">−{won(rc.quote.discount)}</span>
                        </li>
                      )}
                    </ul>
                  )}
                </td>
                <td className="num border-b border-[#E2E0DB] py-2.5 text-right">{qty}</td>
                <td className="num border-b border-[#E2E0DB] py-2.5 text-right font-bold">{won(rc.quote.total)}</td>
              </tr>,
            ];
          })}
        </tbody>
      </table>

      <section className="mt-4 flex justify-end">
        <table className="w-[78mm] text-[12px]">
          <tbody className="num">
            <tr>
              <td className="py-0.5 text-[#55555B]">공간 합계</td>
              <td className="py-0.5 text-right">{won(t.roomsNet)}</td>
            </tr>
            {t.travel > 0 && (
              <tr>
                <td className="py-0.5 text-[#55555B]">출장비</td>
                <td className="py-0.5 text-right">{won(t.travel)}</td>
              </tr>
            )}
            {t.shipping > 0 && (
              <tr>
                <td className="py-0.5 text-[#55555B]">배송비</td>
                <td className="py-0.5 text-right">{won(t.shipping)}</td>
              </tr>
            )}
            {t.siteDiscount > 0 && (
              <tr>
                <td className="py-0.5 text-[#55555B]">추가 할인</td>
                <td className="py-0.5 text-right">−{won(t.siteDiscount)}</td>
              </tr>
            )}
            {s.vatMode !== 'none' && (
              <>
                <tr>
                  <td className="py-0.5 text-[#55555B]">공급가액</td>
                  <td className="py-0.5 text-right">{won(t.supply)}</td>
                </tr>
                <tr>
                  <td className="py-0.5 text-[#55555B]">부가세 ({s.vatRate}%)</td>
                  <td className="py-0.5 text-right">{won(t.vat)}</td>
                </tr>
              </>
            )}
            {t.roundAdj > 0 && (
              <tr>
                <td className="py-0.5 text-[#55555B]">끝전 절사</td>
                <td className="py-0.5 text-right">−{won(t.roundAdj)}</td>
              </tr>
            )}
            <tr className="border-t-2 border-[#1F2023]">
              <td className="pt-1.5 font-bold">합계</td>
              <td className="pt-1.5 text-right text-[15px] font-extrabold">{won(t.total)}</td>
            </tr>
          </tbody>
        </table>
      </section>

      {q.showNotes && info.notes.trim() && (
        <section className="mt-5 rounded-[6px] border border-[#E2E0DB] px-4 py-3">
          <div className="mb-1 text-[11px] font-semibold text-[#76767B]">특이사항</div>
          <p className="whitespace-pre-wrap text-[12px]">{info.notes}</p>
        </section>
      )}
      {t.pendingRooms > 0 && <p className="mt-4 text-[11px] text-[#A6834E]">※ 실측이 끝나지 않은 공간 {t.pendingRooms}곳은 이 견적에 포함되지 않았습니다.</p>}
      <footer className="mt-6 border-t border-[#E2E0DB] pt-3 text-[11px] leading-relaxed text-[#66666B]">
        {q.footer && <p className="whitespace-pre-wrap">{q.footer}</p>}
        <p className="mt-1">치수 단위: {unit} · 원단 소요량은 재단 여유를 포함한 구매 기준 길이입니다.</p>
      </footer>
    </div>
  );
}

function ScaledSheet({ children }: { children: React.ReactNode }) {
  const box = useRef<HTMLDivElement>(null);
  const inner = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);
  const [h, setH] = useState<number | undefined>();
  useLayoutEffect(() => {
    const el = box.current;
    if (!el) return;
    const fit = () => {
      const sheetW = 794; // 210mm @96dpi
      const sc = Math.min(1, el.clientWidth / sheetW);
      setScale(sc);
      setH((inner.current?.scrollHeight ?? 1123) * sc);
    };
    fit();
    const ro = new ResizeObserver(fit);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  return (
    <div ref={box} className="w-full overflow-hidden" style={{ height: h }}>
      <div ref={inner} style={{ width: 794, transform: `scale(${scale})`, transformOrigin: 'top left' }} className="shadow-card">
        {children}
      </div>
    </div>
  );
}

export function QuoteModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { state, calc } = useStore();
  const { toast } = useUi();
  const [printRoot, setPrintRoot] = useState<HTMLElement | null>(null);
  useEffect(() => setPrintRoot(document.getElementById('print-root')), []);
  const sheet = <QuoteSheet site={state.site} calc={calc} s={state.settings} />;
  return (
    <>
      <Modal
        open={open}
        onClose={onClose}
        wide
        title="고객용 견적서 (A4)"
        footer={
          <>
            <button
              type="button"
              className="btn btn-ghost"
              onClick={async () => {
                const ok = await copyText(siteText(state.site, calc, state.settings));
                toast(ok ? '견적 내용을 복사했습니다.' : '복사하지 못했습니다.', ok ? 'ok' : 'warn');
              }}
            >
              <Icon name="copy" size={16} />
              텍스트 복사
            </button>
            {!IS_ARTIFACT && (
              <button type="button" className="btn btn-primary" onClick={() => window.print()}>
                <Icon name="print" size={16} />
                인쇄 / PDF 저장
              </button>
            )}
          </>
        }
      >
        {IS_ARTIFACT && (
          <p className="no-print mb-3 rounded-[10px] bg-sunk px-3 py-2.5 text-[12.5px] leading-relaxed text-ink2">
            이 미리보기 화면은 인쇄 창을 열 수 없습니다. 인쇄·PDF 저장은 PC용 파일(ACRO_CURTAIN_PRO.html)을 크롬으로 열어 사용하세요. 원가·마진은 견적서에 표시되지 않습니다.
          </p>
        )}
        <div className="rounded-[12px] bg-sunk p-3 sm:p-5">
          <ScaledSheet>{sheet}</ScaledSheet>
        </div>
      </Modal>
      {open && printRoot && !IS_ARTIFACT && createPortal(sheet, printRoot)}
    </>
  );
}
