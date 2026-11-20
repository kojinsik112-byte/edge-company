import type { BlindResult } from '../lib/blind';
import type { CurtainResult } from '../lib/curtain';
import { fmt, fmtLen, type Unit } from '../lib/num';
import type { BlindType, Mount } from '../lib/types';

const C = {
  ink: 'rgb(var(--ink))',
  ink2: 'rgb(var(--ink-2))',
  ink3: 'rgb(var(--ink-3))',
  line: 'rgb(var(--line))',
  sunk: 'rgb(var(--sunk))',
  surface: 'rgb(var(--surface))',
  gold: 'rgb(var(--gold))',
  goldSoft: 'rgb(var(--gold-soft))',
  err: 'rgb(var(--err))',
};

const VW = 520;
const VH = 372;

function fitBox(w: number, h: number, maxW: number, maxH: number) {
  const aspect = Math.min(3.4, Math.max(0.55, w / h));
  let bw = maxW;
  let bh = bw / aspect;
  if (bh > maxH) {
    bh = maxH;
    bw = bh * aspect;
  }
  return { bw, bh };
}

function Arrow({ x1, x2, y }: { x1: number; x2: number; y: number }) {
  const dir = x2 > x1 ? 1 : -1;
  return (
    <g style={{ stroke: C.ink2, fill: 'none' }} strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round">
      <line x1={x1} y1={y} x2={x2} y2={y} />
      <polyline points={`${x2 - dir * 8},${y - 5} ${x2},${y} ${x2 - dir * 8},${y + 5}`} />
    </g>
  );
}

function DimH({ x1, x2, y, label }: { x1: number; x2: number; y: number; label: string }) {
  const ticks = Array.from({ length: 11 }, (_, i) => x1 + ((x2 - x1) * i) / 10);
  return (
    <g>
      <line x1={x1} y1={y} x2={x2} y2={y} style={{ stroke: C.ink3 }} strokeWidth={1} />
      {ticks.map((tx, i) => (
        <line key={i} x1={tx} y1={y - (i % 5 === 0 ? 7 : 3.5)} x2={tx} y2={y} style={{ stroke: C.ink3 }} strokeWidth={1} />
      ))}
      <rect x={(x1 + x2) / 2 - 74} y={y - 28} width={148} height={22} rx={4} style={{ fill: C.surface }} />
      <text x={(x1 + x2) / 2} y={y - 12} textAnchor="middle" className="num" style={{ fill: C.ink, fontSize: 16, fontWeight: 700 }}>
        {label}
      </text>
    </g>
  );
}

function DimV({ x, y1, y2, label }: { x: number; y1: number; y2: number; label: string }) {
  const ticks = Array.from({ length: 11 }, (_, i) => y1 + ((y2 - y1) * i) / 10);
  const cy = (y1 + y2) / 2;
  return (
    <g>
      <line x1={x} y1={y1} x2={x} y2={y2} style={{ stroke: C.ink3 }} strokeWidth={1} />
      {ticks.map((ty, i) => (
        <line key={i} x1={x} y1={ty} x2={x + (i % 5 === 0 ? 7 : 3.5)} y2={ty} style={{ stroke: C.ink3 }} strokeWidth={1} />
      ))}
      <text x={x - 10} y={cy} textAnchor="middle" transform={`rotate(-90 ${x - 10} ${cy})`} className="num" style={{ fill: C.ink, fontSize: 16, fontWeight: 700 }}>
        {label}
      </text>
    </g>
  );
}

