import type { ReactNode } from 'react';
import { DEFAULT_CUT, structuredCloneSafe } from '../lib/defaults';
import { clean, fmt, fmtLen, fmtMeters, toUnit, UNIT_DEC, type Unit } from '../lib/num';
import type { CurtainCalc } from '../lib/quote';
import { curtainCut } from '../lib/quote';
import type { CurtainRoom, CutSettings, Settings } from '../lib/types';
import { CURTAIN_TYPES, SPACES } from '../lib/types';
import { useMedia, useStore, useUi } from '../store';
import { CurtainDiagram } from './Diagram';
import { DiscountEditor, EmptyRooms, Metric, OptionsEditor, PriceRow, QuoteBreakdown, RoomStrip, useActiveRoom } from './RoomParts';
import { Card, Disclosure, Icon, IssueList, LengthField, NumberField, Pill, Seg, SelectField, TextField, Toggle } from './ui';

export const FULLNESS_PRESETS = [1.0, 1.3, 1.5, 1.8, 2.0, 2.2, 2.5, 3.0];
export const FABRIC_PRESETS = [135, 140, 145, 150, 280];
const SPLITS: [number, number][] = [
  [50, 50],
  [60, 40],
  [40, 60],
  [70, 30],
];

type Patch = (r: CurtainRoom) => void;

export function FullnessPicker({ value, onChange, idPrefix }: { value: number | null; onChange: (v: number | null) => void; idPrefix: string }) {
  const r2 = (v: number | null) => (v === null ? null : Math.round(v * 100) / 100);
  return (
    <div className="flex flex-col gap-2.5">
      <div className="grid grid-cols-4 gap-2">
        {FULLNESS_PRESETS.map((f) => {
          const on = value !== null && Math.abs(value - f) < 1e-9;
          return (
            <button key={f} type="button" aria-pressed={on} onClick={() => onChange(f)} className="chip h-[54px] flex-col gap-0 px-1">
              <span className="num text-[19px] font-extrabold leading-none">{f.toFixed(1)}</span>
              <span className={`text-[11px] font-semibold ${on ? 'text-onprimary/70' : 'text-ink3'}`}>{f === 1 ? '민자' : '배'}</span>
            </button>
          );
        })}
      </div>
      <div className="flex items-center gap-3">
        <input
          type="range"
          min={1}
          max={4}
          step={0.05}
          value={value ?? 1.5}
          onChange={(e) => onChange(r2(Number(e.target.value)))}
          className="min-w-0 flex-1"
          aria-label="주름 배수 슬라이더"
        />
        <NumberField id={`${idPrefix}-fullness`} className="w-[7.5rem] shrink-0" value={value} onChange={(v) => onChange(r2(v))} suffix="배" size="sm" ariaLabel="주름 배수 직접 입력" />
      </div>
    </div>
  );
}

export function FabricPicker({ value, onChange, unit, idPrefix, hint }: { value: number | null; onChange: (v: number | null) => void; unit: Unit; idPrefix: string; hint?: ReactNode }) {
  return (
    <div className="flex flex-col gap-2.5">
      <div className="grid grid-cols-5 gap-2">
        {FABRIC_PRESETS.map((w) => (
          <button key={w} type="button" aria-pressed={value === w} onClick={() => onChange(w)} className="chip h-11 px-1">
            <span className="num text-[15.5px] font-bold">{fmt(toUnit(w, unit), UNIT_DEC[unit])}</span>
          </button>
        ))}
      </div>
      <LengthField id={`${idPrefix}-fabric`} unit={unit} value={value} onChange={onChange} size="sm" ariaLabel="원단 1폭 직접 입력" hint={hint} />
    </div>
  );
}

function Label({ children, sub }: { children: ReactNode; sub?: ReactNode }) {
  return (
    <div className="mb-2 flex items-baseline justify-between gap-2">
      <span className="text-[14px] font-bold">{children}</span>
      {sub && <span className="text-[12.5px] text-ink3">{sub}</span>}
    </div>
  );
}

