"""자막 전용 글꼴 내려받기 (무료·상업 이용 가능한 OFL 라이선스 글꼴만).

설치.bat 에서 한 번 실행된다:  python -m autoedit.fonts_install
글꼴은 캡컷 ai편집기/assets/fonts 에 저장되고, 자막을 구울 때만 쓰인다(윈도우에 설치하지 않음).
"""

from __future__ import annotations

import sys
import urllib.request

from .styles import fonts_dir

# (파일명, 주소) — Google Fonts 공식 저장소 / Pretendard 공식 배포본
FONTS = [
    ("BlackHanSans-Regular.ttf", "https://github.com/google/fonts/raw/main/ofl/blackhansans/BlackHanSans-Regular.ttf"),
    ("DoHyeon-Regular.ttf", "https://github.com/google/fonts/raw/main/ofl/dohyeon/DoHyeon-Regular.ttf"),
    ("Jua-Regular.ttf", "https://github.com/google/fonts/raw/main/ofl/jua/Jua-Regular.ttf"),
    ("Pretendard-Bold.otf", "https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/public/static/Pretendard-Bold.otf"),
    ("Pretendard-Regular.otf", "https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/public/static/Pretendard-Regular.otf"),
]


def install(force: bool = False) -> int:
    d = fonts_dir()
    d.mkdir(parents=True, exist_ok=True)
    ok = 0
    for name, url in FONTS:
        dst = d / name
        if dst.exists() and dst.stat().st_size > 10_000 and not force:
            print(f"  이미 있음: {name}")
            ok += 1
            continue
        try:
            print(f"  내려받는 중: {name}")
            with urllib.request.urlopen(url, timeout=60) as r:
                data = r.read()
            if len(data) < 10_000:
                raise ValueError("파일이 너무 작습니다")
            dst.write_bytes(data)
            ok += 1
        except Exception as exc:  # noqa: BLE001
            print(f"  [건너뜀] {name}: {exc}")
    print(f"글꼴 {ok}/{len(FONTS)}개 준비 완료 → {d}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(install("--force" in sys.argv))
