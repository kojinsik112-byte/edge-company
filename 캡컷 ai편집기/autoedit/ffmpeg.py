"""ffmpeg / ffprobe 호출을 감싸는 얇은 래퍼.

라이브러리 의존성을 줄이기 위해 영상 처리는 전부 시스템 ffmpeg에 위임한다.
ffprobe가 없는 환경(정적 ffmpeg 단독 설치 등)을 대비해 길이 측정은 대체 경로를 둔다.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

from .utils import logger


class FFmpegError(RuntimeError):
    """ffmpeg/ffprobe 실행 실패."""


# 화면 프로그램(스튜디오)이 인코딩 진행 시간을 받아 갈 수 있는 콜백. fn(처리한 초)
PROGRESS_HOOK = None
_TIME_RE = re.compile(r"time=(\d+):(\d+):(\d+(?:\.\d+)?)")


def _run_with_hook(args: List[str]) -> subprocess.CompletedProcess:
    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    tail: List[str] = []
    buf = b""
    assert proc.stderr is not None
    while True:
        chunk = proc.stderr.read(512)
        if not chunk:
            break
        buf += chunk
        parts = re.split(rb"[\r\n]", buf)
        buf = parts.pop()
        for raw in parts:
            line = raw.decode("utf-8", "replace")
            if not line.strip():
                continue
            tail = (tail + [line])[-15:]
            m = _TIME_RE.search(line)
            if m and PROGRESS_HOOK:
                h, mi, sec = m.groups()
                try:
                    PROGRESS_HOOK(int(h) * 3600 + int(mi) * 60 + float(sec))
                except Exception:  # noqa: BLE001
                    pass
    code = proc.wait()
    if code != 0:
        raise FFmpegError(f"명령 실패 ({args[0]}, code={code}):\n" + "\n".join(tail))
    return subprocess.CompletedProcess(args, code)


def _which(name: str) -> Optional[str]:
    return shutil.which(name)


def _try_bundled_ffmpeg() -> bool:
    """시스템 ffmpeg가 없을 때 imageio-ffmpeg에 동봉된 바이너리를 PATH에 끼워 넣는다.

    imageio-ffmpeg는 OS에 맞는 ffmpeg 정적 바이너리를 자동으로 내려받아 제공한다.
    바이너리 이름이 `ffmpeg`가 아니므로(예: ffmpeg-win64-...exe) 'ffmpeg'(.exe)라는
    이름으로 캐시 폴더에 복사한 뒤 그 폴더를 PATH 맨 앞에 추가한다.
    이렇게 하면 사용자가 ffmpeg를 따로 설치하지 않아도 동작한다.
    """
    try:
        import imageio_ffmpeg  # type: ignore

        src = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:  # noqa: BLE001
        return False
    if not src or not os.path.exists(src):
        return False

    cache = Path(tempfile.gettempdir()) / "autoedit_bin"
    cache.mkdir(exist_ok=True)
    dst = cache / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
    try:
        if not dst.exists():
            shutil.copy2(src, dst)
            if os.name != "nt":
                os.chmod(dst, 0o755)
    except Exception:  # noqa: BLE001
        # 복사가 안 되면 원본 폴더라도 PATH에 추가 시도
        cache = Path(src).parent
    os.environ["PATH"] = str(cache) + os.pathsep + os.environ.get("PATH", "")
    return _which("ffmpeg") is not None


def ensure_ffmpeg() -> None:
    """ffmpeg 실행 파일을 확보한다. 시스템 → 동봉(imageio-ffmpeg) 순으로 찾는다."""
    if _which("ffmpeg") is not None:
        return
    if _try_bundled_ffmpeg():
        logger.info("동봉된 ffmpeg(imageio-ffmpeg)를 사용합니다.")
        return
    raise FFmpegError(
        "ffmpeg 를 찾을 수 없습니다. 아래 중 하나로 해결하세요.\n"
        "  · 가장 쉬움:  pip install imageio-ffmpeg   (ffmpeg 자동 동봉)\n"
        "  · macOS:      brew install ffmpeg\n"
        "  · Ubuntu:     sudo apt install ffmpeg\n"
        "  · Windows:    https://www.gyan.dev/ffmpeg/builds/ 에서 받아 PATH 등록"
    )


def run(
    args: List[str], *, quiet: bool = True, show_progress: bool = False
) -> subprocess.CompletedProcess:
    """ffmpeg/ffprobe 명령을 실행한다.

    show_progress=True 면 ffmpeg 출력을 그대로 콘솔에 흘려보내 진행률(frame/time/speed)이
    실시간으로 보이게 한다. 인코딩처럼 오래 걸리는 단계에서 '멈춘 듯' 보이는 문제를 막는다.
    그 외에는 출력을 캡처해 실패 시 마지막 로그를 예외에 담는다.
    """
    logger.debug("실행: %s", " ".join(args))
    if show_progress and PROGRESS_HOOK is not None:
        return _run_with_hook(args)
    if show_progress:
        display = args
        if args and Path(args[0]).name.startswith("ffmpeg"):
            display = [args[0], "-hide_banner", *args[1:]]
        proc = subprocess.run(display)
        if proc.returncode != 0:
            raise FFmpegError(
                f"명령 실패 ({args[0]}, code={proc.returncode}). 위 로그를 확인하세요."
            )
        return proc

    proc = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        tail = "\n".join(proc.stderr.strip().splitlines()[-15:])
        raise FFmpegError(f"명령 실패 ({args[0]}, code={proc.returncode}):\n{tail}")
    if not quiet and proc.stderr:
        logger.debug(proc.stderr)
    return proc


def probe_duration(path: Path) -> float:
    """미디어 길이(초)를 구한다. ffprobe 우선, 없으면 ffmpeg 파싱으로 대체."""
    ffprobe = _which("ffprobe")
    if ffprobe:
        proc = run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "json",
                str(path),
            ]
        )
        try:
            return float(json.loads(proc.stdout)["format"]["duration"])
        except (KeyError, ValueError, json.JSONDecodeError):
            pass  # 일부 컨테이너는 format.duration이 비어 있다 → 대체 경로로

    # ffprobe가 없으면: 먼저 파일 머리(헤더)의 Duration 을 읽는다 (즉시 끝남).
    m = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", _header(path))
    if m:
        h, mi, sec = m.groups()
        return int(h) * 3600 + int(mi) * 60 + float(sec)

    # 헤더에 길이가 없는 드문 경우에만 전체를 훑어 time= 파싱 (느림)
    proc = subprocess.run(
        ["ffmpeg", "-i", str(path), "-f", "null", "-"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace",
    )
    times = re.findall(r"time=(\d+):(\d+):(\d+\.\d+)", proc.stderr)
    if times:
        h, m, s = times[-1]
        return int(h) * 3600 + int(m) * 60 + float(s)
    raise FFmpegError(f"미디어 길이를 측정할 수 없습니다: {path}")


def _header(path: Path) -> str:
    """ffmpeg -i 로 파일 정보만 읽는다 (영상 전체를 디코딩하지 않음 → 대용량도 즉시)."""
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace",
    )
    return proc.stderr or ""


def _rotated(info: str) -> bool:
    """폰 세로 촬영 영상(회전 정보 ±90°)인지."""
    m = re.search(r"rotation of (-?\d+(?:\.\d+)?) degrees", info) or re.search(r"rotate\s*:\s*(-?\d+)", info)
    return bool(m) and abs(round(float(m.group(1)))) % 180 == 90


def probe_dimensions(path: Path) -> Optional[tuple[int, int]]:
    """영상 해상도(width, height)를 구한다. 측정 불가 시 None."""
    ffprobe = _which("ffprobe")
    if ffprobe:
        proc = run(
            [
                ffprobe,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "json",
                str(path),
            ]
        )
        try:
            stream = json.loads(proc.stdout)["streams"][0]
            return int(stream["width"]), int(stream["height"])
        except (KeyError, IndexError, ValueError, json.JSONDecodeError):
            return None
    info = _header(path)
    # 영상 스트림 줄의 해상도만 (앨범아트·자막 스트림 제외)
    match = None
    for line in info.splitlines():
        if "Video:" in line and "attached pic" not in line:
            match = re.search(r"\b(\d{2,5})x(\d{2,5})\b", line)
            if match:
                break
    if match:
        w, h = int(match.group(1)), int(match.group(2))
        # 폰으로 세로 촬영한 영상은 가로로 저장되고 '회전' 표시만 붙어 있다 → 실제 보이는 크기로
        return (h, w) if _rotated(info) else (w, h)
    return None


def probe_fps(path: Path) -> Optional[int]:
    """영상 fps (정수로 반올림, 24~60). 못 읽으면 None."""
    for line in _header(path).splitlines():
        if "Video:" in line:
            m = re.search(r"(\d+(?:\.\d+)?) fps", line)
            if m:
                return max(24, min(60, round(float(m.group(1)))))
    return None


def has_audio(path: Path) -> bool:
    """영상에 오디오 트랙이 있는지 확인한다."""
    return "Audio:" in _header(path)


def extract_audio(video: Path, out_wav: Path, sample_rate: int = 16000) -> Path:
    """음성 인식용으로 16kHz 모노 WAV 오디오를 추출한다."""
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-vn",
            "-ac",
            "1",
            "-ar",
            str(sample_rate),
            "-c:a",
            "pcm_s16le",
            str(out_wav),
        ]
    )
    return out_wav
