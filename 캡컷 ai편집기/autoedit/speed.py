"""속도 조절 — 말이 빠르면 0.9배처럼 살짝 느리게 (목소리 높이는 그대로).

영상은 setpts, 소리는 atempo(음높이 유지)로 바꾸고, 자막·단어·로고 시간도 같은 비율로 옮긴다.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .config import OutputConfig
from .ffmpeg import has_audio, run
from .transcribe import Caption, Word


def change_speed(video: Path, speed: float, out_path: Path, out_cfg: OutputConfig) -> Path:
    if abs(speed - 1.0) < 0.01:
        return video
    args = ["ffmpeg", "-y", "-i", str(video)]
    if has_audio(video):
        args += ["-filter_complex", f"[0:v]setpts=PTS/{speed:.4f}[v];[0:a]atempo={speed:.4f}[a]",
                 "-map", "[v]", "-map", "[a]", "-c:a", "aac", "-b:a", out_cfg.audio_bitrate]
    else:
        args += ["-vf", f"setpts=PTS/{speed:.4f}"]
    args += ["-c:v", out_cfg.video_codec, "-crf", str(out_cfg.inter_crf), "-preset", out_cfg.inter_preset,
             "-pix_fmt", "yuv420p", "-r", str(out_cfg.fps), str(out_path)]
    run(args, show_progress=True)
    return out_path


def scale_captions(caps: List[Caption], speed: float) -> List[Caption]:
    if abs(speed - 1.0) < 0.01:
        return caps
    k = 1.0 / speed
    return [
        Caption(c.start * k, c.end * k, c.text,
                [Word(w.start * k, w.end * k, w.text, w.prob) for w in c.words] if c.words else None,
                c.emph, c.pos, c.align, c.sfx, c.zoom)
        for c in caps
    ]


def scale_overlays(ovs: List[Dict], speed: float) -> List[Dict]:
    if abs(speed - 1.0) < 0.01:
        return ovs
    k = 1.0 / speed
    return [{**o, "start": round(float(o["start"]) * k, 2), "dur": round(float(o["dur"]) * k, 2)} for o in ovs]
