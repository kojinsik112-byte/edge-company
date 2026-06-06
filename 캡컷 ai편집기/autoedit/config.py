"""편집 파이프라인 설정.

CLI 기본값 + (선택) YAML 파일로 모든 파라미터를 조정할 수 있다.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

try:
    import yaml  # type: ignore
except Exception:  # PyYAML 미설치 환경에서도 기본값으로 동작
    yaml = None


@dataclass
class SilenceConfig:
    """무음 구간 자동 컷 설정."""

    enabled: bool = True
    noise_db: float = -30.0      # 이 값보다 조용하면 무음으로 간주 (dB)
    min_silence: float = 0.6     # 무음으로 잘라낼 최소 길이 (초)
    keep_pad: float = 0.15       # 잘라낸 말소리 앞뒤로 남길 여유 (초)
    min_keep: float = 0.30       # 이보다 짧은 말 토막은 버린다 (초)


@dataclass
class SubtitleConfig:
    """자동 자막(번인) 설정."""

    enabled: bool = True
    model: str = "small"         # whisper 모델 크기 (tiny/base/small/medium/large-v3)
    language: Optional[str] = "ko"
    burn_in: bool = True         # True면 영상에 자막을 구워 넣는다
    font: str = "NanumGothic"
    font_size: int = 22
    primary_color: str = "&H00FFFFFF"   # ASS 색상 (흰색)
    outline_color: str = "&H00000000"   # 검정 외곽선
    outline: int = 2
    margin_v: int = 40           # 화면 하단 여백 (px)
    max_line_chars: int = 28     # 한 줄 최대 글자수 (넘으면 줄바꿈)


@dataclass
class ShortsConfig:
    """숏츠 자동 생성 설정."""

    enabled: bool = True
    count: int = 3               # 만들 숏츠 개수
    min_duration: float = 20.0   # 숏츠 최소 길이 (초)
    max_duration: float = 58.0   # 숏츠 최대 길이 (초, 60초 미만 권장)
    width: int = 1080
    height: int = 1920
    burn_subtitles: bool = True
    font_size: int = 14          # 세로 영상은 자막을 더 크게
    margin_v: int = 320          # 세로 영상 자막 하단 여백


@dataclass
class BrandingConfig:
    """인트로/아웃트로/BGM 설정."""

    enabled: bool = True
    intro: Optional[str] = None  # 인트로 영상 경로 (assets/intro.mp4 등)
    outro: Optional[str] = None
    bgm: Optional[str] = None    # 배경음악 경로
    bgm_volume: float = 0.12     # 본 음성 대비 BGM 볼륨 (0~1)


@dataclass
class OutputConfig:
    """출력/인코딩 설정."""

    width: int = 1920
    height: int = 1080
    fps: int = 30
    video_codec: str = "libx264"
    crf: int = 20                # 화질 (낮을수록 고화질, 18~23 권장)
    preset: str = "medium"
    audio_bitrate: str = "192k"


@dataclass
class Config:
    silence: SilenceConfig = field(default_factory=SilenceConfig)
    subtitle: SubtitleConfig = field(default_factory=SubtitleConfig)
    shorts: ShortsConfig = field(default_factory=ShortsConfig)
    branding: BrandingConfig = field(default_factory=BrandingConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    @classmethod
    def load(cls, path: Optional[Path]) -> "Config":
        """YAML 설정 파일을 읽어 Config를 만든다. 경로가 없으면 기본값."""
        cfg = cls()
        if path is None:
            return cfg
        if yaml is None:
            raise RuntimeError(
                "설정 파일을 쓰려면 PyYAML 이 필요합니다: pip install pyyaml"
            )
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        for section, sub in (
            ("silence", SilenceConfig),
            ("subtitle", SubtitleConfig),
            ("shorts", ShortsConfig),
            ("branding", BrandingConfig),
            ("output", OutputConfig),
        ):
            if section in data and isinstance(data[section], dict):
                merged = {**asdict(getattr(cfg, section)), **data[section]}
                setattr(cfg, section, sub(**merged))
        return cfg
