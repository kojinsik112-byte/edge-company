"""음성 인식(자막 텍스트) 생성.

faster-whisper로 오디오를 받아 적고, 자막 구간(segment) 목록과 SRT 파일을 만든다.
faster-whisper 미설치 시 명확한 안내와 함께 자막 단계만 건너뛴다.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .config import SubtitleConfig
from .ffmpeg import extract_audio
from .utils import fmt_timestamp, logger


class WhisperUnavailable(RuntimeError):
    """faster-whisper 가 설치되지 않음."""


@dataclass
class Caption:
    start: float
    end: float
    text: str


def _load_model(cfg: SubtitleConfig):
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise WhisperUnavailable(
            "자막 생성을 위해 faster-whisper 가 필요합니다:\n"
            "  pip install faster-whisper\n"
            f"(원인: {exc})"
        ) from exc
    logger.info("Whisper 모델 로딩: %s", cfg.model)
    # CPU 환경에서도 합리적으로 동작하도록 int8 양자화 사용.
    return WhisperModel(cfg.model, device="auto", compute_type="int8")


def transcribe(video: Path, work_dir: Path, cfg: SubtitleConfig) -> List[Caption]:
    """영상에서 오디오를 추출해 자막 구간을 인식한다."""
    model = _load_model(cfg)
    wav = extract_audio(video, work_dir / "asr.wav")
    segments, info = model.transcribe(
        str(wav),
        language=cfg.language,
        vad_filter=True,
        beam_size=5,
    )
    logger.info("음성 인식 언어: %s", getattr(info, "language", cfg.language))
    captions = [
        Caption(start=s.start, end=s.end, text=s.text.strip())
        for s in segments
        if s.text.strip()
    ]
    logger.info("자막 구간 %d개 생성", len(captions))
    return captions


def _wrap(text: str, max_chars: int) -> str:
    """한 줄이 너무 길면 줄바꿈한다 (SRT는 \\n 으로 줄 구분)."""
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    return "\n".join(textwrap.wrap(text, width=max_chars)) or text


def write_srt(captions: List[Caption], out_path: Path, max_chars: int = 0) -> Path:
    """자막 구간을 SRT 파일로 저장한다."""
    lines = []
    for i, cap in enumerate(captions, start=1):
        lines.append(str(i))
        lines.append(
            f"{fmt_timestamp(cap.start)} --> {fmt_timestamp(cap.end)}"
        )
        lines.append(_wrap(cap.text, max_chars))
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def slice_captions(
    captions: List[Caption], start: float, end: float
) -> List[Caption]:
    """[start, end] 구간과 겹치는 자막만 추려 0 기준으로 시간을 재정렬한다."""
    out: List[Caption] = []
    for cap in captions:
        if cap.end <= start or cap.start >= end:
            continue
        out.append(
            Caption(
                start=max(0.0, cap.start - start),
                end=min(end, cap.end) - start,
                text=cap.text,
            )
        )
    return out
