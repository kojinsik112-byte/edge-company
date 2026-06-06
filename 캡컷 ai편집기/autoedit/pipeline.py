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

from .audio import normalize_loudness
from .branding import apply_branding
from .config import Config
from .ffmpeg import ensure_ffmpeg, probe_duration
from .silence import cut_silence
from .subtitles import burn_subtitles
from .transcribe import Caption, WhisperUnavailable, parse_srt, transcribe, write_srt
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
    srt_override: Optional[Path] = None,
) -> PipelineResult:
    """원본 영상 한 개를 받아 완성 영상과 숏츠를 만든다.

    srt_override 가 주어지면 음성 인식을 건너뛰고 그 SRT(사용자가 오타를 직접
    고친 자막)를 본편/숏츠에 그대로 사용한다.
    """
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

        # ── 오디오 볼륨 균일화 (loudnorm) ────────────────────────────
        # 본편/숏츠가 모두 이 영상에서 갈라져 나오므로 여기서 한 번만 맞춘다.
        if config.output.normalize_audio:
            logger.info("오디오 볼륨 균일화 (loudnorm, 목표 %.0f LUFS)", config.output.loudness_target)
            norm_path = work_dir / "normalized.mp4"
            normalized = normalize_loudness(
                current, norm_path, config.output, config.output.loudness_target
            )
            if normalized != current:
                current = normalized
                result.steps.append("볼륨 균일화")

        # ── 2) 자막 생성 ─────────────────────────────────────────────
        captions: Optional[List[Caption]] = None
        if config.subtitle.enabled:
            srt_out = output_dir / f"{stem}.srt"
            try:
                if srt_override is not None:
                    if not srt_override.exists():
                        raise FileNotFoundError(
                            f"지정한 자막 파일을 찾을 수 없습니다: {srt_override}"
                        )
                    logger.info("[2/4] 수정된 자막 사용: %s", srt_override)
                    captions = parse_srt(srt_override)
                    logger.info("자막 구간 %d개 불러옴", len(captions))
                    # 본편 출력 폴더에도 동일 자막을 남겨 추적 가능하게 한다.
                    write_srt(captions, srt_out, config.subtitle.max_line_chars)
                    result.steps.append("수정 자막 적용")
                else:
                    logger.info("[2/4] 자동 자막 생성")
                    captions = transcribe(current, work_dir, config.subtitle)
                    write_srt(captions, srt_out, config.subtitle.max_line_chars)
                    result.steps.append("자막 생성")
                result.srt = srt_out

                if config.subtitle.burn_in and captions:
                    logger.info("자막 번인(굽기)")
                    burned = work_dir / "subbed.mp4"
                    # video_size 미지정 → 실제 영상 해상도를 자동 측정해 픽셀 기준을 맞춘다.
                    # (무음 컷은 원본 해상도를 유지하므로 출력 설정값으로 단정하지 않는다.)
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
                assets_dir,
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
