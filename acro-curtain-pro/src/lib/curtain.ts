// 커튼 원단 산출 엔진 — 순수 함수, UI와 무관. 내부 단위 cm.
import { ceilSafe, ceilTo, clean, isNum } from './num';
import { josa } from './josa';
import type { CurtainMethod, CutSettings, Issue, Opening } from './types';

export interface CurtainInput {
  width: number | null;
  height: number | null;
  fabricWidth: number | null;
  fullness: number | null;
  opening: Opening;
  splitLeft: number | null;
  splitRight: number | null;
  method: CurtainMethod;
  cut: CutSettings;
  wideThreshold?: number;
}

export interface CurtainPanel {
  side: 'single' | 'left' | 'right';
  ratio: number; // 0~1
  finishedWidth: number; // 이 장이 덮는 실측 가로
  requiredWidth: number; // 주름 적용 원단 가로 (finished × 주름)
  // 폭 연결형
  widths: number; // 필요 폭 수
  rawRatio: number; // requiredWidth ÷ 원단폭 (올림 전)
  seams: number; // 이음 수
  usableWidth: number; // 유효 원단 가로 = 폭수×원단폭 − 이음손실 − 옆단
  surplus: number; // 유효 가로 − 필요 가로 (잔여 원단 폭)
  actualFullness: number; // 유효 가로 ÷ 실측 가로
  // 광폭형
  pieceLength: number; // 이 장에 쓰는 광폭 원단 길이(롤 길이 방향)
}

export interface CutSteps {
  base: number; // 세로 + 상단 + 하단 + 기타
  afterShrink: number;
  final: number;
  patternApplied: boolean;
  roundApplied: boolean;
  roundSkippedByPattern: boolean;
}

export interface CurtainResult {
  ok: boolean; // 숫자 결과를 보여줄 수 있는가
  producible: boolean; // critical 경고 없이 제작 가능한가
  issues: Issue[];
  method: CurtainMethod;
  opening: Opening;
  width: number;
  height: number;
  fabricWidth: number;
  fullness: number;
  requiredWidthTotal: number; // 실측 가로 × 주름
  panels: CurtainPanel[];
  totalWidths: number; // 폭 연결형: 전체 폭 수 (광폭형: 0)
  naiveWidths: number; // 전체 가로로 한 번만 올림했을 때 (비교용)
  cut: CutSteps; // 폭연결형: 폭당 재단 길이 / 광폭형: 필요 제작 높이
  totalLength: number; // 구매 원단 총 길이 cm
  wide: null | {
    rollWidth: number;
    requiredHeight: number;
    heightOk: boolean;
    shortfall: number;
  };
}

const LIMIT = {
  maxWidth: 10000, // 100m — 이를 넘으면 입력 오류
  warnWidth: 1500, // 15m — 단위 실수 의심
  maxHeight: 3000,
  warnHeight: 600,
  minHeightWarn: 20,
  maxFabric: 600,
  warnFabric: 340,
  maxFullness: 10,
  warnFullness: 4,
};

function emptyResult(inp: CurtainInput, issues: Issue[]): CurtainResult {
  return {
    ok: false,
    producible: false,
    issues,
    method: inp.method,
    opening: inp.opening,
    width: 0,
    height: 0,
    fabricWidth: 0,
    fullness: 0,
    requiredWidthTotal: 0,
    panels: [],
    totalWidths: 0,
    naiveWidths: 0,
    cut: { base: 0, afterShrink: 0, final: 0, patternApplied: false, roundApplied: false, roundSkippedByPattern: false },
    totalLength: 0,
    wide: null,
  };
}

const CUT_LABEL: Record<keyof CutSettings, string> = {
  top: '상단 재단 여유',
  bottom: '하단 재단 여유',
  other: '기타 제조 여유',
  seamLoss: '봉제 손실',
  sideHem: '옆단 여유',
  shrinkPct: '수축 여유율',
  patternRepeat: '무늬 반복 길이',
  roundUnit: '재단 올림 단위',
};

