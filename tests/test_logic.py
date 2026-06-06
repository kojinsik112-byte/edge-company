"""ffmpeg 없이 검증 가능한 순수 로직 단위 테스트."""

from autoedit.utils import (
    fmt_timestamp,
    fmt_duration,
    merge_intervals,
    invert_intervals,
)
from autoedit.transcribe import Caption, slice_captions, _wrap
from autoedit.shorts import _score_windows, _select_non_overlapping
from autoedit.config import ShortsConfig, Config


def test_fmt_timestamp():
    assert fmt_timestamp(0) == "00:00:00,000"
    assert fmt_timestamp(3661.5) == "01:01:01,500"
    assert fmt_timestamp(-1) == "00:00:00,000"


def test_fmt_duration():
    assert fmt_duration(45) == "45s"
    assert fmt_duration(83) == "1m 23s"


def test_merge_intervals():
    assert merge_intervals([]) == []
    assert merge_intervals([(0, 1), (1, 2)], gap=0.1) == [(0, 2)]
    assert merge_intervals([(0, 1), (5, 6)]) == [(0, 1), (5, 6)]
    # 겹치는 구간
    assert merge_intervals([(0, 3), (2, 5)]) == [(0, 5)]


def test_invert_intervals():
    # 무음 [2,4] 를 빼면 말소리는 [0,2], [4,10]
    assert invert_intervals([(2, 4)], 10) == [(0, 2), (4, 10)]
    # 무음이 없으면 전체가 말소리
    assert invert_intervals([], 10) == [(0, 10)]
    # 처음과 끝이 무음
    assert invert_intervals([(0, 2), (8, 10)], 10) == [(2, 8)]


def test_slice_captions():
    caps = [Caption(0, 2, "a"), Caption(3, 5, "b"), Caption(6, 8, "c")]
    out = slice_captions(caps, 3, 8)
    # 3~8 구간 → b, c 가 0기준으로 재정렬
    assert [c.text for c in out] == ["b", "c"]
    assert out[0].start == 0.0
    assert out[0].end == 2.0


def test_wrap():
    assert _wrap("짧은글", 10) == "짧은글"
    wrapped = _wrap("가나다라마바사아자차카타", 4)
    assert "\n" in wrapped


def test_shorts_selection_non_overlapping():
    # 0~30, 30~60 두 개의 알찬 구간이 있는 자막
    caps = [Caption(float(i), float(i + 1), "가나다라" * 5) for i in range(0, 60)]
    cfg = ShortsConfig(min_duration=20, max_duration=30, count=2)
    windows = _score_windows(caps, cfg)
    assert windows, "후보 구간이 생성되어야 함"
    chosen = _select_non_overlapping(windows, cfg.count)
    assert len(chosen) <= cfg.count
    # 선택된 구간끼리 겹치지 않아야 함
    for a in range(len(chosen)):
        for b in range(a + 1, len(chosen)):
            x, y = chosen[a], chosen[b]
            assert x.end <= y.start or x.start >= y.end


def test_config_defaults():
    cfg = Config()
    assert cfg.silence.enabled is True
    assert cfg.shorts.width == 1080 and cfg.shorts.height == 1920
    assert cfg.output.width == 1920 and cfg.output.height == 1080
