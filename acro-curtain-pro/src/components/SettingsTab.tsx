import { useRef, useState } from 'react';
import { defaultSettings, initialState, structuredCloneSafe } from '../lib/defaults';
import { fmtLen, uid } from '../lib/num';
import { exportJson, importJson, safeRemove, HISTORY_KEY, STORAGE_KEY } from '../lib/storage';
import type { BlindType, Mount, SizeAdjust } from '../lib/types';
import { BLIND_TYPES, CURTAIN_TYPES, MOUNTS } from '../lib/types';
import { useStore, useUi } from '../store';
import { CutEditor, cutSummary, FabricPicker, FullnessPicker } from './CurtainTab';
import { PriceRow } from './RoomParts';
import { Card, copyText, Icon, LengthField, Modal, NumberField, Pill, Seg, SelectField, TextField, Toggle } from './ui';

const IS_ARTIFACT = __TARGET__ === 'artifact';

function Row({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <div className="grid grid-cols-1 gap-2 border-b border-line/70 py-3.5 last:border-0 sm:grid-cols-[11rem_minmax(0,1fr)] sm:gap-4">
      <div>
        <div className="text-[14px] font-semibold">{label}</div>
        {hint && <div className="mt-0.5 text-[12.5px] text-ink3">{hint}</div>}
      </div>
      <div className="min-w-0">{children}</div>
    </div>
  );
}

