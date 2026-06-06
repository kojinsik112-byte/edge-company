"""썸네일 자동 생성.

영상에서 대표 프레임을 골라 1280x720으로 만들고, 큰 한글 문구를 얹는다.
클릭률(CTR)을 좌우하는 가장 중요한 요소다.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from .config import ThumbnailConfig
from .ffmpeg import run
from .subtitles import _ass_text, _escape_filter_path
from .transcribe import Caption
from .utils import logger

THUMB_W, THUMB_H = 1280, 720


def _pick_time(captions: Optional[List[Caption]], duration: float) -> float:
    """썸네일로 쓸 프레임 시각을 고른다 (말이 가장 알찬 구간 중심)."""
    if captions:
        best = max(captions, key=lambda c: len(c.text))
        return (best.start + best.end) / 2
    return max(0.0, duration * 0.3)


def _write_thumb_ass(text: str, out_path: Path, cfg: ThumbnailConfig) -> Path:
    """썸네일용 ASS(가운데 정렬, 큰 글씨)를 만든다."""
    body = _ass_text(text)
    margin_lr = int(THUMB_W * 0.06)
    header = (
        "[Script Info]\nScriptType: v4.00+\nWrapStyle: 0\n"
        "ScaledBorderAndShadow: yes\n"
        f"PlayResX: {THUMB_W}\nPlayResY: {THUMB_H}\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, "
        "Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
        "MarginR, MarginV, Encoding\n"
        f"Style: Default,{cfg.font},{cfg.font_size},{cfg.primary_color},"
        f"{cfg.outline_color},&H80000000,1,0,0,0,100,100,0,0,1,"
        f"{cfg.outline},2,5,{margin_lr},{margin_lr},0,1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, "
        "Effect, Text\n"
        f"Dialogue: 0,0:00:00.00,0:00:10.00,Default,,0,0,,{body}\n"
    )
    out_path.write_text(header, encoding="utf-8")
    return out_path


def make_thumbnail(
    video: Path,
    out_path: Path,
    work_dir: Path,
    captions: Optional[List[Caption]],
    cfg: ThumbnailConfig,
    duration: float,
    title: Optional[str] = None,
) -> Optional[Path]:
    """썸네일 이미지를 만들어 경로를 반환한다."""
    text = cfg.text or title
    if not text and captions:
        text = captions[0].text
    if not text:
        text = ""

    at = _pick_time(captions, duration)
    logger.info("썸네일 생성: %.1f초 지점 프레임 + 문구", at)

    # 1) 대표 프레임 추출 → 1280x720 cover-crop
    frame = work_dir / "thumb_frame.png"
    run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{at:.3f}",
            "-i",
            str(video),
            "-vf",
            f"scale={THUMB_W}:{THUMB_H}:force_original_aspect_ratio=increase,"
            f"crop={THUMB_W}:{THUMB_H}",
            "-frames:v",
            "1",
            str(frame),
        ]
    )

    # 2) 문구 얹기
    if text.strip():
        ass = _write_thumb_ass(text, work_dir / "thumb.ass", cfg)
        run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(frame),
                "-vf",
                f"subtitles='{_escape_filter_path(ass)}'",
                "-frames:v",
                "1",
                str(out_path),
            ]
        )
    else:
        frame.replace(out_path)
    return out_path
