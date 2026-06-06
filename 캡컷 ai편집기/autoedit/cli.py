"""autoedit 명령줄 인터페이스.

사용 예:
  autoedit edit 촬영본.mp4                 # 전체 자동 편집
  autoedit edit 촬영본.mp4 -o out --no-shorts
  autoedit edit 촬영본.mp4 -c config.yaml
  autoedit init-config                      # 설정 템플릿 생성
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .config import Config
from .ffmpeg import FFmpegError
from .pipeline import process, reburn
from .utils import logger, setup_logging

CONFIG_TEMPLATE = """\
# autoedit 설정 파일 — 필요한 값만 바꿔 쓰면 됩니다.
# (편집하기.bat 옆에 config.yaml 로 두면 자동 적용됩니다)

audio:
  enabled: true
  denoise: true        # 잡음 제거
  loudnorm: true       # 음량 정규화(유튜브 표준)

silence:
  enabled: true
  speech_only: true    # 말하는 구간만 남기고 나머지(준비/응시/무음) 전부 컷 (가장 과감)
  speech_pad: 0.15     # 말 앞뒤로 남길 여유(초). 작을수록 더 타이트하게 컷
  bridge_gap: 0.35     # 말 사이 이보다 짧은 틈은 유지(초). 작을수록 더 많이 컷
  # (아래는 speech_only: false 일 때만 쓰는 dB 방식)
  noise_db: -30.0
  min_silence: 0.4

subtitle:
  enabled: true        # 음성분석(추임새 제거·메타데이터). 끄려면 false (더 빠름)
  model: base          # tiny / base / small / medium / large-v3 (작을수록 빠름)
  device: cpu          # cpu(권장) 또는 cuda(NVIDIA GPU+CUDA 설치 시)
  language: ko
  burn_in: false       # 화면에 자막 글자 표시 (오타 우려로 기본 끔). 켜려면 true
  dynamic: false       # 단어가 칠해지는 동적 자막 (burn_in: true 일 때만)
  remove_fillers: true # "어/아/음" 추임새를 영상에서 잘라냄

shorts:
  enabled: true
  count: 3             # 만들 숏츠 개수
  min_duration: 20
  max_duration: 58
  burn_subtitles: false # 숏츠에 자막 글자 표시 (기본 끔)
  font_size: 64
  margin_v: 360

thumbnail:
  enabled: true
  text:                # 비워두면 자동 제목 사용
  font_size: 96

metadata:
  enabled: true        # 제목/설명/해시태그/챕터 자동 생성

branding:
  enabled: true
  intro: intro.mp4     # assets/ 폴더 기준 상대경로 (없으면 자동 건너뜀)
  outro: outro.mp4
  bgm: bgm.mp3
  bgm_volume: 0.12

output:
  width: 1920
  height: 1080
  fps: 30
  crf: 22              # 화질(낮을수록 고화질)
  preset: veryfast     # 인코딩 속도(veryfast=빠름, medium/slow=고화질)
