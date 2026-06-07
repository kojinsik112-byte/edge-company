"""AI 기반 스마트 편집 — 자막 '내용'을 이해해서 편집 결정.

Claude(LLM)에게 전사 자막을 보여주고, 의미상 반복(재촬영 NG의 다른 표현),
비문/꼬인 문장, 주제에서 벗어난 잡담 등 '잘라야 할' 구간을 판단하게 한다.
글자 단순 비교(redundancy.py)로는 못 잡는 '같은 뜻 다른 표현'까지 잡아낸다.

Anthropic API 키가 필요하다(환경변수 ANTHROPIC_API_KEY, 또는 config의
smart_edit.api_key, 또는 작업 폴더의 api_key.txt). 없으면 호출하는 쪽에서
기존 휴리스틱으로 폴백한다.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Set

from .config import SmartEditConfig
from .transcribe import Caption
from .utils import logger


class SmartEditUnavailable(RuntimeError):
    """anthropic 미설치 또는 API 키 없음."""


def _resolve_api_key(cfg: SmartEditConfig) -> Optional[str]:
    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ["ANTHROPIC_API_KEY"]
    if cfg.api_key:
        return cfg.api_key.strip()
    key_file = Path.cwd() / "api_key.txt"
    if key_file.exists():
        text = key_file.read_text(encoding="utf-8").strip()
        if text:
            return text
    return None


_SYSTEM = """당신은 한국어 유튜브/방송 영상의 최고 편집 감독입니다.
말하기/강의/방송 영상의 '전사 자막'(번호와 시간이 붙은 문장 목록)을 받습니다.
시청자가 보기에 군더더기 없이 말이 매끄럽게 이어지도록, '잘라낼' 문장의 번호를 고르세요.

반드시 잘라낼 대상:
1) 방송 중 즉흥적으로 '막 던진 말' — 흐름과 무관한 농담, 혼잣말, 옆길로 새는 말,
   말을 던져놓고 수습 안 한 문장, 갑자기 딴소리, 시청자가 봤을 때 "이건 왜 있지?" 싶은 사족
2) 같은 내용을 다시 말한 것(재촬영/말 고쳐 말하기) — 가장 매끄러운 1개만 남기고 나머지 컷
3) 말이 꼬이거나 미완성·비문인 문장(중간에 끊고 다시 시작한 것 등)
4) 본 주제에서 벗어난 잡담·곁가지, 의미 없는 군더더기

판단 기준:
- 핵심 메시지/정보는 절대 자르지 않는다
- "이 문장을 빼도 앞뒤가 자연스럽게 이어지고 내용 손실이 없는가?" → 그렇다면 컷
- 남은 문장들만 이어 읽었을 때 말이 자연스럽고 깔끔하게 흘러야 한다
- 사용자는 '과감하고 깔끔한' 편집을 원한다. 단, 의미가 끊기면 안 된다
- 정말 애매하면 남긴다"""


def analyze(captions: List[Caption], cfg: SmartEditConfig) -> Set[int]:
    """잘라낼 자막 인덱스 집합을 반환한다. 실패 시 SmartEditUnavailable."""
    try:
        import anthropic  # type: ignore
        from pydantic import BaseModel  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise SmartEditUnavailable(
            "스마트 편집을 쓰려면 anthropic 패키지가 필요합니다: pip install anthropic"
        ) from exc

    api_key = _resolve_api_key(cfg)
    if not api_key:
        raise SmartEditUnavailable(
            "Anthropic API 키가 없습니다. api_key.txt 파일에 키를 넣거나 "
            "ANTHROPIC_API_KEY 환경변수를 설정하세요."
        )

    class CutItem(BaseModel):
        index: int
        reason: str

    class EditPlan(BaseModel):
        cuts: List[CutItem]

    lines = [f"[{i}] ({c.start:.1f}s) {c.text}" for i, c in enumerate(captions)]
    transcript = "\n".join(lines)

    client = anthropic.Anthropic(api_key=api_key)
    logger.info("AI 스마트 편집 분석 중... (%s)", cfg.model)
    try:
        response = client.messages.parse(
            model=cfg.model,
            max_tokens=8000,
            system=_SYSTEM,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "다음 전사 자막에서 잘라낼 문장의 번호를 cuts 로 골라주세요.\n"
                        "각 항목에 index(번호)와 reason(한 줄 이유)을 넣으세요.\n\n"
                        + transcript
                    ),
                }
            ],
            output_format=EditPlan,
        )
    except Exception as exc:  # noqa: BLE001
        raise SmartEditUnavailable(f"AI 분석 호출 실패: {exc}") from exc

    plan = response.parsed_output
    if plan is None:
        raise SmartEditUnavailable("AI 응답을 해석하지 못했습니다.")

    n = len(captions)
    drop: Set[int] = set()
    for item in plan.cuts:
        if 0 <= item.index < n:
            drop.add(item.index)
            logger.debug("AI 컷 [%d]: %s", item.index, item.reason)
    logger.info("AI 스마트 편집: %d개 문장을 잘라내기로 판단", len(drop))
    return drop
