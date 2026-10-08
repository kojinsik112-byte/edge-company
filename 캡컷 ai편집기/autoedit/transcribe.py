"""음성 인식(자막 텍스트) 생성.

faster-whisper로 오디오를 받아 적고, 자막 구간(segment) 목록과 SRT 파일을 만든다.
faster-whisper 미설치 시 명확한 안내와 함께 자막 단계만 건너뛴다.
"""

from __future__ import annotations

import json
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .config import SubtitleConfig
from .ffmpeg import extract_audio
from .utils import fmt_timestamp, logger


class WhisperUnavailable(RuntimeError):
    """faster-whisper 가 설치되지 않음."""


@dataclass
class Word:
    start: float
    end: float
    text: str
    prob: float = 1.0  # 음성인식 확신도 (낮으면 오타 의심 → 편집 화면에서 빨간 표시)


@dataclass
class Caption:
    start: float
    end: float
    text: str                     # 줄바꿈("\n")은 화면에서도 그대로 줄이 바뀜
    words: Optional[List["Word"]] = None
    # ── 편집 화면에서 사람이 지정하는 값 (없으면 스타일 기본값) ──
    emph: Optional[Dict[int, str]] = None  # 단어 번호 → 강조 종류(color/big/marker/red)
    pos: Optional[str] = None     # bottom / middle / top
    align: Optional[str] = None   # left / center / right
    sfx: Optional[str] = None     # 효과음 이름 (첫 강조 단어 타이밍, 없으면 자막 시작에 재생)
    zoom: Optional[bool] = None   # 자동 줌인: None=자동(강조·효과음 있으면), True=켬, False=끔


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


def _hallucinated(seg, text: str, vocab: List[str]) -> bool:
    """음성인식이 '말하지 않은 말'을 지어낸 구간인지 판정한다.

    - 용어 사전 힌트를 그대로 되풀이 (예: 말이 없는데 "엣지컴퍼니 아크로 실링팬 주관사…")
    - 같은 말 무한 반복 (압축률이 비정상적으로 높음)
    - 말소리가 아닐 확률이 높고 확신도도 낮음 (음악·소음 구간)
    """
    tokens = [t.strip(".,!?…") for t in text.split()]
    if vocab and len(tokens) >= 3:
        in_vocab = sum(1 for t in tokens if any(t.startswith(v) for v in vocab))
        if in_vocab / len(tokens) >= 0.6:
            return True
    if getattr(seg, "compression_ratio", 0) > 2.4:
        return True
    # 말소리가 아닐 확률이 '매우' 높고 확신도도 매우 낮을 때만 (흐릿한 끝인사 같은 진짜 말은 살림)
    nsp = getattr(seg, "no_speech_prob", 0.0)
    lp = getattr(seg, "avg_logprob", 0.0)
    return nsp > 0.85 and lp < -1.1


def transcribe(
    video: Path, work_dir: Path, cfg: SubtitleConfig, *, want_words: bool = False
) -> List[Caption]:
    """영상에서 오디오를 추출해 자막 구간을 인식한다.

    want_words=True 면 단어별 타임스탬프도 수집한다(과감한 컷·동적 자막용).
    """
    need_words = want_words or cfg.dynamic
    model = _load_model(cfg)
    wav = extract_audio(video, work_dir / "asr.wav")
    segments, info = model.transcribe(
        str(wav),
        language=cfg.language,
        vad_filter=True,
        beam_size=5,
        word_timestamps=need_words,
        # 회사·제품 고유명사를 미리 알려주면 '아크로→아그로' 같은 오타가 크게 줄어든다.
        # (쉼표로 나열하면 Whisper가 자막에도 쉼표를 끼워 넣으므로 띄어쓰기로만 잇는다)
        initial_prompt=(" ".join(cfg.vocab) + " 이야기를 해 볼게요.") if cfg.vocab else None,
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
        if text and _hallucinated(s, text, cfg.vocab):
            logger.info("받아쓰기 환각 의심 → 제외: %s", text[:40])
            text = ""
        if text:
            words = None
            if need_words and getattr(s, "words", None):
                words = [
                    Word(
                        start=w.start,
                        end=w.end,
                        text=w.word.strip(),
                        prob=float(getattr(w, "probability", 1.0) or 1.0),
                    )
                    for w in s.words
                    if w.word.strip()
                ]
            captions.append(Caption(start=s.start, end=s.end, text=text, words=words))
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
    out_path.parent.mkdir(parents=True, exist_ok=True)
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


_SRT_TIME = re.compile(
    r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)"
)


