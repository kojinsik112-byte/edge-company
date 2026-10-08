"""자막 효과음 (띠리링·뽁·딩·휙·두둥 …).

외부 음원을 쓰지 않고 프로그램이 직접 합성한다 → 저작권 걱정 없음, 설치 파일 불필요.
자막마다 고른 효과음을 '첫 강조 단어'(없으면 자막 시작) 타이밍에 깔아 준다.
효과음들을 하나의 트랙(WAV)으로 합친 뒤 ffmpeg 로 원래 음성과 한 번에 섞는다.
"""

from __future__ import annotations

import math
import tempfile
import wave
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from .transcribe import Caption

SR = 48000

# 이름 → (한글 이름, 설명)
SFX_LIST: Dict[str, Tuple[str, str]] = {
    "chime": ("띠리링", "올라가는 맑은 벨 — 핵심 포인트"),
    "ding": ("딩", "한 번 울리는 벨 — 정보·숫자"),
    "pop": ("뽁", "짧고 귀여운 팝 — 단어 강조"),
    "whoosh": ("휙", "바람 가르는 소리 — 장면 전환"),
    "boom": ("두둥", "묵직한 저음 — 반전·임팩트"),
    "sparkle": ("반짝", "반짝이는 소리 — 신제품·자랑"),
    "correct": ("딩동", "정답 소리 — 맞아요·추천"),
    "click": ("딸깍", "가벼운 클릭 — 목록·순서"),
    "notify": ("띵똥", "알림음 — 새 소식·꿀팁"),
    "rise": ("슝", "위로 솟는 소리 — 등장·상승"),
    "boing": ("띠용", "통통 튀는 소리 — 반전·웃음"),
    "coin": ("띠링(코인)", "동전 소리 — 가격·할인·이득"),
    "shutter": ("찰칵", "카메라 셔터 — 사진·비교 컷"),
    "drumroll": ("두구두구", "드럼롤 + 심벌 — 공개 직전"),
    "fail": ("빠밤", "아쉬운 소리 — 실패·불편 사례"),
    "tada": ("짜잔", "팡파레 화음 — 결과 공개·완성"),
    "bubble": ("뽀록", "물방울 — 귀여운 강조"),
    "laser": ("삐융", "레이저 — 빠른 전환"),
    "clap": ("박수", "짧은 박수 — 축하·마무리"),
}

# 사람이 효과음을 안 골랐을 때, 강조 종류별 자동 효과음
AUTO_BY_EMPH = {"big": "pop", "marker": "chime", "red": "boom"}


def _np():
    import numpy as np  # faster-whisper 설치 시 함께 설치됨

    return np


def _env(np, n: int, attack: float, decay: float):
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-t / max(decay, 1e-4))


def _bell(np, freq: float, dur: float, decay: float = 0.35):
    n = int(SR * dur)
    t = np.arange(n) / SR
    tone = (
        np.sin(2 * math.pi * freq * t)
        + 0.45 * np.sin(2 * math.pi * freq * 2.01 * t)
        + 0.2 * np.sin(2 * math.pi * freq * 3.02 * t) * np.exp(-t * 6)
    )
    return tone * _env(np, n, 0.004, decay)


def _place(np, out, sig, at: float):
    i = int(at * SR)
    j = min(len(out), i + len(sig))
    if i < len(out):
        out[i:j] += sig[: j - i]


