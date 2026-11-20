import { emptySite, structuredCloneSafe } from '../lib/defaults';
import { fmt, fmtMeters, koreanWon, uid, won } from '../lib/num';
import { calcSite, CATEGORY_LABEL, type Category } from '../lib/quote';
import { useStore, useUi } from '../store';
import { DiscountEditor } from './RoomParts';
import { Card, Icon, Modal, NumberField, Pill, TextField } from './ui';

export function siteTitle(info: { apartment: string; dongho: string; customer: string }) {
  return [info.apartment, info.dongho].filter((x) => x.trim()).join(' ') || '이름 없는 현장';
}

export function SiteBar({ onOpenRecent }: { onOpenRecent: () => void }) {
  const { state, update } = useStore();
  const { confirm, toast } = useUi();
  const site = state.site;
  const info = site.info;
  const open = state.ui.siteOpen;
  const setInfo = (k: keyof typeof info, v: string) => update((d) => void (d.site.info[k] = v));

  const archive = (d: typeof state) => {
    const i = d.recent.findIndex((r) => r.site.id === d.site.id);
    const entry = { id: uid('r'), savedAt: Date.now(), site: structuredCloneSafe(d.site) };
    if (i >= 0) d.recent.splice(i, 1);
    d.recent.unshift(entry);
    d.recent = d.recent.slice(0, 30);
  };

  const newSite = async () => {
    const ok = await confirm({
      title: '새 현장을 시작할까요?',
      body: site.isSample ? '예시 현장을 비우고 빈 현장을 엽니다.' : '현재 현장은 「최근 현장」 목록에 저장되고, 빈 현장이 열립니다.',
      confirmLabel: '새 현장',
    });
    if (!ok) return;
    update((d) => {
      if (!d.site.isSample) archive(d);
      d.site = emptySite(d.settings);
      d.ui.activeCurtain = d.site.rooms[0].id;
      d.ui.activeBlind = null;
      d.ui.siteOpen = true;
      d.ui.tab = 'curtain';
    }, 'force');
    toast('새 현장을 시작했습니다.');
  };

  const save = () => {
    update((d) => {
      d.site.isSample = false;
      archive(d);
    }, 'none');
    toast('최근 현장 목록에 저장했습니다.');
  };

  return (
    <section className="card min-w-0">
      {site.isSample && (
        <div className="flex flex-wrap items-center justify-between gap-2 rounded-t-[13px] border-b border-gold/30 bg-goldsoft px-4 py-2.5 text-[13.5px]">
          <span className="font-semibold text-ink">
            <span className="text-gold">예시 현장</span> — 숫자와 단가는 보여 드리기 위한 예시입니다.
          </span>
          <button type="button" className="btn btn-primary min-h-[34px] px-3 text-[13px]" onClick={newSite}>
            새 현장으로 시작
          </button>
        </div>
      )}
      <div className="flex flex-wrap items-center gap-x-3 gap-y-2 px-4 py-3">
        <button type="button" onClick={() => update((d) => void (d.ui.siteOpen = !d.ui.siteOpen), 'none')} className="flex min-w-0 flex-1 basis-[15rem] items-center gap-3 text-left" aria-expanded={open}>
          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-[10px] bg-sunk text-gold">
            <Icon name="ruler" size={18} />
          </span>
          <span className="min-w-0">
            <span className="block truncate text-[15px] font-bold">{siteTitle(info)}</span>
            <span className="block truncate text-[12.5px] text-ink3">
              {[info.customer && `고객 ${info.customer}`, info.date && `실측 ${info.date}`, info.surveyor && `담당 ${info.surveyor}`].filter(Boolean).join(' · ') || '현장 정보를 입력하세요'}
            </span>
          </span>
          <Icon name="down" size={18} className={`ml-auto shrink-0 text-ink3 transition ${open ? 'rotate-180' : ''}`} />
        </button>
        <div className="-ml-2 flex shrink-0 items-center gap-1 sm:ml-0">
          <button type="button" className="btn btn-quiet min-h-[36px] px-2.5 text-[13px]" onClick={newSite}>
            <Icon name="plus" size={16} />새 현장
          </button>
          <button type="button" className="btn btn-quiet min-h-[36px] px-2.5 text-[13px]" onClick={onOpenRecent}>
            <Icon name="folder" size={16} />
            최근
          </button>
          <button type="button" className="btn btn-quiet min-h-[36px] px-2.5 text-[13px]" onClick={save}>
            <Icon name="save" size={16} />
            저장
          </button>
        </div>
      </div>
      {open && (
        <div className="border-t border-line px-4 pb-4 pt-3">
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            <TextField label="아파트명" value={info.apartment} onChange={(v) => setInfo('apartment', v)} placeholder="예: 래미안 OO" />
            <TextField label="동 / 호수" value={info.dongho} onChange={(v) => setInfo('dongho', v)} placeholder="101동 1203호" />
            <TextField label="고객명" value={info.customer} onChange={(v) => setInfo('customer', v)} />
            <TextField label="연락처" value={info.phone} onChange={(v) => setInfo('phone', v)} type="tel" inputMode="tel" placeholder="010-0000-0000" />
            <TextField label="실측 담당자" value={info.surveyor} onChange={(v) => setInfo('surveyor', v)} />
            <TextField label="실측 날짜" value={info.date} onChange={(v) => setInfo('date', v)} type="date" />
            <TextField className="col-span-2" label="특이사항" value={info.notes} onChange={(v) => setInfo('notes', v)} placeholder="커튼박스 깊이, 몰딩 간섭, 콘센트 위치 등" />
          </div>
          <p className="mt-3 flex items-center gap-1.5 text-[12px] text-ink3">
            <Icon name="shield" size={14} />
            고객 정보는 이 기기에만 저장됩니다. 환경설정 → 데이터에서 삭제할 수 있습니다.
          </p>
        </div>
      )}
    </section>
  );
}

