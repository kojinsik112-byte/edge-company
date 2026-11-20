import { ruleFromPreset } from '../lib/defaults';
import { fmt, fmtLen, type Unit } from '../lib/num';
import type { BlindCalc } from '../lib/quote';
import { blindRuleFor } from '../lib/quote';
import type { BlindRoom, BlindRule, Settings } from '../lib/types';
import { BLIND_TYPES, MOUNTS, SPACES } from '../lib/types';
import { useMedia, useStore, useUi } from '../store';
import { BlindDiagram } from './Diagram';
import { DiscountEditor, EmptyRooms, Metric, OptionsEditor, PriceRow, QuoteBreakdown, RoomStrip, useActiveRoom } from './RoomParts';
import { Card, Disclosure, Icon, IssueList, LengthField, NumberField, Pill, Seg, SelectField, TextField, Toggle } from './ui';

type Patch = (r: BlindRoom) => void;

const ROUND_MODES = [
  { value: 'ceil' as const, label: '올림' },
  { value: 'round' as const, label: '반올림' },
  { value: 'floor' as const, label: '내림' },
];

export function ruleSummary(r: BlindRule, unit: Unit) {
  const L = (v: number) => fmtLen(v, unit);
  const adj = (d: number, a: number) => `${d ? `−${L(d)}` : ''}${a ? ` +${L(a)}` : ''}`.trim();
  const parts: string[] = [];
  if (r.deductW || r.addW) parts.push(`가로 ${adj(r.deductW, r.addW)}`);
  if (r.deductH || r.addH) parts.push(`세로 ${adj(r.deductH, r.addH)}`);
  if (!parts.length) parts.push('공제·추가 없음');
  if (r.roundUnit) parts.push(`${L(r.roundUnit)} ${ROUND_MODES.find((m) => m.value === r.roundMode)?.label}`);
  if (r.minW || r.maxW) parts.push(`폭 ${r.minW ? L(r.minW) : '–'}~${r.maxW ? L(r.maxW) : '–'}`);
  if (r.minH || r.maxH) parts.push(`높이 ${r.minH ? L(r.minH) : '–'}~${r.maxH ? L(r.maxH) : '–'}`);
  return parts.join(' · ');
}

export function RuleEditor({ value, onChange, unit, disabled }: { value: BlindRule; onChange: (r: BlindRule) => void; unit: Unit; disabled?: boolean }) {
  const f = (k: keyof BlindRule, label: string, hint?: string) => (
    <LengthField key={k} label={label} unit={unit} size="sm" value={value[k] as number} onChange={(v) => onChange({ ...value, [k]: v ?? 0 })} hint={hint} nav={!disabled} />
  );
  return (
    <div className={`flex flex-col gap-3.5 ${disabled ? 'pointer-events-none opacity-60' : ''}`} aria-disabled={disabled}>
      <div className="grid grid-cols-2 gap-3">
        {f('deductW', '가로 차감값')}
        {f('addW', '가로 추가값')}
        {f('deductH', '세로 차감값')}
        {f('addH', '세로 추가값')}
        {f('minW', '최소 제작 폭', '0 = 미설정')}
        {f('maxW', '최대 제작 폭', '0 = 미설정')}
        {f('minH', '최소 제작 높이', '0 = 미설정')}
        {f('maxH', '최대 제작 높이', '0 = 미설정')}
        {f('roundUnit', '계산 반올림 단위', '0 = 반올림 없음')}
        <div className="min-w-0">
          <div className="mb-1.5 text-[13px] font-semibold text-ink2">반올림 방식</div>
          <Seg value={value.roundMode} options={ROUND_MODES} onChange={(m) => onChange({ ...value, roundMode: m })} label="반올림 방식" />
        </div>
      </div>
    </div>
  );
}