function MeasureCard({ rc, patch, s }: { rc: CurtainCalc; patch: (p: Patch) => void; s: Settings }) {
  const r = rc.room;
  const unit = s.unit;
  const fieldErr = (f: string) => rc.result.issues.find((i) => i.field === f && i.level === 'error' && i.code !== 'empty')?.message;
  return (
    <Card eyebrow="실측 입력" title={rc.label}>
      <div className="flex flex-col gap-5">
        <div className="grid grid-cols-2 gap-3">
          <LengthField id="c-width" label="실측 가로" unit={unit} size="xl" value={r.width} onChange={(v) => patch((x) => (x.width = v))} placeholder="0" error={fieldErr('width')} />
          <LengthField id="c-height" label="실측 세로" unit={unit} size="xl" value={r.height} onChange={(v) => patch((x) => (x.height = v))} placeholder="0" error={fieldErr('height')} />
        </div>
        <div>
          <Label sub="기본 1.5배 · 소수 둘째 자리까지">주름 배수</Label>
          <FullnessPicker idPrefix="c" value={r.fullness} onChange={(v) => patch((x) => (x.fullness = v))} />
          {fieldErr('fullness') && <p className="mt-1 text-[12.5px] font-medium text-err">{fieldErr('fullness')}</p>}
        </div>
        <div>
          <Label sub={`기본 ${fmtLen(s.curtain.fabricWidth, unit)} · 환경설정에서 변경`}>{r.method === 'wide' ? '광폭 원단 롤 폭' : '원단 1폭'}</Label>
          <FabricPicker idPrefix="c" unit={unit} value={r.fabricWidth} onChange={(v) => patch((x) => (x.fabricWidth = v))} />
          {fieldErr('fabricWidth') && <p className="mt-1 text-[12.5px] font-medium text-err">{fieldErr('fabricWidth')}</p>}
        </div>
        <div className="grid grid-cols-1 gap-4">
          <div>
            <Label>설치 방식</Label>
            <Seg
              value={r.opening}
              label="설치 방식"
              options={[
                { value: 'double', label: '양개 (좌우 2장)' },
                { value: 'single', label: '편개 (1장)' },
              ]}
              onChange={(v) => patch((x) => (x.opening = v))}
            />
          </div>
          <div>
            <Label>제작 방식</Label>
            <Seg
              value={r.method}
              label="제작 방식"
              options={[
                { value: 'joined', label: '폭 연결형' },
                { value: 'wide', label: '광폭 원단형' },
              ]}
              onChange={(v) => patch((x) => (x.method = v))}
            />
          </div>
        </div>
        {r.opening === 'double' ? (
          <div>
            <Label sub="왼쪽 : 오른쪽">양개 좌우 비율</Label>
            <div className="flex flex-wrap gap-2">
              {SPLITS.map(([a, b]) => (
                <button
                  key={`${a}-${b}`}
                  type="button"
                  className="chip num h-10"
                  aria-pressed={r.splitLeft === a && r.splitRight === b}
                  onClick={() =>
                    patch((x) => {
                      x.splitLeft = a;
                      x.splitRight = b;
                    })
                  }
                >
                  {a}:{b}
                </button>
              ))}
              <div className="flex items-center gap-1.5">
                <NumberField className="w-[5.5rem]" size="sm" value={r.splitLeft} onChange={(v) => patch((x) => (x.splitLeft = v))} suffix="%" ariaLabel="왼쪽 비율" />
                <span className="text-ink3">:</span>
                <NumberField className="w-[5.5rem]" size="sm" value={r.splitRight} onChange={(v) => patch((x) => (x.splitRight = v))} suffix="%" ariaLabel="오른쪽 비율" />
              </div>
            </div>
            {fieldErr('split') && <p className="mt-1.5 text-[12.5px] font-medium text-err">{fieldErr('split')}</p>}
          </div>
        ) : (
          <div>
            <Label>커튼이 모이는 쪽</Label>
            <Seg
              value={r.gatherSide}
              label="커튼이 모이는 쪽"
              options={[
                { value: 'left', label: '왼쪽으로 모음' },
                { value: 'right', label: '오른쪽으로 모음' },
              ]}
              onChange={(v) => patch((x) => (x.gatherSide = v))}
            />
          </div>
        )}
        <p className="-mt-1 text-[12.5px] leading-relaxed text-ink3">
          {r.method === 'joined'
            ? '폭 연결형: 원단 폭 방향으로 여러 장을 이어 붙입니다. 필요 폭 수와 폭당 재단 길이를 계산합니다.'
            : '광폭 원단형: 원단을 가로로 눕혀 원단 폭이 커튼 높이가 됩니다. 원단 폭이 제작 높이를 충족하는지 확인하고, 롤 길이 방향으로 필요한 길이를 계산합니다.'}
        </p>
      </div>
    </Card>
  );
}