export function validateCurtain(inp: CurtainInput): Issue[] {
  const out: Issue[] = [];
  const req = (v: number | null, field: string, name: string): v is number => {
    if (v === null) {
      out.push({ level: 'error', field, code: 'empty', message: `${josa(name, '을/를')} 입력하세요.` });
      return false;
    }
    if (!isNum(v)) {
      out.push({ level: 'error', field, message: `${name}에는 숫자만 입력할 수 있습니다.` });
      return false;
    }
    if (v < 0) {
      out.push({ level: 'error', field, message: `${josa(name, '은/는')} 음수일 수 없습니다.` });
      return false;
    }
    if (v === 0) {
      out.push({ level: 'error', field, message: `${josa(name, '은/는')} 0보다 커야 합니다.` });
      return false;
    }
    return true;
  };

  if (req(inp.width, 'width', '실측 가로')) {
    if (inp.width > LIMIT.maxWidth)
      out.push({ level: 'error', field: 'width', message: '실측 가로가 100m를 넘습니다. 입력값을 확인하세요.' });
    else if (inp.width > LIMIT.warnWidth)
      out.push({ level: 'warning', field: 'width', message: '실측 가로가 15m를 넘습니다. 단위(cm·mm)를 확인하세요.' });
  }
  if (req(inp.height, 'height', '실측 세로')) {
    if (inp.height > LIMIT.maxHeight)
      out.push({ level: 'error', field: 'height', message: '실측 세로가 30m를 넘습니다. 입력값을 확인하세요.' });
    else if (inp.height > LIMIT.warnHeight)
      out.push({ level: 'warning', field: 'height', message: '실측 세로가 6m를 넘습니다. 단위(cm·mm)를 확인하세요.' });
    else if (inp.height < LIMIT.minHeightWarn)
      out.push({ level: 'warning', field: 'height', message: '실측 세로가 20cm 미만입니다. 입력값을 확인하세요.' });
  }
  if (req(inp.fabricWidth, 'fabricWidth', '원단 1폭')) {
    if (inp.fabricWidth > LIMIT.maxFabric)
      out.push({ level: 'error', field: 'fabricWidth', message: '원단 폭이 6m를 넘습니다. 입력값을 확인하세요.' });
    else if (inp.fabricWidth > LIMIT.warnFabric)
      out.push({ level: 'warning', field: 'fabricWidth', message: '원단 폭이 일반 광폭 규격(약 330cm)보다 큽니다.' });
  }

  if (inp.fullness === null) {
    out.push({ level: 'error', field: 'fullness', code: 'empty', message: '주름 배수를 입력하세요.' });
  } else if (!isNum(inp.fullness)) {
    out.push({ level: 'error', field: 'fullness', message: '주름 배수에는 숫자만 입력할 수 있습니다.' });
  } else if (inp.fullness < 1) {
    out.push({ level: 'error', field: 'fullness', message: '주름 배수는 1.0배(민자) 이상이어야 합니다.' });
  } else if (inp.fullness > LIMIT.maxFullness) {
    out.push({ level: 'error', field: 'fullness', message: '주름 배수가 10배를 넘습니다. 입력값을 확인하세요.' });
  } else if (inp.fullness > LIMIT.warnFullness) {
    out.push({ level: 'warning', field: 'fullness', message: '주름 배수가 4배를 넘습니다. 일반적이지 않은 값입니다.' });
  }

  if (inp.opening === 'double') {
    const l = inp.splitLeft;
    const r = inp.splitRight;
    if (!isNum(l) || !isNum(r)) {
      out.push({ level: 'error', field: 'split', message: '양개 좌우 비율을 입력하세요.' });
    } else if (l <= 0 || r <= 0) {
      out.push({ level: 'error', field: 'split', message: '양개 좌우 비율은 각각 0%보다 커야 합니다.' });
    } else if (Math.abs(l + r - 100) > 0.001) {
      out.push({
        level: 'error',
        field: 'split',
        message: `좌우 비율의 합이 100%가 되어야 합니다. (현재 ${clean(l + r)}%)`,
      });
    }
  }

  (Object.keys(CUT_LABEL) as (keyof CutSettings)[]).forEach((k) => {
    const v = inp.cut[k];
    if (!isNum(v)) out.push({ level: 'error', field: `cut.${k}`, message: `${CUT_LABEL[k]} 값이 올바르지 않습니다.` });
    else if (v < 0) out.push({ level: 'error', field: `cut.${k}`, message: `${josa(CUT_LABEL[k], '은/는')} 음수일 수 없습니다.` });
  });
  if (isNum(inp.cut.shrinkPct)) {
    if (inp.cut.shrinkPct >= 50)
      out.push({ level: 'error', field: 'cut.shrinkPct', message: '수축 여유율이 50% 이상입니다. 입력값을 확인하세요.' });
    else if (inp.cut.shrinkPct > 10)
      out.push({ level: 'warning', field: 'cut.shrinkPct', message: '수축 여유율이 10%를 넘습니다. 원단 사양을 확인하세요.' });
  }
  if (inp.method === 'joined' && isNum(inp.fabricWidth) && inp.fabricWidth > 0 && isNum(inp.cut.seamLoss)) {
    if (inp.cut.seamLoss >= inp.fabricWidth)
      out.push({ level: 'error', field: 'cut.seamLoss', message: '봉제 손실이 원단 1폭보다 크거나 같습니다.' });
  }
  return out;
}

