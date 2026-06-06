"""제목·설명·해시태그·챕터 자동 생성.

자막(전사)을 분석해 유튜브 업로드에 바로 쓸 수 있는 메타데이터 초안을 만든다.
외부 API 없이 빈도 기반 키워드 추출 + 타임스탬프로 동작한다(오프라인).
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import List, Tuple

from .config import MetadataConfig
from .transcribe import Caption

# 키워드에서 흔히 떨어지는 한국어 조사/어미 (간단 처리용)
_PARTICLES = (
    "으로서",
    "으로써",
    "에서는",
    "에게서",
    "이라고",
    "라고",
    "으로",
    "에서",
    "에게",
    "한테",
    "까지",
    "부터",
    "이랑",
    "하고",
    "처럼",
    "보다",
    "마다",
    "조차",
    "이나",
    "은",
    "는",
    "이",
    "가",
    "을",
    "를",
    "에",
    "의",
    "도",
    "로",
    "와",
    "과",
    "랑",
    "만",
    "요",
    "고",
)

_STOPWORDS = {
    "그래서",
    "그리고",
    "그러면",
    "그런데",
    "하지만",
    "그러니까",
    "이제",
    "정말",
    "진짜",
    "약간",
    "조금",
    "되게",
    "엄청",
    "이거",
    "저거",
    "그거",
    "여기",
    "거기",
    "우리",
    "제가",
    "저는",
    "그게",
    "근데",
    "이렇게",
    "그렇게",
    "어떤",
    "무슨",
    "그냥",
    "많이",
    "사실",
}

_WORD_RE = re.compile(r"[가-힣A-Za-z0-9]+")


def _strip_particle(token: str) -> str:
    for p in _PARTICLES:
        if token.endswith(p) and len(token) > len(p) + 1:
            return token[: -len(p)]
    return token


def extract_keywords(captions: List[Caption], top_n: int = 12) -> List[str]:
    """자막에서 빈도 높은 키워드를 뽑는다."""
    counter: Counter = Counter()
    for cap in captions:
        for raw in _WORD_RE.findall(cap.text):
            if len(raw) < 2:
                continue
            token = _strip_particle(raw)
            if len(token) < 2 or token in _STOPWORDS:
                continue
            counter[token] += 1
    return [w for w, _ in counter.most_common(top_n)]


def _fmt_ts(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def build_chapters(
    captions: List[Caption], min_gap: float = 40.0, max_title: int = 22
) -> List[Tuple[float, str]]:
    """타임스탬프 챕터 목록을 만든다. 첫 챕터는 항상 0:00."""
    if not captions:
        return []
    chapters: List[Tuple[float, str]] = []
    last = -1e9
    for cap in captions:
        if cap.start - last >= min_gap or not chapters:
            title = cap.text.strip().rstrip(".,!?").strip()
            if len(title) > max_title:
                title = title[:max_title] + "…"
            start = 0.0 if not chapters else cap.start
            chapters.append((start, title))
            last = cap.start
    # 유튜브 챕터는 첫 항목이 0:00 이어야 한다
    if chapters and chapters[0][0] != 0.0:
        chapters[0] = (0.0, chapters[0][1])
    return chapters


def suggest_titles(keywords: List[str], n: int = 5) -> List[str]:
    """키워드 기반 제목 후보(초안)를 만든다."""
    kw = keywords + ["", "", ""]
    templates = [
        f"{kw[0]} 완벽 정리 (이거 모르면 손해)",
        f"{kw[0]}, 이것만 알면 끝납니다",
        f"{kw[0]} 핵심만 빠르게 정리",
        f"초보도 이해하는 {kw[0]} {kw[1]}".strip(),
        f"{kw[0]} 하는 법 | {kw[1]} 총정리".strip().strip("|").strip(),
        f"{kw[0]} 제대로 알려드립니다",
        f"{kw[0]}·{kw[1]} 5분 요약".strip("·"),
    ]
    seen, out = set(), []
    for t in templates:
        t = re.sub(r"\s+", " ", t).strip()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
        if len(out) >= n:
            break
    return out


def generate_metadata(
    captions: List[Caption], cfg: MetadataConfig
) -> Tuple[str, dict]:
    """메타데이터 텍스트와 구조(dict)를 반환한다."""
    keywords = extract_keywords(captions, cfg.num_hashtags)
    titles = suggest_titles(keywords, cfg.num_titles)
    chapters = build_chapters(captions, cfg.min_chapter_gap)
    hashtags = [f"#{k}" for k in keywords[: cfg.num_hashtags]]

    summary = " ".join(c.text for c in captions[:3]).strip()
    if len(summary) > 180:
        summary = summary[:180] + "…"

    lines: List[str] = []
    lines.append("=== 제목 후보 (마음에 드는 걸로 고르거나 다듬어 쓰세요) ===")
    for i, t in enumerate(titles, 1):
        lines.append(f"{i}. {t}")
    lines.append("")
    lines.append("=== 설명란 (복사해서 붙여넣기) ===")
    if summary:
        lines.append(summary)
        lines.append("")
    if chapters:
        lines.append("⏱️ 타임스탬프")
        for ts, title in chapters:
            lines.append(f"{_fmt_ts(ts)} {title}")
        lines.append("")
    if hashtags:
        lines.append(" ".join(hashtags))
    lines.append("")
    lines.append("=== 태그 (쉼표로 구분) ===")
    lines.append(", ".join(keywords))

    text = "\n".join(lines)
    return text, {
        "titles": titles,
        "chapters": chapters,
        "hashtags": hashtags,
        "keywords": keywords,
    }


def write_metadata(captions: List[Caption], out_path: Path, cfg: MetadataConfig):
    """메타데이터를 텍스트 파일로 저장하고 (텍스트, 구조)를 반환한다."""
    text, data = generate_metadata(captions, cfg)
    out_path.write_text(text, encoding="utf-8")
    return text, data
