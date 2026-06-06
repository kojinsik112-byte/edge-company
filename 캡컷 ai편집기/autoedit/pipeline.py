"""전체 자동 편집 파이프라인 오케스트레이션.

원본 영상 1개 →
  1) 무음 컷
  2) 자막 생성 + 추임새 제거
  3) 자막 굽기 / 숏츠 생성
  4) 인트로/아웃트로/BGM
→ 완성 영상 + 숏츠 + (수정 가능한) 자막 파일.
"""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .audio import enhance_audio
from .branding import apply_branding
from .config import Config
from .fillers import find_filler_ranges, remap_captions
from .ffmpeg import ensure_ffmpeg, probe_duration
from .metadata import write_metadata
from .silence import cut_silence, render_cut
from .subtitles import burn_subtitles
from .thumbnail import make_thumbnail
from .transcribe import (
    Caption,
    WhisperUnavailable,
    parse_srt,
    transcribe,
    write_srt,
)
from .shorts import make_shorts
from .utils import Segment, fmt_duration, invert_intervals, logger


@dataclass
class PipelineResult:
    final_video: Optional[Path] = None
    srt: Optional[Path] = None
    clean_video: Optional[Path] = None
    thumbnail: Optional[Path] = None
    metadata_file: Optional[Path] = None
    shorts: List[Path] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)


def _remove_fillers(
    video: Path, captions: List[Caption], work_dir: Path, config: Config
) -> tuple[Path, List[Caption]]:
    """추임새 구간을 영상에서 잘라내고 자막 시간을 다시 맞춘다."""
    ranges = find_filler_ranges(captions)
    if not ranges:
        logger.info("추임새: 제거할 구간 없음")
        return video, captions

    total = probe_duration(video)
    keep = invert_intervals(ranges, total)
    keep_segments = [Segment(s, e) for s, e in keep if e - s > 0.05]
    if not keep_segments:
        return video, captions

    removed = sum(e - s for s, e in ranges)
    logger.info("추임새 %d곳 제거 (%.1f초)", len(ranges), removed)
    out = work_dir / "defiller.mp4"
    render_cut(video, keep_segments, out, config.output)
    new_caps = remap_captions(captions, ranges)
    return out, new_caps


