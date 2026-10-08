"""숏츠 자동 생성.

자막(말소리 밀도)을 근거로 하이라이트 구간을 고르고, 세로형(9:16)으로 잘라
짧은 숏츠 클립을 만든다. 자막이 없으면 영상을 균등 분할하는 방식으로 대체한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set

from .config import OutputConfig, ShortsConfig, SubtitleConfig
from .ffmpeg import probe_duration, run
from .subtitles import burn_subtitles
from .transcribe import Caption, slice_captions, write_srt
from .utils import fmt_duration, logger


@dataclass
class Highlight:
    start: float
    end: float
    score: float

    @property
    def duration(self) -> float:
        return self.end - self.start


def _score_windows(captions: List[Caption], cfg: ShortsConfig) -> List[Highlight]:
    """자막을 슬라이딩하며 길이 조건을 만족하는 후보 구간을 점수화한다."""
    highlights: List[Highlight] = []
    n = len(captions)
    for i in range(n):
        start = captions[i].start
        chars = 0
        for j in range(i, n):
            end = captions[j].end
            chars += len(captions[j].text)
            dur = end - start
            if dur < cfg.min_duration:
                continue
            if dur > cfg.max_duration:
                break
            # 점수 = 말소리 밀도(초당 글자수). 알찬 구간일수록 높다.
            highlights.append(Highlight(start, end, chars / max(dur, 1e-3)))
    return highlights


def _select_non_overlapping(
    highlights: List[Highlight], count: int
) -> List[Highlight]:
    """점수 높은 순으로, 서로 겹치지 않게 greedy 선택."""
    chosen: List[Highlight] = []
    for h in sorted(highlights, key=lambda x: x.score, reverse=True):
        if all(h.end <= c.start or h.start >= c.end for c in chosen):
            chosen.append(h)
        if len(chosen) >= count:
            break
    return sorted(chosen, key=lambda x: x.start)


def pick_highlights(
    video: Path, captions: Optional[List[Caption]], cfg: ShortsConfig
) -> List[Highlight]:
    """하이라이트 구간을 고른다. 자막이 없으면 균등 분할로 대체."""
    if captions:
        windows = _score_windows(captions, cfg)
        chosen = _select_non_overlapping(windows, cfg.count)
        if chosen:
            return chosen
        logger.warning("자막 기반 하이라이트를 못 찾아 균등 분할로 대체합니다.")

    total = probe_duration(video)
    target = min(cfg.max_duration, max(cfg.min_duration, (cfg.min_duration + cfg.max_duration) / 2))
    n = max(1, min(cfg.count, int(total // target)))
    if n == 0:
        return []
    step = total / n
    out = []
    for k in range(n):
        start = k * step
        end = min(total, start + target)
        if end - start >= cfg.min_duration * 0.5:
            out.append(Highlight(start, end, 0.0))
    return out


def render_short(
    video: Path,
    highlight: Highlight,
    out_path: Path,
    cfg: ShortsConfig,
    out_cfg: OutputConfig,
    captions: Optional[List[Caption]],
    sub_cfg: SubtitleConfig,
    work_dir: Path,
    index: int,
    keywords: Optional[Set[str]] = None,
    overlays: Optional[List[dict]] = None,
) -> Path:
    """하이라이트 구간을 9:16 세로 클립으로 렌더링한다."""
    # 1) 구간을 잘라 세로 비율로 cover-crop (가운데 정렬)
    raw = work_dir / f"short_{index}_raw.mp4"
    # 원본에서 9:16 만큼 먼저 잘라낸 뒤 고품질(lanczos) 확대 → 덜 뭉개짐
    vf = (
        f"crop='min(iw,ih*{cfg.width}/{cfg.height})':'min(ih,iw*{cfg.height}/{cfg.width})',"
        f"scale={cfg.width}:{cfg.height}:flags=lanczos,setsar=1"
    )
    # 가로 영상이면 얼굴을 따라 자르는 위치를 옮긴다 (장면 따라가기)
    from .ffmpeg import probe_dimensions

    dims = probe_dimensions(video)
    mode = getattr(cfg, "frame", "auto")
    if dims and dims[0] > dims[1] and mode == "auto":
        # 세로로 자르면 몇 배 늘려야 하는지: 1080p 가로 영상은 1.8배 → 뭉개짐 → '전체+흐린 배경'
        upscale = cfg.height / dims[1]
        mode = "fit" if upscale > 1.4 else "track"
    if dims and dims[0] > dims[1] and mode == "fit":
        # 전체 화면을 가운데에 선명하게 + 위아래는 같은 영상을 흐리게 깐 배경 (늘리지 않아서 선명)
        logger.info("숏츠 %d: 전체 화면 + 흐린 배경 (원본 해상도가 낮아 확대 대신)", index)
        vf = (
            f"split[a][b];"
            f"[a]scale={cfg.width}:{cfg.height}:force_original_aspect_ratio=increase,"
            f"crop={cfg.width}:{cfg.height},boxblur=24:2,eq=brightness=-0.06[bg];"
            f"[b]scale={cfg.width}:-2:flags=lanczos[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1"
        )
    elif getattr(cfg, "track", True) and dims and dims[0] > dims[1]:
        from .track import crop_x_expr, face_track

        sw, sh = dims
        cw = int(sh * cfg.width / cfg.height) // 2 * 2
        xexpr = crop_x_expr(face_track(video, highlight.start, highlight.end), sw, cw)
        if xexpr:
            logger.info("숏츠 %d: 얼굴 따라가기 적용", index)
            vf = (
                f"crop={cw}:{sh}:x='{xexpr}':y=0,"
                f"scale={cfg.width}:{cfg.height}:flags=lanczos,unsharp=5:5:0.6,setsar=1"
            )
    run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{highlight.start:.3f}",
            "-to",
            f"{highlight.end:.3f}",
            "-i",
            str(video),
            "-vf",
            vf,
            "-r",
            str(out_cfg.fps),
            "-c:v",
            out_cfg.video_codec,
            "-crf",
            str(out_cfg.inter_crf if (cfg.burn_subtitles and captions) else out_cfg.crf),
            "-preset",
            out_cfg.inter_preset if (cfg.burn_subtitles and captions) else out_cfg.preset,
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            out_cfg.audio_bitrate,
            str(raw),
        ],
        show_progress=True,
    )

    # 2) 자막 굽기 (있고, 켜져 있으면) — 세로 해상도에 맞춰 크게
    if cfg.burn_subtitles and captions:
        clip_caps = slice_captions(captions, highlight.start, highlight.end)
        if clip_caps:
            burn_subtitles(
                raw,
                clip_caps,
                out_path,
                sub_cfg,
                out_cfg,
                work_dir,
                width=cfg.width,
                height=cfg.height,
                font_size=cfg.font_size,
                margin_v=cfg.margin_v,
                keywords=keywords,
            )
            raw.unlink(missing_ok=True)
            _finish_short(out_path, clip_caps, sub_cfg, out_cfg, work_dir, overlays, highlight)
            return out_path

    raw.replace(out_path)
    _finish_short(
        out_path,
        slice_captions(captions, highlight.start, highlight.end) if captions else [],
        sub_cfg, out_cfg, work_dir, overlays, highlight,
    )
    return out_path


def make_shorts(
    video: Path,
    out_dir: Path,
    work_dir: Path,
    captions: Optional[List[Caption]],
    cfg: ShortsConfig,
    out_cfg: OutputConfig,
    sub_cfg: SubtitleConfig,
    stem: str,
    keywords: Optional[Set[str]] = None,
    overlays: Optional[List[dict]] = None,
) -> List[Path]:
    """숏츠 여러 개를 만들어 경로 목록을 반환한다."""
    highlights = pick_highlights(video, captions, cfg)
    if not highlights:
        logger.warning("숏츠로 만들 구간이 없습니다.")
        return []

    out_dir.mkdir(parents=True, exist_ok=True)
    results: List[Path] = []
    for i, h in enumerate(highlights, start=1):
        logger.info(
            "숏츠 %d/%d 생성: %s ~ %s (%s)",
            i,
            len(highlights),
            fmt_duration(h.start),
            fmt_duration(h.end),
            fmt_duration(h.duration),
        )
        out_path = out_dir / f"{stem}_short{i}.mp4"
        render_short(
            video, h, out_path, cfg, out_cfg, captions, sub_cfg, work_dir, i, keywords, overlays
        )
        results.append(out_path)
    return results


def _finish_short(
    clip: Path,
    caps: List[Caption],
    sub_cfg: SubtitleConfig,
    out_cfg: OutputConfig,
    work_dir: Path,
    overlays: Optional[List[dict]],
    highlight: "Highlight",
) -> None:
    """숏츠에도 같은 로고·효과음을 넣는다 (제자리 교체)."""
    from .overlays import apply_overlays, sfx_cues, shift, valid
    from .sfx import apply_sfx

    ovs = shift(valid(overlays), highlight.start, highlight.end)
    if ovs:
        tmp = work_dir / f"{clip.stem}_ov.mp4"
        if apply_overlays(clip, ovs, tmp, out_cfg) != clip:
            tmp.replace(clip)
    tmp = work_dir / f"{clip.stem}_sfx.mp4"
    out = apply_sfx(
        clip, caps, tmp, work_dir, volume=sub_cfg.sfx_volume, auto=sub_cfg.auto_sfx,
        extra=sfx_cues(ovs),
    )
    if out != clip:
        out.replace(clip)
