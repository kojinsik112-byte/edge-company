"""어댑터 레지스트리 — 작업(task)에 맞는 최강 선수를 자동 선발.

config.routing 우선순위대로 '사용 가능한' 첫 어댑터를 고른다.
키가 하나도 없으면 placeholder 드라이런 어댑터를 쓴다.
"""
from __future__ import annotations

from pathlib import Path

from ..config import Config
from .base import ImageAdapter, ImageRequest, ImageResult
from .gemini import GeminiAdapter
from .imagen import ImagenAdapter
from .flux import FluxAdapter
from .ideogram import IdeogramAdapter
from .fashn import FashnAdapter
from .claid import ClaidAdapter


# 어댑터 이름 → (클래스, 키 이름)
_BUILDERS = {
    "imagen": (ImagenAdapter, "google"),
    "gemini": (GeminiAdapter, "google"),
    "flux": (FluxAdapter, "fal"),
    "ideogram": (IdeogramAdapter, "ideogram"),
    "fashn": (FashnAdapter, "fashn"),
    "claid": (ClaidAdapter, "claid"),
}


class _Placeholder(ImageAdapter):
    name = "dryrun"

    def available(self) -> bool:  # 항상 드라이런
        return False


class Registry:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._cache: dict[str, ImageAdapter] = {}

    def _get(self, name: str) -> ImageAdapter:
        if name not in self._cache:
            cls, key_name = _BUILDERS[name]
            self._cache[name] = cls(api_key=self.cfg.keys.get(key_name))
        return self._cache[name]

    def select(self, task: str) -> ImageAdapter:
        for name in self.cfg.routing.get(task, []):
            if name in _BUILDERS and self._get(name).available():
                return self._get(name)
        # 사용 가능한 키가 없으면 우선순위 1순위로 드라이런 (로그용 이름 유지)
        prefs = self.cfg.routing.get(task, [])
        if prefs and prefs[0] in _BUILDERS:
            return self._get(prefs[0])
        return _Placeholder()

    def render(self, req: ImageRequest, outdir: Path) -> ImageResult:
        return self.select(req.task).run(req, outdir)


def build_registry(cfg: Config) -> Registry:
    return Registry(cfg)
