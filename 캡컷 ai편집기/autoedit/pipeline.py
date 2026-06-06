"""전체 자동 편집 파이프라인 오케스트레이션.

원본 영상 1개 →
  1) 무음 컷
  2) 자막 생성(번인)
  3) 숏츠 생성
  4) 인트로/아웃트로/BGM
→ 완성 영상 + 숏츠 클립들.
"""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .branding import apply_branding
from .config import Config
from .ffmpeg import ensure_ffmpeg, probe_duration
from .silence import cut_silence
from .subtitles import burn_subtitles
from .transcribe import Caption, WhisperUnavailable, transcribe, write_srt
from .shorts import make_shorts
from .utils import fmt_duration, logger


@dataclass
class PipelineResult:
    final_video: Optional[Path] = None
    srt: Optional[Path] = None
    shorts: List[Path] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)


def process(
    input_video: Path,
    output_dir: Path,
    config: Config,
    *,
    assets_dir: Optional[Path] = None,
    keep_temp: bool = False,
) -> PipelineResult:
    """원본 영상 한 개를 받아 완성 영상과 숏츠를 만든다."""
    ensure_ffmpeg()
    input_video = input_video.resolve()
    if not input_video.exists():
        raise FileNotFoundError(f"입력 영상을 찾을 수 없습니다: {input_video}")

    output_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = (assets_dir or (Path.cwd() / "assets")).resolve()
    stem = input_video.stem
    result = PipelineResult()

    work_dir = Path(tempfile.mkdtemp(prefix="autoedit_"))
    logger.info("작업 폴더: %s", work_dir)
    try:
        dur = probe_duration(input_video)
        logger.info("입력 영상: %s (%s)", input_video.name, fmt_duration(dur))

        # ── 1) 무음 컷 ───────────────────────────────────────────────
        current = input_video
        if config.silence.enabled:
            logger.info("[1/4] 무음 구간 자동 컷")
            cut_path = work_dir / "cut.mp4"
            current, _segments = cut_silence(
                current, cut_path, config.silence, config.output
            )
            result.steps.append("무음 컷")
        else:
            logger.info("[1/4] 무음 컷 건너뜀 (비활성화)")

        # ── 2) 자막 생성 ─────────────────────────────────────────────
        captions: Optional[List[Caption]] = None
        if config.subtitle.enabled:
            logger.info("[2/4] 자동 자막 생성")
            try:
                captions = transcribe(current, work_dir, config.subtitle)
                srt_out = output_dir / f"{stem}.srt"
                write_srt(captions, srt_out, config.subtitle.max_line_chars)
                result.srt = srt_out
                result.steps.append("자막 생성")

                if config.subtitle.burn_in and captions:
                    logger.info("자막 번인(굽기)")
                    burned = work_dir / "subbed.mp4"
                    burn_subtitles(
                        current, srt_out, burned, config.subtitle, config.output
                    )
                    current = burned
                    result.steps.append("자막 번인")
            except WhisperUnavailable as exc:
                logger.warning("자막 단계 건너뜀: %s", exc)
        else:
            logger.info("[2/4] 자막 건너뜀 (비활성화)")

        # ── 3) 숏츠 생성 ─────────────────────────────────────────────
        # 숏츠는 자막이 구워지기 전의 영상(current)을 기준으로 만든다 →
        # 세로 클립에 맞는 자막을 다시 입히기 위함.
        if config.shorts.enabled:
            logger.info("[3/4] 숏츠 자동 생성")
            shorts_dir = output_dir / "shorts"
            result.shorts = make_shorts(
                current,
                shorts_dir,
                work_dir,
                captions,
                config.shorts,
                config.output,
                config.subtitle,
                stem,
            )
            if result.shorts:
                result.steps.append(f"숏츠 {len(result.shorts)}개")
        else:
            logger.info("[3/4] 숏츠 건너뜀 (비활성화)")

        # ── 4) 인트로/아웃트로/BGM ──────────────────────────────────
        final_out = output_dir / f"{stem}_edited.mp4"
        if config.branding.enabled:
            logger.info("[4/4] 인트로/아웃트로/BGM")
            apply_branding(
                current,
                final_out,
                work_dir,
                config.branding,
                config.output,
                assets_dir,
            )
            result.steps.append("브랜딩")
        else:
            logger.info("[4/4] 브랜딩 건너뜀 (비활성화)")
            shutil.copy2(current, final_out)

        result.final_video = final_out
        return result
    finally:
        if keep_temp:
            logger.info("임시 폴더 보존: %s", work_dir)
        else:
            shutil.rmtree(work_dir, ignore_errors=True)
