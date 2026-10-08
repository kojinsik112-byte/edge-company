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
from typing import List, Optional, Set

from .audio import enhance_audio
from .branding import apply_branding
from .config import Config
from .fillers import find_filler_ranges, remap_captions
from .ffmpeg import ensure_ffmpeg, probe_dimensions, probe_duration, probe_fps
from .metadata import write_metadata
from .silence import cut_silence, render_cut
from .subtitles import burn_subtitles
from .thumbnail import make_thumbnail
from .transcribe import (
    Caption,
    WhisperUnavailable,
    captions_to_json,
    parse_srt,
    transcribe,
    write_srt,
)
from .shorts import make_shorts
from .utils import (
    Segment,
    fmt_duration,
    invert_intervals,
    logger,
    merge_intervals,
)


def _match_orientation(config: Config, video: Path) -> None:
    """세로로 찍은 영상이면 출력 규격(인트로/아웃트로 맞춤 등)도 세로로 바꾼다."""
    dims = probe_dimensions(video)
    out = config.output
    if dims and dims[1] > dims[0] and out.width > out.height:
        out.width, out.height = out.height, out.width
        logger.info("세로 영상 → 출력도 세로 %dx%d", out.width, out.height)
    # 원본 fps 유지 (60fps로 찍은 영상을 30fps로 깎지 않도록)
    fps = probe_fps(video)
    if fps:
        out.fps = fps


@dataclass
class PipelineResult:
    final_video: Optional[Path] = None
    srt: Optional[Path] = None
    clean_video: Optional[Path] = None
    thumbnail: Optional[Path] = None
    metadata_file: Optional[Path] = None
    shorts: List[Path] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)
    captions_json: Optional[Path] = None
    title: Optional[str] = None
    cut: Optional[dict] = None   # {"source", "keep", "total"} 컷 타임라인
    captions: Optional[List[Caption]] = None
    keywords: Set[str] = field(default_factory=set)


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


