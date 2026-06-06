"""무음 구간 자동 컷.

ffmpeg의 silencedetect 필터로 무음 구간을 찾고, 그 여집합(=말소리 구간)만
이어 붙여 군더더기 없는 영상을 만든다.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple

from .config import SilenceConfig, OutputConfig
from .ffmpeg import probe_duration, run
from .utils import Segment, invert_intervals, logger, merge_intervals


def detect_silence(video: Path, cfg: SilenceConfig) -> List[Tuple[float, float]]:
    """무음 구간 [(start, end), ...] 을 초 단위로 반환한다."""
    proc = run(
        [
            "ffmpeg",
            "-i",
            str(video),
            "-af",
            f"silencedetect=noise={cfg.noise_db}dB:d={cfg.min_silence}",
            "-f",
            "null",
            "-",
        ]
    )
    stderr = proc.stderr
    starts = [float(x) for x in re.findall(r"silence_start:\s*(-?[\d.]+)", stderr)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*(-?[\d.]+)", stderr)]

    silences: List[Tuple[float, float]] = []
    for i, start in enumerate(starts):
        end = ends[i] if i < len(ends) else probe_duration(video)
        silences.append((max(0.0, start), end))
    return silences


def compute_keep_segments(video: Path, cfg: SilenceConfig) -> List[Segment]:
    """잘라내고 남길 말소리 구간을 계산한다."""
    total = probe_duration(video)
    silences = detect_silence(video, cfg)

    keep = invert_intervals(silences, total)

    # 잘린 경계 앞뒤로 약간의 여유(pad)를 줘 말이 뚝 끊기지 않게 한다.
    padded = [
        (max(0.0, s - cfg.keep_pad), min(total, e + cfg.keep_pad)) for s, e in keep
    ]
    padded = merge_intervals(padded, gap=0.05)

    segments = [Segment(s, e) for s, e in padded if (e - s) >= cfg.min_keep]
    if not segments:
        # 전부 무음으로 잡힌 비정상 케이스 → 원본 전체를 유지
        logger.warning("말소리 구간을 찾지 못해 원본 전체를 유지합니다.")
        segments = [Segment(0.0, total)]
    return segments


def render_cut(
    video: Path,
    segments: List[Segment],
    out_path: Path,
    out_cfg: OutputConfig,
) -> Path:
    """말소리 구간만 이어 붙인 영상을 렌더링한다 (한 번 재인코딩)."""
    parts = []
    filt = []
    for i, seg in enumerate(segments):
        filt.append(
            f"[0:v]trim=start={seg.start:.3f}:end={seg.end:.3f},"
            f"setpts=PTS-STARTPTS[v{i}];"
        )
        filt.append(
            f"[0:a]atrim=start={seg.start:.3f}:end={seg.end:.3f},"
            f"asetpts=PTS-STARTPTS[a{i}];"
        )
        parts.append(f"[v{i}][a{i}]")
    filt.append(f"{''.join(parts)}concat=n={len(segments)}:v=1:a=1[v][a]")
    filter_complex = "".join(filt)

    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-filter_complex",
            filter_complex,
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-c:v",
            out_cfg.video_codec,
            "-crf",
            str(out_cfg.crf),
            "-preset",
            out_cfg.preset,
            "-r",
            str(out_cfg.fps),
            "-c:a",
            "aac",
            "-b:a",
            out_cfg.audio_bitrate,
            str(out_path),
        ],
        show_progress=True,
    )
    return out_path


def cut_silence(
    video: Path, out_path: Path, cfg: SilenceConfig, out_cfg: OutputConfig
) -> Tuple[Path, List[Segment]]:
    """무음 컷 전체 과정. (출력경로, 남긴 구간들)을 반환한다."""
    segments = compute_keep_segments(video, cfg)
    total_kept = sum(s.duration for s in segments)
    logger.info(
        "무음 컷: %d개 구간 유지, 총 %.1f초", len(segments), total_kept
    )
    render_cut(video, segments, out_path, out_cfg)
    return out_path, segments
