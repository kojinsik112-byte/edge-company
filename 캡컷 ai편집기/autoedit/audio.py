"""오디오 후처리 — 볼륨 균일화(loudnorm) + 효과음(SFX) 믹싱."""

from __future__ import annotations

from pathlib import Path

from .config import OutputConfig
from .ffmpeg import has_audio, run
from .utils import logger


def normalize_loudness(
    video: Path, out_path: Path, out_cfg: OutputConfig, target_lufs: float
) -> Path:
    """본 영상의 음량을 유튜브 권장 수준(LUFS)으로 균일화한다.

    오디오 트랙이 없으면 원본을 그대로 반환한다(불필요한 재인코딩 방지).
    영상은 무손실 복사하고 오디오만 다시 인코딩한다.
    """
    if not has_audio(video):
        logger.info("오디오 트랙이 없어 볼륨 균일화를 건너뜁니다.")
        return video
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-af",
            f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11",
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


def overlay_start_sfx(
    video: Path, sfx: Path, out_path: Path, out_cfg: OutputConfig, volume: float
) -> Path:
    """영상 "시작" 지점에 효과음을 본 오디오와 섞는다.

    효과음이 짧아도 amix duration=first 로 영상 길이를 유지하고,
    normalize=0 으로 본 음성 볼륨이 깎이지 않게 한다.
    """
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-i",
            str(sfx),
            "-filter_complex",
            f"[1:a]volume={volume}[s];"
            f"[0:a][s]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a]",
            "-map",
            "0:v",
            "-map",
            "[a]",
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
