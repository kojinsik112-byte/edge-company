"""자막 번인(burn-in).

자막을 영상 해상도에 맞춘 ASS 파일로 만들어 구워 넣는다.
ASS에 PlayResX/Y(영상 크기)를 명시하므로 글자 크기·여백이 픽셀 단위로
예측 가능하게 적용된다(가로 영상·세로 숏츠 모두 일관). 줄바꿈은 libass가
영상 폭에 맞춰 자동 처리한다.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from .config import OutputConfig, SubtitleConfig
from .ffmpeg import probe_dimensions, run
from .transcribe import Caption


def _ass_time(seconds: float) -> str:
    """초 → ASS 시간 형식(H:MM:SS.cc, 1/100초)."""
    if seconds < 0:
        seconds = 0.0
    cs = int(round(seconds * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def _ass_text(text: str) -> str:
    """ASS Dialogue 텍스트로 안전하게 변환한다."""
    return (
        text.replace("\\", "\\\\")
        .replace("{", "(")
        .replace("}", ")")
        .replace("\r\n", " ")
        .replace("\n", " ")
        .strip()
    )


def write_ass(
    captions: List[Caption],
    out_path: Path,
    *,
    width: int,
    height: int,
    font: str,
    font_size: int,
    primary_color: str,
    outline_color: str,
    outline: int,
    margin_v: int,
) -> Path:
    """자막 구간을 영상 해상도에 맞춘 ASS 파일로 저장한다."""
    margin_lr = max(20, int(width * 0.06))
    shadow = 1
    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        "WrapStyle: 0\n"
        "ScaledBorderAndShadow: yes\n"
        f"PlayResX: {width}\n"
        f"PlayResY: {height}\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, "
        "Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
        "MarginR, MarginV, Encoding\n"
        f"Style: Default,{font},{font_size},{primary_color},{outline_color},"
        f"&H80000000,1,0,0,0,100,100,0,0,1,{outline},{shadow},2,"
        f"{margin_lr},{margin_lr},{margin_v},1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, "
        "Effect, Text\n"
    )
    lines = [header]
    for cap in captions:
        text = _ass_text(cap.text)
        if not text:
            continue
        lines.append(
            f"Dialogue: 0,{_ass_time(cap.start)},{_ass_time(cap.end)},"
            f"Default,,0,0,,{text}\n"
        )
    out_path.write_text("".join(lines), encoding="utf-8")
    return out_path


def _escape_filter_path(path: Path) -> str:
    """subtitles 필터에 넣을 경로를 이스케이프한다 (':' 와 '\\')."""
    return str(path).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def burn_subtitles(
    video: Path,
    captions: List[Caption],
    out_path: Path,
    sub_cfg: SubtitleConfig,
    out_cfg: OutputConfig,
    work_dir: Path,
    *,
    width: int,
    height: int,
    font_size: Optional[int] = None,
    margin_v: Optional[int] = None,
) -> Path:
    """영상에 자막을 구워 넣어 새 파일로 저장한다."""
    # ASS PlayRes를 실제 영상 해상도에 맞추면 글자 크기/여백이 픽셀 단위로 정확하다.
    real = probe_dimensions(video)
    if real:
        width, height = real
    ass = write_ass(
        captions,
        work_dir / f"{out_path.stem}.ass",
        width=width,
        height=height,
        font=sub_cfg.font,
        font_size=font_size if font_size is not None else sub_cfg.font_size,
        primary_color=sub_cfg.primary_color,
        outline_color=sub_cfg.outline_color,
        outline=sub_cfg.outline,
        margin_v=margin_v if margin_v is not None else sub_cfg.margin_v,
    )
    vf = f"subtitles='{_escape_filter_path(ass)}'"
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