def _srt_seconds(h: str, m: str, s: str, ms: str) -> float:
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def parse_srt(path: Path) -> List[Caption]:
    """사용자가 수정한 SRT 파일을 읽어 자막 구간 목록으로 되돌린다.

    오타 수정 워크플로(자막을 손본 뒤 다시 굽기)에서 사용한다.
    """
    content = Path(path).read_text(encoding="utf-8-sig")
    captions: List[Caption] = []
    for block in re.split(r"\n\s*\n", content.strip()):
        lines = [ln for ln in block.splitlines() if ln.strip() != ""]
        if not lines:
            continue
        # 첫 줄이 순번이면 건너뛰고, 시간 줄을 찾는다.
        time_idx = next(
            (i for i, ln in enumerate(lines) if _SRT_TIME.search(ln)), None
        )
        if time_idx is None:
            continue
        m = _SRT_TIME.search(lines[time_idx])
        start = _srt_seconds(m.group(1), m.group(2), m.group(3), m.group(4))
        end = _srt_seconds(m.group(5), m.group(6), m.group(7), m.group(8))
        text = " ".join(lines[time_idx + 1 :]).strip()
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
        # 자막 한 줄은 통째로 유지(편집한 글자·강조·위치가 그대로 살도록), 시간만 옮긴다.
        words = None
        if cap.words:
            words = [
                Word(
                    max(0.0, w.start - start),
                    max(0.0, min(end, w.end) - start),
                    w.text,
                    w.prob,
                )
                for w in cap.words
            ]
        out.append(
            Caption(
                start=max(0.0, cap.start - start),
                end=min(end, cap.end) - start,
                text=cap.text,
                words=words,
                emph=cap.emph,
                pos=cap.pos,
                align=cap.align,
                sfx=cap.sfx if cap.start >= start else None,
                zoom=cap.zoom,
            )
        )
    return out


def captions_to_json(captions: List[Caption], out_path: Path) -> Path:
    """자막을 단어 타이밍까지 포함해 JSON으로 저장한다 (자막 편집 화면용)."""
    data = captions_to_list(captions)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return out_path


def captions_to_list(captions: List[Caption]) -> list:
    return [
        {
            "start": round(c.start, 3),
            "end": round(c.end, 3),
            "text": c.text,
            "words": [
                {
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                    "text": w.text,
                    "prob": round(w.prob, 3),
                }
                for w in (c.words or [])
            ],
            "emph": {str(k): v for k, v in c.emph.items()} if c.emph is not None else None,
            "pos": c.pos,
            "align": c.align,
            "sfx": c.sfx,
            "zoom": c.zoom,
        }
        for c in captions
    ]


def captions_from_json(data) -> List[Caption]:
    """captions_to_json 형식(파일 경로 또는 리스트)을 자막 목록으로 되돌린다."""
    if isinstance(data, (str, Path)):
        data = json.loads(Path(data).read_text(encoding="utf-8"))
    out: List[Caption] = []
    for d in data:
        text = "\n".join(
            ln.strip() for ln in str(d.get("text", "")).splitlines() if ln.strip()
        )
        if not text:
            continue
        words = [
            Word(
                float(w["start"]),
                float(w["end"]),
                str(w["text"]),
                float(w.get("prob", 1.0)),
            )
            for w in d.get("words") or []
        ] or None
        emph = d.get("emph")
        if isinstance(emph, dict):
            emph = {int(k): str(v) for k, v in emph.items() if v}
        else:
            emph = None
        out.append(
            Caption(
                float(d["start"]),
                float(d["end"]),
                text,
                words,
                emph=emph,
                pos=d.get("pos") or None,
                align=d.get("align") or None,
                sfx=d.get("sfx") or None,
                zoom=d.get("zoom"),
            )
        )
    return out
