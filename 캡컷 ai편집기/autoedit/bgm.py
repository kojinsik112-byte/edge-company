"""배경음악 — 분위기별로 프로그램이 직접 만드는 반복 음악 (저작권 걱정 없음).

assets/bgm/ 폴더에 직접 고른 mp3/wav 를 넣으면 그 파일도 목록에 함께 뜬다
(파일 이름 앞에 분위기를 붙이면 AI 자동 연출이 골라 쓴다: 예 '밝은_봄노래.mp3').
"""

from __future__ import annotations

import math
import tempfile
import wave
from pathlib import Path
from typing import Dict, List, Tuple

SR = 44100

# 이름 → (한글, 설명)
MOODS: Dict[str, Tuple[str, str]] = {
    "bright": ("밝은", "경쾌한 어쿠스틱 팝 — 제품 홍보·소개"),
    "calm": ("잔잔한", "부드러운 피아노 패드 — 정보·설명·인터뷰"),
    "energetic": ("신나는", "빠른 비트 — 예능·이벤트·숏츠"),
    "lux": ("고급스러운", "느리고 깊은 무드 — 인테리어·조명·프리미엄"),
    "event": ("축제", "박수 섞인 밝은 리듬 — 박람회·행사 안내"),
}

_NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def _hz(name: str, octave: int) -> float:
    n = _NOTE[name[0]] + (1 if "#" in name else 0) + 12 * (octave + 1)
    return 440.0 * 2 ** ((n - 69) / 12)


def _chord(root: str, kind: str, octave: int = 3) -> List[float]:
    r = _hz(root, octave)
    steps = {"maj": (0, 4, 7, 12), "min": (0, 3, 7, 12), "maj7": (0, 4, 7, 11), "min7": (0, 3, 7, 10),
             "min9": (0, 3, 7, 10, 14)}[kind]
    return [r * 2 ** (s / 12) for s in steps]


# 분위기별: (bpm, 코드 진행, 드럼, 아르페지오)
_SPEC = {
    "bright": (100, [("C", "maj"), ("G", "maj"), ("A", "min"), ("F", "maj")], "soft", "8th"),
    "calm": (78, [("F", "maj7"), ("E", "min7"), ("D", "min7"), ("C", "maj7")], None, "4th"),
    "energetic": (122, [("A", "min"), ("F", "maj"), ("C", "maj"), ("G", "maj")], "four", "16th"),
    "lux": (68, [("A", "min9"), ("F", "maj7"), ("D", "min9"), ("E", "min7")], "sub", "sparse"),
    "event": (110, [("D", "maj"), ("A", "maj"), ("B", "min"), ("G", "maj")], "clap", "8th"),
}


