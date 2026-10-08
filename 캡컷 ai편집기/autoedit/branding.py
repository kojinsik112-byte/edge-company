"""브랜딩 — 인트로/아웃트로 이어 붙이기 + 배경음악(BGM) 믹싱."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import List, Optional

from .config import BrandingConfig, OutputConfig
from .ffmpeg import has_audio, run
from .utils import logger


def _is_mono(video: Path) -> bool:
    from .ffmpeg import _header

    return any("Audio:" in ln and " mono" in ln for ln in _header(video).splitlines())


def add_bgm(
    video: Path, bgm: Path, out_path: Path, out_cfg: OutputConfig, volume: float
) -> Path:
    """본 영상의 음성은 유지하면서 배경음악을 낮은 볼륨으로 깐다.

    BGM은 영상 길이에 맞춰 반복(loop)되고, 영상이 끝나면 함께 끝난다(duration=first).
    - 말소리는 원래 크기 그대로 (예전엔 amix 정규화 때문에 목소리가 절반으로 줄었음)
    - 말할 때는 음악이 자동으로 작아지는 '덕킹'(sidechain) — 방송 편집 방식
    - 처음 1.5초 서서히 커지고, 끝 2초 서서히 작아짐
    """
    from .ffmpeg import probe_duration

    dur = probe_duration(video)
    fade_out = max(0.0, dur - 2.0)
    filt = (
        f"[1:a]aformat=channel_layouts=stereo,volume={volume * 2.2:.3f},"
        f"afade=t=in:d=1.5,afade=t=out:st={fade_out:.2f}:d=2[bg];"
        # 모노 목소리는 크기 손실 없이 양쪽에 복사 (그냥 스테레오로 바꾸면 -3dB 작아짐)
        f"[0:a]{'pan=stereo|c0=c0|c1=c0' if _is_mono(video) else 'aformat=channel_layouts=stereo'},asplit=2[voice][sc];"
        "[bg][sc]sidechaincompress=threshold=0.02:ratio=6:attack=15:release=350[duck];"
        "[voice][duck]amix=inputs=2:duration=first:normalize=0:dropout_transition=0[a]"
    )
    if not has_audio(video):
        filt = (
            f"[1:a]volume={volume * 2.2:.3f},afade=t=in:d=1.5,"
            f"afade=t=out:st={fade_out:.2f}:d=2[a]"
        )
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-stream_loop",
            "-1",
            "-i",
            str(bgm),
            "-filter_complex",
            filt,
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
            "-shortest",
            str(out_path),
        ],
        show_progress=True,
    )
    return out_path


def _normalize_clip(
    video: Path, out_path: Path, out_cfg: OutputConfig
) -> Path:
    """한 클립을 출력 규격(해상도/프레임/오디오)으로 통일한다.

    오디오가 없으면 영상 길이에 맞춘 무음 트랙을 입힌다(-shortest로 무한 길이 방지).
    이렇게 모든 클립을 동일 규격으로 맞춰두면 이어 붙일 때 무손실 복사가 가능하다.
    """
    w, h, fps = out_cfg.width, out_cfg.height, out_cfg.fps
    vf = (
        f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
        f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}"
    )
    common = [
        "-c:v",
        out_cfg.video_codec,
        "-crf",
        str(out_cfg.crf),
        "-preset",
        out_cfg.preset,
        "-c:a",
        "aac",
        "-b:a",
        out_cfg.audio_bitrate,
        "-ar",
        "44100",
        "-ac",
        "2",
    ]
    if has_audio(video):
        args = ["ffmpeg", "-y", "-i", str(video), "-vf", vf, *common, str(out_path)]
    else:
        args = [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-f",
            "lavfi",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-vf",
            vf,
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-shortest",
            *common,
            str(out_path),
        ]
    run(args, show_progress=True)
    return out_path


def concat_videos(
    videos: List[Path], out_path: Path, out_cfg: OutputConfig, work_dir: Path
) -> Path:
    """서로 다른 영상들을 규격을 맞춘 뒤 이어 붙인다 (concat 디먹서, 무손실 복사)."""
    normalized: List[Path] = []
    for i, v in enumerate(videos):
        norm = work_dir / f"norm_{i}.mp4"
        normalized.append(_normalize_clip(v, norm, out_cfg))

    # concat 디먹서용 목록 파일 (경로의 작은따옴표는 ffmpeg 규칙대로 이스케이프).
    list_file = work_dir / "concat_list.txt"
    list_file.write_text(
        "\n".join(f"file '{str(p).replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'" for p in normalized),
        encoding="utf-8",
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-c",
            "copy",
            str(out_path),
        ]
    )
    return out_path


def _resolve(path: Optional[str], base: Path) -> Optional[Path]:
    """설정의 상대경로를 기준 디렉터리에 맞춰 절대경로로 바꾼다."""
    if not path:
        return None
    p = Path(path)
    if not p.is_absolute():
        p = base / p
    if not p.exists():
        logger.warning("브랜딩 자원을 찾을 수 없어 건너뜁니다: %s", p)
        return None
    return p


def apply_branding(
    video: Path,
    out_path: Path,
    work_dir: Path,
    cfg: BrandingConfig,
    out_cfg: OutputConfig,
    base_dir: Path,
) -> Path:
    """BGM → 인트로/아웃트로 순으로 브랜딩을 적용한다."""
    current = video

    bgm = _resolve(cfg.bgm, base_dir)
    if bgm:
        logger.info("배경음악 삽입: %s", bgm.name)
        bgm_out = work_dir / "with_bgm.mp4"
        current = add_bgm(current, bgm, bgm_out, out_cfg, cfg.bgm_volume)

    intro = _resolve(cfg.intro, base_dir)
    outro = _resolve(cfg.outro, base_dir)
    sequence = [p for p in (intro, current, outro) if p is not None]

    if len(sequence) > 1:
        logger.info(
            "인트로/아웃트로 결합 (intro=%s, outro=%s)",
            bool(intro),
            bool(outro),
        )
        concat_videos(sequence, out_path, out_cfg, work_dir)
    else:
        # 붙일 게 없으면 현재 결과를 그대로 최종 파일로.
        # 입력 영상 자체(=다시 편집할 때 쓰는 clean 영상일 수 있음)는 옮기지 말고 복사한다.
        if current != out_path:
            if current == video:
                shutil.copy2(current, out_path)
            else:
                current.replace(out_path)
    return out_path
