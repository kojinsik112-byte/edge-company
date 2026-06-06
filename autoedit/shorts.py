"""숏츠 자동 생성.

자막(말소리 밀도)을 근거로 하이라이트 구간을 고르고, 세로형(9:16)으로 잘라
짧은 숏츠 클립을 만든다. 자막이 없으면 영상을 균등 분할하는 방식으로 대체한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

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
) -> Path:
    """하이라이트 구간을 9:16 세로 클립으로 렌더링한다."""
    # 1) 구간을 잘라 세로 비율로 cover-crop (가운데 정렬)
    raw = work_dir / f"short_{index}_raw.mp4"
    vf = (
        f"scale={cfg.width}:{cfg.height}:force_original_aspect_ratio=increase,"
        f"crop={cfg.width}:{cfg.height}"
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
            str(out_cfg.crf),
            "-preset",
            out_cfg.preset,
            "-c:a",
            "aac",
            "-b:a",
            out_cfg.audio_bitrate,
            str(raw),
        ]
    )

    # 2) 자막 굽기 (있고, 켜져 있으면)
    if cfg.burn_subtitles and captions:
        clip_caps = slice_captions(captions, highlight.start, highlight.end)
        if clip_caps:
            srt = write_srt(
                clip_caps, work_dir / f"short_{index}.srt", sub_cfg.max_line_chars
            )
            burn_subtitles(
                raw,
                srt,
                out_path,
                sub_cfg,
                out_cfg,
                font_size=cfg.font_size,
                margin_v=cfg.margin_v,
            )
            raw.unlink(missing_ok=True)
            return out_path

    raw.replace(out_path)
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
            video, h, out_path, cfg, out_cfg, captions, sub_cfg, work_dir, i
        )
        results.append(out_path)
    return results
