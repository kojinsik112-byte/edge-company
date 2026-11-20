// 복사용 텍스트 — 고객에게 보내도 되는 내용만 (원가·마진 제외)
import { fmt, fmtLen, fmtMeters, won, type Unit } from './num';
import type { BlindCalc, CurtainCalc, RoomCalc, SiteCalc } from './quote';
import { CATEGORY_LABEL } from './quote';
import type { Settings, Site } from './types';
import { MOUNTS } from './types';

const OPENING = { single: '편개', double: '양개' };
const METHOD = { joined: '폭 연결형', wide: '광폭 원단형' };

export function curtainText(c: CurtainCalc, unit: Unit): string {
  const r = c.result;
  const room = c.room;
  const L = (v: number) => fmtLen(v, unit);
  const type = room.curtainType === '기타' ? room.curtainTypeCustom || '기타' : room.curtainType;
  const lines = [`[${c.label}] ${type} · ${OPENING[room.opening]} · ${METHOD[room.method]}`];
  if (!r.ok) {
    lines.push('계산 미완료: ' + (r.issues.find((i) => i.level === 'error')?.message ?? '입력값을 확인하세요.'));
    return lines.join('\n');
  }
  lines.push(`실측 ${L(r.width)} × ${L(r.height)} / 원단 ${L(r.fabricWidth)} / 주름 ${fmt(r.fullness, 2)}배`);
  lines.push(`주름 적용 가로: ${L(r.requiredWidthTotal)}`);
  if (r.method === 'joined') {
    if (r.opening === 'double') {
      const [lp, rp] = r.panels;
      lines.push(`왼쪽 커튼: ${lp.widths}폭 / 오른쪽 커튼: ${rp.widths}폭`);
    }
    lines.push(`필요 원단: 총 ${r.totalWidths}폭`);
    lines.push(`폭당 재단 길이: ${L(r.cut.final)}`);
  } else {
    lines.push(`제작 높이: ${L(r.cut.final)} (원단 폭 ${L(r.fabricWidth)})`);
    r.panels.forEach((p) => lines.push(`${p.side === 'left' ? '왼쪽' : p.side === 'right' ? '오른쪽' : '커튼'} 원단 길이: ${L(p.pieceLength)}`));
  }
  lines.push(`총 원단 소요량: ${fmtMeters(r.totalLength)}m`);
  r.issues.filter((i) => i.level === 'critical' || i.level === 'warning').forEach((i) => lines.push(`※ ${i.message}`));
  if (c.quote.total > 0) lines.push(`공간 견적: ${won(c.quote.total)} (부가세 별도)`);
  return lines.join('\n');
}

export function blindText(b: BlindCalc, unit: Unit): string {
  const r = b.result;
  const room = b.room;
  const L = (v: number) => fmtLen(v, unit);
  const type = room.blindType === '기타' ? room.blindTypeCustom || '기타' : room.blindType;
  const mount = MOUNTS.find((m) => m.value === room.mount)?.label ?? '';
  const lines = [`[${b.label}] ${type} · ${mount}`];
  if (!r.ok) {
    lines.push('계산 미완료: ' + (r.issues.find((i) => i.level === 'error')?.message ?? '입력값을 확인하세요.'));
    return lines.join('\n');
  }
  lines.push(`실측 사이즈: ${L(r.width)} × ${L(r.height)}`);
  lines.push(`주문 제작 사이즈: ${L(r.orderW)} × ${L(r.orderH)} · ${r.qty}개`);
  lines.push(`실측 면적: ${fmt(r.measuredArea, 2)}㎡ / 청구 면적: ${fmt(r.billArea, 2)}㎡${r.qty > 1 ? ` × ${r.qty}개 = ${fmt(r.billAreaTotal, 2)}㎡` : ''}`);
  r.issues.filter((i) => i.level === 'critical' || i.level === 'warning').forEach((i) => lines.push(`※ ${i.message}`));
  if (b.quote.total > 0) lines.push(`공간 견적: ${won(b.quote.total)} (부가세 별도)`);
  return lines.join('\n');
}

export function roomText(rc: RoomCalc, unit: Unit) {
  return rc.kind === 'curtain' ? curtainText(rc, unit) : blindText(rc, unit);
}

export function siteText(site: Site, calc: SiteCalc, s: Settings): string {
  const t = calc.totals;
  const i = site.info;
  const head = [s.quote.companyName || 'ACRO', '커튼·블라인드 실측 결과'];
  const where = [i.apartment, i.dongho].filter(Boolean).join(' ');
  if (where) head.push(where);
  if (i.date) head.push(`실측일 ${i.date}`);
  const out = [head.join(' · '), ''];
  calc.rooms.forEach((rc) => {
    out.push(roomText(rc, s.unit));
    out.push('');
  });
  out.push('── 현장 합계 ──');
  if (t.curtainRooms) out.push(`커튼 ${t.curtainRooms}곳: 총 ${t.curtainWidths}폭 · 원단 ${fmtMeters(t.curtainLength)}m`);
  if (t.blindRooms) out.push(`블라인드 ${t.blindCount}개: 청구 면적 ${fmt(t.blindBillArea, 2)}㎡`);
  (Object.keys(t.cat) as (keyof typeof t.cat)[]).forEach((k) => t.cat[k] && out.push(`${CATEGORY_LABEL[k]}: ${won(t.cat[k])}`));
  if (t.roomDiscount) out.push(`공간 할인: −${won(t.roomDiscount)}`);
  if (t.travel) out.push(`출장비: ${won(t.travel)}`);
  if (t.shipping) out.push(`배송비: ${won(t.shipping)}`);
  if (t.siteDiscount) out.push(`추가 할인: −${won(t.siteDiscount)}`);
  if (s.vatMode !== 'none') out.push(`공급가액 ${won(t.supply)} / 부가세 ${won(t.vat)}`);
  if (t.roundAdj) out.push(`끝전 절사: −${won(t.roundAdj)}`);
  out.push(`최종 견적 합계: ${won(t.total)}${s.vatMode === 'none' ? ' (부가세 미적용)' : ' (부가세 포함)'}`);
  if (t.pendingRooms) out.push(`※ 계산이 끝나지 않은 공간 ${t.pendingRooms}곳은 합계에서 빠졌습니다.`);
  return out.join('\n');
}