function downloadFile(name: string, text: string, type = 'application/json') {
  const blob = new Blob([text], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function SettingsTab({ onOpenRecent }: { onOpenRecent: () => void }) {
  const { state, update } = useStore();
  const { toast, confirm } = useUi();
  const s = state.settings;
  const unit = s.unit;
  const [blindType, setBlindType] = useState<BlindType>('콤비블라인드');
  const [profileName, setProfileName] = useState('');
  const [importOpen, setImportOpen] = useState(false);
  const [importText, setImportText] = useState('');
  const [importErr, setImportErr] = useState<string | null>(null);
  const [exportOpen, setExportOpen] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const set = (fn: (d: typeof state) => void) => update(fn, 'none');
  const preset = s.blindPresets[blindType];

  const applyToRooms = async () => {
    const n = state.site.rooms.filter((r) => r.kind === 'curtain').length;
    const ok = await confirm({
      title: `커튼 공간 ${n}곳에 기본값을 적용할까요?`,
      body: `원단 1폭 ${fmtLen(s.curtain.fabricWidth, unit)}, 주름 ${s.curtain.fullness}배를 현재 현장의 모든 커튼 공간에 덮어씁니다. 되돌리기로 복구할 수 있습니다.`,
      confirmLabel: '모두 적용',
    });
    if (!ok) return;
    update((d) => {
      d.site.rooms.forEach((r) => {
        if (r.kind === 'curtain') {
          r.fabricWidth = d.settings.curtain.fabricWidth;
          r.fullness = d.settings.curtain.fullness;
        }
      });
    }, 'force');
    toast('모든 커튼 공간에 적용했습니다.');
  };

  const restoreDefaults = async () => {
    const ok = await confirm({
      title: '환경설정을 기본값으로 복원할까요?',
      body: '원단 폭·주름·재단 여유·블라인드 제작 기준·단가·견적 양식이 모두 처음 값으로 돌아갑니다. 현장 데이터와 저장한 설정 프리셋은 그대로 남습니다.',
      confirmLabel: '기본값 복원',
      danger: true,
    });
    if (!ok) return;
    set((d) => {
      d.settings = defaultSettings();
    });
    toast('기본값으로 복원했습니다.');
  };

  const wipeAll = async () => {
    const ok = await confirm({
      title: '이 기기의 모든 데이터를 삭제할까요?',
      body: '현장·최근 현장 목록·설정·프리셋이 모두 지워지며 되돌릴 수 없습니다. 필요하면 먼저 JSON으로 내보내세요.',
      confirmLabel: '모두 삭제',
      danger: true,
    });
    if (!ok) return;
    safeRemove(STORAGE_KEY);
    safeRemove(HISTORY_KEY);
    const fresh = initialState();
    update((d) => {
      Object.assign(d, fresh);
    }, 'none');
    toast('모든 데이터를 삭제했습니다.');
  };

  const wipePersonal = async () => {
    const ok = await confirm({
      title: '고객 개인정보를 삭제할까요?',
      body: '현재 현장과 최근 현장 목록의 고객명·연락처·동/호수를 이 기기에서 모두 지웁니다. 실측값과 단가는 남습니다.',
      confirmLabel: '개인정보 삭제',
      danger: true,
    });
    if (!ok) return;
    update((d) => {
      const strip = (i: typeof d.site.info) => {
        i.customer = '';
        i.phone = '';
        i.dongho = '';
      };
      strip(d.site.info);
      d.recent.forEach((r) => strip(r.site.info));
    }, 'force');
    toast('개인정보를 삭제했습니다.');
  };

  const doImport = (text: string) => {
    const res = importJson(text);
    if (!res.ok) {
      setImportErr(res.message);
      return;
    }
    update((d) => {
      // 현재 현장은 최근 목록에 보관하고 불러온다
      d.recent = [{ id: uid('r'), savedAt: Date.now(), site: structuredCloneSafe(d.site) }, ...d.recent].slice(0, 30);
      d.settings = res.state.settings;
      d.site = res.state.site;
      d.profiles = res.state.profiles.length ? res.state.profiles : d.profiles;
      d.ui.activeCurtain = res.state.ui.activeCurtain;
      d.ui.activeBlind = res.state.ui.activeBlind;
    }, 'force');
    setImportOpen(false);
    setImportText('');
    setImportErr(null);
    toast('데이터를 불러왔습니다. 이전 현장은 최근 현장 목록에 보관했습니다.');
  };

  const exportText = exportJson(state);
  const fileName = `ACRO_CURTAIN_PRO_${(state.site.info.apartment || '현장').replace(/[\\/:*?"<>|\s]+/g, '_')}_${state.site.info.date || ''}.json`;

  return (
    <div className="grid grid-cols-1 items-start gap-4 lg:grid-cols-2">
      <div className="flex min-w-0 flex-col gap-4">
        <Card eyebrow="표시" title="단위·화면">
          <Row label="측정 단위" hint="입력과 결과 표시에 함께 적용">
            <Seg
              value={unit}
              label="측정 단위"
              options={[
                { value: 'cm', label: 'cm' },
                { value: 'mm', label: 'mm' },
                { value: 'm', label: 'm' },
              ]}
              onChange={(v) => set((d) => (d.settings.unit = v))}
            />
          </Row>
          <Row label="화면 모드">
            <Seg
              value={s.theme}
              label="화면 모드"
              options={[
                { value: 'system', label: '시스템' },
                { value: 'light', label: '라이트' },
                { value: 'dark', label: '다크' },
              ]}
              onChange={(v) => set((d) => (d.settings.theme = v))}
            />
          </Row>
        </Card>

        <Card eyebrow="커튼" title="커튼 기본값" action={<button type="button" className="btn btn-quiet min-h-[34px] px-2 text-[13px]" onClick={applyToRooms}>현재 공간 모두에 적용</button>}>
          <p className="mb-2 text-[12.5px] text-ink3">새로 추가하는 커튼 공간부터 적용됩니다. 이미 입력한 공간은 그대로 두려면 위 버튼을 누르지 마세요.</p>
          <Row label="기본 원단 1폭">
            <FabricPicker idPrefix="s" unit={unit} value={s.curtain.fabricWidth} onChange={(v) => v !== null && v > 0 && set((d) => (d.settings.curtain.fabricWidth = v))} />
          </Row>
          <Row label="기본 주름 배수">
            <FullnessPicker idPrefix="s" value={s.curtain.fullness} onChange={(v) => v !== null && v >= 1 && set((d) => (d.settings.curtain.fullness = v))} />
          </Row>
          <Row label="기본 설치 방식">
            <Seg
              value={s.curtain.opening}
              label="기본 설치 방식"
              options={[
                { value: 'double', label: '양개' },
                { value: 'single', label: '편개' },
              ]}
              onChange={(v) => set((d) => (d.settings.curtain.opening = v))}
            />
          </Row>
          <Row label="기본 제작 방식">
            <Seg
              value={s.curtain.method}
              label="기본 제작 방식"
              options={[
                { value: 'joined', label: '폭 연결형' },
                { value: 'wide', label: '광폭 원단형' },
              ]}
              onChange={(v) => set((d) => (d.settings.curtain.method = v))}
            />
          </Row>
          <Row label="폭 수 판정" hint="폭 연결형에서 필요 폭에 소수가 생겼을 때">
            <div className="flex flex-col gap-2">
              <Seg
                value={s.curtain.widthMode}
                label="폭 수 판정"
                options={[
                  { value: 'field', label: '현장 기준' },
                  { value: 'strict', label: '엄격 올림' },
                ]}
                onChange={(v) => set((d) => (d.settings.curtain.widthMode = v))}
              />
              {s.curtain.widthMode === 'field' ? (
                <>
                  <NumberField
                    size="sm"
                    suffix="폭 이하 버림"
                    value={s.curtain.dropFraction}
                    onChange={(v) => v !== null && v >= 0 && v < 1 && set((d) => (d.settings.curtain.dropFraction = Math.round(v * 100) / 100))}
                    ariaLabel="버림 기준 폭"
                  />
                  <p className="text-[12.5px] leading-relaxed text-ink3">
                    남는 소수가 {s.curtain.dropFraction}폭 이하면 버립니다. 예: 3.10폭 → 3폭, 3.30폭 → 4폭. 양개는 전체 폭을 반폭(0.5폭) 단위로 좌우에 나눕니다(3폭 → 1.5 + 1.5).
                  </p>
                </>
              ) : (
                <p className="text-[12.5px] leading-relaxed text-ink3">소수가 생기면 무조건 올립니다(3.10폭 → 4폭). 양개는 좌우를 각각 올림합니다.</p>
              )}
            </div>
          </Row>
          <Row label="기본 커튼 종류">
            <SelectField label="" value={s.curtain.curtainType} options={CURTAIN_TYPES} onChange={(v) => set((d) => (d.settings.curtain.curtainType = v))} />
          </Row>
          <Row label="광폭 안내 기준" hint="이 폭 이상 원단을 폭 연결형으로 계산하면 광폭형 전환을 안내">
            <LengthField unit={unit} size="sm" value={s.curtain.wideThreshold} onChange={(v) => set((d) => (d.settings.curtain.wideThreshold = v ?? 0))} />
          </Row>
        </Card>

        <Card eyebrow="커튼" title="재단·제작 여유">
          <p className="mb-3 text-[12.5px] leading-relaxed text-ink3">
            제조사·봉제 공장마다 다른 값입니다. 임시 기본값은 상단 10cm + 하단 10cm이며 나머지는 0(미적용)입니다. 각 항목은 따로 계산되고 중복 적용되지 않습니다.
          </p>
          <CutEditor unit={unit} value={s.cut} onChange={(c) => set((d) => (d.settings.cut = c))} />
          <p className="mt-3 rounded-[10px] bg-sunk px-3 py-2 text-[12.5px] text-ink2">{cutSummary(s.cut, unit)}</p>
        </Card>

        <Card eyebrow="블라인드" title="블라인드 제작 기준">
          <div className="flex flex-col gap-4">
            <SelectField label="제품 종류" value={blindType} options={BLIND_TYPES} onChange={setBlindType} />
            <Toggle
              checked={preset.verified}
              onChange={(v) => set((d) => (d.settings.blindPresets[blindType].verified = v))}
              label={preset.verified ? '제조사 기준 입력 완료' : '제조사 기준 미확인'}
              hint="켜기 전까지 결과에 「제작 기준 확인 필요」가 표시됩니다. 실제 제조사 공제 기준을 입력한 뒤 켜세요."
            />
            <TextField label="기준 출처 메모" value={preset.makerNote} onChange={(v) => set((d) => (d.settings.blindPresets[blindType].makerNote = v))} placeholder="예: OO블라인드 2026년 제작 기준표" />
            <div>
              <div className="mb-2 text-[13px] font-semibold text-ink2">설치 방식별 공제·추가값</div>
              <div className="overflow-x-auto rounded-[12px] border border-line">
                <table className="w-full min-w-[460px] text-[13px]">
                  <thead className="bg-sunk text-left text-[12px] text-ink3">
                    <tr>
                      <th className="px-3 py-2 font-semibold">설치</th>
                      <th className="px-1.5 py-2 font-semibold">가로 차감</th>
                      <th className="px-1.5 py-2 font-semibold">가로 추가</th>
                      <th className="px-1.5 py-2 font-semibold">세로 차감</th>
                      <th className="px-1.5 py-2 font-semibold">세로 추가</th>
                    </tr>
                  </thead>
                  <tbody>
                    {MOUNTS.map((m) => (
                      <tr key={m.value} className="border-t border-line">
                        <td className="whitespace-nowrap px-3 py-2 font-semibold">{m.label}</td>
                        {(['deductW', 'addW', 'deductH', 'addH'] as (keyof SizeAdjust)[]).map((k) => (
                          <td key={k} className="px-1.5 py-1.5">
                            <LengthField
                              unit={unit}
                              size="sm"
                              value={preset.byMount[m.value as Mount][k]}
                              ariaLabel={`${m.label} ${k}`}
                              onChange={(v) => set((d) => (d.settings.blindPresets[blindType].byMount[m.value as Mount][k] = v ?? 0))}
                            />
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {(
                [
                  ['minW', '최소 제작 폭'],
                  ['maxW', '최대 제작 폭'],
                  ['minH', '최소 제작 높이'],
                  ['maxH', '최대 제작 높이'],
                  ['roundUnit', '계산 반올림 단위'],
                ] as const
              ).map(([k, label]) => (
                <LengthField key={k} label={label} unit={unit} size="sm" value={preset[k]} hint="0 = 미설정" onChange={(v) => set((d) => (d.settings.blindPresets[blindType][k] = v ?? 0))} />
              ))}
              <div>
                <div className="mb-1.5 text-[13px] font-semibold text-ink2">반올림 방식</div>
                <Seg
                  value={preset.roundMode}
                  label="반올림 방식"
                  options={[
                    { value: 'ceil', label: '올림' },
                    { value: 'round', label: '반올림' },
                    { value: 'floor', label: '내림' },
                  ]}
                  onChange={(v) => set((d) => (d.settings.blindPresets[blindType].roundMode = v))}
                />
              </div>
            </div>
            <div className="border-t border-line pt-4">
              <div className="mb-2 text-[14px] font-bold">청구 기준</div>
              <div className="grid grid-cols-2 gap-3">
                <div className="col-span-2">
                  <div className="mb-1.5 text-[13px] font-semibold text-ink2">청구 면적 기준</div>
                  <Seg
                    value={preset.billing.basis}
                    label="청구 면적 기준"
                    options={[
                      { value: 'order', label: '주문 제작 사이즈' },
                      { value: 'measured', label: '실측 사이즈' },
                    ]}
                    onChange={(v) => set((d) => (d.settings.blindPresets[blindType].billing.basis = v))}
                  />
                </div>
                <LengthField label="최소 청구 가로" unit={unit} size="sm" value={preset.billing.minBillW} hint="0 = 미설정" onChange={(v) => set((d) => (d.settings.blindPresets[blindType].billing.minBillW = v ?? 0))} />
                <LengthField label="최소 청구 세로" unit={unit} size="sm" value={preset.billing.minBillH} hint="0 = 미설정" onChange={(v) => set((d) => (d.settings.blindPresets[blindType].billing.minBillH = v ?? 0))} />
                <NumberField label="최소 청구 면적" suffix="㎡" size="sm" value={preset.billing.minBillArea} hint="장당, 0 = 미설정" onChange={(v) => set((d) => (d.settings.blindPresets[blindType].billing.minBillArea = v ?? 0))} />
                <NumberField label="면적 올림 단위" suffix="㎡" size="sm" value={preset.billing.areaRoundUnit} hint="예: 0.1, 0 = 없음" onChange={(v) => set((d) => (d.settings.blindPresets[blindType].billing.areaRoundUnit = v ?? 0))} />
                <NumberField className="col-span-2" label="최소 제작 요금" suffix="원" size="sm" value={preset.billing.minCharge} hint="장당 금액이 이보다 적으면 이 금액으로 청구, 0 = 미설정" onChange={(v) => set((d) => (d.settings.blindPresets[blindType].billing.minCharge = v ?? 0))} />
              </div>
            </div>
            <div className="border-t border-line pt-1">
              <PriceRow
                label="기본 제품 단가"
                admin={s.adminMode}
                modes={[
                  { value: 'area', label: '㎡ 단가' },
                  { value: 'each', label: '개당 정액' },
                ]}
                mode={preset.priceMode}
                onMode={(m) => set((d) => (d.settings.blindPresets[blindType].priceMode = m))}
                price={preset.unitPrice}
                onPrice={(v) => set((d) => (d.settings.blindPresets[blindType].unitPrice = v))}
                cost={preset.unitCost}
                onCost={(v) => set((d) => (d.settings.blindPresets[blindType].unitCost = v))}
              />
              <PriceRow label="기본 설치비 (개당)" admin={false} price={preset.install} onPrice={(v) => set((d) => (d.settings.blindPresets[blindType].install = v))} />
            </div>
          </div>
        </Card>
      </div>

      <div className="flex min-w-0 flex-col gap-4">
        <Card eyebrow="견적" title="단가·부가세">
          <Row label="부가세">
            <div className="flex flex-col gap-2">
              <Seg
                value={s.vatMode}
                label="부가세 방식"
                options={[
                  { value: 'add', label: '별도 (가산)' },
                  { value: 'included', label: '단가에 포함' },
                  { value: 'none', label: '미적용' },
                ]}
                onChange={(v) => set((d) => (d.settings.vatMode = v))}
              />
              <NumberField size="sm" suffix="%" value={s.vatRate} onChange={(v) => set((d) => (d.settings.vatRate = v ?? 0))} ariaLabel="부가세율" hint="부가세율" />
            </div>
          </Row>
          <Row label="끝전 처리" hint="최종 합계 끝전 절사">
            <Seg
              value={String(s.quote.roundDown) as '1' | '10' | '100' | '1000' | '10000'}
              label="끝전 처리"
              options={[
                { value: '1', label: '없음' },
                { value: '100', label: '백원' },
                { value: '1000', label: '천원' },
                { value: '10000', label: '만원' },
              ]}
              onChange={(v) => set((d) => (d.settings.quote.roundDown = Number(v)))}
            />
          </Row>
          <Row label="관리자 모드" hint="원가·마진 입력과 표시">
            <Toggle checked={s.adminMode} onChange={(v) => set((d) => (d.settings.adminMode = v))} label={s.adminMode ? '켜짐' : '꺼짐'} hint="고객용 견적서·복사 문구에는 원가와 마진이 절대 나오지 않습니다." />
            {s.adminMode && (
              <div className="mt-3">
                <NumberField size="sm" suffix="%" label="기본 마진율" value={s.marginRate} onChange={(v) => set((d) => (d.settings.marginRate = v ?? 0))} hint="원가 입력 후 「마진율로 판매가 채우기」에 쓰입니다" />
              </div>
            )}
          </Row>
          <div className="pt-2">
            <div className="mb-1 text-[14px] font-bold">커튼 기본 단가</div>
            <p className="mb-1 text-[12.5px] text-ink3">새 커튼 공간에 들어가는 단가입니다. 공간 견적에서 「기본 단가 불러오기」로 적용할 수 있습니다.</p>
            <PriceRow
              label="원단"
              admin={s.adminMode}
              modes={[
                { value: 'perMeter', label: 'm당' },
                { value: 'perWidth', label: '폭당' },
              ]}
              mode={s.curtain.pricing.fabric.mode}
              onMode={(m) => set((d) => (d.settings.curtain.pricing.fabric.mode = m))}
              price={s.curtain.pricing.fabric.price}
              onPrice={(v) => set((d) => (d.settings.curtain.pricing.fabric.price = v))}
              cost={s.curtain.pricing.fabric.cost}
              onCost={(v) => set((d) => (d.settings.curtain.pricing.fabric.cost = v))}
            />
            <PriceRow
              label="봉제비"
              admin={s.adminMode}
              modes={[
                { value: 'perWidth', label: '폭당' },
                { value: 'perMeter', label: '가로 m당' },
                { value: 'fixed', label: '정액' },
              ]}
              mode={s.curtain.pricing.sewing.mode}
              onMode={(m) => set((d) => (d.settings.curtain.pricing.sewing.mode = m))}
              price={s.curtain.pricing.sewing.price}
              onPrice={(v) => set((d) => (d.settings.curtain.pricing.sewing.price = v))}
              cost={s.curtain.pricing.sewing.cost}
              onCost={(v) => set((d) => (d.settings.curtain.pricing.sewing.cost = v))}
            />
            <PriceRow label="부자재비" admin={s.adminMode} price={s.curtain.pricing.hardware.price} onPrice={(v) => set((d) => (d.settings.curtain.pricing.hardware.price = v))} cost={s.curtain.pricing.hardware.cost} onCost={(v) => set((d) => (d.settings.curtain.pricing.hardware.cost = v))} />
            <PriceRow
              label="레일비"
              admin={s.adminMode}
              modes={[
                { value: 'perMeter', label: '가로 m당' },
                { value: 'fixed', label: '정액' },
              ]}
              mode={s.curtain.pricing.rail.mode}
              onMode={(m) => set((d) => (d.settings.curtain.pricing.rail.mode = m))}
              price={s.curtain.pricing.rail.price}
              onPrice={(v) => set((d) => (d.settings.curtain.pricing.rail.price = v))}
              cost={s.curtain.pricing.rail.cost}
              onCost={(v) => set((d) => (d.settings.curtain.pricing.rail.cost = v))}
            />
            <PriceRow label="설치비" admin={s.adminMode} price={s.curtain.pricing.install.price} onPrice={(v) => set((d) => (d.settings.curtain.pricing.install.price = v))} cost={s.curtain.pricing.install.cost} onCost={(v) => set((d) => (d.settings.curtain.pricing.install.cost = v))} />
          </div>
        </Card>

        <Card eyebrow="견적서" title="기본 견적 양식">
          <div className="grid grid-cols-2 gap-3">
            <TextField className="col-span-2" label="상호" value={s.quote.companyName} onChange={(v) => set((d) => (d.settings.quote.companyName = v))} />
            <TextField label="연락처" value={s.quote.companyContact} onChange={(v) => set((d) => (d.settings.quote.companyContact = v))} inputMode="tel" />
            <TextField label="사업자등록번호" value={s.quote.bizNumber} onChange={(v) => set((d) => (d.settings.quote.bizNumber = v))} />
            <TextField className="col-span-2" label="주소" value={s.quote.companyAddress} onChange={(v) => set((d) => (d.settings.quote.companyAddress = v))} />
            <NumberField label="견적 유효기간" suffix="일" integer size="sm" value={s.quote.validDays} onChange={(v) => set((d) => (d.settings.quote.validDays = v ?? 0))} />
            <div>
              <div className="mb-1.5 text-[13px] font-semibold text-ink2">표시 방식</div>
              <Seg
                value={s.quote.detail}
                label="표시 방식"
                options={[
                  { value: 'itemized', label: '항목별' },
                  { value: 'room', label: '공간별' },
                ]}
                onChange={(v) => set((d) => (d.settings.quote.detail = v))}
              />
            </div>
            <TextField className="col-span-2" label="하단 안내 문구" multiline value={s.quote.footer} onChange={(v) => set((d) => (d.settings.quote.footer = v))} />
            <div className="col-span-2">
              <Toggle checked={s.quote.showNotes} onChange={(v) => set((d) => (d.settings.quote.showNotes = v))} label="현장 특이사항을 견적서에 표시" />
            </div>
          </div>
        </Card>

        <Card eyebrow="프리셋" title="설정 프리셋">
          <p className="mb-3 text-[12.5px] text-ink3">거래처·원단사별 기준을 이름 붙여 저장해 두고 바꿔 쓸 수 있습니다. (단위·화면 모드 포함 전체 환경설정)</p>
          <div className="flex gap-2">
            <div className="field min-w-0 flex-1">
              <input
                value={profileName}
                onChange={(e) => setProfileName(e.target.value)}
                placeholder="예: A원단사 · 광폭 암막"
                aria-label="프리셋 이름"
                className="h-11 w-full min-w-0 bg-transparent px-3 text-[15px] outline-none placeholder:text-ink3/60"
              />
            </div>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => {
                const name = profileName.trim() || `프리셋 ${state.profiles.length + 1}`;
                set((d) => {
                  d.profiles.unshift({ id: uid('p'), name, savedAt: Date.now(), settings: structuredCloneSafe(d.settings) });
                });
                setProfileName('');
                toast(`「${name}」 프리셋을 저장했습니다.`);
              }}
            >
              <Icon name="save" size={16} />
              현재 설정 저장
            </button>
          </div>
          {state.profiles.length > 0 && (
            <ul className="mt-3 flex flex-col divide-y divide-line rounded-[12px] border border-line">
              {state.profiles.map((p) => (
                <li key={p.id} className="flex items-center gap-2 px-3 py-2.5">
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-[14px] font-semibold">{p.name}</div>
                    <div className="text-[12px] text-ink3">
                      원단 {fmtLen(p.settings.curtain.fabricWidth, p.settings.unit)} · 주름 {p.settings.curtain.fullness}배 · {new Date(p.savedAt).toLocaleDateString('ko-KR')}
                    </div>
                  </div>
                  <button
                    type="button"
                    className="btn btn-ghost min-h-[36px] px-3 text-[13px]"
                    onClick={async () => {
                      const ok = await confirm({ title: `「${p.name}」 프리셋을 적용할까요?`, body: '현재 환경설정이 이 프리셋 값으로 바뀝니다. 현장 데이터는 그대로입니다.', confirmLabel: '적용' });
                      if (!ok) return;
                      set((d) => {
                        d.settings = structuredCloneSafe(p.settings);
                      });
                      toast('프리셋을 적용했습니다.');
                    }}
                  >
                    적용
                  </button>
                  <button
                    type="button"
                    className="btn btn-quiet min-h-[36px] px-2"
                    aria-label={`${p.name} 삭제`}
                    onClick={async () => {
                      const ok = await confirm({ title: `「${p.name}」 프리셋을 삭제할까요?`, confirmLabel: '삭제', danger: true });
                      if (ok) set((d) => (d.profiles = d.profiles.filter((x) => x.id !== p.id)));
                    }}
                  >
                    <Icon name="trash" size={16} />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card eyebrow="데이터" title="저장·내보내기">
          <div className="flex flex-col gap-3">
            <p className="flex items-start gap-2 rounded-[10px] bg-sunk px-3 py-2.5 text-[12.5px] leading-relaxed text-ink2">
              <Icon name="shield" size={16} className="mt-0.5 shrink-0 text-gold" />
              모든 데이터(고객 정보 포함)는 이 기기의 브라우저에만 자동 저장되며 외부 서버로 전송되지 않습니다.
            </p>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                className="btn btn-ghost"
                onClick={async () => {
                  if (IS_ARTIFACT) setExportOpen(true);
                  else {
                    downloadFile(fileName, exportText);
                    toast('JSON 파일로 저장했습니다.');
                  }
                }}
              >
                <Icon name="download" size={16} />
                JSON 내보내기
              </button>
              <button type="button" className="btn btn-ghost" onClick={() => setImportOpen(true)}>
                <Icon name="upload" size={16} />
                불러오기
              </button>
              <button type="button" className="btn btn-ghost" onClick={onOpenRecent}>
                <Icon name="folder" size={16} />
                최근 현장 ({state.recent.length})
              </button>
              <button type="button" className="btn btn-ghost" onClick={wipePersonal}>
                <Icon name="user" size={16} />
                개인정보 삭제
              </button>
            </div>
            <div className="mt-1 flex flex-wrap gap-2 border-t border-line pt-3">
              <button type="button" className="btn btn-danger" onClick={restoreDefaults}>
                <Icon name="reset" size={16} />
                기본값 복원
              </button>
              <button type="button" className="btn btn-danger" onClick={wipeAll}>
                <Icon name="trash" size={16} />
                모든 데이터 삭제
              </button>
            </div>
            <div className="text-[12px] text-ink3">
              <Pill>ACRO CURTAIN PRO 1.0</Pill> <span className="ml-1">{IS_ARTIFACT ? '미리보기판 — 인쇄·파일 저장은 PC용 파일에서' : 'PC·모바일 브라우저판'}</span>
            </div>
          </div>
        </Card>
      </div>

      <Modal
        open={importOpen}
        onClose={() => setImportOpen(false)}
        title="저장 데이터 불러오기"
        footer={
          <>
            <button type="button" className="btn btn-ghost" onClick={() => setImportOpen(false)}>
              취소
            </button>
            <button type="button" className="btn btn-primary" disabled={!importText.trim()} onClick={() => doImport(importText)}>
              붙여 넣은 내용 불러오기
            </button>
          </>
        }
      >
        <div className="flex flex-col gap-3">
          <input
            ref={fileRef}
            type="file"
            accept="application/json,.json"
            className="hidden"
            onChange={async (e) => {
              const f = e.target.files?.[0];
              if (!f) return;
              doImport(await f.text());
              e.target.value = '';
            }}
          />
          <button type="button" className="btn btn-ghost" onClick={() => fileRef.current?.click()}>
            <Icon name="folder" size={16} />
            JSON 파일 선택
          </button>
          <div className="text-center text-[12.5px] text-ink3">또는 내보낸 내용을 붙여 넣기</div>
          <textarea
            value={importText}
            onChange={(e) => {
              setImportText(e.target.value);
              setImportErr(null);
            }}
            rows={7}
            className="field mono w-full p-3 text-[12px] outline-none"
            placeholder='{"app":"ACRO CURTAIN PRO", ...}'
            aria-label="JSON 붙여 넣기"
          />
          {importErr && <p className="text-[13px] font-medium text-err">{importErr}</p>}
          <p className="text-[12.5px] text-ink3">불러오면 현재 현장은 최근 현장 목록에 자동 보관됩니다.</p>
        </div>
      </Modal>

      <Modal
        open={exportOpen}
        onClose={() => setExportOpen(false)}
        title="JSON 내보내기"
        footer={
          <button
            type="button"
            className="btn btn-primary"
            onClick={async () => {
              const ok = await copyText(exportText);
              toast(ok ? 'JSON을 복사했습니다. 메모장 등에 붙여 넣어 보관하세요.' : '복사하지 못했습니다. 아래 내용을 직접 선택해 복사하세요.', ok ? 'ok' : 'warn');
            }}
          >
            <Icon name="clipboard" size={16} />
            전체 복사
          </button>
        }
      >
        <p className="mb-2 text-[13px] text-ink2">이 미리보기 화면에서는 파일 다운로드가 막혀 있어 복사 방식으로 내보냅니다.</p>
        <textarea readOnly value={exportText} rows={10} className="field mono w-full p-3 text-[11.5px] outline-none" onFocus={(e) => e.currentTarget.select()} aria-label="내보낸 JSON" />
      </Modal>
    </div>
  );
}

export { downloadFile };
