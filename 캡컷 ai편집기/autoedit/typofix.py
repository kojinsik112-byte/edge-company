"""AI 자막 오타 교정 + 핵심 단어 선정.

음성인식은 발음이 비슷한 엉뚱한 단어로 적는 일이 많다("입주박람회"→"입주방남외").
Claude에게 전체 문맥과 회사 용어 사전을 주고 '들리는 대로 잘못 적힌 단어'만 고치게 한다.
문장을 다듬거나 말투를 바꾸지는 않는다(실제 말한 것과 자막이 달라지면 안 되므로).
같은 호출에서 자막에 색으로 강조할 핵심 단어도 함께 고른다.

API 키가 없으면 호출하는 쪽이 그냥 건너뛴다 (사람이 편집 화면에서 직접 고치면 됨).
"""

from __future__ import annotations

from typing import List, Set, Tuple

from .config import SmartEditConfig
from .smart_edit import SmartEditUnavailable, _resolve_api_key
from .transcribe import Caption
from .utils import logger

_SYSTEM = """당신은 한국어 방송 자막 교정 전문가입니다.
음성인식(Whisper)으로 만든 자막 목록을 받습니다. 두 가지를 해 주세요.

1) fixes — 음성인식 오타 교정
- 발음이 비슷해서 잘못 받아 적힌 단어만 고친다. (예: 입주방남외→입주박람회, 아그로→아크로, 실링펜→실링팬)
- 앞뒤 문맥과 '용어 사전'을 근거로, 화자가 실제로 말했을 단어로 고친다.
- 띄어쓰기·맞춤법이 명백히 틀린 것도 고친다.
- 말투, 어순, 표현은 바꾸지 마라. 문장을 요약하거나 다듬지 마라. 단어를 추가·삭제하지 마라.
- 고칠 게 없는 줄은 fixes 에 넣지 마라. 확신이 없으면 고치지 마라.

2) keywords — 화면에서 색으로 강조할 핵심 단어
- 영상 전체에서 시청자가 꼭 기억해야 할 단어(제품명, 핵심 장점, 숫자+단위 등) 최대 15개.
- 자막에 실제로 등장하는 형태 그대로 적는다."""


def fix_and_pick_keywords(
    captions: List[Caption], vocab: List[str], cfg: SmartEditConfig
) -> Tuple[List[Caption], Set[str], int]:
    """(교정된 자막, 핵심 단어 집합, 고친 줄 수). 실패 시 SmartEditUnavailable."""
    try:
        import anthropic  # type: ignore
        from pydantic import BaseModel  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise SmartEditUnavailable("anthropic 패키지가 필요합니다") from exc

    api_key = _resolve_api_key(cfg)
    if not api_key:
        raise SmartEditUnavailable("Anthropic API 키가 없습니다 (api_key.txt)")

    class Fix(BaseModel):
        index: int
        text: str

    class Result(BaseModel):
        fixes: List[Fix]
        keywords: List[str]

    transcript = "\n".join(f"[{i}] {c.text}" for i, c in enumerate(captions))
    client = anthropic.Anthropic(api_key=api_key)
    logger.info("AI 자막 오타 교정 중... (%s)", cfg.model)
    try:
        resp = client.messages.parse(
            model=cfg.model,
            max_tokens=16000,
            system=_SYSTEM,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "용어 사전: " + ", ".join(vocab or []) + "\n\n자막:\n" + transcript
                    ),
                }
            ],
            output_format=Result,
        )
    except Exception as exc:  # noqa: BLE001
        raise SmartEditUnavailable(f"AI 교정 호출 실패: {exc}") from exc

    res = resp.parsed_output
    if res is None:
        raise SmartEditUnavailable("AI 응답을 해석하지 못했습니다")

    fixed = list(captions)
    n = 0
    for f in res.fixes:
        if 0 <= f.index < len(fixed) and f.text.strip() and f.text.strip() != fixed[f.index].text:
            old = fixed[f.index]
            # 단어 수가 같으면 원래 단어 타이밍을 유지 (styles.words_for 가 처리)
            fixed[f.index] = Caption(old.start, old.end, f.text.strip(), old.words)
            logger.debug("오타 교정 [%d] %s → %s", f.index, old.text, f.text)
            n += 1
    logger.info("AI 오타 교정: %d줄 수정, 핵심 단어 %d개", n, len(res.keywords))
    return fixed, {k.strip() for k in res.keywords if k.strip()}, n
