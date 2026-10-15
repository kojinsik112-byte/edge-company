"""다운로드한 영상을 '캡컷 AI 편집기'(autoedit)로 넘기는 연결부.

- 윈도우: 캡컷 폴더의 편집하기.bat 를 새 창으로 실행 (드래그&드롭과 똑같은 흐름 —
  진행 로그·바탕화면 '캡컷_완성본' 저장·완료 후 폴더 열기까지 그대로).
- 그 외 OS: autoedit 를 직접 실행.

모드
  repurpose : 이미 편집된 유튜브 영상 → 컷 없이 자막·숏츠·썸네일·업로드정보만 (기본)
  full      : 촬영 원본처럼 무음컷·추임새·AI 스마트편집·브랜딩까지 전부
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAPCUT_DIR_NAME = "캡컷 ai편집기"
MODES = {
    "repurpose": "재가공 — 완성 영상에서 숏츠·자막·썸네일·업로드정보 뽑기 (추천)",
    "full": "풀 편집 — 촬영 원본처럼 무음·추임새까지 컷",
}


class CapcutNotReady(Exception):
    pass


def find_capcut_dir() -> Path | None:
    """EDGE_CAPCUT_DIR 환경변수 → 저장소 내 기본 위치 순으로 찾는다."""
    candidates = []
    if os.environ.get("EDGE_CAPCUT_DIR"):
        candidates.append(Path(os.environ["EDGE_CAPCUT_DIR"]))
    candidates.append(HERE.parent.parent / CAPCUT_DIR_NAME)  # edge-company/캡컷 ai편집기
    for c in candidates:
        if (c / "autoedit" / "cli.py").exists():
            return c.resolve()
    return None


def _venv_python(capcut: Path) -> Path | None:
    for rel in (".venv/Scripts/python.exe", ".venv/bin/python"):
        p = capcut / rel
        if p.exists():
            return p
    return None


def check_ready() -> Path:
    capcut = find_capcut_dir()
    if not capcut:
        raise CapcutNotReady(
            f"'{CAPCUT_DIR_NAME}' 폴더를 찾지 못했습니다.\n"
            "edge-company 폴더 구조 그대로 두거나, 환경변수 EDGE_CAPCUT_DIR 에 경로를 지정하세요.")
    if os.name == "nt" and not _venv_python(capcut):
        raise CapcutNotReady(
            f"캡컷 AI 편집기가 아직 설치되지 않았습니다.\n"
            f"'{capcut}' 폴더의 '설치.bat' 을 먼저 한 번 실행하세요.")
    return capcut


def build_command(video: Path, mode: str = "repurpose", capcut: Path | None = None,
                  out_dir: Path | None = None) -> tuple[list[str], Path]:
    """(실행 명령, 작업 폴더)를 돌려준다. 테스트·자동화용으로 분리."""
    if mode not in MODES:
        raise ValueError(f"mode 는 {list(MODES)} 중 하나")
    capcut = capcut or check_ready()
    video = Path(video).resolve()
    if os.name == "nt":
        bat = capcut / "편집하기.bat"
        # start 대신 call: 공백 있는 경로("캡컷 ai편집기")에서 따옴표가 깨지지 않는다
        cmd = ["cmd", "/c", "call", str(bat), str(video)]
        if mode == "repurpose":
            cmd.append("repurpose")
        return cmd, capcut

    py = _venv_python(capcut) or Path(sys.executable)
    out = out_dir or (Path.home() / "Desktop" / "캡컷_완성본" / video.stem)
    cmd = [str(py), "-m", "autoedit.cli", "edit", str(video), "-o", str(out), "-v"]
    if (capcut / "config.yaml").exists():
        cmd += ["-c", "config.yaml"]
    if mode == "repurpose":
        cmd.append("--repurpose")
    return cmd, capcut


def send_to_capcut(video: str | Path, mode: str = "repurpose", wait: bool = False,
                   out_dir: Path | None = None) -> subprocess.Popen | int:
    """편집을 시작한다. 윈도우는 새 콘솔 창에서 돌고 바로 반환된다."""
    if not Path(video).exists():
        raise FileNotFoundError(f"영상 파일이 없습니다: {video}")
    if str(video).lower().endswith((".mp3", ".m4a")):
        raise CapcutNotReady("음원(MP3)은 편집기로 보낼 수 없습니다. 영상 화질로 받아주세요.")
    cmd, cwd = build_command(Path(video), mode, out_dir=out_dir)
    # 창 모드(pythonw)에서도 진행 로그가 보이도록 새 콘솔 창으로 띄운다
    flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0) if os.name == "nt" else 0
    proc = subprocess.Popen(cmd, cwd=str(cwd), creationflags=flags)
    return proc.wait() if wait else proc
