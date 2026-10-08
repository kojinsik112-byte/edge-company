"""장면 따라가기 — 가로 영상을 세로(9:16) 숏츠로 자를 때 얼굴을 따라 자르는 위치를 옮긴다.

OpenCV 얼굴 인식(정면·옆얼굴)으로 0.25초마다 얼굴 가로 위치를 찾고, 1초 단위로 부드럽게
이어 ffmpeg crop 의 x 위치(시간 함수)로 만든다. 얼굴이 안 보이면 마지막 위치를 유지,
처음부터 안 보이면 가운데. 흔들림 없이 천천히 따라가도록 이동 속도를 제한한다.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

from .utils import logger


def _detectors():
    import cv2  # type: ignore

    base = Path(cv2.data.haarcascades)
    front = cv2.CascadeClassifier(str(base / "haarcascade_frontalface_default.xml"))
    prof = cv2.CascadeClassifier(str(base / "haarcascade_profileface.xml"))
    return cv2, front, prof


def face_track(video: Path, start: float, end: float, step: float = 0.25) -> List[Tuple[float, Optional[float]]]:
    """[(구간 기준 시각, 얼굴 중심 x 비율 0~1 또는 None)]"""
    try:
        cv2, front, prof = _detectors()
    except Exception as exc:  # noqa: BLE001
        logger.info("얼굴 인식 불가(OpenCV 없음) → 가운데로 자름: %s", exc)
        return []
    import subprocess

    import numpy as np

    from .ffmpeg import probe_dimensions

    dims = probe_dimensions(video)
    if not dims:
        return []
    W, H = 480, int(round(480 * dims[1] / dims[0] / 2)) * 2
    # ffmpeg 가 작게 줄인 흑백 프레임을 4장/초로 한 번에 흘려 준다 (한 장씩 찾아가는 것보다 수십 배 빠름)
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{start:.3f}", "-t", f"{end - start:.3f}",
         "-i", str(video), "-vf", f"fps={1 / step:.3f},scale={W}:{H},format=gray", "-f", "rawvideo", "-"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    buf = proc.stdout
    n = len(buf) // (W * H)
    out: List[Tuple[float, Optional[float]]] = []
    for k in range(n):
        gray = cv2.equalizeHist(np.frombuffer(buf, np.uint8, W * H, k * W * H).reshape(H, W))
        small = gray
        t = start + k * step
        min_size = (int(small.shape[0] * 0.12),) * 2
        faces = list(front.detectMultiScale(gray, 1.15, 5, minSize=min_size))
        if not faces:
            faces = list(prof.detectMultiScale(gray, 1.15, 5, minSize=min_size))
            if not faces:  # 반대쪽 옆얼굴
                flipped = cv2.flip(gray, 1)
                faces = [(small.shape[1] - x - fw, y, fw, fh) for x, y, fw, fh in prof.detectMultiScale(flipped, 1.15, 5, minSize=min_size)]
        if faces:
            x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])  # 가장 큰 얼굴
            out.append((t - start, float((x + fw / 2) / small.shape[1])))
        else:
            out.append((t - start, None))
    return out


def crop_x_expr(
    samples: List[Tuple[float, Optional[float]]], src_w: int, crop_w: int, max_speed: float = 0.25
) -> Optional[str]:
    """얼굴 위치 → crop x(t) 식. 얼굴을 한 번도 못 찾으면 None(가운데)."""
    found = [c for _, c in samples if c is not None]
    if not found:
        return None
    # 빈 곳 채우기 (직전 위치 유지, 맨 앞은 첫 발견 위치)
    pos, last = [], found[0]
    for t, c in samples:
        last = c if c is not None else last
        pos.append((t, last))
    # 1초 단위로 평균 → 너무 잦은 흔들림 제거
    keys: List[Tuple[float, float]] = []
    sec = 0.0
    while pos and sec <= pos[-1][0] + 1e-6:
        win = [c for t, c in pos if sec - 0.5 <= t < sec + 0.5]
        if win:
            keys.append((sec, sum(win) / len(win)))
        sec += 1.0
    # 이동 속도 제한 (초당 화면 폭의 max_speed 이하) → 카메라맨이 천천히 따라가는 느낌
    smooth = [keys[0]]
    for t, c in keys[1:]:
        pt, pc = smooth[-1]
        d = max(-max_speed, min(max_speed, c - pc))
        smooth.append((t, pc + d))
    xs = [(t, min(max(c * src_w - crop_w / 2, 0), src_w - crop_w)) for t, c in smooth]
    if len(xs) == 1 or max(x for _, x in xs) - min(x for _, x in xs) < 4:
        return f"{xs[0][1]:.1f}"
    # 구간별 직선 보간 식: if(lt(t,t1), x0+(x1-x0)*(t-t0)/(t1-t0), if(...))
    expr = f"{xs[-1][1]:.1f}"
    for (t0, x0), (t1, x1) in reversed(list(zip(xs, xs[1:]))):
        seg = f"{x0:.1f}+({x1 - x0:.1f})*(t-{t0:.2f})/{t1 - t0:.2f}"
        expr = f"if(lt(t,{t1:.2f}),{seg},{expr})"
    return expr
