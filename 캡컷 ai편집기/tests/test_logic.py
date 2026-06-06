"""ffmpeg 없이 검증 가능한 순수 로직 단위 테스트."""

from autoedit.utils import (
    fmt_timestamp,
    fmt_duration,
    merge_intervals,
    invert_intervals,
)
from autoedit.transcribe import (
    Caption,
    slice_captions,
    write_srt,
    parse_srt,
    _parse_timestamp,
    _wrap,
)
from autoedit.shorts import _score_windows, _select_non_overlapping, _resolve_sfx
from autoedit.subtitles import build_ass, _ass_timestamp, _ass_text
from autoedit.config import ShortsConfig, SubtitleConfig, Config


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
    # 숏츠 자막은 좁은 세로 화면에 맞게 본편보다 한 줄을 짧게 끊는다.
    assert cfg.shorts.max_line_chars < cfg.subtitle.max_line_chars
    # 볼륨 균일화는 기본 켜짐, 숏츠 배경 박스도 기본 켜짐.
    assert cfg.output.normalize_audio is True
    assert cfg.shorts.background_box is True


def test_ass_timestamp():
    assert _ass_timestamp(0) == "0:00:00.00"
    assert _ass_timestamp(3661.5) == "1:01:01.50"
    assert _ass_timestamp(-1) == "0:00:00.00"


def test_ass_text_escapes_and_wraps():
    # 줄바꿈은 \\N 으로, 태그 문자({})는 제거된다.
    out = _ass_text("가나다라마바사아자차", 4)
    assert "\\N" in out and "\n" not in out
    assert _ass_text("a{b}c", 0) == "a(b)c"


def test_build_ass_pixel_accurate(tmp_path):
    caps = [Caption(0.0, 2.0, "픽셀 크기 테스트")]
    # PlayRes 를 영상 크기에 고정 → Fontsize 가 픽셀 단위가 된다.
    p = build_ass(
        caps, tmp_path / "x.ass", dims=(1080, 1920), font="Malgun Gothic",
        font_size=58, primary_color="&H00FFFFFF", outline_color="&H00000000",
        outline=3, margin_v=220, max_line_chars=16,
    )
    text = p.read_text(encoding="utf-8")
    assert "PlayResX: 1080" in text and "PlayResY: 1920" in text
    assert "Fontsize" in text and ",58," in text
    assert "BorderStyle" in text and "Dialogue: 0,0:00:00.00,0:00:02.00" in text

    # 배경 박스 모드: BorderStyle=3, 박스색을 OutlineColour 로 사용.
    pb = build_ass(
        caps, tmp_path / "b.ass", dims=(1080, 1920), font="Malgun Gothic",
        font_size=58, primary_color="&H00FFFFFF", outline_color="&H00000000",
        outline=3, margin_v=220, max_line_chars=16,
        background_box=True, box_color="&H80000000", box_pad=14,
    )
    style = [ln for ln in pb.read_text(encoding="utf-8").splitlines()
             if ln.startswith("Style:")][0]
    parts = style.split(",")
    assert parts[5] == "3"            # BorderStyle
    assert parts[4] == "&H80000000"   # OutlineColour = 박스색
    assert parts[6] == "14"           # Outline = 박스 여백


def test_resolve_sfx(tmp_path):
    # 효과음 미설정 → None
    assert _resolve_sfx(ShortsConfig(), tmp_path) is None
    # 파일이 없으면 None (경고만)
    cfg = ShortsConfig(start_sfx="없는효과음.wav")
    assert _resolve_sfx(cfg, tmp_path) is None
    # assets 폴더에 실제로 있으면 그 경로를 돌려준다
    sfx = tmp_path / "hook.wav"
    sfx.write_bytes(b"RIFF")
    cfg2 = ShortsConfig(start_sfx="hook.wav")
    assert _resolve_sfx(cfg2, tmp_path) == sfx


def test_parse_timestamp():
    assert _parse_timestamp("00:00:00,000") == 0.0
    assert _parse_timestamp("01:01:01,500") == 3661.5
    # 점(.) 구분자도 허용
    assert _parse_timestamp("00:00:02.250") == 2.25
    assert _parse_timestamp("타임코드 아님") is None


def test_parse_srt_roundtrip(tmp_path):
    caps = [Caption(0.0, 2.0, "안녕하세요"), Caption(3.5, 5.0, "반갑습니다")]
    srt = write_srt(caps, tmp_path / "x.srt")
    out = parse_srt(srt)
    assert [c.text for c in out] == ["안녕하세요", "반갑습니다"]
    assert out[0].start == 0.0 and out[0].end == 2.0
    assert out[1].start == 3.5 and out[1].end == 5.0


def test_parse_srt_skips_bad_blocks(tmp_path):
    # BOM, 여러 줄 자막, 형식이 깨진 블록이 섞여 있어도 견고하게 파싱한다.
    text = (
        "﻿1\n00:00:00,000 --> 00:00:02,000\n첫 줄\n둘째 줄\n\n"
        "2\n잘못된 타임코드\n버릴 블록\n\n"
        "3\n00:00:03,000 --> 00:00:04,000\n끝\n"
    )
    p = tmp_path / "messy.srt"
    p.write_text(text, encoding="utf-8")
    out = parse_srt(p)
    assert [c.text for c in out] == ["첫 줄 둘째 줄", "끝"]
