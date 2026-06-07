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
    speech_only: bool = True     # 말하는 구간만 남기고 나머지(준비·응시·무음) 전부 컷 (가장 과감)
    speech_pad: float = 0.08     # 말 앞뒤로 남길 여유(초). 작을수록 더 과감/타이트
    bridge_gap: float = 0.18     # 말 사이 이보다 짧은 틈만 유지(초). 작을수록 더 많이 컷
    noise_db: float = -30.0      # (dB 방식 대비용) 이 값보다 조용하면 무음
    min_silence: float = 0.4     # (dB 방식) 잘라낼 무음 최소 길이(초)
    keep_pad: float = 0.07       # (dB 방식) 말 앞뒤 여유(초)
    min_keep: float = 0.30       # 이보다 짧은 말 토막은 버린다 (초)


@dataclass
class SubtitleConfig:
    """자동 자막(번인) 설정."""

    enabled: bool = True
    model: str = "base"          # whisper 모델 크기 (tiny/base/small/medium/large-v3). base=빠름·괜찮은 정확도
    device: str = "cpu"          # "cpu"(권장, 어디서나 동작) 또는 "cuda"(NVIDIA GPU+CUDA 설치 시)
    language: Optional[str] = "ko"
    burn_in: bool = False        # 화면에 자막 글자 표시 (오타 우려로 기본 끔). 켜려면 true
    dynamic: bool = False        # 말하는 단어가 칠해지는 동적(노래방) 자막 (burn_in 켤 때만)
    highlight_color: str = "&H0000FFFF"  # 동적 자막 강조색 (노란색)
    remove_fillers: bool = True  # "어/아/음" 같은 추임새를 영상에서 잘라냄 (글자 표시와 무관)
    font: str = "Malgun Gothic"  # 한국어 Windows 기본 한글 폰트 (맑은 고딕)
    font_size: int = 48          # 자막 글자 크기 (영상 해상도 기준 픽셀)
    primary_color: str = "&H00FFFFFF"   # ASS 색상 (흰색)
    outline_color: str = "&H00000000"   # 검정 외곽선
    outline: int = 3             # 외곽선 두께 (px)
    margin_v: int = 60           # 화면 하단 여백 (px)
    max_line_chars: int = 28     # SRT 파일 줄바꿈 기준 (번인은 자동 줄바꿈)


@dataclass
class ShortsConfig:
    """숏츠 자동 생성 설정."""

    enabled: bool = True
    count: int = 3               # 만들 숏츠 개수
    min_duration: float = 20.0   # 숏츠 최소 길이 (초)
    max_duration: float = 58.0   # 숏츠 최대 길이 (초, 60초 미만 권장)
    width: int = 1080
    height: int = 1920
    burn_subtitles: bool = False  # 숏츠에 자막 글자 표시 (오타 우려로 기본 끔)
    font_size: int = 64          # 세로 영상은 글자를 더 크게 (px)
    margin_v: int = 360          # 세로 영상 자막 하단 여백 (px, 폰 UI 피해 위로)
    hook_text: Optional[str] = None  # 숏츠 상단 훅 문구 (없으면 첫 자막 사용)
    hook_font_size: int = 72     # 훅 문구 글자 크기 (px)


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
    crf: int = 22                # 화질 (낮을수록 고화질, 18~23 권장)
    preset: str = "veryfast"     # 인코딩 속도 (veryfast=빠름. 더 고화질 원하면 medium/slow)
    audio_bitrate: str = "192k"


@dataclass
class AudioConfig:
    """오디오 음질 개선 설정."""

    enabled: bool = True
    denoise: bool = True         # 잡음 제거 (afftdn)
    loudnorm: bool = True        # 음량 정규화
    target_lufs: float = -14.0   # 유튜브 표준 음량


@dataclass
class ThumbnailConfig:
    """썸네일 자동 생성 설정."""

    enabled: bool = True
    text: Optional[str] = None   # 썸네일 문구 (없으면 자동 생성 제목 사용)
    font: str = "Malgun Gothic"
    font_size: int = 96          # 1280x720 기준 픽셀
    primary_color: str = "&H0000FFFF"   # 노란색 (눈에 띔)
    outline_color: str = "&H00000000"
    outline: int = 6


@dataclass
class MetadataConfig:
    """제목/설명/해시태그/챕터 자동 생성 설정."""

    enabled: bool = True
    num_titles: int = 5          # 제목 후보 개수
    num_hashtags: int = 12
    min_chapter_gap: float = 40.0  # 챕터 최소 간격(초)


@dataclass
class SmartEditConfig:
    """AI 스마트 편집 설정 (자막 내용을 이해해 반복·비문·잡담 컷)."""

    enabled: bool = True         # API 키가 있으면 사용, 없으면 자동으로 휴리스틱 폴백
    model: str = "claude-opus-4-8"
    api_key: Optional[str] = None  # 비워두면 ANTHROPIC_API_KEY 또는 api_key.txt 사용


@dataclass
class Config:
    silence: SilenceConfig = field(default_factory=SilenceConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    subtitle: SubtitleConfig = field(default_factory=SubtitleConfig)
    shorts: ShortsConfig = field(default_factory=ShortsConfig)
    branding: BrandingConfig = field(default_factory=BrandingConfig)
    thumbnail: ThumbnailConfig = field(default_factory=ThumbnailConfig)
    metadata: MetadataConfig = field(default_factory=MetadataConfig)
    smart_edit: SmartEditConfig = field(default_factory=SmartEditConfig)
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
            ("audio", AudioConfig),
            ("subtitle", SubtitleConfig),
            ("shorts", ShortsConfig),
            ("branding", BrandingConfig),
            ("thumbnail", ThumbnailConfig),
            ("metadata", MetadataConfig),
            ("smart_edit", SmartEditConfig),
            ("output", OutputConfig),
        ):
            if section in data and isinstance(data[section], dict):
                merged = {**asdict(getattr(cfg, section)), **data[section]}
                setattr(cfg, section, sub(**merged))
        return cfg
