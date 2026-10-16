"""입예협 사각 도장(인영) 생성기.

사용: python make_seal.py <폰트폴더>
  폰트폴더: Pretendard-Black.otf 와 fontsource nanum-myeongjo 800 woff 조각들이 있는 곳
산출: 같은 폴더(seal/)에 PNG(투명배경) — clean(제작용) / stamp(찍힌 느낌, 문서용)
"""
import glob
import os
import random
import sys

from fontTools.ttLib import TTFont
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROWS = ["e편한세상", "에코델타", "센터포인트", "입예협회장"]
RED = (200, 22, 29)
SIZE = 1200          # 최종 한 변(px) ≈ 24mm 도장 기준 1270dpi급
BORDER = 70          # 외곽 테두리 두께
GAP = 34             # 테두리-글자 여백
LINE_GAP = 26        # 행 간격
OUT = os.path.dirname(os.path.abspath(__file__))


class GlyphFonts:
    """글자별로 해당 글리프가 들어있는 폰트 파일을 찾아준다(조각난 웹폰트 대응)."""

    def __init__(self, paths):
        self.maps = []
        for p in paths:
            cmap = TTFont(p).getBestCmap() or {}
            self.maps.append((p, set(cmap)))

    def path_for(self, ch):
        for p, cps in self.maps:
            if ord(ch) in cps:
                return p
        raise KeyError(f"글리프 없음: {ch}")


def render_char(ch, fonts, px=600):
    font = ImageFont.truetype(fonts.path_for(ch), px)
    im = Image.new("L", (px * 2, px * 2), 0)
    ImageDraw.Draw(im).text((px // 2, px // 4), ch, font=font, fill=255)
    return im.crop(im.getbbox())


def render_row(text, fonts, w, h):
    """한 행을 셀(w×h)에 꽉 차게. 글자마다 같은 폭 칸에 세로로 늘려 도장 특유의 꽉 찬 느낌."""
    n = len(text)
    gap = int(w * 0.035)
    cw = (w - gap * (n - 1)) / n
    row = Image.new("L", (w, h), 0)
    for i, ch in enumerate(text):
        g = render_char(ch, fonts)
        if ch.isascii():  # 소문자 e 는 한글보다 낮으므로 높이 80%로 하단 정렬
            g = g.resize((int(cw * 0.78), int(h * 0.80)), Image.LANCZOS)
            x = int(i * (cw + gap) + (cw - g.width) / 2)
            row.paste(g, (x, h - g.height), g)
        else:
            g = g.resize((int(cw), h), Image.LANCZOS)
            row.paste(g, (int(i * (cw + gap)), 0), g)
    return row


def build_mask(fonts):
    m = Image.new("L", (SIZE, SIZE), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=36, fill=255)
    d.rounded_rectangle([BORDER, BORDER, SIZE - 1 - BORDER, SIZE - 1 - BORDER], radius=14, fill=0)
    inner = BORDER + GAP
    w = SIZE - inner * 2
    rh = (w - LINE_GAP * (len(ROWS) - 1)) // len(ROWS)
    for i, t in enumerate(ROWS):
        r = render_row(t, fonts, w, rh)
        m.paste(255, (inner, inner + i * (rh + LINE_GAP)), r)
    return m


def colorize(mask):
    im = Image.new("RGBA", mask.size, RED + (0,))
    im.putalpha(mask)
    return im


def stamped(mask, seed=7):
    """인주 번짐·잉크 빠짐 질감."""
    rnd = random.Random(seed)
    fine = Image.effect_noise(mask.size, 110).filter(ImageFilter.GaussianBlur(1.3))
    holes = fine.point(lambda v: 0 if v < 78 else 255).filter(ImageFilter.GaussianBlur(0.8))
    coarse = Image.effect_noise((SIZE // 60, SIZE // 60), 40).resize(mask.size, Image.BICUBIC)
    patchy = coarse.point(lambda v: max(215, min(255, v + 110)))  # 인주가 덜 묻은 얼룩
    m = ImageChops.multiply(mask.filter(ImageFilter.GaussianBlur(1.4)), holes)
    m = ImageChops.multiply(m, patchy)
    # 가장자리 압력 불균일(한쪽이 살짝 연함)
    grad = Image.linear_gradient("L").resize(mask.size).point(lambda v: 205 + v * 50 // 255)
    m = ImageChops.multiply(m, grad.rotate(rnd.choice([0, 90, 180, 270])))
    return colorize(m.point(lambda v: 0 if v < 40 else v)).rotate(-1.2, resample=Image.BICUBIC)


def main(font_dir):
    variants = {
        "myeongjo": sorted(glob.glob(os.path.join(font_dir, "**/nanum-myeongjo-*-800-normal.woff"), recursive=True)),
        "gothic": glob.glob(os.path.join(font_dir, "**/Pretendard-Black.otf"), recursive=True),
    }
    for name, paths in variants.items():
        mask = build_mask(GlyphFonts(paths))
        colorize(mask).save(os.path.join(OUT, f"입예협회장_도장_{name}_clean.png"))
        stamped(mask).save(os.path.join(OUT, f"입예협회장_도장_{name}_stamp.png"))
        print("ok", name)


if __name__ == "__main__":
    main(sys.argv[1])
