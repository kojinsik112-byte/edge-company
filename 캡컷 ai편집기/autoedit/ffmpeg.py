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


def run(args: List[str], *, quiet: bool = True) -> subprocess.CompletedProcess:
    """ffmpeg/ffprobe 명령을 실행한다. 실패 시 stderr를 담아 예외를 던진다."""
    logger.debug("실행: %s", " ".join(args))
    proc = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
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

    # ffprobe가 없거나 길이를 못 읽은 경우: ffmpeg를 null 출력으로 돌려 time= 파싱
    proc = subprocess.run(
        ["ffmpeg", "-i", str(path), "-f", "null", "-"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    times = re.findall(r"time=(\d+):(\d+):(\d+\.\d+)", proc.stderr)
    if times:
        h, m, s = times[-1]
        return int(h) * 3600 + int(m) * 60 + float(s)
    raise FFmpegError(f"미디어 길이를 측정할 수 없습니다: {path}")


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
    proc = subprocess.run(
        ["ffmpeg", "-i", str(path), "-f", "null", "-"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    match = re.search(r"(\d{2,5})x(\d{2,5})", proc.stderr)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None


def has_audio(path: Path) -> bool:
    """영상에 오디오 트랙이 있는지 확인한다."""
    proc = subprocess.run(
        ["ffmpeg", "-i", str(path), "-f", "null", "-"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return "Audio:" in proc.stderr


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