def _synth(name: str):
    np = _np()
    rng = np.random.default_rng(7)
    if name == "chime":
        out = np.zeros(int(SR * 1.0))
        for k, f in enumerate([1046.5, 1318.5, 1568.0, 2093.0]):
            _place(np, out, _bell(np, f, 0.8, 0.28) * (0.9 - 0.12 * k), k * 0.065)
    elif name == "ding":
        out = _bell(np, 1318.5, 1.0, 0.45)
    elif name == "pop":
        n = int(SR * 0.12)
        t = np.arange(n) / SR
        f = 900 * np.exp(-t * 28) + 220
        out = np.sin(2 * math.pi * np.cumsum(f) / SR) * _env(np, n, 0.002, 0.035)
    elif name == "whoosh":
        n = int(SR * 0.45)
        noise = rng.standard_normal(n)
        # 간단한 저역통과(이동평균 폭을 바꿔 가며 '휙' 하고 지나가는 느낌)
        out = np.zeros(n)
        acc = 0.0
        for i in range(n):
            p = i / n
            alpha = 0.03 + 0.25 * math.sin(math.pi * p)
            acc += alpha * (noise[i] - acc)
            out[i] = acc
        out *= np.sin(np.pi * np.arange(n) / n) ** 2 * 2.2
    elif name == "boom":
        out = np.zeros(int(SR * 1.0))
        for at in (0.0, 0.22):
            n = int(SR * 0.6)
            t = np.arange(n) / SR
            f = 110 * np.exp(-t * 7) + 42
            hit = np.sin(2 * math.pi * np.cumsum(f) / SR) * _env(np, n, 0.003, 0.22)
            hit += 0.15 * rng.standard_normal(n) * _env(np, n, 0.001, 0.02)
            _place(np, out, hit, at)
    elif name == "sparkle":
        out = np.zeros(int(SR * 0.9))
        for k in range(9):
            f = float(rng.uniform(2400, 4200))
            _place(np, out, _bell(np, f, 0.35, 0.08) * 0.5, k * 0.055 + float(rng.uniform(0, 0.02)))
    elif name == "correct":
        out = np.zeros(int(SR * 0.9))
        _place(np, out, _bell(np, 880.0, 0.6, 0.25), 0.0)
        _place(np, out, _bell(np, 1318.5, 0.7, 0.3), 0.13)
    elif name == "click":
        n = int(SR * 0.05)
        t = np.arange(n) / SR
        out = (np.sin(2 * math.pi * 2200 * t) + 0.5 * rng.standard_normal(n)) * _env(np, n, 0.0005, 0.006)
    elif name == "notify":
        out = np.zeros(int(SR * 0.9))
        _place(np, out, _bell(np, 1567.98, 0.5, 0.18), 0.0)
        _place(np, out, _bell(np, 1174.66, 0.7, 0.3), 0.16)
    elif name == "rise":
        n = int(SR * 0.5)
        t = np.arange(n) / SR
        f = 300 * np.exp(t * 5.2)
        tone = np.sin(2 * math.pi * np.cumsum(f) / SR) * 0.6
        noise = rng.standard_normal(n) * 0.25
        out = (tone + noise * (t / t[-1])) * np.sin(np.pi * t / t[-1]) ** 1.5
    elif name == "boing":
        n = int(SR * 0.6)
        t = np.arange(n) / SR
        f = 220 + 160 * np.sin(2 * math.pi * 9 * t) * np.exp(-t * 4) + 120 * np.exp(-t * 8)
        out = np.sin(2 * math.pi * np.cumsum(f) / SR) * _env(np, n, 0.003, 0.22)
    elif name == "coin":
        out = np.zeros(int(SR * 0.6))
        for at, f, d in ((0.0, 987.77, 0.08), (0.08, 1318.51, 0.45)):
            n = int(SR * d)
            t = np.arange(n) / SR
            sq = np.sign(np.sin(2 * math.pi * f * t)) * 0.35 + np.sin(2 * math.pi * f * t) * 0.4
            _place(np, out, sq * _env(np, n, 0.002, d * 0.6), at)
    elif name == "shutter":
        out = np.zeros(int(SR * 0.25))
        for at, dec in ((0.0, 0.008), (0.07, 0.02)):
            n = int(SR * 0.06)
            hit = rng.standard_normal(n) * _env(np, n, 0.0005, dec)
            _place(np, out, hit, at)
    elif name == "drumroll":
        out = np.zeros(int(SR * 1.8))
        k = 0
        while k * 0.045 < 1.0:
            n = int(SR * 0.05)
            amp = 0.35 + 0.5 * (k * 0.045)
            _place(np, out, rng.standard_normal(n) * _env(np, n, 0.001, 0.012) * amp, k * 0.045)
            k += 1
        n = int(SR * 0.8)
        crash = rng.standard_normal(n)
        crash = np.diff(crash, prepend=0) * _env(np, n, 0.002, 0.25)  # 고음 위주 = 심벌 느낌
        _place(np, out, crash * 0.9, 1.0)
    elif name == "fail":
        out = np.zeros(int(SR * 1.5))
        for j, f in enumerate((392.0, 369.99, 349.23, 329.63)):
            dur = 0.6 if j == 3 else 0.28
            n = int(SR * dur)
            t = np.arange(n) / SR
            ff = f * (1 - 0.03 * t / dur) if j == 3 else np.full(n, f)
            ph = 2 * math.pi * np.cumsum(ff) / SR
            saw = sum(np.sin(ph * h) / h for h in range(1, 7))
            _place(np, out, saw * _env(np, n, 0.02, dur * 0.7) * 0.5, j * 0.3)
    elif name == "tada":
        out = np.zeros(int(SR * 1.3))
        for at, chord in ((0.0, (523.25, 659.25)), (0.12, (523.25, 659.25, 783.99, 1046.5))):
            dur = 0.12 if at == 0 else 1.1
            n = int(SR * dur)
            t = np.arange(n) / SR
            tone = sum(sum(np.sin(2 * math.pi * f * h * t) / h for h in range(1, 5)) for f in chord)
            _place(np, out, tone * _env(np, n, 0.008, dur * 0.5) * 0.3, at)
    elif name == "bubble":
        n = int(SR * 0.16)
        t = np.arange(n) / SR
        f = 350 + 900 * (t / t[-1]) ** 2
        out = np.sin(2 * math.pi * np.cumsum(f) / SR) * _env(np, n, 0.004, 0.05)
    elif name == "laser":
        n = int(SR * 0.3)
        t = np.arange(n) / SR
        f = 2200 * np.exp(-t * 9) + 180
        out = np.sign(np.sin(2 * math.pi * np.cumsum(f) / SR)) * 0.4 * _env(np, n, 0.002, 0.1)
    elif name == "clap":
        out = np.zeros(int(SR * 1.2))
        for k in range(14):
            n = int(SR * 0.04)
            hit = np.diff(rng.standard_normal(n), prepend=0) * _env(np, n, 0.0008, 0.01)
            _place(np, out, hit * float(rng.uniform(0.5, 1.0)), k * 0.07 + float(rng.uniform(0, 0.02)))
    else:
        raise KeyError(name)
    # 효과음끼리 체감 크기를 맞춘다: 평균 세기(RMS) 0.22 목표, 단 최고점은 0.9 넘지 않게
    peak = float(np.max(np.abs(out))) or 1.0
    rms = float(np.sqrt(np.mean(out ** 2))) or 1.0
    return out * min(0.9 / peak, 0.22 / rms)