export function RecentModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { state, update } = useStore();
  const { confirm, toast } = useUi();
  return (
    <Modal open={open} onClose={onClose} title={`최근 작업 현장 (${state.recent.length})`}>
      {state.recent.length === 0 ? (
        <p className="py-6 text-center text-[14px] text-ink3">
          저장한 현장이 없습니다. 현장 정보 줄의 「저장」이나 「새 현장」을 누르면 여기에 보관됩니다.
        </p>
      ) : (
        <ul className="flex flex-col divide-y divide-line">
          {state.recent.map((e) => {
            const t = calcSite(e.site, state.settings).totals;
            return (
              <li key={e.id} className="flex items-center gap-3 py-3">
                <div className="min-w-0 flex-1">
                  <div className="truncate text-[14.5px] font-bold">{siteTitle(e.site.info)}</div>
                  <div className="truncate text-[12.5px] text-ink3">
                    {[e.site.info.customer, `공간 ${e.site.rooms.length}곳`, t.total ? won(t.total) : null, new Date(e.savedAt).toLocaleString('ko-KR', { dateStyle: 'short', timeStyle: 'short' })]
                      .filter(Boolean)
                      .join(' · ')}
                  </div>
                </div>
                <button
                  type="button"
                  className="btn btn-ghost min-h-[36px] px-3 text-[13px]"
                  onClick={() => {
                    update((d) => {
                      const cur = structuredCloneSafe(d.site);
                      const idx = d.recent.findIndex((r) => r.id === e.id);
                      const loaded = structuredCloneSafe(d.recent[idx].site);
                      d.recent.splice(idx, 1);
                      if (!cur.isSample) {
                        const dup = d.recent.findIndex((r) => r.site.id === cur.id);
                        if (dup >= 0) d.recent.splice(dup, 1);
                        d.recent.unshift({ id: uid('r'), savedAt: Date.now(), site: cur });
                      }
                      d.site = loaded;
                      d.ui.activeCurtain = loaded.rooms.find((r) => r.kind === 'curtain')?.id ?? null;
                      d.ui.activeBlind = loaded.rooms.find((r) => r.kind === 'blind')?.id ?? null;
                    }, 'force');
                    onClose();
                    toast('현장을 불러왔습니다.');
                  }}
                >
                  열기
                </button>
                <button
                  type="button"
                  className="btn btn-quiet min-h-[36px] px-2"
                  aria-label="목록에서 삭제"
                  onClick={async () => {
                    const ok = await confirm({ title: `「${siteTitle(e.site.info)}」을 목록에서 삭제할까요?`, body: '이 현장의 저장 데이터가 이 기기에서 지워집니다.', confirmLabel: '삭제', danger: true });
                    if (ok) update((d) => void (d.recent = d.recent.filter((r) => r.id !== e.id)), 'none');
                  }}
                >
                  <Icon name="trash" size={16} />
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </Modal>
  );
}

function Stat({ label, value, unit, sub }: { label: string; value: string; unit?: string; sub?: string }) {
  return (
    <div className="min-w-0 rounded-[12px] bg-sunk px-3.5 py-3">
      <div className="text-[12.5px] font-semibold text-ink2">{label}</div>
      <div className="num mt-0.5 flex items-baseline gap-1">
        <span className="text-[24px] font-extrabold leading-tight">{value}</span>
        {unit && <span className="text-[13px] font-bold text-ink2">{unit}</span>}
      </div>
      {sub && <div className="mt-0.5 truncate text-[11.5px] text-ink3">{sub}</div>}
    </div>
  );
}

export function SiteSummary({ onQuote, onCopy }: { onQuote: () => void; onCopy: () => void }) {
  const { state, calc, update } = useStore();
  const s = state.settings;
  const t = calc.totals;
  const c = state.site.common;
  const go = (id: string, kind: 'curtain' | 'blind') => {
    update((d) => {
      d.ui.tab = kind;
      if (kind === 'curtain') d.ui.activeCurtain = id;
      else d.ui.activeBlind = id;
    }, 'none');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };
  return (
    <Card
      id="site-summary"
      eyebrow="현장 전체"
      title="현장 전체 합계"
      action={
        <>
          <button type="button" className="btn btn-quiet min-h-[36px] px-2.5 text-[13px]" onClick={onCopy}>
            <Icon name="copy" size={16} />
            복사
          </button>
          <button type="button" className="btn btn-primary min-h-[36px] px-3 text-[13px]" onClick={onQuote}>
            <Icon name="doc" size={16} />
            견적서
          </button>
        </>
      }
    >
      <div className="grid grid-cols-2 gap-2.5 md:grid-cols-4">
        <Stat label="커튼 총 폭 수" value={String(t.curtainWidths)} unit="폭" sub={`커튼 ${t.curtainRooms}곳`} />
        <Stat label="커튼 총 원단 길이" value={fmtMeters(t.curtainLength)} unit="m" sub="구매 기준 길이 합계" />
        <Stat label="블라인드 총 개수" value={String(t.blindCount)} unit="개" sub={`블라인드 ${t.blindRooms}곳`} />
        <Stat label="블라인드 총 면적" value={fmt(t.blindBillArea, 2)} unit="㎡" sub={`청구 기준 · 실측 ${fmt(t.blindMeasuredArea, 2)}㎡`} />
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)]">
        <div className="min-w-0 overflow-x-auto">
          <table className="w-full min-w-[360px] text-[13.5px]">
            <thead>
              <tr className="border-b border-line text-left text-[12px] text-ink3">
                <th className="py-2 pr-2 font-semibold">공간</th>
                <th className="px-2 py-2 font-semibold">내용</th>
                <th className="py-2 pl-2 text-right font-semibold">금액</th>
              </tr>
            </thead>
            <tbody>
              {calc.rooms.map((rc) => (
                <tr key={rc.room.id} className="cursor-pointer border-b border-line/70 hover:bg-sunk" onClick={() => go(rc.room.id, rc.kind)}>
                  <td className="py-2.5 pr-2 font-semibold">
                    <span className="block max-w-[9rem] truncate">{rc.label}</span>
                  </td>
                  <td className="num px-2 py-2.5 text-ink2">
                    {rc.kind === 'curtain'
                      ? rc.result.ok
                        ? `${rc.room.curtainType} · ${rc.result.method === 'joined' ? `${rc.result.totalWidths}폭 · ` : '광폭 · '}${fmtMeters(rc.result.totalLength)}m`
                        : '입력 전'
                      : rc.result.ok
                        ? `${rc.room.blindType} · ${fmt(rc.result.billAreaTotal, 2)}㎡ · ${rc.result.qty}개`
                        : '입력 전'}
                    {rc.result.ok && !rc.result.producible && (
                      <span className="ml-1.5">
                        <Pill tone="err">확인</Pill>
                      </span>
                    )}
                  </td>
                  <td className="num py-2.5 pl-2 text-right font-bold">{rc.quote.total ? won(rc.quote.total) : '–'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {t.pendingRooms > 0 && <p className="mt-2 text-[12.5px] text-warn">계산이 끝나지 않은 공간 {t.pendingRooms}곳은 합계에서 빠져 있습니다.</p>}
        </div>

        <div className="min-w-0 rounded-[12px] border border-line p-3.5">
          <ul className="flex flex-col gap-1.5 text-[14px]">
            {(Object.keys(CATEGORY_LABEL) as Category[]).map((k) => (
              <li key={k} className="flex justify-between">
                <span className="text-ink2">{CATEGORY_LABEL[k]} 합계</span>
                <span className="num font-semibold">{won(t.cat[k])}</span>
              </li>
            ))}
            {t.roomDiscount > 0 && (
              <li className="flex justify-between text-ink2">
                <span>공간별 할인</span>
                <span className="num font-semibold">−{won(t.roomDiscount)}</span>
              </li>
            )}
          </ul>
          <div className="mt-3 grid grid-cols-2 gap-2 border-t border-line pt-3">
            <NumberField label="출장비 (현장 1회)" size="sm" suffix="원" min={0} value={c.travelFee} onChange={(v) => update((d) => void (d.site.common.travelFee = v))} />
            <NumberField label="배송비" size="sm" suffix="원" min={0} value={c.shippingFee} onChange={(v) => update((d) => void (d.site.common.shippingFee = v))} />
            {s.adminMode && (
              <>
                <NumberField label="출장 원가" size="sm" suffix="원" min={0} value={c.travelCost ?? null} onChange={(v) => update((d) => void (d.site.common.travelCost = v))} />
                <NumberField label="배송 원가" size="sm" suffix="원" min={0} value={c.shippingCost ?? null} onChange={(v) => update((d) => void (d.site.common.shippingCost = v))} />
              </>
            )}
          </div>
          <DiscountEditor value={c.discount} onChange={(dd) => update((d) => void (d.site.common.discount = dd))} label="추가 할인" />
          <ul className="flex flex-col gap-1.5 border-t border-line pt-3 text-[14px]">
            {t.siteDiscount > 0 && (
              <li className="flex justify-between text-ink2">
                <span>추가 할인</span>
                <span className="num font-semibold">−{won(t.siteDiscount)}</span>
              </li>
            )}
            {s.vatMode !== 'none' && (
              <>
                <li className="flex justify-between">
                  <span className="text-ink2">공급가액</span>
                  <span className="num font-semibold">{won(t.supply)}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-ink2">부가세 {s.vatRate}%{s.vatMode === 'included' ? ' (포함분)' : ''}</span>
                  <span className="num font-semibold">{won(t.vat)}</span>
                </li>
              </>
            )}
            {t.roundAdj > 0 && (
              <li className="flex justify-between text-ink2">
                <span>끝전 절사</span>
                <span className="num font-semibold">−{won(t.roundAdj)}</span>
              </li>
            )}
          </ul>
          <div className="mt-3 rounded-[12px] bg-primary px-4 py-3.5 text-onprimary">
            <div className="flex items-baseline justify-between gap-2">
              <span className="text-[13.5px] font-semibold opacity-80">최종 견적 합계</span>
              <span className="text-[12px] opacity-70">{s.vatMode === 'none' ? '부가세 미적용' : '부가세 포함'}</span>
            </div>
            <div className="num mt-1 text-[32px] font-extrabold leading-none">{won(t.total)}</div>
            <div className="mt-1 text-[12.5px] opacity-75">{koreanWon(t.total)}</div>
          </div>
          {s.adminMode && (
            <div className="mt-3 rounded-[10px] bg-sunk px-3 py-2.5 text-[13px]">
              <div className="flex justify-between">
                <span className="text-ink2">원가 합계{t.costKnown ? '' : ' (일부 미입력)'}</span>
                <span className="num font-semibold">{won(t.costTotal)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-ink2">마진 (공급가 기준)</span>
                <span className={`num font-bold ${t.margin < 0 ? 'text-err' : 'text-ok'}`}>
                  {won(t.margin)} · {fmt(t.marginRate, 1)}%
                </span>
              </div>
              <div className="mt-1 text-[11.5px] text-ink3">관리자 전용 — 견적서·복사 문구에는 나오지 않습니다.</div>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}
