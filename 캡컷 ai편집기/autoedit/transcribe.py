"""음성 인식(자막 텍스트) 생성.

faster-whisper로 오디오를 받아 적고, 자막 구간(segment) 목록과 SRT 파일을 만든다.
faster-whisper 미설치 시 명확한 안내와 함께 자막 단계만 건너뛴다.
"""

from __future__ import annotations

import re
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
    logger.info("Whisper 모델 로딩: %s (장치=%s)", cfg.model, cfg.device)
    # 기본은 CPU(int8). GPU(CUDA) 라이브러리가 없는 PC에서 cublas 오류가 나는 것을 방지.
    # cfg.device 가 "cuda" 인데 로딩이 안 되면 자동으로 CPU 로 떨어진다.
    try:
        compute = "int8" if cfg.device == "cpu" else "float16"
        return WhisperModel(cfg.model, device=cfg.device, compute_type=compute)
    except Exception as exc:  # noqa: BLE001
        if cfg.device != "cpu":
            logger.warning("GPU(%s) 로딩 실패 → CPU 로 전환합니다. (%s)", cfg.device, exc)
            return WhisperModel(cfg.model, device="cpu", compute_type="int8")
        raise


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

    # faster-whisper는 세그먼트를 하나씩 생성하므로, 진행률을 실시간으로 보여준다.
    # (이 단계가 가장 오래 걸려 '멈춘 듯' 보이던 문제를 해결)
    total = getattr(info, "duration", 0) or 0
    captions: List[Caption] = []
    last_pct = -10
    logger.info("음성 인식 시작... (영상 길이에 비례해 시간이 걸립니다)")
    for s in segments:
        text = s.text.strip()
        if text:
            captions.append(Caption(start=s.start, end=s.end, text=text))
        if total:
            pct = min(100, int(s.end / total * 100))
            if pct >= last_pct + 10:
                logger.info("자막 인식 중... %d%%", pct)
                last_pct = pct
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


_TS = re.compile(r"(\d+):(\d{2}):(\d{2})[,\.](\d{1,3})")


def _parse_timestamp(text: str) -> Optional[float]:
    """SRT 타임스탬프(HH:MM:SS,mmm)를 초로 변환한다. 형식이 아니면 None."""
    m = _TS.search(text)
    if not m:
        return None
    h, mm, ss, ms = m.groups()
    return int(h) * 3600 + int(mm) * 60 + int(ss) + int(ms.ljust(3, "0")) / 1000.0


def parse_srt(path: Path) -> List[Caption]:
    """SRT 파일을 읽어 자막 구간 목록으로 되돌린다.

    사용자가 메모장 등으로 오타를 직접 고친 SRT 를 다시 불러올 때 쓴다.
    빈 줄로 구분된 블록 단위로 파싱하며, 번호 줄과 타임코드 줄을 제외한
    나머지를 한 줄(공백으로 연결)로 합친다. 시간/형식이 어긋난 블록은 건너뛴다.
    """
    raw = Path(path).read_text(encoding="utf-8-sig")
    captions: List[Caption] = []
    for block in re.split(r"\r?\n\s*\r?\n", raw.strip()):
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        # 타임코드 줄 찾기 ("--> " 포함). 보통 첫째(번호) 다음 줄.
        ts_idx = next((i for i, ln in enumerate(lines) if "-->" in ln), None)
        if ts_idx is None:
            continue
        left, _, right = lines[ts_idx].partition("-->")
        start, end = _parse_timestamp(left), _parse_timestamp(right)
        if start is None or end is None or end <= start:
            continue
        text = " ".join(lines[ts_idx + 1:]).strip()
        if text:
            captions.append(Caption(start=start, end=end, text=text))
    return captions


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