function MeasureCard({ rc, patch, s }: { rc: BlindCalc; patch: (p: Patch) => void; s: Settings }) {
  const r = rc.room;
  const unit = s.unit;
  const fieldErr = (f: string) => rc.result.issues.find((i) => i.field === f && i.level === 'error' && i.code !== 'empty')?.message;
  const setType = (t: BlindRoom['blindType']) =>
    patch((x) => {
      x.blindType = t;
      const p = s.blindPresets[t];
      if (p.unitPrice !== null) {
        x.priceMode = p.priceMode;
        x.unitPrice = p.unitPrice;
        x.unitCost = p.unitCost;
      }
      if (p.install !== null) x.install = p.install;
    });
  return (
    <Card eyebrow="실측 입력" title={rc.label}>
      <div className="flex flex-col gap-5">
        <div className="grid grid-cols-2 gap-3">
          <LengthField id="b-width" label="실측 가로" unit={unit} size="xl" value={r.width} onChange={(v) => patch((x) => (x.width = v))} placeholder="0" error={fieldErr('width')} />
          <LengthField id="b-height" label="실측 세로" unit={unit} size="xl" value={r.height} onChange={(v) => patch((x) => (x.height = v))} placeholder="0" error={fieldErr('height')} />
        </div>
        <div>
          <div className="mb-2 text-[14px] font-bold">제품 종류</div>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
            {BLIND_TYPES.map((t) => (
              <button key={t} type="button" className="chip h-11 justify-between px-3 text-[14px]" aria-pressed={r.blindType === t} onClick={() => setType(t)}>
                <span className="truncate">{t}</span>
                {!s.blindPresets[t].verified && <span className={`ml-1 h-1.5 w-1.5 shrink-0 rounded-full ${r.blindType === t ? 'bg-onprimary/60' : 'bg-warn'}`} title="제작 기준 미확인" />}
              </button>
            ))}
          </div>
          {r.blindType === '기타' && (
            <TextField className="mt-2" label="제품명 직접 입력" value={r.blindTypeCustom} onChange={(v) => patch((x) => (x.blindTypeCustom = v))} placeholder="예: 버티컬" />
          )}
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-[minmax(0,1fr)_auto]">
          <div>
            <div className="mb-2 text-[14px] font-bold">설치 방식</div>
            <Seg value={r.mount} options={MOUNTS} onChange={(m) => patch((x) => (x.mount = m))} label="설치 방식" />
          </div>
          <div>
            <div className="mb-2 text-[14px] font-bold">수량</div>
            <div className="flex items-center gap-1.5">
              <button type="button" className="btn btn-ghost h-11 w-11 px-0" aria-label="수량 줄이기" onClick={() => patch((x) => (x.qty = Math.max(1, (x.qty ?? 1) - 1)))}>
                <Icon name="minus" />
              </button>
              <NumberField className="w-20" size="sm" integer min={1} value={r.qty} onChange={(v) => patch((x) => (x.qty = v))} suffix="개" ariaLabel="수량" error={fieldErr('qty')} />
              <button type="button" className="btn btn-ghost h-11 w-11 px-0" aria-label="수량 늘리기" onClick={() => patch((x) => (x.qty = Math.min(999, (x.qty ?? 0) + 1)))}>
                <Icon name="plus" />
              </button>
            </div>
          </div>
        </div>
        <p className="-mt-1 text-[12.5px] text-ink3">블라인드는 커튼 주름 배수를 적용하지 않습니다. 실측 사이즈에 제조사 공제·추가 기준을 반영해 주문 사이즈를 만듭니다.</p>
      </div>
    </Card>
  );
}

export function BlindResultCard({ rc }: { rc: BlindCalc }) {
  const { state } = useStore();
  const s = state.settings;
  const unit = s.unit;
  const r = rc.result;
  const { preset, rule } = blindRuleFor(rc.room, s);
  const verified = preset.verified || rc.room.customRule !== null;
  const L = (v: number) => fmtLen(v, unit, false);
  const head = (
    <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
      <div className="eyebrow">블라인드 계산 결과</div>
      <div className="flex flex-wrap items-center gap-1.5">
        <Pill>{MOUNTS.find((m) => m.value === rc.room.mount)?.label}</Pill>
        {!verified ? <Pill tone="warn">제작 기준 확인 필요</Pill> : <Pill tone="ok">{rc.room.customRule ? '공간별 기준' : '제조사 기준 적용'}</Pill>}
        {r.ok && !r.producible && <Pill tone="err">제작 범위 초과</Pill>}
      </div>
    </div>
  );
  if (!r.ok) {
    const empty = r.issues.every((i) => i.code === 'empty');
    return (
      <section className="card p-4 sm:p-5">
        {head}
        {empty ? (
          <div className="flex flex-col items-start gap-2 py-4">
            <div className="num text-[44px] font-extrabold leading-none text-ink3/40">– × –</div>
            <p className="text-[14px] text-ink2">실측 가로·세로를 입력하면 주문 사이즈와 면적이 바로 계산됩니다.</p>
          </div>
        ) : (
          <IssueList issues={r.issues} />
        )}
      </section>
    );
  }
  return (
    <section className="card rise p-4 sm:p-5" aria-live="polite">
      {head}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <Metric label="실측 사이즈" value={`${L(r.width)} × ${L(r.height)}`} unit={unit} caption="현장에서 잰 값" />
        <Metric hero label="주문 제작 사이즈" value={`${L(r.orderW)} × ${L(r.orderH)}`} unit={unit} caption={ruleSummary(rule, unit)} tone={r.producible ? undefined : 'err'} />
      </div>
      <div className="mt-5 grid grid-cols-3 gap-3 border-t border-line pt-4">
        <Metric label="실측 면적" value={fmt(r.measuredArea, 2)} unit="㎡" caption={`${fmt(r.width / 100, 3)} × ${fmt(r.height / 100, 3)}`} />
        <Metric label="주문 면적" value={fmt(r.orderArea, 2)} unit="㎡" caption={`${fmt(r.orderW / 100, 3)} × ${fmt(r.orderH / 100, 3)}`} />
        <Metric
          label="청구 면적"
          value={fmt(r.billArea, 2)}
          unit="㎡"
          tone="gold"
          caption={
            [
              preset.billing.basis === 'order' ? '주문 사이즈 기준' : '실측 기준',
              r.minSizeApplied ? '최소 청구 규격 적용' : null,
              r.minAreaApplied ? `최소 ${fmt(preset.billing.minBillArea, 2)}㎡ 적용` : null,
              r.qty > 1 ? `× ${r.qty}개 = ${fmt(r.billAreaTotal, 2)}㎡` : null,
            ]
              .filter(Boolean)
              .join(' · ') || undefined
          }
        />
      </div>
      {r.issues.length > 0 && (
        <div className="mt-4">
          <IssueList issues={r.issues} />
        </div>
      )}
    </section>
  );
}

