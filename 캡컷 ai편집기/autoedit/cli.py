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
from .pipeline import process
from .utils import logger, setup_logging

CONFIG_TEMPLATE = """\
# autoedit 설정 파일 — 필요한 값만 바꿔 쓰면 됩니다.
silence:
  enabled: true
  noise_db: -30.0      # 이보다 조용하면 무음으로 간주
  min_silence: 0.6     # 잘라낼 무음 최소 길이(초)
  keep_pad: 0.15       # 말 앞뒤로 남길 여유(초)

subtitle:
  enabled: true
  model: small         # tiny / base / small / medium / large-v3 (발음 흐리면 small↑ 권장)
  language: ko
  # 자주 틀리는 고유명사/용어를 미리 알려주면 오타가 줄어듦 (쉼표로 나열)
  # initial_prompt: "에지컴퍼니, 오토에딧, 파이썬"
  burn_in: true        # 영상에 자막 굽기
  font: NanumGothic
  # 크기 값은 "실제 픽셀" 단위(본편 1920x1080 기준)
  font_size: 48        # 본편 자막 글자 크기(px)
  margin_v: 60         # 화면 하단 여백(px)
  max_line_chars: 28   # 한 줄 최대 글자수
  background_box: false # 글자 뒤 반투명 박스(가독성↑) — 본편은 기본 꺼짐

shorts:
  enabled: true
  count: 3             # 만들 숏츠 개수
  min_duration: 20
  max_duration: 58
  # 세로 숏츠용 자막(픽셀 단위). 키우면 양옆이 짤리니 주의.
  font_size: 56        # 숏츠 자막 글자 크기(px)
  margin_v: 220        # 자막 하단 여백(px)
  max_line_chars: 16   # 좁은 세로 화면에 맞춰 짧게
  background_box: true # 숏츠는 배경 박스 기본 켜짐
  # 효과음(옵션): assets/ 에 파일을 넣고 이름을 적으면 각 숏츠 시작에 깔림
  # start_sfx: hook.wav
  # sfx_volume: 0.9

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
  crf: 20              # 화질(낮을수록 고화질)
  preset: medium
  normalize_audio: true   # 볼륨 균일화(영상마다 소리 크기 들쭉날쭉 방지)
  loudness_target: -14.0  # 목표 음량(LUFS), 유튜브 권장 ≈ -14
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
    p_edit.add_argument(
        "--srt",
        type=Path,
        default=None,
        help="오타를 직접 고친 자막(.srt)을 사용 (음성 인식 건너뜀)",
    )
    p_edit.add_argument("--shorts-count", type=int, default=None, help="숏츠 개수")
    p_edit.add_argument("--whisper-model", type=str, default=None, help="Whisper 모델 크기")
    p_edit.add_argument(
        "--initial-prompt",
        type=str,
        default=None,
        help="자주 틀리는 고유명사/용어를 미리 알려줘 자막 정확도↑ (쉼표로 나열)",
    )
    p_edit.add_argument("--keep-temp", action="store_true", help="임시 작업 파일 보존")
    p_edit.add_argument("-v", "--verbose", action="store_true", help="상세 로그")

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
    if args.shorts_count is not None:
        cfg.shorts.count = args.shorts_count
    if args.whisper_model:
        cfg.subtitle.model = args.whisper_model
    if args.initial_prompt:
        cfg.subtitle.initial_prompt = args.initial_prompt
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
            srt_override=args.srt,
        )
    except (FFmpegError, FileNotFoundError) as exc:
        logger.error("%s", exc)
        return 1

    print("\n✅ 편집 완료")
    print(f"   단계: {' → '.join(result.steps) if result.steps else '(없음)'}")
    if result.final_video:
        print(f"   완성 영상: {result.final_video}")
    if result.srt:
        print(f"   자막 파일: {result.srt}")
    if result.shorts:
        print(f"   숏츠 {len(result.shorts)}개:")
        for s in result.shorts:
            print(f"     - {s}")
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
    if args.command == "init-config":
        return cmd_init_config(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