/** 길이 방향 재단 길이 = (세로 + 상단 + 하단 + 기타) × (1 + 수축%) → 무늬 반복 올림 또는 재단 단위 올림 */
export function cutLength(height: number, cut: CutSettings, applyPattern: boolean): CutSteps {
  const base = clean(height + cut.top + cut.bottom + cut.other);
  const afterShrink = clean(base * (1 + cut.shrinkPct / 100));
  let final = afterShrink;
  let patternApplied = false;
  let roundApplied = false;
  let roundSkippedByPattern = false;
  if (applyPattern && cut.patternRepeat > 0) {
    // 무늬 맞춤: 반복 길이의 배수로 올림. 이 경우 재단 단위 올림은 적용하지 않는다(무늬 위치가 어긋나므로).
    final = ceilTo(afterShrink, cut.patternRepeat);
    patternApplied = true;
    roundSkippedByPattern = cut.roundUnit > 0;
  } else if (cut.roundUnit > 0) {
    final = ceilTo(afterShrink, cut.roundUnit);
    roundApplied = true;
  }
  return { base, afterShrink, final, patternApplied, roundApplied, roundSkippedByPattern };
}

/**
 * 폭 연결형 한 장의 필요 폭 수.
 * 유효 가로 = N × 원단폭 − (N−1) × 봉제손실 − 2 × 옆단여유 ≥ 필요 가로 를 만족하는 최소 N.
 * 봉제손실·옆단 0이면 = 올림(필요 가로 ÷ 원단폭).
 */
export function widthsForPanel(required: number, fabricWidth: number, seamLoss: number, sideHem: number): number {
  const n = ceilSafe((required + 2 * sideHem - seamLoss) / (fabricWidth - seamLoss));
  return Math.max(1, n);
}