function captionWidths(rc: CurtainCalc, unit: Unit, cut: CutSettings) {
  const r = rc.result;
  const L = (v: number) => fmtLen(v, unit, false);
  if (r.opening === 'double') return r.panels.map((p) => `${p.side === 'left' ? '좌' : '우'} ${p.widths}폭`).join(' + ') + ` = ${r.totalWidths}폭`;
  const p = r.panels[0];
  if (cut.seamLoss === 0 && cut.sideHem === 0) return `${L(p.requiredWidth)} ÷ ${L(r.fabricWidth)} = ${fmt(p.rawRatio, 2)} → ${p.widths}폭`;
  return `유효 ${L(p.usableWidth)} ≥ 필요 ${L(p.requiredWidth)} → ${p.widths}폭`;
}

function cutCaption(r: CurtainCalc['result'], cut: CutSettings, unit: Unit) {
  const L = (v: number) => fmtLen(v, unit, false);
  const parts = [`세로 ${L(r.height)}`];
  if (cut.top) parts.push(`상단 ${L(cut.top)}`);
  if (cut.bottom) parts.push(`하단 ${L(cut.bottom)}`);
  if (cut.other) parts.push(`기타 ${L(cut.other)}`);
  let s = parts.join(' + ');
  if (parts.length > 1) s += ` = ${L(r.cut.base)}`;
  if (cut.shrinkPct) s += ` × (1+${fmt(cut.shrinkPct, 2)}%) = ${L(r.cut.afterShrink)}`;
  if (r.cut.patternApplied) s += ` → 무늬 ${L(cut.patternRepeat)} 단위 ${L(r.cut.final)}`;
  if (r.cut.roundApplied) s += ` → ${L(cut.roundUnit)} 단위 올림 ${L(r.cut.final)}`;
  return s;
}