export function CurtainDiagram({
  result,
  unit,
  width,
  height,
  gatherSide,
  opening,
  split,
}: {
  result: CurtainResult | null;
  unit: Unit;
  width: number | null;
  height: number | null;
  gatherSide: 'left' | 'right';
  opening: 'single' | 'double';
  split: number;
}) {
  const W = result?.ok ? result.width : width && width > 0 ? width : 360;
  const H = result?.ok ? result.height : height && height > 0 ? height : 240;
  const L = { left: 56, right: 24, top: 86, bottom: 46 };
  const { bw, bh } = fitBox(W, H, VW - L.left - L.right - 20, VH - L.top - L.bottom);
  const x0 = L.left + (VW - L.left - L.right - bw) / 2;
  const y0 = L.top;
  const railY = y0 - 16;
  const ov = 10; // 커튼 양옆 여유 표현
  const cTop = railY + 4;
  const cBot = y0 + bh + 14;
  const panes = W > 300 ? 3 : 2;
  const ratio = opening === 'double' ? Math.min(0.9, Math.max(0.1, split / 100)) : 1;
  const splitX = x0 + bw * ratio;

  const panels =
    opening === 'double'
      ? [
          { key: 'left', x1: x0 - ov, x2: splitX, label: '왼쪽', p: result?.panels[0] },
          { key: 'right', x1: splitX, x2: x0 + bw + ov, label: '오른쪽', p: result?.panels[1] },
        ]
      : [{ key: 'single', x1: x0 - ov, x2: x0 + bw + ov, label: '편개', p: result?.panels[0] }];

  const wide = result?.method === 'wide';
  const fullness = result?.ok ? result.fullness : 1.5;
  const bad = result?.ok && !result.producible;

  return (
    <svg viewBox={`0 0 ${VW} ${VH}`} className="block h-auto w-full" role="img" aria-label="커튼 설치 모식도">
      {/* 천장선 */}
      <line x1={18} y1={railY - 10} x2={VW - 18} y2={railY - 10} style={{ stroke: C.line }} strokeWidth={1} strokeDasharray="3 4" />
      <DimH x1={x0} x2={x0 + bw} y={34} label={`가로 ${width && width > 0 ? fmtLen(width, unit) : '–'}`} />
      <DimV x={30} y1={y0} y2={y0 + bh} label={`세로 ${height && height > 0 ? fmtLen(height, unit) : '–'}`} />

      {/* 창문 */}
      <rect x={x0} y={y0} width={bw} height={bh} style={{ fill: C.sunk, stroke: C.ink3 }} strokeWidth={2} />
      {Array.from({ length: panes - 1 }, (_, i) => (
        <line key={i} x1={x0 + (bw * (i + 1)) / panes} y1={y0} x2={x0 + (bw * (i + 1)) / panes} y2={y0 + bh} style={{ stroke: C.ink3 }} strokeWidth={1.2} />
      ))}
      <line x1={x0} y1={y0 + bh * 0.72} x2={x0 + bw} y2={y0 + bh * 0.72} style={{ stroke: C.line }} strokeWidth={1} />

      {/* 커튼 */}
      {panels.map((pn) => {
        const w = pn.x2 - pn.x1;
        const folds = Math.max(4, Math.min(26, Math.round((w / 22) * (fullness / 1.5))));
        const fw = w / folds;
        return (
          <g key={pn.key}>
            <rect x={pn.x1} y={cTop} width={w} height={cBot - cTop} style={{ fill: C.goldSoft, stroke: bad ? C.err : C.gold }} strokeWidth={1.4} opacity={0.92} />
            {Array.from({ length: folds }, (_, i) => (
              <rect key={i} x={pn.x1 + i * fw + fw * 0.55} y={cTop + 1} width={fw * 0.3} height={cBot - cTop - 2} style={{ fill: C.gold }} opacity={0.13} />
            ))}
            {/* 헤딩 주름 */}
            <path
              d={Array.from({ length: folds }, (_, i) => `${i === 0 ? 'M' : 'L'}${pn.x1 + i * fw},${cTop + 2} Q${pn.x1 + i * fw + fw / 2},${cTop + 9} ${pn.x1 + (i + 1) * fw},${cTop + 2}`).join(' ')}
              style={{ fill: 'none', stroke: C.gold }}
              strokeWidth={1.2}
            />
          </g>
        );
      })}
      {/* 레일 */}
      <rect x={x0 - ov - 6} y={railY - 3} width={bw + 2 * ov + 12} height={6} rx={3} style={{ fill: C.ink }} />

      {/* 패널 라벨 + 개폐 방향 */}
      {panels.map((pn) => {
        const cx = (pn.x1 + pn.x2) / 2;
        const midY = y0 + bh * 0.42;
        const w = pn.x2 - pn.x1;
        const p = pn.p;
        const main = !result?.ok ? pn.label : wide ? fmtLen(p?.pieceLength ?? 0, unit) : `${p?.widths ?? 0}폭`;
        const sub = result?.ok && p ? `${opening === 'double' ? pn.label + ' ' : ''}${fmtLen(p.finishedWidth, unit)}` : '';
        // 열리는 방향(모이는 쪽)
        const toLeft = pn.key === 'left' || (pn.key === 'single' && gatherSide === 'left');
        const ax = Math.min(46, w * 0.3);
        return (
          <g key={`lbl-${pn.key}`}>
            <rect x={cx - 52} y={midY - 30} width={104} height={sub ? 54 : 36} rx={8} style={{ fill: C.surface }} opacity={0.94} />
            <text x={cx} y={midY - 4} textAnchor="middle" className="num" style={{ fill: C.ink, fontSize: 23, fontWeight: 800 }}>
              {main}
            </text>
            {sub && (
              <text x={cx} y={midY + 15} textAnchor="middle" style={{ fill: C.ink2, fontSize: 13, fontWeight: 600 }}>
                {sub}
              </text>
            )}
            <Arrow x1={toLeft ? cx + ax / 2 : cx - ax / 2} x2={toLeft ? cx - ax / 2 - 6 : cx + ax / 2 + 6} y={midY + (sub ? 42 : 26)} />
          </g>
        );
      })}

      {/* 하단 캡션 */}
      <text x={VW / 2} y={VH - 12} textAnchor="middle" className="mono" style={{ fill: C.ink2, fontSize: 14 }}>
        {result?.ok
          ? `${opening === 'double' ? '양개' : `편개(${gatherSide === 'left' ? '왼쪽' : '오른쪽'}으로 모음)`} · 주름 ${fmt(result.fullness, 2)}배 · ${
              wide ? `광폭 ${fmtLen(result.fabricWidth, unit)} 가로 사용·이음 없음` : `원단 ${fmtLen(result.fabricWidth, unit)} · 총 ${result.totalWidths}폭`
            }`
          : '가로·세로를 입력하면 모식도가 맞춰 그려집니다'}
      </text>
    </svg>
  );
}

