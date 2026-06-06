"""오디오 음질 개선 — 노이즈 제거 + 음량 정규화.

유튜브 표준 음량(-14 LUFS)으로 맞추고 배경 잡음을 줄여 '프로 같은' 소리로 만든다.
영상은 그대로 두고(-c:v copy) 오디오만 다시 인코딩한다.
"""

from __future__ import annotations

from pathlib import Path

from .config import AudioConfig, OutputConfig
from .ffmpeg import has_audio, run
from .utils import logger


def enhance_audio(
    video: Path, out_path: Path, cfg: AudioConfig, out_cfg: OutputConfig
) -> Path:
    """노이즈 제거·음량 정규화를 적용한 영상을 만든다."""
    if not has_audio(video):
        return video

    filters = []
    if cfg.denoise:
        # FFT 기반 잡음 제거 (별도 모델 불필요)
        filters.append("afftdn=nf=-25")
    if cfg.loudnorm:
        filters.append(f"loudnorm=I={cfg.target_lufs}:TP=-1.5:LRA=11")
    if not filters:
        return video

    logger.info(
        "오디오 개선: %s%s",
        "노이즈제거 " if cfg.denoise else "",
        f"음량정규화({cfg.target_lufs} LUFS)" if cfg.loudnorm else "",
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-af",
            ",".join(filters),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            out_cfg.audio_bitrate,
            str(out_path),
        ],
        show_progress=True,
    )
    return out_path
