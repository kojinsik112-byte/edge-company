"""로고·스티커(이미지) 얹기.

예: 자이 로고를 12초부터 3초 동안 오른쪽 위에 '팝' 하고 띄우고, 나타날 때 '띠링' 효과음.
편집 화면에서 정한 목록(overlays)을 ffmpeg overlay 필터 한 번으로 입힌다.

overlay 한 개 = {
  "path": 이미지 경로(PNG 권장, 투명 배경 지원),
  "start": 시작(초), "dur": 길이(초),
  "pos": top-left / top / top-right / center / bottom-left / bottom-right / left / right,
  "size": 화면 폭 대비 크기(%, 5~80),
  "anim": pop / fade / none,
  "sfx": 나타날 때 효과음 이름(없으면 None),
}
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .config import OutputConfig
from .ffmpeg import probe_dimensions, run
from .utils import logger

POSITIONS = {
    "top-left": (0.0, 0.0), "top": (0.5, 0.0), "top-right": (1.0, 0.0),
    "left": (0.0, 0.5), "center": (0.5, 0.5), "right": (1.0, 0.5),
    "bottom-left": (0.0, 1.0), "bottom": (0.5, 1.0), "bottom-right": (1.0, 1.0),
}


def valid(overlays: Optional[List[Dict]]) -> List[Dict]:
    out = []
    for o in overlays or []:
        try:
            p = Path(o["path"])
            if p.exists() and float(o.get("dur", 0)) > 0:
                out.append(o)
        except Exception:  # noqa: BLE001
            continue
    return out


def shift(overlays: List[Dict], start: float, end: float) -> List[Dict]:
    """숏츠처럼 일부 구간만 잘라낼 때, 그 구간에 걸친 로고만 시간을 옮겨 돌려준다."""
    out = []
    for o in overlays:
        s, e = float(o["start"]), float(o["start"]) + float(o["dur"])
        if e <= start or s >= end:
            continue
        ns = max(0.0, s - start)
        out.append({**o, "start": ns, "dur": min(e, end) - start - ns,
                    "sfx": o.get("sfx") if s >= start else None})
    return out


def sfx_cues(overlays: List[Dict]) -> List[Tuple[float, str]]:
    return [(float(o["start"]), o["sfx"]) for o in overlays if o.get("sfx")]


def _num(x: float) -> str:
    return f"{x:.3f}"


def apply_overlays(
    video: Path, overlays: List[Dict], out_path: Path, out_cfg: OutputConfig
) -> Path:
    """이미지들을 영상 위에 얹는다. 얹을 게 없으면 원본 경로를 그대로 돌려준다."""
    overlays = valid(overlays)
    if not overlays:
        return video
    dims = probe_dimensions(video) or (out_cfg.width, out_cfg.height)
    W, H = dims
    margin = round(min(W, H) * 0.04)

    inputs: List[str] = ["-i", str(video)]
    chains: List[str] = []
    last = "0:v"
    for i, o in enumerate(overlays, start=1):
        inputs += ["-loop", "1", "-i", str(o["path"])]
        s = float(o["start"])
        e = s + float(o["dur"])
        ow = max(16, round(W * min(80.0, max(5.0, float(o.get("size", 20)))) / 100))
        anim = o.get("anim", "pop")
        fx, fy = POSITIONS.get(o.get("pos", "top-right"), POSITIONS["top-right"])

        f = f"[{i}:v]format=rgba,scale={ow}:-2:flags=lanczos"
        op = float(o.get("opacity", 1.0))
        if op < 0.999:  # 워터마크처럼 반투명
            f += f",colorchannelmixer=aa={max(0.05, op):.2f}"
        if anim == "pop":
            # 0.12초 동안 115%까지 커졌다가 100%로 — '톡' 튀어나오는 느낌
            k = (
                f"if(lt(t-{_num(s)},0.12),0.5+0.65*max(0,t-{_num(s)})/0.12,"
                f"if(lt(t-{_num(s)},0.22),1.15-0.15*(t-{_num(s)}-0.12)/0.10,1))"
            )
            f += f",scale=w='trunc(iw*{k}/2)*2':h='trunc(ih*{k}/2)*2':eval=frame"
        if anim in ("pop", "fade"):
            f += f",fade=in:st={_num(s)}:d=0.2:alpha=1,fade=out:st={_num(max(s, e - 0.25))}:d=0.25:alpha=1"
        chains.append(f + f"[o{i}]")

        # 기준점(모서리/가운데)에 이미지 중심이 오도록 — 팝으로 크기가 변해도 같은 자리
        cx = f"({margin}+(W-2*{margin})*{fx})"
        cy = f"({margin}+(H-2*{margin})*{fy})"
        x = f"{cx}-w*{fx}"
        y = f"{cy}-h*{fy}"
        nxt = f"v{i}"
        chains.append(
            f"[{last}][o{i}]overlay=x='{x}':y='{y}':eval=frame:shortest=1:"
            f"enable='between(t,{_num(s)},{_num(e)})'[{nxt}]"
        )
        last = nxt

    logger.info("로고·스티커 %d개 얹기", len(overlays))
    run(
        [
            "ffmpeg", "-y", *inputs,
            "-filter_complex", ";".join(chains),
            "-map", f"[{last}]", "-map", "0:a?",
            "-c:v", out_cfg.video_codec, "-crf", str(out_cfg.crf), "-preset", out_cfg.preset,
            "-pix_fmt", "yuv420p", "-c:a", "copy",
            str(out_path),
        ],
        show_progress=True,
    )
    return out_path
