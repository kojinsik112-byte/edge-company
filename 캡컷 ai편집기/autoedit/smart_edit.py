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


def _read_key_file(p: Path) -> Optional[str]:
    try:
        text = p.read_text(encoding="utf-8-sig", errors="ignore")
    except Exception:  # noqa: BLE001
        return None
    text = text.strip().strip('"').strip("'").strip()
    # 혹시 메모장이 아닌 곳에 키만 들어있다면 sk- 로 시작하는 토큰을 추출
    if "sk-ant" in text:
        for token in text.split():
            if token.startswith("sk-ant"):
                return token.strip().strip('"').strip("'")
    if text.startswith("sk-"):
        return text
    return None


def _resolve_api_key(cfg: SmartEditConfig) -> Optional[str]:
    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ["ANTHROPIC_API_KEY"].strip()
    if cfg.api_key:
        return cfg.api_key.strip()

    # 파일 위치/확장자를 조금 틀려도 찾아낸다:
    # 작업폴더 · autoedit 폴더 · 그 상위 폴더에서 'api_key*'/'apikey*' 파일을 모두 확인.
    here = Path(__file__).resolve().parent
    search_dirs = [Path.cwd(), here, here.parent]
    seen = set()
    for d in search_dirs:
        if not d.exists() or d in seen:
            continue
        seen.add(d)
        for p in sorted(d.iterdir()):
            if not p.is_file():
                continue
            name = p.name.lower().replace(" ", "").replace("_", "")
            if name.startswith("apikey"):
                key = _read_key_file(p)
                if key:
                    return key
    return None


_SYSTEM = """당신은 한국어 유튜브/방송 영상의 최고 편집 감독입니다.
말하기/강의/방송 영상의 '전사 자막'(번호·시간이 붙은 문장 목록)을 받습니다.
이 자막은 화면에 표시하지 않고, 당신이 '말의 내용을 이해'하기 위한 용도입니다.
시청자가 보기에 말이 매끄럽게 이어지도록, '잘라낼' 문장의 번호를 과감하게 고르세요.

★ 가장 중요 — '글자'가 아니라 '의미'로 판단하라:
- 자막은 음성인식 결과라, 발음이 부정확하면 단어가 틀리게 적혀 있을 수 있다.
  (예: "입주박람회"가 "입주방남외"로, "분양"이 "부냥"으로 잘못 적힘)
- 이렇게 글자가 어색하거나 오타처럼 보여도, 문맥상 그게 '핵심 단어/핵심 내용'이면
  절대 자르지 마라. 발음·인식이 이상한 것일 뿐 중요한 말을 하고 있는 것이다.
- "글자가 이상하다"는 이유만으로 자르지 마라. 앞뒤 맥락으로 무슨 말인지 추론한 뒤,
  '의미'가 핵심이면 남기고, '의미'가 군더더기면 자른다.

반드시 잘라낼 대상(의미 기준):
1) 방송 중 즉흥적으로 '막 던진 말' — 흐름과 무관한 농담, 혼잣말, 옆길로 새는 말,
   던져놓고 수습 안 한 문장, 갑자기 딴소리, "이건 왜 있지?" 싶은 사족
2) 같은 내용을 두 번 이상 말한 것(말을 더듬어 다시 말함/재촬영) — 그중 '가장 잘 말한'
   테이크(문장이 완성되고 깔끔하게 들리는 것) 1개만 남기고 나머지는 모두 잘라라.
   순서와 무관하다(앞의 것일 수도, 뒤의 것일 수도 있다). 더듬은 것·끊긴 것을 버리고
   제대로 말한 것을 선택하라.
   (예: "주관사를 바꿔야 합니다 / 아.. / 바꿔야 합니다" → 더듬은 앞부분을 버리고
    제대로 말한 쪽만 남겨, 한 번 깔끔하게 말한 것처럼 만든다)
3) 진짜로 말이 꼬여 의미가 없는 미완성 발화(인식 오류가 아니라, 실제로 말을 흐린 것)
4) 본 주제에서 벗어난 잡담·곁가지, 의미 없는 군더더기

판단 기준:
- 핵심 메시지/정보/핵심 단어는 절대 자르지 않는다 (글자가 틀려 보여도)
- "이 문장을 빼도 앞뒤가 자연스럽게 이어지고 내용 손실이 없는가?" → 그렇다면 컷
- 남은 문장들만 이어 읽었을 때 말이 자연스럽고 깔끔하게 흘러야 한다
- ★ 사용자는 '아주 과감한' 편집을 강하게 원한다. 핵심 정보가 아니라면 적극적으로 잘라라.
  같은 말을 늘어뜨리는 것, 군더더기 설명, 사족, 옆길은 망설이지 말고 컷.
- 단, 핵심 정보/핵심 단어가 사라지면 안 된다 — 이것만 지키면 최대한 많이 잘라라
- 보통 전체 문장의 20~40%까지도 잘라낼 수 있다. 적게 자르는 것보다 과감한 게 낫다"""


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