"""


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autoedit",
        description="유튜브 영상 자동 편집기 — 무음 컷 / 자막 / 숏츠 / 브랜딩",
    )
    parser.add_argument("--version", action="version", version=f"autoedit {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    # edit
    p_edit = sub.add_parser("edit", help="영상 자동 편집 실행")
    p_edit.add_argument("input", type=Path, help="원본 영상 파일 경로")
    p_edit.add_argument("-o", "--output", type=Path, default=Path("output"), help="출력 폴더 (기본: output)")
    p_edit.add_argument("-c", "--config", type=Path, default=None, help="설정 YAML 경로")
    p_edit.add_argument("--assets", type=Path, default=None, help="인트로/아웃트로/BGM 자원 폴더 (기본: ./assets)")
    p_edit.add_argument("--no-silence", action="store_true", help="무음 컷 비활성화")
    p_edit.add_argument("--no-subtitles", action="store_true", help="자막 비활성화")
    p_edit.add_argument("--no-shorts", action="store_true", help="숏츠 비활성화")
    p_edit.add_argument("--no-branding", action="store_true", help="인트로/아웃트로/BGM 비활성화")
    p_edit.add_argument("--no-fillers", action="store_true", help="추임새 제거 비활성화")
    p_edit.add_argument("--shorts-count", type=int, default=None, help="숏츠 개수")
    p_edit.add_argument("--whisper-model", type=str, default=None, help="Whisper 모델 크기")
    p_edit.add_argument("--keep-temp", action="store_true", help="임시 작업 파일 보존")
    p_edit.add_argument("-v", "--verbose", action="store_true", help="상세 로그")

    # reburn — 수정한 자막(SRT)으로 다시 굽기
    p_reburn = sub.add_parser("reburn", help="수정한 자막으로 다시 굽기 (오타 수정용)")
    p_reburn.add_argument("clean_video", type=Path, help="<이름>_clean.mp4 경로")
    p_reburn.add_argument("srt", type=Path, help="수정한 자막(.srt) 경로")
    p_reburn.add_argument("-o", "--output", type=Path, default=Path("output"), help="출력 폴더 (기본: output)")
    p_reburn.add_argument("-c", "--config", type=Path, default=None, help="설정 YAML 경로")
    p_reburn.add_argument("--assets", type=Path, default=None, help="브랜딩 자원 폴더 (기본: ./assets)")
    p_reburn.add_argument("--no-shorts", action="store_true", help="숏츠 재생성 비활성화")
    p_reburn.add_argument("--no-branding", action="store_true", help="브랜딩 비활성화")
    p_reburn.add_argument("-v", "--verbose", action="store_true", help="상세 로그")

    # init-config
    p_init = sub.add_parser("init-config", help="설정 템플릿 파일 생성")
    p_init.add_argument("path", type=Path, nargs="?", default=Path("config.yaml"), help="생성할 파일 경로")

    return parser


def _apply_overrides(cfg: Config, args: argparse.Namespace) -> Config:
    """CLI 플래그로 설정값을 덮어쓴다."""
    if args.no_silence:
        cfg.silence.enabled = False
    if args.no_subtitles:
        cfg.subtitle.enabled = False
    if args.no_shorts:
        cfg.shorts.enabled = False
    if args.no_branding:
        cfg.branding.enabled = False
    if getattr(args, "no_fillers", False):
        cfg.subtitle.remove_fillers = False
    if args.shorts_count is not None:
        cfg.shorts.count = args.shorts_count
    if args.whisper_model:
        cfg.subtitle.model = args.whisper_model
    return cfg


def cmd_edit(args: argparse.Namespace) -> int:
    setup_logging(args.verbose)
    cfg = Config.load(args.config)
    cfg = _apply_overrides(cfg, args)

    try:
        result = process(
            args.input,
            args.output,
            cfg,
            assets_dir=args.assets,
            keep_temp=args.keep_temp,
        )
    except (FFmpegError, FileNotFoundError) as exc:
        logger.error("%s", exc)
        return 1

    print("\n✅ 편집 완료")
    print(f"   단계: {' → '.join(result.steps) if result.steps else '(없음)'}")
    if result.final_video:
        print(f"   완성 영상: {result.final_video}")
    if result.thumbnail:
        print(f"   썸네일: {result.thumbnail}")
    if result.metadata_file:
        print(f"   업로드정보(제목/설명/해시태그/챕터): {result.metadata_file}")
    if result.srt:
        print(f"   자막 파일: {result.srt}")
    if result.clean_video:
        print(f"   (자막수정용 원본: {result.clean_video})")
    if result.shorts:
        print(f"   숏츠 {len(result.shorts)}개:")
        for s in result.shorts:
            print(f"     - {s}")
    return 0


def cmd_reburn(args: argparse.Namespace) -> int:
    setup_logging(args.verbose)
    cfg = Config.load(args.config)
    if args.no_shorts:
        cfg.shorts.enabled = False
    if args.no_branding:
        cfg.branding.enabled = False

    try:
        result = reburn(
            args.clean_video,
            args.srt,
            args.output,
            cfg,
            assets_dir=args.assets,
        )
    except (FFmpegError, FileNotFoundError) as exc:
        logger.error("%s", exc)
        return 1

    print("\n✅ 자막 재반영 완료")
    if result.final_video:
        print(f"   완성 영상: {result.final_video}")
    if result.shorts:
        print(f"   숏츠 {len(result.shorts)}개 갱신")
    return 0


def cmd_init_config(args: argparse.Namespace) -> int:
    path: Path = args.path
    if path.exists():
        print(f"이미 존재합니다: {path}", file=sys.stderr)
        return 1
    path.write_text(CONFIG_TEMPLATE, encoding="utf-8")
    print(f"설정 템플릿을 생성했습니다: {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "edit":
        return cmd_edit(args)
    if args.command == "reburn":
        return cmd_reburn(args)
    if args.command == "init-config":
        return cmd_init_config(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