def _synth(mood: str):
    import numpy as np

    bpm, prog, drums, arp = _SPEC[mood]
    beat = 60.0 / bpm
    bar = beat * 4
    bars = 8
    n = int(SR * bar * bars)
    t_all = np.arange(n) / SR
    out = np.zeros(n)
    rng = np.random.default_rng(3)

    def env(m, a, r):
        tt = np.arange(m) / SR
        e = np.minimum(1.0, tt / max(a, 1e-4))
        rel = np.clip((m / SR - tt) / max(r, 1e-4), 0, 1)
        return e * rel

    def place(sig, at):
        i = int(at * SR)
        j = min(n, i + len(sig))
        if i < n:
            out[i:j] += sig[: j - i]

    for b in range(bars):
        root, kind = prog[b % len(prog)]
        freqs = _chord(root, kind)
        start = b * bar
        m = int(SR * bar)
        tt = np.arange(m) / SR
        # 패드: 부드러운 화음 (배음 적게 = 따뜻한 소리)
        pad = sum(np.sin(2 * math.pi * f * tt) + 0.25 * np.sin(2 * math.pi * f * 2 * tt) for f in freqs)
        pad *= env(m, bar * 0.35, bar * 0.3) * (0.05 if mood != "calm" else 0.07)
        place(pad, start)
        # 베이스
        bf = _hz(root, 2)
        if mood in ("energetic", "bright", "event"):
            step = beat / 2
            for k in range(8):
                mm = int(SR * step * 0.9)
                t2 = np.arange(mm) / SR
                place(np.sin(2 * math.pi * bf * t2) * env(mm, 0.005, 0.06) * 0.16, start + k * step)
        else:
            place(np.sin(2 * math.pi * bf * tt) * env(m, 0.3, 0.5) * 0.12, start)
        # 아르페지오 (벨/피아노 느낌)
        notes = [f * 2 for f in freqs]
        if arp:
            step = {"4th": beat, "8th": beat / 2, "16th": beat / 4, "sparse": beat * 2}[arp]
            count = int(round(bar / step))
            for k in range(count):
                if arp == "sparse" and rng.random() < 0.3:
                    continue
                f = notes[k % len(notes)] if arp != "16th" else notes[(k * 2) % len(notes)]
                mm = int(SR * min(1.2, step * 2.5))
                t2 = np.arange(mm) / SR
                tone = (np.sin(2 * math.pi * f * t2) + 0.3 * np.sin(2 * math.pi * f * 3 * t2) * np.exp(-t2 * 8))
                tone *= np.exp(-t2 * (3.5 if arp != "sparse" else 1.6)) * np.minimum(1, t2 / 0.004)
                place(tone * (0.06 if arp != "16th" else 0.04), start + k * step)
        # 드럼
        if drums:
            for k in range(4):
                at = start + k * beat
                if drums in ("four", "clap", "soft") and (drums == "four" or k % 2 == 0 or drums == "clap"):
                    mm = int(SR * 0.25)
                    t2 = np.arange(mm) / SR
                    kick = np.sin(2 * math.pi * (50 + 90 * np.exp(-t2 * 30)) * t2) * np.exp(-t2 * 14)
                    place(kick * (0.22 if drums != "soft" else 0.14), at)
                if drums in ("four", "clap") and k % 2 == 1:
                    mm = int(SR * 0.12)
                    snap = np.diff(rng.standard_normal(mm), prepend=0) * np.exp(-np.arange(mm) / SR * 30)
                    place(snap * (0.09 if drums == "four" else 0.12), at)
                if drums in ("soft", "four", "clap"):
                    for h in (0, 0.5):
                        mm = int(SR * 0.04)
                        hat = np.diff(rng.standard_normal(mm), prepend=0) * np.exp(-np.arange(mm) / SR * 90)
                        place(hat * 0.03, at + h * beat)
                if drums == "sub" and k == 0:
                    mm = int(SR * bar)
                    t2 = np.arange(mm) / SR
                    place(np.sin(2 * math.pi * _hz(root, 1) * t2) * env(mm, 0.2, 0.8) * 0.12, start)
    # 살짝 넓게(스테레오), 음량 맞춤
    peak = float(np.max(np.abs(out))) or 1.0
    out = out / peak * 0.8
    d = int(SR * 0.012)
    right = np.concatenate([np.zeros(d), out[:-d]])
    return np.stack([out, right * 0.92 + out * 0.08], axis=1)


def _cache_dir() -> Path:
    d = Path(tempfile.gettempdir()) / "autoedit_bgm"
    d.mkdir(exist_ok=True)
    return d


def mood_path(mood: str) -> Path:
    """분위기 음악 WAV (한 번 만들어 재사용, 약 20초 반복용)."""
    import numpy as np

    p = _cache_dir() / f"{mood}.wav"
    if not p.exists():
        data = (np.clip(_synth(mood), -1, 1) * 32767).astype("<i2")
        with wave.open(str(p), "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(data.tobytes())
    return p


def user_tracks(assets_dir: Path) -> List[Path]:
    d = assets_dir / "bgm"
    if not d.exists():
        return []
    return sorted(p for p in d.iterdir() if p.suffix.lower() in (".mp3", ".wav", ".m4a", ".ogg"))


def resolve(choice: str, assets_dir: Path) -> Path | None:
    """'mood:bright' / 'file:이름.mp3' / '' → 실제 파일."""
    if not choice:
        return None
    if choice.startswith("mood:") and choice[5:] in MOODS:
        return mood_path(choice[5:])
    if choice.startswith("file:"):
        p = assets_dir / "bgm" / Path(choice[5:]).name
        return p if p.exists() else None
    return None
