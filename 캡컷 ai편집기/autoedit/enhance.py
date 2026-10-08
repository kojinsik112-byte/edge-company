"""영상 화면 보정 — 자동 밝기·색 보정 + 손떨림 보정.

폰 영상은 실내에서 어둡거나 색이 칙칙하고, 손에 들고 찍으면 흔들린다.
- 밝기·색: 영상 몇 장면의 평균 밝기·채도를 재서 '필요한 만큼만' 감마·대비·채도를 올린다
  (이미 밝은 영상은 거의 건드리지 않음 → 과보정 방지)
- 손떨림: vidstab 2단계(흔들림 측정 → 부드럽게 보정, 가장자리 살짝 확대로 빈 테두리 숨김)
결과는 거의 무손실(중간 화질)로 저장하고 소리는 그대로 복사한다.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from statistics import mean
from typing import Optional, Tuple

from .config import OutputConfig
from .ffmpeg import FFmpegError, probe_duration, run
from .utils import logger


def measure(video: Path) -> Tuple[float, float]:
    """(평균 밝기 YAVG 0~255, 평균 채도 SATAVG) — 2초마다 한 장씩 작게 재본다."""
    dur = probe_duration(video)
    step = max(1.0, dur / 30)  # 최대 약 30장
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(video), "-vf",
         f"fps=1/{step:.2f},scale=320:-2,signalstats,metadata=print:key=lavfi.signalstats.YAVG,"
         "metadata=print:key=lavfi.signalstats.SATAVG",
         "-an", "-f", "null", "-"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
    )
    out = proc.stdout + proc.stderr
    ys = [float(x) for x in re.findall(r"YAVG=([\d.]+)", out)]
    ss = [float(x) for x in re.findall(r"SATAVG=([\d.]+)", out)]
    return (mean(ys) if ys else 120.0, mean(ss) if ss else 40.0)


def color_filter(yavg: float, satavg: float) -> Optional[str]:
    """측정값 → eq 필터. 보정할 필요가 없으면 None."""
    gamma = 1.0
    if yavg < 90:  # 확실히 어두울 때만 (TV 범위 16~235 기준, 정상 노출 약 100~140)
        gamma = min(1.3, max(1.0, (105 / max(yavg, 30)) ** 0.6))
    sat = 1.0
    if satavg < 15:
        sat = 1.12
    elif satavg < 30:
        sat = 1.06
    contrast = 1.04 if (gamma > 1.0 or sat > 1.0) else 1.0
    if gamma == 1.0 and sat == 1.0:
        return None
    return f"eq=gamma={gamma:.3f}:contrast={contrast:.2f}:saturation={sat:.2f}"


def enhance_video(
    video: Path,
    out_path: Path,
    work_dir: Path,
    out_cfg: OutputConfig,
    *,
    color: bool = True,
    stabilize: bool = False,
) -> Path:
    """보정할 게 없으면 원본 경로를 그대로 돌려준다."""
    filters = []
    if color:
        y, s = measure(video)
        f = color_filter(y, s)
        logger.info("화면 밝기 %.0f · 채도 %.0f → %s", y, s, f or "보정 불필요")
        if f:
            filters.append(f)
    if stabilize:
        logger.info("손떨림 분석 중...")
        trf = "stab.trf"  # 작업 폴더 기준 상대경로 (윈도우 경로의 ':' 이스케이프 문제 회피)
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(video),
                 "-vf", f"vidstabdetect=shakiness=6:accuracy=12:result={trf}", "-f", "null", "-"],
                cwd=str(work_dir), check=True,
            )
            filters.insert(0, f"vidstabtransform=input={trf}:smoothing=14:zoom=2:optzoom=0:interpol=bicubic,unsharp=5:5:0.5")
            logger.info("손떨림 보정 적용")
        except subprocess.CalledProcessError:
            logger.warning("손떨림 분석 실패 → 보정 없이 진행")
    if not filters:
        return video
    vf = ",".join(filters)
    args = [
        "ffmpeg", "-y", "-i", str(video), "-vf", vf,
        "-c:v", out_cfg.video_codec, "-crf", str(out_cfg.inter_crf), "-preset", out_cfg.inter_preset,
        "-pix_fmt", "yuv420p", "-c:a", "copy", str(out_path),
    ]
    if stabilize:
        # vidstabtransform 이 상대경로 trf 를 읽도록 작업 폴더에서 실행
        proc = subprocess.run(args, cwd=str(work_dir), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                              text=True, encoding="utf-8", errors="replace")
        if proc.returncode != 0:
            raise FFmpegError("화면 보정 실패:\n" + "\n".join(proc.stderr.splitlines()[-8:]))
    else:
        run(args, show_progress=True)
    return out_path