def _speech_only_cut(
    video: Path,
    captions: List[Caption],
    work_dir: Path,
    config: Config,
    extra_drop: Optional[set] = None,
) -> tuple[Path, List[Caption]]:
    """말하는 단어만 남기는 과감한 컷.

    제거 대상: ① 말 안 하는 구간(준비·응시·무음) ② 단어 사이의 뜸들임/멈춤
    ③ 추임새("어/아/음") ④ 같은 말 반복(재촬영 NG) ⑤ AI가 판단한 비문·잡담·의미중복.
    단어별 타임스탬프가 있으면 단어 단위로 잘라 문장 내부의 침묵까지 제거한다.
    """
    from .fillers import _shift, is_filler
    from .redundancy import find_duplicate_indices

    total = probe_duration(video)
    sil = config.silence

    dup = find_duplicate_indices(captions)
    if extra_drop:
        dup = dup | set(extra_drop)
    kept = [
        c
        for i, c in enumerate(captions)
        if i not in dup and not is_filler(c.text)
    ]
    if not kept:
        logger.warning("말하는 구간을 못 찾아 과감한 컷을 건너뜁니다.")
        return video, captions

    pad = sil.speech_pad
    # 단어 타임스탬프가 있으면 단어 단위로(문장 내부 침묵까지 컷), 없으면 문장 단위로.
    raw: List[tuple[float, float]] = []
    word_level = False
    for c in kept:
        if c.words:
            word_level = True
            for w in c.words:
                if is_filler(w.text):
                    continue
                raw.append((w.start, w.end))
        else:
            raw.append((c.start, c.end))

    padded = [(max(0.0, s - pad), min(total, e + pad)) for s, e in raw]
    # 시작 직전·끝(마지막 말 뒤 손 흔들기·인사 같은 '말 없는 동작')은 살린다
    if padded and sil.keep_head > 0:
        first = min(s for s, _ in padded)
        padded.append((max(0.0, first - sil.keep_head), first))
    if padded and sil.keep_tail > 0:
        last = max(e for _, e in padded)
        padded.append((last, min(total, last + sil.keep_tail)))
    keep_ranges = merge_intervals(padded, gap=sil.bridge_gap)
    segments = [Segment(s, e) for s, e in keep_ranges if e - s >= sil.min_keep]
    # 컷 타임라인(살리기)용: 원본 시간 기준 남긴 구간 기억
    _speech_only_cut.last_keep = [(round(x.start, 3), round(x.end, 3)) for x in segments]
    if not segments:
        return video, captions

    removed_ranges = invert_intervals([(s.start, s.end) for s in segments], total)
    kept_dur = sum(s.duration for s in segments)
    n_takes = len(captions) - len(kept)
    logger.info(
        "과감한 컷(%s): %d구간 유지, 추임새/반복 %d개 제거, 총 %s",
        "단어 단위" if word_level else "문장 단위",
        len(segments),
        n_takes,
        fmt_duration(kept_dur),
    )
    out = work_dir / "speechcut.mp4"
    render_cut(video, segments, out, config.output)

    from .transcribe import Word

    new_caps = []
    for c in kept:
        words = None
        if c.words:
            # 단어 타이밍도 새 타임라인으로 옮긴다 (움직이는 자막용). 추임새 단어는 뺀다.
            words = [
                Word(
                    _shift(w.start, removed_ranges),
                    _shift(w.end, removed_ranges),
                    w.text,
                    w.prob,
                )
                for w in c.words
                if not is_filler(w.text)
            ]
            text = " ".join(w.text for w in words) or c.text
        else:
            text = c.text
        new_caps.append(
            Caption(
                start=_shift(c.start, removed_ranges),
                end=_shift(c.end, removed_ranges),
                text=text,
                words=words or None,
            )
        )
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
    keywords: Optional[Set[str]] = None,
    overlays: Optional[List[dict]] = None,
) -> None:
    """자막 굽기 → 로고 → 효과음 → 숏츠 → 브랜딩. process/reburn 공통 마무리 단계."""
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
            keywords=keywords,
        )
        main = burned
        result.steps.append("자막 번인")

    # 효과음 (자막마다 고른 소리 / 강조 단어 자동)
    # 로고·스티커
    from .overlays import apply_overlays, sfx_cues, valid

    overlays = valid(overlays)
    if overlays:
        with_ov = apply_overlays(main, overlays, work_dir / "overlay.mp4", config.output)
        if with_ov != main:
            main = with_ov
            result.steps.append(f"로고 {len(overlays)}개")

    if captions or overlays:
        from .sfx import apply_sfx

        with_sfx = apply_sfx(
            main, captions or [], work_dir / "sfx.mp4", work_dir,
            volume=config.subtitle.sfx_volume, auto=config.subtitle.auto_sfx,
            extra=sfx_cues(overlays),
        )
        if with_sfx != main:
            main = with_sfx
            result.steps.append("효과음")

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
            keywords,
            overlays,
        )
        if result.shorts:
            result.steps.append(f"숏츠 {len(result.shorts)}개")
    else:
        logger.info("[3/4] 숏츠 건너뜀 (비활성화)")

    # 오프닝·엔딩 카드 → 브랜딩의 인트로/아웃트로 자리에 끼운다
    branding = config.branding
    cc = config.cards
    if cc.opening or cc.ending:
        from dataclasses import replace

        from .cards import CardInfo, make_card_video
        from .ffmpeg import probe_dimensions

        W, H = probe_dimensions(main) or (config.output.width, config.output.height)
        info = CardInfo(
            title=cc.title or (result.title or ""), subtitle=cc.subtitle, company=cc.company,
            phone=cc.phone, site=cc.site, message=cc.message, logo=cc.logo, qr=cc.qr, theme=cc.theme,
        )
        intro = make_card_video("opening", info, main, W, H, config.output.fps, cc.duration, work_dir) if cc.opening else None
        outro = make_card_video("ending", info, main, W, H, config.output.fps, cc.duration + 0.5, work_dir) if cc.ending else None
        branding = replace(
            branding, enabled=True,
            intro=str(intro) if intro else branding.intro,
            outro=str(outro) if outro else branding.outro,
        )
        result.steps.append("오프닝·엔딩 카드")

    # 브랜딩
    final_out = output_dir / f"{stem}_edited.mp4"
    if branding.enabled:
        logger.info("[4/4] 인트로/아웃트로/BGM")
        # 인트로/아웃트로를 붙일 때 본편 해상도 그대로 (2560x1440 영상을 1920x1080 으로 줄이지 않게)
        from dataclasses import replace as _replace
        from .ffmpeg import probe_dimensions as _dims

        md = _dims(main)
        out_for_brand = _replace(config.output, width=md[0], height=md[1]) if md else config.output
        apply_branding(
            main, final_out, work_dir, branding, out_for_brand, assets_dir
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
    review: bool = False,
) -> PipelineResult:
    """원본 영상 한 개를 받아 완성 영상과 숏츠를 만든다.

    review=True 면 컷 편집 + 자막 분석까지만 하고 멈춘다(자막 오타를 사람이 고친 뒤
    render_final 로 완성본을 만든다).
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
        _match_orientation(config, input_video)
        logger.info("입력 영상: %s (%s)", input_video.name, fmt_duration(dur))

        # ── 0) 오디오 음질 개선 ─────────────────────────────────────
        current = input_video
        if config.audio.enabled:
            current = enhance_audio(
                current, work_dir / "audio.mp4", config.audio, config.output
            )
            if current != input_video:
                result.steps.append("음질 개선")

        # ── 0-2) 화면 보정 (밝기·색 / 손떨림) ─────────────────────────
        if config.video.color or config.video.stabilize:
            from .enhance import enhance_video

            fixed = enhance_video(
                current, work_dir / "videofix.mp4", work_dir, config.output,
                color=config.video.color, stabilize=config.video.stabilize,
            )
            if fixed != current:
                current = fixed
                result.steps.append("화면 보정" + (" + 손떨림" if config.video.stabilize else ""))

        # ── 1·2) 음성 분석 → 과감한 컷 (말하는 구간만 남김) ─────────
        captions: Optional[List[Caption]] = None
        pre_cut: Optional[Path] = None
        cut_keep = None
        if config.subtitle.enabled:
            logger.info("[1/5] 음성 분석 (말하는 구간·추임새·반복 찾기)")
            try:
                captions = transcribe(
                    current,
                    work_dir,
                    config.subtitle,
                    want_words=config.silence.speech_only,
                )
            except WhisperUnavailable as exc:
                logger.warning("음성 분석 건너뜀: %s", exc)

        if captions and config.silence.enabled and config.silence.speech_only:
            # AI 스마트 편집: 자막 '내용'을 이해해 비문·잡담·의미중복까지 컷 대상 선정
            smart_drop: set = set()
            if config.smart_edit.enabled:
                from .smart_edit import SmartEditUnavailable, analyze

                try:
                    smart_drop = analyze(captions, config.smart_edit)
                    result.steps.append("AI 스마트편집")
                except SmartEditUnavailable as exc:
                    logger.info("AI 스마트 편집 건너뜀(휴리스틱 사용): %s", exc)

            # 말하는 구간만 남기고 무음·준비·응시·추임새·반복·잡담 전부 컷
            logger.info("[2/5] 과감한 컷 (무음/준비/응시/추임새/반복/잡담 제거)")
            pre_cut = current
            _speech_only_cut.last_keep = None
            current, captions = _speech_only_cut(
                current, captions, work_dir, config, extra_drop=smart_drop
            )
            cut_keep = _speech_only_cut.last_keep if current != pre_cut else None
            result.steps.append("과감한 컷")
        elif config.silence.enabled:
            # ASR가 없을 때(또는 speech_only 끔)는 dB 기반 무음 컷
            logger.info("[2/5] 무음 구간 자동 컷 (dB 방식)")
            current, _segments = cut_silence(
                current, work_dir / "cut.mp4", config.silence, config.output
            )
            if captions and config.subtitle.remove_fillers:
                current, captions = _remove_fillers(
                    current, captions, work_dir, config
                )

        if captions and config.silence.enabled:
            new_dur = probe_duration(current)
            logger.info(
                "✂️ 편집 결과: %s → %s (%.0f%% 단축)",
                fmt_duration(dur),
                fmt_duration(new_dur),
                (1 - new_dur / dur) * 100 if dur else 0,
            )

        # ── AI 오타 교정 + 핵심 단어 ───────────────────────────────
        keywords: Set[str] = set()
        if captions and config.subtitle.ai_typo_fix:
            from .smart_edit import SmartEditUnavailable
            from .typofix import fix_and_pick_keywords

            try:
                captions, keywords, nfix = fix_and_pick_keywords(
                    captions, config.subtitle.vocab, config.smart_edit
                )
                result.steps.append(f"AI 오타교정 {nfix}줄")
            except SmartEditUnavailable as exc:
                logger.info("AI 오타 교정 건너뜀: %s", exc)
        if captions:
            # 숫자·핵심 단어에 자동 강조 → 편집 화면에서 사람이 켜고 끌 수 있게 미리 표시
            from .styles import auto_emphasis

            auto_emphasis(captions, keywords)
        result.captions = captions
        result.keywords = keywords

        if captions:
            result.captions_json = captions_to_json(
                captions, output_dir / f"{stem}_자막.json"
            )
            (output_dir / f"{stem}_키워드.txt").write_text(
                "\n".join(sorted(keywords)), encoding="utf-8"
            )

        if captions:
            srt_out = output_dir / f"{stem}.srt"
            write_srt(captions, srt_out, config.subtitle.max_line_chars)
            result.srt = srt_out

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

        # 컷 타임라인: 컷 전 영상을 보관해 두면 편집 화면에서 잘린 구간을 '살리기' 할 수 있다
        src_out = output_dir / f"{stem}_source.mp4"
        if cut_keep and pre_cut is not None:
            shutil.copy2(pre_cut, src_out)
            result.cut = {"source": str(src_out), "keep": cut_keep, "total": probe_duration(src_out)}
        else:
            shutil.copy2(current, src_out)
            total = probe_duration(src_out)
            result.cut = {"source": str(src_out), "keep": [(0.0, round(total, 3))], "total": total}

        if review:
            logger.info("자막 검토 대기 — 오타를 고친 뒤 완성본을 만드세요.")
            return result

        # ── 3·4) 자막 굽기(선택) / 숏츠 / 브랜딩 ────────────────────
        _finish(
            current, captions, stem, output_dir, work_dir, config, assets_dir, result,
            keywords,
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


def render_final(
    clean_video: Path,
    captions: List[Caption],
    output_dir: Path,
    config: Config,
    *,
    keywords: Optional[Set[str]] = None,
    assets_dir: Optional[Path] = None,
    keep_temp: bool = False,
    overlays: Optional[List[dict]] = None,
) -> PipelineResult:
    """(사람이 검토·수정한) 자막으로 완성 영상·숏츠·썸네일을 만든다."""
    ensure_ffmpeg()
    clean_video = Path(clean_video).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = (assets_dir or (Path.cwd() / "assets")).resolve()
    stem = clean_video.stem
    if stem.endswith("_clean"):
        stem = stem[: -len("_clean")]
    result = PipelineResult(clean_video=clean_video, captions=captions)
    result.keywords = set(keywords or ())
    _match_orientation(config, clean_video)

    work_dir = Path(tempfile.mkdtemp(prefix="autoedit_render_"))
    try:
        # 속도 조절: 영상·소리 속도를 바꾸고 자막·로고 시간도 같은 비율로
        sp = float(getattr(config.output, "speed", 1.0) or 1.0)
        if abs(sp - 1.0) >= 0.01 and captions is not None:
            from .speed import change_speed, scale_captions, scale_overlays

            logger.info("속도 %.2f배 적용", sp)
            clean_video = change_speed(clean_video, sp, work_dir / "speed.mp4", config.output)
            captions = scale_captions(captions, sp)
            overlays = scale_overlays(overlays or [], sp)
            result.steps.append(f"속도 {sp:g}배")
        if captions:
            result.srt = write_srt(
                captions, output_dir / f"{stem}.srt", config.subtitle.max_line_chars
            )
            result.captions_json = captions_to_json(
                captions, output_dir / f"{stem}_자막.json"
            )
        title = None
        if captions and config.metadata.enabled:
            # 사람이 고친 자막 기준으로 제목·설명·해시태그를 다시 만든다
            meta_out = output_dir / f"{stem}_업로드정보.txt"
            _, meta = write_metadata(captions, meta_out, config.metadata)
            result.metadata_file = meta_out
            title = meta["titles"][0] if meta and meta.get("titles") else None
        result.title = title
        _finish(
            clean_video, captions, stem, output_dir, work_dir, config, assets_dir,
            result, keywords, overlays,
        )
        if config.thumbnail.enabled:
            logger.info("[5/5] 썸네일 생성")
            thumb_out = output_dir / f"{stem}_썸네일.png"
            try:
                make_thumbnail(
                    clean_video, thumb_out, work_dir, captions, config.thumbnail,
                    probe_duration(clean_video), title=title,
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
