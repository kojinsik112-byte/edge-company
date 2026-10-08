"""컷 타임라인 — 원본에서 어디를 남기고 어디를 잘랐는지, 그리고 다시 자르기(살리기).

'원본 시간'(컷 전 영상)과 '편집 시간'(컷 후 영상)을 오가며 자막·단어·로고 시간을 옮긴다.
keep = [(시작, 끝), ...] 원본 시간 기준 남길 구간 (정렬·겹침 없음).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from .transcribe import Caption, Word

Seg = Tuple[float, float]


def normalize(keep: Sequence[Sequence[float]], total: float, min_len: float = 0.15) -> List[Seg]:
    segs = sorted((max(0.0, float(a)), min(total, float(b))) for a, b in keep)
    out: List[Seg] = []
    for a, b in segs:
        if b - a < min_len:
            continue
        if out and a <= out[-1][1] + 0.02:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def to_source(t: float, keep: List[Seg]) -> float:
    """편집 시간 → 원본 시간."""
    acc = 0.0
    for a, b in keep:
        d = b - a
        if t <= acc + d + 1e-6:
            return a + max(0.0, t - acc)
        acc += d
    return keep[-1][1] if keep else t


def to_edit(t: float, keep: List[Seg]) -> Optional[float]:
    """원본 시간 → 편집 시간. 잘린 곳이면 None."""
    acc = 0.0
    for a, b in keep:
        if a - 1e-6 <= t <= b + 1e-6:
            return acc + (min(max(t, a), b) - a)
        acc += b - a
    return None


def _snap(t: float, keep: List[Seg], forward: bool) -> Optional[float]:
    """잘린 곳에 떨어진 시각을 가까운 남은 구간 경계로."""
    v = to_edit(t, keep)
    if v is not None:
        return v
    acc = 0.0
    for a, b in keep:
        if t < a:
            return acc if forward else (acc if acc > 0 else 0.0)
        acc += b - a
    return acc if not forward else None


def remap_captions(caps: List[Caption], old_keep: List[Seg], new_keep: List[Seg]) -> List[Caption]:
    """편집 시간(옛 컷) → 원본 → 편집 시간(새 컷). 새 컷에서 완전히 잘려 나간 자막은 뺀다."""
    out: List[Caption] = []
    for c in caps:
        s_src, e_src = to_source(c.start, old_keep), to_source(c.end, old_keep)
        s, e = _snap(s_src, new_keep, True), _snap(e_src, new_keep, False)
        if s is None or e is None or e - s < 0.1:
            continue
        words = None
        if c.words:
            words = []
            for w in c.words:
                ws = _snap(to_source(w.start, old_keep), new_keep, True)
                we = _snap(to_source(w.end, old_keep), new_keep, False)
                if ws is None or we is None:
                    ws = we = s
                words.append(Word(ws, max(ws, we), w.text, w.prob))
        out.append(Caption(s, e, c.text, words, c.emph, c.pos, c.align, c.sfx, c.zoom))
    return out


def remap_overlays(ovs: List[Dict], old_keep: List[Seg], new_keep: List[Seg]) -> List[Dict]:
    out = []
    for o in ovs:
        s = _snap(to_source(float(o["start"]), old_keep), new_keep, True)
        if s is None:
            continue
        out.append({**o, "start": round(s, 2)})
    return out


def removed(keep: List[Seg], total: float) -> List[Seg]:
    gaps, cur = [], 0.0
    for a, b in keep:
        if a - cur > 0.05:
            gaps.append((cur, a))
        cur = b
    if total - cur > 0.05:
        gaps.append((cur, total))
    return gaps


def recut(source: Path, new_keep: List[Seg], out_path: Path, out_cfg) -> Path:
    from .silence import render_cut
    from .utils import Segment

    render_cut(source, [Segment(a, b) for a, b in new_keep], out_path, out_cfg)
    return out_path