export function calcCurtain(inp: CurtainInput): CurtainResult {
  const issues = validateCurtain(inp);
  if (issues.some((i) => i.level === 'error')) return emptyResult(inp, issues);

  const W = inp.width as number;
  const H = inp.height as number;
  const FW = inp.fabricWidth as number;
  const F = inp.fullness as number;
  const cut = inp.cut;

  const requiredWidthTotal = clean(W * F);
  const leaves: { side: CurtainPanel['side']; ratio: number }[] =
    inp.opening === 'single'
      ? [{ side: 'single', ratio: 1 }]
      : [
          { side: 'left', ratio: (inp.splitLeft as number) / 100 },
          { side: 'right', ratio: (inp.splitRight as number) / 100 },
        ];

  const panels: CurtainPanel[] = leaves.map(({ side, ratio }) => {
    const finishedWidth = clean(W * ratio);
    const requiredWidth = clean(finishedWidth * F);
    if (inp.method === 'joined') {
      const widths = widthsForPanel(requiredWidth, FW, cut.seamLoss, cut.sideHem);
      const seams = widths - 1;
      const usableWidth = clean(widths * FW - seams * cut.seamLoss - 2 * cut.sideHem);
      return {
        side,
        ratio,
        finishedWidth,
        requiredWidth,
        widths,
        rawRatio: clean(requiredWidth / FW),
        seams,
        usableWidth,
        surplus: clean(usableWidth - requiredWidth),
        actualFullness: clean(usableWidth / finishedWidth),
        pieceLength: 0,
      };
    }
    // 광폭: 원단을 가로로 눕혀 롤 길이 방향으로 커튼 가로를 확보 (이음 없음)
    const raw = clean(requiredWidth + 2 * cut.sideHem);
    const pieceLength = cut.roundUnit > 0 ? ceilTo(raw, cut.roundUnit) : raw;
    const usableWidth = clean(pieceLength - 2 * cut.sideHem);
    return {
      side,
      ratio,
      finishedWidth,
      requiredWidth,
      widths: 0,
      rawRatio: 0,
      seams: 0,
      usableWidth,
      surplus: clean(usableWidth - requiredWidth),
      actualFullness: clean(usableWidth / finishedWidth),
      pieceLength,
    };
  });

  const base: CurtainResult = {
    ok: true,
    producible: true,
    issues,
    method: inp.method,
    opening: inp.opening,
    width: W,
    height: H,
    fabricWidth: FW,
    fullness: F,
    requiredWidthTotal,
    panels,
    totalWidths: 0,
    naiveWidths: 0,
    cut: cutLength(H, cut, inp.method === 'joined'),
    totalLength: 0,
    wide: null,
  };

  if (inp.method === 'joined') {
    base.totalWidths = panels.reduce((s, p) => s + p.widths, 0);
    base.naiveWidths = Math.max(1, ceilSafe(requiredWidthTotal / FW));
    base.totalLength = clean(base.totalWidths * base.cut.final);
    if (inp.opening === 'double' && base.naiveWidths !== base.totalWidths && cut.seamLoss === 0 && cut.sideHem === 0) {
      issues.push({
        level: 'info',
        code: 'split-rounding',
        message: `전체 가로로 한 번만 올림하면 ${base.naiveWidths}폭이지만, 양개는 좌우를 각각 올림하므로 ${base.totalWidths}폭이 필요합니다.`,
      });
    }
    if (inp.wideThreshold && FW >= inp.wideThreshold) {
      issues.push({
        level: 'info',
        code: 'wide-hint',
        message: `원단 폭 ${FW}cm는 광폭 원단입니다. 원단을 가로로 눕혀 쓴다면 '광폭 원단형'으로 바꿔 계산하세요.`,
      });
    }
    if (cut.patternRepeat > 0 && base.cut.roundSkippedByPattern) {
      issues.push({
        level: 'info',
        code: 'pattern-round',
        message: '무늬 반복 길이가 설정되어 재단 단위 올림은 적용하지 않았습니다.',
      });
    }
  } else {
    const requiredHeight = base.cut.afterShrink; // 광폭형은 원단 폭이 곧 커튼 높이
    const heightOk = requiredHeight <= FW + 1e-9;
    base.wide = { rollWidth: FW, requiredHeight, heightOk, shortfall: heightOk ? 0 : clean(requiredHeight - FW) };
    base.cut = { ...base.cut, final: requiredHeight, patternApplied: false, roundApplied: false, roundSkippedByPattern: false };
    base.totalLength = clean(panels.reduce((s, p) => s + p.pieceLength, 0));
    if (!heightOk) {
      base.producible = false;
      issues.push({
        level: 'critical',
        code: 'wide-height',
        field: 'fabricWidth',
        message: `원단 폭이 제작 높이를 충족하지 않습니다. (필요 ${clean(requiredHeight)}cm, 원단 ${FW}cm, ${base.wide.shortfall}cm 부족)`,
      });
    }
    if (cut.patternRepeat > 0) {
      issues.push({
        level: 'info',
        code: 'wide-pattern',
        message: '광폭 원단형은 이음이 없어 무늬 반복 길이를 적용하지 않습니다.',
      });
    }
  }

  return base;
}
