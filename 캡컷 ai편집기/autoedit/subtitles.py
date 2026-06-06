"""자막 번인(burn-in) — SRT를 영상 위에 구워 넣는다."""

from __future__ import annotations

from pathlib import Path

from .config import OutputConfig, SubtitleConfig
from .ffmpeg import run


def _escape_path(path: Path) -> str:
    """subtitles 필터에 넣을 경로를 이스케이프한다 (특히 ':' 와 '\\')."""
    p = str(path).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    return p


def build_force_style(
    font: str,
    font_size: int,
    primary_color: str,
    outline_color: str,
    outline: int,
    margin_v: int,
) -> str:
    """ASS force_style 문자열을 만든다."""
    return (
        f"FontName={font},Fontsize={font_size},"
        f"PrimaryColour={primary_color},OutlineColour={outline_color},"
        f"BorderStyle=1,Outline={outline},Shadow=0,Alignment=2,"
        f"MarginV={margin_v}"
    )


def burn_subtitles(
    video: Path,
    srt: Path,
    out_path: Path,
    sub_cfg: SubtitleConfig,
    out_cfg: OutputConfig,
    *,
    font_size: int | None = None,
    margin_v: int | None = None,
) -> Path:
    """영상에 자막을 구워 넣어 새 파일로 저장한다."""
    style = build_force_style(
        font=sub_cfg.font,
        font_size=font_size if font_size is not None else sub_cfg.font_size,
        primary_color=sub_cfg.primary_color,
        outline_color=sub_cfg.outline_color,
        outline=sub_cfg.outline,
        margin_v=margin_v if margin_v is not None else sub_cfg.margin_v,
    )
    vf = f"subtitles='{_escape_path(srt)}':force_style='{style}'"
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
    return out_path