def _write_wav(path: Path, samples) -> Path:
    np = _np()
    data = (np.clip(samples, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    return path


def sample_path(name: str) -> Path:
    """미리듣기용 효과음 WAV (임시 폴더에 한 번 만들어 재사용)."""
    d = Path(tempfile.gettempdir()) / "autoedit_sfx"
    d.mkdir(exist_ok=True)
    p = d / f"{name}.wav"
    if not p.exists():
        _write_wav(p, _synth(name))
    return p


def _cue_time(cap: Caption) -> float:
    """효과음 타이밍 = 첫 강조 단어(크게/형광펜/빨강 우선) 시작, 없으면 자막 시작."""
    from .styles import words_for

    words = words_for(cap)
    emph = cap.emph or {}
    for kinds in (("big", "marker", "red"), ("color",)):
        idx = sorted(i for i, k in emph.items() if k in kinds and i < len(words))
        if idx:
            return words[idx[0]].start
    return cap.start


def plan_cues(captions: List[Caption], auto: bool = False) -> List[Tuple[float, str]]:
    """(재생 시각, 효과음 이름) 목록. auto=True 면 강조 종류에 맞춰 자동 배치."""
    cues: List[Tuple[float, str]] = []
    for cap in captions:
        name = cap.sfx
        if not name and auto and cap.emph:
            for kind in ("marker", "big", "red"):
                if kind in cap.emph.values():
                    name = AUTO_BY_EMPH[kind]
                    break
        if name and name in SFX_LIST:
            cues.append((_cue_time(cap), name))
    # 너무 붙어 있으면(0.6초 이내) 시끄러우니 뒤의 것을 뺀다
    cues.sort()
    out: List[Tuple[float, str]] = []
    for t, n in cues:
        if not out or t - out[-1][0] >= 0.6:
            out.append((t, n))
    return out


def apply_sfx(
    video: Path,
    captions: List[Caption],
    out_path: Path,
    work_dir: Path,
    *,
    volume: float = 0.5,
    auto: bool = False,
    run: Optional[Callable] = None,
) -> Path:
    """효과음을 영상 음성에 섞는다. 효과음이 하나도 없으면 원본 경로를 그대로 돌려준다."""
    from .ffmpeg import probe_duration, run as ff_run
    from .utils import logger

    cues = plan_cues(captions, auto)
    if not cues:
        return video
    np = _np()
    dur = probe_duration(video)
    track = np.zeros(int(SR * (dur + 1.5)))
    cache: Dict[str, object] = {}
    for t, name in cues:
        if name not in cache:
            cache[name] = _synth(name)
        _place(np, track, cache[name], max(0.0, t - 0.02))
    wav = _write_wav(work_dir / f"{out_path.stem}_sfx.wav", track * volume)
    logger.info("효과음 %d개 삽입", len(cues))
    (run or ff_run)(
        [
            "ffmpeg", "-y", "-i", str(video), "-i", str(wav),
            "-filter_complex",
            "[0:a][1:a]amix=inputs=2:duration=first:normalize=0[a]",
            "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            str(out_path),
        ]
    )
    return out_path