def _finish(
    clean: Path,
    captions: Optional[List[Caption]],
    stem: str,
    output_dir: Path,
    work_dir: Path,
    config: Config,
    assets_dir: Path,
    result: PipelineResult,
) -> None:
    """자막 굽기 → 숏츠 → 브랜딩. process/reburn 공통 마무리 단계."""
    # 자막 번인 (메인 영상)
    main = clean
    if config.subtitle.burn_in and captions:
        logger.info("자막 번인(굽기)")
        burned = work_dir / "subbed.mp4"
        burn_subtitles(
            clean,
            captions,
            burned,
            config.subtitle,
            config.output,
            work_dir,
            width=config.output.width,
            height=config.output.height,
        )
        main = burned
        result.steps.append("자막 번인")

    # 숏츠 — 항상 '자막 안 구운' clean 영상에서 생성 (이중 자막 방지)
    if config.shorts.enabled:
        logger.info("[3/4] 숏츠 자동 생성")
        result.shorts = make_shorts(
            clean,
            output_dir / "shorts",
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

    # 브랜딩
    final_out = output_dir / f"{stem}_edited.mp4"
    if config.branding.enabled:
        logger.info("[4/4] 인트로/아웃트로/BGM")
        apply_branding(
            main, final_out, work_dir, config.branding, config.output, assets_dir
        )
        result.steps.append("브랜딩")
    else:
        logger.info("[4/4] 브랜딩 건너뜀 (비활성화)")
        shutil.copy2(main, final_out)
    result.final_video = final_out


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

        # ── 0) 오디오 음질 개선 ─────────────────────────────────────
        current = input_video
        if config.audio.enabled:
            current = enhance_audio(
                current, work_dir / "audio.mp4", config.audio, config.output
            )
            if current != input_video:
                result.steps.append("음질 개선")

        # ── 1) 무음 컷 ───────────────────────────────────────────────
        if config.silence.enabled:
            logger.info("[1/5] 무음 구간 자동 컷")
            current, _segments = cut_silence(
                current, work_dir / "cut.mp4", config.silence, config.output
            )
            new_dur = probe_duration(current)
            logger.info("무음 컷 결과: %s → %s", fmt_duration(dur), fmt_duration(new_dur))
            result.steps.append("무음 컷")
        else:
            logger.info("[1/5] 무음 컷 건너뜀 (비활성화)")

        # ── 2) 자막 분석 + 추임새 제거 (글자 표시는 설정에 따름) ────
        captions: Optional[List[Caption]] = None
        if config.subtitle.enabled:
            logger.info("[2/5] 음성 분석 (추임새 제거·메타데이터용)")
            try:
                captions = transcribe(current, work_dir, config.subtitle)
                if config.subtitle.remove_fillers and captions:
                    current, captions = _remove_fillers(
                        current, captions, work_dir, config
                    )
                    result.steps.append("추임새 제거")
                srt_out = output_dir / f"{stem}.srt"
                write_srt(captions, srt_out, config.subtitle.max_line_chars)
                result.srt = srt_out
            except WhisperUnavailable as exc:
                logger.warning("음성 분석 건너뜀: %s", exc)
        else:
            logger.info("[2/5] 음성 분석 건너뜀 (비활성화)")

        # ── 메타데이터 (제목/설명/해시태그/챕터) ────────────────────
        if config.metadata.enabled and captions:
            logger.info("메타데이터 생성 (제목/설명/해시태그/챕터)")
            meta_out = output_dir / f"{stem}_업로드정보.txt"
            _, meta = write_metadata(captions, meta_out, config.metadata)
            result.metadata_file = meta_out
            result.steps.append("메타데이터")
        else:
            meta = None

        # 자막 수정용으로 '깨끗한' 영상을 보관한다.
        clean_out = output_dir / f"{stem}_clean.mp4"
        shutil.copy2(current, clean_out)
        result.clean_video = clean_out

        # ── 3·4) 자막 굽기(선택) / 숏츠 / 브랜딩 ────────────────────
        _finish(
            current, captions, stem, output_dir, work_dir, config, assets_dir, result
        )

        # ── 5) 썸네일 ───────────────────────────────────────────────
        if config.thumbnail.enabled:
            logger.info("[5/5] 썸네일 생성")
            title = meta["titles"][0] if meta and meta.get("titles") else None
            thumb_out = output_dir / f"{stem}_썸네일.png"
            try:
                make_thumbnail(
                    clean_out, thumb_out, work_dir, captions,
                    config.thumbnail, dur, title=title,
                )
                result.thumbnail = thumb_out
                result.steps.append("썸네일")
            except Exception as exc:  # noqa: BLE001
                logger.warning("썸네일 생성 건너뜀: %s", exc)

        return result
    finally:
        if keep_temp:
            logger.info("임시 폴더 보존: %s", work_dir)
        else:
            shutil.rmtree(work_dir, ignore_errors=True)


def reburn(
    clean_video: Path,
    srt: Path,
    output_dir: Path,
    config: Config,
    *,
    assets_dir: Optional[Path] = None,
    keep_temp: bool = False,
) -> PipelineResult:
    """수정한 SRT로 자막을 다시 구워 완성 영상·숏츠를 재생성한다.

    오타 수정 워크플로: 먼저 edit으로 만든 `<이름>_clean.mp4` 와 수정한
    `<이름>.srt` 를 받아, 무음컷/음성인식 없이 빠르게 다시 만든다.
    """
    ensure_ffmpeg()
    clean_video = clean_video.resolve()
    if not clean_video.exists():
        raise FileNotFoundError(f"clean 영상을 찾을 수 없습니다: {clean_video}")
    if not Path(srt).exists():
        raise FileNotFoundError(f"자막(SRT) 파일을 찾을 수 없습니다: {srt}")

    output_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = (assets_dir or (Path.cwd() / "assets")).resolve()
    stem = clean_video.stem
    if stem.endswith("_clean"):
        stem = stem[: -len("_clean")]
    result = PipelineResult(clean_video=clean_video)

    work_dir = Path(tempfile.mkdtemp(prefix="autoedit_reburn_"))
    logger.info("작업 폴더: %s", work_dir)
    try:
        captions = parse_srt(Path(srt))
        logger.info("수정된 자막 %d개로 다시 굽기", len(captions))
        result.srt = Path(srt)
        result.steps.append("자막 재반영")
        _finish(
            clean_video, captions, stem, output_dir, work_dir, config, assets_dir, result
        )
        return result
    finally:
        if keep_temp:
            logger.info("임시 폴더 보존: %s", work_dir)
        else:
            shutil.rmtree(work_dir, ignore_errors=True)
