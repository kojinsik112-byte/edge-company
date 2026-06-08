"""환경설정 로딩 — .env + config.yaml 을 합쳐 단일 Config 객체로."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:  # python-dotenv 미설치여도 동작
    pass


def _env(name: str) -> str | None:
    val = os.environ.get(name)
    return val.strip() if val and val.strip() else None


@dataclass
class Config:
    """파이프라인 전역 설정. 키가 없는 어댑터는 자동으로 드라이런으로 빠진다."""

    anthropic_api_key: str | None = field(default_factory=lambda: _env("ANTHROPIC_API_KEY"))
    anthropic_model: str = field(default_factory=lambda: _env("ANTHROPIC_MODEL") or "claude-opus-4-8")

    keys: dict[str, str | None] = field(
        default_factory=lambda: {
            "openai": _env("OPENAI_API_KEY"),
            "google": _env("GOOGLE_API_KEY"),
            "fal": _env("FAL_KEY"),
            "bfl": _env("BFL_API_KEY"),
            "ideogram": _env("IDEOGRAM_API_KEY"),
            "fashn": _env("FASHN_API_KEY"),
            "claid": _env("CLAID_API_KEY"),
            "photoroom": _env("PHOTOROOM_API_KEY"),
        }
    )

    # 작업(task) → 선호 어댑터 우선순위. 앞에서부터 사용 가능한 것을 고른다.
    routing: dict[str, list[str]] = field(
        default_factory=lambda: {
            "scene": ["imagen", "gemini", "flux"],
            "edit": ["gemini", "flux"],
            "text_banner": ["ideogram", "gemini"],
            "cleanup": ["claid", "photoroom"],
            "tryon": ["fashn"],
        }
    )

    def has(self, key: str) -> bool:
        return bool(self.keys.get(key))


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
