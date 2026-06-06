"""ffmpeg 없이 검증 가능한 순수 로직 단위 테스트."""

from autoedit.utils import (
    fmt_timestamp,
    fmt_duration,
    merge_intervals,
    invert_intervals,
)
from autoedit.transcribe import Caption, slice_captions, _wrap, write_srt, parse_srt
from autoedit.shorts import _score_windows, _select_non_overlapping
from autoedit.fillers import is_filler, find_filler_ranges, remap_captions
from autoedit.subtitles import write_ass, _ass_time
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


def test_is_filler():
    assert is_filler("어")
    assert is_filler("음...")
    assert is_filler("어어")
    assert is_filler("아 ")
    assert not is_filler("아니요")
    assert not is_filler("그래서")
    assert not is_filler("저는")
    assert not is_filler("")


def test_filler_removal_and_remap():
    caps = [
        Caption(0, 1, "안녕하세요"),
        Caption(1, 1.5, "어"),
        Caption(1.5, 3, "오늘은"),
        Caption(3, 3.4, "음.."),
        Caption(3.4, 5, "강의입니다"),
    ]
    ranges = find_filler_ranges(caps)
    assert len(ranges) == 2
    new = remap_captions(caps, ranges)
    # 추임새 2개는 빠지고 3개만 남는다
    assert [c.text for c in new] == ["안녕하세요", "오늘은", "강의입니다"]
    # 시간이 앞으로 당겨져 연속적이어야 한다 (간격 없음)
    assert new[0].start == 0.0
    assert new[1].start < 1.5  # 추임새 제거로 당겨짐
    assert new[2].end < 5.0


def test_parse_srt_roundtrip(tmp_path):
    caps = [Caption(0, 2, "첫째 줄입니다"), Caption(2.5, 4, "둘째 줄, 쉼표 포함")]
    srt = write_srt(caps, tmp_path / "x.srt")
    back = parse_srt(srt)
    assert len(back) == 2
    assert back[0].text == "첫째 줄입니다"
    assert abs(back[1].start - 2.5) < 0.01


def test_ass_time():
    assert _ass_time(0) == "0:00:00.00"
    assert _ass_time(3661.5) == "1:01:01.50"


def test_write_ass_no_leading_comma(tmp_path):
    caps = [Caption(0, 2, "테스트 자막")]
    ass = write_ass(
        caps,
        tmp_path / "t.ass",
        width=1080,
        height=1920,
        font="Malgun Gothic",
        font_size=64,
        primary_color="&H00FFFFFF",
        outline_color="&H00000000",
        outline=3,
        margin_v=360,
    )
    content = ass.read_text(encoding="utf-8")
    assert "PlayResX: 1080" in content
    assert "PlayResY: 1920" in content
    dialogue = [ln for ln in content.splitlines() if ln.startswith("Dialogue:")][0]
    # Text는 9번째 필드(0-based 인덱스 8). 콤마가 하나 더 있으면 자막 앞에 ','가 찍힌다.
    text_field = dialogue.split(",", 8)[8]
    assert text_field == "테스트 자막"


def test_metadata_chapters_and_keywords():
    from autoedit.metadata import build_chapters, extract_keywords, suggest_titles

    caps = [
        Caption(0, 3, "오늘은 주식 투자 기초를 배웁니다"),
        Caption(60, 63, "분산 투자가 정말 중요합니다"),
        Caption(140, 143, "마지막으로 투자 원칙을 정리합니다"),
    ]
    chapters = build_chapters(caps, min_gap=40)
    assert chapters[0][0] == 0.0          # 첫 챕터는 0:00
    assert len(chapters) == 3
    kws = extract_keywords(caps, 5)
    assert "투자" in kws                  # 빈도 높은 키워드
    titles = suggest_titles(kws, 3)
    assert len(titles) == 3 and all(titles)
