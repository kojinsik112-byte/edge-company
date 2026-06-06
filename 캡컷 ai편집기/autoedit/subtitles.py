"""자막 번인(burn-in) — 자막을 ASS로 만들어 영상 위에 구워 넣는다.

핵심: 자막 크기를 "실제 픽셀" 단위로 정확히 통제하려면, 자막 스크립트의
PlayResX/PlayResY 를 영상 해상도와 똑같이 맞춘 ASS 파일을 직접 만들어야 한다.
(SRT + force_style 방식은 libass 기본 캔버스(288)를 기준으로 폰트를 영상 높이만큼
확대해버려서, 같은 Fontsize 라도 영상이 클수록 글자가 거대해진다 — 자막이 화면을
덮는 문제의 원인.)
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from .config import OutputConfig, SubtitleConfig
from .ffmpeg import probe_dimensions, run
from .transcribe import Caption, _wrap


def _escape_path(path: Path) -> str:
    """subtitles 필터에 넣을 경로를 이스케이프한다 (특히 ':' 와 '\\')."""
    p = str(path).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    return p


def _ass_timestamp(seconds: float) -> str:
    """초를 ASS 타임코드(H:MM:SS.cs, cs=1/100초)로 변환한다."""
    if seconds < 0:
        seconds = 0.0
    cs = int(round(seconds * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def _ass_text(text: str, max_chars: int) -> str:
    """대사 텍스트를 ASS 용으로 안전하게 만든다 (줄바꿈 \\N, 태그 문자 제거)."""
    wrapped = _wrap(text, max_chars)
    safe = wrapped.replace("\\", "").replace("{", "(").replace("}", ")")
    return safe.replace("\n", "\\N")


def build_ass(
    captions: List[Caption],
    out_path: Path,
    *,
    dims: tuple[int, int],
    font: str,
    font_size: int,
    primary_color: str,
    outline_color: str,
    outline: int,
    margin_v: int,
    max_line_chars: int,
    background_box: bool = False,
    box_color: str = "&H80000000",
    box_pad: int = 12,
    alignment: int = 2,
) -> Path:
    """자막 구간을 ASS 파일로 만든다.

    PlayResX/PlayResY 를 영상 해상도(dims)로 고정하므로 Fontsize/Outline/MarginV 가
    모두 실제 픽셀이 된다. background_box=True 면 글자 뒤에 반투명 박스(BorderStyle=3)를
    깐다 (libass 는 BorderStyle=3 박스 색으로 OutlineColour 를 쓰므로 거기에 박스색을 넣고
    Outline 값을 박스 여백으로 쓴다).
    """
    w, h = dims
    if background_box:
        border_style, out_col, out_val = 3, box_color, box_pad
    else:
        border_style, out_col, out_val = 1, outline_color, outline

    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        "WrapStyle: 2\n"
        "ScaledBorderAndShadow: yes\n"
        f"PlayResX: {w}\n"
        f"PlayResY: {h}\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV\n"
        f"Style: Default,{font},{font_size},{primary_color},{out_col},"
        f"{border_style},{out_val},0,{alignment},40,40,{margin_v}\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, "
        "Effect, Text\n"
    )
    lines = [header]
    for cap in captions:
        lines.append(
            f"Dialogue: 0,{_ass_timestamp(cap.start)},{_ass_timestamp(cap.end)},"
            f"Default,,0,0,0,,{_ass_text(cap.text, max_line_chars)}\n"
        )
    out_path.write_text("".join(lines), encoding="utf-8")
    return out_path


def burn_subtitles(
    video: Path,
    captions: List[Caption],
    out_path: Path,
    sub_cfg: SubtitleConfig,
    out_cfg: OutputConfig,
    *,
    font_size: int | None = None,
    margin_v: int | None = None,
    video_size: tuple[int, int] | None = None,
    background_box: bool | None = None,
    max_line_chars: int | None = None,
) -> Path:
    """자막 구간을 ASS로 만들어 영상에 구워 넣는다.

    PlayRes 를 영상 해상도에 맞추므로 폰트 크기가 정확히 픽셀 단위로 적용된다.
    """
    dims = video_size or probe_dimensions(video) or (out_cfg.width, out_cfg.height)
    ass_path = out_path.parent / f"{out_path.stem}_sub.ass"
    build_ass(
        captions,
        ass_path,
        dims=dims,
        font=sub_cfg.font,
        font_size=font_size if font_size is not None else sub_cfg.font_size,
        primary_color=sub_cfg.primary_color,
        outline_color=sub_cfg.outline_color,
        outline=sub_cfg.outline,
        margin_v=margin_v if margin_v is not None else sub_cfg.margin_v,
        max_line_chars=(
            max_line_chars if max_line_chars is not None else sub_cfg.max_line_chars
        ),
        background_box=(
            background_box if background_box is not None else sub_cfg.background_box
        ),
        box_color=sub_cfg.box_color,
        box_pad=sub_cfg.box_pad,
    )
    vf = f"subtitles='{_escape_path(ass_path)}'"
    try:
        run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(video),
                "-vf",
                vf,
                "-c:v",
                out_cfg.video_codec,
                "-crf",
                str(out_cfg.crf),
                "-preset",
                out_cfg.preset,
                "-c:a",
                "copy",
                str(out_path),
            ],
            show_progress=True,
        )
    finally:
        ass_path.unlink(missing_ok=True)
    return out_path