function RuleCard({ rc, patch, s }: { rc: BlindCalc; patch: (p: Patch) => void; s: Settings }) {
  const r = rc.room;
  const { preset, rule } = blindRuleFor(r, s);
  return (
    <Card eyebrow="제작 기준" title="공제·제작 범위">
      <div className="flex flex-col gap-4">
        <div className="rounded-[10px] bg-sunk px-3.5 py-3 text-[13.5px] leading-relaxed text-ink2">
          {r.customRule ? (
            <>이 공간은 직접 입력한 기준을 씁니다.</>
          ) : preset.verified ? (
            <>
              환경설정의 <b>{r.blindType}</b> · {MOUNTS.find((m) => m.value === r.mount)?.label} 기준을 씁니다.{preset.makerNote && <> ({preset.makerNote})</>}
            </>
          ) : (
            <>
              <b className="text-warn">제작 기준 확인 필요</b> — {r.blindType}의 제조사 공제·제작 기준이 아직 입력되지 않았습니다. 지금은 입력한 값({ruleSummary(rule, s.unit)})만 적용됩니다. 환경설정 → 블라인드 제작 기준에서 입력하세요.
            </>
          )}
        </div>
        <Toggle
          checked={!!r.customRule}
          onChange={(on) => patch((x) => (x.customRule = on ? ruleFromPreset(preset, x.mount) : null))}
          label="이 공간만 직접 입력"
          hint="현장 상황(창틀 기울기·간섭물)에 맞춰 이 공간에만 다른 공제값을 씁니다."
        />
        <RuleEditor unit={s.unit} value={r.customRule ?? rule} disabled={!r.customRule} onChange={(v) => patch((x) => (x.customRule = v))} />
      </div>
    </Card>
  );
}

function DetailCard({ rc, patch }: { rc: BlindCalc; patch: (p: Patch) => void }) {
  const r = rc.room;
  return (
    <Card eyebrow="공간 정보" title="공간 정보">
      <div className="grid grid-cols-2 gap-3">
        <SelectField label="공간명" value={r.space} options={SPACES} onChange={(v) => patch((x) => (x.space = v))} />
        {r.space === '기타' ? (
          <TextField label="공간명 직접 입력" value={r.spaceCustom} onChange={(v) => patch((x) => (x.spaceCustom = v))} placeholder="예: 서재" />
        ) : (
          <div />
        )}
        <TextField className="col-span-2" label="설치 위치명" value={r.location} onChange={(v) => patch((x) => (x.location = v))} placeholder="예: 작은방 1 창" />
        <TextField className="col-span-2" label="메모" value={r.memo} onChange={(v) => patch((x) => (x.memo = v))} placeholder="현장 특이사항 (견적서에는 표시되지 않음)" />
      </div>
    </Card>
  );
}