export function CurtainResultCard({ rc }: { rc: CurtainCalc }) {
  const { state } = useStore();
  const s = state.settings;
  const unit = s.unit;
  const r = rc.result;
  const cut = curtainCut(rc.room, s);
  const L = (v: number) => fmtLen(v, unit, false);
  const status = !r.ok ? (
    <Pill>입력 대기</Pill>
  ) : !r.producible ? (
    <Pill tone="err">제작 불가</Pill>
  ) : r.issues.some((i) => i.level === 'warning') ? (
    <Pill tone="warn">확인 필요</Pill>
  ) : (
    <Pill tone="ok">
      <Icon name="check" size={13} />
      계산 완료
    </Pill>
  );
  const head = (
    <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
      <div className="eyebrow">커튼 계산 결과</div>
      <div className="flex flex-wrap items-center gap-1.5">
        <Pill>{rc.room.opening === 'double' ? '양개' : '편개'}</Pill>
        <Pill>{rc.room.method === 'joined' ? '폭 연결형' : '광폭 원단형'}</Pill>
        {status}
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
            <div className="num text-[52px] font-extrabold leading-none text-ink3/40">–폭</div>
            <p className="text-[14px] text-ink2">실측 가로·세로를 입력하면 바로 계산됩니다. 계산 버튼은 없습니다.</p>
          </div>
        ) : (
          <IssueList issues={r.issues} />
        )}
      </section>
    );
  }

  const unitM = 'm';
  return (
    <section className="card rise p-4 sm:p-5" aria-live="polite">
      {head}
      {r.method === 'joined' ? (
        <>
          <div className="grid grid-cols-2 gap-4 sm:gap-5">
            <Metric hero label="필요한 원단" value={String(r.totalWidths)} unit="폭" caption={captionWidths(rc, unit, cut)} tone={r.producible ? undefined : 'err'} />
            <Metric hero label="총 원단 소요량 (구매 길이)" value={fmtMeters(r.totalLength)} unit={unitM} caption={`${r.totalWidths}폭 × ${L(r.cut.final)} = ${fmt(toUnit(r.totalLength, unit), UNIT_DEC[unit])}${unit}`} />
          </div>
          <div className="mt-5 grid grid-cols-2 gap-4 border-t border-line pt-4">
            <Metric label="주름 적용 가로" value={L(r.requiredWidthTotal)} unit={unit} caption={`실측 가로 ${L(r.width)} × 주름 ${fmt(r.fullness, 2)}배`} />
            <Metric label="폭당 재단 길이" value={L(r.cut.final)} unit={unit} caption={cutCaption(r, cut, unit)} />
          </div>
        </>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 sm:gap-5">
            <Metric
              hero
              label="광폭 원단 사용 길이"
              value={fmtMeters(r.totalLength)}
              unit={unitM}
              caption={r.panels.map((p) => `${p.side === 'left' ? '좌 ' : p.side === 'right' ? '우 ' : ''}${L(p.pieceLength)}`).join(' + ') + (r.panels.length > 1 ? ` = ${L(r.totalLength)}` : '')}
            />
            <Metric
              hero
              label="필요 제작 높이"
              value={L(r.cut.final)}
              unit={unit}
              tone={r.wide?.heightOk ? undefined : 'err'}
              caption={r.wide?.heightOk ? `원단 폭 ${L(r.fabricWidth)} 이내 · 여유 ${L(clean(r.fabricWidth - r.cut.final))}` : `원단 폭 ${L(r.fabricWidth)} · ${L(r.wide?.shortfall ?? 0)} 부족`}
            />
          </div>
          <div className="mt-5 grid grid-cols-2 gap-4 border-t border-line pt-4">
            <Metric label="주름 적용 가로" value={L(r.requiredWidthTotal)} unit={unit} caption={`실측 가로 ${L(r.width)} × 주름 ${fmt(r.fullness, 2)}배`} />
            <Metric label="재단 방향" value="가로 사용" caption="롤 길이 방향 = 커튼 가로 · 이음 없음" />
          </div>
        </>
      )}

      {/* 장별 상세 */}
      <div className="mt-4 overflow-x-auto rounded-[12px] bg-sunk">
        <table className="w-full min-w-[420px] text-[13.5px]">
          <thead>
            <tr className="text-left text-[12px] text-ink3">
              <th className="px-3 pb-1.5 pt-2.5 font-semibold">커튼</th>
              <th className="px-2 pb-1.5 pt-2.5 font-semibold">덮는 가로</th>
              <th className="px-2 pb-1.5 pt-2.5 font-semibold">주름 적용</th>
              <th className="px-2 pb-1.5 pt-2.5 font-semibold">{r.method === 'joined' ? '폭 수' : '원단 길이'}</th>
              <th className="px-3 pb-1.5 pt-2.5 text-right font-semibold">실제 주름</th>
            </tr>
          </thead>
          <tbody className="num">
            {r.panels.map((p) => (
              <tr key={p.side} className="border-t border-line/70">
                <td className="px-3 py-2 font-sans font-bold">{p.side === 'left' ? '왼쪽' : p.side === 'right' ? '오른쪽' : '한 장'}</td>
                <td className="px-2 py-2">{fmtLen(p.finishedWidth, unit)}</td>
                <td className="px-2 py-2">{fmtLen(p.requiredWidth, unit)}</td>
                <td className="px-2 py-2 font-bold">
                  {r.method === 'joined' ? (
                    <>
                      {p.widths}폭 <span className="mono text-[11.5px] font-normal text-ink3">({fmt(p.rawRatio, 2)})</span>
                    </>
                  ) : (
                    fmtLen(p.pieceLength, unit)
                  )}
                </td>
                <td className="px-3 py-2 text-right">
                  {fmt(p.actualFullness, 2)}배 <span className="text-[11.5px] text-ink3">(잔여 {fmtLen(p.surplus, unit)})</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-2 text-[12px] leading-relaxed text-ink3">
        실제 주름 = 확보된 유효 원단 가로 ÷ 덮는 가로. 목표 {fmt(r.fullness, 2)}배보다 여유가 생긴 만큼 주름을 더 넣거나 잔여분으로 남길 수 있습니다.
        {r.method === 'joined' && (cut.seamLoss > 0 || cut.sideHem > 0) && ` 유효 가로에 이음 1곳당 ${fmtLen(cut.seamLoss, unit)}, 옆단 한쪽 ${fmtLen(cut.sideHem, unit)}를 뺐습니다.`}
      </p>
      {r.issues.length > 0 && (
        <div className="mt-4">
          <IssueList issues={r.issues} />
        </div>
      )}
    </section>
  );
}

const CUT_FIELDS: { key: keyof CutSettings; label: string; len: boolean; hint: string }[] = [
  { key: 'top', label: '상단 재단 여유', len: true, hint: '헤딩·심지 접힘분' },
  { key: 'bottom', label: '하단 재단 여유', len: true, hint: '밑단 접힘분' },
  { key: 'other', label: '기타 제조 여유', len: true, hint: '세로 방향 추가 여유' },
  { key: 'seamLoss', label: '봉제 손실 (이음 1곳)', len: true, hint: '폭 연결 시 이음 1곳당 줄어드는 가로' },
  { key: 'sideHem', label: '옆단 여유 (한쪽)', len: true, hint: '커튼 한 장의 좌·우 각각' },
  { key: 'shrinkPct', label: '수축 여유율', len: false, hint: '재단 길이에 % 가산' },
  { key: 'patternRepeat', label: '무늬 반복 길이', len: true, hint: '0 = 무지. 설정 시 재단 길이를 반복 단위로 올림' },
  { key: 'roundUnit', label: '재단 길이 올림 단위', len: true, hint: '0 = 올림 없음 (예: 5cm 단위)' },
];

export function CutEditor({ value, onChange, unit, disabled }: { value: CutSettings; onChange: (c: CutSettings) => void; unit: Unit; disabled?: boolean }) {
  return (
    <div className={`grid grid-cols-2 gap-x-3 gap-y-3.5 ${disabled ? 'pointer-events-none opacity-60' : ''}`} aria-disabled={disabled}>
      {CUT_FIELDS.map((f) =>
        f.len ? (
          <LengthField key={f.key} label={f.label} unit={unit} size="sm" value={value[f.key]} onChange={(v) => onChange({ ...value, [f.key]: v ?? 0 })} hint={f.hint} nav={!disabled} />
        ) : (
          <NumberField key={f.key} label={f.label} suffix="%" size="sm" value={value[f.key]} onChange={(v) => onChange({ ...value, [f.key]: v ?? 0 })} hint={f.hint} nav={!disabled} />
        ),
      )}
    </div>
  );
}

export function cutSummary(c: CutSettings, unit: Unit) {
  const L = (v: number) => fmtLen(v, unit);
  return [
    `상단 ${L(c.top)}`,
    `하단 ${L(c.bottom)}`,
    c.other ? `기타 ${L(c.other)}` : null,
    `봉제 ${L(c.seamLoss)}`,
    `옆단 ${L(c.sideHem)}`,
    `수축 ${fmt(c.shrinkPct, 2)}%`,
    c.patternRepeat ? `무늬 ${L(c.patternRepeat)}` : '무늬 없음',
    c.roundUnit ? `${L(c.roundUnit)} 올림` : '올림 없음',
  ]
    .filter(Boolean)
    .join(' · ');
}

function DetailCard({ rc, patch, s }: { rc: CurtainCalc; patch: (p: Patch) => void; s: Settings }) {
  const r = rc.room;
  const cut = curtainCut(r, s);
  return (
    <Card eyebrow="공간·제작 상세" title="공간 정보">
      <div className="grid grid-cols-2 gap-3">
        <SelectField label="공간명" value={r.space} options={SPACES} onChange={(v) => patch((x) => (x.space = v))} />
        <SelectField label="커튼 종류" value={r.curtainType} options={CURTAIN_TYPES} onChange={(v) => patch((x) => (x.curtainType = v))} />
        {r.space === '기타' && <TextField label="공간명 직접 입력" value={r.spaceCustom} onChange={(v) => patch((x) => (x.spaceCustom = v))} placeholder="예: 서재" />}
        {r.curtainType === '기타' && <TextField label="커튼 종류 직접 입력" value={r.curtainTypeCustom} onChange={(v) => patch((x) => (x.curtainTypeCustom = v))} placeholder="예: 쉬폰" />}
        <TextField className="col-span-2" label="설치 위치명" value={r.location} onChange={(v) => patch((x) => (x.location = v))} placeholder="예: 거실 전면창, 안방 우측창" />
        <TextField className="col-span-2" label="메모" value={r.memo} onChange={(v) => patch((x) => (x.memo = v))} placeholder="현장 특이사항 (견적서에는 표시되지 않음)" />
      </div>
      <div className="mt-4">
        <Disclosure
          title="재단·제작 여유"
          sub={cutSummary(cut, s.unit)}
          badge={r.cutOverride ? <Pill tone="gold">이 공간 전용</Pill> : <Pill>환경설정 값</Pill>}
        >
          <div className="flex flex-col gap-4">
            <Toggle
              checked={!!r.cutOverride}
              onChange={(on) => patch((x) => (x.cutOverride = on ? structuredCloneSafe(s.cut) : null))}
              label="이 공간만 따로 지정"
              hint="끄면 환경설정의 재단 여유가 적용됩니다. 각 항목은 서로 중복 계산되지 않습니다."
            />
            <CutEditor unit={s.unit} value={r.cutOverride ?? s.cut} disabled={!r.cutOverride} onChange={(c) => patch((x) => (x.cutOverride = c))} />
            {r.cutOverride && (
              <button type="button" className="btn btn-quiet self-start px-2 text-[13px]" onClick={() => patch((x) => (x.cutOverride = { ...DEFAULT_CUT }))}>
                <Icon name="reset" size={16} />
                기본 산식(상하 10cm, 나머지 0)으로
              </button>
            )}
          </div>
        </Disclosure>
      </div>
    </Card>
  );
}

function PricingCard({ rc, patch, s }: { rc: CurtainCalc; patch: (p: Patch) => void; s: Settings }) {
  const { update } = useStore();
  const { toast } = useUi();
  const p = rc.room.pricing;
  const admin = s.adminMode;
  const wide = rc.room.method === 'wide';
  return (
    <Card
      eyebrow="견적"
      title="이 공간 견적"
      action={
        <button
          type="button"
          className="btn btn-quiet min-h-[34px] px-2 text-[13px]"
          onClick={() => {
            patch((x) => (x.pricing = { ...structuredCloneSafe(s.curtain.pricing), options: x.pricing.options }));
            toast('기본 단가를 불러왔습니다.');
          }}
        >
          기본 단가 불러오기
        </button>
      }
    >
      <PriceRow
        label="원단 단가"
        admin={admin}
        modes={[
          { value: 'perMeter', label: 'm당' },
          { value: 'perWidth', label: '폭당', disabled: wide },
        ]}
        mode={p.fabric.mode}
        onMode={(m) => patch((x) => (x.pricing.fabric.mode = m))}
        price={p.fabric.price}
        onPrice={(v) => patch((x) => (x.pricing.fabric.price = v))}
        cost={p.fabric.cost}
        onCost={(v) => patch((x) => (x.pricing.fabric.cost = v))}
        hint={p.fabric.mode === 'perMeter' ? '총 원단 소요 길이(m) × m당 단가' : '필요 폭 수 × 폭당 단가'}
      />
      <PriceRow
        label="봉제비"
        admin={admin}
        modes={[
          { value: 'perWidth', label: '폭당', disabled: wide },
          { value: 'perMeter', label: '가로 m당' },
          { value: 'fixed', label: '정액' },
        ]}
        mode={p.sewing.mode}
        onMode={(m) => patch((x) => (x.pricing.sewing.mode = m))}
        price={p.sewing.price}
        onPrice={(v) => patch((x) => (x.pricing.sewing.price = v))}
        cost={p.sewing.cost}
        onCost={(v) => patch((x) => (x.pricing.sewing.cost = v))}
      />
      <PriceRow label="부자재비" admin={admin} price={p.hardware.price} onPrice={(v) => patch((x) => (x.pricing.hardware.price = v))} cost={p.hardware.cost} onCost={(v) => patch((x) => (x.pricing.hardware.cost = v))} hint="정액" />
      <PriceRow
        label="레일비"
        admin={admin}
        modes={[
          { value: 'perMeter', label: '가로 m당' },
          { value: 'fixed', label: '정액' },
        ]}
        mode={p.rail.mode}
        onMode={(m) => patch((x) => (x.pricing.rail.mode = m))}
        price={p.rail.price}
        onPrice={(v) => patch((x) => (x.pricing.rail.price = v))}
        cost={p.rail.cost}
        onCost={(v) => patch((x) => (x.pricing.rail.cost = v))}
      />
      <PriceRow label="설치비" admin={admin} price={p.install.price} onPrice={(v) => patch((x) => (x.pricing.install.price = v))} cost={p.install.cost} onCost={(v) => patch((x) => (x.pricing.install.cost = v))} hint="정액 (출장비는 현장 합계에서 1회 입력)" />
      <OptionsEditor admin={admin} options={p.options} onChange={(o) => patch((x) => (x.pricing.options = o))} />
      <DiscountEditor value={rc.room.discount} onChange={(d) => patch((x) => (x.discount = d))} label="공간 할인" />
      <div className="mt-2 flex flex-col gap-3">
        <IssueList issues={rc.quote.issues} />
        <QuoteBreakdown quote={rc.quote} admin={admin} note="부가세·출장비는 현장 전체 합계에서 한 번 계산합니다." />
        {admin && (
          <button
            type="button"
            className="btn btn-ghost self-start text-[13px]"
            onClick={() => {
              const k = 1 + s.marginRate / 100;
              const fill = (c: number | null | undefined, cur: number | null) => (c !== null && c !== undefined ? Math.round((c * k) / 100) * 100 : cur);
              patch((x) => {
                const pr = x.pricing;
                pr.fabric.price = fill(pr.fabric.cost, pr.fabric.price);
                pr.sewing.price = fill(pr.sewing.cost, pr.sewing.price);
                pr.hardware.price = fill(pr.hardware.cost, pr.hardware.price);
                pr.rail.price = fill(pr.rail.cost, pr.rail.price);
                pr.install.price = fill(pr.install.cost, pr.install.price);
                pr.options.forEach((o) => (o.amount = fill(o.cost, o.amount)));
              });
              toast(`원가에 마진 ${s.marginRate}%를 붙여 판매가를 채웠습니다.`);
            }}
          >
            마진율 {s.marginRate}%로 판매가 채우기
          </button>
        )}
        <button
          type="button"
          className="btn btn-quiet self-start px-2 text-[13px]"
          onClick={() => {
            update((d) => {
              d.settings.curtain.pricing = { ...structuredCloneSafe(p), options: [] };
            }, 'none');
            toast('이 단가를 커튼 기본 단가로 저장했습니다.');
          }}
        >
          <Icon name="save" size={16} />이 단가를 기본값으로 저장
        </button>
      </div>
    </Card>
  );
}

export function CurtainTab() {
  const { state, updateRoom } = useStore();
  const rc = useActiveRoom('curtain');
  const wideScreen = useMedia('(min-width: 1024px)');
  const s = state.settings;
  if (!rc)
    return (
      <div className="flex flex-col gap-4">
        <RoomStrip kind="curtain" />
        <EmptyRooms kind="curtain" />
      </div>
    );
  const patch = (p: Patch) => updateRoom(rc.room.id, (r) => p(r as CurtainRoom));
  const diagram = (
    <Card eyebrow="모식도" title="설치 모식도">
      <CurtainDiagram
        result={rc.result}
        unit={s.unit}
        width={rc.room.width}
        height={rc.room.height}
        gatherSide={rc.room.gatherSide}
        opening={rc.room.opening}
        split={rc.room.splitLeft ?? 50}
      />
      <p className="mt-2 text-[12px] leading-relaxed text-ink3">참고용 모식도이며 실제 원단의 주름 형상과는 다릅니다. 화살표는 커튼을 열 때 모이는 방향입니다.</p>
    </Card>
  );
  const measure = <MeasureCard rc={rc} patch={patch} s={s} />;
  const result = <CurtainResultCard rc={rc} />;
  const detail = <DetailCard rc={rc} patch={patch} s={s} />;
  const pricing = <PricingCard rc={rc} patch={patch} s={s} />;
  return (
    <div className="flex flex-col gap-4">
      <RoomStrip kind="curtain" />
      {wideScreen ? (
        <div className="grid grid-cols-[minmax(0,1fr)_minmax(0,1.05fr)] items-start gap-4">
          <div className="flex min-w-0 flex-col gap-4">
            {measure}
            {detail}
            {pricing}
          </div>
          <div className="flex min-w-0 flex-col gap-4">
            {result}
            {diagram}
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          {measure}
          {result}
          {diagram}
          {detail}
          {pricing}
        </div>
      )}
    </div>
  );
}
