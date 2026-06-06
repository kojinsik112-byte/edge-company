"""자막 번인(burn-in) — SRT를 영상 위에 구워 넣는다."""

from __future__ import annotations

from pathlib import Path

from .config import OutputConfig, SubtitleConfig
from .ffmpeg import probe_dimensions, run


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
    *,
    background_box: bool = False,
    box_color: str = "&H80000000",
    box_pad: int = 12,
) -> str:
    """ASS force_style 문자열을 만든다.

    여기서 Fontsize/Outline/MarginV 는 subtitles 필터의 original_size 와 같은
    좌표계(=실제 영상 픽셀)에서 해석된다. original_size 를 영상 해상도로 맞춰
    주므로, 이 값들은 사실상 "픽셀 단위"가 된다.

    background_box=True 면 글자 뒤에 반투명 박스(BorderStyle=3)를 깐다. libass 에서
    BorderStyle=3 의 박스 색은 OutlineColour 를 쓰므로, 박스 색을 거기에 넣고
    Outline 값을 박스 안쪽 여백으로 사용한다.
    """
    if background_box:
        border_style, out_col, out_val = 3, box_color, box_pad
    else:
        border_style, out_col, out_val = 1, outline_color, outline
    return (
        f"FontName={font},Fontsize={font_size},"
        f"PrimaryColour={primary_color},OutlineColour={out_col},"
        f"BorderStyle={border_style},Outline={out_val},Shadow=0,Alignment=2,"
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
    video_size: tuple[int, int] | None = None,
    background_box: bool | None = None,
) -> Path:
    """영상에 자막을 구워 넣어 새 파일로 저장한다.

    자막 크기(폰트/외곽선/여백)를 실제 픽셀 단위로 일관되게 만들기 위해
    subtitles 필터에 original_size(영상 해상도)를 함께 넘긴다. 이렇게 하지 않으면
    libass 기본 캔버스(높이 288)를 기준으로 폰트가 영상 높이만큼 확대되어,
    특히 세로 숏츠(1920)에서 자막이 과도하게 커지고 양옆이 짤리는 문제가 생긴다.
    """
    style = build_force_style(
        font=sub_cfg.font,
        font_size=font_size if font_size is not None else sub_cfg.font_size,
        primary_color=sub_cfg.primary_color,
        outline_color=sub_cfg.outline_color,
        outline=sub_cfg.outline,
        margin_v=margin_v if margin_v is not None else sub_cfg.margin_v,
        background_box=(
            background_box if background_box is not None else sub_cfg.background_box
        ),
        box_color=sub_cfg.box_color,
        box_pad=sub_cfg.box_pad,
    )
    # original_size 를 영상 해상도로 고정 → 위 스타일 값이 곧 픽셀 크기가 된다.
    dims = video_size or probe_dimensions(video)
    vf = f"subtitles='{_escape_path(srt)}'"
    if dims:
        vf += f":original_size={dims[0]}x{dims[1]}"
    vf += f":force_style='{style}'"
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