function PricingCard({ rc, patch, s }: { rc: BlindCalc; patch: (p: Patch) => void; s: Settings }) {
  const { toast } = useUi();
  const r = rc.room;
  const admin = s.adminMode;
  const preset = s.blindPresets[r.blindType];
  return (
    <Card
      eyebrow="견적"
      title="이 공간 견적"
      action={
        <button
          type="button"
          className="btn btn-quiet min-h-[34px] px-2 text-[13px]"
          onClick={() => {
            patch((x) => {
              x.priceMode = preset.priceMode;
              x.unitPrice = preset.unitPrice;
              x.unitCost = preset.unitCost;
              x.install = preset.install;
            });
            toast(`${r.blindType} 기본 단가를 불러왔습니다.`);
          }}
        >
          기본 단가 불러오기
        </button>
      }
    >
      <PriceRow
        label="제품 단가"
        admin={admin}
        modes={[
          { value: 'area', label: '㎡ 단가' },
          { value: 'each', label: '개당 정액' },
        ]}
        mode={r.priceMode}
        onMode={(m) => patch((x) => (x.priceMode = m))}
        price={r.unitPrice}
        onPrice={(v) => patch((x) => (x.unitPrice = v))}
        cost={r.unitCost}
        onCost={(v) => patch((x) => (x.unitCost = v))}
        hint={r.priceMode === 'area' ? '청구 면적(㎡) × ㎡ 단가 × 수량' : '개당 단가 × 수량'}
      />
      <PriceRow label="설치비 (개당)" admin={admin} price={r.install} onPrice={(v) => patch((x) => (x.install = v))} cost={r.installCost} onCost={(v) => patch((x) => (x.installCost = v))} />
      <OptionsEditor admin={admin} options={r.options} onChange={(o) => patch((x) => (x.options = o))} />
      <DiscountEditor value={r.discount} onChange={(d) => patch((x) => (x.discount = d))} label="공간 할인" />
      <div className="mt-2 flex flex-col gap-3">
        <IssueList issues={rc.quote.issues} />
        <QuoteBreakdown
          quote={rc.quote}
          admin={admin}
          note={preset.billing.minCharge > 0 ? `최소 제작 요금 ${fmt(preset.billing.minCharge, 0)}원 적용 기준` : '부가세·배송비는 현장 전체 합계에서 한 번 계산합니다.'}
        />
        {admin && (
          <button
            type="button"
            className="btn btn-ghost self-start text-[13px]"
            onClick={() => {
              const k = 1 + s.marginRate / 100;
              const fill = (c: number | null | undefined, cur: number | null) => (c !== null && c !== undefined ? Math.round((c * k) / 100) * 100 : cur);
              patch((x) => {
                x.unitPrice = fill(x.unitCost, x.unitPrice);
                x.install = fill(x.installCost, x.install);
                x.options.forEach((o) => (o.amount = fill(o.cost, o.amount)));
              });
              toast(`원가에 마진 ${s.marginRate}%를 붙여 판매가를 채웠습니다.`);
            }}
          >
            마진율 {s.marginRate}%로 판매가 채우기
          </button>
        )}
      </div>
    </Card>
  );
}

export function BlindTab() {
  const { state, updateRoom } = useStore();
  const rc = useActiveRoom('blind');
  const wideScreen = useMedia('(min-width: 1024px)');
  const s = state.settings;
  if (!rc)
    return (
      <div className="flex flex-col gap-4">
        <RoomStrip kind="blind" />
        <EmptyRooms kind="blind" />
      </div>
    );
  const patch = (p: Patch) => updateRoom(rc.room.id, (r) => p(r as BlindRoom));
  const measure = <MeasureCard rc={rc} patch={patch} s={s} />;
  const result = <BlindResultCard rc={rc} />;
  const diagram = (
    <Card eyebrow="모식도" title="실측 vs 주문 사이즈">
      <BlindDiagram result={rc.result} unit={s.unit} mount={rc.room.mount} type={rc.room.blindType} />
      <p className="mt-2 text-[12px] leading-relaxed text-ink3">참고용 모식도입니다. 공제·추가 치수는 보기 쉽게 과장해 그렸습니다.</p>
    </Card>
  );
  const rule = <RuleCard rc={rc} patch={patch} s={s} />;
  const detail = <DetailCard rc={rc} patch={patch} />;
  const pricing = <PricingCard rc={rc} patch={patch} s={s} />;
  return (
    <div className="flex flex-col gap-4">
      <RoomStrip kind="blind" />
      {wideScreen ? (
        <div className="grid grid-cols-[minmax(0,1fr)_minmax(0,1.05fr)] items-start gap-4">
          <div className="flex min-w-0 flex-col gap-4">
            {measure}
            {rule}
            {pricing}
          </div>
          <div className="flex min-w-0 flex-col gap-4">
            {result}
            {diagram}
            {detail}
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          {measure}
          {result}
          {diagram}
          <Disclosure title="제작 기준 · 공간 정보" sub={ruleSummary(blindRuleFor(rc.room, s).rule, s.unit)}>
            <div className="flex flex-col gap-4">
              {rule}
              {detail}
            </div>
          </Disclosure>
          {pricing}
        </div>
      )}
    </div>
  );
}