const SLATS: BlindType[] = ['콤비블라인드', '우드블라인드', '알루미늄블라인드', '허니콤블라인드'];

export function BlindDiagram({ result, unit, mount, type }: { result: BlindResult | null; unit: Unit; mount: Mount; type: BlindType }) {
  const ok = !!result?.ok;
  const W = ok ? result!.width : 180;
  const H = ok ? result!.height : 200;
  const L = { left: 56, right: 24, top: 70, bottom: 40 };
  const { bw, bh } = fitBox(W, H, VW - L.left - L.right - 60, VH - L.top - L.bottom - 20);
  const x0 = L.left + (VW - L.left - L.right - bw) / 2;
  const y0 = L.top + 14;
  // 주문 사이즈는 개념적으로만 표시 (안쪽: 틀 안, 바깥쪽: 틀 밖, 천장: 천장선부터)
  const pad = 12;
  const box =
    mount === 'inside'
      ? { x: x0 + pad / 2, y: y0 + pad / 2, w: bw - pad, h: bh - pad }
      : mount === 'outside'
        ? { x: x0 - pad, y: y0 - pad, w: bw + pad * 2, h: bh + pad * 2 }
        : { x: x0 - pad, y: y0 - 30, w: bw + pad * 2, h: bh + 30 + pad };
  const slats = SLATS.includes(type);
  const rows = Math.max(6, Math.min(22, Math.round(box.h / 16)));
  return (
    <svg viewBox={`0 0 ${VW} ${VH}`} className="block h-auto w-full" role="img" aria-label="블라인드 설치 모식도">
      {mount === 'ceiling' && <line x1={18} y1={y0 - 30} x2={VW - 18} y2={y0 - 30} style={{ stroke: C.ink3 }} strokeWidth={1.4} />}
      <DimH x1={x0} x2={x0 + bw} y={30} label={`실측 ${fmtLen(W, unit)}`} />
      <DimV x={30} y1={y0} y2={y0 + bh} label={`실측 ${fmtLen(H, unit)}`} />
      <rect x={x0} y={y0} width={bw} height={bh} style={{ fill: C.sunk, stroke: C.ink3 }} strokeWidth={2} />
      <g opacity={0.95}>
        <rect x={box.x} y={box.y} width={box.w} height={box.h} style={{ fill: C.goldSoft, stroke: C.gold }} strokeWidth={1.5} opacity={0.9} />
        {Array.from({ length: rows }, (_, i) => {
          const yy = box.y + ((i + 1) * box.h) / (rows + 1);
          return slats ? (
            <line key={i} x1={box.x + 2} y1={yy} x2={box.x + box.w - 2} y2={yy} style={{ stroke: C.gold }} strokeWidth={i % 2 && type === '콤비블라인드' ? 5 : 1.2} opacity={type === '콤비블라인드' ? 0.22 : 0.4} />
          ) : null;
        })}
        <rect x={box.x - 4} y={box.y - 8} width={box.w + 8} height={10} rx={3} style={{ fill: C.ink }} />
      </g>
      <rect x={x0 + bw / 2 - 92} y={y0 + bh / 2 - 26} width={184} height={50} rx={8} style={{ fill: C.surface }} opacity={0.95} />
      <text x={x0 + bw / 2} y={y0 + bh / 2 - 4} textAnchor="middle" style={{ fill: C.ink2, fontSize: 12, fontWeight: 600 }}>
        주문 제작 사이즈
      </text>
      <text x={x0 + bw / 2} y={y0 + bh / 2 + 16} textAnchor="middle" className="num" style={{ fill: C.ink, fontSize: 17, fontWeight: 800 }}>
        {ok ? `${fmtLen(result!.orderW, unit, false)} × ${fmtLen(result!.orderH, unit)}` : '–'}
      </text>
      <text x={VW / 2} y={VH - 10} textAnchor="middle" className="mono" style={{ fill: C.ink2, fontSize: 14 }}>
        {mount === 'inside' ? '창틀 안쪽' : mount === 'outside' ? '창틀 바깥쪽' : '천장 설치'} · 회색 창틀 · 금색 제품
      </text>
    </svg>
  );
}
